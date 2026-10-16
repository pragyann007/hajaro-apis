from sqlalchemy import Integer, DateTime, ForeignKey, Enum as SQLEnum, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from datetime import datetime
import enum

class VerificationType(str, enum.Enum):
    MANUAL_CLAIM = "manual_claim"
    DOCUMENT_SUBMISSION = "document_submission"
    PARTNER_INTEGRATION = "partner_integration"


class BusinessVerifications(Base):
    """Stores currently active or historically granted verifications for a business."""
    __tablename__ = "business_verifications"
    
    __table_args__ = (
        Index("idx_business_verification_lookup", "business_id", "verification_type"),
        {"schema": "hajaro"}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("hajaro.businesses.id", ondelete="CASCADE"), nullable=False)
    
    verification_type: Mapped[VerificationType] = mapped_column(
        SQLEnum(VerificationType, schema="hajaro"), 
        nullable=False
    )
    
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expiry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
