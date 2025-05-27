# app/models/role_model.py
# 角色数据模型定义

from app import db # 从 app 包导入 SQLAlchemy 实例
from sqlalchemy import func # 导入 func 用于数据库函数，例如 GETDATE()

class RoleModel(db.Model):
    """
    角色表 (RolesTable) 的 SQLAlchemy 模型。
    存储系统中的用户角色信息。
    """
    __tablename__ = '角色表'  # 指定表名，与 DDL 脚本一致

    角色ID = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='角色唯一标识符，自增')
    角色名称 = db.Column(db.String(50), nullable=False, unique=True, comment='角色名称 (例如: "管理员", "研究员")')
    描述 = db.Column(db.String(255), nullable=True, comment='角色的详细描述')
    创建时间 = db.Column(db.DateTime, nullable=False, server_default=func.now(), comment='记录创建时间，默认为当前时间')
    更新时间 = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment='记录更新时间，默认为当前时间，并在更新时自动更新')

    # relationships - 定义与用户表的关系
    # 'User' 是关联的 UserModel 类的名称
    # back_populates 指明了在 UserModel 中对应的关系属性名称
    # lazy='dynamic' 表示关联对象在被访问时才从数据库加载，并返回一个查询对象，可以进一步过滤
    users = db.relationship('UserModel', back_populates='role', lazy='dynamic', foreign_keys='UserModel.角色ID')

    def __repr__(self):
        return f"<RoleModel 角色ID={self.角色ID}, 角色名称='{self.角色名称}'>"

    @classmethod
    def find_by_id(cls, role_id):
        """
        根据角色ID查找角色。
        :param role_id: 角色ID
        :return: RoleModel 实例或 None
        """
        return cls.query.get(role_id)

    @classmethod
    def find_by_name(cls, role_name):
        """
        根据角色名称查找角色。
        :param role_name: 角色名称
        :return: RoleModel 实例或 None
        """
        return cls.query.filter_by(角色名称=role_name).first()

    def save_to_db(self):
        """
        将当前角色实例保存到数据库。
        """
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """
        从数据库中删除当前角色实例。
        """
        db.session.delete(self)
        db.session.commit()
