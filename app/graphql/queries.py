import strawberry
from typing import List
from app.models.user import User as UserModel
from app.schemas.user import UserType
from app.database import SessionLocal

@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> List[UserType]:
        db = SessionLocal()
        users = db.query(UserModel).all()
        db.close()
        return [UserType(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name
        ) for user in users]