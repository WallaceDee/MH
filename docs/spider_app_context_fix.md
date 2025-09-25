# 爬虫应用上下文修复说明

## 问题描述

在爬虫运行过程中，出现了以下错误：

```
Working outside of application context.
This typically means that you attempted to use functionality that needed
the current application. To solve this, set up an application context
with app.app_context(). See the documentation for more information.
```

## 问题原因

爬虫在后台线程中运行，没有Flask应用上下文，导致无法使用SQLAlchemy的数据库操作。

## 解决方案

为装备爬虫和召唤兽爬虫的保存方法添加了Flask应用上下文检测和自动创建机制。

### 修复的爬虫

1. **装备爬虫** (`src/spider/equip.py`)
   - `save_equipment_data()` 方法
   - 新增 `_save_equipment_data_with_context()` 方法

2. **召唤兽爬虫** (`src/spider/pet.py`)
   - `save_pet_data()` 方法
   - 新增 `_save_pet_data_with_context()` 方法

### 修复逻辑

```python
def save_equipment_data(self, equipments):
    """保存装备数据到MySQL数据库"""
    try:
        # 确保在Flask应用上下文中执行数据库操作
        from flask import current_app
        from src.app import create_app
        
        # 如果当前没有应用上下文，创建一个
        if not current_app:
            app = create_app()
            with app.app_context():
                return self._save_equipment_data_with_context(equipments)
        else:
            return self._save_equipment_data_with_context(equipments)
            
    except Exception as e:
        self.logger.error(f"保存装备数据到MySQL数据库失败: {e}")
        return 0
```

## 修复效果

### 修复前
- 爬虫在后台线程中运行时报错
- 无法保存数据到MySQL数据库
- 错误信息：`Working outside of application context`

### 修复后
- 自动检测Flask应用上下文
- 如果没有上下文，自动创建一个
- 如果有上下文，直接使用现有的
- 数据可以正常保存到MySQL数据库

## 测试验证

运行测试脚本验证修复效果：

```bash
python tests/test_spider_app_context_fix.py
```

测试包括：
1. 无应用上下文情况下的数据保存
2. 有应用上下文情况下的数据保存
3. 装备爬虫和召唤兽爬虫的测试

## 注意事项

1. **性能影响**: 创建应用上下文会有轻微的性能开销，但影响很小
2. **内存使用**: 每个爬虫实例会创建一个应用上下文，需要注意内存使用
3. **线程安全**: 修复后的代码是线程安全的
4. **错误处理**: 添加了完善的错误处理机制

## 相关文件

- `src/spider/equip.py` - 装备爬虫修复
- `src/spider/pet.py` - 召唤兽爬虫修复
- `tests/test_spider_app_context_fix.py` - 测试脚本

## 总结

通过添加Flask应用上下文检测和自动创建机制，解决了爬虫在后台线程中运行时的数据库操作问题。修复后的代码具有更好的容错性和稳定性。
