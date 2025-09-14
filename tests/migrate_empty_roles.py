#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将SQLite中的空角色数据迁移到MySQL
设置role_type为'empty'
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database_config import db_config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.models.role import Role, LargeEquipDescData

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmptyRolesMigrator:
    """空角色数据迁移器"""
    
    def __init__(self):
        self.sqlite_path = 'data/cbg_empty_roles.db'
        self.mysql_engine = None
        self.mysql_session = None
        self.batch_size = 100  # 批量处理大小
        
    def connect_databases(self):
        """连接数据库"""
        try:
            # 连接SQLite
            if not os.path.exists(self.sqlite_path):
                raise FileNotFoundError(f"SQLite数据库文件不存在: {self.sqlite_path}")
            
            # 连接MySQL
            mysql_url = db_config.get_database_url('roles')
            self.mysql_engine = create_engine(mysql_url, echo=False)
            self.mysql_session = sessionmaker(bind=self.mysql_engine)()
            
            logger.info("数据库连接成功")
            return True
            
        except Exception as e:
            logger.error(f"连接数据库失败: {e}")
            return False
    
    def get_sqlite_data(self, table_name: str, limit: int = None) -> List[Dict[str, Any]]:
        """从SQLite获取数据"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row  # 使结果可以按列名访问
            cursor = conn.cursor()
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # 查询数据
            if limit:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            else:
                cursor.execute(f"SELECT * FROM {table_name}")
            
            rows = cursor.fetchall()
            data = []
            
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[i]
                data.append(row_dict)
            
            conn.close()
            logger.info(f"从SQLite {table_name} 表获取了 {len(data)} 条数据")
            return data
            
        except Exception as e:
            logger.error(f"从SQLite获取数据失败: {e}")
            return []
    
    def migrate_roles_data(self):
        """迁移roles表数据"""
        try:
            logger.info("开始迁移roles表数据...")
            
            # 获取SQLite数据
            roles_data = self.get_sqlite_data('roles')
            if not roles_data:
                logger.warning("没有找到roles数据")
                return False
            
            # 批量插入MySQL
            success_count = 0
            error_count = 0
            
            for i in range(0, len(roles_data), self.batch_size):
                batch = roles_data[i:i + self.batch_size]
                
                try:
                    # 为每个角色设置role_type为'empty'
                    for role_data in batch:
                        role_data['role_type'] = 'empty'
                    
                    # 逐条插入数据
                    for role_data in batch:
                        try:
                            # 处理Boolean字段的-1值问题
                            boolean_fields = [
                                'accept_bargain', 'pass_fair_show', 'has_collect', 'allow_cross_buy',
                                'joined_seller_activity', 'is_split_sale', 'is_split_main_role',
                                'is_split_independent_role', 'is_split_independent_equip',
                                'split_equip_sold_happen', 'show_split_equip_sold_remind',
                                'is_onsale_protection_period', 'is_vip_protection', 'is_time_lock',
                                'equip_in_test_server', 'buyer_in_test_server',
                                'equip_in_allow_take_away_server', 'is_weijianding',
                                'is_show_alipay_privilege', 'is_seller_redpacket_flag',
                                'is_show_expert_desc', 'is_show_special_highlight',
                                'is_xyq_game_role_kunpeng_reach_limit'
                            ]
                            
                            for field in boolean_fields:
                                if field in role_data and role_data[field] == -1:
                                    role_data[field] = None
                                elif field in role_data and role_data[field] not in [0, 1, None, True, False]:
                                    role_data[field] = bool(role_data[field]) if role_data[field] is not None else None
                            
                            # 使用ORM方式插入
                            role_obj = Role(**role_data)
                            self.mysql_session.add(role_obj)
                            self.mysql_session.commit()
                        except Exception as e:
                            self.mysql_session.rollback()
                            logger.warning(f"插入单条数据失败: {e}")
                            continue
                    
                    success_count += len(batch)
                    logger.info(f"已迁移 {success_count}/{len(roles_data)} 条roles数据")
                    
                except Exception as e:
                    error_count += len(batch)
                    logger.error(f"批量插入失败: {e}")
                    continue
            
            logger.info(f"roles表迁移完成: 成功 {success_count} 条, 失败 {error_count} 条")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"迁移roles数据失败: {e}")
            return False
    
    def migrate_large_equip_desc_data(self):
        """迁移large_equip_desc_data表数据"""
        try:
            logger.info("开始迁移large_equip_desc_data表数据...")
            
            # 获取SQLite数据
            desc_data = self.get_sqlite_data('large_equip_desc_data')
            if not desc_data:
                logger.warning("没有找到large_equip_desc_data数据")
                return False
            
            # 批量插入MySQL
            success_count = 0
            error_count = 0
            
            for i in range(0, len(desc_data), self.batch_size):
                batch = desc_data[i:i + self.batch_size]
                batch_success = 0
                
                # 逐条插入数据
                for desc_item in batch:
                    try:
                        # 使用ORM方式插入
                        desc_obj = LargeEquipDescData(**desc_item)
                        self.mysql_session.add(desc_obj)
                        self.mysql_session.commit()
                        batch_success += 1
                    except Exception as e:
                        self.mysql_session.rollback()
                        logger.warning(f"插入单条large_equip_desc_data失败: {e}")
                        error_count += 1
                        continue
                
                success_count += batch_success
                logger.info(f"已迁移 {success_count}/{len(desc_data)} 条large_equip_desc_data数据")
            
            logger.info(f"large_equip_desc_data表迁移完成: 成功 {success_count} 条, 失败 {error_count} 条")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"迁移large_equip_desc_data数据失败: {e}")
            return False
    
    def verify_migration(self):
        """验证迁移结果"""
        try:
            logger.info("开始验证迁移结果...")
            
            # 检查roles表
            result = self.mysql_session.execute(text("SELECT COUNT(*) FROM roles WHERE role_type = 'empty'"))
            empty_roles_count = result.fetchone()[0]
            logger.info(f"MySQL中role_type为'empty'的角色数量: {empty_roles_count}")
            
            # 检查large_equip_desc_data表
            result = self.mysql_session.execute(text("SELECT COUNT(*) FROM large_equip_desc_data"))
            desc_data_count = result.fetchone()[0]
            logger.info(f"MySQL中large_equip_desc_data表数据数量: {desc_data_count}")
            
            return True
            
        except Exception as e:
            logger.error(f"验证迁移结果失败: {e}")
            return False
    
    def run_migration(self):
        """执行完整迁移流程"""
        logger.info("开始执行空角色数据迁移...")
        
        # 连接数据库
        if not self.connect_databases():
            return False
        
        try:
            # # 迁移roles数据
            # if not self.migrate_roles_data():
            #     logger.error("迁移roles数据失败")
            #     return False
            
            # 迁移large_equip_desc_data数据
            if not self.migrate_large_equip_desc_data():
                logger.error("迁移large_equip_desc_data数据失败")
                return False
            
            # 验证迁移结果
            if not self.verify_migration():
                logger.error("验证迁移结果失败")
                return False
            
            logger.info("空角色数据迁移完成!")
            return True
            
        except Exception as e:
            logger.error(f"迁移过程中发生错误: {e}")
            return False
        
        finally:
            if self.mysql_session:
                self.mysql_session.close()

def main():
    """主函数"""
    migrator = EmptyRolesMigrator()
    success = migrator.run_migration()
    
    if success:
        print("数据迁移成功完成!")
    else:
        print("数据迁移失败，请查看日志文件 migration.log")
        sys.exit(1)

if __name__ == "__main__":
    main()
