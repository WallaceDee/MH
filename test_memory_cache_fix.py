#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试内存缓存修复
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_memory_cache_auto_load():
    """测试内存缓存自动加载功能"""
    print("=== 测试内存缓存自动加载功能 ===")
    
    try:
        from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
        
        # 获取实例
        collector = EquipMarketDataCollector.get_instance()
        print("✅ 成功获取EquipMarketDataCollector实例")
        
        # 清空内存缓存
        collector._full_data_cache = None
        print("📊 已清空内存缓存")
        
        # 测试获取数据（应该自动从Redis加载）
        print("\n1. 测试从空内存缓存获取数据...")
        memory_data = collector._get_existing_data_from_memory()
        
        if memory_data is not None and not memory_data.empty:
            print(f"✅ 成功从Redis自动加载数据到内存缓存，数据量: {len(memory_data)} 条")
            
            # 验证内存缓存已更新
            if collector._full_data_cache is not None and not collector._full_data_cache.empty:
                print("✅ 内存缓存已正确更新")
            else:
                print("❌ 内存缓存未正确更新")
        else:
            print("⚠️ 未能从Redis加载数据到内存缓存")
        
        # 测试增量更新状态
        print("\n2. 测试增量更新状态...")
        status = collector.get_incremental_update_status()
        
        print(f"   数据源: {status.get('data_source', 'unknown')}")
        print(f"   内存缓存大小: {status.get('memory_cache_size', 0)}")
        print(f"   最后更新时间: {status.get('last_update_time', 'None')}")
        print(f"   MySQL最新时间: {status.get('mysql_latest_time', 'None')}")
        print(f"   有新数据: {status.get('has_new_data', False)}")
        print(f"   新数据数量: {status.get('new_data_count', 0)}")
        
        if status.get('has_new_data', False):
            print("✅ 检测到新数据，可以进行增量更新")
        else:
            print("ℹ️ 没有新数据需要更新")
        
        print("\n🎉 内存缓存自动加载测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_memory_cache_auto_load()
