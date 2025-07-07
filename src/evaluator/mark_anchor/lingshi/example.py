#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵饰锚定评估器使用示例
"""

import sys
import os
from typing import Dict, Any

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(current_dir))))
sys.path.insert(0, project_root)

from src.evaluator.mark_anchor.lingshi.index import LingshiAnchorEvaluator
from src.evaluator.mark_anchor.lingshi.plugins.ring_plugin import RingPlugin
from src.evaluator.mark_anchor.lingshi.plugins.earring_plugin import EarringPlugin
from src.evaluator.mark_anchor.lingshi.plugins.bracelet_plugin import BraceletPlugin
from src.evaluator.mark_anchor.lingshi.plugins.pendant_plugin import PendantPlugin


def main():
    """主函数 - 演示灵饰锚定评估器的使用"""
    
    print("=== 灵饰锚定评估器使用示例 ===\n")
    
    # 1. 创建评估器实例
    print("1. 初始化评估器...")
    evaluator = LingshiAnchorEvaluator()
    
    # 2. 注册插件
    print("2. 注册插件...")
    evaluator.add_plugin(RingPlugin())
    evaluator.add_plugin(EarringPlugin())
    evaluator.add_plugin(BraceletPlugin())
    evaluator.add_plugin(PendantPlugin())
    
    # 3. 示例灵饰数据
    print("3. 准备示例数据...")
    
    # 戒指示例
    ring_example = {
        'kindid': 61,
        'equip_level': 100,
        'large_equip_desc': '等级 100#r伤害 +20#r耐久度 500#r#G伤害 +12#r#G法术伤害 +10#r#W制造者：月入一头牛强化打造#',
        'price': 50000,  # 这个价格会被覆盖
        'server': '测试服务器'
    }
    
    # 耳饰示例
    earring_example = {
        'kindid': 62,
        'equip_level': 100,
        'large_equip_desc': '等级 100#r法术伤害 +18#r耐久度 500#r#G法术伤害 +15#r#G速度 +8#r#W制造者：测试强化打造#',
        'price': 80000,
        'server': '测试服务器'
    }
    
    # 手镯示例
    bracelet_example = {
        'kindid': 63,
        'equip_level': 100,
        'large_equip_desc': '等级 100#r封印命中等级 +16#r耐久度 500#r#G气血 +120#r#G防御 +8#r#W制造者：测试强化打造#',
        'price': 60000,
        'server': '测试服务器'
    }
    
    # 佩饰示例
    pendant_example = {
        'kindid': 64,
        'equip_level': 100,
        'large_equip_desc': '等级 100#r速度 +12#r耐久度 500#r#G速度 +10#r#G气血 +100#r#W制造者：测试强化打造#',
        'price': 70000,
        'server': '测试服务器'
    }
    
    examples = [
        ('戒指', ring_example),
        ('耳饰', earring_example),
        ('手镯', bracelet_example),
        ('佩饰', pendant_example)
    ]
    
    # 4. 进行估价
    print("4. 开始估价...\n")
    
    for name, example_data in examples:
        print(f"--- {name}估价 ---")
        
        try:
            # 提取特征
            features = evaluator.mark_data_collector.feature_extractor.extract_features(example_data)
            features.update(example_data)  # 合并原始数据
            
            print(f"提取的特征: {features}")
            
            # 计算价值
            result = evaluator.calculate_value(
                target_features=features,
                strategy='fair_value',
                similarity_threshold=0.6,
                max_anchors=20
            )
            
            if result['success']:
                print(f"估价结果:")
                print(f"  价值: {result['value']:,} 金币")
                print(f"  置信度: {result['confidence']:.3f}")
                print(f"  锚点数量: {result['anchor_count']}")
                print(f"  策略: {result['strategy']}")
                
                if result['anchors']:
                    print(f"  前3个锚点:")
                    for i, anchor in enumerate(result['anchors'][:3]):
                        print(f"    {i+1}. 相似度:{anchor['similarity']:.3f}, 价格:{anchor['price']:,}, 服务器:{anchor['server']}")
            else:
                print(f"估价失败: {result['message']}")
                
        except Exception as e:
            print(f"处理失败: {e}")
        
        print()
    
    # 5. 批量估价示例
    print("5. 批量估价示例...")
    
    try:
        batch_results = evaluator.batch_valuation(
            lingshi_list=[ring_example, earring_example, bracelet_example, pendant_example],
            strategy='fair_value'
        )
        
        print("批量估价结果:")
        for i, result in enumerate(batch_results):
            name = examples[i][0]
            if result['success']:
                print(f"  {name}: {result['value']:,} 金币 (置信度: {result['confidence']:.3f})")
            else:
                print(f"  {name}: 估价失败 - {result['message']}")
                
    except Exception as e:
        print(f"批量估价失败: {e}")
    
    print("\n=== 示例完成 ===")


if __name__ == "__main__":
    main() 