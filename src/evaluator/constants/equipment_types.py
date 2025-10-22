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


# 装备数据缓存需要的字段列表
# 用于特征提取和估价系统，避免传输不必要的数据
EQUIPMENT_CACHE_REQUIRED_FIELDS = [
    # 基础装备属性
    'equip_level', 'kindid', 'init_damage', 'init_damage_raw',
    'all_damage', 'init_wakan', 'init_defense', 'init_hp',
    'init_dex', 'mingzhong', 'shanghai', 'addon_tizhi',
    'addon_liliang', 'addon_naili', 'addon_minjie', 'addon_lingli',
    'addon_moli', 'agg_added_attrs', 'gem_value', 'gem_level',
    'special_skill', 'special_effect', 'suit_effect', 'large_equip_desc',
    # 灵饰特征提取器需要的字段
    'damage', 'defense', 'magic_damage', 'magic_defense',
    'fengyin', 'anti_fengyin', 'speed',
    # 召唤兽装备特征提取器需要的字段
    'fangyu', 'qixue', 'addon_fali', 'xiang_qian_level', 'addon_status',
    # 基础字段
    'equip_sn', 'price', 'server_name', 'update_time'
]

# 召唤兽数据缓存需要的字段列表
# 用于特征提取和估价系统，避免传输不必要的数据
PET_CACHE_REQUIRED_FIELDS = [
    # 基础召唤兽属性
    'equip_sn', 'eid', 'equip_name', 'level', 'kindid', 'price', 'server_name',
    'update_time', 'desc', 'desc_sumup_short', 'large_equip_desc',
    
    # 解析出的召唤兽属性（核心估价字段）
    'pet_name', 'type_id', 'pet_grade', 'blood', 'magic', 'attack', 'defence',
    'speed', 'soma', 'magic_powner', 'strength', 'endurance', 'smartness',
    'potential', 'wakan', 'max_blood', 'max_magic', 'lifetime', 'five_aptitude',
    
    # 资质相关
    'attack_aptitude', 'defence_aptitude', 'physical_aptitude', 'magic_aptitude',
    'speed_aptitude', 'avoid_aptitude', 'growth',
    
    # 技能相关
    'all_skill', 'sp_skill', 'all_skills', 'sp_skill_id', 'evol_skill_list',
    'evol_skills',
    
    # 进阶和特性
    'is_baobao', 'jinjie', 'lx', 'jinjie_cnt', 'texing', 'core_close',
    
    # 加点相关
    'ti_zhi_add', 'fa_li_add', 'li_liang_add', 'nai_li_add', 'min_jie_add',
    
    # 扩展属性
    'attack_ext', 'defence_ext', 'speed_ext', 'avoid_ext', 'physical_ext', 'magic_ext',
    
    # 其他重要属性
    'neidan', 'equip_list', 'color', 'summon_color', 'iMagDam', 'iMagDef',
    'used_sjg', 'used_yuanxiao', 'used_lianshou', 'used_qianjinlu', 'other',
    
    # 装备估价相关
    'equip_list_amount', 'equip_list_amount_warning'
]