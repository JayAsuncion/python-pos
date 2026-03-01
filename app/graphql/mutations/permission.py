import strawberry
from typing import Optional
from datetime import datetime
from sqlalchemy import func
from app.models.permission import Permission as PermissionModel
from app.schemas.permission import PermissionType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class PermissionMutations:
    @strawberry.mutation(name="createPermission")
    def create_permission(
        self,
        info: strawberry.types.Info,
        code: str,
        name: str,
        category: str,
        description: Optional[str] = None,
    ) -> PermissionType:
        user = require_permission(info, "CREATE_PERMISSION")
        db = SessionLocal()

        existing = db.query(PermissionModel).filter(PermissionModel.code == code).first()
        if existing:
            db.close()
            raise ValueError(f"Permission with code '{code}' already exists")

        db_permission = PermissionModel(
            code=code,
            name=name,
            description=description,
            category=category,
        )
        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)
        result = PermissionType(
            id=db_permission.id,
            code=db_permission.code,
            name=db_permission.name,
            description=db_permission.description,
            category=db_permission.category,
            deleted_at=db_permission.deleted_at,
            deleted_by=db_permission.deleted_by,
        )
        db.close()
        return result

    @strawberry.mutation(name="updatePermission")
    def update_permission(
        self,
        info: strawberry.types.Info,
        permission_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Optional[PermissionType]:
        user = require_permission(info, "UPDATE_PERMISSION")
        db = SessionLocal()
        db_permission = (
            db.query(PermissionModel)
            .filter(PermissionModel.id == permission_id, PermissionModel.deleted_at.is_(None))
            .first()
        )
        if not db_permission:
            db.close()
            return None

        if name is not None:
            db_permission.name = name
        if description is not None:
            db_permission.description = description
        if category is not None:
            db_permission.category = category

        db.commit()
        db.refresh(db_permission)
        result = PermissionType(
            id=db_permission.id,
            code=db_permission.code,
            name=db_permission.name,
            description=db_permission.description,
            category=db_permission.category,
            deleted_at=db_permission.deleted_at,
            deleted_by=db_permission.deleted_by,
        )
        db.close()
        return result

    @strawberry.mutation(name="deletePermission")
    def delete_permission(
        self, info: strawberry.types.Info, permission_id: int
    ) -> Optional[PermissionType]:
        user = require_permission(info, "DELETE_PERMISSION")
        db = SessionLocal()
        db_permission = (
            db.query(PermissionModel)
            .filter(PermissionModel.id == permission_id, PermissionModel.deleted_at.is_(None))
            .first()
        )
        if not db_permission:
            db.close()
            return None

        db_permission.deleted_at = func.now()
        db_permission.deleted_by = user.id
        db.commit()
        db.refresh(db_permission)
        result = PermissionType(
            id=db_permission.id,
            code=db_permission.code,
            name=db_permission.name,
            description=db_permission.description,
            category=db_permission.category,
            deleted_at=db_permission.deleted_at,
            deleted_by=db_permission.deleted_by,
        )
        db.close()
        return result
