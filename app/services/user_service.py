from sqlalchemy.orm import Session

from app.core.security import hash_password,verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def update_user(db: Session, user: User, user_data: UserUpdate) -> User:
    if user_data.username is not None:
        user.username = user_data.username

    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db:Session,email:str,password:str)->User|None:
    user = get_user_by_email(db,email)

    if not user: 
        return None
    
    if not verify_password(password,user.hashed_password):
        return None
    return user

def update_user_avatar(
    db: Session,
    user: User,
    avatar_url: str,
) -> User:
    user.avatar_url = avatar_url

    db.commit()
    db.refresh(user)

    return user

