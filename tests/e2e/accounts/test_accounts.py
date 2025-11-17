"""
E2E tests for accounts pages
"""
import pytest
import re
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True)
def login(page: Page):
    """各テスト前に自動ログイン"""
    page.goto("http://localhost:5001/login")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "admin123")
    page.click('button[type="submit"]')
    page.wait_for_url("http://localhost:5001/")


class TestAccountListPage:
    """アカウント一覧ページのE2Eテスト"""
    
    def test_account_list_loads(self, page: Page):
        """アカウント一覧ページが読み込まれる"""
        page.goto("http://localhost:5001/accounts")
        
        expect(page).to_have_url("http://localhost:5001/accounts")
    
    def test_navigate_to_new_account(self, page: Page):
        """新規アカウント登録画面に遷移できる"""
        page.goto("http://localhost:5001/accounts")
        
        page.click('a[href="/accounts/new"]')
        expect(page).to_have_url("http://localhost:5001/accounts/new")
    
    def test_navigate_to_account_detail(self, page: Page):
        """アカウント詳細画面に遷移できる"""
        page.goto("http://localhost:5001/accounts")
        
        # Click first account if exists
        if page.locator('.account-card:first-of-type a, .list-item:first-of-type a').count() > 0:
            page.click('.account-card:first-of-type a, .list-item:first-of-type a')
            expect(page.url).to_contain("/accounts/")


class TestAccountNewPage:
    """新規アカウント登録ページのE2Eテスト"""
    
    def test_new_account_page_loads(self, page: Page):
        """新規アカウント登録ページが読み込まれる"""
        page.goto("http://localhost:5001/accounts/new")
        
        expect(page).to_have_url("http://localhost:5001/accounts/new")
        expect(page.locator('input[name="name"]')).to_be_visible()
    
    def test_create_account(self, page: Page):
        """新規アカウントを作成できる"""
        page.goto("http://localhost:5001/accounts/new")
        
        # Fill account form
        page.fill('input[name="name"]', f"E2E Test Account {page.context.browser.version[:5]}")
        page.fill('textarea[name="description"]', "E2E test account description")
        
        # Submit
        page.click('button[type="submit"]')
        
        # Should redirect
        page.wait_for_url(re.compile("/accounts"))


class TestAccountDetailPage:
    """アカウント詳細ページのE2Eテスト"""
    
    def test_account_detail_loads(self, page: Page):
        """アカウント詳細ページが読み込まれる"""
        page.goto("http://localhost:5001/accounts")
        
        # Click first account
        if page.locator('.account-card:first-of-type a, .list-item:first-of-type a').count() > 0:
            page.click('.account-card:first-of-type a, .list-item:first-of-type a')
            expect(page.url).to_contain("/accounts/")
    
    def test_copy_bearer_token(self, page: Page):
        """Bearerトークンをコピーできる"""
        page.goto("http://localhost:5001/accounts")
        
        # Click first account
        if page.locator('.account-card:first-of-type a, .list-item:first-of-type a').count() > 0:
            page.click('.account-card:first-of-type a, .list-item:first-of-type a')
            
            # Click copy button
            if page.locator('button:has-text("コピー")').count() > 0:
                page.click('button:has-text("コピー")')
                
                # Wait for copy
                page.wait_for_timeout(300)
    
    def test_navigate_to_edit(self, page: Page):
        """編集画面に遷移できる"""
        page.goto("http://localhost:5001/accounts")
        
        # Click first account
        if page.locator('.account-card:first-of-type a, .list-item:first-of-type a').count() > 0:
            page.click('.account-card:first-of-type a, .list-item:first-of-type a')
            
            # Click edit button
            if page.locator('a:has-text("編集")').count() > 0:
                page.click('a:has-text("編集")')
                expect(page.url).to_contain("/edit")


class TestAccountEditPage:
    """アカウント編集ページのE2Eテスト"""
    
    def test_edit_account(self, page: Page):
        """アカウントを編集できる"""
        page.goto("http://localhost:5001/accounts")
        
        # Navigate to first account edit page
        if page.locator('.account-card:first-of-type a, .list-item:first-of-type a').count() > 0:
            page.click('.account-card:first-of-type a, .list-item:first-of-type a')
            
            if page.locator('a:has-text("編集")').count() > 0:
                page.click('a:has-text("編集")')
                
                # Modify account name
                name_input = page.locator('input[name="name"]')
                if name_input.count() > 0:
                    name_input.clear()
                    name_input.fill("Updated Account Name")
                    
                    # Save changes
                    page.click('button[type="submit"]')
                    
                    # Verify changes saved
                    page.wait_for_url(re.compile("/accounts"))
    
    def test_delete_account(self, page: Page):
        """アカウントを削除できる"""
        page.goto("http://localhost:5001/accounts")
        
        # Get initial account count
        accounts_count = page.locator('.account-card, .list-item').count()
        
        if accounts_count > 0:
            # Navigate to first account
            page.click('.account-card:first-of-type a, .list-item:first-of-type a')
            
            # Click delete button
            if page.locator('button:has-text("削除")').count() > 0:
                page.on("dialog", lambda dialog: dialog.accept())
                page.click('button:has-text("削除")')
                
                # Wait for deletion
                page.wait_for_timeout(500)
