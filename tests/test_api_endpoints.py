#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试API端点是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app

def test_role_api_endpoints():
    """测试角色API端点"""
    print("=== 测试角色API端点 ===")
    
    # 创建Flask应用
    app = create_app()
    
    with app.test_client() as client:
        try:
            # 测试获取角色列表
            response = client.get('/api/v1/role/')
            print(f"✓ 角色列表API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✓ 角色列表数据: {data.get('total', 0)} 条记录")
            else:
                print(f"⚠ 角色列表API返回错误: {response.get_json()}")
            
            # 测试获取角色详情（如果有数据）
            if response.status_code == 200:
                data = response.get_json()
                if data.get('data') and len(data['data']) > 0:
                    first_role = data['data'][0]
                    eid = first_role.get('eid')
                    if eid:
                        detail_response = client.get(f'/api/v1/role/{eid}')
                        print(f"✓ 角色详情API响应状态: {detail_response.status_code}")
                        if detail_response.status_code == 200:
                            detail_data = detail_response.get_json()
                            print(f"✓ 角色详情数据: {detail_data.get('eid', 'N/A')}")
                        else:
                            print(f"⚠ 角色详情API返回错误: {detail_response.get_json()}")
            
            print("✓ 角色API端点测试完成")
            return True
            
        except Exception as e:
            print(f"✗ API测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("开始测试API端点...")
    
    success = test_role_api_endpoints()
    
    if success:
        print("\n🎉 API端点测试通过！")
    else:
        print("\n❌ API端点测试失败")
