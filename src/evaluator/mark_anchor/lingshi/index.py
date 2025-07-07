import importlib.util
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl import Workbook
import warnings
from datetime import datetime
import json
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import numpy as np
import sys
import os
from abc import ABC, abstractmethod

# 添加项目根目录到Python路径，解决模块导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(current_dir))))  # 向上四级到项目根目录
sys.path.insert(0, project_root)

# 直接导入同目录下的模块
current_dir = os.path.dirname(os.path.abspath(__file__))
collector_path = os.path.join(current_dir, 'lingshi_market_data_collector.py')

spec = importlib.util.spec_from_file_location(
    "lingshi_market_data_collector", collector_path)
collector_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector_module)
LingshiMarketDataCollector = collector_module.LingshiMarketDataCollector

warnings.filterwarnings('ignore')


class BaseLingshiConfig:
    """基础灵饰配置类 - 提供默认的配置"""
    
    def __init__(self):
        # 灵饰类型分类
        self.lingshi_categories = {
            # 戒指类
            'rings': {
                'name': '戒指',
                'kindids': [61],
                'description': '戒指类灵饰'
            },
            # 耳饰类  
            'earrings': {
                'name': '耳饰',
                'kindids': [62],
                'description': '耳饰类灵饰'
            },
            # 手镯类
            'bracelets': {
                'name': '手镯',
                'kindids': [63],
                'description': '手镯类灵饰'
            },
            # 佩饰类
            'pendants': {
                'name': '佩饰',
                'kindids': [64],
                'description': '佩饰类灵饰'
            }
        }
        
        # 基础特征权重配置
        self.base_feature_weights = {
            # 默认都有的特征
            'equip_level': 1.0,          # 装备等级很重要
            'gem_score': 3.0,            # 宝石得分非常重要
            'suit_effect_type': 2.0,     # 套装效果类型权重较高
            'suit_effect_level': 2.0,    # 套装效果等级权重较高
            'is_super_simple': 5.0,      # 超级简易非常重要
            'repair_fail_num': 1.0,      # 修理失败次数

            # 主基础属性特征
            'damage': 0,                 # 伤害
            'defense': 0,                # 防御
            'magic_damage': 0,           # 法术伤害
            'magic_defense': 0,          # 法术防御
            'seal_hit': 0,               # 封印命中等级
            'seal_resist': 0,            # 抵抗封印等级
            'speed': 0,                  # 速度

            # 附加属性特征
            'attr_type': 0,              # 附加属性类型
            'attr_value': 0,             # 附加属性值
        }

        
        # 基础相对容忍度配置
        self.base_relative_tolerances = {
            # 相对容忍度
            'equip_level': 0.25,         # 装备等级容忍度25%
            'gem_score': 0.25,           # 宝石得分容忍度25%
            'suit_effect_type': 0.0,     # 套装效果类型必须完全一致
            'suit_effect_level': 0.2,    # 套装效果等级容忍度20%
            'is_super_simple': 0.0,      # 超级简易必须完全一致
            'repair_fail_num': 0.0,      # 修理失败次数必须完全一致
            
            # 主基础属性特征
            'damage': 0.3,               # 伤害容忍度30%
            'defense': 0.3,              # 防御容忍度30%
            'magic_damage': 0.3,         # 法术伤害容忍度30%
            'magic_defense': 0.3,        # 法术防御容忍度30%
            'seal_hit': 0.3,             # 封印命中等级容忍度30%
            'seal_resist': 0.3,          # 抵抗封印等级容忍度30%
            'speed': 0.3,                # 速度容忍度30%

            # 附加属性特征
            'attr_type': 0.0,            # 附加属性类型必须完全一致
            'attr_value': 0.3,           # 附加属性值容忍度30%
        }
    
    def get_lingshi_category(self, kindid: int) -> str:
        """根据kindid获取灵饰类别"""
        for category, config in self.lingshi_categories.items():
            if kindid in config['kindids']:
                return category
        return 'rings'  # 默认返回戒指类


class LingshiTypePlugin(ABC):
    """灵饰类型插件基类"""
    
    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """插件名称"""
        pass
    
    @property
    @abstractmethod
    def supported_kindids(self) -> List[int]:
        """支持的灵饰类型ID列表"""
        pass
    
    @property
    @abstractmethod
    def priority(self) -> int:
        """插件优先级，数字越大优先级越高"""
        pass
    
    def get_derived_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算派生特征
        
        Args:
            features: 原始特征字典
            
        Returns:
            Dict[str, Any]: 派生特征字典
        """
        return {}
    
    def get_weight_overrides(self) -> Dict[str, float]:
        """
        获取权重覆盖配置
        
        Returns:
            Dict[str, float]: 要覆盖的权重配置
        """
        return {}
    
    def get_weight_increments(self) -> Dict[str, float]:
        """
        获取权重增量配置
        
        Returns:
            Dict[str, float]: 要增加的权重配置
        """
        return {}
    
    def get_tolerance_overrides(self) -> Dict[str, float]:
        """
        获取容忍度覆盖配置
        
        Returns:
            Dict[str, float]: 要覆盖的容忍度配置
        """
        return {}
    
    def get_tolerance_increments(self) -> Dict[str, float]:
        """
        获取容忍度增量配置
        
        Returns:
            Dict[str, float]: 要增加的容忍度配置
        """
        return {}
    
    def calculate_custom_similarity(self, 
                                   feature_name: str,
                                   target_val: Any, 
                                   market_val: Any) -> Optional[float]:
        """
        计算自定义相似度
        
        Args:
            feature_name: 特征名称
            target_val: 目标值
            market_val: 市场值
            
        Returns:
            Optional[float]: 相似度值，如果返回None则使用默认计算
        """
        return None


class LingshiPluginManager:
    """灵饰插件管理器"""
    
    def __init__(self, base_config: BaseLingshiConfig):
        self.base_config = base_config
        self.plugins: List[LingshiTypePlugin] = []
    
    def register_plugin(self, plugin: LingshiTypePlugin):
        """注册插件"""
        self.plugins.append(plugin)
        # 按优先级排序
        self.plugins.sort(key=lambda p: p.priority, reverse=True)
    
    def get_plugins_for_kindid(self, kindid: int) -> List[LingshiTypePlugin]:
        """获取指定kindid的插件列表"""
        return [p for p in self.plugins if kindid in p.supported_kindids]
    
    def get_enhanced_features(self, kindid: int, base_features: Dict[str, Any]) -> Dict[str, Any]:
        """获取增强特征"""
        enhanced_features = base_features.copy()
        
        for plugin in self.get_plugins_for_kindid(kindid):
            derived_features = plugin.get_derived_features(base_features)
            enhanced_features.update(derived_features)
        
        return enhanced_features
    
    def get_final_weights(self, kindid: int) -> Dict[str, float]:
        """获取最终权重配置"""
        weights = self.base_config.base_feature_weights.copy()
        
        for plugin in self.get_plugins_for_kindid(kindid):
            # 应用权重覆盖
            overrides = plugin.get_weight_overrides()
            weights.update(overrides)
            
            # 应用权重增量
            increments = plugin.get_weight_increments()
            for key, increment in increments.items():
                if key in weights:
                    weights[key] += increment
        
        return weights
    
    def get_final_tolerances(self, kindid: int) -> Dict[str, float]:
        """获取最终容忍度配置"""
        tolerances = self.base_config.base_relative_tolerances.copy()
        
        for plugin in self.get_plugins_for_kindid(kindid):
            # 应用容忍度覆盖
            overrides = plugin.get_tolerance_overrides()
            tolerances.update(overrides)
            
            # 应用容忍度增量
            increments = plugin.get_tolerance_increments()
            for key, increment in increments.items():
                if key in tolerances:
                    tolerances[key] += increment
        
        return tolerances
    
    def calculate_plugin_similarity(self, 
                                   kindid: int,
                                   feature_name: str,
                                   target_val: Any, 
                                   market_val: Any) -> Optional[float]:
        """计算插件自定义相似度"""
        for plugin in self.get_plugins_for_kindid(kindid):
            similarity = plugin.calculate_custom_similarity(feature_name, target_val, market_val)
            if similarity is not None:
                return similarity
        return None


class LingshiAnchorEvaluator:
    """灵饰锚定评估器"""

    def __init__(self, market_data_collector: Optional[LingshiMarketDataCollector] = None):
        """
        初始化灵饰锚定评估器
        
        Args:
            market_data_collector: 市场数据采集器，如果为None则自动创建
        """
        self.market_data_collector = market_data_collector or LingshiMarketDataCollector()
        self.base_config = BaseLingshiConfig()
        self.plugin_manager = LingshiPluginManager(self.base_config)
        self.logger = logging.getLogger(__name__)

    def add_plugin(self, plugin: LingshiTypePlugin):
        """添加插件"""
        self.plugin_manager.register_plugin(plugin)

    def get_lingshi_type_configs(self, kindid: int) -> Tuple[Dict[str, float], Dict[str, float]]:
        """获取灵饰类型配置"""
        weights = self.plugin_manager.get_final_weights(kindid)
        tolerances = self.plugin_manager.get_final_tolerances(kindid)
        return weights, tolerances

    def find_market_anchors(self,
                            target_features: Dict[str, Any],
                            similarity_threshold: float = 0.7,
                            max_anchors: int = 30) -> List[Dict[str, Any]]:
        """
        查找市场锚点
        
        Args:
            target_features: 目标灵饰特征
            similarity_threshold: 相似度阈值
            max_anchors: 最大锚点数量
            
        Returns:
            List[Dict[str, Any]]: 锚点列表
        """
        try:
            # 获取市场数据
            market_data = self.market_data_collector.get_market_data_with_business_rules(target_features)
            
            if market_data.empty:
                self.logger.warning("未找到市场数据")
                return []
            
            # 获取配置
            kindid = target_features.get('kindid')
            weights, tolerances = self.get_lingshi_type_configs(kindid)
            
            # 计算相似度
            similarities = []
            for _, market_row in market_data.iterrows():
                similarity = self._calculate_similarity(target_features, market_row.to_dict(), weights, tolerances)
                if similarity >= similarity_threshold:
                    similarities.append({
                        'id': market_row['id'],
                        'similarity': similarity,
                        'price': market_row['price'],
                        'server': market_row.get('server', ''),
                        'features': market_row.to_dict()
                    })
            
            # 按相似度排序并限制数量
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:max_anchors]
            
        except Exception as e:
            self.logger.error(f"查找市场锚点失败: {e}")
            return []

    def _calculate_similarity(self,
                              target_features: Dict[str, Any],
                              market_features: Dict[str, Any],
                              weights: Dict[str, float],
                              tolerances: Dict[str, float]) -> float:
        """
        计算相似度
        
        Args:
            target_features: 目标特征
            market_features: 市场特征
            weights: 权重配置
            tolerances: 容忍度配置
            
        Returns:
            float: 相似度值
        """
        total_weight = 0
        weighted_similarity = 0
        
        for feature_name, weight in weights.items():
            if weight <= 0:
                continue
                
            target_val = target_features.get(feature_name)
            market_val = market_features.get(feature_name)
            
            if target_val is None or market_val is None:
                continue
            
            # 尝试使用插件自定义相似度计算
            kindid = target_features.get('kindid')
            custom_similarity = self.plugin_manager.calculate_plugin_similarity(
                kindid, feature_name, target_val, market_val)
            
            if custom_similarity is not None:
                similarity = custom_similarity
            else:
                # 使用默认相似度计算
                similarity = self._calculate_default_similarity(
                    feature_name, target_val, market_val, tolerances.get(feature_name, 0.3))
            
            weighted_similarity += similarity * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_similarity / total_weight

    def _calculate_default_similarity(self,
                                      feature_name: str,
                                      target_val: Any,
                                      market_val: Any,
                                      tolerance: float) -> float:
        """
        计算默认相似度
        
        Args:
            feature_name: 特征名称
            target_val: 目标值
            market_val: 市场值
            tolerance: 容忍度
            
        Returns:
            float: 相似度值
        """
        # 处理不同类型的特征
        if isinstance(target_val, (int, float)) and isinstance(market_val, (int, float)):
            if target_val == 0 and market_val == 0:
                return 1.0
            elif target_val == 0 or market_val == 0:
                return 0.0
            
            # 数值型特征使用相对差异
            diff = abs(target_val - market_val) / max(abs(target_val), abs(market_val))
            return max(0, 1 - diff / tolerance)
        
        elif isinstance(target_val, list) and isinstance(market_val, list):
            # 列表型特征（如attr_type, attr_value）
            if len(target_val) != len(market_val):
                return 0.0
            
            if len(target_val) == 0:
                return 1.0
            
            # 计算列表相似度
            similarities = []
            for t_val, m_val in zip(target_val, market_val):
                if isinstance(t_val, (int, float)) and isinstance(m_val, (int, float)):
                    if t_val == 0 and m_val == 0:
                        similarities.append(1.0)
                    elif t_val == 0 or m_val == 0:
                        similarities.append(0.0)
                    else:
                        diff = abs(t_val - m_val) / max(abs(t_val), abs(m_val))
                        similarities.append(max(0, 1 - diff / tolerance))
                else:
                    # 字符串或其他类型，使用精确匹配
                    similarities.append(1.0 if t_val == m_val else 0.0)
            
            return sum(similarities) / len(similarities)
        
        else:
            # 其他类型使用精确匹配
            return 1.0 if target_val == market_val else 0.0

    def calculate_value(self,
                        target_features: Dict[str, Any],
                        strategy: str = 'fair_value',
                        similarity_threshold: float = 0.7,
                        max_anchors: int = 30) -> Dict[str, Any]:
        """
        计算灵饰价值
        
        Args:
            target_features: 目标灵饰特征
            strategy: 计算策略 ('fair_value', 'min_value', 'max_value')
            similarity_threshold: 相似度阈值
            max_anchors: 最大锚点数量
            
        Returns:
            Dict[str, Any]: 价值计算结果
        """
        try:
            # 查找锚点
            anchors = self.find_market_anchors(target_features, similarity_threshold, max_anchors)
            
            if not anchors:
                return {
                    'success': False,
                    'message': '未找到相似的市场锚点',
                    'value': 0,
                    'confidence': 0,
                    'anchor_count': 0
                }
            
            # 提取价格
            prices = [anchor['price'] for anchor in anchors]
            similarities = [anchor['similarity'] for anchor in anchors]
            
            # 根据策略计算价值
            if strategy == 'fair_value':
                value = self._weighted_median(prices, similarities)
            elif strategy == 'min_value':
                value = min(prices)
            elif strategy == 'max_value':
                value = max(prices)
            else:
                value = self._weighted_median(prices, similarities)
            
            # 计算置信度
            confidence = self._calculate_confidence(anchors, len(anchors))
            
            return {
                'success': True,
                'value': round(value, 2),
                'confidence': round(confidence, 3),
                'anchor_count': len(anchors),
                'strategy': strategy,
                'anchors': anchors[:10]  # 只返回前10个锚点
            }
            
        except Exception as e:
            self.logger.error(f"计算灵饰价值失败: {e}")
            return {
                'success': False,
                'message': f'计算失败: {str(e)}',
                'value': 0,
                'confidence': 0,
                'anchor_count': 0
            }

    def _weighted_median(self, values: List[float], weights: List[float]) -> float:
        """计算加权中位数"""
        if not values:
            return 0.0
        
        # 创建值-权重对并排序
        pairs = list(zip(values, weights))
        pairs.sort(key=lambda x: x[0])
        
        # 计算总权重
        total_weight = sum(weights)
        if total_weight == 0:
            return values[len(values) // 2] if values else 0.0
        
        # 找到中位数位置
        target_weight = total_weight / 2
        current_weight = 0
        
        for value, weight in pairs:
            current_weight += weight
            if current_weight >= target_weight:
                return value
        
        return pairs[-1][0] if pairs else 0.0

    def _calculate_confidence(self, anchors: List[Dict[str, Any]], anchor_count: int) -> float:
        """计算置信度"""
        if not anchors:
            return 0.0
        
        # 基于锚点数量和相似度的置信度计算
        avg_similarity = sum(anchor['similarity'] for anchor in anchors) / len(anchors)
        
        # 锚点数量因子
        count_factor = min(anchor_count / 10, 1.0)  # 10个锚点为满分
        
        # 相似度因子
        similarity_factor = avg_similarity
        
        # 综合置信度
        confidence = (count_factor * 0.4 + similarity_factor * 0.6)
        
        return min(confidence, 1.0)

    def batch_valuation(self,
                        lingshi_list: List[Dict[str, Any]],
                        strategy: str = 'fair_value') -> List[Dict[str, Any]]:
        """
        批量估价
        
        Args:
            lingshi_list: 灵饰列表
            strategy: 计算策略
            
        Returns:
            List[Dict[str, Any]]: 估价结果列表
        """
        results = []
        
        for lingshi_data in lingshi_list:
            try:
                # 提取特征
                features = self.market_data_collector.feature_extractor.extract_features(lingshi_data)
                features.update(lingshi_data)  # 合并原始数据
                
                # 计算价值
                result = self.calculate_value(features, strategy)
                result['id'] = lingshi_data.get('id', 'unknown')
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"批量估价失败: {e}")
                results.append({
                    'success': False,
                    'message': f'估价失败: {str(e)}',
                    'value': 0,
                    'confidence': 0,
                    'anchor_count': 0,
                    'id': lingshi_data.get('id', 'unknown')
                })
        
        return results