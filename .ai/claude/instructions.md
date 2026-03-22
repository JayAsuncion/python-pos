# Claude Instructions for Python POS

## Project Overview

**What:** Python POS (Point of Sale) system  
**Stack:** FastAPI, Strawberry GraphQL, SQLAlchemy, PostgreSQL, Alembic  
**Auth:** JWT token-based authentication with RBAC permission system  
**Architecture:** Entity-based organization (not feature-based)

---

## Critical Guidelines

### 1. RBAC is Mandatory on ALL Resolvers

**Every GraphQL query and mutation must:**
```python
from app.auth.permissions import require_permission

@strawberry.mutation
def create_entity(self, info: strawberry.types.Info, ...) -> EntityType:
    user = require_permission(info, "CREATE_ENTITY")
    # Use user.id for created_by, updated_by, deleted_by
```

**Exception:** Only the `login` mutation is public.

---

### 2. Documentation Updates are Mandatory

**After creating/modifying ANY entity:**
1. Open `prompts/01-entity-reference.md`
2. Add/update entity documentation (purpose, fields, relationships, business rules)
3. Update relationship diagram if needed
4. Update "Last Updated" date at top

**This is NOT optional.** Future AI agents depend on this documentation.

---

### 3. Multi-Edit Efficiency is Expected

**When making multiple independent edits:**
- ✅ Use `multi_replace_string_in_file` to batch them
- ❌ Don't make sequential `replace_string_in_file` calls

**Why:** Significantly improves user's cost and time efficiency.

---

### 4. Virtual Environment Context

**Before running Python commands, remind user:**
```bash
source python-pos-env-39/Scripts/activate
export $(grep -v '^#' .env | xargs)
```

If user gets import errors or database connection issues, this is likely the problem.

---

## File Organization

**Entity-based structure** (one entity per file):

```
app/
├── models/{entity}.py          # SQLAlchemy models
├── schemas/{entity}.py         # Strawberry GraphQL types
└── graphql/
    ├── mutations/{entity}.py   # Entity mutations
    └── queries/{entity}.py     # Entity queries
```

**Aggregation:**
- `app/graphql/mutations/__init__.py` - Combines all mutations
- `app/graphql/queries/__init__.py` - Combines all queries

---

## Quick Reference

### Naming Conventions
- **Python/DB:** snake_case
- **GraphQL:** camelCase
- **Types:** PascalCase + "Type"
- **Permissions:** SCREAMING_SNAKE_CASE

### Permission Pattern
Format: `{ACTION}_{ENTITY}`

Actions: CREATE, VIEW, UPDATE, DELETE, START, END, ASSIGN, GRANT, REVOKE

Examples: `CREATE_USER`, `VIEW_PRODUCT`, `START_SHIFT`

### Audit Trail Levels
1. **No audit** - User (simplest)
2. **Soft delete only** - ProductTemplate, Permission, Role
3. **Full audit trail** - Product, Shift, most operational entities

### Data Types
- String → `Column(String)`
- Integer → `Column(Integer)`
- Decimal/Money → `Column(Numeric(15, 6))` → `float` in GraphQL
- Boolean → `Column(Boolean)`
- Timestamps → `Column(PG_TIMESTAMP(timezone=True))`

---

## Common Pitfalls

### ❌ Forgetting to close database sessions
```python
db = SessionLocal()
# ... do work ...
# MISSING: db.close()
```

**Always:** Use try/finally or ensure `db.close()` before return

---

### ❌ Not filtering soft-deleted records
```python
entities = db.query(EntityModel).all()  # Returns deleted!
```

**Always:** `.filter(EntityModel.deleted_at.is_(None))`

---

### ❌ Missing permission checks
```python
@strawberry.mutation
def create_entity(self, name: str):  # No info param!
```

**Must have:** `info: strawberry.types.Info` + `require_permission()`

---

### ❌ Not updating documentation
Created entity successfully but didn't update `prompts/01-entity-reference.md`

**Must do:** Update documentation EVERY TIME

---

### ❌ Hardcoding audit fields
```python
entity.created_by = 1  # Hardcoded!
```

**Should be:** `entity.created_by = user.id` from `require_permission()`

---

### ❌ Sequential edits
Making 5 separate `replace_string_in_file` calls

**Should be:** One `multi_replace_string_in_file` call

---

## Workflow for Entity Creation

1. **Read** `prompts/01-entity-reference.md` - Understand existing entities
2. **Follow** `prompts/02-entity-creation-guide.md` - Step-by-step process
3. **Copy** `prompts/templates/entity-template.md` - Boilerplate code
4. **Implement** RBAC in all resolvers
5. **Add** permissions to `app/auth/seed_permissions.py`
6. **Run** `python -m app.auth.seed_permissions`
7. **Generate** migration: `alembic revision --autogenerate`
8. **Apply** migration: `alembic upgrade head`
9. **UPDATE** `prompts/01-entity-reference.md` (MANDATORY!)

---

## Essential Documentation Files

**For AI agents:**
- `prompts/00-README.md` - Start here, reading order
- `prompts/01-entity-reference.md` - All entities (what exists)
- `prompts/02-entity-creation-guide.md` - How to create entities
- `prompts/03-auth-and-permissions.md` - Auth system reference
- `prompts/templates/entity-template.md` - Boilerplate code

**For developers:**
- `DEV_WORKFLOW.md` - Development workflows
- `docs/ARCHITECTURE.md` - System architecture (if exists)
- `TODO.md` - Current todos

---

## Permission Map Quick Reference

**Total:** 40+ permissions across 9 categories

**Categories:**
- USER (4) - User management
- PRODUCT (4) - Product CRUD
- PRODUCT_TEMPLATE (4) - Template CRUD
- PRODUCT_SLOT (4) - Slot CRUD
- PRODUCT_SLOT_READING (1) - Delete only
- SHIFT (4) - Shift operations (including START_SHIFT, END_SHIFT)
- SHIFT_TEMPLATE (4) - Template CRUD
- SHIFT_USER (1) - Delete only
- RBAC (14) - Permission, Role, UserRole, RolePermission management

**Default Roles:**
- SUPER_ADMIN (40 permissions) - Full access
- MANAGER (23 permissions) - Operational management
- CASHIER (7 permissions) - Shift operations only
- VIEWER (5 permissions) - Read-only

---

## Testing Pattern

**In GraphQL Playground:**
1. Login to get token
2. Add to HTTP Headers: `{"Authorization": "Bearer <token>"}`
3. Test queries/mutations
4. Verify permission checks work

**Test permission denial:**
Remove token or use user without permission - should get "Permission denied" error

---

## Code Patterns

### Database Session Management
```python
db = SessionLocal()
try:
    # Do work
    db.commit()
    db.refresh(entity)
    result = convert_to_type(entity)
finally:
    db.close()
return result
```

### Error Handling
```python
db = SessionLocal()
if not valid:
    db.close()
    raise ValueError("Descriptive error message")
# ... continue ...
db.close()
```

### Audit Fields
```python
# Create
entity.created_by = user.id

# Update
entity.updated_by = user.id

# Delete (soft)
entity.deleted_at = func.now()
entity.deleted_by = user.id
```

---

## When to Consult Which File

| Task | File |
|------|------|
| Creating new entity | `prompts/02-entity-creation-guide.md` |
| Understanding data model | `prompts/01-entity-reference.md` |
| Working with auth | `prompts/03-auth-and-permissions.md` |
| Need boilerplate code | `prompts/templates/entity-template.md` |
| Project workflows | `DEV_WORKFLOW.md` |
| Architecture questions | `docs/ARCHITECTURE.md` |
| Current tasks | `TODO.md` |

---

## Response Style Preferences

**For this project:**
- Be concise but complete
- Provide working code, not just descriptions
- Use `multi_replace_string_in_file` for batched edits
- Reference documentation files when appropriate
- Remind about venv/env vars when running commands
- Update todo list for multi-step work

**Don't:**
- Ask for permission to proceed (just do it)
- Over-explain what you're doing
- Create summary markdown files unless requested
- Skip mandatory documentation updates
- Make sequential edits when you can batch

---

## Security Reminders

1. **Never skip RBAC** - Every resolver needs permission check
2. **Never return passwords** - Exclude from GraphQL types
3. **Always use audit fields** - Track who created/updated/deleted
4. **Always filter soft-deleted** - Don't return deleted records
5. **Always close sessions** - Prevent connection leaks

---

## Success Checklist for Entity Creation

After creating an entity, verify:
- [x] Model created with correct audit pattern
- [x] Schema created with matching fields
- [x] Mutations have permission checks and use `user.id`
- [x] Queries have permission checks and filter deleted
- [x] Aggregator files updated
- [x] Model imports updated
- [x] Permissions added and seeded
- [x] Migration generated and applied
- [x] **Documentation updated in `prompts/01-entity-reference.md`**
- [x] Service restarted without errors
- [x] Tested in GraphQL playground

---

**Remember:** This project emphasizes security (RBAC on everything) and documentation (keep entity reference up-to-date). These are NOT optional!
