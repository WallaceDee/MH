from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl import Workbook
from datetime import datetime
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

# 导入市场数据采集器
from .equip_market_data_collector import EquipMarketDataCollector
from ..lingshi.lingshi_market_data_collector import LingshiMarketDataCollector
from ..pet_equip.pet_equip_market_data_collector import PetEquipMarketDataCollector


class BaseEquipmentConfig:
    """基础装备配置类 - 提供默认的配置"""

    def __init__(self):
        # 装备类型分类
        self.equip_categories = {
            # 武器类
            'weapons': {
                'name': '武器',
                'kindids': [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 52, 53, 54, 72, 73, 74],
                'description': '包含枪矛、斧钺、剑、双短剑、飘带、爪刺、扇、魔棒、鞭、环圈、刀、锤、宝珠、弓箭、法杖、灯笼、巨剑、伞'
            },
            # 防具类
            'armors': {
                'name': '防具',
                'kindids': [18, 59],
                'description': '包含铠甲、女衣'
            },
            # 饰品类
            'accessories': {
                'name': '饰品',
                'kindids': [17, 19, 20, 21, 58],
                'description': '包含头盔、鞋子、腰带、饰物、发钗'
            },
            # 灵饰类
            'lingshi': {
                'name': '灵饰',
                'kindids': [61, 62, 63, 64],
                'description': '包含灵饰'
            }
        }

        # 基础特征权重配置
        self.base_feature_weights = {
            # 默认都有的特征
            'equip_level': 1.0,          # 装备等级很重要
            'gem_score': 3.0,            # 宝石得分非常重要
            'suit_effect': 2.0,          # 套装效果权重较高
            'hole_score': 3.0,           # 开运孔数得分
            'repair_fail_num': 1.0,      # 修理失败次数

            # 以下特征是各个类型独有的特征，需要单独类型打开
            'init_damage': 0,          # 初伤
            'init_damage_raw': 0,      # 初伤（不包含命中）
            'all_damage': 0,           # 总伤
            'init_wakan': 0,           # 初灵
            'init_defense': 0,         # 初防
            'init_hp': 0,              # 初血
            'init_dex': 0,             # 初敏
            'mingzhong': 0,            # 命中
            'shanghai': 0,             # 伤害
            'addon_total': 0,          # 总附加属性
            'addon_tizhi': 0,          # 附加体质
            'addon_liliang': 0,        # 附加力量
            'addon_naili': 0,          # 附加耐力
            'addon_minjie': 0,         # 附加敏捷
            'addon_fali': 0,           # 附加法力
            'addon_lingli': 0,         # 附加灵力

            # 以下忽略，因为此特征已派生出新特征，不需要再计算
            'special_skill': 0,          # 特技，获取市场数据时候已经分类了
            'kindid': 0,                 # 类别在get_market_data已经过滤
            'gem_value': 0,              # 宝石得分已包含
            'special_effect': 0          # 特技已在get_market_data_for_similarity中过滤
        }

        # 基础相对容忍度配置
        self.base_relative_tolerances = {
            # 相对容忍度
            'equip_level': 0.25,         # 装备等级容忍度25%
            'gem_score': 0.25,           # 宝石得分容忍度15%
            'suit_effect': 0.0,          # 套装效果必须完全一致（通过专门的函数处理）
            'hole_score': 0.2,           # 开运孔数得分容忍度20%
            'repair_fail_num': 0.0,      # 修理失败次数必须完全一致

            # 以下特征是各个类型独有的特征，需要单独类型打开
            'init_damage': 1,          # 初伤
            'init_damage_raw': 1,      # 初伤（不包含命中）
            'all_damage': 1,           # 总伤
            'init_wakan': 1,           # 初灵
            'init_defense': 1,         # 初防
            'init_hp': 1,              # 初血
            'init_dex': 1,             # 初敏
            'mingzhong': 1,            # 命中
            'shanghai': 1,             # 伤害
            'addon_total': 1,          # 总附加属性
            'addon_tizhi': 1,          # 附加体质
            'addon_liliang': 1,        # 附加力量
            'addon_naili': 1,          # 附加耐力
            'addon_minjie': 1,         # 附加敏捷
            'addon_fali': 1,           # 附加法力
            'addon_lingli': 1,         # 附加灵力

            # 以下忽略，因为此特征已派生出新特征，不需要再计算
            'special_skill': 1,          # 特技，获取市场数据时候已经分类了
            'kindid': 1,                 # 类别在get_market_data已经过滤
            'gem_value': 1,              # 宝石得分已包含
            'special_effect': 1          # 特技已在get_market_data_for_similarity中过滤
        }

    def get_equip_category(self, kindid: int) -> str:
        """根据kindid获取装备类别"""
        for category, config in self.equip_categories.items():
            if kindid in config['kindids']:
                return category
        return 'weapons'  # 默认返回武器类

    def needs_addon_classification_filter(self, kindid: int) -> bool:
        """
        判断指定装备类型是否需要属性分类过滤

        Args:
            kindid: 装备类型ID

        Returns:
            bool: True表示需要属性分类过滤，False表示不需要
        """
        # 只有饰品不需要属性分类过滤
        no_addon_filter_kindids = [17, 19, 20, 21, 58]  # 头盔、鞋子、腰带、饰物、发钗

        # 除了指定的饰品类型，其他所有装备类型都需要属性分类过滤
        if kindid in no_addon_filter_kindids:
            return False
        else:
            return True

    def is_lingshi(self, kindid: int) -> bool:
        """
        判断指定装备类型是否灵饰

        Args:
            kindid: 装备类型ID

        Returns:
            bool: True表示是灵饰，False表示不是
        """
        lingshi_kindids = [61, 62, 63, 64]

        if kindid in lingshi_kindids:
            return True
        else:
            return False


class EquipmentTypePlugin(ABC):
    """装备类型插件基类"""

    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """插件名称"""
        pass

    @property
    @abstractmethod
    def supported_kindids(self) -> List[int]:
        """支持的装备类型ID列表"""
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """插件优先级，数字越大优先级越高"""
        pass

    def get_derived_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算派生特征

        Args:
            features: 原始特征字典

        Returns:
            Dict[str, Any]: 派生特征字典
        """
        return {}

    def get_weight_overrides(self, kindid: int = None) -> Dict[str, float]:
        """
        获取权重覆盖配置

        Args:
            kindid: 装备类型ID，用于动态配置权重

        Returns:
            Dict[str, float]: 要覆盖的权重配置
        """
        return {}

    def get_weight_increments(self, kindid: int = None) -> Dict[str, float]:
        """
        获取权重增量配置

        Args:
            kindid: 装备类型ID，用于动态配置权重

        Returns:
            Dict[str, float]: 要增加的权重配置（可以为负数）
        """
        return {}

    def get_tolerance_overrides(self, kindid: int = None) -> Dict[str, float]:
        """
        获取相对容忍度覆盖配置（已废弃绝对容忍度）

        Args:
            kindid: 装备类型ID，用于动态配置容忍度

        Returns:
            Dict[str, float]: 相对容忍度覆盖
        """
        return {}

    def get_tolerance_increments(self, kindid: int = None) -> Dict[str, float]:
        """
        获取相对容忍度增量配置（已废弃绝对容忍度）

        Args:
            kindid: 装备类型ID，用于动态配置容忍度

        Returns:
            Dict[str, float]: 相对容忍度增量
        """
        return {}

    def calculate_custom_similarity(self,
                                    feature_name: str,
                                    target_val: Any,
                                    market_val: Any) -> Optional[float]:
        """
        自定义特征相似度计算

        Args:
            feature_name: 特征名称
            target_val: 目标值
            market_val: 市场值

        Returns:
            Optional[float]: 相似度分数，如果返回None则使用默认计算方法
        """
        return None


class EquipmentPluginManager:
    """装备插件管理器"""

    def __init__(self, base_config: BaseEquipmentConfig):
        self.base_config = base_config
        self.plugins: List[EquipmentTypePlugin] = []
        self._kindid_plugin_map: Dict[int, List[EquipmentTypePlugin]] = {}

        # 使用插件包的自动加载功能
        try:
            # 尝试使用绝对导入路径
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            plugins_dir = os.path.join(current_dir, 'plugins')

            # 添加plugins目录到系统路径
            if plugins_dir not in sys.path:
                sys.path.insert(0, plugins_dir)

            from shoes_plugin import ShoesPlugin
            from helmet_plugin import HelmetPlugin
            from necklace_plugin import NecklacePlugin
            from belt_plugin import BeltPlugin
            from armor_plugin import ArmorPlugin
            from weapon_plugin import WeaponPlugin
            from lingshi_plugin import LingshiPlugin
            from pet_equip_plugin import PetEquipPlugin
            self.register_plugin(ShoesPlugin())
            self.register_plugin(HelmetPlugin())
            self.register_plugin(NecklacePlugin())
            self.register_plugin(BeltPlugin())
            self.register_plugin(ArmorPlugin())
            self.register_plugin(WeaponPlugin())
            self.register_plugin(LingshiPlugin())
            self.register_plugin(PetEquipPlugin())
            print("成功使用绝对导入加载所有插件!")

        except ImportError as e:
            print(f"插件自动加载失败: {e}")

    def register_plugin(self, plugin: EquipmentTypePlugin):
        """注册插件"""
        self.plugins.append(plugin)

        # 按优先级排序
        self.plugins.sort(key=lambda p: p.priority, reverse=True)

        # 更新kindid映射
        for kindid in plugin.supported_kindids:
            if kindid not in self._kindid_plugin_map:
                self._kindid_plugin_map[kindid] = []
            self._kindid_plugin_map[kindid].append(plugin)
            # 按优先级排序
            self._kindid_plugin_map[kindid].sort(
                key=lambda p: p.priority, reverse=True)

        print(f"已注册装备插件: {plugin.plugin_name} (优先级: {plugin.priority})")

    def get_plugins_for_kindid(self, kindid: int) -> List[EquipmentTypePlugin]:
        """获取支持指定kindid的插件列表"""
        return self._kindid_plugin_map.get(kindid, [])

    def get_enhanced_features(self, kindid: int, base_features: Dict[str, Any]) -> Dict[str, Any]:
        """获取增强后的特征（包含派生特征）"""
        enhanced_features = base_features.copy()

        # 应用所有支持该kindid的插件的派生特征
        for plugin in self.get_plugins_for_kindid(kindid):
            derived_features = plugin.get_derived_features(base_features)
            enhanced_features.update(derived_features)

        return enhanced_features

    def get_final_weights(self, kindid: int) -> Dict[str, float]:
        """获取最终的特征权重配置"""
        weights = self.base_config.base_feature_weights.copy()

        # 应用插件的权重配置
        for plugin in self.get_plugins_for_kindid(kindid):
            # 先应用增量
            increments = plugin.get_weight_increments(kindid)
            for key, increment in increments.items():
                weights[key] = weights.get(key, 0) + increment

            # 再应用覆盖
            overrides = plugin.get_weight_overrides(kindid)
            weights.update(overrides)

        return weights

    def get_final_tolerances(self, kindid: int) -> Dict[str, float]:
        """获取最终的相对容忍度配置（不再使用绝对容忍度）"""
        relative_tolerances = self.base_config.base_relative_tolerances.copy()

        # 应用插件的容忍度配置
        for plugin in self.get_plugins_for_kindid(kindid):
            # 先应用增量
            rel_increments = plugin.get_tolerance_increments(kindid)
            for key, increment in rel_increments.items():
                relative_tolerances[key] = relative_tolerances.get(
                    key, 0) + increment

            # 再应用覆盖
            rel_overrides = plugin.get_tolerance_overrides(kindid)
            relative_tolerances.update(rel_overrides)

        return relative_tolerances

    def calculate_plugin_similarity(self,
                                    kindid: int,
                                    feature_name: str,
                                    target_val: Any,
                                    market_val: Any) -> Optional[float]:
        """尝试使用插件计算特征相似度"""
        for plugin in self.get_plugins_for_kindid(kindid):
            similarity = plugin.calculate_custom_similarity(
                feature_name, target_val, market_val)
            if similarity is not None:
                return similarity
        return None


class EquipAnchorEvaluator:
    """装备锚定估价器 - 支持插拔式装备类型配置"""

    def __init__(self):
        """
        初始化装备锚定估价器

        Args:
            market_data_collector: 装备市场数据采集器实例，如果为None则创建新实例
        """
        self.logger = logging.getLogger(__name__)

        # 初始化装备市场数据采集器
        self.market_collector = EquipMarketDataCollector()

        # 初始化灵饰装备市场数据采集器
        self.lingshi_market_collector = LingshiMarketDataCollector()

        # 初始化宠物装备市场数据采集器
        self.pet_equip_market_collector = PetEquipMarketDataCollector()

        # 初始化特征提取器
        from src.evaluator.feature_extractor.equip_feature_extractor import EquipFeatureExtractor
        self.feature_extractor = EquipFeatureExtractor()

        # 初始化灵饰特征提取器
        from src.evaluator.feature_extractor.lingshi_feature_extractor import LingshiFeatureExtractor
        self.lingshi_feature_extractor = LingshiFeatureExtractor()

        # 初始化灵饰特征提取器
        from src.evaluator.feature_extractor.pet_equip_feature_extractor import PetEquipFeatureExtractor
        self.pet_equip_feature_extractor = PetEquipFeatureExtractor()

        # 初始化插拔式配置系统
        self.base_config = BaseEquipmentConfig()
        self.plugin_manager = EquipmentPluginManager(self.base_config)

        print("装备锚定估价器初始化完成，支持插拔式装备类型配置")
        print(f"已加载插件: {[p.plugin_name for p in self.plugin_manager.plugins]}")

    def add_plugin(self, plugin: EquipmentTypePlugin):
        """添加装备类型插件"""
        self.plugin_manager.register_plugin(plugin)

    def get_equip_type_configs(self, kindid: int) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        根据装备类型获取相应的配置（通过插件系统）

        Args:
            kindid: 装备类型ID

        Returns:
            Tuple[特征权重, 相对容忍度]
        """
        feature_weights = self.plugin_manager.get_final_weights(kindid)
        relative_tolerances = self.plugin_manager.get_final_tolerances(kindid)

        return feature_weights, relative_tolerances

    def find_market_anchors(self,
                            target_features: Dict[str, Any],
                            similarity_threshold: float = 0.7,
                            max_anchors: int = 30) -> List[Dict[str, Any]]:
        """
        寻找市场锚点装备

        Args:
            target_features: 目标装备特征字典
            similarity_threshold: 相似度阈值（0-1）
            max_anchors: 最大锚点数量

        Returns:
            List[Dict[str, Any]]: 锚点装备列表，每个元素包含：
                - similarity: 相似度分数
                - price: 价格
                - equip_sn: 装备序列号
                - features: 完整特征数据
        """
        try:
            print(f"开始寻找装备市场锚点，相似度阈值: {similarity_threshold}")
            # 获取目标装备的equip_sn，用于排除自身
            target_equip_sn = target_features.get('equip_sn')
            if target_equip_sn:
                print(f"目标装备序列号: {target_equip_sn}，将排除自身")

            # 构建预过滤条件以提高效率
            pre_filters = self._build_pre_filters(target_features)
            # 根据装备类型决定market_collector
            # 根据装备类型决定是否使用属性分类过滤
            target_kindid = target_features.get('kindid', 0)
            needs_addon_filter = self.base_config.needs_addon_classification_filter(
                target_kindid)
            # 根据装备类型决定饰市场数据采集器
            if self.base_config.is_lingshi(target_kindid):
                # 灵饰使用灵饰市场数据采集器
                market_data = self.lingshi_market_collector.get_market_data(
                    level_range=pre_filters.get('equip_level_range'),
                     **pre_filters,
                    limit=1000
                )
            elif target_kindid == 29:
                # 宠物装备使用宠物装备市场数据采集器
                print(f"宠物装备类型target_features: {pre_filters}")
                market_data = self.pet_equip_market_collector.get_market_data_with_addon_classification({
                        **pre_filters,
                        **target_features
                    })
            elif needs_addon_filter:
                # 需要属性分类过滤的装备类型（武器和防具）
                print(f"装备类型 {target_kindid} 需要属性分类过滤")
                pre_filters.update({
                    'addon_minjie': target_features.get('addon_minjie', 0),
                    'addon_liliang': target_features.get('addon_liliang', 0),
                    'addon_naili': target_features.get('addon_naili', 0),
                    'addon_tizhi': target_features.get('addon_tizhi', 0),
                    'addon_moli': target_features.get('addon_moli', 0)
                })
                # 获取预过滤的市场数据（使用属性分类过滤）
                market_data = self.market_collector.get_market_data_with_addon_classification(
                    pre_filters)
            else:
                # 不需要属性分类过滤的装备类型
                print(f"装备类型 {target_kindid} 不需要属性分类过滤")
                # 获取预过滤的市场数据（不使用属性分类过滤）
                market_data = self.market_collector.get_market_data(
                    kindid=pre_filters.get('kindid'),
                    level_range=pre_filters.get('equip_level_range'),
                    special_skill=pre_filters.get('special_skill'),
                    suit_effect=pre_filters.get('suit_effect'),
                    special_effect=pre_filters.get('special_effect'),
                    limit=1000
                )

            if market_data.empty:
                print("装备市场数据为空，无法找到锚点")
                return []

            print(f"预过滤后获得 {len(market_data)} 条候选装备数据")

            # 计算所有市场装备的相似度
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

                    # 从市场数据提取特征
                    if self.base_config.is_lingshi(target_kindid):
                        market_features = self.lingshi_feature_extractor.extract_features(
                            market_row.to_dict())
                    elif target_kindid == 29:
                        market_features = self.pet_equip_feature_extractor.extract_features(
                            market_row.to_dict())
                    else:
                        market_features = self.feature_extractor.extract_features(
                            market_row.to_dict())

                    # 计算相似度
                    similarity = self._calculate_similarity(
                        target_features, market_features)

                    if similarity >= similarity_threshold:
                        anchor_candidates.append({
                            # 优先使用真实的equip_sn，如果没有则使用索引
                            'equip_sn': current_equip_sn,
                            'similarity': float(similarity),
                            'price': float(market_row.get('price', 0)),
                            'features': market_row.to_dict()
                        })

                except Exception as e:
                    # 记录有问题的数据
                    self.logger.error(
                        f"处理装备 {market_row.get('equip_sn', idx)} 时出错: {e}")
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

            print(f"找到 {len(anchors)} 个装备市场锚点")
            if excluded_self_count > 0:
                print(f"排除目标装备自身 {excluded_self_count} 次")
            if anchors:
                print(
                    f"相似度范围: {anchors[-1]['similarity']:.3f} - {anchors[0]['similarity']:.3f}")
                print(
                    f"价格范围: {min(a['price'] for a in anchors):.1f} - {max(a['price'] for a in anchors):.1f}")

            return anchors

        except Exception as e:
            self.logger.error(f"寻找装备市场锚点失败: {e}")
            return []

    def _build_pre_filters(self, target_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据目标装备特征构建预过滤条件，减少计算量

        Args:
            target_features: 目标装备特征

        Returns:
            Dict[str, Any]: 过滤条件
        """
        filters = {}

        # 装备等级过滤（±10级）
        if 'equip_level' in target_features:
            level = target_features['equip_level']
            filters['equip_level_range'] = (max(1, level - 10), level + 10)

        # 装备类型必须完全一致
        if 'kindid' in target_features:
            filters['kindid'] = target_features['kindid']

        # 高价值特效必须包含
        if 'special_effect' in target_features and len(target_features['special_effect']) > 0:
            filters['special_effect'] = target_features['special_effect']

        # 超级简易 (布尔值类型)
        if 'is_super_simple' in target_features and target_features['is_super_simple'] is not None:
            filters['is_super_simple'] = target_features['is_super_simple']

        # 特技必须完全一致（如果有特技）
        if 'special_skill' in target_features:
            special_skill = target_features['special_skill']
            # 尝试转换为数字后比较
            try:
                special_skill_num = int(
                    special_skill) if special_skill is not None else 0
                if special_skill_num > 0:
                    filters['special_skill'] = special_skill_num
            except (ValueError, TypeError):
                # 转换失败，跳过特技过滤
                pass

        # 套装效果
        if 'suit_effect' in target_features:
            suit_effect = target_features['suit_effect']
            # 尝试转换为数字后比较
            try:
                suit_effect_num = int(
                    suit_effect) if suit_effect is not None else 0
                if suit_effect_num > 0:
                    filters['suit_effect'] = suit_effect_num
            except (ValueError, TypeError):
                # 转换失败（可能是pet_equip的字符串套装），直接使用原值
                if suit_effect and str(suit_effect).strip():
                    filters['suit_effect'] = suit_effect

        # 查找灵饰主属性 （damage、defense、magic_damage、magic_defense、fengyin、anti_fengyin、speed）
        # 以上其中一个大于0则就是主属性记录 main_attr到filters中 ，直接记录字段名字就行，比如damage
        kindid = target_features.get('kindid', 0)
        if self.base_config.is_lingshi(kindid):
            filters['attrs'] = target_features.get('attrs', [])
            # 灵饰装备主属性候选
            lingshi_main_attrs = ['damage', 'defense', 'magic_damage',
                                  'magic_defense', 'fengyin', 'anti_fengyin', 'speed']

            for attr_name in lingshi_main_attrs:
                attr_value = target_features.get(attr_name, 0)
                if attr_value > 0:
                    filters['main_attr'] = attr_name
                    print(
                        f"[灵饰主属性] kindid={kindid}, 主属性={attr_name}, 值={attr_value}")
                    break  # 只取第一个找到的主属性
        elif kindid == 29:
            print(f"TODO:")

        return filters

    def _calculate_similarity(self,
                              target_features: Dict[str, Any],
                              market_features: Dict[str, Any]) -> float:
        """
        计算两个装备特征的相似度 - 支持插拔式装备类型配置

        Args:
            target_features: 目标装备特征
            market_features: 市场装备特征

        Returns:
            float: 相似度分数（0-1）
        """
        try:
            # 输入验证
            if not isinstance(target_features, dict) or not isinstance(market_features, dict):
                self.logger.warning("装备特征数据格式错误，使用默认相似度")
                return 0.0

            # 获取装备类型相关配置（通过插件系统）
            kindid = target_features.get('kindid', 0)
            feature_weights, relative_tolerances = self.get_equip_type_configs(
                kindid)

            # 特征增强：添加派生特征
            enhanced_target_features = self.plugin_manager.get_enhanced_features(
                kindid, target_features)
            enhanced_market_features = self.plugin_manager.get_enhanced_features(
                kindid, market_features)

            total_weight = 0
            weighted_similarity = 0

            # 合并所有特征名称（包括派生特征）
            all_features = set(enhanced_target_features.keys()) | set(
                enhanced_market_features.keys())
            # 过滤掉一些元数据字段
            excluded_features = {'equip_sn',
                                 'price', 'server_id', 'create_time'}
            all_features = all_features - excluded_features

            # 收集所有特征的计算结果，用于按得分排序输出
            feature_results = []

            for feature_name in all_features:
                if feature_name not in enhanced_target_features and feature_name not in enhanced_market_features:
                    continue

                target_val = enhanced_target_features.get(feature_name, 0)
                market_val = enhanced_market_features.get(feature_name, 0)
                weight = feature_weights.get(feature_name, 0.5)

                # 尝试使用插件的自定义相似度计算
                plugin_similarity = self.plugin_manager.calculate_plugin_similarity(
                    kindid, feature_name, target_val, market_val)

                if plugin_similarity is not None:
                    # 使用插件的自定义计算结果
                    feature_similarity = plugin_similarity
                    calculation_method = "插件"
                elif target_val == 0 and market_val == 0:
                    # 两者都为0，完全匹配
                    feature_similarity = 1.0
                    calculation_method = "默认"
                elif feature_name in ['suit_effect']:
                    # 套装效果特殊相似度计算
                    target_kindid = enhanced_target_features.get('kindid')
                    market_kindid = enhanced_market_features.get('kindid')
                    feature_similarity = self._calculate_suit_effect_similarity(
                        target_val, market_val, target_kindid, market_kindid)
                    calculation_method = "套装"
                elif feature_name in relative_tolerances:
                    # 使用装备类型特定的相对容忍度计算
                    tolerance = relative_tolerances[feature_name]

                    if feature_name == 'repair_fail_num':
                        # 修理失败次数特殊处理：次数越多越不好
                        if target_val == market_val:
                            feature_similarity = 1.0
                        elif market_val > target_val:
                            # 市场装备修理失败次数更多，相似度降低更多
                            diff = market_val - target_val
                            feature_similarity = max(
                                0.0, 1.0 - diff * 0.3)  # 每多1次失败，相似度降低0.3
                        else:
                            # 目标装备修理失败次数更多，相似度降低较少
                            diff = target_val - market_val
                            feature_similarity = max(
                                0.0, 1.0 - diff * 0.2)  # 每多1次失败，相似度降低0.2
                        calculation_method = "修理"
                    elif feature_name in ['special_skill', 'suit_effect']:
                        # 特技和套装效果必须完全一致（容忍度为0）
                        if target_val == market_val:
                            feature_similarity = 1.0
                        else:
                            feature_similarity = 0.0
                        calculation_method = "特技"
                    elif target_val == 0 or market_val == 0:
                        feature_similarity = 0.10
                        calculation_method = "零值"
                    else:
                        # 计算相对差异 - 先检查数据类型
                        try:
                            # 处理列表和字典类型的特征值
                            if isinstance(target_val, (list, dict)) or isinstance(market_val, (list, dict)):
                                print(f"[DEBUG] 特征 '{feature_name}' 包含复杂类型:")
                                print(
                                    f"  目标值: {target_val} (类型: {type(target_val)})")
                                print(
                                    f"  市场值: {market_val} (类型: {type(market_val)})")

                                # 对于复杂类型，使用简单匹配
                                if target_val == market_val:
                                    feature_similarity = 1.0
                                else:
                                    feature_similarity = 0.1  # 给予较低相似度
                                calculation_method = "复杂"
                            else:
                                # 确保都是数值类型后进行计算
                                target_numeric = float(
                                    target_val) if target_val is not None else 0
                                market_numeric = float(
                                    market_val) if market_val is not None else 0

                                denominator = max(
                                    abs(target_numeric), abs(market_numeric))
                                diff_ratio = abs(
                                    target_numeric - market_numeric) / denominator

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
                                calculation_method = "容忍"

                        except (TypeError, ValueError) as e:
                            # 捕获类型错误并记录详细信息
                            print(f"[DEBUG] 特征 '{feature_name}' 转换失败:")
                            print(
                                f"  目标值: {target_val} (类型: {type(target_val)})")
                            print(
                                f"  市场值: {market_val} (类型: {type(market_val)})")
                            print(f"  错误信息: {e}")

                            # 对于无法处理的类型，使用简单匹配
                            if target_val == market_val:
                                feature_similarity = 1.0
                            else:
                                feature_similarity = 0.5
                            calculation_method = "错误"
                else:
                    # 未配置的特征，使用默认逻辑
                    if target_val == market_val:
                        feature_similarity = 1.0
                    else:
                        feature_similarity = 0.5  # 给予中等相似度
                    calculation_method = "默认"

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

            # 按加权得分降序排序并输出
            feature_results.sort(key=lambda x: x['weight'], reverse=True)

            # 添加特征权重日志
            print(f"\n=== 相似度计算详情 (kindid: {kindid}) ===")
            print("特征名称                 | 目标值    | 市场值    | 权重     | 相似度   | 加权得分 | 计算方法")
            print("-" * 90)

            for result in feature_results:
                if result['weight'] > 0.1:
                    print(f"{result['name']:20s} | {str(result['target_val']):>8s} | {str(result['market_val']):>8s} | {result['weight']:7.2f} | {result['similarity']:7.3f} | {result['weighted_score']:7.3f} | {result['method']:>6s}")

            print("-" * 90)
            print(
                f"{'总计':20s} | {'':8s} | {'':8s} | {total_weight:7.2f} | {'':7s} | {weighted_similarity:7.3f} | {'':6s}")
            print(
                f"最终相似度: {weighted_similarity:.3f} / {total_weight:.3f} = {weighted_similarity/total_weight if total_weight > 0 else 0:.3f}")
            print("=" * 90)

            return weighted_similarity / total_weight if total_weight > 0 else 0.0

        except Exception as e:
            self.logger.error(f"计算装备相似度失败: {e}")
            return 0.0

    def _calculate_suit_effect_similarity(self, target_val: int, market_val: int, target_kindid: int, market_kindid: int) -> float:
        """
        计算套装效果相似度

        Args:
            target_val: 目标套装效果ID
            market_val: 市场套装效果ID
            target_kindid: 目标装备类型ID
            market_kindid: 市场装备类型ID

        Returns:
            float: 相似度分数（0-1）
        """
        # 完全相同的情况
        if target_val == market_val:
            return 1.0

        # 如果目标装备没有套装效果，市场装备也没有套装效果
        if target_val == 0 and market_val == 0:
            return 1.0

        # 如果目标装备有套装效果，市场装备没有套装效果（或反之）
        if target_val == 0 or market_val == 0:
            return 0.1  # 一个有套装一个没有，相似度很低

        # 敏捷套和魔力套的详细分类逻辑
        # 新增规则：类型kindid为17（男头）、18（男衣）、19（鞋子）敏捷套的不适配跨套装类型匹配，如kindid为17的敏捷套只能和kindid为17的敏捷套匹配，不能再跟kindid为17的魔力套匹配
        # 因为固伤门派都是女性角色，而鞋子有敏捷属性要求，一般敏捷套装不选鞋子，因为对鞋子等级和初敏要求很高
        agility_suits = {
            'B': [1040, 1047, 1049],  # 凤凰, 幽灵, 吸血鬼
            # 画魂, 雾中仙, 机关鸟, 巴蛇, 猫灵（人型）, 修罗傀儡妖
            'A': [1053, 1056, 1065, 1067, 1070, 1077]
        }

        # 魔力套
        # 新增规则：类型kindid为21（饰品）魔力套的不适配跨套装类型匹配，如kindid为21的魔力套只能和kindid为21的魔力套匹配，不能再跟kindid为21的敏捷套匹配
        # 因为饰品有灵力属性要求，一般魔力套装不选饰品，因为对饰品等级和初灵要求很高
        magic_suits = {
            # 蛟龙, 雨师, 如意仙子, 星灵仙子, 净瓶女娲, 灵符女娲
            'B': [1041, 1042, 1043, 1046, 1050, 1052],
            # 灵鹤, 炎魔神, 葫芦宝贝, 混沌兽, 长眉灵猴, 蜃气妖
            'A': [1057, 1059, 1069, 1073, 1074, 1081]
        }

        def get_suit_info(suit_id):
            """获取套装信息：(类型, 等级)"""
            if suit_id in agility_suits['B']:
                return ('agility', 'B')
            elif suit_id in agility_suits['A']:
                return ('agility', 'A')
            elif suit_id in magic_suits['B']:
                return ('magic', 'B')
            elif suit_id in magic_suits['A']:
                return ('magic', 'A')
            else:
                return (None, None)

        # 检查是否为敏捷套或魔力套
        target_type, target_grade = get_suit_info(target_val)
        market_type, market_grade = get_suit_info(market_val)

        # 如果都是敏捷套或魔力套，使用原有的详细逻辑
        if target_type is not None and market_type is not None:
            # 新增规则：检查装备类型限制
            # 类型kindid为19（鞋子）敏捷套的不适配跨套装类型匹配
            # 类型kindid为21（饰品）魔力套的不适配跨套装类型匹配
            # 17（男头）、18（男衣）待定
            restricted_agility_kindids = [19]  # 男头、男衣、鞋子
            restricted_magic_kindids = [21]  # 饰品

            # 检查是否为限制类型的装备
            is_restricted_agility = (target_kindid in restricted_agility_kindids and
                                     market_kindid in restricted_agility_kindids and
                                     target_kindid == market_kindid)
            is_restricted_magic = (target_kindid in restricted_magic_kindids and
                                   market_kindid in restricted_magic_kindids and
                                   target_kindid == market_kindid)

            # 如果是限制类型的装备，且套装类型不同，则相似度为0
            if (is_restricted_agility or is_restricted_magic) and target_type != market_type:
                return 0.0

            # 正常的敏捷套/魔力套相似度计算
            if target_type == market_type and target_grade == market_grade:
                # 同类型同等级（如巴蛇A级敏捷套 -> 机关鸟A级敏捷套）
                return 0.95
            elif target_type != market_type and target_grade == market_grade:
                # 不同类型同等级（如巴蛇A级敏捷套 -> 灵鹤A级魔力套）
                return 0.9
            elif target_type == market_type and target_grade != market_grade:
                # 同类型跨等级（如巴蛇A级敏捷套 -> 凤凰B级敏捷套）
                return 0.75
            elif target_type != market_type and target_grade != market_grade:
                # 不同类型跨等级（如巴蛇A级敏捷套 -> 蛟龙B级魔力套）
                return 0.3

        # 其他套装效果：使用简化逻辑，给予较低的相似度
        # 这样可以避免套装效果差异过大的装备被误认为相似
        return 0.2

    def calculate_value(self,
                        target_features: Dict[str, Any],
                        strategy: str = 'fair_value',
                        similarity_threshold: float = 0.7,
                        max_anchors: int = 30) -> Dict[str, Any]:
        """
        计算装备价值

        Args:
            target_features: 目标装备特征字典
            strategy: 定价策略 ('competitive', 'fair_value', 'premium')
            similarity_threshold: 相似度阈值（0-1）
            max_anchors: 最大锚点数量

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
            print(
                f"开始计算装备价值，策略: {strategy}，相似度阈值: {similarity_threshold}，最大锚点数: {max_anchors}")

            # 寻找市场锚点
            anchors = self.find_market_anchors(
                target_features, similarity_threshold, max_anchors)

            if len(anchors) == 0:
                self.logger.error(f"未找到装备市场锚点")
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
                    'error': '未找到足够的相似装备进行估价',
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
                # 溢价定价：75%分位数 × 0.95
                estimated_price = float(
                    np.percentile(anchor_prices, 75) * 0.95)
            else:  # fair_value
                # 公允价值：相似度加权中位数 × 0.93
                base_price = self._weighted_median(
                    anchor_prices, anchor_similarities)
                estimated_price = float(base_price * 0.93)

            # 计算置信度
            confidence = self._calculate_confidence(
                anchors, len(anchor_prices))

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

            print(
                f"装备估价完成: {estimated_price:.1f}，基于 {len(anchors)} 个锚点，置信度: {confidence:.2f}")

            return result

        except Exception as e:
            self.logger.error(f"计算装备价值失败: {e}")
            return {
                'estimated_price': 0,
                'anchor_count': 0,
                'error': str(e)
            }

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
                return float(value)

        return float(paired[-1][0])  # fallback

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
            avg_similarity = float(np.mean([anchor['similarity']
                                           for anchor in anchors]))
            similarity_bonus = avg_similarity * 0.3
        else:
            similarity_bonus = 0

        # 价格稳定性加成
        if len(anchors) >= 3:
            prices = [anchor['price'] for anchor in anchors]
            price_cv = float(np.std(prices) /
                             np.mean(prices)) if np.mean(prices) > 0 else 1.0
            stability_bonus = max(0, (0.5 - price_cv) * 0.4)  # CV低于0.5时有加成
        else:
            stability_bonus = 0

        final_confidence = min(
            base_confidence + similarity_bonus + stability_bonus, 1.0)
        return float(final_confidence)

    def value_distribution_report(self, target_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成装备价值分布报告

        Args:
            target_features: 目标装备特征字典

        Returns:
            Dict[str, Any]: 价值分布报告
        """
        try:
            print("生成装备价值分布报告...")

            # 寻找锚点
            anchors = self.find_market_anchors(
                target_features, similarity_threshold=0.5, max_anchors=50)

            if len(anchors) == 0:
                return {
                    'error': '未找到足够的装备市场锚点',
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
            competitive_result = self.calculate_value(
                target_features, 'competitive', max_anchors=len(anchors))
            fair_result = self.calculate_value(
                target_features, 'fair_value', max_anchors=len(anchors))

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
                        'equip_sn': anchor['equip_sn'],
                        'price': float(anchor['price']),
                        'similarity': round(float(anchor['similarity']), 3),
                        'equip_level': int(anchor['features'].get('equip_level', 0)),
                        'kindid': int(anchor['features'].get('kindid', 0))
                    }
                    for anchor in anchors[:20]  # 返回前20个详细信息
                ]
            }

            print(f"装备价值分布报告生成完成，基于 {len(anchors)} 个锚点")

            return report

        except Exception as e:
            self.logger.error(f"生成装备价值分布报告失败: {e}")
            return {'error': str(e)}

    def batch_valuation(self,
                        equip_list: List[Dict[str, Any]],
                        strategy: str = 'fair_value') -> List[Dict[str, Any]]:
        """
        批量装备估价

        Args:
            equip_list: 装备特征列表
            strategy: 定价策略

        Returns:
            List[Dict[str, Any]]: 批量估价结果列表
        """
        results = []

        print(f"开始批量装备估价，共 {len(equip_list)} 个装备")

        for i, equip_features in enumerate(equip_list):
            try:
                result = self.calculate_value(equip_features, strategy)
                result['equip_index'] = i
                results.append(result)

                if (i + 1) % 10 == 0:
                    print(f"已完成 {i + 1}/{len(equip_list)} 个装备的估价")

            except Exception as e:
                self.logger.error(f"批量估价第 {i+1} 个装备失败: {e}")
                results.append({
                    'equip_index': i,
                    'estimated_price': 0,
                    'error': str(e)
                })

        print(
            f"批量装备估价完成，成功估价 {len([r for r in results if 'error' not in r])} 个装备")

        return results
