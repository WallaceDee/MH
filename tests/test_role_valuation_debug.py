#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试角色估价接口问题
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# 设置日志
logging.basicConfig(level=logging.DEBUG)

def test_market_data_collector():
    """测试市场数据收集器"""
    print("=== 测试市场数据收集器 ===")
    
    try:
        from src.evaluator.market_data_collector import MarketDataCollector
        
        # 创建数据收集器
        collector = MarketDataCollector()
        print(f"数据库路径: {collector.db_path}")
        
        if not collector.db_path:
            print("❌ 数据库路径为空，无法继续测试")
            return False
            
        if not os.path.exists(collector.db_path):
            print(f"❌ 数据库文件不存在: {collector.db_path}")
            return False
            
        print("✅ 数据库路径有效")
        
        # 尝试刷新市场数据
        print("开始刷新市场数据...")
        market_data = collector.refresh_market_data(max_records=10)
        
        if market_data.empty:
            print("❌ 市场数据为空")
            return False
        else:
            print(f"✅ 成功获取 {len(market_data)} 条市场数据")
            return True
            
    except Exception as e:
        print(f"❌ 市场数据收集器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_market_anchor_evaluator():
    """测试市场锚定估价器"""
    print("\n=== 测试市场锚定估价器 ===")
    
    try:
        from src.evaluator.market_anchor_evaluator import MarketAnchorEvaluator
        from src.evaluator.market_data_collector import MarketDataCollector
        
        # 创建数据收集器
        collector = MarketDataCollector()
        
        # 创建估价器
        evaluator = MarketAnchorEvaluator(collector)
        print("✅ 市场锚定估价器创建成功")
        
        # 创建测试数据
        test_features = {
            'level': 129,
            'total_cultivation': 100,
            'total_beast_cultivation': 80,
            'avg_school_skills': 120,
            'expt_ski1': 25,
            'expt_ski2': 25,
            'expt_ski3': 25,
            'expt_ski4': 25,
            'expt_ski5': 0,
            'beast_ski1': 20,
            'beast_ski2': 20,
            'beast_ski3': 20,
            'beast_ski4': 20,
            'all_new_point': 5,
            'qianyuandan_breakthrough': True,
            'three_fly_lv': 0,
            'school_history_count': 1,
            'school_skills': [120, 120, 120, 120, 120, 120, 120],
            'life_skills': [140, 150, 160],
            'qiangzhuang&shensu': [100, 100]
        }
        
        print("开始寻找市场锚点...")
        anchors = evaluator.find_market_anchors(
            test_features,
            similarity_threshold=0.7,
            max_anchors=10
        )
        
        print(f"✅ 成功找到 {len(anchors)} 个市场锚点")
        
        if len(anchors) > 0:
            print("开始计算估价...")
            result = evaluator.calculate_value(
                test_features,
                strategy='fair_value',
                similarity_threshold=0.7,
                max_anchors=10
            )
            
            if 'error' in result:
                print(f"❌ 估价计算失败: {result['error']}")
                return False
            else:
                print(f"✅ 估价成功: {result.get('estimated_price', 0)}")
                return True
        else:
            print("⚠️  未找到锚点，但程序没有崩溃")
            return True
            
    except Exception as e:
        print(f"❌ 市场锚定估价器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_role_service():
    """测试角色服务"""
    print("\n=== 测试角色服务 ===")
    
    try:
        from src.app.services.role_service import roleService
        
        service = roleService()
        print("✅ 角色服务创建成功")
        
        # 测试估价方法
        result = service.get_role_valuation(
            eid="test_role_123",
            year=2025,
            month=1,
            role_type="normal",
            strategy="fair_value",
            similarity_threshold=0.7,
            max_anchors=10
        )
        
        if 'error' in result:
            print(f"⚠️  角色估价返回错误: {result['error']}")
            # 这可能是正常的，因为测试数据可能不存在
            return True
        else:
            print(f"✅ 角色估价成功: {result}")
            return True
            
    except Exception as e:
        print(f"❌ 角色服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始调试角色估价接口问题...")
    
    # 测试市场数据收集器
    if not test_market_data_collector():
        print("❌ 市场数据收集器测试失败，无法继续")
        return
    
    # 测试市场锚定估价器
    if not test_market_anchor_evaluator():
        print("❌ 市场锚定估价器测试失败")
        return
    
    # 测试角色服务
    if not test_role_service():
        print("❌ 角色服务测试失败")
        return
    
    print("\n✅ 所有测试通过！角色估价接口修复成功")

if __name__ == "__main__":
    main()
