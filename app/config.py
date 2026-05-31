import os
import sqlite3

class Config:
    # 密钥(用于session和csrf保护)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # 数据库配置 - 使用 SQLite 方便开发
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'cms.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 调试模式
    DEBUG = True
