import strawberry
from typing import Optional
from datetime import datetime, time
from app.models.user import User as UserModel
from app.models.product_template import ProductTemplate as ProductTemplateModel
from app.models.product import Product as ProductModel
from app.models.shift import Shift as ShiftModel
from app.schemas.user import UserType
from app.schemas.product_template import ProductTemplateType
from app.schemas.product import ProductType
from app.schemas.shift import ShiftType
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
                deleted_at=db_product.deleted_at,
                deleted_by=db_product.deleted_by
            )
            db.delete(db_product)
            db.commit()
        else:
            result = None
        db.close()
        return result

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
    def delete_product(self, product_id: int) -> Optional[ProductType]:
        db = SessionLocal()
        db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if db_product:
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
            db.delete(db_product)
            db.commit()
        else:
            result = None
        db.close()
        return result

    @strawberry.mutation(name="createShift")
    def create_shift(
        self,
        shift_name: str,
        start_time: time,
        end_time: time,
        is_active: bool = True,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[int] = None,
        created_by: Optional[int] = None
    ) -> ShiftType:
        db = SessionLocal()
        db_shift = ShiftModel(
            shift_name=shift_name,
            start_time=start_time,
            end_time=end_time,
            is_active=is_active,
            deleted_at=deleted_at,
            deleted_by=deleted_by,
            created_by=created_by
        )
        db.add(db_shift)
        db.commit()
        db.refresh(db_shift)
        result = ShiftType(
            id=db_shift.id,
            shift_name=db_shift.shift_name,
            start_time=db_shift.start_time,
            end_time=db_shift.end_time,
            is_active=db_shift.is_active,
            deleted_at=db_shift.deleted_at,
            deleted_by=db_shift.deleted_by,
            created_at=db_shift.created_at,
            created_by=db_shift.created_by,
            updated_at=db_shift.updated_at,
            updated_by=db_shift.updated_by
        )
        db.close()
        return result

    @strawberry.mutation(name="updateShift")
    def update_shift(
        self,
        shift_id: int,
        shift_name: Optional[str] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        is_active: Optional[bool] = None,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[int] = None,
        updated_by: Optional[int] = None
    ) -> Optional[ShiftType]:
        db = SessionLocal()
        db_shift = db.query(ShiftModel).filter(ShiftModel.id == shift_id).first()
        if db_shift:
            if shift_name is not None:
                db_shift.shift_name = shift_name
            if start_time is not None:
                db_shift.start_time = start_time
            if end_time is not None:
                db_shift.end_time = end_time
            if is_active is not None:
                db_shift.is_active = is_active
            if deleted_at is not None:
                db_shift.deleted_at = deleted_at
            if deleted_by is not None:
                db_shift.deleted_by = deleted_by
            
            # Always update updated_by when provided
            db_shift.updated_by = updated_by
            
            db.commit()
            db.refresh(db_shift)
            result = ShiftType(
                id=db_shift.id,
                shift_name=db_shift.shift_name,
                start_time=db_shift.start_time,
                end_time=db_shift.end_time,
                is_active=db_shift.is_active,
                deleted_at=db_shift.deleted_at,
                deleted_by=db_shift.deleted_by,
                created_at=db_shift.created_at,
                created_by=db_shift.created_by,
                updated_at=db_shift.updated_at,
                updated_by=db_shift.updated_by
            )
        else:
            result = None
        db.close()
        return result

    @strawberry.mutation(name="deleteShift")
    def delete_shift(self, shift_id: int) -> Optional[ShiftType]:
        db = SessionLocal()
        db_shift = db.query(ShiftModel).filter(ShiftModel.id == shift_id).first()
        if db_shift:
            result = ShiftType(
                id=db_shift.id,
                shift_name=db_shift.shift_name,
                start_time=db_shift.start_time,
                end_time=db_shift.end_time,
                is_active=db_shift.is_active,
                deleted_at=db_shift.deleted_at,
                deleted_by=db_shift.deleted_by,
                created_at=db_shift.created_at,
                created_by=db_shift.created_by,
                updated_at=db_shift.updated_at,
                updated_by=db_shift.updated_by
            )
            db.delete(db_shift)
            db.commit()
        else:
            result = None
        db.close()
        return result