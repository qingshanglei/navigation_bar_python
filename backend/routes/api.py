from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

@api_bp.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': 'API服务运行正常'})

@api_bp.route('/')
def api_root():
    """API根接口"""
    return jsonify({
        'message': '导航系统API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'navigation': '/api/navs',
            'health': '/api/health'
        }
    })