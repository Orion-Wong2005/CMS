from datetime import datetime
from sqlalchemy import Enum
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = db.Column(db.String(30), nullable=False, unique=True, index=True, comment='登录账号')
    password = db.Column(db.String(64), nullable=False, comment='密码(MD5加密)')
    role = db.Column(Enum('admin', 'teacher', 'student'), nullable=False, default='student', comment='角色')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    
    # 关联关系
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    teacher = db.relationship('Teacher', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
