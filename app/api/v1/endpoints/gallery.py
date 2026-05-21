from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.gallery import (
    UserPlantCreate,
    UserPlantResponse,
    UserPlantUpdate,
)
from app.services.gallery_service import (
    add_plant_to_gallery,
    delete_user_plant,
    get_user_gallery,
    get_user_plant_by_id,
    update_user_plant,
)
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


@router.get(
    "/{user_plant_id}",
    response_model=UserPlantResponse,
)
def get_gallery_item(
    user_plant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_plant = get_user_plant_by_id(
        db=db,
        user_id=current_user.id,
        user_plant_id=user_plant_id,
    )

    if user_plant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Растение в галерее не найдено",
        )

    return user_plant


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


@router.patch(
    "/{user_plant_id}",
    response_model=UserPlantResponse,
)
def update_gallery_item(
    user_plant_id: int,
    data: UserPlantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_plant = get_user_plant_by_id(
        db=db,
        user_id=current_user.id,
        user_plant_id=user_plant_id,
    )

    if user_plant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Растение в галерее не найдено",
        )

    return update_user_plant(
        db=db,
        user_plant=user_plant,
        data=data,
    )


@router.delete(
    "/{user_plant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_gallery_item(
    user_plant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_plant = get_user_plant_by_id(
        db=db,
        user_id=current_user.id,
        user_plant_id=user_plant_id,
    )

    if user_plant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Растение в галерее не найдено",
        )

    delete_user_plant(db, user_plant)

    return None