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
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
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
    },
    {
        'name': 'Notion API',
        'service_type': 'api',
        'description': 'Notion API for pages, databases and content management',
        'icon': '📝',
        'category': 'Productivity',
        'mcp_url': 'https://api.notion.com/v1/',
        'official_url': 'https://developers.notion.com/reference/intro',
        'common_headers': {
            'Authorization': 'Bearer YOUR_NOTION_TOKEN',
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json'
        },
        'capabilities': [
            {
                'name': 'Search',
                'capability_type': 'tool',
                'endpoint_path': 'search',
                'method': 'POST',
                'description': 'Search pages and databases across the workspace',
                'body_params': {
                    'query': {'type': 'string', 'required': False, 'description': 'Search text'}
                }
            },
            {
                'name': 'Retrieve a Page',
                'capability_type': 'resource',
                'endpoint_path': 'pages/{page_id}',
                'method': 'GET',
                'description': 'Get a page by ID'
            },
            {
                'name': 'Create a Page',
                'capability_type': 'tool',
                'endpoint_path': 'pages',
                'method': 'POST',
                'description': 'Create a new page',
                'body_params': {
                    'parent': {'type': 'object', 'required': True, 'description': 'Parent page or database reference'},
                    'properties': {'type': 'object', 'required': True, 'description': 'Page property values'}
                }
            },
            {
                'name': 'Query a Database',
                'capability_type': 'tool',
                'endpoint_path': 'databases/{database_id}/query',
                'method': 'POST',
                'description': 'Query rows of a database',
                'body_params': {
                    'filter': {'type': 'object', 'required': False, 'description': 'Filter conditions'},
                    'sorts': {'type': 'array', 'required': False, 'description': 'Sort conditions'}
                }
            }
        ]
    },
    {
        'name': 'Stripe API',
        'service_type': 'api',
        'description': 'Stripe API for payments, customers and billing',
        'icon': '💳',
        'category': 'Payments',
        'mcp_url': 'https://api.stripe.com/v1/',
        'official_url': 'https://stripe.com/docs/api',
        'common_headers': {
            'Authorization': 'Bearer YOUR_STRIPE_SECRET_KEY',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        'capabilities': [
            {
                'name': 'List Customers',
                'capability_type': 'resource',
                'endpoint_path': 'customers',
                'method': 'GET',
                'description': 'List existing customers',
                'query_params': {
                    'limit': {'type': 'integer', 'required': False, 'description': 'Number of results (max 100)'}
                }
            },
            {
                'name': 'Create Customer',
                'capability_type': 'tool',
                'endpoint_path': 'customers',
                'method': 'POST',
                'description': 'Create a new customer',
                'body_params': {
                    'email': {'type': 'string', 'required': False, 'description': 'Customer email'},
                    'name': {'type': 'string', 'required': False, 'description': 'Customer name'}
                }
            },
            {
                'name': 'Create PaymentIntent',
                'capability_type': 'tool',
                'endpoint_path': 'payment_intents',
                'method': 'POST',
                'description': 'Create a PaymentIntent to collect a payment',
                'body_params': {
                    'amount': {'type': 'integer', 'required': True, 'description': 'Amount in the smallest currency unit (e.g. cents)'},
                    'currency': {'type': 'string', 'required': True, 'description': 'Three-letter ISO currency code (e.g. usd)'}
                }
            },
            {
                'name': 'List Charges',
                'capability_type': 'resource',
                'endpoint_path': 'charges',
                'method': 'GET',
                'description': 'List recent charges',
                'query_params': {
                    'limit': {'type': 'integer', 'required': False, 'description': 'Number of results (max 100)'}
                }
            }
        ]
    },
    {
        'name': 'SendGrid API',
        'service_type': 'api',
        'description': 'SendGrid API for transactional email delivery',
        'icon': '📧',
        'category': 'Communication',
        'mcp_url': 'https://api.sendgrid.com/v3/',
        'official_url': 'https://docs.sendgrid.com/api-reference',
        'common_headers': {
            'Authorization': 'Bearer YOUR_SENDGRID_API_KEY',
            'Content-Type': 'application/json'
        },
        'capabilities': [
            {
                'name': 'Send Mail',
                'capability_type': 'tool',
                'endpoint_path': 'mail/send',
                'method': 'POST',
                'description': 'Send a transactional email',
                'body_params': {
                    'personalizations': {'type': 'array', 'required': True, 'description': 'Recipient(s) and substitution data'},
                    'from': {'type': 'object', 'required': True, 'description': 'Sender email object'},
                    'subject': {'type': 'string', 'required': True, 'description': 'Email subject'},
                    'content': {'type': 'array', 'required': True, 'description': 'Email body content (type/value pairs)'}
                }
            }
        ]
    },
    {
        'name': 'Discord API',
        'service_type': 'api',
        'description': 'Discord API for bots, channels and messaging',
        'icon': '🎮',
        'category': 'Communication',
        'mcp_url': 'https://discord.com/api/v10/',
        'official_url': 'https://discord.com/developers/docs/intro',
        'common_headers': {
            'Authorization': 'Bot YOUR_BOT_TOKEN',
            'Content-Type': 'application/json'
        },
        'capabilities': [
            {
                'name': 'Get Channel',
                'capability_type': 'resource',
                'endpoint_path': 'channels/{channel_id}',
                'method': 'GET',
                'description': 'Get a channel by ID'
            },
            {
                'name': 'Create Message',
                'capability_type': 'tool',
                'endpoint_path': 'channels/{channel_id}/messages',
                'method': 'POST',
                'description': 'Post a message to a channel',
                'body_params': {
                    'content': {'type': 'string', 'required': True, 'description': 'Message text'}
                }
            },
            {
                'name': 'Get Guild',
                'capability_type': 'resource',
                'endpoint_path': 'guilds/{guild_id}',
                'method': 'GET',
                'description': 'Get a guild (server) by ID'
            }
        ]
    },
    {
        'name': 'HubSpot API',
        'service_type': 'api',
        'description': 'HubSpot CRM API for contacts and customer data',
        'icon': '🧡',
        'category': 'CRM',
        'mcp_url': 'https://api.hubapi.com/',
        'official_url': 'https://developers.hubspot.com/docs/api/overview',
        'common_headers': {
            'Authorization': 'Bearer YOUR_HUBSPOT_ACCESS_TOKEN',
            'Content-Type': 'application/json'
        },
        'capabilities': [
            {
                'name': 'List Contacts',
                'capability_type': 'resource',
                'endpoint_path': 'crm/v3/objects/contacts',
                'method': 'GET',
                'description': 'List CRM contacts',
                'query_params': {
                    'limit': {'type': 'integer', 'required': False, 'description': 'Number of results (max 100)'}
                }
            },
            {
                'name': 'Create Contact',
                'capability_type': 'tool',
                'endpoint_path': 'crm/v3/objects/contacts',
                'method': 'POST',
                'description': 'Create a new CRM contact',
                'body_params': {
                    'properties': {'type': 'object', 'required': True, 'description': 'Contact property values (e.g. email, firstname)'}
                }
            }
        ]
    },
    {
        'name': 'Twilio API',
        'service_type': 'api',
        'description': 'Twilio API for SMS and voice messaging',
        'icon': '📱',
        'category': 'Communication',
        'mcp_url': 'https://api.twilio.com/2010-04-01/',
        'official_url': 'https://www.twilio.com/docs/usage/api',
        'common_headers': {
            'Authorization': 'Basic YOUR_BASE64_ACCOUNTSID_AUTHTOKEN',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        'capabilities': [
            {
                'name': 'Send SMS',
                'capability_type': 'tool',
                'endpoint_path': 'Accounts/{AccountSid}/Messages.json',
                'method': 'POST',
                'description': 'Send an SMS message',
                'body_params': {
                    'To': {'type': 'string', 'required': True, 'description': 'Recipient phone number (E.164)'},
                    'From': {'type': 'string', 'required': True, 'description': 'Sender phone number (E.164)'},
                    'Body': {'type': 'string', 'required': True, 'description': 'Message text'}
                }
            },
            {
                'name': 'List Messages',
                'capability_type': 'resource',
                'endpoint_path': 'Accounts/{AccountSid}/Messages.json',
                'method': 'GET',
                'description': 'List sent/received messages',
                'query_params': {
                    'PageSize': {'type': 'integer', 'required': False, 'description': 'Number of results per page'}
                }
            }
        ]
    }
]

# Version tag stamped on locally-seeded builtin templates, kept in sync with the
# latest entry in data/builtin_templates/index.yaml so a fresh install does not
# show a false "update available" badge in the admin UI.
BUILTIN_TEMPLATES_VERSION = '1.1.0'


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
                template.template_id = template_data['name'].lower().replace(' ', '-')
                template.template_version = BUILTIN_TEMPLATES_VERSION
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
                    category=template_data['category'],
                    template_id=template_data['name'].lower().replace(' ', '-'),
                    template_version=BUILTIN_TEMPLATES_VERSION
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

    # Remove builtin templates that are no longer part of the catalog (e.g. a template
    # retired in a later AccelMCP version, such as the removed AWS S3 API template).
    # Child capability rows must be deleted first: there is no ON DELETE CASCADE on the
    # mcp_capability_templates -> mcp_service_templates foreign key.
    current_names = {t['name'] for t in BUILTIN_TEMPLATES}
    stale_templates = McpServiceTemplate.query.filter_by(template_type='builtin').filter(
        ~McpServiceTemplate.name.in_(current_names)
    ).all()
    for stale in stale_templates:
        print(f"  ✗ Removing retired builtin template '{stale.name}'")
        McpCapabilityTemplate.query.filter_by(template_id=stale.id).delete()
        db.session.delete(stale)
    if stale_templates:
        db.session.commit()

    # Record the bootstrapped catalog version so the "check for updates" feature
    # does not report a false update on a fresh install.
    from app.models.models import AdminSettings

    setting = AdminSettings.query.filter_by(setting_key='builtin_templates_version').first()
    if setting:
        setting.setting_value = BUILTIN_TEMPLATES_VERSION
    else:
        db.session.add(AdminSettings(setting_key='builtin_templates_version', setting_value=BUILTIN_TEMPLATES_VERSION))
    db.session.commit()

    print("✓ All builtin templates loaded successfully")
