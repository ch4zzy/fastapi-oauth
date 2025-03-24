# app/auth/social_auth.py
from abc import ABC, abstractmethod

import httpx
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException

from app.core.config import settings
from app.users.models import User
from app.users.repositories import UserRepository


class SocialAuth(ABC):
    def __init__(self, oauth: OAuth, user_service: UserRepository):
        self.oauth = oauth
        self.user_service = user_service
        self.provider_name = self.__class__.__name__.replace('Auth', '').lower()
        self._access_token_url = None

    @property
    def client(self):
        return getattr(self.oauth, self.provider_name, None)

    @abstractmethod
    async def configure_oauth(self):
        pass

    @abstractmethod
    async def get_user_info(self, token: dict) -> dict:
        pass

    async def get_token(self, code: str, redirect_uri: str) -> dict:
        if not self._access_token_url:
            raise HTTPException(
                status_code=500,
                detail=f"Access token URL not configured for {self.provider_name}"
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._access_token_url,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                }
            )
            response.raise_for_status()
            return response.json()

    async def authenticate_user(self, token: dict) -> User:
        user_info = await self.get_user_info(token)
        email = user_info.get('email')
        if not email:
            raise HTTPException(status_code=400, detail="Email not found in provider response")

        user = await self.user_service.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user


class SocialAuthFactory:
    @staticmethod
    async def get_social_auth(provider: str, oauth: OAuth, user_service: UserRepository) -> SocialAuth:
        from app.auth.providers.google import GoogleAuth

        providers = {
            'google': GoogleAuth,
        }

        auth_class = providers.get(provider.lower())
        if not auth_class:
            raise HTTPException(status_code=400, detail="Unsupported social provider")

        auth_instance = auth_class(oauth, user_service)
        await auth_instance.configure_oauth()
        return auth_instance
