import json
import re
import numpy as np
from datetime import datetime
import logging
from typing import Dict, Any, Union, List
import os
from src.utils.jsonc_loader import load_jsonc_relative_to_file

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EquipFeatureExtractor:
    """梦幻西游装备特征提取器"""

    def __init__(self):
        """初始化特征提取器"""
        print("初始化特征提取器...")
        self.logger = logging.getLogger(__name__)

        # 加载配置文件
        self._load_configs()

        # 初始化正则表达式
        self._init_patterns()

    def _load_configs(self):
        """加载配置文件"""
        try:
            # 加载自动搜索配置
            config_path = os.path.join(os.path.dirname(
                __file__), '../../constant/auto_search_config.json')
            self.auto_config = load_jsonc_relative_to_file(
                __file__, '../../constant/auto_search_config.json')

            # 特技配置
            self.special_skills = {}
            if 'equip_special_skills' in self.auto_config:
                for skill in self.auto_config['equip_special_skills']:
                    if len(skill) >= 2:
                        self.special_skills[skill[0]] = skill[1]

            # 特效配置
            self.special_effects = self.auto_config.get(
                'equip_special_effect', {})

            # 宝石配置
            self.gems_name = self.auto_config.get('gems_name', {})

            # 套装效果配置
            self.suit_effects = self.auto_config.get('suit_effects', {})

        except Exception as e:
            self.logger.warning(f"加载配置文件失败: {e}")
            self.auto_config = {}
            self.special_skills = {}
            self.special_effects = {}
            self.gems_name = {}
            self.suit_effects = {}

    def _init_patterns(self):
        """初始化正则表达式"""
        # 开运孔数
        self.hole_pattern = r"开运孔数：(\d+)孔/(\d+)孔"
        # 修理失败次数
        self.repair_fail_pattern = r"修理失败\s+(\d+)次"

    def extract_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float, str]]:
        """
        提取所有特征
        Returns:
            Dict[str, Union[int, float, str]]: 提取的特征字典，包含以下字段:
                
                ===== 基础属性特征 =====
                - equip_level (int): 装备等级
                - kindid (int): 装备类型ID
                - init_damage (int): 初伤（包含命中）
                - init_damage_raw (int): 初伤（不含命中）
                - all_damage (int): 总伤害
                - init_wakan (int): 初灵
                - init_defense (int): 初防
                - init_hp (int): 初血
                - init_dex (int): 初敏
                - mingzhong (int): 命中
                - shanghai (int): 伤害
                
                ===== 附加属性特征 =====
                - addon_tizhi (int): 附加体质
                - addon_liliang (int): 附加力量
                - addon_naili (int): 附加耐力
                - addon_minjie (int): 附加敏捷
                - addon_lingli (int): 附加灵力
                - addon_moli (float): 附加魔力（从agg_added_attrs解析）
                - addon_total (int): 附加属性总和
                
                ===== 宝石特征 =====
                - gem_value (list): 宝石类型列表
                - gem_score (float): 宝石得分（0-100分，基于宝石等级和类型计算）
                
                ===== 特技特效套装特征 =====
                - special_skill (int): 特技ID
                - special_effect (list): 特效列表
                - suit_effect (int): 套装效果ID（仅当不为0时包含）
                
                ===== 其他特征（从large_equip_desc提取） =====
                - hole_score (float): 开运孔数得分（0-100分，基于孔数价值计算）
                - repair_fail_num (int): 修理失败次数
                
                特征说明：
                - 宝石得分计算：基于宝石等级和类型，以10级黑宝石为满分参考
                - 开运孔数得分：0-2孔0分，3孔15分，4孔75分，5孔200分，标准化到0-100分
                - 套装效果：仅当suit_effect不为0时才包含该特征
                - 魔力属性：从agg_added_attrs字符串中解析提取
        """
        try:
            features = {}

            # 一、基础属性特征
            features.update(self._extract_basic_features(equip_data))

            # 二、附加属性
            features.update(self._extract_added_attrs_features(equip_data))

            # 三、宝石
            features.update(self._extract_gem_features(equip_data))

            # 四、特技
            features.update(self._extract_special_skill_features(equip_data))

            # 五、特效
            features.update(self._extract_special_effect_features(equip_data))

            #  六、套装
            features.update(self._extract_suit_effect_features(equip_data))

            # 七、其他特征（从large_equip_desc提取）
            features.update(self._extract_other_features(equip_data))

            return features

        except Exception as e:
            print(f"特征提取失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise

    def _extract_basic_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float]]:
        """提取基础属性特征"""
        features = {}

        # 等级
        features['equip_level'] = equip_data.get(
            'equip_level', equip_data.get('level', 0))

        # 类型
        features['kindid'] = equip_data.get('kindid', 0)

        # 初伤（包含命中）
        features['init_damage'] = equip_data.get('init_damage', 0)
        # 初伤（包含命中）
        features['init_damage_raw'] = equip_data.get('init_damage_raw', 0)
        # 总伤
        features['all_damage'] = equip_data.get('all_damage', 0)

        # 初灵
        features['init_wakan'] = equip_data.get('init_wakan', 0)

        # 初防
        features['init_defense'] = equip_data.get('init_defense', 0)

        # 初血
        features['init_hp'] = equip_data.get('init_hp', 0)

        # 初敏
        features['init_dex'] = equip_data.get('init_dex', 0)

        # 命中
        features['mingzhong'] = equip_data.get('mingzhong', 0)

        # 伤害
        features['shanghai'] = equip_data.get('shanghai', 0)

        return features

    def _extract_added_attrs_features(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取附加属性特征"""
        features = {}

        # 具体附加属性
        features['addon_tizhi'] = equip_data.get('addon_tizhi', 0)
        features['addon_liliang'] = equip_data.get('addon_liliang', 0)
        features['addon_naili'] = equip_data.get('addon_naili', 0)
        features['addon_minjie'] = equip_data.get('addon_minjie', 0)
        features['addon_lingli'] = equip_data.get('addon_lingli', 0)
        # features['addon_fali'] = equip_data.get('addon_fali', 0)
        # 魔力需从agg_added_attrs(示例："[\"灵力 +42 耐力 +24 魔力 +27\"]")中获取 ，这里取 27
        features['addon_moli'] = self._extract_moli_from_agg_added_attrs(equip_data.get('agg_added_attrs', []))
        features['addon_total'] = equip_data.get('addon_total', 0)

        return features

    def _extract_gem_features(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取宝石特征"""
        features = {}

        # 宝石类型
        gem_value = equip_data.get('gem_value', [])
        if isinstance(gem_value, str):
            try:
                gem_value = json.loads(gem_value)
            except:
                gem_value = []
        
        # 确保gem_value是列表
        if not isinstance(gem_value, list):
            gem_value = []
        # 取自藏宝阁8级宝石价格 
        gem_value_score = {
            6: 160,   # 黑宝石（最高价值）
            3: 100,   # 舍利子
            1: 75,    # 红玛瑙
            5: 69,    # 月亮石
            2: 65,    # 太阳石
            4: 32,    # 光芒石
            12: 20,   # 翡翠石（最低价值）
        }
        # 宝石价值参考：
        # - 同等级情况下，黑宝石得分最高，翡翠石得分最低
        # - 最终得分 = (2^宝石等级 - 1) * 宝石基础价值
        # - 标准化后的0-100分以10级黑宝石为满分参考
        features['gem_value'] = gem_value

        # 宝石等级
        gem_level = equip_data.get('gem_level', 0)

        # 宝石得分 - 取价值最小的宝石类型计算，标准化到0-100分
        min_gem_score = 0
        if gem_level > 0 and gem_value:
            base_multiplier = (2 ** gem_level) - 1
            # 找到价值最小的宝石
            min_gem_value = float('inf')
            for gem_id in gem_value:
                gem_score = gem_value_score.get(gem_id, 0)
                min_gem_value = min(min_gem_value, gem_score)
            
            # 如果找到了有效宝石，计算得分
            if min_gem_value != float('inf'):
                raw_score = base_multiplier * min_gem_value
                
                # 标准化到0-100分
                # 计算标准：
                # - 100分: 10级黑宝石 (2^10-1) * 160 = 163,680
                # - 80分: 9级黑宝石 (2^9-1) * 160 = 81,760  
                # - 50分: 8级黑宝石 (2^8-1) * 160 = 40,800
                # - 25分: 7级黑宝石 (2^7-1) * 160 = 20,320
                # - 超过100分的装备会被限制为100分
                max_reference_score = ((2 ** 10) - 1) * 160  # 10级黑宝石作为满分参考
                min_gem_score = min(100.0, (raw_score / max_reference_score) * 100)
        features['gem_score'] = round(min_gem_score, 2)

        return features

    def _extract_special_skill_features(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取特技特征"""
        features = {}

        # 特技ID
        special_skill = equip_data.get('special_skill', 0)
        features['special_skill'] = special_skill

        return features

    def _extract_special_effect_features(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取特效特征"""
        features = {}

        # 特效
        special_effect = equip_data.get('special_effect', [])
        if isinstance(special_effect, str):
            try:
                special_effect = json.loads(special_effect)
            except:
                special_effect = []

        features['special_effect'] = special_effect

        return features

    def _extract_suit_effect_features(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取套装效果特征"""
        features = {}

        # 套装效果ID
        suit_effect = equip_data.get('suit_effect', 0)
        
        # 如果套装效果为0，则不包含这个特征（这样相似度计算时会自动跳过）
        if suit_effect != 0:
            features['suit_effect'] = suit_effect
            print(f"[DEBUG] 提取到有效套装效果: {suit_effect}")
        else:
            print(f"[DEBUG] 套装效果为0，跳过该特征提取")

        return features

    def _extract_other_features(self, equip_data: Dict[str, Any]) -> Dict[str, int]:
        """从large_equip_desc提取其他特征"""
        features = {}

        # 默认值
        current_holes = 0
        features['hole_score'] = 0
        features['repair_fail_num'] = 0

        # 从large_equip_desc解析
        large_desc = equip_data.get('large_equip_desc', '')
        if large_desc:
            # 解析开运孔数
            
            hole_match = re.search(self.hole_pattern, large_desc)
            if hole_match:
                current_holes = int(hole_match.group(1))
                max_holes = int(hole_match.group(2))

            # 解析修理失败次数
            repair_match = re.search(self.repair_fail_pattern, large_desc)
            if repair_match:
                repair_count = int(repair_match.group(1))
                features['repair_fail_num'] = repair_count
                print(f"成功提取修理失败次数: {repair_count}")
            else:
                # 如果包含修理信息但没有匹配到，记录一下
                if "修理失败" in large_desc:
                    print(f"警告：发现修理失败信息但正则匹配失败")
                    print(f"使用的模式: {self.repair_fail_pattern}")
                    # 提取修理失败相关的片段用于调试
                    start_idx = large_desc.find("修理失败")
                    end_idx = large_desc.find("#", start_idx)
                    if end_idx == -1:
                        end_idx = start_idx + 20
                    repair_part = large_desc[start_idx:end_idx]
                    print(f"修理失败片段: '{repair_part}'")
            # 开运孔数得分 0、1、2  、3、4、5孔差异大
            # 以藏宝阁白板鞋子为基准
            # 开运孔数标准化得分计算
            hole_value_mapping = {
                0: 0,    # 0孔：0元
                1: 0,    # 1孔：0元  
                2: 0,    # 2孔：0元
                3: 15,   # 3孔：15元
                4: 75,   # 4孔：75元
                5: 200,  # 5孔：200元（满分参考）
            }
            
            hole_raw_value = hole_value_mapping.get(current_holes, 0)
            # 标准化到0-100分，以5孔200元为满分参考
            max_hole_value = 200  # 5孔的价值
            hole_score = (hole_raw_value / max_hole_value) * 100 if max_hole_value > 0 else 0
            features['hole_score'] = round(hole_score, 2)

        return features

    def extract_features_batch(self, equip_list: List[Dict[str, Any]]) -> List[Dict[str, Union[int, float, str]]]:
        """批量提取特征"""
        results = []
        for equip_data in equip_list:
            try:
                features = self.extract_features(equip_data)
                results.append(features)
            except Exception as e:
                self.logger.error(f"提取装备特征失败: {e}")
                results.append({})
        return results

    def _extract_moli_from_agg_added_attrs(self, agg_added_attrs) -> float:
        """从agg_added_attrs中提取魔力属性值"""
        try:
            # 处理agg_added_attrs的不同格式
            if isinstance(agg_added_attrs, str):
                # 如果是字符串，尝试解析为JSON
                try:
                    import json
                    attrs_list = json.loads(agg_added_attrs)
                except (json.JSONDecodeError, TypeError):
                    # 如果解析失败，尝试直接处理字符串
                    attrs_list = [agg_added_attrs]
            elif isinstance(agg_added_attrs, list):
                attrs_list = agg_added_attrs
            else:
                return 0.0
            
            # 遍历所有属性字符串，查找魔力属性
            for attr in attrs_list:
                if isinstance(attr, str) and "魔力" in attr:
                    # 使用正则表达式提取魔力数值
                    import re
                    moli_match = re.search(r'魔力\s*\+?\s*(\d+(?:\.\d+)?)', attr)
                    if moli_match:
                        return float(moli_match.group(1))
            
            return 0.0
            
        except Exception as e:
            self.logger.warning(f"提取魔力属性时出错: {e}")
            return 0.0
