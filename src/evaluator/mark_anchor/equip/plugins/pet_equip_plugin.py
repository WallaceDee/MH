"""
召唤兽装备插件

专门处理召唤兽装备的估价逻辑，重点主属性和附加属性
"""

from src.evaluator.mark_anchor.equip.index import EquipmentTypePlugin
import sys
import os
from typing import Dict, Any, List, Optional, Tuple


class PetEquipPlugin(EquipmentTypePlugin):
    """召唤兽装备插件 - 专注主属性和附加属性估价
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
        from src.evaluator.constants.equipment_types import PET_EQUIP_KINDID
        return f"召唤兽装备(kindid:{PET_EQUIP_KINDID})专用插件"

    @property
    def supported_kindids(self) -> List[int]:
        from src.evaluator.constants.equipment_types import PET_EQUIP_KINDID
        return [PET_EQUIP_KINDID]  # 召唤兽装备的kindid

    @property
    def priority(self) -> int:
        return 100  # 高优先级

    def get_derived_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """召唤兽装备派生特征"""
        derived = {}

        # 获取装备等级和基础属性
        equip_level = features.get('equip_level', 1)

        # 加载召唤兽装备配置数据
        config_data = self._load_pet_equip_config()

        # 计算主属性标准化得分
        main_attr_scores = self._calculate_main_attr_scores(
            features, equip_level, config_data)
        derived.update(main_attr_scores)

        # 计算附加属性标准化得分
        attr_scores = self._calculate_attr_scores(
            features, equip_level, config_data)
        derived.update(attr_scores)

        # suit_category现在在特征提取阶段计算，不需要在这里重复计算
        
        return derived

    def _load_pet_equip_config(self) -> Dict[str, Any]:
        """加载召唤兽装备配置数据"""
        try:
            from src.evaluator.mark_anchor.equip.constant import get_pet_equip_config
            return get_pet_equip_config()
        except Exception as e:
            print(f"加载召唤兽装备配置失败: {e}")
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
            print(f"未找到等级 {equip_level} 的召唤兽装备配置")
            return scores

        level_config = config_data[level_key]

        # 主属性字段映射（召唤兽装备的属性字段）
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
                    # 使用改进的标准化得分计算方法
                    # 基础分制 - 避免0分问题，适用于召唤兽装备（下限为0的情况）
                    base_score = 30  # 基础分数，避免最小值为0分
                    score_range = 70  # 可变分数范围 (100 - 30)
                    
                    # 计算相对位置 (0-1)，召唤兽装备最小值为0
                    relative_position = attr_value / max_val
                    # 限制在0-1范围内
                    relative_position = max(0.0, min(1.0, relative_position))
                    
                    # 计算最终得分: 基础分 + 相对位置 × 分数范围
                    score_100 = base_score + relative_position * score_range
                    scores[f'{attr_field}_score'] = round(score_100, 2)

                    # print(f"[主属性得分] {attr_name}: {attr_value} (最大值: {max_val}) -> {score_100:.2f}分 (基础分{base_score}+{relative_position*score_range:.2f})")

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
            print(f"未找到等级 {equip_level} 的召唤兽装备配置")
            return scores

        level_config = config_data[level_key]

        # 主属性字段映射（召唤兽装备的属性字段）
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
                    # 使用改进的标准化得分计算方法
                    # 基础分制 - 避免0分问题，适用于召唤兽装备（下限为0的情况）
                    base_score = 30  # 基础分数，避免最小值为0分
                    score_range = 70  # 可变分数范围 (100 - 30)
                    
                    # 计算相对位置 (0-1)，召唤兽装备最小值为0
                    relative_position = attr_value / max_val
                    # 限制在0-1范围内
                    relative_position = max(0.0, min(1.0, relative_position))
                    
                    # 计算最终得分: 基础分 + 相对位置 × 分数范围
                    score_100 = base_score + relative_position * score_range
                    scores[f'{attr_field}_score'] = round(score_100, 2)

                    # print(f"[附加得分] {attr_name}: {attr_value} (最大值: {max_val}) -> {score_100:.2f}分 (基础分{base_score}+{relative_position*score_range:.2f})")

        return scores



    def get_weight_overrides(self, kindid: int = None, target_features: Dict[str, Any] = None) -> Dict[str, float]:
        """
        获取权重覆盖配置

        Args:
            kindid: 装备类型ID，用于动态配置权重
            target_features: 目标装备特征，用于动态调整权重

        Returns:
            Dict[str, float]: 要覆盖的权重配置
        """
        # 基础权重配置
        base_weights = {
            # 宝石得分
            'gem_score': 0.5,            # 宝石得分非常重要
            'addon_status': 0.5,            # 
            'suit_category': 1.5,         # 套装分类权重
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
            'xiang_qian_level':0,
            'gem_level': 0,
            'equip_level': 0,             # 等级跨度大，不考虑
            'suit_effect': 0,             # 使用suit_category代替原始suit_effect
            'hole_score': 0,              # 没有开运
            'addon_classification': 0 
        }

        # 动态权重调整逻辑
        if target_features:
            shanghai = target_features.get('shanghai', 0)
            addon_fali = target_features.get('addon_fali', 0)
            addon_lingli = target_features.get('addon_lingli', 0)
            
            if shanghai > 20:
                # 物理系装备：伤害>20，忽略法力和灵力附加属性
                # print(f"物理系召唤兽装备 (shanghai={shanghai}>20): 忽略法力和灵力权重")
                base_weights['addon_fali'] = 0
                base_weights['addon_fali_score'] = 0
                base_weights['addon_lingli'] = 0
                base_weights['addon_lingli_score'] = 0
                
            elif shanghai <= 20:
                if addon_fali > 0 or addon_lingli > 0:
                    # 法系装备：有法力或灵力属性，忽略shanghai
                    # print(f"法系召唤兽装备 (shanghai={shanghai}<=20, 有法力/灵力): 忽略伤害权重")
                    base_weights['shanghai'] = 0
                    base_weights['shanghai_score'] = 0
                # else:
                    # #无法系属性的装备：不忽略shanghai
                    # print(f"无法系属性装备 (shanghai={shanghai}<=20, 无法力/灵力): 保持伤害权重")
                    # 保持shanghai_score的默认权重，不做修改

        return base_weights

    def get_tolerance_overrides(self, kindid: int = None, target_features: Dict[str, Any] = None) -> Dict[str, float]:
        """
        获取相对容忍度覆盖配置

        Args:
            kindid: 装备类型ID，用于动态配置容忍度
            target_features: 目标装备特征，用于动态调整容忍度

        Returns:
            Dict[str, float]: 相对容忍度覆盖
        """
        # 基础容忍度配置
        base_tolerances = {
            # 宝石得分容忍度
            'gem_score': 0.5,             # 宝石得分容忍度中等
            'suit_category': 0,           # 套装分类必须完全匹配
            
            # 主属性标准化得分容忍度
            'shanghai_score': 0.1,        # 伤害得分容忍度20%
            'fangyu_score': 0.4,          # 防御得分容忍度20%
            'speed_score': 0.2,           # 速度得分容忍度20%
            'qixue_score': 0.2,           # 气血得分容忍度20%
            
            # 附加属性标准化得分容忍度
            'addon_fali_score': 0.2,      # 法力附加得分容忍度20%
            'addon_lingli_score': 0.2,    # 灵力附加得分容忍度20%
            'addon_liliang_score': 0.2,   # 力量附加得分容忍度20%
            'addon_minjie_score': 0.2,    # 敏捷附加得分容忍度20%
            'addon_minjie':0.2,           # 敏捷附加原始值容忍度20%
            'addon_naili_score': 0.2,     # 耐力附加得分容忍度20%
            'addon_tizhi_score': 0.2,     # 体质附加得分容忍度20%

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
            'xiang_qian_level':1,
            'gem_level': 1,
            'suit_effect': 1,             # 使用suit_category代替
            'addon_status':0,            # 使用suit_category代替
            'addon_classification': 1
        }

        # 动态容忍度调整逻辑
        if target_features:
            shanghai = target_features.get('shanghai', 0)
            addon_fali = target_features.get('addon_fali', 0)
            addon_lingli = target_features.get('addon_lingli', 0)
            
            if shanghai > 20:
                # 物理系装备：伤害>20，忽略法力和灵力附加属性
                # print(f"物理系召唤兽装备 (shanghai={shanghai}>20): 设置法力和灵力容忍度为1")
                base_tolerances['addon_fali'] = 1
                base_tolerances['addon_fali_score'] = 1
                base_tolerances['addon_lingli'] = 1
                base_tolerances['addon_lingli_score'] = 1
                
            elif shanghai <= 20:
                if addon_fali > 0 or addon_lingli > 0:
                    # 法系装备：有法力或灵力属性，忽略shanghai
                    # print(f"法系召唤兽装备 (shanghai={shanghai}<=20, 有法力/灵力): 设置伤害容忍度为1")
                    base_tolerances['shanghai'] = 1
                    base_tolerances['shanghai_score'] = 1
                # else:
                #     # 无法系属性的装备：不忽略shanghai
                #     print(f"无法系属性装备 (shanghai={shanghai}<=20, 无法力/灵力): 保持伤害容忍度")
                #     # 保持shanghai_score的默认容忍度，不做修改

        return base_tolerances

    def calculate_custom_similarity(self,
                                    feature_name: str,
                                    target_val: Any,
                                    market_val: Any) -> Optional[float]:
        """
        召唤兽装备的自定义相似度计算

        Args:
            feature_name: 特征名称
            target_val: 目标值
            market_val: 市场值

        Returns:
            Optional[float]: 相似度分数，None表示使用默认计算方法
        """
        # 套装分类的自定义相似度计算
        if feature_name == 'suit_category':
            return self._calculate_suit_category_similarity(target_val, market_val)
                # 套装分类的自定义相似度计算
        if feature_name == 'addon_status':
            # 特技和套装效果必须完全一致（容忍度为0）
            if target_val == market_val:
                return 1.0
            else:
                return 0.4

        return None

    def _calculate_suit_category_similarity(self, target_category: str, market_category: str) -> float:
        """
        计算套装分类的相似度
        
        同类套装相似度为1.0，不同类套装有部分相似度，完全不匹配为0
        
        Args:
            target_category: 目标套装分类
            market_category: 市场套装分类
            
        Returns:
            float: 相似度分数 (0-1)
        """
        if target_category == market_category:
            # 完全匹配
            return 1.0
        
        # 定义套装分类的相似度规则（自动处理顺序）
        def get_similarity(cat1: str, cat2: str) -> float:
            # 无套装和其他套装的相似度
            if cat1 == '无套装' or cat2 == '无套装':
                return 0.75
            
            categories = {'物理系', '法术系','辅助系', '高级其他'}
            if cat1 in categories and cat2 in categories:
                return 0.5
            
            # 特殊系和其他分类的相似度
            if cat1 == '特殊系' or cat2 == '特殊系':
                return 0.2
            
            # 其他情况
            return 0.1
        
        # 自动处理顺序，返回对称的相似度
        return get_similarity(target_category, market_category)
