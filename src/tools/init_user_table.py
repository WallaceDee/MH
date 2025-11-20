#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
初始化用户表
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from flask import Flask
from src.database import db, init_database
from src.models.user import User


def init_user_table():
    """初始化用户表"""
    # 创建Flask应用
    app = Flask(__name__)
    
    # 初始化数据库
    init_database(app)
    
    with app.app_context():
        # 创建所有表
        print("正在创建数据库表...")
        db.create_all()
        print("✅ 数据库表创建成功！")
        
        # 检查users表是否存在
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'users' in tables:
            print("✅ users表已存在")
            
            # 检查是否有用户
            user_count = User.query.count()
            print(f"当前用户数量: {user_count}")
            
            # 设置默认管理员：13202627449
            default_admin_username = '13202627449'
            default_admin = User.query.filter_by(username=default_admin_username).first()
            
            if default_admin:
                # 如果用户已存在，确保设置为管理员
                if not default_admin.is_admin:
                    default_admin.is_admin = True
                    default_admin.is_active = True
                    db.session.commit()
                    print(f"✅ 用户 {default_admin_username} 已设置为管理员")
                else:
                    print(f"✅ 用户 {default_admin_username} 已经是管理员")
            else:
                # 如果用户不存在，创建默认管理员
                print(f"正在创建默认管理员账户: {default_admin_username}")
                default_admin = User(
                    username=default_admin_username,
                    email=f'{default_admin_username}@example.com',
                    is_active=True,
                    is_premium=True,
                    is_admin=True
                )
                # 设置默认密码（建议首次登录后修改）
                default_admin.set_password('admin123456')
                db.session.add(default_admin)
                db.session.commit()
                print(f"✅ 默认管理员账户创建成功: {default_admin_username}")
                print(f"⚠️  默认密码: admin123456 (请尽快修改)")
            
            # 如果没有用户，可以通过命令行参数创建默认管理员
            if user_count == 0 and len(sys.argv) > 1:
                if sys.argv[1] == '--create-admin':
                    username = sys.argv[2] if len(sys.argv) > 2 else 'admin'
                    password = sys.argv[3] if len(sys.argv) > 3 else None
                    email = sys.argv[4] if len(sys.argv) > 4 else None
                    
                    if password:
                        admin = User(
                            username=username,
                            email=email,
                            is_active=True,
                            is_premium=True,
                            is_admin=True
                        )
                        admin.set_password(password)
                        db.session.add(admin)
                        db.session.commit()
                        print(f"✅ 管理员账户创建成功: {username}")
                    else:
                        print("❌ 请提供密码: python3 init_user_table.py --create-admin <username> <password> [email]")
                else:
                    print(f"✅ 表已创建，当前用户数量: {user_count}")
                    print("💡 创建管理员账户: python3 init_user_table.py --create-admin <username> <password> [email]")
            elif user_count == 0:
                print(f"✅ 表已创建，当前用户数量: {user_count}")
                print("💡 创建管理员账户: python3 init_user_table.py --create-admin <username> <password> [email]")
        else:
            print("❌ users表创建失败")


if __name__ == "__main__":
    try:
        init_user_table()
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

