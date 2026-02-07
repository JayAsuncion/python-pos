## Create new table
1. Create the model in [app/models](./app/models).
1. Import the model in [alembic/env.py](./alembic/env.py) to allow alembic discovery.
1. Import the model in [app/models/__init__.py](./app/models/__init__.py) to allow `package import` like `from app.models import User`, instead of `direct import` like `from app.models.user import User` similar to `index.ts` of Typescript. **(Optional)**
1. Generate migration script and apply it. Refer to [alembic.md](./alembic.md).
1. Create the API `mutations` in [app/graphql/mutations.py](./app/graphql/mutations.py) and `queries` in [app/graphql/queries.py](./app/graphql/queries.py)
1. Apply changes using `docker-compose restart web`.

