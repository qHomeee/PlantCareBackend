from pydantic import BaseModel

def Token(BaseModel):
    access_token: str
    token_type: str = "bearer"