"""
E2E Test Configuration
"""
import pytest
import os


@pytest.fixture(scope="session")
def base_url():
    """Base URL for E2E tests"""
    # When running in Docker, use service name 'web'
    # When running locally, use localhost with configurable port
    if os.getenv('DOCKER_ENV'):
        return "http://web:5000"
    port = os.getenv('FLASK_PORT', os.getenv('PORT', '5000'))
    return f"http://localhost:{port}"


@pytest.fixture
def authenticated_page(page, base_url):
    """Pre-authenticated page fixture"""
    page.goto(f"{base_url}/login")
    page.wait_for_selector('input[name="username"]')
    page.fill('input[name="username"]', 'admin')
    page.fill('input[name="password"]', 'admin123')
    
    # Use expect_navigation like test_login.py
    with page.expect_navigation():
        page.locator('button[type="submit"]').click()
    
    page.wait_for_load_state('networkidle')
    
    # Verify we're authenticated (not on login page anymore)
    if '/login' in page.url:
        raise Exception(f"Authentication failed - still on login page: {page.url}")
    
    return page
