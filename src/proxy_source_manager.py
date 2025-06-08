#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代理IP源管理器
支持从多个免费代理源获取代理IP
"""

import requests
import re
import json
import time
import random
from bs4 import BeautifulSoup
import logging
import os

class ProxySourceManager:
    """代理IP源管理器"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.session = self._create_session()
        
    def _setup_logger(self):
        """设置日志"""
        logger = logging.getLogger('ProxySource')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _create_session(self):
        """创建请求会话"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        return session
    
    def get_proxies_from_free_proxy_list(self):
        """从 free-proxy-list.net 获取代理"""
        try:
            url = "https://free-proxy-list.net/"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            proxies = []
            
            # 查找代理表格
            table = soup.find('table', {'id': 'proxylisttable'})
            if not table:
                self.logger.warning("未找到代理表格")
                return []
            
            for row in table.find('tbody').find_all('tr'):
                cols = row.find_all('td')
                if len(cols) >= 7:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    country = cols[2].text.strip()
                    anonymity = cols[4].text.strip()
                    https = cols[6].text.strip()
                    
                    # 只选择高匿名代理
                    if anonymity in ['high anonymity', 'anonymous']:
                        protocol = 'https' if https == 'yes' else 'http'
                        proxy_info = {
                            'ip': ip,
                            'port': int(port),
                            'protocol': protocol,
                            'country': country,
                            'anonymity': anonymity,
                            'source': 'free-proxy-list'
                        }
                        proxies.append(proxy_info)
            
            self.logger.info(f"从 free-proxy-list.net 获取到 {len(proxies)} 个代理")
            return proxies
            
        except Exception as e:
            self.logger.error(f"从 free-proxy-list.net 获取代理失败: {e}")
            return []
    
    def get_proxies_from_proxy_list_download(self):
        """从 proxy-list.download 获取代理"""
        try:
            urls = [
                "https://www.proxy-list.download/api/v1/get?type=http",
                "https://www.proxy-list.download/api/v1/get?type=https"
            ]
            
            proxies = []
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    
                    # 解析文本格式的代理列表
                    for line in response.text.strip().split('\n'):
                        line = line.strip()
                        if ':' in line:
                            try:
                                ip, port = line.split(':', 1)
                                proxy_info = {
                                    'ip': ip.strip(),
                                    'port': int(port.strip()),
                                    'protocol': 'https' if 'https' in url else 'http',
                                    'country': 'Unknown',
                                    'anonymity': 'unknown',
                                    'source': 'proxy-list.download'
                                }
                                proxies.append(proxy_info)
                            except ValueError:
                                continue
                    
                    time.sleep(1)  # 避免请求过快
                    
                except Exception as e:
                    self.logger.warning(f"从 {url} 获取代理失败: {e}")
                    continue
            
            self.logger.info(f"从 proxy-list.download 获取到 {len(proxies)} 个代理")
            return proxies
            
        except Exception as e:
            self.logger.error(f"从 proxy-list.download 获取代理失败: {e}")
            return []
    
    def get_proxies_from_pubproxy(self):
        """从 pubproxy.com 获取代理"""
        try:
            url = "http://pubproxy.com/api/proxy"
            params = {
                'limit': 20,
                'format': 'json',
                'type': 'http',
                'level': 'anonymous',
                'last_check': 60  # 最近60分钟内检查过的
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            proxies = []
            
            if data.get('data'):
                for item in data['data']:
                    proxy_info = {
                        'ip': item.get('ip'),
                        'port': int(item.get('port')),
                        'protocol': item.get('type', 'http'),
                        'country': item.get('country'),
                        'anonymity': item.get('level'),
                        'source': 'pubproxy'
                    }
                    proxies.append(proxy_info)
            
            self.logger.info(f"从 pubproxy.com 获取到 {len(proxies)} 个代理")
            return proxies
            
        except Exception as e:
            self.logger.error(f"从 pubproxy.com 获取代理失败: {e}")
            return []
    
    def get_proxies_from_gimmeproxy(self):
        """从 gimmeproxy.com 获取代理"""
        try:
            proxies = []
            
            # 获取多个代理
            for _ in range(10):
                try:
                    url = "https://gimmeproxy.com/api/getProxy"
                    params = {
                        'format': 'json',
                        'protocol': 'http',
                        'anonymityLevel': 1,  # anonymous
                        'get': 'true'
                    }
                    
                    response = self.session.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if data.get('ip') and data.get('port'):
                        proxy_info = {
                            'ip': data['ip'],
                            'port': int(data['port']),
                            'protocol': data.get('type', 'http'),
                            'country': data.get('country'),
                            'anonymity': 'anonymous',
                            'source': 'gimmeproxy'
                        }
                        proxies.append(proxy_info)
                    
                    time.sleep(0.5)  # API限制
                    
                except Exception as e:
                    self.logger.warning(f"从 gimmeproxy.com 获取单个代理失败: {e}")
                    continue
            
            self.logger.info(f"从 gimmeproxy.com 获取到 {len(proxies)} 个代理")
            return proxies
            
        except Exception as e:
            self.logger.error(f"从 gimmeproxy.com 获取代理失败: {e}")
            return []
    
    def get_proxies_from_all_sources(self):
        """从所有源获取代理IP"""
        self.logger.info("开始从多个源获取免费代理IP...")
        
        all_proxies = []
        
        # 各个代理源获取函数
        sources = [
            self.get_proxies_from_free_proxy_list,
            self.get_proxies_from_proxy_list_download,
            self.get_proxies_from_pubproxy,
            self.get_proxies_from_gimmeproxy,
        ]
        
        for source_func in sources:
            try:
                source_proxies = source_func()
                all_proxies.extend(source_proxies)
                
                # 源之间的延时
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                self.logger.error(f"获取代理源失败: {e}")
                continue
        
        # 去重处理
        unique_proxies = []
        seen = set()
        
        for proxy in all_proxies:
            key = f"{proxy['ip']}:{proxy['port']}"
            if key not in seen:
                seen.add(key)
                unique_proxies.append(proxy)
        
        self.logger.info(f"总共获取到 {len(unique_proxies)} 个去重后的代理IP")
        return unique_proxies
    
    def save_proxies_to_file(self, proxies, filename="proxy_list.txt"):
        """保存代理IP到文件"""
        try:
            # 获取项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            proxy_file_path = os.path.join(project_root, 'config', filename)
            
            with open(proxy_file_path, 'w', encoding='utf-8') as f:
                f.write("# 从免费代理源自动获取的代理IP列表\n")
                f.write(f"# 获取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 总数量: {len(proxies)}\n")
                f.write("# 格式: protocol://ip:port\n\n")
                
                for proxy in proxies:
                    protocol = proxy.get('protocol', 'http')
                    ip = proxy['ip']
                    port = proxy['port']
                    
                    # 简化格式，只写入 protocol://ip:port
                    f.write(f"{protocol}://{ip}:{port}\n")
            
            self.logger.info(f"已保存 {len(proxies)} 个代理IP到文件: {proxy_file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存代理IP文件失败: {e}")
            return False

def auto_fetch_and_save_proxies():
    """自动获取并保存免费代理IP"""
    print("🌐 自动获取免费代理IP")
    print("=" * 50)
    
    source_manager = ProxySourceManager()
    
    # 获取所有代理
    proxies = source_manager.get_proxies_from_all_sources()
    
    if not proxies:
        print("❌ 未能获取到任何代理IP")
        return
    
    # 保存到文件
    success = source_manager.save_proxies_to_file(proxies)
    
    if success:
        print(f"✅ 成功获取并保存了 {len(proxies)} 个代理IP到 proxy_list.txt")
        
        # 按来源统计
        source_stats = {}
        for proxy in proxies:
            source = proxy.get('source', 'unknown')
            source_stats[source] = source_stats.get(source, 0) + 1
        
        print("\n📊 代理来源统计:")
        for source, count in source_stats.items():
            print(f"  {source}: {count} 个")
        
        print("\n💡 使用建议:")
        print("1. 这些是免费代理，稳定性可能不如付费代理")
        print("2. 建议定期更新代理列表")
        print("3. 使用前请先测试代理可用性")
        print("4. 可以运行 'python proxy_rotation_system.py' 来测试代理")
        
    else:
        print("❌ 保存代理IP文件失败")

if __name__ == "__main__":
    auto_fetch_and_save_proxies() 