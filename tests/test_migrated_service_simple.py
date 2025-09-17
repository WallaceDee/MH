#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化的迁移服务测试
专门测试迁移后的ORM角色服务
"""

import os
import sys

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_service_creation():
    """测试服务创建"""
    print("测试服务创建...")
    
    try:
        from src.app import create_app
        from app.services.role_service import RoleService
        
        # 创建Flask应用
        app = create_app()
        print("✅ Flask应用创建成功")
        
        with app.app_context():
            # 创建服务实例
            service = RoleService()
            print("✅ 迁移版本角色服务创建成功")
            
            # 检查服务属性
            print(f"   数据库对象类型: {type(service.db)}")
            print(f"   特征提取器: {'已初始化' if service.feature_extractor else '未初始化'}")
            print(f"   市场估价器: {'已初始化' if service.market_evaluator else '未初始化'}")
            
            return True
        
    except Exception as e:
        print(f"❌ 服务创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_operations():
    """测试数据库操作"""
    print("\n测试数据库操作...")
    
    try:
        from src.app import create_app
        from app.services.role_service import RoleService
        from src.database import db
        
        app = create_app()
        
        with app.app_context():
            service = RoleService()
            
            # 测试数据库连接
            print("1. 测试数据库连接...")
            try:
                # 尝试执行一个简单的查询
                result = db.session.execute(db.text("SELECT 1")).scalar()
                print(f"✅ 数据库连接成功: {result}")
            except Exception as e:
                print(f"❌ 数据库连接失败: {e}")
                return False
            
            # 测试创建表
            print("2. 测试创建表...")
            try:
                db.create_all()
                print("✅ 数据库表创建成功")
            except Exception as e:
                print(f"❌ 数据库表创建失败: {e}")
                return False
            
            # 测试角色查询
            print("3. 测试角色查询...")
            try:
                from src.models.role import Role
                count = db.session.query(Role).count()
                print(f"✅ 角色表查询成功，记录数: {count}")
            except Exception as e:
                print(f"❌ 角色表查询失败: {e}")
                return False
            
            print("✅ 数据库操作测试通过")
            return True
        
    except Exception as e:
        print(f"❌ 数据库操作测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_methods():
    """测试服务方法"""
    print("\n测试服务方法...")
    
    try:
        from src.app import create_app
        from app.services.role_service import RoleService
        
        app = create_app()
        
        with app.app_context():
            service = RoleService()
            
            # 测试获取角色列表
            print("1. 测试获取角色列表...")
            try:
                result = service.get_roles_list(page=1, page_size=5)
                if result and 'data' in result:
                    print(f"✅ 角色列表获取成功，记录数: {len(result['data'])}")
                else:
                    print(f"⚠️  角色列表获取成功，但无数据: {result}")
            except Exception as e:
                print(f"❌ 角色列表获取失败: {e}")
                return False
            
            # 测试获取角色详情（使用现有数据）
            print("2. 测试获取角色详情...")
            try:
                # 先获取一个角色ID
                from src.database import db
                from src.models.role import Role
                
                role = db.session.query(Role).first()
                if role:
                    detail = service.get_role_detail(role.eid)
                    if detail:
                        print(f"✅ 角色详情获取成功: {detail.get('equip_name', '未知')}")
                    else:
                        print("⚠️  角色详情获取成功，但无数据")
                else:
                    print("⚠️  没有角色数据可供测试")
            except Exception as e:
                print(f"❌ 角色详情获取失败: {e}")
                return False
            
            print("✅ 服务方法测试通过")
            return True
        
    except Exception as e:
        print(f"❌ 服务方法测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_compatibility_methods():
    """测试兼容性方法"""
    print("\n测试兼容性方法...")
    
    try:
        from src.app import create_app
        from app.services.role_service import RoleService
        
        app = create_app()
        
        with app.app_context():
            service = RoleService()
            
            # 检查兼容性方法是否存在
            print("1. 检查兼容性方法...")
            compatibility_methods = [
                'create_role',
                'update_equipment_valuation', 
                'get_role_detail',
                'get_roles',
                'get_role_list',
                'get_role_details',
                'delete_role',
                'get_role_valuation',
                'find_role_anchors',
                'batch_role_valuation'
            ]
            
            missing_methods = []
            for method in compatibility_methods:
                if not hasattr(service, method):
                    missing_methods.append(method)
            
            if missing_methods:
                print(f"❌ 缺少兼容性方法: {missing_methods}")
                return False
            else:
                print("✅ 所有兼容性方法都存在")
            
            # 测试方法调用（不执行实际数据库操作）
            print("2. 测试方法调用...")
            try:
                # 测试参数验证
                result = service.get_roles_list(page=0, page_size=0)  # 应该被修正为有效值
                if result and 'page' in result and result['page'] >= 1:
                    print("✅ 参数验证正常")
                else:
                    print("⚠️  参数验证可能有问题")
                
                # 测试错误处理
                detail = service.get_role_detail('')  # 空ID应该返回None
                if detail is None:
                    print("✅ 错误处理正常")
                else:
                    print("⚠️  错误处理可能有问题")
                
            except Exception as e:
                print(f"❌ 方法调用测试失败: {e}")
                return False
            
            print("✅ 兼容性方法测试通过")
            return True
        
    except Exception as e:
        print(f"❌ 兼容性方法测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("简化迁移服务测试")
    print("=" * 60)
    
    success = True
    
    # 测试服务创建
    if not test_service_creation():
        success = False
    
    # 测试数据库操作
    if not test_database_operations():
        success = False
    
    # 测试服务方法
    if not test_service_methods():
        success = False
    
    # 测试兼容性方法
    if not test_compatibility_methods():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有简化测试通过！")
        print("\n迁移状态:")
        print("1. ✅ 服务创建正常")
        print("2. ✅ 数据库操作正常")
        print("3. ✅ 服务方法正常")
        print("4. ✅ 兼容性方法正常")
        print("\n下一步:")
        print("1. 可以开始使用迁移后的服务")
        print("2. 逐步替换原版服务")
        print("3. 进行完整的功能测试")
    else:
        print("❌ 部分测试失败！")
        print("请检查错误信息并修复问题")
    print("=" * 60)

if __name__ == "__main__":
    main()
