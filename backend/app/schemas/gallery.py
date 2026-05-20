from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.plant import PlantResponse


class UserPlantCreate(BaseModel):
    plant_id: int
    custom_name: str | None = Field(default=None, max_length=255)
    image_url: str | None = Field(default=None, max_length=500)


class UserPlantUpdate(BaseModel):
    custom_name: str | None = Field(default=None, max_length=255)
    image_url: str | None = Field(default=None, max_length=500)
    last_watered_at: date | None = None
    next_watering_date: date | None = None


class UserPlantResponse(BaseModel):
    id: int
    user_id: int
    plant_id: int

    custom_name: str | None
    image_url: str | None

    last_watered_at: date | None
    next_watering_date: date | None

    added_at: datetime
    plant: PlantResponse

    model_config = {
        "from_attributes": True
    }