"""
Builtin Service Templates Seed Data

Defines builtin service templates as Python data
"""
from app.models.models import db, McpServiceTemplate
import json


# Builtin service templates definition
BUILTIN_TEMPLATES = [
    {
        'name': 'GitHub MCP',
        'service_type': 'mcp',
        'description': 'GitHub Copilot MCP server for AI-powered development assistance',
        'icon': '🐙',
        'category': 'AI',
        'mcp_url': 'https://api.githubcopilot.com/mcp/',
        'official_url': 'https://github.com/github/github-mcp-server',
        'common_headers': {
            'Authorization': 'Bearer YOUR_GITHUB_TOKEN'
        }
    },
    {
        'name': 'MS Learn MCP',
        'service_type': 'mcp',
        'description': 'Microsoft Learn MCP server for documentation and learning resources',
        'icon': '📚',
        'category': 'Documentation',
        'mcp_url': 'https://learn.microsoft.com/api/mcp',
        'official_url': 'https://learn.microsoft.com/',
        'common_headers': {}
    }
]


def load_service_templates():
    """
    Load builtin service templates from Python data structure
    This is called from migration scripts to seed template data
    """
    print("Loading builtin service templates...")
    
    for template_data in BUILTIN_TEMPLATES:
        try:
            # Check if template already exists
            existing = McpServiceTemplate.query.filter_by(
                name=template_data['name'],
                template_type='builtin'
            ).first()
            
            if existing:
                print(f"  ⊙ Template '{template_data['name']}' already exists, skipping")
                continue
            
            # Create service template
            template = McpServiceTemplate(
                name=template_data['name'],
                template_type='builtin',
                service_type=template_data['service_type'],
                mcp_url=template_data.get('mcp_url'),
                official_url=template_data.get('official_url'),
                description=template_data['description'],
                common_headers=json.dumps(template_data.get('common_headers', {})),
                icon=template_data['icon'],
                category=template_data['category']
            )
            db.session.add(template)
            db.session.commit()
            print(f"  ✓ Successfully loaded '{template_data['name']}'")
            
        except Exception as e:
            print(f"  ✗ Error loading '{template_data['name']}': {e}")
            db.session.rollback()
            raise
    
    print("✓ All builtin templates loaded successfully")
