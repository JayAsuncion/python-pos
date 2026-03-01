# Prompts Directory

This directory contains documentation and guidelines for AI agents working on this codebase.

## Files

### 📋 [AGENTS.md](AGENTS.md)
**READ THIS FIRST!**

Critical instructions that MUST be followed by all AI agents. Contains mandatory checklist for entity creation/modification and enforcement policies.

**Key Rule:** Always update `entity-context.md` when creating, modifying, or deleting entities.

---

### 📚 [entity-context.md](entity-context.md)
**Single Source of Truth for Data Model**

Comprehensive documentation of all entities in the system including:
- Entity purposes, fields, and relationships
- Business rules and validation logic
- Audit trail patterns
- Naming conventions
- Business workflows
- Relationship diagrams

**Must be kept up-to-date** whenever entities change.

---

### 🔧 [scaffoldGraphqlEntity.prompt.md](scaffoldGraphqlEntity.prompt.md)
**Entity Creation Template**

Step-by-step guide for creating new entities with:
- SQLAlchemy model patterns
- Strawberry GraphQL schema patterns
- Migration generation steps
- Implementation checklist
- Code examples

**Always reference `AGENTS.md` and `entity-context.md` before using this template.**

---

## Workflow for Entity Creation

```
1. Read AGENTS.md
   ↓
2. Read entity-context.md to understand existing entities
   ↓
3. Use scaffoldGraphqlEntity.prompt.md as implementation guide
   ↓
4. Create/modify entity following patterns
   ↓
5. Update entity-context.md with new documentation (MANDATORY)
   ↓
6. Update "Last Updated" date in entity-context.md
```

---

## For Humans

If you're a human developer:
- These files are designed for AI agents but are useful for understanding the codebase
- The `entity-context.md` file is the best starting point to understand the data model
- Please keep these files updated when you make changes too!

---

## For AI Agents

These guidelines exist to ensure:
- Consistency across implementations
- Proper documentation of all changes
- Easy onboarding for future agents
- Prevention of duplicate or conflicting entities

**Follow these guidelines strictly.** Incomplete work (especially missing documentation updates) should be flagged and completed before considering a task done.
