from pydantic import BaseModel,EmailStr, Field

class UserCreate(BaseModel):
    email:EmailStr
    username:str = Field(min_length=2,max_length=80)
    password:str =Field(min_length=8,max_length=255)


class UserLogin(BaseModel):
    email:EmailStr
    password:str

class UserUpdate(BaseModel):
    username: str|None = Field(default=None,min_length=2,max_length=100)

class UserResponse(BaseModel):
    id:int
    email:EmailStr
    username:str


    model_config= {
        'from_attributes': True
    }