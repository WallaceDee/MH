#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
尝试不同的MySQL连接方式
"""

import pymysql
import os

def test_mysql_variations():
    """尝试不同的MySQL连接方式"""
    print("=== 尝试不同的MySQL连接方式 ===")
    
    # 连接参数
    host = '47.86.33.98'
    port = 3306
    user = 'cbg_user'
    password = '447363121'
    
    # 尝试不同的连接配置
    configs = [
        {
            'name': '标准连接',
            'config': {
                'host': host,
                'port': port,
                'user': user,
                'password': password,
                'charset': 'utf8mb4',
                'connect_timeout': 10
            }
        },
        {
            'name': '禁用SSL',
            'config': {
                'host': host,
                'port': port,
                'user': user,
                'password': password,
                'charset': 'utf8mb4',
                'connect_timeout': 10,
                'ssl_disabled': True
            }
        },
        {
            'name': '使用root用户',
            'config': {
                'host': host,
                'port': port,
                'user': 'root',
                'password': '447363121',
                'charset': 'utf8mb4',
                'connect_timeout': 10,
                'ssl_disabled': True
            }
        },
        {
            'name': '不指定数据库',
            'config': {
                'host': host,
                'port': port,
                'user': user,
                'password': password,
                'charset': 'utf8mb4',
                'connect_timeout': 10,
                'ssl_disabled': True
            }
        },
        {
            'name': '增加超时时间',
            'config': {
                'host': host,
                'port': port,
                'user': user,
                'password': password,
                'charset': 'utf8mb4',
                'connect_timeout': 30,
                'ssl_disabled': True
            }
        }
    ]
    
    for config in configs:
        print(f"\n--- 尝试 {config['name']} ---")
        try:
            connection = pymysql.connect(**config['config'])
            print(f"✓ {config['name']} 连接成功！")
            
            # 测试查询
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                print(f"✓ MySQL版本: {version}")
                
                # 查看数据库
                cursor.execute("SHOW DATABASES")
                databases = cursor.fetchall()
                print(f"✓ 可用数据库: {[db[0] for db in databases]}")
            
            connection.close()
            return True
            
        except Exception as e:
            print(f"✗ {config['name']} 连接失败: {e}")
    
    return False

if __name__ == "__main__":
    success = test_mysql_variations()
    
    if success:
        print("\n🎉 找到可用的连接方式！")
    else:
        print("\n❌ 所有连接方式都失败了")
        print("建议检查MySQL服务器状态或使用SQLite")

