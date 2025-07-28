"""
CBG爬虫项目 - 源代码包
包含所有核心功能模块
"""

__version__ = "2.0.0"
__author__ = "CBG Spider Team"
__description__ = "梦幻西游藏宝阁智能爬虫系统"

# 导出主要类 - 延迟导入，避免在模块加载时自动创建数据库
# from .cbg_spider import CBGSpider
# from .spider.equip import CBGEquipSpider
from .utils.smart_db_helper import CBGSmartDB, SmartDBHelper
from .proxy_rotation_system import ProxyRotationManager
from .proxy_source_manager import ProxySourceManager

__all__ = [
    # 'CBGEquipSpider',  # 延迟导入
    # 'CBGSpider',       # 延迟导入
    'CBGSmartDB', 
    'SmartDBHelper',
    'ProxyRotationManager',
    'ProxySourceManager'
]

"""
梦幻西游角色评估系统
""" 