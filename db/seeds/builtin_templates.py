"""
Builtin Service Templates Seed Data

Defines builtin service templates and their capabilities as Python data
"""
from app.models.models import db, McpServiceTemplate, McpCapabilityTemplate
import json


# Builtin service templates definition
BUILTIN_TEMPLATES = [
    {
        'name': 'Slack API',
        'service_type': 'api',
        'description': 'Slack Web API for sending messages and managing channels',
        'icon': '💬',
        'category': 'Communication',
        'capabilities': [
            {
                'name': 'post_message',
                'capability_type': 'tool',
                'url': 'https://slack.com/api/chat.postMessage',
                'headers': {'Authorization': 'Bearer YOUR_SLACK_BOT_TOKEN', 'Content-Type': 'application/json'},
                'body_params': {'channel': 'general', 'text': 'Hello from MCP!'},
                'description': 'Post a message to a Slack channel'
            },
            {
                'name': 'list_channels',
                'capability_type': 'tool',
                'url': 'https://slack.com/api/conversations.list',
                'headers': {'Authorization': 'Bearer YOUR_SLACK_BOT_TOKEN'},
                'body_params': {},
                'description': 'List all channels in the workspace'
            },
            {
                'name': 'get_user_info',
                'capability_type': 'tool',
                'url': 'https://slack.com/api/users.info',
                'headers': {'Authorization': 'Bearer YOUR_SLACK_BOT_TOKEN'},
                'body_params': {'user': 'U1234567890'},
                'description': 'Get information about a user'
            }
        ]
    },
    {
        'name': 'GitHub API',
        'service_type': 'api',
        'description': 'GitHub REST API for repository and issue management',
        'icon': '🐙',
        'category': 'Development',
        'capabilities': [
            {
                'name': 'get_repository',
                'capability_type': 'tool',
                'url': 'https://api.github.com/repos/{owner}/{repo}',
                'headers': {'Authorization': 'token YOUR_GITHUB_TOKEN', 'Accept': 'application/vnd.github.v3+json'},
                'body_params': {'owner': 'octocat', 'repo': 'Hello-World'},
                'description': 'Get repository information'
            },
            {
                'name': 'list_issues',
                'capability_type': 'tool',
                'url': 'https://api.github.com/repos/{owner}/{repo}/issues',
                'headers': {'Authorization': 'token YOUR_GITHUB_TOKEN', 'Accept': 'application/vnd.github.v3+json'},
                'body_params': {'owner': 'octocat', 'repo': 'Hello-World', 'state': 'open'},
                'description': 'List issues in a repository'
            },
            {
                'name': 'create_issue',
                'capability_type': 'tool',
                'url': 'https://api.github.com/repos/{owner}/{repo}/issues',
                'headers': {'Authorization': 'token YOUR_GITHUB_TOKEN', 'Accept': 'application/vnd.github.v3+json'},
                'body_params': {'owner': 'octocat', 'repo': 'Hello-World', 'title': 'Bug report', 'body': 'Something is not working'},
                'description': 'Create a new issue'
            }
        ]
    },
    {
        'name': 'AWS S3 API',
        'service_type': 'api',
        'description': 'AWS S3 for object storage operations',
        'icon': '☁️',
        'category': 'Cloud',
        'capabilities': [
            {
                'name': 'list_buckets',
                'capability_type': 'tool',
                'url': 'https://s3.amazonaws.com/',
                'headers': {'Authorization': 'AWS4-HMAC-SHA256 Credential=YOUR_ACCESS_KEY', 'x-amz-date': '20230101T000000Z'},
                'body_params': {},
                'description': 'List all S3 buckets'
            },
            {
                'name': 'get_object',
                'capability_type': 'tool',
                'url': 'https://{bucket}.s3.amazonaws.com/{key}',
                'headers': {'Authorization': 'AWS4-HMAC-SHA256 Credential=YOUR_ACCESS_KEY'},
                'body_params': {'bucket': 'my-bucket', 'key': 'file.txt'},
                'description': 'Get an object from S3'
            },
            {
                'name': 'put_object',
                'capability_type': 'tool',
                'url': 'https://{bucket}.s3.amazonaws.com/{key}',
                'headers': {'Authorization': 'AWS4-HMAC-SHA256 Credential=YOUR_ACCESS_KEY', 'Content-Type': 'application/octet-stream'},
                'body_params': {'bucket': 'my-bucket', 'key': 'file.txt'},
                'description': 'Upload an object to S3'
            }
        ]
    },
    {
        'name': 'OpenWeather API',
        'service_type': 'api',
        'description': 'OpenWeather API for weather data',
        'icon': '🌤️',
        'category': 'Data',
        'capabilities': [
            {
                'name': 'get_current_weather',
                'capability_type': 'tool',
                'url': 'https://api.openweathermap.org/data/2.5/weather',
                'headers': {},
                'body_params': {'q': 'Tokyo', 'appid': 'YOUR_API_KEY', 'units': 'metric'},
                'description': 'Get current weather for a city'
            },
            {
                'name': 'get_forecast',
                'capability_type': 'tool',
                'url': 'https://api.openweathermap.org/data/2.5/forecast',
                'headers': {},
                'body_params': {'q': 'Tokyo', 'appid': 'YOUR_API_KEY', 'units': 'metric'},
                'description': 'Get 5-day weather forecast'
            }
        ]
    },
    {
        'name': 'OpenAI API',
        'service_type': 'api',
        'description': 'OpenAI API for AI completions and chat',
        'icon': '🤖',
        'category': 'AI',
        'capabilities': [
            {
                'name': 'chat_completion',
                'capability_type': 'tool',
                'url': 'https://api.openai.com/v1/chat/completions',
                'headers': {'Authorization': 'Bearer YOUR_OPENAI_API_KEY', 'Content-Type': 'application/json'},
                'body_params': {'model': 'gpt-3.5-turbo', 'messages': [{'role': 'user', 'content': 'Hello!'}]},
                'description': 'Create a chat completion'
            },
            {
                'name': 'create_embedding',
                'capability_type': 'tool',
                'url': 'https://api.openai.com/v1/embeddings',
                'headers': {'Authorization': 'Bearer YOUR_OPENAI_API_KEY', 'Content-Type': 'application/json'},
                'body_params': {'model': 'text-embedding-ada-002', 'input': 'Your text here'},
                'description': 'Create text embeddings'
            }
        ]
    },
    {
        'name': 'Google Calendar API',
        'service_type': 'api',
        'description': 'Google Calendar API for event management',
        'icon': '📅',
        'category': 'Productivity',
        'capabilities': [
            {
                'name': 'list_events',
                'capability_type': 'tool',
                'url': 'https://www.googleapis.com/calendar/v3/calendars/primary/events',
                'headers': {'Authorization': 'Bearer YOUR_GOOGLE_ACCESS_TOKEN'},
                'body_params': {'timeMin': '2023-01-01T00:00:00Z', 'maxResults': 10},
                'description': 'List calendar events'
            },
            {
                'name': 'create_event',
                'capability_type': 'tool',
                'url': 'https://www.googleapis.com/calendar/v3/calendars/primary/events',
                'headers': {'Authorization': 'Bearer YOUR_GOOGLE_ACCESS_TOKEN', 'Content-Type': 'application/json'},
                'body_params': {'summary': 'Meeting', 'start': {'dateTime': '2023-12-25T10:00:00Z'}, 'end': {'dateTime': '2023-12-25T11:00:00Z'}},
                'description': 'Create a new calendar event'
            }
        ]
    },
    {
        'name': 'Filesystem MCP',
        'service_type': 'mcp',
        'description': 'Local filesystem operations via MCP server',
        'icon': '📁',
        'category': 'System',
        'capabilities': [
            {
                'name': 'read_file',
                'capability_type': 'tool',
                'url': 'mcp://filesystem',
                'headers': {},
                'body_params': {'path': '/path/to/file.txt'},
                'description': 'Read contents of a file'
            },
            {
                'name': 'write_file',
                'capability_type': 'tool',
                'url': 'mcp://filesystem',
                'headers': {},
                'body_params': {'path': '/path/to/file.txt', 'content': 'File content'},
                'description': 'Write content to a file'
            },
            {
                'name': 'list_directory',
                'capability_type': 'tool',
                'url': 'mcp://filesystem',
                'headers': {},
                'body_params': {'path': '/path/to/directory'},
                'description': 'List files in a directory'
            }
        ]
    },
    {
        'name': 'Database MCP',
        'service_type': 'mcp',
        'description': 'Database query execution via MCP server',
        'icon': '🗄️',
        'category': 'Data',
        'capabilities': [
            {
                'name': 'execute_query',
                'capability_type': 'tool',
                'url': 'mcp://database',
                'headers': {},
                'body_params': {'query': 'SELECT * FROM users LIMIT 10'},
                'description': 'Execute SQL query'
            },
            {
                'name': 'list_tables',
                'capability_type': 'tool',
                'url': 'mcp://database',
                'headers': {},
                'body_params': {},
                'description': 'List all database tables'
            },
            {
                'name': 'describe_table',
                'capability_type': 'tool',
                'url': 'mcp://database',
                'headers': {},
                'body_params': {'table': 'users'},
                'description': 'Get table schema information'
            }
        ]
    },
    {
        'name': 'Git MCP',
        'service_type': 'mcp',
        'description': 'Git repository operations via MCP server',
        'icon': '🌿',
        'category': 'Development',
        'capabilities': [
            {
                'name': 'git_status',
                'capability_type': 'tool',
                'url': 'mcp://git',
                'headers': {},
                'body_params': {'repository': '/path/to/repo'},
                'description': 'Get repository status'
            },
            {
                'name': 'git_commit',
                'capability_type': 'tool',
                'url': 'mcp://git',
                'headers': {},
                'body_params': {'repository': '/path/to/repo', 'message': 'Commit message'},
                'description': 'Create a git commit'
            },
            {
                'name': 'git_log',
                'capability_type': 'tool',
                'url': 'mcp://git',
                'headers': {},
                'body_params': {'repository': '/path/to/repo', 'limit': 10},
                'description': 'Get commit history'
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
                print(f"  ⊙ Template '{template_data['name']}' already exists, skipping")
                continue
            
            # Create service template
            template = McpServiceTemplate(
                name=template_data['name'],
                template_type='builtin',
                service_type=template_data['service_type'],
                description=template_data['description'],
                common_headers=json.dumps({}),
                icon=template_data['icon'],
                category=template_data['category']
            )
            db.session.add(template)
            db.session.flush()  # Get the ID
            
            # Create capability templates
            for cap_data in template_data['capabilities']:
                capability = McpCapabilityTemplate(
                    service_template_id=template.id,
                    name=cap_data['name'],
                    capability_type=cap_data['capability_type'],
                    url=cap_data['url'],
                    headers=json.dumps(cap_data['headers']),
                    body_params=json.dumps(cap_data['body_params']),
                    template_content='',
                    description=cap_data['description']
                )
                db.session.add(capability)
            
            db.session.commit()
            print(f"  ✓ Successfully loaded '{template_data['name']}' with {len(template_data['capabilities'])} capabilities")
            
        except Exception as e:
            print(f"  ✗ Error loading '{template_data['name']}': {e}")
            db.session.rollback()
            raise
    
    print("✓ All builtin templates loaded successfully")
