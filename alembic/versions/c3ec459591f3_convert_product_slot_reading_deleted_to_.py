"""convert_product_slot_reading_deleted_to_voided

Revision ID: c3ec459591f3
Revises: df79abd7a65d
Create Date: 2026-03-22 20:43:11.666044

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3ec459591f3'
down_revision: Union[str, Sequence[str], None] = 'df79abd7a65d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename columns in product_slot_reading table
    op.alter_column('product_slot_reading', 'deleted_at', new_column_name='voided_at')
    op.alter_column('product_slot_reading', 'deleted_by', new_column_name='voided_by')
    
    # Add void_reason column
    op.add_column('product_slot_reading', sa.Column('void_reason', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove void_reason column
    op.drop_column('product_slot_reading', 'void_reason')
    
    # Revert column names in product_slot_reading table
    op.alter_column('product_slot_reading', 'voided_at', new_column_name='deleted_at')
    op.alter_column('product_slot_reading', 'voided_by', new_column_name='deleted_by')
