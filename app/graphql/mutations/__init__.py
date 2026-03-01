import strawberry
from .auth import AuthMutations
from .user import UserMutations
from .product_template import ProductTemplateMutations
from .product import ProductMutations
from .shift_template import ShiftTemplateMutations
from .product_slot import ProductSlotMutations
from .shift import ShiftMutations
from .shift_user import ShiftUserMutations
from .product_slot_reading import ProductSlotReadingMutations
from .permission import PermissionMutations
from .role import RoleMutations
from .user_role import UserRoleMutations
from .role_permission import RolePermissionMutations


@strawberry.type
class Mutation(
    AuthMutations,
    UserMutations,
    ProductTemplateMutations,
    ProductMutations,
    ShiftTemplateMutations,
    ProductSlotMutations,
    ShiftMutations,
    ShiftUserMutations,
    ProductSlotReadingMutations,
    PermissionMutations,
    RoleMutations,
    UserRoleMutations,
    RolePermissionMutations,
):
    """
    Aggregated mutations from all entities.
    
    This class inherits from all entity-specific mutation classes,
    combining their mutations into a single GraphQL Mutation type.
    """
    pass
