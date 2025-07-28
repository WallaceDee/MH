#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库迁移脚本：修改addon_status字段类型
将addon_status字段从INTEGER类型修改为TEXT类型
"""

import sqlite3
import os
import logging
from datetime import datetime
import sys

# 添加项目根目录到 Python 路径
from src.utils.project_path import get_project_root, get_data_path

class AddonStatusMigrator:
    """addon_status字段类型迁移器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """设置日志"""
        logger = logging.getLogger('AddonStatusMigrator')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def check_field_type(self, table_name: str) -> str:
        """检查addon_status字段的当前类型"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = cursor.fetchall()
                
                for col in columns_info:
                    if col[1] == 'addon_status':  # col[1] 是字段名
                        current_type = col[2]  # col[2] 是字段类型
                        print(f"表 {table_name} 中 addon_status 字段当前类型: {current_type}")
                        return current_type
                
                print(f"表 {table_name} 中未找到 addon_status 字段")
                return None
                
        except Exception as e:
            print(f"检查字段类型失败: {e}")
            return None
    
    def migrate_table(self, table_name: str) -> bool:
        """迁移指定表的addon_status字段"""
        try:
            # 检查字段当前类型
            current_type = self.check_field_type(table_name)
            if current_type is None:
                print(f"表 {table_name} 中未找到 addon_status 字段，跳过")
                return True
            
            if current_type.upper() == 'TEXT':
                print(f"表 {table_name} 中 addon_status 字段已经是TEXT类型，无需迁移")
                return True
            
            print(f"开始迁移表 {table_name} 的 addon_status 字段...")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取表的所有列信息
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = cursor.fetchall()
                
                # 构建新表的列定义
                column_defs = []
                for col in columns_info:
                    col_name = col[1]
                    col_type = col[2]
                    col_notnull = col[3]
                    col_default = col[4]
                    col_pk = col[5]
                    
                    # 如果是addon_status字段，修改为TEXT类型
                    if col_name == 'addon_status':
                        col_type = 'TEXT'
                        col_default = None  # 移除默认值
                    
                    col_def = f"{col_name} {col_type}"
                    if col_pk:
                        col_def += " PRIMARY KEY"
                    if col_notnull and not col_pk:
                        col_def += " NOT NULL"
                    if col_default is not None:
                        col_def += f" DEFAULT {col_default}"
                    
                    column_defs.append(col_def)
                
                # 创建临时表
                temp_table = f"{table_name}_temp_{int(datetime.now().timestamp())}"
                create_sql = f"CREATE TABLE {temp_table} ({', '.join(column_defs)})"
                cursor.execute(create_sql)
                
                # 复制数据到临时表
                select_columns = ', '.join([col[1] for col in columns_info])
                cursor.execute(f"INSERT INTO {temp_table} ({select_columns}) SELECT {select_columns} FROM {table_name}")
                
                # 删除原表
                cursor.execute(f"DROP TABLE {table_name}")
                
                # 重命名临时表
                cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")
                
                conn.commit()
                
                print(f"表 {table_name} 迁移完成")
                return True
                
        except Exception as e:
            print(f"迁移表 {table_name} 失败: {e}")
            return False
    
    def migrate_all_tables(self) -> bool:
        """迁移所有包含addon_status字段的表"""
        tables_to_migrate = ['equipments', 'pets']
        success_count = 0
        
        for table_name in tables_to_migrate:
            if self.migrate_table(table_name):
                success_count += 1
        
        print(f"迁移完成: {success_count}/{len(tables_to_migrate)} 个表成功迁移")
        return success_count == len(tables_to_migrate)

def main():
    """主函数"""
    # 获取项目根目录
    project_root = get_project_root()
    
    # 支持命令行参数指定数据库文件名
    if len(sys.argv) > 1:
        db_filename = sys.argv[1]
    else:
        # 获取当前月份
        current_month = datetime.now().strftime('%Y%m')
        db_filename = f"cbg_equip_{current_month}.db"
    
    equip_db_path = os.path.join(get_data_path(), db_filename)
    
    print("🔧 开始迁移 addon_status 字段类型...")
    print(f"📁 数据库路径: {equip_db_path}")
    
    # 检查数据库是否存在
    if not os.path.exists(equip_db_path):
        print(f"❌ 装备数据库不存在: {equip_db_path}")
        print("请先运行装备爬虫获取数据")
        return
    
    print(f"✅ 找到装备数据库: {equip_db_path}")
    
    # 创建迁移器
    migrator = AddonStatusMigrator(equip_db_path)
    
    # 执行迁移
    print("🚀 开始执行迁移...")
    success = migrator.migrate_all_tables()
    
    if success:
        print("✅ 所有表迁移完成！")
    else:
        print("❌ 部分表迁移失败，请检查日志")

if __name__ == "__main__":
    main() 