# app/models/role_permission_model.py
# 角色权限数据模型定义

from app import db # 从 app 包导入 SQLAlchemy 实例
from sqlalchemy import func # 导入 func 用于数据库函数
# 导入 RoleModel 和 ModuleModel 以建立关系 (确保这些文件已存在且模型已定义)
# from app.models.role_model import RoleModel # 在实际使用中，SQLAlchemy 会通过字符串名称解析关系
# from app.models.module_model import ModuleModel

class RolePermissionModel(db.Model):
    """
    角色权限表 (RolePermissionsTable) 的 SQLAlchemy 模型。
    存储角色对各个模块的操作权限。
    """
    __tablename__ = '角色权限表'  # 指定表名，与 DDL 脚本一致

    角色权限ID = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='角色权限唯一标识符，自增')
    角色ID = db.Column(db.Integer, db.ForeignKey('角色表.角色ID'), nullable=False, comment='外键，关联到角色表的角色ID')
    模块ID = db.Column(db.Integer, db.ForeignKey('模块表.模块ID'), nullable=False, comment='外键，关联到模块表的模块ID')
    允许读取 = db.Column(db.Boolean, nullable=False, default=False, comment='是否允许读取数据 (1: 是, 0: 否)，默认为0')
    允许写入 = db.Column(db.Boolean, nullable=False, default=False, comment='是否允许写入 (创建/更新) 数据 (1: 是, 0: 否)，默认为0')
    允许删除 = db.Column(db.Boolean, nullable=False, default=False, comment='是否允许删除数据 (1: 是, 0: 否)，默认为0')
    允许导入 = db.Column(db.Boolean, nullable=False, default=False, comment='是否允许导入数据 (1: 是, 0: 否)，默认为0')
    允许导出 = db.Column(db.Boolean, nullable=False, default=False, comment='是否允许导出数据 (1: 是, 0: 否)，默认为0')
    创建时间 = db.Column(db.DateTime, nullable=False, server_default=func.now(), comment='记录创建时间，默认为当前时间')
    更新时间 = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment='记录更新时间，默认为当前时间，并在更新时自动更新')

    # Relationships
    # 'RoleModel' 和 'ModuleModel' 是关联模型的类名
    # back_populates 用于双向关系，指明对方模型中对应的关系属性名
    role = db.relationship('RoleModel', backref=db.backref('permissions', lazy='dynamic', foreign_keys=[角色ID])) # 一个权限条目属于一个角色
    module = db.relationship('ModuleModel', back_populates='permissions', foreign_keys=[模块ID]) # 一个权限条目属于一个模块

    # 定义唯一约束，确保同一角色对同一模块只有一条权限记录
    __table_args__ = (db.UniqueConstraint('角色ID', '模块ID', name='UQ_角色权限表_角色ID_模块ID'),)

    def __repr__(self):
        return (f"<RolePermissionModel 角色权限ID={self.角色权限ID}, 角色ID={self.角色ID}, 模块ID={self.模块ID}, "
                f"读:{self.允许读取}, 写:{self.允许写入}, 删:{self.允许删除}>")

    @classmethod
    def get_permissions(cls, role_id, module_id):
        """
        根据角色ID和模块ID查询特定权限记录。
        :param role_id: 角色ID
        :param module_id: 模块ID
        :return: RolePermissionModel 实例或 None
        """
        return cls.query.filter_by(角色ID=role_id, 模块ID=module_id).first()

    @classmethod
    def get_permissions_for_role(cls, role_id):
        """
        获取指定角色的所有权限记录。
        :param role_id: 角色ID
        :return: List[RolePermissionModel]
        """
        return cls.query.filter_by(角色ID=role_id).all()

    def save_to_db(self):
        """
        将当前权限实例保存到数据库。
        """
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """
        从数据库中删除当前权限实例。
        """
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        """
        将权限信息转换为字典。
        """
        return {
            '角色权限ID': self.角色权限ID,
            '角色ID': self.角色ID,
            '模块ID': self.模块ID,
            '允许读取': self.允许读取,
            '允许写入': self.允许写入,
            '允许删除': self.允许删除,
            '允许导入': self.允许导入,
            '允许导出': self.允许导出,
            '创建时间': self.创建时间.isoformat() if self.创建时间 else None,
            '更新时间': self.更新时间.isoformat() if self.更新时间 else None,
        }

    ACTION_COLUMN_MAP = {
        'CanRead': '允许读取',
        'CanWrite': '允许写入',
        'CanDelete': '允许删除',
        'CanImport': '允许导入',
        'CanExport': '允许导出',
    }

    @classmethod
    def get_action_column_name(cls, action_name: str) -> str | None:
        """
        根据通用的操作名称 (如 'CanRead') 获取对应的数据库列名 (如 '允许读取')。
        :param action_name: 通用的操作名称 (例如 'CanRead', 'CanWrite')
        :return: 对应的列名字符串，如果未找到则返回 None
        """
        return cls.ACTION_COLUMN_MAP.get(action_name)
