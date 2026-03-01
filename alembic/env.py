from logging.config import fileConfig
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.database import Base
from app.models.product_template import ProductTemplate
from app.models.user import User
from app.models.shift_template import ShiftTemplate
from app.models.shift import Shift
from app.models.shift_user import ShiftUser
from app.models.product import Product
from app.models.product_slot import ProductSlot
from app.models.product_slot_reading import ProductSlotReading
from app.models.permission import Permission
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission

config = context.config

fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()