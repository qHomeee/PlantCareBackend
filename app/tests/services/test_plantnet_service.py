import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.plantnet_service import recognize_plant_with_plantnet


@pytest.mark.asyncio
async def test_recognize_plant_with_plantnet_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"results": []}'
    mock_response.json.return_value = {"results": []}
    mock_response.raise_for_status = MagicMock()

    mock_file = AsyncMock()
    mock_file.read.return_value = b"image-bytes"
    mock_file.filename = "plant.jpg"
    mock_file.content_type = "image/jpeg"

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "app.services.plantnet_service.httpx.AsyncClient",
        return_value=mock_client,
    ):
        result = await recognize_plant_with_plantnet(mock_file)

    assert result == {"results": []}
    mock_client.post.assert_awaited_once()
