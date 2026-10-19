import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.hajaro.repositories.user_repository import UserRepository
from app.hajaro.schemas.user import UserRegister, UserLogin
from fastapi import HTTPException
from pwdlib import PasswordHash
from app.exceptions import PasswordMismatchException, UserNotFoundException, EmailAlreadyExistsException
from app.core.security import create_tokens, hash_password, verify_password
from app.hajaro.utils.redis_key import refresh_token_redis_key

from app.core.redis import r as redis

password_hash = PasswordHash.recommended()

class AuthService:

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db=db)

    async def register_user(self, user: UserRegister):
        # Check if user exists
        user_exists = await self.repo.get_by_email(user.email)

        if user_exists:
            raise EmailAlreadyExistsException("This email address is already registered")

        # hash password
        hashed_password = hash_password(user.password)

        # register user
        return await self.repo.create(user, hashed_password)


    async def login_user(self, user: UserLogin):
        user_exists = await self.repo.get_by_email(user.email)

        if not user_exists:
            raise UserNotFoundException("No user found with this email")
        
        password_verify = verify_password(user.password, user_exists.password)

        if not password_verify:
            raise PasswordMismatchException("Password didnt match")
        
        business_ids = [b.id for b in user_exists.businesses]
        
        a_payload = {
            "sub": user_exists.id,
            "businesses": business_ids,
            "email": user.email
        }

        r_payload = {
            "sub": user_exists.id,
        }
        tokens = create_tokens(a_payload=a_payload, r_payload=r_payload)

        key = refresh_token_redis_key(tokens[1])

        # FIX: Dictionary converted to String before saving to Redis
        redis_value = json.dumps({
            "userId": user_exists.id,
            "businesses": business_ids,
            "email": user_exists.email
        })
        redis.set(key, redis_value)

        return {"tokens": tokens}

    async def refresh(self, refresh_token: str): # FIX: Added 'self' and fixed typo in argument name
        key = refresh_token_redis_key(refresh_token)

        raw_token_data = redis.get(key)

        if not raw_token_data:
            raise HTTPException(status_code=401, detail="Invalid refresh token") # FIX: Standardized exception to HTTPException
        
        # FIX: String parsed back into a Python Dictionary
        findToken = json.loads(raw_token_data)
        
        r_payload = {
            "sub": findToken["userId"],
            "email": findToken["email"]
        }

        a_payload = {
            **r_payload,
            "businesses": findToken["businesses"] # FIX: Extracted from 'findToken', not the string 'key'
        }

        # Delete the old token immediately
        redis.delete(key)

        tokens = create_tokens(r_payload=r_payload, a_payload=a_payload)

        new_key = refresh_token_redis_key(tokens[1])

        # FIX: Dictionary converted to String for the new refresh token session
        new_redis_value = json.dumps({
            **a_payload,
            "userId": r_payload["sub"]
        })
        redis.set(new_key, new_redis_value)

        return tokens

    async def logout(self, refresh_token: str):
        """
        Invalidates the refresh token by removing it directly from Redis.
        """
        key = refresh_token_redis_key(refresh_token)
        redis.delete(key)
        return {"message": "Successfully logged out"}
