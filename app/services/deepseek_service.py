import json
from typing import Any

from fastapi import HTTPException, status
from openai import OpenAI

from app.core.config import settings
from app.schemas.plant import PlantCreate


client = OpenAI(
    base_url=settings.OPENROUTER_BASE_URL,
    api_key=settings.OPENROUTER_API_KEY,
)


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

JSON должен содержать строго следующие поля:
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
- Без блока ```json.
- Без пояснений до или после JSON.
- Все текстовые поля должны быть на русском языке.
- Не смешивай русский и английский языки.
- common_name должен быть русским названием растения.
- scientific_name должен остаться латинским названием без автора.
- watering_interval_days должен быть целым числом от 1 до 60.
- fertilizing_interval_days должен быть целым числом от 1 до 180.
- min_temperature_celsius и max_temperature_celsius должны быть числами в градусах Цельсия.
- min_temperature_celsius — минимальная допустимая температура содержания растения.
- max_temperature_celsius — максимальная допустимая температура содержания растения.
- max_temperature_celsius должен быть больше min_temperature_celsius.
- Не добавляй лишние поля.
- Не пропускай поля.
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
    """
    Очищает ответ модели и вытаскивает JSON-объект.
    """

    content = content.strip()

    if content.startswith("```json"):
        content = content.removeprefix("```json").strip()

    if content.startswith("```JSON"):
        content = content.removeprefix("```JSON").strip()

    if content.startswith("```"):
        content = content.removeprefix("```").strip()

    if content.endswith("```"):
        content = content.removesuffix("```").strip()

    first_brace = content.find("{")
    last_brace = content.rfind("}")

    if first_brace == -1 or last_brace == -1:
        raise ValueError("В ответе OpenRouter не найден JSON-объект")

    return content[first_brace:last_brace + 1]


def validate_plant_care_dict(data: dict[str, Any]) -> dict[str, Any]:
    required_fields = [
        "common_name",
        "scientific_name",
        "description",
        "watering_info",
        "watering_interval_days",
        "light_info",
        "min_temperature_celsius",
        "max_temperature_celsius",
        "humidity_info",
        "soil_info",
        "fertilizing_info",
        "fertilizing_interval_days",
        "care_info",
        "useful_info",
    ]

    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        raise ValueError(f"AI не вернул обязательные поля: {missing_fields}")

    data["watering_interval_days"] = int(data["watering_interval_days"])
    data["fertilizing_interval_days"] = int(data["fertilizing_interval_days"])
    data["min_temperature_celsius"] = float(data["min_temperature_celsius"])
    data["max_temperature_celsius"] = float(data["max_temperature_celsius"])

    if not 1 <= data["watering_interval_days"] <= 60:
        raise ValueError("watering_interval_days должен быть от 1 до 60")

    if not 1 <= data["fertilizing_interval_days"] <= 180:
        raise ValueError("fertilizing_interval_days должен быть от 1 до 180")

    if data["max_temperature_celsius"] <= data["min_temperature_celsius"]:
        raise ValueError(
            "max_temperature_celsius должен быть больше min_temperature_celsius"
        )

    text_fields = [
        "common_name",
        "scientific_name",
        "description",
        "watering_info",
        "light_info",
        "humidity_info",
        "soil_info",
        "fertilizing_info",
        "care_info",
        "useful_info",
    ]

    for field in text_fields:
        value = data[field]

        if not isinstance(value, str):
            raise ValueError(f"{field} должен быть строкой")

        value = value.strip()

        if not value:
            raise ValueError(f"{field} не должен быть пустым")

        data[field] = value

    return data


async def get_plant_care_from_deepseek(
    scientific_name: str,
    common_name: str | None = None,
) -> PlantCreate:
    try:
        response = client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты возвращаешь только валидный JSON. "
                        "Не используй markdown. "
                        "Не добавляй пояснения. "
                        "Все текстовые значения должны быть на русском языке."
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
            temperature=0.1,
            max_tokens=1200,
        )

        content = response.choices[0].message.content

        if content is None:
            raise ValueError("OpenRouter вернул пустой content")

        print("OpenRouter raw content:")
        print(content)

        cleaned_content = clean_json_content(content)

        print("OpenRouter cleaned JSON:")
        print(cleaned_content)

        parsed = json.loads(cleaned_content)

        if common_name and not parsed.get("common_name"):
            parsed["common_name"] = common_name

        parsed["scientific_name"] = scientific_name

        parsed = validate_plant_care_dict(parsed)

        return PlantCreate(**parsed)

    except json.JSONDecodeError as error:
        print("OpenRouter JSON decode error:", repr(error))
        print("Scientific name:", scientific_name)
        print("Common name:", common_name)

        return get_fallback_plant_care(
            scientific_name=scientific_name,
            common_name=common_name,
        )

    except Exception as error:
        print("OpenRouter error:", repr(error))
        print("Scientific name:", scientific_name)
        print("Common name:", common_name)

        return get_fallback_plant_care(
            scientific_name=scientific_name,
            common_name=common_name,
        )