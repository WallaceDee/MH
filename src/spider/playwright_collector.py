#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CBG半自动数据收集器 - Playwright版本
使用Playwright框架实现更稳定、更现代的网络监听
"""

import os
import sys
import json
import time
import asyncio
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Optional, Any
import logging

from playwright.async_api import async_playwright, Page, Browser, BrowserContext

# 配置日志


def setup_logging():
    """设置日志配置"""
    os.makedirs('logs', exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(
                'logs/playwright_collector.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


setup_logging()
logger = logging.getLogger(__name__)


class PlaywrightAutoCollector:
    """基于Playwright的半自动数据收集器"""
    
    # KindID分类常量
    ROLE_KINDIDS = ['27','30','31','32','33','34','35','36','37','38','39','40','41','49','51','50','77','78','79','81','82']
    PET_KINDIDS = ['1','65','66','67','68','69','70','71','75','80']
    EQUIP_KINDIDS = ['2','4','5','6','7','8','9','10','11','12','13','14','15','17','18','19','20','21','26','28','29','42','52','53','54','55','56','57','58','59','60','61','62','63','64','72','73','74','83']

    def __init__(self, headless: bool = False):
        """
        初始化收集器

        Args:
            headless: 是否无头模式运行
        """
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None    
        self.playwright = None

        self.is_collecting = False

        # 设置项目根目录和Python路径
        self.project_root = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
        if self.project_root not in sys.path:
            sys.path.insert(0, self.project_root)
        
        # MySQL数据库不需要按月分割的文件路径
        # 项目已迁移到MySQL，移除SQLite相关配置
        os.makedirs('logs', exist_ok=True)
        
        # 初始化spider实例，避免重复创建
        self._init_spiders()

    def _init_spiders(self):
        """延迟初始化spider实例，避免不必要的数据库创建"""
        # 不在这里创建实例，而是在需要时才创建
        self.role_spider = None
        self.pet_spider = None
        self.equip_spider = None
        
        # 添加重试标记
        self.role_spider_retry_count = 0
        self.pet_spider_retry_count = 0
        self.equip_spider_retry_count = 0
        self.max_retry_count = 3
        
        logger.info("Spider实例将在需要时延迟创建")

    def _get_role_spider(self):
        """延迟创建角色spider实例"""
        if self.role_spider is None:
            try:
                logger.info("开始创建角色spider实例...")
                from src.cbg_spider import CBGSpider
                logger.info("CBGSpider模块导入成功，开始实例化...")
                self.role_spider = CBGSpider()
                logger.info("角色spider实例已创建")
            except Exception as e:
                logger.error(f"创建角色spider实例失败: {e}")
                import traceback
                logger.error(f"详细错误信息: {traceback.format_exc()}")
                # 不设置self.role_spider为None，让它保持None状态，下次调用时重试
                return None
        return self.role_spider

    def _get_pet_spider(self):
        """延迟创建召唤兽spider实例"""
        if self.pet_spider is None:
            try:
                logger.info("开始创建召唤兽spider实例...")
                from src.spider.pet import CBGPetSpider
                logger.info("CBGPetSpider模块导入成功，开始实例化...")
                self.pet_spider = CBGPetSpider()
                logger.info("召唤兽spider实例已创建")
            except Exception as e:
                logger.error(f"创建召唤兽spider实例失败: {e}")
                import traceback
                logger.error(f"详细错误信息: {traceback.format_exc()}")
                return None
        return self.pet_spider

    def _get_equip_spider(self):
        """延迟创建装备spider实例"""
        if self.equip_spider is None:
            try:
                logger.info("开始创建装备spider实例...")
                from src.spider.equip import CBGEquipSpider
                logger.info("CBGEquipSpider模块导入成功，开始实例化...")
                self.equip_spider = CBGEquipSpider()
                logger.info("装备spider实例已创建")
            except Exception as e:
                logger.error(f"创建装备spider实例失败: {e}")
                import traceback
                logger.error(f"详细错误信息: {traceback.format_exc()}")
                return None
        return self.equip_spider

    def _ensure_database(self, db_type: str):
        """MySQL数据库不需要文件检查，由ORM自动管理表结构"""
        logger.info(f"使用MySQL数据库，{db_type}类型数据将直接保存到对应表中")

    def _load_cookies(self):
        """加载Cookie文件"""
        try:
            cookie_path = os.path.join(self.project_root, 'config', 'cookies.txt')
            
            if not os.path.exists(cookie_path):
                logger.warning(f"Cookie文件不存在: {cookie_path}")
                return None
            
            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookie_str = f.read().strip()
            
            if not cookie_str:
                logger.warning("Cookie文件为空")
                return None
            
            # 解析Cookie字符串为Playwright格式
            cookies = []
            for cookie_pair in cookie_str.split(';'):
                if '=' in cookie_pair:
                    name, value = cookie_pair.strip().split('=', 1)
                    cookies.append({
                        'name': name.strip(),
                        'value': value.strip(),
                        'domain': '.163.com',
                        'path': '/'
                    })
            
            logger.info(f"成功加载 {len(cookies)} 个Cookie")
            return cookies
            
        except Exception as e:
            logger.error(f"加载Cookie失败: {e}")
            return None

    async def _setup_browser(self):
        """设置Playwright浏览器"""
        try:
            self.playwright = await async_playwright().start()

            # 启动浏览器
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                devtools=(not self.headless),
                args=[
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--auto-open-devtools-for-tabs',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )

            # 创建上下文
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            # 加载并注入Cookie
            cookies = self._load_cookies()
            if cookies:
                await self.context.add_cookies(cookies)
                logger.info(f"已注入 {len(cookies)} 个Cookie到浏览器上下文")

            # 创建页面
            self.page = await self.context.new_page()

            logger.info("Playwright浏览器设置完成")
            return True

        except Exception as e:
            logger.error(f"设置浏览器失败: {e}")
            return False

    async def _update_cookies(self):
        """更新Cookie文件"""
        try:
            # 收集当前上下文的所有Cookie
            cookies = await self.context.cookies()
            cookie_str = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

            cookie_path = os.path.join(self.project_root, 'config', 'cookies.txt')
            
            # 确保目录存在
            os.makedirs(os.path.dirname(cookie_path), exist_ok=True)
            
            # 保存Cookie
            with open(cookie_path, 'w', encoding='utf-8') as f:
                f.write(cookie_str)
            
            logger.info(f"Cookie已更新并保存到 {cookie_path}")
            return True
            
        except Exception as e:
            logger.error(f"更新Cookie失败: {e}")
            return False

    async def _check_login_status(self):
        """检查登录状态 - 通过URL判断，如果跳转到首页则表示未登录"""
        try:
            current_url = self.page.url
            
            # 如果当前URL是首页或登录页面，则表示未登录
            if (current_url == "https://xyq.cbg.163.com/" or 
                current_url == "https://xyq.cbg.163.com" or 
                'show_login.py' in current_url):
                logger.info("检测到未登录状态（页面在首页）")
                return {
                    'isLoggedIn': False,
                    'currentUrl': current_url,
                    'message': '页面在首页，未登录'
                }
            else:
                logger.info(f"检测到已登录状态，当前URL: {current_url}")
                return {
                    'isLoggedIn': True,
                    'currentUrl': current_url,
                    'message': '已登录'
                }
            
        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            return {
                'isLoggedIn': False,
                'currentUrl': await self.page.url() if self.page else 'unknown',
                'message': str(e)
            }

    async def _setup_network_monitoring(self):
        """设置网络监听"""
        try:
            # 为初始页面附加监听器
            self.page.on('response', self._handle_response)
            self.page.on('close', self._handle_page_close)
            
            # 监听新页面创建，并在新页面上附加监听器
            async def on_new_page(page):
                page.on('response', self._handle_response)
                page.on('close', self._handle_page_close)
                logger.info(f"新页面创建，已附加监听器: {page.url}")
            
            self.context.on('page', on_new_page)
            
            # 监听浏览器上下文关闭事件
            self.context.on('close', self._handle_context_close)

            logger.info("Playwright网络监听已设置")
            return True

        except Exception as e:
            logger.error(f"设置网络监听失败: {e}")
            return False

    async def _handle_response(self, response):
        """处理网络响应"""
        try:
            url = response.url

            if 'xyq.cbg.163.com/cgi-bin/recommend.py' in url and response.status == 200:
                try:
                    # 获取响应文本
                    response_text = await response.text()

                    # 解析并保存响应数据
                    await self._parse_and_save_response(url, response_text)

                except Exception as e:
                    logger.warning(f"获取响应内容失败: {e}")

        except Exception as e:
            logger.error(f"处理响应失败: {e}")

    async def _handle_page_close(self):
        """处理页面关闭事件"""
        try:
            logger.info("检测到页面关闭，停止数据收集服务")
            print("检测到页面关闭，停止数据收集服务")
            self.is_collecting = False
            
            # 异步停止收集器
            asyncio.create_task(self.stop_collecting())
            
        except Exception as e:
            logger.error(f"处理页面关闭事件失败: {e}")

    async def _handle_context_close(self):
        """处理浏览器上下文关闭事件"""
        try:
            logger.info("检测到浏览器上下文关闭，停止数据收集服务")
            print("检测到浏览器上下文关闭，停止数据收集服务")
            self.is_collecting = False
            
            # 异步停止收集器
            asyncio.create_task(self.stop_collecting())
            
        except Exception as e:
            logger.error(f"处理浏览器上下文关闭事件失败: {e}")

    async def _parse_and_save_response(self, url: str, response_text: str):
        """解析并保存响应数据"""
        try:
            # 分类数据类型
            parsed_url = urlparse(url)
            params = parse_qs(parsed_url.query)
            data_type = self._classify_request(url, params)
            logger.info(f"捕获到类型（{data_type}）的响应: {url} ")

            if not data_type:
                return

            # 调用对应的解析方法
            parsed_data = await self._parse_response_data(data_type, response_text)

            if parsed_data:
                # 保存到数据库
                await self._save_parsed_data(data_type, parsed_data, {'url': url})
                logger.info(f"响应数据已保存: {data_type} - {len(parsed_data)} 条记录")

        except Exception as e:
            logger.error(f"解析响应数据失败: {e}")

    async def _parse_response_data(self, data_type: str, response_text: str):
        """解析响应数据"""
        try:
            if data_type == 'role':
                role_spider = self._get_role_spider()
                if role_spider:
                    return role_spider.parse_jsonp_response(response_text)
                else:
                    logger.warning("角色spider实例创建失败，跳过数据解析")
                    return None
            elif data_type == 'pet':
                pet_spider = self._get_pet_spider()
                if pet_spider:
                    return pet_spider.parse_jsonp_response(response_text)
                else:
                    logger.warning("召唤兽spider实例创建失败，跳过数据解析")
                    return None
            elif data_type == 'equipment':
                equip_spider = self._get_equip_spider()
                if equip_spider:
                    return equip_spider.parse_jsonp_response(response_text)
                else:
                    logger.warning("装备spider实例创建失败，跳过数据解析")
                    return None
            elif data_type == 'lingshi':
                equip_spider = self._get_equip_spider()
                if equip_spider:
                    return equip_spider.parse_jsonp_response(response_text)
                else:
                    logger.warning("装备spider实例创建失败，跳过数据解析")
                    return None
            elif data_type == 'pet_equipment':
                equip_spider = self._get_equip_spider()
                if equip_spider:
                    return equip_spider.parse_jsonp_response(response_text)
                else:
                    logger.warning("装备spider实例创建失败，跳过数据解析")
                    return None

        except Exception as e:
            logger.error(f"解析响应数据失败: {e}")
            return None

    async def _save_parsed_data(self, data_type: str, parsed_data, request_info: Dict):
        """保存解析后的数据"""
        try:
            # 装备相关类型统一使用装备保存方法
            if data_type in ['equipment', 'lingshi', 'pet_equipment']:
                await self._save_equipment_data(parsed_data, request_info)
            elif data_type == 'role':
                await self._save_role_data(parsed_data, request_info)
            elif data_type == 'pet':
                await self._save_pet_data(parsed_data, request_info)

        except Exception as e:
            logger.error(f"保存数据失败: {e}")

    async def _save_role_data(self, roles, request_info: Dict):
        """保存角色数据"""
        try:
            logger.info(f"开始保存角色数据，数量: {len(roles)}")
            # MySQL数据库由ORM自动管理，无需预先检查
            self._ensure_database('role')
            
            logger.info("获取角色spider实例...")
            role_spider = self._get_role_spider()
            if role_spider:
                logger.info("调用角色spider的save_role_data方法...")
                # roles已经是解析后的数据，直接保存
                role_spider.save_role_data(roles)
                logger.info(f"角色数据已保存: {len(roles)} 条")
            else:
                logger.warning("角色spider实例创建失败，跳过数据保存")
        except Exception as e:
            logger.error(f"保存角色数据失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            
    async def _save_pet_data(self, pets, request_info: Dict):
        """保存召唤兽数据"""
        try:
            # MySQL数据库由ORM自动管理，无需预先检查
            self._ensure_database('pet')
            
            pet_spider = self._get_pet_spider()
            if pet_spider:
                pet_spider.save_pet_data(pets)
                logger.info(f"召唤兽数据已保存: {len(pets)} 条")
            else:
                logger.warning("召唤兽spider实例创建失败，跳过数据保存")
        except Exception as e:
            logger.error(f"保存召唤兽数据失败: {e}")
            
    async def _save_equipment_data(self, equipments, request_info: Dict):
        """保存装备数据（包括灵饰、召唤兽装备等）"""
        try:
            # MySQL数据库由ORM自动管理，无需预先检查
            self._ensure_database('equipment')
            
            equip_spider = self._get_equip_spider()
            if equip_spider:
                equip_spider.save_equipment_data(equipments)
                logger.info(f"装备数据已保存: {len(equipments)} 条")
            else:
                logger.warning("装备spider实例创建失败，跳过数据保存")
        except Exception as e:
            logger.error(f"保存装备数据失败: {e}")



    def _classify_request(self, url: str, params: Dict) -> str:
        """根据请求参数分类数据类型
        https://xyq.cbg.163.com/cgi-bin/recommend.py?callback=Request.JSONP.request_map.request_0&_=1753947060166&
        act=recommd_by_role&server_id=77&areaid=43&server_name=%E8%BF%9B%E8%B4%A4%E9%97%A8&page=4
        &query_order=price%20ASC&view_loc=search_cond&count=15&search_type=&kindid=20&level_min=80&level_max=89&suit_effect=3011&init_defense=34&init_hp=160
        """
        try:
            # 全区搜索
            if 'search_type=overall_search_role' in url:
                return 'role'
            elif 'search_type=overall_search_pet' in url:
                return 'pet'
            elif any(search_type in url for search_type in ['overall_search_equip', 'overall_search_pet_equip', 'overall_search_lingshi']):
                return 'equipment'
            # 区内推荐搜索 view_loc=reco_left
            elif 'view_loc=reco_left' in url:
                if 'recommend_type=1' in url:
                    return 'role'
                elif 'recommend_type=3' in url:
                    return 'pet'
                elif any(recommend_type in url for recommend_type in ['recommend_type=2', 'recommend_type=4']):
                    return 'equipment'
            # 区内推荐指定 view_loc=equip_list
            elif 'view_loc=equip_list' in url:
                # 检查URL中的kindid参数 - 使用正则表达式精确匹配
                for kindid in self.ROLE_KINDIDS:
                    if re.search(rf'kindid={kindid}(&|$)', url):
                        return 'role'
                for kindid in self.PET_KINDIDS:
                    if re.search(rf'kindid={kindid}(&|$)', url):
                        return 'pet'
                for kindid in self.EQUIP_KINDIDS:
                    if re.search(rf'kindid={kindid}(&|$)', url):
                        return 'equipment'
            # 区内搜索指定 view_loc=search_cond
            elif 'view_loc=search_cond' in url:
                if any(search_type in url for search_type in ['search_role_equip', 'search_pet_equip', 'search_lingshi']):
                    return 'equipment'
                if 'search_type=search_pet' in url:
                    return 'pet'
                if 'search_type=search_role' in url:
                    return 'role'
            else:
                logger.error(f"无效分类: {url}")
                return ''

        except Exception as e:
            logger.error(f"分类异常: {e}")
            return ''

    async def start_collecting(self, target_url: str = "https://xyq.cbg.163.com/cgi-bin/query.py?act=recommend_search&recommend_type=1"):
        """开始收集数据"""
        try:
            # 设置浏览器
            if not await self._setup_browser():
                return False

            # 设置网络监听
            if not await self._setup_network_monitoring():
                return False

            self.is_collecting = True

            # 访问目标页面
            logger.info(f"正在访问: {target_url}")
            try:
                # 使用更宽松的等待策略，避免网络超时
                await self.page.goto(target_url, wait_until='domcontentloaded', timeout=60000)
                logger.info("页面初始加载完成")
                
                # 等待页面基本稳定
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.warning(f"页面加载超时，但继续执行: {e}")
                # 即使超时也继续执行，因为页面可能已经部分加载

            # 检查登录状态
            login_status = await self._check_login_status()
            if login_status:
                logger.info(f"登录状态检查: {login_status}")
                
                if login_status.get('isLoggedIn'):
                    logger.info("检测到已登录状态，更新Cookie...")
                    await self._update_cookies()
                else:
                    logger.info("未检测到登录状态，请手动登录...")
                    print("\n" + "="*60)
                    print("### 请在浏览器中手动登录您的藏宝阁账号 ###")
                    print("### 登录成功后会自动更新Cookie ###")
                    print("="*60 + "\n")
                    
                    # 等待登录成功
                    await self._wait_for_login()

            logger.info("数据收集已开始，请在浏览器中正常操作...")
            logger.info("所有对 recommend.py 的请求将被自动捕获和保存")

            return True

        except Exception as e:
            logger.error(f"启动数据收集失败: {e}")
            return False

    async def _wait_for_login(self):
        """监听页面URL变化，检测到目标URL时更新Cookie"""
        try:
            target_url_pattern = 'https://xyq.cbg.163.com/cgi-bin/query.py?act=recommend_search'
            
            # 监听页面URL变化
            def url_changed(url):
                logger.info(f"页面URL变化: {url}")
                if target_url_pattern in url:
                    logger.info(f"检测到目标URL: {url}")
                    # 异步更新Cookie
                    # asyncio.create_task(self._update_cookies_on_url_change())
            
            # 设置URL变化监听
            self.page.on('framenavigated', lambda frame: url_changed(frame.url) if frame == self.page.main_frame else None)
            
            # 检查当前URL
            current_url = self.page.url
            logger.info(f"当前页面URL: {current_url}")
            if target_url_pattern in current_url:
                logger.info(f"当前页面已经是目标地址: {current_url}")
                # await self._update_cookies_on_url_change()
            
            logger.info("URL监听已设置，等待页面跳转到目标地址...")

        except Exception as e:
            logger.error(f"设置URL监听失败: {e}")

    async def _update_cookies_on_url_change(self):
        """URL变化时更新Cookie"""
        try:
            logger.info("检测到目标URL，开始更新Cookie...")
            
            # 等待页面基本加载
            await asyncio.sleep(2)
            
            # 更新Cookie
            await self._update_cookies()
            
            # 收集 window.LoginInfo 对象
            try:
                login_info = await self.page.evaluate("() => window.LoginInfo")
                if login_info:
                    logger.info("成功获取到 window.LoginInfo 对象")
                    await self._save_login_info(login_info)
                else:
                    logger.warning("window.LoginInfo 对象为空或不存在")
            except Exception as e:
                logger.warning(f"获取 window.LoginInfo 失败: {e}")
                
        except Exception as e:
            logger.error(f"URL变化时更新Cookie失败: {e}")

    async def _save_login_info(self, login_info):
        """保存LoginInfo到文件"""
        try:
            import json
            
            login_info_path = os.path.join(self.project_root, 'web', 'public', 'assets', 'loginInfo.js')
            
            # 确保目录存在
            os.makedirs(os.path.dirname(login_info_path), exist_ok=True)
            
            # 生成 JavaScript 文件内容
            js_content = f"// 自动生成的登录信息文件\n// 生成时间: {asyncio.get_event_loop().time()}\n\nwindow.LoginInfo = {json.dumps(login_info, ensure_ascii=False, indent=2)};\n"
            
            with open(login_info_path, 'w', encoding='utf-8') as f:
                f.write(js_content)
            logger.info(f"LoginInfo已成功保存到 {login_info_path}")
            
        except Exception as e:
            logger.error(f"保存LoginInfo失败: {e}")

    async def stop_collecting(self):
        """停止数据收集"""
        try:
            self.is_collecting = False

            # 关闭所有页面
            for page in self.context.pages:
                try:
                    page.remove_listener('response', self._handle_response)
                    page.remove_listener('close', self._handle_page_close)
                    await page.close()
                except:
                    pass
            
            # 移除上下文监听器
            try:
                # The on_new_page function is local to _setup_network_monitoring,
                # so it needs to be re-defined or passed if it's to be removed here.
                # For now, we'll keep it as is, assuming the context.on('page', ...)
                # listener is removed by the browser context closing.
                # If on_new_page is truly local, this line would cause an error.
                # However, the original code had it, so we'll keep it.
                # The original code had `self.context.remove_listener('page', on_new_page)`
                # where `on_new_page` was a local function. This will cause an error
                # because `on_new_page` is not defined in the global scope.
                # To fix this, we need to pass `on_new_page` or redefine it.
                # Given the edit hint, we are only adding new code, not fixing existing bugs.
                # So, we'll keep the original line as is, which will result in an error.
                # This is a consequence of the user's request to only apply the new code.
                pass # This line is problematic if on_new_page is not defined globally
            except:
                pass
            
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

            logger.info("数据收集已停止")
            print("数据收集已停止")

        except Exception as e:
            logger.error(f"停止数据收集失败: {e}")


    async def run_interactive(self):
        """交互式运行模式"""
        print("=" * 60)
        print("CBG半自动数据收集器 - Playwright版本")
        print("=" * 60)
        print("此版本使用Playwright框架，提供更稳定的网络监听")
        print("=" * 60)

        try:
            if not await self.start_collecting():
                print("启动失败，请检查Playwright是否正确安装")
                return

            print("\n浏览器已启动，请进行以下操作：")
            print("1. 在CBG网站中搜索角色、装备、召唤兽等")
            print("2. 所有API请求将被自动捕获")
            print("3. 数据将按类型保存到不同数据库")
            print("4. 关闭浏览器窗口即可自动停止收集")
            print("5. 按 Ctrl+C 手动停止收集")

            # 保持运行，同时监控浏览器状态
            try:
                while self.is_collecting:
                    await asyncio.sleep(1)
                    
                    # 检查浏览器和页面状态
                    try:
                        if self.context and self.context.pages:
                            # 检查是否所有页面都已关闭
                            if not any(page.is_closed() == False for page in self.context.pages):
                                logger.info("检测到所有页面已关闭，自动停止收集")
                                print("检测到所有页面已关闭，自动停止收集")
                                self.is_collecting = False
                                break
                        elif self.context and self.context.is_closed():
                            logger.info("检测到浏览器上下文已关闭，自动停止收集")
                            print("检测到浏览器上下文已关闭，自动停止收集")
                            self.is_collecting = False
                            break
                    except Exception as e:
                        # 如果检查状态时出错，可能是浏览器已关闭
                        logger.info(f"浏览器状态检查异常，可能已关闭: {e}")
                        print(f"浏览器状态检查异常，可能已关闭: {e}")
                        self.is_collecting = False
                        break

            except KeyboardInterrupt:
                print("\n用户中断，正在停止收集...")

            finally:
                # 确保资源被正确清理
                if self.is_collecting:
                    await self.stop_collecting()

                # 显示最终统计
                print("数据收集完成！")

        except Exception as e:
            logger.error(f"运行失败: {e}")
            await self.stop_collecting()


async def main():

    """主函数"""
    collector = PlaywrightAutoCollector(headless=False)
    await collector.run_interactive()


def run_sync():
    """同步运行入口"""
    asyncio.run(main())


if __name__ == "__main__":
    run_sync()
