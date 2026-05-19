from app.extensions import db

class Course(db.Model):
    __tablename__ = 'courses'
    
    course_id = db.Column(db.String(20), primary_key=True, comment='课程编号')
    course_name = db.Column(db.String(100), nullable=False, comment='课程名称')
    credit = db.Column(db.Numeric(3, 1), nullable=False, comment='学分')
    hours = db.Column(db.Integer, nullable=False, comment='学时')
    teacher_id = db.Column(db.String(20), db.ForeignKey('teachers.teacher_id', ondelete='SET NULL'), index=True, comment='授课教师工号')
    semester = db.Column(db.String(30), comment='开课学期')
    capacity = db.Column(db.Integer, default=60, comment='容量')
    
    # 关联关系
    enrollments = db.relationship('Enrollment', backref='course', cascade='all, delete-orphan')
    grades = db.relationship('Grade', backref='course', cascade='all, delete-orphan')
    schedules = db.relationship('Schedule', backref='course', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.course_id} {self.course_name}>'
