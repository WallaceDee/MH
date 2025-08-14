"""
常量管理包

统一管理项目中的各种常量，避免硬编码
"""

from .equipment_types import (
    LINGSHI_KINDIDS, PET_EQUIP_KINDID, WEAPON_KINDIDS, ARMOR_KINDIDS, ACCESSORY_KINDIDS,
    ALL_EQUIP_KINDIDS, EQUIP_CATEGORIES,
    is_lingshi, is_pet_equip, is_weapon, is_armor, is_accessory, get_equip_category_name
)

from .lingshi_priorities import (
    RING_EARRING_PRIORITY, BRACELET_ACCESSORY_PRIORITY,
    get_priority_by_attr_name, is_same_priority
)

__all__ = [
    'LINGSHI_KINDIDS', 'PET_EQUIP_KINDID', 'WEAPON_KINDIDS', 'ARMOR_KINDIDS', 'ACCESSORY_KINDIDS',
    'ALL_EQUIP_KINDIDS', 'EQUIP_CATEGORIES',
    'is_lingshi', 'is_pet_equip', 'is_weapon', 'is_armor', 'is_accessory','get_equip_category_name',
    'RING_EARRING_PRIORITY', 'BRACELET_ACCESSORY_PRIORITY',
    'get_priority_by_attr_name', 'is_same_priority'
] 