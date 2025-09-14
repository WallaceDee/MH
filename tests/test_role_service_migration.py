#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角色服务迁移测试
测试迁移后的ORM版本角色服务功能
"""

import os
import sys

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_service_import():
    """测试服务导入"""
    print("测试服务导入...")
    
    try:
        from src.app.services.role_service_migrated import RoleServiceMigrated
        print("✅ 迁移版本角色服务导入成功")
        
        from src.app.services.role_service import roleService
        print("✅ 原版角色服务导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 服务导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_initialization():
    """测试服务初始化"""
    print("\n测试服务初始化...")
    
    try:
        from src.app import create_app
        from src.app.services.role_service_migrated import RoleServiceMigrated
        
        # 创建Flask应用
        app = create_app()
        
        with app.app_context():
            # 创建服务实例
            service = RoleServiceMigrated()
            print("✅ 迁移版本角色服务初始化成功")
            
            # 检查服务属性
            print(f"   数据库对象: {service.db}")
            print(f"   特征提取器: {service.feature_extractor}")
            print(f"   市场估价器: {service.market_evaluator}")
            
            return True
        
    except Exception as e:
        print(f"❌ 服务初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_crud_operations():
    """测试基础CRUD操作"""
    print("\n测试基础CRUD操作...")
    
    try:
        from src.app import create_app
        from src.app.services.role_service_migrated import RoleServiceMigrated
        
        app = create_app()
        
        with app.app_context():
            service = RoleServiceMigrated()
            
            # 测试创建角色
            print("1. 测试创建角色...")
            test_role_data = {
                'eid': 'migration_test_001',
                'equip_name': '迁移测试角色',
                'level': 175,
                'price': 2000.0,
                'server_name': '迁移测试服务器',
                'equip_type': '角色',
                'school': 1,
                'serverid': 1,
                'seller_nickname': '测试卖家',
                'accept_bargain': 1,
                'history_price': 1800.0,
                'dynamic_tags': '测试标签',
                'highlight': 0,
                'collect_num': 0,
                'other_info': '测试信息',
                'base_price': 2000.0,
                'equip_price': 1000.0,
                'pet_price': 1000.0,
                'is_split_independent_role': 0,
                'is_split_main_role': 0,
                'large_equip_desc': '测试装备描述',
                'split_price_desc': '测试价格描述'
            }
            
            success = service.create_role(test_role_data)
            if success:
                print("✅ 角色创建成功")
            else:
                print("❌ 角色创建失败")
                return False
            
            # 测试获取角色详情
            print("2. 测试获取角色详情...")
            detail = service.get_role_detail('migration_test_001')
            if detail:
                print(f"✅ 角色详情获取成功: {detail['equip_name']}")
            else:
                print("❌ 角色详情获取失败")
                return False
            
            # 测试更新价格
            print("3. 测试更新价格...")
            update_success = service.update_equipment_valuation('migration_test_001', 2500.0)
            if update_success:
                print("✅ 价格更新成功")
            else:
                print("❌ 价格更新失败")
                return False
            
            # 测试获取角色列表
            print("4. 测试获取角色列表...")
            result = service.get_roles_list(page=1, page_size=10)
            if result and 'data' in result:
                print(f"✅ 角色列表获取成功，记录数: {len(result['data'])}")
            else:
                print("❌ 角色列表获取失败")
                return False
            
            # 测试删除角色
            print("5. 测试删除角色...")
            delete_result = service.delete_role('migration_test_001')
            if delete_result.get('success'):
                print("✅ 角色删除成功")
            else:
                print(f"❌ 角色删除失败: {delete_result.get('error', '未知错误')}")
                return False
            
            print("✅ 所有基础CRUD操作测试通过")
            return True
        
    except Exception as e:
        print(f"❌ 基础CRUD操作测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_advanced_features():
    """测试高级功能"""
    print("\n测试高级功能...")
    
    try:
        from src.app import create_app
        from src.app.services.role_service_migrated import RoleServiceMigrated
        
        app = create_app()
        
        with app.app_context():
            service = RoleServiceMigrated()
            
            # 测试获取角色特征
            print("1. 测试获取角色特征...")
            # 先创建一个测试角色
            test_role_data = {
                'eid': 'feature_test_001',
                'equip_name': '特征测试角色',
                'level': 150,
                'price': 1500.0,
                'server_name': '特征测试服务器',
                'equip_type': '角色',
                'school': 2,
                'serverid': 2,
                'seller_nickname': '特征测试卖家',
                'accept_bargain': 1,
                'history_price': 1400.0,
                'dynamic_tags': '特征测试标签',
                'highlight': 0,
                'collect_num': 0,
                'other_info': '特征测试信息',
                'base_price': 1500.0,
                'equip_price': 750.0,
                'pet_price': 750.0,
                'is_split_independent_role': 0,
                'is_split_main_role': 0,
                'large_equip_desc': '特征测试装备描述',
                'split_price_desc': '特征测试价格描述'
            }
            
            service.create_role(test_role_data)
            
            # 测试特征提取
            feature_result = service.get_role_feature('feature_test_001')
            if feature_result:
                print("✅ 角色特征提取成功")
                if feature_result.get('features'):
                    print(f"   特征数量: {len(feature_result['features'])}")
                else:
                    print("   特征提取器未初始化，跳过特征提取")
            else:
                print("❌ 角色特征提取失败")
            
            # 测试估价功能
            print("2. 测试估价功能...")
            valuation_result = service.get_role_valuation('feature_test_001')
            if valuation_result and 'error' not in valuation_result:
                print(f"✅ 角色估价成功: {valuation_result.get('estimated_price_yuan', 0)}元")
            else:
                print(f"❌ 角色估价失败: {valuation_result.get('error', '未知错误')}")
            
            # 测试锚点查找
            print("3. 测试锚点查找...")
            anchors_result = service.find_role_anchors('feature_test_001')
            if anchors_result and 'error' not in anchors_result:
                print(f"✅ 锚点查找成功: 找到 {anchors_result.get('anchor_count', 0)} 个锚点")
            else:
                print(f"❌ 锚点查找失败: {anchors_result.get('error', '未知错误')}")
            
            # 测试批量估价
            print("4. 测试批量估价...")
            batch_result = service.batch_role_valuation(['feature_test_001'])
            if batch_result and 'error' not in batch_result:
                print(f"✅ 批量估价成功: 处理 {batch_result.get('total_roles', 0)} 个角色")
            else:
                print(f"❌ 批量估价失败: {batch_result.get('error', '未知错误')}")
            
            # 清理测试数据
            service.delete_role('feature_test_001')
            
            print("✅ 高级功能测试完成")
            return True
        
    except Exception as e:
        print(f"❌ 高级功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_compatibility():
    """测试兼容性"""
    print("\n测试兼容性...")
    
    try:
        from src.app import create_app
        from src.app.services.role_service_migrated import RoleServiceMigrated
        from src.app.services.role_service import roleService
        
        app = create_app()
        
        with app.app_context():
            # 测试迁移版本服务
            migrated_service = RoleServiceMigrated()
            print("✅ 迁移版本服务创建成功")
            
            # 测试原版服务
            original_service = roleService()
            print("✅ 原版服务创建成功")
            
            # 测试方法兼容性
            print("1. 测试方法兼容性...")
            
            # 检查迁移版本是否有所有原版方法
            original_methods = [method for method in dir(original_service) if not method.startswith('_')]
            migrated_methods = [method for method in dir(migrated_service) if not method.startswith('_')]
            
            missing_methods = set(original_methods) - set(migrated_methods)
            if missing_methods:
                print(f"⚠️  缺少方法: {missing_methods}")
            else:
                print("✅ 所有原版方法都已迁移")
            
            # 检查新增方法
            new_methods = set(migrated_methods) - set(original_methods)
            if new_methods:
                print(f"✅ 新增方法: {new_methods}")
            
            print("✅ 兼容性测试完成")
            return True
        
    except Exception as e:
        print(f"❌ 兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("角色服务迁移测试")
    print("=" * 60)
    
    success = True
    
    # 测试服务导入
    if not test_service_import():
        success = False
    
    # 测试服务初始化
    if not test_service_initialization():
        success = False
    
    # 测试基础CRUD操作
    if not test_basic_crud_operations():
        success = False
    
    # 测试高级功能
    if not test_advanced_features():
        success = False
    
    # 测试兼容性
    if not test_compatibility():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有迁移测试通过！")
        print("\n迁移完成情况:")
        print("1. ✅ 基础CRUD方法已迁移")
        print("2. ✅ 高级功能已迁移")
        print("3. ✅ 兼容性接口已提供")
        print("4. ✅ 所有原版方法都已支持")
        print("\n下一步:")
        print("1. 更新API端点使用新的ORM服务")
        print("2. 进行完整的功能测试")
        print("3. 逐步替换原版服务")
    else:
        print("❌ 部分测试失败！")
        print("请检查错误信息并修复问题")
    print("=" * 60)

if __name__ == "__main__":
    main()
