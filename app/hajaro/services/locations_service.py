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
    

    async def get_loaction_trees(self):
        locations =await  self.repo.get_all_active_locations()

        node_map = {}

        for loc in locations:
            node_map[loc.id]={
                "id":loc.slug,
                "slug":loc.slug,
                "type":loc.location_type,
                "parent_id":loc.parent_id,
                "name_en":loc.name_en,
                "name_ne":loc.name_ne,
                "status":"active" if loc.is_active else "inactive",
                "business_count":0,
                "children":[]
            }
        tree = []

        for loc in locations:
            node = node_map[loc.id]
            if loc.parent_id is None:
                tree.append(node)
            else:
                if loc.parent_id in node_map:
                    node_map[loc.parent_id]["children"].append(node)


        return tree








