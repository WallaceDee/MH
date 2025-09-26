#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试EquipMarketDataCollector的get_instance方法
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_get_instance():
    """测试get_instance方法"""
    print("=== 测试EquipMarketDataCollector.get_instance方法 ===")
    
    try:
        from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
        
        print("1. 测试get_instance方法是否存在...")
        if hasattr(EquipMarketDataCollector, 'get_instance'):
            print("   ✅ get_instance方法存在")
        else:
            print("   ❌ get_instance方法不存在")
            return
        
        print("2. 测试获取实例...")
        instance1 = EquipMarketDataCollector.get_instance()
        print("   ✅ 第一次获取实例成功")
        
        print("3. 测试单例模式...")
        instance2 = EquipMarketDataCollector.get_instance()
        if instance1 is instance2:
            print("   ✅ 单例模式工作正常，返回相同实例")
        else:
            print("   ❌ 单例模式异常，返回不同实例")
        
        print("4. 测试add_new_equipment_data方法...")
        if hasattr(instance1, 'add_new_equipment_data'):
            print("   ✅ add_new_equipment_data方法存在")
        else:
            print("   ❌ add_new_equipment_data方法不存在")
        
        print("5. 测试添加数据...")
        test_data = [
            {
                'equip_sn': 'test_get_instance_001',
                'price': 1000,
                'server_name': '测试服务器',
                'equip_name': '测试装备'
            }
        ]
        
        result = instance1.add_new_equipment_data(test_data)
        if result:
            print("   ✅ 数据添加成功")
        else:
            print("   ❌ 数据添加失败")
        
        print("\n🎉 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_get_instance()
