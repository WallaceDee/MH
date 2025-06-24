#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON序列化问题检查工具

用于检测代码中可能导致JSON序列化失败的numpy数据类型使用
"""

import os
import re
import sys
from pathlib import Path

def check_numpy_serialization_issues(file_path):
    """检查单个文件中的numpy序列化问题"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        print(f"❌ 无法读取文件 {file_path}: {e}")
        return []
    
    # 检查模式
    patterns = [
        # 直接返回numpy计算结果
        (r'return.*np\.(mean|median|std|var|percentile|min|max)', 
         "直接返回numpy计算结果，可能导致序列化问题"),
        
        # 字典中包含numpy计算
        (r"['\"][\w_]+['\"]:\s*np\.(mean|median|std|var|percentile|min|max)",
         "字典值包含numpy计算结果，需要用float()包装"),
         
        # 列表中包含numpy计算
        (r'\[.*np\.(mean|median|std|var|percentile|min|max).*\]',
         "列表包含numpy计算结果，需要类型转换"),
         
        # 变量赋值numpy计算但没有转换
        (r'(\w+)\s*=\s*np\.(mean|median|std|var|percentile|min|max)\(',
         "变量赋值numpy计算结果，如果用于API返回需要类型转换"),
    ]
    
    for line_num, line in enumerate(lines, 1):
        for pattern, description in patterns:
            if re.search(pattern, line):
                # 检查是否已经被float()或int()包装
                if not re.search(r'(float|int)\s*\(\s*np\.', line):
                    issues.append({
                        'file': file_path,
                        'line': line_num,
                        'content': line.strip(),
                        'issue': description
                    })
    
    return issues

def check_directory(directory):
    """检查目录下的所有Python文件"""
    all_issues = []
    python_files = []
    
    # 查找所有Python文件
    for root, dirs, files in os.walk(directory):
        # 跳过虚拟环境和缓存目录
        dirs[:] = [d for d in dirs if d not in ['.venv', 'venv', '__pycache__', '.git', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"🔍 检查 {len(python_files)} 个Python文件...")
    
    for file_path in python_files:
        issues = check_numpy_serialization_issues(file_path)
        all_issues.extend(issues)
    
    return all_issues

def main():
    """主函数"""
    print("🚀 JSON序列化问题检查工具")
    print("=" * 50)
    
    # 检查src目录
    src_dir = Path(__file__).parent.parent / 'src'
    if not src_dir.exists():
        print("❌ 找不到src目录")
        return
    
    issues = check_directory(str(src_dir))
    
    if not issues:
        print("✅ 未发现潜在的JSON序列化问题")
        return
    
    print(f"⚠️  发现 {len(issues)} 个潜在问题:")
    print("-" * 50)
    
    for issue in issues:
        print(f"📁 文件: {issue['file']}")
        print(f"📍 行号: {issue['line']}")
        print(f"📝 代码: {issue['content']}")
        print(f"⚠️  问题: {issue['issue']}")
        print("-" * 30)
    
    print("\n💡 修复建议:")
    print("1. 在numpy计算结果外包装 float() 或 int()")
    print("2. 例如: float(np.mean(data)) 替代 np.mean(data)")
    print("3. 参考: docs/开发规则.md")

if __name__ == '__main__':
    main() 