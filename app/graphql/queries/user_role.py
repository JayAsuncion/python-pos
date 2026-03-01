import strawberry
from typing import List
from app.models.user_role import UserRole as UserRoleModel
from app.schemas.user_role import UserRoleType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class UserRoleQueries:
    @strawberry.field
    def user_roles(self, info: strawberry.types.Info, user_id: int) -> List[UserRoleType]:
        require_permission(info, "VIEW_USER_ROLE")
        db = SessionLocal()
        user_roles = (
            db.query(UserRoleModel)
            .filter(UserRoleModel.user_id == user_id, UserRoleModel.deleted_at.is_(None))
            .all()
        )
        db.close()
        return [
            UserRoleType(
                id=ur.id,
                user_id=ur.user_id,
                role_id=ur.role_id,
                deleted_at=ur.deleted_at,
                deleted_by=ur.deleted_by,
                created_at=ur.created_at,
                created_by=ur.created_by,
                updated_at=ur.updated_at,
                updated_by=ur.updated_by,
            )
            for ur in user_roles
        ]

    @strawberry.field
    def role_users(self, info: strawberry.types.Info, role_id: int) -> List[UserRoleType]:
        require_permission(info, "VIEW_USER_ROLE")
        db = SessionLocal()
        role_users = (
            db.query(UserRoleModel)
            .filter(UserRoleModel.role_id == role_id, UserRoleModel.deleted_at.is_(None))
            .all()
        )
        db.close()
        return [
            UserRoleType(
                id=ur.id,
                user_id=ur.user_id,
                role_id=ur.role_id,
                deleted_at=ur.deleted_at,
                deleted_by=ur.deleted_by,
                created_at=ur.created_at,
                created_by=ur.created_by,
                updated_at=ur.updated_at,
                updated_by=ur.updated_by,
            )
            for ur in role_users
        ]
