import asyncio
from playwright.async_api import async_playwright
import logging
import json
import os

logger = logging.getLogger(__name__)

async def collect_search_params():
    """
    使用 Playwright 打开搜索表单页面并收集搜索参数
    返回: 收集到的搜索参数列表
    """
    try:
        # 读取cookies
        cookie_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'cookies.txt')
        if not os.path.exists(cookie_path):
            logger.error("未找到cookies文件，请先运行 get_cbg_cookies.py 获取cookies")
            return None

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
            # 启动浏览器
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
            
            # 设置 cookies
            await context.add_cookies(cookies)
            
            # 创建新页面
            page = await context.new_page()
            
            # 存储收集到的参数
            collected_params = None
            
            # 设置全局请求监听
            async def handle_request(request):
                nonlocal collected_params  # 使用nonlocal而不是global
                if 'https://xyq.cbg.163.com/cgi-bin/recommend.py?' in request.url:
                    try:
                        # 从URL中获取参数
                        url = request.url
                        # 提取URL中的查询参数部分
                        if '?' in url:
                            query_string = url.split('?')[1]
                            # 将查询字符串转换为字典
                            params_dict = {}
                            for param in query_string.split('&'):
                                if '=' in param:
                                    key, value = param.split('=', 1)
                                    params_dict[key] = value
                            if params_dict:
                                collected_params = params_dict
                                # 立即保存参数
                                os.makedirs('config', exist_ok=True)
                                params_file = os.path.join('config', 'search_params.json')
                                with open(params_file, 'w', encoding='utf-8') as f:
                                    json.dump(params_dict, f, ensure_ascii=False, indent=2)
                                logger.info(f"搜索参数已保存到: {params_file}")
                    except Exception as e:
                        logger.error(f"处理请求参数时出错: {e}")

            # 在创建新标签页之前设置监听器
            context.on('request', handle_request)
            
            # 打开搜索表单页面
            url = 'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py?act=show_search_role_form'
            await page.goto(url)
            
            # 设置页面级别的请求监听
            page.on('request', handle_request)
            
            print("\n" + "="*60)
            print("请在打开的浏览器窗口中设置搜索条件并点击搜索")
            print("程序会自动收集搜索参数")
            print("完成后请按回车键继续...")
            print("="*60 + "\n")
            input()
            
            await browser.close()
            return collected_params
            
    except Exception as e:
        logger.error(f"收集搜索参数时发生错误: {e}")
        return None

def get_search_params():
    """
    同步包装器，用于在非异步代码中调用
    """
    return asyncio.run(collect_search_params())

if __name__ == '__main__':
    # 用于直接测试此模块
    logging.basicConfig(level=logging.INFO)
    params = get_search_params()
    if params:
        print(f"收集到的参数: {params}")
    else:
        print("未收集到有效的搜索参数") 