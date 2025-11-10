import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む（ローカル開発用）
load_dotenv()

class Config:
    """基本設定クラス"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_fallback'
    
    # SQLAlchemy設定
    # compose.yamlの環境変数を参照
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'example')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'db')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'app_db')
    
    # PyMySQLを使用するための接続文字列
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@"
        f"{MYSQL_HOST}:3306/{MYSQL_DATABASE}"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False # Trueにすると実行SQLをログに出力

class DevelopmentConfig(Config):
    """開発環境用設定"""
    DEBUG = True
    SQLALCHEMY_ECHO = True # 開発中はSQLログを有効にすると便利

class ProductionConfig(Config):
    """本番環境用設定"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

# 環境変数に応じて設定を切り替える
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}