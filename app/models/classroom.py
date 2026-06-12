# app/models/classroom.py
from app.extensions import db
from datetime import datetime


class Classroom(db.Model):
    """教室模型"""
    __tablename__ = 'classrooms'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    classroom_number = db.Column(db.String(20), unique=True, nullable=False, comment='教室编号')
    building = db.Column(db.String(50), nullable=False, comment='教学楼')
    floor = db.Column(db.Integer, comment='楼层')
    capacity = db.Column(db.Integer, default=60, comment='容量')
    type = db.Column(db.String(20), default='普通教室', comment='类型')
    equipment = db.Column(db.String(200), comment='设备配置')
    status = db.Column(db.String(20), default='可用', comment='状态')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    schedules = db.relationship('ClassroomSchedule', backref='classroom', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'classroom_number': self.classroom_number,
            'building': self.building,
            'floor': self.floor,
            'capacity': self.capacity,
            'type': self.type,
            'equipment': self.equipment,
            'status': self.status
        }

    def __repr__(self):
        return f'<Classroom {self.classroom_number}>'


class ClassroomSchedule(db.Model):
    """教室排课模型 - 使用自定义约束确保同一教室同一时间不安排多门课"""
    __tablename__ = 'classroom_schedules'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    course_id = db.Column(db.String(20), db.ForeignKey('courses.course_id'), nullable=False)
    semester = db.Column(db.String(20), nullable=False, comment='学期')
    week = db.Column(db.Integer, nullable=False, comment='周次(1-20)')
    weekday = db.Column(db.Integer, nullable=False, comment='星期几(1-7)')
    start_section = db.Column(db.Integer, nullable=False, comment='开始节次')
    end_section = db.Column(db.Integer, nullable=False, comment='结束节次')
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 自定义约束：同一教室同一学期同一周次同一天同一时间段不能安排多门课
    __table_args__ = (
        db.UniqueConstraint('classroom_id', 'semester', 'week', 'weekday', 'start_section',
                            name='uq_classroom_time_slot'),
    )

    # 关系定义
    course = db.relationship('Course', backref='classroom_schedules', foreign_keys=[course_id])

    def to_dict(self):
        course_name = self.course.course_name if self.course else None
        return {
            'id': self.id,
            'classroom_id': self.classroom_id,
            'classroom_number': self.classroom.classroom_number if self.classroom else None,
            'building': self.classroom.building if self.classroom else None,
            'course_id': self.course_id,
            'course_name': course_name,
            'semester': self.semester,
            'week': self.week,
            'weekday': self.weekday,
            'weekday_name': self.get_weekday_name(),
            'start_section': self.start_section,
            'end_section': self.end_section,
            'sections': f'{self.start_section}-{self.end_section}节'
        }

    @staticmethod
    def get_weekday_name_by_num(weekday):
        weekdays = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
        return weekdays[weekday] if 1 <= weekday <= 7 else ''

    def get_weekday_name(self):
        return self.get_weekday_name_by_num(self.weekday)

    def __repr__(self):
        return f'<ClassroomSchedule {self.classroom_id} {self.weekday} {self.start_section}-{self.end_section}>'