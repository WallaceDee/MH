#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
整合代理IP轮换的完整CBG爬虫示例
演示如何在实际爬虫中使用代理IP轮换系统
"""

import sys
import os
import time
import json
import sqlite3
from datetime import datetime
import pandas as pd

# 导入我们的代理系统
from proxy_rotation_system import ProxyRotationManager, CBGProxyCrawler
from proxy_source_manager import ProxySourceManager

class EnhancedCBGCrawler:
    """增强版CBG爬虫，集成代理IP轮换"""
    
    def __init__(self, use_proxy=True, auto_fetch_proxies=False):
        """
        初始化增强版CBG爬虫
        
        Args:
            use_proxy: 是否使用代理IP
            auto_fetch_proxies: 是否自动获取免费代理IP
        """
        self.use_proxy = use_proxy
        self.proxy_manager = None
        self.crawler = None
        
        # 设置输出目录
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.output_dir = f"output/{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化代理系统
        if use_proxy:
            self._setup_proxy_system(auto_fetch_proxies)
        
        print(f"🚀 CBG爬虫初始化完成")
        print(f"📁 输出目录: {self.output_dir}")
        if use_proxy:
            print(f"🌐 代理模式: {'已启用' if self.proxy_manager else '启用失败'}")
        else:
            print("🔗 直连模式: 已启用")
    
    def _setup_proxy_system(self, auto_fetch=False):
        """设置代理系统"""
        try:
            # 如果需要自动获取代理
            if auto_fetch:
                print("🔄 自动获取免费代理IP...")
                source_manager = ProxySourceManager()
                proxies = source_manager.get_proxies_from_all_sources()
                
                if proxies:
                    source_manager.save_proxies_to_file(proxies)
                    print(f"✅ 获取到 {len(proxies)} 个代理IP")
                else:
                    print("❌ 未能获取到免费代理IP，将尝试使用本地代理文件")
            
            # 初始化代理管理器
            self.proxy_manager = ProxyRotationManager()
            
            if not self.proxy_manager.proxy_pool:
                print("❌ 没有可用的代理IP，切换到直连模式")
                self.use_proxy = False
                return
            
            # 测试代理可用性
            print("🔍 测试代理IP可用性...")
            working_proxies, failed_proxies = self.proxy_manager.test_all_proxies()
            
            if not working_proxies:
                print("❌ 所有代理IP都不可用，切换到直连模式")
                self.use_proxy = False
                return
            
            print(f"✅ 发现 {len(working_proxies)} 个可用代理")
            
            # 创建代理爬虫
            self.crawler = CBGProxyCrawler(self.proxy_manager)
            
        except Exception as e:
            print(f"❌ 设置代理系统失败: {e}")
            self.use_proxy = False
    
    def create_database(self):
        """创建数据库和表结构"""
        db_path = os.path.join(self.output_dir, "cbg_data.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建角色表（简化版，包含主要字段）
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equip_id TEXT UNIQUE,
            character_name TEXT,
            price REAL,
            server_name TEXT,
            level INTEGER,
            profession TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            proxy_used TEXT,
            response_time REAL
        )
        """)
        
        conn.commit()
        conn.close()
        
        return db_path
    
    def fetch_page_data(self, page):
        """获取单页数据"""
        if self.use_proxy and self.crawler:
            # 使用代理爬取
            result = self.crawler.fetch_page_with_proxy_retry(page)
            return result
        else:
            # 直连爬取（这里可以集成你原有的爬虫逻辑）
            print(f"⚡ 直连模式获取第{page}页数据")
            time.sleep(2)  # 模拟请求延时
            return None  # 这里应该返回实际的数据
    
    def parse_character_data(self, raw_data, proxy_info=None):
        """解析角色数据"""
        characters = []
        
        try:
            if not raw_data or 'result' not in raw_data:
                return characters
            
            for item in raw_data['result']:
                character = {
                    'equip_id': item.get('equip_id'),
                    'character_name': item.get('equip_name'),
                    'price': float(item.get('price', 0)) / 100,  # 分转元
                    'server_name': item.get('server_name'),
                    'level': int(item.get('level', 0)),
                    'profession': item.get('school_name'),
                    'proxy_used': f"{proxy_info['ip']}:{proxy_info['port']}" if proxy_info else 'direct',
                    'response_time': proxy_info.get('response_time', 0) if proxy_info else 0
                }
                characters.append(character)
        
        except Exception as e:
            print(f"❌ 解析角色数据失败: {e}")
        
        return characters
    
    def save_to_database(self, characters, db_path):
        """保存数据到数据库"""
        if not characters:
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            for char in characters:
                cursor.execute("""
                INSERT OR REPLACE INTO characters 
                (equip_id, character_name, price, server_name, level, profession, proxy_used, response_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    char['equip_id'], char['character_name'], char['price'],
                    char['server_name'], char['level'], char['profession'],
                    char['proxy_used'], char['response_time']
                ))
            
            conn.commit()
            conn.close()
            
            print(f"💾 已保存 {len(characters)} 条角色数据")
            
        except Exception as e:
            print(f"❌ 保存数据失败: {e}")
    
    def crawl_multiple_pages(self, start_page=1, end_page=10):
        """爬取多页数据"""
        print(f"🚀 开始爬取第{start_page}-{end_page}页数据")
        
        # 创建数据库
        db_path = self.create_database()
        
        total_characters = 0
        successful_pages = 0
        
        for page in range(start_page, end_page + 1):
            try:
                print(f"\n📄 正在处理第{page}页...")
                
                # 获取页面数据
                start_time = time.time()
                raw_data = self.fetch_page_data(page)
                fetch_time = time.time() - start_time
                
                if raw_data:
                    # 获取当前使用的代理信息（如果有）
                    proxy_info = None
                    if self.use_proxy and self.proxy_manager:
                        # 这里可以获取最后使用的代理信息
                        active_proxies = [p for p in self.proxy_manager.proxy_pool if p['status'] == 'active']
                        if active_proxies:
                            proxy_info = active_proxies[0]  # 简化处理
                    
                    # 解析数据
                    characters = self.parse_character_data(raw_data, proxy_info)
                    
                    # 保存到数据库
                    self.save_to_database(characters, db_path)
                    
                    total_characters += len(characters)
                    successful_pages += 1
                    
                    print(f"✅ 第{page}页完成，获取{len(characters)}条数据，耗时{fetch_time:.2f}秒")
                
                else:
                    print(f"❌ 第{page}页获取失败")
                
                # 页面间延时
                if page < end_page:
                    delay = 3 if not self.use_proxy else 1
                    print(f"⏰ 等待{delay}秒...")
                    time.sleep(delay)
                
            except Exception as e:
                print(f"❌ 第{page}页处理异常: {e}")
                continue
        
        # 显示统计信息
        self._show_crawl_summary(successful_pages, end_page - start_page + 1, total_characters, db_path)
        
        # 如果使用了代理，显示代理统计
        if self.use_proxy and self.proxy_manager:
            print("\n📊 代理使用统计:")
            self.proxy_manager.show_proxy_status()
        
        return db_path
    
    def _show_crawl_summary(self, successful_pages, total_pages, total_characters, db_path):
        """显示爬取汇总"""
        print("\n" + "="*60)
        print("🎉 爬取任务完成！")
        print(f"📊 成功页面: {successful_pages}/{total_pages}")
        print(f"👥 总角色数: {total_characters}")
        print(f"💾 数据库文件: {db_path}")
        
        if total_characters > 0:
            success_rate = (successful_pages / total_pages) * 100
            print(f"✅ 成功率: {success_rate:.1f}%")
            
            # 快速统计
            try:
                conn = sqlite3.connect(db_path)
                df = pd.read_sql_query("SELECT * FROM characters", conn)
                conn.close()
                
                if len(df) > 0:
                    print(f"💰 价格范围: {df['price'].min():.2f}元 - {df['price'].max():.2f}元")
                    print(f"📈 平均价格: {df['price'].mean():.2f}元")
                    
                    if self.use_proxy:
                        proxy_stats = df['proxy_used'].value_counts()
                        print(f"🌐 使用代理数: {len(proxy_stats)}")
            
            except Exception as e:
                print(f"❌ 统计信息生成失败: {e}")
    
    def export_to_excel(self, db_path):
        """导出Excel文件"""
        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("SELECT * FROM characters", conn)
            conn.close()
            
            if len(df) == 0:
                print("❌ 没有数据可导出")
                return
            
            # Excel文件路径
            excel_path = os.path.join(self.output_dir, "cbg_characters.xlsx")
            
            # 导出Excel
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='角色数据', index=False)
            
            print(f"📊 Excel文件已导出: {excel_path}")
            return excel_path
            
        except Exception as e:
            print(f"❌ Excel导出失败: {e}")
            return None

def demo_proxy_crawling():
    """演示代理IP轮换爬虫"""
    print("🎯 CBG代理IP轮换爬虫演示")
    print("="*60)
    
    # 选择模式
    print("\n请选择运行模式:")
    print("1. 使用现有代理文件")
    print("2. 自动获取免费代理")
    print("3. 直连模式（无代理）")
    
    try:
        choice = input("请输入选择 (1-3): ").strip()
    except KeyboardInterrupt:
        print("\n👋 用户取消操作")
        return
    
    # 初始化爬虫
    if choice == "1":
        crawler = EnhancedCBGCrawler(use_proxy=True, auto_fetch_proxies=False)
    elif choice == "2":
        crawler = EnhancedCBGCrawler(use_proxy=True, auto_fetch_proxies=True)
    else:
        crawler = EnhancedCBGCrawler(use_proxy=False)
    
    # 爬取页面数
    try:
        pages = int(input("请输入要爬取的页面数 (默认5页): ") or "5")
    except (ValueError, KeyboardInterrupt):
        pages = 5
    
    print(f"\n🚀 开始爬取{pages}页数据...")
    
    # 执行爬取
    db_path = crawler.crawl_multiple_pages(1, pages)
    
    # 导出Excel
    excel_path = crawler.export_to_excel(db_path)
    
    print("\n🎉 任务完成！")
    if excel_path:
        print(f"📊 可以查看Excel文件: {excel_path}")

if __name__ == "__main__":
    demo_proxy_crawling() 