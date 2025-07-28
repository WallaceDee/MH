"""
装备类型常量管理

统一管理所有装备类型ID，避免硬编码
"""

# 灵饰装备类型
LINGSHI_KINDIDS = [61, 62, 63, 64]

# 宠物装备类型
PET_EQUIP_KINDID = 29

# 武器类装备类型
WEAPON_KINDIDS = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 52, 53, 54, 72, 73, 74]

# 防具类装备类型
ARMOR_KINDIDS = [18, 59]

# 饰品类装备类型
ACCESSORY_KINDIDS = [17, 19, 20, 21, 58]

# 所有装备类型
ALL_EQUIP_KINDIDS = WEAPON_KINDIDS + ARMOR_KINDIDS + ACCESSORY_KINDIDS + LINGSHI_KINDIDS + [PET_EQUIP_KINDID]

# 装备类型分类映射
EQUIP_CATEGORIES = {
    'weapons': {
        'name': '武器',
        'kindids': WEAPON_KINDIDS,
        'description': '包含枪矛、斧钺、剑、双短剑、飘带、爪刺、扇、魔棒、鞭、环圈、刀、锤、宝珠、弓箭、法杖、灯笼、巨剑、伞'
    },
    'armors': {
        'name': '防具',
        'kindids': ARMOR_KINDIDS,
        'description': '包含铠甲、女衣'
    },
    'accessories': {
        'name': '饰品',
        'kindids': ACCESSORY_KINDIDS,
        'description': '包含头盔、鞋子、腰带、饰物、发钗'
    },
    'lingshi': {
        'name': '灵饰',
        'kindids': LINGSHI_KINDIDS,
        'description': '包含灵饰'
    },
    'pet_equip': {
        'name': '宠物装备',
        'kindids': [PET_EQUIP_KINDID],
        'description': '包含宠物装备'
    }
}


def is_lingshi(kindid: int) -> bool:
    """判断是否为灵饰装备"""
    return kindid in LINGSHI_KINDIDS


def is_pet_equip(kindid: int) -> bool:
    """判断是否为宠物装备"""
    return kindid == PET_EQUIP_KINDID


def is_weapon(kindid: int) -> bool:
    """判断是否为武器"""
    return kindid in WEAPON_KINDIDS


def is_armor(kindid: int) -> bool:
    """判断是否为防具"""
    return kindid in ARMOR_KINDIDS


def is_accessory(kindid: int) -> bool:
    """判断是否为饰品"""
    return kindid in ACCESSORY_KINDIDS


def get_equip_category(kindid: int) -> str:
    """获取装备分类"""
    for category, info in EQUIP_CATEGORIES.items():
        if kindid in info['kindids']:
            return category
    return 'unknown'


def get_equip_category_name(kindid: int) -> str:
    """获取装备分类名称"""
    for category, info in EQUIP_CATEGORIES.items():
        if kindid in info['kindids']:
            return info['name']
    return '未知' 