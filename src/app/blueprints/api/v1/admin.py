#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
管理员API
"""

from flask import Blueprint, request
from src.models.user import User
from src.database import db
from src.app.utils.response import success_response, error_response
from src.app.utils.auth import require_auth, get_current_user

admin_bp = Blueprint('admin', __name__)


def require_admin(f):
    """需要管理员权限的装饰器
    
    验证流程：
    1. @require_auth 先验证token，验证通过后设置 request.current_user
    2. 检查 request.current_user.is_admin，如果不是管理员则返回403
    3. 只有管理员才能继续执行被装饰的函数
    
    安全说明：
    - 普通用户即使有有效的token，也会在is_admin检查时被拒绝
    - 无法绕过此验证，因为所有检查都在后端进行
    """
    from functools import wraps
    
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        # require_auth装饰器已经验证了token并设置了request.current_user
        user = getattr(request, 'current_user', None)
        
        # 双重检查：确保用户存在且是管理员
        if not user:
            return error_response("用户未认证", code=401)
        
        if not user.is_admin:
            return error_response("需要管理员权限", code=403)
        
        return f(*args, **kwargs)
    
    return decorated_function


@admin_bp.route('/users', methods=['GET'])
@require_admin
def get_users():
    """获取用户列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        is_active = request.args.get('is_active')
        
        query = User.query
        
        # 过滤激活状态
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            query = query.filter_by(is_active=is_active_bool)
        
        # 分页
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page,
            per_page=page_size,
            error_out=False
        )
        
        users = [user.to_dict() for user in pagination.items]
        
        return success_response(
            data={
                'users': users,
                'total': pagination.total,
                'page': page,
                'page_size': page_size,
                'pages': pagination.pages
            },
            message="获取用户列表成功"
        )
    except Exception as e:
        return error_response(f"获取用户列表失败: {str(e)}")


@admin_bp.route('/users/<int:user_id>/activate', methods=['POST'])
@require_admin
def activate_user(user_id):
    """激活用户"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response("用户不存在", code=404)
        
        user.is_active = True
        db.session.commit()
        
        return success_response(
            data={'user': user.to_dict()},
            message="用户激活成功"
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"激活用户失败: {str(e)}")


@admin_bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
@require_admin
def deactivate_user(user_id):
    """禁用用户"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response("用户不存在", code=404)
        
        user.is_active = False
        # 禁用用户时，清除token
        user.api_token = None
        user.token_expires_at = None
        db.session.commit()
        
        return success_response(
            data={'user': user.to_dict()},
            message="用户已禁用"
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"禁用用户失败: {str(e)}")


@admin_bp.route('/users/<int:user_id>/set-premium', methods=['POST'])
@require_admin
def set_premium(user_id):
    """设置用户为高级用户"""
    try:
        data = request.get_json() or {}
        is_premium = data.get('is_premium', True)
        
        user = User.query.get(user_id)
        if not user:
            return error_response("用户不存在", code=404)
        
        user.is_premium = bool(is_premium)
        db.session.commit()
        
        return success_response(
            data={'user': user.to_dict()},
            message=f"用户已{'设置为' if is_premium else '取消'}高级用户"
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"设置失败: {str(e)}")


@admin_bp.route('/users/<int:user_id>/set-admin', methods=['POST'])
@require_admin
def set_admin(user_id):
    """设置用户为管理员"""
    try:
        data = request.get_json() or {}
        is_admin = data.get('is_admin', True)
        
        user = User.query.get(user_id)
        if not user:
            return error_response("用户不存在", code=404)
        
        # 不能取消自己的管理员权限
        current_user = get_current_user()
        if current_user and current_user.id == user_id and not is_admin:
            return error_response("不能取消自己的管理员权限", code=400)
        
        user.is_admin = bool(is_admin)
        # 设置为管理员时，自动激活并设置为高级用户
        if is_admin:
            user.is_active = True
            user.is_premium = True
        
        db.session.commit()
        
        return success_response(
            data={'user': user.to_dict()},
            message=f"用户已{'设置为' if is_admin else '取消'}管理员"
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"设置失败: {str(e)}")


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@require_admin
def get_user(user_id):
    """获取用户详情"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response("用户不存在", code=404)
        
        return success_response(
            data={'user': user.to_dict()},
            message="获取用户信息成功"
        )
    except Exception as e:
        return error_response(f"获取用户信息失败: {str(e)}")

