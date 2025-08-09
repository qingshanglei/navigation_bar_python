#!/usr/bin/env python3
"""
测试登录功能的调试脚本
"""

from app import create_app
from models.user_simple import User
import traceback

def test_login():
    """测试登录逻辑"""
    app = create_app()
    
    with app.app_context():
        try:
            print("1. 测试用户查询...")
            user = User.query().filter_by(username='admin').first()
            if user:
                print(f"   找到用户: {user.username}, ID: {user.id}")
                print(f"   密码哈希: {user.password[:50]}...")
                
                print("2. 测试密码验证...")
                is_valid = user.check_password('123456')
                print(f"   密码验证结果: {is_valid}")
                
                if is_valid:
                    print("3. 测试token生成...")
                    from flask_jwt_extended import create_access_token
                    from datetime import timedelta
                    
                    access_token = create_access_token(
                        identity=user.id,
                        expires_delta=timedelta(hours=24)
                    )
                    print(f"   Token生成成功: {access_token[:50]}...")
                    
                else:
                    print("   密码验证失败！")
            else:
                print("   未找到admin用户！")
                
        except Exception as e:
            print(f"测试失败: {e}")
            print("详细错误信息:")
            traceback.print_exc()

if __name__ == '__main__':
    test_login()
