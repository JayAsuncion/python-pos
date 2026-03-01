## How to create a new table, schema, queries, mutation, and graphQL endpoint for an entity?
1. Create the model in [app/models](./app/models).
1. Import the model in [alembic/env.py](./alembic/env.py) to allow alembic discovery.
1. Import the model in [app/models/__init__.py](./app/models/__init__.py) to allow `package import` like `from app.models import User`, instead of `direct import` like `from app.models.user import User` similar to `index.ts` of Typescript. **(Optional)**
1. Generate migration script and apply it. Refer to [alembic.md](./alembic.md).
1. Create entity-specific GraphQL files:
   - Create `mutations` in [app/graphql/mutations/{entity}.py](./app/graphql/mutations/) with a `{Entity}Mutations` class
   - Create `queries` in [app/graphql/queries/{entity}.py](./app/graphql/queries/) with a `{Entity}Queries` class
   - Update [app/graphql/mutations/__init__.py](./app/graphql/mutations/__init__.py) to import and include your mutations class
   - Update [app/graphql/queries/__init__.py](./app/graphql/queries/__init__.py) to import and include your queries class
1. Apply changes using `docker-compose restart web`.

