from typing import Optional
from datetime import datetime
import strawberry

@strawberry.input
class StartReadingInput:
    product_slot_id: int
    start_reading: float
    start_reading_image_url: str

@strawberry.input
class EndReadingInput:
    product_slot_id: int
    end_reading: float
    end_reading_image_url: str

@strawberry.type
class ProductSlotReadingType:
    id: int
    shift_id: int
    product_slot_id: int
    product_id: int
    start_reading: float
    end_reading: Optional[float]
    start_reading_image_url: str
    end_reading_image_url: Optional[str]
    cost_price_snapshot: float
    selling_price_snapshot: float
    quantity_sold: Optional[float]  # Computed: end_reading - start_reading
    revenue_amount: Optional[float]  # Computed: quantity_sold * selling_price_snapshot
    cost_amount: Optional[float]  # Computed: quantity_sold * cost_price_snapshot
    voided_at: Optional[datetime]
    voided_by: Optional[int]
    void_reason: Optional[str]
    created_at: datetime
    created_by: Optional[int]
    updated_at: datetime
    updated_by: Optional[int]
