from app.extensions import db

class Student(db.Model):
    __tablename__ = 'students'
    
    student_id = db.Column(db.String(20), primary_key=True, comment='学号')
    name = db.Column(db.String(20), nullable=False, comment='姓名')
    gender = db.Column(db.String(2), comment='性别')
    major = db.Column(db.String(50), comment='专业')
    class_name = db.Column(db.String(50), comment='班级')
    phone = db.Column(db.String(20), comment='手机号')
    email = db.Column(db.String(50), comment='邮箱')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True, comment='关联用户ID')
    
    # 关联关系
    enrollments = db.relationship('Enrollment', backref='student', cascade='all, delete-orphan')
    grades = db.relationship('Grade', backref='student', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Student {self.student_id} {self.name}>'
