from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import update_user

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