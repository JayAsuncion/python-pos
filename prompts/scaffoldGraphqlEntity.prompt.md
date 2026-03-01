---
name: scaffoldGraphqlEntity
description: Create complete entity with model, schema, GraphQL endpoints, migration, and Postman collection
argument-hint: entity name and fields (e.g., "shift with shift_name, start_time, end_time")
---

Create a new entity for the specified name with all necessary components following the project's established patterns.

**First, gather requirements if not provided:**
- Entity name
- Field names and their data types
- Which fields are required vs optional
- Any relationships to other entities
- Any special constraints or validation rules

If any of these details are missing, ask the user before proceeding.

Requirements:
1. Create the SQLAlchemy model in `app/models/` with:
   - All specified fields with appropriate data types
   - Standard audit fields: `is_active`, `deleted_at`, `deleted_by`, `created_at`, `created_by`, `updated_at`, `updated_by`
   - Use `PG_TIMESTAMP(timezone=True)` for timestamp fields
   - Use `Time(timezone=True)` for time-only fields to store UTC values
   - Use proper imports from sqlalchemy and app.database

2. Create the Strawberry GraphQL schema in `app/schemas/` with:
   - All model fields properly typed
   - Use Optional for nullable fields
   - Import appropriate types from strawberry, typing, and datetime

3. Update import files:
   - Add model import to `app/models/__init__.py`
   - Add model import to `alembic/env.py` for migration discovery

4. Generate and apply database migration:
   - Activate virtual environment: `source python-pos-env-39/Scripts/activate`
   - Set PYTHONPATH: Either `export $(grep -v '^#' .env | xargs)` or use `PYTHONPATH=.` prefix
   - Run alembic autogenerate: `alembic revision --autogenerate -m "create_{entity}_table"`
   - Apply migration: `alembic upgrade head`
   - Refer to alembic.md for proper environment setup and avoid module import errors

5. Create GraphQL queries in `app/graphql/queries.py`:
   - `{entities}` - Get list of all records
   - `{entity}` - Get single record by ID
   - Add necessary imports for model and schema

6. Create GraphQL mutations in `app/graphql/mutations.py`:
   - `create{Entity}` - Create new record
   - `update{Entity}` - Update existing record
   - `delete{Entity}` - Delete record (hard delete)
   - Add necessary imports for model and schema
   - Handle optional parameters properly
   - Always update `updated_by` when provided in update mutation

7. Create Postman collection in `testing/postman/`:
   - Follow existing collection format
   - Include all 5 requests: Get All, Get By ID, Create, Update, Delete
   - Use GraphQL queries/mutations with proper variables
   - Include sample data in variables section
   - Use `{{baseURL}}/graphql` endpoint

8. Restart the service to apply changes (docker-compose restart web)

Ensure all components follow the existing code patterns in the project, including naming conventions, field types, and GraphQL query/mutation structures.
