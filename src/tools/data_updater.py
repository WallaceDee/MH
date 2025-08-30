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
from src.utils.project_path import get_project_root
project_root = get_project_root()
sys.path.append(project_root)

from src.parser.pet_parser import PetParser
from src.parser.equipment_parser import EquipmentParser
from src.parser.shenqi_parser import ShenqiParser
from src.parser.rider_parser import RiderParser
from src.parser.ex_avt_parser import ExAvtParser
from src.utils.lpc_helper import LPCHelper
from src.parser.common_parser import CommonParser
from src.parser.fabao_parser import FabaoParser

# 导入特征提取器
from src.evaluator.feature_extractor.lingshi_feature_extractor import LingshiFeatureExtractor

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
        self.common_parser = CommonParser(self.logger)
        self.fabao_parser = FabaoParser(self.logger)
        
        # 初始化特征提取器
        self.lingshi_feature_extractor = LingshiFeatureExtractor()

    def update_role_data(self, role_id=None):
        """
        更新角色数据
        
        Args:
            role_id: 要更新的角色ID，如果为None则更新所有角色
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取要更新的角色
            if role_id:
                cursor.execute("""
                    SELECT c.equip_id, c.seller_nickname, d.raw_data_json
                    FROM roles c
                    JOIN large_equip_desc_data d ON c.equip_id = d.equip_id
                    WHERE c.equip_id = ?
                """, (role_id,))
            else:
                cursor.execute("""
                    SELECT c.equip_id, c.seller_nickname, d.raw_data_json
                    FROM roles c
                    JOIN large_equip_desc_data d ON c.equip_id = d.equip_id
                """)
            
            roles = cursor.fetchall()
            updated_count = 0
            
            for char in roles:
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
                    
                    # # 更新育兽术
                    # yushoushu_skill = self.common_parser.parse_yushoushu_skill(parsed_desc.get('all_skills', {}))
                    # self.logger.info(f"更新角色 {equip_id} 的育兽术数据成功: {yushoushu_skill}")
                    # updates['yushoushu_skill'] = yushoushu_skill
                    
                    # 更新法宝数据
                    fabao = self.fabao_parser.process_role_fabao(parsed_desc, seller_nickname)
                    if fabao:
                        updates['all_fabao_json'] = json.dumps(fabao, ensure_ascii=False)
                    
                    # # 更新召唤兽数据
                    # pets = self.pet_parser.process_role_pets(parsed_desc, seller_nickname)
                    # if pets:
                    #     updates['all_pets_json'] = json.dumps(pets, ensure_ascii=False)
                    
                    # # 更新装备数据
                    # if parsed_desc and 'AllEquip' in parsed_desc:
                    #     equip_info = self.equipment_parser.process_role_equipment(
                    #         parsed_desc, seller_nickname
                    #     )
                    #     if equip_info:
                    #         updates['all_equip_json'] = json.dumps(equip_info, ensure_ascii=False)
                    
                    # # 更新神器数据
                    # if parsed_desc and parsed_desc.get('shenqi'):
                    #     all_shenqi = self.shenqi_parser.process_role_shenqi(parsed_desc, seller_nickname)
                    #     if all_shenqi and all_shenqi.get('神器名称'):
                    #         updates['all_shenqi_json'] = json.dumps(all_shenqi, ensure_ascii=False)
                    
                    # # 更新坐骑数据
                    # if parsed_desc and parsed_desc.get('AllRider'):
                    #     all_rider = self.rider_parser.process_role_rider(
                    #         {'rider': parsed_desc.get('AllRider')}, seller_nickname
                    #     )
                    #     if all_rider and all_rider.get('坐骑列表'):
                    #         updates['all_rider_json'] = json.dumps(all_rider, ensure_ascii=False)
                    
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
                        all_ex_avt = self.ex_avt_parser.process_role_clothes(ex_avt_data, seller_nickname)
                        if all_ex_avt:
                            updates['ex_avt_json'] = json.dumps(all_ex_avt, ensure_ascii=False)
                    
                    # 执行更新
                    if updates:
                        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
                        values = list(updates.values())
                        values.append(equip_id)
                        
                        cursor.execute(
                            f"UPDATE roles SET {set_clause} WHERE equip_id = ?",
                            values
                        )
                        
                        # # 单独更新 large_equip_desc_data 表中的 all_new_point 字段
                        # if parsed_desc.get('TA_iAllNewPoint'):
                        #     cursor.execute(
                        #         "UPDATE large_equip_desc_data SET all_new_point = ? WHERE equip_id = ?",
                        #         [parsed_desc.get('TA_iAllNewPoint'), equip_id]
                        #     )
                        #     self.logger.info(f"更新角色 {equip_id} 的乾元丹数据: {parsed_desc.get('TA_iAllNewPoint')}")


                        # 单独更新 large_equip_desc_data 表中的 sum_amount 字段
                        if parsed_desc.get('pet'):
                            cursor.execute(
                                "UPDATE large_equip_desc_data SET pet = ? WHERE equip_id = ?",
                                [json.dumps(parsed_desc.get('pet'), ensure_ascii=False), equip_id]
                            )
                            self.logger.info(f"更新角色 {equip_id} 的 pet 数据: {parsed_desc.get('pet')}")
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
    
    def add_column_to_roles(self, column_name, column_type):
        """
        为roles表添加新字段
        
        Args:
            column_name: 字段名称
            column_type: 字段类型 (如 'TEXT', 'INTEGER', 'REAL' 等)
            
        Returns:
            bool: 是否添加成功
        """
        return self.add_column_to_table('roles', column_name, column_type)
    
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
    
    def drop_column_from_roles(self, column_name):
        """
        从roles表删除字段的便捷方法
        
        Args:
            column_name: 要删除的字段名
            
        Returns:
            bool: 是否删除成功
        """
        return self.drop_column_from_table('roles', column_name)
    
    def drop_column_from_large_equip_desc(self, column_name):
        """
        从large_equip_desc_data表删除字段的便捷方法
        
        Args:
            column_name: 要删除的字段名
            
        Returns:
            bool: 是否删除成功
        """
        return self.drop_column_from_table('large_equip_desc_data', column_name)
    
    def update_equipment_features(self, equip_db_path=None):
        """
        更新装备数据库中的特征数据
        
        使用特征提取器重新提取灵饰装备的附加属性特征，并覆盖agg_added_attrs字段
        
        Args:
            equip_db_path: 装备数据库路径，如果为None则使用默认路径
            
        Returns:
            int: 更新的装备数量
        """
        try:
            # 如果没有指定数据库路径，使用默认路径
            if equip_db_path is None:
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                current_month = datetime.now().strftime('%Y%m')
                equip_db_path = os.path.join(project_root, 'data', current_month, f'cbg_equip_{current_month}.db')
            
            self.logger.info(f"开始更新装备数据库: {equip_db_path}")
            
            # 连接装备数据库
            conn = sqlite3.connect(equip_db_path)
            cursor = conn.cursor()
            
            # 获取所有灵饰装备数据 (kindid: 61, 62, 63, 64)
            cursor.execute("""
                SELECT eid, kindid, large_equip_desc, agg_added_attrs
                FROM equipments 
                WHERE kindid IN (61, 62, 63, 64)
                AND large_equip_desc IS NOT NULL 
                AND large_equip_desc != ''
            """)
            
            equipments = cursor.fetchall()
            self.logger.info(f"找到 {len(equipments)} 个灵饰装备需要更新特征")
            
            updated_count = 0
            error_count = 0
            
            for equip in equipments:
                try:
                    eid = equip[0]
                    kindid = equip[1]
                    large_equip_desc = equip[2]
                    old_agg_added_attrs = equip[3]
                    
                    # 构建装备数据字典
                    equip_data = {
                        'kindid': kindid,
                        'large_equip_desc': large_equip_desc
                    }
                    
                    # 使用特征提取器提取附加属性
                    added_attrs_features = self.lingshi_feature_extractor._extract_added_attrs_features(equip_data)
                    extracted_attrs = added_attrs_features.get('attrs', [])
                    
                    # 转换为JSON字符串
                    new_agg_added_attrs = json.dumps(extracted_attrs, ensure_ascii=False) if extracted_attrs else ''
                    
                    # 检查是否有变化
                    if new_agg_added_attrs != old_agg_added_attrs:
                        # 更新数据库
                        cursor.execute(
                            "UPDATE equipments SET agg_added_attrs = ? WHERE eid = ?",
                            (new_agg_added_attrs, eid)
                        )
                        
                        updated_count += 1
                        
                        # 记录详细信息
                        if extracted_attrs:
                            attr_info = []
                            for attr in extracted_attrs:
                                attr_info.append(f"{attr['attr_type']}+{attr['attr_value']}")
                            self.logger.info(f"更新装备 {eid} (kindid:{kindid}): {', '.join(attr_info)}")
                        else:
                            self.logger.info(f"更新装备 {eid} (kindid:{kindid}): 清空附加属性")
                    else:
                        self.logger.debug(f"装备 {eid} (kindid:{kindid}): 特征无变化，跳过")
                        
                except Exception as e:
                    error_count += 1
                    self.logger.error(f"更新装备 {eid} 特征时出错: {e}")
                    continue
            
            # 提交更改
            conn.commit()
            
            self.logger.info(f"装备特征更新完成:")
            self.logger.info(f"  - 总装备数: {len(equipments)}")
            self.logger.info(f"  - 成功更新: {updated_count}")
            self.logger.info(f"  - 错误数量: {error_count}")
            
            return updated_count
            
        except Exception as e:
            self.logger.error(f"更新装备特征时出错: {e}")
            if 'conn' in locals():
                conn.rollback()
            return 0
        finally:
            if 'conn' in locals():
                conn.close()
    
    def update_equipment_features_batch(self, batch_size=100, equip_db_path=None):
        """
        批量更新装备数据库中的特征数据
        
        分批处理大量数据，避免内存占用过高
        
        Args:
            batch_size: 每批处理的装备数量
            equip_db_path: 装备数据库路径，如果为None则使用默认路径
            
        Returns:
            int: 更新的装备数量
        """
        try:
            # 如果没有指定数据库路径，使用默认路径
            if equip_db_path is None:
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                current_month = datetime.now().strftime('%Y%m')
                equip_db_path = os.path.join(project_root, 'data', current_month, f'cbg_equip_{current_month}.db')
            
            self.logger.info(f"开始批量更新装备数据库: {equip_db_path}")
            
            # 连接装备数据库
            conn = sqlite3.connect(equip_db_path)
            cursor = conn.cursor()
            
            # 获取总数量
            cursor.execute("""
                SELECT COUNT(*) 
                FROM equipments 
                WHERE kindid IN (61, 62, 63, 64)
                AND large_equip_desc IS NOT NULL 
                AND large_equip_desc != ''
            """)
            total_count = cursor.fetchone()[0]
            
            self.logger.info(f"总共需要处理 {total_count} 个灵饰装备")
            
            updated_count = 0
            error_count = 0
            processed_count = 0
            
            # 分批处理
            offset = 0
            while offset < total_count:
                # 获取当前批次的装备
                cursor.execute("""
                    SELECT eid, kindid, large_equip_desc, agg_added_attrs
                    FROM equipments 
                    WHERE kindid IN (61, 62, 63, 64)
                    AND large_equip_desc IS NOT NULL 
                    AND large_equip_desc != ''
                    ORDER BY eid
                    LIMIT ? OFFSET ?
                """, (batch_size, offset))
                
                equipments = cursor.fetchall()
                
                if not equipments:
                    break
                
                self.logger.info(f"处理第 {offset//batch_size + 1} 批，共 {len(equipments)} 个装备")
                
                # 处理当前批次
                for equip in equipments:
                    try:
                        eid = equip[0]
                        kindid = equip[1]
                        large_equip_desc = equip[2]
                        old_agg_added_attrs = equip[3]
                        
                        # 构建装备数据字典
                        equip_data = {
                            'kindid': kindid,
                            'large_equip_desc': large_equip_desc
                        }
                        
                        # 使用特征提取器提取附加属性
                        added_attrs_features = self.lingshi_feature_extractor._extract_added_attrs_features(equip_data)
                        extracted_attrs = added_attrs_features.get('attrs', [])
                        
                        # 转换为JSON字符串
                        new_agg_added_attrs = json.dumps(extracted_attrs, ensure_ascii=False) if extracted_attrs else ''
                        
                        # 检查是否有变化
                        if new_agg_added_attrs != old_agg_added_attrs:
                            # 更新数据库
                            cursor.execute(
                                "UPDATE equipments SET agg_added_attrs = ? WHERE eid = ?",
                                (new_agg_added_attrs, eid)
                            )
                            updated_count += 1
                        
                        processed_count += 1
                        
                        # 每处理100个装备显示一次进度
                        if processed_count % 100 == 0:
                            self.logger.info(f"已处理 {processed_count}/{total_count} 个装备，更新 {updated_count} 个")
                            
                    except Exception as e:
                        error_count += 1
                        self.logger.error(f"更新装备 {eid} 特征时出错: {e}")
                        continue
                
                # 提交当前批次的更改
                conn.commit()
                
                # 移动到下一批
                offset += batch_size
                
                # 短暂休息，避免过度占用资源
                time.sleep(0.1)
            
            self.logger.info(f"批量装备特征更新完成:")
            self.logger.info(f"  - 总装备数: {total_count}")
            self.logger.info(f"  - 已处理: {processed_count}")
            self.logger.info(f"  - 成功更新: {updated_count}")
            self.logger.info(f"  - 错误数量: {error_count}")
            
            return updated_count
            
        except Exception as e:
            self.logger.error(f"批量更新装备特征时出错: {e}")
            if 'conn' in locals():
                conn.rollback()
            return 0
        finally:
            if 'conn' in locals():
                conn.close()

def main():
    """简单的测试函数"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 获取当前月份
    current_month = datetime.now().strftime('%Y%m')
    
    # 角色数据库路径
    char_db_filename = f"empty_roles_{current_month}.db"
    char_db_path = os.path.join(project_root, 'data', char_db_filename)
    
    # 装备数据库路径
    equip_db_filename = f"cbg_equip_{current_month}.db"
    equip_db_path = os.path.join(project_root, 'data', equip_db_filename)
    
    # 创建更新器
    updater = DataUpdater(char_db_path, logger)
    
    # 测试装备特征更新功能
    print("🔧 开始测试装备特征更新功能...")
    
    # 检查装备数据库是否存在
    if os.path.exists(equip_db_path):
        print(f"📁 找到装备数据库: {equip_db_path}")
        
        # 使用批量更新方法（推荐用于大量数据）
        print("🚀 开始批量更新装备特征...")
        updated_count = updater.update_equipment_features_batch(batch_size=50, equip_db_path=equip_db_path)
        print(f"✅ 批量更新完成，共更新 {updated_count} 个装备")
        
        # 或者使用普通更新方法（适用于小量数据）
        # print("🚀 开始更新装备特征...")
        # updated_count = updater.update_equipment_features(equip_db_path=equip_db_path)
        # print(f"✅ 更新完成，共更新 {updated_count} 个装备")
        
    else:
        print(f"❌ 装备数据库不存在: {equip_db_path}")
        print("请先运行装备爬虫获取数据")
    
    # 原有的角色数据更新功能（已注释）
    # updater.add_column_to_roles('sum_amount','INTEGER')
    # updater.add_column_to_table('large_equip_desc_data','pet','TEXT')
    # updater.update_role_data()
    # updater.drop_column_from_table('roles','sum_amount')

if __name__ == "__main__":
    main() 