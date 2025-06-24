#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
爬虫控制器
"""

import threading
import logging
from app.services.spider_service import SpiderService

logger = logging.getLogger(__name__)


class SpiderController:
    """爬虫控制器"""
    
    def __init__(self):
        self.service = SpiderService()
        self.current_task = None
    
    def get_task_status(self):
        """获取任务状态"""
        return self.service.get_task_status()
    
    def start_basic_spider(self, max_pages=5, export_excel=True, export_json=True):
        """启动基础爬虫"""
        if self.service.is_task_running():
            raise Exception("已有任务在运行中")
        
        def run_spider():
            try:
                self.service.run_basic_spider(max_pages, export_excel, export_json)
            except Exception as e:
                logger.error(f"基础爬虫执行失败: {e}")
        
        thread = threading.Thread(target=run_spider)
        thread.start()
        self.current_task = thread
        
        return {"task_id": id(thread)}
    
    def start_proxy_spider(self, max_pages=5):
        """启动代理爬虫"""
        if self.service.is_task_running():
            raise Exception("已有任务在运行中")
        
        def run_proxy_spider():
            try:
                self.service.run_proxy_spider(max_pages)
            except Exception as e:
                logger.error(f"代理爬虫执行失败: {e}")
        
        thread = threading.Thread(target=run_proxy_spider)
        thread.start()
        self.current_task = thread
        
        return {"task_id": id(thread)}
    
    def manage_proxies(self):
        """管理代理IP"""
        if self.service.is_task_running():
            raise Exception("已有任务在运行中")
        
        def get_proxies():
            try:
                self.service.manage_proxies()
            except Exception as e:
                logger.error(f"代理管理失败: {e}")
        
        thread = threading.Thread(target=get_proxies)
        thread.start()
        
        return {"task_id": id(thread)} 