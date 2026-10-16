from sqlalchemy import Integer,Boolean,DateTime,ForeignKey,Enum as SQLEnum,String,func,Float,JSON,Index
from sqlalchemy.orm import Mapped,mapped_column

from app.core.database import Base
from datetime import datetime

import enum

# 1. Define states for the submission process lifecycle
class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class BusinessSubmissions(Base):
     __tablename__="business_submissions"
     __table_args__=(
      

        {"schema":"hajaro"}
    )
     id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
     business_id:Mapped[int] = mapped_column(ForeignKey("hajaro.businesses.id",ondelete="CASCADE"),nullable=False)
     submited_data:Mapped[dict] = mapped_column(JSON,nullable=False)
     tracking_token:Mapped[str]=mapped_column(String(70),nullable=False,index=True,unique=True)
     submission_status: Mapped[SubmissionStatus] = mapped_column(SQLEnum(SubmissionStatus,schema='hajaro'),index=True,default=SubmissionStatus.PENDING, nullable=False)
     contact_name:Mapped[str] = mapped_column(String,nullable=False)
     contact_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
     created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
     reviewed_at:Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)

