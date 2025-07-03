#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CBG爬虫后端启动脚本 - 生产模式
性能优化，不启用调试功能
"""

import os
import sys

# 设置生产环境
os.environ['FLASK_ENV'] = 'production'

# 添加src目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

if __name__ == "__main__":
    from app import create_app
    
    print("🚀 CBG爬虫API服务器 - 生产模式")
    print("🌐 API地址: http://localhost:5000")
    print("📱 前端地址: http://localhost:8080 (需要单独启动)")
    print("⚡ 性能优化模式，关闭调试功能")
    print("🚀 Ctrl+C 停止服务器")
    print("-" * 50)
    
    app = create_app()
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=False,
        use_reloader=False,  # 关闭自动重载
        use_debugger=False,  # 关闭调试器
        threaded=True        # 启用多线程支持
    ) 