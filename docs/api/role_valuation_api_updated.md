# 角色估价API文档（更新版）

## 概述

角色估价API提供了基于市场锚定和规则引擎的混合估价功能，支持单个角色估价和批量角色估价。**更新后接口不再需要前端传递角色数据，只需提供年、月、eid等参数，后端自动查询对应的角色数据进行估价。**

## API接口

### 1. 单个角色估价

**接口地址**: `POST /api/v1/role/valuation`

**功能描述**: 对单个角色进行估价，后端根据eid查询角色数据

**请求参数**:
```json
{
    "eid": "role_123",                    // 角色唯一标识符（必需）
    "year": 2025,                         // 年份（可选，默认当前年）
    "month": 1,                           // 月份（可选，默认当前月）
    "role_type": "normal",                // 角色类型（可选，默认normal）
    "strategy": "fair_value",             // 估价策略（可选，默认fair_value）
    "similarity_threshold": 0.7,          // 相似度阈值（可选，默认0.7）
    "max_anchors": 30                     // 最大锚点数量（可选，默认30）
}
```

**响应示例**:
```json
{
    "code": 200,
    "data": {
        "estimated_price": 50000,           // 估价价格（分）
        "estimated_price_yuan": 500.0,     // 估价价格（元）
        "confidence": 0.85,                // 置信度
        "market_value": 48000,             // 市场估价
        "rule_value": 52000,               // 规则估价
        "integration_strategy": "hybrid",  // 整合策略
        "anomaly_score": 0.1,              // 异常分数
        "anchor_count": 25,                // 锚点数量
        "value_breakdown": {               // 价值分解
            "base_value": 30000,
            "skill_value": 15000,
            "equipment_value": 5000
        },
        "warnings": [],                    // 警告信息
        "feature": {...},                  // 角色特征
        "role_data": {...},                // 角色原始数据
        "eid": "role_123",                 // 角色eid
        "strategy": "fair_value",
        "similarity_threshold": 0.7,
        "max_anchors": 30
    },
    "message": "获取角色估价成功",
    "timestamp": 1234567890
}
```

### 2. 批量角色估价

**接口地址**: `POST /api/v1/role/batch-valuation`

**功能描述**: 对多个角色进行批量估价，后端根据eid列表查询角色数据

**请求参数**:
```json
{
    "eid_list": [                          // 角色eid列表（必需）
        "role_123",
        "role_456",
        "role_789"
    ],
    "year": 2025,                          // 年份（可选，默认当前年）
    "month": 1,                            // 月份（可选，默认当前月）
    "role_type": "normal",                 // 角色类型（可选，默认normal）
    "strategy": "fair_value",              // 估价策略（可选，默认fair_value）
    "similarity_threshold": 0.7,           // 相似度阈值（可选，默认0.7）
    "max_anchors": 30,                     // 最大锚点数量（可选，默认30）
    "verbose": true                         // 是否详细日志（可选，默认false）
}
```

**响应示例**:
```json
{
    "code": 200,
    "data": {
        "total_roles": 3,                  // 总角色数
        "success_count": 3,                 // 成功估价数
        "error_count": 0,                   // 失败估价数
        "total_value": 150000,             // 总价值（分）
        "total_value_yuan": 1500.0,        // 总价值（元）
        "strategy": "fair_value",
        "similarity_threshold": 0.7,
        "max_anchors": 30,
        "results": [
            {
                "index": 0,
                "eid": "role_123",
                "success": true,
                "data": {
                    "estimated_price": 50000,
                    "estimated_price_yuan": 500.0,
                    // ... 其他估价结果
                }
            },
            {
                "index": 1,
                "eid": "role_456",
                "success": true,
                "data": {
                    "estimated_price": 50000,
                    "estimated_price_yuan": 500.0,
                    // ... 其他估价结果
                }
            },
            {
                "index": 2,
                "eid": "role_789",
                "success": true,
                "data": {
                    "estimated_price": 50000,
                    "estimated_price_yuan": 500.0,
                    // ... 其他估价结果
                }
            }
        ]
    },
    "message": "批量角色估价完成",
    "timestamp": 1234567890
}
```

### 3. 通过eid获取估价（便捷接口）

**接口地址**: `GET /api/v1/role/valuation/{eid}`

**功能描述**: 通过角色eid直接获取估价，无需提供角色数据

**请求参数**:
- `eid`: 角色唯一标识符（路径参数）
- `year`: 年份（查询参数，可选）
- `month`: 月份（查询参数，可选）
- `role_type`: 角色类型（查询参数，可选，默认normal）
- `strategy`: 估价策略（查询参数，可选，默认fair_value）
- `similarity_threshold`: 相似度阈值（查询参数，可选，默认0.7）
- `max_anchors`: 最大锚点数量（查询参数，可选，默认30）

**响应格式**: 与单个角色估价接口相同

## 主要更新内容

### 1. 接口参数简化
- **之前**: 需要前端传递完整的角色数据 `role_data`
- **现在**: 只需传递 `eid`、`year`、`month` 等参数
- **优势**: 简化前端调用，减少数据传输，提高接口易用性

### 2. 后端数据查询
- 后端根据 `eid`、`year`、`month`、`role_type` 自动查询角色数据
- 支持按年月查询不同时期的角色数据
- 支持查询不同类型的角色（normal、empty等）

### 3. 返回数据增强
- 返回结果中包含 `role_data` 字段，提供完整的角色原始数据
- 返回结果中包含 `eid` 字段，便于前端识别
- 批量估价结果中每个项目都包含对应的 `eid`

## 使用方式

### Python示例
```python
import requests

# 单个角色估价
response = requests.post(
    "http://localhost:5000/api/v1/role/valuation",
    json={
        "eid": "role_123",
        "year": 2025,
        "month": 1,
        "strategy": "fair_value",
        "similarity_threshold": 0.7,
        "max_anchors": 30
    }
)

if response.status_code == 200:
    result = response.json()
    estimated_price = result['data']['estimated_price_yuan']
    print(f"角色估价: {estimated_price}元")
```

### JavaScript示例
```javascript
// 批量角色估价
const response = await fetch('/api/v1/role/batch-valuation', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        eid_list: ['role_123', 'role_456', 'role_789'],
        year: 2025,
        month: 1,
        strategy: 'fair_value',
        similarity_threshold: 0.7,
        max_anchors: 30
    })
});

const result = await response.json();
if (result.code === 200) {
    const totalValue = result.data.total_value_yuan;
    console.log(`总价值: ${totalValue}元`);
}
```

## 参数说明

### 必需参数
- **eid**: 角色唯一标识符，用于查询角色数据

### 可选参数
- **year**: 年份，用于查询指定年份的角色数据
- **month**: 月份，用于查询指定月份的角色数据
- **role_type**: 角色类型，支持 'normal'（正常角色）和 'empty'（空号角色）
- **strategy**: 估价策略，支持 'fair_value'、'competitive'、'premium'
- **similarity_threshold**: 相似度阈值，范围 0.0-1.0
- **max_anchors**: 最大锚点数量，范围 1-100

## 错误处理

### 常见错误情况
1. **角色不存在**: 当提供的eid在数据库中找不到对应角色时
2. **数据文件不存在**: 当指定的年月数据文件不存在时
3. **估价引擎未初始化**: 当估价相关组件未正确初始化时
4. **参数验证失败**: 当传递的参数不符合要求时

### 错误响应示例
```json
{
    "code": 400,
    "data": {
        "error": "未找到角色 role_123 的数据",
        "estimated_price": 0,
        "estimated_price_yuan": 0
    },
    "message": "未找到角色 role_123 的数据",
    "timestamp": 1234567890
}
```

## 注意事项

1. **数据完整性**: 确保数据库中已存在对应的角色数据
2. **年月参数**: 如果不提供年月参数，系统会使用当前年月
3. **角色类型**: 根据实际需要选择正确的角色类型
4. **批量处理**: 建议单次批量处理不超过100个角色，避免超时
5. **错误处理**: 建议实现重试机制，处理网络异常和服务器错误

## 更新日志

- **v1.1.0**: 接口参数简化，改为接收eid、年、月等参数
- **v1.0.0**: 初始版本，支持基本的角色估价功能
