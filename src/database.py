#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQLAlchemy数据库初始化
"""

import os
from flask_sqlalchemy import SQLAlchemy
from src.database_config import db_config
from src.models.base import Base
from src.utils.redis_cache import get_redis_cache

# 创建SQLAlchemy实例
db = SQLAlchemy(model_class=Base)

def init_database(app):
    """初始化数据库"""
    # 配置数据库连接

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

    # 其他配置
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False  # 设置为True可以看到SQL语句
    
    # Redis缓存配置
    app.config['REDIS_HOST'] = os.getenv('REDIS_HOST', 'localhost')
    app.config['REDIS_PORT'] = int(os.getenv('REDIS_PORT', 6379))
    app.config['REDIS_DB'] = int(os.getenv('REDIS_DB', 0))
    app.config['REDIS_PASSWORD'] = os.getenv('REDIS_PASSWORD', None)
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化Redis缓存（可选）
    try:
        redis_cache = get_redis_cache()
        if redis_cache and redis_cache.is_available():
            app.config['REDIS_AVAILABLE'] = True
            print("Redis缓存初始化成功")
        else:
            app.config['REDIS_AVAILABLE'] = False
            print("Redis缓存不可用，将使用内存缓存")
    except Exception as e:
        app.config['REDIS_AVAILABLE'] = False
        print(f"Redis缓存初始化失败: {e}")
    
    return db

def get_database_url(db_name: str = 'roles') -> str:
    """获取指定数据库的连接URL"""
    return db_config.get_database_url(db_name)
