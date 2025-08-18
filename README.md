# staff-db

## ディレクトリ構成

```
project/
├── compose.yaml                 # 本番用（ベース定義）
├── compose.override.yaml        # 開発用オーバーライド
├── frontend/
│   ├── Dockerfile               # 本番用
│   ├── Dockerfile.dev           # 開発用
│   └── nginx.conf               # 本番用
│   └── nginx.dev.conf           # 開発用
├── backend/
│   └── Dockerfile
```



## 概念図

### 開発モード

```
                   ┌─────────────────┐
   Browser         │     Nginx       │  (公開:80)
 http://localhost  │ (reverse proxy) │
──────────────────▶│  / → frontend   │──▶ React Dev Server (3000)
                   │ /api → backend  │──▶ Flask (5000)
                   └─────────────────┘
                                │
                                ▼
                           MySQL (3306)

【外部からアクセス可能】
- Nginx (80) のみ

【コンテナ間通信】
- Nginx → frontend:3000
- Nginx → backend:5000
- backend → db:3306
```

### 本番モード

```
                   ┌──────────────────┐
   Browser         │  Nginx(frontend) │  (公開:80)
 http://localhost  │------------------│
──────────────────▶│  / → React build │ (静的配信)
                   │ /api → backend   │──▶ Flask (5000)
                   └──────────────────┘
                                │
                                ▼
                           MySQL (3306)

【外部からアクセス可能】
- Nginx (80) のみ

【コンテナ間通信】
- Nginx → backend:5000
- backend → db:3306
```



## 疎通確認

### 開発モード（compose.yaml + compose.override.yaml）

```bash
docker compose -f compose.yaml -f compose.override.yaml up --build
```

チェック項目

1. Nginx が立ち上がるか
   - ブラウザで http://localhost/ を開く
   - React Dev Server のページが表示されるか確認
   - ページを編集して保存するとホットリロードされるか確認
2. フロントエンド → バックエンド（API）通信
   - http://localhost/api/health のような簡単なエンドポイントを Flask に実装して確認
     200 OK が返ってくれば疎通成功
3. バックエンド → DB 通信
   - Flask 側から MySQL に接続してクエリを実行できるか確認
     例：SELECT 1; を叩いて正常応答をログで確認
4. ネットワークの制限確認
   - http://localhost:5000 → アクセスできないことを確認（外部公開していないため）
   - http://localhost:3306 → アクセスできないことを確認

### 本番モード（compose.yaml 単体）

```bash
docker compose up --build
```

1. Nginx が立ち上がるか
   - ブラウザで http://localhost/ を開く
   - React ビルド済みの静的ページが表示されることを確認
2. フロントエンド → バックエンド（API）通信
   - ブラウザまたは curl で http://localhost/api/health
     200 OK が返ってくれば疎通成功
3. バックエンド → DB 通信
   - Flask 側から MySQL に接続してテーブル一覧を取得できるか確認
   - アプリのログでエラーが出ていないかチェック
4. ネットワークの制限確認
   - http://localhost:5000 → アクセスできないことを確認
   - http://localhost:3306 → アクセスできないことを確認