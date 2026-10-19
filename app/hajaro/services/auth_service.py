
from sqlalchemy.ext.asyncio import AsyncSession
from app.hajaro.repositories.user_repository import UserRepository
from app.hajaro.schemas.user import UserRegister,UserLogin
from fastapi import HTTPException
from pwdlib import PasswordHash
from app.exceptions import PasswordMismatchException,UserNotFoundException,EmailAlreadyExistsException


password_hash = PasswordHash.recommended()

class AuthService:

    def __init__(self,db:AsyncSession):
        self.repo = UserRepository(db=db)

    async def register_user(self,user:UserRegister):

        # Check of user exists

        user_exists = await self.repo.get_by_email(user.email)

        if(user_exists):
            raise EmailAlreadyExistsException("This email address is already registered")
        


        # hash password
        hashed_password = password_hash.hash(user.password)

        # register user

        return await self.repo.create(user,hashed_password)


    async def login_user(self,user:UserLogin):

        user_exists = await self.repo.get_by_email(user.email)

        if not user_exists:
            raise UserNotFoundException("No user found with this email")
        
        verify_password = password_hash.verify(user.password,user_exists.password)

        if not verify_password :
            raise PasswordMismatchException("Password didnt match")
        
        return user_exists


