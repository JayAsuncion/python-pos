import strawberry
from typing import List, Optional
from app.models.user import User as UserModel
from app.models.product_template import ProductTemplate as ProductTemplateModel
from app.schemas.user import UserType
from app.schemas.product_template import ProductTemplateType
from app.database import SessionLocal

@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> List[UserType]:
        db = SessionLocal()
        users = db.query(UserModel).all()
        db.close()
        return [UserType(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name
        ) for user in users]

    @strawberry.field
    def product_templates(self) -> List[ProductTemplateType]:
        db = SessionLocal()
        products = db.query(ProductTemplateModel).all()
        db.close()
        return [ProductTemplateType(
            id=product.id,
            name=product.name,
            code=product.code,
            image=product.image,
            is_active=product.is_active,
            is_deleted_at=product.is_deleted_at,
            is_deleted_by=product.is_deleted_by
        ) for product in products]

    @strawberry.field
    def product_template(self, product_id: int) -> Optional[ProductTemplateType]:
        db = SessionLocal()
        product = db.query(ProductTemplateModel).filter(ProductTemplateModel.id == product_id).first()
        db.close()
        if product:
            return ProductTemplateType(
                id=product.id,
                name=product.name,
                code=product.code,
                image=product.image,
                is_active=product.is_active,
                is_deleted_at=product.is_deleted_at,
                is_deleted_by=product.is_deleted_by
            )
        return None