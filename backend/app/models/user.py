from datetime import datetime

from sqlalchemy import *
from sqlalchemy.orm import Mapped,mapped_column

from app.core.database import Base


class User(Base):
    __tablename__="user"
    
    id: Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True,index=True, nullable=False)

    username:Mapped[str] = mapped_column(String(100), nullable=False)

    hashed_password:Mapped[str] =mapped_column(String(255),nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default= datetime.now,onupdate=datetime.now)
    
     