# app/auth/providers/github.py
import httpx
from fastapi import HTTPException

from app.auth.social_auth import SocialAuth
from app.core.config import settings


class GithubAuth(SocialAuth):
    async def configure_oauth(self):
        self._client_id = settings.GITHUB_CLIENT_ID
        self._client_secret = settings.GITHUB_CLIENT_SECRET
        self._access_token_url = "https://github.com/login/oauth/access_token"

        self.oauth.register(
            name="github",
            client_id=self._client_id,
            client_secret=self._client_secret,
            authorize_url="https://github.com/login/oauth/authorize",
            access_token_url=self._access_token_url,
            userinfo_endpoint="https://api.github.com/user",
            client_kwargs={"scope": "user:email"}
        )

    async def get_user_info(self, token: dict) -> dict:
        access_token = token.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access_token in token response")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()
