#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试编码修复功能
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

def test_encoding_fix():
    """测试编码修复功能"""
    print("\n=== 测试编码修复功能 ===")
    
    try:
        from src.spider.encoding_fix import fix_encoding, safe_print
        
        print("1. 测试编码修复...")
        result = fix_encoding()
        if result:
            print("   ✅ 编码修复成功")
        else:
            print("   ❌ 编码修复失败")
        
        print("\n2. 测试Unicode字符输出...")
        try:
            print("   🎉 测试成功字符")
            print("   ⚠️ 测试警告字符")
            print("   ❌ 测试错误字符")
            print("   📁 测试文件字符")
            print("   📊 测试数据字符")
            print("   🔧 测试修复字符")
            print("   ✅ 测试完成字符")
            print("   ✅ Unicode字符输出测试成功")
        except UnicodeEncodeError as e:
            print(f"   ❌ Unicode字符输出失败: {e}")
            print("   使用安全打印函数...")
            safe_print("   🎉 安全打印测试")
            safe_print("   ⚠️ 安全打印测试")
            safe_print("   ❌ 安全打印测试")
        
        print("\n3. 测试爬虫初始化...")
        try:
            from src.spider.equip import CBGEquipSpider
            spider = CBGEquipSpider()
            print("   ✅ 装备爬虫初始化成功")
        except Exception as e:
            print(f"   ❌ 装备爬虫初始化失败: {e}")
        
        try:
            from src.spider.pet import CBGPetSpider
            spider = CBGPetSpider()
            print("   ✅ 召唤兽爬虫初始化成功")
        except Exception as e:
            print(f"   ❌ 召唤兽爬虫初始化失败: {e}")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("编码修复测试")
    print("=" * 50)
    
    test_encoding_fix()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n修复说明:")
    print("1. 设置了PYTHONIOENCODING环境变量为utf-8")
    print("2. 重新配置了标准输出和错误输出的编码")
    print("3. 在爬虫初始化时自动调用编码修复")
    print("4. 提供了安全的打印函数作为备用方案")

if __name__ == '__main__':
    main()
