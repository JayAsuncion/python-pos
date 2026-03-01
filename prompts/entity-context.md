# Entity Context Map

**⚠️ IMPORTANT:** This document must be kept up-to-date whenever entities are created, modified, or deleted.  
See [`AGENTS.md`](AGENTS.md) for the mandatory update checklist.

This document provides a comprehensive overview of all entities in the Python POS system, their relationships, and business rules.

**Last Updated:** March 1, 2026

---

## Table of Contents
1. [Master Data Entities](#master-data-entities)
2. [Operational Entities](#operational-entities)
3. [Junction/Association Entities](#junctionassociation-entities)
4. [Entity Relationships](#entity-relationships)
5. [Common Patterns](#common-patterns)

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

## Entity Relationships

### Relationship Diagram (Text)

```
User
├─→ Shift.started_by (who started shift)
├─→ Shift.ended_by (who ended shift)
├─→ ShiftUser.user_id (who worked on shift)
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
```

---

## Common Patterns

### Audit Trail Levels

1. **No Audit** (User only)
   - Just basic fields

2. **Soft Delete Only** (ProductTemplate)
   - Fields: `deleted_at`, `deleted_by`
   - Records marked as deleted but not removed

3. **Full Audit Trail** (Product, ProductSlot, ShiftTemplate, Shift, ShiftUser, ProductSlotReading)
   - Fields: `deleted_at`, `deleted_by`, `created_at`, `created_by`, `updated_at`, `updated_by`
   - Complete tracking of all changes

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
- `delete{Entity}` - Hard delete (despite soft delete fields existing in models)

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

## Notes for AI Agents

When creating new entities, follow these guidelines:

1. **Determine audit level needed:**
   - Simple reference data → No audit
   - Configuration/setup data → Soft delete only
   - Transactional/operational data → Full audit trail

2. **Use standard field names and types:**
   - Follow the naming conventions above
   - Use Numeric(15,6) for measurements/prices
   - Use proper timestamp types with timezone

3. **Define relationships clearly:**
   - Use ForeignKey constraints
   - Define SQLAlchemy relationships with backref
   - Use appropriate cascade rules

4. **Create corresponding GraphQL schema:**
   - Create Strawberry @strawberry.type for each model
   - Add queries (list and single)
   - Add mutations (CRUD or workflow-specific)

5. **Generate Alembic migration:**
   - Import all new models in `alembic/env.py`
   - Run `alembic revision --autogenerate`
   - Review and test migration

6. **Update this document:**
   - Add new entity documentation
   - Update relationship diagram
   - Document business rules
