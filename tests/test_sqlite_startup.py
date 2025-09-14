#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试SQLite启动
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置环境变量为SQLite
os.environ['DATABASE_TYPE'] = 'sqlite'

from src.app import create_app

def test_sqlite_startup():
    """测试SQLite启动"""
    print("=== 测试SQLite启动 ===")
    
    try:
        app = create_app()
        print("✓ Flask应用创建成功")
        
        with app.app_context():
            from src.database import db
            print("✓ 数据库连接成功")
            
            # 测试角色服务
            from src.app.services.role_service_migrated import RoleServiceMigrated
            role_service = RoleServiceMigrated()
            
            # 测试获取角色列表
            result = role_service.get_role_list(page=1, page_size=5)
            print(f"✓ 角色服务测试成功，获取到 {result.get('total', 0)} 条记录")
            
        return True
        
    except Exception as e:
        print(f"✗ SQLite启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sqlite_startup()
    
    if success:
        print("\n🎉 SQLite启动测试成功！")
    else:
        print("\n❌ SQLite启动测试失败")

