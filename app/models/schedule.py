from app.extensions import db

class Schedule(db.Model):
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.String(20), db.ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False, comment='课程编号')
    day_of_week = db.Column(db.Integer, comment='星期(1-7)')
    start_time = db.Column(db.String(20), comment='开始节次')
    end_time = db.Column(db.String(20), comment='结束节次')
    classroom = db.Column(db.String(30), comment='教室')
    semester = db.Column(db.String(30), comment='学期')
    week_start = db.Column(db.Integer, comment='起始周次')
    week_end = db.Column(db.Integer, comment='结束周次')

    def get_period_range(self):
        """获取节次范围"""
        try:
            return int(self.start_time), int(self.end_time)
        except (ValueError, TypeError):
            return None, None

    def get_weekday_name(self):
        """获取星期名称"""
        weekdays = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
        return weekdays.get(self.day_of_week, '')

    def to_dict(self):
        """转为字典"""
        start, end = self.get_period_range()
        return {
            'id': self.id,
            'course_id': self.course_id,
            'course_name': self.course.course_name if self.course else None,
            'day_of_week': self.day_of_week,
            'weekday_name': self.get_weekday_name(),
            'start_time': self.start_time,
            'end_time': self.end_time,
            'start_period': start,
            'end_period': end,
            'classroom': self.classroom,
            'semester': self.semester,
            'week_start': self.week_start,
            'week_end': self.week_end,
        }

    def __repr__(self):
        return f'<Schedule {self.course_id} 周{self.day_of_week} 第{self.start_time}-{self.end_time}节 {self.classroom}>'
