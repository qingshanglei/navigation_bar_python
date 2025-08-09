import os
from datetime import timedelta

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'navigation-jwt-secret-key-2025'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    # 启用JTI（JWT ID）以支持token黑名单功能
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']
    
    # 其他配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'navigation-secret-key-2025'
    DEBUG = True
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:8080']
    
    # 安全配置
    JSON_AS_ASCII = False  # 支持中文JSON响应