#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试解析响应数据API
"""

import requests
import json
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_parse_response_api():
    """测试解析响应数据API"""
    
    # API端点
    base_url = "http://localhost:5000"
    api_url = f"{base_url}/api/v1/spider/parse/response"
    
    # 测试数据
    test_cases = [
        {
            "name": "角色数据解析测试",
            "url": "https://xyq.cbg.163.com/cgi-bin/query.py?act=overall_search_role&server_id=9&page=1&order_by=price%20ASC&count=15&search_type=overall_search_role",
            "response_text": "callback_12345({\"errno\":0,\"msg\":\"\",\"data\":{\"page\":1,\"total_page\":10,\"total_count\":100,\"items\":[{\"id\":\"12345\",\"name\":\"测试角色\",\"price\":1000,\"server_name\":\"紫禁城\"}]}});"
        },
        {
            "name": "装备数据解析测试", 
            "url": "https://xyq.cbg.163.com/cgi-bin/query.py?act=overall_search_equip&server_id=9&page=1&order_by=price%20ASC&count=15&search_type=overall_search_equip",
            "response_text": "callback_67890({\"errno\":0,\"msg\":\"\",\"data\":{\"page\":1,\"total_page\":5,\"total_count\":50,\"items\":[{\"id\":\"67890\",\"name\":\"测试装备\",\"price\":500,\"server_name\":\"紫禁城\"}]}});"
        },
        {
            "name": "召唤兽数据解析测试",
            "url": "https://xyq.cbg.163.com/cgi-bin/query.py?act=overall_search_pet&server_id=9&page=1&order_by=price%20ASC&count=15&search_type=overall_search_pet", 
            "response_text": "callback_11111({\"errno\":0,\"msg\":\"\",\"data\":{\"page\":1,\"total_page\":3,\"total_count\":30,\"items\":[{\"id\":\"11111\",\"name\":\"测试召唤兽\",\"price\":800,\"server_name\":\"紫禁城\"}]}});"
        }
    ]
    
    print("开始测试解析响应数据API...")
    print(f"API端点: {api_url}")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['name']}")
        print(f"URL: {test_case['url']}")
        print(f"响应数据长度: {len(test_case['response_text'])} 字符")
        
        try:
            # 发送POST请求
            response = requests.post(
                api_url,
                json={
                    "url": test_case["url"],
                    "response_text": test_case["response_text"]
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get("code") == 200:
                    print("✅ 测试通过")
                else:
                    print(f"❌ 测试失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败: 请确保Flask服务器正在运行 (python run.py)")
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
        
        print("-" * 30)
    
    print("\n测试完成!")

def test_invalid_parameters():
    """测试无效参数"""
    
    base_url = "http://localhost:5000"
    api_url = f"{base_url}/api/v1/spider/parse/response"
    
    print("\n开始测试无效参数...")
    print("=" * 50)
    
    invalid_cases = [
        {
            "name": "缺少url参数",
            "data": {"response_text": "test"}
        },
        {
            "name": "缺少response_text参数", 
            "data": {"url": "https://example.com"}
        },
        {
            "name": "url参数为空",
            "data": {"url": "", "response_text": "test"}
        },
        {
            "name": "response_text参数为空",
            "data": {"url": "https://example.com", "response_text": ""}
        },
        {
            "name": "url参数类型错误",
            "data": {"url": 123, "response_text": "test"}
        },
        {
            "name": "response_text参数类型错误",
            "data": {"url": "https://example.com", "response_text": 123}
        }
    ]
    
    for i, test_case in enumerate(invalid_cases, 1):
        print(f"\n无效参数测试 {i}: {test_case['name']}")
        
        try:
            response = requests.post(
                api_url,
                json=test_case["data"],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"HTTP状态码: {response.status_code}")
            result = response.json()
            print(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get("code") != 200:
                print("✅ 正确返回错误信息")
            else:
                print("❌ 应该返回错误但返回了成功")
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
        
        print("-" * 30)

if __name__ == "__main__":
    print("解析响应数据API测试")
    print("=" * 50)
    
    # 测试正常功能
    test_parse_response_api()
    
    # 测试无效参数
    test_invalid_parameters()
    
    print("\n所有测试完成!")
