from typing import Optional
from datetime import datetime
import strawberry

@strawberry.type
class ProductTemplateType:
    id: int
    name: str
    code: str
    image: Optional[str]
    is_active: bool
    is_deleted_at: Optional[datetime]
    is_deleted_by: Optional[int]
