"""
通用估价基类

提供所有估价类可以共用的核心方法
"""

import numpy as np
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


class BaseValuator(ABC):
    """通用估价基类 - 提供所有估价类可以共用的核心方法"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 初始化极端值过滤工具
        from .extreme_value_filter import ExtremeValueFilter
        self.extreme_value_filter = ExtremeValueFilter()
    
    print
    @abstractmethod
    def find_market_anchors(self,
                           target_features: Dict[str, Any],
                           similarity_threshold: float = 0.7,
                           max_anchors: int = 30,
                           verbose: bool = True) -> List[Dict[str, Any]]:
        """
        寻找市场锚点（抽象方法）
        
        Args:
            target_features: 目标特征字典
            similarity_threshold: 相似度阈值
            max_anchors: 最大锚点数
            verbose: 是否显示详细调试日志（单个估价默认开启）
            
        Returns:
            List[Dict[str, Any]]: 锚点列表
        """
        pass
    
    def calculate_value(self,
                       target_features: Dict[str, Any],
                       strategy: str = 'fair_value',
                       similarity_threshold: float = 0.7,
                       max_anchors: int = 30,
                       verbose: bool = True) -> Dict[str, Any]:
        """
        计算价值（通用方法）
        
        Args:
            target_features: 目标特征字典
            strategy: 定价策略 ('fair_value', 'competitive', 'premium')
            similarity_threshold: 相似度阈值
            max_anchors: 最大锚点数
            verbose: 是否显示详细调试日志（单个估价默认开启）
            
        Returns:
            Dict[str, Any]: 估价结果
        """
        try:
            # 首先检测物品是否无效
            from .invalid_item_detector import InvalidItemDetector
            invalid_detector = InvalidItemDetector()
            
            should_skip, skip_reason, skip_value = invalid_detector.should_skip_valuation(target_features)
            if should_skip:
                if verbose:
                    print(f"物品无效，跳过估价: {skip_reason}")
                return {
                    'estimated_price': skip_value,
                    'anchor_count': 0,
                    'invalid_item': True,
                    'skip_reason': skip_reason,
                    'confidence': 1 if skip_value > 0 else 0,
                    'kindid': target_features.get('kindid', ''), 
                    'equip_sn': target_features.get('equip_sn', '')  # 添加装备序列号
                }
            
            # 寻找市场锚点
            anchors = self.find_market_anchors(
                target_features, similarity_threshold, max_anchors, verbose=verbose)
            
            if len(anchors) == 0:
                return {
                    'estimated_price': 0,
                    'anchor_count': 0,
                    'error': '未找到相似的市场锚点',
                    'kindid': target_features.get('kindid', ''), 
                    'equip_sn': target_features.get('equip_sn', '')  # 添加装备序列号
                }
            
            # 提取价格和相似度
            anchor_prices = [anchor['price'] for anchor in anchors]
            anchor_similarities = [anchor['similarity'] for anchor in anchors]
            
            # 根据策略计算估价
            if strategy == 'competitive':
                # 竞争性定价：25%分位数 × 0.9
                sorted_prices = sorted(anchor_prices)
                percentile_25_index = int(len(sorted_prices) * 0.25)
                percentile_25_value = sorted_prices[percentile_25_index] if percentile_25_index < len(sorted_prices) else sorted_prices[-1]
                estimated_price = float(percentile_25_value * 0.9)
            elif strategy == 'premium':
                # 溢价定价：75%分位数 × 0.95
                sorted_prices = sorted(anchor_prices)
                percentile_75_index = int(len(sorted_prices) * 0.75)
                percentile_75_value = sorted_prices[percentile_75_index] if percentile_75_index < len(sorted_prices) else sorted_prices[-1]
                estimated_price = float(percentile_75_value * 0.95)
            else:  # fair_value
                # 公允价值：相似度加权中位数 × 0.93
                base_price = self._weighted_median(anchor_prices, anchor_similarities)
                estimated_price = float(base_price * 0.93)
            
            # 计算置信度
            confidence = self._calculate_confidence(anchors, len(anchor_prices))
            
            # 构建结果 - 确保所有数值都是Python原生类型
            result = {
                'estimated_price': round(estimated_price, 1),
                'anchor_count': len(anchors),
                'price_range': {
                    'min': float(min(anchor_prices)),
                    'max': float(max(anchor_prices)),
                    'mean': float(sum(anchor_prices) / len(anchor_prices)),
                    'median': float(sorted(anchor_prices)[len(anchor_prices) // 2])
                },
                'confidence': float(confidence),
                'strategy_used': strategy,
                'invalid_item': False,
                'kindid': target_features.get('kindid', ''), 
                'equip_sn': target_features.get('equip_sn', '')  # 添加装备序列号
            }
            
            if verbose:
                print(f"价值计算完成: {estimated_price:.1f}，基于 {len(anchors)} 个锚点，置信度: {confidence:.2f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"计算价值失败: {e}")
            return {
                'estimated_price': 0,
                'anchor_count': 0,
                'error': str(e),
                'invalid_item': False,
                'kindid': target_features.get('kindid', ''), 
                'equip_sn': target_features.get('equip_sn', '')  # 添加装备序列号
            }
    
    def _weighted_median(self, values: List[float], weights: List[float]) -> float:
        """
        计算加权中位数（通用方法）
        
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
                return float(value)
        
        return float(paired[-1][0])  # fallback
    
    def _calculate_confidence(self, anchors: List[Dict[str, Any]], anchor_count: int) -> float:
        """
        计算估价置信度（通用方法）
        
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
            similarities = [anchor['similarity'] for anchor in anchors]
            avg_similarity = float(sum(similarities) / len(similarities))  # 使用原生Python计算平均值
            similarity_bonus = avg_similarity * 0.3
        else:
            similarity_bonus = 0
        
        # 价格稳定性加成
        if len(anchors) >= 3:
            prices = [anchor['price'] for anchor in anchors]
            mean_price = float(sum(prices) / len(prices))  # 使用原生Python计算平均值
            if mean_price > 0:
                # 计算标准差
                variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
                std_price = float(variance ** 0.5)
                price_cv = float(std_price / mean_price)
            else:
                price_cv = 1.0
            stability_bonus = max(0, (0.5 - price_cv) * 0.4)  # CV低于0.5时有加成
        else:
            stability_bonus = 0
        
        final_confidence = min(base_confidence + similarity_bonus + stability_bonus, 1.0)
        return float(final_confidence)
    
    def batch_valuation(self,
                       item_list: List[Dict[str, Any]],
                       strategy: str = 'fair_value',
                       similarity_threshold: float = 0.7,
                       max_anchors: int = 30,
                       verbose: bool = False) -> List[Dict[str, Any]]:
        """
        批量估价（通用方法）
        
        Args:
            item_list: 项目特征列表
            strategy: 定价策略
            similarity_threshold: 相似度阈值
            max_anchors: 最大锚点数
            verbose: 是否显示详细调试日志（批量估价默认关闭）
            
        Returns:
            List[Dict[str, Any]]: 批量估价结果列表
        """
        results = []
        
        if verbose:
            print(f"开始批量估价，共 {len(item_list)} 个项目")
        
        for i, item_features in enumerate(item_list):
            try:
                # 将verbose参数传递给calculate_value方法
                result = self.calculate_value(
                    item_features, strategy,
                    similarity_threshold=similarity_threshold,
                    max_anchors=max_anchors,
                    verbose=verbose
                )
                result['item_index'] = i
                results.append(result)
                
                if verbose and (i + 1) % 10 == 0:
                    print(f"已完成 {i + 1}/{len(item_list)} 个项目的估价")
                    
            except Exception as e:
                self.logger.error(f"批量估价第 {i+1} 个项目失败: {e}")
                results.append({
                    'item_index': i,
                    'estimated_price': 0,
                    'error': str(e),
                    'kindid': item_features.get('kindid', 0),
                    'equip_sn': item_features.get('equip_sn', '')  # 添加装备序列号
                })
        
        if verbose:
            print(f"批量估价完成，成功估价 {len([r for r in results if 'error' not in r])} 个项目")
        
        return results
    
    def value_distribution_report(self, target_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成价值分布报告（通用方法）
        
        Args:
            target_features: 目标特征字典
            
        Returns:
            Dict[str, Any]: 价值分布报告
        """
        try:
            print("生成价值分布报告...")
            
            print
            # 寻找锚点
            anchors = self.find_market_anchors(
                target_features, similarity_threshold=0.5, max_anchors=50)
            
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
            competitive_result = self.calculate_value(
                target_features, 'competitive', max_anchors=len(anchors))
            fair_result = self.calculate_value(
                target_features, 'fair_value', max_anchors=len(anchors))
            
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
                        'id': anchor.get('equip_sn', anchor.get('equip_id', anchor.get('id', i))),
                        'price': float(anchor['price']),
                        'similarity': round(float(anchor['similarity']), 3)
                    }
                    for i, anchor in enumerate(anchors[:20])  # 返回前20个详细信息
                ]
            }
            
            print(f"价值分布报告生成完成，基于 {len(anchors)} 个锚点")
            
            return report
            
        except Exception as e:
            self.logger.error(f"生成价值分布报告失败: {e}")
            return {'error': str(e)} 