# app/models/__init__.py
# 这个文件使得 "models" 目录成为一个Python包。
# 它也可以用来集中导入所有模型，方便其他模块引用，并确保SQLAlchemy能够发现它们。

# 导入各个模型类，以便SQLAlchemy和Flask-Migrate能够发现它们。
from .role_model import RoleModel
from .user_model import UserModel
from .module_model import ModuleModel
from .role_permission_model import RolePermissionModel
from .resin_spinning_model import ResinSpinningProcessModel # 新增模型导入

# 可以选择性地定义 __all__ 来控制 'from app.models import *' 的行为
# __all__ = [
#     'RoleModel',
#     'UserModel',
#     'ModuleModel',
#     'RolePermissionModel',
#     'ResinSpinningProcessModel' # 新增模型到 __all__
# ]

# 打印一条消息，表明模型包已加载 (可选，用于调试)
# print("数据库模型包 'app.models' 已加载。")
