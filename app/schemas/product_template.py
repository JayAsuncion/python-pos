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
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
