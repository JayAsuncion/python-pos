from typing import Optional
from datetime import datetime
import strawberry


@strawberry.type
class PermissionType:
    id: int
    code: str
    name: str
    description: Optional[str]
    category: str
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
