47.86.33.98#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试修复后的MariaDB连接
"""

import pymysql
import os

def test_fixed_connection():
    """测试修复后的连接"""
    print("=== 测试修复后的MariaDB连接 ===")
    
    # 连接参数
    host = '47.86.33.98'
    port = 3306
    user = 'root'
    password = '447363121'
    database = 'cbg_spider'
    
    try:
        # 连接MariaDB
        print(f"正在连接MariaDB服务器: {host}:{port}")
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
            
            # 创建项目数据库（如果不存在）
            cursor.execute("CREATE DATABASE IF NOT EXISTS cbg_spider CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✓ 项目数据库创建/确认成功")
            
            # 使用项目数据库
            cursor.execute("USE cbg_spider")
            
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
    success = test_fixed_connection()
    
    if success:
        print("\n🎉 MariaDB连接修复成功！")
        print("现在可以使用MySQL启动项目了")
    else:
        print("\n❌ MariaDB连接仍然失败")
        print("请检查服务器上的用户权限设置")

