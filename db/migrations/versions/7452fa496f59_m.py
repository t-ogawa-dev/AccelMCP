"""rename subdomain to identifier

Revision ID: 7452fa496f59
Revises: af9ae70b6d04
Create Date: 2025-12-02 11:11:51.359458

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7452fa496f59'
down_revision = 'af9ae70b6d04'
branch_labels = None
depends_on = None


def upgrade():
    # Rename subdomain column to identifier
    with op.batch_alter_table('mcp_services', schema=None) as batch_op:
        batch_op.alter_column('subdomain',
                              new_column_name='identifier',
                              existing_type=sa.String(length=50),
                              nullable=False)


def downgrade():
    # Rename identifier column back to subdomain
    with op.batch_alter_table('mcp_services', schema=None) as batch_op:
        batch_op.alter_column('identifier',
                              new_column_name='subdomain',
                              existing_type=sa.String(length=50),
                              nullable=False)
