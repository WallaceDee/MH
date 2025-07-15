import sys
import os

# 添加项目根目录到Python路径，解决模块导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # 向上两级到项目根目录
sys.path.insert(0, project_root)

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import json
from datetime import datetime
import warnings
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows

try:
    from .pet_market_data_collector import PetMarketDataCollector
except ImportError:
    from pet_market_data_collector import PetMarketDataCollector

warnings.filterwarnings('ignore')


class PetMarketAnchorEvaluator:
    """市场锚定估价器 - 基于市场相似召唤兽的价格锚定估价"""
    
    def __init__(self, market_data_collector: Optional[PetMarketDataCollector] = None):
        """
        初始化市场锚定估价器
        
        Args:
            market_data_collector: 市场数据采集器实例，如果为None则创建新实例
        """
        self.logger = logging.getLogger(__name__)
        
        # 初始化市场数据采集器
        if market_data_collector is None:
            self.market_collector = PetMarketDataCollector()
        else:
            self.market_collector = market_data_collector
        
        
        # 相对容忍度：用于大数值特征（如经验、金钱等）
        self.relative_tolerances = {
            "role_grade_limit":1
        }
        
        # 定义关键特征权重（用于相似度计算）
        self.feature_weights = {
         "role_grade_limit":1
        }
        
        print("市场锚定估价器初始化完成")
    
    def find_market_anchors(self, 
                           target_features: Dict[str, Any],
                           similarity_threshold: float = 0.7,
                           max_anchors: int = 30) -> List[Dict[str, Any]]:
        """
        寻找市场锚点召唤兽
        
        Args:
            target_features: 目标召唤兽特征字典
            similarity_threshold: 相似度阈值（0-1）
            max_anchors: 最大锚点数量
            
        Returns:
            List[Dict[str, Any]]: 锚点召唤兽列表，每个元素包含：
                - similarity: 相似度分数
                - price: 价格
                - equip_id: 装备ID
                - features: 完整特征数据
        """
        try:
            print(f"开始寻找市场锚点，相似度阈值: {similarity_threshold}")
            # 获取目标装备的equip_sn，用于排除自身
            target_equip_sn = target_features.get('equip_sn')
            if target_equip_sn:
                print(f"目标装备序列号: {target_equip_sn}，将排除自身")
                
            # 构建预过滤条件以提高效率
            pre_filters = self._build_pre_filters(target_features)
            
            # 获取预过滤的市场数据
            market_data = self.market_collector.get_market_data_for_similarity(pre_filters)
           
            if market_data.empty:
                print("市场数据为空，无法找到锚点")
                return []
            
            print(f"预过滤后获得 {len(market_data)} 条候选数据")
            
            
            # 计算所有市场召唤兽的相似度
            anchor_candidates = []
            error_count = 0
            excluded_self_count = 0
            
            for idx, market_row in market_data.iterrows():
                try:
                    # 获取当前市场装备的equip_sn
                    current_equip_sn = market_row.get('equip_sn', idx)

                    # 排除目标装备自身
                    if target_equip_sn and current_equip_sn == target_equip_sn:
                        excluded_self_count += 1
                        continue

                    # 计算相似度
                    similarity = self._calculate_similarity(target_features, market_row.to_dict())
                    print(f"相似度------------------: {similarity}{target_features}")
                    if similarity >= similarity_threshold:
                        anchor_candidates.append({
                            'equip_sn': current_equip_sn,
                            'similarity': similarity,
                            'price': market_row.get('price', 0),
                            'features': market_row.to_dict()
                        })
                        
                except Exception as e:
                    # 详细记录有问题的数据
                    market_dict = market_row.to_dict()
                    self.logger.error(f"处理召唤兽 {current_equip_sn} 时出错: {e}")
                    self.logger.error(f"问题数据内容: {market_dict}")
                    
                    error_count += 1
                    continue
            
            # 输出处理统计
            processed_count = len(market_data)
            success_count = processed_count - error_count - excluded_self_count
            if error_count > 0 or excluded_self_count > 0:
                self.logger.warning(f"数据处理统计: 总数={processed_count}, 成功={success_count}, 失败={error_count}, 排除自身={excluded_self_count}")
            
            # 按相似度排序
            anchor_candidates.sort(key=lambda x: x['similarity'], reverse=True)
            # 返回前N个锚点
            anchors = anchor_candidates[:max_anchors]
            
            print(f"找到 {len(anchors)} 个市场锚点召唤兽")
            if anchors:
                print(f"相似度范围: {anchors[-1]['similarity']:.3f} - {anchors[0]['similarity']:.3f}")
                print(f"价格范围: {min(a['price'] for a in anchors):.1f} - {max(a['price'] for a in anchors):.1f}")
            
            return anchors
            
        except Exception as e:
            self.logger.error(f"寻找市场锚点失败: {e}")
            return []
    
    def _build_pre_filters(self, target_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据目标特征构建预过滤条件，减少计算量
        
        Args:
            target_features: 目标召唤兽特征
            
        Returns:
            Dict[str, Any]: 过滤条件
        """
        filters = {}
        
        return filters

    def _calculate_similarity(self, 
                            target_features: Dict[str, Any], 
                            market_features: Dict[str, Any]) -> float:
        """
        计算两个召唤兽特征的相似度
        
        Args:
            target_features: 目标召唤兽特征
            market_features: 市场召唤兽特征
            
        Returns:
            float: 相似度分数（0-1）
        """
        try:
            # 输入验证
            if not isinstance(target_features, dict) or not isinstance(market_features, dict):
                self.logger.warning("特征数据格式错误，使用默认相似度")
                return 0.0
            
            total_weight = 0
            weighted_similarity = 0
            
            # 合并所有特征名称
            all_features = set(self.relative_tolerances.keys())
            
            for feature_name in all_features:
                if feature_name not in target_features and feature_name not in market_features:
                    continue
                    
                target_val = target_features.get(feature_name, 0)
                market_val = market_features.get(feature_name, 0)
                weight = self.feature_weights.get(feature_name, 0.5)
                
                # 计算特征相似度
                if target_val == 0 and market_val == 0:
                    # 两者都为0，完全匹配
                    feature_similarity = 1.0
     
                elif feature_name in self.relative_tolerances:
                    # 使用相对容忍度计算
                    tolerance = self.relative_tolerances[feature_name]
                    
                    if target_val == 0 or market_val == 0:
                        # 一个为0一个不为0，给予部分相似度
                        feature_similarity = 0.3
                    else:
                        # 计算相对差异
                        denominator = max(abs(target_val), abs(market_val))
                        diff_ratio = abs(target_val - market_val) / denominator
                        
                        if diff_ratio <= tolerance:
                            # 在容忍度内，相似度为1
                            feature_similarity = 1.0
                        elif diff_ratio <= tolerance * 2:
                            # 超出容忍度但在2倍范围内，线性递减
                            feature_similarity = max(0, 1.0 - (diff_ratio - tolerance) / max(tolerance, 0.1))
                        else:
                            # 差异太大，相似度为0
                            feature_similarity = 0.0
                else:
                    # 未配置的特征，使用默认逻辑
                    if target_val == market_val:
                        feature_similarity = 1.0
                    else:
                        feature_similarity = 0.5  # 给予中等相似度
                
                weighted_similarity += feature_similarity * weight
                total_weight += weight
            
            # 计算加权平均相似度
            if total_weight > 0:
                final_similarity = weighted_similarity / total_weight
            else:
                final_similarity = 0.0
            
            return final_similarity
            
        except Exception as e:
            self.logger.error(f"计算相似度失败: {e}")
            return 0.0
    
   
    def calculate_value(self, 
                       target_features: Dict[str, Any],
                       strategy: str = 'fair_value',
                       similarity_threshold: float = 0.7,
                       max_anchors: int = 30) -> Dict[str, Any]:
        """
        计算召唤兽价值
        
        Args:
            target_features: 目标召唤兽特征字典
            strategy: 定价策略 ('competitive', 'fair_value', 'premium')
            similarity_threshold: 相似度阈值（0-1）
            max_anchors: 最大锚点数量
            
        Returns:
            Dict[str, Any]: 估价结果，包含：
                - estimated_price: 估算价格
                - anchor_count: 锚点数量
                - price_range: 价格范围
                - confidence: 置信度
                - strategy_used: 使用的策略
                - fallback_used: 是否使用了保底估价
        """
        try:
            print(f"开始计算召唤兽价值，策略: {strategy}，相似度阈值: {similarity_threshold}，最大锚点数: {max_anchors}")
            
            # 寻找市场锚点
            anchors = self.find_market_anchors(target_features, similarity_threshold, max_anchors)
            
            if len(anchors) == 0:
                self.logger.error(f"未找到市场锚点")
                return {
                    'estimated_price': 0,
                    'anchor_count': 0,
                    'price_range': {
                        'min': 0,
                        'max': 0,
                        'mean': 0,
                        'median': 0
                    },
                    'confidence': 0,
                    'strategy_used': strategy,
                    'fallback_used': True,
                    'error': '未找到足够的相似召唤兽进行估价',
                    'anchors': []
                }
            
            # 提取锚点价格
            anchor_prices = [anchor['price'] for anchor in anchors]
            anchor_similarities = [anchor['similarity'] for anchor in anchors]
            
                        # 根据策略计算估价
            if strategy == 'competitive':
                # 竞争性定价：25%分位数 × 0.9
                estimated_price = float(np.percentile(anchor_prices, 25) * 0.9)
            elif strategy == 'premium':
                # 溢价定价：75%分位数 × 0.95 (下调系数，避免过度溢价)
                estimated_price = float(np.percentile(anchor_prices, 75) * 0.7)
            else:  # fair_value
                # 公允价值：相似度加权中位数 × 0.93 (稍微下调，更贴近成交价)
                base_price = self._weighted_median(anchor_prices, anchor_similarities)
                estimated_price = float(base_price * 0.7)

            # 计算置信度
            confidence = self._calculate_confidence(anchors, len(anchor_prices))

            # 构建结果
            result = {
                'estimated_price': round(estimated_price, 1),
                'anchor_count': len(anchors),
                'price_range': {
                    'min': float(min(anchor_prices)),
                    'max': float(max(anchor_prices)),
                    'mean': float(np.mean(anchor_prices)),
                    'median': float(np.median(anchor_prices))
                },
                'confidence': float(confidence),
                'strategy_used': strategy,
                'fallback_used': False,
                'anchors': anchors[:5]  # 返回前5个最相似的锚点用于展示
            }
            
            print(f"估价完成: {estimated_price:.1f}，基于 {len(anchors)} 个锚点，置信度: {confidence:.2f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"计算召唤兽价值失败: {e}")
    
    def _weighted_median(self, values: List[float], weights: List[float]) -> float:
        """
        计算加权中位数
        
        Args:
            values: 数值列表
            weights: 权重列表
            
        Returns:
            float: 加权中位数
        """
        if not values or not weights:
            return 0.0
        
        # 将数值和权重配对并排序
        paired = list(zip(values, weights))
        paired.sort(key=lambda x: x[0])
        
        # 计算累积权重
        total_weight = sum(weights)
        cumulative_weight = 0
        
        for value, weight in paired:
            cumulative_weight += weight
            if cumulative_weight >= total_weight * 0.5:
                return value
        
        return paired[-1][0]  # fallback
    
    def _calculate_confidence(self, anchors: List[Dict[str, Any]], anchor_count: int) -> float:
        """
        计算估价置信度
        
        Args:
            anchors: 锚点列表
            anchor_count: 锚点数量
            
        Returns:
            float: 置信度（0-1）
        """
        # 基础置信度基于锚点数量
        base_confidence = min(anchor_count / 20.0, 1.0)  # 20个锚点达到满分
        
        # 相似度加成
        if anchors:
            avg_similarity = float(np.mean([anchor['similarity'] for anchor in anchors]))
            similarity_bonus = avg_similarity * 0.3
        else:
            similarity_bonus = 0

        # 价格稳定性加成
        if len(anchors) >= 3:
            prices = [anchor['price'] for anchor in anchors]
            price_cv = float(np.std(prices) / np.mean(prices)) if np.mean(prices) > 0 else 1.0
            stability_bonus = max(0, (0.5 - price_cv) * 0.4)  # CV低于0.5时有加成
        else:
            stability_bonus = 0

        final_confidence = min(base_confidence + similarity_bonus + stability_bonus, 1.0)
        return float(final_confidence)
    
  
    
    def value_distribution_report(self, target_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成价值分布报告
        
        Args:
            target_features: 目标召唤兽特征字典
            
        Returns:
            Dict[str, Any]: 价值分布报告，包含：
                - min_price, max_price, median_price: 价格统计
                - percentile_25, percentile_75: 分位数
                - recommended_competitive, recommended_fair: 推荐价格
                - anchor_count: 锚点数量
                - price_distribution: 价格分布直方图数据
        """
        try:
            print("生成价值分布报告...")
            
            # 寻找锚点
            anchors = self.find_market_anchors(target_features, similarity_threshold=0.5, max_anchors=50)
            
            if len(anchors) == 0:
                return {
                    'error': '未找到足够的市场锚点',
                    'min_price': 0,
                    'max_price': 0,
                    'median_price': 0,
                    'anchor_count': 0
                }
            
            # 提取价格数据
            prices = [anchor['price'] for anchor in anchors]
            similarities = [anchor['similarity'] for anchor in anchors]
            
            # 计算统计量
            min_price = float(min(prices))
            max_price = float(max(prices))
            median_price = float(np.median(prices))
            percentile_25 = float(np.percentile(prices, 25))
            percentile_75 = float(np.percentile(prices, 75))
            
            # 计算推荐价格
            competitive_result = self.calculate_value(target_features, 'competitive', max_anchors=len(anchors))
            fair_result = self.calculate_value(target_features, 'fair_value', max_anchors=len(anchors))
            
            # 生成价格分布直方图数据
            hist_bins = 10
            hist_counts, hist_edges = np.histogram(prices, bins=hist_bins)
            
            # 构建报告
            report = {
                'min_price': min_price,
                'max_price': max_price,
                'median_price': median_price,
                'percentile_25': percentile_25,
                'percentile_75': percentile_75,
                'recommended_competitive': competitive_result['estimated_price'],
                'recommended_fair': fair_result['estimated_price'],
                'anchor_count': len(anchors),
                'price_distribution': {
                    'bins': [float(edge) for edge in hist_edges],
                    'counts': [int(count) for count in hist_counts]
                },
                'anchor_details': [
                    {
                        'equip_id': anchor['equip_id'],
                        'price': float(anchor['price']),
                        'similarity': round(float(anchor['similarity']), 3),
                        'level': int(anchor['features'].get('level', 0)),
                        'cultivation': int(anchor['features'].get('total_cultivation', 0))
                    }
                    for anchor in anchors[:10]  # 返回前10个详细信息
                ]
            }
            
            print(f"价值分布报告生成完成，基于 {len(anchors)} 个锚点")
            
            return report
            
        except Exception as e:
            self.logger.error(f"生成价值分布报告失败: {e}")
            return {'error': str(e)}
    
    def batch_valuation(self, 
                       character_list: List[Dict[str, Any]],
                       strategy: str = 'fair_value') -> List[Dict[str, Any]]:
        """
        批量估价
        
        Args:
            character_list: 召唤兽特征列表
            strategy: 定价策略
            
        Returns:
            List[Dict[str, Any]]: 批量估价结果列表
        """
        results = []
        
        print(f"开始批量估价，共 {len(character_list)} 个召唤兽")
        
        for i, character_features in enumerate(character_list):
            try:
                result = self.calculate_value(character_features, strategy)
                result['character_index'] = i
                results.append(result)
                
                if (i + 1) % 10 == 0:
                    print(f"已完成 {i + 1}/{len(character_list)} 个召唤兽的估价")
                    
            except Exception as e:
                self.logger.error(f"批量估价第 {i+1} 个召唤兽失败: {e}")
                results.append({
                    'character_index': i,
                    'estimated_price': 0,
                    'error': str(e)
                })
        
        print(f"批量估价完成，成功估价 {len([r for r in results if 'error' not in r])} 个召唤兽")
        
        return results
 