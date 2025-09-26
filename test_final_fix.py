#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试最终修复
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_final_fix():
    """测试最终修复"""
    print("=== 测试最终修复 ===")
    
    try:
        from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
        
        # 获取实例
        collector = EquipMarketDataCollector.get_instance()
        print("✅ 成功获取EquipMarketDataCollector实例")
        
        # 清空内存缓存
        collector._full_data_cache = None
        print("📊 已清空内存缓存")
        
        print("\n1. 测试获取内存缓存数据...")
        memory_data = collector._get_existing_data_from_memory()
        
        if memory_data is not None and not memory_data.empty:
            print(f"✅ 成功获取数据，数据量: {len(memory_data)} 条")
        else:
            print("⚠️ 未能获取数据")
        
        print("\n2. 测试获取最后更新时间...")
        last_update_time = collector._get_last_cache_update_time()
        
        if last_update_time:
            print(f"✅ 成功获取最后更新时间: {last_update_time}")
        else:
            print("⚠️ 未能获取最后更新时间")
        
        print("\n🎉 最终修复测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_final_fix()
