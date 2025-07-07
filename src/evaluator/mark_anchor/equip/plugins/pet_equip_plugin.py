"""
宠物装备插件

专门处理宠物装备的估价逻辑，重点主属性和附加属性
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


class PetEquipPlugin(EquipmentTypePlugin):
    """宠物装备插件 - 专注主属性和附加属性估价
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
        return "宠物装备(kindid:29)专用插件"

    @property
    def supported_kindids(self) -> List[int]:
        return [29]  # 宠物装备的kindid

    @property
    def priority(self) -> int:
        return 100  # 高优先级

    def get_derived_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """宠物装备派生特征"""
        derived = {}

        # 获取装备等级和基础属性
        equip_level = features.get('equip_level', 1)

        # 加载宠物装备配置数据
        config_data = self._load_pet_equip_config()

        # 计算主属性标准化得分
        main_attr_scores = self._calculate_main_attr_scores(
            features, equip_level, config_data)
        derived.update(main_attr_scores)

        # 计算附加属性标准化得分
        attr_scores = self._calculate_attr_scores(
            features, equip_level, config_data)
        derived.update(attr_scores)

        return derived

    def _load_pet_equip_config(self) -> Dict[str, Any]:
        """加载宠物装备配置数据"""
        try:
            import json
            config_path = os.path.join(
                os.path.dirname(__file__), 'pet_equip.jsonc')
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载宠物装备配置失败: {e}")
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
            print(f"未找到等级 {equip_level} 的宠物装备配置")
            return scores

        level_config = config_data[level_key]

        # 主属性字段映射（宠物装备的属性字段）
        main_attrs = {
            'shanghai': '伤害',
            'fangyu': '防御', 
            'speed': '速度',
            'qixue': '气血',
        }

        # 计算每个主属性的标准化得分
        for attr_field, attr_name in main_attrs.items():
            attr_value = features.get(attr_field, 0)
            if attr_value > 0:
                # 获取该属性的最大值（pet_equip.jsonc中直接存储最大值）
                max_val = level_config.get(attr_name, 0)
                if max_val > 0:
                    # 计算标准化得分 (0-1)，下限为0
                    normalized_score = attr_value / max_val
                    # 限制在0-1范围内
                    normalized_score = max(0.0, min(1.0, normalized_score))
                    # 转换为0-100分制
                    score_100 = normalized_score * 100
                    scores[f'{attr_field}_score'] = round(score_100, 2)

                    # print(f"[主属性得分] {attr_name}: {attr_value} (最大值: {max_val}) -> {score_100:.2f}分")

        return scores

    def _calculate_attr_scores(self, features: Dict[str, Any], equip_level: int, config_data: Dict[str, Any]) -> Dict[str, float]:
        """计算附加属性标准化得分"""
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
            print(f"未找到等级 {equip_level} 的宠物装备配置")
            return scores

        level_config = config_data[level_key]

        # 主属性字段映射（宠物装备的属性字段）
        main_attrs = {
            'addon_fali': '法力',
            'addon_lingli': '灵力', 
            'addon_liliang': '力量',
            'addon_minjie': '敏捷',
            'addon_naili': '耐力',
            'addon_tizhi': '体质',
        }

        # 计算每个附加属性的标准化得分
        for attr_field, attr_name in main_attrs.items():
            attr_value = features.get(attr_field, 0)
            if attr_value > 0:
                # 获取该属性的最大值（pet_equip.jsonc中直接存储最大值）
                max_val = level_config.get(attr_name, 0)
                if max_val > 0:
                    # 计算标准化得分 (0-1)，下限为0
                    normalized_score = attr_value / max_val
                    # 限制在0-1范围内
                    normalized_score = max(0.0, min(1.0, normalized_score))
                    # 转换为0-100分制
                    score_100 = normalized_score * 100
                    scores[f'{attr_field}_score'] = round(score_100, 2)

                    # print(f"[附加得分] {attr_name}: {attr_value} (最大值: {max_val}) -> {score_100:.2f}分")

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
            # 宝石得分
            'gem_score': 0.5,            # 宝石得分非常重要
            
            # 主属性标准化得分
            'shanghai_score': 2.0,       # 伤害得分
            'fangyu_score': 1.0,         # 防御得分
            'speed_score': 1.0,          # 速度得分
            'qixue_score': 1.0,          # 气血得分
            
            # 附加属性标准化得分
            'addon_fali_score': 2.0,     # 法力附加得分
            'addon_lingli_score': 2.0,   # 灵力附加得分
            'addon_liliang_score': 2.0,  # 力量附加得分
            'addon_minjie_score': 0.8,   # 敏捷附加得分
            'addon_minjie': 0.8,           # 敏捷附加原始值
            'addon_naili_score': 0.8,    # 耐力附加得分
            'addon_tizhi_score': 0.8,    # 体质附加得分

            # 原始数值设为0，使用标准化得分代替
            'shanghai': 0,               # 伤害原始值
            'fangyu': 0,                 # 防御原始值
            'speed': 0,                  # 速度原始值
            'qixue': 0,                  # 气血原始值
            'addon_fali': 0,             # 法力附加原始值
            'addon_lingli': 0,           # 灵力附加原始值
            'addon_liliang': 0,          # 力量附加原始值
          
            'addon_naili': 0,            # 耐力附加原始值
            'addon_tizhi': 0,            # 体质附加原始值

            # 忽略的特征
            'gem_level': 0,
            'equip_level': 0,             # 等级跨度大，不考虑
            'suit_effect': 0,             # 没有套装（TODO: 钟灵石套装可以用这个）
            'hole_score': 0,              # 没有开运
        }

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
            # 宝石得分容忍度
            'gem_score': 0.5,             # 宝石得分容忍度中等
            
            # 主属性标准化得分容忍度
            'shanghai_score': 0.3,        # 伤害得分容忍度30%
            'fangyu_score': 0.3,          # 防御得分容忍度30%
            'speed_score': 0.3,           # 速度得分容忍度30%
            'qixue_score': 0.3,           # 气血得分容忍度30%
            
            # 附加属性标准化得分容忍度
            'addon_fali_score': 0.4,      # 法力附加得分容忍度40%
            'addon_lingli_score': 0.4,    # 灵力附加得分容忍度40%
            'addon_liliang_score': 0.4,   # 力量附加得分容忍度40%
            'addon_minjie_score': 0.4,    # 敏捷附加得分容忍度40%
            'addon_minjie':0.4,           # 敏捷附加原始值容忍度40%
            'addon_naili_score': 0.4,     # 耐力附加得分容忍度40%
            'addon_tizhi_score': 0.4,     # 体质附加得分容忍度40%

            # 原始数值完全忽略
            'shanghai': 1,                # 伤害原始值完全忽略
            'fangyu': 1,                  # 防御原始值完全忽略
            'speed': 1,                   # 速度原始值完全忽略
            'qixue': 1,                   # 气血原始值完全忽略
            'addon_fali': 1,              # 法力附加原始值完全忽略
            'addon_lingli': 1,            # 灵力附加原始值完全忽略
            'addon_liliang': 1,           # 力量附加原始值完全忽略
 
            'addon_naili': 1,             # 耐力附加原始值完全忽略
            'addon_tizhi': 1,             # 体质附加原始值完全忽略

            # 忽略的特征
            'gem_level': 1,
        }

        return base_tolerances

    def calculate_custom_similarity(self,
                                    feature_name: str,
                                    target_val: Any,
                                    market_val: Any) -> Optional[float]:
        """宠物装备自定义相似度计算"""

        return None  # 其他特征使用默认计算
