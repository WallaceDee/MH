#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Redis Hash数据结构
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app
from src.utils.redis_cache import RedisCache

def test_redis_hash():
    """测试Redis Hash数据"""
    app = create_app()
    
    with app.app_context():
        print("=== 测试Redis Hash数据结构 ===")
        
        # 创建Redis缓存实例
        redis_cache = RedisCache()
        
        if not redis_cache.is_available():
            print("❌ Redis不可用")
            return
        
        print("✅ Redis连接成功")
        
        # 检查装备数据的Hash键
        hash_key = "equipment_market_data_full:hash"
        full_key = redis_cache._make_key(hash_key)
        meta_key = f"{full_key}:meta"
        
        print(f"\n1. 检查Hash键: {full_key}")
        
        # 检查Hash是否存在
        if redis_cache.client.exists(full_key):
            hash_len = redis_cache.client.hlen(full_key)
            print(f"✅ Hash存在，包含 {hash_len} 条记录")
            
            # 获取几个示例记录
            hash_data = redis_cache.client.hgetall(full_key)
            print(f"Hash总字段数: {len(hash_data)}")
            
            # 显示前3个equip_sn
            equip_sns = list(hash_data.keys())[:3]
            for equip_sn in equip_sns:
                print(f"  示例equip_sn: {equip_sn}")
        else:
            print("❌ Hash不存在")
        
        print(f"\n2. 检查元数据键: {meta_key}")
        
        # 检查元数据
        if redis_cache.client.exists(meta_key):
            meta_data = redis_cache.client.get(meta_key)
            if meta_data:
                import pickle
                metadata = pickle.loads(meta_data)
                print("✅ 元数据存在:")
                for key, value in metadata.items():
                    print(f"  {key}: {value}")
            else:
                print("❌ 元数据为空")
        else:
            print("❌ 元数据不存在")
        
        print(f"\n3. 测试get_hash_data方法")
        try:
            df = redis_cache.get_hash_data(hash_key)
            if df is not None and not df.empty:
                print(f"✅ get_hash_data成功，数据量: {len(df)} 条")
                print(f"字段数量: {len(df.columns)}")
                print(f"字段列表: {list(df.columns)}")
            else:
                print("❌ get_hash_data返回空数据")
        except Exception as e:
            print(f"❌ get_hash_data失败: {e}")
        
        print(f"\n4. 检查其他可能的键")
        
        # 检查是否有其他格式的键
        pattern = "equipment_market_data_full*"
        keys = redis_cache.client.keys(pattern)
        print(f"匹配 '{pattern}' 的键:")
        for key in keys:
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
    test_redis_hash()
