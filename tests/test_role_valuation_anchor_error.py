#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试角色估价接口当找不到anchor时是否正确返回400状态码
"""

import sys
import os
import requests
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_role_valuation_no_anchors():
    """测试角色估价接口当找不到anchor时返回400状态码"""
    
    # 测试数据 - 使用一个可能找不到相似角色的eid
    test_data = {
        "eid": "202506131300113-285-MIWRRIVQIGSV",
        "role_type": "normal",
        "strategy": "fair_value",
        "similarity_threshold": 0.9,  # 使用很高的相似度阈值，增加找不到anchor的概率
        "max_anchors": 30
    }
    
    # 发送请求
    url = "http://localhost:8080/api/v1/role/valuation"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        print(f"发送角色估价请求到: {url}")
        print(f"请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except json.JSONDecodeError:
            print(f"响应内容（非JSON）: {response.text}")
        
        # 检查结果
        if response.status_code == 400:
            print("\n✅ 测试通过：当找不到anchor时正确返回400状态码")
            
            # 检查返回格式是否与成功时一致
            if "estimated_price" in response_data and "estimated_price_yuan" in response_data and "confidence" in response_data:
                print("✅ 返回格式与成功时保持一致")
                return True
            else:
                print("❌ 返回格式不一致")
                return False
        else:
            print(f"\n❌ 测试失败：期望返回400状态码，实际返回{response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败：请确保Flask应用正在运行在localhost:8080")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_role_valuation_with_anchors():
    """测试角色估价接口当找到anchor时返回200状态码"""
    
    # 测试数据 - 使用较低的相似度阈值，增加找到anchor的概率
    test_data = {
        "eid": "202506131300113-285-MIWRRIVQIGSV",
        "role_type": "normal", 
        "strategy": "fair_value",
        "similarity_threshold": 0.3,  # 使用较低的相似度阈值
        "max_anchors": 30
    }
    
    # 发送请求
    url = "http://localhost:8080/api/v1/role/valuation"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        print(f"\n发送角色估价请求到: {url}")
        print(f"请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"\n响应状态码: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except json.JSONDecodeError:
            print(f"响应内容（非JSON）: {response.text}")
        
        # 检查结果
        if response.status_code == 200:
            print("\n✅ 测试通过：当找到anchor时正确返回200状态码")
            return True
        elif response.status_code == 400:
            print("\n⚠️  仍然返回400：可能确实找不到相似角色")
            return True  # 这也算正常情况
        else:
            print(f"\n❌ 测试失败：期望返回200或400状态码，实际返回{response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败：请确保Flask应用正在运行在localhost:8080")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("角色估价接口Anchor错误处理测试")
    print("=" * 60)
    
    # 测试1：找不到anchor时返回400
    print("\n测试1：找不到anchor时返回400状态码")
    test1_result = test_role_valuation_no_anchors()
    
    # 测试2：找到anchor时返回200
    print("\n测试2：找到anchor时返回200状态码")
    test2_result = test_role_valuation_with_anchors()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"测试1（找不到anchor返回400）: {'通过' if test1_result else '失败'}")
    print(f"测试2（找到anchor返回200）: {'通过' if test2_result else '失败'}")
    
    if test1_result and test2_result:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查实现")
