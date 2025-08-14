#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一的Cookie管理模块
封装Cookie读取、设置和验证功能
"""

import os
import logging
import asyncio
import time
from typing import Optional, Dict, Any
from .project_path import get_project_root, get_config_path, get_web_path, ensure_dir_exists


class CookieManager:
    """Cookie管理器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化Cookie管理器
        
        Args:
            logger: 日志器，如果为None则创建一个默认的
        """
        self.logger = logger or self._create_default_logger()
        self.cookie_content = None
        self._load_cookies()
    
    def _create_default_logger(self) -> logging.Logger:
        """创建默认日志器"""
        logger = logging.getLogger('CookieManager')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _get_cookie_path(self) -> str:
        """获取Cookie文件路径"""
        cookie_path = os.path.join(get_config_path(), 'cookies.txt')
        return cookie_path
    
    def _load_cookies(self) -> None:
        """加载Cookie内容"""
        try:
            cookie_path = self._get_cookie_path()
            with open(cookie_path, 'r', encoding='utf-8') as f:
                self.cookie_content = f.read().strip()
            
            if self.cookie_content:
                self.logger.info("成功从config/cookies.txt文件加载Cookie")
            else:
                self.logger.warning("config/cookies.txt文件为空")
                
        except FileNotFoundError:
            self.logger.error("未找到config/cookies.txt文件，请创建该文件并添加有效的Cookie")
            self.cookie_content = None
        except Exception as e:
            self.logger.error(f"读取config/cookies.txt文件失败: {e}")
            self.cookie_content = None
    
    def get_cookie_content(self) -> Optional[str]:
        """获取Cookie内容"""
        return self.cookie_content
    
    def get_cookie_headers(self) -> Dict[str, str]:
        """获取包含Cookie的请求头"""
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'script',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        }
        
        if self.cookie_content:
            headers['Cookie'] = self.cookie_content
        else:
            self.logger.warning("未找到有效的Cookie，可能影响数据获取")
        
        return headers
    
    def setup_session_headers(self, session, referer: str = None) -> None:
        """
        为session设置包含Cookie的请求头
        
        Args:
            session: requests.Session对象
            referer: 可选的referer头
        """
        headers = self.get_cookie_headers()
        
        if referer:
            headers['referer'] = referer
        
        session.headers.update(headers)
    
    def get_playwright_cookies(self) -> list:
        """
        获取Playwright格式的Cookie列表
        
        Returns:
            list: Playwright格式的Cookie列表
        """
        if not self.cookie_content:
            return []
        
        cookies = []
        for cookie in self.cookie_content.split('; '):
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.163.com',
                    'path': '/'
                })
        
        return cookies
    
    def is_cookie_available(self) -> bool:
        """检查Cookie是否可用"""
        return bool(self.cookie_content)
    
    def reload_cookies(self) -> None:
        """重新加载Cookie"""
        self._load_cookies()


# 全局Cookie管理器实例
_cookie_manager = None

def get_cookie_manager(logger: Optional[logging.Logger] = None) -> CookieManager:
    """
    获取全局Cookie管理器实例
    
    Args:
        logger: 可选的日志器
        
    Returns:
        CookieManager: Cookie管理器实例
    """
    global _cookie_manager
    if _cookie_manager is None:
        _cookie_manager = CookieManager(logger)
    return _cookie_manager


def setup_session_with_cookies(session, referer: str = None, logger: Optional[logging.Logger] = None) -> None:
    """
    为session设置Cookie的便捷函数
    
    Args:
        session: requests.Session对象
        referer: 可选的referer头
        logger: 可选的日志器
    """
    cookie_manager = get_cookie_manager(logger)
    cookie_manager.setup_session_headers(session, referer)


def get_playwright_cookies_for_context(logger: Optional[logging.Logger] = None) -> list:
    """
    获取Playwright格式Cookie的便捷函数
    
    Args:
        logger: 可选的日志器
        
    Returns:
        list: Playwright格式的Cookie列表
    """
    cookie_manager = get_cookie_manager(logger)
    return cookie_manager.get_playwright_cookies()


# ==================== Cookie更新功能 ====================

async def _update_cookies_internal(logger: Optional[logging.Logger] = None):
    """
    使用Playwright启动浏览器，让用户登录并获取Cookie和LoginInfo。
    
    Args:
        logger: 可选的日志器
        
    Returns:
        bool: 更新是否成功
    """
    from playwright.async_api import async_playwright
    import json
    
    log = logger or logging.getLogger(__name__)
    
    try:
        async with async_playwright() as p:
            log.info("启动浏览器以更新Cookie...")
            try:
                browser = await p.chromium.launch(headless=False)
            except Exception:
                log.info("未找到默认浏览器，尝试安装Playwright浏览器驱动...")
                log.info("请在终端中运行: playwright install")
                print("\n" + "="*50)
                print("!! Playwright浏览器驱动未安装 !!")
                print("请打开一个新的终端，然后运行以下命令:")
                print("pip install playwright")
                print("playwright install")
                print("="*50 + "\n")
                input("安装完成后，请按回车键继续...")
                browser = await p.chromium.launch(headless=False)

            context = await browser.new_context()
            page = await context.new_page()

            url = 'https://xyq.cbg.163.com/'
            await page.goto(url)

            print("\n" + "#"*60)
            print("### 请在弹出的浏览器窗口中手动登录您的藏宝阁账号。 ###")
            print("### 登录成功后会自动收集Cookie，无需手动操作。 ###")
            print("#"*60 + "\n")

            target_url_pattern = 'https://xyq.cbg.163.com/cgi-bin/query.py?act=recommend_search'
            
            try:
                await page.wait_for_url(lambda url: target_url_pattern in url, timeout=300000)
                current_url = page.url
                log.info(f"检测到页面跳转到目标地址: {current_url}")
            except Exception as e:
                log.warning(f"等待页面跳转超时或失败: {e}")
                current_url = page.url
                if target_url_pattern in current_url:
                    log.info("当前页面已经是目标地址，继续处理")
                else:
                    try:
                        login_success = await page.evaluate("""
                            () => {
                                const loginElements = document.querySelectorAll('[class*="login"], [class*="user"], [class*="avatar"]');
                                const hasLoginInfo = window.LoginInfo && Object.keys(window.LoginInfo).length > 0;
                                return loginElements.length > 0 || hasLoginInfo;
                            }
                        """)
                        if login_success:
                            log.info("检测到登录成功标志，继续收集Cookie")
                        else:
                            log.warning("页面未跳转到目标地址且未检测到登录成功标志，但继续尝试收集Cookie")
                    except Exception as eval_error:
                        log.warning(f"检测登录状态失败: {eval_error}")
                        log.warning("页面未跳转到目标地址，但继续尝试收集Cookie")

            await page.wait_for_load_state('networkidle', timeout=10000)
            log.info("页面加载完成，开始收集Cookie...")

            cookies = await context.cookies()
            cookie_str = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

            login_info = None
            try:
                login_info = await page.evaluate("() => window.LoginInfo")
                if login_info:
                    log.info("成功获取到 window.LoginInfo 对象")
                else:
                    log.warning("window.LoginInfo 对象为空或不存在")
            except Exception as e:
                log.warning(f"获取 window.LoginInfo 失败: {e}")

            cookie_manager = get_cookie_manager(logger)
            cookie_path = cookie_manager._get_cookie_path()
            
            os.makedirs(os.path.dirname(cookie_path), exist_ok=True)
            with open(cookie_path, 'w', encoding='utf-8') as f:
                f.write(cookie_str)
            log.info(f"Cookie已成功更新并保存到 {cookie_path}")

            if login_info:
                login_info_path = os.path.join(get_web_path(), 'public', 'assets', 'loginInfo.js')
                ensure_dir_exists(os.path.dirname(login_info_path))
                
                js_content = f"// 自动生成的登录信息文件\n// 生成时间: {time.time()}\n\nwindow.LoginInfo = {json.dumps(login_info, ensure_ascii=False, indent=2)};\n"
                
                with open(login_info_path, 'w', encoding='utf-8') as f:
                    f.write(js_content)
                log.info(f"LoginInfo已成功保存到 {login_info_path}")
            else:
                log.warning("未能获取到有效的 LoginInfo 数据，跳过保存")

            await browser.close()
            
            cookie_manager.reload_cookies()
            
            return True
    except Exception as e:
        log.error(f"使用Playwright更新Cookie时发生错误: {e}")
        return False


def update_cookies_with_playwright(logger: Optional[logging.Logger] = None):
    """
    同步包装器，以便在非async代码中调用。
    
    Args:
        logger: 可选的日志器
        
    Returns:
        bool: 更新是否成功
    """
    log = logger or logging.getLogger(__name__)
    log.info("检测到登录失效，正在启动Cookie更新程序...")
    try:
        try:
            loop = asyncio.get_running_loop()
            log.warning("在异步环境中无法更新Cookie，请使用异步版本的更新函数")
            return False
        except RuntimeError:
            pass
        
        return asyncio.run(_update_cookies_internal(logger))
    except Exception as e:
        log.error(f"更新Cookie时发生错误: {e}")
        return False


def update_cookies_from_command_line():
    """
    命令行入口点，用于直接运行Cookie更新
    """
    logging.basicConfig(level=logging.INFO)
    success = update_cookies_with_playwright()
    if success:
        print("✅ Cookie更新成功！")
    else:
        print("❌ Cookie更新失败！")
    return success


# ==================== Cookie验证功能 ====================

async def verify_cookie_validity_async(logger: Optional[logging.Logger] = None, disable_resources: bool = True):
    """
    异步验证Cookie的有效性
    使用无头浏览器访问搜索页面来检查Cookie是否有效
    返回: True表示Cookie有效，False表示Cookie无效
    
    Args:
        logger: 可选的日志器
        disable_resources: 是否禁用CSS加载以提高速度，默认True
        
    Returns:
        bool: Cookie是否有效
    """
    log = logger or logging.getLogger(__name__)
    
    try:
        from playwright.async_api import async_playwright
    except Exception as e:
        log.error(f"导入playwright.async_api失败: {e}")
        return False
    
    async def check_with_playwright(cookie_str):
        """使用Playwright检查Cookie有效性的异步函数"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                
                cookies = []
                for cookie in cookie_str.split('; '):
                    if '=' in cookie:
                        name, value = cookie.split('=', 1)
                        cookies.append({
                            'name': name,
                            'value': value,
                            'domain': '.163.com',
                            'path': '/'
                        })
                
                await context.add_cookies(cookies)
                
                page = await context.new_page()
                
                # 禁用CSS以提高加载速度
                if disable_resources:
                    # 禁用所有非必要资源
                    await page.route("**/*.css", lambda route: route.abort())
                    await page.route("**/*.png", lambda route: route.abort())
                    await page.route("**/*.webp", lambda route: route.abort())
                    await page.route("**/*.jpg", lambda route: route.abort())
                    await page.route("**/*.jpeg", lambda route: route.abort())
                    await page.route("**/*.gif", lambda route: route.abort())
                    await page.route("**/*.svg", lambda route: route.abort())
                    await page.route("**/*.woff*", lambda route: route.abort())
                    await page.route("**/*.ttf", lambda route: route.abort())
                    await page.route("**/*.eot", lambda route: route.abort())
                
                test_url = "https://xyq.cbg.163.com/equip?s=2"
                await page.goto(test_url, wait_until='networkidle', timeout=30000)
                
                final_url = page.url
                is_login_page = 'show_login.py' in final_url or 'login' in final_url.lower()
                
                await browser.close()
                
                is_valid = not is_login_page
                
                return is_valid
                
        except Exception as e:
            log.error(f"使用Playwright验证Cookie时出错: {e}")
            return False

    try:
        cookie_manager = get_cookie_manager(logger)
        cookie_content = cookie_manager.get_cookie_content()
        
        if not cookie_content:
            return False
        
        result = await check_with_playwright(cookie_content)
        return result
            
    except Exception as e:
        log.error(f"验证Cookie有效性时出错: {e}")
        return False


def verify_cookie_validity(logger: Optional[logging.Logger] = None, disable_resources: bool = True):
    """
    同步验证Cookie的有效性（仅用于同步环境）
    使用无头浏览器访问搜索页面来检查Cookie是否有效
    返回: True表示Cookie有效，False表示Cookie无效
    
    Args:
        logger: 可选的日志器
        disable_resources: 是否禁用CSS加载以提高速度，默认True
        
    Returns:
        bool: Cookie是否有效
    """
    log = logger or logging.getLogger(__name__)
    
    try:
        cookie_manager = get_cookie_manager(logger)
        cookie_content = cookie_manager.get_cookie_content()
        
        if not cookie_content:
            return False
        
        result = asyncio.run(verify_cookie_validity_async(logger, disable_resources))
        return result
            
    except Exception as e:
        log.error(f"验证Cookie有效性时出错: {e}")
        return False


def get_cookies() -> Optional[str]:
    """
    获取Cookie内容的便捷函数
    
    Returns:
        Optional[str]: Cookie内容，如果不存在则返回None
    """
    cookie_manager = get_cookie_manager()
    return cookie_manager.get_cookie_content() 