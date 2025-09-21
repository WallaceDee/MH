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
                print("✅ Flask-Caching 初始化成功，Redis连接正常")
                cache.delete('test_key')  # 清理测试键
            else:
                print("⚠️ Flask-Caching 初始化成功，但Redis连接可能有问题")
    except Exception as e:
        print(f"⚠️ Flask-Caching 初始化警告: {e}")
        print("💡 将使用内存缓存作为降级方案")
        
        # 降级到内存缓存
        app.config['CACHE_TYPE'] = 'SimpleCache'
        cache = Cache()
        cache.init_app(app)
    
    return cache


def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    
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
    
    # 根路由
    @app.route('/')
    def index():
        from .utils.response import success_response
        return success_response(data={
            "message": "CBG Spider API Server",
            "version": "2.0",
            "frontend": "请访问前端项目: http://localhost:8080"
        })
    
    return app 