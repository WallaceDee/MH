#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
装备数据同步诊断脚本
用于检测爬虫保存数据后，内存缓存是否正确更新
"""

import sys
import os
import time
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_redis_pubsub():
    """测试Redis发布/订阅功能"""
    print("\n" + "="*60)
    print("测试 1: Redis发布/订阅功能")
    print("="*60)
    
    try:
        from src.utils.redis_pubsub import get_redis_pubsub, MessageType, Channel
        import pandas as pd
        
        pubsub = get_redis_pubsub()
        
        # 测试数据
        test_df = pd.DataFrame({
            'equip_sn': ['TEST001', 'TEST002'],
            'equip_name': ['测试装备1', '测试装备2'],
            'price': [1000, 2000]
        })
        
        message = {
            'type': MessageType.EQUIPMENT_DATA_SAVED,
            'data_count': 2,
            'action': 'add_dataframe'
        }
        
        print(f"📢 发布测试消息...")
        success = pubsub.publish_with_dataframe(Channel.EQUIPMENT_UPDATES, message, test_df)
        
        if success:
            print(f"✅ 消息发布成功")
        else:
            print(f"❌ 消息发布失败")
            
        return success
        
    except Exception as e:
        print(f"❌ Redis发布/订阅测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_cache_status():
    """测试内存缓存状态"""
    print("\n" + "="*60)
    print("测试 2: 内存缓存状态")
    print("="*60)
    
    try:
        from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
        
        collector = EquipMarketDataCollector.get_instance()
        
        print(f"📊 内存缓存状态:")
        if collector._full_data_cache is None:
            print(f"  - 内存缓存: 空 (None)")
            print(f"  ⚠️ 需要先加载数据到内存缓存")
        elif collector._full_data_cache.empty:
            print(f"  - 内存缓存: 空 (Empty DataFrame)")
            print(f"  ⚠️ 需要先加载数据到内存缓存")
        else:
            print(f"  - 内存缓存: {len(collector._full_data_cache):,} 条数据")
            print(f"  ✅ 内存缓存正常")
        
        print(f"\n📡 Redis订阅状态:")
        if hasattr(collector, 'redis_pubsub') and collector.redis_pubsub:
            print(f"  - Redis Pub/Sub: 已初始化")
            print(f"  - 订阅的频道: {list(collector.redis_pubsub.subscribers.keys())}")
            print(f"  - 订阅线程运行: {collector.redis_pubsub.running}")
            print(f"  ✅ Redis订阅正常")
        else:
            print(f"  - Redis Pub/Sub: 未初始化")
            print(f"  ❌ Redis订阅未正常工作")
        
        return True
        
    except Exception as e:
        print(f"❌ 内存缓存状态检测失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_message_handling():
    """测试消息处理逻辑"""
    print("\n" + "="*60)
    print("测试 3: 消息处理逻辑")
    print("="*60)
    
    try:
        from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
        from src.utils.redis_pubsub import get_redis_pubsub, MessageType, Channel
        import pandas as pd
        
        collector = EquipMarketDataCollector.get_instance()
        
        # 确保内存缓存已初始化
        if collector._full_data_cache is None:
            print(f"⚠️ 内存缓存为空，先初始化...")
            collector._full_data_cache = pd.DataFrame()
        
        # 记录初始数据量
        initial_count = len(collector._full_data_cache) if not collector._full_data_cache.empty else 0
        print(f"📊 初始内存缓存数据量: {initial_count:,} 条")
        
        # 发送测试消息
        print(f"\n📢 发送测试DataFrame消息...")
        test_df = pd.DataFrame({
            'equip_sn': ['DIAG_TEST_001'],
            'equip_name': ['诊断测试装备'],
            'price': [9999],
            'level': [150]
        })
        
        pubsub = get_redis_pubsub()
        message = {
            'type': MessageType.EQUIPMENT_DATA_SAVED,
            'data_count': 1,
            'action': 'add_dataframe'
        }
        
        success = pubsub.publish_with_dataframe(Channel.EQUIPMENT_UPDATES, message, test_df)
        
        if success:
            print(f"✅ 测试消息发送成功")
            
            # 等待消息处理
            print(f"⏳ 等待3秒，让消息处理...")
            time.sleep(3)
            
            # 检查内存缓存是否更新
            final_count = len(collector._full_data_cache) if not collector._full_data_cache.empty else 0
            print(f"📊 最终内存缓存数据量: {final_count:,} 条")
            
            if final_count > initial_count:
                print(f"✅ 内存缓存已更新 (+{final_count - initial_count} 条)")
                return True
            else:
                print(f"❌ 内存缓存未更新，可能存在问题")
                return False
        else:
            print(f"❌ 测试消息发送失败")
            return False
        
    except Exception as e:
        print(f"❌ 消息处理逻辑测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_redis_connection():
    """测试Redis连接"""
    print("\n" + "="*60)
    print("测试 4: Redis连接")
    print("="*60)
    
    try:
        from src.utils.redis_cache import get_redis_cache
        
        redis_cache = get_redis_cache()
        
        if redis_cache and redis_cache.is_available():
            print(f"✅ Redis连接正常")
            
            # 测试基本操作
            test_key = "diagnosis_test_key"
            test_value = "diagnosis_test_value"
            
            redis_cache.set(test_key, test_value, ttl=10)
            retrieved_value = redis_cache.get(test_key)
            
            if retrieved_value == test_value:
                print(f"✅ Redis读写功能正常")
                redis_cache.delete(test_key)
                return True
            else:
                print(f"❌ Redis读写功能异常")
                return False
        else:
            print(f"❌ Redis连接失败")
            return False
        
    except Exception as e:
        print(f"❌ Redis连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("装备数据同步诊断")
    print("="*60)
    
    # 需要在Flask应用上下文中运行
    from src.app import create_app
    app = create_app()
    
    with app.app_context():
        results = []
        
        # 测试1: Redis连接
        results.append(("Redis连接", test_redis_connection()))
        
        # 测试2: Redis发布/订阅
        results.append(("Redis Pub/Sub", test_redis_pubsub()))
        
        # 测试3: 内存缓存状态
        results.append(("内存缓存状态", test_memory_cache_status()))
        
        # 测试4: 消息处理
        results.append(("消息处理逻辑", test_message_handling()))
        
        # 汇总结果
        print("\n" + "="*60)
        print("诊断结果汇总")
        print("="*60)
        
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
        
        all_passed = all(result for _, result in results)
        
        print("\n" + "="*60)
        if all_passed:
            print("✅ 所有测试通过，装备数据同步功能正常")
        else:
            print("❌ 部分测试失败，请检查上述失败项")
        print("="*60)


if __name__ == '__main__':
    main()

