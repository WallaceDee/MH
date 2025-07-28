# CBG半自动数据收集器使用指南

## 概述

半自动数据收集器是一个创新的数据收集工具，它通过监听浏览器中的CBG API请求来自动收集数据。与传统的爬虫不同，这个工具不需要预先设置搜索参数，而是通过JavaScript注入来监听所有对 `https://xyq.cbg.163.com/cgi-bin/recommend.py` 的请求。

## 主要特性

- **自动监听**: 自动捕获所有CBG API请求
- **智能分类**: 根据请求参数自动分类数据类型
- **多数据库存储**: 不同类型数据存储到不同数据库
- **实时监控**: 实时显示收集统计信息
- **数据导出**: 支持导出为JSON格式
- **交互式操作**: 支持手动操作和后台监控
- **页面刷新恢复**: 自动检测页面刷新并重新注入监控脚本
- **智能脚本管理**: 防止重复注入，确保监控连续性

## 数据类型分类

收集器会自动将数据分为以下5种类型，并按照项目原有的数据库结构存储：

1. **角色数据** (`role`): 存储到 `data/YYYYMM/cbg_characters_YYYYMM.db`
2. **普通装备** (`equipment`): 存储到 `data/YYYYMM/cbg_equip_YYYYMM.db`
3. **灵饰** (`lingshi`): 存储到 `data/YYYYMM/cbg_equip_YYYYMM.db` (与装备共用数据库)
4. **宠物装备** (`pet_equipment`): 存储到 `data/YYYYMM/cbg_equip_YYYYMM.db` (与装备共用数据库)
5. **宠物** (`pet`): 存储到 `data/YYYYMM/cbg_pets_YYYYMM.db`

**注意**: 数据库按年月分割，使用项目原有的表结构和保存逻辑，确保数据的一致性和兼容性。

## 使用方法

### 1. 交互式模式（推荐）

```bash
python run.py auto-collect
```

这个模式会：
- 启动浏览器（有界面）
- 自动注入监控脚本
- 显示操作指导
- 实时显示收集统计
- 支持手动停止和导出

### 2. 无头模式

```bash
python run.py auto-collect --headless --url https://xyq.cbg.163.com/
```

这个模式会：
- 启动无头浏览器
- 访问指定URL
- 在后台监控请求
- 自动保存数据

### 3. 自定义URL

```bash
python run.py auto-collect --url https://xyq.cbg.163.com/cgi-bin/query.py?act=search_role
```

## 操作流程

### 启动收集器

1. 运行命令启动收集器
2. 等待浏览器加载完成
3. 监控脚本自动注入到页面

### 数据收集

1. 在CBG网站中正常操作：
   - 搜索角色
   - 搜索装备
   - 搜索灵饰
   - 搜索宠物
   - 搜索宠物装备

2. 所有API请求会被自动捕获：
   - 请求URL和参数
   - 请求时间戳
   - 请求方法类型

3. 数据自动分类和保存：
   - 根据参数自动判断数据类型
   - 保存到对应的SQLite数据库
   - 同时在内存中维护统计

### 监控统计

收集器会定期显示统计信息：
```
当前收集统计: {'role': 15, 'equipment': 8, 'pet': 3, 'lingshi': 2, 'pet_equipment': 1}
```

### 停止和导出

1. 按 `Ctrl+C` 停止收集
2. 选择是否导出数据到JSON文件
3. 查看最终统计信息

## 数据库结构

半自动收集器使用项目原有的数据库结构，确保与现有系统的完全兼容：

### 角色数据库 (cbg_characters_YYYYMM.db)
使用项目原有的 `characters` 表结构，包含完整的角色信息字段。

### 装备数据库 (cbg_equip_YYYYMM.db)
使用项目原有的 `equipments` 表结构，包含完整的装备信息字段。

### 宠物数据库 (cbg_pets_YYYYMM.db)
使用项目原有的 `pets` 表结构，包含完整的宠物信息字段。

### 数据存储特点
- **按月分割**: 数据库文件按年月命名，便于管理和查询
- **完整兼容**: 使用项目原有的表结构和字段定义
- **统一接口**: 与现有爬虫使用相同的保存和查询接口
- **数据一致性**: 确保收集的数据与手动爬取的数据格式完全一致

### 智能数据库初始化
收集器具有智能的数据库初始化机制，确保数据安全和系统稳定性：

- **已存在数据库**: 如果数据库文件已存在且包含表结构，系统会直接使用现有数据库，不会重新创建
- **新建数据库**: 如果数据库不存在或存在但无表结构，系统会自动创建相应的表结构
- **数据保护**: 不会覆盖或删除现有数据，确保数据安全
- **兼容性**: 完全兼容项目原有的数据库格式和表结构

```python
# 数据库初始化逻辑示例
def _create_database(self, db_type: str, db_path: str):
    db_exists = os.path.exists(db_path)
    
    if db_exists:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        if existing_tables:
            logger.info(f"数据库 {db_path} 已存在，包含表: {existing_tables}")
            return  # 直接使用现有数据库
        else:
            logger.info(f"数据库 {db_path} 存在但无表，将创建表结构")
    
    # 创建表结构（仅在需要时）
    cursor.execute(DB_TABLE_SCHEMAS[table_name])
```

## 技术原理

### JavaScript注入

收集器通过注入JavaScript代码来监听网络请求：

```javascript
// 监听XMLHttpRequest
const originalXHROpen = XMLHttpRequest.prototype.open;
const originalXHRSend = XMLHttpRequest.prototype.send;

XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
    this._url = url;
    this._method = method;
    return originalXHROpen.apply(this, arguments);
};

XMLHttpRequest.prototype.send = function(data) {
    if (this._url && this._url.includes('xyq.cbg.163.com/cgi-bin/recommend.py')) {
        // 捕获请求数据
        window.cbgRequests.push({
            type: 'xhr',
            url: this._url,
            method: this._method,
            data: data,
            timestamp: new Date().toISOString()
        });
    }
    return originalXHRSend.apply(this, arguments);
};
```

### 请求分类算法

根据URL参数自动分类：

- `act=search_role` → 角色数据
- `act=search_equip&equip_type=1` → 普通装备
- `act=search_equip&equip_type=2` → 灵饰
- `act=search_equip&equip_type=3` → 宠物装备
- `act=search_pet` → 宠物数据

## 优势特点

### 相比传统爬虫的优势

1. **无需预设参数**: 不需要预先设置搜索条件
2. **实时响应**: 可以捕获用户的实际操作
3. **数据完整性**: 捕获完整的请求参数
4. **操作简单**: 只需要正常使用网站即可
5. **分类准确**: 自动根据参数分类数据

### 适用场景

- 研究CBG搜索行为模式
- 收集用户实际搜索参数
- 分析不同数据类型的分布
- 监控特定类型的交易数据
- 数据挖掘和分析

## 注意事项

1. **浏览器要求**: 需要安装Chrome浏览器
2. **网络环境**: 确保能正常访问CBG网站
3. **图片加载**: 浏览器会正常加载图片，确保完整的页面体验和视觉效果
4. **数据量**: 大量数据收集时注意磁盘空间
5. **隐私保护**: 收集的数据仅用于研究分析
6. **合规使用**: 遵守网站使用条款和robots.txt

## 故障排除

### 常见问题

1. **Chrome驱动问题**
   ```bash
   # 确保Chrome浏览器已安装
   # 检查Chrome版本与驱动版本匹配
   ```

2. **网络连接问题**
   ```bash
   # 检查网络连接
   # 确认能访问CBG网站
   ```

3. **权限问题**
   ```bash
   # 确保有写入data目录的权限
   # 确保有创建数据库的权限
   ```

### 调试模式

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 扩展功能

### 自定义监控

可以修改监控脚本来捕获其他类型的请求：

```javascript
// 监控其他API
if (this._url && this._url.includes('your-target-api')) {
    // 自定义处理逻辑
}
```

### 数据过滤

可以在保存前添加数据过滤逻辑：

```python
def _save_data(self, data_type: str, data: Dict):
    # 添加过滤条件
    if data.get('price', 0) < 1000:
        return  # 跳过低价数据
    
    # 保存数据
    # ...
```

### 实时分析

可以添加实时数据分析功能：

```python
def _analyze_data(self, data_type: str, data: Dict):
    # 实时分析逻辑
    # 价格趋势分析
    # 数据质量检查
    # 异常检测
    pass
```

## 总结

半自动数据收集器为CBG数据收集提供了一个全新的解决方案，它结合了传统爬虫的自动化特性和手动操作的灵活性，特别适合需要收集真实用户行为数据的场景。 