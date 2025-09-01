#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角色估价接口测试（更新版）
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

def test_role_valuation_api():
    """测试角色估价API"""
    
    # API基础URL
    base_url = "http://localhost:5000/api/v1"
    
    print("=== 测试角色估价API（更新版） ===")
    
    # 1. 测试单个角色估价
    print("\n1. 测试单个角色估价")
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
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 单个角色估价成功")
            print(f"   估价结果: {result.get('data', {}).get('estimated_price_yuan', 0)}元")
            print(f"   置信度: {result.get('data', {}).get('confidence', 0)}")
        else:
            print(f"❌ 单个角色估价失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 单个角色估价请求异常: {e}")
    
    # 2. 测试批量角色估价
    print("\n2. 测试批量角色估价")
    try:
        response = requests.post(
            f"{base_url}/role/batch-valuation",
            json={
                "eid_list": ["test_role_123", "test_role_456"],  # 测试角色eid列表
                "year": 2025,
                "month": 1,
                "role_type": "normal",
                "strategy": "fair_value",
                "similarity_threshold": 0.7,
                "max_anchors": 30,
                "verbose": True
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 批量角色估价成功")
            print(f"   总角色数: {result.get('data', {}).get('total_roles', 0)}")
            print(f"   成功数: {result.get('data', {}).get('success_count', 0)}")
            print(f"   总价值: {result.get('data', {}).get('total_value_yuan', 0)}元")
        else:
            print(f"❌ 批量角色估价失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 批量角色估价请求异常: {e}")
    
    # 3. 测试通过eid获取估价（便捷接口）
    print("\n3. 测试通过eid获取估价（便捷接口）")
    print("   注意: 此测试需要数据库中已有角色数据")
    
    # 4. 测试不同策略
    print("\n4. 测试不同估价策略")
    strategies = ['fair_value', 'competitive', 'premium']
    
    for strategy in strategies:
        try:
            response = requests.post(
                f"{base_url}/role/valuation",
                json={
                    "eid": "test_role_123",
                    "year": 2025,
                    "month": 1,
                    "strategy": strategy,
                    "similarity_threshold": 0.7,
                    "max_anchors": 30
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                estimated_price = result.get('data', {}).get('estimated_price_yuan', 0)
                print(f"   ✅ {strategy}: {estimated_price}元")
            else:
                print(f"   ❌ {strategy}: 失败 ({response.status_code})")
                
        except Exception as e:
            print(f"   ❌ {strategy}: 异常 ({e})")
    
    print("\n=== 测试完成 ===")

def test_role_valuation_parameters():
    """测试角色估价参数验证"""
    
    base_url = "http://localhost:5000/api/v1"
    
    print("\n=== 测试角色估价参数验证 ===")
    
    # 1. 测试缺少eid参数
    print("\n1. 测试缺少eid参数")
    try:
        response = requests.post(
            f"{base_url}/role/valuation",
            json={
                "year": 2025,
                "month": 1,
                "strategy": "fair_value",
                "similarity_threshold": 0.7,
                "max_anchors": 30
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ 缺少eid参数验证成功")
        else:
            print(f"❌ 缺少eid参数验证失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 缺少eid参数验证异常: {e}")
    
    # 2. 测试无效年份参数
    print("\n2. 测试无效年份参数")
    try:
        response = requests.post(
            f"{base_url}/role/valuation",
            json={
                "eid": "test_role_123",
                "year": "invalid_year",
                "month": 1,
                "strategy": "fair_value",
                "similarity_threshold": 0.7,
                "max_anchors": 30
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ 无效年份参数验证成功")
        else:
            print(f"❌ 无效年份参数验证失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 无效年份参数验证异常: {e}")
    
    # 3. 测试无效月份参数
    print("\n3. 测试无效月份参数")
    try:
        response = requests.post(
            f"{base_url}/role/valuation",
            json={
                "eid": "test_role_123",
                "year": 2025,
                "month": "invalid_month",
                "strategy": "fair_value",
                "similarity_threshold": 0.7,
                "max_anchors": 30
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ 无效月份参数验证成功")
        else:
            print(f"❌ 无效月份参数验证失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 无效月份参数验证异常: {e}")
    
    # 4. 测试无效策略
    print("\n4. 测试无效策略")
    try:
        response = requests.post(
            f"{base_url}/role/valuation",
            json={
                "eid": "test_role_123",
                "year": 2025,
                "month": 1,
                "strategy": "invalid_strategy",
                "similarity_threshold": 0.7,
                "max_anchors": 30
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ 无效策略参数验证成功")
        else:
            print(f"❌ 无效策略参数验证失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 无效策略参数验证异常: {e}")
    
    print("\n=== 参数验证测试完成 ===")

def test_batch_valuation_parameters():
    """测试批量角色估价参数验证"""
    
    base_url = "http://localhost:5000/api/v1"
    
    print("\n=== 测试批量角色估价参数验证 ===")
    
    # 1. 测试缺少eid_list参数
    print("\n1. 测试缺少eid_list参数")
    try:
        response = requests.post(
            f"{base_url}/role/batch-valuation",
            json={
                "year": 2025,
                "month": 1,
                "strategy": "fair_value",
                "similarity_threshold": 0.7,
                "max_anchors": 30
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ 缺少eid_list参数验证成功")
        else:
            print(f"❌ 缺少eid_list参数验证失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 缺少eid_list参数验证异常: {e}")
    
    # 2. 测试空eid_list参数
    print("\n2. 测试空eid_list参数")
    try:
        response = requests.post(
            f"{base_url}/role/batch-valuation",
            json={
                "eid_list": [],
                "year": 2025,
                "month": 1,
                "strategy": "fair_value",
                "similarity_threshold": 0.7,
                "max_anchors": 30
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ 空eid_list参数验证成功")
        else:
            print(f"❌ 空eid_list参数验证失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 空eid_list参数验证异常: {e}")
    
    print("\n=== 批量估价参数验证测试完成 ===")

if __name__ == "__main__":
    print("开始测试更新后的角色估价接口...")
    
    # 测试基本功能
    test_role_valuation_api()
    
    # 测试参数验证
    test_role_valuation_parameters()
    
    # 测试批量估价参数验证
    test_batch_valuation_parameters()
    
    print("\n所有测试完成！")
