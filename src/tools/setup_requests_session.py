import json
import requests
from urllib.parse import urlparse
import os
import asyncio
from playwright.async_api import async_playwright
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_browser_info():
    """获取浏览器信息"""
    async with async_playwright() as p:
        # 启动 Chromium 浏览器
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        # 打开藏宝阁登录页
        url = 'https://xyq.cbg.163.com/cgi-bin/show_login.py?act=show_login&area_id=43&area_name=%E5%B9%BF%E4%B8%9C2%E5%8C%BA&server_id=77&server_name=%E8%BF%9B%E8%B4%A4%E9%97%A8&return_url=https%3A%2F%2Fxyq.cbg.163.com%2Fcgi-bin%2Fxyq_overall_search.py%3Fact%3Dshow_search_role_form'
        await page.goto(url)

        print('请在打开的浏览器窗口中手动登录，登录完成后回到这里按回车...')
        input()

        # 获取浏览器信息
        browser_info = {
            'cookies': await context.cookies(),
            'user_agent': await page.evaluate('() => navigator.userAgent'),
            'viewport': await page.evaluate('() => ({ width: window.innerWidth, height: window.innerHeight })'),
            'platform': await page.evaluate('() => navigator.platform'),
            'language': await page.evaluate('() => navigator.language'),
            'timezone': await page.evaluate('() => Intl.DateTimeFormat().resolvedOptions().timeZone'),
            'screen': await page.evaluate('() => ({ width: screen.width, height: screen.height })'),
            'color_depth': await page.evaluate('() => screen.colorDepth'),
            'device_memory': await page.evaluate('() => navigator.deviceMemory'),
            'hardware_concurrency': await page.evaluate('() => navigator.hardwareConcurrency'),
            'webgl_vendor': await page.evaluate('() => { const canvas = document.createElement("canvas"); const gl = canvas.getContext("webgl"); return gl ? gl.getParameter(gl.VENDOR) : null; }'),
            'webgl_renderer': await page.evaluate('() => { const canvas = document.createElement("canvas"); const gl = canvas.getContext("webgl"); return gl ? gl.getParameter(gl.RENDERER) : null; }')
        }

        # 确保 config 目录存在
        os.makedirs('config', exist_ok=True)
        
        # 保存到 config/browser_info.json
        with open('config/browser_info.json', 'w', encoding='utf-8') as f:
            json.dump(browser_info, f, indent=2, ensure_ascii=False)

        print('浏览器信息已成功保存到 config/browser_info.json')
        await browser.close()
        return browser_info

def setup_session():
    """
    设置一个带有cookies的 requests session
    """
    # 创建新的 session
    session = requests.Session()

    # 设置默认请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'DNT': '1',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://xyq.cbg.163.com/',
        'Origin': 'https://xyq.cbg.163.com'
    }
    session.headers.update(headers)

    # 读取cookies
    try:
        cookie_path = os.path.join('config', 'cookies.txt')
        if not os.path.exists(cookie_path):
            logger.warning("未找到cookies文件，请先使用爬虫系统的自动cookie更新功能")
            return session

        with open(cookie_path, 'r', encoding='utf-8') as f:
            cookie_str = f.read().strip()
            if cookie_str:
                session.headers.update({'Cookie': cookie_str})
                logger.info("成功从config/cookies.txt加载Cookie")
            else:
                logger.warning("config/cookies.txt文件为空")
    except Exception as e:
        logger.error(f"读取config/cookies.txt文件失败: {e}")

    return session

def get_domain_cookies(domain):
    """
    获取指定域名的 cookies
    """
    try:
        with open('config/cookies.txt', 'r', encoding='utf-8') as f:
            cookie_str = f.read().strip()
        
        domain_cookies = []
        for cookie in cookie_str.split('; '):
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                if domain in name or domain in value:
                    domain_cookies.append({'name': name, 'value': value})
        return domain_cookies
    except Exception as e:
        logger.error(f"读取cookies失败: {e}")
        return []

if __name__ == '__main__':
    # 测试代码
    session = setup_session()
    
    # 测试请求
    test_url = 'https://xyq.cbg.163.com/cgi-bin/query.py?act=search_role&server_type=3&search_type=overall_search_role&view_loc=overall_search'
    logger.info(f"发送测试请求到: {test_url}")
    
    try:
        response = session.get(test_url, timeout=30)
        logger.info(f"状态码: {response.status_code}")
        logger.info(f"响应头: {dict(response.headers)}")
        logger.info(f"响应内容长度: {len(response.text)}")
        logger.info(f"响应内容前200字符: {response.text[:200]}")
        logger.info(f"Cookies: {[{'name': c.name, 'value': c.value, 'domain': c.domain} for c in session.cookies]}")
    except Exception as e:
        logger.error(f"请求失败: {str(e)}") 