
from sqlalchemy import select,update,delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.hajaro.models.locations import Locations

class LocationRepository:
    def __init__(self,db:AsyncSession):
        self.db = db 

    async def get_by_slug(self,slug:str):
        results= await self.db.execute(select(Locations).where(Locations.slug==slug.lower()))
     
        r =   results.scalar_one_or_none()
        return r 

    async def get_children_locations(self,parent_id:str):

        if parent_id:
            query=select(Locations).where(Locations.parent_id == parent_id)

        else:
            query = select(Locations).where(Locations.is_active==True)



        results = await self.db.execute(query)

  
        return results.scalars().all()
    
    async def get_all_active_locations(self):

        query = select(Locations).where(Locations.is_active==True)
        result =await  self.db.execute(query)

        return result.scalars().all()

        



