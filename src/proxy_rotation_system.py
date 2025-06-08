#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代理IP轮换系统实现
提供多种代理IP管理和轮换策略
"""

import requests
import random
import time
import threading
import json
import logging
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import os

class ProxyRotationManager:
    def __init__(self, proxy_sources=None, max_workers=3):
        """
        初始化代理IP轮换管理器
        
        Args:
            proxy_sources: 代理IP源配置
            max_workers: 最大并发工作者数量
        """
        self.proxy_pool = []
        self.max_workers = max_workers
        self.current_proxy_index = 0
        self.proxy_lock = threading.Lock()
        self.proxy_stats = {}
        
        # 初始化日志
        self.logger = self._setup_logger()
        
        # 加载代理IP
        if proxy_sources:
            self.load_proxies_from_sources(proxy_sources)
        else:
            self.load_proxies_from_file()
    
    def _setup_logger(self):
        """设置日志记录器"""
        logger = logging.getLogger('ProxyRotation')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def load_proxies_from_file(self, filename="proxy_list.txt"):
        """从文件加载代理列表"""
        try:
            # 获取项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            proxy_file_path = os.path.join(project_root, 'config', filename)
            
            with open(proxy_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        proxy_info = self._parse_proxy_line(line)
                        if proxy_info:
                            self.proxy_pool.append(proxy_info)
            
            self.logger.info(f"从文件加载了 {len(self.proxy_pool)} 个代理IP")
            
        except FileNotFoundError:
            self.logger.warning(f"代理IP文件 {filename} 不存在，创建示例文件...")
            self._create_sample_proxy_file(filename)
        except Exception as e:
            self.logger.error(f"加载代理IP文件失败: {e}")
    
    def _parse_proxy_line(self, line):
        """解析代理IP行"""
        try:
            # 支持多种格式
            # 格式1: ip:port
            # 格式2: protocol://ip:port
            # 格式3: protocol://username:password@ip:port
            # 格式4: ip:port:username:password
            
            if '://' in line:
                # 带协议的格式
                if '@' in line:
                    # 带认证的格式: protocol://username:password@ip:port
                    protocol = line.split('://')[0]
                    auth_and_addr = line.split('://')[1]
                    auth, addr = auth_and_addr.split('@')
                    username, password = auth.split(':')
                    ip, port = addr.split(':')
                else:
                    # 无认证的格式: protocol://ip:port
                    protocol = line.split('://')[0]
                    addr = line.split('://')[1]
                    ip, port = addr.split(':')
                    username = password = None
            else:
                # 无协议格式
                parts = line.split(':')
                if len(parts) == 2:
                    # ip:port
                    ip, port = parts
                    protocol = 'http'
                    username = password = None
                elif len(parts) == 4:
                    # ip:port:username:password
                    ip, port, username, password = parts
                    protocol = 'http'
                else:
                    return None
            
            return {
                'ip': ip,
                'port': int(port),
                'protocol': protocol,
                'username': username,
                'password': password,
                'url': self._build_proxy_url(protocol, ip, port, username, password),
                'success_count': 0,
                'failure_count': 0,
                'last_used': 0,
                'status': 'active',  # active, failed, banned
                'response_time': 0
            }
        except Exception as e:
            self.logger.warning(f"解析代理IP行失败: {line}, 错误: {e}")
            return None
    
    def _build_proxy_url(self, protocol, ip, port, username=None, password=None):
        """构建代理URL"""
        if username and password:
            return f"{protocol}://{username}:{password}@{ip}:{port}"
        else:
            return f"{protocol}://{ip}:{port}"
    
    def _create_sample_proxy_file(self, filename):
        """创建示例代理IP文件"""
        sample_content = """# 代理IP配置文件
# 支持多种格式:
# 
# 1. 简单格式: ip:port
# 127.0.0.1:8080
# 192.168.1.100:3128
# 
# 2. 带协议: protocol://ip:port  
# http://127.0.0.1:8080
# https://192.168.1.100:3128
# socks5://127.0.0.1:1080
# 
# 3. 带认证: protocol://username:password@ip:port
# http://user:pass@127.0.0.1:8080
# 
# 4. 四段格式: ip:port:username:password
# 127.0.0.1:8080:user:pass
# 
# 请添加你的代理IP地址
"""
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(sample_content)
            self.logger.info(f"已创建示例代理IP文件: {filename}")
        except Exception as e:
            self.logger.error(f"创建示例文件失败: {e}")
    
    def get_next_proxy(self):
        """获取下一个可用的代理IP"""
        with self.proxy_lock:
            if not self.proxy_pool:
                return None
            
            # 过滤可用的代理
            active_proxies = [p for p in self.proxy_pool if p['status'] == 'active']
            
            if not active_proxies:
                self.logger.warning("没有可用的代理IP")
                return None
            
            # 选择策略：轮询 + 成功率权重
            proxy = self._select_best_proxy(active_proxies)
            
            # 更新使用统计
            proxy['last_used'] = time.time()
            
            return proxy
    
    def _select_best_proxy(self, proxies):
        """选择最佳代理IP"""
        # 策略1: 简单轮询
        if all(p['success_count'] == 0 and p['failure_count'] == 0 for p in proxies):
            return random.choice(proxies)
        
        # 策略2: 基于成功率和响应时间的权重选择
        best_proxy = None
        best_score = -1
        
        for proxy in proxies:
            total_requests = proxy['success_count'] + proxy['failure_count']
            if total_requests == 0:
                success_rate = 1.0
            else:
                success_rate = proxy['success_count'] / total_requests
            
            # 响应时间权重（越快越好）
            time_weight = 1.0 / (proxy['response_time'] + 0.1)
            
            # 综合评分
            score = success_rate * 0.7 + time_weight * 0.3
            
            if score > best_score:
                best_score = score
                best_proxy = proxy
        
        return best_proxy
    
    def test_proxy(self, proxy, test_url="http://httpbin.org/ip", timeout=10):
        """测试代理IP是否可用"""
        try:
            proxies = {
                'http': proxy['url'],
                'https': proxy['url']
            }
            
            start_time = time.time()
            response = requests.get(test_url, proxies=proxies, timeout=timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                proxy['response_time'] = response_time
                self.logger.info(f"代理 {proxy['ip']}:{proxy['port']} 测试成功，响应时间: {response_time:.2f}s")
                return True
            else:
                self.logger.warning(f"代理 {proxy['ip']}:{proxy['port']} 测试失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.warning(f"代理 {proxy['ip']}:{proxy['port']} 测试异常: {e}")
            return False
    
    def test_all_proxies(self, test_url="http://httpbin.org/ip"):
        """测试所有代理IP"""
        self.logger.info("开始测试所有代理IP...")
        
        working_proxies = []
        failed_proxies = []
        
        for proxy in self.proxy_pool:
            if self.test_proxy(proxy, test_url):
                proxy['status'] = 'active'
                working_proxies.append(proxy)
            else:
                proxy['status'] = 'failed'
                failed_proxies.append(proxy)
        
        self.logger.info(f"代理测试完成: {len(working_proxies)} 个可用, {len(failed_proxies)} 个失败")
        return working_proxies, failed_proxies
    
    def mark_proxy_failed(self, proxy, reason="request_failed"):
        """标记代理为失败状态"""
        with self.proxy_lock:
            proxy['failure_count'] += 1
            
            # 如果失败率过高，标记为失败状态
            total_requests = proxy['success_count'] + proxy['failure_count']
            failure_rate = proxy['failure_count'] / total_requests
            
            if failure_rate > 0.5 and total_requests > 5:
                proxy['status'] = 'failed'
                self.logger.warning(f"代理 {proxy['ip']}:{proxy['port']} 被标记为失败: {reason}")
    
    def mark_proxy_success(self, proxy):
        """标记代理使用成功"""
        with self.proxy_lock:
            proxy['success_count'] += 1
            if proxy['status'] == 'failed' and proxy['success_count'] > proxy['failure_count']:
                proxy['status'] = 'active'
                self.logger.info(f"代理 {proxy['ip']}:{proxy['port']} 恢复活跃状态")
    
    def get_proxy_stats(self):
        """获取代理使用统计"""
        stats = {
            'total_proxies': len(self.proxy_pool),
            'active_proxies': len([p for p in self.proxy_pool if p['status'] == 'active']),
            'failed_proxies': len([p for p in self.proxy_pool if p['status'] == 'failed']),
            'banned_proxies': len([p for p in self.proxy_pool if p['status'] == 'banned']),
        }
        return stats
    
    def show_proxy_status(self):
        """显示代理状态"""
        stats = self.get_proxy_stats()
        
        print("\n📊 代理IP状态统计")
        print("=" * 50)
        print(f"总代理数: {stats['total_proxies']}")
        print(f"可用代理: {stats['active_proxies']}")
        print(f"失败代理: {stats['failed_proxies']}")
        print(f"被封代理: {stats['banned_proxies']}")
        
        print("\n📋 详细代理列表:")
        print("-" * 80)
        print(f"{'状态':<8} {'地址':<20} {'成功':<6} {'失败':<6} {'成功率':<8} {'响应时间':<8}")
        print("-" * 80)
        
        for proxy in self.proxy_pool:
            total = proxy['success_count'] + proxy['failure_count']
            success_rate = proxy['success_count'] / total if total > 0 else 0
            status_emoji = {'active': '✅', 'failed': '❌', 'banned': '🚫'}.get(proxy['status'], '❓')
            
            print(f"{status_emoji:<8} {proxy['ip']}:{proxy['port']:<12} "
                  f"{proxy['success_count']:<6} {proxy['failure_count']:<6} "
                  f"{success_rate:.1%:<8} {proxy['response_time']:.2f}s")

class CBGProxyCrawler:
    """整合代理IP轮换的CBG爬虫"""
    
    def __init__(self, proxy_manager, cookies_file="cookies.txt"):
        self.proxy_manager = proxy_manager
        self.logger = self._setup_logger()
        self.base_url = "https://xyq.cbg.163.com/cgi-bin/recommend.py"
        
        # 加载Cookie
        self.cookie = self._load_cookie(cookies_file)
        
    def _setup_logger(self):
        """设置日志"""
        logger = logging.getLogger('CBGProxyCrawler')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_cookie(self, filename):
        """加载Cookie"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            self.logger.error(f"加载Cookie失败: {e}")
            return None
    
    def create_session_with_proxy(self, proxy=None):
        """创建带代理的会话"""
        session = requests.Session()
        
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': 'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py',
        }
        
        if self.cookie:
            headers['Cookie'] = self.cookie
        
        session.headers.update(headers)
        
        # 设置代理
        if proxy:
            proxies = {
                'http': proxy['url'],
                'https': proxy['url']
            }
            session.proxies.update(proxies)
            self.logger.info(f"使用代理: {proxy['ip']}:{proxy['port']}")
        
        return session
    
    def fetch_page_with_proxy_retry(self, page, max_retries=3):
        """使用代理轮换获取页面"""
        for attempt in range(max_retries):
            # 获取代理
            proxy = self.proxy_manager.get_next_proxy()
            if not proxy:
                self.logger.error(f"第{page}页: 没有可用的代理IP")
                return None
            
            try:
                # 创建会话
                session = self.create_session_with_proxy(proxy)
                
                # 构建请求参数
                params = {
                    'callback': f'Request.JSONP.request_map.request_{random.randint(0, 999)}',
                    '_': str(int(time.time() * 1000)),
                    'server_type': 3,
                    'act': 'recommd_by_role',
                    'page': page,
                    'count': 15,
                    'search_type': 'overall_search_role',
                    'view_loc': 'overall_search'
                }
                
                url = f"{self.base_url}?{urlencode(params)}"
                
                self.logger.info(f"第{page}页 使用代理 {proxy['ip']}:{proxy['port']}")
                
                # 发送请求
                start_time = time.time()
                response = session.get(url, timeout=30)
                response_time = time.time() - start_time
                
                proxy['response_time'] = response_time
                
                if response.status_code == 200:
                    # 检查响应内容
                    if self._is_valid_response(response.text):
                        self.proxy_manager.mark_proxy_success(proxy)
                        self.logger.info(f"第{page}页成功获取 (代理: {proxy['ip']}:{proxy['port']}, 响应时间: {response_time:.2f}s)")
                        return self._parse_jsonp_response(response.text)
                    else:
                        self.logger.warning(f"第{page}页响应异常，可能被反爬虫检测")
                        self.proxy_manager.mark_proxy_failed(proxy, "invalid_response")
                
                elif response.status_code in [403, 429]:
                    self.logger.warning(f"第{page}页: 代理 {proxy['ip']}:{proxy['port']} 被限制 ({response.status_code})")
                    self.proxy_manager.mark_proxy_failed(proxy, f"http_{response.status_code}")
                
                else:
                    self.logger.warning(f"第{page}页: HTTP {response.status_code}")
                    self.proxy_manager.mark_proxy_failed(proxy, f"http_{response.status_code}")
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"第{page}页: 代理 {proxy['ip']}:{proxy['port']} 超时")
                self.proxy_manager.mark_proxy_failed(proxy, "timeout")
                
            except requests.exceptions.ConnectionError:
                self.logger.warning(f"第{page}页: 代理 {proxy['ip']}:{proxy['port']} 连接失败")
                self.proxy_manager.mark_proxy_failed(proxy, "connection_error")
                
            except Exception as e:
                self.logger.warning(f"第{page}页: 代理 {proxy['ip']}:{proxy['port']} 异常: {e}")
                self.proxy_manager.mark_proxy_failed(proxy, "unknown_error")
            
            # 重试前等待
            if attempt < max_retries - 1:
                wait_time = random.uniform(1, 3)
                self.logger.info(f"等待 {wait_time:.1f}秒后重试...")
                time.sleep(wait_time)
        
        self.logger.error(f"第{page}页: 所有重试都失败")
        return None
    
    def _is_valid_response(self, text):
        """检查响应是否有效"""
        try:
            # 检查是否包含正常的JSONP结构
            if 'Request.JSONP.request_map.request_' in text and '({' in text and '})' in text:
                return True
            return False
        except Exception:
            return False
    
    def _parse_jsonp_response(self, text):
        """解析JSONP响应"""
        try:
            match = re.search(r'Request\.JSONP\.request_map\.request_\d+\((.*)\)', text)
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"解析响应失败: {e}")
        return None
    
    def parallel_crawl_with_proxy(self, start_page, end_page, delay_range=(1, 3)):
        """使用代理并行爬取"""
        self.logger.info(f"开始使用代理并行爬取第{start_page}-{end_page}页")
        
        results = {}
        
        def crawl_single_page(page):
            """爬取单页"""
            result = self.fetch_page_with_proxy_retry(page)
            
            # 随机延时
            delay = random.uniform(*delay_range)
            time.sleep(delay)
            
            return page, result
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=min(3, len([p for p in self.proxy_manager.proxy_pool if p['status'] == 'active']))) as executor:
            future_to_page = {executor.submit(crawl_single_page, page): page 
                             for page in range(start_page, end_page + 1)}
            
            for future in as_completed(future_to_page):
                page, result = future.result()
                results[page] = result
        
        successful_pages = len([r for r in results.values() if r])
        self.logger.info(f"并行爬取完成，成功获取 {successful_pages} 页数据")
        
        return results

def demo_proxy_rotation():
    """演示代理IP轮换功能"""
    print("🌐 代理IP轮换演示")
    print("=" * 50)
    
    # 1. 初始化代理管理器
    proxy_manager = ProxyRotationManager()
    
    if not proxy_manager.proxy_pool:
        print("❌ 没有可用的代理IP，请在 proxy_list.txt 中添加代理IP")
        print("\n📝 代理IP格式示例:")
        print("http://127.0.0.1:8080")
        print("192.168.1.100:3128") 
        print("socks5://user:pass@127.0.0.1:1080")
        return
    
    # 2. 测试所有代理
    print("\n🔍 测试代理IP可用性...")
    working_proxies, failed_proxies = proxy_manager.test_all_proxies()
    
    if not working_proxies:
        print("❌ 所有代理IP都不可用")
        return
    
    # 3. 显示代理状态
    proxy_manager.show_proxy_status()
    
    # 4. 演示CBG爬虫集成
    print("\n🚀 测试CBG爬虫集成...")
    crawler = CBGProxyCrawler(proxy_manager)
    
    # 测试单页爬取
    result = crawler.fetch_page_with_proxy_retry(1)
    if result:
        print("✅ 单页爬取成功")
    else:
        print("❌ 单页爬取失败")
    
    # 显示最终统计
    print("\n📊 最终代理统计:")
    proxy_manager.show_proxy_status()

if __name__ == "__main__":
    demo_proxy_rotation() 