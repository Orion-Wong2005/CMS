import os
import secrets

class Config:
    """基础配置类（所有环境通用）"""
    # ==============================================
    # 核心安全配置（生产环境必须修改！）
    # ==============================================
    # 用于加密Session、Cookie等的密钥
    # 本地开发可以用默认值，生产环境必须替换为随机字符串
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-2026-05-19-cms'
    
    # ==============================================
    # 数据库配置
    # ==============================================
    # 数据库连接字符串
    # 格式：mysql+pymysql://用户名:密码@主机地址:端口/数据库名
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'mysql+pymysql://root:123456@localhost:3306/course_management_system'
    
    # 关闭SQLAlchemy的修改跟踪（提升性能，避免警告）
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 显示SQL语句（开发调试用，生产环境关闭）
    SQLALCHEMY_ECHO = False
    
    # ==============================================
    # Flask 基础配置
    # ==============================================
    # 调试模式（开发环境开启，生产环境必须关闭）
    DEBUG = False
    
    # 测试模式
    TESTING = False
    
    # 应用根路径
    APPLICATION_ROOT = '/'
    
    # ==============================================
    # Session 配置
    # ==============================================
    # Session过期时间（秒），默认30分钟
    PERMANENT_SESSION_LIFETIME = 1800
    
    # 生产环境开启Cookie安全标志
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevelopmentConfig(Config):
    """本地开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # 开启后会在控制台打印所有SQL语句，调试时很有用

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 生产环境强制使用环境变量中的密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # 生产环境开启Cookie安全标志
    SESSION_COOKIE_SECURE = True
    
    # 数据库连接池配置（生产环境优化）
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
