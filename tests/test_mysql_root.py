#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用root用户测试MySQL连接
"""

import pymysql
import os

def test_mysql_root_connection():
    """使用root用户测试MySQL连接"""
    print("=== 使用root用户测试MySQL连接 ===")
    
    # 连接参数 - 使用root用户
    host = '47.86.33.98'
    port = 3306
    user = 'root'  # 使用root用户
    password = '447363121'  # root密码
    database = 'cbg_spider'
    
    try:
        # 直接连接MySQL
        print(f"正在连接MySQL服务器: {host}:{port}")
        print(f"使用用户: {user}")
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            connect_timeout=10,
            ssl_disabled=True,
            autocommit=True
        )
        
        print("✓ MySQL连接成功！")
        
        # 测试查询
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"✓ MySQL版本: {version}")
            
            # 查看数据库
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print(f"✓ 可用数据库: {[db[0] for db in databases]}")
            
            # 查看用户权限
            cursor.execute("SELECT User, Host FROM mysql.user WHERE User = 'cbg_user'")
            users = cursor.fetchall()
            print(f"✓ cbg_user用户: {users}")
            
            # 查看表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✓ 当前数据库表: {[table[0] for table in tables]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ MySQL连接失败: {e}")
        return False

if __name__ == "__main__":
    success = test_mysql_root_connection()
    
    if success:
        print("\n🎉 MySQL root用户连接测试成功！")
        print("现在可以修复cbg_user的权限问题")
    else:
        print("\n❌ MySQL root用户连接测试失败")
        print("请检查root密码或MySQL服务器状态")

