import strawberry
from typing import Optional
from datetime import datetime, time
from sqlalchemy import func
from app.auth.permissions import require_permission
from app.models.shift_template import ShiftTemplate as ShiftTemplateModel
from app.models.shift import Shift as ShiftModel
from app.models.shift_user import ShiftUser as ShiftUserModel
from app.models.product_slot_reading import ProductSlotReading as ProductSlotReadingModel
from app.schemas.shift_template import ShiftTemplateType
from app.database import SessionLocal


@strawberry.type
class ShiftTemplateMutations:
    @strawberry.mutation(name="createShiftTemplate")
    def create_shift_template(
        self,
        info: strawberry.types.Info,
        shift_name: str,
        start_time: time,
        end_time: time,
        order: int,
        is_active: bool = True,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[int] = None,
        created_by: Optional[int] = None
    ) -> ShiftTemplateType:
        require_permission(info, "CREATE_SHIFT_TEMPLATE")
        db = SessionLocal()
        db_shift_template = ShiftTemplateModel(
            shift_name=shift_name,
            start_time=start_time,
            end_time=end_time,
            order=order,
            is_active=is_active,
            deleted_at=deleted_at,
            deleted_by=deleted_by,
            created_by=created_by
        )
        db.add(db_shift_template)
        db.commit()
        db.refresh(db_shift_template)
        result = ShiftTemplateType(
            id=db_shift_template.id,
            shift_name=db_shift_template.shift_name,
            start_time=db_shift_template.start_time,
            end_time=db_shift_template.end_time,
            order=db_shift_template.order,
            is_active=db_shift_template.is_active,
            deleted_at=db_shift_template.deleted_at,
            deleted_by=db_shift_template.deleted_by,
            created_at=db_shift_template.created_at,
            created_by=db_shift_template.created_by,
            updated_at=db_shift_template.updated_at,
            updated_by=db_shift_template.updated_by
        )
        db.close()
        return result

    @strawberry.mutation(name="updateShiftTemplate")
    def update_shift_template(
        self,
        info: strawberry.types.Info,
        shift_template_id: int,
        shift_name: Optional[str] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        order: Optional[int] = None,
        is_active: Optional[bool] = None,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[int] = None,
        updated_by: Optional[int] = None
    ) -> Optional[ShiftTemplateType]:
        require_permission(info, "UPDATE_SHIFT_TEMPLATE")
        db = SessionLocal()
        db_shift_template = db.query(ShiftTemplateModel).filter(ShiftTemplateModel.id == shift_template_id).first()
        if db_shift_template:
            if shift_name is not None:
                db_shift_template.shift_name = shift_name
            if start_time is not None:
                db_shift_template.start_time = start_time
            if end_time is not None:
                db_shift_template.end_time = end_time
            if order is not None:
                db_shift_template.order = order
            if is_active is not None:
                db_shift_template.is_active = is_active
            if deleted_at is not None:
                db_shift_template.deleted_at = deleted_at
            if deleted_by is not None:
                db_shift_template.deleted_by = deleted_by
            
            # Always update updated_by when provided
            db_shift_template.updated_by = updated_by
            
            db.commit()
            db.refresh(db_shift_template)
            result = ShiftTemplateType(
                id=db_shift_template.id,
                shift_name=db_shift_template.shift_name,
                start_time=db_shift_template.start_time,
                end_time=db_shift_template.end_time,
                order=db_shift_template.order,
                is_active=db_shift_template.is_active,
                deleted_at=db_shift_template.deleted_at,
                deleted_by=db_shift_template.deleted_by,
                created_at=db_shift_template.created_at,
                created_by=db_shift_template.created_by,
                updated_at=db_shift_template.updated_at,
                updated_by=db_shift_template.updated_by
            )
        else:
            result = None
        db.close()
        return result

    @strawberry.mutation(name="deleteShiftTemplate")
    def delete_shift_template(self, info: strawberry.types.Info, shift_template_id: int, deleted_by: int) -> Optional[ShiftTemplateType]:
        require_permission(info, "DELETE_SHIFT_TEMPLATE")
        db = SessionLocal()
        db_shift_template = db.query(ShiftTemplateModel).filter(ShiftTemplateModel.id == shift_template_id).first()
        if db_shift_template:
            # Cascading soft delete: Delete all related child records first
            
            # 1. Get all shifts for this template
            shifts = db.query(ShiftModel).filter(
                ShiftModel.shift_template_id == shift_template_id,
                ShiftModel.deleted_at.is_(None)
            ).all()
            
            for shift in shifts:
                # 1a. Soft delete all ShiftUser records for this shift
                shift_users = db.query(ShiftUserModel).filter(
                    ShiftUserModel.shift_id == shift.id,
                    ShiftUserModel.deleted_at.is_(None)
                ).all()
                for shift_user in shift_users:
                    shift_user.deleted_at = func.now()
                    shift_user.deleted_by = deleted_by
                
                # 1b. Soft delete all ProductSlotReading records for this shift
                readings = db.query(ProductSlotReadingModel).filter(
                    ProductSlotReadingModel.shift_id == shift.id,
                    ProductSlotReadingModel.deleted_at.is_(None)
                ).all()
                for reading in readings:
                    reading.deleted_at = func.now()
                    reading.deleted_by = deleted_by
                
                # 1c. Soft delete the shift
                shift.deleted_at = func.now()
                shift.deleted_by = deleted_by
            
            # 2. Soft delete the shift template itself
            db_shift_template.deleted_at = func.now()
            db_shift_template.deleted_by = deleted_by
            
            db.commit()
            db.refresh(db_shift_template)
            result = ShiftTemplateType(
                id=db_shift_template.id,
                shift_name=db_shift_template.shift_name,
                start_time=db_shift_template.start_time,
                end_time=db_shift_template.end_time,
                order=db_shift_template.order,
                is_active=db_shift_template.is_active,
                deleted_at=db_shift_template.deleted_at,
                deleted_by=db_shift_template.deleted_by,
                created_at=db_shift_template.created_at,
                created_by=db_shift_template.created_by,
                updated_at=db_shift_template.updated_at,
                updated_by=db_shift_template.updated_by
            )
        else:
            result = None
        db.close()
        return result
