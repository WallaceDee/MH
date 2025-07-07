# 灵饰锚定评估系统

## 概述

灵饰锚定评估系统是一个基于市场数据的灵饰装备估价系统，通过相似度计算和锚点匹配来评估灵饰的市场价值。

## 系统架构

```
lingshi/
├── index.py                           # 主评估器
├── lingshi_market_data_collector.py   # 市场数据采集器
├── plugins/                           # 插件目录
│   ├── __init__.py
│   ├── ring_plugin.py                 # 戒指插件
│   ├── earring_plugin.py              # 耳饰插件
│   ├── bracelet_plugin.py             # 手镯插件
│   └── pendant_plugin.py              # 佩饰插件
├── example.py                         # 使用示例
└── README.md                          # 说明文档
```

## 核心组件

### 1. LingshiAnchorEvaluator (主评估器)
- 负责整体估价流程
- 管理插件系统
- 计算相似度和价值

### 2. LingshiMarketDataCollector (数据采集器)
- 从数据库获取市场数据
- 支持多种过滤条件
- 自动特征提取

### 3. 插件系统
- 支持不同灵饰类型的定制化配置
- 可扩展的权重和容忍度设置
- 自定义相似度计算

## 支持的灵饰类型

| 类型 | kindid | 主属性 | 插件 |
|------|--------|--------|------|
| 戒指 | 61 | 伤害/防御 | RingPlugin |
| 耳饰 | 62 | 法术伤害/法术防御 | EarringPlugin |
| 手镯 | 63 | 封印命中等级/抵抗封印等级 | BraceletPlugin |
| 佩饰 | 64 | 速度 | PendantPlugin |

## 特征体系

### 基础特征
- `equip_level`: 装备等级
- `gem_score`: 宝石得分
- `suit_effect_type`: 套装效果类型
- `suit_effect_level`: 套装效果等级
- `is_super_simple`: 是否超级简易
- `repair_fail_num`: 修理失败次数

### 主属性特征
- `damage`: 伤害 (戒指)
- `defense`: 防御 (戒指)
- `magic_damage`: 法术伤害 (耳饰)
- `magic_defense`: 法术防御 (耳饰)
- `seal_hit`: 封印命中等级 (手镯)
- `seal_resist`: 抵抗封印等级 (手镯)
- `speed`: 速度 (佩饰)

### 附加属性特征
- `attr_type`: 附加属性类型列表
- `attr_value`: 附加属性值列表

## 使用方法

### 基本使用

```python
from src.evaluator.mark_anchor.lingshi.index import LingshiAnchorEvaluator
from src.evaluator.mark_anchor.lingshi.plugins.ring_plugin import RingPlugin

# 创建评估器
evaluator = LingshiAnchorEvaluator()

# 注册插件
evaluator.add_plugin(RingPlugin())

# 准备灵饰数据
lingshi_data = {
    'kindid': 61,
    'equip_level': 100,
    'large_equip_desc': '等级 100#r伤害 +20#r耐久度 500#r#G伤害 +12#r#G法术伤害 +10#r#W制造者：测试强化打造#',
    'price': 50000,
    'server': '测试服务器'
}

# 提取特征
features = evaluator.market_data_collector.feature_extractor.extract_features(lingshi_data)
features.update(lingshi_data)

# 计算价值
result = evaluator.calculate_value(
    target_features=features,
    strategy='fair_value',
    similarity_threshold=0.7,
    max_anchors=30
)

print(f"估价结果: {result['value']:,} 金币")
print(f"置信度: {result['confidence']:.3f}")
```

### 批量估价

```python
# 批量估价
lingshi_list = [lingshi_data1, lingshi_data2, ...]
results = evaluator.batch_valuation(lingshi_list, strategy='fair_value')

for result in results:
    if result['success']:
        print(f"ID: {result['id']}, 价值: {result['value']:,} 金币")
    else:
        print(f"ID: {result['id']}, 估价失败: {result['message']}")
```

## 配置说明

### 权重配置
权重决定了各个特征在相似度计算中的重要性：

```python
# 基础权重配置
base_feature_weights = {
    'equip_level': 1.0,          # 装备等级
    'gem_score': 3.0,            # 宝石得分
    'suit_effect_type': 2.0,     # 套装效果类型
    'is_super_simple': 5.0,      # 超级简易
    # ... 其他特征
}
```

### 容忍度配置
容忍度决定了特征匹配的严格程度：

```python
# 基础容忍度配置
base_relative_tolerances = {
    'equip_level': 0.25,         # 装备等级容忍度25%
    'gem_score': 0.25,           # 宝石得分容忍度25%
    'suit_effect_type': 0.0,     # 套装效果类型必须完全一致
    # ... 其他特征
}
```

## 估价策略

系统支持三种估价策略：

1. **fair_value**: 加权中位数 (默认)
2. **min_value**: 最低价格
3. **max_value**: 最高价格

## 置信度计算

置信度基于以下因素计算：
- 锚点数量 (40%权重)
- 平均相似度 (60%权重)

## 扩展开发

### 添加新插件

1. 继承 `LingshiTypePlugin` 基类
2. 实现必要的抽象方法
3. 注册到评估器中

```python
class CustomPlugin(LingshiTypePlugin):
    @property
    def plugin_name(self) -> str:
        return "自定义插件"
    
    @property
    def supported_kindids(self) -> List[int]:
        return [65]  # 新的灵饰类型
    
    @property
    def priority(self) -> int:
        return 10
    
    def get_weight_overrides(self) -> Dict[str, float]:
        return {
            'custom_feature': 5.0
        }

# 注册插件
evaluator.add_plugin(CustomPlugin())
```

### 自定义相似度计算

```python
def calculate_custom_similarity(self, 
                               feature_name: str,
                               target_val: Any, 
                               market_val: Any) -> Optional[float]:
    if feature_name == 'custom_feature':
        # 自定义相似度计算逻辑
        return custom_similarity_calculation(target_val, market_val)
    return None
```

## 注意事项

1. **数据库依赖**: 系统需要灵饰市场数据数据库
2. **特征提取**: 确保 `large_equip_desc` 格式正确
3. **插件注册**: 使用前需要注册相应的插件
4. **参数调优**: 根据实际需求调整相似度阈值和锚点数量

## 示例运行

```bash
cd src/evaluator/mark_anchor/lingshi
python example.py
```

这将运行完整的使用示例，展示系统的各项功能。 