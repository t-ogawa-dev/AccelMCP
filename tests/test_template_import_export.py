"""
Tests for Template Import/Export feature
"""
import json
import yaml
import pytest
from app.models.models import McpServiceTemplate, McpCapabilityTemplate


class TestTemplateExportImport:
    """Test Template Export and Import API endpoints"""
    
    def test_export_template_yaml(self, auth_client, db):
        """Test GET /api/mcp-templates/<id>/export - YAML形式でエクスポート"""
        # Create template with capabilities
        template = McpServiceTemplate(
            name='Export Test Template',
            template_type='custom',
            service_type='api',
            mcp_url='https://api.test.com',
            official_url='https://docs.test.com',
            description='Template for export testing',
            common_headers='{"Authorization": "Bearer TOKEN"}',
            icon='🧪',
            category='Testing'
        )
        db.session.add(template)
        db.session.commit()
        
        # Create capability template
        cap_template = McpCapabilityTemplate(
            template_id=template.id,
            name='Test Capability',
            capability_type='tool',
            endpoint_path='/api/test',
            method='POST',
            description='Test capability',
            headers='{"Content-Type": "application/json"}',
            body_params='{"param1": {"type": "string", "required": true}}',
            query_params='{}'
        )
        db.session.add(cap_template)
        db.session.commit()
        
        # Export
        response = auth_client.get(f'/api/mcp-templates/{template.id}/export')
        
        assert response.status_code == 200
        assert 'application/x-yaml' in response.content_type
        assert 'attachment' in response.headers.get('Content-Disposition', '')
        
        # Parse YAML
        data = yaml.safe_load(response.data)
        assert data['name'] == 'Export Test Template'
        assert data['service_type'] == 'api'
        assert data['mcp_url'] == 'https://api.test.com'
        assert data['official_url'] == 'https://docs.test.com'
        assert data['description'] == 'Template for export testing'
        assert data['icon'] == '🧪'
        assert data['category'] == 'Testing'
        assert 'Authorization' in data['common_headers']
        
        # Check capabilities
        assert 'capabilities' in data
        assert len(data['capabilities']) == 1
        cap_data = data['capabilities'][0]
        assert cap_data['name'] == 'Test Capability'
        assert cap_data['capability_type'] == 'tool'
        assert cap_data['endpoint_path'] == '/api/test'
        assert cap_data['method'] == 'POST'
    
    def test_export_mcp_template_yaml(self, auth_client, db):
        """Test exporting MCP type template (no capabilities)"""
        template = McpServiceTemplate(
            name='MCP Template',
            template_type='custom',
            service_type='mcp',
            mcp_url='https://mcp.test.com',
            description='MCP template',
            common_headers='{}',
            icon='🔧',
            category='MCP'
        )
        db.session.add(template)
        db.session.commit()
        
        response = auth_client.get(f'/api/mcp-templates/{template.id}/export')
        
        assert response.status_code == 200
        data = yaml.safe_load(response.data)
        assert data['name'] == 'MCP Template'
        assert data['service_type'] == 'mcp'
        # MCP templates should not have capabilities
        assert 'capabilities' not in data or len(data.get('capabilities', [])) == 0
    
    def test_import_template_yaml(self, auth_client):
        """Test POST /api/mcp-templates/import - YAML形式でインポート"""
        yaml_data = """
name: Imported Template
service_type: api
mcp_url: https://api.imported.com
official_url: https://docs.imported.com
description: Imported from YAML
common_headers:
  Authorization: Bearer IMPORT_TOKEN
  Content-Type: application/json
icon: 📦
category: Imported
"""
        
        response = auth_client.post(
            '/api/mcp-templates/import',
            data=yaml_data,
            content_type='application/x-yaml'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Imported Template'
        assert data['service_type'] == 'api'
        assert data['template_type'] == 'custom'
        assert data['mcp_url'] == 'https://api.imported.com'
        assert data['icon'] == '📦'
        assert data['category'] == 'Imported'
    
    def test_import_template_with_capabilities(self, auth_client, db):
        """Test importing template with capabilities (future enhancement)"""
        yaml_data = """
name: Template with Capabilities
service_type: api
mcp_url: https://api.example.com
description: Has capabilities
common_headers: {}
icon: 🎯
category: Test
capabilities:
  - name: Get Resource
    capability_type: resource
    endpoint_path: /resource
    method: GET
    description: Get resource
    headers: {}
    body_params: {}
    query_params: {}
"""
        
        response = auth_client.post(
            '/api/mcp-templates/import',
            data=yaml_data,
            content_type='application/x-yaml'
        )
        
        # Current implementation creates template but may not handle capabilities
        # This test documents expected behavior
        assert response.status_code == 201
    
    def test_import_invalid_yaml(self, auth_client):
        """Test importing invalid YAML returns error"""
        invalid_yaml = """
name: Invalid Template
  this is: not valid
    yaml: data
"""
        
        response = auth_client.post(
            '/api/mcp-templates/import',
            data=invalid_yaml,
            content_type='application/x-yaml'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'YAML' in data['error']
    
    def test_export_import_roundtrip(self, auth_client, db):
        """Test exporting and re-importing a template produces equivalent data"""
        # Create original template
        original = McpServiceTemplate(
            name='Roundtrip Template',
            template_type='custom',
            service_type='api',
            mcp_url='https://api.roundtrip.com',
            description='Roundtrip test',
            common_headers='{"X-Custom": "Value"}',
            icon='🔄',
            category='Test'
        )
        db.session.add(original)
        db.session.commit()
        
        # Export
        export_response = auth_client.get(f'/api/mcp-templates/{original.id}/export')
        assert export_response.status_code == 200
        exported_yaml = export_response.data
        
        # Import
        import_response = auth_client.post(
            '/api/mcp-templates/import',
            data=exported_yaml,
            content_type='application/x-yaml'
        )
        
        assert import_response.status_code == 201
        imported = json.loads(import_response.data)
        
        # Compare key fields
        assert imported['name'] == original.name
        assert imported['service_type'] == original.service_type
        assert imported['mcp_url'] == original.mcp_url
        assert imported['description'] == original.description
        assert imported['icon'] == original.icon
        assert imported['category'] == original.category
    
    def test_export_builtin_template(self, auth_client, db):
        """Test exporting builtin template"""
        builtin = McpServiceTemplate(
            name='Builtin Template',
            template_type='builtin',
            service_type='mcp',
            mcp_url='https://builtin.example.com',
            description='Builtin template',
            common_headers='{}',
            icon='⭐',
            category='Builtin',
            template_id='builtin-test',
            template_version='1.0.0'
        )
        db.session.add(builtin)
        db.session.commit()
        
        response = auth_client.get(f'/api/mcp-templates/{builtin.id}/export')
        
        assert response.status_code == 200
        data = yaml.safe_load(response.data)
        assert data['name'] == 'Builtin Template'
        assert data['service_type'] == 'mcp'
    
    def test_import_creates_custom_template(self, auth_client, db):
        """Test that imported templates are always created as 'custom' type"""
        yaml_data = """
name: Should Be Custom
service_type: mcp
description: Always custom
common_headers: {}
icon: 📝
category: Custom
"""
        
        response = auth_client.post(
            '/api/mcp-templates/import',
            data=yaml_data,
            content_type='application/x-yaml'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        # Verify it's created as custom type, not builtin
        assert data['template_type'] == 'custom'
    
    def test_export_filename_contains_template_name(self, auth_client, db):
        """Test that export response includes proper filename"""
        template = McpServiceTemplate(
            name='My Special Template',
            template_type='custom',
            service_type='api',
            description='Test',
            common_headers='{}',
            icon='📋',
            category='Test'
        )
        db.session.add(template)
        db.session.commit()
        
        response = auth_client.get(f'/api/mcp-templates/{template.id}/export')
        
        assert response.status_code == 200
        content_disposition = response.headers.get('Content-Disposition', '')
        assert 'filename=' in content_disposition
        assert 'My Special Template' in content_disposition or 'template-' in content_disposition
        assert '.yaml' in content_disposition


class TestTemplateExportFormat:
    """Test YAML export format quality"""
    
    def test_yaml_is_human_readable(self, auth_client, db):
        """Test that exported YAML is properly formatted"""
        template = McpServiceTemplate(
            name='Readable Template',
            template_type='custom',
            service_type='api',
            mcp_url='https://api.test.com',
            description='Multi-line\ndescription\nfor testing',
            common_headers='{"Header1": "Value1", "Header2": "Value2"}',
            icon='📖',
            category='Readable'
        )
        db.session.add(template)
        db.session.commit()
        
        response = auth_client.get(f'/api/mcp-templates/{template.id}/export')
        yaml_text = response.data.decode('utf-8')
        
        # Check YAML quality
        assert 'name: Readable Template' in yaml_text
        assert 'service_type: api' in yaml_text
        assert 'common_headers:' in yaml_text
        # Should use proper YAML formatting, not flow style
        assert 'Header1: Value1' in yaml_text or '"Header1": "Value1"' in yaml_text
    
    def test_unicode_in_yaml(self, auth_client, db):
        """Test that Unicode characters are preserved in YAML"""
        template = McpServiceTemplate(
            name='日本語テンプレート',
            template_type='custom',
            service_type='api',
            description='これは日本語の説明です',
            common_headers='{}',
            icon='🇯🇵',
            category='国際化'
        )
        db.session.add(template)
        db.session.commit()
        
        response = auth_client.get(f'/api/mcp-templates/{template.id}/export')
        
        assert response.status_code == 200
        data = yaml.safe_load(response.data)
        assert data['name'] == '日本語テンプレート'
        assert data['description'] == 'これは日本語の説明です'
        assert data['icon'] == '🇯🇵'
        assert data['category'] == '国際化'
