"""
Tests for connection log search and filtering (simplified)
"""
import pytest
import json
from datetime import datetime
from app.models.models import db


def test_connection_logs_api_requires_auth(client, db):
    """Test that connection logs API requires authentication"""
    # Try without login
    response = client.get('/api/connection-logs')
    
    # Should redirect to login or return 401
    assert response.status_code in [302, 401]


def test_connection_logs_api_with_auth(client, db):
    """Test that connection logs API works with authentication"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Should return JSON
    response = client.get('/api/connection-logs')
    
    assert response.status_code == 200
    assert response.content_type == 'application/json'


def test_connection_logs_api_search_parameter(client, db):
    """Test that search parameter is accepted"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Search with parameter
    response = client.get('/api/connection-logs?search=test')
    
    assert response.status_code == 200
    data = response.json
    assert 'items' in data


def test_connection_logs_api_empty_search(client, db):
    """Test with empty search parameter"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Empty search
    response = client.get('/api/connection-logs?search=')
    
    assert response.status_code == 200
    data = response.json
    assert 'items' in data


def test_connection_logs_api_returns_json_list(client, db):
    """Test that API returns proper JSON list"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    response = client.get('/api/connection-logs')
    
    assert response.status_code == 200
    data = response.json
    assert 'items' in data
    assert isinstance(data['items'], list)
