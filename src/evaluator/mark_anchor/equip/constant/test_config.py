#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试配置文件加载
"""

from . import (
    get_agility_suits, get_magic_suits, get_high_value_suits,
    get_precise_filter_suits, get_high_value_effects, get_important_effects,
    get_low_value_effects, get_high_value_simple_levels,
    get_low_value_special_skills, get_simple_effect_id, get_config,
    get_weapon_config, get_lingshi_config, get_jade_config, get_pet_equip_config,
    get_agility_suits_detailed, get_magic_suits_detailed,
    get_agility_suits_b, get_agility_suits_a, get_magic_suits_b, get_magic_suits_a
)

def test_config_loading():
    """测试配置加载"""
    print("测试主配置:")
    print(f"敏捷套装: {get_agility_suits()}")
    print(f"魔力套装: {get_magic_suits()}")
    print(f"高价值套装: {get_high_value_suits()}")
    print(f"精确筛选套装: {get_precise_filter_suits()}")
    
    print("\n测试敏捷套详细分类:")
    agility_detailed = get_agility_suits_detailed()
    print(f"敏捷套详细分类: {agility_detailed}")
    print(f"B级敏捷套: {get_agility_suits_b()}")
    print(f"A级敏捷套: {get_agility_suits_a()}")
    
    print("\n测试魔力套详细分类:")
    magic_detailed = get_magic_suits_detailed()
    print(f"魔力套详细分类: {magic_detailed}")
    print(f"B级魔力套: {get_magic_suits_b()}")
    print(f"A级魔力套: {get_magic_suits_a()}")
    
    print("\n测试特效配置:")
    print(f"高价值特效: {get_high_value_effects()}")
    print(f"重要特效: {get_important_effects()}")
    print(f"低价值特效: {get_low_value_effects()}")
    print(f"简易特效ID: {get_simple_effect_id()}")
    
    print("\n测试装备配置:")
    print(f"高价值简易等级: {get_high_value_simple_levels()}")
    print(f"低价值特技: {get_low_value_special_skills()}")
    
    print("\n测试武器配置:")
    weapon_config = get_weapon_config()
    print(f"武器配置键: {list(weapon_config.keys())}")
    print(f"60级初始伤害标准: {weapon_config.get('init_damage_raw_standards', {}).get('60', [])}")
    
    print("\n测试灵石配置:")
    lingshi_config = get_lingshi_config()
    print(f"灵石配置等级: {list(lingshi_config.keys())}")
    print(f"60级主属性: {list(lingshi_config.get('60', {}).get('main', {}).keys())}")
    
    print("\n测试玉佩配置:")
    jade_config = get_jade_config()
    print(f"玉佩配置类型: {list(jade_config.keys())}")
    print(f"类型0主属性: {list(jade_config.get('0', {}).get('main', {}).keys())}")
    
    print("\n测试召唤兽装备配置:")
    pet_config = get_pet_equip_config()
    print(f"召唤兽装备等级: {list(pet_config.keys())}")
    print(f"65级属性: {list(pet_config.get('65', {}).keys())}")

if __name__ == "__main__":
    test_config_loading() 