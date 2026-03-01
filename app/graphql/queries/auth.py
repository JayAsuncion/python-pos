import strawberry
from typing import List, Optional
from app.schemas.user import UserType
from app.schemas.role import RoleType
from app.auth.permissions import require_auth, get_user_permissions
from app.database import SessionLocal


@strawberry.type
class AuthQueries:
    @strawberry.field
    def me(self, info: strawberry.types.Info) -> Optional[UserType]:
        """Get the currently authenticated user."""
        user = info.context.get("user")
        if not user:
            return None
        return UserType(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )

    @strawberry.field
    def my_permissions(self, info: strawberry.types.Info) -> List[str]:
        """Get all permission codes for the current user."""
        user = require_auth(info)
        db = SessionLocal()
        try:
            permissions = get_user_permissions(db, user.id)
        finally:
            db.close()
        return sorted(list(permissions))

    @strawberry.field
    def my_roles(self, info: strawberry.types.Info) -> List[RoleType]:
        """Get all active roles for the current user."""
        from app.models.user_role import UserRole
        from app.models.role import Role

        user = require_auth(info)
        db = SessionLocal()
        roles = (
            db.query(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(
                UserRole.user_id == user.id,
                UserRole.deleted_at.is_(None),
                Role.deleted_at.is_(None),
            )
            .all()
        )
        result = [
            RoleType(
                id=role.id,
                code=role.code,
                name=role.name,
                description=role.description,
                is_system_role=role.is_system_role,
                deleted_at=role.deleted_at,
                deleted_by=role.deleted_by,
            )
            for role in roles
        ]
        db.close()
        return result
