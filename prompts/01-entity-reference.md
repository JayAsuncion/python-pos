# Entity Reference Documentation

**Purpose:** Single source of truth for all entities in the Python POS system

**Last Updated:** March 22, 2026

---

## Table of Contents
1. [Master Data Entities](#master-data-entities)
2. [Operational Entities](#operational-entities)
3. [Junction/Association Entities](#junctionassociation-entities)
4. [Entity Relationships](#entity-relationships)
5. [Common Patterns](#common-patterns)
6. [Authentication & Authorization](#authentication--authorization)

---

## Master Data Entities

### User
**Purpose:** User management and authentication

**Table:** `users`

**Key Fields:**
- `id` (PK) - Integer
- `username` - String, unique, indexed
- `email` - String, unique, indexed
- `first_name` - String, indexed
- `last_name` - String, indexed
- `hashed_password` - String

**Audit Pattern:** None (simplest entity)

**Relationships:**
- Referenced by: Shift (started_by, ended_by), ShiftUser, all audit fields (created_by, updated_by, deleted_by)

**Business Rules:**
- Username and email must be unique
- No soft delete capability

---

### Permission
**Purpose:** Defines system permissions for fine-grained access control

**Table:** `permission`

**Key Fields:**
- `id` (PK) - Integer
- `code` - String, unique (e.g., "CREATE_USER", "VIEW_PRODUCT")
- `name` - String (human-readable name)
- `description` - String (optional)
- `category` - String (e.g., "USER", "PRODUCT", "RBAC")
- Soft delete fields: `deleted_at`, `deleted_by`

**Audit Pattern:** Soft delete only

**Relationships:**
- Referenced by: RolePermission (many-to-many with Role)

**Business Rules:**
- Code must be unique and follows SCREAMING_SNAKE_CASE convention
- Base permissions are seeded via `app/auth/seed_permissions.py`
- New permissions can be added dynamically via GraphQL mutations
- Category groups related permissions together for UI organization
- Cannot hard delete permissions that are assigned to roles

---

### Role
**Purpose:** Groups permissions into named roles for assignment to users

**Table:** `role`

**Key Fields:**
- `id` (PK) - Integer
- `code` - String, unique (e.g., "SUPER_ADMIN", "CASHIER")
- `name` - String (human-readable name)
- `description` - String (optional)
- `is_system_role` - Boolean (true for seeded default roles)
- Soft delete fields: `deleted_at`, `deleted_by`

**Audit Pattern:** Soft delete only

**Relationships:**
- Referenced by: UserRole (many-to-many with User)
- Referenced by: RolePermission (many-to-many with Permission)

**Business Rules:**
- Code must be unique and follows SCREAMING_SNAKE_CASE convention
- System roles (SUPER_ADMIN, MANAGER, CASHIER, VIEWER) are protected from modification
- Cannot delete system roles
- Custom roles can be created via GraphQL mutations
- Permissions are assigned to roles, not directly to users
- Cannot hard delete roles that have active user assignments

---

### ProductTemplate
**Purpose:** Master template/prototype definition for product types

**Table:** `product_template`

**Key Fields:**
- `id` (PK) - Integer
- `name` - String
- `code` - String, unique
- `image` - String (optional)
- `is_active` - Boolean
- Soft delete fields: `deleted_at`, `deleted_by`

**Audit Pattern:** Soft delete only (no created/updated tracking)

**Relationships:**
- One-to-many with Product

**Business Rules:**
- Code must be unique
- Can be soft deleted
- Serves as master data for creating product instances

---

### Product
**Purpose:** Actual product instances with pricing, inventory, and specific attributes

**Table:** `product`

**Key Fields:**
- `id` (PK) - Integer
- `product_template_id` (FK) - Reference to ProductTemplate
- `name` - String
- `code` - String, unique
- `image` - String (optional)
- `starting_stock` - Numeric(15,6) - initial inventory
- `running_stock` - Numeric(15,6) - current inventory
- `cost_price` - Numeric(15,6)
- `selling_price` - Numeric(15,6)
- `is_active` - Boolean
- Full audit fields: `deleted_at`, `deleted_by`, `created_at`, `created_by`, `updated_at`, `updated_by`

**Audit Pattern:** Full audit trail (soft delete + timestamps)

**Relationships:**
- Many-to-one with ProductTemplate
- One-to-many with ProductSlot (current assignments)
- One-to-many with ProductSlotReading (historical snapshots)

**Business Rules:**
- Code must be unique
- Must reference a valid ProductTemplate
- Pricing and stock use Numeric(15,6) precision
- Can be soft deleted

---

### ProductSlot
**Purpose:** Physical locations/slots where products are placed (e.g., dispensers, shelves)

**Table:** `product_slot`

**Key Fields:**
- `id` (PK) - Integer
- `slot_name` - String (e.g., "Slot A1", "Dispenser 3")
- `product_id` (FK) - Currently assigned product (nullable)
- `is_active` - Boolean
- Full audit fields: `deleted_at`, `deleted_by`, `created_at`, `created_by`, `updated_at`, `updated_by`

**Audit Pattern:** Full audit trail

**Relationships:**
- Many-to-one with Product (current assignment)
- One-to-many with ProductSlotReading

**Business Rules:**
- Can exist without an assigned product (`product_id` nullable)
- Slot name identifies the physical location
- Product assignment can change over time

---

### ShiftTemplate
**Purpose:** Defines shift schedules (e.g., "Morning 8am-4pm", "Evening 4pm-12am")

**Table:** `shift_template`

**Key Fields:**
- `id` (PK) - Integer
- `shift_name` - String (e.g., "Shift A", "Morning Shift")
- `start_time` - Time with TZ (scheduled start)
- `end_time` - Time with TZ (scheduled end)
- `order` - Integer (sequence order: 1, 2, 3 for ordering and validation)
- `is_active` - Boolean
- Full audit fields: `deleted_at`, `deleted_by`, `created_at`, `created_by`, `updated_at`, `updated_by`

**Audit Pattern:** Full audit trail

**Relationships:**
- One-to-many with Shift (instances of this template)

**Business Rules:**
- Templates define the schedule but do NOT track actual occurrences
- Order field enables UI sorting and cross-shift validation
- Start/end times are time-only (not datetime) - defines typical schedule
- Can span multiple calendar days (e.g., night shift 11pm-7am)

---

## Operational Entities

### Shift
**Purpose:** Tracks actual shift occurrences with date, time, and users

**Table:** `shift`

**Key Fields:**
- `id` (PK) - Integer
- `shift_template_id` (FK) - Which shift template this instance represents
- `shift_date` - Date (calendar date this shift belongs to)
- `actual_start_datetime` - Timestamp TZ (when user clicked "Start Shift")
- `actual_end_datetime` - Timestamp TZ (when user clicked "End Shift", nullable until ended)
- `started_by` (FK → users) - User who initiated the shift
- `ended_by` (FK → users) - User who ended the shift (nullable)
- `status` - String ("active" or "completed")
- `is_active` - Boolean
- Full audit fields: `deleted_at`, `deleted_by`, `created_at`, `created_by`, `updated_at`, `updated_by`

**Audit Pattern:** Full audit trail

**Relationships:**
- Many-to-one with ShiftTemplate
- Many-to-one with User (started_by)
- Many-to-one with User (ended_by)  
- One-to-many with ShiftUser
- One-to-many with ProductSlotReading

**Business Rules:**
- Only ONE active shift per shift template at a time (validation required)
- Status transitions: "active" → "completed" (one-way)
- `actual_start_datetime` uses server timestamp when shift starts
- `actual_end_datetime` populated when shift ends
- `shift_date` is the business date (may differ from actual start time for night shifts)
- Separate tracking of who started vs who ended the shift for accountability

---

### ProductSlotReading
**Purpose:** Records meter readings per product slot per shift with cost/revenue calculations

**Table:** `product_slot_reading`

**Key Fields:**
- `id` (PK) - Integer
- `shift_id` (FK) - The shift this reading belongs to
- `product_slot_id` (FK) - Which slot was measured
- `product_id` (FK) - Product snapshot (what was in the slot at shift start)
- `start_reading` - Numeric(15,6) (meter reading at shift start)
- `end_reading` - Numeric(15,6) (meter reading at shift end, nullable until shift ends)
- `start_reading_image_url` - String, NOT NULL (required photo URL, e.g., S3 link)
- `end_reading_image_url` - String, nullable (required when shift ends)
- `cost_price_snapshot` - Numeric(15,6) (product cost price at shift start)
- `selling_price_snapshot` - Numeric(15,6) (product selling price at shift start)  
- Audit fields: `deleted_at`, `deleted_by`, `created_at`, `created_by`, `updated_at`, `updated_by`

**Computed Properties:**
- `quantity_sold` - `end_reading - start_reading`
- `revenue_amount` - `quantity_sold * selling_price_snapshot`
- `cost_amount` - `quantity_sold * cost_price_snapshot`

**Unique Constraint:** `(shift_id, product_slot_id)` - one reading record per slot per shift

**Audit Pattern:** Full audit trail

**Relationships:**
- Many-to-one with Shift
- Many-to-one with ProductSlot
- Many-to-one with Product (snapshot)

**Business Rules:**
- One reading record per product slot per shift (enforced by unique constraint)
- Start reading photo is REQUIRED (cannot start shift without photos)
- End reading photo is REQUIRED when ending shift
- Pricing is snapshotted at shift start (immutable for historical accuracy)
- Product assignment is snapshotted (even if slot product changes later)
- Validation: `end_reading` must be >= `start_reading`
- Computed properties calculated from readings and snapshot prices

---

## Junction/Association Entities

### ShiftUser
**Purpose:** Many-to-many relationship tracking which users worked on a shift

**Table:** `shift_user`

**Key Fields:**
- `id` (PK) - Integer
- `shift_id` (FK → shift)
- `user_id` (FK → users)
- Standard audit fields

**Audit Pattern:** Full audit trail

**Relationships:**
- Many-to-one with Shift
- Many-to-one with User

**Business Rules:**
- Records all users assigned to work a shift (multi-select at shift start)
- User list is locked at shift start (cannot be modified during shift)
- Separate from `started_by` and `ended_by` fields (those track who clicked buttons)

---

### UserRole
**Purpose:** Many-to-many relationship tracking which roles are assigned to each user

**Table:** `user_role`

**Key Fields:**
- `id` (PK) - Integer
- `user_id` (FK → users)
- `role_id` (FK → role)
- Full audit fields: `deleted_at`, `deleted_by`, `created_at`, `created_by`, `updated_at`, `updated_by`

**Audit Pattern:** Full audit trail

**Relationships:**
- Many-to-one with User
- Many-to-one with Role

**Business Rules:**
- A user can have multiple roles
- A role can be assigned to multiple users
- Soft delete preserves historical role assignments
- Audit trail tracks who assigned/revoked roles and when

---

### RolePermission
**Purpose:** Many-to-many relationship defining which permissions are granted to each role

**Table:** `role_permission`

**Key Fields:**
- `id` (PK) - Integer
- `role_id` (FK → role)
- `permission_id` (FK → permission)
- Full audit fields: `deleted_at`, `deleted_by`, `created_at`, `created_by`, `updated_at`, `updated_by`

**Audit Pattern:** Full audit trail

**Relationships:**
- Many-to-one with Role
- Many-to-one with Permission

**Business Rules:**
- A role can have multiple permissions
- A permission can be granted to multiple roles
- Default role-permission mappings are seeded via `app/auth/seed_permissions.py`
- Permissions can be dynamically added/removed from roles
- Soft delete preserves historical permission grants
- Audit trail tracks who granted/revoked permissions and when

---

## Entity Relationships

### Relationship Diagram (Text)

```
User
├─→ Shift.started_by (who started shift)
├─→ Shift.ended_by (who ended shift)
├─→ ShiftUser.user_id (who worked on shift)
├─→ UserRole.user_id (role assignments)
└─→ [All audit fields: created_by, updated_by, deleted_by]

ProductTemplate
└─→ Product.product_template_id

Product
├─→ ProductSlot.product_id (current assignment)
└─→ ProductSlotReading.product_id (historical snapshot)

ProductSlot
└─→ ProductSlotReading.product_slot_id

ShiftTemplate
└─→ Shift.shift_template_id

Shift
├─→ ShiftUser.shift_id
└─→ ProductSlotReading.shift_id

Permission
└─→ RolePermission.permission_id

Role
├─→ UserRole.role_id
└─→ RolePermission.role_id

RBAC Flow: User → UserRole → Role → RolePermission → Permission
```

---

## Common Patterns

### Audit Trail Levels

1. **No Audit** (User only)
   - Just basic fields
   - No tracking of changes

2. **Soft Delete Only** (ProductTemplate, Permission, Role)
   - Fields: `deleted_at`, `deleted_by`
   - Records marked as deleted but not removed
   - No update tracking

3. **Full Audit Trail** (Product, ProductSlot, ShiftTemplate, Shift, ShiftUser, ProductSlotReading, UserRole, RolePermission)
   - Fields: `deleted_at`, `deleted_by`, `created_at`, `created_by`, `updated_at`, `updated_by`
   - Complete tracking of all changes
   - Who created, who last updated, who deleted

### Field Conventions

- **Primary Keys:** Always `id` (Integer, auto-increment)
- **Foreign Keys:** `{table_singular}_id` (e.g., `product_id`, `shift_template_id`)
- **Booleans:** `is_active`, `is_deleted` format
- **Timestamps:** `{action}_at` format (e.g., `created_at`, `deleted_at`)
- **User References:** `{action}_by` format (e.g., `created_by`, `started_by`)
- **Indexes:** Primary keys are indexed; unique fields are indexed
- **Numeric Precision:** Numeric(15, 6) for all money and measurement fields

### GraphQL Naming

- **Python (DB):** snake_case (e.g., `shift_name`, `product_id`)
- **GraphQL:** camelCase (e.g., `shiftName`, `productId`)
- **Types:** PascalCase + "Type" suffix (e.g., `ShiftType`, `ProductSlotReadingType`)
- **Queries:** camelCase, plural for lists (e.g., `shifts`, `products`)
- **Mutations:** camelCase with verb prefix (e.g., `createProduct`, `startShift`)

### Standard Mutations (CRUD Entities)

- `create{Entity}` - Create new record
- `update{Entity}` - Update existing record (all fields optional)
- `delete{Entity}` - Soft delete (marks deleted_at, doesn't remove from DB)

### Special Mutations (Workflow Operations)

- `startShift` - Complex operation: creates Shift + ShiftUser + ProductSlotReading records
- `endShift` - Complex operation: updates readings, validates, marks shift completed

---

## Business Workflow: Shift Tracking

### Starting a Shift

**Triggered by:** User selects shift template, records users and start readings

**GraphQL:** `startShift` mutation

**Validations:**
1. No active shift exists for this shift template
2. All selected product slots have assigned products
3. Start reading photos are provided for all slots

**Creates:**
1. One `Shift` record (status: "active")
2. Multiple `ShiftUser` records (one per selected user)
3. Multiple `ProductSlotReading` records (one per product slot)
   - Snapshots product_id, cost_price, selling_price
   - Records start_reading and start_reading_image_url
   - end_reading and end_reading_image_url remain NULL

**Result:** Active shift ready for operations

---

### Ending a Shift

**Triggered by:** User enters end readings and photos

**GraphQL:** `endShift` mutation

**Validations:**
1. Shift exists and is active
2. All end_reading values >= corresponding start_reading values  
3. End reading photos provided for all slots

**Updates:**
1. All `ProductSlotReading` records for this shift
   - Sets end_reading and end_reading_image_url
   - Computes quantity_sold, revenue_amount, cost_amount
2. The `Shift` record
   - Sets actual_end_datetime
   - Sets ended_by
   - Changes status to "completed"

**Result:** Completed shift with full sales calculation

---

## Authentication & Authorization

### JWT Token Flow

**Authentication Method:** Stateless JWT (JSON Web Token) authentication

**Configuration:**
- Algorithm: HS256
- Expiration: 60 minutes (configurable via JWT_EXPIRATION_MINUTES)
- Secret Key: Stored in `.env` file (JWT_SECRET_KEY)

**Login Flow:**
1. Client calls `login` mutation with username and password
2. Server validates credentials using bcrypt password verification
3. If valid, server generates JWT token containing user ID
4. Client receives token and stores it for subsequent requests
5. Client includes token in `Authorization: Bearer <token>` header for all protected operations

**Token Contents:**
- `sub` (subject): User ID
- `exp` (expiration): Token expiry timestamp
- `iat` (issued at): Token creation timestamp

**Public Operations (No Authentication Required):**
- `login` - Authenticate and get token

**Authenticated Operations (Token Required, No Permission Check):**
- `me` - Get current user info
- `myPermissions` - List current user's permissions
- `myRoles` - List current user's roles
- `resetPassword` - Change own password

**Protected Operations (Token + Permission Required):**
- All other queries and mutations require valid JWT AND appropriate permission

---

### Password Management

**Password Hashing:**
- Algorithm: bcrypt via passlib
- All new passwords are automatically hashed before storage
- Plaintext password detection: Database may contain legacy plaintext passwords

**Password Reset Flow:**
1. Login response includes `requiresPasswordReset: Boolean` flag
2. If true (plaintext password detected), user must call `resetPassword` before normal operations
3. `resetPassword` mutation validates old password and hashes new password
4. Admin users can force password reset for other users via `changeUserPassword` (requires UPDATE_USER permission)

**Security Rules:**
- Passwords must never be returned in GraphQL responses
- Password verification uses constant-time comparison (bcrypt.verify)
- Old plaintext passwords can still be used for verification but trigger reset requirement

---

### Permission-Based Authorization

**Authorization Model:** Permission-based (not role-based)

**Permission Check Flow:**
1. Extract JWT token from `Authorization` header in request
2. Decode token to get user ID
3. Load user from database
4. Traverse relationships: User → UserRole → Role → RolePermission → Permission
5. Build set of permission codes user has access to
6. Check if required permission code exists in user's permission set
7. Allow operation if permission exists, deny otherwise

**Implementation Pattern:**

Every protected GraphQL resolver must:
```python
from app.auth.permissions import require_permission
import strawberry.types

@strawberry.mutation
def create_product(self, info: strawberry.types.Info, name: str, ...) -> ProductType:
    require_permission(info, "CREATE_PRODUCT")
    # ... rest of mutation logic
```

**Permission Naming Convention:**
- Format: `{ACTION}_{ENTITY}` (e.g., `CREATE_USER`, `VIEW_PRODUCT`, `DELETE_SHIFT`)
- Actions: `VIEW`, `CREATE`, `UPDATE`, `DELETE`, and custom actions (e.g., `START_SHIFT`, `GRANT_PERMISSION`)
- Special permissions: `ASSIGN_ROLE`, `REVOKE_ROLE`, `GRANT_PERMISSION`, `REVOKE_PERMISSION`

**Permission Categories:**
- `USER` - User management operations
- `PRODUCT` - Product CRUD operations
- `PRODUCT_TEMPLATE` - Product template management
- `PRODUCT_SLOT` - Product slot management
- `PRODUCT_SLOT_READING` - Reading deletion (only delete allowed)
- `SHIFT` - Shift operations
- `SHIFT_TEMPLATE` - Shift template management
- `SHIFT_USER` - Shift user assignment deletion
- `RBAC` - Role and permission management

**Default Roles and Permissions:**

1. **SUPER_ADMIN** (40 permissions)
   - All permissions in the system
   - System role, cannot be modified or deleted

2. **MANAGER** (23 permissions)
   - All VIEW permissions
   - All CREATE/UPDATE/DELETE for products, templates, slots, shifts
   - Limited RBAC: VIEW permissions/roles, ASSIGN/REVOKE roles
   - Cannot create/modify permissions or roles

3. **CASHIER** (7 permissions)
   - VIEW: Products, Product Templates, Product Slots, Shifts, Shift Templates
   - START_SHIFT, END_SHIFT
   - No administrative or editing capabilities

4. **VIEWER** (5 permissions)
   - VIEW only: Products, Product Templates, Product Slots, Shifts, Shift Templates
   - Read-only access, no modifications

**Permission Seeding:**
- Base permissions defined in `app/auth/seed_permissions.py`
- Run with: `python -m app.auth.seed_permissions`
- Idempotent: Safe to run multiple times, skips existing records
- New permissions can be added dynamically via `createPermission` mutation

---

### GraphQL Context

**Custom Context Structure:**
```python
{
    "request": Request,  # FastAPI request object
    "user": User | None  # Authenticated user or None
}
```

**Context Getter:** `app/context.py` extracts JWT from headers and loads user

**Accessing Context in Resolvers:**
```python
def my_resolver(self, info: strawberry.types.Info):
    user = info.context.get("user")  # Authenticated user or None
    request = info.context.get("request")  # FastAPI request object
```

---

### Security Best Practices

1. **Never expose passwords:** User queries/mutations never return `hashed_password` field
2. **Always verify tokens:** Use `require_auth()` or `require_permission()` on all protected operations
3. **Use permission checks, not role checks:** Check for `CREATE_USER` permission, not `is_admin` flag
4. **Audit all permission changes:** Full audit trail on UserRole and RolePermission
5. **Protect system roles:** System roles (is_system_role=true) cannot be deleted or have permissions modified
6. **Force password resets:** Detect legacy plaintext passwords and require reset on next login
7. **Token expiration:** Tokens expire after 60 minutes, client must re-authenticate
8. **Centralized permission logic:** All permission checks go through `app/auth/permissions.py`

---

## Entity Summary

**Total Entities:** 12

**Master Data (5):**
- User
- Permission
- Role
- ProductTemplate
- ShiftTemplate

**Operational (3):**
- Product
- ProductSlot
- Shift
- ProductSlotReading

**Junction (3):**
- UserRole
- RolePermission
- ShiftUser

**Audit Patterns:**
- No audit: 1 (User)
- Soft delete only: 3 (Permission, Role, ProductTemplate)
- Full audit trail: 8 (Product, ProductSlot, ShiftTemplate, Shift, ProductSlotReading, UserRole, RolePermission, ShiftUser)

---

**Remember:** This document must be kept up-to-date. When you create, modify, or delete entities, update this file immediately. See [02-entity-creation-guide.md](02-entity-creation-guide.md) for the mandatory update checklist.
