#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宠物解析器模块
负责处理梦幻西游CBG中所有与宠物相关的数据解析
"""

import os
import re
import json
import sqlite3
import logging
from datetime import datetime

# 导入统一配置加载器
try:
    from .config_loader import get_config_loader
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    try:
        from config_loader import get_config_loader
    except ImportError:
        # 如果都失败，创建一个简单的替代函数
        def get_config_loader():
            return None

try:
    from ..utils.lpc_helper import LPCHelper
except ImportError:
    # 当作为独立模块运行时，使用绝对导入
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.lpc_helper import LPCHelper


class PetParser:
    """宠物数据解析器"""
    
    def __init__(self, logger=None):
        """初始化宠物解析器"""
        self.logger = logger or logging.getLogger(__name__)
        self.config_loader = get_config_loader()
        if not self.config_loader:
            self.logger.warning("配置加载器不可用，将使用原有的配置加载方式")
        
        # 配置缓存
        self._skill_mapping_cache = None
        self._neidan_config_cache = None
        self._pet_type_config = None
        self._pet_shipin_config = None
        
        # 初始化LPC助手
        self.lpc_helper = LPCHelper(self.logger)
    
    def process_character_pets(self, parsed_data, character_name=None):
        """
        处理角色宠物信息的主要入口方法
        包含解析、输出显示等完整逻辑
        
        Args:
            parsed_data: 解析后的角色数据
            character_name: 角色名称，用于显示
            
        Returns:
            list: 处理后的宠物信息列表，可以直接保存到数据库
        """
        pets_list = []
        
        if not parsed_data or 'AllSummon' not in parsed_data:
            return pets_list
        
        summon_data = parsed_data['AllSummon']
        self.logger.debug(f"检查AllSummon字段，类型: {type(summon_data)}")
        
        # 现在AllSummon应该已经是解析好的数据结构，不再是LPC字符串
        if isinstance(summon_data, list):
            # 如果是列表，直接使用
            pets_data = summon_data
        elif isinstance(summon_data, dict):
            # 如果是字典，可能需要进一步处理
            pets_data = [summon_data]  # 单个宠物包装为列表
        else:
            # 其他类型或空数据
            self.logger.debug(f"AllSummon数据类型不支持: {type(summon_data)}")
            return pets_list
        
        # 过滤有效的宠物数据
        valid_pets = []
        for pet in pets_data:
            if isinstance(pet, dict) and len(pet) > 5:  # 确保是有效的宠物数据
                valid_pets.append(pet)
        
        if not valid_pets:
            return pets_list
        
        try:
            if valid_pets and len(valid_pets) > 0:
                for i, pet_data in enumerate(valid_pets):
                    pet_info = self.extract_pet_info(pet_data, i+1)
                    if pet_info:
                        pets_list.append(pet_info)
                        
                self.logger.debug(f"成功解析到 {len(valid_pets)} 只宝宝")
            else:
                self.logger.debug("AllSummon解析结果为空")
                
        except Exception as pe:
            self.logger.error(f"宠物解析异常: {pe}")
        
        if len(pets_list) == 0:
            self.logger.debug("该角色没有宝宝")
        else:
            self.logger.debug(f"该角色共有 {len(pets_list)} 只宝宝")
        
        return pets_list

    def extract_pet_info(self, pet_data, pet_index):
        """从宠物数据中提取信息，参考官方模板字段映射"""
        if not isinstance(pet_data, dict):
            return None
            
        try:
            # 参考官方模板pet_detail_templ的字段映射，使用中文字段名
            pet_info = {
                "类型": self.get_pet_type_name(pet_data.get('iType', '')),   # 解析类型ID为中文名称
                # 详细信息
                "详细信息": {
                    "宠物序号": pet_index,
                    "是否宝宝": "是" if pet_data.get('iBaobao', 0) == 1 else "否",
                    "宠物名称": "",  # 宠物名称（如果有的话）
                    "等级": pet_data.get('iGrade', 0),  # pet_grade
                    "气血": pet_data.get('iHp_max', pet_data.get('HP_MAX', 0)),      # blood_max
                    "魔法": pet_data.get('iMp_max', pet_data.get('MP_MAX', 0)),      # magic_max
                    "攻击": pet_data.get('iAtt_all', pet_data.get('ATK_MAX', 0)),    # attack
                    "防御": pet_data.get('iDef_All', pet_data.get('DEF_MAX', 0)),    # defence
                    "速度": pet_data.get('iDex_All', 0),    # speed
                    # 新版灵力系统
                    "法伤": pet_data.get('iMagDam', 0),           # 法伤
                    "法防": pet_data.get('iMagDef', 0),           # 法防
                    
                    "成长": pet_data.get('grow', pet_data.get('growthMax', 0))/1000,      # cheng_zhang
                    "寿命": pet_data.get('life', 0),                                 # lifetime
                },
                
                # 五项属性加点
                "属性加点": {
                    "体质": self.get_pet_attribute_point(pet_data, 'iCor_all', 'iCor'),
                    "法力": self.get_pet_attribute_point(pet_data, 'iMag_all', 'iMag'),
                    "力量": self.get_pet_attribute_point(pet_data, 'iStr_all', 'iStr'),
                    "耐力": self.get_pet_attribute_point(pet_data, 'iRes_all', 'iRes'),
                    "敏捷": self.get_pet_attribute_point(pet_data, 'iSpe_all', 'iSpe'),
                    "潜能": pet_data.get('iPoint', 0),     # 潜能点
                },
                
                # 资质系统 - 根据pet.js官方实现逻辑
                "资质": {
                    "攻击资质": self.get_pet_aptitude(pet_data, 'attack', 0),
                    "防御资质": self.get_pet_aptitude(pet_data, 'defence', 1), 
                    "速度资质": self.get_pet_aptitude(pet_data, 'speed', 2),
                    "躲闪资质": self.get_pet_aptitude(pet_data, 'avoid', 3),
                    "体力资质": self.get_pet_aptitude(pet_data, 'physical', 4),
                    "法力资质": self.get_pet_aptitude(pet_data, 'magic', 5),
                },
                
                # 道具使用情况
                "道具使用": {
                    "已用元宵": pet_data.get('yuanxiao', 0),          # used_yuanxiao
                    "已用千金露": pet_data.get('qianjinlu', 0),        # used_qianjinlu
                    "已用炼兽珍经": pet_data.get('lianshou', 0),        # used_lianshou
                    "幻色丹使用": pet_data.get('summon_color', 0),     # summon_color使用情况
                },
                
                # 技能相关
                "技能": [],   # 技能列表，需要解析all_skills
                "赐福技能": [],   # 赐福技能列表
                
                # 装备相关
                "装备": [],      # 装备列表
                "饰品": [],      # 饰品列表
                "内丹": [],      # 内丹列表
                
                # 特性相关
                "特性": "已关闭" if pet_data.get('core_close', '') == 1 else "已开启",     # 特性名称
                "进阶信息": pet_data.get('jinjie', {}),     # 进阶信息
                
                # 梦影相关  
                "梦影列表": pet_data.get('avt_list', []),         # 梦影列表
                "当前穿戴梦影": {},    # 当前穿戴梦影
                
                # 五行系统 - 根据parse_role.js逻辑
                "五行": self.get_pet_wuxing(pet_data.get('iAtt_F', 0)),  # 五行属性
            }
            
            # 解析技能信息
            all_skills = pet_data.get('all_skills', '')
            if all_skills:
                if isinstance(all_skills, dict):
                    # 如果all_skills是字典格式
                    skills_list = []
                    for skill_id, skill_level in all_skills.items():
                        skill_name = self.get_skill_name(skill_id)
                        skills_list.append(f"{skill_name}")
                    pet_info["技能"] = skills_list
                elif isinstance(all_skills, str):
                    # 如果all_skills是字符串格式
                    pet_info["技能"] = [all_skills]
                else:
                    pet_info["技能"] = [str(all_skills)]
                    
            # 解析进阶技能（EvolSkill）
            evol_skill = pet_data.get('EvolSkill', {})
            if evol_skill:
                # 如果EvolSkill是字符串且包含|分隔符，按|切割并查找中文名称
                if isinstance(evol_skill, str) and '|' in evol_skill:
                    skill_ids = evol_skill.split('|')
                    evol_skill_names = []
                    for skill_id in skill_ids:
                        if skill_id.strip():  # 忽略空字符串
                            skill_name = self.get_skill_name(skill_id.strip())
                            evol_skill_names.append(skill_name)
                    pet_info["赐福技能"] = evol_skill_names
                elif isinstance(evol_skill, str):
                    # 单个技能ID
                    skill_name = self.get_skill_name(evol_skill)
                    pet_info["赐福技能"] = [skill_name]
                else:
                    # 其他格式直接赋值
                    pet_info["赐福技能"] = evol_skill
            
            # 解析装备信息
            equip_list = []
            for i in range(1, 5):  # summon_equip1-4
                equip_key = f'summon_equip{i}'
                equip_desc_key = f'summon_equip{i}_desc'
                equip_type_key = f'summon_equip{i}_type'
                
                if equip_key in pet_data or equip_desc_key in pet_data:
                    equip_info = {
                        "装备位置": i,
                        "装备数据": pet_data.get(equip_key, ''),
                        "装备描述": pet_data.get(equip_desc_key, ''),
                        "装备类型": pet_data.get(equip_type_key, '')
                    }
                    equip_list.append(equip_info)
            pet_info["装备"] = equip_list
                     
            # 解析饰品信息
            shipin_list = []
            shipin_type = pet_data.get('summon_equip4_type', '')
            shipin_desc = pet_data.get('summon_equip4_desc', '')
            
            if shipin_type or shipin_desc:
                shipin_info = {
                    "饰品ID": shipin_type,
                    "饰品名称": self.get_pet_shipin_name(shipin_type),
                    "饰品描述": shipin_desc
                }
                shipin_list.append(shipin_info)
            
            pet_info["饰品"] = shipin_list
                     
            # 解析内丹信息
            neidan_list = self.parse_pet_neidan(pet_data)
            pet_info["内丹"] = neidan_list
            
            return pet_info
            
        except Exception as e:
            self.logger.error(f"提取宠物信息失败: {e}")
            return None

    def parse_allsummon_data(self, allsummon_data):
        """
        处理AllSummon数据，现在应该直接是解析好的数据结构
        
        Args:
            allsummon_data: 已解析的AllSummon数据（列表或字典）
            
        Returns:
            list: 宠物数据列表
        """
        try:
            # 现在AllSummon应该已经是解析好的数据结构
            if isinstance(allsummon_data, list):
                # 如果是列表，直接返回
                self.logger.debug(f"AllSummon是列表格式，包含{len(allsummon_data)}只宠物")
                return allsummon_data
            elif isinstance(allsummon_data, dict):
                # 如果是字典，可能是单个宠物，包装为列表
                self.logger.debug("AllSummon是字典格式，包装为列表")
                return [allsummon_data]
            else:
                # 数据为空或类型不支持
                self.logger.debug("AllSummon数据为空或类型不支持")
                return []
                    
        except Exception as e:
            self.logger.error(f"处理AllSummon数据失败: {e}")
            return []

    def format_multiple_pets(self, equip_id, db_path):
        """格式化角色的所有宝宝信息为JSON格式"""
        conn = sqlite3.connect(db_path)
        try:
            # 查询该角色的宝宝JSON数据
            cursor = conn.cursor()
            cursor.execute('''
                SELECT all_pets_json
                FROM characters 
                WHERE equip_id = ? AND (all_pets_json IS NOT NULL AND all_pets_json != "")
            ''', (equip_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            all_pets_json = result[0]
            
            # 如果有多宝宝JSON数据，直接返回JSON
            if all_pets_json:
                try:
                    pets_data = json.loads(all_pets_json)
                    if pets_data and isinstance(pets_data, list):
                        # 直接返回JSON字符串（格式化为紧凑格式）
                        return json.dumps(pets_data, ensure_ascii=False, separators=(',', ':'))
                except Exception as e:
                    self.logger.error(f"解析宝宝JSON数据失败: {e}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"格式化宝宝信息失败: {e}")
            return None
        finally:
            conn.close()

    def get_pet_aptitude(self, pet_data, aptitude_type, index):
        """
        根据pet.js逻辑获取宠物资质数据
        优先使用csavezz处理后的数据，否则回退到MAX字段
        """
        # 首先尝试从csavezz获取处理后的资质数据
        csavezz = pet_data.get('csavezz', '')
        if csavezz and isinstance(csavezz, str):
            try:
                zz_values = csavezz.split('|')
                if len(zz_values) > index:
                    return int(zz_values[index])
            except (ValueError, IndexError):
                pass
        
        # 回退到MAX字段映射
        max_field_mapping = {
            'attack': 'ATK_MAX',
            'defence': 'DEF_MAX', 
            'physical': 'HP_MAX',
            'magic': 'MP_MAX',
            'speed': 'SPD_MAX',
            'avoid': 'MS_MAX'
        }
        
        max_field = max_field_mapping.get(aptitude_type)
        if max_field:
            return pet_data.get(max_field, 0)
        
        return 0

    def load_skill_config(self):
        """
        从ConfigLoader加载技能配置
        """
        if hasattr(self, '_skill_mapping_cache') and self._skill_mapping_cache:
            return self._skill_mapping_cache
            
        if not self.config_loader:
            raise RuntimeError("ConfigLoader不可用")
            
        try:
            self._skill_mapping_cache = self.config_loader.get_pet_skill_config()
            self.logger.debug(f"加载技能配置: {len(self._skill_mapping_cache)}个技能")
        except Exception as e:
            self.logger.error(f"加载技能配置失败: {e}")
            raise e
            
        return self._skill_mapping_cache

    def get_skill_name(self, skill_id):
        """
        根据技能ID获取中文技能名称
        """
        skill_mapping = self.load_skill_config()
        return skill_mapping.get(str(skill_id), f"未知技能{skill_id}")

    def get_pet_wuxing(self, iAtt_F):
        """
        根据iAtt_F字段获取五行属性
        参考parse_role.js第790-795行的wuxing_info映射
        """
        wuxing_mapping = {
            0: "未知",
            1: "金", 
            2: "木",
            4: "土", 
            8: "水",
            16: "火"
        }
        return wuxing_mapping.get(iAtt_F, "未知")

    def get_pet_attribute_point(self, pet_data, field, attr_field):
        """
        根据pet.js逻辑获取宠物属性加点
        参考pet.js第110-125行的计算逻辑：原始属性 - 进阶额外加点
        """
        # 获取当前总属性值
        total_value = pet_data.get(field, 0)
        
        # 获取进阶额外加点 (jj_extra_add)
        jj_extra_add = pet_data.get('jj_extra_add', {})
        extra_add = 0
        if isinstance(jj_extra_add, dict):
            extra_add = jj_extra_add.get(attr_field, 0)
        
        # 根据pet.js逻辑：原始属性加点 = 总属性 - 进阶额外加点
        original_points = total_value - extra_add
        
        return max(0, original_points)  # 确保不为负数

    def parse_pet_neidan(self, pet_data):
        """
        解析内丹信息
        参考pet.js第307-326行的parse_neidan函数实现
        """
        neidan_list = []
        summon_core = pet_data.get('summon_core', {})
        
        if summon_core:
            # 加载内丹配置
            neidan_config = self.load_neidan_config()
            
            for neidan_id, neidan_info in summon_core.items():
                # 处理内丹等级数据
                level = 0
                if isinstance(neidan_info, str):
                    # 字符串格式如: "[5,0,([]),]"，提取第一个数字
                    match = re.search(r'\[(\d+)', neidan_info)
                    if match:
                        level = int(match.group(1))
                elif isinstance(neidan_info, (list, tuple)) and len(neidan_info) > 0:
                    level = neidan_info[0]
                elif isinstance(neidan_info, (int, float)):
                    level = neidan_info
                
                # 从配置文件获取内丹名称和描述
                config_info = neidan_config.get(neidan_id, {})
                neidan_name = config_info.get('name', f"内丹_{neidan_id}")
                neidan_desc = config_info.get('desc', '')
                
                # 根据pet.js逻辑构造内丹信息
                neidan_item = {
                    "内丹名称": neidan_name,
                    "等级": level,
                    "描述": neidan_desc
                }
                neidan_list.append(neidan_item)
        
        return neidan_list

    def load_neidan_config(self):
        """
        从ConfigLoader加载内丹配置信息
        """
        if hasattr(self, '_neidan_config_cache') and self._neidan_config_cache:
            return self._neidan_config_cache
            
        if not self.config_loader:
            raise RuntimeError("ConfigLoader不可用")
            
        try:
            self._neidan_config_cache = self.config_loader.get_pet_neidan_config()
            self.logger.debug(f"加载内丹配置: {len(self._neidan_config_cache)}个内丹")
        except Exception as e:
            self.logger.error(f"加载内丹配置失败: {e}")
            raise e
            
        return self._neidan_config_cache

    def load_pet_type_config(self):
        """
        从ConfigLoader加载宠物类型配置
        """
        if hasattr(self, '_pet_type_config') and self._pet_type_config:
            return self._pet_type_config
            
        if not self.config_loader:
            raise RuntimeError("ConfigLoader不可用")
            
        try:
            self._pet_type_config = self.config_loader.get_pet_type_config()
            self.logger.debug(f"加载宠物类型配置: {len(self._pet_type_config)}个类型")
        except Exception as e:
            self.logger.error(f"加载宠物类型配置失败: {e}")
            raise e
            
        return self._pet_type_config

    def get_pet_type_name(self, type_id):
        """
        根据宠物类型ID获取中文名称
        
        Args:
            type_id: 宠物类型ID（数字或字符串）
            
        Returns:
            str: 宠物类型的中文名称，如果未找到则返回原始ID
        """
        if not type_id:
            return ""
            
        config = self.load_pet_type_config()
        type_id_str = str(type_id)
        
        return config.get(type_id_str, type_id_str)
    
    def load_pet_shipin_config(self):
        """
        从ConfigLoader加载宠物饰品配置
        """
        if hasattr(self, '_pet_shipin_config') and self._pet_shipin_config:
            return self._pet_shipin_config
            
        if not self.config_loader:
            raise RuntimeError("ConfigLoader不可用")
            
        try:
            self._pet_shipin_config = self.config_loader.get_pet_shipin_config()
            self.logger.debug(f"加载宠物饰品配置: {len(self._pet_shipin_config)}个饰品")
        except Exception as e:
            self.logger.error(f"加载宠物饰品配置失败: {e}")
            raise e
            
        return self._pet_shipin_config

    def get_pet_shipin_name(self, shipin_id):
        """
        根据饰品类型ID获取中文名称
        
        Args:
            shipin_id: 饰品类型ID（数字或字符串）
            
        Returns:
            str: 饰品的中文名称，如果未找到则返回原始ID
        """
        if not shipin_id:
            return ""
            
        config = self.load_pet_shipin_config()
        shipin_id_str = str(shipin_id)
        
        return config.get(shipin_id_str, shipin_id_str) 