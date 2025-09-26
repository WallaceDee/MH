# 装备数据保存流程指南

## 概述

装备数据保存流程已优化为：**内存缓存 → MySQL → Redis** 的三层存储架构，确保数据在三个存储层都保持一致。

## 新的保存流程

### 流程图

```
新装备数据
    ↓
┌─────────────────┐
│   内存缓存      │ ← 第一步：添加到EquipMarketDataCollector
│ (_full_data_cache) │
└─────────────────┘
    ↓
┌─────────────────┐
│   MySQL数据库   │ ← 第二步：保存到数据库
│   (equipment表)  │
└─────────────────┘
    ↓
┌─────────────────┐
│   Redis缓存     │ ← 第三步：同步内存缓存到Redis
│ (分块存储)      │
└─────────────────┘
```

### 详细步骤

#### 第一步：添加到内存缓存
```python
# 获取EquipMarketDataCollector实例
collector = EquipMarketDataCollector.get_instance()

# 添加数据到内存缓存
cache_success = collector.add_new_equipment_data(equipments)
```

**功能**：
- 将新装备数据添加到 `_full_data_cache` 内存缓存
- 如果内存缓存为空，直接使用新数据
- 如果内存缓存不为空，合并新数据和现有数据
- 使用 `equip_sn` 作为主键进行去重

#### 第二步：保存到MySQL数据库
```python
# 检查是否已存在相同的装备
existing = db.session.query(Equipment).filter_by(equip_sn=equip_sn).first()

if existing:
    # 更新现有记录
    for key, value in equipment_data.items():
        if hasattr(existing, key):
            setattr(existing, key, value)
    existing.update_time = datetime.now()
else:
    # 创建新记录
    equipment = Equipment(**equipment_data)
    db.session.add(equipment)

# 提交事务
db.session.commit()
```

**功能**：
- 检查装备是否已存在（基于 `equip_sn`）
- 如果存在，更新现有记录
- 如果不存在，创建新记录
- 提交事务到MySQL数据库

#### 第三步：同步到Redis缓存
```python
# 获取当前内存缓存数据
memory_data = collector._get_existing_data_from_memory()

if memory_data is not None and not memory_data.empty:
    # 同步到Redis
    redis_success = collector._sync_memory_cache_to_redis(memory_data)
```

**功能**：
- 获取更新后的内存缓存数据
- 将内存缓存数据同步到Redis
- 更新Redis中的分块数据
- 更新缓存元数据

## 核心方法

### EquipMarketDataCollector.add_new_equipment_data()

```python
def add_new_equipment_data(self, new_equipments: List[Dict[str, Any]]) -> bool:
    """
    添加新的装备数据到内存缓存
    
    Args:
        new_equipments: 新的装备数据列表
        
    Returns:
        bool: 是否添加成功
    """
```

**功能**：
- 将新装备数据转换为DataFrame
- 与现有内存缓存数据合并
- 更新 `_full_data_cache` 内存缓存
- 处理数据去重和合并逻辑

### CBGEquipSpider._save_equipment_data_with_context()

```python
def _save_equipment_data_with_context(self, equipments):
    """在Flask应用上下文中保存装备数据 - 内存缓存 → MySQL → Redis"""
```

**功能**：
- 实现完整的三层保存流程
- 处理错误和异常情况
- 提供详细的日志记录
- 确保数据一致性

## 错误处理

### 容错机制

1. **内存缓存失败**：继续保存到MySQL，记录警告日志
2. **MySQL保存失败**：回滚事务，记录错误日志
3. **Redis同步失败**：记录警告日志，不影响整体流程

### 日志记录

```python
# 成功日志
self.logger.info("✅ 装备数据已添加到内存缓存")
self.logger.info("✅ 成功保存 X 条新装备数据到MySQL数据库")
self.logger.info("✅ 内存缓存已同步到Redis")

# 警告日志
self.logger.warning("⚠️ 装备数据添加到内存缓存失败，继续保存到MySQL")
self.logger.warning("⚠️ 内存缓存同步到Redis失败")

# 错误日志
self.logger.error("保存装备数据到MySQL数据库失败: {e}")
```

## 性能优势

### 1. 内存优先
- 新数据首先存储在内存中，访问速度最快
- 减少对MySQL和Redis的频繁访问

### 2. 数据一致性
- 三个存储层保持数据同步
- 确保数据的一致性和完整性

### 3. 容错性
- 即使某个存储层失败，其他层仍能正常工作
- 提供详细的错误日志和状态信息

## 测试验证

运行测试脚本验证保存流程：

```bash
python tests/test_equipment_save_flow.py
```

测试包括：
1. 完整的保存流程测试
2. 内存缓存验证
3. Redis缓存验证
4. EquipMarketDataCollector添加方法测试

## 使用示例

```python
# 创建装备爬虫实例
spider = CBGEquipSpider()

# 准备装备数据
equipments = [
    {
        'equip_sn': 'equip_001',
        'price': 1000,
        'server_name': '测试服务器',
        'equip_name': '测试装备'
    }
]

# 保存装备数据（自动执行三层保存流程）
result = spider.save_equipment_data(equipments)

if result > 0:
    print("装备数据保存成功")
else:
    print("装备数据保存失败")
```

## 总结

新的装备数据保存流程通过三层存储架构，实现了：

1. **高效性**：内存优先，快速访问
2. **一致性**：三层数据同步
3. **可靠性**：容错机制和详细日志
4. **可维护性**：清晰的流程和错误处理

这确保了装备数据在爬虫、估价系统和缓存系统之间的一致性和高效性。
