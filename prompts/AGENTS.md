# Agents

**CRITICAL INSTRUCTIONS FOR ALL AI AGENTS WORKING ON THIS PROJECT**

This document contains mandatory guidelines that MUST be followed when working on this codebase.

---

## Entity Creation Checklist

**⚠️ MANDATORY:** Whenever you create, modify, or delete an entity in this project, you MUST update the entity documentation.

### Steps for Entity Changes

1. **Before Creating/Modifying an Entity:**
   - Read [`prompts/entity-context.md`](entity-context.md) to understand existing entities and relationships
   - Verify your new entity doesn't duplicate existing functionality
   - Identify which entities it will relate to

2. **During Entity Creation/Modification:**
   - Follow the patterns documented in [`prompts/scaffoldGraphqlEntity.prompt.md`](scaffoldGraphqlEntity.prompt.md)
   - Follow naming conventions from `entity-context.md`
   - Choose appropriate audit trail level

3. **After Creating/Modifying an Entity:**
   - **ALWAYS UPDATE** [`prompts/entity-context.md`](entity-context.md) with:
     - New entity documentation (purpose, fields, relationships, business rules)
     - Updated relationship diagram (if relationships changed)
     - Any new business workflows
     - Update the "Last Updated" date at the top of the file
   - Update alembic imports in `alembic/env.py`
   - Generate and apply database migration
   - Update GraphQL schema, queries, and mutations

4. **When Deleting an Entity:**
   - Remove entity documentation from [`prompts/entity-context.md`](entity-context.md)
   - Update relationship diagram
   - Remove related business workflows
   - Create migration to drop tables
   - Remove GraphQL types, queries, and mutations

---

## Why This Matters

The [`entity-context.md`](entity-context.md) file serves as the **single source of truth** for:
- Understanding the data model without reading code
- Onboarding new developers or AI agents
- Planning new features
- Avoiding conflicts and duplicates
- Maintaining consistency

**If you don't update it, future agents will:**
- Work with outdated information
- Create duplicate entities
- Break existing relationships
- Introduce inconsistencies

---

## Quick Reference

| Action | Required Updates |
|--------|-----------------|
| Create new entity | Add full documentation to `entity-context.md` |
| Modify entity fields | Update field list in `entity-context.md` |
| Add/remove relationships | Update relationship section and diagram |
| Change business rules | Update business rules section |
| Add workflow mutations | Document workflow in business workflow section |
| Delete entity | Remove all references from `entity-context.md` |

---

## Template for Entity Documentation

When adding a new entity to `entity-context.md`, use this template:

```markdown
### EntityName
**Purpose:** Brief description of what this entity represents

**Table:** `table_name`

**Key Fields:**
- `id` (PK) - Integer
- `field_name` - Type, constraints
- ...

**Audit Pattern:** [None | Soft delete only | Full audit trail]

**Relationships:**
- Relationship description

**Business Rules:**
- Rule 1
- Rule 2
```

---

## Enforcement

This is not optional. Entity changes without documentation updates are considered **incomplete work**.

If you are an AI agent and you've just created/modified an entity but haven't updated `entity-context.md`, **STOP** and update it now before considering your task complete.
