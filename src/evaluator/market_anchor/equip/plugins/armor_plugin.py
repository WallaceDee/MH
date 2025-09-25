"""
衣服插件

专门处理衣服装备的估价逻辑，重点关注防御和属性加成
"""

from src.evaluator.market_anchor.equip.index import EquipmentTypePlugin
import sys
import os
from typing import Dict, Any, List, Optional, Tuple

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))))
sys.path.insert(0, project_root)


class ArmorPlugin(EquipmentTypePlugin):
    """衣服装备插件 - 专注于防御和属性加成的估价"""

    @property
    def plugin_name(self) -> str:
        return "衣服(kindid:18、59)专用插件"

    @property
    def supported_kindids(self) -> List[int]:
        return [18,59]  # 衣服的kindid

    @property
    def priority(self) -> int:
        return 100  # 高优先级

    def get_derived_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """衣服派生特征"""
        derived = {}

        # 获取装备等级和基础属性
        equip_level = features.get('equip_level', 1)
        init_defense = features.get('init_defense', 0)
        addon_minjie = features.get('addon_minjie', 0) #敏捷
        addon_liliang = features.get('addon_liliang', 0) #力量
        addon_naili = features.get('addon_naili', 0) #耐力
        addon_tizhi = features.get('addon_tizhi', 0) #体质
        addon_moli = features.get('addon_moli', 0) #魔力
        addon_total = features.get('addon_total', 0) #附加属性总和

        # 计算防御标准化得分（衣服特有）
        defense_score = self._calculate_defense_score(
            equip_level, init_defense)
        derived['defense_score'] = defense_score

        # 计算附加属性总和标准化得分
        # 如果addon_minjie、addon_liliang、addon_naili、addon_tizhi、addon_moli中有两个属性点是正整数则属于双加
        # 如果addon_minjie、addon_liliang、addon_naili、addon_tizhi、addon_moli中有一个属性点是正整数且没有其它属性点为正整数则属于单加
        # 单加和双加的上限不一样，双加的addon_total上限要高一些
        addon_total_score = self._calculate_addon_total_score(
            equip_level, addon_total, addon_minjie, addon_liliang, addon_naili, addon_tizhi, addon_moli)
        derived['addon_total_score'] = addon_total_score

        return derived

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
            60: (105, 136),   # 最低～最高
            70: (120, 156),
            80: (136, 177),
            # 区间2：90-100
            90: (152, 197),
            100: (168, 218),
            # 区间3：110-120
            110: (183, 238),
            120: (190, 247),
            # 区间4：130-140
            130: (215, 279),
            140: (231, 300),
            # 区间5：150-160
            150: (246, 320),
            160: (249, 340),
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

    def _calculate_addon_total_score(self, equip_level: int, addon_total: int, addon_minjie: int, addon_liliang: int, addon_naili: int, addon_tizhi: int, addon_moli: int) -> float:
        """
        计算附加属性总和标准化得分（0-100分）
        # 等级|单加上限|双加上限
        # 60| 22| 28
        # 70| 26| 34
        # 80| 30| 40
        # 90| 30| 42
        # 100| 34| 48
        # 110| 36| 52
        # 120| 38| 56
        # 130| 42| 64
        # 140| 45| 66
        Args:
            equip_level: 装备等级
            addon_total: 附加属性总和


        Returns:
            float: 附加属性总和得分（0-100）
        """
        # 定义各等级附加属性总和标准区间
        addon_total_standards = {
            # 区间1：60-80
            60: (22, 28),   # 单加最高，双加最高
            70: (26, 34),
            80: (30, 40),
            # 区间2：90-100
            90: (30, 42),
            100: (34, 48),
            # 区间3：110-120
            110: (36, 52),
            120: (38, 56),
            # 区间4：130-140
            130: (42, 64),
            140: (45, 66),
            # 区间5：150-160
            150: (48, 72),
            160: (61, 86),
        }

        # 找到最接近的等级标准
        closest_level = min(addon_total_standards.keys(),
                            key=lambda x: abs(x - equip_level))
        max_single_addon_total, max_double_addon_total = addon_total_standards[closest_level]

        # 判断是单加还是双加
        positive_attrs = [attr for attr in [addon_minjie, addon_liliang, addon_naili, addon_tizhi, addon_moli] if attr > 0]
        is_double_add = len(positive_attrs) >= 2
        
        # 根据单加或双加选择对应的上限
        if is_double_add:
            max_addon_total = max_double_addon_total
        else:
            max_addon_total = max_single_addon_total
        
        # 计算标准化得分
        if addon_total <= 0:
            # 没有附加属性
            score = 0
        elif addon_total >= max_addon_total:
            # 达到或超过最高标准
            excess_ratio = (addon_total - max_addon_total) / max_addon_total
            # 100分+超出奖励，最高120分再压缩到100
            score = min(100, 100 + excess_ratio * 20)
            score = min(100, score)
        else:
            # 在标准区间内
            ratio = addon_total / max_addon_total
            score = ratio * 100  # 0-100分
        
        # 单加装备得分打8折
        if not is_double_add:
            score = score * 0.8

        return round(score, 1)
    # TODO: 130 140 修理失败影响价钱严重
    def get_weight_overrides(self, kindid: int = None) -> Dict[str, float]:
        """衣服权重覆盖配置"""
        return {
            'init_defense': 2.0,                # 初防
            'defense_score': 3.0,               # 防御标准化得分很重要
            'addon_total_score': 3.0,          # 附加属性总和标准化得分很重要
            'addon_minjie': 1.0,               # 衣服没有附加属性
            'addon_moli': 1.0,                  # 衣服没有附加属性
            'addon_liliang': 1.0,               # 衣服没有附加属性
            'addon_tizhi': 1.0,                 # 衣服没有附加属性
            'addon_naili': 1.0,                 # 衣服没有附加属性
        }

    def get_tolerance_overrides(self, kindid: int = None) -> Dict[str, float]:
        """衣服相对容忍度覆盖配置（已废弃绝对容忍度）"""
        return {
            'dex_score': 0.08,                  # 敏捷标准化得分容忍度极小
            'defense_score': 0.12,              # 防御标准化得分容忍度小
            'addon_total_score': 0.2,         # 附加属性总和标准化得分容忍度小
            'addon_moli': 0.4,                 # 衣服没有附加属性
            'addon_lingli': 0.4,               # 衣服没有附加属性
            'addon_tizhi': 0.4,                 # 衣服没有附加属性
            'addon_naili': 0.4,                # 衣服没有附加属性
            'addon_minjie': 0.4,            # 衣服没有附加属性
        }

    def calculate_custom_similarity(self,
                                    feature_name: str,
                                    target_val: Any,
                                    market_val: Any) -> Optional[float]:
        """衣服自定义相似度计算"""
        if feature_name == 'defense_score':
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

        elif feature_name == 'addon_total_score':
            # 附加属性总和标准化得分：使用分档计算
            if target_val == 0 and market_val == 0:
                return 1.0

            if target_val == 0 or market_val == 0:
                return 0.1  # 一个有附加属性一个没有，相似度很低

            def get_addon_total_tier(score):
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

            target_tier = get_addon_total_tier(target_val)
            market_tier = get_addon_total_tier(market_val)

            tier_similarity = {
                ('S+', 'S+'): 1.0, ('S+', 'S'): 0.95, ('S+', 'A'): 0.8, ('S+', 'B'): 0.5, ('S+', 'C'): 0.2, ('S+', 'D'): 0.1,
                ('S', 'S+'): 0.95, ('S', 'S'): 1.0, ('S', 'A'): 0.9, ('S', 'B'): 0.6, ('S', 'C'): 0.3, ('S', 'D'): 0.1,
                ('A', 'S+'): 0.8, ('A', 'S'): 0.9, ('A', 'A'): 1.0, ('A', 'B'): 0.8, ('A', 'C'): 0.4, ('A', 'D'): 0.1,
                ('B', 'S+'): 0.5, ('B', 'S'): 0.6, ('B', 'A'): 0.8, ('B', 'B'): 1.0, ('B', 'C'): 0.6, ('B', 'D'): 0.2,
                ('C', 'S+'): 0.2, ('C', 'S'): 0.3, ('C', 'A'): 0.4, ('C', 'B'): 0.6, ('C', 'C'): 1.0, ('C', 'D'): 0.5,
                ('D', 'S+'): 0.1, ('D', 'S'): 0.1, ('D', 'A'): 0.1, ('D', 'B'): 0.2, ('D', 'C'): 0.5, ('D', 'D'): 1.0,
            }

            return tier_similarity.get((target_tier, market_tier), 0.3)

        return None  # 其他特征使用默认计算
