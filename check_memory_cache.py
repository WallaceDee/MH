#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查内存缓存状态
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def check_memory_cache():
    """检查内存缓存状态"""
    print("=== 检查EquipMarketDataCollector内存缓存状态 ===")
    
    try:
        from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
        
        # 获取实例
        collector = EquipMarketDataCollector.get_instance()
        print("✅ 成功获取EquipMarketDataCollector实例")
        
        # 检查内存缓存
        memory_data = collector._get_existing_data_from_memory()
        
        if memory_data is not None and not memory_data.empty:
            print(f"✅ 内存缓存存在，数据量: {len(memory_data)} 条")
            print(f"   列数: {len(memory_data.columns)}")
            print(f"   列名: {list(memory_data.columns)[:5]}...")  # 显示前5列
            
            # 显示最近几条数据的equip_sn
            if 'equip_sn' in memory_data.columns:
                recent_equips = memory_data['equip_sn'].tail(5).tolist()
                print(f"   最近5条数据的equip_sn: {recent_equips}")
            
            # 检查是否有测试数据
            if 'equip_sn' in memory_data.columns:
                test_equips = memory_data[memory_data['equip_sn'].str.contains('test_', na=False)]
                if len(test_equips) > 0:
                    print(f"   包含测试数据: {len(test_equips)} 条")
                    print(f"   测试数据equip_sn: {test_equips['equip_sn'].tolist()}")
                else:
                    print("   未找到测试数据")
        else:
            print("⚠️ 内存缓存为空或不存在")
        
        # 检查Redis缓存
        print("\n=== 检查Redis缓存状态 ===")
        try:
            redis_data = collector.get_full_data()
            if redis_data is not None and not redis_data.empty:
                print(f"✅ Redis缓存存在，数据量: {len(redis_data)} 条")
            else:
                print("⚠️ Redis缓存为空或不存在")
        except Exception as e:
            print(f"❌ Redis缓存检查失败: {e}")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_memory_cache()
