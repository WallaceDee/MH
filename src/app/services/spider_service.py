#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
爬虫服务层
"""

import logging

logger = logging.getLogger(__name__)

# 全局任务状态
task_status = {"status": "idle", "message": "", "progress": 0}


class SpiderService:
    """爬虫服务"""
    
    def __init__(self):
        pass
    
    def get_task_status(self):
        """获取任务状态"""
        return task_status
    
    def is_task_running(self):
        """检查是否有任务在运行"""
        return task_status["status"] == "running"
    
    def run_basic_spider(self, max_pages, export_excel, export_json):
        """运行基础爬虫"""
        global task_status
        try:
            task_status = {"status": "running", "message": "初始化爬虫...", "progress": 10}
            logger.info(f"启动基础爬虫，最大页数: {max_pages}")
            
            from cbg_spider import CBGSpider
            spider = CBGSpider()
            
            task_status["message"] = "开始爬取数据..."
            task_status["progress"] = 30
            
            spider.crawl_all_pages(max_pages=max_pages)
            
            task_status["message"] = "爬取完成，正在导出..."
            task_status["progress"] = 70
            
            results = {"files": []}
            
            if export_excel:
                excel_file = spider.export_to_excel()
                if excel_file:
                    results["files"].append({"type": "excel", "path": excel_file})
            
            if export_json:
                json_file = spider.export_to_json()
                if json_file:
                    results["files"].append({"type": "json", "path": json_file})
            
            task_status = {
                "status": "completed", 
                "message": f"完成！生成了 {len(results['files'])} 个文件", 
                "progress": 100,
                "results": results
            }
            
            logger.info("基础爬虫完成")
            
        except Exception as e:
            task_status = {"status": "error", "message": f"执行出错: {str(e)}", "progress": 0}
            logger.error(f"基础爬虫出错: {e}")
            raise
    
    def run_proxy_spider(self, max_pages):
        """运行代理爬虫"""
        global task_status
        try:
            task_status = {"status": "running", "message": "初始化代理爬虫...", "progress": 10}
            logger.info(f"启动代理爬虫，最大页数: {max_pages}")
            
            from cbg_crawler_with_proxy import EnhancedCBGCrawler
            
            task_status["message"] = "开始爬取数据..."
            task_status["progress"] = 30
            
            crawler = EnhancedCBGCrawler()
            crawler.start_crawling(max_pages=max_pages)
            
            task_status = {
                "status": "completed", 
                "message": "代理爬虫完成！", 
                "progress": 100
            }
            
            logger.info("代理爬虫完成")
            
        except Exception as e:
            task_status = {"status": "error", "message": f"执行出错: {str(e)}", "progress": 0}
            logger.error(f"代理爬虫出错: {e}")
            raise
    
    def manage_proxies(self):
        """管理代理IP"""
        global task_status
        try:
            task_status = {"status": "running", "message": "获取代理IP...", "progress": 50}
            logger.info("开始管理代理IP")
            
            from proxy_source_manager import ProxySourceManager
            manager = ProxySourceManager()
            proxies = manager.get_all_proxies()
            manager.save_proxies_to_file(proxies)
            
            task_status = {
                "status": "completed", 
                "message": f"获取到 {len(proxies)} 个代理IP", 
                "progress": 100,
                "results": {"proxy_count": len(proxies)}
            }
            
            logger.info(f"代理管理完成，获取到 {len(proxies)} 个代理")
            
        except Exception as e:
            task_status = {"status": "error", "message": f"执行出错: {str(e)}", "progress": 0}
            logger.error(f"代理管理出错: {e}")
            raise 