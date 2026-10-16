from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from datetime import datetime
import enum

class VerificationEventType(str, enum.Enum):
    STATUS_CHANGED = "status_changed"
    REVOKED = "revoked"
    EXPIRED = "expired"

class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVOKED = "revoked"


class VerificationEvents(Base):
    """The Audit Trail: Tracks every action taken on an application for maximum transparency."""
    __tablename__ = "verification_events"
    
    __table_args__ = (
        Index("idx_verification_request_events", "verification_request_id"),
        {"schema": "hajaro"}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Points to your business_claims table file
    verification_request_id: Mapped[int] = mapped_column(
        ForeignKey("hajaro.business_claims.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    event_type: Mapped[VerificationEventType] = mapped_column(
        SQLEnum(VerificationEventType, schema="hajaro"), 
        nullable=False
    )
    
    previous_status: Mapped[VerificationStatus | None] = mapped_column(
        SQLEnum(VerificationStatus, schema="hajaro"), 
        nullable=True
    )
    new_status: Mapped[VerificationStatus] = mapped_column(
        SQLEnum(VerificationStatus, schema="hajaro"), 
        nullable=False
    )
    
    actor_reference: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
