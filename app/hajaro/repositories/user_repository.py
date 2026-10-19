
from sqlalchemy import select,update,delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.hajaro.models.users import UsersModel
from app.hajaro.schemas.user import UserRegister

class UserRepository:
    def __init__(self,db:AsyncSession):
        self.db = db 
    
    async def get_by_email(self,email:str)->UsersModel | None :
        query = select(UsersModel).where(UsersModel.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    

    async def create(self,users:UserRegister,hashed_password:str)->UsersModel:
        db_user = UsersModel(
            name=users.name,
            email=users.email,
            password=hashed_password
          )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)

        return db_user
