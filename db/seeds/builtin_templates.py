"""
Builtin Service Templates Seed Data

Defines builtin service templates as Python data
"""
from app.models.models import db, McpServiceTemplate, McpCapabilityTemplate
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
    },
    {
        'name': 'Slack API',
        'service_type': 'api',
        'description': 'Slack Web API for messaging and collaboration',
        'icon': '💬',
        'category': 'Communication',
        'mcp_url': 'https://slack.com/api/',
        'official_url': 'https://api.slack.com/',
        'common_headers': {
            'Authorization': 'Bearer YOUR_SLACK_TOKEN',
            'Content-Type': 'application/json'
        },
        'capabilities': [
            {
                'name': 'Post Message',
                'capability_type': 'tool',
                'endpoint_path': 'chat.postMessage',
                'method': 'POST',
                'description': 'Post a message to a Slack channel',
                'headers': {},
                'body_params': {
                    'channel': {'type': 'string', 'required': True, 'description': 'Channel ID or name'},
                    'text': {'type': 'string', 'required': True, 'description': 'Message text'},
                    'thread_ts': {'type': 'string', 'required': False, 'description': 'Thread timestamp'}
                }
            },
            {
                'name': 'List Channels',
                'capability_type': 'resource',
                'endpoint_path': 'conversations.list',
                'method': 'GET',
                'description': 'List all channels in workspace',
                'query_params': {
                    'types': {'type': 'string', 'required': False, 'description': 'Channel types (public_channel, private_channel)'}
                }
            }
        ]
    },
    {
        'name': 'GitHub API',
        'service_type': 'api',
        'description': 'GitHub REST API for repository management',
        'icon': '🐙',
        'category': 'Development',
        'mcp_url': 'https://api.github.com/',
        'official_url': 'https://docs.github.com/rest',
        'common_headers': {
            'Authorization': 'Bearer YOUR_GITHUB_TOKEN',
            'Accept': 'application/vnd.github.v3+json'
        },
        'capabilities': [
            {
                'name': 'Get Repository',
                'capability_type': 'resource',
                'endpoint_path': 'repos/{owner}/{repo}',
                'method': 'GET',
                'description': 'Get repository information',
                'headers': {}
            },
            {
                'name': 'Create Issue',
                'capability_type': 'tool',
                'endpoint_path': 'repos/{owner}/{repo}/issues',
                'method': 'POST',
                'description': 'Create a new issue',
                'headers': {'Content-Type': 'application/json'},
                'body_params': {
                    'title': {'type': 'string', 'required': True, 'description': 'Issue title'},
                    'body': {'type': 'string', 'required': False, 'description': 'Issue body'},
                    'labels': {'type': 'array', 'required': False, 'description': 'Labels'}
                }
            },
            {
                'name': 'List Pull Requests',
                'capability_type': 'resource',
                'endpoint_path': 'repos/{owner}/{repo}/pulls',
                'method': 'GET',
                'description': 'List pull requests',
                'query_params': {
                    'state': {'type': 'string', 'required': False, 'description': 'open, closed, or all'}
                }
            }
        ]
    },
    {
        'name': 'AWS S3 API',
        'service_type': 'api',
        'description': 'Amazon S3 API for cloud storage operations',
        'icon': '☁️',
        'category': 'Storage',
        'mcp_url': 'https://s3.amazonaws.com/',
        'official_url': 'https://docs.aws.amazon.com/s3/',
        'common_headers': {},
        'capabilities': [
            {
                'name': 'List Buckets',
                'capability_type': 'resource',
                'endpoint_path': '',
                'method': 'GET',
                'description': 'List all S3 buckets'
            },
            {
                'name': 'Upload Object',
                'capability_type': 'tool',
                'endpoint_path': '{bucket}/{key}',
                'method': 'PUT',
                'description': 'Upload an object to S3',
                'headers': {'Content-Type': 'application/octet-stream'}
            },
            {
                'name': 'Get Object',
                'capability_type': 'resource',
                'endpoint_path': '{bucket}/{key}',
                'method': 'GET',
                'description': 'Retrieve an object from S3'
            }
        ]
    },
    {
        'name': 'OpenWeather API',
        'service_type': 'api',
        'description': 'Weather data and forecasting API',
        'icon': '🌤️',
        'category': 'Data',
        'mcp_url': 'https://api.openweathermap.org/data/2.5/',
        'official_url': 'https://openweathermap.org/api',
        'common_headers': {},
        'capabilities': [
            {
                'name': 'Current Weather',
                'capability_type': 'resource',
                'endpoint_path': 'weather',
                'method': 'GET',
                'description': 'Get current weather data',
                'query_params': {
                    'q': {'type': 'string', 'required': True, 'description': 'City name'},
                    'appid': {'type': 'string', 'required': True, 'description': 'API key'},
                    'units': {'type': 'string', 'required': False, 'description': 'metric or imperial'}
                }
            },
            {
                'name': 'Weather Forecast',
                'capability_type': 'resource',
                'endpoint_path': 'forecast',
                'method': 'GET',
                'description': '5 day / 3 hour forecast',
                'query_params': {
                    'q': {'type': 'string', 'required': True, 'description': 'City name'},
                    'appid': {'type': 'string', 'required': True, 'description': 'API key'}
                }
            }
        ]
    },
    {
        'name': 'OpenAI API',
        'service_type': 'api',
        'description': 'OpenAI API for GPT models and AI capabilities',
        'icon': '🤖',
        'category': 'AI',
        'mcp_url': 'https://api.openai.com/v1/',
        'official_url': 'https://platform.openai.com/docs/api-reference',
        'common_headers': {
            'Authorization': 'Bearer YOUR_OPENAI_API_KEY'
        },
        'capabilities': [
            {
                'name': 'Create Chat Completion',
                'capability_type': 'tool',
                'endpoint_path': 'chat/completions',
                'method': 'POST',
                'description': 'Create a chat completion',
                'headers': {'Content-Type': 'application/json'},
                'body_params': {
                    'model': {'type': 'string', 'required': True, 'description': 'Model ID (e.g., gpt-4)'},
                    'messages': {'type': 'array', 'required': True, 'description': 'Array of message objects'},
                    'temperature': {'type': 'number', 'required': False, 'description': 'Sampling temperature'}
                }
            },
            {
                'name': 'List Models',
                'capability_type': 'resource',
                'endpoint_path': 'models',
                'method': 'GET',
                'description': 'List available models'
            }
        ]
    },
    {
        'name': 'Google Calendar API',
        'service_type': 'api',
        'description': 'Google Calendar API for event management',
        'icon': '📅',
        'category': 'Productivity',
        'mcp_url': 'https://www.googleapis.com/calendar/v3/',
        'official_url': 'https://developers.google.com/calendar/api',
        'common_headers': {
            'Authorization': 'Bearer YOUR_GOOGLE_TOKEN'
        },
        'capabilities': [
            {
                'name': 'List Events',
                'capability_type': 'resource',
                'endpoint_path': 'calendars/{calendarId}/events',
                'method': 'GET',
                'description': 'List calendar events',
                'query_params': {
                    'timeMin': {'type': 'string', 'required': False, 'description': 'Start time (RFC3339)'},
                    'timeMax': {'type': 'string', 'required': False, 'description': 'End time (RFC3339)'}
                }
            },
            {
                'name': 'Create Event',
                'capability_type': 'tool',
                'endpoint_path': 'calendars/{calendarId}/events',
                'method': 'POST',
                'description': 'Create a new event',
                'headers': {'Content-Type': 'application/json'},
                'body_params': {
                    'summary': {'type': 'string', 'required': True, 'description': 'Event title'},
                    'start': {'type': 'object', 'required': True, 'description': 'Start time object'},
                    'end': {'type': 'object', 'required': True, 'description': 'End time object'}
                }
            }
        ]
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
                print(f"  ⊙ Template '{template_data['name']}' already exists, updating capabilities...")
                template = existing
                # Update common_headers and other fields
                template.common_headers = json.dumps(template_data.get('common_headers', {}))
                template.description = template_data['description']
                template.icon = template_data['icon']
                template.category = template_data['category']
                template.mcp_url = template_data.get('mcp_url')
                template.official_url = template_data.get('official_url')
            else:
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
                db.session.flush()  # Get template ID
                print(f"  ✓ Successfully loaded '{template_data['name']}'")
            
            # For API templates, load capabilities
            if template_data['service_type'] == 'api' and 'capabilities' in template_data:
                # Remove existing capabilities for this template
                McpCapabilityTemplate.query.filter_by(template_id=template.id).delete()
                
                for cap_data in template_data['capabilities']:
                    capability = McpCapabilityTemplate(
                        template_id=template.id,
                        name=cap_data['name'],
                        capability_type=cap_data['capability_type'],
                        endpoint_path=cap_data.get('endpoint_path', ''),
                        method=cap_data.get('method', 'GET'),
                        description=cap_data.get('description', ''),
                        headers=json.dumps(cap_data.get('headers', {})),
                        body_params=json.dumps(cap_data.get('body_params', {})),
                        query_params=json.dumps(cap_data.get('query_params', {}))
                    )
                    db.session.add(capability)
                print(f"    → {len(template_data['capabilities'])} capabilities loaded")
            
            db.session.commit()
            
        except Exception as e:
            print(f"  ✗ Error loading '{template_data['name']}': {e}")
            db.session.rollback()
            raise
    
    print("✓ All builtin templates loaded successfully")
