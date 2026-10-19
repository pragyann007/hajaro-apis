from sqlalchemy import String,Text,Time,ForeignKey,Enum as SQLEnum , Index,func,Integer,Boolean
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.core.database import Base
from datetime import time



class BusinessHours(Base):
    __tablename__="business_hours"
    __table_args__=(
        {"schema":"hajaro"}
    )
   
    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    business_id:Mapped[int] = mapped_column(ForeignKey("hajaro.businesses.id"),nullable=False)
    weekday:Mapped[int]=mapped_column(Integer,nullable=False)
    open_time:Mapped[time]=mapped_column(Time(timezone=True))
    close_time:Mapped[time]=mapped_column(Time(timezone=True))
    is_closed:Mapped[bool]=mapped_column(Boolean,default=False)
    business:Mapped["BusinessModel"]=relationship("BusinessModel",back_populates="business_hours")



