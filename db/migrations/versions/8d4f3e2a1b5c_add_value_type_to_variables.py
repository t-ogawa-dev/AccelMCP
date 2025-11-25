"""add_value_type_to_variables

Revision ID: 8d4f3e2a1b5c
Revises: 754c321806ca
Create Date: 2025-11-25 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d4f3e2a1b5c'
down_revision = '754c321806ca'
branch_labels = None
depends_on = None


def upgrade():
    # Add value_type column with default 'string'
    op.add_column('variables', sa.Column('value_type', sa.String(20), nullable=False, server_default='string'))


def downgrade():
    op.drop_column('variables', 'value_type')
