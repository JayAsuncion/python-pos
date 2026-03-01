from typing import Optional
from datetime import datetime
import strawberry


@strawberry.type
class RolePermissionType:
    id: int
    role_id: int
    permission_id: int
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    created_at: datetime
    created_by: Optional[int]
    updated_at: datetime
    updated_by: Optional[int]
