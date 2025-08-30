#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置加载器
用于从game_auto_config.js加载各种配置信息
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from functools import lru_cache


class ConfigLoader:
    """配置加载器 - 从game_auto_config.js读取配置"""
    
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'constant', 'game_auto_config.js')
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger if logger else self._setup_logger()
        self._cached_config: Optional[Dict[str, Any]] = None
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志器"""
        logger = logging.getLogger('ConfigLoader')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    @lru_cache(maxsize=1)
    def _load_full_config(self) -> Dict[str, Any]:
        """加载完整配置（带缓存）"""
        if self._cached_config:
            return self._cached_config
            
        try:
            if not os.path.exists(self.CONFIG_FILE):
                raise FileNotFoundError(f"配置文件不存在: {self.CONFIG_FILE}")
            
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # game_auto_config.js 是一个JavaScript变量文件
            # 格式：var CBG_GAME_CONFIG={...}
            var_prefix = 'var CBG_GAME_CONFIG='
            start_pos = content.find(var_prefix)
            if start_pos == -1:
                raise ValueError(f"未找到JavaScript变量: CBG_GAME_CONFIG")
            
            # 获取JSON部分（从=号后开始）
            json_start = start_pos + len(var_prefix)
            json_content = content[json_start:].strip()
            
            self._cached_config = json.loads(json_content)
            self.logger.info(f"成功加载game_auto_config.js配置，包含{len(self._cached_config)}个配置项")
            return self._cached_config
            
        except json.JSONDecodeError as e:
            self.logger.error(f"配置文件JSON格式错误: {e}")
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            raise e
    
    def get_shenqi_config(self) -> Dict[str, Dict[str, str]]:
        """获取神器配置"""
        try:
            config = self._load_full_config()
            shenqi_info = config.get('shenqi_info', {})
            
            # 转换为ID->{name, desc}的映射
            mapping = {}
            for shenqi_id, shenqi_config in shenqi_info.items():
                if isinstance(shenqi_config, dict) and 'name' in shenqi_config:
                    mapping[shenqi_id] = {
                        'name': shenqi_config.get('name', ''),
                        'desc': shenqi_config.get('desc', '')
                    }
            
            self.logger.debug(f"加载了{len(mapping)}个神器配置")
            return mapping
            
        except Exception as e:
            self.logger.error(f"获取神器配置失败: {e}")
            raise e
    
    def get_wuxing_affix_config(self) -> Dict[str, str]:
        """获取灵犀玉特性配置"""
        try:
            config = self._load_full_config()
            wuxing_affix_info = config.get('wuxing_affix_info', {})
            
            # 转换为ID->名称的映射
            mapping = {str(k): str(v) for k, v in wuxing_affix_info.items()}
            
            self.logger.debug(f"加载了{len(mapping)}个灵犀玉特性配置")
            return mapping
            
        except Exception as e:
            self.logger.error(f"获取灵犀玉特性配置失败: {e}")
            raise e
    
    def get_life_skill_mapping(self) -> Dict[str, str]:
        """获取生活技能映射"""
        try:
            config = self._load_full_config()
            life_skill_desc = config.get('life_skill_desc', {})
            
            # 转换为ID->名称的映射
            mapping = {}
            for skill_id, skill_info in life_skill_desc.items():
                if isinstance(skill_info, dict) and 'name' in skill_info:
                    mapping[skill_id] = skill_info['name']
            
            self.logger.debug(f"加载了{len(mapping)}个生活技能配置")
            return mapping
            
        except Exception as e:
            self.logger.error(f"获取生活技能配置失败: {e}")
            raise e
    
    def get_school_skill_mapping(self) -> Dict[str, Dict[str, Any]]:
        """获取师门技能映射"""
        try:
            config = self._load_full_config()
            school_skill_desc = config.get('school_skill_desc', {})
            school_skill = config.get('school_skill', {})
            
            # 转换为ID->{name, pos}的映射
            mapping = {}
            for skill_id, skill_info in school_skill_desc.items():
                if isinstance(skill_info, dict) and 'name' in skill_info:
                    # 从school_skill中获取pos信息
                    pos_info = school_skill.get(skill_id, {})
                    pos = pos_info.get('pos', 0) if isinstance(pos_info, dict) else 0
                    
                    mapping[skill_id] = {
                        'name': skill_info['name'],
                        'pos': pos
                    }
            
            self.logger.debug(f"加载了{len(mapping)}个师门技能配置")
            return mapping
            
        except Exception as e:
            self.logger.error(f"获取师门技能配置失败: {e}")
            raise e
    
    def get_juqing_skill_mapping(self) -> Dict[str, str]:
        """获取剧情技能映射"""
        try:
            config = self._load_full_config()
            ju_qing_skill = config.get('ju_qing_skill', {})
            
            self.logger.debug(f"加载了{len(ju_qing_skill)}个剧情技能配置")
            return ju_qing_skill
            
        except Exception as e:
            self.logger.error(f"获取剧情技能配置失败: {e}")
            raise e
    
    def get_school_mapping(self) -> Dict[str, str]:
        """获取门派映射"""
        try:
            config = self._load_full_config()
            school_info = config.get('school_info', {})
            
            self.logger.debug(f"加载了{len(school_info)}个门派配置")
            return school_info
            
        except Exception as e:
            self.logger.error(f"获取门派配置失败: {e}")
            raise e
    
    def get_outdoor_level_mapping(self) -> Dict[str, str]:
        """获取庭院等级映射"""
        try:
            config = self._load_full_config()
            tingyuan_info = config.get('tingyuan_info', {})
            
            self.logger.debug(f"加载了{len(tingyuan_info)}个庭院等级配置")
            return tingyuan_info
            
        except Exception as e:
            self.logger.error(f"获取庭院等级配置失败: {e}")
            raise e
    
    def get_farm_level_mapping(self) -> Dict[str, str]:
        """获取牧场等级映射"""
        try:
            config = self._load_full_config()
            muchang_info = config.get('muchang_info', {})
            
            self.logger.debug(f"加载了{len(muchang_info)}个牧场等级配置")
            return muchang_info
            
        except Exception as e:
            self.logger.error(f"获取牧场等级配置失败: {e}")
            raise e
    
    def get_fangwu_level_mapping(self) -> Dict[str, str]:
        """获取房屋等级映射"""
        try:
            config = self._load_full_config()
            fangwu_info = config.get('fangwu_info', {})
            
            self.logger.debug(f"加载了{len(fangwu_info)}个房屋等级配置")
            return fangwu_info
            
        except Exception as e:
            self.logger.error(f"获取房屋等级配置失败: {e}")
            raise e
    
    def get_pet_skill_config(self) -> Dict[str, str]:
        """获取召唤兽技能配置"""
        try:
            config = self._load_full_config()
            pet_skills_for_front = config.get('pet_skills_for_front', {})
            
            # 转换为ID->名称的映射
            mapping = {str(k): str(v) for k, v in pet_skills_for_front.items()}
            
            self.logger.debug(f"加载了{len(mapping)}个召唤兽技能配置")
            return mapping
            
        except Exception as e:
            self.logger.error(f"获取召唤兽技能配置失败: {e}")
            raise e
    
    def get_pet_neidan_config(self) -> Dict[str, Dict[str, str]]:
        """获取召唤兽内丹配置"""
        try:
            config = self._load_full_config()
            neidan_desc = config.get('neidan_desc', {})
            pet_neidans = config.get('pet_neidans', {})
            
            # 转换为ID->{name, desc}的映射
            mapping = {}
            
            # 优先从neidan_desc获取名称和描述
            for neidan_id, neidan_info in neidan_desc.items():
                if isinstance(neidan_info, dict):
                    mapping[neidan_id] = {
                        'name': neidan_info.get('name', ''),
                        'desc': neidan_info.get('desc', '')
                    }
            
            # 如果neidan_desc没有足够数据，从pet_neidans补充名称
            for neidan_id, neidan_name in pet_neidans.items():
                if neidan_id not in mapping:
                    mapping[neidan_id] = {
                        'name': str(neidan_name),
                        'desc': ''
                    }
            
            self.logger.debug(f"加载了{len(mapping)}个召唤兽内丹配置")
            return mapping
            
        except Exception as e:
            self.logger.error(f"获取召唤兽内丹配置失败: {e}")
            raise e
    
    def get_pet_type_config(self) -> Dict[str, str]:
        """获取召唤兽类型配置"""
        try:
            config = self._load_full_config()
            
            # 从pet_type_info_for_front和pet_info获取类型映射
            mapping = {}
            
            # 首先从pet_type_info_for_front获取
            pet_type_info_for_front = config.get('pet_type_info_for_front', [])
            if isinstance(pet_type_info_for_front, list):
                for type_info in pet_type_info_for_front:
                    if isinstance(type_info, list) and len(type_info) >= 2:
                        type_ids_str = type_info[0]
                        type_name = type_info[1]
                        
                        # 处理可能的多个ID（用逗号分隔）
                        if ',' in type_ids_str:
                            type_ids = type_ids_str.split(',')
                        else:
                            type_ids = [type_ids_str]
                        
                        for type_id in type_ids:
                            type_id = type_id.strip()
                            if type_id:
                                mapping[type_id] = type_name
            
            # 然后从pet_info补充
            pet_info = config.get('pet_info', {})
            for type_id, type_name in pet_info.items():
                if type_id not in mapping:
                    mapping[type_id] = str(type_name)
            
            self.logger.debug(f"加载了{len(mapping)}个召唤兽类型配置")
            return mapping
            
        except Exception as e:
            self.logger.error(f"获取召唤兽类型配置失败: {e}")
            raise e
    
    def get_pet_shipin_config(self) -> Dict[str, str]:
        """获取召唤兽饰品配置"""
        try:
            config = self._load_full_config()
            pet_shipin_info = config.get('pet_shipin_info', {})
            
            # 转换为ID->名称的映射
            mapping = {str(k): str(v) for k, v in pet_shipin_info.items()}
            
            self.logger.debug(f"加载了{len(mapping)}个召唤兽饰品配置")
            return mapping
            
        except Exception as e:
            self.logger.error(f"获取召唤兽饰品配置失败: {e}")
            raise e
    
    def get_equipment_config(self) -> Dict[str, str]:
        """获取装备配置"""
        try:
            config = self._load_full_config()
            mapping = {}
            
            # 主要从equip_info获取装备配置
            equip_info = config.get('equip_info', {})
            if isinstance(equip_info, dict):
                for equip_id, equip_data in equip_info.items():
                    if isinstance(equip_data, dict) and 'name' in equip_data:
                        mapping[str(equip_id)] = equip_data['name']
                    elif isinstance(equip_data, str):
                        mapping[str(equip_id)] = equip_data
            
            # 如果equip_info中没有足够数据，从其他装备配置补充
            other_configs = [
                'pet_equip_type_to_grade_mapping',
                'equip_special_effect',
                'equip_addon_status'
            ]
            
            for config_key in other_configs:
                if config_key in config and len(mapping) < 100:  # 避免过度合并
                    data = config[config_key]
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if str(key) not in mapping:
                                if isinstance(value, dict) and 'name' in value:
                                    mapping[str(key)] = value['name']
                                elif isinstance(value, str) and len(value) > 0:
                                    mapping[str(key)] = value
            
            self.logger.debug(f"加载了{len(mapping)}个装备配置")
            return mapping
            
        except Exception as e:
            self.logger.error(f"获取装备配置失败: {e}")
            raise e
    
    def get_rider_config(self) -> Dict[str, Any]:
        """获取坐骑配置信息"""
        config = self._load_full_config()
        return config.get('rider_info', {})

    def get_fabao_config(self) -> Dict[str, Dict[str, str]]:
        """
        获取法宝配置信息
        
        Returns:
            Dict[str, Dict[str, str]]: 法宝配置信息，格式为:
            {
                "法宝ID": {
                    "name": "法宝名称",
                    "desc": "法宝描述"
                }
            }
        """
        config = self._load_full_config()
        return config.get('fabao_info', {})

    def get_clothes_config(self) -> Dict[str, Any]:
        """获取锦衣配置"""
        try:
            config = self._load_full_config()
            
            # 锦衣相关配置
            clothes_configs = {}
            
            # 获取锦衣信息
            if 'clothes_info' in config:
                clothes_configs['clothes_info'] = config['clothes_info']
            
            # 获取锦衣类型配置
            if 'clothes_type_conf' in config:
                clothes_configs['clothes_type_conf'] = config['clothes_type_conf']
            
            # 获取挂件信息（用于显示）
            if 'widget_info_for_display' in config:
                clothes_configs['widget_info_for_display'] = config['widget_info_for_display']
            
            # 如果没有找到预期配置，记录警告
            if not clothes_configs.get('clothes_info'):
                self.logger.warning("未找到clothes_info配置")
            if not clothes_configs.get('clothes_type_conf'):
                self.logger.warning("未找到clothes_type_conf配置")
            if not clothes_configs.get('widget_info_for_display'):
                self.logger.warning("未找到widget_info_for_display配置")
            
            self.logger.debug(f"加载了锦衣配置，包含{len(clothes_configs)}个配置块")
            return clothes_configs
            
        except Exception as e:
            self.logger.error(f"获取锦衣配置失败: {e}")
            raise e


# 全局实例
_config_loader = None

def get_config_loader() -> ConfigLoader:
    """获取配置加载器单例"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader 