from flask import Flask
from app.extensions import db, migrate
from app.config import Config
from flask import Flask, render_template

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

    # ==============================
    # 全局错误处理器
    # ==============================
    @app.errorhandler(403)
    def forbidden_error(error):
        """403 无权限错误"""
        return render_template('common/403.html'), 403
    
    @app.errorhandler(404)
    def page_not_found_error(error):
        """404 页面不存在错误"""
        return render_template('common/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        """500 服务器内部错误"""
        return render_template('common/500.html'), 500
        
    return app
