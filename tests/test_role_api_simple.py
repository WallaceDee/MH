#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的角色API测试
测试新的角色服务在实际API中的使用
"""

import os
import sys

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_api_with_new_service():
    """测试使用新服务的API"""
    print("测试使用新服务的API...")
    
    try:
        from src.app import create_app
        
        app = create_app()
        print("✅ Flask应用创建成功")
        
        with app.test_client() as client:
            # 测试角色列表API
            print("1. 测试角色列表API...")
            response = client.get('/api/v1/role/')
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   响应格式: {type(data)}")
                if data and 'code' in data:
                    print(f"   业务状态码: {data['code']}")
                    if data['code'] == 200:
                        print("✅ 角色列表API正常工作")
                        return True
                    else:
                        print(f"   业务错误: {data.get('message', '未知错误')}")
                else:
                    print("   响应格式异常")
            else:
                print(f"   HTTP错误: {response.status_code}")
                try:
                    error_data = response.get_json()
                    print(f"   错误信息: {error_data}")
                except:
                    print(f"   响应内容: {response.data.decode('utf-8')[:200]}")
            
            return False
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_controller_service_type():
    """测试控制器使用的服务类型"""
    print("\n测试控制器服务类型...")
    
    try:
        from src.app.controllers.role_controller import roleController
        
        controller = roleController()
        service_type = type(controller.service).__name__
        print(f"   控制器使用的服务类型: {service_type}")
        
        if service_type == 'RoleServiceMigrated':
            print("✅ 控制器已成功使用新的ORM服务")
            return True
        else:
            print(f"❌ 控制器仍在使用旧服务: {service_type}")
            return False
        
    except Exception as e:
        print(f"❌ 控制器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_import():
    """测试服务导入"""
    print("\n测试服务导入...")
    
    try:
        from src.app.services.role_service_migrated import RoleServiceMigrated
        print("✅ 新角色服务导入成功")
        
        from src.app.services.role_service import roleService
        print("✅ 原版角色服务导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 服务导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("简单角色API测试")
    print("=" * 60)
    
    success = True
    
    # 测试服务导入
    if not test_service_import():
        success = False
    
    # 测试控制器服务类型
    if not test_controller_service_type():
        success = False
    
    # 测试API
    if not test_api_with_new_service():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过！")
        print("\n新角色服务部署成功:")
        print("1. ✅ 服务导入正常")
        print("2. ✅ 控制器已使用新服务")
        print("3. ✅ API端点正常工作")
        print("\n现在可以正常使用新的角色服务了！")
    else:
        print("❌ 部分测试失败！")
        print("请检查错误信息并修复问题")
    print("=" * 60)

if __name__ == "__main__":
    main()
