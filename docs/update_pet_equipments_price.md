# 召唤兽装备价格更新接口

## 功能概述

新增了召唤兽装备价格更新接口，根据召唤兽的 `pet_sn` 和年月自动获取装备信息进行批量估价，返回结果与 `/equipment/batch-valuation` 接口保持一致。

## API接口

### 召唤兽装备价格更新接口

**接口地址**: `POST /api/v1/pet/update-equipments-price`

**请求参数**:
```json
{
  "pet_sn": "召唤兽序列号",
  "year": 2024,
  "month": 12,
  "strategy": "fair_value",
  "similarity_threshold": 0.8,
  "max_anchors": 30
}
```

**参数说明**:
- `pet_sn`: 召唤兽的序列号（必填）
- `year`: 数据年份（必填）
- `month`: 数据月份（必填）
- `strategy`: 估价策略，可选值：`fair_value`、`competitive`、`premium`（默认：`fair_value`）
- `similarity_threshold`: 相似度阈值，范围0.0-1.0（默认：0.8）
- `max_anchors`: 最大锚点数量，范围1-100（默认：30）

**响应格式**:
```json
{
  "code": 200,
  "data": {
    "results": [
      {
        "index": 0,
        "equipment_data": {...},
        "estimated_price": 50000,
        "estimated_price_yuan": 500.00,
        "anchors_count": 15,
        "similarity_score": 0.85,
        "valuation_details": {...},
        "error": null
      }
    ],
    "total_estimated_price": 150000,
    "total_estimated_price_yuan": 1500.00,
    "equipment_count": 3,
    "successful_count": 3,
    "strategy": "fair_value",
    "similarity_threshold": 0.8,
    "max_anchors": 30,
    "pet_info": {
      "pet_sn": "123456789",
      "pet_name": "召唤兽名称",
      "level": 85,
      "year": 2024,
      "month": 12
    }
  },
  "message": "召唤兽装备价格更新完成"
}
```

## 前端使用

### 1. API调用

```javascript
import { petApi } from '@/api/pet'

// 调用召唤兽装备价格更新API
const response = await petApi.updatePetEquipmentsPrice({
  pet_sn: '123456789',
  year: 2024,
  month: 12,
  strategy: 'fair_value',
  similarity_threshold: 0.8,
  max_anchors: 30
})
```

### 2. 在召唤兽列表中使用

在 `PetList.vue` 中，装备估价按钮调用此接口：

```vue
<el-button 
  @click="updatePetEquipmentsPrice(scope.row.equip_sn)"
  :loading="equipmentValuationLoading">
  装备估价
</el-button>
```

### 3. 响应处理

```javascript
if (response.code === 200) {
  const data = response.data
  const results = data.results || []
  const totalValue = data.total_estimated_price || 0
  const petInfo = data.pet_info || {}

  // 显示估价结果
  // ...
}
```

## 后端实现

### 1. API端点

在 `src/app/blueprints/api/v1/pet.py` 中新增了 `update_pet_equipments_price` 端点：

```python
@pet_bp.route('/update-equipments-price', methods=['POST'])
def update_pet_equipments_price():
    """更新召唤兽装备价格"""
```

### 2. 数据流程

1. **接收参数**: 召唤兽序列号、年月和估价参数
2. **查询召唤兽详情**: 调用 `controller.get_pet_details()` 获取召唤兽完整信息
3. **提取装备列表**: 从召唤兽的 `equip_list` 字段中解析装备信息
4. **构建装备数据**: 将装备信息转换为装备控制器需要的格式
5. **调用批量估价**: 使用 `equipment_controller.batch_equipment_valuation()` 进行批量估价
6. **返回结果**: 添加召唤兽信息后返回与批量装备估价接口一致的响应

### 3. 实现细节

```python
# 1. 获取召唤兽详情
pet_details = controller.get_pet_details(pet_sn, int(year), int(month))

# 2. 从equip_list中提取装备信息
equip_list_json = pet_details.get('equip_list', '[]')
equip_list = json.loads(equip_list_json) if isinstance(equip_list_json, str) else equip_list_json

# 3. 构建装备数据列表
equipment_list = []
for equip_info in equip_list:
    if equip_info and equip_info.get('desc'):
        equipment_data = {
            'kindid': 29,  # 宠物装备的kindid
            'desc': equip_info.get('desc', ''),
            'equip_sn': f"pet_{pet_sn}_{len(equipment_list)}",
            'equip_name': equip_info.get('name', ''),
            'equip_type': equip_info.get('type', ''),
            'level': 0,
            'equip_level': 0
        }
        equipment_list.append(equipment_data)

# 4. 调用装备控制器的批量估价方法
result = equipment_controller.batch_equipment_valuation(
    equipment_list=equipment_list,
    strategy=strategy,
    similarity_threshold=similarity_threshold,
    max_anchors=max_anchors
)

# 5. 添加召唤兽信息到结果中
result["pet_info"] = {
    "pet_sn": pet_sn,
    "pet_name": pet_details.get('equip_name', ''),
    "level": pet_details.get('level', 0),
    "year": int(year),
    "month": int(month)
}
```

### 4. 与批量装备估价接口的一致性

该接口内部调用了装备服务的批量估价功能，确保返回结果与 `/equipment/batch-valuation` 接口完全一致：

- 相同的响应结构
- 相同的字段命名
- 相同的错误处理
- 额外的召唤兽信息字段

## 优势

1. **接口一致性**: 返回结果与批量装备估价接口完全一致
2. **简化调用**: 只需提供召唤兽序列号和年月，无需手动传入装备数据
3. **数据准确性**: 直接从数据库获取召唤兽的装备信息
4. **用户体验**: 前端操作更简单，一键完成装备估价

## 测试

可以使用提供的测试文件进行功能验证：

```bash
python tests/test_update_pet_equipments_price.py
```

## 注意事项

1. 确保召唤兽数据中包含装备信息
2. 年月参数必须与数据库中实际存在的数据对应
3. 如果召唤兽没有携带装备，会返回相应的提示信息
4. 装备估价结果依赖于市场数据的完整性和准确性
5. 返回结果结构与 `/equipment/batch-valuation` 接口保持一致 