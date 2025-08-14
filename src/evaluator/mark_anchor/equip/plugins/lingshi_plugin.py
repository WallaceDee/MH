"""
灵饰插件

专门处理灵饰装备的估价逻辑，重点主属性和附加属性
"""

from src.evaluator.mark_anchor.equip.index import EquipmentTypePlugin
from src.evaluator.constants.lingshi_priorities import is_same_priority
import sys
import os
from typing import Dict, Any, List, Optional, Tuple

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))))
sys.path.insert(0, project_root)


class LingshiPlugin(EquipmentTypePlugin):
    """灵饰装备插件 - 专注主属性和附加属性估价
    主属性：
            damage: int - 伤害值 (戒指主属性)
            defense: int - 防御值 (戒指主属性)
            magic_damage: int - 法术伤害值 (耳饰主属性)
            magic_defense: int - 法术防御值 (耳饰主属性)
            fengyin: int - 封印命中等级 (手镯主属性)
            anti_fengyin: int - 抵抗封印等级 (手镯主属性)
            speed: int - 速度值 (佩饰主属性)

    """

    @property
    def plugin_name(self) -> str:
        return "灵饰(kindid:61/62/63/64)专用插件"

    @property
    def supported_kindids(self) -> List[int]:
        from src.evaluator.constants.equipment_types import LINGSHI_KINDIDS
        return LINGSHI_KINDIDS  # 灵饰的kindid

    @property
    def priority(self) -> int:
        return 100  # 高优先级

    def get_derived_features(self, features: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """灵饰派生特征"""
        derived = {}

        # 获取装备等级和基础属性
        equip_level = features.get('equip_level', 1)

        # 加载灵饰配置数据
        config_data = self._load_lingshi_config()

        # 计算主属性标准化得分
        main_attr_scores = self._calculate_main_attr_scores(
            features, equip_level, config_data)
        derived.update(main_attr_scores)

        # 计算附加属性标准化得分 - 传入目标匹配属性
        target_match_attrs = context.get('target_match_attrs') if context else None
        attr_scores = self._calculate_attr_scores(
            features, equip_level, config_data, target_match_attrs)
        derived.update(attr_scores)

        # 添加attr_3_type字段 - 根据目标装备属性计算
        if context and 'target_match_attrs' in context:
            target_match_attrs = context['target_match_attrs']
            # 获取目标装备的所有属性类型
            target_attrs = features.get('attrs', [])
            target_attr_types = []
            for attr in target_attrs:
                attr_type = attr.get('attr_type', '')
                if attr_type:
                    target_attr_types.append(attr_type)
            
            # 排除target_match_attrs后，获得剩余的属性类型
            remaining_attrs = [attr_type for attr_type in target_attr_types if attr_type not in target_match_attrs]
            # 取第一个剩余的属性类型作为attr_3_type
            attr_3_type = remaining_attrs[0] if remaining_attrs else None
            derived['attr_3_type'] = attr_3_type

        return derived

    def _load_lingshi_config(self) -> Dict[str, Any]:
        """加载灵饰配置数据"""
        try:
            import json
            config_path = os.path.join(
                os.path.dirname(__file__), 'lingshi.jsonc')
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载灵饰配置失败: {e}")
            return {}

    def _calculate_main_attr_scores(self, features: Dict[str, Any], equip_level: int, config_data: Dict[str, Any]) -> Dict[str, float]:
        """计算主属性标准化得分"""
        scores = {}

        # 确定装备等级对应的配置
        level_key = str(equip_level)
        if level_key not in config_data:
            # 如果找不到精确等级，使用最接近的等级
            available_levels = list(config_data.keys())
            if available_levels:
                # 找到最接近的等级
                closest_level = min(
                    available_levels, key=lambda x: abs(int(x) - equip_level))
                level_key = closest_level
                print(f"使用等级 {closest_level} 的配置计算等级 {equip_level} 的装备")

        if level_key not in config_data:
            print(f"未找到等级 {equip_level} 的灵饰配置")
            return scores

        level_config = config_data[level_key]
        main_config = level_config.get('main', {})

        # 主属性字段映射
        main_attrs = {
            'damage': '伤害',
            'defense': '防御',
            'magic_damage': '法术伤害',
            'magic_defense': '法术防御',
            'fengyin': '封印命中等级',
            'anti_fengyin': '抵抗封印等级',
            'speed': '速度'
        }

        # 计算每个主属性的标准化得分
        for attr_field, attr_name in main_attrs.items():
            attr_value = features.get(attr_field, 0)
            if attr_value > 0:
                # 获取该属性的配置范围
                attr_range = main_config.get(attr_name, [0, 1])
                if len(attr_range) == 2:
                    min_val, max_val = attr_range
                    if max_val > min_val:
                        # 使用改进的标准化得分计算方法
                        # 方案1: 基础分制 - 最小值给30分，最大值给100分，避免0分问题
                        base_score = 30  # 基础分数，避免最小值为0分
                        score_range = 70  # 可变分数范围 (100 - 30)
                        
                        # 计算相对位置 (0-1)
                        relative_position = (attr_value - min_val) / (max_val - min_val)
                        # 限制在0-1范围内
                        relative_position = max(0.0, min(1.0, relative_position))
                        
                        # 计算最终得分: 基础分 + 相对位置 × 分数范围
                        score_100 = base_score + relative_position * score_range
                        scores[f'{attr_field}_score'] = round(score_100, 2)

                        print(
                            f"[主属性得分] {attr_name}: {attr_value} (范围: {min_val}-{max_val}) -> {score_100:.2f}分 (基础分{base_score}+{relative_position*score_range:.2f})")

        return scores

    def _calculate_attr_scores(self, features: Dict[str, Any], equip_level: int, config_data: Dict[str, Any], target_match_attrs: List[str] = None) -> Dict[str, float]:
        """计算附加属性标准化得分 - 只计算匹配的属性类型"""
        scores = {}

        # 获取附加属性列表
        attrs = features.get('attrs', [])
        if not attrs:
            return scores

        # 确定装备等级对应的配置
        level_key = str(equip_level)
        if level_key not in config_data:
            # 如果找不到精确等级，使用最接近的等级
            available_levels = list(config_data.keys())
            if available_levels:
                closest_level = min(
                    available_levels, key=lambda x: abs(int(x) - equip_level))
                level_key = closest_level
                print(f"使用等级 {closest_level} 的配置计算等级 {equip_level} 的附加属性")

        if level_key not in config_data:
            print(f"未找到等级 {equip_level} 的灵饰配置")
            return scores

        level_config = config_data[level_key]
        attrs_config = level_config.get('attrs', {})

        # 只计算匹配的属性类型得分，但使用位置索引命名
        matched_attrs = []
        for attr in attrs:
            attr_type = attr.get('attr_type', '')
            attr_value = attr.get('attr_value', 0)

            # 如果指定了目标匹配属性，只计算这些属性的得分
            if target_match_attrs and attr_type not in target_match_attrs:
                continue

            if attr_type and attr_value > 0:
                matched_attrs.append(attr)

        # 按target_match_attrs的顺序重新排序，确保位置索引一致
        if target_match_attrs:
            # 创建一个映射，记录每个属性类型在target_match_attrs中的位置
            attr_order_map = {attr_type: i for i, attr_type in enumerate(target_match_attrs)}
            
            # 按照target_match_attrs的顺序排序，相同类型的属性按值降序排序
            matched_attrs.sort(key=lambda attr: (
                attr_order_map.get(attr.get('attr_type', ''), 999),  # 先按属性类型顺序
                -attr.get('attr_value', 0)  # 再按属性值降序（负号表示降序）
            ))

        # 按位置索引计算得分
        for i, attr in enumerate(matched_attrs):
            attr_type = attr.get('attr_type', '')
            attr_value = attr.get('attr_value', 0)

            # 获取该属性的配置范围
            attr_range = attrs_config.get(attr_type, [0, 1])
            if len(attr_range) == 2:
                min_val, max_val = attr_range
                if max_val > min_val:
                    # 使用改进的标准化得分计算方法
                    # 基础分制 - 最小值给30分，最大值给100分，避免0分问题
                    base_score = 30  # 基础分数，避免最小值为0分
                    score_range = 70  # 可变分数范围 (100 - 30)
                    
                    # 计算相对位置 (0-1)
                    relative_position = (attr_value - min_val) / (max_val - min_val)
                    # 限制在0-1范围内
                    relative_position = max(0.0, min(1.0, relative_position))
                    
                    # 计算最终得分: 基础分 + 相对位置 × 分数范围
                    score_100 = base_score + relative_position * score_range
                    
                    # 使用位置索引命名
                    score_key = f'attr_{i+1}_score'
                    scores[score_key] = round(score_100, 2)

                    print(
                        f"[附加属性得分] {attr_type}: {attr_value} (范围: {min_val}-{max_val}) -> {score_100:.2f}分 (基础分{base_score}+{relative_position*score_range:.2f})")

        return scores

    def get_weight_overrides(self, kindid: int = None) -> Dict[str, float]:
        """
        获取权重覆盖配置

        Args:
            kindid: 装备类型ID，用于动态配置权重

        Returns:
            Dict[str, float]: 要覆盖的权重配置
        """
        # 基础权重配置
        base_weights = {
            # 灵饰特有的权重配置
            'gem_score': 0.5,            # 宝石得分非常重要

            # 附加属性得分权重
            # 'attrs_avg_score': 1.0,       # 附加属性平均得分
            'attr_1_score': 1.0,          # 第一个附加属性得分
            'attr_2_score': 1.0,          # 第二个附加属性得分
            'attr_3_score': 1.0,            # 第三个附加属性得分
            'attr_3_type': 0.5,            # 第三个属性类型权重
            # 忽略的特征
            'gem_level': 0,
            'is_super_simple': 0,
            'damage_score': 0,    # 戒指伤害得分
            'defense_score': 0,   # 戒指防御得分
            'magic_damage_score': 0,  # 其他设为0
            'magic_defense_score': 0,
            'fengyin_score': 0,
            'anti_fengyin_score': 0,
            'speed_score': 0,
            'damage': 0,  # 得分代替
            'defense': 0,  # 得分代替
            'magic_damage': 0,  # 得分代替
            'magic_defense': 0,  # 得分代替
            'fengyin': 0,  # 得分代替
            'anti_fengyin': 0,  # 得分代替
            'speed': 0,  # 得分代替

            'equip_level': 0,             # 等级跨度大，不考虑
            'suit_effect': 0,             # 没有套装
            'hole_score': 0,              # 没有开运
            'attrs': 0,                   # 附加属性
            'suit_effect_type': 0,
            'suit_effect_level': 0,
        }

        # 根据kindid设置主属性得分权重
        if kindid is not None:
            if kindid == 61:  # 戒指 - 只有伤害和防御
                base_weights.update({
                    'damage_score': 1.0,      # 戒指伤害得分
                    'defense_score': 1.0,     # 戒指防御得分
                })
            elif kindid == 62:  # 耳饰 - 只有法术伤害和法术防御
                base_weights.update({

                    'magic_damage_score': 1.0,    # 耳饰法术伤害得分
                    'magic_defense_score': 1.0,   # 耳饰法术防御得分

                })
            elif kindid == 63:  # 手镯 - 只有封印命中等级和抵抗封印等级
                base_weights.update({
                    'fengyin_score': 1.0,         # 手镯封印命中得分
                    'anti_fengyin_score': 1.0,    # 手镯抵抗封印得分
                })
            elif kindid == 64:  # 佩饰 - 只有速度
                base_weights.update({
                    'speed_score': 1.0,           # 佩饰速度得分
                })

        return base_weights

    def get_tolerance_overrides(self, kindid: int = None) -> Dict[str, float]:
        """
        获取相对容忍度覆盖配置

        Args:
            kindid: 装备类型ID，用于动态配置容忍度

        Returns:
            Dict[str, float]: 相对容忍度覆盖
        """
        # 基础容忍度配置
        base_tolerances = {
            # 灵饰特有的容忍度配置
            'gem_score': 0.5,             # 宝石得分容忍度中等

            # 附加属性得分容忍度
            # 'attrs_avg_score': 0.4,       # 附加属性平均得分容忍度40%
            'attr_1_score': 0.25,          # 第一个附加属性得分容忍度25%
            'attr_2_score': 0.25,          # 第二个附加属性得分容忍度25%
            'attr_3_score': 0.25,          # 第三个附加属性得分容忍度25%
            'attr_3_type':0,
            # 忽略的特征
            'suit_effect_type': 1,
            'suit_effect_level': 1,
            'is_super_simple': 1,
            'gem_level': 1,
        }

        # 根据kindid设置主属性得分容忍度
        if kindid is not None:
            if kindid == 61:  # 戒指 - 只有伤害和防御
                base_tolerances.update({
                    'damage_score': 0.3,      # 戒指伤害得分容忍度30%
                    'defense_score': 0.3,     # 戒指防御得分容忍度30%
                    'magic_damage_score': 1,  # 其他设为1（忽略）
                    'magic_defense_score': 1,
                    'fengyin_score': 1,
                    'anti_fengyin_score': 1,
                    'speed_score': 1,
                })
            elif kindid == 62:  # 耳饰 - 只有法术伤害和法术防御
                base_tolerances.update({
                    'damage_score': 1,
                    'defense_score': 1,
                    'magic_damage_score': 0.3,    # 耳饰法术伤害得分容忍度30%
                    'magic_defense_score': 0.3,   # 耳饰法术防御得分容忍度30%
                    'fengyin_score': 1,
                    'anti_fengyin_score': 1,
                    'speed_score': 1,
                })
            elif kindid == 63:  # 手镯 - 只有封印命中等级和抵抗封印等级
                base_tolerances.update({
                    'damage_score': 1,
                    'defense_score': 1,
                    'magic_damage_score': 1,
                    'magic_defense_score': 1,
                    'fengyin_score': 0.3,         # 手镯封印命中得分容忍度30%
                    'anti_fengyin_score': 0.3,    # 手镯抵抗封印得分容忍度30%
                    'speed_score': 1,
                })
            elif kindid == 64:  # 佩饰 - 只有速度
                base_tolerances.update({
                    'damage_score': 1,
                    'defense_score': 1,
                    'magic_damage_score': 1,
                    'magic_defense_score': 1,
                    'fengyin_score': 1,
                    'anti_fengyin_score': 1,
                    'speed_score': 0.3,           # 佩饰速度得分容忍度30%
                })

        return base_tolerances

    def calculate_custom_similarity(self,
                                    feature_name: str,
                                    target_val: Any,
                                    market_val: Any,
                                    context: Dict[str, Any] = None) -> Optional[float]:
        """灵饰自定义相似度计算"""
        # 灵饰特有的相似度计算逻辑
        if feature_name == 'attr_3_type':
            # attr_3_type相似度计算
            if target_val is None and market_val is None:
                return 1.0  # 都没有第三个属性，完全匹配
            elif target_val is None or market_val is None:
                return 0.5  # 一个有第三个属性一个没有，给予中等相似度
            else:
                # 都有第三个属性，根据优先级判断是否相似
                # 获取装备类型用于优先级判断
                equipment_type = context.get('kindid') if context else None
                
                 # 完全相同的属性
                if target_val == market_val:
                    return 1.0 
                # 使用优先级判断属性是否相似
                elif is_same_priority(target_val, market_val, equipment_type):
                    return 0.75  # 优先级相同，认为相似
                else:
                    return 0.0  # 优先级不同，不相似
        
        return None  # 其他特征使用默认计算
