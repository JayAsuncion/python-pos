import strawberry
from typing import Optional
from datetime import datetime
from sqlalchemy import func
from app.models.product_template import ProductTemplate as ProductTemplateModel
from app.models.product import Product as ProductModel
from app.models.product_slot import ProductSlot as ProductSlotModel
from app.models.product_slot_reading import ProductSlotReading as ProductSlotReadingModel
from app.schemas.product_template import ProductTemplateType
from app.database import SessionLocal


@strawberry.type
class ProductTemplateMutations:
    @strawberry.mutation(name="createProductTemplate")
    def create_product_template(
        self,
        name: str,
        code: str,
        image: Optional[str] = None,
        is_active: bool = True,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[int] = None
    ) -> ProductTemplateType:
        db = SessionLocal()
        db_product = ProductTemplateModel(
            name=name,
            code=code,
            image=image,
            is_active=is_active,
            deleted_at=deleted_at,
            deleted_by=deleted_by
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        result = ProductTemplateType(
            id=db_product.id,
            name=db_product.name,
            code=db_product.code,
            image=db_product.image,
            is_active=db_product.is_active,
            deleted_at=db_product.deleted_at,
            deleted_by=db_product.deleted_by
        )
        db.close()
        return result

    @strawberry.mutation(name="updateProductTemplate")
    def update_product_template(
        self,
        product_id: int,
        name: Optional[str] = None,
        code: Optional[str] = None,
        image: Optional[str] = None,
        is_active: Optional[bool] = None,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[int] = None
    ) -> Optional[ProductTemplateType]:
        db = SessionLocal()
        db_product = db.query(ProductTemplateModel).filter(ProductTemplateModel.id == product_id).first()
        if db_product:
            if name is not None:
                db_product.name = name
            if code is not None:
                db_product.code = code
            if image is not None:
                db_product.image = image
            if is_active is not None:
                db_product.is_active = is_active
            if deleted_at is not None:
                db_product.deleted_at = deleted_at
            if deleted_by is not None:
                db_product.deleted_by = deleted_by
            db.commit()
            db.refresh(db_product)
            result = ProductTemplateType(
                id=db_product.id,
                name=db_product.name,
                code=db_product.code,
                image=db_product.image,
                is_active=db_product.is_active,
                deleted_at=db_product.deleted_at,
                deleted_by=db_product.deleted_by
            )
        else:
            result = None
        db.close()
        return result

    @strawberry.mutation(name="deleteProductTemplate")
    def delete_product_template(self, product_id: int, deleted_by: int) -> Optional[ProductTemplateType]:
        db = SessionLocal()
        db_product = db.query(ProductTemplateModel).filter(ProductTemplateModel.id == product_id).first()
        if db_product:
            # Cascading soft delete: Delete all related child records first
            
            # 1. Get all products for this template
            products = db.query(ProductModel).filter(
                ProductModel.product_template_id == product_id,
                ProductModel.deleted_at.is_(None)
            ).all()
            
            for product in products:
                # 1a. Soft delete ProductSlotReadings for this product
                product_readings = db.query(ProductSlotReadingModel).filter(
                    ProductSlotReadingModel.product_id == product.id,
                    ProductSlotReadingModel.deleted_at.is_(None)
                ).all()
                for reading in product_readings:
                    reading.deleted_at = func.now()
                    reading.deleted_by = deleted_by
                
                # 1b. Soft delete ProductSlots for this product
                product_slots = db.query(ProductSlotModel).filter(
                    ProductSlotModel.product_id == product.id,
                    ProductSlotModel.deleted_at.is_(None)
                ).all()
                for slot in product_slots:
                    # Soft delete ProductSlotReadings for this slot
                    slot_readings = db.query(ProductSlotReadingModel).filter(
                        ProductSlotReadingModel.product_slot_id == slot.id,
                        ProductSlotReadingModel.deleted_at.is_(None)
                    ).all()
                    for reading in slot_readings:
                        reading.deleted_at = func.now()
                        reading.deleted_by = deleted_by
                    
                    slot.deleted_at = func.now()
                    slot.deleted_by = deleted_by
                
                # 1c. Soft delete the product
                product.deleted_at = func.now()
                product.deleted_by = deleted_by
            
            # 2. Soft delete the product template itself
            db_product.deleted_at = func.now()
            db_product.deleted_by = deleted_by
            
            db.commit()
            db.refresh(db_product)
            result = ProductTemplateType(
                id=db_product.id,
                name=db_product.name,
                code=db_product.code,
                image=db_product.image,
                is_active=db_product.is_active,
                deleted_at=db_product.deleted_at,
                deleted_by=db_product.deleted_by
            )
        else:
            result = None
        db.close()
        return result
