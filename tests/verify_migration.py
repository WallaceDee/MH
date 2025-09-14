#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证数据迁移结果
"""

import os
import sys
import sqlite3

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database_config import db_config
from sqlalchemy import create_engine, text

def verify_migration():
    """验证迁移结果"""
    try:
        # 连接MySQL
        mysql_url = db_config.get_database_url('roles')
        mysql_engine = create_engine(mysql_url, echo=False)
        
        with mysql_engine.connect() as conn:
            # 检查roles表
            result = conn.execute(text("SELECT COUNT(*) FROM roles WHERE role_type = 'empty'"))
            empty_roles_count = result.fetchone()[0]
            print(f"MySQL中role_type为'empty'的角色数量: {empty_roles_count}")
            
            # 检查large_equip_desc_data表
            result = conn.execute(text("SELECT COUNT(*) FROM large_equip_desc_data"))
            desc_data_count = result.fetchone()[0]
            print(f"MySQL中large_equip_desc_data表数据数量: {desc_data_count}")
            
            # 检查SQLite原始数据
            sqlite_path = 'data/cbg_empty_roles.db'
            if os.path.exists(sqlite_path):
                conn_sqlite = sqlite3.connect(sqlite_path)
                cursor = conn_sqlite.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM roles")
                sqlite_roles_count = cursor.fetchone()[0]
                print(f"SQLite中roles表数据数量: {sqlite_roles_count}")
                
                cursor.execute("SELECT COUNT(*) FROM large_equip_desc_data")
                sqlite_desc_count = cursor.fetchone()[0]
                print(f"SQLite中large_equip_desc_data表数据数量: {sqlite_desc_count}")
                
                conn_sqlite.close()
                
                # 计算迁移成功率
                roles_success_rate = (empty_roles_count / sqlite_roles_count) * 100 if sqlite_roles_count > 0 else 0
                desc_success_rate = (desc_data_count / sqlite_desc_count) * 100 if sqlite_desc_count > 0 else 0
                
                print(f"\n迁移成功率:")
                print(f"roles表: {roles_success_rate:.1f}% ({empty_roles_count}/{sqlite_roles_count})")
                print(f"large_equip_desc_data表: {desc_success_rate:.1f}% ({desc_data_count}/{sqlite_desc_count})")
            
            # 检查一些样本数据
            print(f"\n样本数据检查:")
            result = conn.execute(text("SELECT eid, equip_name, level, price FROM roles WHERE role_type = 'empty' LIMIT 5"))
            sample_roles = result.fetchall()
            print("前5条空角色数据:")
            for role in sample_roles:
                print(f"  {role[0]}: {role[1]} (等级{role[2]}, 价格{role[3]})")
        
        return True
        
    except Exception as e:
        print(f"验证失败: {e}")
        return False

if __name__ == "__main__":
    verify_migration()
