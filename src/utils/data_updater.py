#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新解析每个角色的 large_equip_desc 数据
数据更新工具 - 用于更新历史数据
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
import sys
import time

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.parser.pet_parser import PetParser
from src.parser.equipment_parser import EquipmentParser
from src.parser.shenqi_parser import ShenqiParser
from src.parser.rider_parser import RiderParser
from src.parser.ex_avt_parser import ExAvtParser
from src.utils.lpc_helper import LPCHelper

class DataUpdater:
    def __init__(self, db_path, logger=None):
        self.db_path = db_path
        self.logger = logger or logging.getLogger(__name__)
        
        # 初始化解析器
        self.pet_parser = PetParser(self.logger)
        self.equipment_parser = EquipmentParser(self.logger)
        self.shenqi_parser = ShenqiParser(self.logger)
        self.rider_parser = RiderParser(self.logger)
        self.ex_avt_parser = ExAvtParser(self.logger)
        self.lpc_helper = LPCHelper(self.logger)
    
    def update_character_data(self, character_id=None):
        """
        更新角色数据
        
        Args:
            character_id: 要更新的角色ID，如果为None则更新所有角色
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取要更新的角色
            if character_id:
                cursor.execute("""
                    SELECT c.equip_id, c.seller_nickname, d.raw_data_json
                    FROM characters c
                    JOIN large_equip_desc_data d ON c.equip_id = d.equip_id
                    WHERE c.equip_id = ?
                """, (character_id,))
            else:
                cursor.execute("""
                    SELECT c.equip_id, c.seller_nickname, d.raw_data_json
                    FROM characters c
                    JOIN large_equip_desc_data d ON c.equip_id = d.equip_id
                """)
            
            characters = cursor.fetchall()
            updated_count = 0
            
            for char in characters:
                try:
                    # 获取原始数据
                    equip_id = char[0]  # equip_id
                    seller_nickname = char[1]  # seller_nickname
                    raw_data_json = char[2]  # raw_data_json from large_equip_desc_data
                    
                    if not raw_data_json:
                        continue
                    
                    try:
                        # 解析JSON字符串为Python对象
                        parsed_desc = json.loads(raw_data_json)
                    except json.JSONDecodeError as e:
                        self.logger.error(f"解析JSON数据失败 (equip_id: {equip_id}): {e}")
                        continue
                    
                    if not parsed_desc:
                        continue
                    
                    # 更新各个字段
                    updates = {}
                    
                    # 更新宠物数据
                    pets = self.pet_parser.process_character_pets(parsed_desc, seller_nickname)
                    if pets:
                        updates['all_pets_json'] = json.dumps(pets, ensure_ascii=False)
                    
                    # 更新装备数据
                    if parsed_desc and 'AllEquip' in parsed_desc:
                        equip_info = self.equipment_parser.process_character_equipment(
                            parsed_desc, seller_nickname
                        )
                        if equip_info:
                            updates['all_equip_json'] = json.dumps(equip_info, ensure_ascii=False)
                    
                    # 更新神器数据
                    if parsed_desc and parsed_desc.get('shenqi'):
                        all_shenqi = self.shenqi_parser.process_character_shenqi(parsed_desc, seller_nickname)
                        if all_shenqi and all_shenqi.get('神器名称'):
                            updates['all_shenqi_json'] = json.dumps(all_shenqi, ensure_ascii=False)
                    
                    # 更新坐骑数据
                    if parsed_desc and parsed_desc.get('AllRider'):
                        all_rider = self.rider_parser.process_character_rider(
                            {'rider': parsed_desc.get('AllRider')}, seller_nickname
                        )
                        if all_rider and all_rider.get('坐骑列表'):
                            updates['all_rider_json'] = json.dumps(all_rider, ensure_ascii=False)
                    
                    # 更新锦衣数据
                    if parsed_desc and parsed_desc.get('ExAvt'):
                        ex_avt_data = {
                            'ExAvt': parsed_desc.get('ExAvt'),
                            'basic_info': {
                                'total_avatar': parsed_desc.get('total_avatar', 0),
                                'xianyu': parsed_desc.get('xianyu', 0),
                                'xianyu_score': parsed_desc.get('xianyu_score', 0),
                                'qicai_score': parsed_desc.get('qicai_score', 0)
                            },
                            'chat_effect': parsed_desc.get('chat_effect'),
                            'icon_effect': parsed_desc.get('icon_effect'),
                            'title_effect': parsed_desc.get('title_effect'),
                            'perform_effect': parsed_desc.get('perform_effect'),
                            'achieve_show': parsed_desc.get('achieve_show', []),
                            'avt_widget': parsed_desc.get('avt_widget', {})
                        }
                        all_ex_avt = self.ex_avt_parser.process_character_clothes(ex_avt_data, seller_nickname)
                        if all_ex_avt:
                            updates['ex_avt_json'] = json.dumps(all_ex_avt, ensure_ascii=False)
                    
                    # 执行更新
                    if updates:
                        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
                        values = list(updates.values())
                        values.append(equip_id)
                        
                        cursor.execute(
                            f"UPDATE characters SET {set_clause} WHERE equip_id = ?",
                            values
                        )
                        
                        # 单独更新 large_equip_desc_data 表中的 all_new_point 字段
                        if parsed_desc.get('TA_iAllNewPoint'):
                            cursor.execute(
                                "UPDATE large_equip_desc_data SET all_new_point = ? WHERE equip_id = ?",
                                [parsed_desc.get('TA_iAllNewPoint'), equip_id]
                            )
                            self.logger.info(f"更新角色 {equip_id} 的乾元丹数据: {parsed_desc.get('TA_iAllNewPoint')}")
                        
                        updated_count += 1
                        self.logger.info(f"更新角色 {equip_id} 的数据成功")
                
                except Exception as e:
                    self.logger.error(f"更新角色 {equip_id} 时出错: {e}")
                    continue
            
            conn.commit()
            self.logger.info(f"数据更新完成，共更新 {updated_count} 个角色")
            
        except Exception as e:
            self.logger.error(f"更新数据时出错: {e}")
        finally:
            conn.close()
    
    def parse_large_equip_desc(self, large_desc):
        """
        解析large_equip_desc字段
        
        Args:
            large_desc: 原始装备描述数据
        
        Returns:
            dict: 解析后的数据
        """
        if not large_desc or not isinstance(large_desc, str):
            return {}
        
        try:
            # 移除可能的编码标记
            clean_desc = large_desc.strip()
            if clean_desc.startswith('@') and clean_desc.endswith('@'):
                clean_desc = clean_desc[1:-1]
            
            # 使用lpc_to_js方法进行解析
            js_format = self.lpc_helper.lpc_to_js(clean_desc, return_dict=False)
            if js_format:
                # 然后用js_eval解析JavaScript格式字符串
                parsed_data = self.lpc_helper.js_eval(js_format)
                if parsed_data and isinstance(parsed_data, dict) and len(parsed_data) > 0:
                    return parsed_data
            
            self.logger.warning(f"LPC->JS解析失败，原始数据前200字符: {clean_desc[:200]}")
            return {}
            
        except Exception as e:
            self.logger.warning(f"解析large_equip_desc失败: {e}")
            return {}
    
    def get_house_real_owner_name(self, owner_status):
        """转换房屋真实拥有者状态为中文名称"""
        return self.common_parser.get_house_real_owner_name(owner_status)
    
    def add_column_to_characters(self, column_name, column_type):
        """
        为characters表添加新字段
        
        Args:
            column_name: 字段名称
            column_type: 字段类型 (如 'TEXT', 'INTEGER', 'REAL' 等)
            
        Returns:
            bool: 是否添加成功
        """
        return self.add_column_to_table('characters', column_name, column_type)
    
    def add_column_to_table(self, table_name, column_name, column_type):
        """
        为指定表添加新字段
        
        Args:
            table_name: 表名
            column_name: 字段名称
            column_type: 字段类型 (如 'TEXT', 'INTEGER', 'REAL' 等)
            
        Returns:
            bool: 是否添加成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                self.logger.error(f"表 {table_name} 不存在")
                return False
            
            # 检查字段是否已存在
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_columns = [column[1] for column in cursor.fetchall()]
            
            if column_name in existing_columns:
                self.logger.warning(f"字段 {column_name} 在表 {table_name} 中已存在")
                return False
            
            # 添加新字段
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            conn.commit()
            self.logger.info(f"成功添加字段 {column_name} ({column_type}) 到表 {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加字段 {column_name} 到表 {table_name} 失败: {e}")
            return False
        finally:
            conn.close()
    
    def add_column_to_large_equip_desc(self, column_name, column_type):
        """
        为large_equip_desc_data表添加新字段的便捷方法
        
        Args:
            column_name: 字段名称
            column_type: 字段类型 (如 'TEXT', 'INTEGER', 'REAL' 等)
            
        Returns:
            bool: 是否添加成功
        """
        return self.add_column_to_table('large_equip_desc_data', column_name, column_type)
    
    def drop_column_from_table(self, table_name, column_name):
        """
        删除表中的字段
        
        Args:
            table_name: 表名
            column_name: 要删除的字段名
            
        Returns:
            bool: 是否删除成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                self.logger.error(f"表 {table_name} 不存在")
                return False
            
            # 检查字段是否存在
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if column_name not in column_names:
                self.logger.warning(f"字段 {column_name} 在表 {table_name} 中不存在")
                return False
            
            # 获取SQLite版本
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            version_parts = [int(x) for x in version.split('.')]
            
            # SQLite 3.35.0+ 支持 ALTER TABLE DROP COLUMN
            supports_drop_column = (version_parts[0] > 3 or 
                                  (version_parts[0] == 3 and version_parts[1] > 35) or
                                  (version_parts[0] == 3 and version_parts[1] == 35 and version_parts[2] >= 0))
            
            if supports_drop_column:
                # 使用新语法直接删除字段
                self.logger.info(f"使用 ALTER TABLE DROP COLUMN 删除字段 {column_name}")
                cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
            else:
                # 使用传统方法：重建表
                self.logger.info(f"使用表重建方法删除字段 {column_name}")
                
                # 获取除了要删除字段外的所有字段信息
                remaining_columns = [col for col in columns if col[1] != column_name]
                
                if not remaining_columns:
                    self.logger.error(f"不能删除表 {table_name} 的最后一个字段")
                    return False
                
                # 构建新表的字段定义
                column_defs = []
                column_names_new = []
                for col in remaining_columns:
                    col_name = col[1]
                    col_type = col[2]
                    col_notnull = col[3]
                    col_default = col[4]
                    col_pk = col[5]
                    
                    col_def = f"{col_name} {col_type}"
                    if col_pk:
                        col_def += " PRIMARY KEY"
                    if col_notnull and not col_pk:
                        col_def += " NOT NULL"
                    if col_default is not None:
                        col_def += f" DEFAULT {col_default}"
                    
                    column_defs.append(col_def)
                    column_names_new.append(col_name)
                
                # 创建临时表
                temp_table = f"{table_name}_temp_{int(time.time())}"
                create_sql = f"CREATE TABLE {temp_table} ({', '.join(column_defs)})"
                cursor.execute(create_sql)
                
                # 复制数据到临时表
                select_columns = ', '.join(column_names_new)
                cursor.execute(f"INSERT INTO {temp_table} ({select_columns}) SELECT {select_columns} FROM {table_name}")
                
                # 删除原表
                cursor.execute(f"DROP TABLE {table_name}")
                
                # 重命名临时表
                cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")
            
            conn.commit()
            self.logger.info(f"成功从表 {table_name} 删除字段 {column_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"从表 {table_name} 删除字段 {column_name} 失败: {e}")
            if 'conn' in locals():
                conn.rollback()
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def drop_column_from_characters(self, column_name):
        """
        从characters表删除字段的便捷方法
        
        Args:
            column_name: 要删除的字段名
            
        Returns:
            bool: 是否删除成功
        """
        return self.drop_column_from_table('characters', column_name)
    
    def drop_column_from_large_equip_desc(self, column_name):
        """
        从large_equip_desc_data表删除字段的便捷方法
        
        Args:
            column_name: 要删除的字段名
            
        Returns:
            bool: 是否删除成功
        """
        return self.drop_column_from_table('large_equip_desc_data', column_name)

def main():
    """简单的测试函数"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 获取当前月份
    current_month = datetime.now().strftime('%Y%m')
    db_filename = f"cbg_data_{current_month}.db"
    db_path = os.path.join(project_root, 'data', db_filename)
    
    # 创建更新器
    updater = DataUpdater(db_path, logger)
    
    # 更新所有数据
    # updater.add_column_to_characters('all_new_point','INTEGER')
    updater.update_character_data()
    # updater.drop_column_from_table('characters','all_new_point')
    # updater.add_column_to_table('large_equip_desc_data','all_new_point','INTEGER')
if __name__ == "__main__":
    main() 