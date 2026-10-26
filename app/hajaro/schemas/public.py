from pydantic import BaseModel
from typing import List
class HomeResposne(BaseModel):
    featured_organisation:List[dict]
    popular_locations:List[dict]
    featured_businesses:List[dict]
    active_offers_count:List[dict]


