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
            print("### 登录成功后会自动收集Cookie，无需手动操作。 ###")
            print("#"*60 + "\n")

            # 监听页面跳转到指定地址
            target_url_pattern = 'https://xyq.cbg.163.com/cgi-bin/query.py?act=recommend_search'
            
            # 等待页面跳转到目标地址或登录成功标志
            try:
                # 使用更灵活的URL匹配模式
                await page.wait_for_url(lambda url: target_url_pattern in url, timeout=300000)  # 5分钟超时
                current_url = page.url
                logger.info(f"检测到页面跳转到目标地址: {current_url}")
            except Exception as e:
                logger.warning(f"等待页面跳转超时或失败: {e}")
                # 如果超时，检查当前URL是否包含目标模式
                current_url = page.url
                if target_url_pattern in current_url:
                    logger.info("当前页面已经是目标地址，继续处理")
                else:
                    # 尝试检测登录成功标志
                    try:
                        # 检查是否存在登录成功的元素或标志
                        login_success = await page.evaluate("""
                            () => {
                                // 检查是否存在登录成功的标志
                                const loginElements = document.querySelectorAll('[class*="login"], [class*="user"], [class*="avatar"]');
                                const hasLoginInfo = window.LoginInfo && Object.keys(window.LoginInfo).length > 0;
                                return loginElements.length > 0 || hasLoginInfo;
                            }
                        """)
                        if login_success:
                            logger.info("检测到登录成功标志，继续收集Cookie")
                        else:
                            logger.warning("页面未跳转到目标地址且未检测到登录成功标志，但继续尝试收集Cookie")
                    except Exception as eval_error:
                        logger.warning(f"检测登录状态失败: {eval_error}")
                        logger.warning("页面未跳转到目标地址，但继续尝试收集Cookie")

            # 等待页面完全加载
            await page.wait_for_load_state('networkidle', timeout=10000)
            logger.info("页面加载完成，开始收集Cookie...")

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