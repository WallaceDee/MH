"""
极端值过滤工具类

提供通用的极端值过滤功能，供各个估价类使用
"""

import numpy as np
import logging
from typing import Dict, Any, List, Optional


class ExtremeValueFilter:
    """极端值过滤工具类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def filter_anchors_for_extreme_values(self, anchors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        对锚点进行极端值过滤（只过滤，不修正价格）
        
        Args:
            anchors: 原始锚点列表
            
        Returns:
            List[Dict[str, Any]]: 过滤后的锚点列表
        """
        if len(anchors) < 3:
            # 锚点太少，直接返回
            return anchors
            
        # 提取价格
        prices = [anchor['price'] for anchor in anchors]
        
        print(f"极端值过滤前: {len(anchors)}个锚点，价格范围: {min(prices):.1f} - {max(prices):.1f}")
        
        # 使用中位数校验过滤极端异常值
        filtered_anchors = self._filter_anchors_by_median_check(anchors, prices)
        
        # 如果过滤后锚点太少，返回原始数据
        if len(filtered_anchors) < 3:
            print(f"极端值过滤后锚点太少({len(filtered_anchors)})，返回原始数据")
            return anchors
        
        # 输出处理统计
        original_count = len(anchors)
        filtered_count = len(filtered_anchors)
        if original_count != filtered_count:
            print(f"锚点极端值过滤: {original_count} -> {filtered_count} 个锚点")
            if filtered_anchors:
                original_range = f"{min(prices):.1f} - {max(prices):.1f}"
                filtered_range = f"{min(a['price'] for a in filtered_anchors):.1f} - {max(a['price'] for a in filtered_anchors):.1f}"
                print(f"价格范围: {original_range} -> {filtered_range}")
        
        return filtered_anchors
    
    def _filter_anchors_by_median_check(self, anchors: List[Dict[str, Any]], prices: List[float]) -> List[Dict[str, Any]]:
        """
        使用中位数校验过滤极端异常值
        
        Args:
            anchors: 锚点列表
            prices: 价格列表
            
        Returns:
            List[Dict[str, Any]]: 过滤后的锚点列表
        """
        if len(prices) < 3:
            return anchors
            
        # 计算中位数和四分位数
        sorted_prices = sorted(prices)
        median_price = sorted_prices[len(sorted_prices) // 2]
        
        # 计算四分位数
        q1_idx = len(sorted_prices) // 4
        q3_idx = 3 * len(sorted_prices) // 4
        q1_price = sorted_prices[q1_idx]
        q3_price = sorted_prices[q3_idx]
        
        # 计算IQR（四分位距）
        iqr = q3_price - q1_price
        
        # 设置异常值边界（使用1.0倍IQR规则）
        lower_bound = q1_price - 1.0 * iqr
        upper_bound = q3_price + 1.0 * iqr
        
        # 过滤异常值
        filtered_anchors = []
        for i, anchor in enumerate(anchors):
            if i < len(prices):
                price = prices[i]
                if lower_bound <= price <= upper_bound:
                    # 保持原始价格，不在这里修改
                    filtered_anchors.append(anchor)
                else:
                    # 记录被过滤的异常值
                    print(f"过滤异常价格: {price:.1f} (边界: {lower_bound:.1f} - {upper_bound:.1f})")
        
        return filtered_anchors
    
    def filter_with_custom_threshold(self, anchors: List[Dict[str, Any]], 
                                   iqr_multiplier: float = 1.0,
                                   min_anchors: int = 3) -> List[Dict[str, Any]]:
        """
        使用自定义阈值进行极端值过滤
        
        Args:
            anchors: 锚点列表
            iqr_multiplier: IQR倍数（默认1.0，越大越宽松）
            min_anchors: 最小锚点数量
            
        Returns:
            List[Dict[str, Any]]: 过滤后的锚点列表
        """
        if len(anchors) < min_anchors:
            return anchors
            
        prices = [anchor['price'] for anchor in anchors]
        
        # 计算中位数和四分位数
        sorted_prices = sorted(prices)
        q1_idx = len(sorted_prices) // 4
        q3_idx = 3 * len(sorted_prices) // 4
        q1_price = sorted_prices[q1_idx]
        q3_price = sorted_prices[q3_idx]
        
        # 计算IQR
        iqr = q3_price - q1_price
        
        # 设置自定义边界
        lower_bound = q1_price - iqr_multiplier * iqr
        upper_bound = q3_price + iqr_multiplier * iqr
        
        # 过滤异常值
        filtered_anchors = []
        for i, anchor in enumerate(anchors):
            if i < len(prices):
                price = prices[i]
                if lower_bound <= price <= upper_bound:
                    filtered_anchors.append(anchor)
                else:
                    print(f"过滤异常价格: {price:.1f} (边界: {lower_bound:.1f} - {upper_bound:.1f})")
        
        # 如果过滤后锚点太少，返回原始数据
        if len(filtered_anchors) < min_anchors:
            print(f"极端值过滤后锚点太少({len(filtered_anchors)})，返回原始数据")
            return anchors
        
        return filtered_anchors 