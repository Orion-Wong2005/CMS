from datetime import datetime
from app.extensions import db

class Semester(db.Model):
    __tablename__ = 'semesters'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='学期ID')
    year_start = db.Column(db.Integer, nullable=False, comment='学年开始年份')
    year_end = db.Column(db.Integer, nullable=False, comment='学年结束年份')
    semester_num = db.Column(db.Integer, nullable=False, comment='学期序号(1,2,3)')
    start_date = db.Column(db.Date, nullable=True, comment='学期开始日期')
    end_date = db.Column(db.Date, nullable=True, comment='学期结束日期')
    status = db.Column(db.Integer, default=1, comment='状态：1开启 0关闭')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    
    @property
    def name(self):
        """返回学期名称"""
        return f"{self.year_start}-{self.year_end}-{self.semester_num}"
    
    def __repr__(self):
        return f'<Semester {self.name}>'
