#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Redis发布订阅功能测试
测试装备市场数据采集器的Redis发布订阅功能是否正常工作
"""

import sys
import os
import time
import json
import threading
import redis
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
from src.utils.redis_cache import RedisCache


class RedisPubSubTester:
    """Redis发布订阅测试器"""
    
    def __init__(self):
        self.redis_cache = RedisCache()
        self.collector = None
        self.received_messages = []
        self.test_channel = "test_equipment_update"
        
    def test_redis_connection(self):
        """测试Redis连接"""
        print("=" * 50)
        print("测试Redis连接...")
        
        try:
            if self.redis_cache.is_available():
                print("✅ Redis连接正常")
                return True
            else:
                print("❌ Redis连接失败")
                return False
        except Exception as e:
            print(f"❌ Redis连接异常: {e}")
            return False
    
    def test_pubsub_basic(self):
        """测试基本的发布订阅功能"""
        print("=" * 50)
        print("测试基本发布订阅功能...")
        
        try:
            # 创建Redis连接
            redis_client = redis.Redis(
                host=self.redis_cache.host,
                port=self.redis_cache.port,
                db=self.redis_cache.db,
                password=self.redis_cache.password,
                decode_responses=True
            )
            
            # 测试连接
            redis_client.ping()
            print("✅ Redis客户端连接成功")
            
            # 创建发布订阅对象
            pubsub = redis_client.pubsub()
            pubsub.subscribe(self.test_channel)
            print(f"✅ 已订阅频道: {self.test_channel}")
            
            # 启动订阅线程
            def subscriber():
                try:
                    for message in pubsub.listen():
                        if message['type'] == 'message':
                            print(f"📨 收到消息: {message['data']}")
                            self.received_messages.append(message['data'])
                            break  # 收到一条消息后退出
                except Exception as e:
                    print(f"❌ 订阅线程异常: {e}")
            
            sub_thread = threading.Thread(target=subscriber, daemon=True)
            sub_thread.start()
            
            # 等待订阅线程启动
            time.sleep(1)
            
            # 发布测试消息
            test_message = {
                'type': 'test_message',
                'timestamp': datetime.now().isoformat(),
                'data': {'test': 'hello world'}
            }
            
            redis_client.publish(self.test_channel, json.dumps(test_message))
            print(f"📤 已发布测试消息: {test_message}")
            
            # 等待消息接收
            sub_thread.join(timeout=5)
            
            if self.received_messages:
                print("✅ 发布订阅功能正常")
                return True
            else:
                print("❌ 未收到发布的消息")
                return False
                
        except Exception as e:
            print(f"❌ 发布订阅测试失败: {e}")
            return False
        finally:
            try:
                pubsub.close()
            except:
                pass
    
    def test_equip_collector_pubsub(self):
        """测试装备采集器的发布订阅功能"""
        print("=" * 50)
        print("测试装备采集器发布订阅功能...")
        
        try:
            # 获取装备采集器实例
            self.collector = EquipMarketDataCollector.get_instance()
            print("✅ 装备采集器实例获取成功")
            
            # 检查Redis发布订阅连接
            if hasattr(self.collector, '_redis_pubsub') and self.collector._redis_pubsub:
                print("✅ 装备采集器Redis发布订阅连接已建立")
            else:
                print("❌ 装备采集器Redis发布订阅连接未建立")
                return False
            
            # 检查订阅线程
            if hasattr(self.collector, '_pubsub_thread') and self.collector._pubsub_thread and self.collector._pubsub_thread.is_alive():
                print("✅ 装备采集器订阅线程正在运行")
            else:
                print("❌ 装备采集器订阅线程未运行")
                return False
            
            # 测试发布消息
            test_data = {
                'count': 10,
                'total_count': 100,
                'test': True
            }
            
            print("📤 测试发布装备数据更新消息...")
            self.collector._publish_equipment_update_message('equipment_data_added', test_data)
            
            # 等待一下让消息处理
            time.sleep(2)
            
            print("✅ 装备采集器发布订阅功能测试完成")
            return True
            
        except Exception as e:
            print(f"❌ 装备采集器发布订阅测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_redis_channels(self):
        """测试Redis频道信息"""
        print("=" * 50)
        print("测试Redis频道信息...")
        
        try:
            redis_client = redis.Redis(
                host=self.redis_cache.host,
                port=self.redis_cache.port,
                db=self.redis_cache.db,
                password=self.redis_cache.password,
                decode_responses=True
            )
            
            # 获取频道信息
            channels = redis_client.pubsub_channels()
            print(f"📡 当前活跃频道数量: {len(channels)}")
            
            if channels:
                print("📡 活跃频道列表:")
                for channel in channels:
                    print(f"  - {channel}")
            else:
                print("📡 当前没有活跃频道")
            
            # 获取订阅者信息
            if hasattr(self.collector, '_equipment_update_channel'):
                channel = self.collector._equipment_update_channel
                subscribers = redis_client.pubsub_numsub(channel)
                print(f"📡 频道 '{channel}' 订阅者数量: {subscribers.get(channel, 0)}")
            
            return True
            
        except Exception as e:
            print(f"❌ 获取Redis频道信息失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始Redis发布订阅功能测试")
        print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = []
        
        # 测试Redis连接
        results.append(("Redis连接", self.test_redis_connection()))
        
        # 测试基本发布订阅
        results.append(("基本发布订阅", self.test_pubsub_basic()))
        
        # 测试装备采集器发布订阅
        results.append(("装备采集器发布订阅", self.test_equip_collector_pubsub()))
        
        # 测试Redis频道信息
        results.append(("Redis频道信息", self.test_redis_channels()))
        
        # 输出测试结果
        print("=" * 50)
        print("📊 测试结果汇总:")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print("=" * 50)
        print(f"📈 测试通过率: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 所有测试通过！Redis发布订阅功能正常")
        else:
            print("⚠️  部分测试失败，请检查Redis配置和连接")
        
        return passed == total


def main():
    """主函数"""
    tester = RedisPubSubTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Redis发布订阅功能测试完成，功能正常")
        return 0
    else:
        print("\n❌ Redis发布订阅功能测试失败，请检查配置")
        return 1


if __name__ == "__main__":
    exit(main())
