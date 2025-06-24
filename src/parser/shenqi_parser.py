#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
神器数据解析器 - 简化版本
用于处理已经解析好的神器JSON数据，生成中文可读的神器信息
"""

import json
import os
import logging
from typing import Dict, List, Optional, Union, Any

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


# 常量定义
class ShenqiConstants:
    """神器解析相关常量"""
    
    # 五行映射
    WUXING_MAPPING = {
        0:"",
        1: "金",
        2: "木", 
        4: "土",
        8: "水",
        16: "火"
    }


class ShenqiParser:
    """神器数据解析器 - 简化版本"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger if logger else self._setup_logger()
        self.config_loader = get_config_loader()
        if not self.config_loader:
            self.logger.warning("配置加载器不可用，某些功能可能受限")

    def _setup_logger(self) -> logging.Logger:
        """设置日志器"""
        logger = logging.getLogger('ShenqiParser')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def process_character_shenqi(self, parsed_data: Dict[str, Any], character_name: Optional[str] = None) -> Dict[str, Any]:
        """
        处理角色神器信息，转换为中文可读格式
        
        Args:
            parsed_data: 解析后的数据
            character_name: 角色名称（可选）
            
        Returns:
            中文格式的神器信息
        """
        try:
            # 从parsed_data中获取shenqi信息
            shenqi_data = parsed_data.get('shenqi', {})
            if not shenqi_data:
                self.logger.warning("未找到神器数据")
                return self._empty_shenqi_info()
            
            # 现在shenqi_data应该已经是解析好的字典格式
            if isinstance(shenqi_data, dict):
                return self._format_shenqi_data(shenqi_data)
            else:
                self.logger.warning(f"神器数据类型不支持: {type(shenqi_data)}")
                return self._empty_shenqi_info()
            
        except Exception as e:
            self.logger.error(f"处理角色神器信息失败: {e}", exc_info=True)
            return self._empty_shenqi_info()
    
    def _format_shenqi_data(self, shenqi_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化神器数据为中文可读格式
        
        Args:
            shenqi_data: 神器数据字典
            
        Returns:
            格式化后的神器信息
        """
        try:
            # 神器基本信息
            shenqi_id = shenqi_data.get('id') or shenqi_data.get('skill')
            if not shenqi_id:
                self.logger.warning("未找到有效的神器ID")
                return self._empty_shenqi_info()
            
            # 获取神器名称
            shenqi_config = self.load_shenqi_config()
            shenqi_name = shenqi_config.get(str(shenqi_id), {}).get('name', f"神器ID:{shenqi_id}")
            
            # 获取作用描述
            skill_desc = shenqi_data.get('skill_desc', '')
            
            # 解析套装数据 - suit字段应该已经是解析好的列表格式
            神器属性 = []
            
            suit_data = shenqi_data.get('suit')
            
            if suit_data and isinstance(suit_data, list):
                for i, suit in enumerate(suit_data):
                    if isinstance(suit, dict) and suit.get('components'):
                        # 每个套装的组件灵犀玉数据
                        套装属性 = []
                        for component in suit['components']:
                            if component.get('wuxing'):
                                # 每个组件的灵犀玉数据
                                for wuxing in component['wuxing']:
                                    灵犀玉信息 = self._format_wuxing_stone_info(wuxing)
                                    套装属性.append(灵犀玉信息)
                        
                        if 套装属性:
                            神器属性.append(套装属性)
            
            # 如果没有找到套装数据，尝试旧格式
            if not 神器属性 and 'components' in shenqi_data:
                套装属性 = []
                for component in shenqi_data.get('components', []):
                    if component.get('wuxing'):
                        for wuxing in component['wuxing']:
                            灵犀玉信息 = self._format_wuxing_stone_info(wuxing)
                            套装属性.append(灵犀玉信息)
                
                if 套装属性:
                    神器属性.append(套装属性)
            
            # 构建最终格式
            result = {
                "神器名称": shenqi_name,
                "作用描述": skill_desc,
                "神器属性": 神器属性
            }
            
            # 添加兼容性字段
            result['是否新版神器'] = 'suit' in shenqi_data
            result['激活套装'] = [f"套装{i+1}" for i in range(len(神器属性))] if 神器属性 else ["无激活套装"]
            
            return result
            
        except Exception as e:
            self.logger.error(f"格式化神器数据失败: {e}", exc_info=True)
            return self._empty_shenqi_info()

    def _format_wuxing_stone_info(self, wuxing: Dict[str, Any]) -> Dict[str, Any]:
        """格式化灵犀玉信息为用户要求的格式"""
        try:
            # 获取五行类型
            wuxing_id = wuxing.get('id', 0)
            五行名称 = self._get_wuxing_name(wuxing_id)
            
            # 解析属性值 - 简化版本，不使用正则表达式
            attr = wuxing.get('attr', '')
            属性信息 = self._parse_attribute_value(attr)
            
            # 获取特性（词缀）
            affix_id = wuxing.get('wuxingshi_affix', 0)
            特性 = self._get_wuxing_affix_name(affix_id) if affix_id > 0 else None
            
            # 构建结果
            result = {
                "五行": 五行名称
            }
            
            # 添加属性信息
            if 属性信息:
                result.update(属性信息)
            
            # 添加特性
            if 特性:
                result["特性"] = 特性
            
            return result
            
        except Exception as e:
            self.logger.error(f"格式化灵犀玉信息失败: {e}")
            return {"五行": "未知"}

    def _parse_attribute_value(self, attr_str: str) -> Dict[str, str]:
        """直接返回属性值，不再解析字符串"""
        try:
            if not attr_str:
                return {}
            
            # 直接返回属性值，不再进行字符串解析
            return {"属性": attr_str}
            
        except Exception as e:
            self.logger.error(f"处理属性值失败: {e}")
            return {}

    def _get_wuxing_name(self, wuxing_id: int) -> str:
        """根据灵犀玉ID获取名称"""
        return ShenqiConstants.WUXING_MAPPING.get(wuxing_id, f"五行_{wuxing_id}")

    def _get_wuxing_affix_name(self, affix_id: int) -> str:
        """获取特性名称 - 使用统一配置加载器"""
        try:
            if self.config_loader:
                affix_config = self.config_loader.get_wuxing_affix_config()
                return affix_config.get(str(affix_id), f"特性{affix_id}")
            else:
                return f"特性{affix_id}"
        except Exception as e:
            self.logger.error(f"获取特性名称失败: {e}")
            return f"特性{affix_id}"

    def _empty_shenqi_info(self):
        """返回空的神器信息结构"""
        return {
            "神器名称": "",
            "神器描述": "",
            "是否新版神器": False,
            "激活套装": [],
            "神器属性": []
        }
    
    def load_shenqi_config(self) -> Dict[str, Dict[str, str]]:
        """加载神器配置信息 - 使用统一配置加载器"""
        try:
            if self.config_loader:
                return self.config_loader.get_shenqi_config()
            else:
                self.logger.warning("配置加载器不可用，返回空配置")
                return {}
        except Exception as e:
            self.logger.error(f"加载神器配置失败: {e}")
            return {}
