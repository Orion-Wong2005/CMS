from flask import Flask
from app.extensions import db, migrate
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 注册蓝图
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.student import student_bp
    from app.blueprints.teacher import teacher_bp
    from app.blueprints.course import course_bp
    from app.blueprints.enrollment import enrollment_bp
    from app.blueprints.grade import grade_bp
    from app.blueprints.schedule import schedule_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(course_bp, url_prefix='/course')
    app.register_blueprint(enrollment_bp, url_prefix='/enrollment')
    app.register_blueprint(grade_bp, url_prefix='/grade')
    app.register_blueprint(schedule_bp, url_prefix='/schedule')
    
    return app
