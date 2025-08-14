import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    # 读取保存的cookies
    cookie_path = os.path.join('config', 'cookies.txt')
    if not os.path.exists(cookie_path):
        print('错误：未找到cookies文件，请先使用爬虫系统的自动cookie更新功能')
        return

    with open(cookie_path, 'r', encoding='utf-8') as f:
        cookie_str = f.read().strip()

    # 解析cookie字符串为字典列表
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

    async with async_playwright() as p:
        # 创建浏览器上下文
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            device_scale_factor=1,
            has_touch=False,
            is_mobile=False,
            color_scheme='light',
            reduced_motion='no-preference',
            forced_colors='none',
            accept_downloads=True
        )

        # 设置 cookies
        await context.add_cookies(cookies)

        # 创建新页面
        page = await context.new_page()

        # 访问藏宝阁
        await page.goto('https://xyq.cbg.163.com/')
        
        print('浏览器已启动，使用保存的cookies访问藏宝阁...')
        print('按回车键退出...')
        input()

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main()) 