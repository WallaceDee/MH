#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask应用工厂
"""

from flask import Flask
from flask_cors import CORS
from flask_caching import Cache
from .blueprints.api.v1 import api_v1_bp
from .utils.response import register_error_handlers
from .utils.logger import setup_logging
from src.database import init_database


def init_cache(app):
    """初始化Flask-Caching缓存"""
    # Flask-Caching配置
    app.config.update({
        'CACHE_TYPE': 'RedisCache',
        'CACHE_REDIS_HOST': app.config.get('REDIS_HOST', '47.86.33.98'),
        'CACHE_REDIS_PORT': app.config.get('REDIS_PORT', 6379),
        'CACHE_REDIS_PASSWORD': app.config.get('REDIS_PASSWORD', '447363121'),
        'CACHE_REDIS_DB': app.config.get('REDIS_DB', 0),
        'CACHE_DEFAULT_TIMEOUT': 6 * 3600,  # 6小时默认超时
        'CACHE_KEY_PREFIX': 'cbg_market:',
        'CACHE_REDIS_URL': None  # 使用单独的host/port配置
    })
    
    # 初始化缓存
    cache = Cache()
    
    try:
        cache.init_app(app)
        
        # 测试缓存连接
        with app.app_context():
            cache.set('test_key', 'test_value', timeout=10)
            test_result = cache.get('test_key')
            if test_result == 'test_value':
                print(" Flask-Caching 初始化成功，Redis连接正常")
                cache.delete('test_key')  # 清理测试键
            else:
                print(" Flask-Caching 初始化成功，但Redis连接可能有问题")
    except Exception as e:
        print(f" Flask-Caching 初始化警告: {e}")
        print(" 将使用内存缓存作为降级方案")
        
        # 降级到内存缓存
        app.config['CACHE_TYPE'] = 'SimpleCache'
        cache = Cache()
        cache.init_app(app)
    
    return cache


def create_app(config_name='default'):
    """应用工厂函数"""
    # 检查是否存在前端构建文件
    import os
    from pathlib import Path
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent
    static_folder = project_root / 'web' / 'dist'
    template_folder = static_folder
    
    # 如果存在前端构建文件，使用静态文件服务
    if static_folder.exists() and (static_folder / 'index.html').exists():
        app = Flask(__name__, 
                   static_folder=str(static_folder),
                   static_url_path='',
                   template_folder=str(template_folder))
        print(f" 前端静态文件路径: {static_folder}")
    else:
        app = Flask(__name__)
        print(" 未找到前端构建文件，仅提供API服务")
    
    # 配置CORS
    CORS(app)
    
    # 设置日志
    setup_logging(app)
    
    # 初始化数据库
    init_database(app)
    
    # 配置Flask-Caching
    cache = init_cache(app)
    
    # 将缓存实例绑定到应用，方便外部访问
    app.cache = cache
    
    # 注册蓝图
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 前端静态文件路由
    if static_folder.exists() and (static_folder / 'index.html').exists():
        from flask import send_from_directory, send_file
        
        @app.route('/')
        def index():
            """服务前端首页"""
            return send_file(str(static_folder / 'index.html'))
        
        @app.route('/<path:path>')
        def serve_static(path):
            """服务静态文件"""
            # 如果请求的是文件且存在，直接返回
            file_path = static_folder / path
            if file_path.exists() and file_path.is_file():
                return send_from_directory(str(static_folder), path)
            
            # 对于SPA路由，返回index.html让前端路由处理
            if not '.' in path:  # 没有扩展名的路径，可能是前端路由
                return send_file(str(static_folder / 'index.html'))
            
            # 文件不存在，返回404
            from flask import abort
            abort(404)
        
        print(" 前端静态文件服务已启用")
    else:
        # 根路由 - 仅API模式
        @app.route('/')
        def index():
            from .utils.response import success_response
            return success_response(data={
                "message": "CBG Spider API Server",
                "version": "2.0",
                "frontend": "请访问前端项目: http://localhost:8080"
            })
    
    return app 