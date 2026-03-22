import strawberry
from typing import Optional
from sqlalchemy import func
from app.auth.permissions import require_permission
from app.models.product_slot_reading import ProductSlotReading as ProductSlotReadingModel
from app.schemas.product_slot_reading import ProductSlotReadingType
from app.database import SessionLocal


@strawberry.type
class ProductSlotReadingMutations:
    @strawberry.mutation(name="voidProductSlotReading")
    def void_product_slot_reading(
        self, 
        info: strawberry.types.Info, 
        product_slot_reading_id: int, 
        voided_by: int,
        void_reason: str
    ) -> Optional[ProductSlotReadingType]:
        require_permission(info, "VOID_PRODUCT_SLOT_READING")
        db = SessionLocal()
        db_reading = db.query(ProductSlotReadingModel).filter(
            ProductSlotReadingModel.id == product_slot_reading_id,
            ProductSlotReadingModel.voided_at.is_(None)
        ).first()
        
        if db_reading:
            # Void the reading
            db_reading.voided_at = func.now()
            db_reading.voided_by = voided_by
            db_reading.void_reason = void_reason
            db.commit()
            db.refresh(db_reading)
            
            # Calculate computed properties
            quantity_sold = None
            if db_reading.end_reading is not None and db_reading.start_reading is not None:
                quantity_sold = float(db_reading.end_reading) - float(db_reading.start_reading)
            
            revenue_amount = None
            if quantity_sold is not None:
                revenue_amount = quantity_sold * float(db_reading.selling_price_snapshot)
            
            cost_amount = None
            if quantity_sold is not None:
                cost_amount = quantity_sold * float(db_reading.cost_price_snapshot)
            
            result = ProductSlotReadingType(
                id=db_reading.id,
                shift_id=db_reading.shift_id,
                product_slot_id=db_reading.product_slot_id,
                product_id=db_reading.product_id,
                start_reading=float(db_reading.start_reading),
                end_reading=float(db_reading.end_reading) if db_reading.end_reading is not None else None,
                start_reading_image_url=db_reading.start_reading_image_url,
                end_reading_image_url=db_reading.end_reading_image_url,
                cost_price_snapshot=float(db_reading.cost_price_snapshot),
                selling_price_snapshot=float(db_reading.selling_price_snapshot),
                quantity_sold=quantity_sold,
                revenue_amount=revenue_amount,
                cost_amount=cost_amount,
                voided_at=db_reading.voided_at,
                voided_by=db_reading.voided_by,
                void_reason=db_reading.void_reason,
                created_at=db_reading.created_at,
                created_by=db_reading.created_by,
                updated_at=db_reading.updated_at,
                updated_by=db_reading.updated_by
            )
        else:
            result = None
        db.close()
        return result
