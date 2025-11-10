from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# インスタンスを初期化（まだアプリには紐付けない）
db = SQLAlchemy()
migrate = Migrate()