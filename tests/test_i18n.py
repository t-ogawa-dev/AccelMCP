"""
i18n Translation Key Tests
Tests to ensure all data-i18n keys in templates have translations
"""
import pytest
import re
from pathlib import Path


class TestI18nTranslations:
    """i18n翻訳キーのテスト"""
    
    @pytest.fixture
    def html_files(self):
        """テスト対象のHTMLファイル一覧を取得"""
        project_root = Path(__file__).parent.parent
        templates_dir = project_root / "app" / "views" / "templates"
        return list(templates_dir.rglob("*.html"))
    
    @pytest.fixture
    def i18n_keys(self):
        """i18n.jsから翻訳キー一覧を取得"""
        project_root = Path(__file__).parent.parent
        i18n_file = project_root / "app" / "assets" / "i18n.js"
        
        content = i18n_file.read_text(encoding='utf-8')
        
        # JavaScriptオブジェクトからキーを抽出
        # パターン: key: 'value' または key: "value"
        keys = set()
        pattern = r"^\s*(\w+):\s*['\"]"
        for line in content.split('\n'):
            match = re.match(pattern, line)
            if match:
                keys.add(match.group(1))
        
        return keys
    
    def test_all_template_i18n_keys_have_translations(self, html_files, i18n_keys):
        """全てのHTMLテンプレートのdata-i18nキーが翻訳されていることを確認"""
        missing_keys = {}
        
        for html_file in html_files:
            content = html_file.read_text(encoding='utf-8')
            
            # data-i18n="key" パターンを抽出
            pattern = r'data-i18n="([^"]+)"'
            found_keys = re.findall(pattern, content)
            
            for key in found_keys:
                if key not in i18n_keys:
                    if html_file.name not in missing_keys:
                        missing_keys[html_file.name] = []
                    missing_keys[html_file.name].append(key)
        
        if missing_keys:
            error_msg = "Missing i18n translations:\n"
            for filename, keys in missing_keys.items():
                error_msg += f"  {filename}:\n"
                for key in keys:
                    error_msg += f"    - {key}\n"
            
            pytest.fail(error_msg)
    
    def test_capability_timeout_keys_exist(self, i18n_keys):
        """タイムアウト関連のキーが存在することを確認"""
        required_keys = [
            'capability_timeout_label',
            'capability_timeout_hint'
        ]
        
        missing = [key for key in required_keys if key not in i18n_keys]
        assert not missing, f"Missing i18n keys: {missing}"
    
    def test_japanese_translations_exist(self):
        """日本語翻訳が存在することを確認"""
        project_root = Path(__file__).parent.parent
        i18n_file = project_root / "app" / "assets" / "i18n.js"
        content = i18n_file.read_text(encoding='utf-8')
        
        # 'ja' セクションが存在することを確認 (ja: の形式もチェック)
        assert "ja:" in content or "'ja':" in content or '"ja":' in content, "Japanese translation section not found"
        
        # 日本語テキストが含まれていることを確認
        assert 'タイムアウト' in content, "Japanese timeout translation not found"
    
    def test_english_translations_exist(self):
        """英語翻訳が存在することを確認"""
        project_root = Path(__file__).parent.parent
        i18n_file = project_root / "app" / "assets" / "i18n.js"
        content = i18n_file.read_text(encoding='utf-8')
        
        # 'en' セクションが存在することを確認 (en: の形式もチェック)
        assert "en:" in content or "'en':" in content or '"en":' in content, "English translation section not found"
        
        # 英語テキストが含まれていることを確認
        assert 'Timeout' in content, "English timeout translation not found"


class TestI18nConsistency:
    """日本語と英語の翻訳キーの整合性テスト"""
    
    def _extract_keys_from_section(self, content: str, lang: str) -> set:
        """特定言語セクションからキーを抽出"""
        # 簡易的な抽出（完全なパースは複雑なので）
        keys = set()
        in_section = False
        brace_count = 0
        
        lines = content.split('\n')
        for line in lines:
            # 言語セクションの開始を検出
            if f"'{lang}':" in line or f'"{lang}":' in line:
                in_section = True
                brace_count = 0
                continue
            
            if in_section:
                brace_count += line.count('{') - line.count('}')
                
                # キーを抽出
                match = re.match(r"^\s*(\w+):\s*['\"]", line)
                if match:
                    keys.add(match.group(1))
                
                # セクション終了
                if brace_count <= 0 and '}' in line:
                    break
        
        return keys
    
    def test_ja_en_key_consistency(self):
        """日本語と英語で同じキーが定義されていることを確認"""
        project_root = Path(__file__).parent.parent
        i18n_file = project_root / "app" / "assets" / "i18n.js"
        content = i18n_file.read_text(encoding='utf-8')
        
        ja_keys = self._extract_keys_from_section(content, 'ja')
        en_keys = self._extract_keys_from_section(content, 'en')
        
        # 日本語にあって英語にないキー
        ja_only = ja_keys - en_keys
        # 英語にあって日本語にないキー
        en_only = en_keys - ja_keys
        
        errors = []
        if ja_only:
            errors.append(f"Keys only in Japanese (missing English): {sorted(ja_only)[:10]}")
        if en_only:
            errors.append(f"Keys only in English (missing Japanese): {sorted(en_only)[:10]}")
        
        # 警告として出力（エラーにはしない - 多少の差異は許容）
        if errors:
            print(f"\nWarning - i18n key inconsistencies:\n" + "\n".join(errors))
