"""add routing_type to mcp_services

Revision ID: af9ae70b6d04
Revises: 3b81aca73e8a
Create Date: 2025-12-02 10:55:06.258337

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'af9ae70b6d04'
down_revision = '3b81aca73e8a'
branch_labels = None
depends_on = None


def upgrade():
    # Add routing_type column with default value
    with op.batch_alter_table('mcp_services', schema=None) as batch_op:
        batch_op.add_column(sa.Column('routing_type', sa.String(length=20), nullable=False, server_default='subdomain'))


def downgrade():
    # Remove routing_type column
    with op.batch_alter_table('mcp_services', schema=None) as batch_op:
        batch_op.drop_column('routing_type')
