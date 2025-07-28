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
            
            # 检查是否只有large_equip_desc字段，如果是则先解析
            if self._is_desc_only_data(equip_data):
                equip_data = self._parse_equip_data_from_desc(equip_data)
            
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

    def _is_desc_only_data(self, equip_data: Dict[str, Any]) -> bool:
        """
        判断是否为只有large_equip_desc字段的数据
        
        Args:
            equip_data: 装备数据字典
            
        Returns:
            bool: 如果只有large_equip_desc字段则返回True
        """
        # 检查是否只有large_equip_desc字段
        if 'large_equip_desc' not in equip_data:
            return False
        
        # 检查其他关键字段是否缺失
        key_fields = ['kindid', 'equip_level', 'speed', 'qixue', 'fangyu', 'shanghai']
        missing_fields = [field for field in key_fields if field not in equip_data or equip_data[field] is None]
        
        # 如果大部分关键字段都缺失，认为是desc_only数据
        return len(missing_fields) >= len(key_fields) * 0.7

    def _parse_equip_data_from_desc(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从large_equip_desc解析出完整的装备数据
        
        Args:
            equip_data: 原始装备数据（只有large_equip_desc）
            
        Returns:
            Dict[str, Any]: 解析后的完整装备数据
        """
        desc = equip_data.get('large_equip_desc', '')
        if not desc:
            return equip_data
        
        # 创建新的装备数据字典
        parsed_data = equip_data.copy()
        
        # 设置默认值
        from ..constants.equipment_types import PET_EQUIP_KINDID
        parsed_data['kindid'] = PET_EQUIP_KINDID  # 宠物装备默认kindid
        parsed_data['equip_level'] = 0
        
        # 初始化所有字段为0
        parsed_data['speed'] = 0
        parsed_data['qixue'] = 0
        parsed_data['fangyu'] = 0
        parsed_data['shanghai'] = 0
        parsed_data['addon_fali'] = 0
        parsed_data['addon_lingli'] = 0
        parsed_data['addon_liliang'] = 0
        parsed_data['addon_minjie'] = 0
        parsed_data['addon_naili'] = 0
        parsed_data['addon_tizhi'] = 0
        parsed_data['xiang_qian_level'] = 0
        parsed_data['addon_status'] = ''
        
        # 解析基础属性
        self._parse_basic_attrs_from_desc(desc, parsed_data)
        
        # 解析附加属性
        self._parse_added_attrs_from_desc(desc, parsed_data)
        
        # 解析宝石信息
        self._parse_gem_info_from_desc(desc, parsed_data)
        
        # 解析套装信息
        self._parse_suit_info_from_desc(desc, parsed_data)
        
        # 解析装备等级
        self._parse_equip_level_from_desc(desc, parsed_data)
        
        return parsed_data

    def _parse_basic_attrs_from_desc(self, desc: str, parsed_data: Dict[str, Any]):
        """从描述中解析基础属性"""
        # 解析速度 - 只匹配基础属性，避免匹配宝石属性
        speed_patterns = [
            r'#r速度\s*\+(\d+)',      # #r速度 +48
            r'速度\s*\+(\d+)(?!\s*镶嵌)',  # 速度 +48 (后面不是镶嵌)
            r'\+(\d+)\s*速度(?!\s*镶嵌)',  # +48 速度 (后面不是镶嵌)
        ]
        for pattern in speed_patterns:
            speed_match = re.search(pattern, desc)
            if speed_match:
                parsed_data['speed'] = int(speed_match.group(1))
                break
        
        # 解析气血 - 只匹配基础属性，避免匹配宝石属性，支持负值
        qixue_patterns = [
            r'#r气血\s*\+(\d+)',      # #r气血 +120
            r'#r气血\s*-(\d+)',       # #r气血 -3
            r'气血\s*\+(\d+)(?!\s*镶嵌)',  # 气血 +120 (后面不是镶嵌)
            r'气血\s*-(\d+)(?!\s*镶嵌)',  # 气血 -3 (后面不是镶嵌)
            r'\+(\d+)\s*气血(?!\s*镶嵌)',  # +120 气血 (后面不是镶嵌)
            r'-(\d+)\s*气血(?!\s*镶嵌)',  # -3 气血 (后面不是镶嵌)
        ]
        for pattern in qixue_patterns:
            qixue_match = re.search(pattern, desc)
            if qixue_match:
                value = int(qixue_match.group(1))
                # 如果是负值模式，需要取负
                if '-(\d+)' in pattern or '气血\s*-(\d+)' in pattern:
                    value = -value
                parsed_data['qixue'] = value
                break
        
        # 解析防御 - 只匹配基础属性，避免匹配宝石属性
        fangyu_patterns = [
            r'#r防御\s*\+(\d+)',      # #r防御 +120
            r'防御\s*\+(\d+)(?!\s*镶嵌)',  # 防御 +120 (后面不是镶嵌)
            r'\+(\d+)\s*防御(?!\s*镶嵌)',  # +120 防御 (后面不是镶嵌)
        ]
        for pattern in fangyu_patterns:
            fangyu_match = re.search(pattern, desc)
            if fangyu_match:
                parsed_data['fangyu'] = int(fangyu_match.group(1))
                break
        
        # 解析伤害 - 只匹配基础属性，避免匹配宝石属性
        shanghai_patterns = [
            r'#r伤害\s*\+(\d+)',      # #r伤害 +65
            r'伤害\s*\+(\d+)(?!\s*镶嵌)',  # 伤害 +65 (后面不是镶嵌)
            r'\+(\d+)\s*伤害(?!\s*镶嵌)',  # +65 伤害 (后面不是镶嵌)
        ]
        for pattern in shanghai_patterns:
            shanghai_match = re.search(pattern, desc)
            if shanghai_match:
                parsed_data['shanghai'] = int(shanghai_match.group(1))
                break

    def _parse_added_attrs_from_desc(self, desc: str, parsed_data: Dict[str, Any]):
        """从描述中解析附加属性"""
        # 解析法力 - 支持多种格式，包括负值
        fali_patterns = [
            r'法力\s*\+(\d+)',
            r'法力\s*-(\d+)',      # 法力 -16
            r'\+(\d+)\s*法力',
            r'-(\d+)\s*法力',      # -16 法力
            r'法力\s*(\d+)',
            r'#Y\+(\d+)\s*法力',
            r'#Y-(\d+)\s*法力',    # #Y-16 法力
            r'#G#G法力\s*\+(\d+)',  # #G#G法力 +19
            r'#G#G法力\s*-(\d+)',  # #G#G法力 -16
            r'#G#G\+(\d+)\s*法力',
            r'#G#G-(\d+)\s*法力'   # #G#G-16 法力
        ]
        for pattern in fali_patterns:
            fali_match = re.search(pattern, desc)
            if fali_match:
                value = int(fali_match.group(1))
                # 如果是负值模式，需要取负
                if '-(\d+)' in pattern or '法力\s*-(\d+)' in pattern or '#G#G法力\s*-(\d+)' in pattern:
                    value = -value
                parsed_data['addon_fali'] = value
                break
        
        # 解析灵力 - 支持多种格式，避免匹配镶嵌效果，包括负值
        lingli_patterns = [
            r'#G#G灵力\s*\+(\d+)',  # #G#G灵力 +10 (附加属性)
            r'#G#G灵力\s*-(\d+)',   # #G#G灵力 -8 (附加属性)
            r'#G#G\+(\d+)\s*灵力',  # #G#G+10 灵力 (附加属性)
            r'#G#G-(\d+)\s*灵力',   # #G#G-8 灵力 (附加属性)
            r'灵力\s*\+(\d+)(?!\s*镶嵌)',  # 灵力 +10 (非镶嵌)
            r'灵力\s*-(\d+)(?!\s*镶嵌)',  # 灵力 -8 (非镶嵌)
            r'\+(\d+)\s*灵力(?!\s*镶嵌)',  # +10 灵力 (非镶嵌)
            r'-(\d+)\s*灵力(?!\s*镶嵌)',  # -8 灵力 (非镶嵌)
            r'灵力\s*(\d+)(?!\s*镶嵌)',    # 灵力 10 (非镶嵌)
            r'#Y\+(\d+)\s*灵力(?!\s*镶嵌)', # #Y+10 灵力 (非镶嵌)
            r'#Y-(\d+)\s*灵力(?!\s*镶嵌)'  # #Y-8 灵力 (非镶嵌)
        ]
        for pattern in lingli_patterns:
            lingli_match = re.search(pattern, desc)
            if lingli_match:
                value = int(lingli_match.group(1))
                # 如果是负值模式，需要取负
                if '-(\d+)' in pattern or '灵力\s*-(\d+)' in pattern or '#G#G灵力\s*-(\d+)' in pattern:
                    value = -value
                parsed_data['addon_lingli'] = value
                break
        
        # 解析力量 - 支持多种格式，包括负值
        liliang_patterns = [
            r'力量\s*\+(\d+)',
            r'力量\s*-(\d+)',      # 力量 -8
            r'\+(\d+)\s*力量',
            r'-(\d+)\s*力量',      # -8 力量
            r'力量\s*(\d+)',
            r'#Y\+(\d+)\s*力量',
            r'#Y-(\d+)\s*力量',    # #Y-8 力量
            r'#G#G力量\s*\+(\d+)',  # #G#G力量 +23
            r'#G#G力量\s*-(\d+)',  # #G#G力量 -8
            r'#G#G\+(\d+)\s*力量',
            r'#G#G-(\d+)\s*力量'   # #G#G-8 力量
        ]
        for pattern in liliang_patterns:
            liliang_match = re.search(pattern, desc)
            if liliang_match:
                value = int(liliang_match.group(1))
                # 如果是负值模式，需要取负
                if '-(\d+)' in pattern or '力量\s*-(\d+)' in pattern or '#G#G力量\s*-(\d+)' in pattern:
                    value = -value
                parsed_data['addon_liliang'] = value
                break
        
        # 解析敏捷 - 支持多种格式，包括负值
        minjie_patterns = [
            r'敏捷\s*\+(\d+)',
            r'敏捷\s*-(\d+)',      # 敏捷 -13
            r'\+(\d+)\s*敏捷',
            r'-(\d+)\s*敏捷',      # -13 敏捷
            r'敏捷\s*(\d+)',
            r'#Y\+(\d+)\s*敏捷',
            r'#Y-(\d+)\s*敏捷',    # #Y-13 敏捷
            r'#G#G敏捷\s*\+(\d+)',  # #G#G敏捷 +16
            r'#G#G敏捷\s*-(\d+)',  # #G#G敏捷 -13
            r'#G#G\+(\d+)\s*敏捷',
            r'#G#G-(\d+)\s*敏捷'   # #G#G-13 敏捷
        ]
        for pattern in minjie_patterns:
            minjie_match = re.search(pattern, desc)
            if minjie_match:
                value = int(minjie_match.group(1))
                # 如果是负值模式，需要取负
                if '-(\d+)' in pattern or '敏捷\s*-(\d+)' in pattern or '#G#G敏捷\s*-(\d+)' in pattern:
                    value = -value
                parsed_data['addon_minjie'] = value
                break
        
        # 解析耐力 - 支持多种格式，包括负值
        naili_patterns = [
            r'耐力\s*\+(\d+)',
            r'耐力\s*-(\d+)',      # 耐力 -11
            r'\+(\d+)\s*耐力',
            r'-(\d+)\s*耐力',      # -11 耐力
            r'耐力\s*(\d+)',
            r'#Y\+(\d+)\s*耐力',
            r'#Y-(\d+)\s*耐力',    # #Y-11 耐力
            r'#G#G耐力\s*\+(\d+)',  # #G#G耐力 +19
            r'#G#G耐力\s*-(\d+)',  # #G#G耐力 -11
            r'#G#G\+(\d+)\s*耐力',
            r'#G#G-(\d+)\s*耐力'   # #G#G-11 耐力
        ]
        for pattern in naili_patterns:
            naili_match = re.search(pattern, desc)
            if naili_match:
                value = int(naili_match.group(1))
                # 如果是负值模式，需要取负
                if '-(\d+)' in pattern or '耐力\s*-(\d+)' in pattern or '#G#G耐力\s*-(\d+)' in pattern:
                    value = -value
                parsed_data['addon_naili'] = value
                break
        
        # 解析体质 - 支持多种格式，包括负值
        tizhi_patterns = [
            r'体质\s*\+(\d+)',
            r'体质\s*-(\d+)',      # 体质 -3
            r'\+(\d+)\s*体质',
            r'-(\d+)\s*体质',      # -3 体质
            r'体质\s*(\d+)',
            r'#Y\+(\d+)\s*体质',
            r'#Y-(\d+)\s*体质',    # #Y-3 体质
            r'#G#G体质\s*\+(\d+)',  # #G#G体质 +5
            r'#G#G体质\s*-(\d+)',  # #G#G体质 -3
            r'#G#G\+(\d+)\s*体质',
            r'#G#G-(\d+)\s*体质'   # #G#G-3 体质
        ]
        for pattern in tizhi_patterns:
            tizhi_match = re.search(pattern, desc)
            if tizhi_match:
                value = int(tizhi_match.group(1))
                # 如果是负值模式，需要取负
                if '-(\d+)' in pattern or '体质\s*-(\d+)' in pattern or '#G#G体质\s*-(\d+)' in pattern:
                    value = -value
                parsed_data['addon_tizhi'] = value
                break

    def _parse_gem_info_from_desc(self, desc: str, parsed_data: Dict[str, Any]):
        """从描述中解析宝石信息"""
        # 解析宝石等级 - 支持多种格式
        gem_level_patterns = [
            r'镶嵌等级[：:]\s*(\d+)',  # 镶嵌等级：8
        ]
        for pattern in gem_level_patterns:
            gem_level_match = re.search(pattern, desc)
            if gem_level_match:
                parsed_data['xiang_qian_level'] = int(gem_level_match.group(1))
                break

    def _parse_suit_info_from_desc(self, desc: str, parsed_data: Dict[str, Any]):
        """从描述中解析套装信息"""
        if not desc:
            # 如果没有描述，设置默认值
            parsed_data['addon_status'] = ''
            parsed_data['suit_category'] = '无套装'
            return
        
        # 移除颜色代码
        desc_clean = re.sub(r'#c4DBAF4', '', desc)
        desc_clean = re.sub(r'#[A-Z]', '', desc_clean)
        
        # 查找套装效果相关信息
        pattern = r'套装效果：附加状态\s*([^#\n]+)'  # 套装效果：xxx
        match = re.search(pattern, desc_clean)
        if match:
            suit_info = match.group(1).strip()
            # 清理多余的空格和特殊字符
            suit_info = re.sub(r'\s+', ' ', suit_info)
            parsed_data['addon_status'] = suit_info
            
            # 计算suit_category
            suit_category = self._classify_suit_effect(suit_info)
            parsed_data['suit_category'] = suit_category
        else:
            # 没有找到套装效果，设置默认值
            parsed_data['addon_status'] = ''
            parsed_data['suit_category'] = '无套装'

    def _classify_suit_effect(self, suit_effect: str) -> str:
        """
        根据套装效果分类
        
        Args:
            suit_effect: 套装效果名称
            
        Returns:
            str: 套装分类 ('无套装', '物理系', '法术系', '辅助系', '特殊系', '其他')
        """
        if not suit_effect or suit_effect.strip() == '':
            return '无套装'
        
        # 转换为字符串并去除空格
        effect_name = str(suit_effect).strip()
        
        # 物理系套装效果
        physical_suits = [
            '高级必杀', '高级偷袭', '高级吸血', '高级连击', '高级进击必杀'
        ]
        
        # 法术系套装效果
        magic_suits = [
            '高级魔之心', '高级法术连击', '高级法术暴击', '高级法术波动', '高级进击法爆'
        ]
        
        # 辅助系套装效果
        support_suits = [
            '高级神佑', '高级鬼混术'
        ]
        
        # 特殊系套装效果
        special_suits = [
            '善恶有报', '力劈华山', '死亡召唤', '上古灵符', '壁垒击破', 
            '嗜血追击', '剑荡四方', '夜舞倾城', '惊心一剑'
        ]
        
        # 检查分类
        if effect_name in physical_suits:
            return '物理系'
        elif effect_name in magic_suits:
            return '法术系'
        elif effect_name in support_suits:
            return '辅助系'
        elif effect_name in special_suits:
            return '特殊系'
        elif '高级'  in effect_name:
            return '高级其他'
        else:
            return '其他'

    def _parse_equip_level_from_desc(self, desc: str, parsed_data: Dict[str, Any]):
        """从描述中解析装备等级"""
        # 解析装备等级 - 只匹配开头的等级信息，避免匹配到宝石等级
        level_patterns = [
            r'#r等级\s*(\d+)',          # #r等级 125
        ]
        for pattern in level_patterns:
            level_match = re.search(pattern, desc)
            if level_match:
                parsed_data['equip_level'] = int(level_match.group(1))
                break

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
        from ..constants.equipment_types import PET_EQUIP_KINDID
        features['kindid'] = equip_data.get('kindid', PET_EQUIP_KINDID)  # 宠物装备默认为PET_EQUIP_KINDID
        
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
        
        # 添加宝石等级字段（兼容字段）
        features['xiang_qian_level'] = gem_level
        
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
                addon_status: str - 套装效果名称（兼容字段）
                suit_category: str - 套装分类 ('无套装', '物理系', '法术系', '辅助系', '特殊系', '其他')
        """
        features = {}
        
        # 套装名称
        suit_effect = equip_data.get('addon_status', '')
        features['suit_effect'] = suit_effect
        features['addon_status'] = suit_effect  # 兼容字段
        
        # 套装分类
        suit_category = self._classify_suit_effect(suit_effect)
        features['suit_category'] = suit_category
        
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
