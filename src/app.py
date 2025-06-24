#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CBG爬虫Web界面 - 重构版Flask应用
"""

import os
import sys

# 添加src目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from app import create_app


def main():
    """启动API服务器"""
    print("🌐 CBG爬虫API服务器启动中...")
    print("🔗 API地址: http://localhost:5000")
    print("📱 前端地址: http://localhost:8080 (需要单独启动)")
    
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == "__main__":
    main() 