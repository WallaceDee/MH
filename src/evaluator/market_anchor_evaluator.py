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
    from .market_data_collector import MarketDataCollector
except ImportError:
    from market_data_collector import MarketDataCollector

warnings.filterwarnings('ignore')


class MarketAnchorEValuator:
    """市场锚定估价器 - 基于市场相似角色的价格锚定估价"""
    
    def __init__(self, market_data_collector: Optional[MarketDataCollector] = None):
        """
        初始化市场锚定估价器
        
        Args:
            market_data_collector: 市场数据采集器实例，如果为None则创建新实例
        """
        self.logger = logging.getLogger(__name__)
        
        # 初始化市场数据采集器
        if market_data_collector is None:
            self.market_collector = MarketDataCollector()
        else:
            self.market_collector = market_data_collector
        
        # 定义特征容忍度配置 - 分为绝对容忍度和相对容忍度
        # 绝对容忍度：用于整数值特征（如修炼等级）
        self.absolute_tolerances = {
            # 修炼系统特征 - 绝对差值容忍度
            'expt_ski1': 1,          # 攻击修炼允许±1级差异
            'expt_ski2': 1,          # 防御修炼允许±1级差异
            'expt_ski3': 1,          # 法术修炼允许±1级差异
            'expt_ski4': 1,          # 抗法修炼允许±1级差异
            'expt_ski5': 1,          # 猎术修炼允许±1级差异
            'beast_ski1': 1,         # 召唤兽攻击修炼允许±1级差异
            'beast_ski2': 1,         # 召唤兽防御修炼允许±1级差异
            'beast_ski3': 1,         # 召唤兽法术修炼允许±1级差异
            'beast_ski4': 1,         # 召唤兽抗法修炼允许±1级差异
            'total_cultivation': 5,  # 总修炼允许±5级差异
            'total_beast_cultivation': 4,  # 召唤兽总修炼允许±4级差异
            
            # 等级和关键整数特征
            'level': 30,              # 等级允许±30级差异
            'all_new_point': 0,      # 乾元丹必须完全一致
            'three_fly_lv': 0,       # 化圣等级必须一致
            'school_history_count': 1,  # 历史门派数允许±1差异
            'packet_page': 2,        # 行囊页数允许±2差异
            'allow_pet_count': 2,    # 召唤兽上限允许±2差异
            
            # 宠物和法宝系统
            'premium_pet_count': 2,     # 特殊宠物允许±2差异
            'premium_fabao_count': 10,   # 法宝允许±10差异
            'hight_grow_rider_count': 1, # 高成长坐骑允许±1差异
            
            # 特殊状态
            'qianyuandan_breakthrough': 0,  # 乾元丹突破必须一致
        }
        
        # 相对容忍度：用于大数值特征（如经验、金钱等）
        self.relative_tolerances = {
            # 经验和成长系统 - 相对容忍度
            'sum_exp': 1.0,         # 总经验容忍度30%
            'yushoushu_skill': 1.0,  # 育兽术等级容忍度100%
            
            # 其他增值系统
            'lingyou_count': 0.50,   # 灵佑次数容忍度50%
            'jiyuan_amount': 0.50,   # 机缘值容忍度50%
            'xianyu_amount': 1.0,   # 仙玉容忍度80%
            'learn_cash': 0.80,      # 储备金容忍度80%
            
            # 技能系统 - 组合特征（移除冗余特征）
            'avg_school_skills': 0.05,      # 师门技能平均值
            'high_life_skills_count': 0.20, # 高等级生活技能数量
            'total_qiangzhuang_shensu': 0.10, # 强壮神速总和
            
            # 外观和神器系统
            'shenqi_score': 0.5,           # 神器得分容忍度50%
            'limited_skin_score': 0.5,     # 限量锦衣得分容忍度50%
            'limited_huge_horse_score': 0.5, # 限量祥瑞得分容忍度50%
        }
        
        # 定义关键特征权重（用于相似度计算）
        self.feature_weights = {
            # 最重要特征 
            # 修炼细节特征 - 提高权重以增强影响力
            'expt_ski1': 1, 'expt_ski2': 1, 'expt_ski3': 1, 'expt_ski4': 1, 'expt_ski5': 0.4,
            'beast_ski1': 1, 'beast_ski2': 1, 'beast_ski3': 1, 'beast_ski4': 1,
            # 乾元丹和乾元丹突破
            'all_new_point': 1.0,
            'qianyuandan_breakthrough': 1.0,
            
            # 很重要特征 - 显著影响价值
            'total_beast_cultivation': 1, # 召唤兽总修炼
            'total_cultivation': 1, # 总修炼
            
            # 重要特征 - 中等影响
            'avg_school_skills': 0.8,
            'three_fly_lv': 1, # 化圣等级
            'total_qiangzhuang_shensu': 0.6, # 强壮神速总和
            'school_history_count': 0.6, # 历史门派数
            'high_life_skills_count': 0.6, # 高等级生活技能数量
         
            # 辅助特征 - 较低权重
            'level': 0.5, # 等级
            'lingyou_count': 0.4, # 灵佑次数    
            'hight_grow_rider_count': 0.4, # 高成长坐骑数量
            
            # 外观和神器特征 - 中等权重
            'shenqi_score': 0.5, # 神器得分
            'limited_skin_score': 0.5, # 限量锦衣得分
            'limited_huge_horse_score': 0.5, # 限量祥瑞得分
            
            # 次要特征 - 低权重
            'jiyuan_amount': 0.3, # 机缘值
            
            # 可选特征 - 最低权重
            'premium_pet_count': 0.1,
            'yushoushu_skill': 0.1,
            'xianyu_amount': 0.1,
            'learn_cash': 0.2,
            'sum_exp': 0.2,
            'packet_page': 0.1,
            'allow_pet_count': 0.1,
            'premium_fabao_count': 0.1
        }
        
        print("市场锚定估价器初始化完成")
    
    def find_market_anchors(self, 
                           target_features: Dict[str, Any],
                           similarity_threshold: float = 0.7,
                           max_anchors: int = 30) -> List[Dict[str, Any]]:
        """
        寻找市场锚点角色
        
        Args:
            target_features: 目标角色特征字典
            similarity_threshold: 相似度阈值（0-1）
            max_anchors: 最大锚点数量
            
        Returns:
            List[Dict[str, Any]]: 锚点角色列表，每个元素包含：
                - similarity: 相似度分数
                - price: 价格
                - equip_id: 装备ID
                - features: 完整特征数据
        """
        try:
            print(f"开始寻找市场锚点，相似度阈值: {similarity_threshold}")
            
            # 构建预过滤条件以提高效率
            pre_filters = self._build_pre_filters(target_features)
            
            # 获取预过滤的市场数据
            market_data = self.market_collector.get_market_data_for_similarity(pre_filters)
            
            if market_data.empty:
                print("市场数据为空，无法找到锚点")
                return []
            
            print(f"预过滤后获得 {len(market_data)} 条候选数据")
            
            # 统计数据质量
            total_rows = len(market_data)
            cultivation_fields = ['expt_ski1', 'expt_ski2', 'expt_ski3', 'expt_ski4', 'expt_ski5']
            none_count_by_field = {}
            for field in cultivation_fields:
                if field in market_data.columns:
                    none_count = market_data[field].isnull().sum()
                    none_count_by_field[field] = none_count
            
            if any(count > 0 for count in none_count_by_field.values()):
                self.logger.info(f"数据质量统计 - 总行数: {total_rows}")
                self.logger.info(f"修炼字段None值统计: {none_count_by_field}")
            
            # 计算所有市场角色的相似度
            anchor_candidates = []
            error_count = 0
            
            for equip_id, market_row in market_data.iterrows():
                try:
                    # 计算相似度
                    similarity = self._calculate_similarity(target_features, market_row.to_dict())
                    
                    if similarity >= similarity_threshold:
                        anchor_candidates.append({
                            'equip_id': equip_id,
                            'similarity': similarity,
                            'price': market_row.get('price', 0),
                            'features': market_row.to_dict()
                        })
                        
                except Exception as e:
                    # 详细记录有问题的数据
                    market_dict = market_row.to_dict()
                    self.logger.error(f"处理角色 {equip_id} 时出错: {e}")
                    self.logger.error(f"问题数据内容: {market_dict}")
                    
                    # 记录具体的修炼字段值，帮助诊断
                    cultivation_fields = ['expt_ski1', 'expt_ski2', 'expt_ski3', 'expt_ski4', 'expt_ski5', 
                                        'beast_ski1', 'beast_ski2', 'beast_ski3', 'beast_ski4']
                    problematic_fields = {}
                    for field in cultivation_fields:
                        if field in market_dict:
                            value = market_dict[field]
                            if value is None or (isinstance(value, str) and value.strip() == ''):
                                problematic_fields[field] = value
                    
                    if problematic_fields:
                        self.logger.error(f"发现问题字段: {problematic_fields}")
                    
                    # 记录数据类型信息
                    field_types = {k: type(v).__name__ for k, v in market_dict.items() if k in cultivation_fields}
                    self.logger.error(f"字段类型信息: {field_types}")
                    
                    error_count += 1
                    continue
            
            # 输出处理统计
            processed_count = len(market_data)
            success_count = processed_count - error_count
            if error_count > 0:
                self.logger.warning(f"数据处理统计: 总数={processed_count}, 成功={success_count}, 失败={error_count}")
            
            # 按相似度排序
            anchor_candidates.sort(key=lambda x: x['similarity'], reverse=True)
            # 返回前N个锚点
            anchors = anchor_candidates[:max_anchors]
            
            print(f"找到 {len(anchors)} 个市场锚点角色")
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
            target_features: 目标角色特征
            
        Returns:
            Dict[str, Any]: 过滤条件
        """
        filters = {}
        
        # 等级过滤（±30级）
        if 'level' in target_features:
            level = target_features['level']
            filters['level_range'] = (max(1, level - 30), level + 30)
            
        # 修炼等级总和相差(±30) 不包含猎修
        if 'total_cultivation' in target_features:
            total_cultivation = target_features['total_cultivation']
            cultivation_tolerance = 30
            filters['total_cultivation_range'] = (
                max(0, total_cultivation - cultivation_tolerance),
                total_cultivation + cultivation_tolerance
            )
 
        # 宠物控制力总和相差(±30)
        if 'total_beast_cultivation' in target_features:
            total_beast_cultivation = target_features['total_beast_cultivation']
            beast_cultivation_tolerance = 30
            filters['total_beast_cultivation_range'] = (
                max(0, total_beast_cultivation - beast_cultivation_tolerance),
                total_beast_cultivation + beast_cultivation_tolerance
            )
 
        # 师门技能平均值相差(±30)
        if 'avg_school_skills' in target_features:
            avg_school_skills = target_features['avg_school_skills']
            school_skills_tolerance = 30
            filters['avg_school_skills_range'] = (
                max(0, avg_school_skills - school_skills_tolerance),
                avg_school_skills + school_skills_tolerance
            )

        return filters
    
    def _create_feature_vector(self, features: Dict[str, Any]) -> np.ndarray:
        """
        创建特征向量
        
        Args:
            features: 特征字典
            
        Returns:
            np.ndarray: 标准化的特征向量
        """
        vector = []
        # 合并所有特征名称
        all_features = set(self.absolute_tolerances.keys()) | set(self.relative_tolerances.keys())
        
        for feature_name in sorted(all_features):
            value = features.get(feature_name, 0)
            # 简单标准化
            if feature_name == 'level':
                normalized_value = value / 200.0  # 假设最高等级200
            elif feature_name in ['sum_exp']:
                normalized_value = min(value / 10000.0, 1.0)  # 经验标准化
            elif feature_name in ['total_cultivation', 'total_beast_cultivation']:
                normalized_value = value / 400.0  # 修炼标准化（假设最高100*4）
            elif feature_name in ['total_gem_level']:
                normalized_value = value / 1000.0  # 宝石标准化
            else:
                normalized_value = min(value / 50.0, 1.0)  # 通用标准化
            
            vector.append(normalized_value)
        
        return np.array(vector)
    
    def _calculate_similarity(self, 
                            target_features: Dict[str, Any], 
                            market_features: Dict[str, Any]) -> float:
        """
        计算两个角色特征的相似度
        
        Args:
            target_features: 目标角色特征
            market_features: 市场角色特征
            
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
            all_features = set(self.absolute_tolerances.keys()) | set(self.relative_tolerances.keys())
            
            # 实现门派修炼智能匹配逻辑
            # 在梦幻西游中，物理门派主修攻击修炼(expt_ski1)，法术门派主修法术修炼(expt_ski3)
            # 两者价值等同，需要智能匹配最优组合
            target_features_adjusted = self._adjust_cultivation_features(target_features)
            market_features_adjusted = self._adjust_cultivation_features(market_features)
            
            for feature_name in all_features:
                if feature_name not in target_features_adjusted and feature_name not in market_features_adjusted:
                    continue
                    
                target_val = target_features_adjusted.get(feature_name, 0)
                market_val = market_features_adjusted.get(feature_name, 0)
                weight = self.feature_weights.get(feature_name, 0.5)
                
                # 计算特征相似度
                if target_val == 0 and market_val == 0:
                    # 两者都为0，完全匹配
                    feature_similarity = 1.0
                elif feature_name in ['all_new_point', 'qianyuandan_breakthrough', 'three_fly_lv']:
                    # 关键特征必须完全一致
                    feature_similarity = 1.0 if target_val == market_val else 0.0
                elif feature_name in self.absolute_tolerances:
                    # 使用绝对容忍度计算
                    tolerance = self.absolute_tolerances[feature_name]
                    abs_diff = abs(target_val - market_val)
                    
                    if abs_diff <= tolerance:
                        # 在容忍度内，相似度为1
                        feature_similarity = 1.0
                    elif abs_diff <= tolerance * 2:
                        # 超出容忍度但在2倍范围内，线性递减
                        feature_similarity = max(0, 1.0 - (abs_diff - tolerance) / max(tolerance, 1))
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
    
    def _adjust_cultivation_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        调整人物修炼特征以支持门派间智能匹配
        
        在梦幻西游中：
        - 物理门派主修攻击修炼(expt_ski1)，法术门派主修法术修炼(expt_ski3)
        - 两者价值等同，应该取最大值作为主修炼等级
        - 防御修炼(expt_ski2)和抗法修炼(expt_ski4)对所有门派都重要
        - 猎术修炼(expt_ski5)
        - 召唤兽修炼暂不处理，保持原始值
        
        Args:
            features: 原始特征字典
            
        Returns:
            Dict[str, Any]: 调整后的特征字典
        """
        try:
            adjusted_features = features.copy()
            
            # 记录原始输入数据（只在有问题时记录）
            cultivation_fields = ['expt_ski1', 'expt_ski2', 'expt_ski3', 'expt_ski4', 'expt_ski5']
            original_cultivation = {field: features.get(field) for field in cultivation_fields}
            
            # 获取修炼相关数值
            expt_ski1 = features.get('expt_ski1', 0)  # 攻击修炼（物理门派主修）
            expt_ski2 = features.get('expt_ski2', 0)  # 防御修炼（通用）
            expt_ski3 = features.get('expt_ski3', 0)  # 法术修炼（法术门派主修）
            expt_ski4 = features.get('expt_ski4', 0)  # 抗法修炼（通用）
            expt_ski5 = features.get('expt_ski5', 0)  # 猎术修炼（特殊门派）
            
            # 检查是否有异常值并记录
            problematic_values = {}
            if expt_ski1 is None: problematic_values['expt_ski1'] = expt_ski1
            if expt_ski2 is None: problematic_values['expt_ski2'] = expt_ski2
            if expt_ski3 is None: problematic_values['expt_ski3'] = expt_ski3
            if expt_ski4 is None: problematic_values['expt_ski4'] = expt_ski4
            if expt_ski5 is None: problematic_values['expt_ski5'] = expt_ski5
            
            if problematic_values:
                self.logger.warning(f"修炼特征调整: 发现None值: {problematic_values}")
                self.logger.warning(f"原始修炼数据: {original_cultivation}")
            
            # 处理None值，确保所有值都是数字
            expt_ski1 = 0 if expt_ski1 is None else expt_ski1
            expt_ski2 = 0 if expt_ski2 is None else expt_ski2
            expt_ski3 = 0 if expt_ski3 is None else expt_ski3
            expt_ski4 = 0 if expt_ski4 is None else expt_ski4
            expt_ski5 = 0 if expt_ski5 is None else expt_ski5
            
            # 智能匹配主修炼：攻击修炼和法术修炼取最大值
            # 这样物理门派角色可以匹配到法术门派角色，反之亦然
            main_cultivation = max(expt_ski1, expt_ski3)
            second_cultivation = min(expt_ski1, expt_ski3)
            # 调整特征值
            adjusted_features['expt_ski1'] = main_cultivation  # 统一主修炼
            adjusted_features['expt_ski2'] = expt_ski2  # 防御修炼保持原值
            adjusted_features['expt_ski3'] = second_cultivation  # 统一主修炼
            adjusted_features['expt_ski4'] = expt_ski4  # 抗法修炼保持原值
            adjusted_features['expt_ski5'] = expt_ski5  # 猎术修炼保持原值
            
            # 重新计算人物总修炼值（基于调整后的数值），确保所有值都是数字
            total_cultivation = (
                adjusted_features.get('expt_ski1', 0) + 
                adjusted_features.get('expt_ski2', 0) + 
                adjusted_features.get('expt_ski3', 0) + 
                adjusted_features.get('expt_ski4', 0) 
            )
            adjusted_features['total_cultivation'] = total_cultivation
            
            # 召唤兽总修炼保持原值，不重新计算
            # total_beast_cultivation 保持原始值
            
            return adjusted_features
            
        except Exception as e:
            self.logger.error(f"调整人物修炼特征失败: {e}")
            return features
    
    def calculate_value(self, 
                       target_features: Dict[str, Any],
                       strategy: str = 'fair_value') -> Dict[str, Any]:
        """
        计算角色价值
        
        Args:
            target_features: 目标角色特征字典
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
            print(f"开始计算角色价值，策略: {strategy}")
            
            # 寻找市场锚点
            anchors = self.find_market_anchors(target_features)
            
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
                    'error': '未找到足够的相似角色进行估价',
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
            self.logger.error(f"计算角色价值失败: {e}")
    
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
            target_features: 目标角色特征字典
            
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
            competitive_result = self.calculate_value(target_features, 'competitive')
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
            character_list: 角色特征列表
            strategy: 定价策略
            
        Returns:
            List[Dict[str, Any]]: 批量估价结果列表
        """
        results = []
        
        print(f"开始批量估价，共 {len(character_list)} 个角色")
        
        for i, character_features in enumerate(character_list):
            try:
                result = self.calculate_value(character_features, strategy)
                result['character_index'] = i
                results.append(result)
                
                if (i + 1) % 10 == 0:
                    print(f"已完成 {i + 1}/{len(character_list)} 个角色的估价")
                    
            except Exception as e:
                self.logger.error(f"批量估价第 {i+1} 个角色失败: {e}")
                results.append({
                    'character_index': i,
                    'estimated_price': 0,
                    'error': str(e)
                })
        
        print(f"批量估价完成，成功估价 {len([r for r in results if 'error' not in r])} 个角色")
        
        return results
    
    def export_valuation_report_to_excel(self, 
                                       target_features: Dict[str, Any],
                                       output_file: str = None,
                                       include_anchors: bool = True) -> str:
        """
        导出估价报告到Excel文件
        
        Args:
            target_features: 目标角色特征字典
            output_file: 输出文件路径，如果为None则自动生成
            include_anchors: 是否包含锚点角色详细信息
            
        Returns:
            str: 导出的文件路径
        """
        try:
            print("开始生成Excel估价报告...")
            
            # 生成文件名
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"角色估价报告_{timestamp}.xlsx"
            
            # 获取估价结果和分布报告
            fair_result = self.calculate_value(target_features, 'fair_value')
            competitive_result = self.calculate_value(target_features, 'competitive')
            premium_result = self.calculate_value(target_features, 'premium')
            distribution_report = self.value_distribution_report(target_features)
            
            # 创建Excel工作簿
            wb = Workbook()
            
            # 删除默认工作表
            wb.remove(wb.active)
            
            # 1. 创建估价摘要工作表
            self._create_summary_sheet(wb, target_features, fair_result, competitive_result, premium_result)
            
            # 2. 创建价格分布工作表
            self._create_distribution_sheet(wb, distribution_report)
            
            # 3. 创建相似角色列表工作表
            if include_anchors and fair_result.get('anchor_count', 0) > 0:
                self._create_anchors_sheet(wb, target_features)
            
            # 保存文件
            wb.save('./output/'+output_file)
            print(f"Excel报告已保存至: /output/{output_file}")
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"导出Excel报告失败: {e}")
            raise e
    
    def _create_summary_sheet(self, wb: Workbook, 
                            target_features: Dict[str, Any],
                            fair_result: Dict[str, Any],
                            competitive_result: Dict[str, Any],
                            premium_result: Dict[str, Any]):
        """创建估价摘要工作表"""
        ws = wb.create_sheet("估价摘要", 0)
        
        # 设置标题样式
        title_font = Font(name='微软雅黑', size=14, bold=True, color='FFFFFF')
        title_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        
        header_font = Font(name='微软雅黑', size=12, bold=True)
        header_fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
        
        normal_font = Font(name='微软雅黑', size=11)
        
        # 标题
        ws['A1'] = '梦幻西游角色估价报告'
        ws['A1'].font = title_font
        ws['A1'].fill = title_fill
        ws.merge_cells('A1:D1')
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        
        # 角色特征信息
        row = 3
        ws[f'A{row}'] = '角色特征信息'
        ws[f'A{row}'].font = header_font
        ws[f'A{row}'].fill = header_fill
        ws.merge_cells(f'A{row}:D{row}')
        
        row += 1
        
        # 按类别组织特征显示
        feature_categories = {
            '基础属性': ['level', 'all_new_point', 'sum_exp', 'three_fly_lv', 'nine_fight_level'],
            '修炼等级': ['expt_ski1', 'expt_ski2', 'expt_ski3', 'expt_ski4', 'expt_ski5', 'total_cultivation'],
            '修炼上限': ['max_expt1', 'max_expt2', 'max_expt3', 'max_expt4'],
            '召唤兽修炼': ['beast_ski1', 'beast_ski2', 'beast_ski3', 'beast_ski4', 'total_beast_cultivation'],
            '门派与技能': ['school_history_count', 'life_skills_count'],
            '装备与道具': ['premium_fabao_count', 'premium_pet_count', 'hight_grow_rider_count', 'packet_page', 'allow_pet_count'],
            '外观与神器': ['shenqi_score', 'limited_skin_score', 'limited_huge_horse_score']
        }
        
        # 显示所有特征，按类别分组
        for category, features in feature_categories.items():
            # 检查该类别是否有任何特征值
            has_features = any(feature in target_features for feature in features)
            if not has_features:
                continue
                
            # 类别标题
            ws[f'A{row}'] = category
            ws[f'A{row}'].font = Font(name='微软雅黑', size=11, bold=True, color='4472C4')
            ws.merge_cells(f'A{row}:B{row}')
            row += 1
            
            # 该类别下的特征
            for feature in features:
                if feature in target_features:
                    ws[f'A{row}'] = f"  {self._get_feature_display_name(feature)}"
                    ws[f'B{row}'] = target_features[feature]
                    ws[f'A{row}'].font = normal_font
                    ws[f'B{row}'].font = normal_font
                    row += 1
            
            # 类别间空行
            row += 1
        
        # 显示其他未分类的特征
        displayed_features = set()
        for features in feature_categories.values():
            displayed_features.update(features)
        
        other_features = {k: v for k, v in target_features.items() if k not in displayed_features}
        if other_features:
            ws[f'A{row}'] = '其他特征'
            ws[f'A{row}'].font = Font(name='微软雅黑', size=11, bold=True, color='4472C4')
            ws.merge_cells(f'A{row}:B{row}')
            row += 1
            
            for feature, value in other_features.items():
                ws[f'A{row}'] = f"  {self._get_feature_display_name(feature)}"
                ws[f'B{row}'] = value
                ws[f'A{row}'].font = normal_font
                ws[f'B{row}'].font = normal_font
                row += 1
        
        # 估价结果
        row += 1
        ws[f'A{row}'] = '估价结果'
        ws[f'A{row}'].font = header_font
        ws[f'A{row}'].fill = header_fill
        ws.merge_cells(f'A{row}:D{row}')
        
        row += 1
        pricing_data = [
            ('竞争性定价', competitive_result['estimated_price'], competitive_result['confidence']),
            ('公允价值定价', fair_result['estimated_price'], fair_result['confidence']),
            ('溢价定价', premium_result['estimated_price'], premium_result['confidence']),
        ]
        
        ws[f'A{row}'] = '定价策略'
        ws[f'B{row}'] = '估算价格'
        ws[f'C{row}'] = '置信度'
        ws[f'D{row}'] = '锚点数量'
        
        for i in range(4):
            ws[f'{chr(65+i)}{row}'].font = header_font
            ws[f'{chr(65+i)}{row}'].fill = header_fill
        
        row += 1
        for strategy, price, confidence in pricing_data:
            ws[f'A{row}'] = strategy
            ws[f'B{row}'] = f"{price:.1f}"
            ws[f'C{row}'] = f"{confidence:.2%}"
            ws[f'D{row}'] = fair_result['anchor_count']
            
            for i in range(4):
                ws[f'{chr(65+i)}{row}'].font = normal_font
            row += 1
        
        # 调整列宽
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 15
    
    def _create_distribution_sheet(self, wb: Workbook, distribution_report: Dict[str, Any]):
        """创建价格分布工作表"""
        ws = wb.create_sheet("价格分布分析")
        
        if 'error' in distribution_report:
            ws['A1'] = f"价格分布分析失败: {distribution_report['error']}"
            return
        
        # 标题样式
        header_font = Font(name='微软雅黑', size=12, bold=True)
        header_fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
        normal_font = Font(name='微软雅黑', size=11)
        
        # 价格统计
        ws['A1'] = '价格统计信息'
        ws['A1'].font = header_font
        ws['A1'].fill = header_fill
        ws.merge_cells('A1:B1')
        
        stats_data = [
            ('最低价格', f"{distribution_report['min_price']:.1f}"),
            ('最高价格', f"{distribution_report['max_price']:.1f}"),
            ('中位价格', f"{distribution_report['median_price']:.1f}"),
            ('25%分位数', f"{distribution_report['percentile_25']:.1f}"),
            ('75%分位数', f"{distribution_report['percentile_75']:.1f}"),
            ('锚点数量', f"{distribution_report['anchor_count']}个"),
        ]
        
        row = 2
        for label, value in stats_data:
            ws[f'A{row}'] = label
            ws[f'B{row}'] = value
            ws[f'A{row}'].font = normal_font
            ws[f'B{row}'].font = normal_font
            row += 1
        
        # 调整列宽
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 15
    
    def _create_anchors_sheet(self, wb: Workbook, target_features: Dict[str, Any]):
        """创建相似角色列表工作表"""
        ws = wb.create_sheet("相似角色列表")
        
        # 获取锚点数据
        anchors = self.find_market_anchors(target_features, similarity_threshold=0.4, max_anchors=100)
        
        if not anchors:
            ws['A1'] = "未找到相似角色"
            return
        
        # 标题样式
        header_font = Font(name='微软雅黑', size=10, bold=True)
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_font.color = 'FFFFFF'
        
        normal_font = Font(name='微软雅黑', size=9)
        
        # 收集所有特征列
        all_features = set()
        for anchor in anchors:
            all_features.update(anchor['features'].keys())
        
        # 按优先级排序特征
        priority_features = [
            'level', 'all_new_point', 'sum_exp', 'three_fly_lv', 'nine_fight_level',
            'expt_ski1', 'expt_ski2', 'expt_ski3', 'expt_ski4', 'expt_ski5', 'total_cultivation',
            'max_expt1', 'max_expt2', 'max_expt3', 'max_expt4',
            'beast_ski1', 'beast_ski2', 'beast_ski3', 'beast_ski4', 'total_beast_cultivation',
            'school_history_count', 'life_skills_count',
            'premium_fabao_count', 'premium_pet_count', 'hight_grow_rider_count', 'packet_page', 'allow_pet_count',
            'shenqi_score', 'limited_skin_score', 'limited_huge_horse_score',
        ]
        
        # 构建最终的特征列表（优先级特征 + 其他特征）
        ordered_features = []
        for feature in priority_features:
            if feature in all_features:
                ordered_features.append(feature)
        
        # 添加其他未分类的特征
        remaining_features = sorted(all_features - set(ordered_features))
        ordered_features.extend(remaining_features)
        
        # 构建表头
        headers = ['序号', '角色ID', '价格', '相似度']
        headers.extend([self._get_feature_display_name(feature) for feature in ordered_features])
        headers.append('藏宝阁链接')
        
        # 设置表头
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # 填充数据
        for idx, anchor in enumerate(anchors, 1):
            row = idx + 1
            features = anchor['features']
            
            # 基本信息
            ws.cell(row=row, column=1, value=idx)
            # 藏宝阁链接
            try:
                from ..utils.cbg_link_generator import CBGLinkGenerator
            except ImportError:
                try:
                    from utils.cbg_link_generator import CBGLinkGenerator
                except ImportError:
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
                    from cbg_link_generator import CBGLinkGenerator
            cbg_url = CBGLinkGenerator.generate_cbg_link(anchor['equip_id'])
            ws.cell(row=row, column=2, value=str(anchor['equip_id']))
              # 设置超链接
            from openpyxl.worksheet.hyperlink import Hyperlink
            ws.cell(row=row, column=2).hyperlink = cbg_url
            ws.cell(row=row, column=2).style = "Hyperlink"
            ws.cell(row=row, column=3, value=f"{anchor['price']:.1f}")
            ws.cell(row=row, column=4, value=f"{anchor['similarity']:.3f}")
            
            # 所有特征值
            col = 5
            for feature in ordered_features:
                value = features.get(feature, 0)
                # 处理不同类型的值
                if isinstance(value, (list, tuple)):
                    # 列表或元组转换为字符串
                    display_value = str(value) if len(str(value)) < 50 else f"[{len(value)}项]"
                elif isinstance(value, dict):
                    # 字典转换为字符串
                    display_value = f"{{dict:{len(value)}项}}"
                elif isinstance(value, float):
                    # 浮点数格式化
                    if value > 1000:
                        display_value = f"{value:.0f}"
                    else:
                        display_value = f"{value:.2f}"
                elif isinstance(value, (int, str)):
                    # 整数和字符串直接使用
                    display_value = value
                else:
                    # 其他类型转换为字符串
                    display_value = str(value)
                
                ws.cell(row=row, column=col, value=display_value)
                col += 1
            
            # 设置字体
            for c in range(1, col + 1):
                ws.cell(row=row, column=c).font = normal_font
        
        # 动态调整列宽
        column_widths = [6, 15, 10, 8]  # 序号、角色ID、价格、相似度
        
        # 为每个特征设置合适的列宽
        for feature in ordered_features:
            feature_name = self._get_feature_display_name(feature)
            if len(feature_name) > 8:
                column_widths.append(12)
            elif len(feature_name) > 6:
                column_widths.append(10)
            else:
                column_widths.append(8)
        
        column_widths.append(25)  # 藏宝阁链接
        
        # 应用列宽
        for col, width in enumerate(column_widths, 1):
            if col <= 26:  # A-Z
                ws.column_dimensions[chr(64+col)].width = width
            else:  # AA, AB, AC...
                first_char = chr(64 + (col - 1) // 26)
                second_char = chr(65 + (col - 1) % 26)
                ws.column_dimensions[f'{first_char}{second_char}'].width = width
        
        # 设置筛选
        last_col = chr(64 + len(headers)) if len(headers) <= 26 else f"{chr(64 + len(headers) // 26)}{chr(65 + (len(headers) - 1) % 26)}"
        ws.auto_filter.ref = f"A1:{last_col}{len(anchors)+1}"
        
        # 冻结前4列（序号、角色ID、价格、相似度）
        ws.freeze_panes = 'E2'
        
        print(f"已导出 {len(anchors)} 个相似角色到Excel，包含 {len(ordered_features)} 个特征列")
    
    def _get_feature_display_name(self, feature_name: str) -> str:
        """获取特征的显示名称"""
        display_names = {
            # 基础属性
            'level': '角色等级',
            'all_new_point': '乾元丹',
            'sum_exp': '总经验(亿)',
            'three_fly_lv': '化圣等级',
            'nine_fight_level': '生死劫等级',
            
            # 修炼等级
            'expt_ski1': '攻击修炼',
            'expt_ski2': '防御修炼',
            'expt_ski3': '法术修炼',
            'expt_ski4': '抗法修炼',
            'expt_ski5': '猎术修炼',
            'total_cultivation': '总修炼等级',
            
            # 修炼上限
            'max_expt1': '攻击修炼上限',
            'max_expt2': '防御修炼上限',
            'max_expt3': '法术修炼上限',
            'max_expt4': '抗法修炼上限',
            
            # 召唤兽修炼
            'beast_ski1': '召唤兽攻击修炼',
            'beast_ski2': '召唤兽防御修炼',
            'beast_ski3': '召唤兽法术修炼',
            'beast_ski4': '召唤兽抗法修炼',
            'total_beast_cultivation': '召唤兽总修炼',
            
            # 门派与技能
            'school_history_count': '历史门派数',
            'life_skills_count': '生活技能数量',
            
            # 装备与道具
            'premium_fabao_count': '高价值法宝数量',
            'premium_pet_count': '特殊宠物数量',
            'hight_grow_rider_count': '高成长坐骑数量',
            'packet_page': '行囊页数',
            'allow_pet_count': '召唤兽上限',
            'learn_cash': '储备金',
            'xianyu_amount': '仙玉数量',
            'jiyuan_amount': '机缘数量',
            
            # 外观和神器系统
            'shenqi_score': '神器得分',
            'limited_skin_score': '限量锦衣得分',
            'limited_huge_horse_score': '限量祥瑞得分',
        }
        return display_names.get(feature_name, feature_name)


if __name__ == "__main__":
    # 测试代码
    try:
        # 初始化估价器
        valuator = MarketAnchorEValuator()
        
        # 构造测试角色特征
        test_features = {
            'level': 129,
            'expt_ski2': 21,       # 防御修炼
            'expt_ski3': 21,       # 法术修炼
            'expt_ski4': 21,       # 抗法修炼
            'beast_ski1': 20,      # 召唤兽攻击修炼
            'beast_ski2': 20,      # 召唤兽防御修炼
            'beast_ski3': 20,      # 召唤兽法术修炼
            'beast_ski4': 20,      # 召唤兽抗法修炼
            'avg_school_skills': 150  # 师门技能平均值
        }
        
        # 计算派生特征
        test_features['total_cultivation'] = test_features.get('expt_ski1', 0) + test_features.get('expt_ski2', 0) + test_features.get('expt_ski3', 0) + test_features.get('expt_ski4', 0)
        test_features['total_beast_cultivation'] = test_features.get('beast_ski1', 0) + test_features.get('beast_ski2', 0) + test_features.get('beast_ski3', 0) + test_features.get('beast_ski4', 0)
        
        print("=== 测试角色特征 ===")
        for key, value in test_features.items():
            print(f"{key}: {value}")
        
        # 测试估价
        print("\n=== 开始估价测试 ===")
        
        # 公允价值估价
        fair_result = valuator.calculate_value(test_features, 'fair_value')
        print(f"\n公允价值估价: {fair_result['estimated_price']:.1f}")
        print(f"锚点数量: {fair_result['anchor_count']}")
        print(f"置信度: {fair_result['confidence']:.2f}")
        
        # 竞争性估价
        competitive_result = valuator.calculate_value(test_features, 'competitive')
        print(f"\n竞争性估价: {competitive_result['estimated_price']:.1f}")
        
        # 溢价估价
        premium_result = valuator.calculate_value(test_features, 'premium')
        print(f"\n溢价估价: {premium_result['estimated_price']:.1f}")
        
        # 生成价值分布报告
        print("\n=== 生成价值分布报告 ===")
        report = valuator.value_distribution_report(test_features)
        
        if 'error' not in report:
            print(f"价格范围: {report['min_price']:.1f} - {report['max_price']:.1f}")
            print(f"中位价格: {report['median_price']:.1f}")
            print(f"推荐竞争价格: {report['recommended_competitive']:.1f}")
            print(f"推荐公允价格: {report['recommended_fair']:.1f}")
            print(f"锚点数量: {report['anchor_count']}")
        else:
            print(f"报告生成失败: {report['error']}")
        
        # 测试Excel导出
        print("\n=== 测试Excel导出 ===")
        excel_file = valuator.export_valuation_report_to_excel(test_features)
        print(f"Excel报告已生成: {excel_file}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc() 