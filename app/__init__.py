# app/__init__.py
# 应用程序包构造文件

from flask import Flask
from flask_sqlalchemy import SQLAlchemy # 取消注释以使用SQLAlchemy
from flask_migrate import Migrate # 取消注释以使用Migrate

db = SQLAlchemy() # 取消注释以使用SQLAlchemy
migrate = Migrate() # 取消注释以使用Migrate

def create_app():
    """
    工厂函数，用于创建和配置Flask应用实例。
    """
    app = Flask(__name__)

    # 加载配置
    # 实际项目中，这些配置应该从环境变量或配置文件中加载
    app.config['SECRET_KEY'] = 'your_very_secret_key_here'  # 替换为强随机密钥
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://user:password@host/database?driver=ODBC+Driver+17+for+SQL+Server' # SQL Server连接字符串示例
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭不必要的 SQLAlchemy 事件通知

    # 初始化扩展
    db.init_app(app) # 取消注释以使用SQLAlchemy
    migrate.init_app(app, db) # 取消注释以使用Migrate

    # 注册蓝图
    from .routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .routes.resin_spinning_routes import resin_spinning_bp 
    app.register_blueprint(resin_spinning_bp, url_prefix='/api/resin-spinning')

    from .routes.attachment_routes import attachment_bp # 导入附件蓝图
    app.register_blueprint(attachment_bp, url_prefix='/api/attachments') # 注册附件蓝图

    # 可以添加更多的应用初始化代码，例如日志配置等

    @app.route('/hello')
    def hello():
        return '你好, Flask!'

    # Load instance config if it exists (for UPLOAD_FOLDER)
    app.config.from_pyfile('../instance/config.py', silent=True) # Go up one level to reach instance folder

    return app
