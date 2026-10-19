from app.core.database import Base
from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime


class UsersModel(Base):
    __tablename__ = "users"

    __table_args__=(
        {"schema":"hajaro"}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_url: Mapped[str | None] = mapped_column(String(2083), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    businesses: Mapped[list["BusinessModel"]] = relationship(
        "BusinessModel", back_populates="owner", lazy="selectin"
    )
