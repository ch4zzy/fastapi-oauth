# app/auth/routers.py
import logging
import secrets

import httpx
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBasicCredentials
from starlette.responses import JSONResponse

from app.auth.dependencies import AuthService, get_auth_service, security
from app.auth.security import SecurityService
from app.auth.services import SocialAuthService
from app.auth.social_auth import SocialAuth, SocialAuthFactory
from app.core.config import settings
from app.core.dependencies import get_user_service
from app.auth.forms import OAuth2EmailRequestForm

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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
"""
@router.get("/{provider}/login")
async def social_login_start(
    request: Request,
    service: SocialAuthService = Depends(SocialAuthService.create)
):
    auth_url = await service.generate_auth_url(request)
    return JSONResponse(auth_url)

@router.get("/{provider}/callback")
async def social_callback(
    request: Request,
    service: SocialAuthService = Depends(SocialAuthService.create)
):
    return await service.handle_callback(request)

"""
@router.get("/{provider}/login")
async def social_login_start(
        provider: str,
        request: Request,
        auth_service: SocialAuth = Depends(SocialAuthFactory.get_social_auth)
):
    redirect_uri = f"{settings.BASE_URL}/auth/{provider}/callback"
    state = secrets.token_urlsafe(16)
    auth_url_data = await auth_service.client.create_authorization_url(
        redirect_uri=redirect_uri,
        state=state
    )
    request.session[f"oauth_state_{provider}"] = state
    logger.info(f"Generated state: {state}")
    logger.info(f"Session before: {request.session}")
    return JSONResponse({"url": auth_url_data["url"]})


@router.get("/{provider}/callback")
async def social_callback(
        provider: str,
        request: Request,
        auth_service: SocialAuth = Depends(SocialAuthFactory.get_social_auth)
):
    logger.info(f"Callback query params: {request.query_params}")
    logger.info(f"Session before: {request.session}")

    session_state = request.session.get(f"oauth_state_{provider}")
    query_state = request.query_params.get("state")

    if not session_state or session_state != query_state:
        logger.error("State mismatch detected")
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": f"{settings.BASE_URL}/auth/{provider}/callback",
                    "grant_type": "authorization_code"
                }
            )
            response.raise_for_status()
            token = response.json()
            logger.info(f"Received token: {token}")

            user = await auth_service.authenticate_user(token)
            access_token = SecurityService.create_access_token(data={"sub": user.email})
            request.session.pop(f"oauth_state_{provider}", None)
            return {"access_token": access_token, "token_type": "Bearer"}
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during token request: {e.response.text}")
        raise HTTPException(status_code=400, detail=f"Token request failed: {e.response.text}")
    except Exception as e:
        logger.error(f"Error during authentication: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")
