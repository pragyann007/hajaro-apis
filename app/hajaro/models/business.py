from datetime import datetime
from sqlalchemy import String,Text,DateTime,ForeignKey,Enum as SQLEnum , Index,func
from sqlalchemy.orm import Mapped,mapped_column,relationship

from geoalchemy2 import Geography
from app.core.database import Base
import enum 

class PublicationStatus(str,enum.Enum):
    draft = "draft"
    pending_review = "pending_review"
    published = "published"
    rejected = "rejected"
    suspended = "suspended"

class BusinessModel(Base):
    __tablename__="businesses"
    __table_args__=( 
        Index("idx_business_geo_point","geographic_point",postgresql_using="gist"),
        {"schema":"hajaro"}

    )

    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name:Mapped[str]=mapped_column(String(150),index=True,nullable=False)
    slug:Mapped[str]=mapped_column(String(100),unique=True,index=True,nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ownerId:Mapped[int]=mapped_column(ForeignKey("hajaro.users.id"))

    location_id:Mapped[int]=mapped_column(ForeignKey("hajaro.locations.id"),nullable=False)
    geographic_point = mapped_column(Geography(geometry_type="POINT",srid=4326),nullable=False)

    publication_status:Mapped[PublicationStatus] = mapped_column(SQLEnum(PublicationStatus),default=PublicationStatus.pending_review,nullable=False)

    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    location = relationship("LocationModel",back_populates="business")

    owner = relationship("UsersModel",back_populates="businesses")

    business_categories_links = relationship("BusinessCategories",back_populates="category",cascade="all, delete-orphan")
    business_claims = relationship("BusinessClaims",back_populates="business",cascade="all")

    business_hours= relationship("BusinessHours",back_populates="business",cascade="all")

    business_medias= relationship("BusinessMedia",back_populates="business",cascade="all")
    business_submissions=relationship("BusinessSubmissions",back_populates="business",cascade="all")

    business_verifications=relationship("BusinessVerifications",back_populates="business",cascade="all")
    catalog_items=relationship("CatalogItems",back_populates="business",cascade="all")
    business_offers=relationship("Offers",back_populates="business",cascade="all")

    business_reviews=relationship("Offers",back_populates="business",cascade="all")
    verifications_requests=relationship("VerificationRequests",back_populates="business",cascade="all")
