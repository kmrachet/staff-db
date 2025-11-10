import os
from . import create_app
from .extensions import db, migrate

# 環境変数 'FLASK_CONFIG' から設定名を読み込む。なければ 'default' を使用。
config_name = os.environ.get('FLASK_CONFIG', 'default')

app = create_app(config_name)

if __name__ == "__main__":
    # DockerfileのCMD ["flask", "run", ...] で起動されるため、
    # この app.run() は主にローカルでの直接実行用（コンテナ外）
    app.run(debug=True, host="0.0.0.0", port=5000)