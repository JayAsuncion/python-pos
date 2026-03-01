import strawberry
from typing import List
from app.models.role_permission import RolePermission as RolePermissionModel
from app.schemas.role_permission import RolePermissionType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class RolePermissionQueries:
    @strawberry.field
    def role_permissions(self, info: strawberry.types.Info, role_id: int) -> List[RolePermissionType]:
        require_permission(info, "VIEW_ROLE_PERMISSION")
        db = SessionLocal()
        role_permissions = (
            db.query(RolePermissionModel)
            .filter(RolePermissionModel.role_id == role_id, RolePermissionModel.deleted_at.is_(None))
            .all()
        )
        db.close()
        return [
            RolePermissionType(
                id=rp.id,
                role_id=rp.role_id,
                permission_id=rp.permission_id,
                deleted_at=rp.deleted_at,
                deleted_by=rp.deleted_by,
                created_at=rp.created_at,
                created_by=rp.created_by,
                updated_at=rp.updated_at,
                updated_by=rp.updated_by,
            )
            for rp in role_permissions
        ]

    @strawberry.field
    def permission_roles(self, info: strawberry.types.Info, permission_id: int) -> List[RolePermissionType]:
        require_permission(info, "VIEW_ROLE_PERMISSION")
        db = SessionLocal()
        permission_roles = (
            db.query(RolePermissionModel)
            .filter(RolePermissionModel.permission_id == permission_id, RolePermissionModel.deleted_at.is_(None))
            .all()
        )
        db.close()
        return [
            RolePermissionType(
                id=rp.id,
                role_id=rp.role_id,
                permission_id=rp.permission_id,
                deleted_at=rp.deleted_at,
                deleted_by=rp.deleted_by,
                created_at=rp.created_at,
                created_by=rp.created_by,
                updated_at=rp.updated_at,
                updated_by=rp.updated_by,
            )
            for rp in permission_roles
        ]
