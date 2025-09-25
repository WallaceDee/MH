#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
编码修复工具
解决Windows下GBK编码无法处理Unicode字符的问题
"""

import os
import sys
import io

def fix_encoding():
    """修复编码问题"""
    try:
        # 设置环境变量强制使用UTF-8
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # 重新配置标准输出和错误输出
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
        
        # 设置默认编码
        if hasattr(sys, 'setdefaultencoding'):
            sys.setdefaultencoding('utf-8')
        
        print("✅ 编码修复完成，现在支持Unicode字符输出")
        return True
        
    except Exception as e:
        print(f"⚠️ 编码修复失败: {e}")
        return False

def safe_print(*args, **kwargs):
    """安全的打印函数，处理编码问题"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # 如果遇到编码错误，尝试使用ASCII替代
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # 替换Unicode字符为ASCII等价字符
                safe_arg = arg.replace('🎉', '[SUCCESS]')
                safe_arg = safe_arg.replace('⚠️', '[WARNING]')
                safe_arg = safe_arg.replace('❌', '[ERROR]')
                safe_arg = safe_arg.replace('📁', '[FILE]')
                safe_arg = safe_arg.replace('📊', '[DATA]')
                safe_arg = safe_arg.replace('🔧', '[FIX]')
                safe_arg = safe_arg.replace('✅', '[OK]')
                safe_args.append(safe_arg)
            else:
                safe_args.append(arg)
        print(*safe_args, **kwargs)

if __name__ == '__main__':
    fix_encoding()
