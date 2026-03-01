# Implementation Plan: JWT Authentication + RBAC Permission System

**Created:** March 1, 2026  
**Status:** Ready for implementation  
**Estimated Effort:** 32 new files, 14 modified files, 4 database migrations

---

## Overview

Implement stateless JWT authentication with a flexible Role-Based Access Control (RBAC) system for the Python POS API. Users authenticate with username/password to receive a JWT access token. Every GraphQL operation (except `login`) requires a valid token AND the user must have the corresponding permission through their assigned roles.

**Key Design Decisions:**
- Permission-based authorization (not role-checked directly)
- Hybrid permissions: seeded base set + allow dynamic additions via mutations
- Admin-only user creation (no public registration)
- Force password reset for existing plaintext passwords
- All operations protected except `login`
- Many-to-many: Users ↔ Roles ↔ Permissions

---

## Current State of the Codebase

### Existing Files That Will Be Modified

**`requirements.txt`** (already has auth libs from a partial earlier attempt):
```
FastAPI==0.128.0
Strawberry-GraphQL==0.283.3
SQLAlchemy==2.0.46
uvicorn==0.39.0
alembic==1.16.5
pydantic==2.12.5
psycopg2-binary==2.9.11
python-dotenv==1.2.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
```

**`.env`** (currently only has):
```
PYTHONPATH=.
```

**`app/main.py`**:
```python
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from app.graphql.schema import schema

app = FastAPI()

graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI GraphQL app!"}
```

**`app/database.py`**:
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "fastapi_graphql")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**`app/models/user.py`** (note: `hashed_password` stores plaintext currently):
```python
from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    hashed_password = Column(String)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email}, first_name={self.first_name}, last_name={self.last_name})>"
```

**`app/schemas/user.py`**:
```python
import strawberry

@strawberry.type
class UserType:
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
```

**`app/graphql/mutations/__init__.py`**:
```python
import strawberry
from .user import UserMutations
from .product_template import ProductTemplateMutations
from .product import ProductMutations
from .shift_template import ShiftTemplateMutations
from .product_slot import ProductSlotMutations
from .shift import ShiftMutations
from .shift_user import ShiftUserMutations
from .product_slot_reading import ProductSlotReadingMutations


@strawberry.type
class Mutation(
    UserMutations,
    ProductTemplateMutations,
    ProductMutations,
    ShiftTemplateMutations,
    ProductSlotMutations,
    ShiftMutations,
    ShiftUserMutations,
    ProductSlotReadingMutations,
):
    """
    Aggregated mutations from all entities.
    
    This class inherits from all entity-specific mutation classes,
    combining their mutations into a single GraphQL Mutation type.
    """
    pass
```

**`app/graphql/queries/__init__.py`**:
```python
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
```

**`app/models/__init__.py`**:
```python
from .user import *
from .product_template import *
from .product import *
from .shift_template import *
from .shift import *
from .shift_user import *
from .product_slot import *
from .product_slot_reading import *
```

**`alembic/env.py`** model imports section (lines 10-18):
```python
from app.database import Base
from app.models.product_template import ProductTemplate
from app.models.user import User
from app.models.shift_template import ShiftTemplate
from app.models.shift import Shift
from app.models.shift_user import ShiftUser
from app.models.product import Product
from app.models.product_slot import ProductSlot
from app.models.product_slot_reading import ProductSlotReading
```

### Existing Patterns to Follow

**Junction entity pattern** (from `app/models/shift_user.py`):
```python
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base

class ShiftUser(Base):
    __tablename__ = "shift_user"

    id = Column(Integer, primary_key=True, index=True)
    shift_id = Column(Integer, ForeignKey("shift.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Standard audit fields
    deleted_at = Column(PG_TIMESTAMP(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(Integer, nullable=True)

    # Relationships
    shift = relationship("Shift", backref="shift_users")
    user = relationship("User", backref="shift_users")
```

**Error handling pattern** (from mutations):
```python
if not valid_condition:
    db.close()
    raise ValueError("Descriptive error message")
```

**Mutation pattern** (from existing code):
```python
@strawberry.mutation(name="createProduct")
def create_product(self, field1: str, field2: int, created_by: Optional[int] = None) -> ProductType:
    db = SessionLocal()
    # ... validation, create, commit, refresh ...
    db.close()
    return result
```

**Query pattern** (from existing code):
```python
@strawberry.field
def products(self) -> List[ProductType]:
    db = SessionLocal()
    products = db.query(ProductModel).filter(ProductModel.deleted_at.is_(None)).all()
    db.close()
    return [ProductType(...) for product in products]
```

---

## Complete Permission Map

Every GraphQL operation maps to a permission code:

| Entity | Operation | Permission Code |
|--------|-----------|-----------------|
| **User** | `users` query | `VIEW_USER` |
| **User** | `createUser` | `CREATE_USER` |
| **User** | `updateUser` | `UPDATE_USER` |
| **User** | `deleteUser` | `DELETE_USER` |
| **Product** | `products` / `product` query | `VIEW_PRODUCT` |
| **Product** | `createProduct` | `CREATE_PRODUCT` |
| **Product** | `updateProduct` | `UPDATE_PRODUCT` |
| **Product** | `deleteProduct` | `DELETE_PRODUCT` |
| **ProductTemplate** | `product_templates` / `product_template` query | `VIEW_PRODUCT_TEMPLATE` |
| **ProductTemplate** | `createProductTemplate` | `CREATE_PRODUCT_TEMPLATE` |
| **ProductTemplate** | `updateProductTemplate` | `UPDATE_PRODUCT_TEMPLATE` |
| **ProductTemplate** | `deleteProductTemplate` | `DELETE_PRODUCT_TEMPLATE` |
| **ProductSlot** | `product_slots` / `product_slot` query | `VIEW_PRODUCT_SLOT` |
| **ProductSlot** | `createProductSlot` | `CREATE_PRODUCT_SLOT` |
| **ProductSlot** | `updateProductSlot` | `UPDATE_PRODUCT_SLOT` |
| **ProductSlot** | `deleteProductSlot` | `DELETE_PRODUCT_SLOT` |
| **ProductSlotReading** | `deleteProductSlotReading` | `DELETE_PRODUCT_SLOT_READING` |
| **Shift** | `shifts` / `shift` / `active_shift` query | `VIEW_SHIFT` |
| **Shift** | `startShift` | `START_SHIFT` |
| **Shift** | `endShift` | `END_SHIFT` |
| **Shift** | `deleteShift` | `DELETE_SHIFT` |
| **ShiftTemplate** | `shift_templates` / `shift_template` query | `VIEW_SHIFT_TEMPLATE` |
| **ShiftTemplate** | `createShiftTemplate` | `CREATE_SHIFT_TEMPLATE` |
| **ShiftTemplate** | `updateShiftTemplate` | `UPDATE_SHIFT_TEMPLATE` |
| **ShiftTemplate** | `deleteShiftTemplate` | `DELETE_SHIFT_TEMPLATE` |
| **ShiftUser** | `deleteShiftUser` | `DELETE_SHIFT_USER` |
| **Permission** | `permissions` / `permission` / `permissionsByCategory` query | `VIEW_PERMISSION` |
| **Permission** | `createPermission` | `CREATE_PERMISSION` |
| **Permission** | `updatePermission` | `UPDATE_PERMISSION` |
| **Permission** | `deletePermission` | `DELETE_PERMISSION` |
| **Role** | `roles` / `role` query | `VIEW_ROLE` |
| **Role** | `createRole` | `CREATE_ROLE` |
| **Role** | `updateRole` | `UPDATE_ROLE` |
| **Role** | `deleteRole` | `DELETE_ROLE` |
| **UserRole** | `userRoles` / `roleUsers` query | `VIEW_USER_ROLE` |
| **UserRole** | `assignRoleToUser` | `ASSIGN_ROLE` |
| **UserRole** | `removeRoleFromUser` | `REVOKE_ROLE` |
| **RolePermission** | `rolePermissions` / `permissionRoles` query | `VIEW_ROLE_PERMISSION` |
| **RolePermission** | `addPermissionToRole` | `GRANT_PERMISSION` |
| **RolePermission** | `removePermissionFromRole` | `REVOKE_PERMISSION` |

**Public (no permission needed):** `login`, `me`, `myPermissions`, `myRoles`, `resetPassword`

---

## Phase 1: Environment & Dependencies

### Step 1.1: Update `.env`

**File:** `.env`  
**Action:** Already completed. The `.env` file has been updated with:

```env
JWT_SECRET_KEY=<your-generated-secret-key>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
```

> **Note:** ✅ Secret key already generated and added to `.env`

### Step 1.2: Verify `requirements.txt`

**File:** `requirements.txt`  
**Action:** Verify these 3 lines are present (they already are from a partial attempt):
```
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
```

Then run: `pip install -r requirements.txt`

---

## ⚠️ Important: Virtual Environment & Environment Variables

**Before running any Python scripts or Alembic commands**, always ensure:

1. **Virtual environment is activated:**
   ```bash
   source python-pos-env-39/Scripts/activate
   ```

2. **Environment variables are loaded:**
   ```bash
   export $(grep -v '^#' .env | xargs)
   ```

If you get stuck running Python scripts (import errors, database connection issues, etc.), make sure you've run both commands above first.

---

## Phase 2: Auth Infrastructure (5 new files)

### Step 2.1: Create `app/auth/__init__.py`

**File:** `app/auth/__init__.py` (NEW)  
```python
```
*(empty file)*

### Step 2.2: Create `app/auth/security.py`

**File:** `app/auth/security.py` (NEW)  
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def is_bcrypt_hash(value: str) -> bool:
    """Check if a string is a bcrypt hash (starts with $2b$ or $2a$)."""
    return value.startswith(("$2b$", "$2a$", "$2y$"))
```

### Step 2.3: Create `app/auth/jwt.py`

**File:** `app/auth/jwt.py` (NEW)  
```python
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-dev-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with the given data payload."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRATION_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token. Raises ValueError on failure."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid or expired token: {str(e)}")
```

### Step 2.4: Create `app/auth/permissions.py`

**File:** `app/auth/permissions.py` (NEW)  
```python
import strawberry
from app.database import SessionLocal
from app.models.user import User as UserModel


def get_user_permissions(db, user_id: int) -> set:
    """
    Get all permission codes for a user by traversing:
    User -> UserRole -> Role -> RolePermission -> Permission
    Only includes active (non-deleted) records.
    """
    from app.models.user_role import UserRole
    from app.models.role_permission import RolePermission
    from app.models.permission import Permission

    results = (
        db.query(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .filter(
            UserRole.user_id == user_id,
            UserRole.deleted_at.is_(None),
            RolePermission.deleted_at.is_(None),
            Permission.deleted_at.is_(None),
        )
        .distinct()
        .all()
    )
    return {row[0] for row in results}


def require_permission(info: strawberry.types.Info, permission_code: str) -> UserModel:
    """
    Validate that the current user (from context) has the required permission.
    Returns the authenticated user if authorized.
    Raises ValueError if not authenticated or not authorized.
    """
    user = info.context.get("user")
    if not user:
        raise ValueError("Authentication required. Please provide a valid token in the Authorization header.")

    db = SessionLocal()
    try:
        permissions = get_user_permissions(db, user.id)
    finally:
        db.close()

    if permission_code not in permissions:
        raise ValueError(f"Permission denied. Required permission: {permission_code}")

    return user


def require_auth(info: strawberry.types.Info) -> UserModel:
    """
    Validate that the request has a valid authenticated user.
    Returns the user. Raises ValueError if not authenticated.
    """
    user = info.context.get("user")
    if not user:
        raise ValueError("Authentication required. Please provide a valid token in the Authorization header.")
    return user
```

### Step 2.5: Create `app/context.py`

**File:** `app/context.py` (NEW)  
```python
from fastapi import Request
from app.auth.jwt import decode_access_token
from app.database import SessionLocal
from app.models.user import User as UserModel


async def get_context(request: Request) -> dict:
    """
    Custom context getter for Strawberry GraphQLRouter.
    Extracts the JWT token from the Authorization header,
    validates it, and loads the user from the database.
    Returns a dict with 'request' and 'user' (or None if not authenticated).
    """
    context = {"request": request, "user": None}

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return context

    token = auth_header.split("Bearer ")[1]
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            return context

        db = SessionLocal()
        try:
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            context["user"] = user
        finally:
            db.close()
    except ValueError:
        # Invalid token - return context without user
        pass

    return context
```

---

## Phase 3: New RBAC Entities (4 models, 4 schemas)

### Step 3.1: Create `app/models/permission.py`

**File:** `app/models/permission.py` (NEW)  
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from app.database import Base


class Permission(Base):
    __tablename__ = "permission"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=False, index=True)

    # Soft delete fields
    deleted_at = Column(PG_TIMESTAMP(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<Permission(id={self.id}, code={self.code}, name={self.name}, category={self.category})>"
```

### Step 3.2: Create `app/models/role.py`

**File:** `app/models/role.py` (NEW)  
```python
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from app.database import Base


class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_system_role = Column(Boolean, default=False, nullable=False)

    # Soft delete fields
    deleted_at = Column(PG_TIMESTAMP(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<Role(id={self.id}, code={self.code}, name={self.name})>"
```

### Step 3.3: Create `app/models/user_role.py`

**File:** `app/models/user_role.py` (NEW)  
```python
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(Base):
    __tablename__ = "user_role"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)

    # Standard audit fields
    deleted_at = Column(PG_TIMESTAMP(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(Integer, nullable=True)

    # Relationships
    user = relationship("User", backref="user_roles")
    role = relationship("Role", backref="user_roles")

    def __repr__(self):
        return f"<UserRole(id={self.id}, user_id={self.user_id}, role_id={self.role_id})>"
```

### Step 3.4: Create `app/models/role_permission.py`

**File:** `app/models/role_permission.py` (NEW)  
```python
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base


class RolePermission(Base):
    __tablename__ = "role_permission"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permission.id"), nullable=False)

    # Standard audit fields
    deleted_at = Column(PG_TIMESTAMP(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(Integer, nullable=True)

    # Relationships
    role = relationship("Role", backref="role_permissions")
    permission = relationship("Permission", backref="role_permissions")

    def __repr__(self):
        return f"<RolePermission(id={self.id}, role_id={self.role_id}, permission_id={self.permission_id})>"
```

### Step 3.5: Create `app/schemas/permission.py`

**File:** `app/schemas/permission.py` (NEW)  
```python
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
```

### Step 3.6: Create `app/schemas/role.py`

**File:** `app/schemas/role.py` (NEW)  
```python
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
```

### Step 3.7: Create `app/schemas/user_role.py`

**File:** `app/schemas/user_role.py` (NEW)  
```python
from typing import Optional
from datetime import datetime
import strawberry


@strawberry.type
class UserRoleType:
    id: int
    user_id: int
    role_id: int
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    created_at: datetime
    created_by: Optional[int]
    updated_at: datetime
    updated_by: Optional[int]
```

### Step 3.8: Create `app/schemas/role_permission.py`

**File:** `app/schemas/role_permission.py` (NEW)  
```python
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
```

### Step 3.9: Create `app/schemas/auth.py`

**File:** `app/schemas/auth.py` (NEW)  
```python
import strawberry
from app.schemas.user import UserType


@strawberry.type
class TokenType:
    access_token: str
    token_type: str


@strawberry.type
class AuthPayloadType:
    token: TokenType
    user: UserType
    requires_password_reset: bool
```

---

## Phase 4: Auth GraphQL Operations (2 new files)

### Step 4.1: Create `app/graphql/mutations/auth.py`

**File:** `app/graphql/mutations/auth.py` (NEW)  
```python
import strawberry
from typing import Optional
from app.models.user import User as UserModel
from app.schemas.auth import AuthPayloadType, TokenType
from app.schemas.user import UserType
from app.auth.security import verify_password, is_bcrypt_hash, hash_password
from app.auth.jwt import create_access_token
from app.auth.permissions import require_auth
from app.database import SessionLocal


@strawberry.type
class AuthMutations:
    @strawberry.mutation(name="login")
    def login(self, username: str, password: str) -> AuthPayloadType:
        db = SessionLocal()
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            db.close()
            raise ValueError("Invalid username or password")

        requires_reset = False

        if is_bcrypt_hash(user.hashed_password):
            # Password is properly hashed - verify with bcrypt
            if not verify_password(password, user.hashed_password):
                db.close()
                raise ValueError("Invalid username or password")
        else:
            # Password is plaintext (legacy) - compare directly
            if password != user.hashed_password:
                db.close()
                raise ValueError("Invalid username or password")
            requires_reset = True

        db.close()

        # Create JWT token
        token_data = {"sub": user.username, "user_id": user.id}
        access_token = create_access_token(data=token_data)

        return AuthPayloadType(
            token=TokenType(access_token=access_token, token_type="bearer"),
            user=UserType(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
            ),
            requires_password_reset=requires_reset,
        )

    @strawberry.mutation(name="resetPassword")
    def reset_password(
        self, info: strawberry.types.Info, old_password: str, new_password: str
    ) -> bool:
        user = require_auth(info)
        db = SessionLocal()

        db_user = db.query(UserModel).filter(UserModel.id == user.id).first()
        if not db_user:
            db.close()
            raise ValueError("User not found")

        # Verify old password (handle both plaintext and hashed)
        if is_bcrypt_hash(db_user.hashed_password):
            if not verify_password(old_password, db_user.hashed_password):
                db.close()
                raise ValueError("Current password is incorrect")
        else:
            if old_password != db_user.hashed_password:
                db.close()
                raise ValueError("Current password is incorrect")

        # Hash and save new password
        db_user.hashed_password = hash_password(new_password)
        db.commit()
        db.close()
        return True

    @strawberry.mutation(name="changeUserPassword")
    def change_user_password(
        self, info: strawberry.types.Info, user_id: int, new_password: str
    ) -> bool:
        """Admin-only: Reset another user's password. Requires CREATE_USER permission."""
        from app.auth.permissions import require_permission

        require_permission(info, "UPDATE_USER")
        db = SessionLocal()

        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            db.close()
            raise ValueError(f"User with id {user_id} not found")

        db_user.hashed_password = hash_password(new_password)
        db.commit()
        db.close()
        return True
```

### Step 4.2: Create `app/graphql/queries/auth.py`

**File:** `app/graphql/queries/auth.py` (NEW)  
```python
import strawberry
from typing import List, Optional
from app.schemas.user import UserType
from app.schemas.role import RoleType
from app.auth.permissions import require_auth, get_user_permissions
from app.database import SessionLocal


@strawberry.type
class AuthQueries:
    @strawberry.field
    def me(self, info: strawberry.types.Info) -> Optional[UserType]:
        """Get the currently authenticated user."""
        user = info.context.get("user")
        if not user:
            return None
        return UserType(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )

    @strawberry.field
    def my_permissions(self, info: strawberry.types.Info) -> List[str]:
        """Get all permission codes for the current user."""
        user = require_auth(info)
        db = SessionLocal()
        try:
            permissions = get_user_permissions(db, user.id)
        finally:
            db.close()
        return sorted(list(permissions))

    @strawberry.field
    def my_roles(self, info: strawberry.types.Info) -> List[RoleType]:
        """Get all active roles for the current user."""
        from app.models.user_role import UserRole
        from app.models.role import Role

        user = require_auth(info)
        db = SessionLocal()
        roles = (
            db.query(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(
                UserRole.user_id == user.id,
                UserRole.deleted_at.is_(None),
                Role.deleted_at.is_(None),
            )
            .all()
        )
        result = [
            RoleType(
                id=role.id,
                code=role.code,
                name=role.name,
                description=role.description,
                is_system_role=role.is_system_role,
                deleted_at=role.deleted_at,
                deleted_by=role.deleted_by,
            )
            for role in roles
        ]
        db.close()
        return result
```

---

## Phase 5: RBAC GraphQL Operations (8 new files)

### Step 5.1: Create `app/graphql/mutations/permission.py`

**File:** `app/graphql/mutations/permission.py` (NEW)  
```python
import strawberry
from typing import Optional
from datetime import datetime
from sqlalchemy import func
from app.models.permission import Permission as PermissionModel
from app.schemas.permission import PermissionType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class PermissionMutations:
    @strawberry.mutation(name="createPermission")
    def create_permission(
        self,
        info: strawberry.types.Info,
        code: str,
        name: str,
        category: str,
        description: Optional[str] = None,
    ) -> PermissionType:
        user = require_permission(info, "CREATE_PERMISSION")
        db = SessionLocal()

        existing = db.query(PermissionModel).filter(PermissionModel.code == code).first()
        if existing:
            db.close()
            raise ValueError(f"Permission with code '{code}' already exists")

        db_permission = PermissionModel(
            code=code,
            name=name,
            description=description,
            category=category,
        )
        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)
        result = PermissionType(
            id=db_permission.id,
            code=db_permission.code,
            name=db_permission.name,
            description=db_permission.description,
            category=db_permission.category,
            deleted_at=db_permission.deleted_at,
            deleted_by=db_permission.deleted_by,
        )
        db.close()
        return result

    @strawberry.mutation(name="updatePermission")
    def update_permission(
        self,
        info: strawberry.types.Info,
        permission_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Optional[PermissionType]:
        user = require_permission(info, "UPDATE_PERMISSION")
        db = SessionLocal()
        db_permission = (
            db.query(PermissionModel)
            .filter(PermissionModel.id == permission_id, PermissionModel.deleted_at.is_(None))
            .first()
        )
        if not db_permission:
            db.close()
            return None

        if name is not None:
            db_permission.name = name
        if description is not None:
            db_permission.description = description
        if category is not None:
            db_permission.category = category

        db.commit()
        db.refresh(db_permission)
        result = PermissionType(
            id=db_permission.id,
            code=db_permission.code,
            name=db_permission.name,
            description=db_permission.description,
            category=db_permission.category,
            deleted_at=db_permission.deleted_at,
            deleted_by=db_permission.deleted_by,
        )
        db.close()
        return result

    @strawberry.mutation(name="deletePermission")
    def delete_permission(
        self, info: strawberry.types.Info, permission_id: int
    ) -> Optional[PermissionType]:
        user = require_permission(info, "DELETE_PERMISSION")
        db = SessionLocal()
        db_permission = (
            db.query(PermissionModel)
            .filter(PermissionModel.id == permission_id, PermissionModel.deleted_at.is_(None))
            .first()
        )
        if not db_permission:
            db.close()
            return None

        db_permission.deleted_at = func.now()
        db_permission.deleted_by = user.id
        db.commit()
        db.refresh(db_permission)
        result = PermissionType(
            id=db_permission.id,
            code=db_permission.code,
            name=db_permission.name,
            description=db_permission.description,
            category=db_permission.category,
            deleted_at=db_permission.deleted_at,
            deleted_by=db_permission.deleted_by,
        )
        db.close()
        return result
```

### Step 5.2: Create `app/graphql/queries/permission.py`

**File:** `app/graphql/queries/permission.py` (NEW)  
```python
import strawberry
from typing import List, Optional
from app.models.permission import Permission as PermissionModel
from app.schemas.permission import PermissionType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class PermissionQueries:
    @strawberry.field
    def permissions(self, info: strawberry.types.Info) -> List[PermissionType]:
        require_permission(info, "VIEW_PERMISSION")
        db = SessionLocal()
        permissions = db.query(PermissionModel).filter(PermissionModel.deleted_at.is_(None)).all()
        db.close()
        return [
            PermissionType(
                id=p.id, code=p.code, name=p.name, description=p.description,
                category=p.category, deleted_at=p.deleted_at, deleted_by=p.deleted_by,
            )
            for p in permissions
        ]

    @strawberry.field
    def permission(self, info: strawberry.types.Info, permission_id: int) -> Optional[PermissionType]:
        require_permission(info, "VIEW_PERMISSION")
        db = SessionLocal()
        p = (
            db.query(PermissionModel)
            .filter(PermissionModel.id == permission_id, PermissionModel.deleted_at.is_(None))
            .first()
        )
        db.close()
        if not p:
            return None
        return PermissionType(
            id=p.id, code=p.code, name=p.name, description=p.description,
            category=p.category, deleted_at=p.deleted_at, deleted_by=p.deleted_by,
        )

    @strawberry.field
    def permissions_by_category(self, info: strawberry.types.Info, category: str) -> List[PermissionType]:
        require_permission(info, "VIEW_PERMISSION")
        db = SessionLocal()
        permissions = (
            db.query(PermissionModel)
            .filter(PermissionModel.category == category, PermissionModel.deleted_at.is_(None))
            .all()
        )
        db.close()
        return [
            PermissionType(
                id=p.id, code=p.code, name=p.name, description=p.description,
                category=p.category, deleted_at=p.deleted_at, deleted_by=p.deleted_by,
            )
            for p in permissions
        ]
```

### Step 5.3: Create `app/graphql/mutations/role.py`

**File:** `app/graphql/mutations/role.py` (NEW)  
```python
import strawberry
from typing import Optional
from sqlalchemy import func
from app.models.role import Role as RoleModel
from app.schemas.role import RoleType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class RoleMutations:
    @strawberry.mutation(name="createRole")
    def create_role(
        self,
        info: strawberry.types.Info,
        code: str,
        name: str,
        description: Optional[str] = None,
    ) -> RoleType:
        user = require_permission(info, "CREATE_ROLE")
        db = SessionLocal()

        existing = db.query(RoleModel).filter(RoleModel.code == code).first()
        if existing:
            db.close()
            raise ValueError(f"Role with code '{code}' already exists")

        db_role = RoleModel(
            code=code,
            name=name,
            description=description,
            is_system_role=False,
        )
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        result = RoleType(
            id=db_role.id,
            code=db_role.code,
            name=db_role.name,
            description=db_role.description,
            is_system_role=db_role.is_system_role,
            deleted_at=db_role.deleted_at,
            deleted_by=db_role.deleted_by,
        )
        db.close()
        return result

    @strawberry.mutation(name="updateRole")
    def update_role(
        self,
        info: strawberry.types.Info,
        role_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[RoleType]:
        user = require_permission(info, "UPDATE_ROLE")
        db = SessionLocal()
        db_role = (
            db.query(RoleModel)
            .filter(RoleModel.id == role_id, RoleModel.deleted_at.is_(None))
            .first()
        )
        if not db_role:
            db.close()
            return None

        if name is not None:
            db_role.name = name
        if description is not None:
            db_role.description = description

        db.commit()
        db.refresh(db_role)
        result = RoleType(
            id=db_role.id,
            code=db_role.code,
            name=db_role.name,
            description=db_role.description,
            is_system_role=db_role.is_system_role,
            deleted_at=db_role.deleted_at,
            deleted_by=db_role.deleted_by,
        )
        db.close()
        return result

    @strawberry.mutation(name="deleteRole")
    def delete_role(
        self, info: strawberry.types.Info, role_id: int
    ) -> Optional[RoleType]:
        user = require_permission(info, "DELETE_ROLE")
        db = SessionLocal()
        db_role = (
            db.query(RoleModel)
            .filter(RoleModel.id == role_id, RoleModel.deleted_at.is_(None))
            .first()
        )
        if not db_role:
            db.close()
            return None

        if db_role.is_system_role:
            db.close()
            raise ValueError("Cannot delete a system role")

        db_role.deleted_at = func.now()
        db_role.deleted_by = user.id
        db.commit()
        db.refresh(db_role)
        result = RoleType(
            id=db_role.id,
            code=db_role.code,
            name=db_role.name,
            description=db_role.description,
            is_system_role=db_role.is_system_role,
            deleted_at=db_role.deleted_at,
            deleted_by=db_role.deleted_by,
        )
        db.close()
        return result
```

### Step 5.4: Create `app/graphql/queries/role.py`

**File:** `app/graphql/queries/role.py` (NEW)  
```python
import strawberry
from typing import List, Optional
from app.models.role import Role as RoleModel
from app.schemas.role import RoleType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class RoleQueries:
    @strawberry.field
    def roles(self, info: strawberry.types.Info) -> List[RoleType]:
        require_permission(info, "VIEW_ROLE")
        db = SessionLocal()
        roles = db.query(RoleModel).filter(RoleModel.deleted_at.is_(None)).all()
        db.close()
        return [
            RoleType(
                id=r.id, code=r.code, name=r.name, description=r.description,
                is_system_role=r.is_system_role, deleted_at=r.deleted_at, deleted_by=r.deleted_by,
            )
            for r in roles
        ]

    @strawberry.field
    def role(self, info: strawberry.types.Info, role_id: int) -> Optional[RoleType]:
        require_permission(info, "VIEW_ROLE")
        db = SessionLocal()
        r = (
            db.query(RoleModel)
            .filter(RoleModel.id == role_id, RoleModel.deleted_at.is_(None))
            .first()
        )
        db.close()
        if not r:
            return None
        return RoleType(
            id=r.id, code=r.code, name=r.name, description=r.description,
            is_system_role=r.is_system_role, deleted_at=r.deleted_at, deleted_by=r.deleted_by,
        )
```

### Step 5.5: Create `app/graphql/mutations/user_role.py`

**File:** `app/graphql/mutations/user_role.py` (NEW)  
```python
import strawberry
from typing import Optional
from sqlalchemy import func
from app.models.user_role import UserRole as UserRoleModel
from app.models.user import User as UserModel
from app.models.role import Role as RoleModel
from app.schemas.user_role import UserRoleType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class UserRoleMutations:
    @strawberry.mutation(name="assignRoleToUser")
    def assign_role_to_user(
        self, info: strawberry.types.Info, user_id: int, role_id: int
    ) -> UserRoleType:
        assigner = require_permission(info, "ASSIGN_ROLE")
        db = SessionLocal()

        # Validate user exists
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            db.close()
            raise ValueError(f"User with id {user_id} not found")

        # Validate role exists and is not deleted
        role = db.query(RoleModel).filter(
            RoleModel.id == role_id, RoleModel.deleted_at.is_(None)
        ).first()
        if not role:
            db.close()
            raise ValueError(f"Role with id {role_id} not found")

        # Check if assignment already exists (and is not deleted)
        existing = (
            db.query(UserRoleModel)
            .filter(
                UserRoleModel.user_id == user_id,
                UserRoleModel.role_id == role_id,
                UserRoleModel.deleted_at.is_(None),
            )
            .first()
        )
        if existing:
            db.close()
            raise ValueError(f"User {user_id} already has role {role_id}")

        db_user_role = UserRoleModel(
            user_id=user_id,
            role_id=role_id,
            created_by=assigner.id,
        )
        db.add(db_user_role)
        db.commit()
        db.refresh(db_user_role)
        result = UserRoleType(
            id=db_user_role.id,
            user_id=db_user_role.user_id,
            role_id=db_user_role.role_id,
            deleted_at=db_user_role.deleted_at,
            deleted_by=db_user_role.deleted_by,
            created_at=db_user_role.created_at,
            created_by=db_user_role.created_by,
            updated_at=db_user_role.updated_at,
            updated_by=db_user_role.updated_by,
        )
        db.close()
        return result

    @strawberry.mutation(name="removeRoleFromUser")
    def remove_role_from_user(
        self, info: strawberry.types.Info, user_id: int, role_id: int
    ) -> Optional[UserRoleType]:
        remover = require_permission(info, "REVOKE_ROLE")
        db = SessionLocal()

        db_user_role = (
            db.query(UserRoleModel)
            .filter(
                UserRoleModel.user_id == user_id,
                UserRoleModel.role_id == role_id,
                UserRoleModel.deleted_at.is_(None),
            )
            .first()
        )
        if not db_user_role:
            db.close()
            return None

        db_user_role.deleted_at = func.now()
        db_user_role.deleted_by = remover.id
        db_user_role.updated_by = remover.id
        db.commit()
        db.refresh(db_user_role)
        result = UserRoleType(
            id=db_user_role.id,
            user_id=db_user_role.user_id,
            role_id=db_user_role.role_id,
            deleted_at=db_user_role.deleted_at,
            deleted_by=db_user_role.deleted_by,
            created_at=db_user_role.created_at,
            created_by=db_user_role.created_by,
            updated_at=db_user_role.updated_at,
            updated_by=db_user_role.updated_by,
        )
        db.close()
        return result
```

### Step 5.6: Create `app/graphql/queries/user_role.py`

**File:** `app/graphql/queries/user_role.py` (NEW)  
```python
import strawberry
from typing import List
from app.models.user_role import UserRole as UserRoleModel
from app.schemas.user_role import UserRoleType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class UserRoleQueries:
    @strawberry.field
    def user_roles(self, info: strawberry.types.Info, user_id: int) -> List[UserRoleType]:
        require_permission(info, "VIEW_USER_ROLE")
        db = SessionLocal()
        user_roles = (
            db.query(UserRoleModel)
            .filter(UserRoleModel.user_id == user_id, UserRoleModel.deleted_at.is_(None))
            .all()
        )
        db.close()
        return [
            UserRoleType(
                id=ur.id, user_id=ur.user_id, role_id=ur.role_id,
                deleted_at=ur.deleted_at, deleted_by=ur.deleted_by,
                created_at=ur.created_at, created_by=ur.created_by,
                updated_at=ur.updated_at, updated_by=ur.updated_by,
            )
            for ur in user_roles
        ]

    @strawberry.field
    def role_users(self, info: strawberry.types.Info, role_id: int) -> List[UserRoleType]:
        require_permission(info, "VIEW_USER_ROLE")
        db = SessionLocal()
        user_roles = (
            db.query(UserRoleModel)
            .filter(UserRoleModel.role_id == role_id, UserRoleModel.deleted_at.is_(None))
            .all()
        )
        db.close()
        return [
            UserRoleType(
                id=ur.id, user_id=ur.user_id, role_id=ur.role_id,
                deleted_at=ur.deleted_at, deleted_by=ur.deleted_by,
                created_at=ur.created_at, created_by=ur.created_by,
                updated_at=ur.updated_at, updated_by=ur.updated_by,
            )
            for ur in user_roles
        ]
```

### Step 5.7: Create `app/graphql/mutations/role_permission.py`

**File:** `app/graphql/mutations/role_permission.py` (NEW)  
```python
import strawberry
from typing import Optional
from sqlalchemy import func
from app.models.role_permission import RolePermission as RolePermissionModel
from app.models.role import Role as RoleModel
from app.models.permission import Permission as PermissionModel
from app.schemas.role_permission import RolePermissionType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class RolePermissionMutations:
    @strawberry.mutation(name="addPermissionToRole")
    def add_permission_to_role(
        self, info: strawberry.types.Info, role_id: int, permission_id: int
    ) -> RolePermissionType:
        granter = require_permission(info, "GRANT_PERMISSION")
        db = SessionLocal()

        # Validate role exists
        role = db.query(RoleModel).filter(
            RoleModel.id == role_id, RoleModel.deleted_at.is_(None)
        ).first()
        if not role:
            db.close()
            raise ValueError(f"Role with id {role_id} not found")

        # Validate permission exists
        permission = db.query(PermissionModel).filter(
            PermissionModel.id == permission_id, PermissionModel.deleted_at.is_(None)
        ).first()
        if not permission:
            db.close()
            raise ValueError(f"Permission with id {permission_id} not found")

        # Check if assignment already exists
        existing = (
            db.query(RolePermissionModel)
            .filter(
                RolePermissionModel.role_id == role_id,
                RolePermissionModel.permission_id == permission_id,
                RolePermissionModel.deleted_at.is_(None),
            )
            .first()
        )
        if existing:
            db.close()
            raise ValueError(f"Role {role_id} already has permission {permission_id}")

        db_rp = RolePermissionModel(
            role_id=role_id,
            permission_id=permission_id,
            created_by=granter.id,
        )
        db.add(db_rp)
        db.commit()
        db.refresh(db_rp)
        result = RolePermissionType(
            id=db_rp.id,
            role_id=db_rp.role_id,
            permission_id=db_rp.permission_id,
            deleted_at=db_rp.deleted_at,
            deleted_by=db_rp.deleted_by,
            created_at=db_rp.created_at,
            created_by=db_rp.created_by,
            updated_at=db_rp.updated_at,
            updated_by=db_rp.updated_by,
        )
        db.close()
        return result

    @strawberry.mutation(name="removePermissionFromRole")
    def remove_permission_from_role(
        self, info: strawberry.types.Info, role_id: int, permission_id: int
    ) -> Optional[RolePermissionType]:
        revoker = require_permission(info, "REVOKE_PERMISSION")
        db = SessionLocal()

        db_rp = (
            db.query(RolePermissionModel)
            .filter(
                RolePermissionModel.role_id == role_id,
                RolePermissionModel.permission_id == permission_id,
                RolePermissionModel.deleted_at.is_(None),
            )
            .first()
        )
        if not db_rp:
            db.close()
            return None

        db_rp.deleted_at = func.now()
        db_rp.deleted_by = revoker.id
        db_rp.updated_by = revoker.id
        db.commit()
        db.refresh(db_rp)
        result = RolePermissionType(
            id=db_rp.id,
            role_id=db_rp.role_id,
            permission_id=db_rp.permission_id,
            deleted_at=db_rp.deleted_at,
            deleted_by=db_rp.deleted_by,
            created_at=db_rp.created_at,
            created_by=db_rp.created_by,
            updated_at=db_rp.updated_at,
            updated_by=db_rp.updated_by,
        )
        db.close()
        return result
```

### Step 5.8: Create `app/graphql/queries/role_permission.py`

**File:** `app/graphql/queries/role_permission.py` (NEW)  
```python
import strawberry
from typing import List
from app.models.role_permission import RolePermission as RolePermissionModel
from app.schemas.role_permission import RolePermissionType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class RolePermissionQueries:
    @strawberry.field
    def role_permissions(self, info: strawberry.types.Info, role_id: int) -> List[RolePermissionType]:
        require_permission(info, "VIEW_ROLE_PERMISSION")
        db = SessionLocal()
        rps = (
            db.query(RolePermissionModel)
            .filter(RolePermissionModel.role_id == role_id, RolePermissionModel.deleted_at.is_(None))
            .all()
        )
        db.close()
        return [
            RolePermissionType(
                id=rp.id, role_id=rp.role_id, permission_id=rp.permission_id,
                deleted_at=rp.deleted_at, deleted_by=rp.deleted_by,
                created_at=rp.created_at, created_by=rp.created_by,
                updated_at=rp.updated_at, updated_by=rp.updated_by,
            )
            for rp in rps
        ]

    @strawberry.field
    def permission_roles(self, info: strawberry.types.Info, permission_id: int) -> List[RolePermissionType]:
        require_permission(info, "VIEW_ROLE_PERMISSION")
        db = SessionLocal()
        rps = (
            db.query(RolePermissionModel)
            .filter(RolePermissionModel.permission_id == permission_id, RolePermissionModel.deleted_at.is_(None))
            .all()
        )
        db.close()
        return [
            RolePermissionType(
                id=rp.id, role_id=rp.role_id, permission_id=rp.permission_id,
                deleted_at=rp.deleted_at, deleted_by=rp.deleted_by,
                created_at=rp.created_at, created_by=rp.created_by,
                updated_at=rp.updated_at, updated_by=rp.updated_by,
            )
            for rp in rps
        ]
```

---

## Phase 6: Seed Script

### Step 6.1: Create `app/auth/seed_permissions.py`

**File:** `app/auth/seed_permissions.py` (NEW)  
```python
"""
Seed script for permissions and default roles.
Run with: python -m app.auth.seed_permissions
"""

from app.database import SessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission

# (code, name, description, category)
BASE_PERMISSIONS = [
    # User
    ("VIEW_USER", "View Users", "Can view user list and details", "USER"),
    ("CREATE_USER", "Create User", "Can create new users", "USER"),
    ("UPDATE_USER", "Update User", "Can update user details", "USER"),
    ("DELETE_USER", "Delete User", "Can delete users", "USER"),
    # Product
    ("VIEW_PRODUCT", "View Products", "Can view product list and details", "PRODUCT"),
    ("CREATE_PRODUCT", "Create Product", "Can create new products", "PRODUCT"),
    ("UPDATE_PRODUCT", "Update Product", "Can update product details", "PRODUCT"),
    ("DELETE_PRODUCT", "Delete Product", "Can delete products", "PRODUCT"),
    # ProductTemplate
    ("VIEW_PRODUCT_TEMPLATE", "View Product Templates", "Can view product template list and details", "PRODUCT_TEMPLATE"),
    ("CREATE_PRODUCT_TEMPLATE", "Create Product Template", "Can create new product templates", "PRODUCT_TEMPLATE"),
    ("UPDATE_PRODUCT_TEMPLATE", "Update Product Template", "Can update product template details", "PRODUCT_TEMPLATE"),
    ("DELETE_PRODUCT_TEMPLATE", "Delete Product Template", "Can delete product templates", "PRODUCT_TEMPLATE"),
    # ProductSlot
    ("VIEW_PRODUCT_SLOT", "View Product Slots", "Can view product slot list and details", "PRODUCT_SLOT"),
    ("CREATE_PRODUCT_SLOT", "Create Product Slot", "Can create new product slots", "PRODUCT_SLOT"),
    ("UPDATE_PRODUCT_SLOT", "Update Product Slot", "Can update product slot details", "PRODUCT_SLOT"),
    ("DELETE_PRODUCT_SLOT", "Delete Product Slot", "Can delete product slots", "PRODUCT_SLOT"),
    # ProductSlotReading
    ("DELETE_PRODUCT_SLOT_READING", "Delete Product Slot Reading", "Can delete product slot readings", "PRODUCT_SLOT_READING"),
    # Shift
    ("VIEW_SHIFT", "View Shifts", "Can view shift list and details", "SHIFT"),
    ("START_SHIFT", "Start Shift", "Can start a new shift", "SHIFT"),
    ("END_SHIFT", "End Shift", "Can end an active shift", "SHIFT"),
    ("DELETE_SHIFT", "Delete Shift", "Can delete shifts", "SHIFT"),
    # ShiftTemplate
    ("VIEW_SHIFT_TEMPLATE", "View Shift Templates", "Can view shift template list and details", "SHIFT_TEMPLATE"),
    ("CREATE_SHIFT_TEMPLATE", "Create Shift Template", "Can create new shift templates", "SHIFT_TEMPLATE"),
    ("UPDATE_SHIFT_TEMPLATE", "Update Shift Template", "Can update shift template details", "SHIFT_TEMPLATE"),
    ("DELETE_SHIFT_TEMPLATE", "Delete Shift Template", "Can delete shift templates", "SHIFT_TEMPLATE"),
    # ShiftUser
    ("DELETE_SHIFT_USER", "Delete Shift User", "Can delete shift user assignments", "SHIFT_USER"),
    # Permission (RBAC management)
    ("VIEW_PERMISSION", "View Permissions", "Can view permission list", "RBAC"),
    ("CREATE_PERMISSION", "Create Permission", "Can create new permissions", "RBAC"),
    ("UPDATE_PERMISSION", "Update Permission", "Can update permissions", "RBAC"),
    ("DELETE_PERMISSION", "Delete Permission", "Can delete permissions", "RBAC"),
    # Role (RBAC management)
    ("VIEW_ROLE", "View Roles", "Can view role list", "RBAC"),
    ("CREATE_ROLE", "Create Role", "Can create new roles", "RBAC"),
    ("UPDATE_ROLE", "Update Role", "Can update roles", "RBAC"),
    ("DELETE_ROLE", "Delete Role", "Can delete roles", "RBAC"),
    # UserRole (RBAC management)
    ("VIEW_USER_ROLE", "View User Roles", "Can view user role assignments", "RBAC"),
    ("ASSIGN_ROLE", "Assign Role", "Can assign roles to users", "RBAC"),
    ("REVOKE_ROLE", "Revoke Role", "Can revoke roles from users", "RBAC"),
    # RolePermission (RBAC management)
    ("VIEW_ROLE_PERMISSION", "View Role Permissions", "Can view role permission assignments", "RBAC"),
    ("GRANT_PERMISSION", "Grant Permission", "Can grant permissions to roles", "RBAC"),
    ("REVOKE_PERMISSION", "Revoke Permission", "Can revoke permissions from roles", "RBAC"),
]

# Default roles: (code, name, description, permission_codes)
DEFAULT_ROLES = [
    (
        "SUPER_ADMIN",
        "Super Administrator",
        "Full access to all system features",
        None,  # None means ALL permissions
    ),
    (
        "MANAGER",
        "Manager",
        "Can manage products, shifts, and view reports",
        [
            "VIEW_USER", "CREATE_USER", "UPDATE_USER",
            "VIEW_PRODUCT", "CREATE_PRODUCT", "UPDATE_PRODUCT", "DELETE_PRODUCT",
            "VIEW_PRODUCT_TEMPLATE", "CREATE_PRODUCT_TEMPLATE", "UPDATE_PRODUCT_TEMPLATE", "DELETE_PRODUCT_TEMPLATE",
            "VIEW_PRODUCT_SLOT", "CREATE_PRODUCT_SLOT", "UPDATE_PRODUCT_SLOT", "DELETE_PRODUCT_SLOT",
            "DELETE_PRODUCT_SLOT_READING",
            "VIEW_SHIFT", "START_SHIFT", "END_SHIFT", "DELETE_SHIFT",
            "VIEW_SHIFT_TEMPLATE", "CREATE_SHIFT_TEMPLATE", "UPDATE_SHIFT_TEMPLATE", "DELETE_SHIFT_TEMPLATE",
            "DELETE_SHIFT_USER",
        ],
    ),
    (
        "CASHIER",
        "Cashier",
        "Can operate shifts and view products",
        [
            "VIEW_PRODUCT", "VIEW_PRODUCT_TEMPLATE", "VIEW_PRODUCT_SLOT",
            "VIEW_SHIFT", "START_SHIFT", "END_SHIFT",
            "VIEW_SHIFT_TEMPLATE",
        ],
    ),
    (
        "VIEWER",
        "Viewer",
        "Read-only access to operational data",
        [
            "VIEW_USER", "VIEW_PRODUCT", "VIEW_PRODUCT_TEMPLATE",
            "VIEW_PRODUCT_SLOT", "VIEW_SHIFT", "VIEW_SHIFT_TEMPLATE",
        ],
    ),
]


def seed_permissions():
    """Seed base permissions into the database. Skips existing ones."""
    db = SessionLocal()
    created_count = 0
    for code, name, description, category in BASE_PERMISSIONS:
        existing = db.query(Permission).filter(Permission.code == code).first()
        if not existing:
            db.add(Permission(code=code, name=name, description=description, category=category))
            created_count += 1
    db.commit()
    db.close()
    print(f"Seeded {created_count} new permissions ({len(BASE_PERMISSIONS)} total defined)")


def seed_default_roles():
    """Seed default roles and assign permissions. Skips existing roles."""
    db = SessionLocal()
    all_permissions = {p.code: p.id for p in db.query(Permission).all()}
    created_count = 0

    for code, name, description, permission_codes in DEFAULT_ROLES:
        existing = db.query(Role).filter(Role.code == code).first()
        if existing:
            continue

        role = Role(code=code, name=name, description=description, is_system_role=True)
        db.add(role)
        db.commit()
        db.refresh(role)

        # Determine which permissions to assign
        if permission_codes is None:
            # SUPER_ADMIN gets all permissions
            codes_to_assign = list(all_permissions.keys())
        else:
            codes_to_assign = permission_codes

        for perm_code in codes_to_assign:
            perm_id = all_permissions.get(perm_code)
            if perm_id:
                db.add(RolePermission(role_id=role.id, permission_id=perm_id))

        db.commit()
        created_count += 1
        print(f"  Created role '{code}' with {len(codes_to_assign)} permissions")

    db.close()
    print(f"Seeded {created_count} new roles ({len(DEFAULT_ROLES)} total defined)")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("=== Seeding Permissions ===")
    seed_permissions()
    print("\n=== Seeding Default Roles ===")
    seed_default_roles()
    print("\n=== Done! ===")
```

---

## Phase 7: Modify Existing Files

### Step 7.1: Modify `app/main.py`

**Replace the entire file with:**
```python
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from app.graphql.schema import schema
from app.context import get_context

app = FastAPI()

graphql_app = GraphQLRouter(schema, context_getter=get_context)

app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI GraphQL app!"}
```

### Step 7.2: Modify `app/models/__init__.py`

**Replace the entire file with:**
```python
from .user import *
from .product_template import *
from .product import *
from .shift_template import *
from .shift import *
from .shift_user import *
from .product_slot import *
from .product_slot_reading import *
from .permission import *
from .role import *
from .user_role import *
from .role_permission import *
```

### Step 7.3: Modify `alembic/env.py`

**Add these 4 import lines after the existing model imports (after line 18):**
```python
from app.models.permission import Permission
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission
```

### Step 7.4: Modify `app/graphql/mutations/__init__.py`

**Replace the entire file with:**
```python
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
```

### Step 7.5: Modify `app/graphql/queries/__init__.py`

**Replace the entire file with:**
```python
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
```

---

## Phase 8: Protect Existing Operations

For every existing mutation and query file, add `info: strawberry.types.Info` parameter and a `require_permission(info, "PERMISSION_CODE")` call at the start of each resolver.

### Step 8.1: Modify `app/graphql/mutations/user.py`

**Replace the entire file with:**
```python
import strawberry
from typing import Optional
from app.models.user import User as UserModel
from app.schemas.user import UserType
from app.auth.security import hash_password
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class UserMutations:
    @strawberry.mutation(name="createUser")
    def create_user(
        self,
        info: strawberry.types.Info,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        hashed_password: str
    ) -> UserType:
        user = require_permission(info, "CREATE_USER")
        db = SessionLocal()
        db_user = UserModel(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hash_password(hashed_password)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.close()
        return UserType(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            first_name=db_user.first_name,
            last_name=db_user.last_name
        )

    @strawberry.mutation(name="updateUser")
    def update_user(
        self,
        info: strawberry.types.Info,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        hashed_password: Optional[str] = None
    ) -> Optional[UserType]:
        user = require_permission(info, "UPDATE_USER")
        db = SessionLocal()
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            if username is not None:
                db_user.username = username
            if email is not None:
                db_user.email = email
            if first_name is not None:
                db_user.first_name = first_name
            if last_name is not None:
                db_user.last_name = last_name
            if hashed_password is not None:
                db_user.hashed_password = hash_password(hashed_password)
            db.commit()
            db.refresh(db_user)
            result = UserType(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                first_name=db_user.first_name,
                last_name=db_user.last_name
            )
        else:
            result = None
        db.close()
        return result

    @strawberry.mutation(name="deleteUser")
    def delete_user(self, info: strawberry.types.Info, user_id: int) -> Optional[UserType]:
        user = require_permission(info, "DELETE_USER")
        db = SessionLocal()
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            result = UserType(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                first_name=db_user.first_name,
                last_name=db_user.last_name
            )
            db.delete(db_user)
            db.commit()
        else:
            result = None
        db.close()
        return result
```

### Step 8.2: Modify `app/graphql/queries/user.py`

**Replace the entire file with:**
```python
import strawberry
from typing import List
from app.models.user import User as UserModel
from app.schemas.user import UserType
from app.auth.permissions import require_permission
from app.database import SessionLocal


@strawberry.type
class UserQueries:
    @strawberry.field
    def users(self, info: strawberry.types.Info) -> List[UserType]:
        require_permission(info, "VIEW_USER")
        db = SessionLocal()
        users = db.query(UserModel).all()
        db.close()
        return [UserType(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name
        ) for user in users]
```

### Step 8.3: Modify remaining mutation files

For each of the following files, apply the same pattern:
1. Add `from app.auth.permissions import require_permission` import
2. Add `info: strawberry.types.Info` as first param after `self` in every resolver
3. Add `require_permission(info, "PERMISSION_CODE")` as first line of each resolver

**`app/graphql/mutations/product.py`** — Add to each resolver:
- `create_product`: `require_permission(info, "CREATE_PRODUCT")`
- `update_product`: `require_permission(info, "UPDATE_PRODUCT")`
- `delete_product`: `require_permission(info, "DELETE_PRODUCT")`

**`app/graphql/mutations/product_template.py`** — Add to each resolver:
- `create_product_template`: `require_permission(info, "CREATE_PRODUCT_TEMPLATE")`
- `update_product_template`: `require_permission(info, "UPDATE_PRODUCT_TEMPLATE")`
- `delete_product_template`: `require_permission(info, "DELETE_PRODUCT_TEMPLATE")`

**`app/graphql/mutations/product_slot.py`** — Add to each resolver:
- `create_product_slot`: `require_permission(info, "CREATE_PRODUCT_SLOT")`
- `update_product_slot`: `require_permission(info, "UPDATE_PRODUCT_SLOT")`
- `delete_product_slot`: `require_permission(info, "DELETE_PRODUCT_SLOT")`

**`app/graphql/mutations/product_slot_reading.py`** — Add to each resolver:
- `delete_product_slot_reading`: `require_permission(info, "DELETE_PRODUCT_SLOT_READING")`

**`app/graphql/mutations/shift.py`** — Add to each resolver:
- `start_shift`: `require_permission(info, "START_SHIFT")`
- `end_shift`: `require_permission(info, "END_SHIFT")`
- `delete_shift`: `require_permission(info, "DELETE_SHIFT")`

**`app/graphql/mutations/shift_template.py`** — Add to each resolver:
- `create_shift_template`: `require_permission(info, "CREATE_SHIFT_TEMPLATE")`
- `update_shift_template`: `require_permission(info, "UPDATE_SHIFT_TEMPLATE")`
- `delete_shift_template`: `require_permission(info, "DELETE_SHIFT_TEMPLATE")`

**`app/graphql/mutations/shift_user.py`** — Add to each resolver:
- `delete_shift_user`: `require_permission(info, "DELETE_SHIFT_USER")`

### Step 8.4: Modify remaining query files

Same pattern for queries:

**`app/graphql/queries/product.py`** — Add to each resolver:
- `products`: `require_permission(info, "VIEW_PRODUCT")`
- `product`: `require_permission(info, "VIEW_PRODUCT")`

**`app/graphql/queries/product_template.py`** — Add to each resolver:
- `product_templates`: `require_permission(info, "VIEW_PRODUCT_TEMPLATE")`
- `product_template`: `require_permission(info, "VIEW_PRODUCT_TEMPLATE")`

**`app/graphql/queries/product_slot.py`** — Add to each resolver:
- `product_slots`: `require_permission(info, "VIEW_PRODUCT_SLOT")`
- `product_slot`: `require_permission(info, "VIEW_PRODUCT_SLOT")`

**`app/graphql/queries/shift.py`** — Add to each resolver:
- `shifts`: `require_permission(info, "VIEW_SHIFT")`
- `shift`: `require_permission(info, "VIEW_SHIFT")`
- `active_shift`: `require_permission(info, "VIEW_SHIFT")`

**`app/graphql/queries/shift_template.py`** — Add to each resolver:
- `shift_templates`: `require_permission(info, "VIEW_SHIFT_TEMPLATE")`
- `shift_template`: `require_permission(info, "VIEW_SHIFT_TEMPLATE")`

---

## Phase 9: Database Migrations

Run these commands after all files are created:

```bash
# 1. Activate virtual environment (REQUIRED)
source python-pos-env-39/Scripts/activate

# 2. Load env vars (REQUIRED)
export $(grep -v '^#' .env | xargs)

# 3. Generate single migration for all 4 new tables
alembic revision --autogenerate -m "create_permission_role_user_role_role_permission_tables"

# 4. Apply migration
alembic upgrade head

# 5. Seed permissions and roles
python -m app.auth.seed_permissions
```

> **⚠️ Reminder:** If any of the above commands fail with import or database errors, verify you've run steps 1 and 2 first.

---

## Phase 10: Bootstrap First Super Admin

After seeding, create the first super admin user directly in the database:

```sql
-- Insert super admin user (password will be plaintext, login will flag for reset)
INSERT INTO users (username, email, first_name, last_name, hashed_password)
VALUES ('superadmin', 'admin@pos.com', 'Super', 'Admin', 'changeme123');

-- Assign SUPER_ADMIN role
INSERT INTO user_role (user_id, role_id, created_at, updated_at)
SELECT 
    (SELECT id FROM users WHERE username = 'superadmin'),
    (SELECT id FROM role WHERE code = 'SUPER_ADMIN'),
    NOW(), NOW();
```

---

## Phase 11: Verification

### Test Sequence in GraphQL Playground (`http://localhost:8000/graphql`)

```graphql
# 1. Try accessing without token (should fail)
query { users { id username } }

# 2. Login as super admin
mutation {
  login(username: "superadmin", password: "changeme123") {
    token { accessToken tokenType }
    user { id username }
    requiresPasswordReset
  }
}

# 3. Add token to HTTP Headers section in playground:
# { "Authorization": "Bearer <paste-token-here>" }

# 4. Check current user
query { me { id username email } }

# 5. Check your permissions
query { myPermissions }

# 6. Check your roles
query { myRoles { code name isSystemRole } }

# 7. Reset password (since it was plaintext)
mutation {
  resetPassword(oldPassword: "changeme123", newPassword: "SecurePass123!") 
}

# 8. Re-login with new password
mutation {
  login(username: "superadmin", password: "SecurePass123!") {
    token { accessToken }
    requiresPasswordReset
  }
}

# 9. Create a new user (requires CREATE_USER permission)
mutation {
  createUser(
    username: "cashier1"
    email: "cashier1@pos.com"
    firstName: "John"
    lastName: "Doe"
    hashedPassword: "welcome123"
  ) { id username }
}

# 10. Assign CASHIER role to new user
mutation {
  assignRoleToUser(userId: 2, roleId: 3) {
    id userId roleId
  }
}

# 11. Login as cashier and test permission denied
mutation {
  login(username: "cashier1", password: "welcome123") {
    token { accessToken }
  }
}
# Use cashier's token, then try:
mutation {
  createUser(username: "test", email: "t@t.com", firstName: "T", lastName: "T", hashedPassword: "x") {
    id
  }
}
# Expected: "Permission denied. Required permission: CREATE_USER"

# 12. But cashier CAN view products:
query { products { id name } }
```

---

## File Checklist

### New Files to Create (27)
- [ ] `app/auth/__init__.py`
- [ ] `app/auth/security.py`
- [ ] `app/auth/jwt.py`
- [ ] `app/auth/permissions.py`
- [ ] `app/auth/seed_permissions.py`
- [ ] `app/context.py`
- [ ] `app/schemas/auth.py`
- [ ] `app/schemas/permission.py`
- [ ] `app/schemas/role.py`
- [ ] `app/schemas/user_role.py`
- [ ] `app/schemas/role_permission.py`
- [ ] `app/models/permission.py`
- [ ] `app/models/role.py`
- [ ] `app/models/user_role.py`
- [ ] `app/models/role_permission.py`
- [ ] `app/graphql/mutations/auth.py`
- [ ] `app/graphql/mutations/permission.py`
- [ ] `app/graphql/mutations/role.py`
- [ ] `app/graphql/mutations/user_role.py`
- [ ] `app/graphql/mutations/role_permission.py`
- [ ] `app/graphql/queries/auth.py`
- [ ] `app/graphql/queries/permission.py`
- [ ] `app/graphql/queries/role.py`
- [ ] `app/graphql/queries/user_role.py`
- [ ] `app/graphql/queries/role_permission.py`

### Files to Modify (10)
- [ ] `.env` — Add JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_MINUTES
- [ ] `app/main.py` — Add context_getter
- [ ] `app/models/__init__.py` — Add 4 new model imports
- [ ] `alembic/env.py` — Add 4 new model imports
- [ ] `app/graphql/mutations/__init__.py` — Add 5 new mutation class imports
- [ ] `app/graphql/queries/__init__.py` — Add 5 new query class imports
- [ ] `app/graphql/mutations/user.py` — Add auth + password hashing
- [ ] `app/graphql/queries/user.py` — Add auth check
- [ ] All other existing mutation files (6 files) — Add auth checks
- [ ] All other existing query files (5 files) — Add auth checks

### Post-File Commands
- [ ] `pip install -r requirements.txt`
- [ ] `alembic revision --autogenerate -m "create_permission_role_user_role_role_permission_tables"`
- [ ] `alembic upgrade head`
- [ ] `python -m app.auth.seed_permissions`
- [ ] Insert super admin user via SQL
- [ ] Run verification tests

---

## Update `prompts/entity-context.md`

After implementation, add these 4 new entity sections to entity-context.md using the existing format:

1. **Permission** — Master data entity, soft delete only. Table: `permission`. Fields: id, code, name, description, category, deleted_at, deleted_by.
2. **Role** — Master data entity, soft delete only. Table: `role`. Fields: id, code, name, description, is_system_role, deleted_at, deleted_by.
3. **UserRole** — Junction entity, full audit. Table: `user_role`. Fields: id, user_id (FK→users), role_id (FK→role), + all audit fields.
4. **RolePermission** — Junction entity, full audit. Table: `role_permission`. Fields: id, role_id (FK→role), permission_id (FK→permission), + all audit fields.

Also add a new section: **"Authentication & Authorization"** documenting:
- JWT token flow
- Permission checking pattern (`require_permission(info, "CODE")`)
- Password hashing requirement
- Public vs protected operations
