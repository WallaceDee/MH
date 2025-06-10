import asyncio
from playwright.async_api import async_playwright
import os
import logging

# 获取一个logger实例
logger = logging.getLogger(__name__)

async def _update_cookies_internal():
    """
    使用Playwright启动浏览器，让用户登录并获取Cookie。
    """
    try:
        async with async_playwright() as p:
            logger.info("启动浏览器以更新Cookie...")
            try:
                browser = await p.chromium.launch(headless=False)
            except Exception:
                logger.info("未找到默认浏览器，尝试安装Playwright浏览器驱动...")
                logger.info("请在终端中运行: playwright install")
                # 提示用户手动安装
                print("\n" + "="*50)
                print("!! Playwright浏览器驱动未安装 !!")
                print("请打开一个新的终端，然后运行以下命令:")
                print("pip install playwright")
                print("playwright install")
                print("="*50 + "\n")
                input("安装完成后，请按回车键继续...")
                # 再次尝试启动
                browser = await p.chromium.launch(headless=False)

            context = await browser.new_context()
            page = await context.new_page()

            url = 'https://xyq.cbg.163.com/'
            await page.goto(url)

            print("\n" + "#"*60)
            print("### 请在弹出的浏览器窗口中手动登录您的藏宝阁账号。 ###")
            print("### 登录成功后，回到此控制台窗口，按 Enter/回车键。 ###")
            print("#"*60 + "\n")
            input("登录完成后请按 Enter/回车键继续...")

            cookies = await context.cookies()
            cookie_str = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

            # 找到项目根目录下的 config/cookies.txt
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            cookie_path = os.path.join(project_root, 'config', 'cookies.txt')
            
            os.makedirs(os.path.dirname(cookie_path), exist_ok=True)
            with open(cookie_path, 'w', encoding='utf-8') as f:
                f.write(cookie_str)

            logger.info(f"Cookie已成功更新并保存到 {cookie_path}")
            await browser.close()
            return True
    except Exception as e:
        logger.error(f"使用Playwright更新Cookie时发生错误: {e}")
        return False

def update_cookies_with_playwright():
    """
    同步包装器，以便在非async代码中调用。
    """
    logger.info("检测到登录失效，正在启动Cookie更新程序...")
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果事件循环已在运行，则在其中创建任务
            task = loop.create_task(_update_cookies_internal())
            # 在同步代码中等待异步任务完成不是最佳实践，但在这种特定场景下，
            # 为了集成，这是一个可行的解决方案。
            # 这会阻塞，直到任务完成。
            return loop.run_until_complete(task)
        else:
            return asyncio.run(_update_cookies_internal())
    except RuntimeError: # 如果没有正在运行的事件循环
        return asyncio.run(_update_cookies_internal())

if __name__ == '__main__':
    # 用于直接测试此模块
    logging.basicConfig(level=logging.INFO)
    update_cookies_with_playwright() 