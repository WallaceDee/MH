#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单个宠物信息解析用例
"""

import json
import sys
import os
from decode_desc import parse_pet_info

def test_single_case():
    """测试单个用例"""
    # 加载测试数据
    test_file = os.path.join(os.path.dirname(__file__), 'test.json')
    with open(test_file, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    
    # 测试第三个用例
    test_case = test_cases[2]
    desc = test_case['desc']
    expected_result = test_case['petData']
    
    print(f"测试宠物: {expected_result.get('pet_name', 'Unknown')}")
    print(f"宠物ID: {expected_result.get('type_id', 'Unknown')}")
    
    try:
        # 使用Python版本解析
        py_result = parse_pet_info(desc)
        
        print("\n=== Python解析结果 ===")
        print(f"pet_name: {py_result.get('pet_name')}")
        print(f"type_id: {py_result.get('type_id')}")
        print(f"pet_grade: {py_result.get('pet_grade')}")
        print(f"blood: {py_result.get('blood')}")
        print(f"magic: {py_result.get('magic')}")
        print(f"attack: {py_result.get('attack')}")
        print(f"defence: {py_result.get('defence')}")
        print(f"speed: {py_result.get('speed')}")
        
        print("\n=== JavaScript期望结果 ===")
        print(f"pet_name: {expected_result.get('pet_name')}")
        print(f"type_id: {expected_result.get('type_id')}")
        print(f"pet_grade: {expected_result.get('pet_grade')}")
        print(f"blood: {expected_result.get('blood')}")
        print(f"magic: {expected_result.get('magic')}")
        print(f"attack: {expected_result.get('attack')}")
        print(f"defence: {expected_result.get('defence')}")
        print(f"speed: {expected_result.get('speed')}")
        
        # 比较关键字段
        key_fields = ['pet_name', 'type_id', 'pet_grade', 'blood', 'magic', 'attack', 'defence', 'speed']
        print("\n=== 差异对比 ===")
        for field in key_fields:
            py_val = py_result.get(field)
            js_val = expected_result.get(field)
            if py_val != js_val:
                print(f"❌ {field}: Python={py_val}, JS={js_val}")
            else:
                print(f"✅ {field}: {py_val}")
        
        # 比较进阶加点
        print("\n=== 进阶加点对比 ===")
        py_ti = py_result.get('ti_zhi_add')
        js_ti = expected_result.get('ti_zhi_add')
        print(f"ti_zhi_add: Python={py_ti}, JS={js_ti}")
        
        py_fa = py_result.get('fa_li_add')
        js_fa = expected_result.get('fa_li_add')
        print(f"fa_li_add: Python={py_fa}, JS={js_fa}")
        
        py_li = py_result.get('li_liang_add')
        js_li = expected_result.get('li_liang_add')
        print(f"li_liang_add: Python={py_li}, JS={js_li}")
        
        py_nai = py_result.get('nai_li_add')
        js_nai = expected_result.get('nai_li_add')
        print(f"nai_li_add: Python={py_nai}, JS={js_nai}")
        
        py_min = py_result.get('min_jie_add')
        js_min = expected_result.get('min_jie_add')
        print(f"min_jie_add: Python={py_min}, JS={js_min}")
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_case() 