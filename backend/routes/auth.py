from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
import re

# 延迟导入避免循环导入
def get_db():
    from flask import current_app
    return current_app.extensions['sqlalchemy']

def get_user_model():
    from models.user_simple import User
    return User

auth_bp = Blueprint('auth', __name__)

# 用于存储已注销的token（简单实现，生产环境建议使用Redis）
blacklisted_tokens = set()

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

def validate_password(password):
    """验证密码格式"""
    if len(password) < 6:
        return False, "密码长度不能少于6个字符"
    
    return True, None

@auth_bp.route('/login', methods=['POST'])
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
        User = get_user_model()
        user = User.query().filter_by(username=username).first()
        if not user:
            return jsonify({
                'code': 0,
                'msg': '用户名或密码错误',
                'data': None
            }), 401
        
        # 验证密码
        if not user.check_password(password):
            return jsonify({
                'code': 0,
                'msg': '用户名或密码错误',
                'data': None
            }), 401
        
        # 设置token过期时间
        expires_delta = timedelta(days=7) if remember_me else timedelta(hours=24)
        access_token = create_access_token(
            identity=user.id,
            expires_delta=expires_delta
        )
        
        # 计算过期时间
        expires_at = datetime.utcnow() + expires_delta
        
        return jsonify({
            'code': 1,
            'msg': '登录成功',
            'data': {
                'user': user.to_dict(),
                'token': {
                    'access_token': access_token,
                    'token_type': 'Bearer',
                    'expires_in': int(expires_delta.total_seconds()),
                    'expires_at': expires_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        }), 200
        
    except Exception as e:
        import traceback
        print(f"登录错误: {e}")  # 添加调试信息
        print("详细错误信息:")
        traceback.print_exc()
        return jsonify({
            'code': 0,
            'msg': '服务器内部错误',
            'data': None
        }), 500

@auth_bp.route('/logout', methods=['POST'])
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

@auth_bp.route('/profile', methods=['GET'])
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
        User = get_user_model()
        user = User.get(user_id)
        
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
                'user': user.to_dict()
            }
        }), 200
        
    except Exception as e:
        print(f"获取用户信息错误: {e}")  # 添加调试信息
        return jsonify({
            'code': 0,
            'msg': '获取用户信息失败',
            'data': None
        }), 500

@auth_bp.route('/verify', methods=['GET'])
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

        # 验证用户是否存在
        user_id = get_jwt_identity()
        User = get_user_model()
        user = User.get(user_id)
        
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
                'user': user.to_dict()
            }
        }), 200
        
    except Exception as e:
        print(f"验证令牌错误: {e}")  # 添加调试信息
        return jsonify({
            'code': 0,
            'msg': '令牌验证失败',
            'data': None
        }), 500

@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    """用户注册接口（管理员功能）"""
    try:
        # 检查当前用户是否为管理员
        current_user_id = get_jwt_identity()
        User = get_user_model()
        current_user = User.get(current_user_id)
        
        if not current_user or current_user.username != 'admin':
            return jsonify({
                'code': 0,
                'msg': '权限不足，只有管理员可以注册新用户',
                'data': None
            }), 403
        
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
        email = data.get('email', '').strip()
        
        # 验证用户名格式
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            return jsonify({
                'code': 0,
                'msg': error_msg,
                'data': None
            }), 400
        
        # 验证密码格式
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({
                'code': 0,
                'msg': error_msg,
                'data': None
            }), 400
        
        # 检查用户名是否已存在
        existing_user = User.query().filter_by(username=username).first()
        if existing_user:
            return jsonify({
                'code': 0,
                'msg': '用户名已存在',
                'data': None
            }), 409
        
        # 创建新用户
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        if new_user.save():
            return jsonify({
                'code': 1,
                'msg': '用户注册成功',
                'data': {
                    'user': new_user.to_dict()
                }
            }), 201
        else:
            return jsonify({
                'code': 0,
                'msg': '用户注册失败',
                'data': None
            }), 500
        
    except Exception as e:
        print(f"注册错误: {e}")  # 添加调试信息
        return jsonify({
            'code': 0,
            'msg': '服务器内部错误',
            'data': None
        }), 500
