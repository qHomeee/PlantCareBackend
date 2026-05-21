from pydantic import BaseModel, Field, model_validator


class PlantBase(BaseModel):
    common_name: str = Field(min_length=1, max_length=255)
    scientific_name: str = Field(min_length=1, max_length=255)

    description: str

    watering_info: str
    watering_interval_days: int = Field(ge=1, le=60)

    light_info: str

    min_temperature_celsius: float = Field(ge=-10, le=60)
    max_temperature_celsius: float = Field(ge=-10, le=60)

    humidity_info: str

    soil_info: str

    fertilizing_info: str
    fertilizing_interval_days: int = Field(ge=1, le=180)

    care_info: str
    useful_info: str

    @model_validator(mode="after")
    def validate_temperature_range(self):
        if self.max_temperature_celsius <= self.min_temperature_celsius:
            raise ValueError(
                "max_temperature_celsius должен быть больше min_temperature_celsius"
            )
        return self


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
    image_url: str | None = None