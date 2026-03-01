import strawberry
from typing import List, Optional
from app.auth.permissions import require_permission
from app.models.product_template import ProductTemplate as ProductTemplateModel
from app.schemas.product_template import ProductTemplateType
from app.database import SessionLocal


@strawberry.type
class ProductTemplateQueries:
    @strawberry.field
    def product_templates(self, info: strawberry.types.Info) -> List[ProductTemplateType]:
        require_permission(info, "VIEW_PRODUCT_TEMPLATE")
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
    def product_template(self, info: strawberry.types.Info, product_id: int) -> Optional[ProductTemplateType]:
        require_permission(info, "VIEW_PRODUCT_TEMPLATE")
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
