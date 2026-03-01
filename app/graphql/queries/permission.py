import strawberry
from typing import List, Optional
from app.models.permission import Permission as PermissionModel
from app.schemas.permission import PermissionType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class PermissionQueries:
    @strawberry.field
    def permissions(self, info: strawberry.types.Info) -> List[PermissionType]:
        require_permission(info, "VIEW_PERMISSION")
        db = SessionLocal()
        permissions = db.query(PermissionModel).filter(PermissionModel.deleted_at.is_(None)).all()
        db.close()
        return [
            PermissionType(
                id=p.id,
                code=p.code,
                name=p.name,
                description=p.description,
                category=p.category,
                deleted_at=p.deleted_at,
                deleted_by=p.deleted_by,
            )
            for p in permissions
        ]

    @strawberry.field
    def permission(self, info: strawberry.types.Info, permission_id: int) -> Optional[PermissionType]:
        require_permission(info, "VIEW_PERMISSION")
        db = SessionLocal()
        p = (
            db.query(PermissionModel)
            .filter(PermissionModel.id == permission_id, PermissionModel.deleted_at.is_(None))
            .first()
        )
        db.close()
        if not p:
            return None
        return PermissionType(
            id=p.id, code=p.code, name=p.name, description=p.description,
            category=p.category, deleted_at=p.deleted_at, deleted_by=p.deleted_by,
        )

    @strawberry.field
    def permissions_by_category(self, info: strawberry.types.Info, category: str) -> List[PermissionType]:
        require_permission(info, "VIEW_PERMISSION")
        db = SessionLocal()
        permissions = (
            db.query(PermissionModel)
            .filter(PermissionModel.category == category, PermissionModel.deleted_at.is_(None))
            .all()
        )
        db.close()
        return [
            PermissionType(
                id=p.id,
                code=p.code,
                name=p.name,
                description=p.description,
                category=p.category,
                deleted_at=p.deleted_at,
                deleted_by=p.deleted_by,
            )
            for p in permissions
        ]
