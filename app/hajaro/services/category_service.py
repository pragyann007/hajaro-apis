from app.core.database import AsyncSession
from app.hajaro.repositories.category_repository import CategoryRepository

class CategoryService:

    def __init__(self,db:AsyncSession):
        self.repo = CategoryRepository(db=db)

    async def get(self):
        categories = await self.repo.getAllCategories()

        return categories
    
