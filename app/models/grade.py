from app.extensions import db

class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False, comment='学号')
    course_id = db.Column(db.String(20), db.ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False, comment='课程编号')
    grade = db.Column(db.Numeric(5, 1), nullable=True, comment='成绩')
    remark = db.Column(db.String(100), comment='备注')
    
    # 唯一约束：一个学生同一门课只有一个成绩
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='uk_student_course_grade'),
    )
    
    def __repr__(self):
        return f'<Grade {self.student_id} {self.course_id}: {self.grade}>'
