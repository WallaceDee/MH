#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
召唤兽信息解析比较脚本
比较Python版本和JavaScript版本的解析结果差异
"""

import json
import sys
import os
from typing import Dict, Any, List, Set
from decode_desc import parse_pet_info

def load_test_data() -> List[Dict]:
    """加载测试数据"""
    test_file = os.path.join(os.path.dirname(__file__), 'test.json')
    with open(test_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def compare_dicts(py_result: Dict, js_result: Dict, path: str = "") -> List[str]:
    """递归比较两个字典的差异"""
    differences = []
    
    # 获取所有键
    py_keys = set(py_result.keys())
    js_keys = set(js_result.keys())
    
    # 检查缺失的键
    missing_in_py = js_keys - py_keys
    missing_in_js = py_keys - js_keys
    
    for key in missing_in_py:
        differences.append(f"{path}.{key}: 缺失于Python版本")
    
    # 对于Python有而JavaScript缺失的键，检查是否为0值
    for key in missing_in_js:
        py_value = py_result[key]
        # 如果Python值为0、空字符串、空列表、None等"空"值，则视为一致
        if (py_value == 0 or py_value == "" or py_value == [] or 
            py_value is None or (isinstance(py_value, (int, float)) and py_value == 0)):
            continue  # 跳过这个差异
        differences.append(f"{path}.{key}: 缺失于JavaScript版本")
        differences.append(f"{path}.{key}: Python值: {py_value}")
    
    # 比较共同键的值
    common_keys = py_keys & js_keys
    for key in common_keys:
        current_path = f"{path}.{key}" if path else key
        py_value = py_result[key]
        js_value = js_result[key]
        
        # 检查空值等价性：[] 等价于 None，"" 等价于 None
        if ((py_value == [] and js_value is None) or 
            (js_value == [] and py_value is None) or
            (py_value == "" and js_value is None) or
            (js_value == "" and py_value is None)):
            continue  # 跳过这个差异
        # 新增：如果str值相等，视为一致
        if str(py_value) == str(js_value):
            continue
        if isinstance(py_value, dict) and isinstance(js_value, dict):
            # 递归比较字典
            differences.extend(compare_dicts(py_value, js_value, current_path))
        elif isinstance(py_value, str) and isinstance(js_value, str):
            # 对字符串strip后再比较
            if py_value.strip() != js_value.strip():
                differences.append(f"{current_path}: 值不同 (Python: {py_value}, JS: {js_value})")
        elif isinstance(py_value, list) and isinstance(js_value, list):
            # 比较列表
            if len(py_value) != len(js_value):
                differences.append(f"{current_path}: 列表长度不同 (Python: {len(py_value)}, JS: {len(js_value)})")
            else:
                for i, (py_item, js_item) in enumerate(zip(py_value, js_value)):
                    # 新增：如果str值相等，视为一致
                    if str(py_item) == str(js_item):
                        continue
                    if isinstance(py_item, dict) and isinstance(js_item, dict):
                        differences.extend(compare_dicts(py_item, js_item, f"{current_path}[{i}]"))
                    elif py_item != js_item:
                        differences.append(f"{current_path}[{i}]: 值不同 (Python: {py_item}, JS: {js_item})")
        elif py_value != js_value:
            # 比较基本类型
            differences.append(f"{current_path}: 值不同 (Python: {py_value}, JS: {js_value})")
    
    return differences

def analyze_differences(test_cases: List[Dict]) -> None:
    """分析所有测试用例的差异"""
    print("🔍 开始分析Python版本和JavaScript版本的差异")
    print("=" * 80)
    
    total_cases = len(test_cases)
    cases_with_diffs = 0
    cases_matched = 0
    
    for i, test_case in enumerate(test_cases, 1):
        desc = test_case['desc']
        expected_result = test_case['petData']
        
        try:
            # 使用Python版本解析
            py_result = parse_pet_info(desc)
            
            # 比较结果
            differences = compare_dicts(py_result, expected_result)
            
            if differences:
                cases_with_diffs += 1
                print(f"\n 测试用例 {i}/{total_cases}")
                print(f"召唤兽名称: {expected_result.get('pet_name', 'Unknown')}")
                print(f"召唤兽ID: {expected_result.get('type_id', 'Unknown')}")
                print(f" 发现 {len(differences)} 个差异:")
                
                # 按路径分组显示差异
                diff_groups = {}
                for diff in differences:
                    path = diff.split(':')[0]
                    if path not in diff_groups:
                        diff_groups[path] = []
                    diff_groups[path].append(diff)
                
                for path, diffs in diff_groups.items():
                    print(f"  📍 {path}:")
                    for diff in diffs[:3]:  # 只显示前3个差异
                        print(f"    - {diff.split(':', 1)[1].strip()}")
                    if len(diffs) > 3:
                        print(f"    ... 还有 {len(diffs) - 3} 个差异")
                
                # 显示关键字段的差异
                key_fields = ['pet_name', 'type_id', 'pet_grade', 'blood', 'magic', 'attack', 'defence', 'speed']
                print("  🔑 关键字段对比:")
                for field in key_fields:
                    py_val = py_result.get(field)
                    js_val = expected_result.get(field)
                    if py_val != js_val:
                        print(f"    {field}: Python={py_val}, JS={js_val}")
                
            else:
                cases_matched += 1
                # 完全匹配时不输出任何日志
                
        except Exception as e:
            print(f"\n 测试用例 {i}/{total_cases}")
            print(f"召唤兽名称: {expected_result.get('pet_name', 'Unknown')}")
            print(f"召唤兽ID: {expected_result.get('type_id', 'Unknown')}")
            print(f" 解析失败: {e}")
            cases_with_diffs += 1
    
    print("\n" + "=" * 80)
    print(f" 总结: {total_cases} 个测试用例中，{cases_matched} 个完全匹配，{cases_with_diffs} 个有差异")
    
    if cases_with_diffs > 0:
        print(" 需要修复Python版本的解析逻辑")
    else:
        print(" 所有测试用例都通过！")

def detailed_analysis(test_cases: List[Dict]) -> None:
    """详细分析第一个有差异的测试用例"""
    print("\n🔬 详细分析第一个有差异的测试用例")
    print("=" * 80)
    
    for test_case in test_cases:
        desc = test_case['desc']
        expected_result = test_case['petData']
        
        try:
            py_result = parse_pet_info(desc)
            differences = compare_dicts(py_result, expected_result)
            
            if differences:
                print(f"召唤兽名称: {expected_result.get('pet_name', 'Unknown')}")
                print(f"召唤兽ID: {expected_result.get('type_id', 'Unknown')}")
                print(f"发现 {len(differences)} 个差异:")
                
                # 按类型分组显示差异
                type_groups = {
                    '基础属性': [],
                    '进阶属性': [],
                    '装备信息': [],
                    '内丹信息': [],
                    '技能信息': [],
                    '其他': []
                }
                
                for diff in differences:
                    path = diff.split(':')[0]
                    if any(keyword in path.lower() for keyword in ['name', 'grade', 'blood', 'magic', 'attack', 'defence', 'speed']):
                        type_groups['基础属性'].append(diff)
                    elif any(keyword in path.lower() for keyword in ['jinjie', 'evol', 'ext']):
                        type_groups['进阶属性'].append(diff)
                    elif any(keyword in path.lower() for keyword in ['equip', '装备']):
                        type_groups['装备信息'].append(diff)
                    elif any(keyword in path.lower() for keyword in ['neidan', '内丹']):
                        type_groups['内丹信息'].append(diff)
                    elif any(keyword in path.lower() for keyword in ['skill', '技能']):
                        type_groups['技能信息'].append(diff)
                    else:
                        type_groups['其他'].append(diff)
                
                for category, diffs in type_groups.items():
                    if diffs:
                        print(f"\n  📂 {category} ({len(diffs)} 个差异):")
                        for diff in diffs[:5]:  # 只显示前5个
                            print(f"    - {diff}")
                        if len(diffs) > 5:
                            print(f"    ... 还有 {len(diffs) - 5} 个差异")
                
                # 显示原始数据的关键部分
                print(f"\n  📄 原始描述数据 (前200字符):")
                print(f"    {desc[:200]}...")
                
                break
            # 如果完全匹配，不输出任何信息，继续下一个测试用例
                
        except Exception as e:
            print(f"解析失败: {e}")
            continue

def main():
    """主函数"""
    try:
        # 加载测试数据
        test_cases = load_test_data()
        print(f" 加载了 {len(test_cases)} 个测试用例")
        
        # 分析差异
        analyze_differences(test_cases)
        
        # 详细分析
        detailed_analysis(test_cases)
        
    except Exception as e:
        print(f" 程序执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 