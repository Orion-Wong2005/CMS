from flask import Blueprint, jsonify, request

# 创建选课蓝图
enrollment_bp = Blueprint('enrollment', __name__, url_prefix='/enrollment')

# 示例：学生选课接口
@enrollment_bp.route('/select', methods=['POST'])
def select_course():
    data = request.get_json()
    # 这里后续可以写选课逻辑
    return jsonify({
        "code": 200,
        "msg": "选课成功",
        "data": data
    })

# 示例：查看已选课程接口
@enrollment_bp.route('/my', methods=['GET'])
def my_enrollment():
    # 这里后续可以写查询已选课程逻辑
    return jsonify({
        "code": 200,
        "msg": "已选课程获取成功",
        "data": []
    })