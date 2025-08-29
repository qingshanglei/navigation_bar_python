from flask import Flask, jsonify, send_from_directory,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
import os

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    
    # 配置CORS
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']))
    
    # JWT错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'code': 0,
            'msg': '令牌已过期，请重新登录',
            'data': None
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'code': 0,
            'msg': '无效的令牌',
            'data': None
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'code': 0,
            'msg': '缺少认证令牌',
            'data': None
        }), 401
    
    # 注册蓝图
    from routes.auth import auth_bp
    from routes.api import api_bp
    from routes.navigation import nav_bp
    from routes.categories import categories_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth') # 认证接口
    app.register_blueprint(api_bp, url_prefix='/api') # API接口
    app.register_blueprint(nav_bp, url_prefix='/admin/navs') # 导航接口
    app.register_blueprint(categories_bp, url_prefix='/admin/categories') # 分类接口
    
    # 添加根路径路由
    @app.route('/')
    def index():
          return redirect('/admin/login.html')
    
    # 添加健康检查接口
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'code': 1,
            'msg': '服务正常运行',
            'data': {
                'status': 'healthy',
                'service': 'navigation-backend'
            }
        }), 200
    
 
    
    # 静态文件服务路由
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    admin_dir = os.path.join(project_root, 'admin')
    web_dir = os.path.join(project_root, 'web')
    
    # 管理后台静态文件路由
    @app.route('/admin/<path:filename>')
    def admin_static(filename):
        try:
            return send_from_directory(admin_dir, filename)
        except Exception as e:
            app.logger.error(f'Error serving admin file {filename}: {e}')
            return jsonify({'code': 0, 'msg': f'File not found: {filename}', 'data': None}), 404
    
    # 前端静态文件路由
    @app.route('/web/<path:filename>')
    def web_static(filename):
        try:
            return send_from_directory(web_dir, filename)
        except Exception as e:
            app.logger.error(f'Error serving web file {filename}: {e}')
            return jsonify({'code': 0, 'msg': f'File not found: {filename}', 'data': None}), 404
    
    # 创建数据库表
    with app.app_context():
        # 确保实例目录存在
        instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
        if not os.path.exists(instance_dir):
            os.makedirs(instance_dir)
        
        db.create_all()
        # 兼容原生SQL模型：确保表存在
        try:
            from models.category import Category
            from models.navs import Nav
            Category.create_table()
            Nav.create_table()
        except Exception as e:
            app.logger.error(f"原生SQL表创建失败: {e}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("导航系统后端服务启动中...")
    print("API地址: http://localhost:5000")
    print("健康检查: http://localhost:5000/api/health")
    print("- 管理端登录页: http://localhost:5000/admin/login.html")
    print("- 管理端首页: http://localhost:5000/admin/dashboard.html")
    print("- 用户端登录页: http://localhost:5000/web/login.html")
    print("- 用户端首页: http://localhost:5000/web/index.html")
    app.run(debug=False, host='0.0.0.0', port=5000)