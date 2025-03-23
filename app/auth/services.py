# app/auth/services.py
import secrets
from typing import Dict

import httpx
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBasicCredentials
from app.auth.security import SecurityService
from app.auth.social_auth import SocialAuthFactory
from app.core.config import settings
from app.repositories.user import UserRepository
from app.users.models import User

class AuthService:
    def __init__(self, user_service: UserRepository):
        self.user_service = user_service

    async def authenticate_user(self, token: str) -> User:
        email = SecurityService.decode_token(token)
        user = await self.user_service.get_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return user

    async def authenticate_basic(self, credentials: HTTPBasicCredentials) -> User:
        user = await self.user_service.get_by_email(credentials.username)
        if not user or not SecurityService.verify_password(credentials.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return user


class SocialAuthService:
    def __init__(self, auth_service):
        self.auth_service = auth_service
        self.provider = auth_service.provider_name

    @staticmethod
    async def create(
        provider: str,
        oauth=Depends(),
        user_service=Depends(SocialAuthFactory.get_social_auth)
    ):
        auth_service = await SocialAuthFactory.get_social_auth(provider, oauth, user_service)
        return SocialAuthService(auth_service)

    async def generate_auth_url(self, request: Request) -> Dict:
        redirect_uri = f"{settings.BASE_URL}/auth/{self.provider}/callback"
        state = secrets.token_urlsafe(16)
        auth_url_data = await self.auth_service.client.create_authorization_url(
            redirect_uri=redirect_uri,
            state=state
        )
        request.session[f"oauth_state_{self.provider}"] = state
        return {"url": auth_url_data["url"]}

    async def handle_callback(self, request: Request) -> Dict:

        session_state = request.session.get(f"oauth_state_{self.provider}")
        query_state = request.query_params.get("state")

        if not session_state or session_state != query_state:
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        code = request.query_params.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Missing authorization code")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": f"{settings.BASE_URL}/auth/{self.provider}/callback",
                    "grant_type": "authorization_code"
                }
            )
            response.raise_for_status()
            token = response.json()
            user = await self.auth_service.authenticate_user(token)
            access_token = SecurityService.create_access_token(data={"sub": user.email})
            request.session.pop(f"oauth_state_{self.provider}", None)
            return {"access_token": access_token, "token_type": "Bearer"}
