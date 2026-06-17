import os

class Config:
    # 密钥(用于session和csrf保护)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/course_management_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 调试模式
    DEBUG = True
