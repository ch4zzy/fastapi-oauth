# app/auth/dependencies.py
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials
from app.auth.services import AuthService
from app.core.dependencies import get_user_service
from app.repositories.user import UserRepository
from app.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
security = HTTPBasic()


async def get_auth_service(service: UserRepository = Depends(get_user_service)) -> AuthService:
    return AuthService(service)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return await auth_service.authenticate_user(token)


async def get_basic_auth_user(
    credentials: HTTPBasicCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return await auth_service.authenticate_basic(credentials)
