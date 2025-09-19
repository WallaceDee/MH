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


class RedisCache:
    """Redis缓存管理器"""
    
    def __init__(self, 
                 host: str = 'localhost',
                 port: int = 6379, 
                 db: int = 0,
                 password: Optional[str] = None,
                 decode_responses: bool = False,
                 socket_timeout: float = 5.0,
                 socket_connect_timeout: float = 5.0,
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
            expire_time = ttl or self.default_ttl
            result = self.client.setex(full_key, expire_time, serialized_value)
            
            if result:
                self.logger.debug(f"缓存设置成功: {key}, TTL: {expire_time}秒")
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
