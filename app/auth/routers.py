# app/auth/routers.py
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBasicCredentials

from app.auth.dependencies import security, get_auth_service, get_social_auth_service
from app.auth.forms import OAuth2EmailRequestForm
from app.auth.security import SecurityService
from app.auth.services import AuthService, SocialAuthService
from app.users.dependencies import get_user_service
from app.users.services import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
        form_data: OAuth2EmailRequestForm = Depends(),
        service: UserService = Depends(get_user_service)
):
    user = await service.get_by_email(form_data.email)
    if not user or not SecurityService.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")
    access_token = SecurityService.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "Bearer"}


@router.post("/basic-login")
async def basic_login(
        credentials: HTTPBasicCredentials = Depends(security),
        auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.authenticate_basic(credentials)
    access_token = SecurityService.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "Bearer"}


@router.get("/{provider}/login")
async def social_login_start(
        request: Request,
        social_auth: SocialAuthService = Depends(get_social_auth_service)
):
    return await social_auth.generate_auth_url(request)


@router.get("/{provider}/callback")
async def social_callback(
        request: Request,
        social_auth: SocialAuthService = Depends(get_social_auth_service)
):
    return await social_auth.handle_callback(request)
