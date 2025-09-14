#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQLAlchemy数据库初始化
"""

from flask_sqlalchemy import SQLAlchemy
from src.database_config import db_config
from src.models.base import Base

# 创建SQLAlchemy实例
db = SQLAlchemy(model_class=Base)

def init_database(app):
    """初始化数据库"""
    # 配置数据库连接
    if db_config.is_mysql():
        # MySQL配置
        config = db_config.config
        app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?charset={config['charset']}"
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 10,
            'pool_recycle': 3600,
            'pool_pre_ping': True,
            'connect_args': {
                'charset': 'utf8mb4',
                'use_unicode': True
            }
        }
    else:
        # SQLite配置
        app.config['SQLALCHEMY_DATABASE_URI'] = db_config.get_database_url('roles')
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
        }
    
    # 其他配置
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False  # 设置为True可以看到SQL语句
    
    # 初始化数据库
    db.init_app(app)
    
    return db

def get_database_url(db_name: str = 'roles') -> str:
    """获取指定数据库的连接URL"""
    return db_config.get_database_url(db_name)
