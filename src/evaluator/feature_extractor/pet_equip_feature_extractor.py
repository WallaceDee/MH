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

class PetEquipFeatureExtractor:
    """梦幻西游宠物装备特征提取器"""

    def __init__(self):
        """初始化特征提取器"""
        print("初始化特征提取器...")
        self.logger = logging.getLogger(__name__)



    def extract_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float, str]]:
        """
        提取宠物装备的所有特征
        
        Args:
            equip_data: 装备数据字典
            
        Returns:
            Dict[str, Union[int, float, str]]: 提取的特征字典，包含以下字段:
            
            基础属性特征 (Basic Features):
                equip_level: int - 装备等级
                kindid: int - 装备类型ID
                mingzhong: int - 命中值
                speed: int - 速度值
                qixue: int - 气血值
                fangyu: int - 防御值
                shanghai: int - 伤害值
                
            附加属性特征 (Added Attributes):
                addon_fali: int - 法力附加属性
                addon_lingli: int - 灵力附加属性
                addon_liliang: int - 力量附加属性
                addon_minjie: int - 敏捷附加属性
                addon_naili: int - 耐力附加属性
                addon_tizhi: int - 体质附加属性
                
            宝石特征 (Gem Features):
                gem_score: float - 标准化宝石得分 (0-1之间)
                
            套装特征 (Suit Features):
                suit_effect: str - 套装效果名称 (如"高级强力"、"高级反震"等)
        """
        try:
            features = {}
            
            # 一、基础属性特征
            features.update(self._extract_basic_features(equip_data))

            # 二、附加属性
            features.update(self._extract_added_attrs_features(equip_data))

            # 三、宝石
            features.update(self._extract_gem_features(equip_data))

            # 四、套装
            features.update(self._extract_suit_effect_features(equip_data))
            
            # 五、其他特征（从large_equip_desc提取）
            features.update(self._extract_other_features(equip_data))

            return features

        except Exception as e:
            print(f"特征提取失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise

    def _extract_basic_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float]]:
        """
        提取宠物装备的基础属性特征
        Args:
            equip_data: 装备数据字典
            
        Returns:
            Dict[str, Union[int, float]]: 基础属性特征字典
                equip_level: int - 装备等级
                kindid: int - 装备类型ID
                mingzhong: int - 命中
                speed: int - 速度
                qixue: int - 气血
                fangyu: int - 防御
                shanghai: int - 伤害
        """
        features = {}
        
        # 装备等级
        features['equip_level'] = equip_data.get('equip_level', 0)
        
        # 装备类型ID - 这个非常重要，用于插件系统识别
        features['kindid'] = equip_data.get('kindid', 29)  # 宠物装备默认为29
        
        # 基础属性
        # features['mingzhong'] = equip_data.get('mingzhong', 0) #不重要
        features['speed'] = equip_data.get('speed', 0)
        features['qixue'] = equip_data.get('qixue', 0)
        features['fangyu'] = equip_data.get('fangyu', 0)
        features['shanghai'] = equip_data.get('shanghai', 0)
        
        return features
    
    def _extract_added_attrs_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float]]:
        """
        提取宠物装备的附加属性特征
        Args:
            equip_data: 装备数据字典
            
        Returns:
            Dict[str, Union[int, float]]: 附加属性特征字典
                addon_fali: int - 法力
                addon_lingli: int - 灵力
                addon_liliang: int - 力量
                addon_minjie: int - 敏捷
                addon_naili: int - 耐力
                addon_tizhi: int - 体质
        """
        features = {}
        
        # 附加属性
        features['addon_fali'] = equip_data.get('addon_fali', 0)
        features['addon_lingli'] = equip_data.get('addon_lingli', 0)
        features['addon_liliang'] = equip_data.get('addon_liliang', 0)
        features['addon_minjie'] = equip_data.get('addon_minjie', 0)
        features['addon_naili'] = equip_data.get('addon_naili', 0)
        features['addon_tizhi'] = equip_data.get('addon_tizhi', 0)
        
        return features
    
    def _extract_gem_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float, str]]:
        """
        提取宠物装备的宝石特征
        
        宝石类型及价值权重：
        - 速度(90): 最高价值，对宠物速度影响最大
        - 伤害(80): 高价值，提升宠物攻击力
        - 气血(80): 高价值，提升宠物生存能力
        - 灵力(65): 中等价值，提升法术相关属性
        - 防御(45): 较低价值，提升物理防御
        - 躲避(10): 最低价值，提升闪避能力
        
        宝石类型从装备描述中提取，示例格式：
        "#Y镶嵌效果：#r#Y+48速度 镶嵌等级：8#Y"
        
        Args:
            equip_data: 装备数据字典
            
        Returns:
            Dict[str, Union[int, float, str]]: 宝石特征字典
                gem_score: float - 标准化宝石得分 (0-1之间)，综合考虑宝石等级和类型价值
        """
        # 宝石类型价值映射
        gemType2Value = {
            "速度": 90,
            "伤害": 80,
            "气血": 80,
            "灵力": 65,
            "防御": 45,
            "躲避": 10
        }
        
        features = {}
        
        # 获取宝石等级
        gem_level = equip_data.get('xiang_qian_level', 0)
        
        # 提取宝石类型
        gem_type = self._extract_gem_type(equip_data.get('large_equip_desc', ''))
        
        # 计算标准化宝石得分
        gem_score = self._calculate_gem_score(gem_level, gem_type, gemType2Value)
        features['gem_score'] = gem_score
        
        return features
    
    def _extract_gem_type(self, large_equip_desc: str) -> str:
        """
        从装备描述中提取宝石类型
        
        支持的宝石类型：速度、伤害、气血、灵力、防御、躲避
        
        提取策略：
        1. 优先匹配精确格式："#Y镶嵌效果：#r#Y+数字+宝石类型"
        2. 备选匹配格式："+数字+宝石类型+镶嵌等级"
        
        示例数据格式：
        "#Y镶嵌效果：#r#Y+48速度 镶嵌等级：8#Y"
        
        Args:
            large_equip_desc: 装备详细描述字符串
            
        Returns:
            str: 提取到的宝石类型，如"速度"、"伤害"等，未找到时返回空字符串
        """
        if not large_equip_desc:
            return ""
        
        import re
        
        # 宝石类型列表
        gem_types = ["速度", "伤害", "气血", "灵力", "防御", "躲避"]
        
        # 精确匹配镶嵌效果部分
        # 匹配模式：#Y镶嵌效果：#r#Y+数字+宝石类型
        xiang_qian_pattern = r'#Y镶嵌效果：#r#Y\+\d+([^#\s]+)'
        match = re.search(xiang_qian_pattern, large_equip_desc)
        
        if match:
            gem_text = match.group(1)
            # 精确匹配宝石类型
            for gem_type in gem_types:
                if gem_type == gem_text:
                    return gem_type
        
        # 备选方案：如果上面的模式没匹配到，尝试更宽松的模式
        # 匹配：+数字+宝石类型+镶嵌等级
        gem_pattern = r'\+(\d+)([^#\s]+)\s*镶嵌等级'
        match = re.search(gem_pattern, large_equip_desc)
        
        if match:
            gem_text = match.group(2)
            for gem_type in gem_types:
                if gem_type == gem_text:
                    return gem_type
        
        return ""
    
    def _calculate_gem_score(self, gem_level: int, gem_type: str, gemType2Value: Dict[str, int]) -> float:
        """
        计算标准化宝石得分
        
        计算公式：
        gem_value = (2^gem_level - 1) * gemType2Value[gem_type]
        normalized_score = gem_value / max_possible_value
        
        其中：
        - gem_level: 宝石等级 (1-16)
        - gemType2Value[gem_type]: 宝石类型基础价值 (10-90)
        - max_possible_value: 最大可能价值，以10级速度宝石为基准
        
        标准化基准：假设最高等级为10级，最高价值宝石为速度(90)
        max_possible_value = (2^10 - 1) * 90 = 1023 * 90 = 92070
        
        Args:
            gem_level: 宝石镶嵌等级
            gem_type: 宝石类型名称
            gemType2Value: 宝石类型到基础价值的映射字典
            
        Returns:
            float: 标准化得分，范围0-1，值越大表示宝石价值越高
        """
        if not gem_type or gem_level <= 0:
            return 0.0
        
        # 获取宝石类型的基础价值
        base_value = gemType2Value.get(gem_type, 0)
        if base_value == 0:
            return 0.0
        
        # 计算宝石价值：(2^gem_level - 1) * base_value
        gem_value = (2 ** gem_level - 1) * base_value
        
        # 标准化：除以最大可能价值 (假设最高等级为10级，最高价值宝石为速度90)
        max_possible_value = (2 ** 10 - 1) * 90  # 10级速度宝石的价值作为标准化基准
        
        # 返回标准化得分 (0-1之间)
        return min(gem_value / max_possible_value, 1.0)
    
    def _extract_suit_effect_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float, str]]:
        """
        提取宠物装备的套装特征
        
        Args:
            equip_data: 装备数据字典
            
        Returns:
            Dict[str, Union[int, float, str]]: 套装特征字典
                suit_effect: str - 套装效果名称，如"高级强力"、"高级反震"、"高级强力"等
                             如果装备没有套装效果则返回空字符串
        """
        features = {}
        
        # 套装名称
        features['suit_effect'] = equip_data.get('addon_status', '')
        
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
