# app/models/module_model.py
# 系统功能模块数据模型定义

from app import db # 从 app 包导入 SQLAlchemy 实例
from sqlalchemy import func # 导入 func 用于数据库函数

class ModuleModel(db.Model):
    """
    模块表 (ModulesTable) 的 SQLAlchemy 模型。
    存储系统功能模块信息。
    """
    __tablename__ = '模块表'  # 指定表名，与 DDL 脚本一致

    模块ID = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='模块唯一标识符，自增')
    模块名称 = db.Column(db.String(100), nullable=False, unique=True, comment='模块名称 (例如: "材料管理", "纤维性能")')
    模块路由 = db.Column(db.String(255), nullable=True, comment='模块前端路由 (例如: "/materials", "/fiber-performance")')
    父模块ID = db.Column(db.Integer, db.ForeignKey('模块表.模块ID'), nullable=True, comment='父模块ID，用于层级结构 (例如导航菜单)')
    创建时间 = db.Column(db.DateTime, nullable=False, server_default=func.now(), comment='记录创建时间，默认为当前时间')
    更新时间 = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment='记录更新时间，默认为当前时间，并在更新时自动更新')

    # Self-referential relationship for parent/child modules
    # 子模块列表
    children = db.relationship(
        'ModuleModel',
        backref=db.backref('parent', remote_side=[模块ID]), # 'parent' 是在子模块实例上访问父模块的属性
        lazy='dynamic', # 子模块集合将作为查询对象返回
        cascade='all, delete-orphan' # 如果父模块被删除，其子模块也将被删除
    )

    # Relationship to RolePermissionModel - 一个模块可以关联多个角色权限记录
    permissions = db.relationship('RolePermissionModel', back_populates='module', lazy='dynamic', foreign_keys='RolePermissionModel.模块ID')


    def __repr__(self):
        return f"<ModuleModel 模块ID={self.模块ID}, 模块名称='{self.模块名称}', 父模块ID={self.父模块ID}>"

    @classmethod
    def find_by_id(cls, module_id):
        """
        根据模块ID查找模块。
        :param module_id: 模块ID
        :return: ModuleModel 实例或 None
        """
        return cls.query.get(module_id)

    @classmethod
    def find_by_name(cls, module_name):
        """
        根据模块名称查找模块。
        :param module_name: 模块名称
        :return: ModuleModel 实例或 None
        """
        return cls.query.filter_by(模块名称=module_name).first()

    @classmethod
    def find_by_route(cls, route):
        """
        根据模块路由查找模块。
        :param route: 模块路由
        :return: ModuleModel 实例或 None
        """
        if route:
            return cls.query.filter_by(模块路由=route).first()
        return None
        
    @classmethod
    def get_all_modules(cls):
        """
        获取所有模块的列表。
        :return: List[ModuleModel]
        """
        return cls.query.all()

    def save_to_db(self):
        """
        将当前模块实例保存到数据库。
        """
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """
        从数据库中删除当前模块实例。
        这将级联删除子模块和相关的角色权限记录 (如果数据库层面设置了级联或模型中定义了)。
        """
        db.session.delete(self)
        db.session.commit()

    def to_dict(self, include_children=False, include_parent=False):
        """
        将模块信息转换为字典。
        :param include_children: 是否包含子模块信息
        :param include_parent: 是否包含父模块信息
        :return: dict
        """
        data = {
            '模块ID': self.模块ID,
            '模块名称': self.模块名称,
            '模块路由': self.模块路由,
            '父模块ID': self.父模块ID,
            '创建时间': self.创建时间.isoformat() if self.创建时间 else None,
            '更新时间': self.更新时间.isoformat() if self.更新时间 else None,
        }
        if include_children:
            data['children'] = [child.to_dict(include_children=True) for child in self.children]
        
        if include_parent and self.parent: # 检查 self.parent 是否存在
            data['parent'] = {
                '模块ID': self.parent.模块ID,
                '模块名称': self.parent.模块名称
            }
        return data
