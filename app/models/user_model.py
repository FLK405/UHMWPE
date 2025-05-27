# app/models/user_model.py
# 用户数据模型定义

from app import db # 从 app 包导入 SQLAlchemy 实例
from app.models.role_model import RoleModel # 导入 RoleModel 以建立关系
from sqlalchemy import func # 导入 func 用于数据库函数
from werkzeug.security import generate_password_hash, check_password_hash # 用于密码哈希

class UserModel(db.Model):
    """
    用户表 (UsersTable) 的 SQLAlchemy 模型。
    存储系统的用户信息。
    """
    __tablename__ = '用户表' # 指定表名，与 DDL 脚本一致

    用户ID = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户唯一标识符，自增')
    用户名 = db.Column(db.String(100), nullable=False, unique=True, comment='用户登录名，唯一且不为空')
    密码哈希 = db.Column(db.String(255), nullable=False, comment='存储用户密码的哈希值，不为空')
    角色ID = db.Column(db.Integer, db.ForeignKey('角色表.角色ID'), nullable=False, comment='外键，关联到角色表的角色ID')
    全名 = db.Column(db.String(100), nullable=True, comment='用户全名')
    邮箱 = db.Column(db.String(100), nullable=True, unique=True, comment='用户邮箱，唯一')
    是否启用 = db.Column(db.Boolean, nullable=False, default=True, comment='账户是否启用 (1: 是, 0: 否)，默认为1')
    创建时间 = db.Column(db.DateTime, nullable=False, server_default=func.now(), comment='记录创建时间，默认为当前时间')
    更新时间 = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment='记录更新时间，默认为当前时间，并在更新时自动更新')

    # relationships - 定义与角色表的关系
    # 'RoleModel' 是关联的 RoleModel 类的名称
    # back_populates 指明了在 RoleModel 中对应的关系属性名称
    role = db.relationship('RoleModel', back_populates='users', foreign_keys=[角色ID])

    def __repr__(self):
        return f"<UserModel 用户ID={self.用户ID}, 用户名='{self.用户名}', 角色ID={self.角色ID}>"

    def set_password(self, password):
        """
        设置用户密码，存储哈希值。
        :param password: 明文密码
        """
        self.密码哈希 = generate_password_hash(password)

    def check_password(self, password):
        """
        校验用户密码。
        :param password: 明文密码
        :return: True 如果密码匹配, False 否则
        """
        return check_password_hash(self.密码哈希, password)

    @classmethod
    def find_by_username(cls, username):
        """
        根据用户名查找用户。
        :param username: 用户名
        :return: UserModel 实例或 None
        """
        return cls.query.filter_by(用户名=username).first()

    @classmethod
    def find_by_id(cls, user_id):
        """
        根据用户ID查找用户。
        :param user_id: 用户ID
        :return: UserModel 实例或 None
        """
        return cls.query.get(user_id)

    @classmethod
    def find_by_email(cls, email):
        """
        根据邮箱查找用户。
        :param email: 邮箱
        :return: UserModel 实例或 None
        """
        if email: # 确保 email 不是 None 或空字符串
            return cls.query.filter_by(邮箱=email).first()
        return None

    def save_to_db(self):
        """
        将当前用户实例保存到数据库。
        如果角色不存在，则不允许保存。
        """
        # 检查角色是否存在
        if self.角色ID:
            role = RoleModel.find_by_id(self.角色ID)
            if not role:
                raise ValueError(f"角色ID {self.角色ID} 不存在。")
        else:
            raise ValueError("用户的角色ID不能为空。")

        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """
        从数据库中删除当前用户实例。
        """
        db.session.delete(self)
        db.session.commit()

    def to_dict(self, include_role=False):
        """
        将用户信息转换为字典，可选包含角色信息。
        不包含密码哈希。
        """
        data = {
            '用户ID': self.用户ID,
            '用户名': self.用户名,
            '角色ID': self.角色ID,
            '全名': self.全名,
            '邮箱': self.邮箱,
            '是否启用': self.是否启用,
            '创建时间': self.创建时间.isoformat() if self.创建时间 else None,
            '更新时间': self.更新时间.isoformat() if self.更新时间 else None,
        }
        if include_role and self.role:
            data['角色'] = {
                '角色ID': self.role.角色ID,
                '角色名称': self.role.角色名称
            }
        return data
