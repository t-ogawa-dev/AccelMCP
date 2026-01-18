"""merge heads

Revision ID: 20260118_merge
Revises: 12ebcecda7af, 20260118_timeout
Create Date: 2026-01-18

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260118_merge'
down_revision = ('12ebcecda7af', '20260118_timeout')
branch_labels = None
depends_on = None


def upgrade():
    # This is a merge migration, no changes needed
    pass


def downgrade():
    # This is a merge migration, no changes needed
    pass
