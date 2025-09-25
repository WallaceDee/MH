#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试爬虫应用上下文修复
"""

import sys
import os
import unittest
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

def test_equipment_spider_app_context():
    """测试装备爬虫应用上下文修复"""
    print("\n=== 测试装备爬虫应用上下文修复 ===")
    
    try:
        from src.spider.equip import CBGEquipSpider
        
        # 创建装备爬虫实例
        spider = CBGEquipSpider()
        
        # 模拟装备数据
        mock_equipments = [
            {
                'equip_sn': 'test_equip_001',
                'price': 1000,
                'server_name': '测试服务器',
                'update_time': datetime.now(),
                'equip_level': 80,
                'kindid': 1
            },
            {
                'equip_sn': 'test_equip_002',
                'price': 2000,
                'server_name': '测试服务器',
                'update_time': datetime.now(),
                'equip_level': 90,
                'kindid': 2
            }
        ]
        
        print("1. 测试装备数据保存（无应用上下文）...")
        # 在没有应用上下文的情况下测试
        result = spider.save_equipment_data(mock_equipments)
        print(f"   保存结果: {result}")
        
        if result > 0:
            print("   ✅ 装备数据保存成功（应用上下文修复有效）")
        else:
            print("   ⚠️ 装备数据保存失败或跳过")
        
    except Exception as e:
        print(f"❌ 装备爬虫测试异常: {e}")
        import traceback
        traceback.print_exc()

def test_pet_spider_app_context():
    """测试召唤兽爬虫应用上下文修复"""
    print("\n=== 测试召唤兽爬虫应用上下文修复 ===")
    
    try:
        from src.spider.pet import CBGPetSpider
        
        # 创建召唤兽爬虫实例
        spider = CBGPetSpider()
        
        # 模拟召唤兽数据
        mock_pets = [
            {
                'eid': 'test_pet_001',
                'equip_name': '测试召唤兽1',
                'price': 500,
                'server_name': '测试服务器',
                'update_time': datetime.now()
            },
            {
                'eid': 'test_pet_002',
                'equip_name': '测试召唤兽2',
                'price': 800,
                'server_name': '测试服务器',
                'update_time': datetime.now()
            }
        ]
        
        print("1. 测试召唤兽数据保存（无应用上下文）...")
        # 在没有应用上下文的情况下测试
        result = spider.save_pet_data(mock_pets)
        print(f"   保存结果: {result}")
        
        if result > 0:
            print("   ✅ 召唤兽数据保存成功（应用上下文修复有效）")
        else:
            print("   ⚠️ 召唤兽数据保存失败或跳过")
        
    except Exception as e:
        print(f"❌ 召唤兽爬虫测试异常: {e}")
        import traceback
        traceback.print_exc()

def test_spider_with_existing_context():
    """测试在已有应用上下文中的爬虫"""
    print("\n=== 测试在已有应用上下文中的爬虫 ===")
    
    try:
        from src.app import create_app
        from src.spider.equip import CBGEquipSpider
        
        # 创建Flask应用
        app = create_app()
        
        with app.app_context():
            # 在应用上下文中测试
            spider = CBGEquipSpider()
            
            mock_equipments = [
                {
                    'equip_sn': 'test_equip_context_001',
                    'price': 1500,
                    'server_name': '测试服务器',
                    'update_time': datetime.now(),
                    'equip_level': 85,
                    'kindid': 3
                }
            ]
            
            print("1. 在应用上下文中测试装备数据保存...")
            result = spider.save_equipment_data(mock_equipments)
            print(f"   保存结果: {result}")
            
            if result > 0:
                print("   ✅ 在应用上下文中保存成功")
            else:
                print("   ⚠️ 在应用上下文中保存失败或跳过")
        
    except Exception as e:
        print(f"❌ 应用上下文测试异常: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("爬虫应用上下文修复测试")
    print("=" * 50)
    
    # 测试装备爬虫
    test_equipment_spider_app_context()
    
    # 测试召唤兽爬虫
    test_pet_spider_app_context()
    
    # 测试在已有应用上下文中的爬虫
    test_spider_with_existing_context()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n修复说明:")
    print("1. 装备爬虫和召唤兽爬虫现在都会自动检测Flask应用上下文")
    print("2. 如果没有应用上下文，会自动创建一个")
    print("3. 如果有应用上下文，会直接使用现有的")
    print("4. 这解决了爬虫在后台线程中运行时的问题")

if __name__ == '__main__':
    main()
