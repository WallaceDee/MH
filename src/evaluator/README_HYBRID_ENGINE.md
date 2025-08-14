# 混合估价引擎 (Hybrid Valuation Engine)

## 概述

混合估价引擎是一个集成了市场锚定估价和规则估价的智能估价系统，专为梦幻西游角色价值评估设计。该引擎通过多种策略智能整合不同估价方法的结果，提供准确、可靠的角色价值估算。

## 系统架构

```
graph TD
    A[角色特征] --> B(市场锚定引擎)
    A --> C(规则引擎)
    B --> D{主估价}
    C --> E{辅助验证}
    D --> F[市场价值]
    E --> G[规则价值]
    F --> H{价值整合}
    G --> H
    H --> I[最终估价]
    H --> J[可信度报告]
    
    G --> K[异常检测]
    K --> B
    B --> L[特征校准]
    L --> C
```

## 核心组件

### 1. 特征提取和校准 (Feature Extraction & Calibration)
- **功能**: 从原始角色数据中提取标准化特征
- **校准**: 检测和修正异常数据值，确保特征一致性
- **实现**: `_extract_and_calibrate_features()`

### 2. 市场锚定引擎 (Market Anchor Engine)
- **功能**: 基于市场相似角色进行价值估算
- **优势**: 反映真实市场价格趋势
- **特点**: 动态权重调整、相似度智能匹配

### 3. 规则引擎 (Rule Engine)  
- **功能**: 基于游戏内价值规则进行估算
- **优势**: 稳定性高，不受市场波动影响
- **特点**: 价值分解详细、逻辑透明

### 4. 异常检测 (Anomaly Detection)
- **检测项**: 价格差异、置信度异常、数据完整性
- **阈值**: 可配置的多级检测阈值
- **响应**: 自动调整估价策略

### 5. 价值整合 (Value Integration)
- **策略**: 动态选择最优整合策略
- **权重**: 基于数据质量自动调整
- **输出**: 单一的最终估价值

## 整合策略

### 1. 市场主导策略 (Market Dominant)
- **触发条件**: 高市场置信度(>0.8) + 充足锚点(≥10)
- **权重**: 市场85% + 规则15%
- **适用**: 市场数据充足且可靠的情况

### 2. 规则主导策略 (Rule Dominant)
- **触发条件**: 低市场置信度(<0.3) 或 锚点不足(<3)
- **权重**: 市场20% + 规则80%
- **适用**: 市场数据稀少的情况

### 3. 平衡策略 (Balanced)
- **触发条件**: 中等市场数据质量
- **权重**: 市场70% + 规则30%
- **适用**: 标准估价情况

### 4. 异常保守策略 (Anomaly Conservative)
- **触发条件**: 检测到异常(异常分数>0.7)
- **策略**: 选择更保守的估价并打折(×0.8)
- **适用**: 数据异常时的风险控制

## 核心类和方法

### HybridValuationEngine

```python
class HybridValuationEngine:
    def __init__(self, market_evaluator=None, rule_evaluator=None)
    def evaluate(self, role_data) -> ValuationResult
    def batch_evaluate(self, role_list) -> List[ValuationResult]
    def generate_comprehensive_report(self, role_data) -> Dict
```

### ValuationResult

```python
@dataclass
class ValuationResult:
    market_value: float          # 市场锚定价值
    rule_value: float           # 规则引擎价值
    final_value: float          # 最终估价
    confidence: float           # 整体置信度
    integration_strategy: str   # 价值整合策略
    anomaly_score: float        # 异常分数
    anchor_count: int           # 市场锚点数量
    value_breakdown: Dict       # 价值分解
    warnings: List[str]         # 警告信息
```

## 使用示例

### 基本使用

```python
from evaluator.hybrid_valuation_engine import HybridValuationEngine

# 初始化引擎
engine = HybridValuationEngine()

# 准备角色数据
role_data = {
    'level': 129,
    'expt_ski1': 0,   # 攻击修炼
    'expt_ski2': 21,  # 防御修炼
    'expt_ski3': 21,  # 法术修炼
    'expt_ski4': 21,  # 抗法修炼
    'beast_ski1': 20, # 召唤兽攻击修炼
    'beast_ski2': 20, # 召唤兽防御修炼
    'beast_ski3': 20, # 召唤兽法术修炼
    'beast_ski4': 20, # 召唤兽抗法修炼
    'all_new_point': 8,  # 乾元丹
    'school_history_count': 3,
    # ... 其他特征
}

# 执行估价
result = engine.evaluate(role_data)

print(f"最终估价: {result.final_value:.1f}")
print(f"置信度: {result.confidence:.2%}")
print(f"策略: {result.integration_strategy}")
```

### 批量估价

```python
# 批量估价
role_list = [role_data1, role_data2, ...]
results = engine.batch_evaluate(role_list)

for i, result in enumerate(results):
    print(f"角色{i+1}: {result.final_value:.1f}")
```

### 生成综合报告

```python
# 生成详细报告
report = engine.generate_comprehensive_report(role_data)

# 访问报告内容
summary = report['evaluation_summary']
risk_assessment = report['risk_assessment']
recommendations = report['recommendations']
```

## 配置文件

### hybrid_config.jsonc
包含引擎的所有配置参数：
- 整合权重
- 置信度阈值  
- 异常检测参数
- 策略选择矩阵

### rate.jsonc
包含市场折价系数：
- 各类特征的市场流通性系数
- 用于调整理论价值到市场价值

## 质量保证

### 特征校准
- 修炼等级上限检查(≤100)
- 等级与修炼一致性验证
- 总值重新计算确保准确性

### 异常检测
1. **价值差异检测**: 市场价值与规则价值比值异常
2. **置信度检测**: 市场估价置信度过低
3. **数据完整性**: 关键特征缺失检测
4. **锚点数量**: 市场参考数据不足

### 置信度计算
```python
overall_confidence = (market_confidence + rule_confidence) / 2 - anomaly_penalty
```

## 优势特性

### 1. 智能策略选择
- 根据数据质量自动选择最优策略
- 动态权重调整机制
- 异常情况自动降级处理

### 2. 多维度价值分解
- 市场分析：价格范围、锚点分析
- 规则分析：详细价值构成
- 风险评估：数据质量评级

### 3. 鲁棒性设计
- 异常数据自动修正
- 缺失数据优雅处理
- 多重备用策略

### 4. 可解释性
- 详细的价值分解
- 策略选择理由
- 置信度计算过程

## 性能特点

- **准确性**: 多引擎互补，提高估价准确度
- **稳定性**: 异常检测和策略降级保证稳定输出
- **可靠性**: 置信度指标反映估价可信程度
- **透明性**: 完整的价值分解和策略解释

## 测试覆盖

### 测试场景
1. 高修炼角色（市场主导）
2. 低等级角色（规则主导）
3. 异常数据角色（校准+异常检测）
4. 完美角色（平衡策略）
5. 数据缺失角色（容错处理）

### 功能覆盖
- ✅ 多种整合策略
- ✅ 特征校准
- ✅ 异常检测
- ✅ 市场数据处理
- ✅ 批量处理
- ✅ 报告生成

## 扩展性

引擎设计具有良好的扩展性：
- 新的估价策略可以轻松集成
- 配置文件支持动态调整
- 模块化设计便于功能扩展
- 标准化接口支持新的特征类型

## 使用建议

1. **数据质量**: 确保输入数据的完整性和准确性
2. **配置调优**: 根据实际需求调整配置参数
3. **结果解读**: 结合置信度和警告信息理解估价结果
4. **策略理解**: 了解不同策略的适用场景
5. **异常处理**: 关注异常分数高的估价结果 