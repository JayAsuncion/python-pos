import strawberry
from typing import List, Optional
from app.models.user import User as UserModel
from app.models.product_template import ProductTemplate as ProductTemplateModel
from app.models.product import Product as ProductModel
from app.schemas.user import UserType
from app.schemas.product_template import ProductTemplateType
from app.schemas.product import ProductType
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

    @strawberry.field
    def products(self) -> List[ProductType]:
        db = SessionLocal()
        products = db.query(ProductModel).all()
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
            is_deleted_at=product.is_deleted_at,
            is_deleted_by=product.is_deleted_by,
            created_at=product.created_at,
            created_by=product.created_by,
            updated_at=product.updated_at,
            updated_by=product.updated_by
        ) for product in products]

    @strawberry.field
    def product(self, product_id: int) -> Optional[ProductType]:
        db = SessionLocal()
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
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
                is_deleted_at=product.is_deleted_at,
                is_deleted_by=product.is_deleted_by,
                created_at=product.created_at,
                created_by=product.created_by,
                updated_at=product.updated_at,
                updated_by=product.updated_by
            )
        return None