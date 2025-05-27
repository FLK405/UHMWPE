# app/utils/decorators.py
# 自定义装饰器，用于权限校验等

from functools import wraps
from flask import jsonify, session # 导入 session
from app.services.rbac_service import RbacService
from app.services.auth_service import AuthService # 用于获取当前用户ID

def login_required(f):
    """
    装饰器：检查用户是否已登录。
    如果用户未登录，则返回401 Unauthorized错误。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = AuthService.get_current_user_id()
        if current_user_id is None:
            return jsonify({"success": False, "message": "访问未授权，请先登录。"}), 401
        # 可以选择将 current_user 或 user_id 作为参数传递给被装饰的函数
        # kwargs['current_user_id'] = current_user_id 
        return f(*args, **kwargs)
    return decorated_function

def permission_required(module_name: str, action: str):
    """
    装饰器：检查当前登录用户是否对指定模块拥有特定操作权限。
    必须在 @login_required 之后使用 (或者自行包含登录检查)。

    :param module_name: 模块的名称 (例如: "纤维性能", "材料管理")。
    :param action: 需要检查的操作权限 (例如: "CanRead", "CanWrite", "CanDelete")。
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. 检查用户是否登录 (也可以依赖于 @login_required 先行检查)
            user_id = AuthService.get_current_user_id()
            if user_id is None:
                return jsonify({"success": False, "message": "访问未授权，请先登录以进行权限检查。"}), 401

            # 2. 检查权限
            if not RbacService.check_permission(user_id=user_id, module_name=module_name, action=action):
                # print(f"权限拒绝: 用户ID {user_id} 对模块 '{module_name}' 执行操作 '{action}' 失败。") # 日志
                return jsonify({
                    "success": False,
                    "message": f"权限不足。您没有 '{action}' 权限访问模块 '{module_name}'。"
                }), 403 # 403 Forbidden
            
            # print(f"权限允许: 用户ID {user_id} 对模块 '{module_name}' 执行操作 '{action}' 成功。") # 日志
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 示例：组合装饰器
# @some_blueprint.route('/protected_resource')
# @login_required
# @permission_required(module_name="SomeModule", action="CanRead")
# def view_protected_resource():
#     # ...
#     pass
