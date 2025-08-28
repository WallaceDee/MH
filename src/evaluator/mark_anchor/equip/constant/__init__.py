"""
装备估价系统常量配置模块
"""

import json
import os
from typing import Dict, Any, List

def _load_config(filename: str) -> Dict[str, Any]:
    """加载配置文件"""
    config_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(config_dir, filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        # 移除注释行
        lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('//')]
        content = '\n'.join(lines)
        return json.loads(content)

def get_config() -> Dict[str, Any]:
    """获取主配置"""
    return _load_config('config.jsonc')

def get_weapon_config() -> Dict[str, Any]:
    """获取武器配置"""
    return _load_config('weapon.jsonc')

def get_lingshi_config() -> Dict[str, Any]:
    """获取灵石配置"""
    return _load_config('lingshi.jsonc')

def get_jade_config() -> Dict[str, Any]:
    """获取玉佩配置"""
    return _load_config('jade.jsonc')

def get_pet_equip_config() -> Dict[str, Any]:
    """获取宠物装备配置"""
    return _load_config('pet_equip.jsonc')

# 便捷访问函数
def get_agility_suits() -> List[int]:
    """获取敏捷套装ID列表"""
    config = get_config()
    return config['suits']['agility']

def get_magic_suits() -> List[int]:
    """获取魔力套装ID列表"""
    config = get_config()
    return config['suits']['magic']

def get_high_value_suits() -> List[int]:
    """获取高价值套装ID列表"""
    config = get_config()
    return config['suits']['high_value']

def get_precise_filter_suits() -> List[int]:
    """获取精确筛选套装ID列表"""
    config = get_config()
    return config['suits']['precise_filter']

def get_agility_suits_detailed() -> Dict[str, List[int]]:
    """获取敏捷套装详细分类"""
    config = get_config()
    return config['suits']['agility_detailed']

def get_magic_suits_detailed() -> Dict[str, List[int]]:
    """获取魔力套装详细分类"""
    config = get_config()
    return config['suits']['magic_detailed']

def get_agility_suits_b() -> List[int]:
    """获取B级敏捷套装ID列表"""
    config = get_config()
    return config['suits']['agility_detailed']['B']

def get_agility_suits_a() -> List[int]:
    """获取A级敏捷套装ID列表"""
    config = get_config()
    return config['suits']['agility_detailed']['A']

def get_magic_suits_b() -> List[int]:
    """获取B级魔力套装ID列表"""
    config = get_config()
    return config['suits']['magic_detailed']['B']

def get_magic_suits_a() -> List[int]:
    """获取A级魔力套装ID列表"""
    config = get_config()
    return config['suits']['magic_detailed']['A']

def get_high_value_effects() -> List[int]:
    """获取高价值特效ID列表"""
    config = get_config()
    return config['effects']['high_value']

def get_important_effects() -> List[int]:
    """获取重要特效ID列表"""
    config = get_config()
    return config['effects']['important']

def get_low_value_effects() -> List[int]:
    """获取低价值特效ID列表"""
    config = get_config()
    return config['effects']['low_value']

def get_high_value_simple_levels() -> List[int]:
    """获取高价值简易装备等级列表"""
    config = get_config()
    return config['equipment']['high_value_simple_levels']

def get_low_value_special_skills() -> List[int]:
    """获取低价值特技ID列表"""
    config = get_config()
    return config['equipment']['low_value_special_skills']

def get_simple_effect_id() -> int:
    """获取简易装备特效编号"""
    config = get_config()
    return config['effects']['simple'] 