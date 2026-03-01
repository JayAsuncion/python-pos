import strawberry
from typing import List, Optional
from app.auth.permissions import require_permission
from app.models.shift_template import ShiftTemplate as ShiftTemplateModel
from app.schemas.shift_template import ShiftTemplateType
from app.database import SessionLocal


@strawberry.type
class ShiftTemplateQueries:
    @strawberry.field
    def shift_templates(self, info: strawberry.types.Info) -> List[ShiftTemplateType]:
        require_permission(info, "VIEW_SHIFT_TEMPLATE")
        db = SessionLocal()
        shift_templates = db.query(ShiftTemplateModel).filter(ShiftTemplateModel.deleted_at.is_(None)).all()
        db.close()
        return [ShiftTemplateType(
            id=shift_template.id,
            shift_name=shift_template.shift_name,
            start_time=shift_template.start_time,
            end_time=shift_template.end_time,
            order=shift_template.order,
            is_active=shift_template.is_active,
            deleted_at=shift_template.deleted_at,
            deleted_by=shift_template.deleted_by,
            created_at=shift_template.created_at,
            created_by=shift_template.created_by,
            updated_at=shift_template.updated_at,
            updated_by=shift_template.updated_by
        ) for shift_template in shift_templates]

    @strawberry.field
    def shift_template(self, info: strawberry.types.Info, shift_template_id: int) -> Optional[ShiftTemplateType]:
        require_permission(info, "VIEW_SHIFT_TEMPLATE")
        db = SessionLocal()
        shift_template = db.query(ShiftTemplateModel).filter(
            ShiftTemplateModel.id == shift_template_id,
            ShiftTemplateModel.deleted_at.is_(None)
        ).first()
        db.close()
        if shift_template:
            return ShiftTemplateType(
                id=shift_template.id,
                shift_name=shift_template.shift_name,
                start_time=shift_template.start_time,
                end_time=shift_template.end_time,
                order=shift_template.order,
                is_active=shift_template.is_active,
                deleted_at=shift_template.deleted_at,
                deleted_by=shift_template.deleted_by,
                created_at=shift_template.created_at,
                created_by=shift_template.created_by,
                updated_at=shift_template.updated_at,
                updated_by=shift_template.updated_by
            )
        return None
