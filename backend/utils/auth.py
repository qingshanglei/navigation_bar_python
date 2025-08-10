from flask_jwt_extended import get_jwt, get_jwt_identity

# 统一从认证路由导入黑名单，避免重复定义
try:
    from routes.auth import blacklisted_tokens
except Exception:
    # 兜底：如果导入失败，仍保证变量存在，避免运行期错误
    blacklisted_tokens = set()


def _get_user_model():
    # 延迟导入，避免循环依赖
    from models.user_simple import User
    return User


def validate_token():
    """验证当前请求的JWT是否有效，并返回用户对象
    :return: (True, user) | (False, error_msg)
    """
    jti = get_jwt().get("jti")
    if jti and jti in blacklisted_tokens:
        return False, "Token已失效，请重新登录"

    User = _get_user_model()
    user = User.get(get_jwt_identity())
    if not user:
        return False, "用户不存在"

    return True, user
