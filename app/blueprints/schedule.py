from flask import Blueprint, jsonify, request

# 创建排课蓝图
schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

# 示例：排课接口
@schedule_bp.route('/create', methods=['POST'])
def create_schedule():
    data = request.get_json()
    # 这里后续可以写排课逻辑
    return jsonify({
        "code": 200,
        "msg": "排课成功",
        "data": data
    })

# 示例：查看课表接口
@schedule_bp.route('/list', methods=['GET'])
def get_schedule_list():
    # 这里后续可以写课表查询逻辑
    return jsonify({
        "code": 200,
        "msg": "课表获取成功",
        "data": []
    })