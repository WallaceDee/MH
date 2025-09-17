#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQLite到MySQL数据迁移脚本
将SQLite数据库中的数据迁移到MySQL数据库
"""

import os
import sys
import sqlite3
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.models.equipment import Equipment
from src.models.pet import Pet
from src.database_config import db_config

class DataMigrator:
    """数据迁移器"""
    
    def __init__(self, equip_db_path, pet_db_path, mysql_config):
        self.equip_db_path = equip_db_path
        self.pet_db_path = pet_db_path
        self.mysql_config = mysql_config
        
        # 连接SQLite数据库
        self.equip_conn = sqlite3.connect(equip_db_path)
        self.equip_conn.row_factory = sqlite3.Row
        
        self.pet_conn = sqlite3.connect(pet_db_path)
        self.pet_conn.row_factory = sqlite3.Row
        
        # 连接MySQL数据库
        mysql_url = f"mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}?charset={mysql_config['charset']}"
        self.mysql_engine = create_engine(mysql_url, echo=False)
        self.mysql_session = sessionmaker(bind=self.mysql_engine)()
        
    def get_table_info(self, conn, table_name):
        """获取表信息"""
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    
    def get_table_columns(self, conn, table_name):
        """获取表的列信息"""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        cursor.close()
        return columns
    
    def migrate_equipments(self, resume_from_offset=None):
        """迁移装备数据"""
        print("📦 开始迁移装备数据...")
        
        # 获取装备表信息
        total_count = self.get_table_info(self.equip_conn, 'equipments')
        print(f"   总记录数: {total_count}")
        
        if total_count == 0:
            print("   ⚠️ 装备表为空，跳过迁移")
            return
        
        # 获取列信息
        columns = self.get_table_columns(self.equip_conn, 'equipments')
        print(f"   列数: {len(columns)}")
        
        # 检查MySQL中已有的数据量，用于断点续传
        mysql_existing_count = self.mysql_session.query(Equipment).count()
        print(f"   MySQL中已有记录数: {mysql_existing_count}")
        
        # 分批迁移数据
        batch_size = 100
        
        # 如果指定了恢复位置，使用指定位置；否则从MySQL已有数据量开始
        if resume_from_offset is not None:
            offset = resume_from_offset
            print(f"   🔄 从指定位置恢复: offset={offset}")
        else:
            # 计算应该从哪里开始（考虑已迁移的数据）
            offset = (mysql_existing_count // batch_size) * batch_size
            print(f"   🔄 自动计算恢复位置: offset={offset}")
        
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        while offset < total_count:
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
                
                # 转换为MySQL格式并插入
                for row in rows:
                    try:
                        # 创建Equipment对象
                        equipment_data = {}
                        for i, column in enumerate(columns):
                            value = row[i]
                            # 跳过不存在的字段
                            if not hasattr(Equipment, column):
                                continue
                                
                            # 处理数据类型转换
                            if value is not None:
                                if column in ['accept_bargain', 'pass_fair_show', 'has_collect', 
                                            'allow_cross_buy', 'joined_seller_activity', 'is_split_sale',
                                            'is_split_main_role', 'is_split_independent_role',
                                            'is_split_independent_equip', 'split_equip_sold_happen',
                                            'show_split_equip_sold_remind', 'is_onsale_protection_period',
                                            'is_vip_protection', 'is_time_lock', 'equip_in_test_server',
                                            'buyer_in_test_server', 'equip_in_allow_take_away_server',
                                            'is_weijianding', 'is_show_alipay_privilege',
                                            'is_seller_redpacket_flag', 'is_show_expert_desc',
                                            'is_show_special_highlight', 'is_xyq_game_role_kunpeng_reach_limit']:
                                    # 布尔字段转换为整数
                                    equipment_data[column] = 1 if value else 0
                                else:
                                    equipment_data[column] = value
                            else:
                                equipment_data[column] = None
                        
                        # 设置时间戳
                        now = datetime.utcnow()
                        equipment_data['create_time'] = now
                        equipment_data['update_time'] = now
                        
                        # 检查是否已存在该记录
                        existing = self.mysql_session.query(Equipment).filter_by(equip_sn=equipment_data['equip_sn']).first()
                        if existing:
                            # 跳过重复记录
                            skipped_count += 1
                            continue
                            
                        # 创建Equipment对象
                        equipment = Equipment(**equipment_data)
                        self.mysql_session.add(equipment)
                        
                        migrated_count += 1
                        
                    except Exception as e:
                        print(f"   ❌ 迁移装备数据失败: {e}")
                        error_count += 1
                        continue
                
                # 提交批次
                try:
                    self.mysql_session.commit()
                    offset += batch_size
                    print(f"   进度: {min(offset, total_count)}/{total_count} (已迁移:{migrated_count}, 跳过:{skipped_count}, 错误:{error_count})")
                    
                    # 每1000条记录保存一次进度
                    if offset % 1000 == 0:
                        print(f"   💾 进度检查点: offset={offset}")
                        
                except Exception as e:
                    print(f"   ❌ 提交装备数据失败: {e}")
                    print(f"   💾 当前进度: offset={offset}, 可从此位置恢复")
                    self.mysql_session.rollback()
                    break
        
        print(f"✅ 装备数据迁移完成:")
        print(f"   新迁移: {migrated_count}")
        print(f"   跳过重复: {skipped_count}")
        print(f"   错误: {error_count}")
        print(f"   总计处理: {migrated_count + skipped_count + error_count}/{total_count}")
    
    def migrate_pets(self):
        """迁移宠物数据"""
        print("🐾 开始迁移宠物数据...")
        
        # 获取宠物表信息
        total_count = self.get_table_info(self.pet_conn, 'pets')
        print(f"   总记录数: {total_count}")
        
        if total_count == 0:
            print("   ⚠️ 宠物表为空，跳过迁移")
            return
        
        # 获取列信息
        columns = self.get_table_columns(self.pet_conn, 'pets')
        print(f"   列数: {len(columns)}")
        
        # 分批迁移数据
        batch_size = 1000
        offset = 0
        migrated_count = 0
        
        while offset < total_count:
                # 从SQLite读取数据
                cursor = self.pet_conn.cursor()
                cursor.execute(f"""
                    SELECT * FROM pets 
                    LIMIT {batch_size} OFFSET {offset}
                """)
                rows = cursor.fetchall()
                cursor.close()
                
                if not rows:
                    break
                
                # 转换为MySQL格式并插入
                for row in rows:
                    try:
                        # 创建Pet对象
                        pet_data = {}
                        for i, column in enumerate(columns):
                            value = row[i]
                            # 跳过不存在的字段
                            if not hasattr(Pet, column):
                                continue
                                
                            # 处理数据类型转换
                            if value is not None:
                                if column in ['accept_bargain', 'pass_fair_show', 'has_collect', 
                                            'allow_cross_buy', 'joined_seller_activity', 'is_split_sale',
                                            'is_split_main_role', 'is_split_independent_role',
                                            'is_split_independent_equip', 'split_equip_sold_happen',
                                            'show_split_equip_sold_remind', 'is_onsale_protection_period',
                                            'is_vip_protection', 'is_time_lock', 'equip_in_test_server',
                                            'buyer_in_test_server', 'equip_in_allow_take_away_server',
                                            'is_weijianding', 'is_show_alipay_privilege',
                                            'is_seller_redpacket_flag', 'is_show_expert_desc',
                                            'is_show_special_highlight', 'is_xyq_game_role_kunpeng_reach_limit']:
                                    # 布尔字段转换为整数
                                    pet_data[column] = 1 if value else 0
                                else:
                                    pet_data[column] = value
                            else:
                                pet_data[column] = None
                        
                        # 设置时间戳
                        now = datetime.utcnow()
                        pet_data['create_time'] = now
                        pet_data['update_time'] = now
                        
                        # 检查是否已存在该记录
                        existing = self.mysql_session.query(Pet).filter_by(eid=pet_data['eid']).first()
                        if existing:
                            # 跳过重复记录
                            continue
                            
                        # 创建Pet对象
                        pet = Pet(**pet_data)
                        self.mysql_session.add(pet)
                        
                        migrated_count += 1
                        
                    except Exception as e:
                        print(f"   ❌ 迁移宠物数据失败: {e}")
                        continue
                
                # 提交批次
                try:
                    self.mysql_session.commit()
                    offset += batch_size
                    print(f"   进度: {min(offset, total_count)}/{total_count}")
                except Exception as e:
                    print(f"   ❌ 提交宠物数据失败: {e}")
                    self.mysql_session.rollback()
                    break
        
        print(f"✅ 宠物数据迁移完成: {migrated_count}/{total_count}")
    
    def check_migration_status(self):
        """检查迁移状态"""
        print("\n📊 迁移状态检查...")
        
        # 检查SQLite数据
        cursor = self.equip_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM equipments")
        sqlite_equip_count = cursor.fetchone()[0]
        cursor.close()
        
        cursor = self.pet_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pets")
        sqlite_pet_count = cursor.fetchone()[0]
        cursor.close()
        
        # 检查MySQL数据
        mysql_equip_count = self.mysql_session.query(Equipment).count()
        mysql_pet_count = self.mysql_session.query(Pet).count()
        
        print(f"   装备数据: SQLite({sqlite_equip_count}) -> MySQL({mysql_equip_count})")
        print(f"   宠物数据: SQLite({sqlite_pet_count}) -> MySQL({mysql_pet_count})")
        
        # 验证迁移结果
        if sqlite_equip_count == mysql_equip_count:
            print("   ✅ 装备数据迁移成功")
        else:
            print("   ⚠️ 装备数据迁移不完整")
            
        if sqlite_pet_count == mysql_pet_count:
            print("   ✅ 宠物数据迁移成功")
        else:
            print("   ⚠️ 宠物数据迁移不完整")
    
    def close_connections(self):
        """关闭数据库连接"""
        self.equip_conn.close()
        self.pet_conn.close()
        self.mysql_session.close()

def main():
    """主函数"""
    print("🚀 CBG爬虫项目 - SQLite到MySQL数据迁移工具")
    print("=" * 60)
    
    # SQLite数据库路径
    equip_db_path = r"C:\Users\Administrator\Desktop\mh\data\202509\cbg_equip_202509.db"
    pet_db_path = r"C:\Users\Administrator\Desktop\mh\data\202509\cbg_pets_202509.db"
    
    # 检查SQLite文件是否存在
    if not os.path.exists(equip_db_path):
        print(f"❌ 装备数据库文件不存在: {equip_db_path}")
        return
        
    if not os.path.exists(pet_db_path):
        print(f"❌ 宠物数据库文件不存在: {pet_db_path}")
        return
    
    print(f"📁 装备数据库: {equip_db_path}")
    print(f"📁 宠物数据库: {pet_db_path}")
    
    # 获取MySQL配置
    if not db_config.is_mysql():
        print("❌ 当前配置不是MySQL数据库")
        return
    
    mysql_config = db_config.config
    print(f"🔗 MySQL数据库: {mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}")
    
    # 创建迁移器
    migrator = DataMigrator(equip_db_path, pet_db_path, mysql_config)
    
    try:
        # 检查当前迁移状态
        print("\n🔍 检查当前迁移状态...")
        migrator.check_migration_status()
        
        # 询问是否从断点继续
        print("\n⚠️ 检测到装备数据迁移不完整")
        print("选择操作:")
        print("1. 从断点继续迁移（推荐）")
        print("2. 从指定位置继续")
        print("3. 重新开始迁移")
        
        choice = input("请选择 [1/2/3]: ").strip()
        
        if choice == "1":
            # 从断点继续迁移
            print("\n🔄 从断点继续迁移...")
            migrator.migrate_equipments()
        elif choice == "2":
            # 从指定位置继续
            resume_offset = input("请输入恢复位置 (如: 39400): ").strip()
            try:
                resume_offset = int(resume_offset)
                print(f"\n🔄 从位置 {resume_offset} 继续迁移...")
                migrator.migrate_equipments(resume_from_offset=resume_offset)
            except ValueError:
                print("❌ 无效的位置数字")
                return
        elif choice == "3":
            # 重新开始迁移
            print("\n🔄 重新开始迁移...")
            # 清空MySQL表
            confirm = input("⚠️ 确认要清空MySQL装备表重新迁移吗? [y/N]: ").strip().lower()
            if confirm == 'y':
                print("🗑️ 清空MySQL装备表...")
                migrator.mysql_session.query(Equipment).delete()
                migrator.mysql_session.commit()
                migrator.migrate_equipments(resume_from_offset=0)
            else:
                print("❌ 取消操作")
                return
        else:
            print("❌ 无效选择")
            return
        
        # 迁移宠物数据（如果需要）
        print("\n🐾 检查宠物数据迁移状态...")
        pet_migrated = migrator.mysql_session.query(Pet).count()
        pet_total = migrator.get_table_info(migrator.pet_conn, 'pets')
        
        if pet_migrated < pet_total:
            migrate_pets = input(f"宠物数据迁移不完整 ({pet_migrated}/{pet_total})，是否迁移? [y/N]: ").strip().lower()
            if migrate_pets == 'y':
                migrator.migrate_pets()
        
        # 最终检查迁移状态
        print("\n📊 最终迁移状态:")
        migrator.check_migration_status()
        
        print("\n🎉 数据迁移任务完成!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ 用户中断迁移")
        print(f"💾 当前可以从 offset={offset if 'offset' in locals() else 0} 恢复")
    except Exception as e:
        print(f"\n❌ 迁移过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        migrator.close_connections()

if __name__ == "__main__":
    main()
