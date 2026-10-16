from sqlalchemy import Integer,Boolean,DateTime,ForeignKey,Text,func,Float,CheckConstraint,Index
from sqlalchemy.orm import Mapped,mapped_column

from app.core.database import Base
from datetime import datetime
class Reviews(Base):
    __tablename__="reviews"
    __table_args__=(
        CheckConstraint("rating >=1.0 AND rating <= 5.0 ",name="check_rating_range"),
        Index("idx_business_review_summary","business_id","rating"),

        {"schema":"hajaro"}
    )
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    business_id:Mapped[int] = mapped_column(ForeignKey("hajaro.businesses.id",ondelete="CASCADE"),nullable=False)
    rating:Mapped[float]= mapped_column(Float,nullable=False,index=True,default=5)
    comment:Mapped[str|None]=mapped_column(Text,nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
