"""
装备类型插件包

这个包包含了各种装备类型的专用插件，用于实现差异化的装备估价逻辑。

插件结构：
- weapons_plugin.py: 武器插件
- shoes_plugin.py: 鞋子插件
- necklace_plugin.py: 项链插件  
- belt_plugin.py: 腰带插件
- lingshi_plugin.py: 灵饰插件

使用方法：
```python
from src.evaluator.mark_anchor.equip.plugins import get_all_plugins
from src.evaluator.mark_anchor.equip.index import EquipAnchorEvaluator

# 获取所有插件
plugins = get_all_plugins()

# 添加到估价器
evaluator = EquipAnchorEvaluator()
for plugin in plugins:
    evaluator.add_plugin(plugin)
```
"""

import os
import sys
import importlib
from typing import List, Type
from abc import ABC, abstractmethod

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))))
sys.path.insert(0, project_root)

from src.evaluator.mark_anchor.equip.index import EquipmentTypePlugin


def get_all_plugins() -> List[EquipmentTypePlugin]:
    """
    自动发现并返回所有可用的装备类型插件
    
    Returns:
        List[EquipmentTypePlugin]: 所有可用插件的实例列表
    """
    plugins = []
    
    # 导入所有插件模块
    try:
        # 头盔插件
        from .helmet_plugin import HelmetPlugin
        plugins.append(HelmetPlugin())
        
        # 鞋子插件
        from .shoes_plugin import ShoesPlugin
        plugins.append(ShoesPlugin())

        # 项链插件
        from .necklace_plugin import NecklacePlugin
        plugins.append(NecklacePlugin())

        # 腰带插件
        from .belt_plugin import BeltPlugin
        plugins.append(BeltPlugin())

         # 武器插件
        from .weapon_plugin import WeaponPlugin
        plugins.append(WeaponPlugin())

        # 衣服插件
        from .armor_plugin import ArmorPlugin
        plugins.append(ArmorPlugin())

        # 灵饰插件
        from .lingshi_plugin import LingshiPlugin
        plugins.append(LingshiPlugin())

        # 召唤兽装备插件
        from .pet_equip_plugin import PetEquipPlugin
        plugins.append(PetEquipPlugin())
        
        print(f"已自动加载 {len(plugins)} 个装备类型插件")
        
    except ImportError as e:
        print(f"插件加载警告: {e}")
        print("部分插件可能尚未实现")
    
    return plugins


def get_plugins_by_category(category: str) -> List[EquipmentTypePlugin]:
    """
    根据装备类别获取插件
    
    Args:
        category: 装备类别 ('weapons', 'armors', 'accessories', 'lingshi')
        
    Returns:
        List[EquipmentTypePlugin]: 该类别的插件列表
    """
    all_plugins = get_all_plugins()
    
    category_kindids = {
        'weapons': [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 52, 53, 54, 72, 73, 74],
        'armors': [17, 18, 59],
        'accessories': [19, 20, 21, 58],
        'lingshi': [61, 62, 63, 64]
    }
    
    target_kindids = set(category_kindids.get(category, []))
    
    filtered_plugins = []
    for plugin in all_plugins:
        plugin_kindids = set(plugin.supported_kindids)
        if plugin_kindids & target_kindids:  # 有交集
            filtered_plugins.append(plugin)
    
    return filtered_plugins 