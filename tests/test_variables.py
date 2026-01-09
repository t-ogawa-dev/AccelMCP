"""
Tests for Variables feature
"""
import json
import pytest
from app.models.models import Variable


class TestVariableModel:
    """Test Variable model"""
    
    def test_create_variable(self, db):
        """Test creating a variable"""
        variable = Variable(
            name='TEST_VAR',
            value='test_value',
            source_type='manual',
            value_type='string',
            is_secret=False
        )
        db.session.add(variable)
        db.session.commit()
        
        assert variable.id is not None
        assert variable.name == 'TEST_VAR'
        assert variable.value == 'test_value'
    
    def test_variable_to_dict(self, db):
        """Test variable to_dict method"""
        variable = Variable(
            name='API_KEY',
            value='secret123',
            source_type='manual',
            value_type='string',
            is_secret=True,
            description='Test API key'
        )
        db.session.add(variable)
        db.session.commit()
        
        data = variable.to_dict()
        assert data['name'] == 'API_KEY'
        assert data['value'] == '********'  # Secret values are masked
        assert data['is_secret'] is True
        assert data['value_type'] == 'string'
    
    def test_env_variable(self, db):
        """Test environment variable type"""
        variable = Variable(
            name='PATH_VAR',
            value='MY_ENV_VAR',  # This refers to an env var name
            source_type='env',
            value_type='string',
            is_secret=False
        )
        db.session.add(variable)
        db.session.commit()
        
        assert variable.source_type == 'env'
        assert variable.value == 'MY_ENV_VAR'
    
    def test_number_variable(self, db):
        """Test number type variable"""
        variable = Variable(
            name='MAX_RETRIES',
            value='5',
            source_type='manual',
            value_type='number',
            is_secret=False
        )
        db.session.add(variable)
        db.session.commit()
        
        assert variable.value_type == 'number'
        assert variable.value == '5'


class TestVariableAPI:
    """Test Variable API endpoints"""
    
    def test_get_variables(self, auth_client, db):
        """Test GET /api/variables"""
        # Create test variables using set_value() for proper encryption
        var1 = Variable(name='VAR1', source_type='manual', value_type='string', is_secret=False)
        var1.set_value('value1')
        var2 = Variable(name='VAR2', source_type='manual', value_type='string', is_secret=True)
        var2.set_value('value2')
        db.session.add_all([var1, var2])
        db.session.commit()
        
        response = auth_client.get('/api/variables')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 2
        assert any(v['name'] == 'VAR1' for v in data)
        assert any(v['name'] == 'VAR2' for v in data)
    
    def test_create_variable(self, auth_client):
        """Test POST /api/variables"""
        payload = {
            'name': 'NEW_VAR',
            'value': 'new_value',
            'source_type': 'manual',
            'value_type': 'string',
            'is_secret': False,
            'description': 'Test variable'
        }
        response = auth_client.post('/api/variables',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'NEW_VAR'
        assert data['value'] == 'new_value'
    
    def test_create_secret_variable(self, auth_client):
        """Test creating a secret variable"""
        payload = {
            'name': 'API_SECRET',
            'value': 'super_secret',
            'source_type': 'manual',
            'value_type': 'string',
            'is_secret': True,
            'description': 'Secret API key'
        }
        response = auth_client.post('/api/variables',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['is_secret'] is True
    
    def test_create_env_variable(self, auth_client):
        """Test creating an environment variable reference"""
        payload = {
            'name': 'DB_PASSWORD',
            'value': 'DATABASE_PASSWORD',  # Env var name
            'source_type': 'env',
            'value_type': 'string',
            'is_secret': True,
            'description': 'Database password from env'
        }
        response = auth_client.post('/api/variables',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['source_type'] == 'env'
    
    def test_get_variable_detail(self, auth_client, db):
        """Test GET /api/variables/<id>"""
        variable = Variable(
            name='DETAIL_VAR',
            source_type='manual',
            value_type='string',
            is_secret=False
        )
        variable.set_value('detail_value')
        db.session.add(variable)
        db.session.commit()
        
        response = auth_client.get(f'/api/variables/{variable.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == variable.id
        assert data['name'] == 'DETAIL_VAR'
    
    def test_update_variable(self, auth_client, db):
        """Test PUT /api/variables/<id>"""
        variable = Variable(
            name='UPDATE_VAR',
            value='old_value',
            source_type='manual',
            value_type='string',
            is_secret=False
        )
        db.session.add(variable)
        db.session.commit()
        
        payload = {
            'value': 'new_value',
            'description': 'Updated description'
        }
        response = auth_client.put(f'/api/variables/{variable.id}',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['value'] == 'new_value'
    
    def test_delete_variable(self, auth_client, db):
        """Test DELETE /api/variables/<id>"""
        variable = Variable(
            name='DELETE_VAR',
            value='delete_value',
            source_type='manual',
            value_type='string',
            is_secret=False
        )
        db.session.add(variable)
        db.session.commit()
        variable_id = variable.id
        
        response = auth_client.delete(f'/api/variables/{variable_id}')
        
        assert response.status_code == 204
        
        # Verify deletion
        response = auth_client.get(f'/api/variables/{variable_id}')
        assert response.status_code == 404
    
    def test_duplicate_variable_name(self, auth_client, db):
        """Test preventing duplicate variable names"""
        variable = Variable(
            name='DUPLICATE',
            source_type='manual',
            value_type='string',
            is_secret=False
        )
        variable.set_value('value1')
        db.session.add(variable)
        db.session.commit()
        
        payload = {
            'name': 'DUPLICATE',
            'value': 'value2',
            'source_type': 'manual',
            'value_type': 'string',
            'is_secret': False
        }
        response = auth_client.post('/api/variables',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code in [400, 409]  # Bad request or conflict


class TestVariableReplacement:
    """Test variable replacement in capabilities"""
    
    def test_replace_in_url(self, db):
        """Test variable replacement in capability URL"""
        from app.services.variable_replacer import replace_variables
        
        # Create variable
        variable = Variable(
            name='API_ENDPOINT',
            source_type='manual',
            value_type='string',
            is_secret=False
        )
        variable.set_value('https://api.example.com')
        db.session.add(variable)
        db.session.commit()
        
        url = '{{API_ENDPOINT}}/users'
        result = replace_variables(url)
        
        assert result == 'https://api.example.com/users'
    
    def test_replace_in_headers(self, db):
        """Test variable replacement in headers"""
        from app.services.variable_replacer import replace_variables
        
        variable = Variable(
            name='AUTH_TOKEN',
            source_type='manual',
            value_type='string',
            is_secret=True
        )
        variable.set_value('Bearer abc123')
        db.session.add(variable)
        db.session.commit()
        
        headers = '{"Authorization": "{{AUTH_TOKEN}}"}'
        result = replace_variables(headers)
        
        assert 'Bearer abc123' in result
    
    def test_replace_multiple_variables(self, db):
        """Test replacing multiple variables in same string"""
        from app.services.variable_replacer import replace_variables
        
        var1 = Variable(name='HOST', source_type='manual', value_type='string', is_secret=False)
        var1.set_value('example.com')
        var2 = Variable(name='PORT', source_type='manual', value_type='number', is_secret=False)
        var2.set_value('8080')
        db.session.add_all([var1, var2])
        db.session.commit()
        
        url = 'https://{{HOST}}:{{PORT}}/api'
        result = replace_variables(url)
        
        assert result == 'https://example.com:8080/api'
    
    def test_missing_variable(self, db):
        """Test behavior when variable is not found"""
        from app.services.variable_replacer import replace_variables
        
        text = 'Value: {{MISSING_VAR}}'
        result = replace_variables(text)
        
        # Should keep placeholder if variable not found
        assert '{{MISSING_VAR}}' in result or result == 'Value: '
    
    def test_no_variables(self, db):
        """Test string with no variables returns unchanged"""
        from app.services.variable_replacer import replace_variables
        
        text = 'No variables here'
        result = replace_variables(text)
        
        assert result == 'No variables here'


class TestVariableViews:
    """Test Variable view endpoints"""
    
    def test_variable_list_view(self, auth_client):
        """Test GET /variables"""
        response = auth_client.get('/variables')
        
        assert response.status_code == 200
        assert b'Variables' in response.data or b'variables' in response.data
    
    def test_variable_new_view(self, auth_client):
        """Test GET /variables/new"""
        response = auth_client.get('/variables/new')
        
        assert response.status_code == 200
    
    def test_variable_edit_view(self, auth_client, db):
        """Test GET /variables/<id>/edit"""
        variable = Variable(
            name='EDIT_VIEW_VAR',
            value='value',
            source_type='manual',
            value_type='string',
            is_secret=False
        )
        db.session.add(variable)
        db.session.commit()
        
        response = auth_client.get(f'/variables/{variable.id}/edit')
        
        assert response.status_code == 200
