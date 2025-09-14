#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试MySQL数据库连接
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置环境变量
os.environ['DATABASE_TYPE'] = 'mysql'
os.environ['MYSQL_HOST'] = '47.86.33.98'
os.environ['MYSQL_USER'] = 'cbg_user'
os.environ['MYSQL_PASSWORD'] = '447363121'
os.environ['MYSQL_DATABASE'] = 'cbg_spider'

from src.app import create_app
from src.database_config import db_config

def test_mysql_connection():
    """测试MySQL数据库连接"""
    print("=== 测试MySQL数据库连接 ===")
    
    # 检查数据库配置
    print(f"数据库类型: {db_config.db_type}")
    print(f"是否为MySQL: {db_config.is_mysql()}")
    print(f"MySQL配置: {db_config.config}")
    
    # 创建Flask应用
    app = create_app()
    
    with app.app_context():
        try:
            from src.database import db
            
            # 测试数据库连接
            from sqlalchemy import text
            with db.engine.connect() as connection:
                result = connection.execute(text("SELECT 1 as test"))
                test_value = result.fetchone()[0]
                print(f"✓ MySQL连接成功，测试查询结果: {test_value}")
            
            # 测试创建表
            print("正在创建数据库表...")
            db.create_all()
            print("✓ 数据库表创建成功")
            
            # 测试角色服务
            from src.app.services.role_service_migrated import RoleServiceMigrated
            role_service = RoleServiceMigrated()
            
            # 测试获取角色列表
            result = role_service.get_role_list(page=1, page_size=5)
            print(f"✓ 角色服务测试成功，获取到 {result.get('total', 0)} 条记录")
            
            return True
            
        except Exception as e:
            print(f"✗ MySQL连接失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("开始测试MySQL连接...")
    
    success = test_mysql_connection()
    
    if success:
        print("\n🎉 MySQL连接测试成功！")
    else:
        print("\n❌ MySQL连接测试失败")
