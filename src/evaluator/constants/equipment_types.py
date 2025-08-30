"""
装备类型常量管理

统一管理所有装备类型ID，避免硬编码
"""
# 材料28 宝石 指南书 钟灵石  点化石 灵饰指南书 元灵晶石
MATERIAL_KINDID = 28
# 高级内丹
HIGH_INNER_DAN_KINDID = 41
# 魔兽要诀 26
MAGIC_MONSTER_KINDID = 26
# 项链
NECKLACE_KINDID = 21
# 头盔
HELMET_KINDIDS = [17,58]
HELMET_KINDID = 17  # 主要头盔类型
# 腰带
BELT_KINDID = 20
# 鞋子
SHOES_KINDID = 19
# 灵饰装备类型
LINGSHI_KINDIDS = [61, 62, 63, 64]
# 上古玉魄装备类型（暂定）
JADE_KINDIDS = [99, 98 ]

# 召唤兽装备类型
PET_EQUIP_KINDID = 29

# 武器类装备类型
WEAPON_KINDIDS = [4, 5, 6, 7, 8,
 9, 10, 11, 12, 13, 14, 15, 52, 53, 54, 72, 73, 74, 83]

# 防具类装备类型
ARMOR_KINDIDS = [18, 59]

# 饰品类装备类型
ACCESSORY_KINDIDS = [SHOES_KINDID, BELT_KINDID,NECKLACE_KINDID] + HELMET_KINDIDS

# 所有装备类型
ALL_EQUIP_KINDIDS = WEAPON_KINDIDS + ARMOR_KINDIDS + ACCESSORY_KINDIDS + LINGSHI_KINDIDS + [PET_EQUIP_KINDID] + JADE_KINDIDS

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
        'name': '召唤兽装备',
        'kindids': [PET_EQUIP_KINDID],
        'description': '包含召唤兽装备'
    },
    'jade':{
        'name': '上古玉魄',
        'kindids': JADE_KINDIDS,
        'description': '包含上古玉魄'
    }
}

def is_jade(kindid: int) -> bool:
    """判断是否为上古玉魄装备"""
    return kindid in JADE_KINDIDS


def is_lingshi(kindid: int) -> bool:
    """判断是否为灵饰装备"""
    return kindid in LINGSHI_KINDIDS


def is_pet_equip(kindid: int) -> bool:
    """判断是否为召唤兽装备"""
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

def get_equip_category_name(kindid: int) -> str:
    """获取装备分类名称"""
    for category, info in EQUIP_CATEGORIES.items():
        if kindid in info['kindids']:
            return info['name']
    return '未知' 

def is_helm(kindid: int) -> bool:
    """判断是否为头盔"""
    return kindid in HELMET_KINDIDS
