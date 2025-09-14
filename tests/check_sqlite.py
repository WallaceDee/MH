#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_sqlite_database():
    """检查SQLite数据库结构和数据"""
    db_path = 'data/cbg_empty_roles.db'
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"数据库中的表: {[table[0] for table in tables]}")
        
        # 检查roles表的数据量
        cursor.execute("SELECT COUNT(*) FROM roles")
        count = cursor.fetchone()[0]
        print(f"roles表数据量: {count}")
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(roles)")
        columns = cursor.fetchall()
        print(f"roles表字段数量: {len(columns)}")
        
        # 检查前几条数据
        cursor.execute("SELECT eid, equip_name, level FROM roles LIMIT 5")
        sample_data = cursor.fetchall()
        print(f"前5条数据示例: {sample_data}")
        
    except Exception as e:
        print(f"检查数据库时出错: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_sqlite_database()
