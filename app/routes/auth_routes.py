# app/routes/auth_routes.py
# 认证相关的API路由定义

from flask import Blueprint, request, jsonify, session
from app.services.auth_service import AuthService
from app.models.user_model import UserModel # 主要用于类型提示或直接返回用户信息
# from app.utils.decorators import login_required # 稍后可能需要登录保护装饰器

# 创建认证蓝图
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth') # url_prefix 会自动加在所有路由前

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册API端点。
    接收JSON: { "username": "...", "password": "...", "role_id": ..., "full_name": "...", "email": "..." }
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "请求体不能为空且必须是JSON格式。"}), 400

    username = data.get('username')
    password = data.get('password')
    role_id = data.get('role_id')
    full_name = data.get('full_name')
    email = data.get('email')

    # 基本输入验证
    if not all([username, password, role_id]):
        return jsonify({"success": False, "message": "用户名、密码和角色ID是必填项。"}), 400
    
    if not isinstance(role_id, int):
        return jsonify({"success": False, "message": "角色ID必须是整数。"}), 400

    success, message, user = AuthService.register_user(
        username=username,
        password=password,
        role_id=role_id,
        full_name=full_name,
        email=email
    )

    if success and user:
        # user 是 UserModel 实例，可以转换为字典返回
        return jsonify({
            "success": True,
            "message": message,
            "user": user.to_dict(include_role=True) # 使用 to_dict 方法
        }), 201 # 201 Created
    else:
        return jsonify({"success": False, "message": message}), 400 # 或其他适当的错误码，例如 409 Conflict for existing user

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录API端点。
    接收JSON: { "username": "...", "password": "..." }
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "请求体不能为空且必须是JSON格式。"}), 400

    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({"success": False, "message": "用户名和密码是必填项。"}), 400

    success, message, user_data = AuthService.login_user(username, password)

    if success and user_data:
        # user_data 已经是字典格式
        return jsonify({
            "success": True,
            "message": message,
            "user": user_data
        }), 200
    else:
        return jsonify({"success": False, "message": message}), 401 # 401 Unauthorized

@auth_bp.route('/logout', methods=['POST'])
# @login_required # 通常登出操作需要用户已登录
def logout():
    """
    用户登出API端点。
    """
    # 检查 session 中是否有用户，虽然 AuthService.logout_user() 会处理空 session
    # 但在这里可以提前返回，如果严格要求已登录用户才能调用登出
    # if 'user_id' not in session:
    #     return jsonify({"success": False, "message": "用户未登录。"}), 401

    success, message = AuthService.logout_user()

    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        # 理论上，基于当前 session 的登出不应该失败，除非有特殊逻辑
        return jsonify({"success": False, "message": message}), 500

@auth_bp.route('/status', methods=['GET'])
def status():
    """
    检查当前用户的登录状态和会话信息。
    """
    user_id = session.get('user_id')
    if user_id:
        current_user = AuthService.get_current_user()
        if current_user:
            return jsonify({
                "logged_in": True,
                "user": current_user.to_dict(include_role=True),
                "session": dict(session) # 显示当前 session 内容 (调试用，生产环境慎用)
            }), 200
        else: # Session 中有 user_id 但数据库中找不到该用户
            AuthService.logout_user() # 清理无效的 session
            return jsonify({"logged_in": False, "message": "会话无效，用户不存在，已自动登出。"}), 404
    else:
        return jsonify({"logged_in": False, "message": "用户未登录。"}), 200


# 可以在蓝图级别添加错误处理器
@auth_bp.errorhandler(Exception)
def handle_auth_errors(e):
    # TODO: 根据异常类型返回更具体的错误信息和状态码
    # 例如: SQLAlchemyError, ValidationError 等
    # 对于未知异常，记录日志并返回通用错误
    print(f"Auth Blueprint Error: {e}") # 替换为实际的日志记录
    return jsonify({"success": False, "message": "认证过程中发生内部服务器错误。"}), 500
