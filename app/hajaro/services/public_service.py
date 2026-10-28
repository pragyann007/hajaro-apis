from app.core.database import AsyncSession
from app.hajaro.repositories.category_repository import CategoryRepository

class PublicService:

    def __init__(self,db:AsyncSession):
        self.repo = CategoryRepository(db=db)

    
