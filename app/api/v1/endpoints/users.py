from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import update_user, update_user_avatar


AVATAR_UPLOAD_DIR = Path("static/uploads/avatars")
ALLOWED_AVATAR_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


router = APIRouter()

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch(
    "/me",
    response_model=UserResponse,
)
def update_me(
    user_data:UserUpdate,
    db:Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    user = update_user(db,current_user,user_data)
    return user

@router.post(
    "/me/avatar",
    response_model=UserResponse,
)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Допустимые форматы аватара: JPG, PNG, WEBP",
        )

    AVATAR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    extension = ALLOWED_AVATAR_TYPES[file.content_type]
    filename = f"user_{current_user.id}_{uuid4().hex}{extension}"
    file_path = AVATAR_UPLOAD_DIR / filename

    content = await file.read()

    max_size_bytes = 5 * 1024 * 1024

    if len(content) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Размер изображения не должен превышать 5 МБ",
        )

    file_path.write_bytes(content)

    avatar_url = f"/static/uploads/avatars/{filename}"

    user = update_user_avatar(
        db=db,
        user=current_user,
        avatar_url=avatar_url,
    )

    return user