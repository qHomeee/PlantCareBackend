from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserPlant(Base):
    __tablename__ = "user_plants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    plant_id: Mapped[int] = mapped_column(
        ForeignKey("plants.id", ondelete="CASCADE"),
        nullable=False,
    )

    custom_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    last_watered_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_watering_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    added_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )

    plant = relationship("Plant")

    watering_events = relationship(
        "WateringEvent",
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="user_plant",
    )