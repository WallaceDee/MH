#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
紧急迁移脚本 - 磁盘空间不足时使用
超小批次，最小内存占用，避免锁等待
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

class EmergencyMigrator:
    """紧急迁移器 - 最小资源占用"""
    
    def __init__(self, equip_db_path, mysql_config):
        self.equip_db_path = equip_db_path
        
        # SQLite连接
        self.equip_conn = sqlite3.connect(equip_db_path)
        self.equip_conn.row_factory = sqlite3.Row
        
        # MySQL连接配置
        mysql_url = f"mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}?charset={mysql_config['charset']}"
        self.mysql_engine = create_engine(
            mysql_url, 
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                'connect_timeout': 60,
                'read_timeout': 60,
                'write_timeout': 60
            }
        )
    
    def migrate_emergency(self, start_offset=39400):
        """紧急模式迁移 - 超小批次"""
        print(f"🚨 紧急迁移模式 - 从位置 {start_offset} 开始")
        
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
        
        # 超小批次处理
        batch_size = 10  # 极小批次
        offset = start_offset
        migrated_count = 0
        error_count = 0
        
        while offset < total_count:
            # 每个批次创建新会话
            Session = sessionmaker(bind=self.mysql_engine)
            session = Session()
            
            try:
                print(f"   📦 处理: {offset}-{min(offset + batch_size, total_count)}")
                
                # 读取小批次数据
                cursor = self.equip_conn.cursor()
                cursor.execute(f"""
                    SELECT * FROM equipments 
                    LIMIT {batch_size} OFFSET {offset}
                """)
                rows = cursor.fetchall()
                cursor.close()
                
                if not rows:
                    break
                
                # 逐条插入，立即提交
                for row in rows:
                    try:
                        # 检查是否已存在
                        equip_sn = None
                        for i, column in enumerate(columns):
                            if column == 'equip_sn':
                                equip_sn = row[i]
                                break
                        
                        if equip_sn:
                            existing = session.query(Equipment).filter_by(equip_sn=equip_sn).first()
                            if existing:
                                continue
                        
                        # 准备数据
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
                        
                        # 插入单条记录
                        equipment = Equipment(**equipment_data)
                        session.add(equipment)
                        session.commit()  # 立即提交单条记录
                        
                        migrated_count += 1
                        
                    except Exception as e:
                        session.rollback()
                        print(f"     ❌ 记录失败: {str(e)[:50]}...")
                        error_count += 1
                        continue
                
                print(f"   ✅ 批次完成: +{len(rows)}条")
                
            except Exception as e:
                print(f"   ❌ 批次失败: {e}")
                session.rollback()
                break
            finally:
                session.close()
            
            offset += batch_size
            
            # 每100条记录休息1秒
            if (offset - start_offset) % 100 == 0:
                print(f"   💾 进度: {offset}/{total_count} (已迁移:{migrated_count}, 错误:{error_count})")
                time.sleep(1)  # 让系统休息
        
        print(f"\n✅ 紧急迁移完成:")
        print(f"   新迁移: {migrated_count}")
        print(f"   错误: {error_count}")
    
    def close_connections(self):
        """关闭连接"""
        self.equip_conn.close()

def main():
    """主函数"""
    print("🚨 紧急迁移工具 - 磁盘空间不足专用")
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
    migrator = EmergencyMigrator(equip_db_path, mysql_config)
    
    try:
        # 从39400位置继续迁移
        migrator.migrate_emergency(39400)
        print("\n🎉 紧急迁移完成!")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        migrator.close_connections()

if __name__ == "__main__":
    main()
