#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理旧的Redis分块数据，保留Hash结构数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app
from src.utils.redis_cache import RedisCache

def cleanup_old_redis_data():
    """清理旧的Redis分块数据"""
    app = create_app()
    
    with app.app_context():
        print("=== 清理旧的Redis分块数据 ===")
        
        # 创建Redis缓存实例
        redis_cache = RedisCache()
        
        if not redis_cache.is_available():
            print("❌ Redis不可用")
            return
        
        print("✅ Redis连接成功")
        
        # 要清理的旧数据模式
        old_patterns = [
            "equipment_market_data_full:meta",  # 旧的分块元数据
            "equipment_market_data_full:chunk_*",  # 旧的分块数据
        ]
        
        total_cleared = 0
        
        for pattern in old_patterns:
            print(f"\n🔍 查找匹配模式: {pattern}")
            
            # 构建完整键名
            if "*" in pattern:
                # 通配符模式
                full_pattern = redis_cache._make_key(pattern)
                keys = redis_cache.client.keys(full_pattern)
            else:
                # 精确键名
                full_key = redis_cache._make_key(pattern)
                keys = [full_key] if redis_cache.client.exists(full_key) else []
            
            if keys:
                print(f"找到 {len(keys)} 个匹配的键:")
                for key in keys:
                    key_type = redis_cache.client.type(key).decode()
                    if key_type == 'string':
                        key_size = redis_cache.client.strlen(key)
                        print(f"  {key} (string, {key_size} bytes)")
                    elif key_type == 'list':
                        list_len = redis_cache.client.llen(key)
                        print(f"  {key} (list, {list_len} 条记录)")
                    else:
                        print(f"  {key} ({key_type})")
                
                # 删除这些键
                deleted_count = redis_cache.client.delete(*keys)
                print(f"✅ 已删除 {deleted_count} 个键")
                total_cleared += deleted_count
            else:
                print("没有找到匹配的键")
        
        print(f"\n📊 清理完成，总共删除了 {total_cleared} 个键")
        
        # 显示清理后的Redis状态
        print("\n🔍 清理后的Redis状态:")
        remaining_keys = redis_cache.client.keys("*equipment_market_data_full*")
        print(f"剩余的equipment_market_data_full相关键: {len(remaining_keys)} 个")
        for key in remaining_keys:
            key_type = redis_cache.client.type(key).decode()
            if key_type == 'hash':
                hash_len = redis_cache.client.hlen(key)
                print(f"  {key} (hash, {hash_len} 条记录)")
            elif key_type == 'string':
                print(f"  {key} (string)")
            elif key_type == 'list':
                list_len = redis_cache.client.llen(key)
                print(f"  {key} (list, {list_len} 条记录)")
            else:
                print(f"  {key} ({key_type})")

if __name__ == "__main__":
    cleanup_old_redis_data()
