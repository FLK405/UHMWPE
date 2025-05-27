# app/services/rbac_service.py
# RBAC (Role-Based Access Control) 服务

from app.models.user_model import UserModel
from app.models.module_model import ModuleModel
from app.models.role_permission_model import RolePermissionModel
from app.services.auth_service import AuthService # 用于获取当前用户和角色信息

class RbacService:
    """
    提供基于角色的访问控制检查服务。
    """

    @staticmethod
    def check_permission(user_id: int, module_name: str, action: str) -> bool:
        """
        检查指定用户是否对特定模块拥有特定操作权限。

        :param user_id: 用户ID。
        :param module_name: 模块的名称 (例如: "纤维性能", "材料管理")。
        :param action: 需要检查的操作权限 (例如: "CanRead", "CanWrite", "CanDelete", "CanImport", "CanExport")。
                       这些操作名会映射到 RolePermissionModel 中的布尔字段。
        :return: True 如果用户拥有权限, False 否则。
        """
        if not user_id:
            # print("RBAC Check: 用户未登录或用户ID无效。") # 日志
            return False

        user = UserModel.find_by_id(user_id)
        if not user or not user.是否启用:
            # print(f"RBAC Check: 用户ID {user_id} 未找到或用户已禁用。") # 日志
            return False

        role_id = user.角色ID
        if not role_id:
            # print(f"RBAC Check: 用户 {user.用户名} (ID: {user_id}) 没有分配角色。") # 日志
            return False

        module = ModuleModel.find_by_name(module_name)
        if not module:
            # print(f"RBAC Check: 模块 '{module_name}' 未找到。") # 日志
            return False

        # 从 RolePermissionModel 获取对应的数据库列名
        permission_column_name = RolePermissionModel.get_action_column_name(action)
        if not permission_column_name:
            # print(f"RBAC Check: 未知的操作 '{action}'。无法映射到权限列。") # 日志
            return False

        # 查询角色权限记录
        permission_record = RolePermissionModel.get_permissions(role_id=role_id, module_id=module.模块ID)

        if not permission_record:
            # print(f"RBAC Check: 未找到角色ID {role_id} 对模块ID {module.模块ID} ('{module_name}') 的权限记录。") # 日志
            return False

        # 检查特定权限列的值
        # getattr 会获取 permission_record 对象的 permission_column_name 属性值
        has_permission = getattr(permission_record, permission_column_name, False)
        
        # print(f"RBAC Check: 用户 {user.用户名} (角色ID {role_id}), 模块 '{module_name}' (ID {module.模块ID}), "
        #       f"操作 '{action}' (列 '{permission_column_name}'): 结果 -> {has_permission}") # 详细日志

        return bool(has_permission) # 确保返回的是布尔值

    @staticmethod
    def get_user_permissions_for_module(user_id: int, module_name: str) -> dict:
        """
        获取用户对特定模块的所有权限设置。
        :param user_id: 用户ID
        :param module_name: 模块名称
        :return: 一个字典，键是操作名 (如 'CanRead'), 值是布尔型权限。如果模块或用户无效，返回空字典。
        """
        permissions_dict = {}
        if not user_id:
            return permissions_dict

        user = UserModel.find_by_id(user_id)
        if not user or not user.是否启用 or not user.角色ID:
            return permissions_dict

        module = ModuleModel.find_by_name(module_name)
        if not module:
            return permissions_dict
        
        permission_record = RolePermissionModel.get_permissions(role_id=user.角色ID, module_id=module.模块ID)
        if permission_record:
            for action, column_name in RolePermissionModel.ACTION_COLUMN_MAP.items():
                permissions_dict[action] = getattr(permission_record, column_name, False)
        
        return permissions_dict

    @staticmethod
    def get_all_user_permissions(user_id: int) -> dict:
        """
        获取用户对其角色允许的所有模块的所有权限。
        :param user_id: 用户ID
        :return: 字典，键是模块名称，值是该模块的权限字典 (同 get_user_permissions_for_module 返回)
        """
        all_perms = {}
        if not user_id:
            return all_perms

        user = UserModel.find_by_id(user_id)
        if not user or not user.是否启用 or not user.角色ID:
            return all_perms
        
        role_permissions = RolePermissionModel.get_permissions_for_role(user.角色ID)
        for perm_record in role_permissions:
            if perm_record.module: # 确保关联的模块存在
                module_name = perm_record.module.模块名称
                module_perms = {}
                for action, column_name in RolePermissionModel.ACTION_COLUMN_MAP.items():
                    module_perms[action] = getattr(perm_record, column_name, False)
                all_perms[module_name] = module_perms
        return all_perms
