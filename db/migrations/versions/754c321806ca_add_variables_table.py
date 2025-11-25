"""add_variables_table

Revision ID: 754c321806ca
Revises: a39dd60460a1
Create Date: 2025-11-25 05:40:05.079127

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '754c321806ca'
down_revision = 'a39dd60460a1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'variables',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_secret', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_variable_name')
    )


def downgrade():
    op.drop_table('variables')
