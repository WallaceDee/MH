#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户认证API
"""

from flask import Blueprint, request, jsonify
from src.models.user import User
from src.database import db
from src.app.utils.response import success_response, error_response, info_response
from datetime import datetime
import hashlib
import re

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请提供注册信息")
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if not username or not password:
            return error_response("手机号和密码不能为空")
        
        # 验证手机号格式（中国手机号：11位数字，以1开头，第二位是3-9）
        if not re.match(r'^1[3-9]\d{9}$', username):
            return error_response("请输入正确的手机号格式")
        
        # 检查用户名（手机号）是否已存在
        if User.query.filter_by(username=username).first():
            return error_response("该手机号已被注册")
        
        # 检查邮箱是否已存在
        if email and User.query.filter_by(email=email).first():
            return error_response("邮箱已被注册")
        
        # 创建新用户（默认未激活，需管理员启用）
        user = User(username=username, email=email, is_active=False)
        user.set_password(password)
        
        # 如果有fingerprint，绑定到用户（不区分大小写）
        fingerprint = request.headers.get('X-Fingerprint') or request.headers.get('x-fingerprint')
        if fingerprint:
            user.fingerprint = fingerprint
        
        db.session.add(user)
        db.session.commit()
        
        return success_response(
            data={
                'user_id': user.id,
                'username': user.username,
                'is_active': user.is_active
            },
            message="注册成功，等待管理员审核激活"
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"注册失败: {str(e)}")


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请提供登录信息")
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return error_response("用户名和密码不能为空")
        
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', username):
            return error_response("请输入正确的手机号格式")
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return error_response("手机号或密码错误")
        
        if not user.is_active:
            # 检查是否是刚注册的用户（创建时间在7天内）
            from datetime import timedelta
            days_since_created = (datetime.utcnow() - user.created_at).days if user.created_at else 999
            if days_since_created <= 7:
                return info_response("账户未激活，等待管理员审核激活")
            else:
                return error_response("账户已被禁用，请联系管理员")
        
        # 生成或刷新token
        token = user.generate_api_token(expires_days=30)
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        
        # 如果有fingerprint，绑定到用户（不区分大小写）
        fingerprint = request.headers.get('X-Fingerprint') or request.headers.get('x-fingerprint')
        if fingerprint:
            user.fingerprint = fingerprint
        
        db.session.commit()
        
        return success_response(
            data={
                'token': token,
                'user': user.to_dict(),
                'expires_in': 30 * 24 * 60 * 60  # 30天（秒）
            },
            message="登录成功"
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"登录失败: {str(e)}")


@auth_bp.route('/refresh-token', methods=['POST'])
def refresh_token():
    """刷新token"""
    try:
        # 从请求头获取token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return error_response("未提供token", code=401)
        
        # 查找用户
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        user = User.query.filter_by(api_token=token_hash).first()
        
        if not user or not user.is_token_valid():
            return error_response("Token无效或已过期", code=401)
        
        # 刷新token
        new_token = user.refresh_token(expires_days=30)
        
        return success_response(
            data={
                'token': new_token,
                'expires_in': 30 * 24 * 60 * 60
            },
            message="Token刷新成功"
        )
    except Exception as e:
        return error_response(f"刷新token失败: {str(e)}")


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """获取当前用户信息"""
    try:
        # 从请求头获取token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return error_response("未提供token", code=401)
        
        # 查找用户
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        user = User.query.filter_by(api_token=token_hash).first()
        
        if not user or not user.is_token_valid():
            return error_response("Token无效或已过期", code=401)
        
        return success_response(
            data={'user': user.to_dict()},
            message="获取用户信息成功"
        )
    except Exception as e:
        return error_response(f"获取用户信息失败: {str(e)}")


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    try:
        # 从请求头获取token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return error_response("未提供token", code=401)
        
        # 查找用户并清除token
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        user = User.query.filter_by(api_token=token_hash).first()
        
        if user:
            user.api_token = None
            user.token_expires_at = None
            db.session.commit()
        
        return success_response(message="登出成功")
    except Exception as e:
        return error_response(f"登出失败: {str(e)}")


@auth_bp.route('/update-fingerprint', methods=['POST'])
def update_fingerprint():
    """更新用户的fingerprint（需要认证）"""
    try:
        # 从请求头获取token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return error_response("未提供token", code=401)
        
        # 查找用户
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        user = User.query.filter_by(api_token=token_hash).first()
        
        if not user or not user.is_token_valid():
            return error_response("Token无效或已过期", code=401)
        
        # 获取新的fingerprint
        data = request.get_json()
        new_fingerprint = data.get('fingerprint') if data else None
        
        if not new_fingerprint:
            new_fingerprint = request.headers.get('X-Fingerprint') or request.headers.get('x-fingerprint')
        
        if not new_fingerprint:
            return error_response("请提供fingerprint")
        
        # 更新fingerprint
        user.fingerprint = new_fingerprint
        db.session.commit()
        
        return success_response(
            data={'fingerprint': user.fingerprint},
            message="Fingerprint更新成功"
        )
    except Exception as e:
        return error_response(f"更新fingerprint失败: {str(e)}")

