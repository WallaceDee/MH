#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试角色估价接口修复
"""

import sys
import os
import json
import requests

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

def test_role_valuation_fix():
    """测试角色估价接口修复"""
    
    # API基础URL
    base_url = "http://localhost:5000/api/v1"
    
    print("=== 测试角色估价接口修复 ===")
    
    # 1. 测试单个角色估价（使用修复后的接口）
    print("\n1. 测试单个角色估价（修复版）")
    try:
        response = requests.post(
            f"{base_url}/role/valuation",
            json={
                "eid": "test_role_123",  # 测试角色eid
                "year": 2025,
                "month": 1,
                "role_type": "normal",
                "strategy": "fair_value",
                "similarity_threshold": 0.7,
                "max_anchors": 30
            },
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text[:500]}...")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print("✅ 角色估价成功！")
                print(f"估价结果: {result.get('data', {})}")
            else:
                print(f"❌ 角色估价失败: {result.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求异常: {e}")
    except Exception as e:
        print(f"❌ 测试异常: {e}")
    
    # 2. 测试批量角色估价（使用修复后的接口）
    print("\n2. 测试批量角色估价（修复版）")
    try:
        response = requests.post(
            f"{base_url}/role/batch-valuation",
            json={
                "eid_list": ["test_role_123", "test_role_456"],
                "year": 2025,
                "month": 1,
                "role_type": "normal",
                "strategy": "fair_value",
                "similarity_threshold": 0.7,
                "max_anchors": 30,
                "verbose": True
            },
            timeout=60
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text[:500]}...")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print("✅ 批量角色估价成功！")
                print(f"估价结果: {result.get('data', {})}")
            else:
                print(f"❌ 批量角色估价失败: {result.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求异常: {e}")
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_role_valuation_fix()
