# app/routes/resin_spinning_routes.py
# "前端树脂与纺丝工艺参数" 模块的API路由定义

from flask import Blueprint, request, jsonify
from app.services.resin_spinning_service import ResinSpinningService
from app.services.auth_service import AuthService # 用于获取当前用户ID
from app.utils.decorators import login_required, permission_required # 权限装饰器

# 创建蓝图
# 注意：模块名称 "前端树脂与纺丝工艺表" 用于权限检查，必须与数据库中模块表（ModulesTable）的记录一致。
MODULE_NAME_FOR_RBAC = "前端树脂与纺丝工艺表" 

resin_spinning_bp = Blueprint(
    'resin_spinning_bp', 
    __name__, 
    url_prefix='/api/resin-spinning' # 使用 /api 前缀以区分前端路由
)

@resin_spinning_bp.route('/', methods=['POST'])
@login_required
@permission_required(MODULE_NAME_FOR_RBAC, 'CanWrite')
def create_resin_spinning_record():
    """
    创建一条新的前端树脂与纺丝工艺参数记录。
    请求体应为JSON格式，包含记录的各个字段。
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "请求体不能为空且必须是JSON格式。"}), 400

    current_user_id = AuthService.get_current_user_id()
    if not current_user_id: # 理论上 @login_required 会处理，但双重检查无害
        return jsonify({"success": False, "message": "无法获取当前用户信息，请重新登录。"}), 401
        
    success, result, status_code = ResinSpinningService.create_record(data=data, user_id=current_user_id)

    if success:
        return jsonify({"success": True, "message": "记录创建成功。", "record": result}), status_code
    else:
        return jsonify({"success": False, "message": result}), status_code

@resin_spinning_bp.route('/<int:record_id>', methods=['GET'])
@login_required
@permission_required(MODULE_NAME_FOR_RBAC, 'CanRead')
def get_resin_spinning_record(record_id):
    """
    根据记录ID获取单个前端树脂与纺丝工艺参数记录。
    """
    success, result, status_code = ResinSpinningService.get_record_by_id(record_id)
    
    if success:
        return jsonify({"success": True, "record": result}), status_code
    else:
        return jsonify({"success": False, "message": result}), status_code

@resin_spinning_bp.route('/', methods=['GET'])
@login_required
@permission_required(MODULE_NAME_FOR_RBAC, 'CanRead')
def get_all_resin_spinning_records():
    """
    获取前端树脂与纺丝工艺参数记录列表（支持分页和过滤）。
    查询参数:
        - page (int, optional): 页码，默认为1。
        - per_page (int, optional): 每页记录数，默认为10。
        - material_grade (str, optional): 按材料牌号过滤 (模糊匹配)。
        - batch_number (str, optional): 按批号过滤 (模糊匹配)。
        - resin_type (str, optional): 按树脂类型过滤 (模糊匹配)。
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    filters = {
        'material_grade': request.args.get('material_grade', type=str),
        'batch_number': request.args.get('batch_number', type=str),
        'resin_type': request.args.get('resin_type', type=str)
        # 可以从 request.args 添加更多过滤参数
    }
    # 清除值为None的过滤器，以避免传递它们
    filters = {k: v for k, v in filters.items() if v is not None}

    success, result, status_code = ResinSpinningService.get_all_records(page=page, per_page=per_page, filters=filters)

    if success:
        return jsonify({"success": True, **result}), status_code # result 包含 records, total, pages 等
    else:
        return jsonify({"success": False, "message": result}), status_code

@resin_spinning_bp.route('/<int:record_id>', methods=['PUT'])
@login_required
@permission_required(MODULE_NAME_FOR_RBAC, 'CanWrite')
def update_resin_spinning_record(record_id):
    """
    更新指定ID的前端树脂与纺丝工艺参数记录。
    请求体应为JSON格式，包含要更新的字段。
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "请求体不能为空且必须是JSON格式。"}), 400

    current_user_id = AuthService.get_current_user_id()
    if not current_user_id:
        return jsonify({"success": False, "message": "无法获取当前用户信息，请重新登录。"}), 401

    success, result, status_code = ResinSpinningService.update_record(
        record_id=record_id, 
        data=data, 
        user_id=current_user_id
    )

    if success:
        return jsonify({"success": True, "message": "记录更新成功。", "record": result}), status_code
    else:
        return jsonify({"success": False, "message": result}), status_code

@resin_spinning_bp.route('/<int:record_id>', methods=['DELETE'])
@login_required
@permission_required(MODULE_NAME_FOR_RBAC, 'CanDelete')
def delete_resin_spinning_record(record_id):
    """
    删除指定ID的前端树脂与纺丝工艺参数记录。
    """
    current_user_id = AuthService.get_current_user_id() # 虽然服务层目前没用，但记录操作者可能有用
    if not current_user_id:
        return jsonify({"success": False, "message": "无法获取当前用户信息，请重新登录。"}), 401
        
    success, message, status_code = ResinSpinningService.delete_record(record_id)

    if success:
        return jsonify({"success": True, "message": message}), status_code
    else:
        return jsonify({"success": False, "message": message}), status_code

# 可以在蓝图级别添加错误处理器，处理例如 RBAC 权限不足的通用情况等
# @resin_spinning_bp.errorhandler(Exception)
# def handle_resin_spinning_errors(e):
#     # Log e
#     return jsonify({"success": False, "message": "树脂纺丝模块发生内部错误。"}), 500
