import strawberry
from .user import UserQueries
from .product_template import ProductTemplateQueries
from .product import ProductQueries
from .shift_template import ShiftTemplateQueries
from .product_slot import ProductSlotQueries
from .shift import ShiftQueries


@strawberry.type
class Query(
    UserQueries,
    ProductTemplateQueries,
    ProductQueries,
    ShiftTemplateQueries,
    ProductSlotQueries,
    ShiftQueries,
):
    """
    Aggregated queries from all entities.
    
    This class inherits from all entity-specific query classes,
    combining their queries into a single GraphQL Query type.
    """
    pass
