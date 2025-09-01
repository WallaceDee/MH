#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化的角色估价测试，专门用于查看详细日志
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# 设置详细的日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True  # 强制重新配置日志
)

# 专门为我们关心的模块设置DEBUG级别
logger = logging.getLogger('src.evaluator.market_anchor_evaluator')
logger.setLevel(logging.DEBUG)

logger2 = logging.getLogger('src.evaluator.market_data_collector')
logger2.setLevel(logging.DEBUG)

def test_simple_valuation():
    """简单的角色估价测试"""
    
    try:
        from src.app.services.role_service import roleService
        
        print("=== 开始简化的角色估价测试 ===")
        
        # 创建角色服务
        service = roleService()
        print("角色服务创建成功")
        
        # 测试估价方法
        print("开始调用角色估价...")
        result = service.get_role_valuation(
            eid="202103231100113-207-EC2D2BNNRLXO",  # 使用真实的角色ID
            year=2025,
            month=9,
            role_type="normal",
            strategy="fair_value",
            similarity_threshold=0.7,
            max_anchors=5  # 减少数量，便于调试
        )
        
        print(f"估价结果: {result}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_valuation()
