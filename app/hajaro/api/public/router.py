from fastapi import APIRouter,Depends
from app.core.database import get_db 
from app.core.database import AsyncSession
from app.hajaro.schemas.public import HomeResposne
from sqlalchemy import select,func
from app.hajaro.models.categories import CategoryModel

from app.hajaro.services.category_service import CategoryService

from app.hajaro.services.locations_service import LocationService

# from app.hajaro.api.public import ""

public_router = APIRouter(
    prefix="/public",
    tags=["Public"]
)

@public_router.get("/categories")
async def categories(db:AsyncSession=Depends(get_db)):
    category_service =  CategoryService(db=db)

    return await category_service.get()

@public_router.get("/locations/")
async def locations(city:str|None = None,db:AsyncSession=Depends(get_db)):
    location_service = LocationService(db=db)

    return await location_service.getLocalities(city=city)
    
    
  






