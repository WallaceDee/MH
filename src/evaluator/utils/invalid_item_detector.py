"""
无效物品检测工具类

提供通用的无效物品判断功能，供各个估价类使用
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

from src.evaluator.constants.equipment_types import PET_EQUIP_KINDID

class ItemType(Enum):
    """物品类型枚举"""
    EQUIPMENT = "equipment"      # 装备
    PET = "pet"                  # 召唤兽


class InvalidReason(Enum):
    """无效原因枚举"""
    NO_VALUE = "no_value"                    # 无价值
    BROKEN_EQUIPMENT = "broken_equipment"    # 损坏装备
    WORTHLESS_PET = "worthless_pet"         # 无价值召唤兽


class InvalidItemDetector:
    """无效物品检测工具类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    
    def detect_invalid_item(self, 
                           item_data: Dict[str, Any]) -> Tuple[bool, Optional[InvalidReason], str]:
        """
        检测物品是否无效
        
        Args:
            item_data: 物品数据字典
            item_type: 物品类型，如果为None则自动判断
            
        Returns:
            Tuple[bool, Optional[InvalidReason], str]: 
                - 是否无效
                - 无效原因（如果有效则为None）
                - 详细说明
        """
        try:
            # 自动判断物品类型
            item_type = self._detect_item_type(item_data)
            # 根据物品类型进行相应的无效检测
            if item_type == ItemType.EQUIPMENT:
                return self._detect_invalid_equipment(item_data)
            elif item_type == ItemType.PET:
                return self._detect_invalid_pet(item_data)
                
        except Exception as e:
            self.logger.error(f"检测无效物品时出错: {e}")
            return False, None, f"检测过程出错: {str(e)}"
    
    def _detect_item_type(self, item_data: Dict[str, Any]) -> ItemType:
        """自动检测物品类型"""
        try:
            # 通过kindid判断装备类型
            kindid = item_data.get('kindid', 0)
            if kindid > 0:
                return ItemType.EQUIPMENT
            elif item_data.get('iType', 0) == 17320:
                return ItemType.EQUIPMENT
            else:
                return ItemType.PET
   
                    
        except Exception as e:
            self.logger.warning(f"自动检测物品类型失败: {e}")
            return ItemType.EQUIPMENT
    
    def _detect_invalid_equipment(self, item_data: Dict[str, Any]) -> Tuple[bool, Optional[InvalidReason], str]:
        """检测装备是否无效"""
        try:
            # 检查修理失败次数
            repair_fail = item_data.get('repair_fail_num', 0)
            equip_level = item_data.get('equip_level', 0)
            kindid = item_data.get('kindid', 0)
            if equip_level == 0:
                return True, InvalidReason.NO_VALUE, f"不是有效的装备"
            elif equip_level < 60:
                return True, InvalidReason.NO_VALUE, f"装备等级过低: {equip_level}"
            if repair_fail >= 3 and equip_level > 120:
                return True, InvalidReason.BROKEN_EQUIPMENT, f"修理失败次数过多: {repair_fail}"
            
            if kindid == PET_EQUIP_KINDID:
                if item_data.get('qixue', 0) == 0  and item_data.get('shanghai', 0) == 0 and item_data.get('addon_fali', 0) == 0 and item_data.get('addon_lingli', 0) == 0 and item_data.get('addon_liliang', 0) == 0 and item_data.get('addon_minjie', 0) == 0 and item_data.get('addon_naili', 0) == 0 and item_data.get('addon_tizhi', 0) == 0  and item_data.get('addon_status', '') == '':
                     return True, InvalidReason.NO_VALUE, f"白板召唤兽装备"
            return False, None, "装备有效"
            
        except Exception as e:
            self.logger.error(f"检测装备无效性时出错: {e}")
            return False, None, f"检测过程出错: {str(e)}"
  
    
    
    def _detect_invalid_pet(self, item_data: Dict[str, Any]) -> Tuple[bool, Optional[InvalidReason], str]:
        """检测召唤兽是否无效"""
        try:
            
            # 检查等级
            equip_level = item_data.get('equip_level', 0)
            if equip_level < 30:
                return True, InvalidReason.WORTHLESS_PET, f"等级过低: {equip_level}"
            
            # 检查技能数量
            is_baobao = item_data.get('is_baobao', False)
            skill_count = item_data.get('skill_count', 0)
            if not is_baobao:
                if equip_level < 100:
                    return True, InvalidReason.WORTHLESS_PET, f"野生且等级过低: {equip_level}"
                if skill_count < 5:
                    return True, InvalidReason.WORTHLESS_PET, f"野生且技能数量过少: {skill_count}"
            
            return False, None, "召唤兽有效"
            
        except Exception as e:
            self.logger.error(f"检测召唤兽无效性时出错: {e}")
            return False, None, f"检测过程出错: {str(e)}"
    
    def get_invalid_reason_description(self, reason: InvalidReason) -> str:
        """获取无效原因的详细描述"""
        descriptions = {
            InvalidReason.NO_VALUE: "物品无实际价值",
            InvalidReason.BROKEN_EQUIPMENT: "装备损坏严重",
            InvalidReason.WORTHLESS_PET: "召唤兽价值过低",
        }
        return descriptions.get(reason, "未知原因")
    
    def should_skip_valuation(self, 
                            item_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        判断是否应该跳过估价
        
        Args:
            item_data: 物品数据
            item_type: 物品类型
            
        Returns:
            Tuple[bool, str]: 是否跳过估价，跳过原因
        """
        is_invalid, reason, description = self.detect_invalid_item(item_data )
        
        if is_invalid:
            reason_desc = self.get_invalid_reason_description(reason) if reason else "未知原因"
            return True, f"{reason_desc}: {description}"
        
        return False, ""