import strawberry
from typing import Optional
from app.models.user import User as UserModel
from app.schemas.user import UserType
from app.auth.security import hash_password
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class UserMutations:
    @strawberry.mutation(name="createUser")
    def create_user(
        self,
        info: strawberry.types.Info,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        hashed_password: str
    ) -> UserType:
        user = require_permission(info, "CREATE_USER")
        db = SessionLocal()
        db_user = UserModel(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hash_password(hashed_password)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.close()
        return UserType(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            first_name=db_user.first_name,
            last_name=db_user.last_name
        )

    @strawberry.mutation(name="updateUser")
    def update_user(
        self,
        info: strawberry.types.Info,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        hashed_password: Optional[str] = None
    ) -> Optional[UserType]:
        user = require_permission(info, "UPDATE_USER")
        db = SessionLocal()
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            if username is not None:
                db_user.username = username
            if email is not None:
                db_user.email = email
            if first_name is not None:
                db_user.first_name = first_name
            if last_name is not None:
                db_user.last_name = last_name
            if hashed_password is not None:
                db_user.hashed_password = hash_password(hashed_password)
            db.commit()
            db.refresh(db_user)
            result = UserType(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                first_name=db_user.first_name,
                last_name=db_user.last_name
            )
        else:
            result = None
        db.close()
        return result

    @strawberry.mutation(name="deleteUser")
    def delete_user(self, info: strawberry.types.Info, user_id: int) -> Optional[UserType]:
        user = require_permission(info, "DELETE_USER")
        db = SessionLocal()
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            result = UserType(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                first_name=db_user.first_name,
                last_name=db_user.last_name
            )
            db.delete(db_user)
            db.commit()
        else:
            result = None
        db.close()
        return result
