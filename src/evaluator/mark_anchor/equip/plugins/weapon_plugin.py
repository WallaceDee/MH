"""
武器插件

专门处理武器装备的估价逻辑，重点关注伤害、总伤害和属性加成
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


class WeaponPlugin(EquipmentTypePlugin):
    """武器装备插件 - 专注于伤害、总伤害和属性加成的估价
    60 命中(231～300)，伤害（199～259），总伤（276~359）
    70 命中(267～347)，伤害（231～300），总伤（320~415）
    80 命中(304～395)，伤害（262～341），总伤（363.33~472.67）
    90 命中(341～443)，伤害（294～382），总伤（407.67~529.67）
    100 命中(378～491)，伤害（325～423），总伤（451~586.67）**
    110 命中(414～538)，伤害（357～464），总伤（485~643.33）
    120 命中(451～586)，伤害（388～505），总伤（538.33~700.33）**
    130 命中(488～634)，伤害（420～546），总伤（582.67~757.33*
    140 命中(525～682)，伤害（451～586），总伤（626~813.33）*
    150 命中(561～729)，伤害（483～627），总伤（670~870）*
    160 命中(571～777)，伤害（490～667），总伤（680.33~926）*
    """

    @property
    def plugin_name(self) -> str:
        return "武器(kindid:[ 14, 10, 6, 5, 15, 4, 13, 7, 12, 9, 11, 8, 52, 53, 54, 72, 73, 74, 83 ])专用插件"

    @property
    def supported_kindids(self) -> List[int]:
        return [ 14, 10, 6, 5, 15, 4, 13, 7, 12, 9, 11, 8, 52, 53, 54, 72, 73, 74, 83 ]  # 武器的kindid

    @property
    def priority(self) -> int:
        return 100  # 高优先级

    def get_derived_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """武器派生特征"""
        derived = {}

        # 获取装备等级和基础属性
        equip_level = features.get('equip_level', 1)
        init_damage_raw = features.get('init_damage_raw', 0) # 初伤不含命中
        all_damage = features.get('all_damage', 0) # 总伤
        addon_minjie = features.get('addon_minjie', 0) #敏捷
        addon_liliang = features.get('addon_liliang', 0) #力量
        addon_naili = features.get('addon_naili', 0) #耐力
        addon_tizhi = features.get('addon_tizhi', 0) #体质
        addon_moli = features.get('addon_moli', 0) #魔力
        addon_total = features.get('addon_total', 0) #附加属性总和

        # 计算初伤害标准化得分
        init_damage_raw_score = self._calculate_init_damage_raw_score(
            equip_level, init_damage_raw)
        derived['init_damage_raw_score'] = init_damage_raw_score

        # 计算总伤害标准化得分
        all_damage_score = self._calculate_all_damage_score(
            equip_level, all_damage)
        derived['all_damage_score'] = all_damage_score

        # 计算附加属性总和标准化得分
        # 如果addon_minjie、addon_liliang、addon_naili、addon_tizhi、addon_moli中有两个属性点是正整数则属于双加
        # 如果addon_minjie、addon_liliang、addon_naili、addon_tizhi、addon_moli中有一个属性点是正整数且没有其它属性点为正整数则属于单加
        # 单加和双加的上限不一样，双加的addon_total上限要高一些
        addon_total_score = self._calculate_addon_total_score(
            equip_level, addon_total, addon_minjie, addon_liliang, addon_naili, addon_tizhi, addon_moli)
        print(f"addon_total_score: {equip_level, addon_total, addon_minjie, addon_liliang, addon_naili, addon_tizhi, addon_moli}")
        derived['addon_total_score'] = addon_total_score

        return derived

    def _calculate_init_damage_raw_score(self, equip_level: int, init_damage: int) -> float:
        """
        计算初伤标准化得分（0-100分）
        "init_damage": "初伤（包含命中）≥",
        "init_damage_raw": "初伤（不含命中）≥",
        "all_damage": "总伤≥",
        Args:
            equip_level: 装备等级
            init_damage: 初始伤害值

        Returns:
            float:  初始伤害得分（0-100）
        """
        # 定义各等级 初始伤害标准区间
        damage_standards = {
            # 区间1：60-80
            60: (199, 259),   # 最低～最高
            70: (231, 300),
            80: (262, 341),
            # 区间2：90-100
            90: (294, 382),
            100: (325, 423),
            # 区间3：110-120
            110: (357, 464),
            120: (388, 505),
            # 区间4：130-140
            130: (420, 546),
            140: (451, 586),
            # 区间5：150-160
            150: (483, 627),
            160: (490, 667),
        }

        # 找到最接近的等级标准
        closest_level = min(damage_standards.keys(),
                            key=lambda x: abs(x - equip_level))
        min_damage, max_damage = damage_standards[closest_level]

        # 计算标准化得分
        # 武器伤害最差情况是比最低标准低5%
        worst_damage = min_damage * 0.95
        
        if init_damage <= worst_damage:
            # 低于最差标准（比最低标准还低5%）- 很少见
            score = 0  # 直接给0分
        elif init_damage <= min_damage:
            # 最差标准到最低标准
            ratio = (init_damage - worst_damage) / (min_damage - worst_damage)
            score = ratio * 10  # 0-10分
        elif init_damage >= max_damage:
            # 达到或超过最高标准
            excess_ratio = (init_damage - max_damage) / max_damage
            # 100分+超出奖励，最高120分再压缩到100
            score = min(100, 100 + excess_ratio * 20)
            score = min(100, score)
        else:
            # 在标准区间内
            ratio = (init_damage - min_damage) / (max_damage - min_damage)
            score = 10 + ratio * 90  # 10-100分

        return round(score, 1)

    def _calculate_all_damage_score(self, equip_level: int, all_damage: int) -> float:
        """
        计算总伤害标准化得分（0-100分）
        60 总伤（276~359）
        70 总伤（320~415）
        80 总伤（363.33~472.67）
        90 总伤（407.67~529.67）
        100 总伤（451~586.67）
        110 总伤（485~643.33）
        120 总伤（538.33~700.33）
        130 总伤（582.67~757.33）
        140 总伤（626~813.33）
        150 总伤（670~870）
        160 总伤（680.33~926）
        
        Args:
            equip_level: 装备等级
            all_damage: 总伤害值

        Returns:
            float: 总伤害得分（0-100）
        """
        # 定义各等级总伤害标准区间
        all_damage_standards = {
            # 区间1：60-80
            60: (276, 359),   # 最低～最高
            70: (320, 415),
            80: (363.33, 472.67),
            # 区间2：90-100
            90: (407.67, 529.67),
            100: (451, 586.67),
            # 区间3：110-120
            110: (485, 643.33),
            120: (538.33, 700.33),
            # 区间4：130-140
            130: (582.67, 757.33),
            140: (626, 813.33),
            # 区间5：150-160
            150: (670, 870),
            160: (680.33, 926),
        }

        # 找到最接近的等级标准
        closest_level = min(all_damage_standards.keys(),
                            key=lambda x: abs(x - equip_level))
        min_damage, max_damage = all_damage_standards[closest_level]

        # 计算标准化得分
        # 武器伤害最差情况是比最低标准低5%
        worst_damage = min_damage * 0.95
        
        if all_damage <= worst_damage:
            # 低于最差标准（比最低标准还低5%）- 很少见
            score = 0  # 直接给0分
        elif all_damage <= min_damage:
            # 最差标准到最低标准
            ratio = (all_damage - worst_damage) / (min_damage - worst_damage)
            score = ratio * 10  # 0-10分
        elif all_damage >= max_damage:
            # 达到或超过最高标准
            excess_ratio = (all_damage - max_damage) / max_damage
            # 100分+超出奖励，最高120分再压缩到100
            score = min(100, 100 + excess_ratio * 20)
            score = min(100, score)
        else:
            # 在标准区间内
            ratio = (all_damage - min_damage) / (max_damage - min_damage)
            score = 10 + ratio * 90  # 10-100分

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
        # 150| 48| 72
        # 160| 61| 86
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

    # 130 140 修理失败影响价钱严重
    def get_weight_overrides(self, kindid: int = None) -> Dict[str, float]:
        """武器权重覆盖配置"""
        return {
            'init_damage_raw_score': 3.0,               # 初伤标准化得分很重要
            'all_damage_score': 3.0,          # 总伤害标准化得分很重要
            'addon_total_score': 4.0,          # 附加属性总和标准化得分很重要
            'addon_moli': 1.0,                 # 魔力
            'addon_minjie': 1.0,               # 敏捷
            'addon_liliang': 1.0,               # 力量
            'addon_tizhi': 1.0,                 # 体质
            'addon_naili': 1.0,                 # 耐力
        }

    def get_tolerance_overrides(self, kindid: int = None) -> Dict[str, float]:
        """武器相对容忍度覆盖配置（已废弃绝对容忍度）"""
        return {
            'init_damage_raw_score': 0.12,              # 初伤标准化得分容忍度小
            'all_damage_score': 0.12,          # 总伤害标准化得分容忍度小
            'addon_total_score': 0.12,          # 附加属性总和标准化得分容忍度小
            'addon_moli': 0.3,                 # 魔力
            'addon_minjie': 0.3,               # 敏捷
            'addon_liliang': 0.3,               # 力量
            'addon_tizhi': 0.3,                 # 体质
            'addon_naili': 0.3,                 # 耐力
            'gem_score': 0.5,                  # 宝石得分容忍度中等
        }

    def calculate_custom_similarity(self,
                                    feature_name: str,
                                    target_val: Any,
                                    market_val: Any) -> Optional[float]:
        """武器自定义相似度计算"""
        if feature_name == 'init_damage_raw_score':
            # 初伤标准化得分：使用分档计算
            if target_val == 0 and market_val == 0:
                return 1.0

            if target_val == 0 or market_val == 0:
                return 0.1

            def get_init_damage_tier(score):
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

            target_tier = get_init_damage_tier(target_val)
            market_tier = get_init_damage_tier(market_val)

            tier_similarity = {
                ('S', 'S'): 1.0, ('S', 'A'): 0.85, ('S', 'B'): 0.6, ('S', 'C'): 0.3, ('S', 'D'): 0.1,
                ('A', 'S'): 0.85, ('A', 'A'): 1.0, ('A', 'B'): 0.8, ('A', 'C'): 0.5, ('A', 'D'): 0.2,
                ('B', 'S'): 0.6, ('B', 'A'): 0.8, ('B', 'B'): 1.0, ('B', 'C'): 0.7, ('B', 'D'): 0.3,
                ('C', 'S'): 0.3, ('C', 'A'): 0.5, ('C', 'B'): 0.7, ('C', 'C'): 1.0, ('C', 'D'): 0.6,
                ('D', 'S'): 0.1, ('D', 'A'): 0.2, ('D', 'B'): 0.3, ('D', 'C'): 0.6, ('D', 'D'): 1.0,
            }

            return tier_similarity.get((target_tier, market_tier), 0.4)

        elif feature_name == 'all_damage_score':
            # 总伤害标准化得分：使用分档计算
            if target_val == 0 and market_val == 0:
                return 1.0

            if target_val == 0 or market_val == 0:
                return 0.1

            def get_all_damage_tier(score):
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

            target_tier = get_all_damage_tier(target_val)
            market_tier = get_all_damage_tier(market_val)

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
