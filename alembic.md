# Alembic

Here’s the list of commands to generate the Alembic migration for your product_template table, using your existing setup:

Activate your virtual environment:
```
source python-pos-env-39/Scripts/activate
```

Load your .env variables (including PYTHONPATH=.):
```
export $(grep -v '^#' .env | xargs)
```

Run Alembic from your project root:
Generate migration
```
alembic revision --autogenerate -m "create product_template table"
```

This sequence ensures your environment and PYTHONPATH are set correctly for Alembic to find your app module and generate the migration.

## Common commands
Generate a migration:
```
alembic revision --autogenerate -m "your migration message"
```

Run/Apply migrations:
```
alembic upgrade head
```

Other useful commands:
```
# Show current migration version
alembic current

# Show migration history
alembic history

# Downgrade one version
alembic downgrade -1

# Downgrade to a specific revision
alembic downgrade <revision_id>

# Upgrade to a specific revision
alembic upgrade <revision_id>

# Show pending migrations
alembic history --verbose
```