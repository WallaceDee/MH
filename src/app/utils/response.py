#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一API响应工具
"""

from flask import jsonify
import time
import logging

logger = logging.getLogger(__name__)


def success_response(data=None, message="success", code=200):
    """成功响应"""
    return jsonify({
        "code": code,
        "data": data,
        "message": message,
        "timestamp": int(time.time())
    }), 200


def error_response(message="error", code=400, http_code=400, data=None):
    """错误响应"""
    return jsonify({
        "code": code,
        "data": data,  # 允许传入data参数
        "message": message,
        "timestamp": int(time.time())
    }), http_code


def paginated_response(data, total, page, page_size, message="success"):
    """分页响应"""
    return jsonify({
        "code": 200,
        "data": {
            "items": data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        },
        "message": message,
        "timestamp": int(time.time())
    }), 200


def register_error_handlers(app):
    """注册全局错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"Bad request: {error}")
        return error_response("请求参数错误", code=400, http_code=400)
    
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"Not found: {error}")
        return error_response("资源不存在", code=404, http_code=404)
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        return error_response("服务器内部错误", code=500, http_code=500)
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {e}")
        return error_response("系统异常", code=500, http_code=500) 