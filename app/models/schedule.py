from app.extensions import db

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.String(20), db.ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False, comment='课程编号')
    day_of_week = db.Column(db.Integer, comment='星期(1-7)')
    start_time = db.Column(db.String(20), comment='开始节次/时间')
    end_time = db.Column(db.String(20), comment='结束节次/时间')
    classroom = db.Column(db.String(30), comment='教室')
    
    def __repr__(self):
        return f'<Schedule {self.course_id} 周{self.day_of_week} {self.classroom}>'
