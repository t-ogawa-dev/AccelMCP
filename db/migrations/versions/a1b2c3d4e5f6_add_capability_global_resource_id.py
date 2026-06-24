"""Add global_resource_id to capabilities

Revision ID: a1b2c3d4e5f6
Revises: 285639cf2990
Create Date: 2026-01-21 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '285639cf2990'
branch_labels = None
depends_on = None


def upgrade():
    # Add global_resource_id column to capabilities table
    with op.batch_alter_table('capabilities', schema=None) as batch_op:
        batch_op.add_column(sa.Column('global_resource_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_capabilities_global_resource', 'resources', ['global_resource_id'], ['id'])


def downgrade():
    # Remove global_resource_id column from capabilities table
    with op.batch_alter_table('capabilities', schema=None) as batch_op:
        batch_op.drop_constraint('fk_capabilities_global_resource', type_='foreignkey')
        batch_op.drop_column('global_resource_id')
