"""update mcp template schema

Revision ID: 20251204014934
Revises: 
Create Date: 2025-12-04 01:49:34

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251204014934'
down_revision = '7452fa496f59'  # Latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Add official_url and mcp_url to mcp_service_templates
    with op.batch_alter_table('mcp_service_templates', schema=None) as batch_op:
        batch_op.add_column(sa.Column('official_url', sa.String(500), nullable=True))
        batch_op.add_column(sa.Column('mcp_url', sa.String(500), nullable=True))
    
    # Drop mcp_capability_templates table as it's no longer needed
    op.drop_table('mcp_capability_templates')


def downgrade():
    # Recreate mcp_capability_templates table
    op.create_table('mcp_capability_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('service_template_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('capability_type', sa.String(50), nullable=False),
        sa.Column('url', sa.String(500), nullable=True),
        sa.Column('headers', sa.Text(), nullable=True),
        sa.Column('body_params', sa.Text(), nullable=True),
        sa.Column('template_content', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['service_template_id'], ['mcp_service_templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Remove columns
    with op.batch_alter_table('mcp_service_templates', schema=None) as batch_op:
        batch_op.drop_column('mcp_url')
        batch_op.drop_column('official_url')
