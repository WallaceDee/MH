#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试宠物装备市场数据采集器缓存优化功能
"""

import sys
import os
import time
import pandas as pd

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evaluator.mark_anchor.pet_equip.pet_equip_market_data_collector import PetEquipMarketDataCollector


def test_cache_optimization():
    """测试缓存优化功能"""
    print("=" * 60)
    print("测试宠物装备市场数据采集器缓存优化功能")
    print("=" * 60)
    
    # 创建采集器实例
    collector = PetEquipMarketDataCollector()
    
    print("\n1. 第一次获取数据（应该从装备数据采集器读取并缓存）")
    start_time = time.time()
    data1 = collector.get_market_data(fangyu=1, limit=100)  # 铠甲类型
    elapsed1 = time.time() - start_time
    print(f"第一次获取数据耗时: {elapsed1:.3f}秒，获取到 {len(data1)} 条数据")
    
    print("\n2. 第二次获取相同数据（应该使用实例缓存）")
    start_time = time.time()
    data2 = collector.get_market_data(fangyu=1, limit=100)  # 铠甲类型
    elapsed2 = time.time() - start_time
    print(f"第二次获取数据耗时: {elapsed2:.3f}秒，获取到 {len(data2)} 条数据")
    
    print("\n3. 第三次获取不同类型数据（应该使用实例缓存过滤）")
    start_time = time.time()
    data3 = collector.get_market_data(speed=1, limit=100)  # 项圈类型
    elapsed3 = time.time() - start_time
    print(f"第三次获取数据耗时: {elapsed3:.3f}秒，获取到 {len(data3)} 条数据")
    
    print("\n4. 第四次获取护腕类型数据（应该使用实例缓存过滤）")
    start_time = time.time()
    data4 = collector.get_market_data(limit=200)  # 护腕类型（默认）
    elapsed4 = time.time() - start_time
    print(f"第四次获取数据耗时: {elapsed4:.3f}秒，获取到 {len(data4)} 条数据")
    
    print("\n5. 清除缓存后重新获取数据")
    collector.clear_cache()
    start_time = time.time()
    data5 = collector.get_market_data(fangyu=1, limit=100)
    elapsed5 = time.time() - start_time
    print(f"清除缓存后获取数据耗时: {elapsed5:.3f}秒，获取到 {len(data5)} 条数据")
    
    # 验证数据一致性
    print("\n6. 验证数据一致性")
    if not data1.empty and not data2.empty:
        # 检查数据是否一致（忽略顺序）
        data1_sorted = data1.sort_values('equip_sn').reset_index(drop=True)
        data2_sorted = data2.sort_values('equip_sn').reset_index(drop=True)
        
        if data1_sorted.equals(data2_sorted):
            print("✅ 缓存数据与原始数据一致")
        else:
            print("❌ 缓存数据与原始数据不一致")
    
    # 性能对比
    print("\n7. 性能对比分析")
    print(f"第一次获取（无缓存）: {elapsed1:.3f}秒")
    print(f"第二次获取（有缓存）: {elapsed2:.3f}秒")
    if elapsed1 > 0:
        speedup = elapsed1 / elapsed2 if elapsed2 > 0 else float('inf')
        print(f"缓存加速比: {speedup:.2f}x")
    
    print("\n8. 缓存状态检查")
    if collector._cached_pet_equip_data is not None:
        print(f"✅ 实例缓存有效，包含 {len(collector._cached_pet_equip_data)} 条宠物装备数据")
        print(f"缓存时间: {collector._cache_timestamp}")
    else:
        print("❌ 实例缓存为空")
    
    print("\n9. 测试不同装备类型过滤")
    print("测试铠甲类型过滤...")
    armor_data = collector.get_market_data(fangyu=1, limit=50)
    print(f"铠甲类型数据: {len(armor_data)} 条")
    
    print("测试项圈类型过滤...")
    collar_data = collector.get_market_data(speed=1, limit=50)
    print(f"项圈类型数据: {len(collar_data)} 条")
    
    print("测试护腕类型过滤...")
    bracer_data = collector.get_market_data(limit=50)
    print(f"护腕类型数据: {len(bracer_data)} 条")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_cache_optimization()
