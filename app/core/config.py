# app/core/config.py.py
import os

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    load_dotenv()
    BASE_URL: str = "http://localhost:8000"
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"), 30)
    DATABASE_URL = 'postgresql+asyncpg://postgres:postgres@172.23.76.185/postgres'
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
