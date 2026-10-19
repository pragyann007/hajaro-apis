from sqlalchemy import String,Text,DateTime,ForeignKey,Enum as SQLEnum , Index,func,Integer,Boolean
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.core.database import Base
from datetime import datetime
import enum 

class ItemType(str,enum.Enum):
    PRODUCTS="products"
    SERVICE="service"


class CatalogItems(Base):
    __tablename__="catalog_items"
    __table_args__=(
        Index(
            "uq_business_catalog_slug",
            "business_id",
            "slug",
            unique=True
        ),
        {"schema":"hajaro"}
    )

   
    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    business_id:Mapped[int] = mapped_column(ForeignKey("hajaro.businesses.id",ondelete="CASCADE"),nullable=False)
    category:Mapped[int] = mapped_column(ForeignKey("hajaro.categories.id",ondelete="RESTRICT"),nullable=False)

    name:Mapped[str]=mapped_column(String(150),index=True,nullable=False)
    slug:Mapped[str]=mapped_column(String(100),unique=True,index=True,nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    brand: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit:Mapped[int]=mapped_column(Integer,nullable=False,default=1)
    item_type:Mapped[ItemType]=mapped_column(SQLEnum(ItemType,schema="hajaro"),nullable=False,default=ItemType.PRODUCTS)
    is_published:Mapped[bool]=mapped_column(Boolean,default=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    business:Mapped["BusinessModel"]=relationship("BusinessModel",back_populates="catalog_items")







