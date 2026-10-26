from fastapi import APIRouter, Depends, status,Response,Header,Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.hajaro.schemas.user import UserRegister, UserResponse,UserLogin
from app.hajaro.services.auth_service import AuthService
from app.core.config import settings
from typing import Annotated


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register")
async def register(
    paylaod:UserRegister,
    db:AsyncSession=Depends(get_db),
):
    auth_service=AuthService(db)
    return await auth_service.register_user(paylaod)


@router.post("/login",status_code=status.HTTP_200_OK)
async def login(
    payload:UserLogin,
    response:Response,
    db:AsyncSession=Depends(get_db),
):
    auth_service=AuthService(db)

    results =await auth_service.login_user(payload)

    access_token, refresh_token = results["tokens"]
    refresh_token_expiry_seconds = settings.REFRESH_TOKEN_TTL_MINUTES * 60
    response.set_cookie(
        key="refresh",
        value=refresh_token,
        httponly=True,               
        secure=settings.ENVIRONMENT=="production",                 
        samesite="lax",              # Protects against CSRF attacks
        max_age=refresh_token_expiry_seconds 

    )

    return {"access_token":access_token}


@router.post("/refresh")
async def rotate_token(request:Request,response:Response,db:AsyncSession=Depends(get_db)):
    refresh_token_old = request.cookies.get("refresh")
    auth_service= AuthService(db)

    access_token, refresh_token =await auth_service.refresh(refresh_token_old)
    refresh_token_expiry_seconds = settings.REFRESH_TOKEN_TTL_MINUTES * 60
    response.set_cookie(
        key="refresh",
        value=refresh_token,
        httponly=True,               
        secure=settings.ENVIRONMENT=="production",                 
        samesite="lax",              # Protects against CSRF attacks
        max_age=refresh_token_expiry_seconds 

    )


    
    return {"access_token":access_token}  

@router.post("/logout")
async def logout(request:Request,db:AsyncSession = Depends(get_db)):
        # Code

    refresh_token = request.cookies.get("refresh")
    auth_service = await AuthService(db)
    auth_service.logout(refresh_token=refresh_token)
    return {"message":"Logged out succesfully"}
