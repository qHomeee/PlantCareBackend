import httpx
from fastapi import UploadFile

from app.core.config import settings


async def recognize_plant_with_plantnet(
    file: UploadFile,
    organ: str = "leaf",
) -> dict:
    image_bytes = await file.read()

    files = {
        "images": (
            file.filename or "plant.jpg",
            image_bytes,
            file.content_type or "image/jpeg",
        )
    }

    data = {
        "organs": organ,
    }

    params = {
        "api-key": settings.PLANTNET_API_KEY,
        "include-related-images": "false",
        "lang": "ru",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            settings.PLANTNET_API_URL,
            params=params,
            data=data,
            files=files,
        )

    print("PlantNet status:", response.status_code)
    print("PlantNet response:", response.text)

    response.raise_for_status()

    return response.json()