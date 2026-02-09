# Prompt and Resource Capability Tests

テスト対象: 2026年2月9日の修正/変更内容に対するテストスイート

## テストファイル

- `test_prompt_and_resource_capability.py` - Prompt/Resource機能の包括的なテスト

## 対象機能

### 1. Promptタイプのcapability作成でResourceレコードを作成しない

- **テストクラス**: `TestPromptCapabilityCreation`
- **目的**: promptタイプのcapabilityがResourceテーブルにレコードを作成しないことを確認
- **対象コード**: `app/controllers/api_controller.py` (lines 636, 716)

**テストケース**:

- `test_create_prompt_capability_without_resource_record` - prompt作成時にResourceが作成されない
- `test_create_tool_capability_without_resource_record` - tool作成時にResourceが作成されない

### 2. Resourceタイプのcapability作成でResourceレコードを作成

- **テストクラス**: `TestResourceCapabilityCreation`
- **目的**: resourceタイプのcapabilityのみがResourceレコードを作成することを確認
- **対象コード**: `app/controllers/api_controller.py` (capability作成/更新ロジック)

**テストケース**:

- `test_create_resource_capability_with_new_resource` - 新規リソース作成時にResourceレコードが作成される
- `test_create_resource_capability_with_existing_resource` - 既存リソース参照時に新規Resourceは作成されない

### 3. Promptタイプのcapability更新でResourceレコードを作成しない

- **テストクラス**: `TestPromptCapabilityUpdate`
- **目的**: prompt更新時にResourceレコードが作成されないことを確認

**テストケース**:

- `test_update_prompt_capability_without_resource_record` - prompt更新時にResourceが作成されない
- `test_update_resource_capability_creates_resource_record` - resource更新時にResourceが作成される

### 4. prompts/getエンドポイントのテンプレート取得

- **テストクラス**: `TestPromptsGetEndpoint`
- **目的**: MCPプロトコルのprompts/getエンドポイントが正しくテンプレートを返すことを確認
- **対象コード**: `app/services/mcp_handler.py` `_handle_prompts_get` (lines 1047-1096)

**テストケース**:

- `test_prompts_get_with_template_content` - template_contentフィールドから直接取得
- `test_prompts_get_with_resource_fallback` - template_contentがnullの場合、global_resource_idからResource tableにフォールバック

### 5. Capability一覧APIのレスポンス

- **テストクラス**: `TestCapabilityListAPI`
- **目的**: capability一覧APIが各タイプに応じて正しいデータを返すことを確認
- **対象コード**: `app/assets/view/services/capabilities.js` (URL表示ロジック)

**テストケース**:

- `test_capability_list_includes_all_types` - 全タイプのcapabilityが正しく返される
- `test_capability_detail_returns_correct_fields_for_prompt` - prompt詳細が正しいフィールドを含む
- `test_capability_detail_returns_correct_fields_for_resource` - resource詳細が正しいフィールドを含む

## テスト実行

### 全テスト実行

```bash
python -m pytest tests/test_prompt_and_resource_capability.py -v
```

### 特定クラスのみ実行

```bash
python -m pytest tests/test_prompt_and_resource_capability.py::TestPromptCapabilityCreation -v
```

### 特定テストケースのみ実行

```bash
python -m pytest tests/test_prompt_and_resource_capability.py::TestPromptsGetEndpoint::test_prompts_get_with_template_content -v
```

## テスト結果

```
11 tests collected
11 passed
```

## 主要な修正内容

### 1. Prompt/Resource分離 (api_controller.py)

```python
# Resourceタイプの場合のみResourceレコード作成
if capability_type == 'resource' and not global_resource_id and (resource_uri or template_content):
    # Create Resource record
```

### 2. prompts/get Resource fallback (mcp_handler.py)

```python
# template_contentがnullの場合、Resourceテーブルから取得
if not template_content and capability.global_resource_id:
    resource = Resource.query.get(capability.global_resource_id)
    if resource:
        template_content = resource.content
```

### 3. UI表示制御 (capabilities.js, edit.js)

- tool/mcp_toolタイプのみURL表示
- promptタイプは専用フィールドを表示、toolフィールドを非表示

## Fixtures

### `sample_mcp_service_for_prompt`

- テスト用MCPサービス (path-based routing)

### `sample_service_for_prompt`

- テスト用Service (mcp_builtin)

### `sample_global_resource`

- テスト用グローバルResource (テンプレート変数含む)

### `sample_connection_account`

- MCP認証用ConnectionAccount (Bearer token)

## カバレッジ

### APIエンドポイント

- ✅ POST `/api/apps/{id}/capabilities` (prompt作成)
- ✅ POST `/api/apps/{id}/capabilities` (resource作成)
- ✅ PUT `/api/capabilities/{id}` (prompt更新)
- ✅ PUT `/api/capabilities/{id}` (resource更新)
- ✅ GET `/api/apps/{id}/capabilities` (一覧取得)
- ✅ GET `/api/capabilities/{id}` (詳細取得)

### MCPプロトコル

- ✅ POST `/{path}/mcp` with `prompts/get` method (template_content)
- ✅ POST `/{path}/mcp` with `prompts/get` method (Resource fallback)

### データモデル

- ✅ Capability (prompt, resource, tool, mcp_tool)
- ✅ Resource (global resources)
- ✅ McpService (path-based routing)
- ✅ Service (mcp_builtin)
- ✅ ConnectionAccount (Bearer authentication)
