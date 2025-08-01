#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用解析器模块
负责处理梦幻西游CBG中各种通用的数据解析和转换
"""

import logging
import json
import re
from typing import Dict, Any, Optional
from functools import lru_cache

try:
    from ..cbg_config import (
        HUMAN_SCHOOLS, DEMON_SCHOOLS, IMMORTAL_SCHOOLS,
        CHINESE_NUM_CONFIG, ROLE_ZHUAN_ZHI_CONFIG
    )
    from .config_loader import get_config_loader
except ImportError:
    # 当作为独立模块运行时，使用绝对导入
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from cbg_config import (
        HUMAN_SCHOOLS, DEMON_SCHOOLS, IMMORTAL_SCHOOLS,
        CHINESE_NUM_CONFIG, ROLE_ZHUAN_ZHI_CONFIG
    )
    # 导入当前目录下的config_loader
    from parser.config_loader import get_config_loader


class CommonParser:
    """通用数据解析器"""
    
    def __init__(self, logger=None):
        """初始化通用解析器"""
        self.logger = logger or logging.getLogger(__name__)
        self._config_loader = get_config_loader()
        # 缓存配置映射
        self._life_skill_mapping: Optional[Dict[str, str]] = None
        self._school_skill_mapping: Optional[Dict[str, Dict[str, Any]]] = None
        self._juqing_skill_mapping: Optional[Dict[str, str]] = None
        self._school_mapping: Optional[Dict[str, str]] = None
        self._outdoor_level_mapping: Optional[Dict[str, str]] = None
        self._farm_level_mapping: Optional[Dict[str, str]] = None
        self._fangwu_level_mapping: Optional[Dict[str, str]] = None
    
    @lru_cache(maxsize=1)
    def _get_life_skill_mapping(self) -> Dict[str, str]:
        """获取生活技能映射（带缓存）"""
        if self._life_skill_mapping is None:
            self._life_skill_mapping = self._config_loader.get_life_skill_mapping()
        return self._life_skill_mapping
    
    @lru_cache(maxsize=1)
    def _get_school_skill_mapping(self) -> Dict[str, Dict[str, Any]]:
        """获取师门技能映射（带缓存）"""
        if self._school_skill_mapping is None:
            self._school_skill_mapping = self._config_loader.get_school_skill_mapping()
        return self._school_skill_mapping
    
    @lru_cache(maxsize=1)
    def _get_juqing_skill_mapping(self) -> Dict[str, str]:
        """获取剧情技能映射（带缓存）"""
        if self._juqing_skill_mapping is None:
            self._juqing_skill_mapping = self._config_loader.get_juqing_skill_mapping()
        return self._juqing_skill_mapping
    
    @lru_cache(maxsize=1)
    def _get_school_mapping(self) -> Dict[str, str]:
        """获取门派映射（带缓存）"""
        if self._school_mapping is None:
            self._school_mapping = self._config_loader.get_school_mapping()
        return self._school_mapping
    
    @lru_cache(maxsize=1)
    def _get_outdoor_level_mapping(self) -> Dict[str, str]:
        """获取庭院等级映射（带缓存）"""
        if self._outdoor_level_mapping is None:
            self._outdoor_level_mapping = self._config_loader.get_outdoor_level_mapping()
        return self._outdoor_level_mapping
    
    @lru_cache(maxsize=1)
    def _get_farm_level_mapping(self) -> Dict[str, str]:
        """获取牧场等级映射（带缓存）"""
        if self._farm_level_mapping is None:
            self._farm_level_mapping = self._config_loader.get_farm_level_mapping()
        return self._farm_level_mapping
    
    @lru_cache(maxsize=1)
    def _get_fangwu_level_mapping(self) -> Dict[str, str]:
        """获取房屋等级映射（带缓存）"""
        if not hasattr(self, '_fangwu_level_mapping') or self._fangwu_level_mapping is None:
            self._fangwu_level_mapping = self._config_loader.get_fangwu_level_mapping()
        return self._fangwu_level_mapping
    
    def get_school_name(self, school_id):
        """根据门派ID获取门派名称"""
        school_id_str = str(school_id)
        school_mapping = self._get_school_mapping()
        return school_mapping.get(school_id_str, f"未知门派({school_id})")
    
    def get_race_name(self, school_id):
        """根据门派ID获取种族名称"""
        try:
            school_id_int = int(school_id)
            if school_id_int in HUMAN_SCHOOLS:
                return "人族"
            elif school_id_int in DEMON_SCHOOLS:
                return "魔族"
            elif school_id_int in IMMORTAL_SCHOOLS:
                return "仙族"
            else:
                return "未知种族"
        except (ValueError, TypeError):
            return "未知种族"
    
    def get_fly_status(self, equip_data):
        """解析飞升状态（从large_equip_desc字段中解析）"""
        try:
            # 尝试从large_equip_desc字段中解析飞升信息
            large_desc = equip_data.get('large_equip_desc', '')
            if isinstance(large_desc, str) and large_desc:
                # 查找iZhuanZhi值
                zhuan_zhi_match = re.search(r'"iZhuanZhi":(\d+)', large_desc)
                i_zhuan_zhi = int(zhuan_zhi_match.group(1)) if zhuan_zhi_match else 0
                
                # 查找i3FlyLv值
                fly_lv_match = re.search(r'"i3FlyLv":(\d+)', large_desc)
                i3_fly_lv = int(fly_lv_match.group(1)) if fly_lv_match else 0
                
                # 查找nine_fight_level值（生死劫等级）
                nine_fight_match = re.search(r'"nine_fight_level":(\d+)', large_desc)
                nine_fight_level = int(nine_fight_match.group(1)) if nine_fight_match else 0
                
                # 根据解析结果判断飞升状态
                if i3_fly_lv and i3_fly_lv > 0:
                    # 三界飞升状态：飞升+中文数字
                    chinese_num = CHINESE_NUM_CONFIG.get(i3_fly_lv, str(i3_fly_lv))
                    return f"化圣{chinese_num}"
                elif nine_fight_level > 0:
                    # 生死劫状态
                    if nine_fight_level >= 9:
                        return "已渡劫"
                    else:
                        chinese_num = CHINESE_NUM_CONFIG.get(nine_fight_level, str(nine_fight_level))
                        return f"生死劫{chinese_num}层"
                elif i_zhuan_zhi is not None and i_zhuan_zhi >= 0:
                    # 使用转职状态
                    return ROLE_ZHUAN_ZHI_CONFIG.get(i_zhuan_zhi, "未知")
                else:
                    return "未飞升"
                    
        except Exception as e:
            self.logger.debug(f"解析飞升状态失败: {e}")
            
        # 如果解析失败，尝试从顶层字段获取
        i3_fly_lv = equip_data.get('i3FlyLv')
        i_zhuan_zhi = equip_data.get('iZhuanZhi')
        
        if i3_fly_lv and i3_fly_lv > 0:
            chinese_num = CHINESE_NUM_CONFIG.get(i3_fly_lv, str(i3_fly_lv))
            return f"飞升{chinese_num}"
        elif i_zhuan_zhi is not None and i_zhuan_zhi >= 0:
            return ROLE_ZHUAN_ZHI_CONFIG.get(i_zhuan_zhi, "未知")
        else:
            return "未知"
    
    def get_rent_level_name(self, level):
        """转换房屋等级数字为中文名称"""
        if level is None:
            return "未知"
        fangwu_level_mapping = self._get_fangwu_level_mapping()
        return fangwu_level_mapping.get(str(level), f"未知等级({level})")
    
    def get_outdoor_level_name(self, level):
        """转换庭院等级数字为中文名称"""
        if level is None:
            return "未知"
        outdoor_level_mapping = self._get_outdoor_level_mapping()
        return outdoor_level_mapping.get(str(level), f"未知等级({level})")
    
    def get_farm_level_name(self, level):
        """转换牧场等级数字为中文名称"""
        if level is None:
            return "未知"
        farm_level_mapping = self._get_farm_level_mapping()
        return farm_level_mapping.get(str(level), f"未知等级({level})")
    
    def get_house_real_owner_name(self, owner_status):
        """转换房屋真实拥有者状态为中文名称"""
        if owner_status is None:
            return "未知"
        # 参考parse_role.js中的get_fangwu_owner_info逻辑
        if owner_status == 1 or owner_status == "1" or owner_status is True:
            return "是"
        elif owner_status == 0 or owner_status == "0" or owner_status is False:
            return "否"
        else:
            return "未知"
    
    def parse_life_skills(self, skills_data):
        """解析生活技能数据
        
        Args:
            skills_data (dict|str): 生活技能数据，可以是字典或JSON字符串
            
        Returns:
            str: JSON格式的生活技能字符串，如 '{"强身":45,"巧匠":40}'
        """
        try:
            # 如果输入是字符串，尝试解析为字典
            if isinstance(skills_data, str):
                if not skills_data:
                    return ""
                try:
                    skills_data = json.loads(skills_data)
                except json.JSONDecodeError:
                    self.logger.warning(f"无法解析技能数据: {skills_data}")
                    return ""
            
            if not isinstance(skills_data, dict):
                self.logger.warning(f"技能数据格式错误: {type(skills_data)}")
                return ""
            
            # 获取生活技能映射
            life_skill_mapping = self._get_life_skill_mapping()
            
            # 提取生活技能
            life_skills = {}
            for skill_id, level in skills_data.items():
                # 确保skill_id是字符串
                skill_id = str(skill_id)
                if skill_id in life_skill_mapping:
                    skill_name = life_skill_mapping[skill_id]
                    life_skills[skill_name] = level
            
            # 返回JSON格式字符串
            return json.dumps(life_skills, ensure_ascii=False) if life_skills else ""
            
        except Exception as e:
            self.logger.error(f"解析生活技能时出错: {e}")
            return ""
    
    def parse_school_skills(self, skills_data):
        """解析师门技能数据
        
        Args:
            skills_data (dict|str): 技能数据，可以是字典或JSON字符串
            
        Returns:
            str: JSON格式的师门技能字符串，如 '{"十方无敌":130,"无双一击":130}'
        """
        try:
            # 如果输入是字符串，尝试解析为字典
            if isinstance(skills_data, str):
                if not skills_data:
                    return ""
                try:
                    skills_data = json.loads(skills_data)
                except json.JSONDecodeError:
                    self.logger.warning(f"无法解析技能数据: {skills_data}")
                    return ""
            
            if not isinstance(skills_data, dict):
                self.logger.warning(f"技能数据格式错误: {type(skills_data)}")
                return ""
            
            # 获取师门技能映射
            school_skill_mapping = self._get_school_skill_mapping()
            
            # 提取师门技能
            school_skills = {}
            for skill_id, level in skills_data.items():
                # 确保skill_id是字符串
                skill_id = str(skill_id)
                if skill_id in school_skill_mapping:
                    skill_info = school_skill_mapping[skill_id]
                    skill_name = skill_info['name']
                    school_skills[skill_name] = level
            
            # 返回JSON格式字符串
            return json.dumps(school_skills, ensure_ascii=False) if school_skills else ""
            
        except Exception as e:
            self.logger.error(f"解析师门技能时出错: {e}")
            return ""
    
    def parse_ju_qing_skills(self, skills_data):
        """解析剧情技能数据
        
        Args:
            skills_data (dict|str): 剧情技能数据，可以是字典或JSON字符串
            
        Returns:
            str: JSON格式的剧情技能字符串，如 '{"古董评估":30,"建筑之术":25}'
        """
        try:
            # 如果输入是字符串，尝试解析为字典
            if isinstance(skills_data, str):
                if not skills_data:
                    return ""
                try:
                    skills_data = json.loads(skills_data)
                except json.JSONDecodeError:
                    self.logger.warning(f"无法解析技能数据: {skills_data}")
                    return ""
            
            if not isinstance(skills_data, dict):
                self.logger.warning(f"技能数据格式错误: {type(skills_data)}")
                return ""
            
            # 获取剧情技能映射
            juqing_skill_mapping = self._get_juqing_skill_mapping()
            
            # 提取剧情技能
            ju_qing_skills = {}
            for skill_id, level in skills_data.items():
                # 确保skill_id是字符串
                skill_id = str(skill_id)
                if skill_id in juqing_skill_mapping:
                    skill_name = juqing_skill_mapping[skill_id]
                    ju_qing_skills[skill_name] = level
            
            # 返回JSON格式字符串
            return json.dumps(ju_qing_skills, ensure_ascii=False) if ju_qing_skills else ""
            
        except Exception as e:
            self.logger.error(f"解析剧情技能时出错: {e}")
            return "" 