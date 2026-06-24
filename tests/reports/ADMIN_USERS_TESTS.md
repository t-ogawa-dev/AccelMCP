# Multi-Admin Account Management Tests

テスト対象: 2026年6月の機能追加「管理画面アカウントの複数管理対応」

## 背景・変更内容

従来、Web管理画面にログインできる管理者アカウント (`AdminCredentials`) は実質1件しか持てなかった
(常に `AdminCredentials.query.first()` で取得していたため)。今回の変更で以下を実現した。

1. `AdminCredentials.username` に unique 制約を追加し、複数アカウントを許容
2. 最初の1件は環境変数 (`ADMIN_USERNAME`/`ADMIN_PASSWORD`) からシードされ、`is_initialized=False` の
   ため初回ログイン時に資格情報変更画面 (`/change-credentials`) へ強制リダイレクトされる
3. 2件目以降は管理画面内の新しい「管理者アカウント管理」メニュー (`/admin-users`) から登録する。
   ここで作成したアカウントは管理者が直接ユーザー名/パスワードを設定するため `is_initialized=True` で
   作成され、強制変更フローを経由しない
4. ログイン処理・`login_required` の強制変更チェック・`/change-credentials` の自己変更処理を、
   「テーブルの先頭行」ではなく「現在ログイン中のユーザー自身」基準に修正

## 変更対象コード

- `app/models/models.py` — `AdminCredentials.username` に `unique=True`
- `db/migrations/versions/c2d3e4f5a6b7_*.py` — unique制約追加マイグレーション
- `app/controllers/auth_controller.py` — ログイン・`login_required` のユーザー名ベース化
- `app/controllers/admin_controller.py` — `/admin-users` 系ルート追加、`/change-credentials` の修正
- `app/controllers/api_controller.py` — `/api/admin-users` (CRUD) 追加、`/api/admin/credentials` の修正
- `app/views/templates/admin_users/` (list/new/detail) + `app/assets/view/admin_users/` (JS)
- `app/assets/i18n.js` — `admin_user_*` 翻訳キー追加

## テストファイル

- `tests/unit/admin/test_admin_users.py` — ユニットテスト (36 tests)
- `tests/e2e/admin_users/test_admin_users.py` — E2Eテスト (Playwright, 8 tests)

## ユニットテストの内訳

### `TestAdminCredentialsModel` (3 tests)

- `test_set_password_and_check_password`
- `test_username_unique_constraint` — 重複ユーザー名で `IntegrityError`
- `test_to_dict_excludes_password_hash`

### `TestMultiAdminLogin` (5 tests)

- `test_login_with_existing_admin`
- `test_login_with_second_admin_alongside_first` — 2つの独立した管理者アカウントが共存できる
- `test_login_wrong_password_for_existing_username`
- `test_login_unknown_username_when_other_admins_exist` — テーブルに行がある場合は env フォールバック禁止
- `test_bootstrap_env_fallback_when_table_empty` — テーブルが空の場合のみ env フォールバック許可

### `TestPerUserForcedCredentialChange` (3 tests)

- `test_pending_admin_redirected_to_change_credentials`
- `test_initialized_admin_not_redirected`
- `test_one_pending_admin_does_not_block_other_initialized_admin` — 回帰防止テスト
  (以前は「テーブルの先頭行」を見ていたため、他人が未初期化だと自分もリダイレクトされる不具合があった)

### `TestSelfServiceCredentialChange` (6 tests) — `POST /api/admin/credentials`

- `test_requires_login`
- `test_updates_own_password`
- `test_updates_own_username_and_syncs_session` — 自分のユーザー名変更後もセッションが有効
- `test_rejects_username_already_used_by_another_admin`
- `test_only_changes_logged_in_users_own_account` — 他人のアカウントに影響しないことを確認
- `test_marks_initialized_after_change`

### `TestAdminUsersListAndCreate` (7 tests) — `GET/POST /api/admin-users`

- `test_list_requires_login`
- `test_list_returns_all_admin_accounts`
- `test_create_admin_user` — `is_initialized=True` で作成されることを確認
- `test_create_admin_user_can_login_immediately` — 強制変更フローを経由しない
- `test_create_rejects_duplicate_username`
- `test_create_rejects_short_password`
- `test_create_rejects_missing_username`

### `TestAdminUserDetailUpdateDelete` (12 tests) — `GET/PUT/DELETE /api/admin-users/<id>`

- `test_get_detail` / `test_get_detail_404_for_unknown_id`
- `test_update_username` / `test_update_rejects_duplicate_username`
- `test_update_password` / `test_update_rejects_short_password`
- `test_delete_succeeds_when_multiple_admins_exist`
- `test_delete_last_remaining_admin_is_forbidden` — 最後の1件はロックアウト防止のため削除不可
- `test_cannot_delete_own_logged_in_account` — 自分自身の削除を防止
- `test_can_delete_other_account_while_logged_in`
- `test_renaming_own_account_via_management_api_syncs_session`
- `test_renaming_another_account_does_not_affect_own_session`

## E2Eテストの内訳 (`tests/e2e/admin_users/test_admin_users.py`)

### `TestAdminUsersListPage` (3 tests)

- `test_admin_users_list_loads`
- `test_navigate_to_new_admin_user`
- `test_dashboard_links_to_admin_users`

### `TestAdminUsersNewPage` (3 tests)

- `test_new_admin_user_page_loads`
- `test_create_admin_user`
- `test_password_mismatch_blocks_submission`

### `TestAdminUserDetailPage` (4 tests)

- `test_navigate_to_detail_from_list`
- `test_edit_username`
- `test_delete_admin_user`
- `test_cannot_delete_own_logged_in_account`

## テスト実行

```bash
# ユニットテストのみ
python -m pytest tests/unit/admin/test_admin_users.py -v

# E2Eテスト (要: 起動済みのサーバー http://localhost:5000)
python -m pytest tests/e2e/admin_users/test_admin_users.py -v
```

## テスト結果

```
tests/unit/admin/test_admin_users.py: 36 passed
tests/unit/ (全体): 326 passed  ※既存290 + 新規36、回帰なし
```

E2Eテストは Playwright + 起動済みサーバーが必要なため、本レポート作成時点では構文チェック
(`python -m py_compile`) と Ruff のみ実施済み。CI/ローカルでサーバー起動後に実行すること。

## カバレッジ

### APIエンドポイント

- ✅ `POST /login` (複数管理者対応)
- ✅ `GET /dashboard` (per-user 強制変更リダイレクト)
- ✅ `POST /api/admin/credentials` (自己サービス変更)
- ✅ `GET/POST /api/admin-users`
- ✅ `GET/PUT/DELETE /api/admin-users/<id>`

### 画面

- ✅ `/admin-users` (一覧)
- ✅ `/admin-users/new` (新規登録)
- ✅ `/admin-users/<id>` (詳細・編集・削除)
- ✅ `/dashboard` (新規カードからの遷移)

### データモデル

- ✅ `AdminCredentials` (unique username, 複数行)
