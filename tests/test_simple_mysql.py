#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的MySQL连接测试
"""

import pymysql
import os

def test_mysql_connection():
    """测试MySQL连接"""
    print("=== 简单MySQL连接测试 ===")
    
    # 连接参数
    host = '47.86.33.98'
    port = 3306
    user = 'root'  # 使用root用户
    password = '447363121'
    database = None  # 先不指定数据库
    
    try:
        # 直接连接MySQL
        print(f"正在连接MySQL服务器: {host}:{port}")
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
            
            # 如果指定了数据库，查看表
            if database:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print(f"✓ 当前数据库表: {[table[0] for table in tables]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ MySQL连接失败: {e}")
        return False

if __name__ == "__main__":
    success = test_mysql_connection()
    
    if success:
        print("\n🎉 MySQL连接测试成功！")
    else:
        print("\n❌ MySQL连接测试失败")
