#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试内存缓存增量更新功能
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

def test_memory_cache_incremental_update():
    """测试内存缓存增量更新功能"""
    print("\n=== 测试内存缓存增量更新功能 ===")
    
    try:
        from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
        
        # 创建采集器实例
        collector = EquipMarketDataCollector()
        
        print("1. 检查内存缓存状态...")
        memory_data = collector._get_existing_data_from_memory()
        if memory_data is not None:
            print(f"   内存缓存数据量: {len(memory_data)} 条")
        else:
            print("   内存缓存为空")
        
        print("\n2. 测试获取最后更新时间（优先从内存缓存）...")
        last_update_time = collector._get_last_cache_update_time()
        if last_update_time:
            print(f"   最后更新时间: {last_update_time}")
        else:
            print("   未找到最后更新时间")
        
        print("\n3. 测试增量更新状态（优先从内存缓存）...")
        status = collector.get_incremental_update_status()
        print(f"   状态: {status}")
        print(f"   数据源: {status.get('data_source', 'unknown')}")
        print(f"   内存缓存大小: {status.get('memory_cache_size', 0)} 条")
        
        print("\n4. 测试自动增量更新...")
        success = collector.auto_incremental_update()
        print(f"   结果: {success}")
        
        print("\n5. 检查更新后的内存缓存状态...")
        memory_data = collector._get_existing_data_from_memory()
        if memory_data is not None:
            print(f"   内存缓存数据量: {len(memory_data)} 条")
        else:
            print("   内存缓存为空")
        
        print("\n6. 测试基于时间戳的增量更新...")
        last_update_time = datetime.now() - timedelta(hours=1)
        success = collector.incremental_update(last_update_time)
        print(f"   结果: {success}")
        
        print("\n7. 检查最终内存缓存状态...")
        memory_data = collector._get_existing_data_from_memory()
        if memory_data is not None:
            print(f"   内存缓存数据量: {len(memory_data)} 条")
        else:
            print("   内存缓存为空")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()

def test_memory_cache_workflow():
    """测试内存缓存工作流程"""
    print("\n=== 测试内存缓存工作流程 ===")
    
    try:
        from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
        import pandas as pd
        
        # 创建采集器实例
        collector = EquipMarketDataCollector()
        
        print("1. 模拟内存缓存数据...")
        # 创建模拟数据
        mock_data = pd.DataFrame({
            'equip_sn': ['test_001', 'test_002'],
            'price': [1000, 2000],
            'update_time': [datetime.now(), datetime.now()]
        })
        
        # 设置内存缓存
        collector._full_data_cache = mock_data
        print(f"   设置内存缓存数据: {len(mock_data)} 条")
        
        print("\n2. 测试从内存缓存获取数据...")
        memory_data = collector._get_existing_data_from_memory()
        if memory_data is not None:
            print(f"   获取到内存缓存数据: {len(memory_data)} 条")
        else:
            print("   获取内存缓存数据失败")
        
        print("\n3. 测试同步到Redis...")
        success = collector._sync_memory_cache_to_redis(mock_data)
        print(f"   同步结果: {success}")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("内存缓存增量更新功能测试")
    print("=" * 50)
    
    # 测试内存缓存增量更新功能
    test_memory_cache_incremental_update()
    
    # 测试内存缓存工作流程
    test_memory_cache_workflow()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n新的增量更新流程:")
    print("1. 优先从内存缓存获取现有数据")
    print("2. 如果内存缓存为空，从Redis加载到内存")
    print("3. 将增量数据合并到内存缓存")
    print("4. 更新内存缓存变量")
    print("5. 同步内存缓存到Redis")

if __name__ == '__main__':
    main()
