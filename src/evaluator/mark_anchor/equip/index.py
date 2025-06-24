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

# 添加项目根目录到Python路径，解决模块导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(current_dir))))  # 向上四级到项目根目录
sys.path.insert(0, project_root)


# 修复导入问题

# 直接导入同目录下的模块
current_dir = os.path.dirname(os.path.abspath(__file__))
collector_path = os.path.join(current_dir, 'equip_market_data_collector.py')

spec = importlib.util.spec_from_file_location(
    "equip_market_data_collector", collector_path)
collector_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector_module)
EquipMarketDataCollector = collector_module.EquipMarketDataCollector

warnings.filterwarnings('ignore')


class EquipAnchorEvaluator:
    """装备锚定估价器 - 基于市场相似装备的价格锚定估价"""

    def __init__(self, market_data_collector: Optional[EquipMarketDataCollector] = None):
        """
        初始化装备锚定估价器

        Args:
            market_data_collector: 装备市场数据采集器实例，如果为None则创建新实例
        """
        self.logger = logging.getLogger(__name__)

        # 初始化装备市场数据采集器
        if market_data_collector is None:
            self.market_collector = EquipMarketDataCollector()
        else:
            self.market_collector = market_data_collector

        # 初始化特征提取器
        from src.evaluator.feature_extractor.equip_feature_extractor import EquipFeatureExtractor
        self.feature_extractor = EquipFeatureExtractor()

        # 定义装备特征容忍度配置 - 分为绝对容忍度和相对容忍度
        # 绝对容忍度：用于整数值特征（如等级、属性）
        self.absolute_tolerances = {
            # 基础属性特征 - 绝对差值容忍度
            'equip_level': 20,           # 装备等级允许±20级差异
            'kindid': 0,                 # 装备类型必须完全一致
            'init_damage': 50,           # 初伤允许±50差异
            'all_damage': 50,            # 总伤允许±50差异
            'init_wakan': 10,            # 初灵允许±50差异
            'init_defense': 10,          # 初防允许±50差异
            'init_hp': 100,              # 初血允许±100差异
            'init_dex': 10,              # 初敏允许±50差异
            'mingzhong': 30,             # 命中允许±30差异
            'shanghai': 30,              # 伤害允许±30差异

            # 附加属性特征
            'addon_tizhi': 10,           # 附加体质允许±10差异
            'addon_liliang': 10,         # 附加力量允许±10差异
            'addon_naili': 10,           # 附加耐力允许±10差异
            'addon_minjie': 10,          # 附加敏捷允许±10差异
            'addon_fali': 10,            # 附加法力允许±10差异
            'addon_lingli': 10,          # 附加灵力允许±10差异
            'addon_total': 20,           # 总附加属性允许±20差异

            # 宝石和强化特征
            'hole_num': 2,               # 开运孔数允许±1差异
            'repair_fail_num': 2,        # 修理失败次数允许±2差异

            # 特技、特效、套装 - 必须完全匹配
            'special_skill': 0,          # 特技必须完全一致
            'suit_effect': 0,            # 套装效果必须完全一致
        }

        # 相对容忍度：用于大数值特征或比例特征
        self.relative_tolerances = {
            # 综合评分特征 - 相对容忍度
            'gem_score': 0.3,            # 宝石得分容忍度20%
            'total_addon': 0.2,          # 总附加属性容忍度20%
            'total_gem_value': 0.3,      # 总宝石价值容忍度30%
        }

        # 定义关键特征权重（用于相似度计算）
        self.feature_weights = {
            # 最重要特征 - 装备类型和等级
            'kindid': 2.0,               # 装备类型是最重要的
            'equip_level': 1.5,          # 装备等级很重要
            'gem_score': 1.0,            # 宝石得分很重要
            # 很重要特征 - 基础属性
            'init_damage': 1.2,          # 初伤
            'all_damage': 1.2,           # 总伤
            'init_wakan': 1.0,           # 初灵
            'init_defense': 1.0,         # 初防
            'init_hp': 0.8,              # 初血
            'init_dex': 0.8,             # 初敏
            'mingzhong': 0.6,            # 命中
            'shanghai': 0.6,             # 伤害

            # 重要特征 - 附加属性
            'addon_total': 1.0,          # 总附加属性
            'addon_tizhi': 0.6,          # 附加体质
            'addon_liliang': 0.6,        # 附加力量
            'addon_naili': 0.6,          # 附加耐力
            'addon_minjie': 0.6,         # 附加敏捷
            'addon_fali': 0.6,           # 附加法力
            'addon_lingli': 0.6,         # 附加灵力

            # 特殊特征 - 高权重 TODO:
            'suit_effect': 2.0,          # 套装效果

            # 辅助特征
            'total_gem_value': 0.8,      # 总宝石价值
            'hole_num': 0.4,             # 开运孔数
            'repair_fail_num': -0.2,     # 修理失败次数（负权重）

        }

        print("装备锚定估价器初始化完成")

    def find_market_anchors(self,
                            target_features: Dict[str, Any],
                            similarity_threshold: float = 0.7,
                            max_anchors: int = 30) -> List[Dict[str, Any]]:
        """
        寻找市场锚点装备

        Args:
            target_features: 目标装备特征字典
            similarity_threshold: 相似度阈值（0-1）
            max_anchors: 最大锚点数量

        Returns:
            List[Dict[str, Any]]: 锚点装备列表，每个元素包含：
                - similarity: 相似度分数
                - price: 价格
                - equip_sn: 装备序列号
                - features: 完整特征数据
        """
        try:
            print(f"开始寻找装备市场锚点，相似度阈值: {similarity_threshold}")

            # 获取目标装备的equip_sn，用于排除自身
            target_equip_sn = target_features.get('equip_sn')
            if target_equip_sn:
                print(f"目标装备序列号: {target_equip_sn}，将排除自身")

            # 构建预过滤条件以提高效率
            pre_filters = self._build_pre_filters(target_features)

            # 获取预过滤的市场数据
            market_data = self.market_collector.get_market_data_for_similarity(
                pre_filters)

            if market_data.empty:
                print("装备市场数据为空，无法找到锚点")
                return []

            print(f"预过滤后获得 {len(market_data)} 条候选装备数据")

            # 计算所有市场装备的相似度
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
                    
                    # 从市场数据提取特征
                    market_features = self.feature_extractor.extract_features(
                        market_row.to_dict())

                    # 计算相似度
                    similarity = self._calculate_similarity(
                        target_features, market_features)

                    if similarity >= similarity_threshold:
                        anchor_candidates.append({
                            # 优先使用真实的equip_sn，如果没有则使用索引
                            'equip_sn': current_equip_sn,
                            'similarity': float(similarity),
                            'price': float(market_row.get('price', 0)),
                            'features': market_row.to_dict()
                        })

                except Exception as e:
                    # 记录有问题的数据
                    self.logger.error(f"处理装备 {market_row.get('equip_sn', idx)} 时出错: {e}")
                    error_count += 1
                    continue

            # 输出处理统计
            processed_count = len(market_data)
            success_count = processed_count - error_count - excluded_self_count
            if error_count > 0 or excluded_self_count > 0:
                self.logger.warning(
                    f"数据处理统计: 总数={processed_count}, 成功={success_count}, 失败={error_count}, 排除自身={excluded_self_count}")

            # 按相似度排序
            anchor_candidates.sort(key=lambda x: x['similarity'], reverse=True)
            # 返回前N个锚点
            anchors = anchor_candidates[:max_anchors]

            print(f"找到 {len(anchors)} 个装备市场锚点")
            if excluded_self_count > 0:
                print(f"排除目标装备自身 {excluded_self_count} 次")
            if anchors:
                print(
                    f"相似度范围: {anchors[-1]['similarity']:.3f} - {anchors[0]['similarity']:.3f}")
                print(
                    f"价格范围: {min(a['price'] for a in anchors):.1f} - {max(a['price'] for a in anchors):.1f}")

            return anchors

        except Exception as e:
            self.logger.error(f"寻找装备市场锚点失败: {e}")
            return []

    def _build_pre_filters(self, target_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据目标装备特征构建预过滤条件，减少计算量

        Args:
            target_features: 目标装备特征

        Returns:
            Dict[str, Any]: 过滤条件
        """
        filters = {}

        # 装备等级过滤（±10级）
        if 'equip_level' in target_features:
            level = target_features['equip_level']
            filters['equip_level_range'] = (max(1, level - 10), level + 10)

        # 装备类型必须完全一致
        if 'kindid' in target_features:
            filters['kindid'] = target_features['kindid']

        # 伤害范围过滤（±100）
        if 'all_damage' in target_features:
            damage = target_features['all_damage']
            damage_tolerance = 100
            filters['damage_range'] = (
                max(0, damage - damage_tolerance),
                damage + damage_tolerance
            )
        # 高价值特效必须包含
        if 'special_effect' in target_features and len(target_features['special_effect']) > 0:
            filters['special_effect'] = target_features['special_effect']

        # 特技必须完全一致（如果有特技）
        if 'special_skill' in target_features and target_features['special_skill'] > 0:
            filters['special_skill'] = target_features['special_skill']

        # 套装效果
        if 'suit_effect' in target_features and target_features['suit_effect'] > 0:
            filters['suit_effect'] = target_features['suit_effect']

        return filters

    def _calculate_similarity(self,
                              target_features: Dict[str, Any],
                              market_features: Dict[str, Any]) -> float:
        """
        计算两个装备特征的相似度

        Args:
            target_features: 目标装备特征
            market_features: 市场装备特征

        Returns:
            float: 相似度分数（0-1）
        """
        try:
            # 输入验证
            if not isinstance(target_features, dict) or not isinstance(market_features, dict):
                self.logger.warning("装备特征数据格式错误，使用默认相似度")
                return 0.0

            total_weight = 0
            weighted_similarity = 0

            # 合并所有特征名称
            all_features = set(self.absolute_tolerances.keys()) | set(
                self.relative_tolerances.keys())

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
                elif feature_name in ['suit_effect']:
                    # 套装效果特殊相似度计算
                    # 敏捷套
                    # B "1040": "凤凰",
                    # B "1047": "幽灵",
                    # B "1049": "吸血鬼",
                    # A "1053": "画魂",
                    # A "1056": "雾中仙",  
                    # A "1065": "机关鸟",
                    # A "1067": "巴蛇",  
                    # A "1070": "猫灵（人型）",  
                    # A "1077": "修罗傀儡妖",
                    agility_suits = {
                        'B': [1040, 1047, 1049],  # 凤凰, 幽灵, 吸血鬼
                        'A': [1053, 1056, 1065, 1067, 1070, 1077]  # 画魂, 雾中仙, 机关鸟, 巴蛇, 猫灵（人型）, 修罗傀儡妖
                    }
                    
                    # 魔力套
                    # B "1041": "蛟龙",
                    # B "1042": "雨师",
                    # B "1043": "如意仙子",
                    # B "1046": "星灵仙子",
                    # B "1050": "净瓶女娲",
                    # B "1052": "灵符女娲",
                    # A "1057": "灵鹤",
                    # A "1059": "炎魔神",
                    # A "1069": "葫芦宝贝",
                    # A "1073": "混沌兽",
                    # A "1074": "长眉灵猴",
                    # A "1081": "蜃气妖"

                    magic_suits = {
                        'B': [1041, 1042, 1043, 1046, 1050, 1052],  # 蛟龙, 雨师, 如意仙子, 星灵仙子, 净瓶女娲, 灵符女娲
                        'A': [1057, 1059, 1069, 1073, 1074, 1081]   # 灵鹤, 炎魔神, 葫芦宝贝, 混沌兽, 长眉灵猴, 蜃气妖
                    }
                    
                    def get_suit_info(suit_id):
                        """获取套装信息：(类型, 等级)"""
                        if suit_id in agility_suits['B']:
                            return ('agility', 'B')
                        elif suit_id in agility_suits['A']:
                            return ('agility', 'A')
                        elif suit_id in magic_suits['B']:
                            return ('magic', 'B')
                        elif suit_id in magic_suits['A']:
                            return ('magic', 'A')
                        else:
                            return (None, None)
                    
                    if target_val == market_val:
                        # 完全相同
                        feature_similarity = 1.0
                    else:
                        target_type, target_grade = get_suit_info(target_val)
                        market_type, market_grade = get_suit_info(market_val)
                        
                        if target_type is None or market_type is None:
                            # 如果有一个不是敏捷套或魔力套，则使用原来的逻辑
                            feature_similarity = 0.0
                        elif target_type == market_type and target_grade == market_grade:
                            # 同类型同等级（如巴蛇A级敏捷套 -> 机关鸟A级敏捷套）
                            feature_similarity = 0.95
                        elif target_type != market_type and target_grade == market_grade:
                            # 不同类型同等级（如巴蛇A级敏捷套 -> 灵鹤A级魔力套）
                            feature_similarity = 0.9
                        elif target_type == market_type and target_grade != market_grade:
                            # 同类型跨等级（如巴蛇A级敏捷套 -> 凤凰B级敏捷套）
                            feature_similarity = 0.75
                        elif target_type != market_type and target_grade != market_grade:
                            # 不同类型跨等级（如巴蛇A级敏捷套 -> 蛟龙B级魔力套）
                            feature_similarity = 0.3
                        else:
                            feature_similarity = 0.0
                elif feature_name in self.absolute_tolerances:
                    # 使用绝对容忍度计算
                    tolerance = self.absolute_tolerances[feature_name]
                    abs_diff = abs(target_val - market_val)

                    if abs_diff <= tolerance:
                        # 在容忍度内，相似度为1
                        feature_similarity = 1.0
                    elif abs_diff <= tolerance * 2:
                        # 超出容忍度但在2倍范围内，线性递减
                        feature_similarity = max(
                            0, 1.0 - (abs_diff - tolerance) / max(tolerance, 1))
                    else:
                        # 差异太大，相似度为0
                        feature_similarity = 0.0
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
                            feature_similarity = max(
                                0, 1.0 - (diff_ratio - tolerance) / max(tolerance, 0.1))
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
            self.logger.error(f"计算装备相似度失败: {e}")
            return 0.0

    def calculate_value(self,
                        target_features: Dict[str, Any],
                        strategy: str = 'fair_value') -> Dict[str, Any]:
        """
        计算装备价值

        Args:
            target_features: 目标装备特征字典
            strategy: 定价策略 ('competitive', 'fair_value', 'premium')

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
            print(f"开始计算装备价值，策略: {strategy}")

            # 寻找市场锚点
            anchors = self.find_market_anchors(target_features)

            if len(anchors) == 0:
                self.logger.error(f"未找到装备市场锚点")
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
                    'error': '未找到足够的相似装备进行估价',
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
                # 溢价定价：75%分位数 × 0.95
                estimated_price = float(np.percentile(anchor_prices, 75) * 0.95)
            else:  # fair_value
                # 公允价值：相似度加权中位数 × 0.93
                base_price = self._weighted_median(
                    anchor_prices, anchor_similarities)
                estimated_price = float(base_price * 0.93)

            # 计算置信度
            confidence = self._calculate_confidence(
                anchors, len(anchor_prices))

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

            print(
                f"装备估价完成: {estimated_price:.1f}，基于 {len(anchors)} 个锚点，置信度: {confidence:.2f}")

            return result

        except Exception as e:
            self.logger.error(f"计算装备价值失败: {e}")
            return {
                'estimated_price': 0,
                'anchor_count': 0,
                'error': str(e)
            }

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
                return float(value)

        return float(paired[-1][0])  # fallback

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
            avg_similarity = float(np.mean([anchor['similarity']
                                           for anchor in anchors]))
            similarity_bonus = avg_similarity * 0.3
        else:
            similarity_bonus = 0

        # 价格稳定性加成
        if len(anchors) >= 3:
            prices = [anchor['price'] for anchor in anchors]
            price_cv = float(np.std(prices) / 
                           np.mean(prices)) if np.mean(prices) > 0 else 1.0
            stability_bonus = max(0, (0.5 - price_cv) * 0.4)  # CV低于0.5时有加成
        else:
            stability_bonus = 0

        final_confidence = min(
            base_confidence + similarity_bonus + stability_bonus, 1.0)
        return float(final_confidence)

    def value_distribution_report(self, target_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成装备价值分布报告

        Args:
            target_features: 目标装备特征字典

        Returns:
            Dict[str, Any]: 价值分布报告
        """
        try:
            print("生成装备价值分布报告...")

            # 寻找锚点
            anchors = self.find_market_anchors(
                target_features, similarity_threshold=0.5, max_anchors=50)

            if len(anchors) == 0:
                return {
                    'error': '未找到足够的装备市场锚点',
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
                target_features, 'competitive')
            fair_result = self.calculate_value(target_features, 'fair_value')

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
                        'equip_sn': anchor['equip_sn'],
                        'price': float(anchor['price']),
                        'similarity': round(float(anchor['similarity']), 3),
                        'equip_level': int(anchor['features'].get('equip_level', 0)),
                        'kindid': int(anchor['features'].get('kindid', 0))
                    }
                    for anchor in anchors[:10]  # 返回前10个详细信息
                ]
            }

            print(f"装备价值分布报告生成完成，基于 {len(anchors)} 个锚点")

            return report

        except Exception as e:
            self.logger.error(f"生成装备价值分布报告失败: {e}")
            return {'error': str(e)}

    def batch_valuation(self,
                        equip_list: List[Dict[str, Any]],
                        strategy: str = 'fair_value') -> List[Dict[str, Any]]:
        """
        批量装备估价

        Args:
            equip_list: 装备特征列表
            strategy: 定价策略

        Returns:
            List[Dict[str, Any]]: 批量估价结果列表
        """
        results = []

        print(f"开始批量装备估价，共 {len(equip_list)} 个装备")

        for i, equip_features in enumerate(equip_list):
            try:
                result = self.calculate_value(equip_features, strategy)
                result['equip_index'] = i
                results.append(result)

                if (i + 1) % 10 == 0:
                    print(f"已完成 {i + 1}/{len(equip_list)} 个装备的估价")

            except Exception as e:
                self.logger.error(f"批量估价第 {i+1} 个装备失败: {e}")
                results.append({
                    'equip_index': i,
                    'estimated_price': 0,
                    'error': str(e)
                })

        print(
            f"批量装备估价完成，成功估价 {len([r for r in results if 'error' not in r])} 个装备")

        return results


if __name__ == "__main__":
    # 测试代码
    try:
        # 初始化估价器
        evaluator = EquipAnchorEvaluator()

        # 构造测试装备特征 (使用数据库中实际存在的kindid=20)
        test_features = {
            'equip_level': 80,         # 调整到数据库中存在的等级范围
            'kindid': 20,              # 使用数据库中存在的类型
            'init_damage': 300,        # 初伤
            'all_damage': 350,         # 总伤
            'addon_total': 40,         # 总附加属性
            'gem_level': 8,            # 宝石等级
            'special_skill': 0,        # 无特技
            'suit_effect': 0,          # 无套装
        }

        print("=== 测试装备特征 ===")
        for key, value in test_features.items():
            print(f"{key}: {value}")

        # 测试估价
        print("\n=== 开始装备估价测试 ===")

        # 公允价值估价
        fair_result = evaluator.calculate_value(test_features, 'fair_value')
        print(f"\n公允价值估价: {fair_result['estimated_price']:.1f}")
        print(f"锚点数量: {fair_result['anchor_count']}")
        print(f"置信度: {fair_result['confidence']:.2f}")

        # 竞争性估价
        competitive_result = evaluator.calculate_value(
            test_features, 'competitive')
        print(f"\n竞争性估价: {competitive_result['estimated_price']:.1f}")

        # 溢价估价
        premium_result = evaluator.calculate_value(test_features, 'premium')
        print(f"\n溢价估价: {premium_result['estimated_price']:.1f}")

        # 生成价值分布报告
        print("\n=== 生成装备价值分布报告 ===")
        report = evaluator.value_distribution_report(test_features)

        if 'error' not in report:
            print(
                f"价格范围: {report['min_price']:.1f} - {report['max_price']:.1f}")
            print(f"中位价格: {report['median_price']:.1f}")
            print(f"推荐竞争价格: {report['recommended_competitive']:.1f}")
            print(f"推荐公允价格: {report['recommended_fair']:.1f}")
            print(f"锚点数量: {report['anchor_count']}")
        else:
            print(f"报告生成失败: {report['error']}")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
