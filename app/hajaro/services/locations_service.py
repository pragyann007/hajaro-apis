from app.hajaro.repositories.locations_repository import LocationRepository
from app.core.database import AsyncSession
from app.exceptions import LocationNotFoundException

class LocationService:

    def __init__(self,db:AsyncSession):
        self.repo = LocationRepository(db=db)
    
    async def getLocalities(self,city:str | None = None):

        if city and city.lower()!="nepal":
            city_info = await self.repo.get_by_slug(slug=city)

            if not city_info:
              raise LocationNotFoundException(f"{city} city  not found ")
            
            city_id = city_info.id 
        else:
            city_id=None

    
        
        locations = await self.repo.get_children_locations(parent_id=city_id)

        return [ loc.name_en for loc in locations]
    






