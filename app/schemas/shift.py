from typing import Optional
from datetime import datetime, time
import strawberry

@strawberry.type
class ShiftType:
    id: int
    shift_name: str
    start_time: time
    end_time: time
    is_active: bool
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    created_at: datetime
    created_by: Optional[int]
    updated_at: datetime
    updated_by: Optional[int]
