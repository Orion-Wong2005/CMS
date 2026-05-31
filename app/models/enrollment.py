from datetime import datetime
from app.extensions import db

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False, comment='学号')
    course_id = db.Column(db.String(20), db.ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False, comment='课程编号')
    enroll_time = db.Column(db.DateTime, default=datetime.now, comment='选课时间')
    status = db.Column(db.Integer, default=1, comment='1正常 0退课')
    
    # 唯一约束：一个学生不能重复选同一门课
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='uk_student_course'),
    )
    
    def __repr__(self):
        return f'<Enrollment {self.student_id} -> {self.course_id}>'
