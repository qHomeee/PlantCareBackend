from pydantic import BaseModel, Field


class PlantBase(BaseModel):
    common_name: str = Field(min_length=1, max_length=255)
    scientific_name: str = Field(min_length=1, max_length=255)

    description: str

    watering_info: str
    watering_interval_days: int = Field(ge=1, le=60)

    light_info: str
    temperature_info: str
    humidity_info: str

    soil_info: str
    fertilizing_info: str
    fertilizing_interval_days: int = Field(ge=1, le=180)

    care_info: str
    useful_info: str


class PlantCreate(PlantBase):
    pass


class PlantResponse(PlantBase):
    id: int

    model_config = {
        "from_attributes": True
    }


class PlantRecognizeResponse(PlantBase):
    plant_id: int
    confidence: float = Field(ge=0, le=1)