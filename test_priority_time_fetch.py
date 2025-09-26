#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试优先级时间获取：内存缓存 → Redis → MySQL
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_priority_time_fetch():
    """测试优先级时间获取"""
    print("=== 测试优先级时间获取 ===")
    
    try:
        from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
        
        # 获取实例
        collector = EquipMarketDataCollector.get_instance()
        print("✅ 成功获取EquipMarketDataCollector实例")
        
        # 清空内存缓存
        collector._full_data_cache = None
        print("📊 已清空内存缓存")
        
        print("\n1. 测试获取最后更新时间（优先级：内存缓存 → Redis → MySQL）...")
        last_update_time = collector._get_last_cache_update_time()
        
        if last_update_time:
            print(f"✅ 成功获取最后更新时间: {last_update_time}")
            print(f"   时间来源: 根据日志判断来源")
        else:
            print("⚠️ 未能获取最后更新时间")
        
        print("\n2. 测试获取内存缓存数据（优先级：内存缓存 → Redis → MySQL）...")
        memory_data = collector._get_existing_data_from_memory()
        
        if memory_data is not None and not memory_data.empty:
            print(f"✅ 成功获取数据，数据量: {len(memory_data)} 条")
            print(f"   数据来源: 根据日志判断来源")
            
            # 检查是否有update_time列
            if 'update_time' in memory_data.columns:
                print("✅ 数据包含update_time列")
            else:
                print("⚠️ 数据不包含update_time列")
        else:
            print("⚠️ 未能获取数据")
        
        print("\n3. 测试增量更新状态...")
        status = collector.get_incremental_update_status()
        
        print(f"   数据源: {status.get('data_source', 'unknown')}")
        print(f"   内存缓存大小: {status.get('memory_cache_size', 0)}")
        print(f"   最后更新时间: {status.get('last_update_time', 'None')}")
        print(f"   MySQL最新时间: {status.get('mysql_latest_time', 'None')}")
        print(f"   有新数据: {status.get('has_new_data', False)}")
        print(f"   新数据数量: {status.get('new_data_count', 0)}")
        
        print("\n🎉 优先级时间获取测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_priority_time_fetch()
