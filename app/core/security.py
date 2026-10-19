from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import settings


def create_token(payload: dict, token_type: str) -> str:
    if token_type == "access":
        ttl_minutes = settings.ACCESS_TOKEN_TTL_MINUTES
        secret_key = settings.ACCESS_TOKEN_SECRET_KEY
    elif token_type == "refresh":
        ttl_minutes = settings.REFRESH_TOKEN_TTL_MINUTES
        secret_key = settings.REFRESH_TOKEN_SECRET_KEY
    else:
        raise ValueError("Incorrect token type. Must be 'access' or 'refresh'.")

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)

    token_payload = {
        **payload,
        "exp": expires_at
    }

    return jwt.encode(
        payload=token_payload, 
        key=secret_key, 
        algorithm=settings.JWT_ALGORITHM
    )


def create_tokens(a_payload: dict, r_payload: dict) -> tuple[str, str]:
    access_token = create_token(payload=a_payload, token_type="access")
    refresh_token = create_token(payload=r_payload, token_type="refresh")
    return access_token, refresh_token
