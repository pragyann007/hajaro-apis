from datetime import datetime
from sqlalchemy import String,Text,DateTime,ForeignKey,Enum as SQLEnum , Index,func,Integer,Boolean
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.core.database import Base

class CategoryModel(Base):
    __tablename__="categories"
    __table_args__=(
        {"schema":"hajaro"}
    )

    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name_en:Mapped[str]=mapped_column(String(150),index=True,nullable=False)
    name_ne:Mapped[str]=mapped_column(String(150),index=True,nullable=False)

    slug:Mapped[str]=mapped_column(String(100),unique=True,index=True,nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id:Mapped[int]=mapped_column(Integer,nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean,default=False, nullable=False)

    business_categories_links = relationship("BusinessCategories",back_populates="category",cascade="all delete-orphan")

