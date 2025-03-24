# app/auth/dependencies.py
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBasic

from app.auth.services import AuthService, SocialAuthService
from app.users.dependencies import get_user_service
from app.users.models import User
from app.users.repositories import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
security = HTTPBasic()
oauth = OAuth()


async def get_auth_service(user_service: UserRepository = Depends(get_user_service)) -> AuthService:
    return AuthService(user_service)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return await auth_service.authenticate_user(token)


async def get_social_auth_service(provider: str,
                                  user_service: UserRepository = Depends(get_user_service)) -> SocialAuthService:
    return await SocialAuthService.create(provider, user_service)
