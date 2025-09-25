from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl import Workbook
import warnings
from datetime import datetime
import logging
from typing import Dict, Any, List, Optional, Union, Tuple

from src.evaluator.market_anchor.pet.pet_market_data_collector import PetMarketDataCollector
from src.evaluator.utils.extreme_value_filter import ExtremeValueFilter
from src.evaluator.utils.base_valuator import BaseValuator

warnings.filterwarnings('ignore')


class PetMarketAnchorEvaluator(BaseValuator):
    """市场锚定估价器 - 基于市场相似召唤兽的价格锚定估价"""

    def __init__(self, market_data_collector: Optional[PetMarketDataCollector] = None):
        super().__init__()
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
            "role_grade_limit": 0.5,
            "growth": 0.1,
            "lx": 0.1,
            "skill_count": 0,
            "texing": 0,
            "neidan_count": 0.2,
            "equip_level":0.8,
            "is_baobao":0,
            "evol_skill_list_value":0.5
        }

        # 定义关键特征权重（用于相似度计算）
        self.feature_weights = {
            "role_grade_limit": 1,
            "growth": 0.2,
            "lx": 0.3,
            "skill_count": 0.2,
            "texing": 0.2,
            "neidan_count": 0.2,
            "equip_level":0.8,
            "is_baobao":0.2,
            "evol_skill_list_value":0.2
        }

        print("市场锚定估价器初始化完成")

    def find_market_anchors(self,
                            target_features: Dict[str, Any],
                            similarity_threshold: float = 0.7,
                            max_anchors: int = 30,
                            verbose: bool = True) -> List[Dict[str, Any]]:
        """
        寻找市场锚点召唤兽

        Args:
            target_features: 目标召唤兽特征字典
            similarity_threshold: 相似度阈值（0-1）
            max_anchors: 最大锚点数量
            verbose: 是否显示详细调试日志

        Returns:
            List[Dict[str, Any]]: 锚点召唤兽列表，每个元素包含：
                - similarity: 相似度分数
                - price: 价格
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
            market_data = self.market_collector.get_market_data_with_business_rules(
                pre_filters)

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
                    similarity = self._calculate_similarity(
                        target_features, market_row.to_dict())
                    if similarity >= similarity_threshold:
                        # 提取价格，如果有equip_list_amount则减去装备估价
                        total_price = market_row.get('price', 0)
                        equip_list_amount = market_row.get('equip_list_amount', 0)
                        # TODO:带装备只算了裸价，没有算装备价格？怎么办？
                        # 计算纯召唤兽价格（总价格减去装备估价）
                        pet_price = total_price - equip_list_amount
                        if equip_list_amount > 0:
                            print({
                                'total_price': total_price,
                                'equip_list_amount': equip_list_amount,
                                'pet_price': pet_price
                            })
                        if pet_price < 0:
                            pet_price = 0  # 确保价格不为负数
                        
                        anchor_candidates.append({
                            'equip_sn': current_equip_sn,
                            'similarity': round(float(similarity), 3),
                            'price': pet_price,  # 使用纯召唤兽价格
                            'total_price': total_price,  # 保留总价格用于参考
                            'equip_list_amount': equip_list_amount,  # 保留装备估价用于参考
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
                self.logger.warning(
                    f"数据处理统计: 总数={processed_count}, 成功={success_count}, 失败={error_count}, 排除自身={excluded_self_count}")

            # 按相似度排序
            anchor_candidates.sort(key=lambda x: x['similarity'], reverse=True)
            # 返回前N个锚点
            anchors = anchor_candidates[:max_anchors]
            # 对锚点进行极端值过滤
            if anchors:
                anchors = self.extreme_value_filter.filter_anchors_for_extreme_values(anchors)
            print(f"找到 {len(anchors)} 个市场锚点召唤兽")
            if anchors:
                print(
                    f"相似度范围: {anchors[-1]['similarity']:.3f} - {anchors[0]['similarity']:.3f}")
                print(
                    f"价格范围: {min(a['price'] for a in anchors):.1f} - {max(a['price'] for a in anchors):.1f}")

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
        filters = {**target_features}
        print(f"_build_pre_filters {filters}")
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
            # 收集所有特征的计算结果，用于按得分排序输出
            feature_results = []
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

                # 计算加权得分
                weighted_score = feature_similarity * weight

                # 收集特征结果
                feature_results.append({
                    'name': feature_name,
                    'target_val': target_val,
                    'market_val': market_val,
                    'weight': weight,
                    'similarity': feature_similarity,
                    'weighted_score': weighted_score
                })

                weighted_similarity += feature_similarity * weight
                total_weight += weight

            # 按加权得分降序排序并输出
            feature_results.sort(key=lambda x: x['weight'], reverse=True)

            # 添加特征权重日志
            print(f"\n=== 相似度计算详情  ===")
            print("特征名称                 | 目标值    | 市场值    | 权重     | 相似度   | 加权得分")
            print("-" * 90)

            for result in feature_results:
                if result['weight'] > 0.1:
                    print(f"{result['name']:20s} | {str(result['target_val']):>8s} | {str(result['market_val']):>8s} | {result['weight']:7.2f} | {result['similarity']:7.3f} | {result['weighted_score']:7.3f}")

            print("-" * 90)
            print(
                f"{'总计':20s} | {'':8s} | {'':8s} | {total_weight:7.2f} | {'':7s} | {weighted_similarity:7.3f}")
            print(
                f"最终相似度: {weighted_similarity:.3f} / {total_weight:.3f} = {weighted_similarity/total_weight if total_weight > 0 else 0:.3f}")
            print("=" * 90)
            # 计算加权平均相似度
            if total_weight > 0:
                final_similarity = weighted_similarity / total_weight
            else:
                final_similarity = 0.0

            return final_similarity

        except Exception as e:
            self.logger.error(f"计算相似度失败: {e}")
            return 0.0