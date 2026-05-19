from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.plant import PlantCreate, PlantRecognizeResponse
from app.services.deepseek_service import (
    get_fallback_plant_care,
    get_plant_care_from_deepseek,
)
from app.services.plant_service import (
    create_plant,
    get_plant_by_scientific_name,
)
from app.services.plantnet_service import recognize_plant_with_plantnet


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
        fertilizing_info=(
            "Подкармливать в период активного роста примерно один раз в месяц."
        ),
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


@router.post(
    "/recognize",
    response_model=PlantRecognizeResponse,
)
async def recognize_plant(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл должен быть изображением",
        )

    try:
        plantnet_data = await recognize_plant_with_plantnet(file, organ="leaf")
    except Exception as error:
        print("PlantNet error:", repr(error))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка при обращении к PlantNet API: {str(error)}",
        )

    results = plantnet_data.get("results", [])

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Растение не распознано",
        )

    best_result = results[0]
    confidence = float(best_result.get("score", 0))

    species = best_result.get("species", {})

    scientific_name = (
        species.get("scientificNameWithoutAuthor")
        or species.get("scientificName")
    )

    common_names = species.get("commonNames") or []
    common_name = common_names[0] if common_names else None

    if not scientific_name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Не удалось определить название растения",
        )

    plant = get_plant_by_scientific_name(db, scientific_name)

    if plant is None:
        try:
            plant_data = await get_plant_care_from_deepseek(
                scientific_name=scientific_name,
                common_name=common_name,
            )
        except Exception as error:
            print("DeepSeek fallback used:", repr(error))
            plant_data = get_fallback_plant_care(
                scientific_name=scientific_name,
                common_name=common_name,
            )

        plant = create_plant(db, plant_data)

    return {
        "plant_id": plant.id,
        "common_name": plant.common_name,
        "scientific_name": plant.scientific_name,
        "description": plant.description,
        "watering_info": plant.watering_info,
        "watering_interval_days": plant.watering_interval_days,
        "light_info": plant.light_info,
        "min_temperature_celsius": plant.min_temperature_celsius,
        "max_temperature_celsius": plant.max_temperature_celsius,
        "humidity_info": plant.humidity_info,
        "soil_info": plant.soil_info,
        "fertilizing_info": plant.fertilizing_info,
        "fertilizing_interval_days": plant.fertilizing_interval_days,
        "care_info": plant.care_info,
        "useful_info": plant.useful_info,
        "confidence": confidence,
    }