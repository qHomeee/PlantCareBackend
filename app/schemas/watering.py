from datetime import date, datetime

from pydantic import BaseModel, Field


class WateringEventResponse(BaseModel):
    id: int
    user_plant_id: int

    scheduled_date: date
    completed_at: datetime | None

    status: str
    note: str | None

    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class WateringEventUpdate(BaseModel):
    note: str | None = Field(default=None, max_length=1000)


class WateringEventWithPlantResponse(BaseModel):
    id: int
    user_plant_id: int

    scheduled_date: date
    completed_at: datetime | None

    status: str
    note: str | None

    created_at: datetime

    plant_common_name: str
    plant_scientific_name: str
    custom_name: str | None
    image_url: str | None

    model_config = {
        "from_attributes": True
    }