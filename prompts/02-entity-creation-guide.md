# Entity Creation Guide

**Purpose:** Step-by-step guide for creating, modifying, and deleting entities

**Last Updated:** March 22, 2026

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step-by-Step Creation Process](#step-by-step-creation-process)
3. [Code Patterns](#code-patterns)
4. [RBAC Implementation](#rbac-implementation)
5. [Testing & Verification](#testing--verification)
6. [Documentation Requirements](#documentation-requirements-mandatory)
7. [Common Pitfalls](#common-pitfalls)

---

## Prerequisites

### ⚠️ MANDATORY READING BEFORE STARTING

**Before creating ANY new entity, you MUST:**

1. **Read [01-entity-reference.md](01-entity-reference.md)** to understand:
   - All existing entities and their relationships
   - Naming conventions and patterns
   - Audit trail levels (no audit, soft delete, full audit)
   - Business rules and constraints

2. **Verify:**
   - Your new entity doesn't duplicate existing functionality
   - You understand which entities it will relate to
   - You've chosen the appropriate audit trail level

3. **Plan:**
   - Entity name and purpose
   - Field names and data types
   - Required vs optional fields
   - Relationships to other entities
   - Business rules and validation
   - Permission codes needed

**If you skip this step, you risk:**
- Creating duplicate entities
- Breaking existing relationships
- Introducing inconsistencies
- Choosing wrong audit patterns

---

## Step-by-Step Creation Process

### Step 1: Create SQLAlchemy Model

**File:** `app/models/{entity}.py`

**Choose your audit pattern:**

<details>
<summary><b>Option A: No Audit (User pattern)</b></summary>

```python
from sqlalchemy import Column, Integer, String
from app.database import Base

class EntityName(Base):
    __tablename__ = "entity_name"

    id = Column(Integer, primary_key=True, index=True)
    field_name = Column(String, nullable=False)
    # Add other fields...

    def __repr__(self):
        return f"<EntityName(id={self.id}, field_name={self.field_name})>"
```
</details>

<details>
<summary><b>Option B: Soft Delete Only (ProductTemplate pattern)</b></summary>

```python
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from app.database import Base

class EntityName(Base):
    __tablename__ = "entity_name"

    id = Column(Integer, primary_key=True, index=True)
    field_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Soft delete fields
    deleted_at = Column(PG_TIMESTAMP(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<EntityName(id={self.id}, field_name={self.field_name})>"
```
</details>

<details>
<summary><b>Option C: Full Audit Trail (Product pattern) - RECOMMENDED</b></summary>

```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base

class EntityName(Base):
    __tablename__ = "entity_name"

    id = Column(Integer, primary_key=True, index=True)
    field_name = Column(String, nullable=False)
    foreign_key_id = Column(Integer, ForeignKey("other_table.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Full audit fields
    deleted_at = Column(PG_TIMESTAMP(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(Integer, nullable=True)

    # Relationships (if applicable)
    related_entity = relationship("RelatedEntity", backref="entity_names")

    def __repr__(self):
        return f"<EntityName(id={self.id}, field_name={self.field_name})>"
```
</details>

**Data Type Mappings:**
- String fields → `Column(String, nullable=False/True)`
- Integer fields → `Column(Integer, nullable=False/True)`
- Decimal/Money → `Column(Numeric(15, 6), nullable=False/True)`
- Boolean → `Column(Boolean, default=True)`
- Foreign keys → `Column(Integer, ForeignKey("table.id"), nullable=False/True)`
- Timestamps → `Column(PG_TIMESTAMP(timezone=True), nullable=True)`
- Time only → `Column(Time(timezone=True), nullable=True)` (import Time from sqlalchemy)

---

### Step 2: Create Strawberry GraphQL Schema

**File:** `app/schemas/{entity}.py`

```python
from typing import Optional
from datetime import datetime
import strawberry

@strawberry.type
class EntityNameType:
    id: int
    # Add entity-specific fields (match model)
    field_name: str
    foreign_key_id: Optional[int]
    is_active: bool
    
    # Audit fields (include based on your chosen pattern)
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
- Numeric/Decimal → `float` (convert with `float()` in resolvers)
- Boolean → `bool`
- Optional fields → `Optional[type]`
- Timestamps → `datetime` or `Optional[datetime]`

---

### Step 3: Create GraphQL Mutations

**File:** `app/graphql/mutations/{entity}.py`

```python
import strawberry
from typing import Optional
from sqlalchemy import func
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
        # ... other fields
    ) -> EntityNameType:
        # 🔒 RBAC: Require permission
        user = require_permission(info, "CREATE_ENTITY_NAME")
        
        db = SessionLocal()
        
        # Add validation if needed
        # if invalid_condition:
        #     db.close()
        #     raise ValueError("Descriptive error message")
        
        entity = EntityModel(
            field1=field1,
            field2=field2,
            created_by=user.id  # Use authenticated user for audit
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
        
        result = EntityNameType(
            id=entity.id,
            field_name=entity.field_name,
            # Map all fields...
            created_at=entity.created_at,
            created_by=entity.created_by,
            updated_at=entity.updated_at,
            updated_by=entity.updated_by,
        )
        db.close()
        return result
    
    @strawberry.mutation(name="updateEntityName")
    def update_entity_name(
        self,
        info: strawberry.types.Info,
        entity_id: int,
        field1: Optional[str] = None,
        field2: Optional[int] = None,
        # ... other optional fields
    ) -> Optional[EntityNameType]:
        # 🔒 RBAC: Require permission
        user = require_permission(info, "UPDATE_ENTITY_NAME")
        
        db = SessionLocal()
        entity = (
            db.query(EntityModel)
            .filter(EntityModel.id == entity_id, EntityModel.deleted_at.is_(None))
            .first()
        )
        
        if not entity:
            db.close()
            return None
        
        # Update fields only if provided
        if field1 is not None:
            entity.field1 = field1
        if field2 is not None:
            entity.field2 = field2
        
        entity.updated_by = user.id  # Track who updated
        db.commit()
        db.refresh(entity)
        
        result = EntityNameType(
            id=entity.id,
            field_name=entity.field_name,
            # Map all fields...
        )
        db.close()
        return result
    
    @strawberry.mutation(name="deleteEntityName")
    def delete_entity_name(
        self,
        info: strawberry.types.Info,
        entity_id: int
    ) -> Optional[EntityNameType]:
        # 🔒 RBAC: Require permission
        user = require_permission(info, "DELETE_ENTITY_NAME")
        
        db = SessionLocal()
        entity = (
            db.query(EntityModel)
            .filter(EntityModel.id == entity_id, EntityModel.deleted_at.is_(None))
            .first()
        )
        
        if not entity:
            db.close()
            return None
        
        # Soft delete
        entity.deleted_at = func.now()
        entity.deleted_by = user.id  # Track who deleted
        entity.updated_by = user.id
        db.commit()
        db.refresh(entity)
        
        result = EntityNameType(
            id=entity.id,
            field_name=entity.field_name,
            # Map all fields...
        )
        db.close()
        return result
```

---

### Step 4: Create GraphQL Queries

**File:** `app/graphql/queries/{entity}.py`

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
        # 🔒 RBAC: Require permission
        require_permission(info, "VIEW_ENTITY_NAME")
        
        db = SessionLocal()
        entities = db.query(EntityModel).filter(EntityModel.deleted_at.is_(None)).all()
        db.close()
        
        return [
            EntityNameType(
                id=e.id,
                field_name=e.field_name,
                # Map all fields...
            )
            for e in entities
        ]
    
    @strawberry.field
    def entity_name(
        self, info: strawberry.types.Info, entity_id: int
    ) -> Optional[EntityNameType]:
        # 🔒 RBAC: Require permission
        require_permission(info, "VIEW_ENTITY_NAME")
        
        db = SessionLocal()
        entity = (
            db.query(EntityModel)
            .filter(EntityModel.id == entity_id, EntityModel.deleted_at.is_(None))
            .first()
        )
        db.close()
        
        if not entity:
            return None
        
        return EntityNameType(
            id=entity.id,
            field_name=entity.field_name,
            # Map all fields...
        )
```

---

### Step 5: Update Aggregator Files

**Add imports to `app/graphql/mutations/__init__.py`:**

```python
from .{entity} import EntityNameMutations

@strawberry.type
class Mutation(
    # ... existing mutations ...
    EntityNameMutations,  # Add this line
):
    pass
```

**Add imports to `app/graphql/queries/__init__.py`:**

```python
from .{entity} import EntityNameQueries

@strawberry.type
class Query(
    # ... existing queries ...
    EntityNameQueries,  # Add this line
):
    pass
```

---

### Step 6: Update Model Imports

**Add to `app/models/__init__.py`:**

```python
from .{entity} import *
```

**Add to `alembic/env.py`:**

```python
from app.models.{entity} import EntityName
```

---

### Step 7: Add Permissions

**Edit `app/auth/seed_permissions.py`:**

Add to `BASE_PERMISSIONS` list:

```python
BASE_PERMISSIONS = [
    # ... existing permissions ...
    
    # EntityName
    ("VIEW_ENTITY_NAME", "View Entity Names", "Can view entity name list and details", "ENTITY_NAME"),
    ("CREATE_ENTITY_NAME", "Create Entity Name", "Can create new entity names", "ENTITY_NAME"),
    ("UPDATE_ENTITY_NAME", "Update Entity Name", "Can update entity name details", "ENTITY_NAME"),
    ("DELETE_ENTITY_NAME", "Delete Entity Name", "Can delete entity names", "ENTITY_NAME"),
]
```

**Run permission seeding:**

```bash
source python-pos-env-39/Scripts/activate
export $(grep -v '^#' .env | xargs)
python -m app.auth.seed_permissions
```

---

### Step 8: Generate and Apply Migration

```bash
# Ensure venv is activated and env vars loaded
source python-pos-env-39/Scripts/activate
export $(grep -v '^#' .env | xargs)

# Generate migration
alembic revision --autogenerate -m "create_{entity}_table"

# Review the generated migration file in alembic/versions/

# Apply migration
alembic upgrade head
```

---

### Step 9: Create Postman Collection (Optional)

**File:** `testing/postman/{Entity Name}.postman_collection.json`

Create a collection with these 5 requests:
1. Get All EntityNames (query)
2. Get EntityName by ID (query)
3. Create EntityName (mutation)
4. Update EntityName (mutation)
5. Delete EntityName (mutation)

Follow existing collection patterns in `testing/postman/` folder.

---

### Step 10: Verify Implementation

```bash
# Restart service
docker-compose restart web

# Check logs for errors
docker-compose logs -f web
```

Test in GraphQL playground (`http://localhost:8000/graphql`):

1. Login to get token
2. Test queries with token
3. Test mutations with token
4. Verify permission checks work

---

## Code Patterns

### Naming Conventions

- **Model class:** PascalCase (e.g., `ProductSlot`)
- **Table name:** snake_case (e.g., `product_slot`)
- **Python fields:** snake_case (e.g., `slot_name`)
- **GraphQL fields:** camelCase (e.g., `slotName`)
- **GraphQL types:** PascalCase + "Type" (e.g., `ProductSlotType`)
- **Mutation classes:** PascalCase + "Mutations" (e.g., `ProductSlotMutations`)
- **Query classes:** PascalCase + "Queries" (e.g., `ProductSlotQueries`)
- **Mutation names:** camelCase with verb (e.g., `createProductSlot`)
- **Query names:** camelCase, plural/singular (e.g., `productSlots`, `productSlot`)
- **File names:** snake_case (e.g., `product_slot.py`)

### Error Handling Pattern

```python
db = SessionLocal()

# Validation
if not valid_condition:
    db.close()
    raise ValueError("Descriptive error message")

# ... do work ...

db.close()
return result
```

### Database Session Management

```python
db = SessionLocal()
try:
    # ... do work ...
    db.commit()
    db.refresh(entity)
    result = convert_to_graphql_type(entity)
finally:
    db.close()
return result
```

---

## RBAC Implementation

### 🔒 Security Requirements (MANDATORY)

**Every GraphQL resolver MUST:**

1. **Accept `info` parameter:**
   ```python
   def my_resolver(self, info: strawberry.types.Info, ...):
   ```

2. **Import permission helper:**
   ```python
   from app.auth.permissions import require_permission
   ```

3. **Check permission at the start:**
   ```python
   # For mutations (returns user for audit fields):
   user = require_permission(info, "CREATE_ENTITY_NAME")
   
   # For queries (when you don't need user object):
   require_permission(info, "VIEW_ENTITY_NAME")
   ```

4. **Use authenticated user for audit fields:**
   ```python
   entity.created_by = user.id
   entity.updated_by = user.id
   entity.deleted_by = user.id
   ```

### Permission Naming Convention

Format: `{ACTION}_{ENTITY_NAME}`

- **Actions:** `CREATE`, `VIEW`, `UPDATE`, `DELETE`
- **Entity name:** SCREAMING_SNAKE_CASE
- **Examples:** `CREATE_USER`, `VIEW_PRODUCT`, `DELETE_SHIFT_TEMPLATE`

### Exception: Public Endpoints

Only these endpoints should NOT require authentication:
- `login` mutation
- (No other exceptions)

---

## Testing & Verification

### Checklist

- [ ] Model created with correct audit pattern
- [ ] Schema created with matching fields
- [ ] Mutations implement all CRUD operations
- [ ] Queries implement list and single-item fetching
- [ ] All resolvers have `info: strawberry.types.Info` parameter
- [ ] All resolvers call `require_permission()`
- [ ] Permissions added to `seed_permissions.py`
- [ ] Permission seeding script run successfully
- [ ] Aggregator files updated (mutations and queries __init__.py)
- [ ] Model imports updated (models __init__.py and alembic env.py)
- [ ] Migration generated and applied
- [ ] Service restarted without errors
- [ ] GraphQL queries work with authentication
- [ ] Permission denied works for unauthorized users
- [ ] Soft delete filters work (deleted_at.is_(None))
- [ ] Audit fields populate correctly

### Test Queries

```graphql
# Login first
mutation {
  login(username: "superadmin", password: "password") {
    token { accessToken }
    user { id username }
  }
}

# Add token to HTTP Headers:
# { "Authorization": "Bearer <token>" }

# Test list query
query {
  entityNames {
    id
    fieldName
  }
}

# Test single query
query {
  entityName(entityId: 1) {
    id
    fieldName
  }
}

# Test create mutation
mutation {
  createEntityName(field1: "test", field2: 123) {
    id
    fieldName
  }
}

# Test without token (should fail)
# Remove Authorization header and try query
query {
  entityNames {
    id
  }
}
# Expected: "Authentication required"
```

---

## Documentation Requirements (MANDATORY)

### ⚠️ CRITICAL: After creating/modifying an entity, you MUST update documentation

**Update [01-entity-reference.md](01-entity-reference.md) with:**

1. **Entity documentation using this template:**

```markdown
### EntityName
**Purpose:** Brief description of what this entity represents

**Table:** `table_name`

**Key Fields:**
- `id` (PK) - Integer
- `field_name` - Type, constraints, description
- ...

**Audit Pattern:** [None | Soft delete only | Full audit trail]

**Relationships:**
- Many-to-one with OtherEntity (via foreign_key_id)
- One-to-many with ChildEntity

**Business Rules:**
- Rule 1
- Rule 2
```

2. **Update relationship diagram** if relationships changed

3. **Document business workflows** if this entity participates in special workflows

4. **Update "Last Updated" date** at the top of 01-entity-reference.md

### Why This Matters

- Future AI agents depend on accurate documentation
- Prevents duplicate entities
- Maintains consistency
- Helps with onboarding
- Documents business logic

**If you don't update documentation:**
- ❌ Future agents will work with outdated information
- ❌ Creates risk of duplicate entities
- ❌ Relationships may break
- ❌ Inconsistencies will be introduced

---

## Common Pitfalls

### ❌ Forgetting to close database sessions
```python
db = SessionLocal()
# ... do work ...
# ❌ MISSING: db.close()
```
**Fix:** Always call `db.close()` before returning

---

### ❌ Not filtering soft-deleted records
```python
entities = db.query(EntityModel).all()  # ❌ Returns deleted records
```
**Fix:** Always filter: `.filter(EntityModel.deleted_at.is_(None))`

---

### ❌ Missing permission checks
```python
@strawberry.mutation
def create_entity(self, field1: str):  # ❌ No info parameter, no permission check
    db = SessionLocal()
    # ...
```
**Fix:** Add `info` parameter and call `require_permission()`

---

### ❌ Not using authenticated user for audit fields
```python
entity = EntityModel(
    field1=field1,
    created_by=1  # ❌ Hardcoded user ID
)
```
**Fix:** Use `created_by=user.id` from `require_permission()`

---

### ❌ Forgetting to update documentation
```python
# Entity created successfully but...
# ❌ Did not update 01-entity-reference.md
```
**Fix:** ALWAYS update documentation after entity changes

---

### ❌ Using sequential edits instead of batch
```python
# Making 5 separate replace_string_in_file calls
# ❌ Inefficient, costly
```
**Fix:** Use `multi_replace_string_in_file` for multiple independent edits

---

### ❌ Not updating aggregator files
```python
# Created mutations file but...
# ❌ Forgot to add import to app/graphql/mutations/__init__.py
```
**Fix:** Always update both mutations and queries __init__.py files

---

### ❌ Not seeding permissions
```python
# Added permissions to seed_permissions.py but...
# ❌ Did not run: python -m app.auth.seed_permissions
```
**Fix:** Run seeding script after adding permissions

---

## Quick Reference Card

### Minimum Files to Create/Update

**Create (4 files):**
1. `app/models/{entity}.py`
2. `app/schemas/{entity}.py`
3. `app/graphql/mutations/{entity}.py`
4. `app/graphql/queries/{entity}.py`

**Update (4 files):**
5. `app/models/__init__.py` - Add import
6. `alembic/env.py` - Add import
7. `app/graphql/mutations/__init__.py` - Add class to Mutation
8. `app/graphql/queries/__init__.py` - Add class to Query

**Update (1 file):**
9. `app/auth/seed_permissions.py` - Add 4 permissions

**Run commands:**
10. `python -m app.auth.seed_permissions`
11. `alembic revision --autogenerate -m "create_{entity}_table"`
12. `alembic upgrade head`

**MUST UPDATE (1 file):**
13. `prompts/01-entity-reference.md` - Document entity **(MANDATORY)**

---

## Summary

Creating an entity involves:
1. ✅ Read prerequisites ([01-entity-reference.md](01-entity-reference.md))
2. ✅ Create model, schema, mutations, queries
3. ✅ Implement RBAC in all resolvers
4. ✅ Add and seed permissions
5. ✅ Update imports and aggregators
6. ✅ Generate and apply migration
7. ✅ Test thoroughly
8. ✅ **UPDATE DOCUMENTATION** (mandatory)

**Total typical effort:** 4 new files, 4 modified files, 1 documentation update, 3 commands

For code templates, see [templates/entity-template.md](templates/entity-template.md).

For entity reference, see [01-entity-reference.md](01-entity-reference.md).

For auth patterns, see [03-auth-and-permissions.md](03-auth-and-permissions.md).
