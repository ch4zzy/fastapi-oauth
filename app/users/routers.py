# app/users/routers.py
from fastapi import APIRouter, Depends
from pydantic import EmailStr


from app.auth.dependencies import get_current_user
from app.core.dependencies import get_user_service
from app.users.models import User
from app.users.schemas import UserResponse, UserCreate
from app.users.services import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    created_user = await service.create_user(user.email, user.password)
    return created_user

@router.get(
    "/profile",
    response_model=UserResponse,
    status_code=200,
    dependencies=[Depends(get_current_user)]
)
async def get_profile(
        user: User = Depends(get_current_user),
):
    return user

@router.get("/{user_email}", response_model=UserResponse, status_code=200)
async def get_user(user_email: EmailStr, service: UserService = Depends(get_user_service)):
    user = await service.get_by_email(user_email)
    return user

