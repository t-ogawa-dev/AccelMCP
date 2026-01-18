"""add timeout_seconds to capabilities

Revision ID: 20260118_timeout
Revises: d1e2f3a4b5c6
Create Date: 2026-01-18

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260118_timeout'
down_revision = 'd1e2f3a4b5c6'
branch_labels = None
depends_on = None


def upgrade():
    # Add timeout_seconds column to capabilities table
    with op.batch_alter_table('capabilities', schema=None) as batch_op:
        batch_op.add_column(sa.Column('timeout_seconds', sa.Integer(), nullable=True, server_default='30'))


def downgrade():
    # Remove timeout_seconds column
    with op.batch_alter_table('capabilities', schema=None) as batch_op:
        batch_op.drop_column('timeout_seconds')
