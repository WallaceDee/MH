"""
无效物品判断规则配置

提供各种物品类型的无效判断规则配置，便于维护和调整
"""

from typing import Dict, Any, List


class InvalidItemConfig:
    """无效物品判断规则配置类"""
    
    def __init__(self):
        self._init_equipment_rules()
        self._init_pet_rules()
        self._init_lingshi_rules()
        self._init_pet_equip_rules()
        self._init_common_rules()
    
    def _init_equipment_rules(self):
        """初始化装备无效规则"""
        self.equipment_rules = {
            # 修理失败次数过多
            'max_repair_fail': 5,
            
            # 宝石等级过低（某些装备类型）
            'min_gem_level': 0,
            
            # 开孔数量为0（某些装备类型）
            'min_hole_count': 0,
            
            # 属性值过低阈值
            'min_attr_values': {
                'init_damage': 0,
                'init_damage_raw': 0,
                'all_damage': 0,
                'init_defense': 0,
                'init_hp': 0,
                'init_wakan': 0,
                'init_dex': 0,
                'mingzhong': 0,
                'shanghai': 0
            },
            
            # 特定装备类型的特殊规则
            'type_specific_rules': {
                # 武器类型
                'weapon': {
                    'min_init_damage': 10,  # 武器初伤不能太低
                    'min_hole_count': 1     # 武器至少要有1个孔
                },
                # 防具类型
                'armor': {
                    'min_init_defense': 5,  # 防具初防不能太低
                    'min_hole_count': 1     # 防具至少要有1个孔
                },
                # 饰品类型
                'accessory': {
                    'min_hole_count': 0     # 饰品可以没有孔
                }
            },
            
            # 高价值特效装备的最低要求
            'high_value_effect_min_requirements': {
                'simple_effect': {  # 简易特效
                    'min_levels': [70, 90, 110, 130],  # 只有这些等级才有价值
                    'min_gem_level': 3,                 # 至少3级宝石
                    'min_hole_count': 2                 # 至少2个孔
                },
                'no_level_limit': {  # 无级别限制
                    'min_gem_level': 5,                 # 至少5级宝石
                    'min_hole_count': 3                 # 至少3个孔
                },
                'anger': {          # 愤怒特效
                    'min_gem_level': 4,                 # 至少4级宝石
                    'min_hole_count': 2                 # 至少2个孔
                }
            }
        }
    
    def _init_pet_rules(self):
        """初始化召唤兽无效规则"""
        self.pet_rules = {
            # 等级过低
            'min_level': 0,
            
            # 技能数量过少
            'min_skill_count': 0,
            
            # 成长过低
            'min_growth': 0.0,
            
            # 资质过低
            'min_aptitude': {
                'attack': 0,
                'defense': 0,
                'hp': 0,
                'magic': 0,
                'speed': 0
            },
            
            # 特殊技能要求
            'required_skills': {
                'high_value': ['高级必杀', '高级连击', '高级偷袭', '高级夜战'],
                'medium_value': ['必杀', '连击', '偷袭', '夜战']
            },
            
            # 成长资质组合要求
            'growth_aptitude_combinations': {
                'excellent': {
                    'min_growth': 1.2,
                    'min_aptitude_sum': 1200
                },
                'good': {
                    'min_growth': 1.1,
                    'min_aptitude_sum': 1000
                },
                'acceptable': {
                    'min_growth': 1.0,
                    'min_aptitude_sum': 800
                }
            }
        }
    
    def _init_lingshi_rules(self):
        """初始化灵饰无效规则"""
        self.lingshi_rules = {
            # 主属性为0
            'min_main_attr': 0,
            
            # 附加属性数量过少
            'min_attr_count': 0,
            
            # 属性值过低
            'min_attr_value': 0,
            
            # 主属性类型要求
            'main_attr_types': ['damage', 'defense', 'magic_damage', 'magic_defense', 'fengyin', 'anti_fengyin', 'speed'],
            
            # 附加属性类型要求
            'addon_attr_types': ['addon_tizhi', 'addon_liliang', 'addon_naili', 'addon_minjie', 'addon_moli'],
            
            # 高价值灵饰要求
            'high_value_requirements': {
                'min_main_attr_value': 20,      # 主属性至少20
                'min_addon_attr_count': 2,      # 至少2个附加属性
                'min_addon_attr_value': 8       # 附加属性至少8
            }
        }
    
    def _init_pet_equip_rules(self):
        """初始化宠物装备无效规则"""
        self.pet_equip_rules = {
            # 属性值过低
            'min_attr_values': {
                'shanghai': 0,
                'fangyu': 0,
                'speed': 0
            },
            
            # 属性组合要求
            'attr_combination_requirements': {
                'min_total_attr': 15,           # 总属性至少15
                'min_attr_count': 2,            # 至少2个属性
                'min_attr_value': 5             # 单个属性至少5
            },
            
            # 高价值宠物装备要求
            'high_value_requirements': {
                'min_total_attr': 25,           # 总属性至少25
                'min_attr_count': 3,            # 至少3个属性
                'min_attr_value': 8             # 单个属性至少8
            }
        }
    
    def _init_common_rules(self):
        """初始化通用规则"""
        self.common_rules = {
            # 价格相关规则
            'price_rules': {
                'min_price': 0,                # 最低价格
                'max_price': 10000000,         # 最高价格（防止异常值）
                'suspicious_price_threshold': 1000000  # 可疑价格阈值
            },
            
            # 数据完整性检查
            'data_integrity': {
                'required_fields': ['name', 'kindid'],  # 必需字段
                'optional_fields': ['equip_sn', 'price', 'level']  # 可选字段
            }
        }
    
    def get_equipment_rules(self) -> Dict[str, Any]:
        """获取装备无效规则"""
        return self.equipment_rules
    
    def get_pet_rules(self) -> Dict[str, Any]:
        """获取召唤兽无效规则"""
        return self.pet_rules
    
    def get_lingshi_rules(self) -> Dict[str, Any]:
        """获取灵饰无效规则"""
        return self.lingshi_rules
    
    def get_pet_equip_rules(self) -> Dict[str, Any]:
        """获取宠物装备无效规则"""
        return self.pet_equip_rules
    
    def get_common_rules(self) -> Dict[str, Any]:
        """获取通用规则"""
        return self.common_rules
    
    def update_rule(self, rule_type: str, rule_name: str, new_value: Any):
        """
        更新规则值
        
        Args:
            rule_type: 规则类型 ('equipment', 'pet', 'lingshi', 'pet_equip', 'common')
            rule_name: 规则名称
            new_value: 新值
        """
        try:
            if rule_type == 'equipment':
                self._update_nested_dict(self.equipment_rules, rule_name, new_value)
            elif rule_type == 'pet':
                self._update_nested_dict(self.pet_rules, rule_name, new_value)
            elif rule_type == 'lingshi':
                self._update_nested_dict(self.lingshi_rules, rule_name, new_value)
            elif rule_type == 'pet_equip':
                self._update_nested_dict(self.pet_equip_rules, rule_name, new_value)
            elif rule_type == 'common':
                self._update_nested_dict(self.common_rules, rule_name, new_value)
            else:
                raise ValueError(f"不支持的规则类型: {rule_type}")
        except Exception as e:
            raise ValueError(f"更新规则失败: {e}")
    
    def _update_nested_dict(self, target_dict: Dict[str, Any], rule_name: str, new_value: Any):
        """更新嵌套字典中的规则值"""
        if '.' in rule_name:
            # 处理嵌套规则，如 'type_specific_rules.weapon.min_init_damage'
            keys = rule_name.split('.')
            current_dict = target_dict
            
            for key in keys[:-1]:
                if key not in current_dict:
                    current_dict[key] = {}
                current_dict = current_dict[key]
            
            current_dict[keys[-1]] = new_value
        else:
            # 直接更新
            target_dict[rule_name] = new_value
    
    def get_rule_value(self, rule_type: str, rule_name: str) -> Any:
        """
        获取规则值
        
        Args:
            rule_type: 规则类型
            rule_name: 规则名称
            
        Returns:
            规则值
        """
        try:
            if rule_type == 'equipment':
                return self._get_nested_dict_value(self.equipment_rules, rule_name)
            elif rule_type == 'pet':
                return self._get_nested_dict_value(self.pet_rules, rule_name)
            elif rule_type == 'lingshi':
                return self._get_nested_dict_value(self.lingshi_rules, rule_name)
            elif rule_type == 'pet_equip':
                return self._get_nested_dict_value(self.pet_equip_rules, rule_name)
            elif rule_type == 'common':
                return self._get_nested_dict_value(self.common_rules, rule_name)
            else:
                raise ValueError(f"不支持的规则类型: {rule_type}")
        except Exception as e:
            raise ValueError(f"获取规则值失败: {e}")
    
    def _get_nested_dict_value(self, target_dict: Dict[str, Any], rule_name: str) -> Any:
        """获取嵌套字典中的规则值"""
        if '.' in rule_name:
            keys = rule_name.split('.')
            current_dict = target_dict
            
            for key in keys:
                if key not in current_dict:
                    return None
                current_dict = current_dict[key]
            
            return current_dict
        else:
            return target_dict.get(rule_name) 