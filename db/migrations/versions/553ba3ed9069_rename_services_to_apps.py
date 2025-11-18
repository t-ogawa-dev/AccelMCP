"""Rename services table to apps

Revision ID: 553ba3ed9069
Revises: 553ba3ed9068
Create Date: 2025-11-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '553ba3ed9069'
down_revision = '553ba3ed9068'
branch_labels = None
depends_on = None


def upgrade():
    # Rename services table to apps
    op.rename_table('services', 'apps')
    
    # Update foreign key and column name in capabilities table
    with op.batch_alter_table('capabilities', schema=None) as batch_op:
        batch_op.drop_constraint('capabilities_ibfk_1', type_='foreignkey')
        batch_op.alter_column('service_id', 
                            new_column_name='app_id',
                            existing_type=sa.Integer(),
                            nullable=False)
        batch_op.create_foreign_key('capabilities_ibfk_1', 'apps', ['app_id'], ['id'])


def downgrade():
    # Revert: Update foreign key and column name in capabilities table
    with op.batch_alter_table('capabilities', schema=None) as batch_op:
        batch_op.drop_constraint('capabilities_ibfk_1', type_='foreignkey')
        batch_op.alter_column('app_id',
                            new_column_name='service_id',
                            existing_type=sa.Integer(),
                            nullable=False)
        batch_op.create_foreign_key('capabilities_ibfk_1', 'services', ['service_id'], ['id'])
    
    # Rename apps table back to services
    op.rename_table('apps', 'services')
