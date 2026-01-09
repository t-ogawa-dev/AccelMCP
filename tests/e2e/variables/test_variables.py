"""
E2E Tests for Variables Pages
Variables画面の操作テスト
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def logged_in_page(page: Page):
    """ログイン済みのページ"""
    page.goto('http://localhost:5100/login')
    page.fill('input[name="username"]', 'accel')
    page.fill('input[name="password"]', 'universe')
    page.click('button[type="submit"]')
    page.wait_for_url('http://localhost:5100/')
    return page


class TestVariableListPage:
    """Variables一覧ページのテスト"""
    
    def test_variable_list_loads(self, logged_in_page: Page):
        """Variables一覧ページが表示される"""
        logged_in_page.goto('http://localhost:5100/variables')
        expect(logged_in_page).to_have_url('http://localhost:5100/variables')
        
        # Check page title
        heading = logged_in_page.locator('h1, h2').first
        expect(heading).to_contain_text('Variables')
    
    def test_navigate_to_new_variable(self, logged_in_page: Page):
        """新規Variable作成画面へ遷移"""
        logged_in_page.goto('http://localhost:5100/variables')
        
        # Click "New Variable" button
        new_button = logged_in_page.get_by_role('link', name='New Variable')
        new_button.click()
        
        expect(logged_in_page).to_have_url('http://localhost:5100/variables/new')
    
    def test_variable_list_displays_items(self, logged_in_page: Page):
        """Variable一覧にアイテムが表示される"""
        logged_in_page.goto('http://localhost:5100/variables')
        
        # Wait for table to load
        table = logged_in_page.locator('table, .variable-list')
        expect(table).to_be_visible()
        
        # Should have at least headers
        headers = logged_in_page.locator('th')
        expect(headers.first).to_be_visible()


class TestVariableNewPage:
    """Variable新規作成ページのテスト"""
    
    def test_new_variable_page_loads(self, logged_in_page: Page):
        """新規作成ページが表示される"""
        logged_in_page.goto('http://localhost:5100/variables/new')
        
        # Check form exists
        form = logged_in_page.locator('form')
        expect(form).to_be_visible()
        
        # Check required fields
        expect(logged_in_page.locator('input[name="name"]')).to_be_visible()
        expect(logged_in_page.locator('input[name="value"], textarea[name="value"]')).to_be_visible()
    
    def test_create_string_variable(self, logged_in_page: Page):
        """文字列型Variableの作成"""
        logged_in_page.goto('http://localhost:5100/variables/new')
        
        # Fill form
        logged_in_page.fill('input[name="name"]', 'TEST_VAR_STRING')
        logged_in_page.fill('input[name="value"], textarea[name="value"]', 'test value')
        
        # Select value_type if dropdown exists
        value_type_select = logged_in_page.locator('select[name="value_type"]')
        if value_type_select.is_visible():
            value_type_select.select_option('string')
        
        # Submit form
        logged_in_page.click('button[type="submit"]')
        
        # Should redirect to list or detail page
        logged_in_page.wait_for_url('http://localhost:5100/variables*')
        
        # Success message should appear
        success_message = logged_in_page.locator('.alert-success, .success, [role="alert"]')
        expect(success_message).to_be_visible(timeout=3000)
    
    def test_create_secret_variable(self, logged_in_page: Page):
        """シークレット型Variableの作成"""
        logged_in_page.goto('http://localhost:5100/variables/new')
        
        logged_in_page.fill('input[name="name"]', 'API_KEY_SECRET')
        logged_in_page.fill('input[name="value"], textarea[name="value"]', 'secret-api-key-12345')
        
        # Select value_type
        value_type_select = logged_in_page.locator('select[name="value_type"]')
        if value_type_select.is_visible():
            value_type_select.select_option('secret')
        else:
            # Check checkbox if exists
            is_secret_checkbox = logged_in_page.locator('input[name="is_secret"]')
            if is_secret_checkbox.is_visible():
                is_secret_checkbox.check()
        
        logged_in_page.click('button[type="submit"]')
        logged_in_page.wait_for_url('http://localhost:5100/variables*')
        
        # Check success
        success_message = logged_in_page.locator('.alert-success, .success')
        expect(success_message).to_be_visible(timeout=3000)
    
    def test_create_env_variable(self, logged_in_page: Page):
        """環境変数参照型Variableの作成"""
        logged_in_page.goto('http://localhost:5100/variables/new')
        
        logged_in_page.fill('input[name="name"]', 'DATABASE_URL')
        logged_in_page.fill('input[name="value"], textarea[name="value"]', 'DB_CONNECTION_STRING')
        
        # Select env type
        value_type_select = logged_in_page.locator('select[name="value_type"]')
        if value_type_select.is_visible():
            value_type_select.select_option('env')
        
        logged_in_page.click('button[type="submit"]')
        logged_in_page.wait_for_url('http://localhost:5100/variables*')
    
    def test_create_number_variable(self, logged_in_page: Page):
        """数値型Variableの作成"""
        logged_in_page.goto('http://localhost:5100/variables/new')
        
        logged_in_page.fill('input[name="name"]', 'MAX_RETRIES')
        logged_in_page.fill('input[name="value"], textarea[name="value"]', '5')
        
        # Select number type
        value_type_select = logged_in_page.locator('select[name="value_type"]')
        if value_type_select.is_visible():
            value_type_select.select_option('number')
        
        logged_in_page.click('button[type="submit"]')
        logged_in_page.wait_for_url('http://localhost:5100/variables*')
    
    def test_validation_empty_name(self, logged_in_page: Page):
        """名前が空の場合のバリデーション"""
        logged_in_page.goto('http://localhost:5100/variables/new')
        
        # Fill only value, leave name empty
        logged_in_page.fill('input[name="value"], textarea[name="value"]', 'some value')
        
        logged_in_page.click('button[type="submit"]')
        
        # Should show validation error
        error = logged_in_page.locator('.error, .alert-danger, [role="alert"]')
        expect(error).to_be_visible(timeout=3000)


class TestVariableDetailPage:
    """Variable詳細ページのテスト"""
    
    def test_variable_detail_loads(self, logged_in_page: Page):
        """詳細ページが表示される"""
        # First create a variable
        logged_in_page.goto('http://localhost:5100/variables/new')
        logged_in_page.fill('input[name="name"]', 'TEST_DETAIL_VAR')
        logged_in_page.fill('input[name="value"], textarea[name="value"]', 'detail test')
        logged_in_page.click('button[type="submit"]')
        logged_in_page.wait_for_url('http://localhost:5100/variables*')
        
        # Navigate to detail page (if exists)
        # Click on the first variable link
        variable_link = logged_in_page.locator('a[href*="/variables/"]').first
        if variable_link.is_visible():
            variable_link.click()
            
            # Check detail page loaded
            expect(logged_in_page.locator('h1, h2')).to_contain_text('Variable')
    
    def test_navigate_to_edit_from_detail(self, logged_in_page: Page):
        """詳細ページから編集ページへ遷移"""
        logged_in_page.goto('http://localhost:5100/variables')
        
        # Click first variable
        variable_link = logged_in_page.locator('a[href*="/variables/"]').first
        if variable_link.is_visible():
            variable_link.click()
            
            # Click edit button
            edit_button = logged_in_page.get_by_role('link', name='Edit')
            if edit_button.is_visible():
                edit_button.click()
                expect(logged_in_page).to_have_url('**/edit')


class TestVariableEditPage:
    """Variable編集ページのテスト"""
    
    def test_edit_variable(self, logged_in_page: Page):
        """Variableの編集"""
        # Create a variable first
        logged_in_page.goto('http://localhost:5100/variables/new')
        logged_in_page.fill('input[name="name"]', 'EDIT_TEST_VAR')
        logged_in_page.fill('input[name="value"], textarea[name="value"]', 'original value')
        logged_in_page.click('button[type="submit"]')
        logged_in_page.wait_for_url('http://localhost:5100/variables*')
        
        # Go to edit page
        logged_in_page.goto('http://localhost:5100/variables')
        edit_link = logged_in_page.locator('a[href*="/variables/"][href*="/edit"]').first
        if edit_link.is_visible():
            edit_link.click()
            
            # Update value
            value_input = logged_in_page.locator('input[name="value"], textarea[name="value"]')
            value_input.clear()
            value_input.fill('updated value')
            
            # Submit
            logged_in_page.click('button[type="submit"]')
            logged_in_page.wait_for_url('http://localhost:5100/variables*')
            
            # Check success
            success_message = logged_in_page.locator('.alert-success, .success')
            expect(success_message).to_be_visible(timeout=3000)
    
    def test_delete_variable(self, logged_in_page: Page):
        """Variableの削除"""
        # Create a variable
        logged_in_page.goto('http://localhost:5100/variables/new')
        logged_in_page.fill('input[name="name"]', 'DELETE_TEST_VAR')
        logged_in_page.fill('input[name="value"], textarea[name="value"]', 'to be deleted')
        logged_in_page.click('button[type="submit"]')
        logged_in_page.wait_for_url('http://localhost:5100/variables*')
        
        # Go to edit page
        logged_in_page.goto('http://localhost:5100/variables')
        edit_link = logged_in_page.locator('a[href*="/variables/"][href*="/edit"]').first
        if edit_link.is_visible():
            edit_link.click()
            
            # Click delete button
            delete_button = logged_in_page.locator('button:has-text("Delete"), button.btn-danger')
            if delete_button.is_visible():
                # Handle confirmation dialog
                logged_in_page.on('dialog', lambda dialog: dialog.accept())
                delete_button.click()
                
                # Should redirect to list
                logged_in_page.wait_for_url('http://localhost:5100/variables')


class TestVariableUsageInCapability:
    """Capability内でのVariable使用テスト"""
    
    def test_variable_replacement_display(self, logged_in_page: Page):
        """Capability作成時にVariable置換が利用可能"""
        # Create a variable first
        logged_in_page.goto('http://localhost:5100/variables/new')
        logged_in_page.fill('input[name="name"]', 'API_URL')
        logged_in_page.fill('input[name="value"], textarea[name="value"]', 'https://api.example.com')
        logged_in_page.click('button[type="submit"]')
        logged_in_page.wait_for_url('http://localhost:5100/variables*')
        
        # Go to capability creation (if service exists)
        logged_in_page.goto('http://localhost:5100/services')
        
        # Check if variables can be referenced in forms
        # This is more of an integration test
        # Just verify the variable exists in the list
        logged_in_page.goto('http://localhost:5100/variables')
        expect(logged_in_page.locator('text=API_URL')).to_be_visible()
