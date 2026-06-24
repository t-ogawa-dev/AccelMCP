"""add admin_credentials and is_system to connection_accounts

Revision ID: b1421db192fd
Revises: a1b2c3d4e5f6
Create Date: 2026-04-26 15:59:53.488200

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1421db192fd'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Use IF NOT EXISTS to handle partial migration state gracefully (PostgreSQL compatible)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'admin_credentials' not in inspector.get_table_names():
        op.create_table(
            'admin_credentials',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('username', sa.String(length=100), nullable=False),
            sa.Column('password_hash', sa.String(length=255), nullable=False),
            sa.Column('is_initialized', sa.Boolean(), nullable=False, server_default=sa.text('false')),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )

    # Add is_system column only if it doesn't exist yet
    existing_cols = [col['name'] for col in inspector.get_columns('connection_accounts')]
    if 'is_system' not in existing_cols:
        op.add_column(
            'connection_accounts',
            sa.Column('is_system', sa.Boolean(), nullable=False, server_default=sa.text('false'))
        )


def downgrade():
    op.drop_column('connection_accounts', 'is_system')
    op.drop_table('admin_credentials')
