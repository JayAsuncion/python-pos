import strawberry
from typing import Optional
from sqlalchemy import func
from app.models.user_role import UserRole as UserRoleModel
from app.models.user import User as UserModel
from app.models.role import Role as RoleModel
from app.schemas.user_role import UserRoleType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class UserRoleMutations:
    @strawberry.mutation(name="assignRoleToUser")
    def assign_role_to_user(
        self, info: strawberry.types.Info, user_id: int, role_id: int
    ) -> UserRoleType:
        assigner = require_permission(info, "ASSIGN_ROLE")
        db = SessionLocal()

        # Validate user exists
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            db.close()
            raise ValueError(f"User with id {user_id} not found")

        # Validate role exists and is not deleted
        role = db.query(RoleModel).filter(
            RoleModel.id == role_id, RoleModel.deleted_at.is_(None)
        ).first()
        if not role:
            db.close()
            raise ValueError(f"Role with id {role_id} not found")

        # Check if assignment already exists (and is not deleted)
        existing = (
            db.query(UserRoleModel)
            .filter(
                UserRoleModel.user_id == user_id,
                UserRoleModel.role_id == role_id,
                UserRoleModel.deleted_at.is_(None),
            )
            .first()
        )
        if existing:
            db.close()
            raise ValueError(f"User {user_id} already has role {role_id}")

        db_user_role = UserRoleModel(
            user_id=user_id,
            role_id=role_id,
            created_by=assigner.id,
        )
        db.add(db_user_role)
        db.commit()
        db.refresh(db_user_role)
        result = UserRoleType(
            id=db_user_role.id,
            user_id=db_user_role.user_id,
            role_id=db_user_role.role_id,
            deleted_at=db_user_role.deleted_at,
            deleted_by=db_user_role.deleted_by,
            created_at=db_user_role.created_at,
            created_by=db_user_role.created_by,
            updated_at=db_user_role.updated_at,
            updated_by=db_user_role.updated_by,
        )
        db.close()
        return result

    @strawberry.mutation(name="removeRoleFromUser")
    def remove_role_from_user(
        self, info: strawberry.types.Info, user_id: int, role_id: int
    ) -> Optional[UserRoleType]:
        remover = require_permission(info, "REVOKE_ROLE")
        db = SessionLocal()
        db_user_role = (
            db.query(UserRoleModel)
            .filter(
                UserRoleModel.user_id == user_id,
                UserRoleModel.role_id == role_id,
                UserRoleModel.deleted_at.is_(None),
            )
            .first()
        )
        if not db_user_role:
            db.close()
            return None

        db_user_role.deleted_at = func.now()
        db_user_role.deleted_by = remover.id
        db.commit()
        db.refresh(db_user_role)
        result = UserRoleType(
            id=db_user_role.id,
            user_id=db_user_role.user_id,
            role_id=db_user_role.role_id,
            deleted_at=db_user_role.deleted_at,
            deleted_by=db_user_role.deleted_by,
            created_at=db_user_role.created_at,
            created_by=db_user_role.created_by,
            updated_at=db_user_role.updated_at,
            updated_by=db_user_role.updated_by,
        )
        db.close()
        return result
