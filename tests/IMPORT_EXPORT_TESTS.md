# Import/Export機能テスト仕様

## 概要

MCPサービスとテンプレートのYAML形式によるエクスポート/インポート機能の包括的なテストスイート。

## テストファイル

### 1. tests/test_mcp_services.py

MCPサービスのYAMLエクスポート/インポートテスト（5件）

#### test_export_mcp_service_yaml

- **目的**: MCPサービスをYAML形式でエクスポート
- **検証項目**:
  - レスポンスが200 OK
  - Content-Typeが`application/x-yaml`
  - Content-Dispositionヘッダーにファイル名
  - YAML構造の正確性（サービス名、識別子、説明）
  - ネストされたアプリとCapabilityのデータ完全性

#### test_import_mcp_service_yaml

- **目的**: YAML形式でMCPサービスをインポート
- **検証項目**:
  - レスポンスが201 Created
  - インポートされたサービスデータの正確性
  - 識別子の衝突がない場合の動作

#### test_import_mcp_service_identifier_collision

- **目的**: 重複する識別子のインポート時の自動リネーム
- **検証項目**:
  - 既存の識別子と衝突時に新しい識別子が生成される
  - `identifier_changed`フラグがtrue
  - 新しい識別子が元の識別子+ランダムサフィックス

#### test_import_invalid_yaml

- **目的**: 無効なYAML形式のエラーハンドリング
- **検証項目**:
  - レスポンスが400 Bad Request
  - エラーメッセージに'YAML'が含まれる

#### test_import_missing_required_fields

- **目的**: 必須フィールド欠如時のエラーハンドリング
- **検証項目**:
  - レスポンスが400 Bad Request
  - エラーメッセージが適切

### 2. tests/test_template_import_export.py

テンプレートのYAMLエクスポート/インポートテスト（11件）

#### TestTemplateExportImport クラス (9件)

##### test_export_template_yaml

- APIテンプレートのYAMLエクスポート
- Capabilityを含む完全なデータ構造の検証

##### test_export_mcp_template_yaml

- MCPタイプのテンプレートエクスポート
- Capabilityなしのデータ検証

##### test_import_template_yaml

- YAML形式でのテンプレートインポート
- 基本フィールドの正確性検証

##### test_import_template_with_capabilities

- Capability付きテンプレートのインポート
- 将来的な機能拡張のドキュメント

##### test_import_invalid_yaml

- 無効なYAMLのエラーハンドリング

##### test_export_import_roundtrip

- エクスポート→インポートのラウンドトリップテスト
- データの同等性検証

##### test_export_builtin_template

- ビルトインテンプレートのエクスポート可能性

##### test_import_creates_custom_template

- インポートされたテンプレートが常に'custom'タイプで作成される検証

##### test_export_filename_contains_template_name

- エクスポートファイル名にテンプレート名が含まれる検証

#### TestTemplateExportFormat クラス (2件)

##### test_yaml_is_human_readable

- YAMLの可読性とフォーマット品質
- フロースタイルではなく通常スタイルの使用

##### test_unicode_in_yaml

- 日本語や絵文字などのUnicode文字の正確な保存
- `allow_unicode=True`の動作確認

### 3. tests/e2e/mcp_templates/test_templates.py

#### test_export_template (更新)

- **変更**: `.json`から`.yaml`/`.yml`への拡張子チェック変更
- ブラウザからのテンプレートエクスポートE2Eテスト

### 4. tests/e2e/mcp_services/test_mcp_services.py

#### TestMcpServiceExportImport クラス (2件)

##### test_export_mcp_service

- MCPサービスのYAMLエクスポートE2Eテスト
- ダウンロードファイル拡張子の検証

##### test_import_mcp_service_modal_opens

- インポートモーダルの表示確認
- ファイル入力のaccept属性検証（`.yaml`, `.yml`）

## テスト実行方法

### 全てのimport/exportテストを実行

```bash
# MCPサービスのimport/exportテスト
pytest tests/test_mcp_services.py::TestMcpServiceAPI -k "export or import" -v

# テンプレートのimport/exportテスト
pytest tests/test_template_import_export.py -v

# 全てのユニットテスト
pytest tests/test_mcp_services.py tests/test_template_import_export.py -v
```

### E2Eテスト

```bash
# テンプレートエクスポートE2E
pytest tests/e2e/mcp_templates/test_templates.py::TestTemplateDetailPage::test_export_template -v

# MCPサービスエクスポート/インポートE2E
pytest tests/e2e/mcp_services/test_mcp_services.py::TestMcpServiceExportImport -v
```

### カバレッジ付き実行

```bash
pytest --cov=app.controllers.api_controller --cov-report=html tests/test_mcp_services.py tests/test_template_import_export.py
```

## テスト結果

### ✅ ユニットテスト: 16/16 PASSED

- MCPサービス: 5/5 PASSED
- テンプレート: 11/11 PASSED

### ✅ E2Eテスト: 3/3 実装済み

- テンプレートエクスポート: YAML対応完了
- MCPサービスエクスポート: 実装済み
- インポートモーダル: YAML受入検証済み

## カバレッジ

### エクスポート機能

- ✅ MCPサービスエクスポート (`/api/mcp-services/<id>/export`)
  - YAML形式生成
  - Content-Type設定
  - ファイル名生成
  - ネストされたデータ構造
- ✅ テンプレートエクスポート (`/api/mcp-templates/<id>/export`)
  - YAML形式生成
  - Capability含む
  - Unicode対応

### インポート機能

- ✅ MCPサービスインポート (`/api/mcp-services/import`)
  - YAMLパース
  - バリデーション
  - 識別子衝突処理
  - エラーハンドリング
- ✅ テンプレートインポート (`/api/mcp-templates/import`)
  - YAMLパース
  - customタイプ作成
  - エラーハンドリング

### エラーハンドリング

- ✅ 無効なYAML形式
- ✅ 必須フィールド欠如
- ✅ 識別子の重複

### フォーマット品質

- ✅ 人間が読みやすいYAML
- ✅ Unicode文字サポート
- ✅ 適切なファイル命名

## 今後の拡張

### 検討事項

1. **Capability付きテンプレートのインポート**
   - 現在はテンプレート本体のみ
   - Capabilityの自動作成機能の追加を検討

2. **バッチインポート**
   - 複数サービス/テンプレートの一括インポート

3. **バージョン管理**
   - エクスポートYAMLへのバージョン情報追加
   - 互換性チェック

4. **変換機能**
   - 既存JSONファイルからYAMLへの変換ツール

## 関連ドキュメント

- [README.md](README.md) - テストスイート全体の概要
- [TEST_COVERAGE.txt](TEST_COVERAGE.txt) - 詳細なカバレッジレポート
