#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
锦衣数据解析器
用于处理已经解析好的锦衣JSON数据，生成中文可读的锦衣信息
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


class ExAvtParser:
    """锦衣数据解析器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger if logger else self._setup_logger()
        self.config_loader = get_config_loader()
        if not self.config_loader:
            self.logger.warning("配置加载器不可用，将影响锦衣配置加载")
        self._clothes_config: Optional[Dict[str, Any]] = None
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志器"""
        logger = logging.getLogger('ExAvtParser')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def process_character_clothes(self, parsed_data: Dict[str, Any], character_name: Optional[str] = None) -> Dict[str, Any]:
        """
        处理角色锦衣信息，转换为中文可读格式
        
        Args:
            parsed_data: 解析后的数据
            character_name: 角色名称（可选）
            
        Returns:
            中文格式的锦衣信息
        """
        try:
            self.logger.info(f"开始解析角色 {character_name or '未知'} 的锦衣信息")
            
            # 从parsed_data中获取ExAvt信息
            clothes_data = parsed_data.get('ExAvt', {})
            if not clothes_data:
                self.logger.warning("未找到锦衣数据")
                return self._empty_clothes_info()
            
            # 获取其他相关信息
            basic_info = parsed_data.get('basic_info', {})
            total_avatar = basic_info.get('total_avatar', 0)
            
            # 获取特效信息
            chat_effect = parsed_data.get('chat_effect')
            icon_effect = parsed_data.get('icon_effect') 
            title_effect = parsed_data.get('title_effect')
            perform_effect = parsed_data.get('perform_effect')
            achieve_show = parsed_data.get('achieve_show', [])
            
            # 获取挂件信息
            avt_widget = parsed_data.get('avt_widget', {})
            
            # 格式化锦衣数据
            formatted_result = self._format_clothes_data(
                clothes_data, total_avatar, chat_effect, icon_effect, 
                title_effect, perform_effect, achieve_show, avt_widget
            )
            
            return formatted_result
            
        except Exception as e:
            self.logger.error(f"处理角色锦衣信息失败: {e}", exc_info=True)
            return self._empty_clothes_info()
    
    def _format_clothes_data(self, clothes_data: Dict[str, Any], total_avatar: int = 0,
                           chat_effect=None, icon_effect=None, title_effect=None, 
                           perform_effect=None, achieve_show=None, avt_widget=None) -> Dict[str, Any]:
        """
        格式化锦衣数据为中文可读格式，参照web版parse_clothes_info实现
        
        Args:
            clothes_data: 锦衣数据字典
            total_avatar: 总数
            chat_effect: 冒泡框
            icon_effect: 头像框
            title_effect: 称谓特效
            perform_effect: 施法/攻击特效
            achieve_show: 彩饰-队标
            avt_widget: 挂件信息
            
        Returns:
            格式化后的锦衣信息
        """
        try:
            config = self.load_clothes_config()
            clothes_info = config.get('clothes_info', {})
            clothes_type_conf = config.get('clothes_type_conf', [])
            widget_info = config.get('widget_info_for_display', {})
            
            old_clothes_list = []
            itype_list = []
            new_clothes_map = {}
            
            # 处理每个锦衣
            for pos, clothes_item in clothes_data.items():
                if not isinstance(clothes_item, dict):
                    continue
                
                itype = clothes_item.get('iType')
                if not itype:
                    continue
                
                # 获取锦衣名称
                clothes_name = clothes_item.get('cName') or clothes_info.get(str(itype), f"锦衣{itype}")
                
                # 构建锦衣信息
                info = {
                    "type": itype,
                    "name": clothes_name,
                    "order": clothes_item.get('order', 0),
                    "static_desc": ""
                }
                
                itype_list.append(itype)
                
                # 根据extra_info分类
                if 'extra_info' in clothes_item:
                    extra_id = clothes_item['extra_info']
                    if extra_id in new_clothes_map:
                        new_clothes_map[extra_id].append(info)
                    else:
                        new_clothes_map[extra_id] = [info]
                else:
                    old_clothes_list.append(info)
            
            # 构建锦衣
            new_clothes_list = []
            if new_clothes_map:
                for type_conf in clothes_type_conf:
                    type_id = type_conf.get('id')
                    type_name = type_conf.get('name', f"类型{type_id}")
                    
                    clothes_list = new_clothes_map.get(type_id, [])
                    new_clothes_list.append({
                        "id": type_id,
                        "title": type_name,
                        "list": self._sort_clothes_list(clothes_list)
                    })
            
            # 处理挂件信息
            if avt_widget:
                widget_list = []
                for key in avt_widget:
                    if str(key) in widget_info:
                        widget_list.append({
                            "name": widget_info[str(key)]
                        })
                
                if widget_list:
                    widget_map = {
                        "title": "挂件",
                        "list": widget_list
                    }
                    
                    # 插入到合适位置
                    if new_clothes_list:
                        # 找到"限量"类型后插入
                        insert_index = 0
                        for i, item in enumerate(new_clothes_list):
                            if item.get("title") == "限量":
                                insert_index = i + 1
                                break
                        new_clothes_list.insert(insert_index, widget_map)
                    else:
                        new_clothes_list = [widget_map]
            
            # 构建返回结果
            result = {
                "总数": total_avatar or len(clothes_data),
                "锦衣数量": len(clothes_data)
            }
            
            # 根据是否有title_effect决定返回格式
            if title_effect:
                # 简化锦衣信息：只保留name
                simplified_clothes_list = {}
                for clothes_type in new_clothes_list:
                    simplified_clothes_list[clothes_type.get("title")] = [item.get("name", "") for item in clothes_type.get("list", [])]
                
                result["锦衣"] = simplified_clothes_list
                # 特效字段只保留name
                result["冒泡框"] = self._extract_name_only(chat_effect)
                result["头像框"] = self._extract_name_only(icon_effect)
                result["称谓特效"] = self._extract_name_only(title_effect)
                result["施法/攻击特效"] = self._extract_name_only(perform_effect)
                
                # 处理彩饰-队标（只保留client_type=201的name）
                filtered_achieve = []
                if achieve_show:
                    for item in achieve_show:
                        if isinstance(item, dict) and item.get('client_type') == 201:
                            name = self._extract_name_only(item)
                            if name:
                                filtered_achieve.append(name)
                result["彩饰-队标"] = filtered_achieve
            else:
                # 简化锦衣信息：只保留name
                result["锦衣列表"] = [item.get("name", "") for item in self._sort_clothes_list(old_clothes_list)]
            
            return result
            
        except Exception as e:
            self.logger.error(f"格式化锦衣数据失败: {e}")
            return self._empty_clothes_info()
    
    def _sort_clothes_list(self, clothes_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """对锦衣列表进行排序"""
        def sort_func(a, b):
            a_order = a.get('order', 0)
            b_order = b.get('order', 0)
            a_type = a.get('type', 0)
            b_type = b.get('type', 0)
            
            if a_order and b_order:
                return a_order - b_order
            else:
                return a_type - b_type
        
        # Python版本的排序
        return sorted(clothes_list, key=lambda x: (x.get('order', 0) or x.get('type', 0)))
    
    def _extract_name_only(self, data: Any) -> Any:
        """提取数据中的name字段，简化复杂结构"""
        if data is None:
            return None
        elif isinstance(data, str):
            return data
        elif isinstance(data, dict):
            return data.get('name', data.get('cName', ''))
        elif isinstance(data, list):
            return [self._extract_name_only(item) for item in data]
        else:
            return data
    
    def _empty_clothes_info(self):
        """返回空的锦衣信息结构"""
        return {
            "总数": 0,
            "锦衣数量": 0,
            "锦衣列表": []
        }
    
    @lru_cache(maxsize=1)
    def load_clothes_config(self) -> Dict[str, Any]:
        """从ConfigLoader加载锦衣配置信息"""
        if self._clothes_config:
            return self._clothes_config
            
        if not self.config_loader:
            raise RuntimeError("ConfigLoader不可用")
            
        try:
            self._clothes_config = self.config_loader.get_clothes_config()
            self.logger.debug(f"加载锦衣配置: {len(self._clothes_config)}个配置块")
        except Exception as e:
            self.logger.error(f"加载锦衣配置失败: {e}")
            raise e
            
        return self._clothes_config
