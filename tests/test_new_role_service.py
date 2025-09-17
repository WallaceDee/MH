#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试新的角色服务
验证API端点使用新的ORM服务是否正常工作
"""

import os
import sys

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_controller_import():
    """测试控制器导入"""
    print("测试控制器导入...")
    
    try:
        from src.app.controllers.role_controller import roleController
        print("✅ 角色控制器导入成功")
        
        # 检查控制器使用的服务类型
        controller = roleController()
        service_type = type(controller.service).__name__
        print(f"   使用的服务类型: {service_type}")
        
        if service_type == 'RoleService':
            print("✅ 控制器已使用新的ORM服务")
        else:
            print(f"❌ 控制器仍在使用旧服务: {service_type}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 控制器导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n测试API端点...")
    
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
                if data and 'code' in data:
                    print(f"   响应码: {data['code']}")
                    if 'data' in data and 'total' in data['data']:
                        print(f"   角色总数: {data['data']['total']}")
                        print("✅ 角色列表API测试成功")
                    else:
                        print("⚠️  角色列表API响应格式异常")
                else:
                    print("⚠️  角色列表API响应格式异常")
            else:
                print(f"❌ 角色列表API测试失败: {response.status_code}")
                return False
            
            # 测试角色详情API（如果有数据）
            print("2. 测试角色详情API...")
            # 先获取一个角色ID
            if response.status_code == 200:
                data = response.get_json()
                if data and 'data' in data and 'items' in data['data'] and data['data']['items']:
                    role_eid = data['data']['items'][0].get('eid')
                    if role_eid:
                        detail_response = client.get(f'/api/v1/role/{role_eid}')
                        print(f"   角色详情状态码: {detail_response.status_code}")
                        if detail_response.status_code == 200:
                            print("✅ 角色详情API测试成功")
                        else:
                            print(f"⚠️  角色详情API测试失败: {detail_response.status_code}")
                    else:
                        print("⚠️  没有可用的角色ID进行测试")
                else:
                    print("⚠️  没有角色数据可供测试")
            else:
                print("⚠️  无法获取角色列表进行详情测试")
            
            print("✅ API端点测试完成")
            return True
        
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_functionality():
    """测试服务功能"""
    print("\n测试服务功能...")
    
    try:
        from src.app import create_app
        from app.services.role_service import RoleService
        
        app = create_app()
        
        with app.app_context():
            service = RoleService()
            print("✅ 服务创建成功")
            
            # 测试获取角色列表
            print("1. 测试获取角色列表...")
            result = service.get_roles_list(page=1, page_size=5)
            if result and 'total' in result:
                print(f"   角色总数: {result['total']}")
                print(f"   当前页记录数: {len(result.get('data', []))}")
                print("✅ 角色列表获取成功")
            else:
                print("❌ 角色列表获取失败")
                return False
            
            # 测试获取角色详情
            print("2. 测试获取角色详情...")
            if result.get('data'):
                role_eid = result['data'][0].get('eid')
                if role_eid:
                    detail = service.get_role_detail(role_eid)
                    if detail:
                        print(f"   角色名称: {detail.get('equip_name', '未知')}")
                        print(f"   角色等级: {detail.get('level', 0)}")
                        print("✅ 角色详情获取成功")
                    else:
                        print("❌ 角色详情获取失败")
                        return False
                else:
                    print("⚠️  没有可用的角色ID")
            else:
                print("⚠️  没有角色数据可供测试")
            
            print("✅ 服务功能测试完成")
            return True
        
    except Exception as e:
        print(f"❌ 服务功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_operations():
    """测试数据库操作"""
    print("\n测试数据库操作...")
    
    try:
        from src.app import create_app
        from src.database import db
        from src.models.role import Role
        
        app = create_app()
        
        with app.app_context():
            # 测试数据库连接
            print("1. 测试数据库连接...")
            try:
                result = db.session.execute(db.text("SELECT 1")).scalar()
                print(f"   数据库连接测试: {result}")
                print("✅ 数据库连接正常")
            except Exception as e:
                print(f"❌ 数据库连接失败: {e}")
                return False
            
            # 测试角色表查询
            print("2. 测试角色表查询...")
            try:
                count = db.session.query(Role).count()
                print(f"   角色表记录数: {count}")
                print("✅ 角色表查询正常")
            except Exception as e:
                print(f"❌ 角色表查询失败: {e}")
                return False
            
            # 测试创建表
            print("3. 测试创建表...")
            try:
                db.create_all()
                print("✅ 数据库表创建正常")
            except Exception as e:
                print(f"⚠️  数据库表创建警告: {e}")
            
            print("✅ 数据库操作测试完成")
            return True
        
    except Exception as e:
        print(f"❌ 数据库操作测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("新角色服务测试")
    print("=" * 60)
    
    success = True
    
    # 测试控制器导入
    if not test_controller_import():
        success = False
    
    # 测试数据库操作
    if not test_database_operations():
        success = False
    
    # 测试服务功能
    if not test_service_functionality():
        success = False
    
    # 测试API端点
    if not test_api_endpoints():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过！")
        print("\n新角色服务已成功部署:")
        print("1. ✅ 控制器已更新使用ORM服务")
        print("2. ✅ 数据库操作正常")
        print("3. ✅ 服务功能正常")
        print("4. ✅ API端点正常")
        print("\n现在可以正常使用新的角色服务了！")
    else:
        print("❌ 部分测试失败！")
        print("请检查错误信息并修复问题")
    print("=" * 60)

if __name__ == "__main__":
    main()
