# Entity Code Templates

**Purpose:** Copy/paste boilerplate code for creating new entities

**Last Updated:** March 22, 2026

---

## Table of Contents
1. [SQLAlchemy Model Templates](#sqlalchemy-model-templates)
2. [Strawberry Schema Template](#strawberry-schema-template)
3. [GraphQL Mutations Template](#graphql-mutations-template)
4. [GraphQL Queries Template](#graphql-queries-template)
5. [Permission Seed Template](#permission-seed-template)

---

## SQLAlchemy Model Templates

### Option A: No Audit Pattern (Simple Entity)

**Use for:** Simple reference entities like User

**File:** `app/models/{entity}.py`

```python
from sqlalchemy import Column, Integer, String
from app.database import Base

class EntityName(Base):
    __tablename__ = "entity_name"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)

    def __repr__(self):
        return f"<EntityName(id={self.id}, name={self.name})>"
```

---

### Option B: Soft Delete Only Pattern

**Use for:** Master data entities like ProductTemplate, Permission, Role

**File:** `app/models/{entity}.py`

```python
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from app.database import Base

class EntityName(Base):
    __tablename__ = "entity_name"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Soft delete fields
    deleted_at = Column(PG_TIMESTAMP(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<EntityName(id={self.id}, name={self.name})>"
```

---

### Option C: Full Audit Trail Pattern (RECOMMENDED)

**Use for:** Operational entities like Product, Shift, most transactional data

**File:** `app/models/{entity}.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base

class EntityName(Base):
    __tablename__ = "entity_name"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    amount = Column(Numeric(15, 6), nullable=False)  # For money/measurements
    foreign_key_id = Column(Integer, ForeignKey("other_table.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Full audit fields
    deleted_at = Column(PG_TIMESTAMP(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(Integer, nullable=True)

    # Relationships
    related_entity = relationship("RelatedEntity", backref="entity_names")

    def __repr__(self):
        return f"<EntityName(id={self.id}, name={self.name})>"
```

---

### Data Type Reference

```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, Text
from sqlalchemy import Date, Time
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP

# Common column types:
Column(Integer, ...)                              # Integer
Column(String, ...)                               # Variable-length string
Column(String(100), ...)                          # String with max length
Column(Text, ...)                                 # Unlimited text
Column(Boolean, ...)                              # True/False
Column(Numeric(15, 6), ...)                       # Decimal (precision, scale)
Column(Date, ...)                                 # Date only
Column(Time(timezone=True), ...)                  # Time only with timezone
Column(PG_TIMESTAMP(timezone=True), ...)          # Timestamp with timezone
Column(Integer, ForeignKey("table.id"), ...)      # Foreign key

# Common constraints:
nullable=False                                    # Required field
nullable=True                                     # Optional field
unique=True                                       # Must be unique
index=True                                        # Add database index
default=True                                      # Default value
server_default=func.now()                         # Server-side default
onupdate=func.now()                              # Auto-update on change
```

---

## Strawberry Schema Template

**File:** `app/schemas/{entity}.py`

### With Full Audit Fields

```python
from typing import Optional
from datetime import datetime, date, time
import strawberry

@strawberry.type
class EntityNameType:
    id: int
    name: str
    code: str
    description: Optional[str]
    amount: float  # For Numeric columns
    foreign_key_id: int
    is_active: bool
    
    # Full audit fields
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    created_at: datetime
    created_by: Optional[int]
    updated_at: datetime
    updated_by: Optional[int]
```

### With Soft Delete Only

```python
from typing import Optional
from datetime import datetime
import strawberry

@strawberry.type
class EntityNameType:
    id: int
    name: str
    code: str
    description: Optional[str]
    is_active: bool
    
    # Soft delete fields
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
```

### No Audit

```python
from typing import Optional
import strawberry

@strawberry.type
class EntityNameType:
    id: int
    name: str
    code: str
    description: Optional[str]
```

---

## GraphQL Mutations Template

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
        name: str,
        code: str,
        description: Optional[str] = None,
        amount: Optional[float] = None,
        foreign_key_id: Optional[int] = None,
    ) -> EntityNameType:
        """Create a new EntityName record."""
        # 🔒 RBAC: Require permission
        user = require_permission(info, "CREATE_ENTITY_NAME")
        
        db = SessionLocal()
        
        # Validation: Check unique constraint
        existing = db.query(EntityModel).filter(EntityModel.code == code).first()
        if existing:
            db.close()
            raise ValueError(f"EntityName with code '{code}' already exists")
        
        # Validation: Check foreign key exists (if applicable)
        if foreign_key_id is not None:
            from app.models.other_entity import OtherEntity
            related = db.query(OtherEntity).filter(OtherEntity.id == foreign_key_id).first()
            if not related:
                db.close()
                raise ValueError(f"Related entity with id {foreign_key_id} not found")
        
        # Create entity
        entity = EntityModel(
            name=name,
            code=code,
            description=description,
            amount=amount,
            foreign_key_id=foreign_key_id,
            created_by=user.id  # Audit trail
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
        
        # Map to GraphQL type
        result = EntityNameType(
            id=entity.id,
            name=entity.name,
            code=entity.code,
            description=entity.description,
            amount=float(entity.amount) if entity.amount else None,
            foreign_key_id=entity.foreign_key_id,
            is_active=entity.is_active,
            deleted_at=entity.deleted_at,
            deleted_by=entity.deleted_by,
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
        name: Optional[str] = None,
        description: Optional[str] = None,
        amount: Optional[float] = None,
        foreign_key_id: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[EntityNameType]:
        """Update an existing EntityName record."""
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
        if name is not None:
            entity.name = name
        if description is not None:
            entity.description = description
        if amount is not None:
            entity.amount = amount
        if foreign_key_id is not None:
            # Validate foreign key exists
            from app.models.other_entity import OtherEntity
            related = db.query(OtherEntity).filter(OtherEntity.id == foreign_key_id).first()
            if not related:
                db.close()
                raise ValueError(f"Related entity with id {foreign_key_id} not found")
            entity.foreign_key_id = foreign_key_id
        if is_active is not None:
            entity.is_active = is_active
        
        # Update audit field
        entity.updated_by = user.id
        db.commit()
        db.refresh(entity)
        
        # Map to GraphQL type
        result = EntityNameType(
            id=entity.id,
            name=entity.name,
            code=entity.code,
            description=entity.description,
            amount=float(entity.amount) if entity.amount else None,
            foreign_key_id=entity.foreign_key_id,
            is_active=entity.is_active,
            deleted_at=entity.deleted_at,
            deleted_by=entity.deleted_by,
            created_at=entity.created_at,
            created_by=entity.created_by,
            updated_at=entity.updated_at,
            updated_by=entity.updated_by,
        )
        db.close()
        return result
    
    @strawberry.mutation(name="deleteEntityName")
    def delete_entity_name(
        self,
        info: strawberry.types.Info,
        entity_id: int
    ) -> Optional[EntityNameType]:
        """Soft-delete an EntityName record."""
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
        entity.deleted_by = user.id
        entity.updated_by = user.id
        db.commit()
        db.refresh(entity)
        
        # Map to GraphQL type
        result = EntityNameType(
            id=entity.id,
            name=entity.name,
            code=entity.code,
            description=entity.description,
            amount=float(entity.amount) if entity.amount else None,
            foreign_key_id=entity.foreign_key_id,
            is_active=entity.is_active,
            deleted_at=entity.deleted_at,
            deleted_by=entity.deleted_by,
            created_at=entity.created_at,
            created_by=entity.created_by,
            updated_at=entity.updated_at,
            updated_by=entity.updated_by,
        )
        db.close()
        return result
```

---

## GraphQL Queries Template

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
        """Get all non-deleted EntityName records."""
        # 🔒 RBAC: Require permission
        require_permission(info, "VIEW_ENTITY_NAME")
        
        db = SessionLocal()
        entities = db.query(EntityModel).filter(EntityModel.deleted_at.is_(None)).all()
        db.close()
        
        return [
            EntityNameType(
                id=e.id,
                name=e.name,
                code=e.code,
                description=e.description,
                amount=float(e.amount) if e.amount else None,
                foreign_key_id=e.foreign_key_id,
                is_active=e.is_active,
                deleted_at=e.deleted_at,
                deleted_by=e.deleted_by,
                created_at=e.created_at,
                created_by=e.created_by,
                updated_at=e.updated_at,
                updated_by=e.updated_by,
            )
            for e in entities
        ]
    
    @strawberry.field
    def entity_name(
        self, info: strawberry.types.Info, entity_id: int
    ) -> Optional[EntityNameType]:
        """Get a single EntityName record by ID."""
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
            name=entity.name,
            code=entity.code,
            description=entity.description,
            amount=float(entity.amount) if entity.amount else None,
            foreign_key_id=entity.foreign_key_id,
            is_active=entity.is_active,
            deleted_at=entity.deleted_at,
            deleted_by=entity.deleted_by,
            created_at=entity.created_at,
            created_by=entity.created_by,
            updated_at=entity.updated_at,
            updated_by=entity.updated_by,
        )
    
    @strawberry.field
    def entity_names_by_foreign_key(
        self, info: strawberry.types.Info, foreign_key_id: int
    ) -> List[EntityNameType]:
        """Get EntityNames filtered by foreign key (if applicable)."""
        # 🔒 RBAC: Require permission
        require_permission(info, "VIEW_ENTITY_NAME")
        
        db = SessionLocal()
        entities = (
            db.query(EntityModel)
            .filter(
                EntityModel.foreign_key_id == foreign_key_id,
                EntityModel.deleted_at.is_(None)
            )
            .all()
        )
        db.close()
        
        return [
            EntityNameType(
                id=e.id,
                name=e.name,
                code=e.code,
                description=e.description,
                amount=float(e.amount) if e.amount else None,
                foreign_key_id=e.foreign_key_id,
                is_active=e.is_active,
                deleted_at=e.deleted_at,
                deleted_by=e.deleted_by,
                created_at=e.created_at,
                created_by=e.created_by,
                updated_at=e.updated_at,
                updated_by=e.updated_by,
            )
            for e in entities
        ]
```

---

## Permission Seed Template

**File:** `app/auth/seed_permissions.py`

**Add to `BASE_PERMISSIONS` list:**

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

**Add to DEFAULT_ROLES (optional):**

```python
DEFAULT_ROLES = [
    # ... existing roles ...
    (
        "MANAGER",
        "Manager",
        "Can manage products, shifts, and view reports",
        [
            # ... existing permissions ...
            "VIEW_ENTITY_NAME", "CREATE_ENTITY_NAME", "UPDATE_ENTITY_NAME", "DELETE_ENTITY_NAME",
        ],
    ),
]
```

---

## Aggregator File Updates

### Update `app/graphql/mutations/__init__.py`

```python
import strawberry
from .auth import AuthMutations
from .user import UserMutations
# ... other imports ...
from .{entity} import EntityNameMutations  # ADD THIS LINE


@strawberry.type
class Mutation(
    AuthMutations,
    UserMutations,
    # ... other mutations ...
    EntityNameMutations,  # ADD THIS LINE
):
    """
    Aggregated mutations from all entities.
    """
    pass
```

### Update `app/graphql/queries/__init__.py`

```python
import strawberry
from .auth import AuthQueries
from .user import UserQueries
# ... other imports ...
from .{entity} import EntityNameQueries  # ADD THIS LINE


@strawberry.type
class Query(
    AuthQueries,
    UserQueries,
    # ... other queries ...
    EntityNameQueries,  # ADD THIS LINE
):
    """
    Aggregated queries from all entities.
    """
    pass
```

### Update `app/models/__init__.py`

```python
from .user import *
from .product_template import *
# ... other imports ...
from .{entity} import *  # ADD THIS LINE
```

### Update `alembic/env.py`

```python
from app.models.user import User
from app.models.product_template import ProductTemplate
# ... other imports ...
from app.models.{entity} import EntityName  # ADD THIS LINE
```

---

## Usage Instructions

### Step-by-Step:

1. **Copy the appropriate model template** (no audit, soft delete, or full audit)
2. **Replace all instances of:**
   - `EntityName` → Your entity class name (PascalCase)
   - `entity_name` → Your table name (snake_case)
   - `{entity}` → Your file name (snake_case)
   - Field names and types as needed

3. **Copy the schema template** and update field names

4. **Copy mutations and queries templates** and update:
   - Field names and types
   - Validation logic
   - Foreign key checks

5. **Copy permission seed template** and update:
   - Entity name in permission codes
   - Category name

6. **Update all aggregator files** with your entity imports

7. **Run:**
   ```bash
   python -m app.auth.seed_permissions
   alembic revision --autogenerate -m "create_{entity}_table"
   alembic upgrade head
   ```

8. **Test in GraphQL playground**

9. **MANDATORY: Update [01-entity-reference.md](../01-entity-reference.md)**

---

## Example: Creating "Category" Entity

**Replace:**
- `EntityName` → `Category`
- `entity_name` → `category`
- `{entity}` → `category`
- Update fields

**Result:**
- `app/models/category.py` - CategoryModel
- `app/schemas/category.py` - CategoryType
- `app/graphql/mutations/category.py` - CategoryMutations
- `app/graphql/queries/category.py` - CategoryQueries
- Permissions: `VIEW_CATEGORY`, `CREATE_CATEGORY`, etc.

---

**For step-by-step instructions, see [02-entity-creation-guide.md](../02-entity-creation-guide.md)**

**For entity reference, see [01-entity-reference.md](../01-entity-reference.md)**
