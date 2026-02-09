"""Add resource_uri and resource_mime_type to capabilities

Revision ID: 859d90ed773e
Revises: 20260118_merge
Create Date: 2026-01-20 23:48:27.308956

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '859d90ed773e'
down_revision = '20260118_merge'
branch_labels = None
depends_on = None


def upgrade():
    # Add resource_uri and resource_mime_type columns to capabilities table
    with op.batch_alter_table('capabilities', schema=None) as batch_op:
        batch_op.add_column(sa.Column('resource_uri', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('resource_mime_type', sa.String(length=100), nullable=True))


def downgrade():
    with op.batch_alter_table('capabilities', schema=None) as batch_op:
        batch_op.drop_column('resource_mime_type')
        batch_op.drop_column('resource_uri')
