from datetime import date, datetime

from pydantic import BaseModel, Field


class WateringEventResponse(BaseModel):
    id: int
    user_plant_id: int
    scheduled_date: date
    completed_at: datetime | None
    status: str
    note: str | None

    model_config = {
        "from_attributes": True
    }


class WateringEventUpdate(BaseModel):
    status: str = Field(pattern="^(planned|completed|missed)$")
    note: str | None = None