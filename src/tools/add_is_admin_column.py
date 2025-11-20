#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
添加 is_admin 列到 users 表
数据库迁移脚本
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from flask import Flask
from src.database import db, init_database
from sqlalchemy import text, inspect


def add_is_admin_column():
    """添加 is_admin 列到 users 表"""
    # 创建Flask应用
    app = Flask(__name__)
    
    # 初始化数据库
    init_database(app)
    
    with app.app_context():
        try:
            # 检查列是否已存在
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'is_admin' in columns:
                print("✅ is_admin 列已存在，无需添加")
                return
            
            print("正在添加 is_admin 列到 users 表...")
            
            # 根据数据库类型选择不同的SQL语句
            db_url = str(db.engine.url)
            
            if 'mysql' in db_url.lower() or 'mariadb' in db_url.lower():
                # MySQL/MariaDB
                sql = text("""
                    ALTER TABLE users 
                    ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE 
                    COMMENT '是否管理员'
                """)
            elif 'sqlite' in db_url.lower():
                # SQLite
                sql = text("""
                    ALTER TABLE users 
                    ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0
                """)
            elif 'postgresql' in db_url.lower():
                # PostgreSQL
                sql = text("""
                    ALTER TABLE users 
                    ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE
                """)
            else:
                # 默认使用MySQL语法
                sql = text("""
                    ALTER TABLE users 
                    ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE
                """)
            
            # 执行SQL
            db.session.execute(sql)
            db.session.commit()
            
            print("✅ is_admin 列添加成功！")
            
            # 设置默认管理员：13202627449
            from src.models.user import User
            default_admin_username = '13202627449'
            default_admin = User.query.filter_by(username=default_admin_username).first()
            
            if default_admin:
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
                default_admin.set_password('admin123456')
                db.session.add(default_admin)
                db.session.commit()
                print(f"✅ 默认管理员账户创建成功: {default_admin_username}")
                print(f"⚠️  默认密码: admin123456 (请尽快修改)")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 添加列失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    try:
        add_is_admin_column()
        print("\n" + "=" * 60)
        print("数据库迁移完成！")
        print("=" * 60)
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
