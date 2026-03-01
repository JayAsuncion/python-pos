from typing import Optional
from datetime import datetime
import strawberry


@strawberry.type
class RoleType:
    id: int
    code: str
    name: str
    description: Optional[str]
    is_system_role: bool
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
