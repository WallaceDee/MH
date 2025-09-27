#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的数据流程，找出字段丢失的原因
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app
from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector

def test_data_flow():
    """测试完整的数据流程"""
    app = create_app()
    
    with app.app_context():
        print("=== 测试完整数据流程 ===")
        
        # 获取数据采集器实例
        collector = EquipMarketDataCollector.get_instance()
        
        print("1. 测试从MySQL获取数据...")
        try:
            # 获取少量数据进行测试
            mysql_data = collector._get_market_data_from_mysql(limit=5)
            print(f"MySQL数据字段数量: {len(mysql_data.columns)}")
            print(f"MySQL数据字段: {list(mysql_data.columns)}")
            
            if 'update_time' in mysql_data.columns:
                print("✅ MySQL数据包含update_time字段")
            else:
                print("❌ MySQL数据缺少update_time字段")
                
        except Exception as e:
            print(f"❌ MySQL查询失败: {e}")
            return
        
        print("\n2. 测试从Redis获取数据...")
        try:
            redis_data = collector._get_full_data_from_redis()
            if redis_data is not None and not redis_data.empty:
                print(f"Redis数据字段数量: {len(redis_data.columns)}")
                print(f"Redis数据字段: {list(redis_data.columns)}")
                
                if 'update_time' in redis_data.columns:
                    print("✅ Redis数据包含update_time字段")
                else:
                    print("❌ Redis数据缺少update_time字段")
            else:
                print("⚠️ Redis中没有数据")
                
        except Exception as e:
            print(f"❌ Redis查询失败: {e}")
        
        print("\n3. 测试获取市场数据...")
        try:
            market_data = collector.get_market_data(limit=5)
            print(f"市场数据字段数量: {len(market_data.columns)}")
            print(f"市场数据字段: {list(market_data.columns)}")
            
            if 'update_time' in market_data.columns:
                print("✅ 市场数据包含update_time字段")
            else:
                print("❌ 市场数据缺少update_time字段")
                
        except Exception as e:
            print(f"❌ 市场数据获取失败: {e}")
        
        print("\n4. 测试特征提取...")
        try:
            if not market_data.empty:
                # 取第一条数据进行特征提取测试
                sample_data = market_data.iloc[0].to_dict()
                print(f"样本数据字段数量: {len(sample_data)}")
                print(f"样本数据字段: {list(sample_data.keys())}")
                
                if 'update_time' in sample_data:
                    print("✅ 样本数据包含update_time字段")
                else:
                    print("❌ 样本数据缺少update_time字段")
                    
                # 测试特征提取
                from src.app.services.equipment_service import equipment_service
                features = equipment_service.extract_features(sample_data)
                print(f"提取的特征数量: {len(features)}")
                print(f"提取的特征字段: {list(features.keys())}")
                
        except Exception as e:
            print(f"❌ 特征提取失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_data_flow()
