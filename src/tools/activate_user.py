#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
激活用户工具脚本
用法：python -m src.tools.activate_user <username> [--set-premium]
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.database import db
from src.models.user import User
from src.app import create_app


def activate_user(username, set_premium=False):
    """激活用户"""
    app = create_app()
    
    with app.app_context():
        # 查找用户
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"❌ 用户不存在: {username}")
            return False
        
        # 显示用户信息
        print(f"\n找到用户:")
        print(f"  ID: {user.id}")
        print(f"  用户名: {user.username}")
        print(f"  邮箱: {user.email or '未设置'}")
        print(f"  当前状态: {'已激活' if user.is_active else '未激活'}")
        print(f"  高级用户: {'是' if user.is_premium else '否'}")
        print(f"  注册时间: {user.created_at}")
        
        # 激活用户
        if not user.is_active:
            user.is_active = True
            print(f"\n✅ 已激活用户: {username}")
        else:
            print(f"\n✓ 用户已经是激活状态")
        
        # 设置为高级用户（如果指定）
        if set_premium and not user.is_premium:
            user.is_premium = True
            print(f"✅ 已设置为高级用户（管理员）")
        elif set_premium:
            print(f"✓ 用户已经是高级用户")
        
        # 保存更改
        db.session.commit()
        
        print(f"\n更新后状态:")
        print(f"  激活状态: {'已激活' if user.is_active else '未激活'}")
        print(f"  高级用户: {'是' if user.is_premium else '否'}")
        
        return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='激活用户工具')
    parser.add_argument('username', help='用户手机号')
    parser.add_argument('--set-premium', action='store_true', help='同时设置为高级用户（管理员）')
    
    args = parser.parse_args()
    
    print(f"=== 激活用户工具 ===")
    success = activate_user(args.username, args.set_premium)
    
    if success:
        print(f"\n✅ 操作完成！")
    else:
        print(f"\n❌ 操作失败！")
        sys.exit(1)

