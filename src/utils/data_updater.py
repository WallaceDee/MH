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
    updater.update_character_data()

if __name__ == "__main__":
    main() 