import strawberry
from typing import List, Optional
from app.models.product_slot import ProductSlot as ProductSlotModel
from app.schemas.product_slot import ProductSlotType
from app.database import SessionLocal


@strawberry.type
class ProductSlotQueries:
    @strawberry.field
    def product_slots(self) -> List[ProductSlotType]:
        db = SessionLocal()
        product_slots = db.query(ProductSlotModel).filter(ProductSlotModel.deleted_at.is_(None)).all()
        db.close()
        return [ProductSlotType(
            id=product_slot.id,
            slot_name=product_slot.slot_name,
            product_id=product_slot.product_id,
            is_active=product_slot.is_active,
            deleted_at=product_slot.deleted_at,
            deleted_by=product_slot.deleted_by,
            created_at=product_slot.created_at,
            created_by=product_slot.created_by,
            updated_at=product_slot.updated_at,
            updated_by=product_slot.updated_by
        ) for product_slot in product_slots]

    @strawberry.field
    def product_slot(self, product_slot_id: int) -> Optional[ProductSlotType]:
        db = SessionLocal()
        product_slot = db.query(ProductSlotModel).filter(
            ProductSlotModel.id == product_slot_id,
            ProductSlotModel.deleted_at.is_(None)
        ).first()
        db.close()
        if product_slot:
            return ProductSlotType(
                id=product_slot.id,
                slot_name=product_slot.slot_name,
                product_id=product_slot.product_id,
                is_active=product_slot.is_active,
                deleted_at=product_slot.deleted_at,
                deleted_by=product_slot.deleted_by,
                created_at=product_slot.created_at,
                created_by=product_slot.created_by,
                updated_at=product_slot.updated_at,
                updated_by=product_slot.updated_by
            )
        return None
