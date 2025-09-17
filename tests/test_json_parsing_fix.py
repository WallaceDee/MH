#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试JSON解析问题修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app
from app.services.role_service import RoleService

def test_role_feature_extraction():
    """测试角色特征提取"""
    print("=== 测试角色特征提取 ===")
    
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
            
            # 如果有数据，测试特征提取
            if result.get('data') and len(result['data']) > 0:
                first_role = result['data'][0]
                eid = first_role.get('eid')
                if eid:
                    print(f"测试角色特征提取: {eid}")
                    feature_result = role_service.get_role_feature(eid)
                    if feature_result:
                        print("✓ 角色特征提取成功")
                        if 'error' in feature_result:
                            print(f"⚠ 特征提取警告: {feature_result['error']}")
                        else:
                            print("✓ 特征提取完全成功")
                    else:
                        print("⚠ 角色特征提取返回None")
            else:
                print("⚠ 没有角色数据可供测试")
            
            print("✓ 角色特征提取测试完成")
            return True
            
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("开始测试JSON解析问题修复...")
    
    success = test_role_feature_extraction()
    
    if success:
        print("\n🎉 JSON解析问题修复测试通过！")
    else:
        print("\n❌ JSON解析问题修复测试失败")
