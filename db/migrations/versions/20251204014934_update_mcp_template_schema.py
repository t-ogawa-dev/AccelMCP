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

    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'mcp_capability_templates' not in inspector.get_table_names():
        # Table doesn't exist yet on this path -- create it with the target schema.
        op.create_table('mcp_capability_templates',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('template_id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('capability_type', sa.String(20), nullable=False),
            sa.Column('endpoint_path', sa.String(500), nullable=True),
            sa.Column('method', sa.String(10), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('headers', sa.Text(), nullable=True),
            sa.Column('body_params', sa.Text(), nullable=True),
            sa.Column('query_params', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['template_id'], ['mcp_service_templates.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    else:
        # The table already exists from the initial migration with an older
        # schema (service_template_id/url/template_content columns). Migrate
        # it to the current target schema instead of creating a duplicate
        # table (which fails with "relation already exists").
        existing_cols = {c['name'] for c in inspector.get_columns('mcp_capability_templates')}

        with op.batch_alter_table('mcp_capability_templates', schema=None) as batch_op:
            if 'service_template_id' in existing_cols and 'template_id' not in existing_cols:
                batch_op.alter_column('service_template_id', new_column_name='template_id')
            if 'endpoint_path' not in existing_cols:
                batch_op.add_column(sa.Column('endpoint_path', sa.String(500), nullable=True))
            if 'method' not in existing_cols:
                batch_op.add_column(sa.Column('method', sa.String(10), nullable=True))
            if 'query_params' not in existing_cols:
                batch_op.add_column(sa.Column('query_params', sa.Text(), nullable=True))
            if 'url' in existing_cols:
                batch_op.drop_column('url')
            if 'template_content' in existing_cols:
                batch_op.drop_column('template_content')


def downgrade():
    # Drop mcp_capability_templates table
    op.drop_table('mcp_capability_templates')
    
    # Remove columns
    with op.batch_alter_table('mcp_service_templates', schema=None) as batch_op:
        batch_op.drop_column('mcp_url')
        batch_op.drop_column('official_url')
