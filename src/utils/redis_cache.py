#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Redis缓存工具类
用于优化市场数据采集器的性能
"""

import redis
import pickle
import json
import logging
import hashlib
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os


def _deserialize_chunk_worker(chunk_items):
    """
    多进程worker函数：反序列化单个数据块
    必须定义在模块顶层，才能被ProcessPoolExecutor序列化
    
    Args:
        chunk_items: [(equip_sn, serialized_data), ...]
        
    Returns:
        list: 反序列化后的记录列表
    """
    import pickle
    records = []
    
    for equip_sn, serialized_data in chunk_items:
        try:
            row_data = pickle.loads(serialized_data)
            records.append(row_data)
        except:
            # 忽略错误，继续处理下一条
            continue
    
    return records


class RedisCache:
    """Redis缓存管理器"""
    
    def __init__(self, 
                 host: str = '47.86.33.98',
                 port: int = 6379, 
                 db: int = 0,
                 password: Optional[str] = '447363121',
                 decode_responses: bool = False,
                 socket_timeout: float = 120.0,  # 增加到120秒，支持大数据量操作
                 socket_connect_timeout: float = 30.0,  # 增加到30秒
                 retry_on_timeout: bool = True,
                 health_check_interval: int = 30):
        """
        初始化Redis缓存
        
        Args:
            host: Redis服务器地址
            port: Redis端口
            db: Redis数据库编号
            password: Redis密码
            decode_responses: 是否自动解码响应
            socket_timeout: 套接字超时时间
            socket_connect_timeout: 连接超时时间
            retry_on_timeout: 超时时是否重试
            health_check_interval: 健康检查间隔
        """
        self.logger = logging.getLogger(__name__)
        
        # 从环境变量获取Redis配置
        self.host = os.getenv('REDIS_HOST', host)
        self.port = int(os.getenv('REDIS_PORT', port))
        self.db = int(os.getenv('REDIS_DB', db))
        self.password = os.getenv('REDIS_PASSWORD', password)
        
        # 连接池配置
        self.pool = redis.ConnectionPool(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=decode_responses,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            retry_on_timeout=retry_on_timeout,
            health_check_interval=health_check_interval,
            max_connections=20  # 最大连接数
        )
        #  把参数log出来
        self.logger.info(f"Redis配置: host={self.host}, port={self.port}, db={self.db}, password={self.password}")
        # 创建Redis客户端
        self.client = redis.Redis(connection_pool=self.pool)
        
        # 缓存键前缀
        self.key_prefix = "cbg_market:"
        
        # 默认过期时间（秒）
        self.default_ttl = 3600 * 6  # 6小时
        
        # 测试连接
        self._test_connection()
    
    def _test_connection(self):
        """测试Redis连接"""
        try:
            self.client.ping()
            self.logger.info(f"Redis连接成功: {self.host}:{self.port}/{self.db}")
        except Exception as e:
            self.logger.error(f"Redis连接失败: {e}")
            # 不抛出异常，允许程序继续运行，但缓存功能将不可用
    
    def is_available(self) -> bool:
        """检查Redis是否可用"""
        try:
            self.client.ping()
            return True
        except Exception:
            return False
    
    def _make_key(self, key: str) -> str:
        """生成完整的缓存键"""
        return f"{self.key_prefix}{key}"
    
    def _hash_key(self, data: Union[str, dict, list]) -> str:
        """生成数据的哈希键"""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        else:
            data_str = str(data)
        
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()[:16]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None表示使用默认时间
            
        Returns:
            bool: 是否设置成功
        """
        if not self.is_available():
            return False
        
        try:
            full_key = self._make_key(key)
            
            # 序列化数据
            if isinstance(value, pd.DataFrame):
                # DataFrame特殊处理
                serialized_value = pickle.dumps({
                    'type': 'dataframe',
                    'data': value.to_dict('records'),
                    'index': value.index.tolist() if hasattr(value.index, 'tolist') else list(value.index),
                    'columns': value.columns.tolist()
                })
            elif isinstance(value, np.ndarray):
                # NumPy数组特殊处理
                serialized_value = pickle.dumps({
                    'type': 'numpy',
                    'data': value.tolist(),
                    'shape': value.shape,
                    'dtype': str(value.dtype)
                })
            else:
                # 其他类型使用pickle序列化
                serialized_value = pickle.dumps(value)
            
            # 设置缓存
            if ttl is None:
                # None表示永不过期，使用set而不是setex
                result = self.client.set(full_key, serialized_value)
            else:
                # 有TTL值，使用setex
                expire_time = ttl
                result = self.client.setex(full_key, expire_time, serialized_value)
            
            if result:
                if ttl is None:
                    self.logger.debug(f"缓存设置成功: {key}, TTL: 永不过期")
                else:
                    self.logger.debug(f"缓存设置成功: {key}, TTL: {ttl}秒")
            else:
                self.logger.warning(f"缓存设置失败: {key}")
                
            return result
            
        except Exception as e:
            self.logger.error(f"设置缓存失败 {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在返回None
        """
        if not self.is_available():
            return None
        
        try:
            full_key = self._make_key(key)
            serialized_value = self.client.get(full_key)
            
            if serialized_value is None:
                self.logger.debug(f"缓存未找到: {key}")
                return None
            
            # 反序列化数据
            value = pickle.loads(serialized_value)
            
            # 特殊类型处理
            if isinstance(value, dict) and 'type' in value:
                if value['type'] == 'dataframe':
                    # 重建DataFrame
                    df = pd.DataFrame(value['data'])
                    if 'index' in value and value['index']:
                        df.index = value['index']
                    if 'columns' in value:
                        df.columns = value['columns']
                    return df
                elif value['type'] == 'numpy':
                    # 重建NumPy数组
                    arr = np.array(value['data'], dtype=value['dtype'])
                    return arr.reshape(value['shape'])
            
            self.logger.debug(f"缓存获取成功: {key}")
            return value
            
        except Exception as e:
            self.logger.error(f"获取缓存失败 {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否删除成功
        """
        if not self.is_available():
            return False
        
        try:
            full_key = self._make_key(key)
            result = self.client.delete(full_key)
            
            if result:
                self.logger.debug(f"缓存删除成功: {key}")
            else:
                self.logger.debug(f"缓存不存在: {key}")
                
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"删除缓存失败 {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否存在
        """
        if not self.is_available():
            return False
        
        try:
            full_key = self._make_key(key)
            return bool(self.client.exists(full_key))
        except Exception as e:
            self.logger.error(f"检查缓存存在性失败 {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """
        获取缓存剩余生存时间
        
        Args:
            key: 缓存键
            
        Returns:
            int: 剩余秒数，-1表示永不过期，-2表示不存在
        """
        if not self.is_available():
            return -2
        
        try:
            full_key = self._make_key(key)
            return self.client.ttl(full_key)
        except Exception as e:
            self.logger.error(f"获取缓存TTL失败 {key}: {e}")
            return -2
    
    def clear_pattern(self, pattern: str) -> int:
        """
        根据模式清除缓存
        
        Args:
            pattern: 匹配模式，如 "market_data:*"
            
        Returns:
            int: 清除的键数量
        """
        if not self.is_available():
            return 0
        
        try:
            full_pattern = self._make_key(pattern)
            keys = self.client.keys(full_pattern)
            
            if keys:
                deleted = self.client.delete(*keys)
                self.logger.info(f"清除缓存: {deleted} 个键，模式: {pattern}")
                return deleted
            else:
                self.logger.debug(f"未找到匹配的缓存键: {pattern}")
                return 0
                
        except Exception as e:
            self.logger.error(f"清除缓存失败 {pattern}: {e}")
            return 0
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        获取Redis内存使用情况
        
        Returns:
            Dict: 内存使用信息
        """
        if not self.is_available():
            return {}
        
        try:
            info = self.client.info('memory')
            return {
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'used_memory_peak': info.get('used_memory_peak', 0),
                'used_memory_peak_human': info.get('used_memory_peak_human', '0B'),
                'total_system_memory': info.get('total_system_memory', 0),
                'total_system_memory_human': info.get('total_system_memory_human', '0B'),
                'maxmemory': info.get('maxmemory', 0),
                'maxmemory_human': info.get('maxmemory_human', '0B')
            }
        except Exception as e:
            self.logger.error(f"获取内存使用情况失败: {e}")
            return {}
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict: 缓存统计信息
        """
        if not self.is_available():
            return {'available': False}
        
        try:
            info = self.client.info()
            pattern = self._make_key("*")
            keys = self.client.keys(pattern)
            
            return {
                'available': True,
                'redis_version': info.get('redis_version', 'unknown'),
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'cache_keys_count': len(keys),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            self.logger.error(f"获取缓存统计失败: {e}")
            return {'available': False, 'error': str(e)}

    def set_batch(self, data_dict: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        批量设置缓存 - 使用Redis Pipeline优化性能
        
        Args:
            data_dict: 键值对字典 {key: value, ...}
            ttl: 过期时间（秒）
            
        Returns:
            bool: 是否全部设置成功
        """
        if not self.is_available() or not data_dict:
            return False
        
        try:
            pipe = self.client.pipeline()
            
            self.logger.info(f"开始批量设置缓存，共 {len(data_dict)} 个键，TTL: {'永不过期' if ttl is None else f'{ttl}秒'}")
            
            for key, value in data_dict.items():
                try:
                    full_key = self._make_key(key)
                    
                    # 序列化数据
                    if isinstance(value, pd.DataFrame):
                        serialized_value = pickle.dumps({
                            'type': 'dataframe',
                            'data': value.to_dict('records'),
                            'index': value.index.tolist() if hasattr(value.index, 'tolist') else list(value.index),
                            'columns': value.columns.tolist()
                        })
                    elif isinstance(value, np.ndarray):
                        serialized_value = pickle.dumps({
                            'type': 'numpy',
                            'data': value.tolist(),
                            'shape': value.shape,
                            'dtype': str(value.dtype)
                        })
                    else:
                        serialized_value = pickle.dumps(value)
                    
                    # 添加到Pipeline
                    if ttl is None:
                        pipe.set(full_key, serialized_value)  # 永不过期
                    else:
                        pipe.setex(full_key, ttl, serialized_value)  # 有TTL
                    
                except Exception as e:
                    self.logger.warning(f"序列化键 {key} 失败: {e}")
                    continue
            
            # 执行Pipeline
            results = pipe.execute()
            success_count = sum(1 for r in results if r)
            
            self.logger.info(f"批量缓存设置完成: {success_count}/{len(data_dict)} 成功")
            return success_count == len(data_dict)
            
        except Exception as e:
            self.logger.error(f"批量设置缓存失败: {e}")
            return False

    def get_batch(self, keys: List[str]) -> Dict[str, Any]:
        """
        批量获取缓存 - 使用Redis Pipeline优化性能
        
        Args:
            keys: 键列表
            
        Returns:
            Dict: 键值对字典
        """
        if not self.is_available() or not keys:
            return {}
        
        try:
            pipe = self.client.pipeline()
            full_keys = [self._make_key(key) for key in keys]
            
            # 批量获取
            for full_key in full_keys:
                pipe.get(full_key)
            
            results = pipe.execute()
            
            # 处理结果
            result_dict = {}
            for i, (key, result) in enumerate(zip(keys, results)):
                if result is not None:
                    try:
                        deserialized = pickle.loads(result)
                        
                        # 特殊处理DataFrame
                        if isinstance(deserialized, dict) and deserialized.get('type') == 'dataframe':
                            df_data = deserialized['data']
                            index = deserialized.get('index', list(range(len(df_data))))
                            columns = deserialized.get('columns', [])
                            
                            df = pd.DataFrame(df_data, columns=columns)
                            if index:
                                df.index = index
                            result_dict[key] = df
                        # 特殊处理NumPy数组
                        elif isinstance(deserialized, dict) and deserialized.get('type') == 'numpy':
                            array_data = np.array(deserialized['data'])
                            if 'shape' in deserialized:
                                array_data = array_data.reshape(deserialized['shape'])
                            result_dict[key] = array_data
                        else:
                            result_dict[key] = deserialized
                            
                    except Exception as e:
                        self.logger.warning(f"反序列化键 {key} 失败: {e}")
                        continue
            
            self.logger.debug(f"批量获取缓存: {len(result_dict)}/{len(keys)} 成功")
            return result_dict
            
        except Exception as e:
            self.logger.error(f"批量获取缓存失败: {e}")
            return {}


    def get_redis_info(self):
        """获取Redis服务器信息"""
        try:
            if not self.is_available():
                return None
            
            info = self.client.info()
            return info
        except Exception as e:
            self.logger.error(f"获取Redis信息失败: {e}")
            return None

    def get_cache_types(self):
        """获取缓存类型统计"""
        try:
            if not self.is_available():
                return {}
            
            # 获取所有键
            keys = self.client.keys('*')
            cache_types = {}
            
            for key in keys:
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                
                # 根据键名分类
                if 'role_data' in key_str:
                    cache_type = 'role_data'
                elif 'equipment' in key_str:
                    cache_type = 'equipment_data'
                elif 'search' in key_str:
                    cache_type = 'search_results'
                elif 'analysis' in key_str:
                    cache_type = 'market_analysis'
                elif 'trend' in key_str:
                    cache_type = 'price_trends'
                else:
                    cache_type = 'other'
                
                if cache_type not in cache_types:
                    cache_types[cache_type] = {
                        'count': 0, 
                        'ttl_hours': 0,
                        'keys': [],  # 存储具体的键名
                        'key_details': []  # 存储键的详细信息
                    }
                
                cache_types[cache_type]['count'] += 1
                
                # 获取TTL
                ttl = self.client.ttl(key)
                ttl_hours = 0
                if ttl > 0:
                    ttl_hours = round(ttl / 3600, 1)
                    cache_types[cache_type]['ttl_hours'] = max(
                        cache_types[cache_type]['ttl_hours'], 
                        ttl_hours
                    )
                elif ttl == -1:
                    ttl_hours = -1
                    cache_types[cache_type]['ttl_hours'] = -1  # 永不过期
                
                # 存储键名（去掉前缀）
                clean_key = key_str.replace('cbg_market:', '') if key_str.startswith('cbg_market:') else key_str
                cache_types[cache_type]['keys'].append(clean_key)
                
                # 存储键的详细信息
                key_info = {
                    'key': clean_key,
                    'ttl_hours': ttl_hours,
                    'ttl_display': '永不过期' if ttl_hours == -1 else f'{ttl_hours}小时'
                }
                cache_types[cache_type]['key_details'].append(key_info)
            
            return cache_types
        except Exception as e:
            self.logger.error(f"获取缓存类型统计失败: {e}")
            return {}

    def rename_key(self, old_key: str, new_key: str) -> bool:
        """
        原子性地重命名Redis键（高效的无缝切换）
        同时重命名主键和对应的元数据键
        
        Args:
            old_key: 原键名
            new_key: 新键名
            
        Returns:
            bool: 是否重命名成功
        """
        try:
            if not self.is_available():
                return False
            
            # 使用_make_key方法添加前缀
            old_full_key = self._make_key(old_key)
            new_full_key = self._make_key(new_key)
            
            # 先检查源键是否存在
            if not self.client.exists(old_full_key):
                self.logger.error(f"❌ 源键不存在，无法重命名: {old_full_key}")
                return False
            
            # 使用Redis的RENAME命令进行原子性重命名（会自动覆盖目标键）
            result = self.client.rename(old_full_key, new_full_key)
            if result:
                self.logger.info(f"✅ 主键重命名成功: {old_full_key} -> {new_full_key}")
                
                # 同时重命名元数据键
                old_meta_key = f"{old_full_key}:meta"
                new_meta_key = f"{new_full_key}:meta"
                
                if self.client.exists(old_meta_key):
                    meta_result = self.client.rename(old_meta_key, new_meta_key)
                    if meta_result:
                        self.logger.info(f"✅ 元数据键重命名成功: {old_meta_key} -> {new_meta_key}")
                    else:
                        self.logger.warning(f"⚠️ 元数据键重命名失败: {old_meta_key} -> {new_meta_key}")
                else:
                    self.logger.info(f"ℹ️ 元数据键不存在，跳过重命名: {old_meta_key}")
                
                return True
            else:
                self.logger.warning(f"⚠️ 主键重命名失败: {old_full_key} -> {new_full_key}")
                return False
        except Exception as e:
            self.logger.error(f"❌ 键重命名异常: {e}")
            return False

    def set_hash_data(self, hash_key: str, data: pd.DataFrame, ttl: Optional[int] = None, key_column: str = 'equip_sn') -> bool:
        """
        将DataFrame数据存储为Redis Hash结构
        
        Args:
            hash_key: Hash键名
            data: 要存储的DataFrame
            ttl: 过期时间（秒）
            key_column: 用作Hash field的列名，默认为'equip_sn'（装备）；角色数据使用'eid'
            
        Returns:
            bool: 是否存储成功
        """
        if not self.is_available() or data.empty:
            return False
        
        # 检查DataFrame中是否存在指定的键列
        if key_column not in data.columns:
            # 尝试从索引中获取
            if hasattr(data.index, 'name') and data.index.name == key_column:
                # 索引名匹配，重置索引使其成为普通列
                data = data.reset_index()
            else:
                # 尝试重置索引看是否包含该列
                reset_data = data.reset_index()
                if key_column in reset_data.columns:
                    data = reset_data
                else:
                    # 列不存在，记录详细错误信息
                    available_columns = list(data.columns)
                    self.logger.error(
                        f"主键列 '{key_column}' 不存在于数据中。\n"
                        f"可用的列 ({len(available_columns)} 个): {', '.join(available_columns[:20])}"
                        f"{'...(还有更多列)' if len(available_columns) > 20 else ''}"
                    )
                    return False
        
        try:
            full_key = self._make_key(hash_key)
            
            self.logger.info(f"开始存储Hash数据: {full_key}，数据量: {len(data)} 条，主键列: {key_column}")
            
            # 对于大数据量，使用分批处理
            if len(data) > 2000:
                return self._set_large_hash_data(full_key, data, ttl, key_column)
            else:
                # 小数据量直接处理
                pipe = self.client.pipeline()
                
                for _, row in data.iterrows():
                    # 从指定的列获取键值
                    key_value = str(row[key_column])
                    row_data = row.to_dict()
                    
                    # 序列化行数据
                    serialized_data = pickle.dumps(row_data)
                    
                    # 添加到Hash
                    pipe.hset(full_key, key_value, serialized_data)
                
                # 执行Pipeline
                pipe.execute()
            
            # 设置过期时间
            if ttl:
                self.client.expire(full_key, ttl)
            
            # 存储元数据
            metadata = {
                'total_count': len(data),
                'columns': data.columns.tolist(),
                'created_at': datetime.now().isoformat(),
                'structure': 'hash'
            }
            meta_key = f"{full_key}:meta"
            self.client.set(meta_key, pickle.dumps(metadata))
            if ttl:
                self.client.expire(meta_key, ttl)
            
            self.logger.info(f"✅ Hash数据存储完成: {full_key}，数据量: {len(data)} 条")
            return True
            
        except Exception as e:
            self.logger.error(f"存储Hash数据失败 {hash_key}: {e}")
            return False
    
    def _set_large_hash_data(self, full_key: str, data: pd.DataFrame, ttl: Optional[int], key_column: str = 'equip_sn') -> bool:
        """
        分批存储大数据量Hash数据
        
        Args:
            full_key: 完整的Redis键名
            data: 要存储的数据
            ttl: 过期时间
            key_column: 用作Hash field的列名
            
        Returns:
            bool: 是否存储成功
        """
        try:
            import time
            batch_size = 2000  # 每批2000条
            total_batches = (len(data) + batch_size - 1) // batch_size
            
            self.logger.info(f"大数据量分批存储: {len(data)} 条，分 {total_batches} 批处理，主键列: {key_column}")
            
            # 分批存储数据
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min((batch_num + 1) * batch_size, len(data))
                batch_data = data.iloc[start_idx:end_idx]
                
                self.logger.info(f"  处理第 {batch_num + 1}/{total_batches} 批，数据量: {len(batch_data)} 条")
                
                # 使用Pipeline批量设置
                pipe = self.client.pipeline()
                
                for _, row in batch_data.iterrows():
                    # 从指定的列获取键值
                    key_value = str(row[key_column])
                    row_data = row.to_dict()
                    
                    # 序列化行数据
                    serialized_data = pickle.dumps(row_data)
                    
                    # 添加到Hash
                    pipe.hset(full_key, key_value, serialized_data)
                
                # 执行Pipeline
                pipe.execute()
                
                # 每批之间稍作休息，避免Redis过载
                if batch_num < total_batches - 1:
                    time.sleep(0.1)
            
            # 设置过期时间
            if ttl:
                self.client.expire(full_key, ttl)
            
            # 存储元数据
            metadata = {
                'total_count': len(data),
                'columns': data.columns.tolist(),
                'created_at': datetime.now().isoformat(),
                'structure': 'hash'
            }
            meta_key = f"{full_key}:meta"
            self.client.set(meta_key, pickle.dumps(metadata))
            if ttl:
                self.client.expire(meta_key, ttl)
            
            self.logger.info(f"✅ 大数据量Hash数据存储完成: {full_key}，总数据量: {len(data)} 条（含元数据）")
            return True
            
        except Exception as e:
            self.logger.error(f"大数据量Hash数据存储失败: {e}")
            return False

    def get_hash_data(self, hash_key: str) -> Optional[pd.DataFrame]:
        """
        从Redis Hash获取DataFrame数据
        优化版本：支持大数据量分批读取
        
        Args:
            hash_key: Hash键名
            
        Returns:
            Optional[pd.DataFrame]: 合并后的DataFrame
        """
        if not self.is_available():
            return None
        
        try:
            full_key = self._make_key(hash_key)
            
            # 检查Hash是否存在
            if not self.client.exists(full_key):
                self.logger.info(f"Hash不存在: {full_key}")
                return pd.DataFrame()
            
            # 先获取Hash的大小，判断是否需要分批读取
            hash_size = self.client.hlen(full_key)
            if hash_size == 0:
                return pd.DataFrame()
            
            self.logger.info(f"开始获取Hash数据: {full_key}，数据量: {hash_size} 条")
            
            # 对于大数据量，使用分批读取
            if hash_size > 5000:
                return self._get_large_hash_data(full_key, hash_size)
            else:
                # 小数据量直接读取
                hash_data = self.client.hgetall(full_key)
                return self._deserialize_hash_data(hash_data, full_key)
            
        except Exception as e:
            self.logger.error(f"获取Hash数据失败 {hash_key}: {e}")
            return None
    
    def _get_large_hash_data(self, full_key: str, hash_size: int) -> Optional[pd.DataFrame]:
        """
        分批获取大数据量Hash数据
        
        Args:
            full_key: 完整的Redis键名
            hash_size: Hash大小
            
        Returns:
            Optional[pd.DataFrame]: 合并后的DataFrame
        """
        try:
            import time
            batch_size = 2000  # 每批2000条
            total_batches = (hash_size + batch_size - 1) // batch_size
            
            self.logger.info(f"大数据量分批读取: {hash_size} 条，分 {total_batches} 批处理")
            
            all_records = []
            cursor = 0
            
            for batch_num in range(total_batches):
                self.logger.info(f"  读取第 {batch_num + 1}/{total_batches} 批数据...")
                
                # 使用HSCAN分批读取
                batch_data = {}
                scan_cursor = cursor
                
                while True:
                    scan_cursor, data = self.client.hscan(full_key, cursor=scan_cursor, count=batch_size)
                    batch_data.update(data)
                    
                    # 如果扫描完成（cursor=0）或者已经读取足够的数据，跳出循环
                    if scan_cursor == 0:
                        break
                    # 如果当前批次数据量已经达到预期，也跳出循环
                    if len(batch_data) >= batch_size:
                        break
                
                # 反序列化当前批次数据
                batch_records = self._deserialize_hash_data(batch_data, full_key, batch_num + 1)
                if batch_records is not None and not batch_records.empty:
                    all_records.append(batch_records)
                    self.logger.info(f"  第 {batch_num + 1} 批数据反序列化完成: {len(batch_records)} 条")
                
                cursor = scan_cursor
                # 如果扫描完成，跳出外层循环
                if cursor == 0:
                    self.logger.info(f"  Redis扫描完成，总共处理了 {batch_num + 1} 批数据")
                    break
                
                # 每批之间稍作休息
                time.sleep(0.01)
            
            if not all_records:
                return pd.DataFrame()
            
            # 合并所有批次数据
            df = pd.concat(all_records, ignore_index=True)
            self.logger.info(f"✅ 大数据量Hash数据获取完成: {full_key}，总数据量: {len(df)} 条")
            return df
            
        except Exception as e:
            self.logger.error(f"大数据量Hash数据获取失败: {e}")
            return None
    
    def _deserialize_hash_data(self, hash_data: dict, full_key: str, batch_num: int = None) -> Optional[pd.DataFrame]:
        """
        反序列化Hash数据
        
        Args:
            hash_data: Hash数据字典
            full_key: 完整的Redis键名
            batch_num: 批次号（用于日志）
            
        Returns:
            Optional[pd.DataFrame]: 反序列化后的DataFrame
        """
        try:
            if not hash_data:
                return pd.DataFrame()
            
            # 根据数据量选择串行或并行反序列化
            data_size = len(hash_data)
            
            if data_size < 500:
                # 小数据量：串行处理（避免进程开销）
                records = []
                for equip_sn, serialized_data in hash_data.items():
                    try:
                        row_data = pickle.loads(serialized_data)
                        records.append(row_data)
                    except Exception as e:
                        self.logger.warning(f"反序列化数据失败 {equip_sn}: {e}")
                        continue
                
                if not records:
                    return pd.DataFrame()
                
                df = pd.DataFrame(records)
                batch_info = f"第 {batch_num} 批" if batch_num else ""
                self.logger.info(f"✅ {batch_info}Hash数据反序列化完成: {len(df)} 条（串行）")
                return df
            
            else:
                # 大数据量：多进程并行处理（绕过GIL限制）
                import time
                from concurrent.futures import ProcessPoolExecutor, as_completed
                import multiprocessing
                
                start_time = time.time()
                # 使用CPU核心数，但不超过8个进程
                max_workers = min(multiprocessing.cpu_count(), 8)
                
                # 将数据分块
                items = list(hash_data.items())
                chunk_size = max(len(items) // max_workers, 100)
                chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
                
                self.logger.info(f"  并行反序列化: {len(items)}条，分{len(chunks)}块，{max_workers}进程")
                
                all_records = []
                
                # 使用多进程池并行反序列化
                with ProcessPoolExecutor(max_workers=max_workers) as executor:
                    futures = [
                        executor.submit(_deserialize_chunk_worker, chunk) 
                        for chunk in chunks
                    ]
                    
                    for future in as_completed(futures):
                        try:
                            chunk_records = future.result(timeout=30)
                            if chunk_records:
                                all_records.extend(chunk_records)
                        except Exception as e:
                            self.logger.error(f"  块反序列化失败: {e}")
                
                if not all_records:
                    return pd.DataFrame()
                
                df = pd.DataFrame(all_records)
                elapsed = time.time() - start_time
                
                batch_info = f"第 {batch_num} 批" if batch_num else ""
                self.logger.info(f"✅ {batch_info}Hash数据反序列化完成: {len(df)} 条（并行{max_workers}进程，{elapsed:.2f}s）")
                return df
            
        except Exception as e:
            self.logger.error(f"反序列化Hash数据失败: {e}")
            return None

    def update_hash_incremental(self, hash_key: str, new_data: pd.DataFrame, ttl: Optional[int] = None, 
                                pipeline_batch_size: int = 1000, key_column: str = 'equip_sn') -> bool:
        """
        增量更新Hash数据，使用优化的Pipeline批量处理
        
        Args:
            hash_key: Hash键名
            new_data: 新增数据DataFrame
            ttl: 过期时间（秒）
            pipeline_batch_size: Pipeline批次大小，默认1000条
            key_column: 用作Hash field的列名，默认为'equip_sn'（装备）；角色数据使用'eid'
            
        Returns:
            bool: 是否更新成功
        """
        if not self.is_available() or new_data.empty:
            return False
        
        # 检查DataFrame中是否存在指定的键列
        if key_column not in new_data.columns and key_column != new_data.index.name:
            # 如果key_column不在列中，检查是否是索引
            if key_column not in new_data.columns and not (hasattr(new_data.index, 'name') and new_data.index.name == key_column):
                # 尝试重置索引看是否包含该列
                reset_data = new_data.reset_index()
                if key_column not in reset_data.columns:
                    self.logger.error(f"DataFrame必须包含{key_column}列或将其设为索引")
                    return False
                # 如果重置索引后有该列，使用重置后的数据
                new_data = reset_data
        
        try:
            full_key = self._make_key(hash_key)
            total_rows = len(new_data)
            
            self.logger.info(f"开始增量更新Hash数据: {full_key}，新增: {total_rows} 条，主键列: {key_column}")
            
            # 分批处理，避免Pipeline命令过多导致内存问题
            batch_count = 0
            total_batches = (total_rows + pipeline_batch_size - 1) // pipeline_batch_size
            
            for start_idx in range(0, total_rows, pipeline_batch_size):
                end_idx = min(start_idx + pipeline_batch_size, total_rows)
                batch_data = new_data.iloc[start_idx:end_idx]
                batch_count += 1
                
                # 创建Pipeline
                pipe = self.client.pipeline(transaction=False)  # 非事务模式，性能更好
                
                # 批量添加HSET命令
                for _, row in batch_data.iterrows():
                    # 从指定的列获取键值
                    key_value = str(row[key_column])
                    row_data = row.to_dict()
                    serialized_data = pickle.dumps(row_data)
                    pipe.hset(full_key, key_value, serialized_data)
                
                # 执行Pipeline（一次网络往返执行所有命令）
                pipe.execute()
                
                if total_batches > 1:
                    self.logger.debug(f"批次 {batch_count}/{total_batches} 完成 ({end_idx}/{total_rows})")
            
            # 使用Pipeline优化元数据更新（减少网络往返）
            self._update_hash_metadata_with_pipeline(full_key, ttl)
            
            self.logger.info(f"✅ 增量更新Hash数据完成: {full_key}，新增: {total_rows} 条，批次: {batch_count}")
            return True
            
        except Exception as e:
            self.logger.error(f"增量更新Hash数据失败 {hash_key}: {e}")
            return False
    
    def _update_hash_metadata_with_pipeline(self, full_key: str, ttl: Optional[int] = None):
        """
        使用Pipeline优化元数据更新，减少网络往返
        
        Args:
            full_key: Redis完整键名
            ttl: 过期时间（秒）
        """
        try:
            meta_key = f"{full_key}:meta"
            
            # 创建Pipeline
            pipe = self.client.pipeline(transaction=False)
            
            # 批量执行多个命令
            pipe.hlen(full_key)  # 获取Hash长度
            pipe.exists(meta_key)  # 检查元数据是否存在
            pipe.get(meta_key)  # 获取现有元数据（如果存在）
            
            # 一次性执行所有命令
            results = pipe.execute()
            actual_count = results[0]
            meta_exists = results[1]
            existing_meta = results[2]
            
            # 构建元数据
            if meta_exists and existing_meta:
                metadata = pickle.loads(existing_meta)
                metadata['last_update'] = datetime.now().isoformat()
                metadata['total_count'] = actual_count
            else:
                metadata = {
                    'created_at': datetime.now().isoformat(),
                    'last_update': datetime.now().isoformat(),
                    'total_count': actual_count,
                    'data_type': 'equipment_hash'
                }
            
            # 使用Pipeline更新元数据
            pipe = self.client.pipeline(transaction=False)
            pipe.set(meta_key, pickle.dumps(metadata))
            if ttl:
                pipe.expire(meta_key, ttl)
                pipe.expire(full_key, ttl)
            pipe.execute()
            
            self.logger.debug(f"元数据已更新: {meta_key}, 数据量: {actual_count}")
            
        except Exception as e:
            self.logger.warning(f"更新元数据失败: {e}")


# 全局缓存实例
_redis_cache = None

def get_redis_cache() -> Optional[RedisCache]:
    """获取Redis缓存实例（单例模式）"""
    global _redis_cache
    
    if _redis_cache is None:
        try:
            _redis_cache = RedisCache()
        except Exception as e:
            logging.getLogger(__name__).warning(f"Redis缓存初始化失败: {e}")
            return None
    
    return _redis_cache


def clear_redis_cache():
    """清空全局Redis缓存实例"""
    global _redis_cache
    _redis_cache = None
