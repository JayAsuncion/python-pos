from typing import Optional
from datetime import datetime
import strawberry

@strawberry.type
class ProductSlotType:
    id: int
    slot_name: str
    product_id: Optional[int]
    is_active: bool
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    created_at: datetime
    created_by: Optional[int]
    updated_at: datetime
    updated_by: Optional[int]
