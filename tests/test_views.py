"""
Tests for view controllers (HTML pages)
"""
import pytest


class TestAuthViews:
    """Test authentication views"""
    
    def test_login_page(self, client):
        """Test GET /login"""
        response = client.get('/login')
        
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_login_success(self, client):
        """Test POST /login with correct credentials"""
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_login_failure(self, client):
        """Test POST /login with incorrect credentials"""
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'wrong'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should stay on login page or show error
    
    def test_logout(self, auth_client):
        """Test GET /logout"""
        response = auth_client.get('/logout', follow_redirects=True)
        
        assert response.status_code == 200


class TestDashboardViews:
    """Test dashboard views"""
    
    def test_dashboard_authenticated(self, auth_client):
        """Test GET / (dashboard) when authenticated"""
        response = auth_client.get('/', follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_dashboard_unauthenticated(self, client):
        """Test GET / (dashboard) redirects when not authenticated"""
        response = client.get('/', follow_redirects=False)
        
        # Should redirect to login
        assert response.status_code in [302, 401]


class TestServiceViews:
    """Test service views"""
    
    def test_service_list(self, auth_client):
        """Test GET /services"""
        response = auth_client.get('/services')
        
        assert response.status_code == 200
    
    def test_service_new(self, auth_client):
        """Test GET /services/new"""
        response = auth_client.get('/services/new')
        
        assert response.status_code == 200
    
    def test_service_detail(self, auth_client, sample_service):
        """Test GET /services/<id>"""
        response = auth_client.get(f'/services/{sample_service.id}')
        
        assert response.status_code == 200
    
    def test_service_edit(self, auth_client, sample_service):
        """Test GET /services/<id>/edit"""
        response = auth_client.get(f'/services/{sample_service.id}/edit')
        
        assert response.status_code == 200
    
    def test_service_capabilities(self, auth_client, sample_service):
        """Test GET /services/<id>/capabilities"""
        response = auth_client.get(f'/services/{sample_service.id}/capabilities')
        
        assert response.status_code == 200


class TestCapabilityViews:
    """Test capability views"""
    
    def test_capability_new(self, auth_client, sample_service):
        """Test GET /services/<id>/capabilities/new"""
        response = auth_client.get(f'/services/{sample_service.id}/capabilities/new')
        
        assert response.status_code == 200
    
    def test_capability_detail(self, auth_client, sample_capability):
        """Test GET /capabilities/<id>"""
        response = auth_client.get(f'/capabilities/{sample_capability.id}')
        
        assert response.status_code == 200
    
    def test_capability_edit(self, auth_client, sample_capability):
        """Test GET /capabilities/<id>/edit"""
        response = auth_client.get(f'/capabilities/{sample_capability.id}/edit')
        
        assert response.status_code == 200


class TestAccountViews:
    """Test connection account views"""
    
    def test_account_list(self, auth_client):
        """Test GET /accounts"""
        response = auth_client.get('/accounts')
        
        assert response.status_code == 200
    
    def test_account_new(self, auth_client):
        """Test GET /accounts/new"""
        response = auth_client.get('/accounts/new')
        
        assert response.status_code == 200
    
    def test_account_detail(self, auth_client, sample_account):
        """Test GET /accounts/<id>"""
        response = auth_client.get(f'/accounts/{sample_account.id}')
        
        assert response.status_code == 200
    
    @pytest.mark.skip(reason="Account edit route not implemented")
    def test_account_edit(self, auth_client, sample_account):
        """Test GET /accounts/<id>/edit"""
        response = auth_client.get(f'/accounts/{sample_account.id}/edit')
        
        assert response.status_code == 200


class TestTemplateViews:
    """Test template views"""
    
    def test_template_list(self, auth_client):
        """Test GET /templates"""
        response = auth_client.get('/mcp-templates')
        
        assert response.status_code == 200
    
    def test_template_new(self, auth_client):
        """Test GET /templates/new"""
        response = auth_client.get('/mcp-templates/new')
        
        assert response.status_code == 200
    
    def test_template_detail(self, auth_client, sample_template):
        """Test GET /templates/<id>"""
        response = auth_client.get(f'/mcp-templates/{sample_template.id}')
        
        assert response.status_code == 200
    
    def test_template_edit(self, auth_client, sample_template):
        """Test GET /templates/<id>/edit"""
        response = auth_client.get(f'/mcp-templates/{sample_template.id}/edit')
        
        assert response.status_code == 200
    
    def test_template_capabilities(self, auth_client, sample_template):
        """Test GET /templates/<id>/capabilities"""
        response = auth_client.get(f'/mcp-templates/{sample_template.id}/capabilities')
        
        assert response.status_code == 200
