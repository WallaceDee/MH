import logging
from typing import Dict, Any, Union, List, Optional
from abc import ABC, abstractmethod

# 导入各个特征提取器
from .equip_feature_extractor import EquipFeatureExtractor
from .lingshi_feature_extractor import LingshiFeatureExtractor
from .pet_equip_feature_extractor import PetEquipFeatureExtractor
from .pet_feature_extractor import PetFeatureExtractor

# 导入装备类型常量
from ..constants.equipment_types import LINGSHI_KINDIDS, PET_EQUIP_KINDID

logger = logging.getLogger(__name__)


class UnifiedFeatureExtractor:
    """
    统一特征提取器
    
    根据kindid自动调用相应的特征提取器：
    - kindid 61-64: 灵饰装备 -> LingshiFeatureExtractor
    - kindid 29: 宠物装备 -> PetEquipFeatureExtractor
    - 其他: 普通装备 -> EquipFeatureExtractor
    - 宠物: 使用PetFeatureExtractor
    """
    
    def __init__(self):
        """初始化统一特征提取器"""
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个特征提取器
        self.equip_extractor = EquipFeatureExtractor()
        self.lingshi_extractor = LingshiFeatureExtractor()
        self.pet_equip_extractor = PetEquipFeatureExtractor()
        self.pet_extractor = PetFeatureExtractor()
        
        # 定义kindid映射规则
        self.kindid_mapping = {
            # 灵饰装备 (61-64)
            **{kindid: 'lingshi' for kindid in LINGSHI_KINDIDS},
            
            # 宠物装备
            PET_EQUIP_KINDID: 'pet_equip',  # 宠物装备
            
            # 默认使用普通装备提取器
            'default': 'equip'
        }
        
        print("统一特征提取器初始化完成")
    
    def get_extractor_by_kindid(self, kindid: int) -> Any:
        """
        根据kindid获取对应的特征提取器
        
        Args:
            kindid: 装备类型ID
            
        Returns:
            对应的特征提取器实例
        """
        extractor_type = self.kindid_mapping.get(kindid, self.kindid_mapping['default'])
        
        if extractor_type == 'lingshi':
            return self.lingshi_extractor
        elif extractor_type == 'pet_equip':
            return self.pet_equip_extractor
        elif extractor_type == 'equip':
            return self.equip_extractor
        else:
            # 默认使用普通装备提取器
            return self.equip_extractor
    
    def extract_features(self, data: Dict[str, Any], data_type: str = 'equipment') -> Dict[str, Union[int, float, str]]:
        """
        提取特征
        
        Args:
            data: 数据字典
            data_type: 数据类型 ('equipment' 或 'pet')
            
        Returns:
            Dict[str, Union[int, float, str]]: 提取的特征字典
        """
        try:
            if data_type == 'pet':
                # 宠物数据使用宠物特征提取器
                return self.pet_extractor.extract_features(data)
            
            # 装备数据根据kindid选择提取器
            kindid = data.get('kindid', 0)
            extractor = self.get_extractor_by_kindid(kindid)
            
            self.logger.info(f"使用 {extractor.__class__.__name__} 提取 kindid={kindid} 的特征")
            
            return extractor.extract_features(data)
            
        except Exception as e:
            self.logger.error(f"特征提取失败: {e}")
            raise
    
    def extract_features_batch(self, data_list: List[Dict[str, Any]], data_type: str = 'equipment') -> List[Dict[str, Union[int, float, str]]]:
        """
        批量提取特征
        
        Args:
            data_list: 数据字典列表
            data_type: 数据类型 ('equipment' 或 'pet')
            
        Returns:
            List[Dict[str, Union[int, float, str]]]: 特征字典列表
        """
        try:
            if data_type == 'pet':
                # 宠物数据使用宠物特征提取器
                return self.pet_extractor.extract_features_batch(data_list)
            
            # 装备数据按kindid分组处理
            results = []
            
            for data in data_list:
                try:
                    features = self.extract_features(data, data_type)
                    results.append(features)
                except Exception as e:
                    self.logger.error(f"批量提取特征失败: {e}")
                    results.append({})
            
            return results
            
        except Exception as e:
            self.logger.error(f"批量特征提取失败: {e}")
            raise
    
    def get_supported_kindids(self) -> Dict[str, List[int]]:
        """
        获取支持的kindid列表
        
        Returns:
            Dict[str, List[int]]: 支持的kindid分类
        """
        return {
            'lingshi': LINGSHI_KINDIDS,
            'pet_equip': [PET_EQUIP_KINDID],
            'equip': [i for i in range(1, 100) if i not in [PET_EQUIP_KINDID] + LINGSHI_KINDIDS]
        }
    
    def is_supported_kindid(self, kindid: int) -> bool:
        """
        检查是否支持指定的kindid
        
        Args:
            kindid: 装备类型ID
            
        Returns:
            bool: 是否支持
        """
        supported_kindids = []
        for kindids in self.get_supported_kindids().values():
            supported_kindids.extend(kindids)
        
        return kindid in supported_kindids
    
    def get_extractor_info(self, kindid: int) -> Dict[str, Any]:
        """
        获取指定kindid的提取器信息
        
        Args:
            kindid: 装备类型ID
            
        Returns:
            Dict[str, Any]: 提取器信息
        """
        extractor = self.get_extractor_by_kindid(kindid)
        
        return {
            'kindid': kindid,
            'extractor_class': extractor.__class__.__name__,
            'extractor_type': self.kindid_mapping.get(kindid, self.kindid_mapping['default']),
            'supported': self.is_supported_kindid(kindid)
        } 