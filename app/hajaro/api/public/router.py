from fastapi import APIRouter,Depends
from app.core.database import get_db 
from app.core.database import AsyncSession
from app.hajaro.schemas.public import HomeResposne
from sqlalchemy import select,func
from app.hajaro.models.categories import CategoryModel
# from app.hajaro.api.public import ""

public_router = APIRouter(
    prefix="/public",
    tags=["Public"]
)

@public_router.get("/categories")
async def categories(db:AsyncSession=Depends(get_db)):
    
    categories_result = await db.execute(select(CategoryModel).where(CategoryModel.parent_id == 0 ,CategoryModel.is_active == True))

    categories = categories_result.scalars().all()

    return categories 





