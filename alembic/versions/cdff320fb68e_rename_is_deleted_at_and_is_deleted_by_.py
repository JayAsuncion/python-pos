"""rename_is_deleted_at_and_is_deleted_by_columns

Revision ID: cdff320fb68e
Revises: 2cf4a958cc91
Create Date: 2026-02-08 00:13:05.318160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cdff320fb68e'
down_revision: Union[str, Sequence[str], None] = '2cf4a958cc91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename columns in product_template table
    op.alter_column('product_template', 'is_deleted_at', new_column_name='deleted_at')
    op.alter_column('product_template', 'is_deleted_by', new_column_name='deleted_by')
    
    # Rename columns in product table
    op.alter_column('product', 'is_deleted_at', new_column_name='deleted_at')
    op.alter_column('product', 'is_deleted_by', new_column_name='deleted_by')


def downgrade() -> None:
    """Downgrade schema."""
    # Revert column names in product table
    op.alter_column('product', 'deleted_at', new_column_name='is_deleted_at')
    op.alter_column('product', 'deleted_by', new_column_name='is_deleted_by')
    
    # Revert column names in product_template table
    op.alter_column('product_template', 'deleted_at', new_column_name='is_deleted_at')
    op.alter_column('product_template', 'deleted_by', new_column_name='is_deleted_by')
