import strawberry
from typing import Optional, List
from datetime import date
from sqlalchemy import func
from app.models.shift import Shift as ShiftModel
from app.models.shift_user import ShiftUser as ShiftUserModel
from app.models.product_slot import ProductSlot as ProductSlotModel
from app.models.product import Product as ProductModel
from app.models.product_slot_reading import ProductSlotReading as ProductSlotReadingModel
from app.schemas.shift import ShiftType
from app.schemas.product_slot_reading import StartReadingInput, EndReadingInput
from app.database import SessionLocal


@strawberry.type
class ShiftMutations:
    @strawberry.mutation(name="startShift")
    def start_shift(
        self,
        shift_template_id: int,
        shift_date: date,
        user_ids: List[int],
        started_by: int,
        readings: List[StartReadingInput],
        created_by: Optional[int] = None
    ) -> ShiftType:
        db = SessionLocal()
        
        # Validate no active shift exists for this template
        existing_active_shift = db.query(ShiftModel).filter(
            ShiftModel.shift_template_id == shift_template_id,
            ShiftModel.status == "active"
        ).first()
        
        if existing_active_shift:
            db.close()
            raise ValueError(f"An active shift already exists for shift template {shift_template_id}")
        
        # Create Shift record
        db_shift = ShiftModel(
            shift_template_id=shift_template_id,
            shift_date=shift_date,
            actual_start_datetime=func.now(),
            started_by=started_by,
            status="active",
            created_by=created_by
        )
        db.add(db_shift)
        db.commit()
        db.refresh(db_shift)
        
        # Create ShiftUser records
        for user_id in user_ids:
            db_shift_user = ShiftUserModel(
                shift_id=db_shift.id,
                user_id=user_id,
                created_by=created_by
            )
            db.add(db_shift_user)
        
        # Create ProductSlotReading records
        for reading_input in readings:
            # Get product info from product_slot
            product_slot = db.query(ProductSlotModel).filter(
                ProductSlotModel.id == reading_input.product_slot_id
            ).first()
            
            if not product_slot or not product_slot.product_id:
                db.rollback()
                db.close()
                raise ValueError(f"Product slot {reading_input.product_slot_id} does not have a product assigned")
            
            # Get product pricing info
            product = db.query(ProductModel).filter(
                ProductModel.id == product_slot.product_id
            ).first()
            
            if not product:
                db.rollback()
                db.close()
                raise ValueError(f"Product {product_slot.product_id} not found")
            
            db_reading = ProductSlotReadingModel(
                shift_id=db_shift.id,
                product_slot_id=reading_input.product_slot_id,
                product_id=product.id,
                start_reading=reading_input.start_reading,
                start_reading_image_url=reading_input.start_reading_image_url,
                cost_price_snapshot=product.cost_price,
                selling_price_snapshot=product.selling_price,
                created_by=created_by
            )
            db.add(db_reading)
        
        db.commit()
        db.refresh(db_shift)
        
        result = ShiftType(
            id=db_shift.id,
            shift_template_id=db_shift.shift_template_id,
            shift_date=db_shift.shift_date,
            actual_start_datetime=db_shift.actual_start_datetime,
            actual_end_datetime=db_shift.actual_end_datetime,
            started_by=db_shift.started_by,
            ended_by=db_shift.ended_by,
            status=db_shift.status,
            is_active=db_shift.is_active,
            deleted_at=db_shift.deleted_at,
            deleted_by=db_shift.deleted_by,
            created_at=db_shift.created_at,
            created_by=db_shift.created_by,
            updated_at=db_shift.updated_at,
            updated_by=db_shift.updated_by
        )
        db.close()
        return result
    
    @strawberry.mutation(name="endShift")
    def end_shift(
        self,
        shift_id: int,
        ended_by: int,
        readings: List[EndReadingInput],
        updated_by: Optional[int] = None
    ) -> ShiftType:
        db = SessionLocal()
        
        # Get the shift
        db_shift = db.query(ShiftModel).filter(ShiftModel.id == shift_id).first()
        
        if not db_shift:
            db.close()
            raise ValueError(f"Shift {shift_id} not found")
        
        if db_shift.status != "active":
            db.close()
            raise ValueError(f"Shift {shift_id} is not active (status: {db_shift.status})")
        
        # Update ProductSlotReading records with end readings
        for reading_input in readings:
            db_reading = db.query(ProductSlotReadingModel).filter(
                ProductSlotReadingModel.shift_id == shift_id,
                ProductSlotReadingModel.product_slot_id == reading_input.product_slot_id
            ).first()
            
            if not db_reading:
                db.rollback()
                db.close()
                raise ValueError(f"Reading for product slot {reading_input.product_slot_id} not found in shift {shift_id}")
            
            # Validate end_reading >= start_reading
            if reading_input.end_reading < float(db_reading.start_reading):
                db.rollback()
                db.close()
                raise ValueError(
                    f"End reading ({reading_input.end_reading}) must be greater than or equal to "
                    f"start reading ({float(db_reading.start_reading)}) for product slot {reading_input.product_slot_id}"
                )
            
            db_reading.end_reading = reading_input.end_reading
            db_reading.end_reading_image_url = reading_input.end_reading_image_url
            db_reading.updated_by = updated_by
        
        # Update shift to completed
        db_shift.actual_end_datetime = func.now()
        db_shift.ended_by = ended_by
        db_shift.status = "completed"
        db_shift.updated_by = updated_by
        
        db.commit()
        db.refresh(db_shift)
        
        result = ShiftType(
            id=db_shift.id,
            shift_template_id=db_shift.shift_template_id,
            shift_date=db_shift.shift_date,
            actual_start_datetime=db_shift.actual_start_datetime,
            actual_end_datetime=db_shift.actual_end_datetime,
            started_by=db_shift.started_by,
            ended_by=db_shift.ended_by,
            status=db_shift.status,
            is_active=db_shift.is_active,
            deleted_at=db_shift.deleted_at,
            deleted_by=db_shift.deleted_by,
            created_at=db_shift.created_at,
            created_by=db_shift.created_by,
            updated_at=db_shift.updated_at,
            updated_by=db_shift.updated_by
        )
        db.close()
        return result
    
    @strawberry.mutation(name="deleteShift")
    def delete_shift(self, shift_id: int, deleted_by: int) -> Optional[ShiftType]:
        db = SessionLocal()
        db_shift = db.query(ShiftModel).filter(ShiftModel.id == shift_id).first()
        if db_shift:
            # Cascading soft delete: Delete all related child records first
            
            # 1. Soft delete all ShiftUser records for this shift
            shift_users = db.query(ShiftUserModel).filter(
                ShiftUserModel.shift_id == shift_id,
                ShiftUserModel.deleted_at.is_(None)
            ).all()
            for shift_user in shift_users:
                shift_user.deleted_at = func.now()
                shift_user.deleted_by = deleted_by
            
            # 2. Soft delete all ProductSlotReading records for this shift
            readings = db.query(ProductSlotReadingModel).filter(
                ProductSlotReadingModel.shift_id == shift_id,
                ProductSlotReadingModel.deleted_at.is_(None)
            ).all()
            for reading in readings:
                reading.deleted_at = func.now()
                reading.deleted_by = deleted_by
            
            # 3. Soft delete the shift itself
            db_shift.deleted_at = func.now()
            db_shift.deleted_by = deleted_by
            
            db.commit()
            db.refresh(db_shift)
            result = ShiftType(
                id=db_shift.id,
                shift_template_id=db_shift.shift_template_id,
                shift_date=db_shift.shift_date,
                actual_start_datetime=db_shift.actual_start_datetime,
                actual_end_datetime=db_shift.actual_end_datetime,
                started_by=db_shift.started_by,
                ended_by=db_shift.ended_by,
                status=db_shift.status,
                is_active=db_shift.is_active,
                deleted_at=db_shift.deleted_at,
                deleted_by=db_shift.deleted_by,
                created_at=db_shift.created_at,
                created_by=db_shift.created_by,
                updated_at=db_shift.updated_at,
                updated_by=db_shift.updated_by
            )
        else:
            result = None
        db.close()
        return result
