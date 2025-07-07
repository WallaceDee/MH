from typing import Dict, Any, List, Optional
from ..index import LingshiTypePlugin


class BraceletPlugin(LingshiTypePlugin):
    """手镯类灵饰插件"""
    
    @property
    def plugin_name(self) -> str:
        return "手镯插件"
    
    @property
    def supported_kindids(self) -> List[int]:
        return [63]  # 手镯
    
    @property
    def priority(self) -> int:
        return 10
    
    def get_weight_overrides(self) -> Dict[str, float]:
        """获取权重覆盖配置"""
        return {
            # 手镯的主属性是封印命中等级和抵抗封印等级
            'seal_hit': 4.0,        # 封印命中等级权重很高
            'seal_resist': 4.0,     # 抵抗封印等级权重很高
            'attr_type': 3.0,       # 附加属性类型权重较高
            'attr_value': 3.0,      # 附加属性值权重较高
        }
    
    def get_tolerance_overrides(self) -> Dict[str, float]:
        """获取容忍度覆盖配置"""
        return {
            'seal_hit': 0.25,       # 封印命中等级容忍度25%
            'seal_resist': 0.25,    # 抵抗封印等级容忍度25%
            'attr_type': 0.0,       # 附加属性类型必须完全一致
            'attr_value': 0.25,     # 附加属性值容忍度25%
        }
    
    def get_derived_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """计算派生特征"""
        derived = {}
        
        # 计算主属性总分
        seal_hit = features.get('seal_hit', 0)
        seal_resist = features.get('seal_resist', 0)
        derived['main_attr_total'] = seal_hit + seal_resist
        
        # 计算附加属性总分
        attr_values = features.get('attr_value', [])
        derived['addon_attr_total'] = sum(attr_values) if attr_values else 0
        
        return derived 