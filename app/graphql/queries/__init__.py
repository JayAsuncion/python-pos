import strawberry
from .auth import AuthQueries
from .user import UserQueries
from .product_template import ProductTemplateQueries
from .product import ProductQueries
from .shift_template import ShiftTemplateQueries
from .product_slot import ProductSlotQueries
from .shift import ShiftQueries
from .permission import PermissionQueries
from .role import RoleQueries
from .user_role import UserRoleQueries
from .role_permission import RolePermissionQueries


@strawberry.type
class Query(
    AuthQueries,
    UserQueries,
    ProductTemplateQueries,
    ProductQueries,
    ShiftTemplateQueries,
    ProductSlotQueries,
    ShiftQueries,
    PermissionQueries,
    RoleQueries,
    UserRoleQueries,
    RolePermissionQueries,
):
    """
    Aggregated queries from all entities.
    
    This class inherits from all entity-specific query classes,
    combining their queries into a single GraphQL Query type.
    """
    pass
