from sqlalchemy import String,Text,DateTime,ForeignKey,Enum as SQLEnum , Index,func,Integer,Boolean
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.core.database import Base

class BusinessCategories(Base):
    __tablename__="business_categories"
    __table_args__=(
        {"schema":"hajaro"}
    )
    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    business_id:Mapped[int] = mapped_column(ForeignKey("hajaro.businesses.id"),nullable=False)
    category_id:Mapped[int] = mapped_column(ForeignKey("hajaro.categories.id"),nullable=False)

    business:Mapped["BusinessModel"]=relationship("BusinessModel",back_populates="business_categories_links")

    category:Mapped["CategoryModel"]=relationship("CategoryModel",back_populates="business_categories_links")
    
    

