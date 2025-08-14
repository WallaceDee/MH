"""
灵饰属性优先级配置
用于判断不同属性之间的相似度，优先级相同的属性被认为是相似的
"""

# 戒指和耳饰属性优先级配置
RING_EARRING_PRIORITY = {
    # 物理系 - S级
    '伤害': 1,
    # 物理系 - A级
    '物理暴击等级': 2,
    # 物理系 - B级
    '穿刺等级': 3,
    # 物理系 - C级
    '狂暴等级': 4,
    
    # 法术系 - S级
    '法术伤害': 1,
    # 法术系 - A级
    '法术暴击等级': 2,
    # 法术系 - B级
    '法术伤害结果': 3,
    
    # 辅助系 - S级
    '固定伤害': 1,
    # 辅助系 - A级
    '治疗能力': 2,
    # 辅助系 - B级
    '速度': 3,
    # 辅助系 - C级
    '封印命中等级': 4,
}

# 手镯和配饰属性优先级配置
BRACELET_ACCESSORY_PRIORITY = {
    # S级
    '气血': 1,
    '防御': 1,
    # A级
    '抵抗封印等级': 2,
    '抗物理暴击': 2,
    # B级
    '格挡值': 3,
    '法术防御': 3,
    # C级
    '抗法术暴击': 4,
    '气血回复效果': 4,
}

def get_priority_by_attr_name(attr_name: str, equipment_type: str = None) -> int:
    """
    根据属性名称和装备类型获取优先级
    
    Args:
        attr_name: 属性名称
        equipment_type: 装备类型，可以是字符串或数字kindid(61,62,63,64)
    
    Returns:
        优先级数值，数值越小优先级越高，如果未找到则返回999
    """
    if equipment_type in [61, 62] or attr_name in RING_EARRING_PRIORITY:
        return RING_EARRING_PRIORITY.get(attr_name, 999)
    elif equipment_type in [63, 64] or attr_name in BRACELET_ACCESSORY_PRIORITY:
        return BRACELET_ACCESSORY_PRIORITY.get(attr_name, 999)
    else:
        # 如果都不匹配，返回999表示最低优先级
        return 999

def is_same_priority(attr1: str, attr2: str, equipment_type: str = None) -> bool:
    """
    判断两个属性是否具有相同的优先级
    
    Args:
        attr1: 第一个属性名称
        attr2: 第二个属性名称
        equipment_type: 装备类型，可以是字符串或数字kindid(61,62,63,64)
    
    Returns:
        如果两个属性优先级相同返回True，否则返回False
    """
    priority1 = get_priority_by_attr_name(attr1, equipment_type)
    priority2 = get_priority_by_attr_name(attr2, equipment_type)
    return priority1 == priority2 