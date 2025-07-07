"""
腰带插件

专门处理腰带装备的估价逻辑，重点关注速度和生存属性
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


class BeltPlugin(EquipmentTypePlugin):
    """腰带装备插件 - 专注于速度和生存属性的估价"""

    @property
    def plugin_name(self) -> str:
        return "腰带(kindid:20)专用插件"

    @property
    def supported_kindids(self) -> List[int]:
        return [20]  # 腰带的kindid

    @property
    def priority(self) -> int:
        return 100  # 高优先级

    def get_derived_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """腰带派生特征"""
        derived = {}

        # 获取装备等级和基础属性
        equip_level = features.get('equip_level', 1)
        init_hp = features.get('init_hp', 0)
        init_defense = features.get('init_defense', 0)

        # 计算气血标准化得分（腰带特有）
        hp_score = self._calculate_hp_score(equip_level, init_hp)
        derived['hp_score'] = hp_score

        # 计算防御标准化得分（腰带特有）
        defense_score = self._calculate_defense_score(
            equip_level, init_defense)
        derived['defense_score'] = defense_score

        return derived

    def _calculate_hp_score(self, equip_level: int, init_hp: int) -> float:
        """
        计算气血标准化得分（0-100分）

        Args:
            equip_level: 装备等级
            init_hp: 初始气血值

        Returns:
            float: 气血得分（0-100）
        """
        # 定义各等级气血标准区间
        hp_standards = {
            # 区间1：60-80
            60: (136, 177),   # 最低～最高
            70: (157, 204),
            80: (178, 232),
            # 区间2：90-100
            90: (199, 259),
            100: (220, 286),
            # 区间3：110-120
            110: (241, 313),
            120: (250, 325),
            # 区间4：130-140
            130: (283, 368),
            140: (304, 395),
        }

        # 找到最接近的等级标准
        closest_level = min(hp_standards.keys(),
                            key=lambda x: abs(x - equip_level))
        min_hp, max_hp = hp_standards[closest_level]

        # 计算标准化得分
        if init_hp <= min_hp:
            # 低于最低标准
            score = max(0, (init_hp / min_hp) * 50)  # 0-50分
        elif init_hp >= max_hp:
            # 达到或超过最高标准
            excess_ratio = (init_hp - max_hp) / max_hp
            # 100分+超出奖励，最高120分再压缩到100
            score = min(100, 100 + excess_ratio * 20)
            score = min(100, score)
        else:
            # 在标准区间内
            ratio = (init_hp - min_hp) / (max_hp - min_hp)
            score = 50 + ratio * 50  # 50-100分

        return round(score, 1)

    def _calculate_defense_score(self, equip_level: int, init_defense: int) -> float:
        """
        计算防御标准化得分（0-100分）

        Args:
            equip_level: 装备等级
            init_defense: 初始防御值

        Returns:
            float: 防御得分（0-100）
        """
        # 定义各等级防御标准区间
        defense_standards = {
            # 区间1：60-80
            60: (36, 47),   # 最低～最高
            70: (42, 54),
            80: (47, 61),
            # 区间2：90-100
            90: (52, 68),
            100: (57, 75),
            # 区间3：110-120
            110: (63, 81),
            120: (68, 88),
            # 区间4：130-140
            130: (73, 95),
            140: (78, 102),
        }

        # 找到最接近的等级标准
        closest_level = min(defense_standards.keys(),
                            key=lambda x: abs(x - equip_level))
        min_defense, max_defense = defense_standards[closest_level]

        # 计算标准化得分
        if init_defense <= min_defense:
            # 低于最低标准
            score = max(0, (init_defense / min_defense) * 50)  # 0-50分
        elif init_defense >= max_defense:
            # 达到或超过最高标准
            excess_ratio = (init_defense - max_defense) / max_defense
            # 100分+超出奖励，最高120分再压缩到100
            score = min(100, 100 + excess_ratio * 20)
            score = min(100, score)
        else:
            # 在标准区间内
            ratio = (init_defense - min_defense) / (max_defense - min_defense)
            score = 50 + ratio * 50  # 50-100分

        return round(score, 1)

    def get_weight_overrides(self, kindid: int = None) -> Dict[str, float]:
        """腰带权重覆盖配置"""
        return {
            'init_defense': 2.0,                # 初防
            'init_hp': 2.0,                    # 血量
            'defense_score': 3.0,               # 防御标准化得分很重要
            'hp_score': 3.0,                   # 血量标准化得分最重要
            'gem_score': 3.0,                   # 宝石重要但不是最重要
        }

    def get_tolerance_overrides(self, kindid: int = None) -> Dict[str, float]:
        """腰带相对容忍度覆盖配置（已废弃绝对容忍度）"""
        return {
            'hp_score': 0.20,                  # 敏捷标准化得分容忍度极小
            'defense_score': 0.12,              # 防御标准化得分容忍度小
            'init_defense': 0.15,                   # 敏捷容忍度要小（重要）
            'init_hp': 0.20,                   # 血量容忍度要小（重要）
            'gem_score': 0.5,                  # 宝石得分容忍度中等
        }

    def calculate_custom_similarity(self,
                                    feature_name: str,
                                    target_val: Any,
                                    market_val: Any) -> Optional[float]:
        """腰带自定义相似度计算"""

        if feature_name == 'hp_score':
            # 血量标准化得分：使用分档计算
            if target_val == 0 and market_val == 0:
                return 1.0

            if target_val == 0 or market_val == 0:
                return 0.1  # 一个有血量一个没有，相似度很低

            def get_hp_tier(score):
                if score >= 90:
                    return 'S+'
                elif score >= 80:
                    return 'S'
                elif score >= 70:
                    return 'A'
                elif score >= 60:
                    return 'B'
                elif score >= 50:
                    return 'C'
                else:
                    return 'D'

            target_tier = get_hp_tier(target_val)
            market_tier = get_hp_tier(market_val)

            tier_similarity = {
                ('S+', 'S+'): 1.0, ('S+', 'S'): 0.95, ('S+', 'A'): 0.8, ('S+', 'B'): 0.5, ('S+', 'C'): 0.2, ('S+', 'D'): 0.1,
                ('S', 'S+'): 0.95, ('S', 'S'): 1.0, ('S', 'A'): 0.9, ('S', 'B'): 0.6, ('S', 'C'): 0.3, ('S', 'D'): 0.1,
                ('A', 'S+'): 0.8, ('A', 'S'): 0.9, ('A', 'A'): 1.0, ('A', 'B'): 0.8, ('A', 'C'): 0.4, ('A', 'D'): 0.1,
                ('B', 'S+'): 0.5, ('B', 'S'): 0.6, ('B', 'A'): 0.8, ('B', 'B'): 1.0, ('B', 'C'): 0.6, ('B', 'D'): 0.2,
                ('C', 'S+'): 0.2, ('C', 'S'): 0.3, ('C', 'A'): 0.4, ('C', 'B'): 0.6, ('C', 'C'): 1.0, ('C', 'D'): 0.5,
                ('D', 'S+'): 0.1, ('D', 'S'): 0.1, ('D', 'A'): 0.1, ('D', 'B'): 0.2, ('D', 'C'): 0.5, ('D', 'D'): 1.0,
            }

            return tier_similarity.get((target_tier, market_tier), 0.3)

        elif feature_name == 'defense_score':
            # 防御标准化得分：使用分档计算
            if target_val == 0 and market_val == 0:
                return 1.0

            if target_val == 0 or market_val == 0:
                return 0.1

            def get_defense_tier(score):
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

            target_tier = get_defense_tier(target_val)
            market_tier = get_defense_tier(market_val)

            tier_similarity = {
                ('S', 'S'): 1.0, ('S', 'A'): 0.85, ('S', 'B'): 0.6, ('S', 'C'): 0.3, ('S', 'D'): 0.1,
                ('A', 'S'): 0.85, ('A', 'A'): 1.0, ('A', 'B'): 0.8, ('A', 'C'): 0.5, ('A', 'D'): 0.2,
                ('B', 'S'): 0.6, ('B', 'A'): 0.8, ('B', 'B'): 1.0, ('B', 'C'): 0.7, ('B', 'D'): 0.3,
                ('C', 'S'): 0.3, ('C', 'A'): 0.5, ('C', 'B'): 0.7, ('C', 'C'): 1.0, ('C', 'D'): 0.6,
                ('D', 'S'): 0.1, ('D', 'A'): 0.2, ('D', 'B'): 0.3, ('D', 'C'): 0.6, ('D', 'D'): 1.0,
            }

            return tier_similarity.get((target_tier, market_tier), 0.4)

        return None  # 其他特征使用默认计算
