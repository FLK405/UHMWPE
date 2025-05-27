# app/services/auth_service.py
# 用户认证服务，处理注册、登录、登出等逻辑

from app.models.user_model import UserModel
from app.models.role_model import RoleModel
from app import db # 导入 SQLAlchemy 实例
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session # 导入 Flask session 用于会话管理

class AuthService:
    """
    提供用户认证相关服务的类。
    """

    @staticmethod
    def register_user(username, password, role_id, full_name=None, email=None):
        """
        注册新用户。
        :param username: 用户名
        :param password: 明文密码
        :param role_id: 角色ID
        :param full_name: 用户全名 (可选)
        :param email: 用户邮箱 (可选)
        :return: (success: bool, message: str, user: UserModel/None)
        """
        # 检查用户名是否已存在
        if UserModel.find_by_username(username):
            return False, f"用户名 '{username}' 已存在。", None

        # 检查邮箱是否已存在 (如果提供)
        if email and UserModel.find_by_email(email):
            return False, f"邮箱 '{email}' 已被注册。", None

        # 检查角色是否存在
        role = RoleModel.find_by_id(role_id)
        if not role:
            return False, f"角色ID '{role_id}' 不存在。", None

        new_user = UserModel(
            用户名=username,
            角色ID=role_id,
            全名=full_name,
            邮箱=email
        )
        new_user.set_password(password) # 设置哈希密码

        try:
            new_user.save_to_db()
            return True, "用户注册成功。", new_user
        except Exception as e:
            db.session.rollback() # 发生错误时回滚
            # TODO: 更详细的日志记录
            print(f"注册用户时发生错误: {e}")
            return False, f"注册用户时发生内部错误: {str(e)}", None

    @staticmethod
    def login_user(username, password):
        """
        用户登录。
        :param username: 用户名
        :param password: 密码
        :return: (success: bool, message: str, user_data: dict/None)
        """
        user = UserModel.find_by_username(username)

        if user and user.是否启用 and user.check_password(password):
            # 登录成功，在 session 中存储用户信息
            session['user_id'] = user.用户ID
            session['username'] = user.用户名
            session['role_id'] = user.角色ID
            # session.permanent = True # 可以设置 session 的持久性

            user_data = user.to_dict(include_role=True) # 获取用户信息字典
            return True, "登录成功。", user_data
        elif user and not user.是否启用:
            return False, "用户账户已被禁用。", None
        else:
            return False, "用户名或密码无效。", None

    @staticmethod
    def logout_user():
        """
        用户登出。
        清除 session 中的用户信息。
        :return: (success: bool, message: str)
        """
        # 从 session 中移除用户信息
        session.pop('user_id', None)
        session.pop('username', None)
        session.pop('role_id', None)
        # session.clear() # 或者直接清除整个 session

        return True, "登出成功。"

    @staticmethod
    def get_current_user_id():
        """
        从session中获取当前登录用户的ID。
        :return: 用户ID 或 None
        """
        return session.get('user_id')

    @staticmethod
    def get_current_user():
        """
        从session中获取当前登录用户对象。
        :return: UserModel 实例 或 None
        """
        user_id = session.get('user_id')
        if user_id:
            return UserModel.find_by_id(user_id)
        return None

# 可以在这里添加其他辅助函数，例如 token 生成与验证 (如果使用 JWT)
# from flask_jwt_extended import create_access_token (示例)
# def generate_jwt_token(user_id):
#     return create_access_token(identity=user_id)
