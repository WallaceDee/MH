#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
专门调试calculate_value方法的脚本
"""

import sys
import os
import logging
import traceback

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# 设置详细的日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)

def debug_calculate_value():
    """调试calculate_value方法"""
    
    try:
        from src.app.services.role_service import roleService
        
        print("=== 开始调试calculate_value方法 ===")
        
        # 创建角色服务
        service = roleService()
        print("角色服务创建成功")
        
        # 获取角色数据
        role_data = service.get_role_details("202103231100113-207-EC2D2BNNRLXO", 2025, 9, "normal")
        if not role_data:
            print("无法获取角色数据")
            return
        
        print("成功获取角色数据")
        
        # 提取特征
        features = service.feature_extractor.extract_features(role_data)
        print(f"特征提取完成，特征数量: {len(features)}")
        
        # 获取市场锚定估价器
        market_evaluator = service.market_evaluator
        print("获取市场锚定估价器成功")
        
        # 先测试 find_market_anchors
        print("\n=== 第一步：测试 find_market_anchors ===")
        try:
            anchors = market_evaluator.find_market_anchors(
                features,
                similarity_threshold=0.7,
                max_anchors=5,
                verbose=True
            )
            print(f"find_market_anchors 成功: {len(anchors)} 个锚点")
            
            if anchors:
                print(f"锚点价格: {[anchor['price'] for anchor in anchors]}")
                
                # 现在测试 calculate_value 方法
                print("\n=== 第二步：测试 calculate_value ===")
                try:
                    print("调用 calculate_value...")
                    result = market_evaluator.calculate_value(
                        features, 
                        strategy='fair_value',
                        similarity_threshold=0.7,
                        max_anchors=5,
                        verbose=True
                    )
                    print(f"calculate_value 成功: {result}")
                    
                except Exception as calc_e:
                    print(f"calculate_value 失败: {calc_e}")
                    print("详细错误信息:")
                    traceback.print_exc()
            else:
                print("没有找到锚点，无法测试 calculate_value")
                
        except Exception as anchor_e:
            print(f"find_market_anchors 失败: {anchor_e}")
            traceback.print_exc()
        
    except Exception as e:
        print(f"调试失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_calculate_value()
