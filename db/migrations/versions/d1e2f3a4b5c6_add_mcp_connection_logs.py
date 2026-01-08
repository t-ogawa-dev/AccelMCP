"""add_mcp_connection_logs

Revision ID: d1e2f3a4b5c6
Revises: 20251204014934
Create Date: 2026-01-08 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'd1e2f3a4b5c6'
down_revision = '20251204014934'
branch_labels = None
depends_on = None


def upgrade():
    # Create mcp_connection_logs table
    op.create_table(
        'mcp_connection_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow, index=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        
        # Account info (nullable for public access)
        sa.Column('account_id', sa.Integer(), sa.ForeignKey('connection_accounts.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('account_name', sa.String(100), nullable=True),  # Snapshot for audit trail
        
        # Resource hierarchy
        sa.Column('mcp_service_id', sa.Integer(), sa.ForeignKey('mcp_services.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('mcp_service_name', sa.String(100), nullable=True),  # Snapshot
        sa.Column('app_id', sa.Integer(), sa.ForeignKey('apps.id', ondelete='SET NULL'), nullable=True),
        sa.Column('app_name', sa.String(100), nullable=True),  # Snapshot
        sa.Column('capability_id', sa.Integer(), sa.ForeignKey('capabilities.id', ondelete='SET NULL'), nullable=True),
        sa.Column('capability_name', sa.String(100), nullable=True),  # Snapshot
        
        # Request info
        sa.Column('mcp_method', sa.String(50), nullable=False, index=True),  # initialize, tools/list, tools/call, etc.
        sa.Column('tool_name', sa.String(100), nullable=True),  # Tool name for tools/call
        sa.Column('request_id', sa.String(100), nullable=True),  # JSON-RPC id
        
        # Request/Response bodies (size-limited, masked)
        sa.Column('request_body', sa.Text(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        
        # Status
        sa.Column('status_code', sa.Integer(), nullable=True),  # HTTP-like status
        sa.Column('is_success', sa.Boolean(), nullable=False, default=True),
        sa.Column('error_code', sa.Integer(), nullable=True),  # JSON-RPC error code
        sa.Column('error_message', sa.Text(), nullable=True),
        
        # Client info
        sa.Column('ip_address', sa.String(45), nullable=True),  # IPv6 compatible
        sa.Column('user_agent', sa.String(500), nullable=True),
        
        # Access control
        sa.Column('access_control', sa.String(20), nullable=True),  # 'public' or 'restricted'
    )
    
    # Create index for common queries
    op.create_index('ix_mcp_connection_logs_created_at_desc', 'mcp_connection_logs', 
                   [sa.text('created_at DESC')], unique=False)
    
    # Insert default log settings into admin_settings
    op.execute("""
        INSERT INTO admin_settings (setting_key, setting_value, created_at, updated_at) VALUES
        ('mcp_log_enabled', 'true', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        ('mcp_log_retention_days', '90', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        ('mcp_log_max_body_size', '10240', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        ('mcp_log_mask_credit_card', 'true', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        ('mcp_log_mask_email', 'true', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        ('mcp_log_mask_phone', 'true', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        ('mcp_log_mask_custom_patterns', '', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """)


def downgrade():
    # Remove log settings from admin_settings
    op.execute("""
        DELETE FROM admin_settings WHERE setting_key IN (
            'mcp_log_enabled',
            'mcp_log_retention_days', 
            'mcp_log_max_body_size',
            'mcp_log_mask_credit_card',
            'mcp_log_mask_email',
            'mcp_log_mask_phone',
            'mcp_log_mask_custom_patterns'
        )
    """)
    
    # Drop indexes
    op.drop_index('ix_mcp_connection_logs_created_at_desc', table_name='mcp_connection_logs')
    
    # Drop table
    op.drop_table('mcp_connection_logs')
