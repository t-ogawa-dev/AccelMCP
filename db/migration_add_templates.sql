-- Migration: Add Service Templates and Capability Templates tables

-- Create service_templates table
CREATE TABLE IF NOT EXISTS service_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    template_type VARCHAR(20) NOT NULL COMMENT 'builtin or custom',
    service_type VARCHAR(20) NOT NULL COMMENT 'api or mcp',
    description TEXT,
    common_headers TEXT COMMENT 'JSON string',
    icon VARCHAR(10) COMMENT 'emoji icon',
    category VARCHAR(50) COMMENT 'e.g., Communication, Cloud, AI',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- Create capability_templates table
CREATE TABLE IF NOT EXISTS capability_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_template_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    capability_type VARCHAR(50) NOT NULL COMMENT 'tool, resource, prompt',
    url VARCHAR(500) COMMENT 'endpoint URL',
    headers TEXT COMMENT 'JSON string',
    body_params TEXT COMMENT 'JSON string',
    template_content TEXT COMMENT 'prompt template',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (service_template_id) REFERENCES service_templates (id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- Insert builtin templates

-- Slack Template
INSERT INTO
    service_templates (
        name,
        template_type,
        service_type,
        description,
        common_headers,
        icon,
        category
    )
VALUES (
        'Slack API',
        'builtin',
        'api',
        'Slack Web API for sending messages and managing channels',
        '{}',
        '💬',
        'Communication'
    );

SET @slack_template_id = LAST_INSERT_ID();

INSERT INTO
    capability_templates (
        service_template_id,
        name,
        capability_type,
        url,
        headers,
        body_params,
        description
    )
VALUES (
        @slack_template_id,
        'post_message',
        'tool',
        'https://slack.com/api/chat.postMessage',
        '{"Authorization": "Bearer YOUR_SLACK_BOT_TOKEN", "Content-Type": "application/json"}',
        '{"channel": "general", "text": "Hello from MCP!"}',
        'Post a message to a Slack channel'
    ),
    (
        @slack_template_id,
        'list_channels',
        'tool',
        'https://slack.com/api/conversations.list',
        '{"Authorization": "Bearer YOUR_SLACK_BOT_TOKEN"}',
        '{}',
        'List all channels in the workspace'
    ),
    (
        @slack_template_id,
        'get_user_info',
        'tool',
        'https://slack.com/api/users.info',
        '{"Authorization": "Bearer YOUR_SLACK_BOT_TOKEN"}',
        '{"user": "U1234567890"}',
        'Get information about a user'
    );

-- GitHub Template
INSERT INTO
    service_templates (
        name,
        template_type,
        service_type,
        description,
        common_headers,
        icon,
        category
    )
VALUES (
        'GitHub API',
        'builtin',
        'api',
        'GitHub REST API for repository and issue management',
        '{}',
        '🐙',
        'Development'
    );

SET @github_template_id = LAST_INSERT_ID();

INSERT INTO
    capability_templates (
        service_template_id,
        name,
        capability_type,
        url,
        headers,
        body_params,
        description
    )
VALUES (
        @github_template_id,
        'get_repository',
        'tool',
        'https://api.github.com/repos/{owner}/{repo}',
        '{"Authorization": "token YOUR_GITHUB_TOKEN", "Accept": "application/vnd.github.v3+json"}',
        '{"owner": "octocat", "repo": "Hello-World"}',
        'Get repository information'
    ),
    (
        @github_template_id,
        'list_issues',
        'tool',
        'https://api.github.com/repos/{owner}/{repo}/issues',
        '{"Authorization": "token YOUR_GITHUB_TOKEN", "Accept": "application/vnd.github.v3+json"}',
        '{"owner": "octocat", "repo": "Hello-World", "state": "open"}',
        'List issues in a repository'
    ),
    (
        @github_template_id,
        'create_issue',
        'tool',
        'https://api.github.com/repos/{owner}/{repo}/issues',
        '{"Authorization": "token YOUR_GITHUB_TOKEN", "Accept": "application/vnd.github.v3+json"}',
        '{"owner": "octocat", "repo": "Hello-World", "title": "Bug report", "body": "Something is not working"}',
        'Create a new issue'
    );

-- AWS S3 Template
INSERT INTO
    service_templates (
        name,
        template_type,
        service_type,
        description,
        common_headers,
        icon,
        category
    )
VALUES (
        'AWS S3 API',
        'builtin',
        'api',
        'AWS S3 for object storage operations',
        '{}',
        '☁️',
        'Cloud'
    );

SET @aws_template_id = LAST_INSERT_ID();

INSERT INTO
    capability_templates (
        service_template_id,
        name,
        capability_type,
        url,
        headers,
        body_params,
        description
    )
VALUES (
        @aws_template_id,
        'list_buckets',
        'tool',
        'https://s3.amazonaws.com/',
        '{"Authorization": "AWS4-HMAC-SHA256 Credential=YOUR_ACCESS_KEY", "x-amz-date": "20230101T000000Z"}',
        '{}',
        'List all S3 buckets'
    ),
    (
        @aws_template_id,
        'get_object',
        'tool',
        'https://{bucket}.s3.amazonaws.com/{key}',
        '{"Authorization": "AWS4-HMAC-SHA256 Credential=YOUR_ACCESS_KEY"}',
        '{"bucket": "my-bucket", "key": "file.txt"}',
        'Get an object from S3'
    ),
    (
        @aws_template_id,
        'put_object',
        'tool',
        'https://{bucket}.s3.amazonaws.com/{key}',
        '{"Authorization": "AWS4-HMAC-SHA256 Credential=YOUR_ACCESS_KEY", "Content-Type": "application/octet-stream"}',
        '{"bucket": "my-bucket", "key": "file.txt"}',
        'Upload an object to S3'
    );

-- OpenWeather Template
INSERT INTO
    service_templates (
        name,
        template_type,
        service_type,
        description,
        common_headers,
        icon,
        category
    )
VALUES (
        'OpenWeather API',
        'builtin',
        'api',
        'OpenWeather API for weather data',
        '{}',
        '🌤️',
        'Data'
    );

SET @weather_template_id = LAST_INSERT_ID();

INSERT INTO
    capability_templates (
        service_template_id,
        name,
        capability_type,
        url,
        headers,
        body_params,
        description
    )
VALUES (
        @weather_template_id,
        'get_current_weather',
        'tool',
        'https://api.openweathermap.org/data/2.5/weather',
        '{}',
        '{"q": "Tokyo", "appid": "YOUR_API_KEY", "units": "metric"}',
        'Get current weather for a city'
    ),
    (
        @weather_template_id,
        'get_forecast',
        'tool',
        'https://api.openweathermap.org/data/2.5/forecast',
        '{}',
        '{"q": "Tokyo", "appid": "YOUR_API_KEY", "units": "metric"}',
        'Get 5-day weather forecast'
    );

-- OpenAI Template
INSERT INTO
    service_templates (
        name,
        template_type,
        service_type,
        description,
        common_headers,
        icon,
        category
    )
VALUES (
        'OpenAI API',
        'builtin',
        'api',
        'OpenAI API for AI completions and chat',
        '{}',
        '🤖',
        'AI'
    );

SET @openai_template_id = LAST_INSERT_ID();

INSERT INTO
    capability_templates (
        service_template_id,
        name,
        capability_type,
        url,
        headers,
        body_params,
        description
    )
VALUES (
        @openai_template_id,
        'chat_completion',
        'tool',
        'https://api.openai.com/v1/chat/completions',
        '{"Authorization": "Bearer YOUR_OPENAI_API_KEY", "Content-Type": "application/json"}',
        '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello!"}]}',
        'Create a chat completion'
    ),
    (
        @openai_template_id,
        'create_embedding',
        'tool',
        'https://api.openai.com/v1/embeddings',
        '{"Authorization": "Bearer YOUR_OPENAI_API_KEY", "Content-Type": "application/json"}',
        '{"model": "text-embedding-ada-002", "input": "Your text here"}',
        'Create text embeddings'
    );

-- Google Calendar Template
INSERT INTO
    service_templates (
        name,
        template_type,
        service_type,
        description,
        common_headers,
        icon,
        category
    )
VALUES (
        'Google Calendar API',
        'builtin',
        'api',
        'Google Calendar API for event management',
        '{}',
        '📅',
        'Productivity'
    );

SET @calendar_template_id = LAST_INSERT_ID();

INSERT INTO
    capability_templates (
        service_template_id,
        name,
        capability_type,
        url,
        headers,
        body_params,
        description
    )
VALUES (
        @calendar_template_id,
        'list_events',
        'tool',
        'https://www.googleapis.com/calendar/v3/calendars/primary/events',
        '{"Authorization": "Bearer YOUR_GOOGLE_ACCESS_TOKEN"}',
        '{"timeMin": "2023-01-01T00:00:00Z", "maxResults": 10}',
        'List calendar events'
    ),
    (
        @calendar_template_id,
        'create_event',
        'tool',
        'https://www.googleapis.com/calendar/v3/calendars/primary/events',
        '{"Authorization": "Bearer YOUR_GOOGLE_ACCESS_TOKEN", "Content-Type": "application/json"}',
        '{"summary": "Meeting", "start": {"dateTime": "2023-12-25T10:00:00Z"}, "end": {"dateTime": "2023-12-25T11:00:00Z"}}',
        'Create a new calendar event'
    );