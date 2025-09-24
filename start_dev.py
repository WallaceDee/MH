#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CBG爬虫后端启动脚本 - 开发模式
启用自动重载和调试功能，使用MySQL数据库
"""

import os
import sys

# 设置开发环境
os.environ['FLASK_ENV'] = 'development'

# 配置 Flask 自动重载排除目录
os.environ['WERKZEUG_IGNORED_DIRECTORIES'] = 'web,node_modules,logs,output,data,__pycache__,.git,tests'

# 设置MySQL数据库环境变量
os.environ['DATABASE_TYPE'] = 'mysql'
os.environ['MYSQL_HOST'] = '47.86.33.98'
os.environ['MYSQL_PORT'] = '3306'
os.environ['MYSQL_USER'] = 'lingtong'
os.environ['MYSQL_PASSWORD'] = '447363121'
os.environ['MYSQL_DATABASE'] = 'cbg_spider'
os.environ['MYSQL_CHARSET'] = 'utf8mb4'

# 设置Redis缓存环境变量
os.environ['REDIS_HOST'] = '47.86.33.98'
os.environ['REDIS_PORT'] = '6379'
os.environ['REDIS_PASSWORD'] = '447363121'
os.environ['REDIS_DB'] = '0'

# 添加src目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

if __name__ == "__main__":
    from app import create_app
    
    print("🔧 CBG爬虫API服务器 - 开发模式")
    print("🌐 API地址: http://localhost:5000")
    print("📱 前端地址: http://localhost:8080 (需要单独启动)")
    print("🗄️ 数据库: MySQL")
    print(f"📍 MySQL主机: {os.environ.get('MYSQL_HOST', 'localhost')}")
    print(f"📊 MySQL数据库: {os.environ.get('MYSQL_DATABASE', 'cbg_spider')}")
    print("⚡ Redis缓存: 已启用")
    print(f"🔑 Redis服务器: {os.environ.get('MYSQL_HOST', 'localhost')}:{os.environ.get('REDIS_PORT', '6379')}")
    print("💡 修改代码后将自动重启服务器")
    print("🚀 Ctrl+C 停止服务器")
    print("-" * 50)
    
    app = create_app()
    
    print("✅ 已配置排除目录：web, node_modules, logs, output, data, __pycache__, .git, tests")
    
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=True,
        use_reloader=True,  # 启用自动重载
        use_debugger=True,  # 启用调试器
        threaded=True,      # 启用多线程支持
        extra_files=None,   # 监控额外文件变化
        reloader_interval=1 # 检查文件变化的间隔（秒）
    ) 