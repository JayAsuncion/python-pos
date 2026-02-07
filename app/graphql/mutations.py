import strawberry
from typing import Optional
from datetime import datetime
from app.models.user import User as UserModel
from app.models.product_template import ProductTemplate as ProductTemplateModel
from app.schemas.user import UserType
from app.schemas.product_template import ProductTemplateType
from app.database import SessionLocal

@strawberry.type
class Mutation:
    @strawberry.mutation(name="createUser")
    def create_user(
        self,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        hashed_password: str
    ) -> UserType:
        db = SessionLocal()
        db_user = UserModel(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.close()
        return UserType(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            first_name=db_user.first_name,
            last_name=db_user.last_name
        )

    @strawberry.mutation(name="updateUser")
    def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        hashed_password: Optional[str] = None
    ) -> Optional[UserType]:
        db = SessionLocal()
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            if username is not None:
                db_user.username = username
            if email is not None:
                db_user.email = email
            if first_name is not None:
                db_user.first_name = first_name
            if last_name is not None:
                db_user.last_name = last_name
            if hashed_password is not None:
                db_user.hashed_password = hashed_password
            db.commit()
            db.refresh(db_user)
            result = UserType(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                first_name=db_user.first_name,
                last_name=db_user.last_name
            )
        else:
            result = None
        db.close()
        return result

    @strawberry.mutation(name="deleteUser")
    def delete_user(self, user_id: int) -> Optional[UserType]:
        db = SessionLocal()
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            result = UserType(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                first_name=db_user.first_name,
                last_name=db_user.last_name
            )
            db.delete(db_user)
            db.commit()
        else:
            result = None
        db.close()
        return result

    @strawberry.mutation(name="createProductTemplate")
    def create_product_template(
        self,
        name: str,
        code: str,
        image: Optional[str] = None,
        is_active: bool = True,
        is_deleted_at: Optional[datetime] = None,
        is_deleted_by: Optional[int] = None
    ) -> ProductTemplateType:
        db = SessionLocal()
        db_product = ProductTemplateModel(
            name=name,
            code=code,
            image=image,
            is_active=is_active,
            is_deleted_at=is_deleted_at,
            is_deleted_by=is_deleted_by
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
            is_deleted_at=db_product.is_deleted_at,
            is_deleted_by=db_product.is_deleted_by
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
        is_deleted_at: Optional[datetime] = None,
        is_deleted_by: Optional[int] = None
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
            if is_deleted_at is not None:
                db_product.is_deleted_at = is_deleted_at
            if is_deleted_by is not None:
                db_product.is_deleted_by = is_deleted_by
            db.commit()
            db.refresh(db_product)
            result = ProductTemplateType(
                id=db_product.id,
                name=db_product.name,
                code=db_product.code,
                image=db_product.image,
                is_active=db_product.is_active,
                is_deleted_at=db_product.is_deleted_at,
                is_deleted_by=db_product.is_deleted_by
            )
        else:
            result = None
        db.close()
        return result

    @strawberry.mutation(name="deleteProductTemplate")
    def delete_product_template(self, product_id: int) -> Optional[ProductTemplateType]:
        db = SessionLocal()
        db_product = db.query(ProductTemplateModel).filter(ProductTemplateModel.id == product_id).first()
        if db_product:
            result = ProductTemplateType(
                id=db_product.id,
                name=db_product.name,
                code=db_product.code,
                image=db_product.image,
                is_active=db_product.is_active,
                is_deleted_at=db_product.is_deleted_at,
                is_deleted_by=db_product.is_deleted_by
            )
            db.delete(db_product)
            db.commit()
        else:
            result = None
        db.close()
        return result