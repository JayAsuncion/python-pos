import strawberry
from typing import List, Optional
from app.models.role import Role as RoleModel
from app.schemas.role import RoleType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class RoleQueries:
    @strawberry.field
    def roles(self, info: strawberry.types.Info) -> List[RoleType]:
        require_permission(info, "VIEW_ROLE")
        db = SessionLocal()
        roles = db.query(RoleModel).filter(RoleModel.deleted_at.is_(None)).all()
        db.close()
        return [
            RoleType(
                id=r.id,
                code=r.code,
                name=r.name,
                description=r.description,
                is_system_role=r.is_system_role,
                deleted_at=r.deleted_at,
                deleted_by=r.deleted_by,
            )
            for r in roles
        ]

    @strawberry.field
    def role(self, info: strawberry.types.Info, role_id: int) -> Optional[RoleType]:
        require_permission(info, "VIEW_ROLE")
        db = SessionLocal()
        r = (
            db.query(RoleModel)
            .filter(RoleModel.id == role_id, RoleModel.deleted_at.is_(None))
            .first()
        )
        db.close()
        if not r:
            return None
        return RoleType(
            id=r.id, code=r.code, name=r.name, description=r.description,
            is_system_role=r.is_system_role, deleted_at=r.deleted_at, deleted_by=r.deleted_by,
        )
