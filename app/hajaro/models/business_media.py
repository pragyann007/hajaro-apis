from sqlalchemy import String,Text,Time,ForeignKey,Enum as SQLEnum , Index,func,Integer,Boolean
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.core.database import Base
import enum 

class MediaType(str,enum.Enum):
    IMAGE="image"
    VIDEO="video"
    PDF="pdf"




class BusinessMedia(Base):
    __tablename__="business_media"
    __table_args__=(
        Index(
            "uq_business_cover_image",
            "business_id",
            unique=True,
            postgresql_where=(Boolean("is_cover")==True)

        ),
        {"schema":"hajaro"}
    )
    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    business_id:Mapped[int] = mapped_column(ForeignKey("hajaro.businesses.id",ondelete="CASCADE"),nullable=False)
    file_url:Mapped[str]=mapped_column(String(2083),nullable=False)
    media_type:Mapped[MediaType]=mapped_column(SQLEnum(MediaType,schema="hajaro"),nullable=False)
    alt_text:Mapped[str|None]=mapped_column(String,nullable=True)
    is_cover:Mapped[bool]=mapped_column(Boolean,default=False)
    display_order:Mapped[int]=mapped_column(Integer,nullable=False)



