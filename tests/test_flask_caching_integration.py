#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试 MarketDataCollector 的 Flask-Caching 集成

这个测试验证从手搓版缓存迁移到 Flask-Caching 后的功能是否正常
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import time
from datetime import datetime
from src.app import create_app
from src.evaluator.market_data_collector import MarketDataCollector


class TestFlaskCachingIntegration(unittest.TestCase):
    """测试Flask-Caching集成"""

    def setUp(self):
        """测试前设置"""
        # 创建Flask应用
        self.app = create_app()
        self.app.config['TESTING'] = True
        
        # 设置测试用的缓存配置
        self.app.config.update({
            'CACHE_TYPE': 'SimpleCache',  # 使用内存缓存进行测试
            'CACHE_DEFAULT_TIMEOUT': 300,  # 5分钟
        })
        
        # 创建应用上下文
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 初始化市场数据采集器
        self.collector = MarketDataCollector()

    def tearDown(self):
        """测试后清理"""
        if hasattr(self, 'app_context'):
            self.app_context.pop()

    def test_cache_instance_creation(self):
        """测试缓存实例创建"""
        print("\n=== 测试缓存实例创建 ===")
        
        cache = self.collector._get_cache()
        self.assertIsNotNone(cache, "缓存实例不应为None")
        
        print(f"✅ 缓存实例创建成功: {type(cache)}")

    def test_cache_key_generation(self):
        """测试缓存键生成"""
        print("\n=== 测试缓存键生成 ===")
        
        # 测试无过滤条件
        key1 = self.collector._generate_cache_key()
        self.assertTrue(key1.startswith("market_data:"), "缓存键应以market_data:开头")
        
        # 测试有过滤条件
        filters = {'level_min': 109, 'price_max': 10000}
        key2 = self.collector._generate_cache_key(filters, 500)
        self.assertNotEqual(key1, key2, "不同条件应产生不同的缓存键")
        
        # 测试相同条件产生相同键
        key3 = self.collector._generate_cache_key(filters, 500)
        self.assertEqual(key2, key3, "相同条件应产生相同的缓存键")
        
        print(f"✅ 无过滤条件键: {key1}")
        print(f"✅ 有过滤条件键: {key2}")
        print(f"✅ 缓存键生成测试通过")

    def test_cache_set_and_get(self):
        """测试缓存设置和获取"""
        print("\n=== 测试缓存设置和获取 ===")
        
        cache = self.collector._get_cache()
        if not cache:
            self.skipTest("缓存不可用，跳过测试")
        
        # 创建测试数据
        import pandas as pd
        test_data = pd.DataFrame({
            'eid': ['test1', 'test2', 'test3'],
            'price': [1000, 2000, 3000],
            'level': [109, 129, 159],
            'school': [1, 2, 3]
        })
        test_data.set_index('eid', inplace=True)
        
        # 测试设置缓存
        filters = {'level_min': 100}
        max_records = 10
        
        success = self.collector._set_cached_data(filters, max_records, test_data)
        self.assertTrue(success, "缓存设置应该成功")
        
        # 测试获取缓存
        cached_data = self.collector._get_cached_data(filters, max_records)
        self.assertIsNotNone(cached_data, "应该能获取到缓存数据")
        self.assertEqual(len(cached_data), len(test_data), "缓存数据长度应该匹配")
        
        print(f"✅ 原始数据: {len(test_data)} 条")
        print(f"✅ 缓存数据: {len(cached_data)} 条")
        print(f"✅ 缓存设置和获取测试通过")

    def test_cache_expiration(self):
        """测试缓存过期"""
        print("\n=== 测试缓存过期 ===")
        
        # 设置较短的缓存过期时间
        original_expiry = self.collector._cache_expiry_hours
        self.collector.set_cache_expiry(0.001)  # 约3.6秒
        
        try:
            # 模拟数据加载
            self.collector._data_loaded = True
            self.collector._last_refresh_time = datetime.now()
            
            # 检查缓存未过期
            self.assertFalse(self.collector._is_cache_expired(), "缓存应该未过期")
            
            # 等待缓存过期
            time.sleep(4)
            
            # 检查缓存已过期
            self.assertTrue(self.collector._is_cache_expired(), "缓存应该已过期")
            
            print("✅ 缓存过期机制测试通过")
            
        finally:
            # 恢复原始过期时间
            self.collector.set_cache_expiry(original_expiry)

    def test_cache_info(self):
        """测试缓存信息获取"""
        print("\n=== 测试缓存信息获取 ===")
        
        cache_info = self.collector.get_cache_info()
        
        # 验证基本信息
        self.assertIn('data_loaded', cache_info)
        self.assertIn('cache_available', cache_info)
        self.assertIn('cache_type', cache_info)
        self.assertIn('data_source', cache_info)
        
        print(f"✅ 缓存可用: {cache_info.get('cache_available')}")
        print(f"✅ 缓存类型: {cache_info.get('cache_type')}")
        print(f"✅ 数据源: {cache_info.get('data_source')}")
        print(f"✅ 缓存信息获取测试通过")

    def test_singleton_pattern(self):
        """测试单例模式"""
        print("\n=== 测试单例模式 ===")
        
        # 创建多个实例
        collector1 = MarketDataCollector()
        collector2 = MarketDataCollector()
        
        # 验证是同一个实例
        self.assertIs(collector1, collector2, "应该返回同一个实例")
        self.assertIs(collector1, self.collector, "应该返回同一个实例")
        
        print("✅ 单例模式测试通过")

    def test_cache_clear(self):
        """测试缓存清理"""
        print("\n=== 测试缓存清理 ===")
        
        # 设置一些数据
        import pandas as pd
        test_data = pd.DataFrame({'test': [1, 2, 3]})
        self.collector.market_data = test_data
        self.collector._data_loaded = True
        self.collector._last_refresh_time = datetime.now()
        
        # 清理缓存
        self.collector.clear_instance_cache()
        
        # 验证清理结果
        self.assertTrue(self.collector.market_data.empty, "市场数据应该被清空")
        self.assertFalse(self.collector._data_loaded, "数据加载标志应该为False")
        self.assertIsNone(self.collector._last_refresh_time, "刷新时间应该为None")
        
        print("✅ 缓存清理测试通过")


def run_comprehensive_test():
    """运行综合测试"""
    print("开始 Flask-Caching 集成综合测试")
    print("=" * 50)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFlaskCachingIntegration)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print("Flask-Caching 集成测试完成")
    
    if result.wasSuccessful():
        print("✅ 所有测试通过！Flask-Caching 集成成功")
        return True
    else:
        print(f"❌ 测试失败：{len(result.failures)} 个失败，{len(result.errors)} 个错误")
        for test, error in result.failures + result.errors:
            print(f"  - {test}: {error}")
        return False


if __name__ == '__main__':
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
