from typing import Dict, Any, List, Optional
from ..index import LingshiTypePlugin


class PendantPlugin(LingshiTypePlugin):
    """佩饰类灵饰插件"""
    
    @property
    def plugin_name(self) -> str:
        return "佩饰插件"
    
    @property
    def supported_kindids(self) -> List[int]:
        return [64]  # 佩饰
    
    @property
    def priority(self) -> int:
        return 10
    
    def get_weight_overrides(self) -> Dict[str, float]:
        """获取权重覆盖配置"""
        return {
            # 佩饰的主属性是速度
            'speed': 4.0,           # 速度权重很高
            'attr_type': 3.0,       # 附加属性类型权重较高
            'attr_value': 3.0,      # 附加属性值权重较高
        }
    
    def get_tolerance_overrides(self) -> Dict[str, float]:
        """获取容忍度覆盖配置"""
        return {
            'speed': 0.25,          # 速度容忍度25%
            'attr_type': 0.0,       # 附加属性类型必须完全一致
            'attr_value': 0.25,     # 附加属性值容忍度25%
        }
    
    def get_derived_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """计算派生特征"""
        derived = {}
        
        # 计算主属性总分
        speed = features.get('speed', 0)
        derived['main_attr_total'] = speed
        
        # 计算附加属性总分
        attr_values = features.get('attr_value', [])
        derived['addon_attr_total'] = sum(attr_values) if attr_values else 0
        
        return derived 