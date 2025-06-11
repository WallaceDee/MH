#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
json导出器模块
负责将CBG角色数据导出为JSON格式
"""

import os
import sqlite3
import json
from datetime import datetime
import logging


class CBGJSONExporter:
    """CBG数据JSON导出器"""
    
    def __init__(self, db_path, output_dir, logger=None):
        """
        初始化JSON导出器
        
        Args:
            db_path (str): 数据库文件路径
            output_dir (str): 输出目录
            logger: 日志对象，如果为None则创建新的logger
        """
        self.db_path = db_path
        self.output_dir = output_dir
        self.logger = logger or self._create_logger()
        
        # 使用动态配置加载器
        try:
            from ..parser.config_loader import get_config_loader
            self.config_loader = get_config_loader()
        except ImportError:
            try:
                from parser.config_loader import get_config_loader
                self.config_loader = get_config_loader()
            except ImportError:
                # 如果没有配置加载器，使用简单的默认配置
                self.config_loader = None
    
    def _create_logger(self):
        """创建默认日志对象"""
        logger = logging.getLogger('CBGJSONExporter')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def get_export_data_sql(self):
        """获取导出数据的SQL查询语句（与Excel导出器相同）"""
        return '''
            SELECT 
                -- 基本信息（优先使用large_equip_desc_data的数据）
                c.equip_id as _internal_equip_id,  -- 内部使用，不显示
                COALESCE(l.character_name, c.seller_nickname) as 角色名,
                c.area_name || '/' || c.server_name as 服务器,
                COALESCE(l.character_level, c.level) as 等级,
                c.school as 门派,
                c.price_desc as 价格,
                
                -- 修炼信息
                l.sum_exp || '亿' as 总经验,
                ROUND(l.up_exp / 100000000.0, 2) || '亿' as 获得经验,
                l.expt_ski1 || '/' || l.max_expt1 as 攻击修炼,
                l.expt_ski2 || '/' || l.max_expt2 as 防御修炼,
                l.expt_ski3 || '/' || l.max_expt3 as 法术修炼,
                l.expt_ski4 || '/' || l.max_expt4 as 抗法修炼,
                l.expt_ski5 as 猎术修炼,
                
                -- 召唤兽技能
                l.beast_ski1 as 攻击控制力,
                l.beast_ski2 as 防御控制力,
                l.beast_ski3 as 法术控制力,
                l.beast_ski4 as 抗法控制力,
                
                -- 飞升状态（使用更直观的显示）
                c.fly_status as 飞升状态,
                l.nine_fight_level as 生死劫等级,
                
                -- 售卖状态
                c.accept_bargain as 接受还价,
                c.status_desc as 角色售卖状态,
                c.onsale_expire_time_desc as 出售剩余时间,
                c.expire_time as 角色到期时间,
                -- 技能                       
                c.school_skills as 师门技能,
                c.life_skills as 生活技能,
                c.ju_qing_skills as 剧情技能,

                -- 装备信息
                c.all_equip_json as 装备信息,
                -- 神器信息
                c.all_shenqi_json as 神器信息,
                -- 宝宝信息
                c.all_pets_json as 宝宝信息,
                -- 坐骑信息
                c.all_rider_json as 坐骑信息,
                 -- 锦衣信息
                c.ex_avt_json as 锦衣信息,
                
                -- 属性信息
                l.hp_max as 气血,
                l.mp_max as 魔法,
                l.att_all as 命中,
                l.damage_all as 伤害,
                l.mag_dam_all as 法术伤害,
                l.def_all as 防御,
                l.dex_all as 速度,
                l.spe_all as 敏捷,
                l.mag_all as 魔力,
                l.mag_def_all as 法术防御,
                l.dod_all as 躲避,
                l.cor_all as 体质,
                l.str_all as 力量,
                l.res_all as 耐力,
                
            
                -- 点数和潜力
                l.skill_point as 剧情技能剩余技能点,
                l.all_new_point as 乾元丹,
                
                -- 金钱和道具
                l.cash as 现金,
                l.saving as 存款,
                l.learn_cash as 储备金,
                l.nuts_num as 潜能果数量,
                l.cg_total_amount as 彩果总数,
                l.cg_body_amount as 身上彩果,
                l.cg_box_amount as 仓库彩果,
                l.xianyu_amount as 仙玉数量,
                
                -- 善恶值
                l.badness as 善恶点,
                l.goodness_sav as 储备善恶点,
                
                -- 社交信息
                l.org_name as 帮派名称,
                l.org_offer as 帮贡,
                
                -- 成就和评分
                l.achievement_total as 成就总点,
                l.hero_score as 比武积分,
                l.datang_feat as 三界功绩,
                l.sword_score as 剑会积分,
                l.dup_score as 副本评分,
                l.shenqi_score as 神器评分,
                l.qicai_score as 奇才评分,
                l.xianyu_score as 仙玉积分,
                
                -- 房屋信息
                l.rent_level as 房屋等级,
                l.outdoor_level as 庭院等级,
                l.farm_level as 牧场等级,
                
                -- 其他信息
                l.pride as 人气值,
                l.version_code as 版本号,
                
                
                -- 时间信息
                c.create_time as 创建时间,
                c.update_time as 更新时间
                
            FROM characters c
            LEFT JOIN large_equip_desc_data l ON c.equip_id = l.equip_id
            ORDER BY c.price_desc DESC
        '''
    
    def prepare_export_data(self, generate_link_callback=None):
        """
        准备导出数据：从数据库获取合并后的数据
        
        Args:
            generate_link_callback: 生成链接的回调函数
            
        Returns:
            list: 合并后的数据列表（字典格式）
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使用Row factory获取字典形式的数据
            cursor = conn.cursor()
            
            sql_query = self.get_export_data_sql()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            # 转换为字典列表
            data_list = []
            for row in rows:
                data_dict = dict(row)
                data_list.append(data_dict)
            
            conn.close()
            
            self.logger.info(f"从数据库获取数据完成，行数: {len(data_list)}")
            return data_list
            
        except Exception as e:
            self.logger.error(f"准备导出数据失败: {e}")
            return []  # 返回空列表
    
    def format_export_data(self, data_list, generate_link_callback=None):
        """
        格式化导出数据
        
        Args:
            data_list: 原始数据列表
            generate_link_callback: 生成链接的回调函数
            
        Returns:
            list: 格式化后的导出数据
        """
        try:
            formatted_list = []
            
            for data_dict in data_list:
                # 创建新字典，移除内部使用的列
                formatted_dict = {}
                
                for key, value in data_dict.items():
                    # 跳过内部使用的字段
                    if key == '_internal_equip_id':
                        continue
                    
                    # 处理JSON字段
                    if key in ['装备信息', '神器信息', '宝宝信息', '坐骑信息', '锦衣信息']:
                        if value and value.strip():
                            try:
                                formatted_dict[key] = json.loads(value)
                            except json.JSONDecodeError:
                                formatted_dict[key] = value
                        else:
                            formatted_dict[key] = None
                    else:
                        formatted_dict[key] = value
                
                # 如果有生成链接的回调，添加CBG链接
                if generate_link_callback and data_dict.get('_internal_equip_id'):
                    cbg_link = generate_link_callback(data_dict['_internal_equip_id'])
                    if cbg_link:
                        formatted_dict['CBG链接'] = cbg_link
                
                formatted_list.append(formatted_dict)
            
            self.logger.info(f"数据格式化完成，输出行数: {len(formatted_list)}")
            return formatted_list
            
        except Exception as e:
            self.logger.error(f"格式化导出数据失败: {e}")
            raise
    
    def save_to_json(self, data_list, json_path, pretty=True):
        """
        保存数据到JSON文件
        
        Args:
            data_list: 要导出的数据列表
            json_path: JSON文件路径
            pretty: 是否格式化输出
        """
        try:
            # 创建输出目录（如果不存在）
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            
            # 直接导出角色数据数组，不包装额外结构
            with open(json_path, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(data_list, f, ensure_ascii=False, indent=2)
                else:
                    json.dump(data_list, f, ensure_ascii=False)
            
            self.logger.info(f"JSON文件保存完成: {json_path}")
            
        except Exception as e:
            self.logger.error(f"保存JSON文件失败: {e}")
            raise
    
    def log_export_results(self, filepath, data_list):
        """记录导出结果"""
        self.logger.info(f"数据已导出到: {filepath}")
        self.logger.info(f"角色数据: {len(data_list)} 条")
    
    def export_to_json(self, filename=None, generate_link_callback=None, pretty=True):
        """
        导出数据到JSON文件
        
        Args:
            filename: 文件名，如果为None则自动生成
            generate_link_callback: 生成CBG链接的回调函数
            pretty: 是否格式化输出JSON
            
        Returns:
            str: 生成的JSON文件路径，失败时返回None
        """
        try:
            # 1. 准备数据：合并角色基础信息和详细信息  
            data_list = self.prepare_export_data(generate_link_callback)
            
            if not data_list:
                self.logger.warning("没有数据可导出")
                return None
                
            # 2. 格式化数据
            formatted_data = self.format_export_data(data_list, generate_link_callback)
            
            # 3. 生成文件名
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'cbg_characters_{timestamp}.json'
            
            if not filename.endswith('.json'):
                filename += '.json'
            
            # 4. 完整文件路径
            json_path = os.path.join(self.output_dir, filename)
            
            # 5. 导出到JSON
            self.save_to_json(formatted_data, json_path, pretty)
            
            # 6. 记录导出结果
            self.log_export_results(json_path, formatted_data)
            
            self.logger.info(f"JSON导出成功: {json_path}")
            return json_path
            
        except Exception as e:
            self.logger.error(f"JSON导出失败: {e}")
            return None
    
    def export_single_character_json(self, character_data, generate_link_callback=None, pretty=True):
        """
        为单个角色导出JSON数据到role_json文件夹
        
        Args:
            character_data: 单个角色的数据字典
            generate_link_callback: 生成CBG链接的回调函数
            pretty: 是否格式化输出JSON
            
        Returns:
            str: 生成的JSON文件路径，失败时返回None
        """
        try:
            # 1. 创建role_json目录
            role_json_dir = os.path.join(self.output_dir, 'role_json')
            os.makedirs(role_json_dir, exist_ok=True)
            
            # 2. 格式化单个角色数据
            formatted_data = self.format_single_character_data(character_data, generate_link_callback)
            
            # 3. 生成文件名（基于角色名和equip_id）
            character_name = formatted_data.get('seller_nickname', '未知角色')
            equip_id = character_data.get('_internal_equip_id') or character_data.get('equip_id', 'unknown')
            server_info = formatted_data.get('服务器', '').replace('/', '_')
            
            # 清理文件名中的非法字符
            safe_name = self._clean_filename(f"{character_name}_{server_info}_{equip_id}")
            filename = f"{safe_name}.json"
            
            # 4. 完整文件路径
            json_path = os.path.join(role_json_dir, filename)
            
            # 5. 创建单个角色的导出数据结构
            export_data = {
                'export_info': {
                    'export_time': datetime.now().isoformat(),
                    'export_format': 'single_character_json',
                    'version': '1.0'
                },
                'character': formatted_data
            }
            
            # 6. 写入JSON文件
            with open(json_path, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                else:
                    json.dump(export_data, f, ensure_ascii=False)
            
            self.logger.debug(f"单个角色JSON保存成功: {json_path}")
            return json_path
            
        except Exception as e:
            self.logger.error(f"保存单个角色JSON失败: {e}")
            return None
    
    def format_single_character_data(self, character_data, generate_link_callback=None):
        """
        格式化单个角色的数据
        
        Args:
            character_data: 单个角色的原始数据字典
            generate_link_callback: 生成链接的回调函数
            
        Returns:
            dict: 格式化后的角色数据
        """
        try:
            # 创建新字典，移除内部使用的列
            formatted_dict = {}
            
            for key, value in character_data.items():
                # 跳过内部使用的字段
                if key == '_internal_equip_id':
                    continue
                
                # 处理JSON字段
                if key in ['装备信息', '神器信息', '宝宝信息', '坐骑信息', '锦衣信息']:
                    if value and value.strip():
                        try:
                            formatted_dict[key] = json.loads(value)
                        except json.JSONDecodeError:
                            formatted_dict[key] = value
                    else:
                        formatted_dict[key] = None
                else:
                    formatted_dict[key] = value
            
            # 如果有生成链接的回调，添加CBG链接
            if generate_link_callback and character_data.get('_internal_equip_id'):
                cbg_link = generate_link_callback(character_data['_internal_equip_id'])
                if cbg_link:
                    formatted_dict['CBG链接'] = cbg_link
            
            return formatted_dict
            
        except Exception as e:
            self.logger.error(f"格式化单个角色数据失败: {e}")
            raise
    
    def _clean_filename(self, filename):
        """
        清理文件名中的非法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的安全文件名
        """
        # 移除或替换非法字符
        import re
        # 替换非法字符为下划线
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 移除多余的空格和点
        safe_filename = re.sub(r'\s+', '_', safe_filename.strip())
        safe_filename = safe_filename.strip('.')
        
        # 限制文件名长度
        if len(safe_filename) > 200:
            safe_filename = safe_filename[:200]
        
        return safe_filename
    
    # 工具方法（与Excel导出器保持一致）
    def get_rent_level_name(self, level):
        """转换房屋等级数字为中文名称"""
        if level is None:
            return "未知"
        fangwu_mapping = self.config_loader.get_fangwu_level_mapping()
        return fangwu_mapping.get(str(level), f"未知等级({level})")
    
    def get_outdoor_level_name(self, level):
        """转换庭院等级数字为中文名称"""
        if level is None:
            return "未知"
        outdoor_mapping = self.config_loader.get_outdoor_level_mapping()
        return outdoor_mapping.get(str(level), f"未知等级({level})")
    
    def get_farm_level_name(self, level):
        """转换牧场等级数字为中文名称"""
        if level is None:
            return "未知"
        farm_mapping = self.config_loader.get_farm_level_mapping()
        return farm_mapping.get(str(level), f"未知等级({level})")
    
    def get_house_real_owner_name(self, owner_status):
        """转换房屋真实拥有者状态为中文名称"""
        if owner_status is None:
            return "未知"
        if owner_status == 1 or owner_status == "1" or owner_status is True:
            return "是"
        elif owner_status == 0 or owner_status == "0" or owner_status is False:
            return "否"
        else:
            return "未知"


# 便利函数
def create_json_exporter(db_path, output_dir, logger=None):
    """创建JSON导出器实例的便利函数"""
    return CBGJSONExporter(db_path, output_dir, logger)


def export_cbg_data_to_json(db_path, output_dir, filename=None, 
                           generate_link_callback=None, logger=None, pretty=True):
    """
    直接导出CBG数据到JSON的便利函数
    
    Args:
        db_path: 数据库路径
        output_dir: 输出目录
        filename: 文件名
        generate_link_callback: 生成链接的回调函数
        logger: 日志对象
        pretty: 是否格式化输出JSON
        
    Returns:
        str: 导出文件路径，失败时返回None
    """
    exporter = CBGJSONExporter(db_path, output_dir, logger)
    return exporter.export_to_json(filename, generate_link_callback, pretty)


def export_single_character_to_json(character_data, output_dir, 
                                   generate_link_callback=None, logger=None, pretty=True):
    """
    直接导出单个角色数据到JSON的便利函数
    
    Args:
        character_data: 单个角色的数据字典
        output_dir: 输出目录
        generate_link_callback: 生成链接的回调函数
        logger: 日志对象
        pretty: 是否格式化输出JSON
        
    Returns:
        str: 导出文件路径，失败时返回None
    """
    # 创建一个临时的导出器实例（不需要数据库路径）
    exporter = CBGJSONExporter(None, output_dir, logger)
    return exporter.export_single_character_json(character_data, generate_link_callback, pretty)