import strawberry
from typing import List, Optional
from app.models.product import Product as ProductModel
from app.schemas.product import ProductType
from app.database import SessionLocal


@strawberry.type
class ProductQueries:
    @strawberry.field
    def products(self) -> List[ProductType]:
        db = SessionLocal()
        products = db.query(ProductModel).filter(ProductModel.deleted_at.is_(None)).all()
        db.close()
        return [ProductType(
            id=product.id,
            product_template_id=product.product_template_id,
            name=product.name,
            code=product.code,
            image=product.image,
            starting_stock=float(product.starting_stock),
            running_stock=float(product.running_stock),
            cost_price=float(product.cost_price),
            selling_price=float(product.selling_price),
            is_active=product.is_active,
            deleted_at=product.deleted_at,
            deleted_by=product.deleted_by,
            created_at=product.created_at,
            created_by=product.created_by,
            updated_at=product.updated_at,
            updated_by=product.updated_by
        ) for product in products]

    @strawberry.field
    def product(self, product_id: int) -> Optional[ProductType]:
        db = SessionLocal()
        product = db.query(ProductModel).filter(
            ProductModel.id == product_id,
            ProductModel.deleted_at.is_(None)
        ).first()
        db.close()
        if product:
            return ProductType(
                id=product.id,
                product_template_id=product.product_template_id,
                name=product.name,
                code=product.code,
                image=product.image,
                starting_stock=float(product.starting_stock),
                running_stock=float(product.running_stock),
                cost_price=float(product.cost_price),
                selling_price=float(product.selling_price),
                is_active=product.is_active,
                deleted_at=product.deleted_at,
                deleted_by=product.deleted_by,
                created_at=product.created_at,
                created_by=product.created_by,
                updated_at=product.updated_at,
                updated_by=product.updated_by
            )
        return None
