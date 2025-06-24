import asyncio
from playwright.async_api import async_playwright
import os
import logging
import json

# 获取一个logger实例
logger = logging.getLogger(__name__)

async def _update_cookies_internal():
    """
    使用Playwright启动浏览器，让用户登录并获取Cookie和LoginInfo。
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

            # 收集 cookies
            cookies = await context.cookies()
            cookie_str = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

            # 收集 window.LoginInfo 对象
            login_info = None
            try:
                login_info = await page.evaluate("() => window.LoginInfo")
                if login_info:
                    logger.info("成功获取到 window.LoginInfo 对象")
                else:
                    logger.warning("window.LoginInfo 对象为空或不存在")
            except Exception as e:
                logger.warning(f"获取 window.LoginInfo 失败: {e}")

            # 找到项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # 保存 cookies
            cookie_path = os.path.join(project_root, 'config', 'cookies.txt')
            os.makedirs(os.path.dirname(cookie_path), exist_ok=True)
            with open(cookie_path, 'w', encoding='utf-8') as f:
                f.write(cookie_str)
            logger.info(f"Cookie已成功更新并保存到 {cookie_path}")

            # 保存 LoginInfo
            if login_info:
                login_info_path = os.path.join(project_root, 'web', 'public', 'assets', 'loginInfo.js')
                os.makedirs(os.path.dirname(login_info_path), exist_ok=True)
                
                # 生成 JavaScript 文件内容
                js_content = f"// 自动生成的登录信息文件\n// 生成时间: {asyncio.get_event_loop().time()}\n\nwindow.LoginInfo = {json.dumps(login_info, ensure_ascii=False, indent=2)};\n"
                
                with open(login_info_path, 'w', encoding='utf-8') as f:
                    f.write(js_content)
                logger.info(f"LoginInfo已成功保存到 {login_info_path}")
            else:
                logger.warning("未能获取到有效的 LoginInfo 数据，跳过保存")

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