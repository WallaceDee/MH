#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库配置管理
支持SQLite和MySQL数据库配置
"""

import os
from enum import Enum
from typing import Dict, Any

class DatabaseType(Enum):
    """数据库类型枚举"""
    SQLITE = "sqlite"
    MYSQL = "mysql"

class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        self.db_type = self._get_database_type()
        self.config = self._load_config()
    
    def _get_database_type(self) -> DatabaseType:
        """获取数据库类型，优先从环境变量读取，默认为MySQL"""
        db_type = os.getenv('DATABASE_TYPE', 'mysql').lower()
        if db_type == 'mysql':
            return DatabaseType.MYSQL
        else:
            return DatabaseType.SQLITE
    
    def _load_config(self) -> Dict[str, Any]:
        """加载数据库配置"""
        if self.db_type == DatabaseType.MYSQL:
            return self._load_mysql_config()
        else:
            return self._load_sqlite_config()
    
    def _load_mysql_config(self) -> Dict[str, Any]:
        """加载MySQL配置"""
        return {
            'host': os.getenv('MYSQL_HOST', '47.86.33.98'),
            'port': int(os.getenv('MYSQL_PORT', '3306')),
            'user': os.getenv('MYSQL_USER', 'lingtong'),
            'password': os.getenv('MYSQL_PASSWORD', '447363121'),
            'database': os.getenv('MYSQL_DATABASE', 'cbg_spider'),
            'charset': os.getenv('MYSQL_CHARSET', 'utf8mb4'),
        }
    
    def _load_sqlite_config(self) -> Dict[str, Any]:
        """加载SQLite配置"""
        from src.utils.project_path import get_project_root
        data_dir = os.path.join(get_project_root(), 'data')
        return {
            'data_dir': data_dir,
            'roles_db': os.path.join(data_dir, 'cbg_roles.db'),
            'equipments_db': os.path.join(data_dir, 'cbg_equip.db'),
            'pets_db': os.path.join(data_dir, 'cbg_pets.db'),
            'abnormal_equipment_db': os.path.join(data_dir, 'abnormal_equipment.db'),
        }
    
    def get_database_url(self, db_name: str = 'roles') -> str:
        """获取数据库连接URL"""
        if self.db_type == DatabaseType.MYSQL:
            config = self.config
            # MySQL使用单一数据库，不区分表名
            return f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?charset={config['charset']}"
        else:
            # SQLite连接URL
            if db_name == 'roles':
                return f"sqlite:///{self.config['roles_db']}"
            elif db_name == 'equipments':
                return f"sqlite:///{self.config['equipments_db']}"
            elif db_name == 'pets':
                return f"sqlite:///{self.config['pets_db']}"
            elif db_name == 'abnormal_equipment':
                return f"sqlite:///{self.config['abnormal_equipment_db']}"
            else:
                return f"sqlite:///{self.config['roles_db']}"
    
    def is_mysql(self) -> bool:
        """判断是否为MySQL数据库"""
        return self.db_type == DatabaseType.MYSQL
    
    def is_sqlite(self) -> bool:
        """判断是否为SQLite数据库"""
        return self.db_type == DatabaseType.SQLITE

# 全局配置实例
db_config = DatabaseConfig()

# 导出常用配置
DATABASE_TYPE = db_config.db_type
IS_MYSQL = db_config.is_mysql()
IS_SQLITE = db_config.is_sqlite()
