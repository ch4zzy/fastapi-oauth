from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.users.routers import router as users_router
from app.auth.routers import router as auth_router

app = FastAPI()


#
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, session_cookie="session_id")
app.include_router(users_router)
app.include_router(auth_router)

