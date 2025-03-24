# app/auth/providers/google.py
import httpx
from fastapi import HTTPException

from app.auth.social_auth import SocialAuth
from app.core.config import settings


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
        self._access_token_url = "https://oauth2.googleapis.com/token"

    async def get_user_info(self, token: dict) -> dict:
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
