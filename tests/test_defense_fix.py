#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试防御计算修复，验证熔炼属性不被重复计算
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.evaluator.feature_extractor.equip_feature_extractor import EquipFeatureExtractor

def test_defense_calculation_fix():
    """测试防御计算修复"""
    extractor = EquipFeatureExtractor()
    
    print("🧪 测试防御计算修复...")
    
    # 测试数据1：多参数版本（有完整数据）
    test_data_multi = {
        "kindid": 17,
        "type": 2509,
        "init_defense": 45,  # 多参数版本有直接的init_defense字段
        "large_equip_desc": "#r等级 80  五行 水#r#r防御 +45 魔法 +87#r耐久度 27#r锻炼等级 8  镶嵌宝石 太阳石、 红玛瑙#r#G#G伤害 +16#Y #G命中 +150#Y#Y#r#c4DBAF4特技：#c4DBAF4破血狂攻#Y#Y#r#c4DBAF4套装效果：追加法术满天花雨#Y#Y#r#G开运孔数：3孔/3孔#Y #r#W制造者：微微清水#Y#r#Y熔炼效果：#r#Y#r+10防御 -15魔法 #r#Y"
    }
    
    # 测试数据2：单参数版本（只有描述数据）
    test_data_single = {
        "kindid": 17,
        "type": 2509,
        "large_equip_desc": "#r等级 80  五行 水#r#r防御 +45 魔法 +87#r耐久度 27#r锻炼等级 8  镶嵌宝石 太阳石、 红玛瑙#r#G#G伤害 +16#Y #G命中 +150#Y#Y#r#c4DBAF4特技：#c4DBAF4破血狂攻#Y#Y#r#c4DBAF4套装效果：追加法术满天花雨#Y#Y#r#G开运孔数：3孔/3孔#Y #r#W制造者：微微清水#Y#r#Y熔炼效果：#r#Y#r+10防御 -15魔法 #r#Y"
    }
    
    print("\n📊 测试多参数版本...")
    print(f"数据: {test_data_multi}")
    
    try:
        features_multi = extractor.extract_features(test_data_multi)
        defense_multi = features_multi.get('init_defense', 0)
        ronglian_defense = features_multi.get('init_defense_ronglian', 0)
        
        print(f"多参数版本结果:")
        print(f"  初始防御: {test_data_multi['init_defense']}")
        print(f"  熔炼防御: {ronglian_defense}")
        print(f"  最终防御: {defense_multi}")
        print(f"  期望防御: {test_data_multi['init_defense'] + ronglian_defense}")
        
        expected_multi = test_data_multi['init_defense'] + ronglian_defense
        if defense_multi == expected_multi:
            print("  ✅ 多参数版本计算正确")
        else:
            print(f"  ❌ 多参数版本计算错误！期望 {expected_multi}，实际 {defense_multi}")
            
    except Exception as e:
        print(f"  ❌ 多参数版本测试失败: {e}")
        import traceback
        print(traceback.format_exc())
    
    print("\n📊 测试单参数版本...")
    print(f"数据: {test_data_single}")
    
    try:
        features_single = extractor.extract_features(test_data_single)
        defense_single = features_single.get('init_defense', 0)
        ronglian_defense = features_single.get('init_defense_ronglian', 0)
        
        print(f"单参数版本结果:")
        print(f"  解析后防御: {defense_single}")
        print(f"  熔炼防御: {ronglian_defense}")
        print(f"  期望防御: 45 + 10 = 55")
        
        if defense_single == 55:
            print("  ✅ 单参数版本计算正确")
        else:
            print(f"  ❌ 单参数版本计算错误！期望 55，实际 {defense_single}")
            
    except Exception as e:
        print(f"  ❌ 单参数版本测试失败: {e}")
        import traceback
        print(traceback.format_exc())
    
    print("\n🔍 问题分析:")
    print("修复前：熔炼属性被计算两次")
    print("  1. 标准映射中计算一次")
    print("  2. 特殊情况处理中又计算一次")
    print("  结果：45 + 10 + 10 = 65")
    print("\n修复后：熔炼属性只计算一次")
    print("  1. 标准映射中跳过基础属性")
    print("  2. 特殊情况处理中计算一次")
    print("  结果：45 + 10 = 55")

if __name__ == "__main__":
    print("🚀 开始测试防御计算修复...")
    test_defense_calculation_fix()
    print("\n✨ 测试完成！") 