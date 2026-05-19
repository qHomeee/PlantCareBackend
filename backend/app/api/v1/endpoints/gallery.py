from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.gallery import UserPlantCreate, UserPlantResponse
from app.services.gallery_service import add_plant_to_gallery, get_user_gallery
from app.services.plant_service import get_plant_by_id


router = APIRouter()


@router.get(
    "",
    response_model=list[UserPlantResponse],
)
def get_gallery(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_gallery(db, current_user.id)


@router.post(
    "",
    response_model=UserPlantResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_to_gallery(
    data: UserPlantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plant = get_plant_by_id(db, data.plant_id)

    if plant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Растение не найдено",
        )

    return add_plant_to_gallery(db, current_user.id, plant, data)