#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查数据库表结构
"""

import sqlite3
import os

def check_db_schema(db_path):
    """检查数据库表结构"""
    print(f"检查数据库: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"数据库中的表: {[table[0] for table in tables]}")
        
        # 检查 roles 表结构
        if any('roles' in table[0] for table in tables):
            for table in tables:
                table_name = table[0]
                if 'roles' in table_name:
                    print(f"\n--- {table_name} 表结构 ---")
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = cursor.fetchall()
                    
                    for col in columns:
                        print(f"  {col[1]} ({col[2]}) - {col}")
        
        # 检查 large_equip_desc_data 表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%large%';")
        large_tables = cursor.fetchall()
        
        if large_tables:
            print(f"\n发现大型数据表: {[table[0] for table in large_tables]}")
            for table in large_tables:
                table_name = table[0]
                print(f"\n--- {table_name} 表结构 ---")
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                for col in columns[:10]:  # 只显示前10列
                    print(f"  {col[1]} ({col[2]})")
                if len(columns) > 10:
                    print(f"  ... 还有 {len(columns) - 10} 列")
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据库失败: {e}")

if __name__ == "__main__":
    # 检查多个数据库文件
    db_files = [
        "data/202509/cbg_roles_202509.db",
        "data/202508 - 副本/cbg_roles_202508.db",
        "data/202507/empty_characters_202507.db"
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            check_db_schema(db_file)
            print("=" * 50)
        else:
            print(f"文件不存在: {db_file}")
