import json
import logging
from typing import Optional, Dict, Any


def log_api_request(url: str, params: Optional[Dict[str, Any]], status_code: int, 
                   response_preview: str, logger: logging.Logger, smart_db):
    """
    记录API请求信息
    
    Args:
        url: 请求的URL
        params: 请求参数
        status_code: HTTP状态码
        response_preview: 响应内容预览
        logger: 日志记录器
        smart_db: 数据库助手实例
    """
    try:
        # 记录到日志文件
        logger.debug(f"API请求记录:")
        logger.debug(f"  URL: {url}")
        logger.debug(f"  参数: {params}")
        logger.debug(f"  状态码: {status_code}")
        logger.debug(f"  响应预览: {response_preview}")
        
        # 保存到数据库
        log_data = {
            'url': url,
            'params': json.dumps(params, ensure_ascii=False) if params else '',
            'status_code': status_code,
            'response_preview': response_preview[:500] if response_preview else ''  # 限制长度
        }
        smart_db.save_api_log(log_data)
        
    except Exception as e:
        logger.warning(f"记录API请求信息失败: {e}")


class APILogger:
    """API日志记录器类，封装了日志记录功能"""
    
    def __init__(self, logger: logging.Logger, smart_db):
        """
        初始化API日志记录器
        
        Args:
            logger: 日志记录器
            smart_db: 数据库助手实例
        """
        self.logger = logger
        self.smart_db = smart_db
    
    def log_request(self, url: str, params: Optional[Dict[str, Any]], 
                   status_code: int, response_preview: str):
        """
        记录API请求信息
        
        Args:
            url: 请求的URL
            params: 请求参数
            status_code: HTTP状态码
            response_preview: 响应内容预览
        """
        log_api_request(url, params, status_code, response_preview, 
                       self.logger, self.smart_db) 