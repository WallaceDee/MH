import asyncio
from playwright.async_api import async_playwright
import os
import time

async def wait_for_cookies(page, timeout=30):
    """等待必要的cookies加载完成"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        cookies = await page.context.cookies()
        # 检查是否包含必要的cookies
        cookie_names = {cookie['name'] for cookie in cookies}
        if 'cbg_qrcode' in cookie_names and 'login_id' in cookie_names:
            return True
        await asyncio.sleep(1)
    return False

async def main():
    async with async_playwright() as p:
        # 启动 Chromium 浏览器
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        # 打开藏宝阁登录页
        url = 'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py?act=show_search_role_form'
        await page.goto(url)

        print('请在打开的浏览器窗口中手动登录，登录完成后回到这里按回车...')
        input()

        # 等待cookies加载完成
        print('等待cookies加载完成...')
        if not await wait_for_cookies(page):
            print('警告：等待cookies超时，可能未获取到所有必要的cookies')

        # 获取cookies
        cookies = await context.cookies()
        cookie_str = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

        # 确保 config 目录存在
        os.makedirs('config', exist_ok=True)
        
        # 保存到 config/cookies.txt
        with open('config/cookies.txt', 'w', encoding='utf-8') as f:
            f.write(cookie_str)

        print('Cookies已成功保存到 config/cookies.txt')
        await browser.close()

if __name__ == '__main__':
    print("正在启动 Playwright...")
    print("提示：如果是首次运行，请先在终端执行 `pip install playwright` 和 `playwright install` 命令。")
    asyncio.run(main()) 