from typing import Dict, Any, List, Optional
from ..index import LingshiTypePlugin


class EarringPlugin(LingshiTypePlugin):
    """耳饰类灵饰插件"""
    
    @property
    def plugin_name(self) -> str:
        return "耳饰插件"
    
    @property
    def supported_kindids(self) -> List[int]:
        return [62]  # 耳饰
    
    @property
    def priority(self) -> int:
        return 10
    
    def get_weight_overrides(self) -> Dict[str, float]:
        """获取权重覆盖配置"""
        return {
            # 耳饰的主属性是法术伤害和法术防御
            'magic_damage': 4.0,    # 法术伤害权重很高
            'magic_defense': 4.0,   # 法术防御权重很高
            'attr_type': 3.0,       # 附加属性类型权重较高
            'attr_value': 3.0,      # 附加属性值权重较高
        }
    
    def get_tolerance_overrides(self) -> Dict[str, float]:
        """获取容忍度覆盖配置"""
        return {
            'magic_damage': 0.25,   # 法术伤害容忍度25%
            'magic_defense': 0.25,  # 法术防御容忍度25%
            'attr_type': 0.0,       # 附加属性类型必须完全一致
            'attr_value': 0.25,     # 附加属性值容忍度25%
        }
    
    def get_derived_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """计算派生特征"""
        derived = {}
        
        # 计算主属性总分
        magic_damage = features.get('magic_damage', 0)
        magic_defense = features.get('magic_defense', 0)
        derived['main_attr_total'] = magic_damage + magic_defense
        
        # 计算附加属性总分
        attr_values = features.get('attr_value', [])
        derived['addon_attr_total'] = sum(attr_values) if attr_values else 0
        
        return derived 