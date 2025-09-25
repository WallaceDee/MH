#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CBG爬虫Web界面 - 重构版Flask应用
"""

import os
import sys

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # 向上到src目录
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.project_path import get_project_root

from app import create_app


def main():
    """启动API服务器"""
    # 检查是否为开发模式
    is_development = os.getenv('FLASK_ENV', 'development').lower() == 'development'
    
    print(" CBG爬虫API服务器启动中...")
    print(" API地址: http://localhost:5000")
    print(" 前端地址: http://localhost:8080 (需要单独启动)")
    
    if is_development:
        print(" 开发模式：启用自动重载和调试功能")
        print(" 修改代码后将自动重启服务器")
    else:
        print(" 生产模式：性能优化模式")
    
    app = create_app()
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=is_development,
        use_reloader=is_development,  # 启用自动重载
        use_debugger=is_development,  # 启用调试器
        threaded=True  # 启用多线程支持
    )


if __name__ == "__main__":
    main() 