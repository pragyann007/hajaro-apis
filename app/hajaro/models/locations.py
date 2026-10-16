from datetime import datetime
from sqlalchemy import String,Text,DateTime,ForeignKey,Enum as SQLEnum , Index,func,Integer,Boolean
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.core.database import Base
import enum 

class Locationtype(str,enum.Enum):
    PROVINCE = "province"
    DISTRICT = "district"
    MUNICIPALITY = "municipality"
    WARD = "ward"
    CITY = "city"
    LOCALITY = "locality"
    BAZAAR = "bazaar"
    CHOWK = "chowk"
    ROAD = "road"
    LANDMARK = "landmark"


class Locations(Base):
    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name_en:Mapped[str]=mapped_column(String(150),index=True,nullable=False)
    name_ne:Mapped[str]=mapped_column(String(150),index=True,nullable=False)

    slug:Mapped[str]=mapped_column(String(100),unique=True,index=True,nullable=False)
    location_type:Mapped[Locationtype]=mapped_column(SQLEnum(Locationtype), nullable=False)
    parent_id:Mapped[int]=mapped_column(Integer,nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean,default=False, nullable=False)

    
   
