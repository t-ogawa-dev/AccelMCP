"""
E2E tests for dashboard page
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.skip(reason="Authentication context isolation issue in test environment")
class TestDashboardPage:
    """ダッシュボードページのE2Eテスト"""
    
    def test_dashboard_loads(self, authenticated_page: Page, base_url):
        """ダッシュボードが読み込まれる"""
        authenticated_page.goto(f"{base_url}/dashboard")
        
        expect(authenticated_page).to_have_url(f"{base_url}/dashboard")
    
    def test_service_card_link(self, authenticated_page: Page, base_url):
        """サービス管理カードのリンクが動作する"""
        authenticated_page.goto(f"{base_url}/dashboard")
        
        authenticated_page.click('a[href="/services"]')
        expect(authenticated_page).to_have_url(f"{base_url}/services")
    
    def test_account_card_link(self, authenticated_page: Page, base_url):
        """アカウント管理カードのリンクが動作する"""
        authenticated_page.goto(f"{base_url}/dashboard")
        
        authenticated_page.click('a[href="/accounts"]')
        expect(authenticated_page).to_have_url(f"{base_url}/accounts")
    
    def test_template_card_link(self, authenticated_page: Page, base_url):
        """テンプレート管理カードのリンクが動作する"""
        authenticated_page.goto(f"{base_url}/dashboard")
        
        authenticated_page.click('a[href="/mcp-templates"]')
        expect(authenticated_page).to_have_url(f"{base_url}/mcp-templates")
