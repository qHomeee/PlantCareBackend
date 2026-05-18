from passlib.context import CryptContext
from app.core.config import settings
from datetime import datetime,timedelta
from jose import jwt,JWTError

pwd_context = CryptContext(schemes=["bcrypt"],deprecated = "auto")

def hash_password(password:str) ->str:
   return pwd_context.hash(password)

def verify_password(plain_password:str, hashed_password:str)->bool:
   return pwd_context.verify(plain_password,hashed_password)


def create_access_token(subject:str)->str:
   expire = datetime.now() + timedelta(
      minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
   )

   payload = {
      "sub": subject,
      "exp": expire,
   }


   return jwt.encode(
      payload,
      settings.SECRET_KEY,
      algorithm=settings.ALGORITHM
   )

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        print("JWT payload:", payload)
        return payload
    except JWTError as error:
        print("JWT decode error:", error)
        return None