from fastapi import APIRouter,Depends,HTTPException,status

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.user import UserCreate, UserResponse,UserLogin
from app.services.user_service import create_user, get_user_by_email,authenticate_user
from app.schemas.token import Token


router = APIRouter()

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED,)
def register(user_data:UserCreate,db:Session = Depends(get_db)):
    existing_user= get_user_by_email(db,user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    user = create_user(db,user_data)
    return user


@router.post(
    "/login",
    response_model=Token,
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, login_data.email, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    access_token = create_access_token(subject=str(user.id))

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

