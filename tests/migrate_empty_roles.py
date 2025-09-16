#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将SQLite中的空角色数据迁移到MySQL
设置role_type为'empty'
并更新MySQL中large_equip_desc长度大于50000的数据
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
        logging.FileHandler('migration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmptyRolesMigrator:
    """空角色数据迁移器"""
    
    def __init__(self):
        self.sqlite_path = 'data/cbg_roles.db'
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
    
    def get_large_desc_data(self) -> List[Dict[str, Any]]:
        """获取SQLite中large_equip_desc长度大于50000的数据"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询large_equip_desc长度大于50000的数据
            query = """
                SELECT eid, large_equip_desc 
                FROM roles 
                WHERE LENGTH(large_equip_desc) > 50000
                ORDER BY LENGTH(large_equip_desc) DESC
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            data = []
            
            for row in rows:
                data.append({
                    'eid': row['eid'],
                    'large_equip_desc': row['large_equip_desc']
                })
            
            conn.close()
            logger.info(f"找到 {len(data)} 条large_equip_desc长度大于50000的数据")
            return data
            
        except Exception as e:
            logger.error(f"获取大字段数据失败: {e}")
            return []
    
    def update_mysql_large_desc(self, large_desc_data: List[Dict[str, Any]]):
        """更新MySQL中对应记录的large_equip_desc字段"""
        try:
            logger.info(f"开始更新MySQL中 {len(large_desc_data)} 条记录的large_equip_desc字段...")
            
            success_count = 0
            error_count = 0
            
            for item in large_desc_data:
                eid = item['eid']
                large_equip_desc = item['large_equip_desc']
                
                try:
                    # 更新MySQL中对应记录的large_equip_desc字段
                    update_query = text("""
                        UPDATE roles 
                        SET large_equip_desc = :large_equip_desc,
                            update_time = :update_time
                        WHERE eid = :eid
                    """)
                    
                    result = self.mysql_session.execute(update_query, {
                        'eid': eid,
                        'large_equip_desc': large_equip_desc,
                        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    if result.rowcount > 0:
                        success_count += 1
                        logger.info(f"[成功] 更新成功: eid={eid}, 长度={len(large_equip_desc)}")
                    else:
                        logger.warning(f"[警告] 未找到对应记录: eid={eid}")
                        error_count += 1
                    
                    # 每100条提交一次
                    if success_count % 100 == 0:
                        self.mysql_session.commit()
                        logger.info(f"已提交 {success_count} 条更新")
                    
                except Exception as e:
                    self.mysql_session.rollback()
                    logger.error(f"更新eid={eid}失败: {e}")
                    error_count += 1
                    continue
            
            # 提交剩余的更新
            self.mysql_session.commit()
            
            logger.info(f"large_equip_desc字段更新完成: 成功 {success_count} 条, 失败 {error_count} 条")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"更新large_equip_desc字段失败: {e}")
            return False
    
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
            
            # 检查large_equip_desc长度大于50000的记录
            result = self.mysql_session.execute(text("SELECT COUNT(*) FROM roles WHERE LENGTH(large_equip_desc) > 50000"))
            large_desc_count = result.fetchone()[0]
            logger.info(f"MySQL中large_equip_desc长度大于50000的记录数量: {large_desc_count}")
            
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
            # 迁移roles数据
            if not self.migrate_roles_data():
                logger.error("迁移roles数据失败")
                return False
            
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
    
    def run_large_desc_update(self):
        """执行large_equip_desc字段更新流程"""
        logger.info("开始执行large_equip_desc字段更新...")
        
        # 连接数据库
        if not self.connect_databases():
            return False
        
        try:
            # 获取SQLite中大字段数据
            large_desc_data = self.get_large_desc_data()
            if not large_desc_data:
                logger.warning("没有找到需要更新的大字段数据")
                return True
            
            # 更新MySQL中的large_equip_desc字段
            if not self.update_mysql_large_desc(large_desc_data):
                logger.error("更新large_equip_desc字段失败")
                return False
            
            # 验证更新结果
            if not self.verify_migration():
                logger.error("验证更新结果失败")
                return False
            
            logger.info("large_equip_desc字段更新完成!")
            return True
            
        except Exception as e:
            logger.error(f"更新过程中发生错误: {e}")
            return False
        
        finally:
            if self.mysql_session:
                self.mysql_session.close()

def main():
    """主函数"""
    migrator = EmptyRolesMigrator()
    
    # 选择执行模式
    print("请选择执行模式:")
    print("1. 执行完整迁移流程")
    print("2. 仅更新large_equip_desc字段")
    print("3. 仅验证数据")
    
    choice = input("请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        success = migrator.run_migration()
    elif choice == "2":
        success = migrator.run_large_desc_update()
    elif choice == "3":
        success = migrator.connect_databases() and migrator.verify_migration()
    else:
        print("无效选择，默认执行large_equip_desc字段更新")
        success = migrator.run_large_desc_update()
    
    if success:
        print("操作成功完成!")
    else:
        print("操作失败，请查看日志文件 migration.log")
        sys.exit(1)

if __name__ == "__main__":
    main()
