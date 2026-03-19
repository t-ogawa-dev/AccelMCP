[日本語](../MIGRATION.md) | English

# Database Migration Guide

AccelMCP uses Flask-Migrate (Alembic) for database migration management.

Migration files are located in the `db/migrations/` directory.

## Directory Structure

```
db/
├── migrate.py              # Migration management script
└── migrations/             # Alembic directory
    ├── alembic.ini          # Alembic configuration
    ├── env.py               # Migration environment settings
    ├── script.py.mako       # Migration template
    └── versions/            # Migration files
```

## Setup

### Initial Setup

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Apply migrations**
   ```bash
   python db/migrate.py upgrade
   ```

## Migration Commands

### Create a new migration

```bash
python db/migrate.py migrate "Description of changes"
```

### Apply migrations (upgrade)

```bash
python db/migrate.py upgrade
```

### Roll back migrations (downgrade)

```bash
python db/migrate.py downgrade
```

### Check current revision

```bash
python db/migrate.py current
```

### Show migration history

```bash
python db/migrate.py history
```

## Using with Docker

### Initial startup

```bash
docker compose up -d
```

`python db/migrate.py upgrade` is automatically executed when the container starts.

### Create a new migration (in local environment)

```bash
# After modifying models locally
python db/migrate.py migrate "Add new field"

# Review the migration file
git add db/migrations/versions/
git commit -m "Add migration: Add new field"

# Restart the container to apply the migration
docker compose restart web
```

### Roll back a migration

```bash
docker compose exec web python db/migrate.py downgrade
```

## Adding Service Templates

Service templates are managed in `BUILTIN_TEMPLATES` within `app/utils/template_loader.py`.

### Steps to add a new template

1. **Edit `app/utils/template_loader.py`**

   Add a new template to the `BUILTIN_TEMPLATES` list:

   ```python
   BUILTIN_TEMPLATES = [
       # ... existing templates ...
       {
           'name': 'MS Office API',
           'service_type': 'api',
           'description': 'Microsoft Office API for document management',
           'icon': '📄',
           'category': 'Productivity',
           'capabilities': [
               {
                   'name': 'list_documents',
                   'capability_type': 'tool',
                   'url': 'https://graph.microsoft.com/v1.0/me/drive/root/children',
                   'headers': {'Authorization': 'Bearer YOUR_MS_TOKEN'},
                   'body_params': {},
                   'description': 'List all documents'
               }
           ]
       }
   ]
   ```

2. **Create a migration**

   ```bash
   python db/migrate.py migrate "Add MS Office template"
   ```

3. **Edit the migration file (if needed)**

   Add data loading logic to the generated migration file:

   ```python
   from app.utils.template_loader import load_service_templates

   def upgrade():
       # Load templates
       load_service_templates()

   def downgrade():
       # Rollback logic
       op.execute("""
           DELETE FROM mcp_capability_templates
           WHERE service_template_id IN (
               SELECT id FROM mcp_service_templates
               WHERE name = 'MS Office API'
           )
       """)
       op.execute("""
           DELETE FROM mcp_service_templates
           WHERE name = 'MS Office API'
       """)
   ```

4. **Apply the migration**

   ```bash
   python db/migrate.py upgrade
   ```

## Troubleshooting

### Resetting the database

```bash
docker compose down -v  # Delete volumes
docker compose up -d    # Restart and apply migrations
```

### When migration history is corrupted

```bash
# Connect to the database directly
docker compose exec db mysql -u mcpuser -p mcpdb

# Check the alembic_version table
SELECT * FROM alembic_version;

# Reset if necessary
DELETE FROM alembic_version;
```

### Migration file conflicts

```bash
# Merge migrations
python db/migrate.py merge heads -m "Merge migrations"
```

## Best Practices

1. **Always create a migration after changing a model**
   - After modifying `app/models/models.py`, run `python db/migrate.py migrate`

2. **Review migration files**
   - Check the auto-generated migration file
   - Adjust manually as needed

3. **Migrations in production**
   - Always take a backup first
   - Test on a staging environment
   - Plan for potential downtime

4. **Team development**
   - Manage migration files in Git
   - Include them in pull requests
   - After merging, everyone must run `upgrade`
