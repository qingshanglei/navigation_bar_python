#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建数据库表并插入默认数据
"""

from app import create_app
from models.user_simple import User
from models.category import Category
import os

def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        try:
            # 创建用户表
            User.create_table()
            print("用户表创建成功")
            
            # 创建分类表
            Category.create_table()
            print("分类表创建成功")
            
            # 检查是否已存在admin用户
            existing_admin = User.query().filter_by(username='admin').first()
            if not existing_admin:
                # 创建默认管理员用户
                admin_user = User(username='admin')
                admin_user.set_password('123456')
                admin_user.save()
                print("默认管理员用户创建成功")
            else:
                print("管理员用户已存在")
            
            print("\n数据库初始化完成！")
            print("默认管理员账户：")
            print("  用户名: admin")
            print("  密码: 123456")
            print("请及时修改默认密码！")
            
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            raise

if __name__ == '__main__':
    init_database()
