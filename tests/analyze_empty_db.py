#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分析空号数据库结构
"""

import sqlite3
import os
import sys

def analyze_empty_db():
    """分析空号数据库结构"""
    db_path = r"C:\Users\Administrator\Desktop\mh\data\202506\cbg_empty_roles_202509.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    # 获取文件大小
    file_size = os.path.getsize(db_path)
    print(f"📊 数据库文件大小: {file_size / 1024 / 1024:.2f} MB")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📋 数据库中的表: {len(tables)} 个")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # 获取表的记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"    记录数: {count}")
            
            if count > 0:
                # 获取表结构
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print(f"    字段数: {len(columns)}")
                
                # 显示前几条记录
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print(f"    前3条记录:")
                for i, row in enumerate(rows):
                    print(f"      第{i+1}条: {str(row)[:100]}...")
        
        conn.close()
        print("✅ 数据库分析完成！")
        
    except Exception as e:
        print(f"❌ 分析数据库失败: {e}")

if __name__ == "__main__":
    analyze_empty_db()
