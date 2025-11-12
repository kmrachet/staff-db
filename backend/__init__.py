from flask import Flask, jsonify
from .config import config
from .extensions import db, migrate

def create_app(config_name='default'):
    """アプリケーションファクトリ"""
    app = Flask(__name__)
    
    # 1. 設定の読み込み
    app.config.from_object(config[config_name])
    
    # 2. 拡張機能の初期化
    db.init_app(app)
    migrate.init_app(app, db)

    # 3. モデルのインポート（Migrateが認識するために必要）
    # このインポートは db.init_app の後に行う必要があります。
    from . import models 

    # 4. ブループリント（APIエンドポイント）の登録
    
    # (例) 既存のヘルスチェックを登録
    @app.route("/health")
    def health():
        return jsonify(status="ok"), 200

    # 5. カスタムCLIコマンドの登録
    # create_app の中でインポートします
    from . import commands 
    commands.register_commands(app)

    return app