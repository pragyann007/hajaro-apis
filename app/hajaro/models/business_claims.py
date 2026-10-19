from sqlalchemy import Integer,Boolean,DateTime,ForeignKey,Enum as SQLEnum,String,func,Float,JSON,Index
from sqlalchemy.orm import Mapped,mapped_column,relationship

from app.core.database import Base
from datetime import datetime

import enum

# 1. Define states for the submission process lifecycle
class Status(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class BusinessClaims(Base):
     __tablename__="business_claims"
     __table_args__=(
          Index(
            "uq_one_pending_claim_per_business",  
            "business_id",
             unique=True,
             postgresql_where="status = pending"
          ),
      

        {"schema":"hajaro"}
    )
     id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
     business_id:Mapped[int] = mapped_column(ForeignKey("hajaro.businesses.id",ondelete="CASCADE"),nullable=False)

     applicant_reference:Mapped[str]=mapped_column(String(255),nullable=False)
     status: Mapped[Status] = mapped_column(SQLEnum(Status,schema='hajaro'),index=True,default=Status.PENDING, nullable=False)
     
     submitted_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
     reviewed_at:Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)

     business:Mapped["BusinessModel"]=relationship("BusinessModel",back_populates="business_claims")

