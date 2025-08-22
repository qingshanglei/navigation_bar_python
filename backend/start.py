#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导航系统后端启动脚本
"""

from app import create_app, db
from models.user_simple import User
import os

def ensure_admin_user():
    """确保管理员用户存在"""
    # 先创建表
    User.create_table()
    
    # 创建分类表
    from models.category import Category
    Category.create_table()
    
    admin = User.query().filter_by(username='admin').first()
    if not admin:
        print("创建默认管理员用户...")
        admin = User(username='admin')
        admin.set_password('123456')
        admin.save()
        print("管理员用户创建成功！")
        print("用户名: admin")
        print("密码: 123456")
        print("请及时修改默认密码！")
    else:
        print("管理员用户已存在")

def main():
    """主函数"""
    print("=" * 50)
    print("导航系统后端服务")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # 确保数据库表存在
        db.create_all()
        
        # 确保管理员用户存在
        ensure_admin_user()
    
    print("\n服务信息:")
    print("- API地址: http://localhost:5000")
    print("- 健康检查: http://localhost:5000/api/health")
    print("- 登录接口: http://localhost:5000/api/auth/login")
    print("- 用户信息: http://localhost:5000/api/auth/profile")
  


    print("\n按 Ctrl+C 停止服务")
    print("=" * 50)
    
    # 启动服务
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
