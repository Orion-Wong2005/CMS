from flask import Blueprint, jsonify, request

# 创建课程蓝图
course_bp = Blueprint('course', __name__, url_prefix='/course')

# 示例：获取课程列表接口
@course_bp.route('/list', methods=['GET'])
def get_course_list():
    # 这里后续可以写数据库查询逻辑
    return jsonify({
        "code": 200,
        "msg": "课程列表获取成功",
        "data": []
    })

# 示例：新增课程接口
@course_bp.route('/add', methods=['POST'])
def add_course():
    data = request.get_json()
    # 这里后续可以写数据库新增逻辑
    return jsonify({
        "code": 200,
        "msg": "课程新增成功",
        "data": data
    })