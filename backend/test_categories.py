#!/usr/bin/env python3
"""
分类管理API测试脚本
"""

import requests
import json

class CategoryAPITest:
    def __init__(self):
        self.base_url = 'http://localhost:5000/api'
        self.token = None
        
    def login(self):
        """登录获取token"""
        url = f'{self.base_url}/auth/login'
        data = {
            'username': 'admin',
            'password': '123456'
        }
        
        try:
            response = requests.post(url, json=data)
            result = response.json()
            
            if result['code'] == 1:
                self.token = result['data']['token']['access_token']
                print("✅ 登录成功")
                return True
            else:
                print(f"❌ 登录失败: {result['msg']}")
                return False
        except Exception as e:
            print(f"❌ 登录请求失败: {e}")
            return False
    
    def get_headers(self):
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def test_create_category(self):
        """测试创建分类"""
        print("\n🧪 测试创建分类...")
        
        url = f'{self.base_url}/categories'
        data = {
            'name': '编程网站',
            'description': '编程相关的网站和工具',
            'sort_order': 1,
            'is_public': True
        }
        
        try:
            response = requests.post(url, json=data, headers=self.get_headers())
            result = response.json()
            
            if result['code'] == 1:
                print(f"✅ 创建分类成功: {result['data']['name']}")
                return result['data']['id']
            else:
                print(f"❌ 创建分类失败: {result['msg']}")
                return None
        except Exception as e:
            print(f"❌ 创建分类请求失败: {e}")
            return None
    
    def test_create_subcategory(self, parent_id):
        """测试创建子分类"""
        print("\n🧪 测试创建子分类...")
        
        url = f'{self.base_url}/categories'
        data = {
            'name': '前端开发',
            'description': '前端开发相关资源',
            'parent_id': parent_id,
            'sort_order': 1,
            'is_public': True
        }
        
        try:
            response = requests.post(url, json=data, headers=self.get_headers())
            result = response.json()
            
            if result['code'] == 1:
                print(f"✅ 创建子分类成功: {result['data']['name']}")
                return result['data']['id']
            else:
                print(f"❌ 创建子分类失败: {result['msg']}")
                return None
        except Exception as e:
            print(f"❌ 创建子分类请求失败: {e}")
            return None
    
    def test_get_categories(self):
        """测试获取分类列表"""
        print("\n🧪 测试获取分类列表...")
        
        url = f'{self.base_url}/categories'
        
        try:
            response = requests.get(url, headers=self.get_headers())
            result = response.json()
            
            if result['code'] == 1:
                print(f"✅ 获取分类列表成功，共 {len(result['data'])} 个分类")
                for category in result['data']:
                    print(f"   - {category['name']} (ID: {category['id']}, 层级: {category['level']})")
                return True
            else:
                print(f"❌ 获取分类列表失败: {result['msg']}")
                return False
        except Exception as e:
            print(f"❌ 获取分类列表请求失败: {e}")
            return False
    
    def test_get_categories_tree(self):
        """测试获取分类树"""
        print("\n🧪 测试获取分类树...")
        
        url = f'{self.base_url}/categories?tree=true'
        
        try:
            response = requests.get(url, headers=self.get_headers())
            result = response.json()
            
            if result['code'] == 1:
                print("✅ 获取分类树成功")
                self.print_tree(result['data'])
                return True
            else:
                print(f"❌ 获取分类树失败: {result['msg']}")
                return False
        except Exception as e:
            print(f"❌ 获取分类树请求失败: {e}")
            return False
    
    def print_tree(self, categories, level=0):
        """打印分类树"""
        for category in categories:
            indent = "  " * level
            print(f"{indent}├─ {category['name']} (ID: {category['id']})")
            if 'children' in category and category['children']:
                self.print_tree(category['children'], level + 1)
    
    def test_get_public_categories(self):
        """测试获取公开分类"""
        print("\n🧪 测试获取公开分类...")
        
        url = f'{self.base_url}/categories/public?tree=true'
        
        try:
            response = requests.get(url)  # 不需要token
            result = response.json()
            
            if result['code'] == 1:
                print("✅ 获取公开分类成功")
                self.print_tree(result['data'])
                return True
            else:
                print(f"❌ 获取公开分类失败: {result['msg']}")
                return False
        except Exception as e:
            print(f"❌ 获取公开分类请求失败: {e}")
            return False
    
    def test_update_category(self, category_id):
        """测试更新分类"""
        print(f"\n🧪 测试更新分类 (ID: {category_id})...")
        
        url = f'{self.base_url}/categories/{category_id}'
        data = {
            'name': '编程网站（已更新）',
            'description': '编程相关的网站和工具（已更新描述）',
            'sort_order': 2
        }
        
        try:
            response = requests.put(url, json=data, headers=self.get_headers())
            result = response.json()
            
            if result['code'] == 1:
                print(f"✅ 更新分类成功: {result['data']['name']}")
                return True
            else:
                print(f"❌ 更新分类失败: {result['msg']}")
                return False
        except Exception as e:
            print(f"❌ 更新分类请求失败: {e}")
            return False
    
    def test_delete_category(self, category_id):
        """测试删除分类"""
        print(f"\n🧪 测试删除分类 (ID: {category_id})...")
        
        url = f'{self.base_url}/categories/{category_id}'
        
        try:
            response = requests.delete(url, headers=self.get_headers())
            result = response.json()
            
            if result['code'] == 1:
                print("✅ 删除分类成功")
                return True
            else:
                print(f"❌ 删除分类失败: {result['msg']}")
                return False
        except Exception as e:
            print(f"❌ 删除分类请求失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始分类管理API测试")
        print("=" * 50)
        
        # 1. 登录
        if not self.login():
            return
        
        # 2. 创建根分类
        root_category_id = self.test_create_category()
        if not root_category_id:
            return
        
        # 3. 创建子分类
        sub_category_id = self.test_create_subcategory(root_category_id)
        
        # 4. 获取分类列表
        self.test_get_categories()
        
        # 5. 获取分类树
        self.test_get_categories_tree()
        
        # 6. 获取公开分类
        self.test_get_public_categories()
        
        # 7. 更新分类
        self.test_update_category(root_category_id)
        
        # 8. 再次获取分类树查看更新结果
        self.test_get_categories_tree()
        
        # 9. 删除子分类（必须先删除子分类）
        if sub_category_id:
            self.test_delete_category(sub_category_id)
        
        # 10. 删除根分类
        self.test_delete_category(root_category_id)
        
        # 11. 最终检查
        self.test_get_categories()
        
        print("\n" + "=" * 50)
        print("🎉 分类管理API测试完成")

if __name__ == '__main__':
    test = CategoryAPITest()
    test.run_all_tests()
