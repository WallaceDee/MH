import sys
import os

# 添加项目根目录到Python路径，解决模块导入问题
from src.utils.project_path import get_project_root
project_root = get_project_root()
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
from .market_data_collector import MarketDataCollector
from .utils.base_valuator import BaseValuator


warnings.filterwarnings('ignore')


class MarketAnchorEvaluator(BaseValuator):
    """市场锚定估价器 - 基于市场相似角色的价格锚定估价"""
    
    def __init__(self, market_data_collector: Optional[MarketDataCollector] = None):
        super().__init__()
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
        
        # 相对容忍度：统一配置所有特征的相对差值比例
        self.relative_tolerances = {
            'gender':0.0,   # 性别必须一致
            'server_heat':0.1,   # 服务器热度容忍度10%
            # 修炼系统特征 - 相对容忍度
            'expt_ski1': 0.05,       # 主修炼容忍度5%
            'expt_ski2': 0.05,       # 防御修炼容忍度5%
            'expt_ski3': 0.25,       # 副修炼容忍度25%
            'expt_ski4': 0.05,       # 抗法修炼容忍度5%
            'expt_ski5': 0.10,       # 猎术修炼容忍度10%
            'beast_ski1': 0.05,      # 召唤兽攻击修炼容忍度5%
            'beast_ski2': 0.05,      # 召唤兽防御修炼容忍度5%
            'beast_ski3': 0.05,      # 召唤兽法术修炼容忍度5%
            'beast_ski4': 0.05,      # 召唤兽抗法修炼容忍度5%
            'total_cultivation': 0.1,  # 总修炼容忍度5%
            'total_beast_cultivation': 0.1,  # 召唤兽总修炼容忍度5%
            
            # 等级和关键特征
            'level': 0.25,           # 等级容忍度25%
            'all_new_point': 0.0,    # 乾元丹必须完全一致
            'three_fly_lv': 0.0,     # 化圣等级必须一致
            'school_history_count': 0.20,  # 历史门派数容忍度20%
            'packet_page': 0.15,     # 行囊页数容忍度15%
            'sum_amount': 0.15, # 召唤兽上限容忍度15%
            
            # 召唤兽和法宝系统
            'hight_grow_rider_count': 0.25, # 高成长坐骑容忍度25%
            
            # 特殊状态
            'qianyuandan_breakthrough': 0.0,  # 乾元丹突破必须一致
            
            # 经验和成长系统
            'sum_exp': 0.5,         # 总经验容忍度50%
            'yushoushu_skill': 1.0,  # 育兽术等级容忍度100%
            
            # 其他增值系统
            'lingyou_count': 0.50,   # 灵佑次数容忍度50%
            'jiyuan_amount': 0.50,   # 机缘值容忍度50%
            'xianyu_amount': 0.8,   # 仙玉容忍度80%
            'learn_cash': 0.80,      # 储备金容忍度80%
            
            # 技能系统 - 组合特征
            'avg_school_skills': 0.05,      # 师门技能平均值容忍度5%
            'high_life_skills_count': 0.20, # 高等级生活技能数量容忍度20%
            'total_qiangzhuang_shensu': 0.10, # 强壮神速总和容忍度10%
            
            # 外观和神器系统
            'shenqi_score': 0.80,           # 神器得分容忍度50%
            'limited_skin_value': 0.5,     # 限量锦衣价值容忍度50%
            'limited_huge_horse_value': 0.5, # 限量祥瑞得分容忍度50%
        }
        
        # 定义关键特征权重（用于相似度计算）
        self.feature_weights = {
            # 最重要特征 
            'server_heat': 1, # 服务器热度
            # 修炼细节特征 - 提高权重以增强影响力
            'expt_ski1': 1, 'expt_ski2': 1, 'expt_ski3': 0.5, 'expt_ski4': 1, 'expt_ski5': 0.4,
            'beast_ski1': 1, 'beast_ski2': 1, 'beast_ski3': 1, 'beast_ski4': 1,
            # 乾元丹和乾元丹突破
            'all_new_point': 1.0,
            'qianyuandan_breakthrough': 1.0,
            
            # 很重要特征 - 显著影响价值
            'total_beast_cultivation': 1, # 召唤兽总修炼
            'total_cultivation': 0.5, # 总修炼
            
            # 重要特征 - 中等影响
            'avg_school_skills': 0.8,
            'three_fly_lv': 1.0, # 化圣等级
            'total_qiangzhuang_shensu': 1.0, # 强壮神速总和
            'school_history_count': 0.6, # 历史门派数
            'high_life_skills_count': 0.6, # 高等级生活技能数量
         
            # 辅助特征 - 较低权重
            'level': 0.5, # 等级
            'lingyou_count': 0.4, # 灵佑次数    
            'hight_grow_rider_count': 1.0, # 高成长坐骑数量
            
            # 外观和神器特征 - 中等权重
            'shenqi_score': 1.0, # 神器得分
            'limited_skin_value': 1.0, # 限量锦衣价值（直接使用价值而非得分）
            'limited_huge_horse_value': 1.0, # 限量祥瑞价值（直接使用价值而非得分）
            # 'limited_skin_score': 0.5, # 限量锦衣得分（不再使用）
            # 'limited_huge_horse_score': 0.5, # 限量祥瑞得分（不再使用）
            
            # 次要特征 - 低权重
            'jiyuan_amount': 1.0, # 机缘值
            
            # 可选特征 - 最低权重
            'yushoushu_skill': 0.1,
            'xianyu_amount': 0.1,
            'learn_cash': 0.1,
            'sum_exp': 0.1,
            'packet_page': 0.1,
            'sum_amount': 0.1,
            'gender': 0.1,
        }
        
        print("市场锚定估价器初始化完成")
    
    def find_market_anchors(self, 
                           target_features: Dict[str, Any],
                           similarity_threshold: float = 0.7,
                           max_anchors: int = 30,
                           verbose: bool = True) -> List[Dict[str, Any]]:
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
                - eid: 角色藏宝阁上架ID
                - features: 完整特征数据
        """
        try:
            print(f"[MARKET_ANCHOR] 开始寻找市场锚点，相似度阈值: {similarity_threshold}")
            print(f"[MARKET_ANCHOR] 目标特征类型: {type(target_features)}")
            print(f"[MARKET_ANCHOR] 目标特征字段: {list(target_features.keys()) if isinstance(target_features, dict) else 'not dict'}")
            
            self.logger.info(f"[FIND_ANCHORS] 开始寻找市场锚点，相似度阈值: {similarity_threshold}")
            self.logger.debug(f"[FIND_ANCHORS] 目标特征: {target_features}")
            
            # 构建预过滤条件以提高效率
            print(f"[MARKET_ANCHOR] 开始构建预过滤条件...")
            pre_filters = self._build_pre_filters(target_features)
            print(f"[MARKET_ANCHOR] 预过滤条件构建完成: {pre_filters}")
            self.logger.debug(f"[FIND_ANCHORS] 预过滤条件: {pre_filters}")
            
            # 获取预过滤的市场数据
            self.logger.info(f"[FIND_ANCHORS] 开始获取市场数据...")
            market_data = self.market_collector.get_market_data_for_similarity(pre_filters)
            self.logger.info(f"[FIND_ANCHORS] 市场数据获取完成，类型: {type(market_data)}")
            
            if market_data.empty:
                self.logger.warning("[FIND_ANCHORS] 市场数据为空，无法找到锚点")
                return []
            
            self.logger.info(f"[FIND_ANCHORS] 预过滤后获得 {len(market_data)} 条候选数据")
            self.logger.debug(f"[FIND_ANCHORS] 市场数据列名: {list(market_data.columns)}")
            
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
            
            self.logger.info(f"[FIND_ANCHORS] 开始计算相似度，处理 {len(market_data)} 条数据")
            
            for i, (eid, market_row) in enumerate(market_data.iterrows()):
                try:
                    if i < 3:  # 只记录前3条的详细日志，避免日志过多
                        self.logger.debug(f"[FIND_ANCHORS] 处理第 {i+1} 条数据，eid: {eid}")
                        self.logger.debug(f"[FIND_ANCHORS] market_row类型: {type(market_row)}")
                    
                    # 计算相似度 - 确保数据类型转换
                    market_dict = self._convert_pandas_row_to_dict(market_row)
                    
                    if i < 3:
                        self.logger.debug(f"[FIND_ANCHORS] market_dict转换完成，包含 {len(market_dict)} 个字段")
                    
                    similarity = self._calculate_similarity(target_features, market_dict, verbose=verbose and i < 3)
                    
                    if similarity >= similarity_threshold:
                        anchor_candidates.append({
                            'eid': eid,
                            'similarity': round(float(similarity), 3),
                            'price': float(market_row.get('price', 0)),
                            'features': market_dict
                        })
                        
                except Exception as e:
                    self.logger.error(f"处理角色 {eid} 时出错")
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
        
        self.logger.debug(f"[BUILD_FILTERS] 开始构建预过滤条件，目标特征: {target_features}")
        
        # 等级过滤（±30级）
        if 'level' in target_features:
            level = target_features['level']
            level_range = (max(1, level - 0), level + 0)
            filters['level_range'] = level_range
            self.logger.debug(f"[BUILD_FILTERS] 等级过滤: {level_range} (目标等级: {level})")
            

        return filters
    
    def _calculate_similarity(self, 
                            target_features: Dict[str, Any], 
                            market_features: Dict[str, Any],
                            verbose: bool = False) -> float:
        """
        计算两个角色特征的相似度
        
        Args:
            target_features: 目标角色特征
            market_features: 市场角色特征
            verbose: 是否显示详细调试日志
            
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
            
            # 获取所有特征名称
            all_features = set(self.relative_tolerances.keys())
            
            # 实现门派修炼智能匹配逻辑
            # 在梦幻西游中，物理门派主修攻击修炼(expt_ski1)，法术门派主修法术修炼(expt_ski3)
            # 两者价值等同，需要智能匹配最优组合
            target_features_adjusted = self._adjust_cultivation_features(target_features)
            market_features_adjusted = self._adjust_cultivation_features(market_features)
            
            # 收集所有特征的计算结果，用于按得分排序输出
            feature_results = []
            
            for feature_name in all_features:
                if feature_name not in target_features_adjusted and feature_name not in market_features_adjusted:
                    continue
                    
                target_val = target_features_adjusted.get(feature_name, 0)
                market_val = market_features_adjusted.get(feature_name, 0)
                
                # 安全处理None值
                if target_val is None:
                    target_val = 0
                if market_val is None:
                    market_val = 0
                
                weight = self.feature_weights.get(feature_name, 0.5)
                
                # 权重为0的特征不参与计算
                if weight == 0:
                    continue
                
                # 计算特征相似度 - 统一使用相对容忍度
                calculation_method = ""
                if target_val == 0 and market_val == 0:
                    # 两者都为0，完全匹配
                    feature_similarity = 1.0
                    calculation_method = "零值匹配"
                # 删除冗余代码，因为容忍度为0的特征已经在下面的逻辑中处理
                elif feature_name in self.relative_tolerances:
                    # 使用相对容忍度计算
                    tolerance = self.relative_tolerances[feature_name]
                    
                    if tolerance == 0.0:
                        # 容忍度为0表示必须完全一致
                        feature_similarity = 1.0 if target_val == market_val else 0.0
                        calculation_method = "精确匹配"
                    # 删除重复的零值判断，因为在外层已经处理过
                    elif target_val == 0 or market_val == 0:
                        # 一个为0一个不为0，给予部分相似度
                        feature_similarity = 0.1
                        calculation_method = "零值处理"
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
                        calculation_method = f"相对容忍({tolerance:.2f})"
                else:
                    # 未配置的特征，使用默认逻辑
                    if target_val == market_val:
                        feature_similarity = 1.0
                    else:
                        feature_similarity = 0.5  # 给予中等相似度
                    calculation_method = "默认逻辑"
                
                # 计算加权得分
                weighted_score = feature_similarity * weight
                
                # 收集特征结果
                feature_results.append({
                    'name': feature_name,
                    'target_val': target_val,
                    'market_val': market_val,
                    'weight': weight,
                    'similarity': feature_similarity,
                    'weighted_score': weighted_score,
                    'method': calculation_method
                })
                
                weighted_similarity += feature_similarity * weight
                total_weight += weight
            
            # 按权重降序排序并输出调试信息
            feature_results.sort(key=lambda x: x['weight'], reverse=True)

            # 添加特征权重日志
            if verbose:
                print(f"\n=== 角色相似度计算详情 ===")
                print("特征名称                 | 目标值    | 市场值    | 权重     | 相似度   | 加权得分 | 计算方法")
                print("-" * 100)

                for result in feature_results:
                    if result['weight'] > 0.05:  # 只显示权重大于0.05的特征
                        # 格式化数值显示
                        target_val_str = f"{result['target_val']:.2f}" if isinstance(result['target_val'], float) else str(result['target_val'])
                        market_val_str = f"{result['market_val']:.2f}" if isinstance(result['market_val'], float) else str(result['market_val'])
                        
                        print(f"{result['name']:20s} | {target_val_str:>8s} | {market_val_str:>8s} | {result['weight']:7.2f} | {result['similarity']:7.3f} | {result['weighted_score']:7.3f} | {result['method']}")

                print("-" * 100)
                print(f"{'总计':20s} | {'':8s} | {'':8s} | {total_weight:7.2f} | {'':7s} | {weighted_similarity:7.3f} | {'':>12s}")
                final_similarity = weighted_similarity / total_weight if total_weight > 0 else 0.0
                print(f"最终相似度: {weighted_similarity:.3f} / {total_weight:.3f} = {final_similarity:.3f}")
                print("=" * 100)

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

            # 召唤兽总修炼保持原值，不重新计算
            # total_beast_cultivation 保持原始值
            
            return adjusted_features
            
        except Exception as e:
            self.logger.error(f"调整人物修炼特征失败: {e}")
            return features
    
    def _convert_pandas_row_to_dict(self, row) -> Dict[str, Any]:
        """
        将pandas行数据转换为Python原生类型的字典
        
        Args:
            row: pandas Series对象
            
        Returns:
            Dict[str, Any]: 转换后的字典，所有数值都是Python原生类型
        """
        try:
            raw_dict = row.to_dict()
            converted_dict = {}
            
            for key, value in raw_dict.items():
                if value is None:
                    converted_dict[key] = None
                elif isinstance(value, (np.integer, np.int64, np.int32)):
                    converted_dict[key] = int(value)
                elif isinstance(value, (np.floating, np.float64, np.float32)):
                    converted_dict[key] = float(value)
                elif isinstance(value, np.ndarray):
                    converted_dict[key] = value.tolist()
                elif isinstance(value, (list, tuple)):
                    # 递归处理列表中的numpy类型
                    converted_dict[key] = self._convert_list_types(value)
                elif isinstance(value, dict):
                    # 递归处理字典中的numpy类型
                    converted_dict[key] = self._convert_dict_types(value)
                else:
                    converted_dict[key] = value
            
            return converted_dict
            
        except Exception as e:
            self.logger.error(f"转换pandas行数据失败: {e}")
            # 降级到原始to_dict()方法
            return row.to_dict()
    
    def _convert_list_types(self, data_list) -> List[Any]:
        """递归转换列表中的numpy类型"""
        converted_list = []
        for item in data_list:
            if isinstance(item, (np.integer, np.int64, np.int32)):
                converted_list.append(int(item))
            elif isinstance(item, (np.floating, np.float64, np.float32)):
                converted_list.append(float(item))
            elif isinstance(item, np.ndarray):
                converted_list.append(item.tolist())
            elif isinstance(item, list):
                converted_list.append(self._convert_list_types(item))
            elif isinstance(item, dict):
                converted_list.append(self._convert_dict_types(item))
            else:
                converted_list.append(item)
        return converted_list
    
    def _convert_dict_types(self, data_dict) -> Dict[str, Any]:
        """递归转换字典中的numpy类型"""
        converted_dict = {}
        for key, value in data_dict.items():
            if isinstance(value, (np.integer, np.int64, np.int32)):
                converted_dict[key] = int(value)
            elif isinstance(value, (np.floating, np.float64, np.float32)):
                converted_dict[key] = float(value)
            elif isinstance(value, np.ndarray):
                converted_dict[key] = value.tolist()
            elif isinstance(value, list):
                converted_dict[key] = self._convert_list_types(value)
            elif isinstance(value, dict):
                converted_dict[key] = self._convert_dict_types(value)
            else:
                converted_dict[key] = value
        return converted_dict