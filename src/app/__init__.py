#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask应用工厂
"""

from flask import Flask
from flask_cors import CORS
from .blueprints.api.v1 import api_v1_bp
from .blueprints.config_bp import config_bp
from .utils.response import register_error_handlers
from .utils.logger import setup_logging


def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 配置CORS
    CORS(app)
    
    # 设置日志
    setup_logging(app)
    
    # 注册蓝图
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    app.register_blueprint(config_bp)
    
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