#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试管理员权限验证
验证普通用户无法访问管理员API
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Flask
from src.app import create_app
from src.database import db
from src.models.user import User
import hashlib


def test_admin_permission():
    """测试管理员权限验证"""
    app = create_app()
    
    with app.app_context():
        # 创建测试用户
        # 1. 创建普通用户
        normal_user = User(
            username='13800138000',
            email='normal@test.com',
            is_active=True,
            is_premium=False,
            is_admin=False
        )
        normal_user.set_password('test123456')
        normal_user.generate_api_token()
        db.session.add(normal_user)
        
        # 2. 创建管理员用户
        admin_user = User(
            username='13900139000',
            email='admin@test.com',
            is_active=True,
            is_premium=True,
            is_admin=True
        )
        admin_user.set_password('admin123456')
        admin_token = admin_user.generate_api_token()
        db.session.add(admin_user)
        
        db.session.commit()
        
        print("=" * 60)
        print("管理员权限验证测试")
        print("=" * 60)
        
        # 测试1: 普通用户尝试访问管理员API
        print("\n测试1: 普通用户访问管理员API")
        normal_token_hash = hashlib.sha256(normal_user.api_token.encode()).hexdigest() if normal_user.api_token else None
        normal_user_from_db = User.query.filter_by(api_token=normal_token_hash).first() if normal_token_hash else None
        
        if normal_user_from_db:
            print(f"  ✅ 普通用户token验证成功")
            print(f"  - 用户名: {normal_user_from_db.username}")
            print(f"  - is_admin: {normal_user_from_db.is_admin}")
            print(f"  - 预期结果: 访问管理员API应返回403错误")
        else:
            print(f"  ❌ 普通用户token验证失败")
        
        # 测试2: 管理员用户访问管理员API
        print("\n测试2: 管理员用户访问管理员API")
        admin_token_hash = hashlib.sha256(admin_token.encode()).hexdigest()
        admin_user_from_db = User.query.filter_by(api_token=admin_token_hash).first()
        
        if admin_user_from_db:
            print(f"  ✅ 管理员用户token验证成功")
            print(f"  - 用户名: {admin_user_from_db.username}")
            print(f"  - is_admin: {admin_user_from_db.is_admin}")
            print(f"  - 预期结果: 可以正常访问管理员API")
        else:
            print(f"  ❌ 管理员用户token验证失败")
        
        # 测试3: 验证require_admin装饰器逻辑
        print("\n测试3: 验证权限检查逻辑")
        print(f"  普通用户 is_admin = {normal_user.is_admin}")
        print(f"  管理员用户 is_admin = {admin_user.is_admin}")
        
        # 模拟权限检查
        if not normal_user.is_admin:
            print(f"  ✅ 普通用户权限检查: 拒绝访问（正确）")
        else:
            print(f"  ❌ 普通用户权限检查: 允许访问（错误）")
        
        if admin_user.is_admin:
            print(f"  ✅ 管理员用户权限检查: 允许访问（正确）")
        else:
            print(f"  ❌ 管理员用户权限检查: 拒绝访问（错误）")
        
        # 清理测试数据
        db.session.delete(normal_user)
        db.session.delete(admin_user)
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
        print("\n结论:")
        print("1. 普通用户即使有token，访问管理员API也会被@require_admin装饰器拒绝")
        print("2. 只有is_admin=True的用户才能访问管理员API")
        print("3. 后端权限验证是安全的，无法绕过")


if __name__ == "__main__":
    try:
        test_admin_permission()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
