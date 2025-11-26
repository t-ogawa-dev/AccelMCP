"""remove_subdomain_from_apps

Revision ID: c8c9d39f9c78
Revises: 8d4f3e2a1b5c
Create Date: 2025-11-25 18:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8c9d39f9c78'
down_revision = '8d4f3e2a1b5c'
branch_labels = None
depends_on = None


def upgrade():
    # Remove subdomain column from apps table
    op.drop_index('subdomain', table_name='apps')
    op.drop_column('apps', 'subdomain')


def downgrade():
    # Re-add subdomain column
    op.add_column('apps', sa.Column('subdomain', sa.String(50), nullable=True))
    op.create_index('subdomain', 'apps', ['subdomain'], unique=True)
