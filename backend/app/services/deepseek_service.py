import json

from fastapi import HTTPException, status
from openai import OpenAI

from app.core.config import settings
from app.schemas.plant import PlantCreate


def build_plant_care_prompt(
    scientific_name: str,
    common_name: str | None = None,
) -> str:
    return f"""
Ты эксперт по уходу за комнатными и садовыми растениями.

Верни строго валидный JSON с рекомендациями по уходу за растением.

Растение:
- Латинское название: {scientific_name}
- Обычное название: {common_name or "не указано"}

JSON должен содержать строго следующие поля(данные у полей являются примером):
{{
  "common_name": "string",
  "scientific_name": "string",
  "description": "string",
  "watering_info": "string",
  "watering_interval_days": 7,
  "light_info": "string",
  "min_temperature_celsius": 18.0,
  "max_temperature_celsius": 26.0,
  "humidity_info": "string",
  "soil_info": "string",
  "fertilizing_info": "string",
  "fertilizing_interval_days": 30,
  "care_info": "string",
  "useful_info": "string"
}}

Требования:
- Ответ должен быть только JSON.
- Без markdown.
- Без пояснений.
- Все текстовые поля должны быть на русском языке.
- watering_interval_days должен быть целым числом от 1 до 60.
- fertilizing_interval_days должен быть целым числом от 1 до 180.
- min_temperature_celsius и max_temperature_celsius должны быть числами в градусах Цельсия.
- min_temperature_celsius — минимальная допустимая температура содержания растения.
- max_temperature_celsius — максимальная допустимая температура содержания растения.
- max_temperature_celsius должен быть больше min_temperature_celsius.
- Если для растения подходит диапазон 18–26 °C, нужно вернуть min_temperature_celsius = 18.0 и max_temperature_celsius = 26.0.
- scientific_name должен остаться латинским названием.
"""


def get_fallback_plant_care(
    scientific_name: str,
    common_name: str | None = None,
) -> PlantCreate:
    display_name = common_name or scientific_name

    return PlantCreate(
        common_name=display_name,
        scientific_name=scientific_name,
        description=(
            f"{display_name} — растение, определенное по фотографии. "
            "Точные рекомендации по уходу требуют дополнительного уточнения."
        ),
        watering_info=(
            "Поливать после подсыхания верхнего слоя почвы. "
            "Не допускать застоя воды в горшке."
        ),
        watering_interval_days=7,
        light_info=(
            "Рекомендуется яркий рассеянный свет. "
            "Следует избегать длительного воздействия прямых солнечных лучей."
        ),
        min_temperature_celsius=18.0,
        max_temperature_celsius=26.0,
        humidity_info="Рекомендуется поддерживать умеренную влажность воздуха.",
        soil_info="Подходит рыхлый грунт с хорошим дренажем.",
        fertilizing_info=(
            "Подкормка рекомендуется в период активного роста, "
            "обычно 1 раз в месяц."
        ),
        fertilizing_interval_days=30,
        care_info=(
            "Следует регулярно осматривать листья, избегать переувлажнения, "
            "пересушивания и резких перепадов температуры."
        ),
        useful_info=(
            "Перед добавлением растения в коллекцию рекомендуется проверить "
            "результат распознавания."
        ),
    )


def clean_json_content(content: str) -> str:
    content = content.strip()

    if content.startswith("```json"):
        content = content.replace("```json", "", 1).strip()

    if content.startswith("```"):
        content = content.replace("```", "", 1).strip()

    if content.endswith("```"):
        content = content[:-3].strip()

    return content


async def get_plant_care_from_deepseek(
    scientific_name: str,
    common_name: str | None = None,
) -> PlantCreate:
    client = OpenAI(
        base_url=settings.OPENROUTER_BASE_URL,
        api_key=settings.OPENROUTER_API_KEY,
    )

    try:
        response = client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты возвращаешь только валидный JSON. "
                        "Не используй markdown. Не добавляй пояснения."
                    ),
                },
                {
                    "role": "user",
                    "content": build_plant_care_prompt(
                        scientific_name=scientific_name,
                        common_name=common_name,
                    ),
                },
            ],
            temperature=0.2,
            extra_body={
                "reasoning": {
                    "enabled": True
                }
            },
        )

        content = response.choices[0].message.content

        if content is None:
            raise ValueError("OpenRouter вернул пустой content")

        content = clean_json_content(content)
        parsed = json.loads(content)

        if common_name and not parsed.get("common_name"):
            parsed["common_name"] = common_name

        parsed["scientific_name"] = scientific_name

        return PlantCreate(**parsed)

    except Exception as error:
        print("OpenRouter error:", repr(error))

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ошибка при обращении к OpenRouter API",
        )