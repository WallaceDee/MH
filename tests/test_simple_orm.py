#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化的ORM功能测试
"""

import os
import sys

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 设置环境变量为SQLite模式（默认）
os.environ['DATABASE_TYPE'] = 'sqlite'

def test_imports():
    """测试基本导入"""
    print("测试基本导入...")
    
    try:
        from src.database_config import db_config, IS_MYSQL, IS_SQLITE
        print(f"✅ 数据库配置导入成功")
        print(f"   数据库类型: {db_config.db_type}")
        print(f"   是否为MySQL: {IS_MYSQL}")
        print(f"   是否为SQLite: {IS_SQLITE}")
        
        from src.models.base import Base
        print(f"✅ Base类导入成功")
        
        from src.models.role import Role
        print(f"✅ Role模型导入成功")
        
        from src.models.equipment import Equipment
        print(f"✅ Equipment模型导入成功")
        
        from src.models.pet import Pet
        print(f"✅ Pet模型导入成功")
        
        from src.models.abnormal_equipment import AbnormalEquipment
        print(f"✅ AbnormalEquipment模型导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_app():
    """测试Flask应用创建"""
    print("\n测试Flask应用创建...")
    
    try:
        from src.app import create_app
        
        app = create_app()
        print(f"✅ Flask应用创建成功")
        
        # 检查数据库是否初始化
        with app.app_context():
            from src.database import db
            print(f"✅ 数据库在应用上下文中可用")
            
            # 测试创建表
            db.create_all()
            print(f"✅ 数据库表创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask应用创建失败: {e}")
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
            # 测试查询
            count = db.session.query(Role).count()
            print(f"✅ 角色表查询成功，记录数: {count}")
            
            # 测试插入（如果表为空）
            if count == 0:
                test_role = Role(
                    eid='test_001',
                    equip_name='测试角色',
                    level=175,
                    price=1000.0,
                    server_name='测试服务器'
                )
                db.session.add(test_role)
                db.session.commit()
                print(f"✅ 测试角色插入成功")
                
                # 测试查询
                role = db.session.query(Role).filter(Role.eid == 'test_001').first()
                if role:
                    print(f"✅ 测试角色查询成功: {role.equip_name}")
                else:
                    print(f"❌ 测试角色查询失败")
                
                # 清理测试数据
                db.session.delete(role)
                db.session.commit()
                print(f"✅ 测试数据清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("简化ORM功能测试")
    print("=" * 60)
    
    success = True
    
    # 测试导入
    if not test_imports():
        success = False
    
    # 测试Flask应用
    if not test_flask_app():
        success = False
    
    # 测试数据库操作
    if not test_database_operations():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有ORM功能测试通过！")
        print("\n使用说明:")
        print("1. 当前使用SQLite数据库")
        print("2. 要切换到MySQL，设置环境变量: export DATABASE_TYPE=mysql")
        print("3. 配置MySQL连接参数后重启应用")
        print("4. 使用 src.app.services.role_service_orm.RoleServiceORM 进行数据库操作")
    else:
        print("❌ 部分测试失败！")
    print("=" * 60)

if __name__ == "__main__":
    main()
