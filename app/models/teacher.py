from app.extensions import db

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    teacher_id = db.Column(db.String(20), primary_key=True, comment='工号')
    name = db.Column(db.String(20), nullable=False, comment='姓名')
    gender = db.Column(db.String(2), comment='性别')
    department = db.Column(db.String(50), comment='院系')
    title = db.Column(db.String(30), comment='职称')
    phone = db.Column(db.String(20), comment='手机号')
    email = db.Column(db.String(50), comment='邮箱')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True, comment='关联用户ID')
    
    # 关联关系
    courses = db.relationship('Course', backref='teacher')
    
    def __repr__(self):
        return f'<Teacher {self.teacher_id} {self.name}>'
