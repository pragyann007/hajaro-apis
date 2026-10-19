from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.hajaro.schemas.user import UserRegister, UserResponse,UserLogin
from app.hajaro.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register")
async def register(
    paylaod:UserRegister,
    db:AsyncSession
):
    auth_service=AuthService(db)
    return await auth_service.register_user(paylaod)


@router.post("/login")
async def login(
    payload:UserLogin,
    db:AsyncSession=Depends(get_db)
):
    auth_service=AuthService(db)

    return await auth_service.login_user(payload)