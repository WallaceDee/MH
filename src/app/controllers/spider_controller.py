#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
爬虫控制器
基于run.py的功能提供完整的爬虫控制
"""

import threading
import logging
from typing import Dict, Any, Optional
from ..services.spider_service import SpiderService

logger = logging.getLogger(__name__)


class SpiderController:
    """爬虫控制器"""
    
    def __init__(self):
        self.service = SpiderService()
        self.current_task = None
    
    def get_task_status(self):
        """获取任务状态"""
        return self.service.get_task_status()
    
    def get_spider_config(self):
        """获取爬虫配置信息"""
        return self.service.get_spider_config()
    
    def start_basic_spider(self,
                          spider_type: str = 'role',
                          equip_type: str = 'normal',
                          max_pages: int = 5,
                          delay_min: float = 5.0,
                          delay_max: float = 8.0,
                          cached_params: dict = None,
                          target_server_list: list = None,
                          multi: bool = False):
        """
        启动基础爬虫
        
        Args:
            spider_type: 爬虫类型 (role, equip, pet)
            equip_type: 装备类型 (normal, lingshi, pet) - 仅当spider_type='equip'时有效
            max_pages: 爬取页数
            delay_min: 最小延迟
            delay_max: 最大延迟
            cached_params: 缓存的搜索参数
            target_server_list: 目标服务器列表
            multi: 是否多服务器模式
        """
        if self.service.is_task_running():
            raise Exception("已有任务在运行中")
        
        def run_spider():
            try:
                self.service.run_basic_spider(
                    spider_type=spider_type,
                    equip_type=equip_type,
                    max_pages=max_pages,
                    delay_min=delay_min,
                    delay_max=delay_max,
                    cached_params=cached_params,
                    target_server_list=target_server_list,
                    multi=multi
                )
            except Exception as e:
                logger.error(f"基础爬虫执行失败: {e}")
        
        thread = threading.Thread(target=run_spider)
        thread.start()
        self.current_task = thread
        
        return {
            "task_id": id(thread),
            "config": {
                "spider_type": spider_type,
                "equip_type": equip_type if spider_type == 'equip' else None,
                "max_pages": max_pages,
                "delay_range": [delay_min, delay_max]
            }
        }
    
    def start_role_spider(self, max_pages: int = 5, 
                         delay_min: float = 5.0, delay_max: float = 8.0, 
                         cached_params: dict = None):
        """启动角色爬虫"""
        return self.start_basic_spider(
            spider_type='role',
            max_pages=max_pages,
            delay_min=delay_min,
            delay_max=delay_max,
            cached_params=cached_params
        )
    
    def start_equip_spider(self, equip_type: str = 'normal', max_pages: int = 5, delay_min: float = 5.0, 
                          delay_max: float = 8.0, cached_params: dict = None,
                          target_server_list: list = None, multi: bool = False):
        """启动装备爬虫"""
        return self.start_basic_spider(
            spider_type='equip',
            equip_type=equip_type,
            max_pages=max_pages,
            delay_min=delay_min,
            delay_max=delay_max,
            cached_params=cached_params,
            target_server_list=target_server_list,
            multi=multi
        )
    
    def start_pet_spider(self, max_pages: int = 5,
                        delay_min: float = 5.0, delay_max: float = 8.0,
                        cached_params: dict = None,
                        target_server_list: list = None,
                        multi: bool = False):
        """启动召唤兽爬虫"""
        return self.start_basic_spider(
            spider_type='pet',
            max_pages=max_pages,
            delay_min=delay_min,
            delay_max=delay_max,
            cached_params=cached_params,
            target_server_list=target_server_list,
            multi=multi
        )
    
    def start_proxy_spider(self, max_pages: int = 5):
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
        
        return {
            "task_id": id(thread),
            "config": {
                "max_pages": max_pages,
                "use_proxy": True
            }
        }
    
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
    
    def stop_current_task(self):
        """停止当前任务"""
        try:
            # 调用服务层的停止方法
            result = self.service.stop_current_task()
            
            # 同时清理控制器层的线程引用
            if self.current_task and self.current_task.is_alive():
                logger.info("清理Python线程引用")
                self.current_task = None
            
            return result
        except Exception as e:
            logger.error(f"停止任务失败: {e}")
            return {"message": f"停止任务失败: {str(e)}"}
    
    def get_task_logs(self, lines: int = 100, log_type: str = 'current', spider_type: str = None, filename: str = None):
        """获取任务日志"""
        return self.service.get_task_logs(lines=lines, log_type=log_type, spider_type=spider_type, filename=filename)
    
    def start_playwright_collector(self, headless: bool = False, target_url: str = None):
        """启动Playwright收集器"""
        if self.service.is_task_running():
            raise Exception("已有任务在运行中")
        
        def run_playwright():
            try:
                self.service.run_playwright_collector(headless=headless, target_url=target_url)
            except Exception as e:
                logger.error(f"Playwright收集器执行失败: {e}")
        
        thread = threading.Thread(target=run_playwright)
        thread.start()
        self.current_task = thread
        
        return {
            "task_id": id(thread),
            "config": {
                "collector_type": "playwright",
                "headless": headless,
                "target_url": target_url
            }
        }
    
    def check_cookie_status(self):
        """检查Cookie状态"""
        return self.service.check_cookie_status()
    
    def update_cookies(self):
        """更新Cookie"""
        return self.service.update_cookies()
    

    
    def reset_task_status(self):
        """重置任务状态"""
        return self.service.reset_task_status()
    
    def parse_response_data(self, url: str, response_text: str):
        """解析响应数据"""
        return self.service.parse_response_data(url, response_text) 