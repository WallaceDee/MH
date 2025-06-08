"""
CBG爬虫项目 - 源代码包
包含所有核心功能模块
"""

__version__ = "2.0.0"
__author__ = "CBG Spider Team"
__description__ = "梦幻西游藏宝阁智能爬虫系统"

# 导出主要类
from .cbg_spider import CBGSpider
from .utils.smart_db_helper import CBGSmartDB, SmartDBHelper
from .proxy_rotation_system import ProxyRotationManager
from .proxy_source_manager import ProxySourceManager

__all__ = [
    'CBGSpider',
    'CBGSmartDB', 
    'SmartDBHelper',
    'ProxyRotationManager',
    'ProxySourceManager'
] 