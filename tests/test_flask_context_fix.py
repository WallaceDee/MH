#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Flask应用上下文修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app
from app.services.role_service import RoleService

def test_role_service_with_app_context():
    """测试在Flask应用上下文中使用角色服务"""
    print("=== 测试Flask应用上下文修复 ===")
    
    # 创建Flask应用
    app = create_app()
    
    with app.app_context():
        try:
            # 创建角色服务实例
            role_service = RoleService()
            print("✓ 角色服务实例创建成功")
            
            # 测试获取角色列表
            result = role_service.get_role_list(page=1, page_size=5)
            print(f"✓ 获取角色列表成功: {result.get('total', 0)} 条记录")
            
            # 测试获取角色详情（如果有数据）
            if result.get('data') and len(result['data']) > 0:
                first_role = result['data'][0]
                eid = first_role.get('eid')
                if eid:
                    detail = role_service.get_role_details(eid)
                    if detail:
                        print(f"✓ 获取角色详情成功: {eid}")
                    else:
                        print(f"⚠ 角色详情为空: {eid}")
            
            print("✓ 所有测试通过！Flask应用上下文修复成功")
            return True
            
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_role_service_without_app_context():
    """测试在Flask应用上下文外使用角色服务（应该失败）"""
    print("\n=== 测试Flask应用上下文外使用（应该失败）===")
    
    try:
        # 直接创建角色服务实例（没有应用上下文）
        role_service = RoleService()
        result = role_service.get_role_list(page=1, page_size=5)
        print("✗ 意外成功：应该失败但没有失败")
        return False
    except RuntimeError as e:
        if "必须在Flask应用上下文中使用数据库操作" in str(e):
            print("✓ 正确失败：必须在Flask应用上下文中使用数据库操作")
            return True
        else:
            print(f"✗ 错误的异常类型: {e}")
            return False
    except Exception as e:
        # 检查异常消息中是否包含我们期望的错误
        if "必须在Flask应用上下文中使用数据库操作" in str(e):
            print("✓ 正确失败：必须在Flask应用上下文中使用数据库操作")
            return True
        else:
            print(f"✗ 意外的异常: {e}")
            return False

if __name__ == "__main__":
    print("开始测试Flask应用上下文修复...")
    
    # 测试1：在应用上下文中使用
    success1 = test_role_service_with_app_context()
    
    # 测试2：在应用上下文外使用
    success2 = test_role_service_without_app_context()
    
    if success1 and success2:
        print("\n🎉 所有测试通过！Flask应用上下文问题已修复")
    else:
        print("\n❌ 部分测试失败，需要进一步修复")
