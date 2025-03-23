# app/auth/social_auth.py
from abc import ABC, abstractmethod
from typing import Dict
import httpx
from fastapi import HTTPException, Depends
from app.core.dependencies import get_user_service
from app.repositories.user import UserRepository
from app.users.models import User
from authlib.integrations.starlette_client import OAuth
from app.core.config import settings


class SocialAuth(ABC):
    def __init__(self, oauth: OAuth, user_service: UserRepository):
        self.oauth = oauth
        self.user_service = user_service
        self.provider_name = self.__class__.__name__.replace('Auth', '').lower()

    @property
    def client(self):
        """Get the OAuth client for this provider"""
        return getattr(self.oauth, self.provider_name)

    @abstractmethod
    async def configure_oauth(self):
        """Configure OAuth client for specific provider"""
        pass

    @abstractmethod
    async def get_user_info(self, token: dict) -> Dict:
        """Get user information from provider"""
        pass

    async def authenticate_user(self, token: dict) -> User:
        user_info = await self.get_user_info(token)
        email = user_info.get('email')
        if not email:
            raise HTTPException(status_code=400, detail="Email not found in provider response")

        user = await self.user_service.get_by_email(email)
        #if not user:
            #user = await self.user_service.create({
                #'email': email,
                #'name': user_info.get('name'),
                #'social_id': user_info.get('sub') or user_info.get('id')
            #})
        return user


class GoogleAuth(SocialAuth):
    async def configure_oauth(self):
        self.oauth.register(
            name='google',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid profile email'},
            authorize_state=settings.SECRET_KEY
        )

    async def get_user_info(self, token: dict) -> Dict:
        access_token = token.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access_token in token response")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()


class SocialAuthFactory:
    @staticmethod
    async def get_social_auth(
            provider: str,
            oauth: OAuth = Depends(),
            user_service: UserRepository = Depends(get_user_service)
    ) -> SocialAuth:
        providers = {
            'google': GoogleAuth,
        }

        auth_class = providers.get(provider.lower())
        if not auth_class:
            raise HTTPException(status_code=400, detail="Unsupported social provider")

        auth_instance = auth_class(oauth, user_service)
        await auth_instance.configure_oauth()
        return auth_instance