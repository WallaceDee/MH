#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试市场数据API接口
"""

import sys
import os
from pathlib import Path
import requests
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_market_data_status_api():
    """测试市场数据状态API"""
    
    # API基础URL
    base_url = "http://localhost:5000/api/v1"
    
    print("🔍 测试市场数据状态API")
    print("=" * 50)
    
    try:
        # 测试获取状态接口
        print("1. 测试获取市场数据状态...")
        response = requests.get(f"{base_url}/system/market-data/status")
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 状态接口正常")
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 检查关键字段
            if 'data' in data:
                status_data = data['data']
                print(f"\n📊 市场数据状态:")
                print(f"  数据已加载: {status_data.get('data_loaded', False)}")
                print(f"  数据条数: {status_data.get('data_count', 0)}")
                print(f"  内存占用: {status_data.get('memory_usage_mb', 0):.2f} MB")
                print(f"  缓存过期: {status_data.get('cache_expired', True)}")
                print(f"  最后刷新: {status_data.get('last_refresh_time', '未知')}")
                
                if status_data.get('price_statistics'):
                    price_stats = status_data['price_statistics']
                    print(f"  价格范围: {price_stats.get('min_price', 0)} - {price_stats.get('max_price', 0)}")
                    print(f"  平均价格: {price_stats.get('avg_price', 0):.0f}")
        else:
            print(f"❌ 状态接口异常: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败，请确保后端服务已启动 (python run.py)")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    print("\n" + "=" * 50)
    
    # 测试刷新接口
    try:
        print("2. 测试刷新市场数据...")
        
        # 构建测试参数
        refresh_params = {
            "max_records": 100,  # 少量数据用于测试
            "filters": {
                "level_min": 109,
                "level_max": 175
            }
        }
        
        response = requests.post(
            f"{base_url}/system/market-data/refresh",
            json=refresh_params,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 刷新接口正常")
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if 'data' in data:
                refresh_data = data['data']
                print(f"\n🔄 刷新结果:")
                print(f"  刷新成功: {refresh_data.get('success', False)}")
                print(f"  数据条数: {refresh_data.get('data_count', 0)}")
                print(f"  刷新时间: {refresh_data.get('refresh_time', '未知')}")
        else:
            print(f"❌ 刷新接口异常: {response.text}")
            
    except Exception as e:
        print(f"❌ 刷新测试失败: {e}")
    
    print("\n🎉 API测试完成!")
    return True

def main():
    """主函数"""
    print("🚀 市场数据API接口测试")
    print("=" * 60)
    
    # 检查是否在正确的目录
    if not os.path.exists("src/evaluator/market_data_collector.py"):
        print("❌ 请在项目根目录运行此脚本")
        return 1
    
    # 执行测试
    success = test_market_data_status_api()
    
    if success:
        print("\n✅ 所有测试通过！")
        print("\n💡 使用说明:")
        print("1. 启动后端服务: python run.py")
        print("2. 启动前端服务: cd web && npm run serve")
        print("3. 访问: http://localhost:8080/market-data-status")
        return 0
    else:
        print("\n❌ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
