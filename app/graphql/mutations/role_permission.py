import strawberry
from typing import Optional
from sqlalchemy import func
from app.models.role_permission import RolePermission as RolePermissionModel
from app.models.role import Role as RoleModel
from app.models.permission import Permission as PermissionModel
from app.schemas.role_permission import RolePermissionType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class RolePermissionMutations:
    @strawberry.mutation(name="addPermissionToRole")
    def add_permission_to_role(
        self, info: strawberry.types.Info, role_id: int, permission_id: int
    ) -> RolePermissionType:
        granter = require_permission(info, "GRANT_PERMISSION")
        db = SessionLocal()

        # Validate role exists and is not deleted
        role = db.query(RoleModel).filter(
            RoleModel.id == role_id, RoleModel.deleted_at.is_(None)
        ).first()
        if not role:
            db.close()
            raise ValueError(f"Role with id {role_id} not found")

        # Validate permission exists and is not deleted
        permission = db.query(PermissionModel).filter(
            PermissionModel.id == permission_id, PermissionModel.deleted_at.is_(None)
        ).first()
        if not permission:
            db.close()
            raise ValueError(f"Permission with id {permission_id} not found")

        # Check if assignment already exists (and is not deleted)
        existing = (
            db.query(RolePermissionModel)
            .filter(
                RolePermissionModel.role_id == role_id,
                RolePermissionModel.permission_id == permission_id,
                RolePermissionModel.deleted_at.is_(None),
            )
            .first()
        )
        if existing:
            db.close()
            raise ValueError(f"Role {role_id} already has permission {permission_id}")

        db_role_permission = RolePermissionModel(
            role_id=role_id,
            permission_id=permission_id,
            created_by=granter.id,
        )
        db.add(db_role_permission)
        db.commit()
        db.refresh(db_role_permission)
        result = RolePermissionType(
            id=db_role_permission.id,
            role_id=db_role_permission.role_id,
            permission_id=db_role_permission.permission_id,
            deleted_at=db_role_permission.deleted_at,
            deleted_by=db_role_permission.deleted_by,
            created_at=db_role_permission.created_at,
            created_by=db_role_permission.created_by,
            updated_at=db_role_permission.updated_at,
            updated_by=db_role_permission.updated_by,
        )
        db.close()
        return result

    @strawberry.mutation(name="removePermissionFromRole")
    def remove_permission_from_role(
        self, info: strawberry.types.Info, role_id: int, permission_id: int
    ) -> Optional[RolePermissionType]:
        revoker = require_permission(info, "REVOKE_PERMISSION")
        db = SessionLocal()
        db_role_permission = (
            db.query(RolePermissionModel)
            .filter(
                RolePermissionModel.role_id == role_id,
                RolePermissionModel.permission_id == permission_id,
                RolePermissionModel.deleted_at.is_(None),
            )
            .first()
        )
        if not db_role_permission:
            db.close()
            return None

        db_role_permission.deleted_at = func.now()
        db_role_permission.deleted_by = revoker.id
        db.commit()
        db.refresh(db_role_permission)
        result = RolePermissionType(
            id=db_role_permission.id,
            role_id=db_role_permission.role_id,
            permission_id=db_role_permission.permission_id,
            deleted_at=db_role_permission.deleted_at,
            deleted_by=db_role_permission.deleted_by,
            created_at=db_role_permission.created_at,
            created_by=db_role_permission.created_by,
            updated_at=db_role_permission.updated_at,
            updated_by=db_role_permission.updated_by,
        )
        db.close()
        return result
