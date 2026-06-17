from datetime import datetime
from app.extensions import db

class Classroom(db.Model):
    __tablename__ = 'classrooms'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='教室ID')
    classroom_code = db.Column(db.String(30), nullable=False, unique=True, comment='教室编号')
    building_id = db.Column(db.Integer, db.ForeignKey('buildings.id', ondelete='SET NULL'), nullable=True, comment='楼栋ID')
    floor = db.Column(db.Integer, comment='楼层')
    capacity = db.Column(db.Integer, default=30, comment='容纳人数')
    has_projector = db.Column(db.Boolean, default=False, comment='是否有投影仪')
    has_computer = db.Column(db.Boolean, default=False, comment='是否有电脑')
    status = db.Column(db.Integer, default=1, comment='状态：1可用 0不可用')
    description = db.Column(db.String(200), nullable=True, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def __repr__(self):
        return f'<Classroom {self.classroom_code}>'