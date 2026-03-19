[English](en/MIGRATION.en.md) | 日本語

# Database Migration Guide

AccelMCP は Flask-Migrate (Alembic)を使用してデータベースマイグレーションを管理しています。

マイグレーションファイルは`db/migrations/`ディレクトリに配置されます。

## ディレクトリ構成

```
db/
├── migrate.py              # マイグレーション管理スクリプト
└── migrations/             # Alembicポイント
    ├── alembic.ini          # Alembic設定
    ├── env.py               # マイグレーション環境設定
    ├── script.py.mako       # マイグレーションテンプレート
    └── versions/            # マイグレーションファイル
```

## セットアップ

### 初回セットアップ

1. **依存関係のインストール**

   ```bash
   pip install -r requirements.txt
   ```

2. **マイグレーションの適用**
   ```bash
   python db/migrate.py upgrade
   ```

## マイグレーションコマンド

### 新しいマイグレーションを作成

```bash
python db/migrate.py migrate "Description of changes"
```

### マイグレーションを適用（アップグレード）

```bash
python db/migrate.py upgrade
```

### マイグレーションをロールバック（ダウングレード）

```bash
python db/migrate.py downgrade
```

### 現在のリビジョンを確認

```bash
python db/migrate.py current
```

### マイグレーション履歴を表示

```bash
python db/migrate.py history
```

## Docker での使用

### 初回起動

```bash
docker compose up -d
```

コンテナ起動時に自動的に`python db/migrate.py upgrade`が実行されます。

### 新しいマイグレーションを作成（ローカル環境で）

```bash
# ローカルでモデルを変更後
python db/migrate.py migrate "Add new field"

# マイグレーションファイルを確認
git add db/migrations/versions/
git commit -m "Add migration: Add new field"

# コンテナを再起動してマイグレーション適用
docker compose restart web
```

### マイグレーションのロールバック

```bash
docker compose exec web python db/migrate.py downgrade
```

## サービステンプレートの追加

サービステンプレートは`app/utils/template_loader.py`の`BUILTIN_TEMPLATES`で管理されます。

### 新しいテンプレートの追加手順

1. **`app/utils/template_loader.py`を編集**

   `BUILTIN_TEMPLATES`リストに新しいテンプレートを追加：

   ```python
   BUILTIN_TEMPLATES = [
       # ... 既存のテンプレート ...
       {
           'name': 'MS Office API',
           'service_type': 'api',
           'description': 'Microsoft Office API for document management',
           'icon': '📄',
           'category': 'Productivity',
           'capabilities': [
               {
                   'name': 'list_documents',
                   'capability_type': 'tool',
                   'url': 'https://graph.microsoft.com/v1.0/me/drive/root/children',
                   'headers': {'Authorization': 'Bearer YOUR_MS_TOKEN'},
                   'body_params': {},
                   'description': 'List all documents'
               }
           ]
       }
   ]
   ```

2. **マイグレーションを作成**

   ```bash
   python db/migrate.py migrate "Add MS Office template"
   ```

3. **マイグレーションファイルを編集（必要に応じて）**

   生成されたマイグレーションファイルにデータロード処理を追加：

   ```python
   from app.utils.template_loader import load_service_templates

   def upgrade():
       # テンプレートをロード
       load_service_templates()

   def downgrade():
       # ロールバック処理
       op.execute("""
           DELETE FROM mcp_capability_templates
           WHERE service_template_id IN (
               SELECT id FROM mcp_service_templates
               WHERE name = 'MS Office API'
           )
       """)
       op.execute("""
           DELETE FROM mcp_service_templates
           WHERE name = 'MS Office API'
       """)
   ```

4. **マイグレーションを適用**

   ```bash
   python db/migrate.py upgrade
   ```

## トラブルシューティング

### データベースをリセットしたい

```bash
docker compose down -v  # ボリュームを削除
docker compose up -d    # 再起動してマイグレーション適用
```

### マイグレーション履歴が壊れた場合

```bash
# データベースに直接接続
docker compose exec db mysql -u mcpuser -p mcpdb

# alembic_versionテーブルを確認
SELECT * FROM alembic_version;

# 必要に応じてリセット
DELETE FROM alembic_version;
```

### マイグレーションファイルの競合

```bash
# マイグレーションを統合
python db/migrate.py merge heads -m "Merge migrations"
```

## ベストプラクティス

1. **モデル変更後は必ずマイグレーションを作成**
   - `app/models/models.py`を変更したら`python db/migrate.py migrate`を実行

2. **マイグレーションファイルをレビュー**
   - 自動生成されたマイグレーションファイルを確認
   - 必要に応じて手動で調整

3. **本番環境でのマイグレーション**
   - 必ずバックアップを取得
   - ステージング環境でテスト
   - ダウンタイムを考慮

4. **チーム開発**
   - マイグレーションファイルは Git で管理
   - プルリクエストに含める
   - マージ後は全員が upgrade を実行
