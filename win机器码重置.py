#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows系统机器码重置工具
支持重置以下关键字段：
- telemetry.machineId
- telemetry.macMachineId  
- telemetry.sqmId
- telemetry.devDeviceId
- storage.serviceMachineId

使用方法：
1. 直接运行：python reset_machine_codes.py
2. 指定新ID：python reset_machine_codes.py <自定义ID>
"""

import os
import json
import uuid
import shutil
from datetime import datetime
import sys

class MachineCodeResetter:
    def __init__(self):
        # 目标文件路径
        self.storage_file = os.path.expanduser(
            r"C:\Users\%s\AppData\Roaming\Cursor\User\globalStorage\storage.json" % os.getenv('USERNAME')
        )
        
        # 需要重置的机器码字段列表
        self.target_fields = [
            "telemetry.machineId",   # 主机器码，32位十六进制字符串
            "telemetry.macMachineId",  # 主机器码   
            "telemetry.sqmId",   # 主机器码，标准 UUID 格式(带大括号)
            "telemetry.devDeviceId",  # 设备ID，32位十六进制字符串
            "storage.serviceMachineId"  # 服务机器码
        ]
        
        # 备份文件前缀
        self.backup_prefix = "storage_backup"
    
    def generate_random_uuid(self):
        """生成随机UUID"""
        return str(uuid.uuid4())
    
    def get_custom_id(self):
        """从命令行获取自定义ID"""
        return sys.argv[1] if len(sys.argv) > 1 else None
    
    def create_backup(self, file_path):
        """创建备份文件"""
        if not os.path.exists(file_path):
            print(f"⚠️  目标文件不存在: {file_path}")
            return None
            
        backup_name = f"{self.backup_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = os.path.join(os.path.dirname(file_path), backup_name)
        
        try:
            shutil.copy2(file_path, backup_path)
            print(f"✅ 备份已创建: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ 备份失败: {e}")
            return None
    
    def load_json_data(self, file_path):
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️  文件读取失败，将创建新文件: {e}")
            return {}
    
    def save_json_data(self, file_path, data):
        """保存JSON文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 文件保存失败: {e}")
            return False
    
    def reset_machine_codes(self, custom_id=None):
        """重置所有机器码"""
        print("🔧 开始重置机器码...")
        
        # 获取新的ID
        new_id = custom_id if custom_id else self.generate_random_uuid()
        
        # 检查目标文件
        if not os.path.exists(self.storage_file):
            print(f"⚠️  目标文件不存在，将创建: {self.storage_file}")
            data = {}
        else:
            data = self.load_json_data(self.storage_file)
        
        # 创建备份
        backup_path = self.create_backup(self.storage_file)
        
        # 记录修改前状态
        modified_fields = []
        for field in self.target_fields:
            old_value = data.get(field, "未设置")
            print(f"📋 {field}: {old_value} → {new_id}")
            data[field] = new_id
            modified_fields.append(field)
        
        # 保存修改
        if self.save_json_data(self.storage_file, data):
            print(f"✅ 成功重置 {len(modified_fields)} 个机器码字段")
            print(f"📁 配置文件: {self.storage_file}")
            if backup_path:
                print(f"💾 备份文件: {backup_path}")
            return True
        else:
            print("❌ 重置失败")
            return False
    
    def verify_reset(self):
        """验证重置结果"""
        print("\n🔍 验证重置结果...")
        
        if not os.path.exists(self.storage_file):
            print("❌ 配置文件不存在")
            return False
        
        data = self.load_json_data(self.storage_file)
        
        all_reset = True
        for field in self.target_fields:
            current_value = data.get(field)
            if current_value:
                print(f"✅ {field}: {current_value}")
            else:
                print(f"❌ {field}: 未找到")
                all_reset = False
        
        return all_reset
    
    def restore_from_backup(self, backup_file):
        """从备份恢复"""
        if not os.path.exists(backup_file):
            print(f"❌ 备份文件不存在: {backup_file}")
            return False
        
        try:
            shutil.copy2(backup_file, self.storage_file)
            print(f"✅ 已从备份恢复: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ 恢复失败: {e}")
            return False

def main():
    """主函数"""
    resetter = MachineCodeResetter()
    
    print("=" * 50)
    print("🔄 Cursor机器码重置工具")
    print("=" * 50)
    
    # 获取自定义ID
    custom_id = resetter.get_custom_id()
    if custom_id:
        print(f"🎯 使用自定义ID: {custom_id}")
    else:
        print("🎯 使用随机生成的UUID")
    
    # 执行重置
    success = resetter.reset_machine_codes(custom_id)
    
    if success:
        # 验证结果
        resetter.verify_reset()
        
        print("\n" + "=" * 50)
        print("📋 操作完成！请重启Cursor应用使更改生效")
        print("=" * 50)
    else:
        print("❌ 操作失败，请检查权限和文件路径")

if __name__ == "__main__":
    main()