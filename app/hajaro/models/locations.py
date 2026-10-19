from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class Locationtype(str, enum.Enum):
    PROVINCE = "province"
    DISTRICT = "district"
    MUNICIPALITY = "municipality"
    WARD = "ward"
    CITY = "city"
    LOCALITY = "locality"
    BAZAAR = "bazaar"
    CHOWK = "chowk"
    ROAD = "road"
    LANDMARK = "landmark"


class Locations(Base):
    __tablename__ = "locations"
    __table_args__ = ({"schema": "hajaro"},)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_en: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    name_ne: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    location_type: Mapped[Locationtype] = mapped_column(SQLEnum(Locationtype), nullable=False)
    # Nullable so root nodes (e.g. province) can exist without a parent
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("hajaro.locations.id", ondelete="RESTRICT"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    parent: Mapped["Locations | None"] = relationship(
        "Locations",
        remote_side=[id],
        back_populates="children",
        foreign_keys=[parent_id],
    )
    children: Mapped[list["Locations"]] = relationship(
        "Locations",
        back_populates="parent",
        foreign_keys=[parent_id],
    )
    businesses: Mapped[list["BusinessModel"]] = relationship(
        "BusinessModel", back_populates="location"
    )
