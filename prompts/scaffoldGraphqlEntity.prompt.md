---
name: scaffoldGraphqlEntity
description: Create complete entity with model, schema, GraphQL endpoints, migration, and Postman collection
argument-hint: entity name and fields (e.g., "shift with shift_name, start_time, end_time")
---

## Prerequisites

**⚠️ MANDATORY READING:**
1. **[`prompts/AGENTS.md`](AGENTS.md)** - Critical instructions for entity changes
2. **[`prompts/entity-context.md`](entity-context.md)** - Current entity documentation

Before creating any new entity, read these files to understand:
- Existing entities and their relationships
- Naming conventions and patterns
- Audit trail levels (no audit, soft delete, full audit)
- Business rules and constraints
- How the new entity fits into the overall data model
- **Your responsibility to update documentation after creating entities**

This ensures consistency and helps avoid conflicts with existing entities.

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

4. **Create Entity-Specific GraphQL Files:**
   
   **a) Create Mutations File** (`app/graphql/mutations/{entity}.py`):
   ```python
   import strawberry
   from typing import Optional
   from app.models.{entity} import EntityName as EntityModel
   from app.schemas.{entity} import EntityNameType
   from app.auth.permissions import require_permission
   from app.database import SessionLocal

   @strawberry.type
   class EntityNameMutations:
       @strawberry.mutation(name="createEntityName")
       def create_entity_name(
           self,
           info: strawberry.types.Info,
           field1: str,
           field2: int,
           ...
       ) -> EntityNameType:
           # RBAC: Require permission before proceeding
           user = require_permission(info, "CREATE_ENTITY_NAME")
           
           db = SessionLocal()
           # Implementation - include created_by from authenticated user
           entity = EntityModel(
               field1=field1,
               field2=field2,
               created_by=user.id
           )
           db.add(entity)
           db.commit()
           db.refresh(entity)
           db.close()
           return result
       
       @strawberry.mutation(name="updateEntityName")
       def update_entity_name(
           self,
           info: strawberry.types.Info,
           entity_id: int,
           ...
       ) -> Optional[EntityNameType]:
           # RBAC: Require permission before proceeding
           user = require_permission(info, "UPDATE_ENTITY_NAME")
           
           db = SessionLocal()
           # Implementation - include updated_by from authenticated user
           entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
           if entity:
               # Update fields
               entity.updated_by = user.id
               db.commit()
           db.close()
           return result
       
       @strawberry.mutation(name="deleteEntityName")
       def delete_entity_name(
           self,
           info: strawberry.types.Info,
           entity_id: int
       ) -> Optional[EntityNameType]:
           # RBAC: Require permission before proceeding
           user = require_permission(info, "DELETE_ENTITY_NAME")
           
           db = SessionLocal()
           # Soft delete implementation - include deleted_by from authenticated user
           entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
           if entity:
               entity.deleted_at = func.now()
               entity.deleted_by = user.id
               db.commit()
           db.close()
           return result
   ```
   
   **b) Create Queries File** (`app/graphql/queries/{entity}.py`):
   ```python
   import strawberry
   from typing import List, Optional
   from app.models.{entity} import EntityName as EntityModel
   from app.schemas.{entity} import EntityNameType
   from app.auth.permissions import require_permission
   from app.database import SessionLocal

   @strawberry.type
   class EntityNameQueries:
       @strawberry.field
       def entity_names(self, info: strawberry.types.Info) -> List[EntityNameType]:
           # RBAC: Require permission before proceeding
           require_permission(info, "VIEW_ENTITY_NAME")
           
           db = SessionLocal()
           # Implementation for list query
           entities = db.query(EntityModel).filter(EntityModel.deleted_at.is_(None)).all()
           db.close()
           return results
       
       @strawberry.field
       def entity_name(self, info: strawberry.types.Info, entity_id: int) -> Optional[EntityNameType]:
           # RBAC: Require permission before proceeding
           require_permission(info, "VIEW_ENTITY_NAME")
           
           db = SessionLocal()
           # Implementation for single entity query
           entity = db.query(EntityModel).filter(
               EntityModel.id == entity_id,
               EntityModel.deleted_at.is_(None)
           ).first()
           db.close()
           return result
   ```
   
   **c) Update Aggregator Files:**
   - Add import to `app/graphql/mutations/__init__.py`:
     ```python
     from .{entity} import EntityNameMutations
     ```
     And add `EntityNameMutations` to the `Mutation` class inheritance list
   
   - Add import to `app/graphql/queries/__init__.py`:
     ```python
     from .{entity} import EntityNameQueries
     ```
     And add `EntityNameQueries` to the `Query` class inheritance list

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

9. **⚠️ UPDATE DOCUMENTATION (MANDATORY):**
   - Open [`prompts/entity-context.md`](entity-context.md)
   - Add complete documentation for your new entity following the template in [`prompts/AGENTS.md`](AGENTS.md)
   - Update the relationship diagram if needed
   - Document any business workflows or special validation rules
   - Update the "Last Updated" date at the top of `entity-context.md`
   - **This step is NOT optional** - see [`prompts/AGENTS.md`](AGENTS.md) for details

## Naming Conventions
- Model class: PascalCase (e.g., `ProductSlot`)
- Table name: snake_case (e.g., `product_slot`)
- Python fields: snake_case (e.g., `slot_name`)
- GraphQL fields: camelCase (e.g., `slotName`)
- GraphQL types: PascalCase with "Type" suffix (e.g., `ProductSlotType`)
- GraphQL class names: PascalCase with "Mutations" or "Queries" suffix (e.g., `ProductSlotMutations`, `ProductSlotQueries`)
- Query names: camelCase, plural/singular (e.g., `productSlots`, `productSlot`)
- Mutation names: camelCase with verb prefix (e.g., `createProductSlot`)
- Parameter names in queries: entity_name + "_id" (e.g., `product_slot_id`)
- File names: snake_case matching entity name (e.g., `product_slot.py`)

## RBAC (Role-Based Access Control) Requirements

**⚠️ MANDATORY:** Every query and mutation MUST implement permission checks using the `require_permission` function.

### Permission Naming Convention
Permissions follow the pattern: `{ACTION}_{ENTITY_NAME}`
- Actions: `CREATE`, `UPDATE`, `DELETE`, `VIEW`
- Entity name: SCREAMING_SNAKE_CASE (e.g., `USER`, `PRODUCT_SLOT`)
- Examples: `CREATE_USER`, `VIEW_PRODUCT`, `DELETE_SHIFT_TEMPLATE`

### Implementation Pattern

**1. Import the permission helper:**
```python
from app.auth.permissions import require_permission
```

**2. Add `info: strawberry.types.Info` parameter:**
Every query and mutation must accept the `info` parameter as the first parameter after `self`.

**3. Call `require_permission` at the start:**
```python
# For mutations that need the authenticated user (create, update, delete):
user = require_permission(info, "CREATE_ENTITY_NAME")
# Use user.id for created_by, updated_by, deleted_by

# For queries (when you don't need the user object):
require_permission(info, "VIEW_ENTITY_NAME")
```

**4. Use the returned user for audit fields:**
- `created_by=user.id` in create operations
- `updated_by=user.id` in update operations  
- `deleted_by=user.id` in delete operations

### Permission Seeding
After creating a new entity, you must add its permissions to `app/auth/seed_permissions.py`:

```python
permissions.extend([
    {"code": "CREATE_ENTITY_NAME", "name": "Create Entity Name", "category": "ENTITY_NAME"},
    {"code": "VIEW_ENTITY_NAME", "name": "View Entity Name", "category": "ENTITY_NAME"},
    {"code": "UPDATE_ENTITY_NAME", "name": "Update Entity Name", "category": "ENTITY_NAME"},
    {"code": "DELETE_ENTITY_NAME", "name": "Delete Entity Name", "category": "ENTITY_NAME"},
])
```

Then run the seeding script to add permissions to the database:
```bash
python -m app.auth.seed_permissions
```

### Exception: Login Mutation
The only mutation that does NOT require authentication is the `login` mutation in `app/graphql/mutations/auth.py`.

## GraphQL Organization (Entity-Based Structure)
The GraphQL layer is organized by entity for better maintainability:

- **Mutations**: Each entity has its own file in `app/graphql/mutations/{entity}.py`
  - Contains a single class `{Entity}Mutations` with all mutations for that entity
  - Aggregated in `app/graphql/mutations/__init__.py` via class inheritance
  
- **Queries**: Each entity has its own file in `app/graphql/queries/{entity}.py`
  - Contains a single class `{Entity}Queries` with all queries for that entity
  - Aggregated in `app/graphql/queries/__init__.py` via class inheritance

**Benefits:**
- Files are 50-150 lines (manageable)
- Easy to locate entity-specific logic
- Better for team collaboration (fewer merge conflicts)
- Consistent with models/ and schemas/ structure

## Key Learnings
- Always use `multi_replace_string_in_file` for multiple independent edits
- Field mappings: Numeric columns convert to float in GraphQL with `float(value)`
- Always close database sessions with `db.close()`
- Update mutations must handle `updated_by` even when not in conditional checks
- Postman collection needs unique `_postman_id` for each collection
- Each entity gets its own mutations and queries file for better organization
