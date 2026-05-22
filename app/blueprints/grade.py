from flask import Blueprint, jsonify, request

# 创建成绩蓝图
grade_bp = Blueprint('grade', __name__, url_prefix='/grade')

# 示例：录入成绩接口
@grade_bp.route('/input', methods=['POST'])
def input_grade():
    data = request.get_json()
    # 这里后续可以写成绩录入逻辑
    return jsonify({
        "code": 200,
        "msg": "成绩录入成功",
        "data": data
    })

# 示例：查看成绩接口
@grade_bp.route('/list', methods=['GET'])
def get_grade_list():
    # 这里后续可以写成绩查询逻辑
    return jsonify({
        "code": 200,
        "msg": "成绩列表获取成功",
        "data": []
    })