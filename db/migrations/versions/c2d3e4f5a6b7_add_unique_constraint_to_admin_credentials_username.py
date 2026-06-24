"""add unique constraint to admin_credentials.username (multi-admin support)

Revision ID: c2d3e4f5a6b7
Revises: b1421db192fd
Create Date: 2026-06-22 10:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'c2d3e4f5a6b7'
down_revision = 'b1421db192fd'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('admin_credentials', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_admin_credentials_username', ['username'])


def downgrade():
    with op.batch_alter_table('admin_credentials', schema=None) as batch_op:
        batch_op.drop_constraint('uq_admin_credentials_username', type_='unique')
