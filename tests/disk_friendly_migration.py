#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
磁盘友好的迁移脚本
优化内存和磁盘使用，从39400位置继续迁移
"""

import os
import sys
import sqlite3
import time
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.models.equipment import Equipment
from src.database_config import db_config

class DiskFriendlyMigrator:
    """磁盘友好的迁移器"""
    
    def __init__(self, equip_db_path, mysql_config):
        self.equip_db_path = equip_db_path
        self.mysql_config = mysql_config
        
        # 连接SQLite数据库
        self.equip_conn = sqlite3.connect(equip_db_path)
        self.equip_conn.row_factory = sqlite3.Row
        
        # 连接MySQL数据库
        mysql_url = f"mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}?charset={mysql_config['charset']}"
        self.mysql_engine = create_engine(mysql_url, echo=False, pool_pre_ping=True)
        
    def get_new_session(self):
        """获取新的MySQL会话"""
        Session = sessionmaker(bind=self.mysql_engine)
        return Session()
    
    def migrate_from_offset(self, start_offset=39400):
        """从指定位置开始迁移"""
        print(f"🔄 从位置 {start_offset} 开始迁移装备数据...")
        
        # 获取总记录数
        cursor = self.equip_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM equipments")
        total_count = cursor.fetchone()[0]
        cursor.close()
        
        print(f"   总记录数: {total_count}")
        print(f"   剩余记录: {total_count - start_offset}")
        
        # 获取列信息
        cursor = self.equip_conn.cursor()
        cursor.execute("PRAGMA table_info(equipments)")
        columns = [row[1] for row in cursor.fetchall()]
        cursor.close()
        
        # 使用小批次减少内存和磁盘使用
        batch_size = 50  # 减小批次大小
        offset = start_offset
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        while offset < total_count:
            # 为每个批次创建新的会话，避免内存累积
            session = self.get_new_session()
            
            try:
                print(f"   📦 处理批次: {offset}-{min(offset + batch_size, total_count)}")
                
                # 从SQLite读取数据
                cursor = self.equip_conn.cursor()
                cursor.execute(f"""
                    SELECT * FROM equipments 
                    LIMIT {batch_size} OFFSET {offset}
                """)
                rows = cursor.fetchall()
                cursor.close()
                
                if not rows:
                    break
                
                batch_migrated = 0
                batch_skipped = 0
                batch_errors = 0
                
                # 逐条处理，减少内存使用
                for row in rows:
                    try:
                        # 检查是否已存在
                        equip_sn = row[columns.index('equip_sn')] if 'equip_sn' in columns else None
                        if equip_sn:
                            existing = session.query(Equipment).filter_by(equip_sn=equip_sn).first()
                            if existing:
                                batch_skipped += 1
                                continue
                        
                        # 创建Equipment对象
                        equipment_data = {}
                        for i, column in enumerate(columns):
                            if hasattr(Equipment, column):
                                value = row[i]
                                if value is not None:
                                    if column in ['accept_bargain', 'pass_fair_show', 'has_collect']:
                                        equipment_data[column] = 1 if value else 0
                                    else:
                                        equipment_data[column] = value
                                else:
                                    equipment_data[column] = None
                        
                        # 设置时间戳
                        now = datetime.utcnow()
                        equipment_data['create_time'] = now
                        equipment_data['update_time'] = now
                        
                        # 创建并添加Equipment对象
                        equipment = Equipment(**equipment_data)
                        session.add(equipment)
                        batch_migrated += 1
                        
                    except Exception as e:
                        print(f"     ❌ 单条记录失败: {str(e)[:100]}...")
                        batch_errors += 1
                        continue
                
                # 提交批次
                try:
                    session.commit()
                    migrated_count += batch_migrated
                    skipped_count += batch_skipped
                    error_count += batch_errors
                    
                    print(f"   ✅ 批次完成: 迁移{batch_migrated}, 跳过{batch_skipped}, 错误{batch_errors}")
                    
                except Exception as e:
                    print(f"   ❌ 批次提交失败: {e}")
                    session.rollback()
                    break
                    
            finally:
                # 关闭会话释放资源
                session.close()
                
            offset += batch_size
            
            # 每100批次休息一下，让系统喘口气
            if (offset - start_offset) % 5000 == 0:
                print(f"   😴 休息2秒，释放系统资源...")
                time.sleep(2)
        
        print(f"\n✅ 迁移完成:")
        print(f"   新迁移: {migrated_count}")
        print(f"   跳过重复: {skipped_count}")
        print(f"   错误: {error_count}")
        print(f"   总处理: {migrated_count + skipped_count + error_count}")
    
    def close_connections(self):
        """关闭连接"""
        self.equip_conn.close()

def main():
    """主函数"""
    print("🚀 磁盘友好迁移工具 - 从39400位置继续")
    print("=" * 50)
    
    # SQLite数据库路径
    equip_db_path = os.path.join(project_root, "data", "202509", "cbg_equip_202509.db")
    
    if not os.path.exists(equip_db_path):
        print(f"❌ 装备数据库文件不存在: {equip_db_path}")
        return
    
    if not db_config.is_mysql():
        print("❌ 当前配置不是MySQL数据库")
        return
    
    mysql_config = db_config.config
    print(f"🔗 MySQL数据库: {mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}")
    
    # 创建迁移器
    migrator = DiskFriendlyMigrator(equip_db_path, mysql_config)
    
    try:
        # 从39400位置继续迁移
        migrator.migrate_from_offset(39400)
        print("\n🎉 断点续传完成!")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        migrator.close_connections()

if __name__ == "__main__":
    main()
