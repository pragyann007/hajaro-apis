from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from datetime import datetime
import enum

class RequestStatus(str, enum.Enum):
    NOT_REQUESTED = "Not requested"
    PENDING = "Pending"
    UNDER_REVIEW = "Under review"
    ADDITIONAL_INFO_REQUIRED = "Additional info required"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    EXPIRED = "Expired"
    REVOKED = "Revoked"

class VerificationType(str, enum.Enum):
    MANUAL_CLAIM = "manual_claim"
    DOCUMENT_SUBMISSION = "document_submission"
    PARTNER_INTEGRATION = "partner_integration"


class VerificationRequests(Base):
    """Tracks active vetting and application review cycles for business verification badges."""
    __tablename__ = "verification_requests"
    
    __table_args__ = (
        # Performance index for looking up all historical requests submitted by a business
        Index("idx_business_requests_history", "business_id", "status"),
        {"schema": "hajaro"}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("hajaro.businesses.id", ondelete="CASCADE"), nullable=False)
    
    # Reusing the verification type structure
    verification_type: Mapped[VerificationType] = mapped_column(
        SQLEnum(VerificationType, schema="hajaro"), 
        nullable=False
    )
    
    # Leverages your exact requested enum status mapping string names
    status: Mapped[RequestStatus] = mapped_column(
        SQLEnum(RequestStatus, schema="hajaro"), 
        default=RequestStatus.PENDING, 
        index=True, 
        nullable=False
    )
    
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Tracks which specific staff member or automated agent is auditing the application
    reviewer_reference: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    
    # Stores URLs or pointers to documents, trade licenses, or IDs provided by the business owner
    evidence_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    expiry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)

    business:Mapped["BusinessModel"]=relationship("BusinessModel",back_populates="verifications_requests")
