# app/main.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import app.hajaro.models  # noqa: F401 — register all ORM models with SQLAlchemy
from app.hajaro.api.auth import router as auth_router
from app.hajaro.api.public.router import public_router

from app.exceptions import PasswordMismatchException, EmailAlreadyExistsException,UserNotFoundException

app = FastAPI(title="Hajaro Backend API")

# 1. Register Global Exception Handlers
@app.exception_handler(PasswordMismatchException)
async def password_mismatch_handler(request: Request, exc: PasswordMismatchException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )

@app.exception_handler(UserNotFoundException)
async def user_not_found_handler(request: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )

@app.exception_handler(EmailAlreadyExistsException)
async def email_exists_handler(request: Request, exc: EmailAlreadyExistsException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )

# 2. Include the Auth Router
app.include_router(auth_router)
app.include_router(public_router)
