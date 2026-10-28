# app/main.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import app.hajaro.models  # noqa: F401 — register all ORM models with SQLAlchemy
from app.hajaro.api.auth import router as auth_router
from app.hajaro.api.public.router import public_router

from app.exceptions import ServiceException

app = FastAPI(title="Hajaro Backend API")

@app.exception_handler(ServiceException)
async def service_exception_handler(request: Request, exc: ServiceException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


app.include_router(auth_router)
app.include_router(public_router)
