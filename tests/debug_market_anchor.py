#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
专门调试市场锚定估价器的脚本
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

def debug_market_anchor():
    """调试市场锚定估价器"""
    
    try:
        from src.app.services.role_service import roleService
        
        print("=== 开始调试市场锚定估价器 ===")
        
        # 创建角色服务
        service = roleService()
        print("角色服务创建成功")
        
        # 获取角色数据
        role_data = service.get_role_details("202103231100113-207-EC2D2BNNRLXO", 2025, 9, "normal")
        if not role_data:
            print("无法获取角色数据")
            return
            
        print(f"成功获取角色数据，类型: {type(role_data)}")
        
        # 提取特征
        print("开始特征提取...")
        features = service.feature_extractor.extract_features(role_data)
        print(f"特征提取完成，特征数量: {len(features)}")
        print(f"特征类型: {type(features)}")
        print(f"前10个特征: {list(features.keys())[:10] if isinstance(features, dict) else 'not dict'}")
        
        # 直接调用市场锚定估价器
        print("开始调试市场锚定估价器...")
        market_evaluator = service.market_evaluator
        
        # 跳过 calculate_value，直接调用 find_market_anchors 来获取详细错误
        print("直接调用 find_market_anchors...")
        try:
            anchors = market_evaluator.find_market_anchors(
                features,
                similarity_threshold=0.7,
                max_anchors=5,
                verbose=True
            )
            print(f"find_market_anchors 成功: {len(anchors)} 个锚点")
            
        except Exception as e:
            print(f"find_market_anchors 失败: {e}")
            print("详细错误信息:")
            traceback.print_exc()
        
    except Exception as e:
        print(f"调试失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_market_anchor()
