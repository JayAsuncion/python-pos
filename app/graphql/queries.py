import strawberry
from typing import List, Optional
from datetime import date
from app.models.user import User as UserModel
from app.models.product_template import ProductTemplate as ProductTemplateModel
from app.models.product import Product as ProductModel
from app.models.shift_template import ShiftTemplate as ShiftTemplateModel
from app.models.shift import Shift as ShiftModel
from app.models.product_slot import ProductSlot as ProductSlotModel
from app.schemas.user import UserType
from app.schemas.product_template import ProductTemplateType
from app.schemas.product import ProductType
from app.schemas.shift_template import ShiftTemplateType
from app.schemas.shift import ShiftType
from app.schemas.product_slot import ProductSlotType
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
            deleted_at=product.deleted_at,
            deleted_by=product.deleted_by
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
                deleted_at=product.deleted_at,
                deleted_by=product.deleted_by
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
                deleted_at=product.deleted_at,
                deleted_by=product.deleted_by,
                created_at=product.created_at,
                created_by=product.created_by,
                updated_at=product.updated_at,
                updated_by=product.updated_by
            )
        return None

    @strawberry.field
    def shift_templates(self) -> List[ShiftTemplateType]:
        db = SessionLocal()
        shift_templates = db.query(ShiftTemplateModel).all()
        db.close()
        return [ShiftTemplateType(
            id=shift_template.id,
            shift_name=shift_template.shift_name,
            start_time=shift_template.start_time,
            end_time=shift_template.end_time,
            order=shift_template.order,
            is_active=shift_template.is_active,
            deleted_at=shift_template.deleted_at,
            deleted_by=shift_template.deleted_by,
            created_at=shift_template.created_at,
            created_by=shift_template.created_by,
            updated_at=shift_template.updated_at,
            updated_by=shift_template.updated_by
        ) for shift_template in shift_templates]

    @strawberry.field
    def shift_template(self, shift_template_id: int) -> Optional[ShiftTemplateType]:
        db = SessionLocal()
        shift_template = db.query(ShiftTemplateModel).filter(ShiftTemplateModel.id == shift_template_id).first()
        db.close()
        if shift_template:
            return ShiftTemplateType(
                id=shift_template.id,
                shift_name=shift_template.shift_name,
                start_time=shift_template.start_time,
                end_time=shift_template.end_time,
                order=shift_template.order,
                is_active=shift_template.is_active,
                deleted_at=shift_template.deleted_at,
                deleted_by=shift_template.deleted_by,
                created_at=shift_template.created_at,
                created_by=shift_template.created_by,
                updated_at=shift_template.updated_at,
                updated_by=shift_template.updated_by
            )
        return None

    @strawberry.field
    def product_slots(self) -> List[ProductSlotType]:
        db = SessionLocal()
        product_slots = db.query(ProductSlotModel).all()
        db.close()
        return [ProductSlotType(
            id=product_slot.id,
            slot_name=product_slot.slot_name,
            product_id=product_slot.product_id,
            is_active=product_slot.is_active,
            deleted_at=product_slot.deleted_at,
            deleted_by=product_slot.deleted_by,
            created_at=product_slot.created_at,
            created_by=product_slot.created_by,
            updated_at=product_slot.updated_at,
            updated_by=product_slot.updated_by
        ) for product_slot in product_slots]

    @strawberry.field
    def product_slot(self, product_slot_id: int) -> Optional[ProductSlotType]:
        db = SessionLocal()
        product_slot = db.query(ProductSlotModel).filter(ProductSlotModel.id == product_slot_id).first()
        db.close()
        if product_slot:
            return ProductSlotType(
                id=product_slot.id,
                slot_name=product_slot.slot_name,
                product_id=product_slot.product_id,
                is_active=product_slot.is_active,
                deleted_at=product_slot.deleted_at,
                deleted_by=product_slot.deleted_by,
                created_at=product_slot.created_at,
                created_by=product_slot.created_by,
                updated_at=product_slot.updated_at,
                updated_by=product_slot.updated_by
            )
        return None

    @strawberry.field
    def shifts(
        self,
        shift_date: Optional[date] = None,
        shift_template_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[ShiftType]:
        db = SessionLocal()
        query = db.query(ShiftModel)
        
        if shift_date is not None:
            query = query.filter(ShiftModel.shift_date == shift_date)
        if shift_template_id is not None:
            query = query.filter(ShiftModel.shift_template_id == shift_template_id)
        if status is not None:
            query = query.filter(ShiftModel.status == status)
        
        shifts = query.all()
        db.close()
        return [ShiftType(
            id=shift.id,
            shift_template_id=shift.shift_template_id,
            shift_date=shift.shift_date,
            actual_start_datetime=shift.actual_start_datetime,
            actual_end_datetime=shift.actual_end_datetime,
            started_by=shift.started_by,
            ended_by=shift.ended_by,
            status=shift.status,
            is_active=shift.is_active,
            deleted_at=shift.deleted_at,
            deleted_by=shift.deleted_by,
            created_at=shift.created_at,
            created_by=shift.created_by,
            updated_at=shift.updated_at,
            updated_by=shift.updated_by
        ) for shift in shifts]

    @strawberry.field
    def shift(self, shift_id: int) -> Optional[ShiftType]:
        db = SessionLocal()
        shift = db.query(ShiftModel).filter(ShiftModel.id == shift_id).first()
        db.close()
        if shift:
            return ShiftType(
                id=shift.id,
                shift_template_id=shift.shift_template_id,
                shift_date=shift.shift_date,
                actual_start_datetime=shift.actual_start_datetime,
                actual_end_datetime=shift.actual_end_datetime,
                started_by=shift.started_by,
                ended_by=shift.ended_by,
                status=shift.status,
                is_active=shift.is_active,
                deleted_at=shift.deleted_at,
                deleted_by=shift.deleted_by,
                created_at=shift.created_at,
                created_by=shift.created_by,
                updated_at=shift.updated_at,
                updated_by=shift.updated_by
            )
        return None

    @strawberry.field
    def active_shift(self, shift_template_id: int) -> Optional[ShiftType]:
        db = SessionLocal()
        shift = db.query(ShiftModel).filter(
            ShiftModel.shift_template_id == shift_template_id,
            ShiftModel.status == "active"
        ).first()
        db.close()
        if shift:
            return ShiftType(
                id=shift.id,
                shift_template_id=shift.shift_template_id,
                shift_date=shift.shift_date,
                actual_start_datetime=shift.actual_start_datetime,
                actual_end_datetime=shift.actual_end_datetime,
                started_by=shift.started_by,
                ended_by=shift.ended_by,
                status=shift.status,
                is_active=shift.is_active,
                deleted_at=shift.deleted_at,
                deleted_by=shift.deleted_by,
                created_at=shift.created_at,
                created_by=shift.created_by,
                updated_at=shift.updated_at,
                updated_by=shift.updated_by
            )
        return None