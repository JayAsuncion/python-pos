import strawberry
from typing import Optional
from sqlalchemy import func
from app.models.role import Role as RoleModel
from app.schemas.role import RoleType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class RoleMutations:
    @strawberry.mutation(name="createRole")
    def create_role(
        self,
        info: strawberry.types.Info,
        code: str,
        name: str,
        description: Optional[str] = None,
    ) -> RoleType:
        user = require_permission(info, "CREATE_ROLE")
        db = SessionLocal()

        existing = db.query(RoleModel).filter(RoleModel.code == code).first()
        if existing:
            db.close()
            raise ValueError(f"Role with code '{code}' already exists")

        db_role = RoleModel(
            code=code,
            name=name,
            description=description,
            is_system_role=False,
        )
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        result = RoleType(
            id=db_role.id,
            code=db_role.code,
            name=db_role.name,
            description=db_role.description,
            is_system_role=db_role.is_system_role,
            deleted_at=db_role.deleted_at,
            deleted_by=db_role.deleted_by,
        )
        db.close()
        return result

    @strawberry.mutation(name="updateRole")
    def update_role(
        self,
        info: strawberry.types.Info,
        role_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[RoleType]:
        user = require_permission(info, "UPDATE_ROLE")
        db = SessionLocal()
        db_role = (
            db.query(RoleModel)
            .filter(RoleModel.id == role_id, RoleModel.deleted_at.is_(None))
            .first()
        )
        if not db_role:
            db.close()
            return None

        if name is not None:
            db_role.name = name
        if description is not None:
            db_role.description = description

        db.commit()
        db.refresh(db_role)
        result = RoleType(
            id=db_role.id,
            code=db_role.code,
            name=db_role.name,
            description=db_role.description,
            is_system_role=db_role.is_system_role,
            deleted_at=db_role.deleted_at,
            deleted_by=db_role.deleted_by,
        )
        db.close()
        return result

    @strawberry.mutation(name="deleteRole")
    def delete_role(
        self, info: strawberry.types.Info, role_id: int
    ) -> Optional[RoleType]:
        user = require_permission(info, "DELETE_ROLE")
        db = SessionLocal()
        db_role = (
            db.query(RoleModel)
            .filter(RoleModel.id == role_id, RoleModel.deleted_at.is_(None))
            .first()
        )
        if not db_role:
            db.close()
            return None

        if db_role.is_system_role:
            db.close()
            raise ValueError("Cannot delete a system role")

        db_role.deleted_at = func.now()
        db_role.deleted_by = user.id
        db.commit()
        db.refresh(db_role)
        result = RoleType(
            id=db_role.id,
            code=db_role.code,
            name=db_role.name,
            description=db_role.description,
            is_system_role=db_role.is_system_role,
            deleted_at=db_role.deleted_at,
            deleted_by=db_role.deleted_by,
        )
        db.close()
        return result
