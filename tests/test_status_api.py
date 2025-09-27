#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试状态接口的Redis数据获取
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app
from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector

def test_status_api():
    """测试状态接口的Redis数据获取"""
    app = create_app()
    
    with app.app_context():
        print("=== 测试状态接口Redis数据获取 ===")
        
        # 获取采集器实例
        collector = EquipMarketDataCollector.get_instance()
        
        print(f"采集器实例ID: {id(collector)}")
        print(f"缓存键名: {collector._full_cache_key}")
        
        # 测试Redis元数据获取
        print("\n1. 测试Redis元数据获取...")
        try:
            if collector.redis_cache and collector.redis_cache.is_available():
                meta_key = f"{collector._full_cache_key}:meta"
                print(f"元数据键名: {meta_key}")
                
                metadata = collector.redis_cache.get(meta_key)
                print(f"元数据: {metadata}")
                
                if metadata:
                    total_count = metadata.get('total_count', 0)
                    total_rows = metadata.get('total_rows', 0)
                    print(f"total_count: {total_count}")
                    print(f"total_rows: {total_rows}")
                    
                    # 使用修复后的逻辑
                    redis_count = metadata.get('total_count', metadata.get('total_rows', 0))
                    print(f"最终Redis数量: {redis_count}")
                else:
                    print("❌ 元数据为空")
            else:
                print("❌ Redis不可用")
        except Exception as e:
            print(f"❌ 获取元数据失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n2. 测试Hash数据直接获取...")
        try:
            if collector.redis_cache and collector.redis_cache.is_available():
                hash_key = f"{collector._full_cache_key}:hash"
                hash_len = collector.redis_cache.client.hlen(hash_key)
                print(f"Hash键名: {hash_key}")
                print(f"Hash长度: {hash_len}")
        except Exception as e:
            print(f"❌ 获取Hash长度失败: {e}")

if __name__ == "__main__":
    test_status_api()
