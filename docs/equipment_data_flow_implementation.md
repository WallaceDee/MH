# 装备爬虫数据流转实现流程

## 核心流程

### 1. 数据获取与解析
**文件**: `src/spider/equip.py`
**方法**: `crawl_all_pages_async()` → `fetch_page()` → `parse_jsonp_response()`

```python
# 爬取单页数据
equipments = await self.fetch_page(page_num, search_params, search_type)

# 解析JSONP响应，提取装备数据
equipments = self.parse_jsonp_response(response.text)

# 特征提取
if kindid in LINGSHI_KINDIDS:
    added_attrs_features = self.lingshi_feature_extractor._extract_added_attrs_features(equip)
```

### 2. 立即内存更新（快速响应）
**文件**: `src/spider/equip.py`
**方法**: `_save_equipment_data_with_context()`

```python
# 过滤字段，创建DataFrame
filtered_equipments = self._filter_equipment_fields(equipments)
new_data_df = pd.DataFrame(filtered_equipments)

# 立即发布DataFrame消息
publish_success = self._publish_dataframe_message(new_data_df, len(equipments))
```

**Redis Pub/Sub消息发布**:
```python
def _publish_dataframe_message(self, new_data_df, data_count):
    message = {
        'type': MessageType.EQUIPMENT_DATA_SAVED,
        'data_count': data_count,
        'action': 'add_dataframe'
    }
    success = pubsub.publish_with_dataframe(Channel.EQUIPMENT_UPDATES, message, new_data_df)
```

### 3. 内存缓存更新
**文件**: `src/evaluator/market_anchor/equip/equip_market_data_collector.py`
**方法**: `_handle_equipment_update_message()`

```python
def _handle_equipment_update_message(self, message):
    if action == 'add_dataframe' and 'dataframe' in message:
        dataframe = message['dataframe']
        # 直接更新内存缓存
        success = self._update_memory_cache_with_dataframe(dataframe)
        if success:
            # 异步增量同步到Redis
            self._async_sync_to_redis(dataframe)
```

**内存缓存更新逻辑**:
```python
def _update_memory_cache_with_dataframe(self, new_dataframe):
    if self._full_data_cache is None or self._full_data_cache.empty:
        self._full_data_cache = new_dataframe.copy()
    else:
        merged_data = self._merge_incremental_data_removed(self._full_data_cache, new_dataframe)
        self._full_data_cache = merged_data
```

### 4. 异步持久化（MySQL → Redis）
**文件**: `src/spider/equip.py`
**方法**: `_async_batch_save_worker()`

```python
def _async_batch_save_worker(self, equipments, new_data_df):
    # 第一步：批量保存到MySQL
    saved_count, updated_count = self._batch_save_to_mysql(equipments)
    
    # 第二步：同步到Redis（只在有新数据时）
    redis_synced = False
    if saved_count > 0:
        redis_synced = self._sync_to_redis_cache(new_data_df)
    
    return saved_count, updated_count, saved_dataframe, redis_synced
```

**MySQL批量保存**:
```python
def _batch_save_to_mysql(self, equipments):
    # 批量查询已存在的装备
    existing_equipments = db.session.query(Equipment).filter(
        Equipment.equip_sn.in_(equip_sns)
    ).all()
    
    # 分类为新增和更新
    for equipment_data in equipments:
        if equip_sn in existing_equipments:
            # 更新现有记录
            update_existing_record(existing, equipment_data)
        else:
            # 准备新记录
            new_equipments.append(Equipment(**equipment_data))
    
    # 批量插入和提交
    db.session.bulk_save_objects(new_equipments)
    db.session.commit()
```

**Redis增量同步**:
```python
def _sync_to_redis_cache(self, new_data_df):
    for index, row in new_data_df.iterrows():
        equip_sn = row['equip_sn']
        row_dict = row.to_dict()
        redis_cache.hset(full_key, equip_sn, json.dumps(row_dict))
```

## 关键组件

### Redis Pub/Sub多订阅者支持
**文件**: `src/utils/redis_pubsub.py`

```python
def subscribe(self, channel: str, callback: Callable) -> bool:
    if channel not in self.subscribers:
        self.subscribers[channel] = []
        self.pubsub.subscribe(channel)
    
    if callback not in self.subscribers[channel]:
        self.subscribers[channel].append(callback)
    
    return True

def _handle_message(self, message):
    if channel in self.subscribers:
        callbacks = self.subscribers[channel]
        if isinstance(callbacks, list):
            for callback in callbacks:
                callback(message_data)
```

### DataFrame智能合并
**文件**: `src/evaluator/market_anchor/equip/equip_market_data_collector.py`

```python
def _merge_incremental_data_removed(self, existing_data, new_data):
    # 获取所有列的并集
    all_columns = list(set(existing_data.columns) | set(new_data.columns))
    
    # 确保两个DataFrame都有所有列（缺失的列填充None）
    for col in all_columns:
        if col not in existing_data.columns:
            existing_data[col] = None
        if col not in new_data.columns:
            new_data[col] = None
    
    # 合并数据
    existing_data_filtered = existing_data[~existing_data['equip_sn'].isin(new_data['equip_sn'])].copy()
    merged_data = pd.concat([existing_data_filtered, new_data], ignore_index=True)
    
    return merged_data
```

## 时序流程

```
T+0ms:   爬虫获取数据
T+5ms:   数据解析和特征提取
T+10ms:  发布DataFrame消息
T+15ms:  内存缓存立即更新 ✅
T+20ms:  提交异步保存任务
T+25ms:  异步线程开始处理
T+100ms: MySQL批量保存完成 ✅
T+200ms: Redis增量同步完成 ✅
```

## 数据存储结构

- **内存缓存**: `_full_data_cache` (pandas.DataFrame)
- **MySQL**: `equipments` 表 (关系型数据库)
- **Redis**: `equipment_market_data_full` (Hash结构)

## 错误处理

```python
# MySQL成功，Redis失败
if saved_count > 0 and not redis_synced:
    self.logger.warning("⚠️ MySQL保存成功但Redis同步失败，需手动同步Redis")

# 内存缓存更新失败
if not success:
    self._refresh_memory_cache_from_redis()
```

## 关键日志标识

- `📨 收到装备数据更新消息` - 消息接收
- `✅ 内存缓存已直接更新` - 内存更新成功
- `✅ 异步保存完成` - MySQL保存成功
- `✅ 异步增量同步到Redis完成` - Redis同步成功
