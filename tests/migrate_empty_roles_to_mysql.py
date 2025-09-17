#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将空号数据库迁移到MySQL
"""

import os
import sys
import sqlite3
import pymysql
from datetime import datetime
import json

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

# MySQL连接配置
MYSQL_CONFIG = {
    'host': '47.86.33.98',
    'port': 3306,
    'user': 'lingtong',
    'password': '447363121',
    'database': 'cbg_spider',
    'charset': 'utf8mb4'
}

def test_mysql_connection():
    """测试MySQL连接"""
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        print("✅ MySQL连接成功!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        return False

def migrate_empty_roles():
    """迁移空号数据到MySQL"""
    sqlite_db_path = r"C:\Users\Administrator\Desktop\mh\data\202506\cbg_empty_roles_202509.db"
    
    if not os.path.exists(sqlite_db_path):
        print(f"❌ SQLite数据库文件不存在: {sqlite_db_path}")
        return False
    
    # 测试MySQL连接
    if not test_mysql_connection():
        return False
    
    try:
        # 连接SQLite
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_cursor = sqlite_conn.cursor()
        
        # 连接MySQL
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        mysql_cursor = mysql_conn.cursor()
        
        # 获取SQLite中的roles数据
        sqlite_cursor.execute("SELECT * FROM roles")
        roles_data = sqlite_cursor.fetchall()
        
        # 获取roles表的列名
        sqlite_cursor.execute("PRAGMA table_info(roles)")
        columns_info = sqlite_cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        print(f"📊 SQLite roles表有 {len(roles_data)} 条记录")
        print(f"📊 SQLite roles表有 {len(column_names)} 个字段")
        
        # 准备插入MySQL的SQL语句
        # 添加role_type字段，设置为'empty'
        mysql_column_names = column_names + ['role_type']
        # 对保留字添加反引号
        escaped_column_names = [f"`{col}`" for col in mysql_column_names]
        placeholders = ', '.join(['%s'] * len(mysql_column_names))
        insert_sql = f"""
        INSERT INTO roles ({', '.join(escaped_column_names)}) 
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE
            `role_type` = VALUES(`role_type`),
            `update_time` = NOW()
        """
        
        # 批量插入数据
        batch_size = 100
        success_count = 0
        error_count = 0
        
        for i in range(0, len(roles_data), batch_size):
            batch = roles_data[i:i + batch_size]
            batch_data = []
            
            for row in batch:
                # 将SQLite数据转换为MySQL格式，并添加role_type='empty'
                mysql_row = list(row) + ['empty']
                batch_data.append(mysql_row)
            
            try:
                mysql_cursor.executemany(insert_sql, batch_data)
                mysql_conn.commit()
                success_count += len(batch)
                print(f"✅ 已迁移 {success_count}/{len(roles_data)} 条roles记录")
            except Exception as e:
                error_count += len(batch)
                print(f"❌ 批次迁移失败: {e}")
                continue
        
        # 迁移large_equip_desc_data表
        print("\n开始迁移large_equip_desc_data表...")
        sqlite_cursor.execute("SELECT * FROM large_equip_desc_data")
        desc_data = sqlite_cursor.fetchall()
        
        # 获取large_equip_desc_data表的列名
        sqlite_cursor.execute("PRAGMA table_info(large_equip_desc_data)")
        desc_columns_info = sqlite_cursor.fetchall()
        desc_column_names = [col[1] for col in desc_columns_info]
        
        print(f"📊 SQLite large_equip_desc_data表有 {len(desc_data)} 条记录")
        
        if len(desc_data) > 0:
            # 对保留字添加反引号
            escaped_desc_column_names = [f"`{col}`" for col in desc_column_names]
            desc_placeholders = ', '.join(['%s'] * len(desc_column_names))
            desc_insert_sql = f"""
            INSERT INTO large_equip_desc_data ({', '.join(escaped_desc_column_names)}) 
            VALUES ({desc_placeholders})
            ON DUPLICATE KEY UPDATE
                `update_time` = NOW()
            """
            
            desc_success_count = 0
            desc_error_count = 0
            
            for i in range(0, len(desc_data), batch_size):
                batch = desc_data[i:i + batch_size]
                
                try:
                    mysql_cursor.executemany(desc_insert_sql, batch)
                    mysql_conn.commit()
                    desc_success_count += len(batch)
                    print(f"✅ 已迁移 {desc_success_count}/{len(desc_data)} 条large_equip_desc_data记录")
                except Exception as e:
                    desc_error_count += len(batch)
                    print(f"❌ 批次迁移失败: {e}")
                    continue
        
        # 关闭连接
        sqlite_conn.close()
        mysql_conn.close()
        
        print("\n" + "="*60)
        print("🎉 数据迁移完成!")
        print(f"📊 roles表: 成功 {success_count} 条, 失败 {error_count} 条")
        if len(desc_data) > 0:
            print(f"📊 large_equip_desc_data表: 成功 {desc_success_count} 条, 失败 {desc_error_count} 条")
        print("🏷️  所有迁移的角色已标记为 role_type='empty'")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_migration():
    """验证迁移结果"""
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        mysql_cursor = mysql_conn.cursor()
        
        # 查询empty类型的角色数量
        mysql_cursor.execute("SELECT COUNT(*) FROM roles WHERE role_type = 'empty'")
        empty_count = mysql_cursor.fetchone()[0]
        
        # 查询总角色数量
        mysql_cursor.execute("SELECT COUNT(*) FROM roles")
        total_count = mysql_cursor.fetchone()[0]
        
        print(f"\n📊 验证结果:")
        print(f"   总角色数量: {total_count}")
        print(f"   空号数量: {empty_count}")
        print(f"   普通角色数量: {total_count - empty_count}")
        
        # 显示一些空号记录示例
        mysql_cursor.execute("SELECT eid, equip_name, server_name, role_type FROM roles WHERE role_type = 'empty' LIMIT 5")
        examples = mysql_cursor.fetchall()
        
        if examples:
            print(f"\n📋 空号记录示例:")
            for eid, name, server, role_type in examples:
                print(f"   {eid} | {name} | {server} | {role_type}")
        
        mysql_conn.close()
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")

if __name__ == "__main__":
    print("🚀 开始迁移空号数据到MySQL...")
    print("="*60)
    
    if migrate_empty_roles():
        verify_migration()
    else:
        print("❌ 迁移失败!")
