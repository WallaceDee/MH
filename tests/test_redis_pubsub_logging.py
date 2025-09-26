#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Redis发布订阅日志测试
测试装备市场数据采集器的Redis发布订阅日志记录功能
"""

import sys
import os
import time
import json
import threading
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector


def test_redis_pubsub_logging():
    """测试Redis发布订阅日志记录"""
    print("🚀 开始Redis发布订阅日志测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 获取装备采集器实例
        print("📦 获取装备采集器实例...")
        collector = EquipMarketDataCollector.get_instance()
        print("✅ 装备采集器实例获取成功")
        
        # 检查Redis发布订阅连接
        if hasattr(collector, '_redis_pubsub') and collector._redis_pubsub:
            print("✅ Redis发布订阅连接已建立")
        else:
            print("❌ Redis发布订阅连接未建立")
            return False
        
        # 检查订阅线程
        if hasattr(collector, '_pubsub_thread') and collector._pubsub_thread and collector._pubsub_thread.is_alive():
            print("✅ Redis订阅线程正在运行")
        else:
            print("❌ Redis订阅线程未运行")
            return False
        
        print("\n📤 测试发布消息...")
        
        # 测试发布装备数据添加消息
        test_data_added = {
            'count': 5,
            'total_count': 100,
            'test': True,
            'timestamp': datetime.now().isoformat()
        }
        
        print("📤 发布装备数据添加消息...")
        collector._publish_equipment_update_message('equipment_data_added', test_data_added)
        
        # 等待消息处理
        time.sleep(2)
        
        # 测试发布装备数据更新消息
        test_data_updated = {
            'count': 10,
            'update_time': datetime.now().isoformat(),
            'test': True
        }
        
        print("📤 发布装备数据更新消息...")
        collector._publish_equipment_update_message('equipment_data_updated', test_data_updated)
        
        # 等待消息处理
        time.sleep(2)
        
        # 测试发布未知类型消息
        print("📤 发布未知类型消息...")
        collector._publish_equipment_update_message('unknown_message_type', {'test': True})
        
        # 等待消息处理
        time.sleep(2)
        
        print("\n✅ Redis发布订阅日志测试完成")
        print("📋 请检查日志文件 logs/app_*.log 中的Redis发布订阅相关日志")
        print("🔍 查找以下关键词:")
        print("   - 'Redis发布订阅功能启动成功'")
        print("   - '开始监听Redis频道'")
        print("   - '收到Redis消息'")
        print("   - '已发布装备数据更新消息到Redis频道'")
        print("   - '收到装备数据添加消息'")
        print("   - '收到装备数据更新消息'")
        print("   - '收到未知类型的Redis消息'")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis发布订阅日志测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    success = test_redis_pubsub_logging()
    
    if success:
        print("\n🎉 Redis发布订阅日志测试完成")
        print("📝 现在你应该能在日志文件中看到Redis发布订阅的相关日志了")
        return 0
    else:
        print("\n❌ Redis发布订阅日志测试失败")
        return 1


if __name__ == "__main__":
    exit(main())
