#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试装备序列号列表参数修复
"""

import sys
import os
import requests
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_equip_sn_list_parameter():
    """测试装备序列号列表参数"""
    print("=" * 60)
    print("测试装备序列号列表参数修复")
    print("=" * 60)
    
    # 测试数据
    test_equip_sn_list = [
        "8mI003B7yQy",
        "L3I001IX8eU", 
        "L3I001Jsrj4",
        "L3I001VpXIr"
    ]
    
    # 构建URL
    base_url = "http://localhost:8080/api/v1/equipment/"
    params = {
        "page_size": 99,
        "equip_sn_list": test_equip_sn_list
    }
    
    print(f"测试URL: {base_url}")
    print(f"测试参数: {params}")
    print(f"期望结果: 应该只返回 {len(test_equip_sn_list)} 条装备数据")
    
    try:
        # 发送请求
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ 请求成功")
            print(f"返回状态码: {response.status_code}")
            print(f"返回数据总数: {data.get('total', 0)}")
            print(f"返回数据条数: {len(data.get('data', []))}")
            
            # 打印完整的响应数据结构用于调试
            print(f"完整响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 检查返回的装备序列号
            equipment_data = data.get('data', [])
            if isinstance(equipment_data, list):
                returned_equip_sns = [item.get('equip_sn') if isinstance(item, dict) else str(item) for item in equipment_data]
            else:
                returned_equip_sns = []
            print(f"返回的装备序列号: {returned_equip_sns}")
            
            # 验证结果
            if len(data.get('data', [])) == len(test_equip_sn_list):
                print("✅ 返回数据条数正确")
            else:
                print(f"❌ 返回数据条数错误，期望 {len(test_equip_sn_list)}，实际 {len(data.get('data', []))}")
            
            # 检查是否包含所有请求的装备序列号
            missing_sns = set(test_equip_sn_list) - set(returned_equip_sns)
            if not missing_sns:
                print("✅ 包含所有请求的装备序列号")
            else:
                print(f"❌ 缺少装备序列号: {missing_sns}")
            
            # 检查是否有额外的装备序列号
            extra_sns = set(returned_equip_sns) - set(test_equip_sn_list)
            if not extra_sns:
                print("✅ 没有额外的装备序列号")
            else:
                print(f"❌ 包含额外的装备序列号: {extra_sns}")
                
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_equip_sn_list_parameter()
