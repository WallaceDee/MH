"""
饰品插件

专门处理饰品装备的估价逻辑，重点关注初灵
"""

from src.evaluator.mark_anchor.equip.index import EquipmentTypePlugin
import sys
import os
from typing import Dict, Any, List, Optional, Tuple

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))))
sys.path.insert(0, project_root)


class NecklacePlugin(EquipmentTypePlugin):
    """饰品装备插件 - 专注初灵估价
    【饰品】
    60级 灵力（80～105）
    70级 灵力（93～120）
    80级 灵力（106～137）
    90级  灵力（118～153）
    100级 灵力（131～170）
    110级 灵力（143～186）
    120级 灵力（156～202）
    130级 灵力（169～219）
    140级 灵力（181～235）
    """

    @property
    def plugin_name(self) -> str:
        return "项链(kindid:21)专用插件"

    @property
    def supported_kindids(self) -> List[int]:
        return [21]  # 饰品的kindid

    @property
    def priority(self) -> int:
        return 100  # 高优先级

    def get_derived_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """饰品派生特征"""
        derived = {}

        # 获取装备等级和基础属性
        equip_level = features.get('equip_level', 1)
        init_wakan = features.get('init_wakan', 0)

        # 计算初灵标准化得分（饰品特有）
        wakan_score = self._calculate_wakan_score(
            equip_level, init_wakan)
        derived['wakan_score'] = wakan_score

        return derived


    def _calculate_wakan_score(self, equip_level: int, init_wakan: int) -> float:
        """
        计算初灵标准化得分（0-100分）

        Args:
            equip_level: 装备等级
            init_wakan: 初始初灵值

        Returns:
            float: 初灵得分（0-100）
        """
        # 定义各等级初灵标准区间
        wakan_standards = {
            # 区间1：60-80
            60: (80, 105),   # 最低～最高
            70: (93, 120),
            80: (106, 137),
            # 区间2：90-100
            90: (118, 153),
            100: (131, 170),
            # 区间3：110-120
            110: (143, 186),
            120: (156, 202),
            # 区间4：130-140
            130: (169, 219),
            140: (181, 235),
        }

        # 找到最接近的等级标准
        closest_level = min(wakan_standards.keys(),
                            key=lambda x: abs(x - equip_level))
        min_wakan, max_wakan = wakan_standards[closest_level]

        # 计算标准化得分
        if init_wakan <= min_wakan:
            # 低于最低标准
            score = max(0, (init_wakan / min_wakan) * 50)  # 0-50分
        elif init_wakan >= max_wakan:
            # 达到或超过最高标准
            excess_ratio = (init_wakan - max_wakan) / max_wakan
            # 100分+超出奖励，最高120分再压缩到100
            score = min(100, 100 + excess_ratio * 20)
            score = min(100, score)
        else:
            # 在标准区间内
            ratio = (init_wakan - min_wakan) / (max_wakan - min_wakan)
            score = 50 + ratio * 50  # 50-100分

        return round(score, 1)

    def get_weight_overrides(self, kindid: int = None) -> Dict[str, float]:
        """饰品权重覆盖配置"""
        return {
            'init_wakan': 2.0,                # 初灵
            'wakan_score': 3.0,               # 初灵标准化得分很重要
            'gem_score': 3.0,                   # 宝石重要但不是最重要
        }

    def get_tolerance_overrides(self, kindid: int = None) -> Dict[str, float]:
        """饰品相对容忍度覆盖配置（已废弃绝对容忍度）"""
        return {
            'init_wakan': 1,                  # 初灵
            'wakan_score': 0.12,              # 初灵标准化得分容忍度小
            'gem_score': 0.5,                 # 宝石得分容忍度中等
        }

    def calculate_custom_similarity(self,
                                    feature_name: str,
                                    target_val: Any,
                                    market_val: Any) -> Optional[float]:
        """饰品自定义相似度计算"""

        if feature_name == 'wakan_score':
            # 初灵标准化得分：使用分档计算
            if target_val == 0 and market_val == 0:
                return 1.0

            if target_val == 0 or market_val == 0:
                return 0.1

            def get_wakan_tier(score):
                if score >= 85:
                    return 'S'
                elif score >= 70:
                    return 'A'
                elif score >= 55:
                    return 'B'
                elif score >= 40:
                    return 'C'
                else:
                    return 'D'

            target_tier = get_wakan_tier(target_val)
            market_tier = get_wakan_tier(market_val)

            tier_similarity = {
                ('S', 'S'): 1.0, ('S', 'A'): 0.85, ('S', 'B'): 0.6, ('S', 'C'): 0.3, ('S', 'D'): 0.1,
                ('A', 'S'): 0.85, ('A', 'A'): 1.0, ('A', 'B'): 0.8, ('A', 'C'): 0.5, ('A', 'D'): 0.2,
                ('B', 'S'): 0.6, ('B', 'A'): 0.8, ('B', 'B'): 1.0, ('B', 'C'): 0.7, ('B', 'D'): 0.3,
                ('C', 'S'): 0.3, ('C', 'A'): 0.5, ('C', 'B'): 0.7, ('C', 'C'): 1.0, ('C', 'D'): 0.6,
                ('D', 'S'): 0.1, ('D', 'A'): 0.2, ('D', 'B'): 0.3, ('D', 'C'): 0.6, ('D', 'D'): 1.0,
            }

            return tier_similarity.get((target_tier, market_tier), 0.4)

        return None  # 其他特征使用默认计算
