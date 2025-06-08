#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
坐骑数据解析器
用于处理已经解析好的坐骑JSON数据，生成中文可读的坐骑信息
"""

import json
import os
import logging
from typing import Dict, List, Optional, Union, Any
from functools import lru_cache

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


class RiderParser:
    """坐骑数据解析器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger if logger else self._setup_logger()
        self.config_loader = get_config_loader()
        if not self.config_loader:
            self.logger.warning("配置加载器不可用，将影响坐骑配置加载")
        self._rider_config: Optional[Dict[str, Any]] = None
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志器"""
        logger = logging.getLogger('RiderParser')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def process_character_rider(self, parsed_data: Dict[str, Any], character_name: Optional[str] = None) -> Dict[str, Any]:
        """
        处理角色坐骑信息，转换为中文可读格式
        
        Args:
            parsed_data: 解析后的数据
            character_name: 角色名称（可选）
            
        Returns:
            中文格式的坐骑信息
        """
        try:
            self.logger.info(f"开始解析角色 {character_name or '未知'} 的坐骑信息")
            
            # 从parsed_data中获取rider信息
            rider_data = parsed_data.get('rider', {})
            if not rider_data:
                self.logger.warning("未找到坐骑数据")
                return self._empty_rider_info()
            
            # 现在rider_data应该已经是解析好的字典格式
            if isinstance(rider_data, dict):
                return self._format_rider_data(rider_data)
            else:
                self.logger.warning(f"坐骑数据类型不支持: {type(rider_data)}")
                return self._empty_rider_info()
            
        except Exception as e:
            self.logger.error(f"处理角色坐骑信息失败: {e}", exc_info=True)
            return self._empty_rider_info()
    
    def _format_rider_data(self, rider_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化坐骑数据为中文可读格式
        
        Args:
            rider_data: 坐骑数据字典
            
        Returns:
            格式化后的坐骑信息
        """
        try:
            config = self.load_rider_config()
            formatted_riders = {}
            
            for rider_id, rider_info in rider_data.items():
                if not isinstance(rider_info, dict):
                    continue
                
                # 格式化单个坐骑信息
                formatted_rider = self._format_single_rider(rider_info, config)
                formatted_riders[rider_id] = formatted_rider
            
            result = {
                "坐骑列表": formatted_riders,
                "坐骑数量": len(formatted_riders)
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"格式化坐骑数据失败: {e}", exc_info=True)
            return self._empty_rider_info()
    
    def _format_single_rider(self, rider_info: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """格式化单个坐骑信息"""
        try:
            # 获取坐骑类型
            itype = rider_info.get('iType')
            rider_types = config.get('rider_info', {})
            坐骑类型 = rider_types.get(str(itype), f"类型{itype}")
            
            # 获取技能信息
            all_skills = rider_info.get('all_skills', {})
            skill_config = config.get('zuoqi_skill_desc', {})
            技能列表 = {}
            
            for skill_id, skill_level in all_skills.items():
                skill_info = skill_config.get(str(skill_id), {})
                skill_name = skill_info.get('name', f"技能{skill_id}")
                技能列表[skill_name] = skill_level
            
            # 获取主属性
            主属性 = rider_info.get('mattrib', '')
            
            # 获取等级
            等级 = rider_info.get('iGrade', 0)
            
            # 获取灵气额外成长
            灵气额外成长 = rider_info.get('ExtraGrow', 0)
            
            # 获取成长值并转换
            exgrow = rider_info.get('exgrow', 0)
            成长 = round(exgrow / 10000, 4) if exgrow > 0 else 0
            
            result = {
                "技能": 技能列表,
                "主属性": 主属性,
                "等级": 等级,
                "类型": 坐骑类型,
                "灵气额外成长": 灵气额外成长,
                "成长": 成长
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"格式化单个坐骑信息失败: {e}")
            return {
                "技能": {},
                "主属性": "未知",
                "等级": 0,
                "类型": "未知",
                "灵气额外成长": 0,
                "成长": 0
            }
    
    def _empty_rider_info(self):
        """返回空的坐骑信息结构"""
        return {
            "坐骑列表": {},
            "坐骑数量": 0
        }
    
    @lru_cache(maxsize=1)
    def load_rider_config(self) -> Dict[str, Any]:
        """从ConfigLoader加载坐骑配置信息"""
        if self._rider_config:
            return self._rider_config
            
        if not self.config_loader:
            raise RuntimeError("ConfigLoader不可用")
            
        try:
            self._rider_config = self.config_loader.get_rider_config()
            self.logger.debug(f"加载坐骑配置: {len(self._rider_config)}个配置块")
        except Exception as e:
            self.logger.error(f"加载坐骑配置失败: {e}")
            raise e
            
        return self._rider_config
