"""
常量管理包

统一管理项目中的各种常量，避免硬编码
"""

from .equipment_types import (
    LINGSHI_KINDIDS, PET_EQUIP_KINDID, WEAPON_KINDIDS, ARMOR_KINDIDS, ACCESSORY_KINDIDS,
    ALL_EQUIP_KINDIDS, EQUIP_CATEGORIES,
    is_lingshi, is_pet_equip, is_weapon, is_armor, is_accessory,
    get_equip_category, get_equip_category_name
)

__all__ = [
    'LINGSHI_KINDIDS', 'PET_EQUIP_KINDID', 'WEAPON_KINDIDS', 'ARMOR_KINDIDS', 'ACCESSORY_KINDIDS',
    'ALL_EQUIP_KINDIDS', 'EQUIP_CATEGORIES',
    'is_lingshi', 'is_pet_equip', 'is_weapon', 'is_armor', 'is_accessory',
    'get_equip_category', 'get_equip_category_name'
] 