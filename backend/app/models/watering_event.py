from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class WateringEvent(Base):
    __tablename__ = "watering_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_plant_id: Mapped[int] = mapped_column(
        ForeignKey("user_plants.id", ondelete="CASCADE"),
        nullable=False,
    )

    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="planned")
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )

    user_plant = relationship("UserPlant")