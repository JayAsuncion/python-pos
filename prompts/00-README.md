# Prompts Directory - Start Here

**Last Updated:** March 22, 2026

This directory contains essential documentation for AI agents and developers working on the Python POS system.

---

## 📖 Reading Order

### For New AI Agents or Developers:

1. **Start Here** → `00-README.md` (this file)
2. **Understand What Exists** → [01-entity-reference.md](01-entity-reference.md)
3. **Learn How to Create** → [02-entity-creation-guide.md](02-entity-creation-guide.md)
4. **Reference Auth System** → [03-auth-and-permissions.md](03-auth-and-permissions.md)

### For Specific Tasks:

| Task | Read This |
|------|-----------|
| Creating a new entity | [02-entity-creation-guide.md](02-entity-creation-guide.md) |
| Understanding data model | [01-entity-reference.md](01-entity-reference.md) |
| Working with authentication | [03-auth-and-permissions.md](03-auth-and-permissions.md) |
| Need code templates | [templates/entity-template.md](templates/entity-template.md) |
| Understanding relationships | [01-entity-reference.md](01-entity-reference.md) (Entity Relationships section) |
| Adding new permissions | [03-auth-and-permissions.md](03-auth-and-permissions.md) (Adding Permissions section) |

---

## 📁 File Descriptions

### [01-entity-reference.md](01-entity-reference.md)
**Type:** Reference Documentation  
**Purpose:** Single source of truth for all entities in the system

**Contains:**
- Complete list of all entities (master data, operational, junction)
- Field definitions and data types
- Relationships and foreign keys
- Business rules and constraints
- Common patterns (audit trails, naming conventions)
- Relationship diagrams

**When to read:** Before creating new entities, when understanding the data model

**Must be updated:** After every entity creation/modification/deletion

---

### [02-entity-creation-guide.md](02-entity-creation-guide.md)
**Type:** Procedural Guide  
**Purpose:** Step-by-step instructions for creating and modifying entities

**Contains:**
- Prerequisites checklist
- Step-by-step creation process
- Code patterns and examples
- RBAC implementation requirements
- Migration generation steps
- Documentation update requirements (mandatory)
- Verification checklist

**When to read:** When creating or modifying any entity

**Critical rule:** ALWAYS update `01-entity-reference.md` after following this guide

---

### [03-auth-and-permissions.md](03-auth-and-permissions.md)
**Type:** Reference Documentation  
**Purpose:** Authentication and authorization system reference

**Contains:**
- JWT authentication flow
- Permission-based authorization model
- Role structure and default roles
- How to add new permissions
- Security best practices
- GraphQL context usage
- Password management

**When to read:** When working with authentication, permissions, roles, or securing endpoints

---

### [templates/entity-template.md](templates/entity-template.md)
**Type:** Code Templates  
**Purpose:** Copy/paste boilerplate code

**Contains:**
- SQLAlchemy model template
- Strawberry GraphQL schema template
- Mutations file template
- Queries file template
- Complete working examples

**When to use:** When implementing a new entity (copy/paste, then customize)

---

## 🎯 Quick Reference

### Naming Conventions
- **Python/Database:** snake_case (`product_id`, `shift_name`)
- **GraphQL:** camelCase (`productId`, `shiftName`)
- **Types:** PascalCase + "Type" suffix (`ProductType`, `ShiftType`)
- **Tables:** snake_case, singular/plural as appropriate (`users`, `product_slot`)
- **Permissions:** SCREAMING_SNAKE_CASE (`CREATE_USER`, `VIEW_PRODUCT`)

### Audit Trail Levels
1. **No Audit** - User only (basic fields, no tracking)
2. **Soft Delete Only** - Permission, Role, ProductTemplate (deleted_at, deleted_by)
3. **Full Audit Trail** - Product, Shift, most operational entities (created_at, created_by, updated_at, updated_by, deleted_at, deleted_by)

### Permission Pattern
Every GraphQL resolver must implement:
```python
from app.auth.permissions import require_permission

@strawberry.mutation
def create_entity(self, info: strawberry.types.Info, ...) -> EntityType:
    user = require_permission(info, "CREATE_ENTITY")
    # ... implementation
```

### Permission Naming
Format: `{ACTION}_{ENTITY}` where ACTION is one of:
- `CREATE` - Creating new records
- `VIEW` - Querying/reading records
- `UPDATE` - Modifying existing records
- `DELETE` - Deleting/soft-deleting records
- Custom actions: `START_SHIFT`, `END_SHIFT`, `ASSIGN_ROLE`, etc.

---

## ⚠️ Critical Rules

### 1. Documentation is Mandatory
After creating, modifying, or deleting an entity:
- ✅ Update [01-entity-reference.md](01-entity-reference.md) with entity details
- ✅ Update relationship diagrams if relationships changed
- ✅ Document business rules and constraints
- ✅ Update the "Last Updated" date at the top
- ❌ DO NOT skip this step - future agents depend on accurate documentation

### 2. RBAC is Mandatory
Every GraphQL query and mutation must:
- ✅ Accept `info: strawberry.types.Info` parameter
- ✅ Call `require_permission(info, "PERMISSION_CODE")` at the start
- ✅ Use returned user for audit fields (created_by, updated_by, deleted_by)
- ❌ DO NOT create unprotected endpoints (except login)

### 3. Follow Established Patterns
- ✅ Use multi_replace_string_in_file for multiple independent edits
- ✅ Close database sessions with `db.close()`
- ✅ Filter `deleted_at.is_(None)` for soft-deleted entities
- ✅ Include full audit fields in operational entities
- ✅ Generate Alembic migrations for all schema changes

---

## 🔄 Entity Creation Workflow

```
START
  ↓
1. Read 01-entity-reference.md
   (Understand existing entities and avoid duplicates)
  ↓
2. Follow 02-entity-creation-guide.md
   (Step-by-step implementation)
  ↓
3. Copy templates from templates/entity-template.md
   (Boilerplate code)
  ↓
4. Implement RBAC (require_permission in all resolvers)
   ↓
5. Add permissions to seed_permissions.py
   ↓
6. Run: python -m app.auth.seed_permissions
   ↓
7. Generate migration: alembic revision --autogenerate
   ↓
8. Apply migration: alembic upgrade head
   ↓
9. UPDATE 01-entity-reference.md (MANDATORY)
   ↓
10. Update "Last Updated" date in 01-entity-reference.md
   ↓
END
```

---

## 📊 Project Statistics

**Total Entities:** 12
- Master Data: User, Permission, Role, ProductTemplate, ShiftTemplate
- Operational: Product, ProductSlot, Shift, ProductSlotReading
- Junction: UserRole, RolePermission, ShiftUser

**Total Permissions:** 40+ (see 03-auth-and-permissions.md)

**Default Roles:** 4 (SUPER_ADMIN, MANAGER, CASHIER, VIEWER)

---

## 🤝 For Human Developers

These files are designed primarily for AI agents but are valuable for human developers too:

- **Onboarding:** Read files 01-03 in order to understand the system
- **Reference:** Use 01 as a quick reference for entities and relationships
- **Creating entities:** Follow the guide in 02 for consistency
- **Auth questions:** Check 03 for authentication/authorization patterns

**Please keep these files updated** when you make changes - future AI agents and developers depend on accurate documentation!

---

## 📝 Change Log

| Date | File | Change |
|------|------|--------|
| 2026-03-22 | All files | Reorganized prompts folder with numbered sequential structure |
| 2026-03-02 | entity-context.md | Added RBAC entities (Permission, Role, UserRole, RolePermission) |
| 2026-03-01 | entity-context.md | Added JWT authentication documentation |

---

## 🆘 Need Help?

**Common Issues:**

Q: "Where do I document a new entity?"  
A: In [01-entity-reference.md](01-entity-reference.md) - this is mandatory after creating any entity

Q: "How do I create a new entity?"  
A: Follow [02-entity-creation-guide.md](02-entity-creation-guide.md) step by step

Q: "My resolver gets 'Permission denied' errors"  
A: Check [03-auth-and-permissions.md](03-auth-and-permissions.md) - ensure you've seeded permissions and assigned roles

Q: "Where are the code templates?"  
A: In [templates/entity-template.md](templates/entity-template.md) - copy and customize

Q: "What's the difference between these files and /docs?"  
A: `/prompts` = AI agent domain knowledge and patterns  
   `/docs` = Architecture, workflows, and API documentation

---

**Remember:** These files exist to ensure consistency, prevent duplicates, and maintain proper security. Following these guidelines is not optional!
