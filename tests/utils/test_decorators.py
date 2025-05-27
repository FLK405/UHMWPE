# tests/utils/test_decorators.py
# 权限控制装饰器的单元测试

import pytest
from flask import Flask, jsonify, Blueprint, current_app
from app.utils.decorators import login_required, permission_required
from app.services.auth_service import AuthService # To manipulate session
from app.models import RoleModel, ModuleModel, RolePermissionModel, UserModel

# --- Test Blueprint Setup ---
# 创建一个蓝图用于测试装饰器保护的路由
test_bp = Blueprint('test_bp_for_decorators', __name__)

@test_bp.route('/login-required-route')
@login_required
def login_required_route():
    """一个受 @login_required 保护的路由。"""
    return jsonify(success=True, message="已访问受登录保护的路由。"), 200

@test_bp.route('/permission-required-route-read')
@login_required # 通常 permission_required 会和 login_required 一起使用
@permission_required(module_name="FiberData", action="CanRead")
def permission_required_route_read():
    """一个受 @permission_required(module="FiberData", action="CanRead") 保护的路由。"""
    return jsonify(success=True, message="已访问受 FiberData-CanRead 权限保护的路由。"), 200

@test_bp.route('/permission-required-route-delete')
@login_required
@permission_required(module_name="FiberData", action="CanDelete")
def permission_required_route_delete():
    """一个受 @permission_required(module="FiberData", action="CanDelete") 保护的路由。"""
    return jsonify(success=True, message="已访问受 FiberData-CanDelete 权限保护的路由。"), 200

@test_bp.route('/permission-required-admin-route')
@login_required
@permission_required(module_name="UserData", action="CanWrite") # 假设 UserData 模块, CanWrite 权限
def permission_required_admin_route():
    """一个仅管理员（假设）可访问的路由"""
    return jsonify(success=True, message="已访问受 UserData-CanWrite 权限保护的路由。"), 200


# --- Pytest Fixture to Register Blueprint ---
@pytest.fixture(autouse=True)
def register_test_blueprint(app):
    """自动为测试应用注册包含受保护路由的蓝图。"""
    if not app.blueprints.get(test_bp.name):
        app.register_blueprint(test_bp, url_prefix='/test_decorators')
    # print(f"Blueprints registered on app for decorator tests: {list(app.blueprints.keys())}")
    # print(f"URL Map: {app.url_map}")


class TestLoginRequiredDecorator:
    """测试 @login_required 装饰器"""

    def test_login_required_access_denied_when_not_logged_in(self, client):
        """测试未登录用户访问受 @login_required 保护的路由 (应返回401)"""
        # print("\n--- test_login_required_access_denied_when_not_logged_in ---")
        response = client.get('/test_decorators/login-required-route')
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")
        assert response.status_code == 401
        assert response.json["success"] is False
        assert "访问未授权，请先登录。" in response.json["message"]

    def test_login_required_access_granted_when_logged_in(self, client, test_user):
        """测试已登录用户访问受 @login_required 保护的路由 (应成功)"""
        # print("\n--- test_login_required_access_granted_when_logged_in ---")
        # 先登录用户 (test_user 来自 conftest.py)
        login_resp = client.post('/auth/login', json={"username": test_user.用户名, "password": "password123"})
        assert login_resp.status_code == 200 # 确保登录成功

        response = client.get('/test_decorators/login-required-route')
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")
        assert response.status_code == 200
        assert response.json["success"] is True
        assert "已访问受登录保护的路由。" in response.json["message"]


class TestPermissionRequiredDecorator:
    """测试 @permission_required 装饰器"""

    # test_user (Researcher) 应该有 FiberData 的 CanRead 权限 (通过 researcher_permissions fixture 设置)
    def test_permission_required_access_granted(self, client, test_user, basic_roles, basic_modules, researcher_permissions):
        """测试拥有所需权限的用户访问受保护路由 (应成功)"""
        # print("\n--- test_permission_required_access_granted ---")
        # test_user (Researcher) 被 researcher_permissions fixture 赋予 FiberData 模块的 CanRead=True, CanWrite=True 权限
        assert researcher_permissions is not None # 确保 fixture 已执行
        
        login_resp = client.post('/auth/login', json={"username": test_user.用户名, "password": "password123"})
        assert login_resp.status_code == 200

        response = client.get('/test_decorators/permission-required-route-read') # 需要 FiberData, CanRead
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")
        assert response.status_code == 200
        assert response.json["success"] is True
        assert "已访问受 FiberData-CanRead 权限保护的路由。" in response.json["message"]

    def test_permission_required_access_denied_no_permission(self, client, test_user, researcher_permissions):
        """测试用户没有所需权限 (但已登录) 访问受保护路由 (应返回403)"""
        # print("\n--- test_permission_required_access_denied_no_permission ---")
        # test_user (Researcher) 在 researcher_permissions 中对 FiberData 的 CanDelete 是 False
        assert researcher_permissions is not None
        assert researcher_permissions.允许删除 is False # 确认权限设置

        login_resp = client.post('/auth/login', json={"username": test_user.用户名, "password": "password123"})
        assert login_resp.status_code == 200

        response = client.get('/test_decorators/permission-required-route-delete') # 需要 FiberData, CanDelete
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")
        assert response.status_code == 403
        assert response.json["success"] is False
        assert "权限不足。" in response.json["message"]
        assert "CanDelete" in response.json["message"] and "FiberData" in response.json["message"]

    def test_permission_required_access_denied_different_permission(self, client, test_user, researcher_permissions):
        """测试用户对模块有其他权限但没有具体要求的权限 (应返回403)"""
        # print("\n--- test_permission_required_access_denied_different_permission ---")
        # test_user (Researcher) 有 FiberData 的 CanRead=True, 但此路由需要 CanDelete=True, 而用户没有。
        assert researcher_permissions is not None
        assert researcher_permissions.允许读取 is True
        assert researcher_permissions.允许删除 is False

        login_resp = client.post('/auth/login', json={"username": test_user.用户名, "password": "password123"})
        assert login_resp.status_code == 200

        response = client.get('/test_decorators/permission-required-route-delete') # 需要 CanDelete
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")
        assert response.status_code == 403
        assert response.json["success"] is False
        assert "权限不足。" in response.json["message"]

    def test_permission_required_access_denied_different_module(self, client, test_user, researcher_permissions, admin_permissions):
        """测试用户对其他模块有权限但没有当前模块的权限 (应返回403)"""
        # print("\n--- test_permission_required_access_denied_different_module ---")
        # test_user (Researcher) 对 FiberData 有权限 (via researcher_permissions)
        # 但此路由 /permission-required-admin-route 需要 UserData, CanWrite 权限
        # admin_permissions fixture 为 Admin 角色设置了 UserData 权限，与 test_user (Researcher) 无关
        assert researcher_permissions is not None
        assert admin_permissions is not None # 确保 Admin 权限已设置，但不适用于 test_user

        login_resp = client.post('/auth/login', json={"username": test_user.用户名, "password": "password123"})
        assert login_resp.status_code == 200

        response = client.get('/test_decorators/permission-required-admin-route') # 需要 UserData, CanWrite
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")
        assert response.status_code == 403
        assert response.json["success"] is False
        assert "权限不足。" in response.json["message"]
        assert "CanWrite" in response.json["message"] and "UserData" in response.json["message"]

    def test_permission_required_access_denied_not_logged_in(self, client):
        """测试未登录用户访问受 @permission_required 保护的路由 (应返回401)"""
        # print("\n--- test_permission_required_access_denied_not_logged_in ---")
        response = client.get('/test_decorators/permission-required-route-read')
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")
        assert response.status_code == 401 # @login_required 应先生效
        assert response.json["success"] is False
        assert "访问未授权，请先登录以进行权限检查。" in response.json["message"] # 消息来自 @permission_required

    def test_permission_required_module_not_exist(self, client, test_user, db_session):
        """测试 @permission_required 指向一个不存在的模块 (应返回403，因为权限检查会失败)"""
        # print("\n--- test_permission_required_module_not_exist ---")
        
        # 动态创建一个受不存在模块保护的路由
        # 注意: 在实际应用中，模块名通常是固定的。这里是为了测试装饰器的鲁棒性。
        # 这种动态添加路由的方式在测试中不常见，更好的方式是预定义路由，并确保测试数据覆盖这种情况。
        # 这里我们假设 RbacService.check_permission 会因为找不到模块而返回 False
        
        # 登录用户
        login_resp = client.post('/auth/login', json={"username": test_user.用户名, "password": "password123"})
        assert login_resp.status_code == 200

        # 假设我们有一个路由 @permission_required(module_name="NonExistentModule", action="CanRead")
        # 我们需要调用 RbacService.check_permission 来模拟这种情况，或者创建一个这样的路由
        # 为了简单，我们直接测试 RbacService 的行为，或者依赖于一个预设的路由（如果它存在）
        # 这里的测试将依赖于 RbacService 返回 False
        
        # 我们在 test_bp 中添加一个临时路由，或者直接调用服务
        # 对于装饰器测试，最好是有实际的路由被调用
        # 我们可以在 app 上临时注册一个路由
        with client.application.app_context():
            temp_bp = Blueprint('temp_bp_for_nonexistent_module', __name__)
            @temp_bp.route('/nonexistent-module-route')
            @login_required
            @permission_required(module_name="NonExistentModule", action="CanRead")
            def nonexistent_module_route():
                return jsonify(success=True), 200
            
            # 检查蓝图是否已注册，如果已注册则不重复注册
            if not current_app.blueprints.get(temp_bp.name):
                 current_app.register_blueprint(temp_bp, url_prefix='/temp_test')
            # print(f"URL Map after temp_bp: {current_app.url_map}")


        response = client.get('/temp_test/nonexistent-module-route')
        # print(f"Response Status for non-existent module: {response.status_code}")
        # print(f"Response JSON for non-existent module: {response.json}")
        
        assert response.status_code == 403 # RbacService.check_permission 会因为找不到模块而返回 False
        assert response.json["success"] is False
        assert "权限不足。" in response.json["message"]
        assert "NonExistentModule" in response.json["message"]

        # 清理：如果可以，注销蓝图（Flask 不直接支持注销，需要更复杂的处理或重启 app context）
        # 在测试环境中，通常每个测试函数都有独立的 app context，所以影响不大。
        # 或者，在 fixture 中创建 app 实例，使其在每个测试后被销毁。
        # 我们的 conftest.py 中的 app fixture 是 session-scoped，但 client 是 function-scoped。

    def test_permission_required_admin_access_granted(self, client, db_session, basic_roles, basic_modules, admin_permissions):
        """测试管理员用户 (拥有 UserData-CanWrite 权限) 访问受保护的管理员路由"""
        # print("\n--- test_permission_required_admin_access_granted ---")
        # 1. 创建一个 Admin 用户
        admin_role = basic_roles["Admin"]
        admin_user = UserModel(用户名="adminuser", 角色ID=admin_role.角色ID, 全名="管理员", 邮箱="admin@example.com")
        admin_user.set_password("adminpass")
        db_session.add(admin_user)
        db_session.commit()

        # 确保 admin_permissions fixture 已为 Admin 角色和 UserData 模块设置了权限
        assert admin_permissions is not None
        assert admin_permissions.角色ID == admin_role.角色ID
        assert admin_permissions.module.模块名称 == "UserData"
        assert admin_permissions.允许写入 is True

        # 2. 以 Admin 用户身份登录
        login_resp = client.post('/auth/login', json={"username": "adminuser", "password": "adminpass"})
        assert login_resp.status_code == 200
        assert login_resp.json["user"]["角色"]["角色名称"] == "Admin"

        # 3. 访问受 UserData-CanWrite 保护的路由
        response = client.get('/test_decorators/permission-required-admin-route')
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")
        assert response.status_code == 200
        assert response.json["success"] is True
        assert "已访问受 UserData-CanWrite 权限保护的路由。" in response.json["message"]
