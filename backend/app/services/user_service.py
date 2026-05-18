from sqlalchemy.orm import Session

from app.models import User
from app.core.security import hashed_password

from app.schemas.user import UserCreate,UserUpdate

def get_user_by_email(email:str, db:Session)->User|None:
   return db.query(User).filter(User.email == email).first()


def get_user_by_id(id:int, db:Session) -> User|None:
   return db.query(User).filter(User.id == id).first()

def create_user(db:Session,user_data:UserCreate)->User:
    user= UserCreate(
       email= user_data.email,
       username=user_data.username,
       hashed_password=hashed_password(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)



def update_user(db: Session, user: User, user_data: UserUpdate) -> User:
    if user_data.username is not None:
        user.username = user_data.username

    db.commit()
    db.refresh(user)

    return user