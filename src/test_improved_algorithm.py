#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化改进算法测试脚本 - 只使用市场折价系数
"""

import sys
import os
import json

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir) if current_dir.endswith('src') else current_dir
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from evaluator.character_evaluator import CharacterEvaluator

def test_simplified_algorithm():
    """测试简化的改进估价算法"""
    
    print("=== 简化版改进估价算法测试 ===\n")
    
    # 创建评估器实例
    evaluator = CharacterEvaluator()
    
    # 构造测试角色数据
    test_character = {
        'school_history_count': 2,          # 历史门派2个
        'all_new_point': 5,                 # 乾元丹5个
        'qianyuandan_breakthrough': True,    # 乾元丹突破
        'jiyuan_amount': 10,                # 月饼粽子机缘10个
        'sum_exp': 50,                      # 总经验50亿
        'school_skills': [120, 110, 100, 90, 80],  # 师门技能等级
        'packet_page': 2,                   # 行囊页数2页
        'learn_cash': 500000,               # 储备金50万
        'xianyu_amount': 1000,              # 仙玉1000
        'max_expt1': 23, 'max_expt2': 22, 'max_expt3': 21, 'max_expt4': 20,  # 修炼上限
        'expt_ski1': 20, 'expt_ski2': 18, 'expt_ski3': 16, 'expt_ski4': 15,  # 修炼等级
        'beast_ski1': 15, 'beast_ski2': 12, 'beast_ski3': 10, 'beast_ski4': 8,  # 控制力
        'life_skills': [120, 110, 100],     # 生活技能
        'qiangzhuang&shensu': [25, 20],     # 强壮神速
        'lingyou_count': 5,                 # 灵佑次数
        'hight_grow_rider_count': 2,        # 高成长坐骑
        'allow_pet_count': 10,              # 召唤兽携带量
        'premium_fabao_count': 3,           # 有价值法宝
        'shenqi': {                         # 神器数据
            'same9Count': 1,
            'allTheSameCount': 0,
            '1Count': 2,
            '1attrCount': 1,
            '2Count': 1,
            '2attrCount': 1,
            '3Count': 0,
            '3attrCount': 0
        }
    }
    
    print("测试角色属性:")
    for key, value in test_character.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*50)
    print("原始算法计算结果:")
    print("="*50)
    
    try:
        # 使用原始算法
        original_value = evaluator.calc_base_attributes_value(test_character)
        print(f"原始算法估值: {original_value:.2f}")
    except Exception as e:
        print(f"原始算法计算失败: {e}")
        original_value = 0
    
    print("\n" + "="*50)
    print("简化版改进算法计算结果:")
    print("="*50)
    
    try:
        # 使用简化版改进算法
        improved_result = evaluator.calc_base_attributes_value_improved(test_character)
        improved_value = improved_result['final_value']
        value_breakdown = improved_result['value_breakdown']
        
        print(f"简化版改进算法估值: {improved_value:.2f}")
        print(f"原始总价值: {improved_result['total_raw_value']:.2f}")
        
        print("\n价值分解详情:")
        total_check = 0
        for attr, value in value_breakdown.items():
            print(f"  {attr}: {value:.2f}")
            total_check += value
        print(f"  总计验证: {total_check:.2f}")
        
    except Exception as e:
        print(f"简化版改进算法计算失败: {e}")
        import traceback
        traceback.print_exc()
        improved_value = 0
    
    print("\n" + "="*50)
    print("算法对比分析:")
    print("="*50)
    
    if original_value > 0 and improved_value > 0:
        diff = improved_value - original_value
        diff_ratio = (diff / original_value) * 100
        print(f"原始算法: {original_value:.2f}")
        print(f"简化版改进算法: {improved_value:.2f}")
        print(f"差异: {diff:.2f} ({diff_ratio:+.1f}%)")
        
        if abs(diff_ratio) > 50:
            print("⚠️  估值差异较大，可能需要调整折价系数")
        elif abs(diff_ratio) > 20:
            print("⚡ 估值有适度调整，符合市场修正预期")
        else:
            print("✅ 估值调整适中")
    
    print("\n" + "="*50)
    print("市场折价系数检查:")  
    print("="*50)
    
    # 显示当前折价系数（从rate.jsonc文件读取）
    try:
        rate_config_path = os.path.join(os.path.dirname(__file__), 'evaluator', 'rate.jsonc')
        with open(rate_config_path, 'r', encoding='utf-8') as f:
            # 简单处理jsonc格式，去掉注释
            content = f.read()
            # 去掉行注释
            lines = content.split('\n')
            cleaned_lines = []
            for line in lines:
                if '//' in line:
                    line = line[:line.index('//')]
                cleaned_lines.append(line)
            cleaned_content = '\n'.join(cleaned_lines)
            DISCOUNT_RATES = json.loads(cleaned_content)
        
        print("当前折价系数设置:")
        for attr, rate in DISCOUNT_RATES.items():
            print(f"  {attr}: {rate:.2f} ({'高认可' if rate >= 0.8 else '中认可' if rate >= 0.6 else '低认可'})")
    except Exception as e:
        print(f"读取rate.jsonc文件失败: {e}")

def test_different_scenarios():
    """测试不同场景下的估价差异"""
    
    print("\n" + "="*70)
    print("不同场景测试")
    print("="*70)
    
    evaluator = CharacterEvaluator()
    
    scenarios = [
        {
            'name': '低配角色',
            'data': {
                'school_history_count': 0,
                'all_new_point': 1,
                'jiyuan_amount': 2,
                'sum_exp': 10,
                'school_skills': [60, 50, 40],
                'packet_page': 0,
                'learn_cash': 10000,
                'xianyu_amount': 100,
                'lingyou_count': 1,
                'allow_pet_count': 8,
                'shenqi': {}
            }
        },
        {
            'name': '中配角色', 
            'data': {
                'school_history_count': 1,
                'all_new_point': 3,
                'jiyuan_amount': 5,
                'sum_exp': 30,
                'school_skills': [100, 90, 80, 70],
                'packet_page': 1,
                'learn_cash': 200000,
                'xianyu_amount': 500,
                'lingyou_count': 3,
                'allow_pet_count': 9,
                'shenqi': {'1Count': 1}
            }
        },
        {
            'name': '高配角色',
            'data': {
                'school_history_count': 3,
                'all_new_point': 7,
                'qianyuandan_breakthrough': True,
                'jiyuan_amount': 15,
                'sum_exp': 80,
                'school_skills': [150, 140, 130, 120, 110],
                'packet_page': 3,
                'learn_cash': 1000000,
                'xianyu_amount': 2000,
                'lingyou_count': 8,
                'allow_pet_count': 12,
                'hight_grow_rider_count': 3,
                'premium_fabao_count': 5,
                'shenqi': {
                    'same9Count': 1,
                    '1Count': 3,
                    '2Count': 2,
                    '3Count': 1
                }
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        print("-" * 40)
        
        try:
            # 原始算法
            original = evaluator.calc_base_attributes_value(scenario['data'])
            
            # 简化版改进算法
            improved_result = evaluator.calc_base_attributes_value_improved(scenario['data'])
            improved = improved_result['final_value']
            
            diff = improved - original
            diff_ratio = (diff / original) * 100 if original > 0 else 0
            
            print(f"原始算法: {original:.1f}")
            print(f"简化版改进算法: {improved:.1f}")
            print(f"调整幅度: {diff:+.1f} ({diff_ratio:+.1f}%)")
            
        except Exception as e:
            print(f"计算失败: {e}")

if __name__ == "__main__":
    test_simplified_algorithm()
    test_different_scenarios()
    
    print("\n" + "="*70)
    print("测试完成！")
    print("="*70)
    print("\n简化版改进特点：")
    print("1. 只引入市场折价系数，移除复杂的计算逻辑")
    print("2. 使用rate.jsonc文件配置系数，便于调整")
    print("3. 保持原有算法结构，只在最后应用折价系数")
    print("4. 更简单、更易理解和维护")
    print("\n建议：")
    print("1. 根据实际市场数据调整rate.jsonc中的折价系数")
    print("2. 观察不同价位段角色的估值准确性")
    print("3. 定期根据市场反馈优化系数配置") 