import json
import re
import numpy as np
from datetime import datetime
import logging
from typing import Dict, Any, Union, List
import os
from utils.jsonc_loader import load_js_config_relative_to_file
from src.evaluator.constants.equipment_types import SHOES_KINDID,BELT_KINDID,is_weapon,is_helm,NECKLACE_KINDID, is_armor
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
            self.auto_config = load_js_config_relative_to_file(
                __file__, '../../constant/auto_search_config.js')

            # 特技配置
            self.special_skills = {}
            if 'equip_special_skills' in self.auto_config:
                for skill in self.auto_config['equip_special_skills']:
                    if len(skill) >= 2:
                        self.special_skills[skill[1]] = skill[0]

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
        # 熔炼效果 - 修复正则表达式以包含#r
        self.ronglian_pattern = r"熔炼效果：#r#Y#r([^#]+(?:#r[^#]+)*)"
        # #r玩家68766666专用#r   
        self.binding_pattern = r"玩家(\d+)专用"

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
                - gem_level (int): 宝石等级
                - gem_score (float): 宝石得分（0-100分，基于宝石等级和类型计算）

                ===== 特技特效套装特征 =====
                - special_skill (int): 特技ID
                - special_effect (list): 特效列表
                - suit_effect (int): 套装效果ID（仅当不为0时包含）

                ===== 其他特征（从large_equip_desc提取） =====
                - hole_score (float): 开运孔数得分（0-100分，基于孔数价值计算）
                - repair_fail_num (int): 修理失败次数
                - binding (int): 绑定状态（0: 未绑定，1: 绑定）

                特征说明：
                - 宝石得分计算：基于宝石等级和类型，以10级黑宝石为满分参考
                - 开运孔数得分：0-2孔0分，3孔15分，4孔75分，5孔200分，标准化到0-100分
                - 套装效果：仅当suit_effect不为0时才包含该特征
                - 魔力属性：从agg_added_attrs字符串中解析提取
        """
        try:
            features = {}
            _is_desc_only_data = self._is_desc_only_data(equip_data)
            # 检查是否只有cDesc字段，如果是则先解析
            if _is_desc_only_data:
                equip_data = self._parse_equip_data_from_desc(equip_data)
            # TODO: 这里需要优化，如果kindid为0，则返回equip_data
            if equip_data.get('kindid', 0) == 0:
                return equip_data
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
            
            # 解析熔炼效果
            ronglian_features = self._extract_ronglian_zhizaobang_features(equip_data)
            
            # 应用熔炼特征到装备特征中
            self._apply_ronglian_features(features, ronglian_features, equip_data,_is_desc_only_data)

            return features

        except Exception as e:
            print(f"特征提取失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise

    def _is_desc_only_data(self, equip_data: Dict[str, Any]) -> bool:
        """
        判断是否为只有cDesc字段的数据

        Args:
            equip_data: 装备数据字典

        Returns:
            bool: 如果只有cDesc字段则返回True
        """
        # 检查是否只有cDesc字段
        if 'cDesc' in equip_data and( 'iType' in equip_data or 'kindid' in equip_data ):
            return True
        return False

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
        # 初伤（不包含命中）
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
        """提取附加属性特征
        只有武器和防具有属性加成，其他装备没有属性加成
        """
        features = {}

        # 检查是否为武器或防具
        kindid = equip_data.get('kindid', 0)
        if not self._is_weapon_or_armor_or_shoes(kindid):
            # 非武器防具，设置所有附加属性为0
            features['addon_tizhi'] = 0
            features['addon_liliang'] = 0
            features['addon_naili'] = 0
            features['addon_minjie'] = 0
            features['addon_lingli'] = 0
            features['addon_moli'] = 0
            features['addon_total'] = 0
            return features

        # 武器防具才提取附加属性
        features['addon_tizhi'] = equip_data.get('addon_tizhi', 0)
        features['addon_liliang'] = equip_data.get('addon_liliang', 0)
        features['addon_naili'] = equip_data.get('addon_naili', 0)
        features['addon_minjie'] = equip_data.get('addon_minjie', 0)
        features['addon_lingli'] = equip_data.get('addon_lingli', 0)
        features['addon_moli'] = equip_data.get('addon_moli', 0)
        # 正常模式，从agg_added_attrs解析魔力
        if features['addon_moli'] == 0:
            features['addon_moli'] = self._extract_moli_from_agg_added_attrs(equip_data.get('agg_added_attrs', '[]'))
        # addon_total将在熔炼效果合并后计算
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

        features['gem_level'] = gem_level
        
        # 确保gem_level是整数类型
        if gem_level is None:
            gem_level = 0
        else:
            try:
                gem_level = int(gem_level)
            except (ValueError, TypeError):
                gem_level = 0

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
                min_gem_score = min(
                    100.0, (raw_score / max_reference_score) * 100)
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

        return features

    def _extract_other_features(self, equip_data: Dict[str, Any]) -> Dict[str, int]:
        """从large_equip_desc提取其他特征"""
        features = {}

        # 默认值
        current_holes = 0
        features['hole_score'] = 0
        features['repair_fail_num'] = 0
        features['binding'] = 0

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
            hole_score = (hole_raw_value / max_hole_value) * \
                100 if max_hole_value > 0 else 0
            features['hole_score'] = round(hole_score, 2)

            # #r玩家68766666专用#r   
            binding_match = re.search(self.binding_pattern, large_desc)
            if binding_match:
                features['binding'] = 1
            else:
                features['binding'] = 0

        return features

    def _extract_ronglian_zhizaobang_features(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取熔炼效果/制造帮属性特征"""
        # 定义熔炼属性类型和默认值
        ronglian_attr_types = {
            'addon_tizhi_ronglian': '体质',
            'addon_liliang_ronglian': '力量', 
            'addon_naili_ronglian': '耐力',
            'addon_minjie_ronglian': '敏捷',
            'addon_moli_ronglian': '魔力',
            'addon_lingli_ronglian': '灵力',
            'init_defense_ronglian': '防御',
            'init_hp_ronglian': '气血'
        }
        
        # 初始化特征字典
        features = {attr: 0 for attr in ronglian_attr_types.keys()}

        # 从large_equip_desc或cDesc中提取熔炼效果
        desc = equip_data.get('large_equip_desc', '') or equip_data.get('cDesc', '')
        if not desc:
            return features

        # 提取熔炼和制造帮文本
        ronglian_text = self._extract_ronglian_and_zhizao_text(desc)
        if not ronglian_text:
            return features

        # 解析熔炼属性
        self._parse_ronglian_attributes(ronglian_text, features, ronglian_attr_types)
        
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

    def _extract_moli_from_agg_added_attrs(self, agg_added_attrs) -> int:
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
                return 0

            # 遍历所有属性字符串，查找魔力属性
            for attr in attrs_list:
                if isinstance(attr, str) and "魔力" in attr:
                    # 使用正则表达式提取魔力数值，支持正负值
                    import re
                    moli_match = re.search(r'魔力\s*([+-]?)\s*(\d+(?:\.\d+)?)', attr)
                    if moli_match:
                        value = int(moli_match.group(2))
                        # 如果是负值，取负
                        if moli_match.group(1) == '-':
                            value = -value
                        return value

            return 0

        except Exception as e:
            self.logger.warning(f"提取魔力属性时出错: {e}")
            return 0

    def _parse_equip_data_from_desc(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """从large_equip_desc解析出完整的装备数据"""
        desc = equip_data.get('cDesc', '')

        if not desc:
            return equip_data
        # kindid需要根据iType在KINDID_ITYPE_RANGE中找到对应的kindid
        i_type = equip_data.get('iType', 0)
        # 创建新的装备数据字典
        
        kindid = self._get_kindid_from_itype(equip_data.get('kindid', 0), i_type)
        if kindid == 0:
            return equip_data
        
        # 如果kindid还是为0，则判断是物品
        parsed_data = equip_data.copy()
        parsed_data['large_equip_desc'] = desc
        # 设置默认值
        parsed_data['kindid'] = kindid
        parsed_data['equip_level'] = 0

        # 初始化所有字段为0
        parsed_data['init_damage'] = 0
        parsed_data['init_damage_raw'] = 0
        parsed_data['all_damage'] = 0
        parsed_data['init_wakan'] = 0
        parsed_data['init_defense'] = 0
        parsed_data['init_hp'] = 0
        parsed_data['init_dex'] = 0
        parsed_data['mingzhong'] = 0
        parsed_data['shanghai'] = 0

        # 附加属性
        parsed_data['addon_tizhi'] = 0
        parsed_data['addon_liliang'] = 0
        parsed_data['addon_naili'] = 0
        parsed_data['addon_minjie'] = 0
        parsed_data['addon_lingli'] = 0
        parsed_data['addon_moli'] = 0
        parsed_data['addon_total'] = 0

        # 宝石相关
        parsed_data['gem_level'] = 0
        parsed_data['gem_value'] = []

        # 特技特效
        parsed_data['special_skill'] = 0
        parsed_data['special_effect'] = []
        parsed_data['suit_effect'] = 0
   

        # 解析宝石信息
        self._parse_gem_info_from_desc(desc, parsed_data)

        # 解析基础属性
        self._parse_basic_attrs_from_desc(desc, parsed_data)

        # 解析附加属性
        self._parse_added_attrs_from_desc(desc, parsed_data)

        # 解析特技特效
        self._parse_special_skills_from_desc(desc, parsed_data)

        # 解析套装信息
        self._parse_suit_info_from_desc(desc, parsed_data)

        return parsed_data

    def _parse_basic_attrs_from_desc(self, desc: str, parsed_data: Dict[str, Any]):
        """从描述中解析基础属性
           要先去除开运孔数后的描述再解析
           以下也需要排除，不然会匹配成伤害值
           #c4DBAFF法术暴击伤害 +3.42%
           #c4DBAFF物理暴击伤害 +3.42%
           #c4DBAFF格挡物理伤害 +3
        """

        # 先去除开运孔数后的描述
        # 找到开运孔数的位置，只保留前面的部分
        hole_match = re.search(r'开运孔数：', desc)
        if hole_match:
            desc = desc[:hole_match.start()]

        # 解析装备等级
        level_patterns = [
            r'#r等级\s*(\d+)',          # #r等级 125
        ]
        for pattern in level_patterns:
            level_match = re.search(pattern, desc)
            if level_match:
                parsed_data['equip_level'] = int(level_match.group(1))
                break

        # 解析速度（用于计算黑宝石等级）- 必须在气血解析之前
        speed_patterns = [
            r'#G#G速度\s*\+(\d+)',     # #G#G速度 +104
            r'速度\s*\+(\d+)',         # 速度 +32
        ]
        for pattern in speed_patterns:
            speed_match = re.search(pattern, desc)
            if speed_match:
                speed_value = int(speed_match.group(1))
                # 黑宝石每级提供8点速度，所以等级 = 速度值 / 8
                black_gem_level = speed_value // 8
                parsed_data['black_gem_level'] = black_gem_level
                break
        
        # 只有武器
        kindid = parsed_data.get('kindid', 0)
        if is_weapon(kindid) or is_helm(kindid):
            # 解析命中
            mingzhong_patterns = [
                r'命中\s*\+(\d+)#r',      #r伤害 +596 命中 +561#r => 561
                r'命中\s*\+(\d+)',        # 命中 +561
            ]
            for pattern in mingzhong_patterns:
                mingzhong_match = re.search(pattern, desc)
                if mingzhong_match:
                    # 是头盔
                    if is_helm(kindid):
                        parsed_data['mingzhong_gem_level'] = int(mingzhong_match.group(1))//25
                    else:
                        parsed_data['mingzhong'] = int(mingzhong_match.group(1))
                    break
                    
            # 解析伤害 - 支持多种格式
            # 先排除特定的伤害相关文本，避免误匹配
            desc_for_damage = desc
            exclude_patterns = [
                r'#c4DBAFF法术暴击伤害\s*\+[^#]*',
                r'#c4DBAFF物理暴击伤害\s*\+[^#]*',
                r'#c4DBAFF格挡物理伤害\s*\+[^#]*',
            ]
            for pattern in exclude_patterns:
                desc_for_damage = re.sub(pattern, '', desc_for_damage)
        
            damage_patterns = [
                r'伤害\s*\+(\d+)#r',      #r伤害 +596 命中 +561#r => 561
                r'伤害\s*\+(\d+)',        # 命中 +561
            ]
            
            for pattern in damage_patterns:
                damage_match = re.search(pattern, desc_for_damage)
                if damage_match:
                    gem_level = parsed_data.get('gem_level',0)
                    gem_value = parsed_data['gem_value']
                    extract_init_damage_raw  = int(damage_match.group(1))
                    init_damage_raw = extract_init_damage_raw
                    mingzhong2shanghai = parsed_data['mingzhong'] // 3
                    gem_mingzhong = 0
                    gem_shanghai = 0  # 初始化默认值
                    if is_weapon(kindid):
                        parsed_data['all_damage'] = extract_init_damage_raw + mingzhong2shanghai
                    # 太阳石 玛瑙石计算
                    if gem_level > 0 and (1 in gem_value or 2 in gem_value):
                        # 玛瑙石
                        if gem_value == [1]:
                            gem_mingzhong = 25*gem_level
                        # 太阳石    
                        elif gem_value == [2]:  
                            gem_shanghai = 8 * gem_level
                            init_damage_raw -= gem_shanghai
                        #混打 无解
                        else:
                            gass_shanghai_gem_level = 1
                            gem_shanghai = (8 * gass_shanghai_gem_level) + (gem_level-gass_shanghai_gem_level)*25//3
                            init_damage_raw = init_damage_raw - (8 * gass_shanghai_gem_level)
                    # 是武器
                    if is_weapon(kindid):
                        parsed_data['init_damage_raw'] = init_damage_raw 
                        parsed_data['init_damage'] = (parsed_data['mingzhong'] - gem_mingzhong)//3 + extract_init_damage_raw - gem_shanghai
                    # 是头盔
                    if is_helm(kindid):
                        parsed_data['shanghai_gem_level'] = int(damage_match.group(1)) //8
                    else:
                        parsed_data['shanghai'] = int(damage_match.group(1))

                    break

     
        # 解析气血
        hp_patterns = [
            r'气血\s*\+(\d+)',          # 气血 +639
            r'\+(\d+)\s*气血',          # +639 气血
        ]
        for pattern in hp_patterns:
            hp_match = re.search(pattern, desc)
            if hp_match:
                init_hp = int(hp_match.group(1))
                # 计算非黑宝石的等级（总等级减去黑宝石等级）
                black_gem_level = parsed_data.get('black_gem_level', 0)
                total_gem_level = parsed_data.get('gem_level', 0)
                hp_gem_level = total_gem_level - black_gem_level
                # 是腰带
                if kindid == BELT_KINDID:
                    # 且有光芒石
                    if 4 in parsed_data['gem_value']:
                        # 混搭神秘石
                        if 7 in parsed_data['gem_value']:
                            duobi_gem_level = parsed_data.get('duobi_gem_level',0)
                            hp_gem_level = hp_gem_level - duobi_gem_level
                        parsed_data['init_hp'] = init_hp - 40 * hp_gem_level
                    else:
                        parsed_data['init_hp'] = init_hp
                else:
                    parsed_data['hp_gem_level']  =  init_hp//40
                break

        if kindid == NECKLACE_KINDID or is_armor(kindid):
            # 解析灵力
            magic_patterns = [
                r'灵力\s*\+(\d+)',          # 灵力 +113
            ]
            for pattern in magic_patterns:
                magic_match = re.search(pattern, desc)
                if magic_match:
                    if kindid == NECKLACE_KINDID:
                        parsed_data['init_wakan'] = int(magic_match.group(1))
                        # 舍利子计算
                        if parsed_data['gem_level'] > 0 and 3 in parsed_data['gem_value']:
                            if parsed_data['gem_value'] == [3]:
                                gem_wakan = 6*parsed_data['gem_level']
                                parsed_data['init_wakan'] -= gem_wakan
                            else:
                                # 解析法术吸收率
                                other_gem_level = self._parse_magic_absorption_from_desc(desc)//4
                                gem_wakan = 6*(parsed_data['gem_level']-other_gem_level)
                                parsed_data['init_wakan'] -= gem_wakan
                        break
                    else:
                        parsed_data['wakan_gem_level'] = int(magic_match.group(1))//6
               
        # 解析防御
        defense_patterns = [
            r'防御\s*\+(\d+)',          # 防御 +95
        ]
        # TODO:参考腰带黑宝石，先计算气血，得出光芒石等级，再计算防御
        for pattern in defense_patterns:
            defense_match = re.search(pattern, desc)
            if defense_match:
                parsed_data['init_defense'] = int(defense_match.group(1))
                # 月亮石计算
                gem_level = parsed_data.get('gem_level', 0)
                hp_gem_level = parsed_data.get('hp_gem_level',0)
                black_gem_level = parsed_data.get('black_gem_level', 0)
                shanghai_gem_level = parsed_data.get('shanghai_gem_level',0)
                mingzhong_gem_level = parsed_data.get('mingzhong_gem_level',0)
                wakan_gem_level = parsed_data.get('wakan_gem_level',0)
                
                if gem_level > 0 and 5 in parsed_data['gem_value']:
                    defense_gem_level = gem_level
                    if hp_gem_level > 0:
                        defense_gem_level = defense_gem_level - hp_gem_level
                    if black_gem_level  > 0:
                       defense_gem_level = defense_gem_level - black_gem_level
                    if shanghai_gem_level > 0:
                        defense_gem_level = defense_gem_level - shanghai_gem_level
                    if mingzhong_gem_level > 0:
                        defense_gem_level = defense_gem_level - mingzhong_gem_level
                    if wakan_gem_level > 0:
                        defense_gem_level = defense_gem_level - wakan_gem_level
                    if 12 in parsed_data['gem_value']:
                        # 翡翠石计算法防
                        # 先解析法防值
                        magic_defense_match = re.search(r'#G法防\s*\+(\d+)', desc)
                        if magic_defense_match:
                            magic_defense_value = int(magic_defense_match.group(1))
                            # 翡翠石每级提供12点法防
                            magic_defense_gem_level = magic_defense_value // 12
                            parsed_data['magic_defense_gem_level'] = magic_defense_gem_level
                            # 从防御宝石等级中减去法防宝石等级
                            defense_gem_level = defense_gem_level - magic_defense_gem_level

                    # 月亮石计算
                    gem_defense = 12*defense_gem_level
                    parsed_data['init_defense'] -= gem_defense
                break
        
        # 解析鞋子敏捷
        if kindid == SHOES_KINDID:
            dex_patterns = [
                r'敏捷\s*\+(\d+)',          # 敏捷 +23
            ]
            for pattern in dex_patterns:
                dex_match = re.search(pattern, desc)
                if dex_match:
                    parsed_data['init_dex'] = int(dex_match.group(1))
                    break
        

    def _parse_magic_absorption_from_desc(self, desc: str):
        """从描述中解析法术吸收率
        格式：#G法术吸收率 火+12% => 提取12
        """
        
        # 法术吸收率正则表达式模式 - 匹配任意元素类型
        absorption_pattern = r'#G法术吸收率\s*[^+]*\+(\d+)%'
        
        # 查找匹配
        match = re.search(absorption_pattern, desc)
        if match:
            value = int(match.group(1))
            return value

        return 0    

    def _parse_added_attrs_from_desc(self, desc: str, parsed_data: Dict[str, Any]):
        """从描述中解析附加属性
        需要去除开运孔数后的描述再解析
        """
        # 先去除开运孔数后的描述
        # 找到开运孔数的位置，只保留前面的部分
        hole_match = re.search(r'开运孔数：', desc)
        if hole_match:
            desc = desc[:hole_match.start()]
        # 先去除熔炼效果后的描述
        # 找到熔炼效果的位置，只保留前面的部分
        ronglian_match = re.search(r'熔炼效果：', desc)
        if ronglian_match:
            desc = desc[:ronglian_match.start()]

        # 只有武器和防具才需要提取附加属性
        kindid = parsed_data.get('kindid', 0)
        if not self._is_weapon_or_armor_or_shoes(kindid):
            return

        # 解析敏捷 - 支持多种格式，包括负值
        minjie_patterns = [
            r'#G#G敏捷\s*\+(\d+)',     # #G#G敏捷 +17
            r'#G#G敏捷\s*-(\d+)',      # #G#G敏捷 -13
            r'敏捷\s*\+(\d+)',         # 敏捷 +17
            r'敏捷\s*-(\d+)',          # 敏捷 -13
        ]
        for pattern in minjie_patterns:
            minjie_match = re.search(pattern, desc)
            if minjie_match:
                value = int(minjie_match.group(1))
                if '-(\\d+)' in pattern or '敏捷\\s*-(\\d+)' in pattern or '#G#G敏捷\\s*-(\\d+)' in pattern:
                    value = -value

                # 如果是鞋子，提取为init_dex；否则提取为addon_minjie
                if kindid == SHOES_KINDID:
                    parsed_data['init_dex'] = value
                else:
                    parsed_data['addon_minjie'] = value
                break

        # 如果是鞋子，不需要继续解析其他附加属性
        if kindid == SHOES_KINDID:
            return

        # 解析体质 - 支持多种格式，包括负值
        tizhi_patterns = [
            r'#G#G体质\s*\+(\d+)',     # #G#G体质 +5
            r'#G#G体质\s*-(\d+)',      # #G#G体质 -3
            r'#G体质\s*\+(\d+)',     # #G体质 +5
            r'#G体质\s*-(\d+)',      # #G体质 -3
            r'体质\s*\+(\d+)',         # 体质 +5
            r'体质\s*-(\d+)',          # 体质 -3
        ]
        for pattern in tizhi_patterns:
            tizhi_match = re.search(pattern, desc)
            if tizhi_match:
                value = int(tizhi_match.group(1))
                if '-(\\d+)' in pattern or '体质\\s*-(\\d+)' in pattern or '#G#G体质\\s*-(\\d+)' in pattern:
                    value = -value
                parsed_data['addon_tizhi'] = value
                break

        # 解析力量 - 支持多种格式，包括负值
        liliang_patterns = [
            r'#G#G力量\s*\+(\d+)',     # #G#G力量 +12
            r'#G#G力量\s*-(\d+)',      # #G#G力量 -6
            r'力量\s*\+(\d+)',         # 力量 +12
            r'力量\s*-(\d+)',          # 力量 -6
        ]
        for pattern in liliang_patterns:
            liliang_match = re.search(pattern, desc)
            if liliang_match:
                value = int(liliang_match.group(1))
                if '-(\\d+)' in pattern or '力量\\s*-(\\d+)' in pattern or '#G#G力量\\s*-(\\d+)' in pattern:
                    value = -value
                parsed_data['addon_liliang'] = value
                break

        # 解析耐力 - 支持多种格式，包括负值
        naili_patterns = [
            r'#G#G耐力\s*\+(\d+)',     # #G#G耐力 +10
            r'#G#G耐力\s*-(\d+)',      # #G#G耐力 -8
            r'耐力\s*\+(\d+)',         # 耐力 +10
            r'耐力\s*-(\d+)',          # 耐力 -8
        ]
        for pattern in naili_patterns:
            naili_match = re.search(pattern, desc)
            if naili_match:
                value = int(naili_match.group(1))
                if '-(\\d+)' in pattern or '耐力\\s*-(\\d+)' in pattern or '#G#G耐力\\s*-(\\d+)' in pattern:
                    value = -value
                parsed_data['addon_naili'] = value
                break

        # 解析灵力 - 支持多种格式，包括负值
        lingli_patterns = [
            r'#G#G灵力\s*\+(\d+)',     # #G#G灵力 +10
            r'#G#G灵力\s*-(\d+)',      # #G#G灵力 -8
            r'灵力\s*\+(\d+)',         # 灵力 +10
            r'灵力\s*-(\d+)',          # 灵力 -8
        ]
        for pattern in lingli_patterns:
            lingli_match = re.search(pattern, desc)
            if lingli_match:
                value = int(lingli_match.group(1))
                if '-(\\d+)' in pattern or '灵力\\s*-(\\d+)' in pattern or '#G#G灵力\\s*-(\\d+)' in pattern:
                    value = -value
                parsed_data['addon_lingli'] = value
                break

        # 解析魔力 - 支持多种格式，包括负值
        moli_patterns = [
            r'#G#G魔力\s*\+(\d+)',     # #G#G魔力 +8
            r'#G#G魔力\s*-(\d+)',      # #G#G魔力 -16
            r'#G魔力\s*\+(\d+)',       # #G魔力 +30
            r'#G魔力\s*-(\d+)',        # #G魔力 -16
            r'魔力\s*\+(\d+)',         # 魔力 +8
            r'魔力\s*-(\d+)',          # 魔力 -16
        ]
        for pattern in moli_patterns:
            moli_match = re.search(pattern, desc)
            if moli_match:
                value = int(moli_match.group(1))
                # 检查是否是负值模式
                if pattern.endswith('-(\\d+)') or '魔力\\s*-(\\d+)' in pattern or '#G#G魔力\\s*-(\\d+)' in pattern:
                    value = -value
                parsed_data['addon_moli'] = value
                break

        # 计算附加属性总和
        total = (parsed_data['addon_tizhi'] + parsed_data['addon_liliang'] +
                 parsed_data['addon_naili'] + parsed_data['addon_minjie'] +
                 parsed_data['addon_lingli'] + parsed_data['addon_moli'])
        # 官方数据就是0 这个字段没用
        parsed_data['addon_total'] = 0

    def _parse_gem_info_from_desc(self, desc: str, parsed_data: Dict[str, Any]):
        """从描述中解析宝石信息"""
        # 解析宝石等级
        gem_level_patterns = [
            r'锻炼等级\s*(\d+)',       # 锻炼等级 10
        ]
        for pattern in gem_level_patterns:
            gem_level_match = re.search(pattern, desc)
            if gem_level_match:
                parsed_data['gem_level'] = int(gem_level_match.group(1))
                break

        # 解析宝石类型 #r锻炼等级 13  镶嵌宝石 光芒石、 黑宝石#r
        gem_types = []
        gem_type_patterns = [
            r'镶嵌宝石\s*([^#\r]+)',   # 镶嵌宝石 光芒石、 黑宝石
            r'\+(\d+)([^#\s]+)\s*镶嵌等级',  # +80伤害 镶嵌等级：8
        ]
        for pattern in gem_type_patterns:
            gem_type_match = re.search(pattern, desc)
            if gem_type_match:
                if '镶嵌宝石' in pattern:
                    # 提取完整的宝石字符串，然后分割
                    gem_text = gem_type_match.group(1).strip()
                    # 分割宝石名称，处理"光芒石、 黑宝石"这种情况
                    # 先按"、"分割，再按空格分割，然后清理
                    gem_parts = []
                    for part in gem_text.split('、'):
                        for sub_part in part.split():
                            sub_part = sub_part.strip()
                            if sub_part and sub_part not in ['、', '']:
                                gem_parts.append(sub_part)
                    gem_types.extend(gem_parts)
                else:
                    gem_type = gem_type_match.group(2)
                    gem_types.append(gem_type)
                break

        # 如果没有找到宝石类型，尝试从其他信息推断
        if not gem_types:
            # 检查是否有宝石相关信息
            if '镶嵌宝石' in desc or '锻炼等级' in desc:
                # 根据装备类型或其他信息推断宝石类型
                # 暂时设置为默认值
                gem_types = ['未知宝石']

       
        parsed_data['gem_value'] = gem_types


        # 计算宝石得分
        if parsed_data['gem_level'] > 0 and gem_types:
            # 宝石价值映射（根据宝石名称）
            gem_value_score = {
                '黑宝石': 160,   # 最高价值
                '舍利子': 100,
                '红玛瑙': 75,
                '月亮石': 69,
                '太阳石': 65,
                '光芒石': 32,
                '翡翠石': 20,    # 最低价值
            }

            # 找到价值最小的宝石
            min_gem_value = float('inf')
            for gem_name in gem_types:
                gem_score = gem_value_score.get(gem_name, 0)
                min_gem_value = min(min_gem_value, gem_score)

            # 如果找到了有效宝石，计算得分
            if min_gem_value != float('inf'):
                base_multiplier = (2 ** parsed_data['gem_level']) - 1
                raw_score = base_multiplier * min_gem_value

                # 标准化到0-100分
                max_reference_score = ((2 ** 10) - 1) * 160  # 10级黑宝石作为满分参考
                gem_score = min(100.0, (raw_score / max_reference_score) * 100)
                parsed_data['gem_score'] = round(gem_score, 2)
            else:
                parsed_data['gem_score'] = 0.0
        else:
            parsed_data['gem_score'] = 0.0

        # 将宝石名称映射为ID
        gem_name_to_id = {
            '黑宝石': 6,
            '舍利子': 3,
            '红玛瑙': 1,
            '月亮石': 5,
            '太阳石': 2,
            '光芒石': 4,
            '神秘石': 7,
            '黄宝石':8,
            '红宝石':9,
            '绿宝石':10,
            '蓝宝石': 11,
            '翡翠石': 12,
        }

        gem_ids = []
        for gem_name in gem_types:
            gem_id = gem_name_to_id.get(gem_name, 0)
            if gem_id > 0:
                gem_ids.append(gem_id)

        if gem_ids:
            parsed_data['gem_value'] = gem_ids

        # 混搭宝石预处理
        if 7 in gem_ids:
            duobi_match = re.search(r'#G躲避\s*\+(\d+)', desc)
            if duobi_match:
                duobi_value = int(duobi_match.group(1))
                # 神秘石每级提供20点躲避
                duobi_gem_level = duobi_value // 20
                parsed_data['duobi_gem_level'] = duobi_gem_level
             

    def _parse_special_skills_from_desc(self, desc: str, parsed_data: Dict[str, Any]):
        """从描述中解析特技特效"""
        parsed_data['special_skill'] = 0
        parsed_data['special_effect'] = []
        special_skill_pattern = r'#r#c4DBAF4特技：#c4DBAF4\s*([^#\n]+)#Y#Y'
        if not desc:
            return
        # 解析特技
        special_skill_match = re.search(special_skill_pattern, desc)
        if special_skill_match:
            #'决', '诀' 特技名称
            special_skill_name = special_skill_match.group(1).strip().replace('决', '诀')
            # print(f"special_skill_name------------------------: {special_skill_name}")
            special_skill = self.special_skills.get(special_skill_name, 0)
            # 如果special_skill是字符串，并且包含逗号，则取逗号后面的值
            if isinstance(special_skill, str) and ',' in special_skill:
                special_skill = int(special_skill.split(',')[1])
                
            parsed_data['special_skill'] = special_skill

        # 解析特效 以下是示例数据
        # #r#c4DBAF4特效：#c4DBAF4永不磨损#Y#r => 永不磨损
        # #r#c4DBAF4特效：#c4DBAF4无级别限制#Y #c4DBAF4愤怒#Y#r => 无级别限制 愤怒
        
        # 直接在整个描述中搜索特效
        effects = []
        for effect_id, effect_name in self.special_effects.items():
            # 处理特殊情况：无级别 -> 无级别限制
            search_name = effect_name
            if effect_name == '无级别':
                search_name = '无级别限制'

            # 直接搜索特效名称
            search_pattern = f"#c4DBAF4{search_name}#Y"
            if search_pattern in desc:
                effects.append(int(effect_id))
        
        parsed_data['special_effect'] = effects

    def _parse_suit_info_from_desc(self, desc: str, parsed_data: Dict[str, Any]):
        """从描述中解析套装信息"""
        if not desc:
            parsed_data['suit_effect'] = 0
            return

        # 移除颜色代码
        desc_clean = re.sub(r'#c4DBAF4', '', desc)
        desc_clean = re.sub(r'#[A-Z]', '', desc_clean)

        # 查找套装效果相关信息
        # 第三和第四的套装效果需要特殊处理 提取的名字会一样，需要记录在哪提取的
        # 比如加上index，变身术之 只能在suit_transform_skills查找，变化咒之 只能在suit_transform_charms查找，
        suit_patterns = [
            (r'套装效果：附加状态\s*([^#\n]+)', 'added_status'),  # 套装效果：附加状态 xxx
            (r'套装效果：追加法术\s*([^#\n]+)', 'append_skills'),  # 套装效果：追加法术 xxx
            (r'套装效果：变身术之\s*([^#\n]+)', 'transform_skills'),  # 套装效果：变身术之 xxx
            (r'套装效果：变化咒之\s*([^#\n]+)', 'transform_charms')  # 套装效果：变化咒之 xxx
        ]

        for pattern, suit_type in suit_patterns:
            match = re.search(pattern, desc_clean)
            if match:
                suit_info = match.group(1).strip()
                # 清理多余的空格和特殊字符
                suit_info = re.sub(r'\s+', ' ', suit_info)
                
                # 根据套装类型选择对应的配置
                if suit_type == 'added_status':
                    suit_config = self.auto_config.get('suit_added_status', {})
                elif suit_type == 'append_skills':
                    suit_config = self.auto_config.get('suit_append_skills', {})
                elif suit_type == 'transform_skills':
                    suit_config = self.auto_config.get('suit_transform_skills', {})
                elif suit_type == 'transform_charms':
                    suit_config = self.auto_config.get('suit_transform_charms', {})
                else:
                    continue

                # 在对应的配置中查找匹配的套装
                for suit_id, suit_name in suit_config.items():
                    if suit_name == suit_info:
                        parsed_data['suit_effect'] = int(suit_id)
                        return

                # 如果没有找到匹配的套装，设置为1表示有套装
                parsed_data['suit_effect'] = 1
                return

        parsed_data['suit_effect'] = 0

    def _get_kindid_from_itype(self, kindid: int, i_type: int) -> int:
        """
        根据kindid和iType获取对应的kindid
        如果kindid已存在且有效，直接返回；否则根据iType转换
        
        Args:
            kindid: 现有的kindid值
            i_type: iType值
            
        Returns:
            int: 有效的kindid值
        """
        # 如果kindid已存在且有效，直接返回
        if kindid > 0:
            return kindid
            
        # 如果iType无效，返回0
        if not i_type or i_type <= 0:
            return 0
            
        # 根据iType转换kindid
        from ..constants.i_type_kindid_map import KINDID_ITYPE_RANGE
        
        try:
            i_type = int(i_type)
        except (ValueError, TypeError):
            return 0

        for kindid, ranges in KINDID_ITYPE_RANGE.items():
            for range_tuple in ranges:
                if len(range_tuple) == 2:
                    start, end = range_tuple
                    if int(start) <= i_type <= int(end):
                        return kindid

        return 0

    def _is_weapon_or_armor_or_shoes(self, kindid: int) -> bool:
        """判断是否为武器或防具"""

        return is_weapon(kindid) or is_armor(kindid) or kindid == SHOES_KINDID

    def _apply_ronglian_features(self, features: Dict[str, Any], ronglian_features: Dict[str, Any], equip_data: Dict[str, Any],is_desc_only_data:bool) -> None:
        """
        应用熔炼特征到装备特征中
        
        Args:
            features: 装备特征字典
            ronglian_features: 熔炼特征字典
            equip_data: 原始装备数据
        """
        # 定义熔炼属性映射规则
        ronglian_mappings = {
            # 附加属性映射
            'addon_tizhi_ronglian': 'addon_tizhi',
            'addon_liliang_ronglian': 'addon_liliang', 
            'addon_naili_ronglian': 'addon_naili',
            'addon_moli_ronglian': 'addon_moli',
            'addon_lingli_ronglian': 'addon_lingli',
            
            # 基础属性映射
            'init_defense_ronglian': 'init_defense',
            'init_hp_ronglian': 'init_hp',
            'init_wakan_ronglian': 'init_wakan'
        }
        
        # 特殊映射规则（装备类型相关的特殊处理）
        special_mappings = {
            SHOES_KINDID: {
                'addon_minjie_ronglian': 'init_dex'  # 鞋子熔炼敏捷加到初始敏捷（单参数版本）
            }
        }
        
        # 通用特殊映射（所有装备类型）
        general_special_mappings = {
            'addon_minjie_ronglian': 'addon_minjie'  # 其他装备熔炼敏捷加到附加敏捷
        }
        
        # 获取装备类型
        kindid = features.get('kindid', 0)
             
        # 判断是否为单参数版本（通过检查是否有agg_added_attrs字段）
        is_single_param_version = 'agg_added_attrs' not in equip_data
        # 应用标准熔炼属性映射
        # - 多参数版本：从agg_added_attrs解析，已经包含熔炼效果，不需要再加
        # - 单参数版本：从large_equip_desc解析，不包含熔炼效果，需要加上熔炼效果
        for ronglian_key, target_key in ronglian_mappings.items():
            if ronglian_key in ronglian_features and target_key in features:
                # 特殊处理：魔力属性
                if ronglian_key == 'addon_moli_ronglian':
                    # 魔力属性处理逻辑：
                    if is_single_param_version:
                        features[target_key] += ronglian_features[ronglian_key]
                elif ronglian_key == 'addon_lingli_ronglian':
                    features['addon_lingli'] = 0
                else:
                    # 其他属性正常合并熔炼效果
                    if is_single_param_version:
                        features[target_key] += ronglian_features[ronglian_key]
                    elif 'addon_' in target_key:
                        features[target_key] += ronglian_features[ronglian_key]
        
        # 应用特殊映射规则（装备类型相关）
        if kindid in special_mappings and is_single_param_version:
            for ronglian_key, target_key in special_mappings[kindid].items():
                if ronglian_key in ronglian_features and target_key in features:
                    # 鞋子类型的熔炼敏捷只操作init_dex
                    if kindid == SHOES_KINDID:
                        features[target_key] += ronglian_features[ronglian_key]
        
        # 应用通用特殊映射规则
        for ronglian_key, target_key in general_special_mappings.items():
            if ronglian_key in ronglian_features and target_key in features:
                # 检查是否在装备类型特殊映射中，如果是则跳过
                skip_general_mapping = False
                if kindid in special_mappings:
                    for special_ronglian_key, special_target_key in special_mappings[kindid].items():
                        if ronglian_key == special_ronglian_key:
                            skip_general_mapping = True
                            break
                
                if not skip_general_mapping:
                    features[target_key] += ronglian_features[ronglian_key]
        
        # # 处理只有描述数据的特殊情况
        if is_desc_only_data:
            # 基础属性（防御、气血）
            # if 'init_defense' in features and 'init_defense_ronglian' in ronglian_features:
            #     features['init_defense'] += ronglian_features['init_defense_ronglian']
            # if 'init_hp' in features and 'init_hp_ronglian' in ronglian_features:
            #     features['init_hp'] += ronglian_features['init_hp_ronglian']
            if 'init_wakan' in features and 'addon_lingli_ronglian' in ronglian_features:
                features['init_wakan'] += ronglian_features['addon_lingli_ronglian']
        
        # 计算附加属性总和（在熔炼效果合并后）
        if all(key in features for key in ['addon_tizhi', 'addon_liliang', 'addon_naili', 'addon_minjie', 'addon_moli']):
            features['addon_total'] = (features['addon_tizhi'] + features['addon_liliang'] + 
                                     features['addon_naili'] + features['addon_minjie'] + features['addon_moli'])
      

    def _extract_ronglian_and_zhizao_text(self, desc: str) -> str:
        """
        从装备描述中提取熔炼和制造帮文本
        
        Args:
            desc: 装备描述文本
            
        Returns:
            str: 合并后的熔炼和制造帮文本
        """
        ronglian_text = ""
        
        # 查找熔炼效果部分
        ronglian_match = re.search(self.ronglian_pattern, desc)
        if ronglian_match:
            ronglian_text = ronglian_match.group(1).strip()

        # 查找"制造帮："后面的属性
        zhizao_pattern = r'#r#W制造帮：[^#]*?#r#Y(\+[^#]+)'
        zhizao_match = re.search(zhizao_pattern, desc)
        if zhizao_match:
            zhizao_text = zhizao_match.group(1).strip()
            # 将制造帮的属性也加入到熔炼文本中一起解析
            if ronglian_text:
                ronglian_text += ' ' + zhizao_text
            else:
                ronglian_text = zhizao_text
                
        return ronglian_text

    def _parse_ronglian_attributes(self, ronglian_text: str, features: Dict[str, Any], 
                                  ronglian_attr_types: Dict[str, str]) -> None:
        """
        解析熔炼属性文本并更新特征字典
        
        Args:
            ronglian_text: 熔炼属性文本
            features: 特征字典
            ronglian_attr_types: 熔炼属性类型映射
        """
        # 为每种属性类型生成正则表达式模式
        for feature_name, attr_name in ronglian_attr_types.items():
            # 生成正负值的正则表达式模式
            positive_pattern = rf'\+(\d+)\s*{attr_name}'
            negative_pattern = rf'-(\d+)\s*{attr_name}'
            
            # 查找所有匹配项
            positive_matches = re.findall(positive_pattern, ronglian_text)
            negative_matches = re.findall(negative_pattern, ronglian_text)
            
            # 累加所有匹配的值
            total_value = 0
            for match in positive_matches:
                total_value += int(match)
            for match in negative_matches:
                total_value -= int(match)
                
            # 更新特征值
            features[feature_name] = total_value

