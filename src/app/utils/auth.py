#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
认证工具函数
"""

from functools import wraps
from flask import request, jsonify
from src.models.user import User
from src.app.utils.response import error_response
import hashlib


def require_auth(f):
    """需要认证的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return error_response("未提供认证token", code=401)
        
        # 验证token
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        user = User.query.filter_by(api_token=token_hash).first()
        
        if not user or not user.is_token_valid():
            return error_response("Token无效或已过期，请重新登录", code=401)
        
        if not user.is_active:
            return error_response("账户已被禁用", code=403)
        
        # 验证fingerprint（如果用户已绑定fingerprint，才需要验证）
        if user.fingerprint:
            fingerprint = request.headers.get('X-Fingerprint') or request.headers.get('x-fingerprint')
            if not fingerprint:
                return error_response("请求必须携带X-Fingerprint", code=400)
            if fingerprint != user.fingerprint:
                return error_response("Fingerprint不匹配，请使用正确的设备访问", code=403)
        
        # 将用户对象添加到请求上下文
        request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_premium(f):
    """需要高级用户的装饰器"""
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user') or not request.current_user.is_premium:
            return error_response("此功能需要高级账户", code=403)
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user():
    """获取当前用户（在require_auth装饰器后使用）"""
    return getattr(request, 'current_user', None)

