import strawberry
from typing import Optional
from datetime import datetime
from sqlalchemy import func
from app.models.product_template import ProductTemplate as ProductTemplateModel
from app.models.product import Product as ProductModel
from app.models.product_slot import ProductSlot as ProductSlotModel
from app.models.product_slot_reading import ProductSlotReading as ProductSlotReadingModel
from app.schemas.product import ProductType
from app.database import SessionLocal


@strawberry.type
class ProductMutations:
    @strawberry.mutation(name="createProduct")
    def create_product(
        self,
        product_template_id: int,
        starting_stock: float,
        cost_price: float,
        selling_price: float,
        running_stock: Optional[float] = None,
        name: Optional[str] = None,
        code: Optional[str] = None,
        image: Optional[str] = None,
        is_active: bool = True,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[int] = None,
        created_by: Optional[int] = None
    ) -> ProductType:
        db = SessionLocal()
        
        # Fetch product template to derive values if not provided
        product_template = db.query(ProductTemplateModel).filter(
            ProductTemplateModel.id == product_template_id
        ).first()
        
        if not product_template:
            db.close()
            raise ValueError(f"Product template with id {product_template_id} not found")
        
        # Use template values if not provided
        final_name = name if name is not None else product_template.name
        final_code = code if code is not None else product_template.code
        final_image = image if image is not None else product_template.image
        final_running_stock = running_stock if running_stock is not None else starting_stock
        
        db_product = ProductModel(
            product_template_id=product_template_id,
            name=final_name,
            code=final_code,
            image=final_image,
            starting_stock=starting_stock,
            running_stock=final_running_stock,
            cost_price=cost_price,
            selling_price=selling_price,
            is_active=is_active,
            deleted_at=deleted_at,
            deleted_by=deleted_by,
            created_by=created_by
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        result = ProductType(
            id=db_product.id,
            product_template_id=db_product.product_template_id,
            name=db_product.name,
            code=db_product.code,
            image=db_product.image,
            starting_stock=float(db_product.starting_stock),
            running_stock=float(db_product.running_stock),
            cost_price=float(db_product.cost_price),
            selling_price=float(db_product.selling_price),
            is_active=db_product.is_active,
            deleted_at=db_product.deleted_at,
            deleted_by=db_product.deleted_by,
            created_at=db_product.created_at,
            created_by=db_product.created_by,
            updated_at=db_product.updated_at,
            updated_by=db_product.updated_by
        )
        db.close()
        return result

    @strawberry.mutation(name="updateProduct")
    def update_product(
        self,
        product_id: int,
        product_template_id: Optional[int] = None,
        name: Optional[str] = None,
        code: Optional[str] = None,
        image: Optional[str] = None,
        starting_stock: Optional[float] = None,
        running_stock: Optional[float] = None,
        cost_price: Optional[float] = None,
        selling_price: Optional[float] = None,
        is_active: Optional[bool] = None,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[int] = None,
        updated_by: Optional[int] = None
    ) -> Optional[ProductType]:
        db = SessionLocal()
        db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if db_product:
            if product_template_id is not None:
                db_product.product_template_id = product_template_id
            if name is not None:
                db_product.name = name
            if code is not None:
                db_product.code = code
            if image is not None:
                db_product.image = image
            if starting_stock is not None:
                db_product.starting_stock = starting_stock
            if running_stock is not None:
                db_product.running_stock = running_stock
            if cost_price is not None:
                db_product.cost_price = cost_price
            if selling_price is not None:
                db_product.selling_price = selling_price
            if is_active is not None:
                db_product.is_active = is_active
            if deleted_at is not None:
                db_product.deleted_at = deleted_at
            if deleted_by is not None:
                db_product.deleted_by = deleted_by
            
            # Always update updated_by when provided
            db_product.updated_by = updated_by
            
            db.commit()
            db.refresh(db_product)
            result = ProductType(
                id=db_product.id,
                product_template_id=db_product.product_template_id,
                name=db_product.name,
                code=db_product.code,
                image=db_product.image,
                starting_stock=float(db_product.starting_stock),
                running_stock=float(db_product.running_stock),
                cost_price=float(db_product.cost_price),
                selling_price=float(db_product.selling_price),
                is_active=db_product.is_active,
                deleted_at=db_product.deleted_at,
                deleted_by=db_product.deleted_by,
                created_at=db_product.created_at,
                created_by=db_product.created_by,
                updated_at=db_product.updated_at,
                updated_by=db_product.updated_by
            )
        else:
            result = None
        db.close()
        return result

    @strawberry.mutation(name="deleteProduct")
    def delete_product(self, product_id: int, deleted_by: int) -> Optional[ProductType]:
        db = SessionLocal()
        db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if db_product:
            # Cascading soft delete: Delete all related child records first
            
            # 1. Soft delete ProductSlotReadings for this product
            product_readings = db.query(ProductSlotReadingModel).filter(
                ProductSlotReadingModel.product_id == product_id,
                ProductSlotReadingModel.deleted_at.is_(None)
            ).all()
            for reading in product_readings:
                reading.deleted_at = func.now()
                reading.deleted_by = deleted_by
            
            # 2. Soft delete ProductSlots for this product
            product_slots = db.query(ProductSlotModel).filter(
                ProductSlotModel.product_id == product_id,
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
            
            # 3. Soft delete the product itself
            db_product.deleted_at = func.now()
            db_product.deleted_by = deleted_by
            
            db.commit()
            db.refresh(db_product)
            result = ProductType(
                id=db_product.id,
                product_template_id=db_product.product_template_id,
                name=db_product.name,
                code=db_product.code,
                image=db_product.image,
                starting_stock=float(db_product.starting_stock),
                running_stock=float(db_product.running_stock),
                cost_price=float(db_product.cost_price),
                selling_price=float(db_product.selling_price),
                is_active=db_product.is_active,
                deleted_at=db_product.deleted_at,
                deleted_by=db_product.deleted_by,
                created_at=db_product.created_at,
                created_by=db_product.created_by,
                updated_at=db_product.updated_at,
                updated_by=db_product.updated_by
            )
        else:
            result = None
        db.close()
        return result
