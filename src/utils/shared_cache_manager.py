#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角色数据共享缓存管理器
为MarketDataCollector和RoleService提供统一的Redis缓存支持
"""

import json
import hashlib
import logging
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import pandas as pd

try:
    from .redis_cache import get_redis_cache
except ImportError:
    from src.utils.redis_cache import get_redis_cache


class SharedCacheManager:
    """CBG项目共享缓存管理器 - 管理角色、装备等所有数据的Redis缓存"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.redis_cache = None
        
        # 初始化Redis缓存
        if get_redis_cache:
            try:
                self.redis_cache = get_redis_cache()
                if self.redis_cache and self.redis_cache.is_available():
                    self.logger.info("CBG共享缓存管理器初始化成功")
                else:
                    self.redis_cache = None
                    self.logger.info("Redis不可用，使用内存缓存")
            except Exception as e:
                self.redis_cache = None
                self.logger.warning(f"Redis缓存初始化失败: {e}")
        
        # 缓存键前缀
        self.cache_prefixes = {
            'raw_roles': 'roles_raw:',      # 原始角色数据（用于get_roles）
            'market_data': 'market_data:',   # 市场数据（用于MarketDataCollector）
            'role_features': 'role_features:', # 角色特征数据
            'role_details': 'role_detail:',   # 角色详情数据
            'equip_market': 'equip_market:', # 装备市场数据（用于EquipMarketDataCollector）
            'equip_features': 'equip_features:' # 装备特征数据
        }
        
        # 默认TTL设置（秒）
        self.default_ttl = {
            'raw_roles': 3600 * 2,      # 原始角色数据：2小时
            'market_data': 3600 * 6,    # 市场数据：6小时
            'role_features': 3600 * 4,  # 角色特征：4小时
            'role_details': 3600 * 1,   # 角色详情：1小时
            'equip_market': 3600 * 4,   # 装备市场数据：4小时
            'equip_features': 3600 * 2  # 装备特征数据：2小时
        }
    
    def is_available(self) -> bool:
        """检查缓存是否可用"""
        return self.redis_cache is not None and self.redis_cache.is_available()
    
    def _generate_cache_key(self, cache_type: str, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            cache_type: 缓存类型 ('raw_roles', 'market_data', 'role_features', 'role_details')
            **kwargs: 缓存参数
            
        Returns:
            str: 缓存键
        """
        if cache_type not in self.cache_prefixes:
            raise ValueError(f"不支持的缓存类型: {cache_type}")
        
        # 创建缓存数据字典
        cache_data = dict(kwargs)
        cache_data['version'] = '1.0'
        
        # 生成哈希
        cache_str = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        cache_hash = hashlib.md5(cache_str.encode('utf-8')).hexdigest()[:16]
        
        prefix = self.cache_prefixes[cache_type]
        return f"{prefix}{cache_hash}"
    
    def get_raw_roles_cache(self, filters: Dict[str, Any], page: int = 1, 
                           page_size: int = 15, role_type: str = 'normal') -> Optional[Dict]:
        """
        获取原始角色数据缓存（用于get_roles）
        
        Args:
            filters: 筛选条件
            page: 页码
            page_size: 每页数量
            role_type: 角色类型
            
        Returns:
            Dict: 缓存的角色数据，包含roles列表和total数量
        """
        if not self.is_available():
            return None
        
        try:
            cache_key = self._generate_cache_key(
                'raw_roles',
                filters=filters,
                page=page,
                page_size=page_size,
                role_type=role_type
            )
            
            cached_data = self.redis_cache.get(cache_key)
            if cached_data:
                self.logger.info(f"从Redis获取原始角色数据: {cache_key}")
                return cached_data
            
        except Exception as e:
            self.logger.warning(f"获取原始角色缓存失败: {e}")
        
        return None
    
    def set_raw_roles_cache(self, filters: Dict[str, Any], page: int, page_size: int,
                           role_type: str, roles_data: List[Dict], total: int) -> bool:
        """
        设置原始角色数据缓存
        
        Args:
            filters: 筛选条件
            page: 页码
            page_size: 每页数量
            role_type: 角色类型
            roles_data: 角色数据列表
            total: 总数量
            
        Returns:
            bool: 是否设置成功
        """
        if not self.is_available():
            return False
        
        try:
            cache_key = self._generate_cache_key(
                'raw_roles',
                filters=filters,
                page=page,
                page_size=page_size,
                role_type=role_type
            )
            
            cache_data = {
                'data': roles_data,  # 使用'data'字段而不是'roles'
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size,
                'message': "成功获取角色数据",
                'cached_at': datetime.now().isoformat()
            }
            
            ttl = self.default_ttl['raw_roles']
            success = self.redis_cache.set(cache_key, cache_data, ttl)
            
            if success:
                self.logger.info(f"原始角色数据已缓存: {cache_key}, 数据量: {len(roles_data)}, TTL: {ttl}秒")
            
            return success
            
        except Exception as e:
            self.logger.warning(f"设置原始角色缓存失败: {e}")
            return False
    
    def get_market_data_cache(self, filters: Optional[Dict[str, Any]] = None, 
                             max_records: int = 9999) -> Optional[pd.DataFrame]:
        """
        获取市场数据缓存（用于MarketDataCollector）
        
        Args:
            filters: 筛选条件
            max_records: 最大记录数
            
        Returns:
            pd.DataFrame: 缓存的市场数据
        """
        if not self.is_available():
            return None
        
        try:
            cache_key = self._generate_cache_key(
                'market_data',
                filters=filters or {},
                max_records=max_records
            )
            
            cached_data = self.redis_cache.get(cache_key)
            if cached_data is not None:
                self.logger.info(f"从Redis获取市场数据: {cache_key}")
                return cached_data
            
        except Exception as e:
            self.logger.warning(f"获取市场数据缓存失败: {e}")
        
        return None
    
    def set_market_data_cache(self, filters: Optional[Dict[str, Any]], max_records: int,
                             data: pd.DataFrame) -> bool:
        """
        设置市场数据缓存
        
        Args:
            filters: 筛选条件
            max_records: 最大记录数
            data: 市场数据
            
        Returns:
            bool: 是否设置成功
        """
        if not self.is_available() or data.empty:
            return False
        
        try:
            cache_key = self._generate_cache_key(
                'market_data',
                filters=filters or {},
                max_records=max_records
            )
            
            ttl = self.default_ttl['market_data']
            success = self.redis_cache.set(cache_key, data, ttl)
            
            if success:
                self.logger.info(f"市场数据已缓存: {cache_key}, 数据量: {len(data)}, TTL: {ttl}秒")
            
            return success
            
        except Exception as e:
            self.logger.warning(f"设置市场数据缓存失败: {e}")
            return False
    
    def get_role_features_cache(self, eid: str) -> Optional[Dict]:
        """
        获取角色特征缓存
        
        Args:
            eid: 角色ID
            
        Returns:
            Dict: 角色特征数据
        """
        if not self.is_available():
            return None
        
        try:
            cache_key = self._generate_cache_key('role_features', eid=eid)
            cached_data = self.redis_cache.get(cache_key)
            
            if cached_data:
                self.logger.info(f"从Redis获取角色特征: {eid}")
                return cached_data
            
        except Exception as e:
            self.logger.warning(f"获取角色特征缓存失败: {e}")
        
        return None
    
    def set_role_features_cache(self, eid: str, features: Dict) -> bool:
        """
        设置角色特征缓存
        
        Args:
            eid: 角色ID
            features: 特征数据
            
        Returns:
            bool: 是否设置成功
        """
        if not self.is_available():
            return False
        
        try:
            cache_key = self._generate_cache_key('role_features', eid=eid)
            ttl = self.default_ttl['role_features']
            success = self.redis_cache.set(cache_key, features, ttl)
            
            if success:
                self.logger.info(f"角色特征已缓存: {eid}, TTL: {ttl}秒")
            
            return success
            
        except Exception as e:
            self.logger.warning(f"设置角色特征缓存失败: {e}")
            return False
    
    def get_role_detail_cache(self, eid: str) -> Optional[Dict]:
        """
        获取角色详情缓存
        
        Args:
            eid: 角色ID
            
        Returns:
            Dict: 角色详情数据
        """
        if not self.is_available():
            return None
        
        try:
            cache_key = self._generate_cache_key('role_details', eid=eid)
            cached_data = self.redis_cache.get(cache_key)
            
            if cached_data:
                self.logger.info(f"从Redis获取角色详情: {eid}")
                return cached_data
            
        except Exception as e:
            self.logger.warning(f"获取角色详情缓存失败: {e}")
        
        return None
    
    def set_role_detail_cache(self, eid: str, detail_data: Dict) -> bool:
        """
        设置角色详情缓存
        
        Args:
            eid: 角色ID
            detail_data: 详情数据
            
        Returns:
            bool: 是否设置成功
        """
        if not self.is_available():
            return False
        
        try:
            cache_key = self._generate_cache_key('role_details', eid=eid)
            ttl = self.default_ttl['role_details']
            success = self.redis_cache.set(cache_key, detail_data, ttl)
            
            if success:
                self.logger.info(f"角色详情已缓存: {eid}, TTL: {ttl}秒")
            
            return success
            
        except Exception as e:
            self.logger.warning(f"设置角色详情缓存失败: {e}")
            return False
    
    def get_equip_market_cache(self, **kwargs) -> Optional[pd.DataFrame]:
        """
        获取装备市场数据缓存
        
        Args:
            **kwargs: 装备筛选条件（kindid, level_range, max_records等）
            
        Returns:
            pd.DataFrame: 缓存的装备市场数据
        """
        if not self.is_available():
            return None
        
        try:
            cache_key = self._generate_cache_key('equip_market', **kwargs)
            cached_data = self.redis_cache.get(cache_key)
            
            if cached_data is not None:
                self.logger.info(f"从Redis获取装备市场数据: {cache_key}")
                return cached_data
            
        except Exception as e:
            self.logger.warning(f"获取装备市场缓存失败: {e}")
        
        return None
    
    def set_equip_market_cache(self, data: pd.DataFrame, **kwargs) -> bool:
        """
        设置装备市场数据缓存
        
        Args:
            data: 装备市场数据
            **kwargs: 装备筛选条件
            
        Returns:
            bool: 是否设置成功
        """
        if not self.is_available() or data.empty:
            return False
        
        try:
            cache_key = self._generate_cache_key('equip_market', **kwargs)
            ttl = self.default_ttl['equip_market']
            success = self.redis_cache.set(cache_key, data, ttl)
            
            if success:
                self.logger.info(f"装备市场数据已缓存: {cache_key}, 数据量: {len(data)}, TTL: {ttl}秒")
            
            return success
            
        except Exception as e:
            self.logger.warning(f"设置装备市场缓存失败: {e}")
            return False
    
    def get_equip_features_cache(self, equip_id: str) -> Optional[Dict]:
        """
        获取装备特征缓存
        
        Args:
            equip_id: 装备ID
            
        Returns:
            Dict: 装备特征数据
        """
        if not self.is_available():
            return None
        
        try:
            cache_key = self._generate_cache_key('equip_features', equip_id=equip_id)
            cached_data = self.redis_cache.get(cache_key)
            
            if cached_data:
                self.logger.info(f"从Redis获取装备特征: {equip_id}")
                return cached_data
            
        except Exception as e:
            self.logger.warning(f"获取装备特征缓存失败: {e}")
        
        return None
    
    def set_equip_features_cache(self, equip_id: str, features: Dict) -> bool:
        """
        设置装备特征缓存
        
        Args:
            equip_id: 装备ID
            features: 特征数据
            
        Returns:
            bool: 是否设置成功
        """
        if not self.is_available():
            return False
        
        try:
            cache_key = self._generate_cache_key('equip_features', equip_id=equip_id)
            ttl = self.default_ttl['equip_features']
            success = self.redis_cache.set(cache_key, features, ttl)
            
            if success:
                self.logger.info(f"装备特征已缓存: {equip_id}, TTL: {ttl}秒")
            
            return success
            
        except Exception as e:
            self.logger.warning(f"设置装备特征缓存失败: {e}")
            return False
    
    def clear_all_role_cache(self):
        """清空所有角色相关缓存"""
        if not self.is_available():
            return
        
        try:
            total_cleared = 0
            for cache_type in self.cache_prefixes.keys():
                pattern = f"{self.cache_prefixes[cache_type]}*"
                cleared = self.redis_cache.clear_pattern(pattern)
                total_cleared += cleared
                if cleared > 0:
                    self.logger.info(f"清空{cache_type}缓存: {cleared}个键")
            
            print(f"已清空所有角色缓存，总计: {total_cleared} 个键")
            
        except Exception as e:
            self.logger.error(f"清空角色缓存失败: {e}")
    
    def clear_cache_by_type(self, cache_type: str):
        """按类型清空缓存"""
        if not self.is_available() or cache_type not in self.cache_prefixes:
            return
        
        try:
            pattern = f"{self.cache_prefixes[cache_type]}*"
            cleared = self.redis_cache.clear_pattern(pattern)
            print(f"已清空{cache_type}缓存: {cleared} 个键")
            
        except Exception as e:
            self.logger.error(f"清空{cache_type}缓存失败: {e}")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        if not self.is_available():
            return {'available': False}
        
        try:
            stats = {
                'available': True,
                'redis_stats': self.redis_cache.get_cache_stats(),
                'memory_usage': self.redis_cache.get_memory_usage(),
                'cache_types': {}
            }
            
            # 统计各类型缓存数量
            for cache_type, prefix in self.cache_prefixes.items():
                try:
                    pattern = f"{prefix}*"
                    keys = self.redis_cache.client.keys(self.redis_cache._make_key(pattern))
                    stats['cache_types'][cache_type] = {
                        'count': len(keys),
                        'ttl_hours': self.default_ttl[cache_type] / 3600
                    }
                except Exception:
                    stats['cache_types'][cache_type] = {'count': 0, 'ttl_hours': 0}
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取缓存统计失败: {e}")
            return {'available': False, 'error': str(e)}
    
    def invalidate_related_cache(self, eid: str = None, role_type: str = None):
        """
        失效相关缓存
        
        Args:
            eid: 角色ID，如果提供则失效该角色的所有缓存
            role_type: 角色类型，如果提供则失效该类型的相关缓存
        """
        if not self.is_available():
            return
        
        try:
            if eid:
                # 失效特定角色的缓存
                detail_key = self._generate_cache_key('role_details', eid=eid)
                feature_key = self._generate_cache_key('role_features', eid=eid)
                
                deleted = 0
                deleted += self.redis_cache.delete(detail_key)
                deleted += self.redis_cache.delete(feature_key)
                
                if deleted > 0:
                    self.logger.info(f"已失效角色{eid}的缓存: {deleted}个键")
            
            if role_type:
                # 失效特定类型的缓存
                if role_type == 'empty':
                    # 失效市场数据缓存
                    self.clear_cache_by_type('market_data')
                elif role_type == 'normal':
                    # 失效原始角色数据缓存
                    self.clear_cache_by_type('raw_roles')
                    
        except Exception as e:
            self.logger.error(f"缓存失效操作失败: {e}")


# 全局共享缓存管理器实例
_shared_cache_manager = None

def get_shared_cache_manager() -> SharedCacheManager:
    """获取CBG项目共享缓存管理器实例（单例模式）"""
    global _shared_cache_manager
    
    if _shared_cache_manager is None:
        _shared_cache_manager = SharedCacheManager()
    
    return _shared_cache_manager