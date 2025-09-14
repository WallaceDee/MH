#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试MariaDB连接
"""

import pymysql
import os

def test_mariadb_connection():
    """测试MariaDB连接"""
    print("=== 测试MariaDB连接 ===")
    
    # 连接参数
    host = '47.86.33.98'
    port = 3306
    user = 'root'
    password = '447363121'
    database = 'cbg_spider'
    
    try:
        # 连接MariaDB
        print(f"正在连接MariaDB服务器: {host}:{port}")
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
        
        print("✓ MariaDB连接成功！")
        
        # 测试查询
        with connection.cursor() as cursor:
            # 查看版本信息
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"✓ 数据库版本: {version}")
            
            # 查看数据库
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print(f"✓ 可用数据库: {[db[0] for db in databases]}")
            
            # 查看用户
            cursor.execute("SELECT User, Host FROM mysql.user WHERE User = 'root'")
            users = cursor.fetchall()
            print(f"✓ root用户: {users}")
            
            # 查看表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✓ 当前数据库表: {[table[0] for table in tables]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ MariaDB连接失败: {e}")
        return False

if __name__ == "__main__":
    success = test_mariadb_connection()
    
    if success:
        print("\n🎉 MariaDB连接测试成功！")
    else:
        print("\n❌ MariaDB连接测试失败")

