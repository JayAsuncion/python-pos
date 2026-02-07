from typing import Optional
from datetime import datetime
from decimal import Decimal
import strawberry

@strawberry.type
class ProductType:
    id: int
    product_template_id: int
    name: str
    code: str
    image: Optional[str]
    starting_stock: float
    running_stock: float
    cost_price: float
    selling_price: float
    is_active: bool
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    created_at: datetime
    created_by: Optional[int]
    updated_at: datetime
    updated_by: Optional[int]
