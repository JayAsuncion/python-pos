from pydantic import BaseModel
from typing import Optional
import strawberry

class UserBase(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str

class UserCreate(UserBase):
    hashed_password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    hashed_password: Optional[str] = None

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

@strawberry.type
class UserType:
    id: int
    username: str
    email: str
    first_name: str
    last_name: str