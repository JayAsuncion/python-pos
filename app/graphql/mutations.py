import strawberry
from typing import Optional, List
from datetime import datetime, time, date
from sqlalchemy import func
from app.models.user import User as UserModel
from app.models.product_template import ProductTemplate as ProductTemplateModel
from app.models.product import Product as ProductModel
from app.models.shift_template import ShiftTemplate as ShiftTemplateModel
from app.models.shift import Shift as ShiftModel
from app.models.shift_user import ShiftUser as ShiftUserModel
from app.models.product_slot import ProductSlot as ProductSlotModel
from app.models.product_slot_reading import ProductSlotReading as ProductSlotReadingModel
from app.schemas.user import UserType
from app.schemas.product_template import ProductTemplateType
from app.schemas.product import ProductType
from app.schemas.shift_template import ShiftTemplateType
from app.schemas.shift import ShiftType
from app.schemas.shift_user import ShiftUserType
from app.schemas.product_slot import ProductSlotType
from app.schemas.product_slot_reading import ProductSlotReadingType, StartReadingInput, EndReadingInput
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

    @strawberry.mutation(name="createShiftTemplate")
    def create_shift_template(
        self,
        shift_name: str,
        start_time: time,
        end_time: time,
        order: int,
        is_active: bool = True,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[int] = None,
        created_by: Optional[int] = None
    ) -> ShiftTemplateType:
        db = SessionLocal()
        db_shift_template = ShiftTemplateModel(
            shift_name=shift_name,
            start_time=start_time,
            end_time=end_time,
            order=order,
            is_active=is_active,
            deleted_at=deleted_at,
            deleted_by=deleted_by,
            created_by=created_by
        )
        db.add(db_shift_template)
        db.commit()
        db.refresh(db_shift_template)
        result = ShiftTemplateType(
            id=db_shift_template.id,
            shift_name=db_shift_template.shift_name,
            start_time=db_shift_template.start_time,
            end_time=db_shift_template.end_time,
            order=db_shift_template.order,
            is_active=db_shift_template.is_active,
            deleted_at=db_shift_template.deleted_at,
            deleted_by=db_shift_template.deleted_by,
            created_at=db_shift_template.created_at,
            created_by=db_shift_template.created_by,
            updated_at=db_shift_template.updated_at,
            updated_by=db_shift_template.updated_by
        )
        db.close()
        return result

    @strawberry.mutation(name="updateShiftTemplate")
    def update_shift_template(
        self,
        shift_template_id: int,
        shift_name: Optional[str] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        order: Optional[int] = None,
        is_active: Optional[bool] = None,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[int] = None,
        updated_by: Optional[int] = None
    ) -> Optional[ShiftTemplateType]:
        db = SessionLocal()
        db_shift_template = db.query(ShiftTemplateModel).filter(ShiftTemplateModel.id == shift_template_id).first()
        if db_shift_template:
            if shift_name is not None:
                db_shift_template.shift_name = shift_name
            if start_time is not None:
                db_shift_template.start_time = start_time
            if end_time is not None:
                db_shift_template.end_time = end_time
            if order is not None:
                db_shift_template.order = order
            if is_active is not None:
                db_shift_template.is_active = is_active
            if deleted_at is not None:
                db_shift_template.deleted_at = deleted_at
            if deleted_by is not None:
                db_shift_template.deleted_by = deleted_by
            
            # Always update updated_by when provided
            db_shift_template.updated_by = updated_by
            
            db.commit()
            db.refresh(db_shift_template)
            result = ShiftTemplateType(
                id=db_shift_template.id,
                shift_name=db_shift_template.shift_name,
                start_time=db_shift_template.start_time,
                end_time=db_shift_template.end_time,
                order=db_shift_template.order,
                is_active=db_shift_template.is_active,
                deleted_at=db_shift_template.deleted_at,
                deleted_by=db_shift_template.deleted_by,
                created_at=db_shift_template.created_at,
                created_by=db_shift_template.created_by,
                updated_at=db_shift_template.updated_at,
                updated_by=db_shift_template.updated_by
            )
        else:
            result = None
        db.close()
        return result

    @strawberry.mutation(name="deleteShiftTemplate")
    def delete_shift_template(self, shift_template_id: int, deleted_by: int) -> Optional[ShiftTemplateType]:
        db = SessionLocal()
        db_shift_template = db.query(ShiftTemplateModel).filter(ShiftTemplateModel.id == shift_template_id).first()
        if db_shift_template:
            # Cascading soft delete: Delete all related child records first
            
            # 1. Get all shifts for this template
            shifts = db.query(ShiftModel).filter(
                ShiftModel.shift_template_id == shift_template_id,
                ShiftModel.deleted_at.is_(None)
            ).all()
            
            for shift in shifts:
                # 1a. Soft delete all ShiftUser records for this shift
                shift_users = db.query(ShiftUserModel).filter(
                    ShiftUserModel.shift_id == shift.id,
                    ShiftUserModel.deleted_at.is_(None)
                ).all()
                for shift_user in shift_users:
                    shift_user.deleted_at = func.now()
                    shift_user.deleted_by = deleted_by
                
                # 1b. Soft delete all ProductSlotReading records for this shift
                readings = db.query(ProductSlotReadingModel).filter(
                    ProductSlotReadingModel.shift_id == shift.id,
                    ProductSlotReadingModel.deleted_at.is_(None)
                ).all()
                for reading in readings:
                    reading.deleted_at = func.now()
                    reading.deleted_by = deleted_by
                
                # 1c. Soft delete the shift
                shift.deleted_at = func.now()
                shift.deleted_by = deleted_by
            
            # 2. Soft delete the shift template itself
            db_shift_template.deleted_at = func.now()
            db_shift_template.deleted_by = deleted_by
            
            db.commit()
            db.refresh(db_shift_template)
            result = ShiftTemplateType(
                id=db_shift_template.id,
                shift_name=db_shift_template.shift_name,
                start_time=db_shift_template.start_time,
                end_time=db_shift_template.end_time,
                order=db_shift_template.order,
                is_active=db_shift_template.is_active,
                deleted_at=db_shift_template.deleted_at,
                deleted_by=db_shift_template.deleted_by,
                created_at=db_shift_template.created_at,
                created_by=db_shift_template.created_by,
                updated_at=db_shift_template.updated_at,
                updated_by=db_shift_template.updated_by
            )
        else:
            result = None
        db.close()
        return result

    @strawberry.mutation(name="createProductSlot")
    def create_product_slot(
        self,
        slot_name: str,
        product_id: Optional[int] = None,
        is_active: bool = True,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[int] = None,
        created_by: Optional[int] = None
    ) -> ProductSlotType:
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
        product_slot_id: int,
        slot_name: Optional[str] = None,
        product_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[int] = None,
        updated_by: Optional[int] = None
    ) -> Optional[ProductSlotType]:
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
    def delete_product_slot(self, product_slot_id: int, deleted_by: int) -> Optional[ProductSlotType]:
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

    @strawberry.mutation(name="startShift")
    def start_shift(
        self,
        shift_template_id: int,
        shift_date: date,
        user_ids: List[int],
        started_by: int,
        readings: List[StartReadingInput],
        created_by: Optional[int] = None
    ) -> ShiftType:
        db = SessionLocal()
        
        # Validate no active shift exists for this template
        existing_active_shift = db.query(ShiftModel).filter(
            ShiftModel.shift_template_id == shift_template_id,
            ShiftModel.status == "active"
        ).first()
        
        if existing_active_shift:
            db.close()
            raise ValueError(f"An active shift already exists for shift template {shift_template_id}")
        
        # Create Shift record
        db_shift = ShiftModel(
            shift_template_id=shift_template_id,
            shift_date=shift_date,
            actual_start_datetime=func.now(),
            started_by=started_by,
            status="active",
            created_by=created_by
        )
        db.add(db_shift)
        db.commit()
        db.refresh(db_shift)
        
        # Create ShiftUser records
        for user_id in user_ids:
            db_shift_user = ShiftUserModel(
                shift_id=db_shift.id,
                user_id=user_id,
                created_by=created_by
            )
            db.add(db_shift_user)
        
        # Create ProductSlotReading records
        for reading_input in readings:
            # Get product info from product_slot
            product_slot = db.query(ProductSlotModel).filter(
                ProductSlotModel.id == reading_input.product_slot_id
            ).first()
            
            if not product_slot or not product_slot.product_id:
                db.rollback()
                db.close()
                raise ValueError(f"Product slot {reading_input.product_slot_id} does not have a product assigned")
            
            # Get product pricing info
            product = db.query(ProductModel).filter(
                ProductModel.id == product_slot.product_id
            ).first()
            
            if not product:
                db.rollback()
                db.close()
                raise ValueError(f"Product {product_slot.product_id} not found")
            
            db_reading = ProductSlotReadingModel(
                shift_id=db_shift.id,
                product_slot_id=reading_input.product_slot_id,
                product_id=product.id,
                start_reading=reading_input.start_reading,
                start_reading_image_url=reading_input.start_reading_image_url,
                cost_price_snapshot=product.cost_price,
                selling_price_snapshot=product.selling_price,
                created_by=created_by
            )
            db.add(db_reading)
        
        db.commit()
        db.refresh(db_shift)
        
        result = ShiftType(
            id=db_shift.id,
            shift_template_id=db_shift.shift_template_id,
            shift_date=db_shift.shift_date,
            actual_start_datetime=db_shift.actual_start_datetime,
            actual_end_datetime=db_shift.actual_end_datetime,
            started_by=db_shift.started_by,
            ended_by=db_shift.ended_by,
            status=db_shift.status,
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
    
    @strawberry.mutation(name="endShift")
    def end_shift(
        self,
        shift_id: int,
        ended_by: int,
        readings: List[EndReadingInput],
        updated_by: Optional[int] = None
    ) -> ShiftType:
        db = SessionLocal()
        
        # Get the shift
        db_shift = db.query(ShiftModel).filter(ShiftModel.id == shift_id).first()
        
        if not db_shift:
            db.close()
            raise ValueError(f"Shift {shift_id} not found")
        
        if db_shift.status != "active":
            db.close()
            raise ValueError(f"Shift {shift_id} is not active (status: {db_shift.status})")
        
        # Update ProductSlotReading records with end readings
        for reading_input in readings:
            db_reading = db.query(ProductSlotReadingModel).filter(
                ProductSlotReadingModel.shift_id == shift_id,
                ProductSlotReadingModel.product_slot_id == reading_input.product_slot_id
            ).first()
            
            if not db_reading:
                db.rollback()
                db.close()
                raise ValueError(f"Reading for product slot {reading_input.product_slot_id} not found in shift {shift_id}")
            
            # Validate end_reading >= start_reading
            if reading_input.end_reading < float(db_reading.start_reading):
                db.rollback()
                db.close()
                raise ValueError(
                    f"End reading ({reading_input.end_reading}) must be greater than or equal to "
                    f"start reading ({float(db_reading.start_reading)}) for product slot {reading_input.product_slot_id}"
                )
            
            db_reading.end_reading = reading_input.end_reading
            db_reading.end_reading_image_url = reading_input.end_reading_image_url
            db_reading.updated_by = updated_by
        
        # Update shift to completed
        db_shift.actual_end_datetime = func.now()
        db_shift.ended_by = ended_by
        db_shift.status = "completed"
        db_shift.updated_by = updated_by
        
        db.commit()
        db.refresh(db_shift)
        
        result = ShiftType(
            id=db_shift.id,
            shift_template_id=db_shift.shift_template_id,
            shift_date=db_shift.shift_date,
            actual_start_datetime=db_shift.actual_start_datetime,
            actual_end_datetime=db_shift.actual_end_datetime,
            started_by=db_shift.started_by,
            ended_by=db_shift.ended_by,
            status=db_shift.status,
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
    
    @strawberry.mutation(name="deleteShift")
    def delete_shift(self, shift_id: int, deleted_by: int) -> Optional[ShiftType]:
        db = SessionLocal()
        db_shift = db.query(ShiftModel).filter(ShiftModel.id == shift_id).first()
        if db_shift:
            # Cascading soft delete: Delete all related child records first
            
            # 1. Soft delete all ShiftUser records for this shift
            shift_users = db.query(ShiftUserModel).filter(
                ShiftUserModel.shift_id == shift_id,
                ShiftUserModel.deleted_at.is_(None)
            ).all()
            for shift_user in shift_users:
                shift_user.deleted_at = func.now()
                shift_user.deleted_by = deleted_by
            
            # 2. Soft delete all ProductSlotReading records for this shift
            readings = db.query(ProductSlotReadingModel).filter(
                ProductSlotReadingModel.shift_id == shift_id,
                ProductSlotReadingModel.deleted_at.is_(None)
            ).all()
            for reading in readings:
                reading.deleted_at = func.now()
                reading.deleted_by = deleted_by
            
            # 3. Soft delete the shift itself
            db_shift.deleted_at = func.now()
            db_shift.deleted_by = deleted_by
            
            db.commit()
            db.refresh(db_shift)
            result = ShiftType(
                id=db_shift.id,
                shift_template_id=db_shift.shift_template_id,
                shift_date=db_shift.shift_date,
                actual_start_datetime=db_shift.actual_start_datetime,
                actual_end_datetime=db_shift.actual_end_datetime,
                started_by=db_shift.started_by,
                ended_by=db_shift.ended_by,
                status=db_shift.status,
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
    
    @strawberry.mutation(name="deleteShiftUser")
    def delete_shift_user(self, shift_user_id: int, deleted_by: int) -> Optional[ShiftUserType]:
        db = SessionLocal()
        db_shift_user = db.query(ShiftUserModel).filter(ShiftUserModel.id == shift_user_id).first()
        if db_shift_user:
            # Soft delete
            db_shift_user.deleted_at = func.now()
            db_shift_user.deleted_by = deleted_by
            db.commit()
            db.refresh(db_shift_user)
            result = ShiftUserType(
                id=db_shift_user.id,
                shift_id=db_shift_user.shift_id,
                user_id=db_shift_user.user_id,
                deleted_at=db_shift_user.deleted_at,
                deleted_by=db_shift_user.deleted_by,
                created_at=db_shift_user.created_at,
                created_by=db_shift_user.created_by,
                updated_at=db_shift_user.updated_at,
                updated_by=db_shift_user.updated_by
            )
        else:
            result = None
        db.close()
        return result
    
    @strawberry.mutation(name="deleteProductSlotReading")
    def delete_product_slot_reading(self, product_slot_reading_id: int, deleted_by: int) -> Optional[ProductSlotReadingType]:
        db = SessionLocal()
        db_reading = db.query(ProductSlotReadingModel).filter(ProductSlotReadingModel.id == product_slot_reading_id).first()
        if db_reading:
            # Soft delete
            db_reading.deleted_at = func.now()
            db_reading.deleted_by = deleted_by
            db.commit()
            db.refresh(db_reading)
            
            # Calculate computed properties
            quantity_sold = None
            if db_reading.end_reading is not None and db_reading.start_reading is not None:
                quantity_sold = float(db_reading.end_reading) - float(db_reading.start_reading)
            
            revenue_amount = None
            if quantity_sold is not None:
                revenue_amount = quantity_sold * float(db_reading.selling_price_snapshot)
            
            cost_amount = None
            if quantity_sold is not None:
                cost_amount = quantity_sold * float(db_reading.cost_price_snapshot)
            
            result = ProductSlotReadingType(
                id=db_reading.id,
                shift_id=db_reading.shift_id,
                product_slot_id=db_reading.product_slot_id,
                product_id=db_reading.product_id,
                start_reading=float(db_reading.start_reading),
                end_reading=float(db_reading.end_reading) if db_reading.end_reading is not None else None,
                start_reading_image_url=db_reading.start_reading_image_url,
                end_reading_image_url=db_reading.end_reading_image_url,
                cost_price_snapshot=float(db_reading.cost_price_snapshot),
                selling_price_snapshot=float(db_reading.selling_price_snapshot),
                quantity_sold=quantity_sold,
                revenue_amount=revenue_amount,
                cost_amount=cost_amount,
                deleted_at=db_reading.deleted_at,
                deleted_by=db_reading.deleted_by,
                created_at=db_reading.created_at,
                created_by=db_reading.created_by,
                updated_at=db_reading.updated_at,
                updated_by=db_reading.updated_by
            )
        else:
            result = None
        db.close()
        return result
