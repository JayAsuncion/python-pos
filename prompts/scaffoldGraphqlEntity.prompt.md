---
name: scaffoldGraphqlEntity
description: Create complete entity with model, schema, GraphQL endpoints, migration, and Postman collection
argument-hint: entity name and fields (e.g., "shift with shift_name, start_time, end_time")
---

Create a new entity for the specified name with all necessary components following the project's established patterns.

**First, gather requirements if not provided:**
- Entity name
- Field names and their data types
- Which fields are required vs optional
- Any relationships to other entities
- Any special constraints or validation rules

If any of these details are missing, ask the user before proceeding.

## Code Patterns (Use these directly without reading existing files)

### 1. SQLAlchemy Model Pattern (`app/models/{entity}.py`)
```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base

class EntityName(Base):
    __tablename__ = "entity_name"

    id = Column(Integer, primary_key=True, index=True)
    # Add entity-specific fields here
    field_name = Column(String, nullable=False)
    foreign_key_id = Column(Integer, ForeignKey("other_table.id"), nullable=True)
    
    # Standard audit fields (always include these)
    is_active = Column(Boolean, default=True)
    deleted_at = Column(PG_TIMESTAMP(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(Integer, nullable=True)

    # Relationships (if applicable)
    related_entity = relationship("RelatedEntity", backref="entity_names")
```

**Data Type Mappings:**
- String fields → `Column(String, nullable=False/True)`
- Integer fields → `Column(Integer, nullable=False/True)`
- Decimal/Money → `Column(Numeric(15, 6), nullable=False/True)`
- Boolean → `Column(Boolean, default=True)`
- Foreign keys → `Column(Integer, ForeignKey("table.id"), nullable=False/True)`
- Timestamps → `Column(PG_TIMESTAMP(timezone=True), nullable=True)`
- Time only → `Column(Time(timezone=True), nullable=True)` (import Time from sqlalchemy)

### 2. Strawberry Schema Pattern (`app/schemas/{entity}.py`)
```python
from typing import Optional
from datetime import datetime
import strawberry

@strawberry.type
class EntityNameType:
    id: int
    # Add entity-specific fields (use camelCase in GraphQL, but field names match model)
    field_name: str
    foreign_key_id: Optional[int]
    
    # Standard audit fields (always include these)
    is_active: bool
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    created_at: datetime
    created_by: Optional[int]
    updated_at: datetime
    updated_by: Optional[int]
```

**GraphQL Type Mappings:**
- String → `str`
- Integer → `int`
- Numeric/Decimal → `float` (convert in queries/mutations with `float()`)
- Boolean → `bool`
- Optional fields → `Optional[type]`
- Timestamps → `datetime` or `Optional[datetime]`

**Note:** Use snake_case for field names in Python model, but camelCase in GraphQL queries/mutations.

## Implementation Steps

1. **Create Model File** (`app/models/{entity}.py`)
   - Follow the SQLAlchemy model pattern above
   - Include all standard audit fields

2. **Create Schema File** (`app/schemas/{entity}.py`)
   - Follow the Strawberry schema pattern above
   - Use Optional for nullable fields

3. **Update Import Files:**
   - Add `from .{entity} import *` to `app/models/__init__.py`
   - Add import to `alembic/env.py`: `from app.models.{entity} import EntityName`

4. **Update GraphQL Files:**
   - Add model and schema imports to `app/graphql/queries.py` and `app/graphql/mutations.py`
   - Create query methods: `{entities}()` for list, `{entity}(entity_id)` for single record
   - Create mutation methods: `create{Entity}()`, `update{Entity}()`, `delete{Entity}()`
   - Follow existing patterns in these files for implementation details

5. **Generate & Apply Migration:**
   ```bash
   source python-pos-env-39/Scripts/activate
   export $(grep -v '^#' .env | xargs)
   alembic revision --autogenerate -m "create_{entity}_table"
   alembic upgrade head
   ```

6. **Create Postman Collection** (`testing/postman/{Entity Name}.postman_collection.json`)
   - Follow existing collection patterns with all 5 requests: Get All, Get By ID, Create, Update, Delete
   - Use `{{baseURL}}/graphql` endpoint

7. **Restart Service:**
   ```bash
   docker-compose restart web
   ```

8. **Verify:** Check for errors with `get_errors` tool

## Naming Conventions
- Model class: PascalCase (e.g., `ProductSlot`)
- Table name: snake_case (e.g., `product_slot`)
- Python fields: snake_case (e.g., `slot_name`)
- GraphQL fields: camelCase (e.g., `slotName`)
- GraphQL types: PascalCase with "Type" suffix (e.g., `ProductSlotType`)
- Query names: camelCase, plural/singular (e.g., `productSlots`, `productSlot`)
- Mutation names: camelCase with verb prefix (e.g., `createProductSlot`)
- Parameter names in queries: entity_name + "_id" (e.g., `product_slot_id`)

## Key Learnings
- Always use `multi_replace_string_in_file` for multiple independent edits
- Field mappings: Numeric columns convert to float in GraphQL with `float(value)`
- Always close database sessions with `db.close()`
- Update mutations must handle `updated_by` even when not in conditional checks
- Postman collection needs unique `_postman_id` for each collection
