import strawberry
from typing import List
from app.models.user import User as UserModel
from app.schemas.user import UserType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class UserQueries:
    @strawberry.field
    def users(self, info: strawberry.types.Info) -> List[UserType]:
        require_permission(info, "VIEW_USER")
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
