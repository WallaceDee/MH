#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis连接诊断脚本
用于排查装备爬虫中Redis发布和同步失败的问题
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import time
from datetime import datetime

def test_redis_cache():
    """测试Redis缓存连接"""
    print("=" * 60)
    print("测试1: Redis缓存连接")
    print("=" * 60)
    
    try:
        from src.utils.redis_cache import get_redis_cache
        redis_cache = get_redis_cache()
        
        if not redis_cache:
            print("Redis缓存实例创建失败")
            return False
        
        # 测试连接
        if redis_cache.is_available():
            print("✅ Redis缓存连接成功")
            
            # 测试基本操作
            test_key = "test_connection"
            test_value = {"time": datetime.now().isoformat()}
            
            # 测试写入
            if redis_cache.set(test_key, test_value, ttl=60):
                print("✅ Redis写入测试成功")
            else:
                print("Redis写入测试失败")
                return False
            
            # 测试读取
            result = redis_cache.get(test_key)
            if result:
                print(f"✅ Redis读取测试成功: {result}")
            else:
                print("Redis读取测试失败")
                return False
            
            # 清理测试数据
            redis_cache.delete(test_key)
            print("✅ Redis基本操作测试通过")
            return True
        else:
            print("Redis缓存不可用")
            return False
            
    except Exception as e:
        print(f"Redis缓存测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_redis_pubsub():
    """测试Redis发布订阅"""
    print("\n" + "=" * 60)
    print("测试2: Redis发布订阅")
    print("=" * 60)
    
    try:
        from src.utils.redis_pubsub import get_redis_pubsub, Channel, MessageType
        
        pubsub = get_redis_pubsub()
        
        # 测试普通消息发布
        message = {
            'type': MessageType.EQUIPMENT_DATA_SAVED,
            'data_count': 1,
            'test': True
        }
        
        result = pubsub.publish(Channel.EQUIPMENT_UPDATES, message)
        if result:
            print(f"✅ 普通消息发布成功（订阅者数量: 可能为0）")
        else:
            print("普通消息发布失败")
            return False
        
        print("✅ Redis发布订阅测试通过")
        return True
        
    except Exception as e:
        print(f"Redis发布订阅测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_redis_pubsub_with_dataframe():
    """测试Redis发布DataFrame消息"""
    print("\n" + "=" * 60)
    print("测试3: Redis发布DataFrame消息")
    print("=" * 60)
    
    try:
        from src.utils.redis_pubsub import get_redis_pubsub, Channel, MessageType
        
        pubsub = get_redis_pubsub()
        
        # 创建测试DataFrame
        test_data = {
            'equip_sn': ['test_001', 'test_002'],
            'equip_name': ['测试装备1', '测试装备2'],
            'level': [100, 120],
            'price': [1000, 2000]
        }
        test_df = pd.DataFrame(test_data)
        
        print(f"测试DataFrame: {len(test_df)} 条数据, shape: {test_df.shape}")
        
        # 测试DataFrame消息发布
        message = {
            'type': MessageType.EQUIPMENT_DATA_SAVED,
            'data_count': len(test_df),
            'action': 'add_dataframe'
        }
        
        start_time = time.time()
        result = pubsub.publish_with_dataframe(Channel.EQUIPMENT_UPDATES, message, test_df)
        elapsed_time = time.time() - start_time
        
        if result:
            print(f"✅ DataFrame消息发布成功，耗时: {elapsed_time:.3f}秒")
            print(f"   注意: 返回True表示发布成功，但可能没有订阅者接收")
        else:
            print(f"DataFrame消息发布失败，耗时: {elapsed_time:.3f}秒")
            print("可能原因:")
            print("  1. DataFrame数据太大")
            print("  2. Redis连接超时")
            print("  3. 序列化失败")
            return False
        
        print("✅ Redis发布DataFrame测试通过")
        return True
        
    except Exception as e:
        print(f"Redis发布DataFrame测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_redis_hash_update():
    """测试Redis Hash增量更新"""
    print("\n" + "=" * 60)
    print("测试4: Redis Hash增量更新")
    print("=" * 60)
    
    try:
        from src.utils.redis_cache import get_redis_cache
        
        redis_cache = get_redis_cache()
        
        if not redis_cache or not redis_cache.is_available():
            print("Redis缓存不可用")
            return False
        
        # 创建测试DataFrame
        test_data = {
            'equip_sn': ['test_hash_001', 'test_hash_002', 'test_hash_003'],
            'equip_name': ['测试装备A', '测试装备B', '测试装备C'],
            'level': [100, 120, 140],
            'price': [1000, 2000, 3000]
        }
        test_df = pd.DataFrame(test_data)
        
        print(f"测试DataFrame: {len(test_df)} 条数据")
        
        # 测试增量更新
        test_hash_key = "test_equipment_hash"
        
        start_time = time.time()
        result = redis_cache.update_hash_incremental(
            hash_key=test_hash_key,
            new_data=test_df,
            ttl=300  # 5分钟过期
        )
        elapsed_time = time.time() - start_time
        
        if result:
            print(f"✅ Hash增量更新成功，耗时: {elapsed_time:.3f}秒")
            
            # 验证数据
            hash_count = redis_cache.client.hlen(redis_cache._make_key(test_hash_key))
            print(f"✅ Hash中的数据条数: {hash_count}")
            
            # 清理测试数据
            redis_cache.clear_pattern(f"*{test_hash_key}*")
            print("✅ 测试数据已清理")
        else:
            print(f"Hash增量更新失败，耗时: {elapsed_time:.3f}秒")
            return False
        
        print("✅ Redis Hash增量更新测试通过")
        return True
        
    except Exception as e:
        print(f"Redis Hash增量更新测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_large_dataframe():
    """测试大型DataFrame的Redis操作"""
    print("\n" + "=" * 60)
    print("测试5: 大型DataFrame Redis操作（模拟真实场景）")
    print("=" * 60)
    
    try:
        from src.utils.redis_pubsub import get_redis_pubsub, Channel, MessageType
        from src.utils.redis_cache import get_redis_cache
        
        # 创建15条数据（模拟爬虫每页15条）
        test_data = {
            'equip_sn': [f'large_test_{i:03d}' for i in range(15)],
            'equip_name': [f'测试装备{i}' for i in range(15)],
            'level': [100 + i * 10 for i in range(15)],
            'price': [1000 + i * 100 for i in range(15)],
            'server_name': [f'服务器{i % 5}' for i in range(15)],
            'seller_nickname': [f'卖家{i}' for i in range(15)],
        }
        test_df = pd.DataFrame(test_data)
        
        print(f"测试DataFrame: {len(test_df)} 条数据, 大小: {test_df.memory_usage(deep=True).sum() / 1024:.2f} KB")
        
        # 测试发布DataFrame
        pubsub = get_redis_pubsub()
        message = {
            'type': MessageType.EQUIPMENT_DATA_SAVED,
            'data_count': len(test_df),
            'action': 'add_dataframe'
        }
        
        print("\n正在测试发布DataFrame消息...")
        start_time = time.time()
        pub_result = pubsub.publish_with_dataframe(Channel.EQUIPMENT_UPDATES, message, test_df)
        pub_elapsed = time.time() - start_time
        
        if pub_result:
            print(f"✅ DataFrame发布成功，耗时: {pub_elapsed:.3f}秒")
        else:
            print(f"DataFrame发布失败，耗时: {pub_elapsed:.3f}秒")
        
        # 测试Hash增量更新
        redis_cache = get_redis_cache()
        test_hash_key = "test_large_equipment_hash"
        
        print("\n正在测试Hash增量更新...")
        start_time = time.time()
        hash_result = redis_cache.update_hash_incremental(
            hash_key=test_hash_key,
            new_data=test_df,
            ttl=300
        )
        hash_elapsed = time.time() - start_time
        
        if hash_result:
            print(f"✅ Hash更新成功，耗时: {hash_elapsed:.3f}秒")
            
            # 清理
            redis_cache.clear_pattern(f"*{test_hash_key}*")
        else:
            print(f"Hash更新失败，耗时: {hash_elapsed:.3f}秒")
        
        if pub_result and hash_result:
            print("\n✅ 大型DataFrame测试通过")
            return True
        else:
            print("\n部分测试失败")
            return False
        
    except Exception as e:
        print(f"大型DataFrame测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("CBG装备爬虫 - Redis连接诊断工具")
    print("=" * 60)
    
    results = []
    
    # 运行所有测试
    results.append(("Redis缓存连接", test_redis_cache()))
    results.append(("Redis发布订阅", test_redis_pubsub()))
    results.append(("Redis发布DataFrame", test_redis_pubsub_with_dataframe()))
    results.append(("Redis Hash更新", test_redis_hash_update()))
    results.append(("大型DataFrame操作", test_large_dataframe()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<20} {status}")
    
    # 判断整体结果
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！Redis连接正常")
        print("\n📌 关于 '发布DataFrame消息失败' 的说明：")
        print("   - 如果没有订阅者，Redis publish会返回0")
        print("   - 这不影响数据保存，只是没有进程监听消息")
        print("   - 数据已成功保存到MySQL和Redis")
    else:
        print("\n警告：部分测试失败，请检查Redis连接配置")
        print("\n可能的解决方案：")
        print("1. 检查Redis服务器是否正常运行")
        print("2. 检查网络连接是否正常（远程Redis: 47.86.33.98:6379）")
        print("3. 检查Redis密码是否正确")
        print("4. 增加Redis超时时间配置")

if __name__ == '__main__':
    main()


