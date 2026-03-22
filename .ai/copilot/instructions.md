# GitHub Copilot Instructions for Python POS

## Project Context

Python POS system using FastAPI + GraphQL (Strawberry) + SQLAlchemy + PostgreSQL with JWT auth and RBAC permissions.

---

## Critical Patterns

### Every GraphQL resolver needs RBAC:
```python
from app.auth.permissions import require_permission

@strawberry.mutation
def create_entity(self, info: strawberry.types.Info, ...) -> EntityType:
    user = require_permission(info, "CREATE_ENTITY")
    # Use user.id for audit fields
```

### Always filter soft-deleted records:
```python
db.query(EntityModel).filter(EntityModel.deleted_at.is_(None)).all()
```

### Always close database sessions:
```python
db = SessionLocal()
# ... work ...
db.close()
```

---

## Naming Conventions

- Python/DB: snake_case
- GraphQL: camelCase  
- Types: PascalCase + "Type"
- Permissions: SCREAMING_SNAKE_CASE (e.g., CREATE_USER)

---

## File Organization

- Models: `app/models/{entity}.py`
- Schemas: `app/schemas/{entity}.py`
- Mutations: `app/graphql/mutations/{entity}.py`
- Queries: `app/graphql/queries/{entity}.py`

---

## Reference Files

- Entity reference: `prompts/01-entity-reference.md`
- Creation guide: `prompts/02-entity-creation-guide.md`
- Auth patterns: `prompts/03-auth-and-permissions.md`
- Templates: `prompts/templates/entity-template.md`

---

## Key Reminders

1. RBAC on every resolver (except `login`)
2. Update documentation after entity changes
3. Use audit fields from authenticated user
4. Filter soft-deleted records
5. Close database sessions
