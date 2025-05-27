# tests/routes/test_auth_routes.py
# 认证相关API路由的单元测试

import json
from flask import session
from app.models import UserModel, RoleModel # 用于直接查询数据库进行断言

# --- 辅助函数 ---
def get_role_id(role_name, db_session):
    """辅助函数：根据角色名称获取角色ID"""
    role = RoleModel.find_by_name(role_name)
    if role:
        return role.角色ID
    # 如果在测试设置中角色未创建，则动态创建一个
    new_role = RoleModel(角色名称=role_name, 描述=f"{role_name} (动态创建)")
    db_session.add(new_role)
    db_session.commit()
    return new_role.角色ID

# --- 测试用例 ---

class TestAuthRoutes:
    """包含认证路由 (/auth) 测试用例的类"""

    # === 注册 (/auth/register) 测试 ===

    def test_register_successful(self, client, db_session, basic_roles):
        """测试新用户成功注册"""
        # print("\n--- test_register_successful ---")
        researcher_role_id = basic_roles["Researcher"].角色ID
        response = client.post('/auth/register', json={
            "username": "newuser",
            "password": "password123",
            "role_id": researcher_role_id,
            "full_name": "新用户",
            "email": "newuser@example.com"
        })
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")

        assert response.status_code == 201
        assert response.json["success"] is True
        assert response.json["message"] == "用户注册成功。"
        assert response.json["user"]["用户名"] == "newuser"
        assert response.json["user"]["邮箱"] == "newuser@example.com"
        assert response.json["user"]["角色"]["角色名称"] == "Researcher"

        # 验证用户是否已存入数据库
        user_in_db = UserModel.find_by_username("newuser")
        assert user_in_db is not None
        assert user_in_db.邮箱 == "newuser@example.com"
        assert user_in_db.role.角色名称 == "Researcher"

    def test_register_existing_username(self, client, db_session, test_user):
        """测试使用已存在的用户名进行注册 (应失败)"""
        # print("\n--- test_register_existing_username ---")
        # test_user fixture 已经创建了一个名为 "testuser" 的用户
        role_id = test_user.角色ID # 使用现有用户的角色ID
        response = client.post('/auth/register', json={
            "username": test_user.用户名, # 已存在的用户名
            "password": "newpassword",
            "role_id": role_id,
            "email": "another@example.com"
        })
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")

        assert response.status_code == 400 # 或者 409 Conflict
        assert response.json["success"] is False
        assert f"用户名 '{test_user.用户名}' 已存在。" in response.json["message"]

    def test_register_existing_email(self, client, db_session, test_user):
        """测试使用已存在的邮箱进行注册 (应失败)"""
        # print("\n--- test_register_existing_email ---")
        role_id = test_user.角色ID
        response = client.post('/auth/register', json={
            "username": "anotheruser",
            "password": "password123",
            "role_id": role_id,
            "email": test_user.邮箱 # 已存在的邮箱
        })
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")
        
        assert response.status_code == 400 # 或者 409
        assert response.json["success"] is False
        assert f"邮箱 '{test_user.邮箱}' 已被注册。" in response.json["message"]

    def test_register_invalid_role_id(self, client, db_session):
        """测试使用无效的角色ID进行注册 (应失败)"""
        # print("\n--- test_register_invalid_role_id ---")
        invalid_role_id = 99999 # 一个不存在的角色ID
        response = client.post('/auth/register', json={
            "username": "userwithinvalidrole",
            "password": "password123",
            "role_id": invalid_role_id,
            "email": "invalidrole@example.com"
        })
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")

        assert response.status_code == 400
        assert response.json["success"] is False
        assert f"角色ID '{invalid_role_id}' 不存在。" in response.json["message"]

    def test_register_missing_fields(self, client, db_session):
        """测试注册时缺少必要字段 (应失败)"""
        # print("\n--- test_register_missing_fields ---")
        response = client.post('/auth/register', json={
            "username": "missingfieldsuser"
            # "password" 和 "role_id" 缺失
        })
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")

        assert response.status_code == 400
        assert response.json["success"] is False
        assert "用户名、密码和角色ID是必填项。" in response.json["message"]

    # === 登录 (/auth/login) 测试 ===

    def test_login_successful(self, client, db_session, test_user, basic_roles):
        """测试用户使用有效凭据成功登录"""
        # print("\n--- test_login_successful ---")
        # test_user 的密码是 "password123"
        response = client.post('/auth/login', json={
            "username": test_user.用户名,
            "password": "password123"
        })
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")

        assert response.status_code == 200
        assert response.json["success"] is True
        assert response.json["message"] == "登录成功。"
        assert response.json["user"]["用户名"] == test_user.用户名
        assert response.json["user"]["角色"]["角色名称"] == basic_roles["Researcher"].角色名称 # test_user 是 Researcher

        # 检查 session 是否已设置
        with client.session_transaction() as flask_session:
            # print(f"Session after login: {flask_session}")
            assert flask_session.get('user_id') == test_user.用户ID
            assert flask_session.get('username') == test_user.用户名
            assert flask_session.get('role_id') == test_user.角色ID

    def test_login_invalid_username(self, client, db_session):
        """测试使用无效用户名登录 (应失败)"""
        # print("\n--- test_login_invalid_username ---")
        response = client.post('/auth/login', json={
            "username": "nonexistentuser",
            "password": "password123"
        })
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")

        assert response.status_code == 401 # Unauthorized
        assert response.json["success"] is False
        assert response.json["message"] == "用户名或密码无效。"

    def test_login_incorrect_password(self, client, db_session, test_user):
        """测试使用错误密码登录 (应失败)"""
        # print("\n--- test_login_incorrect_password ---")
        response = client.post('/auth/login', json={
            "username": test_user.用户名,
            "password": "wrongpassword"
        })
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")

        assert response.status_code == 401
        assert response.json["success"] is False
        assert response.json["message"] == "用户名或密码无效。"

    def test_login_disabled_user(self, client, db_session, test_user):
        """测试已禁用的用户尝试登录 (应失败)"""
        # print("\n--- test_login_disabled_user ---")
        # 禁用 test_user
        test_user.是否启用 = False
        db_session.add(test_user)
        db_session.commit()

        response = client.post('/auth/login', json={
            "username": test_user.用户名,
            "password": "password123" # 正确的密码
        })
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")

        assert response.status_code == 401 # 服务端逻辑会先判断用户是否存在和密码是否正确，然后才检查是否启用。
                                          # AuthService.login_user 返回自定义消息
        assert response.json["success"] is False
        assert response.json["message"] == "用户账户已被禁用。"
        
        # 恢复用户状态，以免影响其他测试
        test_user.是否启用 = True
        db_session.add(test_user)
        db_session.commit()


    # === 登出 (/auth/logout) 测试 ===

    def test_logout_successful(self, client, db_session, test_user):
        """测试已登录用户成功登出"""
        # print("\n--- test_logout_successful ---")
        # 先登录用户
        client.post('/auth/login', json={"username": test_user.用户名, "password": "password123"})
        
        with client.session_transaction() as flask_session:
            assert 'user_id' in flask_session # 确认已登录

        # 执行登出
        response = client.post('/auth/logout')
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")

        assert response.status_code == 200
        assert response.json["success"] is True
        assert response.json["message"] == "登出成功。"

        # 检查 session 是否已清除
        with client.session_transaction() as flask_session:
            # print(f"Session after logout: {flask_session}")
            assert 'user_id' not in flask_session
            assert 'username' not in flask_session
            assert 'role_id' not in flask_session

    def test_logout_when_not_logged_in(self, client, db_session):
        """测试未登录用户尝试登出 (应成功，但 session 本来就空)"""
        # print("\n--- test_logout_when_not_logged_in ---")
        # 确保 session 是空的
        with client.session_transaction() as flask_session:
            flask_session.clear()

        response = client.post('/auth/logout')
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")

        assert response.status_code == 200 # 登出操作通常是幂等的
        assert response.json["success"] is True
        assert response.json["message"] == "登出成功。"
        
        with client.session_transaction() as flask_session:
            assert not flask_session # Session 应该仍然是空的


    # === 状态 (/auth/status) 测试 ===

    def test_status_when_logged_out(self, client, db_session):
        """测试未登录时获取用户状态"""
        # print("\n--- test_status_when_logged_out ---")
        with client.session_transaction() as flask_session:
            flask_session.clear() # 确保未登录

        response = client.get('/auth/status')
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")

        assert response.status_code == 200
        assert response.json["logged_in"] is False
        assert response.json["message"] == "用户未登录。"
        assert "user" not in response.json # 不应有用户信息

    def test_status_when_logged_in(self, client, db_session, test_user, basic_roles):
        """测试已登录时获取用户状态"""
        # print("\n--- test_status_when_logged_in ---")
        # 先登录
        client.post('/auth/login', json={"username": test_user.用户名, "password": "password123"})

        response = client.get('/auth/status')
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")

        assert response.status_code == 200
        assert response.json["logged_in"] is True
        assert response.json["user"]["用户名"] == test_user.用户名
        assert response.json["user"]["邮箱"] == test_user.邮箱
        assert response.json["user"]["角色"]["角色名称"] == basic_roles["Researcher"].角色名称
        assert response.json["session"]["user_id"] == test_user.用户ID
        
    def test_status_with_invalid_session_user_id(self, client, db_session):
        """测试 session 中有 user_id 但数据库中用户不存在的情况"""
        # print("\n--- test_status_with_invalid_session_user_id ---")
        with client.session_transaction() as flask_session:
            flask_session['user_id'] = 99999  # 一个不存在的用户ID
            flask_session['username'] = 'ghost'
            flask_session['role_id'] = 1
        
        response = client.get('/auth/status')
        # print(f"Response Status: {response.status_code}")
        # print(f"Response JSON: {response.json}")

        assert response.status_code == 404 # 因为用户不存在，被认为是 Not Found
        assert response.json["logged_in"] is False
        assert "会话无效，用户不存在，已自动登出。" in response.json["message"]

        # 检查 session 是否已被清除
        with client.session_transaction() as flask_session:
            assert 'user_id' not in flask_session
            assert 'username' not in flask_session
            assert 'role_id' not in flask_session
