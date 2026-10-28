
from sqlalchemy import select,update,delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.hajaro.models.categories import CategoryModel

class CategoryRepository:
    def __init__(self,db:AsyncSession):
        self.db = db 

    
    async def getAllCategories(self):
        categories_result = await self.db.execute(select(CategoryModel).where(CategoryModel.parent_id==0,CategoryModel.is_active==True))

        categories = categories_result.scalars().all()

        return categories