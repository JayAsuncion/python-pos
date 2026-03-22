# Authentication & Permissions Reference

**Purpose:** Reference documentation for the JWT authentication and RBAC permission system

**Last Updated:** March 22, 2026

---

## Table of Contents
1. [Overview](#overview)
2. [JWT Authentication](#jwt-authentication)
3. [Permission-Based Authorization](#permission-based-authorization)
4. [Roles and Permissions](#roles-and-permissions)
5. [Adding New Permissions](#adding-new-permissions)
6. [GraphQL Context](#graphql-context)
7. [Password Management](#password-management)
8. [Security Best Practices](#security-best-practices)
9. [Complete Permission Map](#complete-permission-map)

---

## Overview

The Python POS system uses **stateless JWT authentication** with a **permission-based authorization** model (not role-based).

### Authentication Flow

```
1. User calls `login` mutation with username + password
   ↓
2. Server validates credentials (bcrypt)
   ↓
3. Server generates JWT token (60min expiry)
   ↓
4. Client stores token
   ↓
5. Client sends token in Authorization header: "Bearer <token>"
   ↓
6. Server validates token, loads user (via context getter)
   ↓
7. GraphQL resolvers check specific permissions
   ↓
8. Operation allowed or denied based on permissions
```

### Authorization Model

```
User → UserRole → Role → RolePermission → Permission
     (many)     (many)   (many)          (many)

Permission Check: Does user have permission code "CREATE_USER"?
```

**Key Concept:** We check for PERMISSIONS, not roles. A user might have role "MANAGER", but we check if they have the "CREATE_PRODUCT" permission (which happens to be granted to the MANAGER role).

---

## JWT Authentication

### Configuration

**Environment Variables (.env):**
```env
JWT_SECRET_KEY=<your-secret-key>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
```

**File:** `app/auth/jwt.py`

### Token Structure

**Token contains:**
- `sub`: Username
- `user_id`: User ID (for quick lookup)
- `exp`: Expiration timestamp
- `iat`: Issued at timestamp

**Example decoded token:**
```json
{
  "sub": "superadmin",
  "user_id": 1,
  "exp": 1742832000,
  "iat": 1742828400
}
```

### Login Flow

**GraphQL Mutation:**
```graphql
mutation {
  login(username: "superadmin", password: "mypassword") {
    token {
      accessToken
      tokenType
    }
    user {
      id
      username
      email
    }
    requiresPasswordReset
  }
}
```

**Response:**
```json
{
  "data": {
    "login": {
      "token": {
        "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "tokenType": "bearer"
      },
      "user": {
        "id": 1,
        "username": "superadmin",
        "email": "admin@pos.com"
      },
      "requiresPasswordReset": false
    }
  }
}
```

### Using the Token

**Include in all subsequent requests:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**In GraphQL Playground:**
Add to HTTP Headers section:
```json
{
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Public vs Protected Endpoints

**Public (no token required):**
- `login` - Authentication mutation

**Authenticated (token required, no permission check):**
- `me` - Get current user info
- `myPermissions` - List user's permissions
- `myRoles` - List user's roles
- `resetPassword` - Change own password

**Protected (token + specific permission required):**
- All other queries and mutations

---

## Permission-Based Authorization

### How It Works

**File:** `app/auth/permissions.py`

Every protected GraphQL resolver:
1. Accepts `info: strawberry.types.Info` parameter
2. Calls `require_permission(info, "PERMISSION_CODE")`
3. Function validates token and checks permission
4. Returns authenticated user or raises error

### Implementation Pattern

**For mutations (need user for audit):**
```python
from app.auth.permissions import require_permission

@strawberry.mutation
def create_product(self, info: strawberry.types.Info, name: str, ...) -> ProductType:
    user = require_permission(info, "CREATE_PRODUCT")
    
    # user is the authenticated User object
    # Use user.id for created_by, updated_by, deleted_by
    db = SessionLocal()
    product = ProductModel(
        name=name,
        created_by=user.id  # Audit trail
    )
    # ... rest of implementation
```

**For queries (don't need user object):**
```python
from app.auth.permissions import require_permission

@strawberry.field
def products(self, info: strawberry.types.Info) -> List[ProductType]:
    require_permission(info, "VIEW_PRODUCT")
    
    db = SessionLocal()
    products = db.query(ProductModel).filter(ProductModel.deleted_at.is_(None)).all()
    # ... rest of implementation
```

### Permission Check Flow

**Internal process:**
1. Extract JWT token from `Authorization` header
2. Decode token to get `user_id`
3. Load User from database
4. Query: User → UserRole → Role → RolePermission → Permission
5. Build set of permission codes user has
6. Check if required permission code exists in set
7. If yes → return user, if no → raise ValueError

### Permission Naming Convention

**Format:** `{ACTION}_{ENTITY}`

**Actions:**
- `VIEW` - Read operations (queries)
- `CREATE` - Create new records
- `UPDATE` - Modify existing records
- `DELETE` - Delete/soft-delete records
- Custom actions: `START_SHIFT`, `END_SHIFT`, `ASSIGN_ROLE`, `GRANT_PERMISSION`, etc.

**Entity:** SCREAMING_SNAKE_CASE version of entity name

**Examples:**
- `VIEW_PRODUCT`
- `CREATE_USER`
- `UPDATE_SHIFT_TEMPLATE`
- `DELETE_PRODUCT_SLOT`
- `START_SHIFT` (custom action)
- `ASSIGN_ROLE` (custom action)

---

## Roles and Permissions

### Permission Entity

**Table:** `permission`

**Fields:**
- `code` - Unique permission code (e.g., "CREATE_USER")
- `name` - Human-readable name
- `description` - Optional description
- `category` - Grouping (e.g., "USER", "PRODUCT", "RBAC")

**Categories:**
- `USER` - User management
- `PRODUCT` - Product operations
- `PRODUCT_TEMPLATE` - Product template management
- `PRODUCT_SLOT` - Product slot management
- `PRODUCT_SLOT_READING` - Reading operations
- `SHIFT` - Shift operations
- `SHIFT_TEMPLATE` - Shift template management
- `SHIFT_USER` - Shift user assignments
- `RBAC` - Role and permission management

### Role Entity

**Table:** `role`

**Fields:**
- `code` - Unique role code (e.g., "SUPER_ADMIN")
- `name` - Human-readable name
- `description` - Optional description
- `is_system_role` - Boolean (protected from modification)

### Default Roles

#### 1. SUPER_ADMIN (40 permissions)
- **Purpose:** Full system access
- **Permissions:** ALL permissions in the system
- **Protected:** Cannot be deleted or modified (is_system_role=true)

**Use case:** System administrators, full control

#### 2. MANAGER (23 permissions)
- **Purpose:** Operational management
- **Permissions:**
  - All VIEW permissions
  - All CREATE/UPDATE/DELETE for products, templates, slots, shifts
  - Limited RBAC: VIEW permissions/roles, ASSIGN/REVOKE roles
  - Basic user management: VIEW, CREATE, UPDATE users
- **Cannot:** Create/modify permissions or roles

**Use case:** Store managers, supervisors

#### 3. CASHIER (7 permissions)
- **Purpose:** Shift operations
- **Permissions:**
  - VIEW: Products, Product Templates, Product Slots, Shifts, Shift Templates
  - START_SHIFT, END_SHIFT
- **Cannot:** Edit anything, delete, or access RBAC

**Use case:** Cashiers, shift workers

#### 4. VIEWER (5 permissions)
- **Purpose:** Read-only access
- **Permissions:**
  - VIEW only: Products, Product Templates, Product Slots, Shifts, Shift Templates
- **Cannot:** Modify, delete, or start/end shifts

**Use case:** Auditors, observers, reporting

### Permission Distribution

**Total Permissions:** 40

```
USER: 4 permissions
  - VIEW_USER, CREATE_USER, UPDATE_USER, DELETE_USER

PRODUCT: 4 permissions
  - VIEW_PRODUCT, CREATE_PRODUCT, UPDATE_PRODUCT, DELETE_PRODUCT

PRODUCT_TEMPLATE: 4 permissions
  - VIEW_PRODUCT_TEMPLATE, CREATE_PRODUCT_TEMPLATE, UPDATE_PRODUCT_TEMPLATE, DELETE_PRODUCT_TEMPLATE

PRODUCT_SLOT: 4 permissions
  - VIEW_PRODUCT_SLOT, CREATE_PRODUCT_SLOT, UPDATE_PRODUCT_SLOT, DELETE_PRODUCT_SLOT

PRODUCT_SLOT_READING: 1 permission
  - DELETE_PRODUCT_SLOT_READING

SHIFT: 4 permissions
  - VIEW_SHIFT, START_SHIFT, END_SHIFT, DELETE_SHIFT

SHIFT_TEMPLATE: 4 permissions
  - VIEW_SHIFT_TEMPLATE, CREATE_SHIFT_TEMPLATE, UPDATE_SHIFT_TEMPLATE, DELETE_SHIFT_TEMPLATE

SHIFT_USER: 1 permission
  - DELETE_SHIFT_USER

RBAC (Roles & Permissions): 14 permissions
  - Permission management: 4 (VIEW, CREATE, UPDATE, DELETE)
  - Role management: 4 (VIEW, CREATE, UPDATE, DELETE)
  - User-Role management: 3 (VIEW, ASSIGN, REVOKE)
  - Role-Permission management: 3 (VIEW, GRANT, REVOKE)
```

---

## Adding New Permissions

### When to Add Permissions

- Creating a new entity (4 permissions: VIEW, CREATE, UPDATE, DELETE)
- Adding special operations (e.g., APPROVE_ORDER, GENERATE_REPORT)
- Adding custom mutations beyond CRUD

### Step-by-Step Process

#### Step 1: Add to Seed File

**Edit:** `app/auth/seed_permissions.py`

**Add to `BASE_PERMISSIONS` list:**
```python
BASE_PERMISSIONS = [
    # ... existing permissions ...
    
    # NewEntity
    ("VIEW_NEW_ENTITY", "View New Entities", "Can view new entity list and details", "NEW_ENTITY"),
    ("CREATE_NEW_ENTITY", "Create New Entity", "Can create new entities", "NEW_ENTITY"),
    ("UPDATE_NEW_ENTITY", "Update New Entity", "Can update new entity details", "NEW_ENTITY"),
    ("DELETE_NEW_ENTITY", "Delete New Entity", "Can delete new entities", "NEW_ENTITY"),
]
```

#### Step 2: Run Seeding Script

```bash
source python-pos-env-39/Scripts/activate
export $(grep -v '^#' .env | xargs)
python -m app.auth.seed_permissions
```

**Output:**
```
=== Seeding Permissions ===
Seeded 4 new permissions (44 total defined)

=== Seeding Default Roles ===
Seeded 0 new roles (4 total defined)

=== Done! ===
```

#### Step 3: Assign to Roles (Optional)

**Option A: Update DEFAULT_ROLES in seed file**

```python
DEFAULT_ROLES = [
    # ... existing roles ...
    (
        "MANAGER",
        "Manager",
        "Can manage products, shifts, and view reports",
        [
            # ... existing permissions ...
            "VIEW_NEW_ENTITY", "CREATE_NEW_ENTITY", "UPDATE_NEW_ENTITY", "DELETE_NEW_ENTITY",
        ],
    ),
]
```

Then run seeding script again.

**Option B: Use GraphQL mutations**

```graphql
mutation {
  addPermissionToRole(roleId: 2, permissionId: 41) {
    id
    roleId
    permissionId
  }
}
```

#### Step 4: Use in Resolvers

```python
@strawberry.mutation
def create_new_entity(self, info: strawberry.types.Info, ...) -> NewEntityType:
    user = require_permission(info, "CREATE_NEW_ENTITY")
    # ... implementation
```

---

## GraphQL Context

### Custom Context Structure

**File:** `app/context.py`

**Context object:**
```python
{
    "request": Request,  # FastAPI request object
    "user": User | None  # Authenticated user or None if not authenticated
}
```

### How Context is Set

1. Every GraphQL request goes through `get_context()` function
2. Function extracts JWT from `Authorization` header
3. Decodes token to get `user_id`
4. Loads User from database
5. Returns context dict with user

### Accessing Context in Resolvers

```python
def my_resolver(self, info: strawberry.types.Info):
    # Get authenticated user
    user = info.context.get("user")  # User object or None
    
    # Get request object
    request = info.context.get("request")  # FastAPI Request
```

### Using Permission Helpers

**Preferred (use helper functions):**
```python
from app.auth.permissions import require_permission, require_auth

# For protected operations:
user = require_permission(info, "CREATE_PRODUCT")

# For authenticated but not permission-checked operations:
user = require_auth(info)
```

**Manual (not recommended):**
```python
user = info.context.get("user")
if not user:
    raise ValueError("Authentication required")
# ... manual permission check ...
```

---

## Password Management

### Password Hashing

**Algorithm:** bcrypt via passlib  
**File:** `app/auth/security.py`

**Functions:**
- `hash_password(password: str) -> str` - Hash plaintext password
- `verify_password(plain: str, hashed: str) -> bool` - Verify password
- `is_bcrypt_hash(value: str) -> bool` - Check if string is bcrypt hash

### Legacy Plaintext Detection

**Problem:** Database may contain legacy plaintext passwords

**Solution:** Login mutation detects plaintext and flags for reset

```python
if is_bcrypt_hash(user.hashed_password):
    # Properly hashed - verify with bcrypt
    if not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")
else:
    # Plaintext (legacy) - compare directly
    if password != user.hashed_password:
        raise ValueError("Invalid credentials")
    requires_reset = True  # Flag for password reset
```

### Password Reset Flow

**For self:**
```graphql
mutation {
  resetPassword(oldPassword: "current", newPassword: "newsecure123") 
}
```

**For other users (admin only):**
```graphql
mutation {
  changeUserPassword(userId: 5, newPassword: "temporarypass")
}
```

**Requires:** `UPDATE_USER` permission

### Best Practices

1. **Never return passwords** - UserType schema excludes `hashed_password`
2. **Always hash on create/update** - Use `hash_password()` before saving
3. **Force reset for plaintext** - Return `requiresPasswordReset: true` in login
4. **Use strong secrets** - Generate secure JWT_SECRET_KEY
5. **Constant-time comparison** - bcrypt.verify prevents timing attacks

---

## Security Best Practices

### 1. Token Security

✅ **Do:**
- Store JWT in secure storage (httpOnly cookies or secure local storage)
- Include token in `Authorization: Bearer <token>` header
- Implement token refresh logic before expiry
- Clear token on logout

❌ **Don't:**
- Store tokens in plain localStorage if XSS is a risk
- Send tokens in URL parameters
- Share tokens between users
- Use expired tokens

### 2. Permission Checks

✅ **Do:**
- Use `require_permission()` on every protected resolver
- Check for specific permissions, not roles
- Use descriptive permission codes
- Return meaningful error messages

❌ **Don't:**
- Skip permission checks
- Hard-code role checks (e.g., `if user.role == "admin"`)
- Expose sensitive data in error messages
- Create unprotected endpoints (except login)

### 3. Password Management

✅ **Do:**
- Hash all passwords with bcrypt
- Use strong password policies
- Force password reset for plaintext passwords
- Implement password history (optional)

❌ **Don't:**
- Store plaintext passwords
- Return passwords in API responses
- Use weak hashing algorithms
- Log passwords (even hashed)

### 4. Audit Trails

✅ **Do:**
- Use authenticated user for created_by, updated_by, deleted_by
- Track all RBAC changes (UserRole, RolePermission)
- Log security events (login attempts, permission denials)
- Use full audit trail for sensitive entities

❌ **Don't:**
- Use hardcoded user IDs for audit fields
- Skip audit fields
- Delete audit records
- Expose PII in audit logs

### 5. Database Security

✅ **Do:**
- Use parameterized queries (SQLAlchemy ORM)
- Filter soft-deleted records
- Use transactions for multi-step operations
- Close database sessions

❌ **Don't:**
- Build SQL strings manually
- Trust user input
- Leave database sessions open
- Return deleted records

---

## Complete Permission Map

| Entity | Operation | Permission Code | Default Roles |
|--------|-----------|-----------------|---------------|
| **User** | Query users | `VIEW_USER` | SUPER_ADMIN, MANAGER, VIEWER |
| **User** | Create user | `CREATE_USER` | SUPER_ADMIN, MANAGER |
| **User** | Update user | `UPDATE_USER` | SUPER_ADMIN, MANAGER |
| **User** | Delete user | `DELETE_USER` | SUPER_ADMIN |
| **Product** | Query products | `VIEW_PRODUCT` | SUPER_ADMIN, MANAGER, CASHIER, VIEWER |
| **Product** | Create product | `CREATE_PRODUCT` | SUPER_ADMIN, MANAGER |
| **Product** | Update product | `UPDATE_PRODUCT` | SUPER_ADMIN, MANAGER |
| **Product** | Delete product | `DELETE_PRODUCT` | SUPER_ADMIN, MANAGER |
| **ProductTemplate** | Query templates | `VIEW_PRODUCT_TEMPLATE` | SUPER_ADMIN, MANAGER, CASHIER, VIEWER |
| **ProductTemplate** | Create template | `CREATE_PRODUCT_TEMPLATE` | SUPER_ADMIN, MANAGER |
| **ProductTemplate** | Update template | `UPDATE_PRODUCT_TEMPLATE` | SUPER_ADMIN, MANAGER |
| **ProductTemplate** | Delete template | `DELETE_PRODUCT_TEMPLATE` | SUPER_ADMIN, MANAGER |
| **ProductSlot** | Query slots | `VIEW_PRODUCT_SLOT` | SUPER_ADMIN, MANAGER, CASHIER, VIEWER |
| **ProductSlot** | Create slot | `CREATE_PRODUCT_SLOT` | SUPER_ADMIN, MANAGER |
| **ProductSlot** | Update slot | `UPDATE_PRODUCT_SLOT` | SUPER_ADMIN, MANAGER |
| **ProductSlot** | Delete slot | `DELETE_PRODUCT_SLOT` | SUPER_ADMIN, MANAGER |
| **ProductSlotReading** | Delete reading | `DELETE_PRODUCT_SLOT_READING` | SUPER_ADMIN, MANAGER |
| **Shift** | Query shifts | `VIEW_SHIFT` | SUPER_ADMIN, MANAGER, CASHIER, VIEWER |
| **Shift** | Start shift | `START_SHIFT` | SUPER_ADMIN, MANAGER, CASHIER |
| **Shift** | End shift | `END_SHIFT` | SUPER_ADMIN, MANAGER, CASHIER |
| **Shift** | Delete shift | `DELETE_SHIFT` | SUPER_ADMIN, MANAGER |
| **ShiftTemplate** | Query templates | `VIEW_SHIFT_TEMPLATE` | SUPER_ADMIN, MANAGER, CASHIER, VIEWER |
| **ShiftTemplate** | Create template | `CREATE_SHIFT_TEMPLATE` | SUPER_ADMIN, MANAGER |
| **ShiftTemplate** | Update template | `UPDATE_SHIFT_TEMPLATE` | SUPER_ADMIN, MANAGER |
| **ShiftTemplate** | Delete template | `DELETE_SHIFT_TEMPLATE` | SUPER_ADMIN, MANAGER |
| **ShiftUser** | Delete assignment | `DELETE_SHIFT_USER` | SUPER_ADMIN, MANAGER |
| **Permission** | Query permissions | `VIEW_PERMISSION` | SUPER_ADMIN |
| **Permission** | Create permission | `CREATE_PERMISSION` | SUPER_ADMIN |
| **Permission** | Update permission | `UPDATE_PERMISSION` | SUPER_ADMIN |
| **Permission** | Delete permission | `DELETE_PERMISSION` | SUPER_ADMIN |
| **Role** | Query roles | `VIEW_ROLE` | SUPER_ADMIN, MANAGER |
| **Role** | Create role | `CREATE_ROLE` | SUPER_ADMIN |
| **Role** | Update role | `UPDATE_ROLE` | SUPER_ADMIN |
| **Role** | Delete role | `DELETE_ROLE` | SUPER_ADMIN |
| **UserRole** | Query user roles | `VIEW_USER_ROLE` | SUPER_ADMIN |
| **UserRole** | Assign role | `ASSIGN_ROLE` | SUPER_ADMIN, MANAGER |
| **UserRole** | Revoke role | `REVOKE_ROLE` | SUPER_ADMIN, MANAGER |
| **RolePermission** | Query role perms | `VIEW_ROLE_PERMISSION` | SUPER_ADMIN |
| **RolePermission** | Grant permission | `GRANT_PERMISSION` | SUPER_ADMIN |
| **RolePermission** | Revoke permission | `REVOKE_PERMISSION` | SUPER_ADMIN |

**Public (no authentication):** `login`

**Authenticated (no permission check):** `me`, `myPermissions`, `myRoles`, `resetPassword`

---

## Troubleshooting

### "Authentication required" error

**Problem:** No token or invalid token

**Solutions:**
1. Check token is included in `Authorization` header
2. Verify token hasn't expired (60min limit)
3. Confirm token format: `Bearer <token>`
4. Re-login to get new token

### "Permission denied" error

**Problem:** User doesn't have required permission

**Solutions:**
1. Check user's permissions: `query { myPermissions }`
2. Check user's roles: `query { myRoles { code name } }`
3. Assign missing permission to user's role
4. Or assign user to role with permission

### "User not found" error

**Problem:** Token contains invalid user_id

**Solutions:**
1. User may have been deleted
2. Database may have been reset
3. Re-login with valid credentials

### Permission seeding not working

**Problem:** Permissions not appearing in database

**Solutions:**
1. Check virtual environment is activated
2. Check .env is loaded: `export $(grep -v '^#' .env | xargs)`
3. Verify database connection in .env
4. Check seed_permissions.py for syntax errors
5. Run with verbose output: `python -m app.auth.seed_permissions`

---

## Quick Reference

### Common Commands

```bash
# Activate virtual environment
source python-pos-env-39/Scripts/activate

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Seed permissions
python -m app.auth.seed_permissions

# Check user permissions (GraphQL)
query { myPermissions }

# Check user roles (GraphQL)
query { myRoles { code name } }
```

### Common GraphQL Operations

```graphql
# Login
mutation {
  login(username: "user", password: "pass") {
    token { accessToken }
    requiresPasswordReset
  }
}

# Get current user
query {
  me { id username email }
}

# Reset password
mutation {
  resetPassword(oldPassword: "old", newPassword: "new")
}

# Assign role to user
mutation {
  assignRoleToUser(userId: 2, roleId: 3) {
    id
  }
}

# Grant permission to role
mutation {
  addPermissionToRole(roleId: 2, permissionId: 10) {
    id
  }
}
```

---

**For entity creation with RBAC, see [02-entity-creation-guide.md](02-entity-creation-guide.md).**

**For entity reference, see [01-entity-reference.md](01-entity-reference.md).**
