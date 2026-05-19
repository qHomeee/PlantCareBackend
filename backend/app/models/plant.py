from datetime import datetime

from sqlalchemy.orm import Mapped,mapped_column
from app.core.database import Base
from sqlalchemy import DateTime, Integer, String, Text,Float

class Plant(Base):
    __tablename__= "plants"


    id: Mapped[int] = mapped_column(Integer,primary_key=True,index=True)

    common_name: Mapped[str] = mapped_column(String(255),nullable=False)
    scientific_name: Mapped[str] = mapped_column(String(255),nullable=False)
   
    description: Mapped[str] = mapped_column(Text, nullable=False)

    watering_info: Mapped[str] = mapped_column(Text, nullable=False)
    watering_interval_days: Mapped[int] = mapped_column(Integer, nullable=False, default=7)

    light_info: Mapped[str] = mapped_column(Text, nullable=False)
    min_temperature_celsius: Mapped[float] = mapped_column(
       Float,
       nullable=False,
       default=18.0,
    )
    max_temperature_celsius: Mapped[float] = mapped_column(
       Float,
       nullable=False,
       default=26.0,
    )
    humidity_info: Mapped[str] = mapped_column(Text, nullable=False)

    soil_info: Mapped[str] = mapped_column(Text, nullable=False)
    fertilizing_info: Mapped[str] = mapped_column(Text, nullable=False)
    fertilizing_interval_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)

    care_info: Mapped[str] = mapped_column(Text, nullable=False)
    useful_info: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )