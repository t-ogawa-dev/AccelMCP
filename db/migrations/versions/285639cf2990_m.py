""" Add server_settings and resources tables

Revision ID: 285639cf2990
Revises: 859d90ed773e
Create Date: 2026-01-21 00:49:24.673191

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '285639cf2990'
down_revision = '859d90ed773e'
branch_labels = None
depends_on = None


def upgrade():
    # Create server_settings table
    op.create_table('server_settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=50), nullable=False),
    sa.Column('value', sa.String(length=500), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_server_settings_key', 'server_settings', ['key'], unique=True)

    # Create resources table
    op.create_table('resources',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('resource_id', sa.String(length=8), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('mime_type', sa.String(length=100), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('access_control', sa.String(length=20), nullable=False),
    sa.Column('is_enabled', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_resources_resource_id', 'resources', ['resource_id'], unique=True)

    # Create resource_account_access table
    op.create_table('resource_account_access',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('resource_id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['connection_accounts.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['resource_id'], ['resources.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('resource_id', 'account_id', name='uq_resource_account')
    )


def downgrade():
    op.drop_table('resource_account_access')
    op.drop_index('ix_server_settings_key', table_name='server_settings')
    op.drop_table('server_settings')
    op.drop_index('ix_resources_resource_id', table_name='resources')
    op.drop_table('resources')
