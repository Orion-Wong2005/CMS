from datetime import datetime
from app.extensions import db

class Building(db.Model):
    __tablename__ = 'buildings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='楼栋ID')
    building_code = db.Column(db.String(20), nullable=False, unique=True, comment='楼栋编号')
    building_name = db.Column(db.String(50), nullable=False, comment='楼栋名称')
    campus = db.Column(db.String(50), nullable=True, comment='校区')
    min_floor = db.Column(db.Integer, default=1, comment='最低楼层')
    max_floor = db.Column(db.Integer, default=5, comment='最高楼层')
    description = db.Column(db.String(200), nullable=True, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    classrooms = db.relationship('Classroom', backref='building', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Building {self.building_code}: {self.building_name}>'