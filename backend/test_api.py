#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API接口测试脚本
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def test_health():
    """测试健康检查接口"""
    print("=" * 50)
    print("测试健康检查接口")
    print("=" * 50)
    
    try:
        response = requests.get(f'{BASE_URL}/api/health')
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_login(username='admin', password='123456', remember_me=True):
    """测试登录接口"""
    print("=" * 50)
    print("测试登录接口")
    print("=" * 50)
    
    try:
        data = {
            'username': username,
            'password': password,
            'remember_me': remember_me
        }
        
        response = requests.post(
            f'{BASE_URL}/api/auth/login',
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 1:
                return result['data']['token']['access_token']
        
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None

def test_profile(token):
    """测试获取用户信息接口"""
    print("=" * 50)
    print("测试获取用户信息接口")
    print("=" * 50)
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f'{BASE_URL}/api/auth/profile', headers=headers)
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_verify_token(token):
    """测试验证令牌接口"""
    print("=" * 50)
    print("测试验证令牌接口")
    print("=" * 50)
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f'{BASE_URL}/api/auth/verify', headers=headers)
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_logout(token):
    """测试登出接口"""
    print("=" * 50)
    print("测试登出接口")
    print("=" * 50)
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(f'{BASE_URL}/api/auth/logout', headers=headers)
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_register(username='testuser', password='123456'):
    """测试注册接口"""
    print("=" * 50)
    print("测试注册接口")
    print("=" * 50)
    
    try:
        data = {
            'username': username,
            'password': password
        }
        
        response = requests.post(
            f'{BASE_URL}/api/auth/register',
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    """主测试函数"""
    print("导航系统后端API测试")
    print("请确保后端服务已启动 (python start.py)")
    print()
    
    # 测试健康检查
    if not test_health():
        print("健康检查失败，请检查后端服务是否启动")
        return
    
    # 测试登录
    token = test_login()
    if not token:
        print("登录测试失败")
        return
    
    print(f"\n获取到的令牌: {token[:50]}...")
    
    # 测试获取用户信息
    test_profile(token)
    
    # 测试验证令牌
    test_verify_token(token)
    
    # 测试注册（可选）
    test_register('testuser2', '123456')
    
    # 测试登出
    test_logout(token)
    
    # 验证登出后令牌失效
    print("\n验证登出后令牌是否失效:")
    test_profile(token)
    
    print("\n" + "=" * 50)
    print("API测试完成")
    print("=" * 50)

if __name__ == '__main__':
    main()
