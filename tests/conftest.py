# tests/conftest.py
# Pytest配置文件，用于定义通用的测试 fixtures

import pytest
from app import create_app, db
from app.models import UserModel, RoleModel, ModuleModel, RolePermissionModel
# 确保所有模型都被导入，以便 db.create_all() 能够创建它们
# from app.models.user_model import UserModel
# from app.models.role_model import RoleModel
# from app.models.module_model import ModuleModel
# from app.models.role_permission_model import RolePermissionModel

@pytest.fixture(scope='session')
def app():
    """
    Session-wide test Flask application.
    创建一个配置为测试环境的Flask应用实例。
    使用SQLite内存数据库以加速测试并隔离测试环境。
    """
    # print("Creating Flask app for testing session...")
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # 使用内存SQLite数据库进行测试
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False, # 在测试中通常禁用CSRF保护
        "SECRET_KEY": "test-secret-key", # 测试用的密钥
        # "SERVER_NAME": "localhost.localdomain" # 如果需要 URL 生成 (如 url_for)
    })
    # print(f"App configured for testing with DB: {app.config['SQLALCHEMY_DATABASE_URI']}")
    return app

@pytest.fixture(scope='session')
def _db(app):
    """
    Session-wide database fixture.
    在测试会话开始时创建所有数据库表，在会话结束时删除它们。
    """
    # print("Setting up database for testing session...")
    with app.app_context():
        # print("Creating all tables...")
        db.create_all()
        # print("Tables created.")
    
    yield db # 提供 db 实例给测试使用

    # print("Tearing down database after testing session...")
    with app.app_context():
        # print("Dropping all tables...")
        db.drop_all()
        # print("Tables dropped.")

@pytest.fixture
def client(app, _db): # _db fixture ensures database is set up
    """
    Function-scope test client.
    为每个测试函数提供一个Flask测试客户端。
    """
    # print("Creating test client for a test function...")
    with app.test_client() as client:
        with app.app_context(): # 确保在请求上下文中
             # print("Test client and app context ready.")
            yield client
    # print("Test client finished.")

@pytest.fixture
def db_session(app, _db): # Renamed from `database` to avoid conflict if a test needs `db` directly
    """
    Function-scope database session management.
    在每个测试函数开始前清理数据库表中的数据，确保测试隔离。
    这比每次都 drop_all/create_all 更快。
    """
    # print("Setting up clean DB tables for a test function...")
    with app.app_context():
        # 清空所有表中的数据，而不是删除表结构
        # 这种方法更快，但依赖于 _db fixture 已经创建了表
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            # print(f"Clearing table {table.name}...")
            db.session.execute(table.delete())
        db.session.commit()
        # print("All tables cleared.")
    yield _db.session # 提供 SQLAlchemy session 给测试使用
    # print("DB session for test function finished.")


# --- Test Data Setup Fixtures ---

@pytest.fixture
def basic_roles(db_session):
    """
    创建一些基本的角色用于测试。
    :return: 创建的角色字典，键为角色名
    """
    # print("Creating basic roles...")
    roles_data = {
        "Admin": {"描述": "管理员角色"},
        "Researcher": {"描述": "研究员角色"},
        "Guest": {"描述": "访客角色"}
    }
    created_roles = {}
    for name, data in roles_data.items():
        role = RoleModel(角色名称=name, 描述=data["描述"])
        db_session.add(role)
        created_roles[name] = role
    db_session.commit()
    # print(f"Created roles: {[r.角色名称 for r in created_roles.values()]}")
    return created_roles

@pytest.fixture
def test_user(db_session, basic_roles):
    """
    创建一个测试用户，并赋予其 'Researcher' 角色。
    :return: 创建的 UserModel 实例
    """
    # print("Creating test user...")
    researcher_role = basic_roles.get("Researcher")
    if not researcher_role:
        researcher_role = RoleModel(角色名称="Researcher", 描述="研究员角色")
        db_session.add(researcher_role)
        db_session.commit()
        # print("Created 'Researcher' role on the fly for test_user.")

    user = UserModel(
        用户名="testuser",
        角色ID=researcher_role.角色ID,
        全名="测试用户",
        邮箱="testuser@example.com"
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    # print(f"Created test user: {user.用户名} with role ID {user.角色ID}")
    return user

@pytest.fixture
def basic_modules(db_session):
    """
    创建一些基本的模块用于测试。
    :return: 创建的模块字典，键为模块名
    """
    # print("Creating basic modules...")
    modules_data = {
        "UserData": {"模块路由": "/users", "父模块ID": None},
        "FiberData": {"模块路由": "/fibers", "父模块ID": None},
        "SystemSettings": {"模块路由": "/settings", "父模块ID": None},
        "前端树脂与纺丝工艺表": {"模块路由": "/resin-spinning", "父模块ID": None} # 新增模块
    }
    created_modules = {}
    for name, data in modules_data.items():
        module = ModuleModel(模块名称=name, 模块路由=data["模块路由"], 父模块ID=data["父模块ID"])
        db_session.add(module)
        created_modules[name] = module
    db_session.commit()
    # print(f"Created modules: {[m.模块名称 for m in created_modules.values()]}")
    return created_modules

@pytest.fixture
def researcher_permissions(db_session, basic_roles, basic_modules):
    """
    为 'Researcher' 角色设置 'FiberData' 模块的权限。
    允许读取和写入，不允许删除。
    """
    # print("Setting up researcher permissions...")
    researcher_role = basic_roles.get("Researcher")
    fiber_module = basic_modules.get("FiberData") # Existing permission for FiberData
    resin_spinning_module = basic_modules.get("前端树脂与纺丝工艺表")

    permissions_to_add = []

    if researcher_role and fiber_module:
        permissions_to_add.append(RolePermissionModel(
            角色ID=researcher_role.角色ID,
            模块ID=fiber_module.模块ID,
            允许读取=True,
            允许写入=True, # As per existing fixture logic
            允许删除=False,
            允许导入=False,
            允许导出=False
        ))
    
    if researcher_role and resin_spinning_module:
        permissions_to_add.append(RolePermissionModel(
            角色ID=researcher_role.角色ID,
            模块ID=resin_spinning_module.模块ID,
            允许读取=True,  # Researcher gets CanRead for the new module
            允许写入=False,
            允许删除=False,
            允许导入=False,
            允许导出=False
        ))

    if permissions_to_add:
        db_session.add_all(permissions_to_add)
        db_session.commit()
        # print(f"Permissions set for Researcher.")
    
    # Returning the first permission for consistency if some test relies on a single object,
    # though this fixture now potentially sets multiple. Consider returning a list or specific permission.
    return permissions_to_add[0] if permissions_to_add else None

@pytest.fixture
def admin_permissions(db_session, basic_roles, basic_modules):
    """
    为 'Admin' 角色设置 'UserData' 模块的完全权限。
    """
    # print("Setting up admin permissions...")
    admin_role = basic_roles.get("Admin")
    user_data_module = basic_modules.get("UserData") # Existing permission
    resin_spinning_module = basic_modules.get("前端树脂与纺丝工艺表")

    permissions_to_add = []

    if admin_role and user_data_module:
        permissions_to_add.append(RolePermissionModel(
            角色ID=admin_role.角色ID,
            模块ID=user_data_module.模块ID,
            允许读取=True,
            允许写入=True,
            允许删除=True,
            允许导入=True,
            允许导出=True
        ))

    if admin_role and resin_spinning_module:
        permissions_to_add.append(RolePermissionModel(
            角色ID=admin_role.角色ID,
            模块ID=resin_spinning_module.模块ID,
            允许读取=True,  # Full permissions for Admin on the new module
            允许写入=True,
            允许删除=True,
            允许导入=True,
            允许导出=True
        ))

    if permissions_to_add:
        db_session.add_all(permissions_to_add)
        db_session.commit()
        # print(f"Permissions set for Admin.")

    return permissions_to_add[0] if permissions_to_add else None
