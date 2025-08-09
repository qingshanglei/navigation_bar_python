from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import os
import re

app = Flask(__name__)

# 配置
app.config['JWT_SECRET_KEY'] = 'navigation-jwt-secret-key-2025'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SECRET_KEY'] = 'navigation-secret-key-2025'

# 初始化扩展
jwt = JWTManager(app)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:8080'])

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')

# 用于存储已注销的token
blacklisted_tokens = set()

def init_database():
    """初始化数据库"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # 检查是否存在管理员用户
    cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        # 创建默认管理员用户
        password_hash = generate_password_hash('123456')
        created_at = datetime.utcnow().isoformat()
        cursor.execute(
            'INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)',
            ('admin', password_hash, created_at)
        )
        print("创建默认管理员用户: admin / 123456")
    
    conn.commit()
    conn.close()

def get_user_by_username(username):
    """根据用户名获取用户"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, username, password, created_at FROM users WHERE username = ?',
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'username': row[1],
            'password': row[2],
            'created_at': row[3]
        }
    return None

def get_user_by_id(user_id):
    """根据ID获取用户"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, username, password, created_at FROM users WHERE id = ?',
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'username': row[1],
            'password': row[2],
            'created_at': row[3]
        }
    return None

def validate_input(data, required_fields):
    """验证输入参数"""
    if not data:
        return False, "请求数据不能为空"
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"{field}不能为空"
    
    return True, None

def validate_username(username):
    """验证用户名格式"""
    if len(username) < 3 or len(username) > 50:
        return False, "用户名长度必须在3-50个字符之间"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "用户名只能包含字母、数字和下划线"
    
    return True, None

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

# 路由
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

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.get_json()
        
        # 验证输入参数
        is_valid, error_msg = validate_input(data, ['username', 'password'])
        if not is_valid:
            return jsonify({
                'code': 0,
                'msg': error_msg,
                'data': None
            }), 400
        
        username = data['username'].strip()
        password = data['password']
        remember_me = data.get('remember_me', False)
        
        # 验证用户名格式
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            return jsonify({
                'code': 0,
                'msg': error_msg,
                'data': None
            }), 400
        
        # 查找用户
        user = get_user_by_username(username)
        if not user:
            return jsonify({
                'code': 0,
                'msg': '用户名或密码错误',
                'data': None
            }), 401
        
        # 验证密码
        if not check_password_hash(user['password'], password):
            return jsonify({
                'code': 0,
                'msg': '用户名或密码错误',
                'data': None
            }), 401
        
        # 设置token过期时间
        expires_delta = timedelta(days=7) if remember_me else timedelta(hours=24)
        access_token = create_access_token(
            identity=user['id'],
            expires_delta=expires_delta
        )
        
        # 计算过期时间
        expires_at = datetime.utcnow() + expires_delta
        
        return jsonify({
            'code': 1,
            'msg': '登录成功',
            'data': {
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'created_at': user['created_at']
                },
                'token': {
                    'access_token': access_token,
                    'token_type': 'Bearer',
                    'expires_in': int(expires_delta.total_seconds()),
                    'expires_at': expires_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        }), 200
        
    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({
            'code': 0,
            'msg': '服务器内部错误',
            'data': None
        }), 500

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出接口"""
    try:
        # 获取当前token的jti（JWT ID）
        jti = get_jwt()['jti']
        # 将token加入黑名单
        blacklisted_tokens.add(jti)
        
        return jsonify({
            'code': 1,
            'msg': '登出成功',
            'data': None
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 0,
            'msg': '登出失败',
            'data': None
        }), 500

@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def profile():
    """获取用户信息"""
    try:
        # 检查token是否在黑名单中
        jti = get_jwt()['jti']
        if jti in blacklisted_tokens:
            return jsonify({
                'code': 0,
                'msg': '令牌已失效，请重新登录',
                'data': None
            }), 401
        
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'code': 0,
                'msg': '用户不存在',
                'data': None
            }), 404
        
        return jsonify({
            'code': 1,
            'msg': '获取用户信息成功',
            'data': {
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'created_at': user['created_at']
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 0,
            'msg': '获取用户信息失败',
            'data': None
        }), 500

@app.route('/api/auth/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """验证令牌有效性"""
    try:
        # 检查token是否在黑名单中
        jti = get_jwt()['jti']
        if jti in blacklisted_tokens:
            return jsonify({
                'code': 0,
                'msg': '令牌已失效',
                'data': None
            }), 401
        
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'code': 0,
                'msg': '用户不存在',
                'data': None
            }), 404
        
        return jsonify({
            'code': 1,
            'msg': '令牌有效',
            'data': {
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'created_at': user['created_at']
                },
                'valid': True
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 0,
            'msg': '令牌验证失败',
            'data': None
        }), 500

if __name__ == '__main__':
    print("=" * 50)
    print("导航系统后端服务")
    print("=" * 50)
    
    # 初始化数据库
    init_database()
    
    print("\n服务信息:")
    print("- API地址: http://localhost:5000")
    print("- 健康检查: http://localhost:5000/api/health")
    print("- 登录接口: http://localhost:5000/api/auth/login")
    print("- 用户信息: http://localhost:5000/api/auth/profile")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 50)
    
    # 启动服务
    app.run(debug=False, host='0.0.0.0', port=5000)
