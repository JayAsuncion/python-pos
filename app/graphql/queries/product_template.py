import strawberry
from typing import List, Optional
from app.models.product_template import ProductTemplate as ProductTemplateModel
from app.schemas.product_template import ProductTemplateType
from app.database import SessionLocal


@strawberry.type
class ProductTemplateQueries:
    @strawberry.field
    def product_templates(self) -> List[ProductTemplateType]:
        db = SessionLocal()
        products = db.query(ProductTemplateModel).filter(ProductTemplateModel.deleted_at.is_(None)).all()
        db.close()
        return [ProductTemplateType(
            id=product.id,
            name=product.name,
            code=product.code,
            image=product.image,
            is_active=product.is_active,
            deleted_at=product.deleted_at,
            deleted_by=product.deleted_by
        ) for product in products]

    @strawberry.field
    def product_template(self, product_id: int) -> Optional[ProductTemplateType]:
        db = SessionLocal()
        product = db.query(ProductTemplateModel).filter(
            ProductTemplateModel.id == product_id,
            ProductTemplateModel.deleted_at.is_(None)
        ).first()
        db.close()
        if product:
            return ProductTemplateType(
                id=product.id,
                name=product.name,
                code=product.code,
                image=product.image,
                is_active=product.is_active,
                deleted_at=product.deleted_at,
                deleted_by=product.deleted_by
            )
        return None
