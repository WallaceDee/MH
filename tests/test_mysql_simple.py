#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的MySQL连接测试
"""

import os
import sys

# 设置环境变量
os.environ['DATABASE_TYPE'] = 'mysql'
os.environ['MYSQL_HOST'] = '47.86.33.98'
os.environ['MYSQL_PORT'] = '3306'
os.environ['MYSQL_USER'] = 'lingtong'
os.environ['MYSQL_PASSWORD'] = '447363121'
os.environ['MYSQL_DATABASE'] = 'cbg_spider'
os.environ['MYSQL_CHARSET'] = 'utf8mb4'

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_database_config():
    """测试数据库配置"""
    print("=" * 60)
    print("测试数据库配置")
    print("=" * 60)
    
    try:
        from src.database_config import db_config
        
        print(f"数据库类型: {db_config.db_type}")
        print(f"是否为MySQL: {db_config.is_mysql()}")
        print(f"是否为SQLite: {db_config.is_sqlite()}")
        
        if db_config.is_mysql():
            config = db_config.config
            print(f"MySQL配置:")
            print(f"  主机: {config['host']}")
            print(f"  端口: {config['port']}")
            print(f"  用户: {config['user']}")
            print(f"  数据库: {config['database']}")
            print(f"  字符集: {config['charset']}")
            
            # 测试数据库URL
            database_url = db_config.get_database_url('roles')
            print(f"数据库URL: {database_url}")
            
        print("✅ 数据库配置加载成功！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_app():
    """测试Flask应用创建"""
    print("\n" + "=" * 60)
    print("测试Flask应用创建")
    print("=" * 60)
    
    try:
        from src.app import create_app
        
        print("正在创建Flask应用...")
        app = create_app()
        
        with app.app_context():
            print("✅ Flask应用创建成功！")
            
            # 测试数据库连接
            from src.database import db
            from sqlalchemy import text
            
            # 测试简单查询
            result = db.session.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            print(f"✅ 数据库查询测试成功: {test_value}")
            
        return True
        
    except Exception as e:
        print(f"❌ Flask应用创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("MySQL连接测试开始...")
    
    # 测试数据库配置
    config_success = test_database_config()
    
    # 测试Flask应用
    app_success = test_flask_app()
    
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"数据库配置: {'✅ 成功' if config_success else '❌ 失败'}")
    print(f"Flask应用: {'✅ 成功' if app_success else '❌ 失败'}")
    
    if config_success and app_success:
        print("\n🎉 所有测试通过！项目已成功配置为使用MySQL数据库。")
        print("\n可以运行以下命令启动应用:")
        print("python start_mysql.py")
    else:
        print("\n❌ 部分测试失败，请检查配置。")

if __name__ == "__main__":
    main()

