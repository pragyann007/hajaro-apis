from sqlalchemy import String,Text,DateTime,ForeignKey,Enum as SQLEnum , Index,func,Boolean,CheckConstraint
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.core.database import Base
from datetime import datetime



class Offers(Base):
    __tablename__="offers"
    __table_args__=(
        CheckConstraint(
            "close_at > start_at",
            name="check_offer_date_range"
        ),
        
       
        {"schema":"hajaro"}
    )


   
    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    business_id:Mapped[int] = mapped_column(ForeignKey("hajaro.businesses.id",ondelete="CASCADE"),nullable=False)

    title:Mapped[str]=mapped_column(String(150),nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    terms: Mapped[str] = mapped_column(Text, nullable=False)

    start_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),index=True,nullable=False)
    close_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),index=True,nullable=True)
    
    is_published:Mapped[bool]=mapped_column(Boolean,default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    






