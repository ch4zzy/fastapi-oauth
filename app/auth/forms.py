from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm


class OAuth2EmailRequestForm(OAuth2PasswordRequestForm):
    username: str = Form(..., alias="email")

    @property
    def email(self) -> str:
        return self.username
