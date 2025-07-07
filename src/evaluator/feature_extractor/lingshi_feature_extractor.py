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


class LingshiFeatureExtractor:
    """
    梦幻西游灵饰装备特征提取器
    
    该类用于从梦幻西游灵饰装备数据中提取结构化的特征信息，支持以下装备类型：
    - kindid=61: 戒指 (伤害/防御主属性)
    - kindid=62: 耳饰 (法术伤害/法术防御主属性)
    - kindid=63: 手镯 (封印命中等级/抵抗封印等级主属性)
    - kindid=64: 佩饰 (速度主属性)
    
    提取的特征包括：
    1. 基础属性特征 (8个字段): 装备等级、主属性值
    2. 附加属性特征 (1个字段): 附加属性对象列表
    3. 宝石特征 (2个字段): 精炼等级和标准化得分
    4. 套装效果特征 (2个字段): 套装类型和等级
    5. 特效特征 (1个字段): 超级简易特效标识
    6. 其他特征 (1个字段): 修理失败次数
    
    总计15个特征字段，用于装备估价和相似度计算。
    """

    def __init__(self):
        """初始化特征提取器"""
        print("初始化特征提取器...")
        self.logger = logging.getLogger(__name__)

        # 加载配置文件
        self._load_configs()

    def _load_configs(self):
        """加载配置文件"""
        try:
            self.auto_config = load_jsonc_relative_to_file(
                __file__, '../../constant/auto_search_config.json')

            # 特效配置
            self.suit_effects = self.auto_config.get(
                'lingshi_suit_effects', [])

        except Exception as e:
            self.logger.warning(f"加载配置文件失败: {e}")
            self.auto_config = {}
            self.suit_effects = []


    def extract_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float, str]]:
        """
        提取梦幻西游灵饰装备的所有特征
        
        Args:
            equip_data: 装备数据字典，包含装备的原始信息
            
        Returns:
            Dict[str, Union[int, float, str]]: 提取的特征字典，包含以下字段:
            
            # 一、基础属性特征 (8个字段)
            equip_level: int - 装备等级
            damage: int - 伤害值 (戒指主属性)
            defense: int - 防御值 (戒指主属性)
            magic_damage: int - 法术伤害值 (耳饰主属性)
            magic_defense: int - 法术防御值 (耳饰主属性)
            fengyin: int - 封印命中等级 (手镯主属性)
            anti_fengyin: int - 抵抗封印等级 (手镯主属性)
            speed: int - 速度值 (佩饰主属性)
            
            # 二、附加属性特征 (1个字段)
            attrs: List[Dict] - 附加属性对象列表，最多3个
                每个对象包含:
                - attr_type: str - 属性类型，如"伤害"、"法术伤害"
                - attr_value: int - 属性数值
            
            # 三、宝石特征 (2个字段)
            gem_level: int - 精炼等级 (1-10级)
            gem_score: float - 宝石标准化得分 (0-100分，基于精炼等级计算)
            
            # 四、套装效果特征 (2个字段)
            suit_effect_type: str - 套装效果类型，如"健步如飞"
            suit_effect_level: int - 套装效果等级 (1-10级)
            
            # 五、特效特征 (1个字段)
            is_super_simple: bool - 是否具有超级简易特效标识
            
            # 六、其他特征 (1个字段)
            repair_fail_num: int - 修理失败次数
        """
        try:
            features = {}

            # 一、主基础属性特征
            features.update(self._extract_basic_features(equip_data))

            # 二、附加属性
            features.update(self._extract_added_attrs_features(equip_data))

            # 三、星辉石
            features.update(self._extract_gem_features(equip_data))

            #  四、套装
            features.update(self._extract_suit_effect_features(equip_data))

            #  五、特效
            features.update(self._extract_special_effect_features(equip_data))

            # 六、其他特征（从large_equip_desc提取）
            features.update(self._extract_other_features(equip_data))

            return features

        except Exception as e:
            print(f"特征提取失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise

    def _extract_basic_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float]]:
        """
        提取灵饰装备的基础属性特征
        
        根据装备类型(kindid)从large_equip_desc中提取主基础属性：
        - kindid=61 (戒指): 伤害(damage) / 防御(defense)
        - kindid=62 (耳饰): 法术伤害(magic_damage) / 法术防御(magic_defense)  
        - kindid=63 (手镯): 封印命中等级(fengyin) / 抵抗封印等级(anti_fengyin)
        - kindid=64 (佩饰): 速度(speed)
        
        Args:
            equip_data: 装备数据字典
            
        Returns:
            Dict[str, Union[int, float]]: 基础属性特征字典
                equip_level: int - 装备等级
                damage: int - 伤害值 (戒指主属性)
                defense: int - 防御值 (戒指主属性)
                magic_damage: int - 法术伤害值 (耳饰主属性)
                magic_defense: int - 法术防御值 (耳饰主属性)
                fengyin: int - 封印命中等级 (手镯主属性)
                anti_fengyin: int - 抵抗封印等级 (手镯主属性)
                speed: int - 速度值 (佩饰主属性)
        """
        features = {
            "equip_level": 0,
            "kindid": 0,
            "damage": 0,
            "defense": 0,
            "magic_damage": 0,
            "magic_defense": 0,
            "fengyin": 0,
            "anti_fengyin": 0,
            "speed": 0,
        }

        # 获取装备类型和描述
        kindid = equip_data.get('kindid', 0)
        large_desc = equip_data.get('large_equip_desc', '')
        features['equip_level'] = equip_data.get('equip_level', 0)
        features['kindid'] = kindid
        
        if not large_desc:
            return features
            
        try:
            # 提取"耐久度"之前的部分，避免被附加属性干扰
            durability_index = large_desc.find('耐久度')
            if durability_index != -1:
                main_desc = large_desc[:durability_index]
            else:
                main_desc = large_desc
            
            # 根据kindid确定主属性类型并提取
            if kindid == 61:  # 戒指 - 伤害/防御
                # 提取伤害
                damage_match = re.search(r'伤害\s*\+?\s*(\d+)', main_desc)
                if damage_match:
                    features['damage'] = int(damage_match.group(1))
                
                # 提取防御
                defense_match = re.search(r'防御\s*\+?\s*(\d+)', main_desc)
                if defense_match:
                    features['defense'] = int(defense_match.group(1))
                    
            elif kindid == 62:  # 耳饰 - 法术伤害/法术防御
                # 提取法术伤害
                magic_damage_match = re.search(r'法术伤害\s*\+?\s*(\d+)', main_desc)
                if magic_damage_match:
                    features['magic_damage'] = int(magic_damage_match.group(1))
                
                # 提取法术防御
                magic_defense_match = re.search(r'法术防御\s*\+?\s*(\d+)', main_desc)
                if magic_defense_match:
                    features['magic_defense'] = int(magic_defense_match.group(1))
                    
            elif kindid == 63:  # 手镯 - 封印命中等级/抵抗封印等级
                # 提取封印命中等级
                seal_hit_match = re.search(r'封印命中等级\s*\+?\s*(\d+)', main_desc)
                if seal_hit_match:
                    features['fengyin'] = int(seal_hit_match.group(1))
                
                # 提取抵抗封印等级
                seal_resist_match = re.search(r'抵抗封印等级\s*\+?\s*(\d+)', main_desc)
                if seal_resist_match:
                    features['anti_fengyin'] = int(seal_resist_match.group(1))
                    
            elif kindid == 64:  # 佩饰 - 速度
                # 提取速度
                speed_match = re.search(r'速度\s*\+?\s*(\d+)', main_desc)
                if speed_match:
                    features['speed'] = int(speed_match.group(1))
            
            # 调试信息
            # if any(value > 0 for value in features.values()):
            #     print(f"[DEBUG] 成功提取基础属性 - kindid:{kindid}")
            #     print(f"[DEBUG] 主描述部分: {main_desc}")
            #     for key, value in features.items():
            #         if value > 0:
            #             print(f"  {key}: {value}")
                        
        except Exception as e:
            self.logger.warning(f"提取基础属性时出错: {e}")
            
        return features

    def _extract_added_attrs_features(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取灵饰装备的附加属性特征
        
        根据装备类型(kindid)从large_equip_desc中提取附加属性：
        
        攻击类附加属性 (kindid=61/62 戒指/耳饰):
        - 伤害、法术伤害、固定伤害、封印命中等级、法术暴击等级
        - 物理暴击等级、狂暴等级、穿刺等级、法术伤害结果、治疗能力、速度
        
        防御类附加属性 (kindid=63/64 手镯/佩饰):
        - 气血、防御、法术防御、格挡值、抗物理暴击等级
        - 抗法术暴击等级、抵抗封印等级、气血回复效果
        
        Args:
            equip_data: 装备数据字典
            
        Returns:
            Dict[str, Any]: 附加属性特征字典
                attrs: List[Dict] - 附加属性对象列表，最多3个
                    每个对象包含:
                    - attr_type: str - 属性类型，如"伤害"、"法术伤害"
                    - attr_value: int - 属性数值
        """
        features = {
            "attrs": []  # [{"attr_type": "伤害", "attr_value": 12}, {"attr_type": "治疗能力", "attr_value": 12}]
        }
        
        # 获取装备类型和描述
        kindid = equip_data.get('kindid', 0)
        large_desc = equip_data.get('large_equip_desc', '')
        
        if not large_desc:
            return features
            
        try:
            # 提取"耐久度"之后的部分，获取附加属性
            durability_index = large_desc.find('耐久度')
            if durability_index != -1:
                added_desc = large_desc[durability_index:]
                
                # 按#r分割成行，每行代表一个独立的属性或信息
                lines = added_desc.split('#r')
                
                # 查找#G或#W开头的行（附加属性行）
                attr_lines = []
                for line in lines:
                    if line.startswith('#G') or line.startswith('#W'):
                        # 移除颜色标记，保留属性内容
                        attr_content = re.sub(r'^#[GW]', '', line).strip()
                        if attr_content:
                            attr_lines.append(attr_content)
            else:
                # 如果没有耐久度，尝试直接按#r分割查找#G/#W行
                lines = large_desc.split('#r')
                attr_lines = []
                for line in lines:
                    if line.startswith('#G') or line.startswith('#W'):
                        attr_content = re.sub(r'^#[GW]', '', line).strip()
                        if attr_content:
                            attr_lines.append(attr_content)
            
            if not attr_lines:
                return features
                
            # 定义不同kindid的附加属性类型
            # 注意：更具体的属性名称要放在更通用的属性名称之前，避免误匹配
            if kindid in [61, 62]:  # 戒指/耳饰 - 攻击类附加属性
                attr_patterns = [
                    ("法术伤害结果", r'法术伤害结果\s*\+?\s*(\d+)'),
                    ("法术伤害", r'法术伤害\s*\+?\s*(\d+)'),
                    ("固定伤害", r'固定伤害\s*\+?\s*(\d+)'),
                    ("法术暴击等级", r'法术暴击等级\s*\+?\s*(\d+)'),
                    ("物理暴击等级", r'物理暴击等级\s*\+?\s*(\d+)'),
                    ("封印命中等级", r'封印命中等级\s*\+?\s*(\d+)'),
                    ("狂暴等级", r'狂暴等级\s*\+?\s*(\d+)'),
                    ("穿刺等级", r'穿刺等级\s*\+?\s*(\d+)'),
                    ("治疗能力", r'治疗能力\s*\+?\s*(\d+)'),
                    ("伤害", r'伤害\s*\+?\s*(\d+)'),  # 更通用的放后面
                    ("速度", r'速度\s*\+?\s*(\d+)')
                ]
            else:  # 手镯/佩饰 - 防御类附加属性
                attr_patterns = [
                    ("抗法术暴击等级", r'抗法术暴击等级\s*\+?\s*(\d+)'),
                    ("抗物理暴击等级", r'抗物理暴击等级\s*\+?\s*(\d+)'),
                    ("抵抗封印等级", r'抵抗封印等级\s*\+?\s*(\d+)'),
                    ("气血回复效果", r'气血回复效果\s*\+?\s*(\d+)'),
                    ("法术防御", r'法术防御\s*\+?\s*(\d+)'),  # 更具体的放前面
                    ("防御", r'防御\s*\+?\s*(\d+)'),  # 更通用的放后面
                    ("格挡值", r'格挡值\s*\+?\s*(\d+)'),
                    ("气血", r'气血\s*\+?\s*(\d+)')
                ]

            # 处理每个附加属性行，最多取3个
            for attr_line in attr_lines[:3]:
                # 为每行单独匹配属性
                attr_found = False
                for attr_name, pattern in attr_patterns:
                    match = re.search(pattern, attr_line)
                    if match:
                        features["attrs"].append({
                            "attr_type": attr_name,
                            "attr_value": int(match.group(1))
                        })
                        attr_found = True
                        break  # 找到匹配就跳出，每行只匹配一个属性
                
                # 如果没有匹配到已知属性，记录调试信息
                # if not attr_found:
                #     print(f"[DEBUG] 未识别的附加属性行: {repr(attr_line)}")
            
            # 调试信息
            # if features["attrs"]:
            #     print(f"[DEBUG] 成功提取附加属性 - kindid:{kindid}")
            #     print(f"[DEBUG] 附加属性行: {attr_lines}")
            #     for i, attr_obj in enumerate(features["attrs"]):
            #         print(f"  attr{i+1}: {attr_obj['attr_type']} +{attr_obj['attr_value']}")
                        
        except Exception as e:
            self.logger.warning(f"提取附加属性时出错: {e}")
            
        return features

    def _extract_gem_features(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取灵饰装备的宝石特征
        
        从large_equip_desc中提取精炼等级信息，并计算标准化得分：
        - 精炼等级范围：1-10级
        - 得分计算：每级精炼得分为3^(n-1)，如3级精炼 = 1+3+9=13分
        - 标准化：以10级精炼为满分(29524分)，转换为0-100分制
        
        Args:
            equip_data: 装备数据字典
            
        Returns:
            Dict[str, Any]: 宝石特征字典
                gem_level: int - 精炼等级 (1-10级)
                gem_score: float - 宝石标准化得分 (0-100分)
        """
        features = {
            "gem_score": 0,
            "gem_level": 0,
        }

        # 获取装备描述
        large_desc = equip_data.get('large_equip_desc', '')
        
        if not large_desc:
            return features
            
        try:
            # 提取精炼等级
            gem_level_match = re.search(r'精炼等级\s*(\d+)', large_desc)
            if gem_level_match:
                gem_level = int(gem_level_match.group(1))
                features['gem_level'] = gem_level
                
                # 计算宝石得分
                # 计算规则：如gem_level=3，则1+3+9=13, gem_level=8，则1+3+9+27+81+243+729+2187=3280
                gem_score = 0
                for i in range(1, gem_level + 1):
                    gem_score += (3 ** (i - 1))
                
                # 标准化到0-100分，以10级为满分参考
                # 10级得分：1+3+9+27+81+243+729+2187+6561+19683 = 29524
                max_reference_score = 29524  # 10级精炼的总得分
                normalized_score = (gem_score / max_reference_score) * 100
                features['gem_score'] = round(normalized_score, 2)
                
                # 调试信息
                # print(f"[DEBUG] 成功提取宝石特征 - 精炼等级:{gem_level}, 原始得分:{gem_score}, 标准化得分:{features['gem_score']}")
                
        except Exception as e:
            self.logger.warning(f"提取宝石特征时出错: {e}")
            
        return features

    def _extract_suit_effect_features(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取灵饰装备的套装效果特征
        
        从large_equip_desc中提取套装效果信息：
        - 匹配格式：特效：套装名称（等级）
        - 例如：特效：健步如飞（7级）
        
        Args:
            equip_data: 装备数据字典
            
        Returns:
            Dict[str, Any]: 套装效果特征字典
                suit_effect_type: str - 套装效果类型，如"健步如飞"
                suit_effect_level: int - 套装效果等级 (1-10级)
        """
        features = {
            "suit_effect_type": "",
            "suit_effect_level": 0,
        }

        # 获取装备描述
        large_desc = equip_data.get('large_equip_desc', '')
        
        if not large_desc:
            return features
            
        try:
            # 提取套装效果类型和等级
            # 匹配格式：特效：套装名称（等级）
            suit_effect_match = re.search(r'特效：([^（]+)（(\d+)级）', large_desc)
            if suit_effect_match:
                suit_effect_type = suit_effect_match.group(1).strip()
                suit_effect_level = int(suit_effect_match.group(2))
                
                features['suit_effect_type'] = suit_effect_type
                features['suit_effect_level'] = suit_effect_level
                
                # 调试信息
                # print(f"[DEBUG] 成功提取套装效果 - 类型:{suit_effect_type}, 等级:{suit_effect_level}")
                
        except Exception as e:
            self.logger.warning(f"提取套装效果特征时出错: {e}")
            
        return features


    def _extract_special_effect_features(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取灵饰装备的特效特征
        
        从large_equip_desc中提取特殊效果信息：
        - 超级简易特效：降低装备等级要求，提高价值
        - 匹配格式：特效：超级简易
        
        Args:
            equip_data: 装备数据字典
            
        Returns:
            Dict[str, Any]: 特效特征字典
                is_super_simple: bool - 是否具有超级简易特效
        """
        features = {
            "is_super_simple": False
        }

        # 获取装备描述
        large_desc = equip_data.get('large_equip_desc', '')
        
        if not large_desc:
            return features
            
        try:
            # 检查是否包含超级简易特效
            if '特效：超级简易' in large_desc:
                features['is_super_simple'] = True
                
                # 调试信息
                print(f"[DEBUG] 成功提取特效 - 超级简易: True")
                
        except Exception as e:
            self.logger.warning(f"提取特效特征时出错: {e}")
            
        return features
    
    def _extract_other_features(self, equip_data: Dict[str, Any]) -> Dict[str, int]:
        """
        提取灵饰装备的其他特征
        
        从large_equip_desc中提取装备的其他信息：
        - 修理失败次数：影响装备耐久度和价值
        
        Args:
            equip_data: 装备数据字典
            
        Returns:
            Dict[str, int]: 其他特征字典
                repair_fail_num: int - 修理失败次数
        """
        features = {}

        # 默认值
        features['repair_fail_num'] = 0

        # 从large_equip_desc解析
        large_desc = equip_data.get('large_equip_desc', '')
        if large_desc:
            # 解析修理失败次数
            repair_match = re.search(r'修理失败\s+(\d+)次', large_desc)
            if repair_match:
                repair_count = int(repair_match.group(1))
                features['repair_fail_num'] = repair_count
                # print(f"成功提取修理失败次数: {repair_count}")
            else:
                # 如果包含修理信息但没有匹配到，记录一下
                if "修理失败" in large_desc:
                    print(f"警告：发现修理失败信息但正则匹配失败")
                    # 提取修理失败相关的片段用于调试
                    start_idx = large_desc.find("修理失败")
                    end_idx = large_desc.find("#", start_idx)
                    if end_idx == -1:
                        end_idx = start_idx + 20
                    repair_part = large_desc[start_idx:end_idx]
                    print(f"修理失败片段: '{repair_part}'")

        return features

    def extract_features_batch(self, equip_list: List[Dict[str, Any]]) -> List[Dict[str, Union[int, float, str]]]:
        """
        批量提取灵饰装备特征
        
        Args:
            equip_list: 装备数据列表
            
        Returns:
            List[Dict[str, Union[int, float, str]]]: 特征字典列表
                每个字典包含15个特征字段，详见extract_features方法的返回值说明
        """
        results = []
        for equip_data in equip_list:
            try:
                features = self.extract_features(equip_data)
                results.append(features)
            except Exception as e:
                self.logger.error(f"提取灵饰装备特征失败: {e}")
                results.append({})
        return results
