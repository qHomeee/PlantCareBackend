import json

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.plant import PlantCreate


def build_plant_care_prompt(
    scientific_name: str,
    common_name: str | None = None,
) -> str:
    return f"""
Ты эксперт по растениям.

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
  "temperature_info": "string",
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
- scientific_name должен остаться латинским названием.
"""


async def get_plant_care_from_deepseek(
    scientific_name: str,
    common_name: str | None = None,
) -> PlantCreate:
    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Ты возвращаешь только валидный JSON без markdown и пояснений.",
            },
            {
                "role": "user",
                "content": build_plant_care_prompt(scientific_name, common_name),
            },
        ],
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=40.0) as client:
        response = await client.post(
            settings.DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ошибка при обращении к DeepSeek API",
        )

    data = response.json()

    try:
        content = data["choices"][0]["message"]["content"].strip()

        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(content)

        if common_name and not parsed.get("common_name"):
            parsed["common_name"] = common_name

        parsed["scientific_name"] = scientific_name

        return PlantCreate(**parsed)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="DeepSeek вернул некорректный JSON",
        )