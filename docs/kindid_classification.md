# KindID分类功能完整实现

## 功能概述

Playwright收集器现在支持完整的kindid分类功能，能够根据URL中的kindid参数准确识别和分类不同类型的CBG数据。

## KindID分类规则

### 角色相关 KindID
```
27, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 49, 51, 50, 77, 78, 79, 81, 82
```

### 宠物相关 KindID
```
1, 65, 66, 67, 68, 69, 70, 71, 75, 80
```

### 装备相关 KindID
```
2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 26, 28, 29, 42, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 72, 73, 74, 83
```

## 实现细节

### 1. 精确匹配算法

使用正则表达式进行精确匹配，避免子字符串匹配问题：

```python
import re

# 检查URL中的kindid参数 - 使用正则表达式精确匹配
for kindid in role_kindids:
    if re.search(rf'kindid={kindid}(&|$)', url):
        return 'role'
for kindid in pet_kindids:
    if re.search(rf'kindid={kindid}(&|$)', url):
        return 'pet'
for kindid in equip_kindids:
    if re.search(rf'kindid={kindid}(&|$)', url):
        return 'equipment'
```

### 2. 匹配模式说明

- `kindid={kindid}&` - 匹配URL中间位置的kindid参数
- `kindid={kindid}$` - 匹配URL末尾的kindid参数
- 使用`(&|$)`确保不会匹配到子字符串（如kindid=1匹配kindid=10）

### 3. 分类优先级

按照以下顺序进行匹配：
1. 角色kindid
2. 宠物kindid  
3. 装备kindid

## 支持的URL模式

### 1. 全区搜索
```
search_type=overall_search_role
search_type=overall_search_equip
search_type=overall_search_pet_equip
search_type=overall_search_lingshi
search_type=overall_search_pet
```

### 2. 区内推荐搜索 (view_loc=reco_left)
```
recommend_type=1 -> role
recommend_type=2 -> equipment
recommend_type=3 -> pet
recommend_type=4 -> equipment
```

### 3. 区内推荐指定 (view_loc=equip_list)
根据kindid参数进行分类

### 4. 区内搜索指定 (view_loc=search_cond)
```
search_type=search_role_equip -> equipment
search_type=search_role -> role
search_type=search_pet_equip -> equipment
search_type=search_pet -> pet
search_type=search_lingshi -> equipment
```

## 测试验证

### 测试脚本
- `tests/test_kindid_classification.py` - 基础分类测试
- `tests/debug_kindid_10.py` - 特定问题调试

### 测试结果
```
✅ 测试  1: role       | kindid=27
✅ 测试  2: role       | kindid=30
✅ 测试  3: role       | kindid=35
✅ 测试  4: role       | kindid=50
✅ 测试  5: role       | kindid=82
✅ 测试  6: pet        | kindid=1
✅ 测试  7: pet        | kindid=65
✅ 测试  8: pet        | kindid=70
✅ 测试  9: pet        | kindid=75
✅ 测试 10: pet        | kindid=80
✅ 测试 11: equipment  | kindid=2
✅ 测试 12: equipment  | kindid=4
✅ 测试 13: equipment  | kindid=10  # 修复后的结果
✅ 测试 14: equipment  | kindid=20
✅ 测试 15: equipment  | kindid=42
✅ 测试 16: equipment  | kindid=83

测试完成: 16/16 通过
成功率: 100.0%
```

## 关键修复

### 问题描述
最初的字符串匹配方式存在子字符串匹配问题：
- `kindid=1` 会错误匹配 `kindid=10`
- 导致kindid=10被错误分类为pet而不是equipment

### 解决方案
使用正则表达式精确匹配：
```python
# 修复前
if f'kindid={kindid}' in url:

# 修复后  
if re.search(rf'kindid={kindid}(&|$)', url):
```

### 验证结果
```
修复前: kindid=10 -> pet (错误)
修复后: kindid=10 -> equipment (正确)
```

## 使用示例

### 基本使用
```python
from src.spider.playwright_collector import PlaywrightAutoCollector

collector = PlaywrightAutoCollector(headless=True)

# 测试不同kindid的分类
url1 = "https://xyq.cbg.163.com/cgi-bin/query.py?act=recommend_search&view_loc=equip_list&kindid=27"
url2 = "https://xyq.cbg.163.com/cgi-bin/query.py?act=recommend_search&view_loc=equip_list&kindid=1"
url3 = "https://xyq.cbg.163.com/cgi-bin/query.py?act=recommend_search&view_loc=equip_list&kindid=10"

print(collector._classify_request(url1, {}))  # 'role'
print(collector._classify_request(url2, {}))  # 'pet'
print(collector._classify_request(url3, {}))  # 'equipment'
```

### 实际应用
在Playwright收集器中，所有对`recommend.py`的请求都会自动根据kindid进行分类，并保存到对应的数据库中。

## 注意事项

1. **精确匹配**: 使用正则表达式确保不会出现子字符串匹配问题
2. **优先级**: 按照角色->宠物->装备的顺序进行匹配
3. **扩展性**: 可以轻松添加新的kindid到对应分类中
4. **测试覆盖**: 建议添加新kindid时进行充分测试

## 总结

通过实现完整的kindid分类功能，Playwright收集器现在能够：

1. **准确识别**: 根据kindid精确识别数据类型
2. **自动分类**: 将数据自动保存到正确的数据库
3. **避免错误**: 解决了子字符串匹配导致的分类错误
4. **易于维护**: 清晰的分类规则和测试覆盖

这个功能大大提升了数据收集的准确性和自动化程度。 