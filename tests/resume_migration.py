#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
断点续传迁移脚本
从指定位置继续SQLite到MySQL的数据迁移
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tests.helper.migrate_sqlite_to_mysql import DataMigrator
from src.database_config import db_config

def resume_migration_from_39400():
    """从39400位置继续迁移"""
    print("🚀 断点续传迁移工具 - 从39400位置继续")
    print("=" * 60)
    
    # SQLite数据库路径
    equip_db_path = os.path.join(project_root, "data", "202509", "cbg_equip_202509.db")
    pet_db_path = os.path.join(project_root, "data", "202509", "cbg_pets_202509.db")
    
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
        # 显示当前状态
        print("\n📊 当前迁移状态:")
        migrator.check_migration_status()
        
        # 从39400位置继续迁移
        resume_offset = 39400
        print(f"\n🔄 从位置 {resume_offset} 继续装备数据迁移...")
        print("💡 提示：这将跳过已迁移的39400条记录，继续迁移剩余的数据")
        
        confirm = input("确认继续吗? [y/N]: ").strip().lower()
        if confirm != 'y':
            print("❌ 取消操作")
            return
        
        # 开始断点续传
        migrator.migrate_equipments(resume_from_offset=resume_offset)
        
        # 最终检查
        print("\n📊 迁移完成后状态:")
        migrator.check_migration_status()
        
        print("\n🎉 断点续传迁移完成!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ 用户中断迁移")
    except Exception as e:
        print(f"\n❌ 迁移过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        migrator.close_connections()

def quick_status_check():
    """快速状态检查"""
    print("🔍 快速状态检查")
    print("=" * 40)
    
    # SQLite数据库路径
    equip_db_path = os.path.join(project_root, "data", "202509", "cbg_equip_202509.db")
    pet_db_path = os.path.join(project_root, "data", "202509", "cbg_pets_202509.db")
    
    if not os.path.exists(equip_db_path) or not os.path.exists(pet_db_path):
        print("❌ SQLite数据库文件不存在")
        return
    
    if not db_config.is_mysql():
        print("❌ 当前配置不是MySQL数据库")
        return
    
    mysql_config = db_config.config
    migrator = DataMigrator(equip_db_path, pet_db_path, mysql_config)
    
    try:
        migrator.check_migration_status()
    except Exception as e:
        print(f"❌ 检查状态失败: {e}")
    finally:
        migrator.close_connections()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        quick_status_check()
    else:
        resume_migration_from_39400()
