from fastapi import APIRouter,Depends,HTTPException,status

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_user, get_user_by_email

router = APIRouter()

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED,)
def register(user_data:UserCreate,db:Session = Depends(get_db)):
    existing_user= get_user_by_email(user_data.email,db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    user = create_user(db,user_data)
    return user
