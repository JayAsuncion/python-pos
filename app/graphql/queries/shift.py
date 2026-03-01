import strawberry
from typing import List, Optional
from datetime import date
from app.models.shift import Shift as ShiftModel
from app.schemas.shift import ShiftType
from app.database import SessionLocal


@strawberry.type
class ShiftQueries:
    @strawberry.field
    def shifts(
        self,
        shift_date: Optional[date] = None,
        shift_template_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[ShiftType]:
        db = SessionLocal()
        query = db.query(ShiftModel).filter(ShiftModel.deleted_at.is_(None))
        
        if shift_date is not None:
            query = query.filter(ShiftModel.shift_date == shift_date)
        if shift_template_id is not None:
            query = query.filter(ShiftModel.shift_template_id == shift_template_id)
        if status is not None:
            query = query.filter(ShiftModel.status == status)
        
        shifts = query.all()
        db.close()
        return [ShiftType(
            id=shift.id,
            shift_template_id=shift.shift_template_id,
            shift_date=shift.shift_date,
            actual_start_datetime=shift.actual_start_datetime,
            actual_end_datetime=shift.actual_end_datetime,
            started_by=shift.started_by,
            ended_by=shift.ended_by,
            status=shift.status,
            is_active=shift.is_active,
            deleted_at=shift.deleted_at,
            deleted_by=shift.deleted_by,
            created_at=shift.created_at,
            created_by=shift.created_by,
            updated_at=shift.updated_at,
            updated_by=shift.updated_by
        ) for shift in shifts]

    @strawberry.field
    def shift(self, shift_id: int) -> Optional[ShiftType]:
        db = SessionLocal()
        shift = db.query(ShiftModel).filter(
            ShiftModel.id == shift_id,
            ShiftModel.deleted_at.is_(None)
        ).first()
        db.close()
        if shift:
            return ShiftType(
                id=shift.id,
                shift_template_id=shift.shift_template_id,
                shift_date=shift.shift_date,
                actual_start_datetime=shift.actual_start_datetime,
                actual_end_datetime=shift.actual_end_datetime,
                started_by=shift.started_by,
                ended_by=shift.ended_by,
                status=shift.status,
                is_active=shift.is_active,
                deleted_at=shift.deleted_at,
                deleted_by=shift.deleted_by,
                created_at=shift.created_at,
                created_by=shift.created_by,
                updated_at=shift.updated_at,
                updated_by=shift.updated_by
            )
        return None

    @strawberry.field
    def active_shift(self, shift_template_id: int) -> Optional[ShiftType]:
        db = SessionLocal()
        shift = db.query(ShiftModel).filter(
            ShiftModel.shift_template_id == shift_template_id,
            ShiftModel.status == "active",
            ShiftModel.deleted_at.is_(None)
        ).first()
        db.close()
        if shift:
            return ShiftType(
                id=shift.id,
                shift_template_id=shift.shift_template_id,
                shift_date=shift.shift_date,
                actual_start_datetime=shift.actual_start_datetime,
                actual_end_datetime=shift.actual_end_datetime,
                started_by=shift.started_by,
                ended_by=shift.ended_by,
                status=shift.status,
                is_active=shift.is_active,
                deleted_at=shift.deleted_at,
                deleted_by=shift.deleted_by,
                created_at=shift.created_at,
                created_by=shift.created_by,
                updated_at=shift.updated_at,
                updated_by=shift.updated_by
            )
        return None
