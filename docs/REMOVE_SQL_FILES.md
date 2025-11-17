# データベースマイグレーション - SQL から Python への移行完了

## 変更内容

AccelMCP のデータベース管理を、SQL ファイルベースから Flask-Migrate（Alembic）を使用した Python ベースのマイグレーション管理に移行しました。

### マイグレーションディレクトリ構成

マイグレーションファイルは**テーブルグループごとに分割**され、`db/migrate/`配下に配置されます：

```
db/
└── migrate/                    # マイグレーションディレクトリ
    ├── alembic.ini
    ├── env.py
    ├── script.py.mako
    └── versions/              # バージョン管理されたマイグレーションファイル
        ├── 001_core_tables.py              # 基本テーブル
        ├── 002_template_tables.py          # テンプレートテーブル
        └── 003_builtin_templates.py        # ビルトインデータ
```

## 削除済みのファイル

以下の SQL ファイルは、マイグレーションシステムに統合されたため、**既に削除済み**です：

```
db/  ❌ ディレクトリごと削除済み
```

元々あったファイル：

- `db/init.sql`
- `db/migration_add_notes.sql`
- `db/migration_add_templates.sql`
- `db/migration_add_capability_enabled.sql`
- `db/migration_rename_template_tables.sql`
- `db/service_templates/` （ディレクトリと全 SQL ファイル）

## 新しい管理方法

### スキーマ定義

- **場所**: `app/models/models.py`
- **方法**: SQLAlchemy モデルで定義
- **マイグレーション**: Flask-Migrate が自動生成

### テンプレートデータ

- **場所**: `app/utils/template_loader.py`の`BUILTIN_TEMPLATES`
- **形式**: Python 辞書
- **ロード**: マイグレーション実行時に自動投入

## 使用方法

### 初回セットアップ

```bash
# 1. 自動セットアップ
python setup_migrations.py

# 2. マイグレーション適用
python migrate.py upgrade
```

### 新しいテンプレート追加

```python
# app/utils/template_loader.pyを編集
BUILTIN_TEMPLATES = [
    # ... 既存のテンプレート ...
    {
        'name': 'New Service',
        'service_type': 'api',
        'description': 'Service description',
        'icon': '🔧',
        'category': 'Category',
        'capabilities': [...]
    }
]
```

```bash
# マイグレーション作成と適用
python migrate.py migrate "Add new service template"
python migrate.py upgrade
```

### スキーマ変更

```python
# 1. app/models/models.pyを編集
class MyModel(db.Model):
    new_field = db.Column(db.String(100))  # 新しいフィールド追加

# 2. マイグレーション生成
python migrate.py migrate "Add new field"

# 3. 適用
python migrate.py upgrade
```

## メリット

### SQL ファイル方式の問題点

- ❌ マイグレーション履歴がない
- ❌ ロールバックができない
- ❌ 既存 DB への適用が困難
- ❌ SQL とモデル定義が二重管理
- ❌ チーム開発で同期が難しい

### Flask-Migrate 方式のメリット

- ✅ 変更履歴を完全に追跡
- ✅ ロールバック可能
- ✅ 既存 DB に段階的に適用
- ✅ モデルが真実の情報源（Single Source of Truth）
- ✅ Git でマイグレーションを VoC 管理
- ✅ チーム開発で同期しやすい
- ✅ テストが容易

## Docker 環境

`compose.yaml`は自動的にマイグレーションを実行するように設定済み：

```yaml
command: >
  sh -c "
    python migrate.py upgrade &&
    python run.py
  "
```

コンテナ起動時に自動でマイグレーションが適用されます。

## 削除コマンド

SQL ファイルを削除する場合：

```bash
# 個別ファイルを削除
rm db/init.sql
rm db/migration_*.sql

# service_templatesディレクトリを削除
rm -rf db/service_templates/

# dbディレクトリが空なら削除
rmdir db/
```

または、Git で管理している場合：

```bash
git rm db/init.sql
git rm db/migration_*.sql
git rm -r db/service_templates/
git commit -m "Remove legacy SQL files, migrate to Flask-Migrate"
```

## 参考ドキュメント

- [docs/MIGRATION.md](./MIGRATION.md) - マイグレーション詳細ガイド
- [docs/SQL_TO_MIGRATE.md](./SQL_TO_MIGRATE.md) - 移行手順の詳細
