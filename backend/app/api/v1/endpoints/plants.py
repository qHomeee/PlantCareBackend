from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.plant import PlantCreate, PlantRecognizeResponse
from app.services.plant_service import create_plant, get_plant_by_scientific_name


router = APIRouter()


@router.post(
    "/mock-recognize",
    response_model=PlantRecognizeResponse,
)
def mock_recognize(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plant_data = PlantCreate(
        common_name="Монстера",
        scientific_name="Monstera deliciosa",
        description="Популярное комнатное растение с крупными декоративными листьями.",

        watering_info="Поливать после подсыхания верхнего слоя почвы.",
        watering_interval_days=7,

        light_info="Предпочитает яркий рассеянный свет.",
        temperature_info="Оптимальная температура содержания 18–26 °C.",
        humidity_info="Предпочитает умеренную или повышенную влажность воздуха.",

        soil_info="Подходит рыхлый питательный грунт с хорошим дренажем.",
        fertilizing_info="Подкармливать в период активного роста примерно один раз в месяц.",
        fertilizing_interval_days=30,

        care_info="Избегать переувлажнения почвы и прямых солнечных лучей.",
        useful_info="Хорошо подходит для декоративного озеленения помещений.",
    )

    plant = get_plant_by_scientific_name(db, plant_data.scientific_name)

    if plant is None:
        plant = create_plant(db, plant_data)

    return {
        **plant_data.model_dump(),
        "plant_id": plant.id,
        "confidence": 0.92,
    }