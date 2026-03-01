import strawberry
from typing import Optional
from datetime import datetime
from sqlalchemy import func
from app.auth.permissions import require_permission
from app.models.product_slot import ProductSlot as ProductSlotModel
from app.models.product_slot_reading import ProductSlotReading as ProductSlotReadingModel
from app.schemas.product_slot import ProductSlotType
from app.database import SessionLocal


@strawberry.type
class ProductSlotMutations:
    @strawberry.mutation(name="createProductSlot")
    def create_product_slot(
        self,
        info: strawberry.types.Info,
        slot_name: str,
        product_id: Optional[int] = None,
        is_active: bool = True,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[int] = None,
        created_by: Optional[int] = None
    ) -> ProductSlotType:
        require_permission(info, "CREATE_PRODUCT_SLOT")
        db = SessionLocal()
        db_product_slot = ProductSlotModel(
            slot_name=slot_name,
            product_id=product_id,
            is_active=is_active,
            deleted_at=deleted_at,
            deleted_by=deleted_by,
            created_by=created_by
        )
        db.add(db_product_slot)
        db.commit()
        db.refresh(db_product_slot)
        result = ProductSlotType(
            id=db_product_slot.id,
            slot_name=db_product_slot.slot_name,
            product_id=db_product_slot.product_id,
            is_active=db_product_slot.is_active,
            deleted_at=db_product_slot.deleted_at,
            deleted_by=db_product_slot.deleted_by,
            created_at=db_product_slot.created_at,
            created_by=db_product_slot.created_by,
            updated_at=db_product_slot.updated_at,
            updated_by=db_product_slot.updated_by
        )
        db.close()
        return result

    @strawberry.mutation(name="updateProductSlot")
    def update_product_slot(
        self,
        info: strawberry.types.Info,
        product_slot_id: int,
        slot_name: Optional[str] = None,
        product_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[int] = None,
        updated_by: Optional[int] = None
    ) -> Optional[ProductSlotType]:
        require_permission(info, "UPDATE_PRODUCT_SLOT")
        db = SessionLocal()
        db_product_slot = db.query(ProductSlotModel).filter(ProductSlotModel.id == product_slot_id).first()
        if db_product_slot:
            if slot_name is not None:
                db_product_slot.slot_name = slot_name
            if product_id is not None:
                db_product_slot.product_id = product_id
            if is_active is not None:
                db_product_slot.is_active = is_active
            if deleted_at is not None:
                db_product_slot.deleted_at = deleted_at
            if deleted_by is not None:
                db_product_slot.deleted_by = deleted_by
            
            # Always update updated_by when provided
            db_product_slot.updated_by = updated_by
            
            db.commit()
            db.refresh(db_product_slot)
            result = ProductSlotType(
                id=db_product_slot.id,
                slot_name=db_product_slot.slot_name,
                product_id=db_product_slot.product_id,
                is_active=db_product_slot.is_active,
                deleted_at=db_product_slot.deleted_at,
                deleted_by=db_product_slot.deleted_by,
                created_at=db_product_slot.created_at,
                created_by=db_product_slot.created_by,
                updated_at=db_product_slot.updated_at,
                updated_by=db_product_slot.updated_by
            )
        else:
            result = None
        db.close()
        return result

    @strawberry.mutation(name="deleteProductSlot")
    def delete_product_slot(self, info: strawberry.types.Info, product_slot_id: int, deleted_by: int) -> Optional[ProductSlotType]:
        require_permission(info, "DELETE_PRODUCT_SLOT")
        db = SessionLocal()
        db_product_slot = db.query(ProductSlotModel).filter(ProductSlotModel.id == product_slot_id).first()
        if db_product_slot:
            # Cascading soft delete: Delete all related child records first
            
            # 1. Soft delete all ProductSlotReading records for this slot
            readings = db.query(ProductSlotReadingModel).filter(
                ProductSlotReadingModel.product_slot_id == product_slot_id,
                ProductSlotReadingModel.deleted_at.is_(None)
            ).all()
            for reading in readings:
                reading.deleted_at = func.now()
                reading.deleted_by = deleted_by
            
            # 2. Soft delete the product slot itself
            db_product_slot.deleted_at = func.now()
            db_product_slot.deleted_by = deleted_by
            
            db.commit()
            db.refresh(db_product_slot)
            result = ProductSlotType(
                id=db_product_slot.id,
                slot_name=db_product_slot.slot_name,
                product_id=db_product_slot.product_id,
                is_active=db_product_slot.is_active,
                deleted_at=db_product_slot.deleted_at,
                deleted_by=db_product_slot.deleted_by,
                created_at=db_product_slot.created_at,
                created_by=db_product_slot.created_by,
                updated_at=db_product_slot.updated_at,
                updated_by=db_product_slot.updated_by
            )
        else:
            result = None
        db.close()
        return result
