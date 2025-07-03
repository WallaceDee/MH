import asyncio
from playwright.async_api import async_playwright
import logging
import json
import os
import requests
from functools import partial

# 导入cookie更新器（异步版本将在需要时动态导入）

logger = logging.getLogger(__name__)

# --- 默认参数定义 ---

DEFAULT_PARAMS = {
    'normal': {
        'level_min': 60,
        'level_max': 160,
        'search_type': 'overall_search_equip',
        'server_type': 3,
        'count': 15,
        'view_loc': 'overall_search'
    },
    'lingshi': {
        'level_min': 60,
        'level_max': 140,
        'search_type': 'overall_search_lingshi',
        'server_type': 3,
        'count': 15,
        'view_loc': 'overall_search'
    },
    'pet': {
        'level_min': 0,
        'level_max': 180,
        'search_type': 'overall_search_pet',
        'server_type': 3,
        'evol_skill_mode': 0,
        'count': 15,
        'view_loc': 'overall_search'
    },
    'pet_equip': {
        'level_min': 5,
        'level_max': 145,
        'search_type': 'overall_search_pet_equip',
        'server_type': 3,
        'count': 15,
        'view_loc': 'overall_search'
    }
}

# --- 核心逻辑 ---

async def _get_params_async(equip_type: str, use_browser: bool, collector_logic, collector_url: str):
    """
    异步获取参数的核心逻辑。
    1. 如果 use_browser=True，启动浏览器收集。
    2. 如果 use_browser=False，尝试从文件加载。
    3. 如果文件不存在，使用默认参数。
    4. 收集/加载后，保存到文件。
    """
    params_file = os.path.join('config', f'equip_params_{equip_type}.json')

    if use_browser:
        logger.info(f"模式: 浏览器. 启动浏览器为 '{equip_type}' 收集参数.")
        params = await _collect_params_base_async(collector_url, collector_logic)
        if params:
            with open(params_file, 'w', encoding='utf-8') as f:
                json.dump(params, f, ensure_ascii=False, indent=2)
            logger.info(f"参数已保存到 {params_file}")
            return params
        else:
            logger.warning("浏览器收集参数失败。将使用默认参数。")
            return DEFAULT_PARAMS[equip_type]

    # 非浏览器模式
    if os.path.exists(params_file):
        logger.info(f"模式: 本地文件. 从 {params_file} 加载参数.")
        with open(params_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        logger.info(f"模式: 默认. 未找到参数文件，使用默认的 '{equip_type}' 参数.")
        # 保存默认参数以供下次使用
        with open(params_file, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_PARAMS[equip_type], f, ensure_ascii=False, indent=2)
        return DEFAULT_PARAMS[equip_type]

def _get_params_sync(equip_type: str, use_browser: bool, collector_logic, collector_url: str):
    """
    同步获取参数的核心逻辑。
    与异步版本逻辑相同，但使用同步调用。
    """
    params_file = os.path.join('config', f'equip_params_{equip_type}.json')

    if use_browser:
        logger.info(f"模式: 浏览器. 启动浏览器为 '{equip_type}' 收集参数.")
        params = _collect_params_base_sync(collector_url, collector_logic)
        if params:
            with open(params_file, 'w', encoding='utf-8') as f:
                json.dump(params, f, ensure_ascii=False, indent=2)
            logger.info(f"参数已保存到 {params_file}")
            return params
        else:
            logger.warning("浏览器收集参数失败。将使用默认参数。")
            return DEFAULT_PARAMS[equip_type]

    # 非浏览器模式
    if os.path.exists(params_file):
        logger.info(f"模式: 本地文件. 从 {params_file} 加载参数.")
        with open(params_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        logger.info(f"模式: 默认. 未找到参数文件，使用默认的 '{equip_type}' 参数.")
        with open(params_file, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_PARAMS[equip_type], f, ensure_ascii=False, indent=2)
        return DEFAULT_PARAMS[equip_type]


def verify_cookie_validity():
    """
    验证Cookie的有效性
    使用默认参数发送一个测试请求来检查Cookie是否有效
    返回: True表示Cookie有效，False表示Cookie无效
    """
    try:
        # 读取Cookie文件
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cookie_path = os.path.join(project_root, 'config', 'cookies.txt')
        
        if not os.path.exists(cookie_path):
            logger.warning("Cookie文件不存在")
            return False
        
        with open(cookie_path, 'r', encoding='utf-8') as f:
            cookie_str = f.read().strip()
        
        if not cookie_str:
            logger.warning("Cookie文件为空")
            return False
        
        # 使用默认参数发送测试请求，参考cbg_spider.py的参数
        test_url = "https://xyq.cbg.163.com/cgi-bin/recommend.py"
        test_params = {
            'act': 'recommd_by_role',
            'search_type': 'overall_search_role',
            'server_type': 3,
            'page': 1,
            'count': 15,
            'callback': 'Request.JSONP.request_map.request_0',
            '_': str(int(__import__('time').time() * 1000))
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': cookie_str,
            'Referer': 'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py'
        }
        
        response = requests.get(test_url, params=test_params, headers=headers, timeout=10)
        
        # 检查响应内容判断Cookie是否有效
        if response.status_code == 200:
            response_text = response.text
            
            # 解析JSONP响应，参考cbg_spider.py的逻辑
            try:
                # 查找JSONP响应的JSON部分
                start = response_text.find('(') + 1
                end = response_text.rfind(')')
                
                if start <= 0 or end <= 0:
                    logger.warning("响应不是有效的JSONP格式")
                    return False
                    
                json_str = response_text[start:end]
                data = json.loads(json_str)
                
                if not isinstance(data, dict):
                    logger.warning("解析JSONP响应失败：响应不是一个有效的JSON对象")
                    return False
                
                # 检查API响应状态，参考cbg_spider.py的逻辑
                status = data.get('status')
                if status == 1:
                    # status=1表示成功，Cookie有效
                    logger.info("Cookie验证成功")
                    return True
                elif status == 2:
                    # status=2表示登录状态失效，Cookie无效
                    logger.warning("Cookie已失效，需要重新登录 (status=2)")
                    return False
                else:
                    # 其他状态码也认为Cookie无效
                    msg = data.get('msg', 'N/A')
                    logger.warning(f"API返回错误状态: {status}, 消息: {msg}")
                    return False
                    
            except json.JSONDecodeError as e:
                logger.warning(f"解析JSON响应失败: {e}")
                return False
            except Exception as e:
                logger.warning(f"解析响应时出错: {e}")
                return False
        else:
            logger.warning(f"Cookie验证请求失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"验证Cookie有效性时出错: {e}")
        return False

async def _collect_params_base_async(url, collector_logic):
    """参数收集的基础函数 (异步)"""
    try:
        # Cookie 验证和准备
        logger.info("正在验证Cookie有效性...")
        if not verify_cookie_validity():
            logger.warning("Cookie验证失败，正在更新Cookie...")
            from ..utils.cookie_updater import _update_cookies_internal
            if not await _update_cookies_internal():
                logger.error("Cookie更新失败，无法继续")
                return None
        else:
            logger.info("Cookie验证通过")
        
        cookie_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'cookies.txt')
        with open(cookie_path, 'r', encoding='utf-8') as f:
            cookie_str = f.read().strip()
        cookies = [{'name': c.split('=', 1)[0], 'value': c.split('=', 1)[1], 'domain': '.163.com', 'path': '/'} for c in cookie_str.split('; ') if '=' in c]

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
            await context.add_cookies(cookies)
            page = await context.new_page()
            
            logger.info(f"正在打开页面: {url}")
            await page.goto(url, wait_until='networkidle')
            logger.info("页面加载完成。")

            
            print("\n" + "="*60)
            print("请在打开的浏览器窗口中设置搜索条件并点击搜索按钮")
            print("点击搜索后，请回到控制台按回车键继续...")
            print("="*60 + "\n")
            await asyncio.to_thread(input, "设置完搜索条件并点击搜索后，请按回车键...")
            
            params_dict = await collector_logic(page) # 调用特定的收集逻辑
            
            await browser.close()
            
            if params_dict:
                print(f"✅ 搜索参数收集成功！")
            
            return params_dict
            
    except Exception as e:
        logger.error(f"收集搜索参数时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def _collect_params_base_sync(url, collector_logic):
    """参数收集的基础函数 (同步)"""
    return asyncio.run(_collect_params_base_async(url, collector_logic))


async def _collect_lingshi_logic(page):
    """灵饰参数收集的具体逻辑 - 直接模拟原始JavaScript逻辑"""
    params_dict = {}
    
    print("🚀 开始收集灵饰参数...")
    
    # 1. 等级范围参数 - 从LevelSlider对象获取
    try:
        # 按照原JS逻辑：arg['equip_level_min'] = this.level_slider.value.min;
        level_values = await page.evaluate('''
            () => {
                if (window.OverallLingshiSearcher && window.OverallLingshiSearcher.level_slider && window.OverallLingshiSearcher.level_slider.value) {
                    return {
                        min: window.OverallLingshiSearcher.level_slider.value.min,
                        max: window.OverallLingshiSearcher.level_slider.value.max
                    };
                }
                return { min: 60, max: 160 };  // 默认值
            }
        ''')
        
        params_dict['equip_level_min'] = level_values['min']
        params_dict['equip_level_max'] = level_values['max']
        print(f"✅ 等级范围: {level_values['min']}-{level_values['max']}")
    except Exception as e:
        print(f"❌ 获取等级范围参数失败: {e}")
        params_dict['equip_level_min'] = 60
        params_dict['equip_level_max'] = 160
    
    # 2. 收集各种选择器参数
    check_panels = [
        ['pass_fair_show', 'fair_show_panel', True],
        ['server_type', 'server_type_panel', True],
        ['kindid', 'kind_panel', True],
        ['added_attr_num', 'added_attr_num_panel', False],
        ['added_attr_repeat_num', 'added_attr_repeat_num_panel', False]
    ]
    
    for param_name, panel_id, check_all_skip in check_panels:
        try:
            value = await page.evaluate(f'''
                () => {{
                    const panel = document.getElementById('{panel_id}');
                    if (!panel) return null;
                    
                    // 查找带有'on'类的li元素（ButtonChecker的选中标识）
                    const liElements = panel.querySelectorAll('li');
                    const selectedValues = [];
                    
                    for (let li of liElements) {{
                        if (li.classList.contains('on')) {{
                            // 获取文本内容
                            let text = '';
                            const span = li.querySelector('span');
                            if (span) {{
                                text = span.textContent.trim();
                            }}
                            
                            // 根据参数类型进行转换
                            let value = text;
                            if ('{param_name}' === 'kindid' && window.Kinds) {{
                                for (let item of window.Kinds) {{
                                    if (item[1] === text) {{
                                        value = item[0];
                                        break;
                                    }}
                                }}
                            }} else if ('{param_name}' === 'server_type' && window.ServerTypes) {{
                                for (let item of window.ServerTypes) {{
                                    if (item[1] === text) {{
                                        value = item[0];
                                        break;
                                    }}
                                }}
                            }} else if ('{param_name}' === 'pass_fair_show' && window.FairShowStatus) {{
                                for (let item of window.FairShowStatus) {{
                                    if (item[1] === text) {{
                                        value = item[0];
                                        break;
                                    }}
                                }}
                            }} else if ('{param_name}' === 'added_attr_num' || '{param_name}' === 'added_attr_repeat_num') {{
                                // 附加属性条数直接使用数字
                                value = text.replace('条', '');
                            }}
                            
                            selectedValues.push(value);
                        }}
                    }}
                    
                    // 检查是否全选（需要跳过的情况）
                    if ({str(check_all_skip).lower()}) {{
                        const totalItems = liElements.length;
                        if (selectedValues.length === totalItems) {{
                            return null;  // 全选时跳过
                        }}
                    }}
                    
                    return selectedValues.length > 0 ? selectedValues.join(',') : null;
                }}
            ''')
            
            if value:
                params_dict[param_name] = value
                print(f"✅ {param_name}: {value}")
            else:
                print(f"⚠️ {param_name}: 无选择")
        except Exception as e:
            print(f"❌ 获取{param_name}参数失败: {e}")
    
    # 3. 附加属性逻辑
    try:
        # 获取附加属性逻辑选择
        added_attr_logic = await page.evaluate('''
            () => {
                const checkedRadio = document.querySelector('input[name="added_attr_logic"]:checked');
                return checkedRadio ? checkedRadio.value : null;
            }
        ''')
        
        if added_attr_logic:
            params_dict['added_attr_logic'] = added_attr_logic
            print(f"✅ 附加属性逻辑: {added_attr_logic}")
            
            # 根据逻辑类型处理附加属性
            if added_attr_logic == 'detail':
                # 详细属性模式
                for i in range(1, 4):
                    attr_value = await page.evaluate(f'''
                        () => {{
                            const select = document.getElementById('sel_add_attr{i}');
                            return select ? select.value : '';
                        }}
                    ''')
                    if attr_value:
                        key = f'added_attr.{attr_value}'
                        params_dict[key] = (params_dict.get(key, 0) + 1)
                        print(f"✅ 详细附加属性{i}: {attr_value}")
            else:
                # 简单模式 - 收集两个面板的附加属性
                added_attr_values = await page.evaluate('''
                    () => {
                        const panel1 = document.getElementById('added_attr1_panel');
                        const panel2 = document.getElementById('added_attr2_panel');
                        const selectedValues = [];
                        
                        [panel1, panel2].forEach(panel => {
                            if (panel) {
                                const liElements = panel.querySelectorAll('li.on');
                                liElements.forEach(li => {
                                    const span = li.querySelector('span');
                                    if (span) {
                                        const text = span.textContent.trim();
                                        // 根据文本找到对应的数值
                                        if (window.AddedAttr1) {
                                            for (let item of window.AddedAttr1) {
                                                if (item[1] === text) {
                                                    selectedValues.push(item[0]);
                                                    break;
                                                }
                                            }
                                        }
                                        if (window.AddedAttr2) {
                                            for (let item of window.AddedAttr2) {
                                                if (item[1] === text) {
                                                    selectedValues.push(item[0]);
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                });
                            }
                        });
                        
                        return selectedValues;
                    }
                ''')
                
                for attr_value in added_attr_values:
                    key = f'added_attr.{attr_value}'
                    params_dict[key] = 1
                    print(f"✅ 附加属性: {attr_value}")
        else:
            print("⚠️ 附加属性逻辑: 无选择")
    except Exception as e:
        print(f"❌ 获取附加属性逻辑参数失败: {e}")
    
    # 4. 特效
    try:
        if await page.evaluate('() => document.getElementById("chk_has_eazy_effect")?.checked'):
            params_dict['special_effect'] = 1
            print("✅ 特效: 超级简易")
        else:
            print("⚠️ 特效: 无选择")
    except Exception as e:
        print(f"❌ 获取特效参数失败: {e}")
    
    # 5. 收集数值输入参数 - 完全按照原始JavaScript逻辑
    txt_int_items = [
        ['basic_attr_value', 0, 10000, '技能数量'],
        ['price_min', 0, 99999, '价格'],
        ['price_max', 0, 99999, '价格'],
        ['jinglian_level', 0, 16, '精炼等级'],
        ['suit_effect_level', 0, 99, '套装等级']
    ]
    
    for item_name, min_val, max_val, desc in txt_int_items:
        try:
            value = await page.evaluate(f'''
                () => {{
                    const el = document.getElementById('txt_{item_name}');
                    return el ? el.value : '';
                }}
            ''')
            
            if value:
                # 验证整数格式
                if not value.isdigit():
                    print(f"❌ {desc}必须是整数: {value}")
                    continue
                
                int_value = int(value)
                if not (min_val <= int_value <= max_val):
                    print(f"❌ {desc}超出取值范围 {min_val}-{max_val}: {int_value}")
                    continue
                
                params_dict[item_name] = int_value
                print(f"✅ {desc}: {int_value}")
            else:
                print(f"⚠️ {desc}: 无值")
        except Exception as e:
            print(f"❌ 获取{item_name}参数失败: {e}")
    
    # 6. 基础属性类型和值
    try:
        basic_attr_type = await page.evaluate('''
            () => {
                const select = document.getElementById('sel_basic_attr_type');
                return select ? select.value : '';
            }
        ''')
        
        if basic_attr_type:
            params_dict[basic_attr_type] = params_dict.get('basic_attr_value', 1)
            print(f"✅ 基础属性类型: {basic_attr_type}")
        else:
            print("⚠️ 基础属性类型: 无选择")
    except Exception as e:
        print(f"❌ 获取基础属性类型参数失败: {e}")
    
    # 7. 综合属性
    try:
        synthesized_attr_type = await page.evaluate('''
            () => {
                const select = document.getElementById('synthesized_attr_type');
                return select ? select.value : '';
            }
        ''')
        
        if synthesized_attr_type:
            synthesized_attr_value = await page.evaluate('''
                () => {
                    const input = document.getElementById('txt_synthesized_attr_value');
                    return input ? input.value : '1';
                }
            ''')
            
            params_dict['synthesized_attr_total'] = {
                synthesized_attr_type: synthesized_attr_value or "1"
            }
            print(f"✅ 综合属性: {synthesized_attr_type} = {synthesized_attr_value}")
        else:
            print("⚠️ 综合属性: 无选择")
    except Exception as e:
        print(f"❌ 获取综合属性参数失败: {e}")
    
    # 8. 修理失败次数
    try:
        repair_fail = await page.evaluate('''
            () => {
                const input = document.getElementById('txt_repair_fail');
                return input ? input.value : '';
            }
        ''')
        
        if repair_fail:
            if not repair_fail.isdigit() or int(repair_fail) > 3:
                print(f"❌ 修理失败取值范围是0~3的整数: {repair_fail}")
            else:
                params_dict['repair_fail'] = int(repair_fail)
                print(f"✅ 修理失败次数: {repair_fail}")
        else:
            print("⚠️ 修理失败次数: 无值")
    except Exception as e:
        print(f"❌ 获取修理失败参数失败: {e}")
    
    # 9. 套装效果
    try:
        suit_effect = await page.evaluate('''
            () => {
                const select = document.getElementById('sel_suit_effect');
                return select ? select.value : '';
            }
        ''')
        
        if suit_effect:
            params_dict['suit_effect'] = suit_effect
            print(f"✅ 套装效果: {suit_effect}")
        else:
            print("⚠️ 套装效果: 无选择")
    except Exception as e:
        print(f"❌ 获取套装效果参数失败: {e}")
    
    # 10. 价格处理（原JS: if (arg['price_min']) arg['price_min'] = arg['price_min'] * 100;）
    if 'price_min' in params_dict: 
        params_dict['price_min'] *= 100
        print(f"  价格转换: price_min *= 100 = {params_dict['price_min']}")
    if 'price_max' in params_dict: 
        params_dict['price_max'] *= 100
        print(f"  价格转换: price_max *= 100 = {params_dict['price_max']}")
    
    # 11. 服务器相关
    try:
        # 指定服务器
        serverid = await page.evaluate('''
            () => {
                if (window.OverallLingshiSearcher && window.OverallLingshiSearcher.select_server) {
                    return window.OverallLingshiSearcher.select_server.get_serverid();
                }
                return null;
            }
        ''')
        if serverid: 
            params_dict['serverid'] = serverid
            print(f"✅ 服务器ID: {serverid}")
        else:
            print("⚠️ 服务器ID: 无值")
    except Exception as e:
        print(f"❌ 获取服务器ID参数失败: {e}")
    
    # 跨服购买服务器ID
    try:
        cross_buy_serverid = await page.evaluate("() => document.getElementById('user_serverid')?.value || ''")
        if cross_buy_serverid: 
            params_dict['cross_buy_serverid'] = cross_buy_serverid
            print(f"✅ 跨服购买服务器ID: {cross_buy_serverid}")
        else:
            print("⚠️ 跨服购买服务器ID: 无值")
    except Exception as e:
        print(f"❌ 获取跨服购买服务器ID参数失败: {e}")
    
    # 12. 清理临时参数
    if 'basic_attr_value' in params_dict:
        del params_dict['basic_attr_value']
    
    print(f"\n📊 灵饰参数收集完成，共获取 {len(params_dict)} 个参数:")
    for key, value in params_dict.items():
        print(f"  {key}: {value}")
    
    return params_dict

async def _collect_pet_equip_logic(page):
    """收集召唤兽装备搜索逻辑"""
    params_dict = {}
    
    # 基础等级范围
    level_min = await page.evaluate('() => document.getElementById("txt_level_min")?.value')
    if level_min: params_dict['level_min'] = level_min

    level_max = await page.evaluate('() => document.getElementById("txt_level_max")?.value')
    if level_max: params_dict['level_max'] = level_max

    # 价格范围
    price_min = await page.evaluate('() => document.getElementById("txt_price_min")?.value')
    if price_min: params_dict['price_min'] = price_min

    price_max = await page.evaluate('() => document.getElementById("txt_price_max")?.value')
    if price_max: params_dict['price_max'] = price_max
    
    # 前端状态
    if await page.evaluate('() => document.getElementById("front_status_pass_fair_show")?.checked'):
        params_dict['front_status'] = 'pass_fair_show'
    elif await page.evaluate('() => document.getElementById("front_status_fair_show")?.checked'):
        params_dict['front_status'] = 'fair_show'
    
    return params_dict

async def _collect_pet_logic(page):
    """收集召唤兽搜索逻辑"""
    params_dict = {}
    
    # 基础等级范围
    level_min = await page.evaluate('() => document.getElementById("txt_level_min")?.value')
    if level_min: params_dict['level_min'] = level_min

    level_max = await page.evaluate('() => document.getElementById("txt_level_max")?.value')
    if level_max: params_dict['level_max'] = level_max

    # 价格范围
    price_min = await page.evaluate('() => document.getElementById("txt_price_min")?.value')
    if price_min: params_dict['price_min'] = price_min

    price_max = await page.evaluate('() => document.getElementById("txt_price_max")?.value')
    if price_max: params_dict['price_max'] = price_max
    
    # 宠物类型
    pet_type = await page.evaluate('() => document.getElementById("pet_select_box")?.value')
    if pet_type: params_dict['pet_type'] = pet_type
    
    # 技能数量
    skill_num = await page.evaluate('() => document.getElementById("txt_skill_num")?.value')
    if skill_num: params_dict['skill_num'] = skill_num
    
    # 成长值
    growth = await page.evaluate('() => document.getElementById("txt_growth")?.value')
    if growth: params_dict['growth'] = growth
    
    # 已使用炼兽珍经数量
    used_lianshou_max = await page.evaluate('() => document.getElementById("txt_used_lianshou_max")?.value')
    if used_lianshou_max: params_dict['used_lianshou_max'] = used_lianshou_max
    
    # 已使用元宵数量
    used_yuanxiao_max = await page.evaluate('() => document.getElementById("txt_used_yuanxiao_max")?.value')
    if used_yuanxiao_max: params_dict['used_yuanxiao_max'] = used_yuanxiao_max
    
    # 有效赐福技能数
    valid_evol_skill_num = await page.evaluate('() => document.getElementById("txt_valid_evol_skill_num")?.value')
    if valid_evol_skill_num: params_dict['valid_evol_skill_num'] = valid_evol_skill_num
    
    # 资质范围
    attack_aptitude = await page.evaluate('() => document.getElementById("txt_attack_aptitude")?.value')
    if attack_aptitude: params_dict['attack_aptitude'] = attack_aptitude
    
    defence_aptitude = await page.evaluate('() => document.getElementById("txt_defence_aptitude")?.value')
    if defence_aptitude: params_dict['defence_aptitude'] = defence_aptitude
    
    physical_aptitude = await page.evaluate('() => document.getElementById("txt_physical_aptitude")?.value')
    if physical_aptitude: params_dict['physical_aptitude'] = physical_aptitude
    
    magic_aptitude = await page.evaluate('() => document.getElementById("txt_magic_aptitude")?.value')
    if magic_aptitude: params_dict['magic_aptitude'] = magic_aptitude
    
    speed_aptitude_min = await page.evaluate('() => document.getElementById("txt_speed_aptitude_min")?.value')
    if speed_aptitude_min: params_dict['speed_aptitude_min'] = speed_aptitude_min
    
    speed_aptitude_max = await page.evaluate('() => document.getElementById("txt_speed_aptitude_max")?.value')
    if speed_aptitude_max: params_dict['speed_aptitude_max'] = speed_aptitude_max
    
    # 属性
    max_blood = await page.evaluate('() => document.getElementById("txt_max_blood")?.value')
    if max_blood: params_dict['max_blood'] = max_blood
    
    attack = await page.evaluate('() => document.getElementById("txt_attack")?.value')
    if attack: params_dict['attack'] = attack
    
    defence = await page.evaluate('() => document.getElementById("txt_defence")?.value')
    if defence: params_dict['defence'] = defence
    
    speed_min = await page.evaluate('() => document.getElementById("txt_speed_min")?.value')
    if speed_min: params_dict['speed_min'] = speed_min
    
    speed_max = await page.evaluate('() => document.getElementById("txt_speed_max")?.value')
    if speed_max: params_dict['speed_max'] = speed_max
    
    lingxing = await page.evaluate('() => document.getElementById("txt_lingxing")?.value')
    if lingxing: params_dict['lingxing'] = lingxing
    
    # 法伤法防
    fashang = await page.evaluate('() => document.getElementById("txt_fashang")?.value')
    if fashang: params_dict['fashang'] = fashang
    
    fafang = await page.evaluate('() => document.getElementById("txt_fafang")?.value')
    if fafang: params_dict['fafang'] = fafang
    
    # 复选框
    if await page.evaluate('() => document.getElementById("chk_is_baobao")?.checked'):
        params_dict['is_baobao'] = 1
    
    if await page.evaluate('() => document.getElementById("chk_summon_color")?.checked'):
        params_dict['summon_color'] = 1
    
    if await page.evaluate('() => document.getElementById("no_include_sp_skill")?.checked'):
        params_dict['no_include_sp_skill'] = 1
    
    if await page.evaluate('() => document.getElementById("chk_advanced_evol_skill")?.checked'):
        params_dict['advanced_evol_skill'] = 1
    
    # 前端状态
    if await page.evaluate('() => document.getElementById("front_status_pass_fair_show")?.checked'):
        params_dict['front_status'] = 'pass_fair_show'
    elif await page.evaluate('() => document.getElementById("front_status_fair_show")?.checked'):
        params_dict['front_status'] = 'fair_show'
    
    # 服务器类型
    server_type_3 = await page.evaluate('() => document.getElementById("server_type_3")?.checked')
    server_type_2 = await page.evaluate('() => document.getElementById("server_type_2")?.checked')
    server_type_1 = await page.evaluate('() => document.getElementById("server_type_1")?.checked')
    
    if server_type_3:
        params_dict['server_type'] = 3
    elif server_type_2:
        params_dict['server_type'] = 2
    elif server_type_1:
        params_dict['server_type'] = 1
    
    # 内丹等级
    high_neidan_level = await page.evaluate('() => document.getElementById("txt_high_neidan_level")?.value')
    if high_neidan_level: params_dict['high_neidan_level'] = high_neidan_level
    
    low_neidan_level = await page.evaluate('() => document.getElementById("txt_low_neidan_level")?.value')
    if low_neidan_level: params_dict['low_neidan_level'] = low_neidan_level
    
    return params_dict

async def _collect_normal_equip_logic(page):
    """普通装备参数收集的具体逻辑 - 直接模拟原始JavaScript逻辑"""
    params_dict = {}
    
    print("🚀 开始收集参数...")
    

    
    # 1. 等级范围参数 - 从LevelSlider对象获取
    try:
        # 按照原JS逻辑：arg['level_min'] = this.level_slider.value.min;
        level_values = await page.evaluate('''
            () => {
                if (window.OverallEquipSearcher && window.OverallEquipSearcher.level_slider && window.OverallEquipSearcher.level_slider.value) {
                    return {
                        min: window.OverallEquipSearcher.level_slider.value.min,
                        max: window.OverallEquipSearcher.level_slider.value.max
                    };
                }
                return { min: 60, max: 160 };  // 默认值
            }
        ''')
        
        params_dict['level_min'] = level_values['min']
        params_dict['level_max'] = level_values['max']
        print(f"✅ 等级范围: {level_values['min']}-{level_values['max']}")
    except Exception as e:
        print(f"❌ 获取等级范围参数失败: {e}")
        params_dict['level_min'] = 60
        params_dict['level_max'] = 160
    
    # 2. 收集各种选择器参数
    check_panels = [
        ['kindid', 'kind_check_panel', True],
        ['special_effect', 'special_effect_panel', False], 
        ['special_skill', 'special_skill_panel', False],
        ['front_status', 'fair_show_panel', True],
        ['server_type', 'server_type_panel', True],
        ['gem_value', 'gem_panel', False],
        ['produce_from', 'produce_from_panel', True]
    ]
    
    for param_name, panel_id, skip_all in check_panels:
        try:
            # 查找带有'on'类的li元素，并使用window字典转换值
            selected_values = await page.evaluate(f'''
            () => {{
                    const panel = document.getElementById('{panel_id}');
                    if (!panel) return null;
                    
                    // 查找所有li元素
                    const liElements = panel.querySelectorAll('li');
                    if (liElements.length === 0) return null;
                    
                    // 查找带有'on'类的li元素（ButtonChecker的选中标识）
                    const checkedLis = [];
                    liElements.forEach(li => {{
                        if (li.classList.contains('on')) {{
                            checkedLis.push(li);
                        }}
                    }});
                    
                    if (checkedLis.length === 0) return null;
                    
                    // 如果是需要跳过全选的类型，检查是否全选
                    if ({str(skip_all).lower()}) {{
                        if (checkedLis.length === liElements.length) {{
                            return 'all_checked';  // 全选标记
                        }}
                    }}
                    
                    // 收集选中li元素的值，使用window上的字典进行转换
                    const values = [];
                    checkedLis.forEach(li => {{
                        // 先获取文本内容
                        let text = '';
                        const span = li.querySelector('span');
                        if (span) {{
                            text = span.textContent.trim();
                        }}
                        
                        // 根据参数类型使用对应的字典转换
                        let value = text;
                        if ('{param_name}' === 'kindid' && window.EquipKinds) {{
                            for (let item of window.EquipKinds) {{
                                if (item[1] === text) {{
                                    value = item[0];
                                    break;
                                }}
                            }}
                        }} else if ('{param_name}' === 'special_effect' && window.SpecialEffects) {{
                            for (let item of window.SpecialEffects) {{
                                if (item[1] === text) {{
                                    value = item[0];
                                    break;
                                }}
                            }}
                        }} else if ('{param_name}' === 'special_skill' && window.SpecialSkills) {{
                            for (let item of window.SpecialSkills) {{
                                if (item[1] === text) {{
                                    value = item[0];
                                    break;
                                }}
                            }}
                        }} else if ('{param_name}' === 'gem_value' && window.Gems) {{
                            for (let item of window.Gems) {{
                                if (item[1] === text) {{
                                    value = item[0];
                                    break;
                                }}
                            }}
                        }} else if ('{param_name}' === 'server_type' && window.ServerTypes) {{
                            for (let item of window.ServerTypes) {{
                                if (item[1] === text) {{
                                    value = item[0];
                                    break;
                                }}
                            }}
                        }} else if ('{param_name}' === 'front_status' && window.FrontStatus) {{
                            for (let item of window.FrontStatus) {{
                                if (item[1] === text) {{
                                    value = item[0];
                                    break;
                                }}
                            }}
                        }} else if ('{param_name}' === 'produce_from' && window.ProduceFroms) {{
                            for (let item of window.ProduceFroms) {{
                                if (item[1] === text) {{
                                    value = item[0];
                                    break;
                                }}
                            }}
                        }}
                        
                        if (value) values.push(value);
                    }});
                    
                    return values.length > 0 ? values.join(',') : null;
            }}
        ''')
            
            if selected_values == 'all_checked':
                print(f"⚠️ {param_name}: 全选，跳过")
                continue
            elif selected_values:
                params_dict[param_name] = selected_values
                print(f"✅ {param_name}: {selected_values}")
            else:
                print(f"⚠️ {param_name}: 无选择")
                
        except Exception as e:
            print(f"❌ 获取 {param_name} 参数失败: {e}")
            continue
    
    # 3. 特效模式
    if 'special_effect' in params_dict:
        try:
            check_mode = await page.evaluate('''
                () => {
                    // 查找选中的特效模式单选框
                    const checkedRadio = document.querySelector('#check_mode_panel input[type="radio"]:checked');
                    return checkedRadio ? checkedRadio.value : 'and';
                }
            ''')
            params_dict['special_mode'] = check_mode
            print(f"✅ 特效模式: {check_mode}")
        except Exception as e:
            print(f"❌ 获取特效模式参数失败: {e}")
            params_dict['special_mode'] = 'and'
    
    # 4. 属性总和类型
    try:
        sum_attr_type = await page.evaluate('''
            () => {
                const panel = document.getElementById('sum_attr_panel');
                if (!panel) return null;
                
                // 查找带有'on'类的li元素（ButtonChecker的选中标识）
                const liElements = panel.querySelectorAll('li');
                for (let li of liElements) {
                    if (li.classList.contains('on')) {
                        // 获取文本内容
                        let text = '';
                        const span = li.querySelector('span');
                        if (span) {
                            text = span.textContent.trim();
                        }
                        
                        // 使用window.SumAttrs字典转换
                        let value = text;
                        if (window.SumAttrs) {
                            for (let item of window.SumAttrs) {
                                if (item[1] === text) {
                                    value = item[0];
                                    break;
                                }
                            }
                        }
                        
                        return value;
                    }
                }
                
                return null;
            }
        ''')
        if sum_attr_type:
            params_dict['sum_attr_type'] = sum_attr_type
            print(f"✅ 属性总和类型: {sum_attr_type}")
        else:
            print("⚠️ 属性总和类型: 无选择")
    except Exception as e:
        print(f"❌ 获取属性总和类型参数失败: {e}")
    
    # 5. 收集数值输入参数 - 完全按照原始JavaScript逻辑
    # 原JS: var txt_int_items = [['init_damage', 0, 10000, '初伤（包含命中）'], ...];
    txt_int_items = [
        ['init_damage', 0, 10000, '初伤（包含命中）'], 
        ['init_damage_raw', 0, 10000, '初伤（不含命中）'], 
        ['all_damage', 0, 10000, '总伤'], 
        ['damage', 0, 10000, '伤害'], 
        ['init_defense', 0, 10000, '初防'], 
        ['init_hp', 0, 10000, '初血'],
        ['init_dex', 0, 10000, '初敏'], 
        ['init_wakan', 0, 10000, '初灵'], 
        ['all_wakan', 0, 10000, '总灵'], 
        ['sum_attr_value', 0, 10000, '属性总和'], 
        ['price_min', 0, 99999, '价格'], 
        ['price_max', 0, 99999, '价格'], 
        ['gem_level', 0, 20, '宝石锻炼等级'], 
        ['hole_num', 0, 5, '装备开孔数目'], 
        ['repair_fail', 0, 5, '修理失败次数']
    ]
    
    # 原JS逻辑：
    # var el = $('txt_' + item[0]);
    # var value = el.value;
    # if (!value) continue;
    # if (!intReg.test(value)) { alert(...); return; }
    # if (!(item[1] <= parseInt(value) && parseInt(value) <= item[2])) { alert(...); return; }
    # arg[item[0]] = parseInt(value);
    
    for param_name, min_val, max_val, desc in txt_int_items:
        try:
            # 使用MooTools风格的选择器获取元素值（原JS用的是$函数）
            element_value = await page.evaluate(f'''
            () => {{
                    // 模拟原始JavaScript的$('txt_' + item[0])
                var el = document.getElementById('txt_{param_name}');
                    if (!el) return null;
                    var value = el.value;
                    if (!value) return null;
                    
                    // 原JS验证逻辑: var intReg = /^\\d+$/;
                    var intReg = /^\\d+$/;
                    if (!intReg.test(value)) return 'invalid_number';
                    
                    var intValue = parseInt(value);
                    if (!({min_val} <= intValue && intValue <= {max_val})) return 'out_of_range';
                    
                    return intValue;
                }}
            ''')
            
            if element_value == 'invalid_number':
                print(f"⚠️ {param_name}: 必须是整数")
                continue
            elif element_value == 'out_of_range':
                print(f"⚠️ {param_name}: 超出取值范围 {min_val}-{max_val}")
                continue
            elif element_value is not None:
                params_dict[param_name] = element_value
                print(f"✅ {param_name}: {element_value}")
            else:
                print(f"⚠️ {param_name}: 无值")
                
        except Exception as e:
            print(f"❌ 获取 {param_name} 数值参数失败: {e}")
            continue
    
    # 6. 价格处理（原JS: if (arg['price_min']) arg['price_min'] = arg['price_min'] * 100;）
    if 'price_min' in params_dict: 
        params_dict['price_min'] *= 100
        print(f"  价格转换: price_min *= 100 = {params_dict['price_min']}")
    if 'price_max' in params_dict: 
        params_dict['price_max'] *= 100
        print(f"  价格转换: price_max *= 100 = {params_dict['price_max']}")

    # 7. 其他布尔值或特定值参数 - 按照原始JavaScript逻辑
    
    # 原JS: if ($('chk_star').checked) arg['star'] = 1;
    try:
        star_checked = await page.evaluate("() => document.getElementById('chk_star')?.checked || false")
        if star_checked:
            params_dict['star'] = 1
            print("✅ 星级: 已选择")
        else:
            print("⚠️ 星级: 未选择")
    except Exception as e:
        print(f"❌ 获取星级参数失败: {e}")
    
    # 原JS: if (this.select_server.get_serverid()) arg['serverid'] = this.select_server.get_serverid();
    # 这个需要通过JavaScript对象，先尝试获取
    try:
        serverid = await page.evaluate('''
            () => {
                if (window.OverallEquipSearcher && window.OverallEquipSearcher.select_server) {
                    return window.OverallEquipSearcher.select_server.get_serverid();
                }
                return null;
            }
        ''')
        if serverid: 
            params_dict['serverid'] = serverid
            print(f"✅ 服务器ID: {serverid}")
        else:
            print("⚠️ 服务器ID: 无值")
    except Exception as e:
        print(f"❌ 获取服务器ID参数失败: {e}")

    # 原JS: var suit_effect_ret = this.suit_value_getter.get_value(); if (suit_effect_ret.value) arg['suit_effect'] = suit_effect_ret.value;
    try:
        suit_effect = await page.evaluate('''
            () => {
                if (window.OverallEquipSearcher && window.OverallEquipSearcher.suit_value_getter) {
                    var ret = window.OverallEquipSearcher.suit_value_getter.get_value();
                    return (ret && ret.valid) ? ret.value : null;
                }
                return null;
            }
        ''')
        if suit_effect: 
            params_dict['suit_effect'] = suit_effect
            print(f"✅ 套装效果: {suit_effect}")
        else:
            print("⚠️ 套装效果: 无值")
    except Exception as e:
        print(f"❌ 获取套装效果参数失败: {e}")
    
    # 原JS: if ($("user_serverid") && $("user_serverid").value) arg['cross_buy_serverid'] = $("user_serverid").value;
    try:
        cross_buy_serverid = await page.evaluate("() => document.getElementById('user_serverid')?.value || ''")
        if cross_buy_serverid: 
            params_dict['cross_buy_serverid'] = cross_buy_serverid
            print(f"✅ 跨服购买服务器ID: {cross_buy_serverid}")
        else:
            print("⚠️ 跨服购买服务器ID: 无值")
    except Exception as e:
        print(f"❌ 获取跨服购买服务器ID参数失败: {e}")
    
    # 原JS: if ($('for_role_race').value) arg['for_role_race'] = $('for_role_race').value;
    try:
        for_role_race = await page.evaluate("() => document.getElementById('for_role_race')?.value || ''")
        if for_role_race: 
            params_dict['for_role_race'] = for_role_race
            print(f"✅ 角色种族: {for_role_race}")
        else:
            print("⚠️ 角色种族: 无值")
    except Exception as e:
        print(f"❌ 获取角色种族参数失败: {e}")
    
    # 原JS: if ($('for_role_sex').value) arg['for_role_sex'] = $('for_role_sex').value;
    try:
        for_role_sex = await page.evaluate("() => document.getElementById('for_role_sex')?.value || ''")
        if for_role_sex: 
            params_dict['for_role_sex'] = for_role_sex
            print(f"✅ 角色性别: {for_role_sex}")
        else:
            print("⚠️ 角色性别: 无值")
    except Exception as e:
        print(f"❌ 获取角色性别参数失败: {e}")

    # 原JS: var $160_attr = $('160_attr'); if ($160_attr.value) arg['160_attr'] = $160_attr.value;
    try:
        attr_160 = await page.evaluate("() => document.getElementById('160_attr')?.value || ''")
        if attr_160: 
            params_dict['160_attr'] = attr_160
            print(f"✅ 160属性: {attr_160}")
        else:
            print("⚠️ 160属性: 无值")
    except Exception as e:
        print(f"❌ 获取160属性参数失败: {e}")

    # 原JS: if ($('chk_filter_hun_da_gem').checked) arg['filter_hun_da_gem'] = 1;
    try:
        hun_da_gem_checked = await page.evaluate("() => document.getElementById('chk_filter_hun_da_gem')?.checked || false")
        if hun_da_gem_checked:
            params_dict['filter_hun_da_gem'] = 1
            print("✅ 混打宝石过滤: 已选择")
        else:
            print("⚠️ 混打宝石过滤: 未选择")
    except Exception as e:
        print(f"❌ 获取混打宝石过滤参数失败: {e}")

    # 8. 熔炼属性处理 - 完全按照原始JavaScript逻辑
    
    # 原JS熔炼逻辑:
    # if ($('chk_attr_with_melt').checked) {
    #     var attrInput = ['init_damage', 'init_damage_raw', 'all_damage', 'damage', 'init_defense', 'init_hp', 'init_dex', 'init_wakan', 'all_wakan'];
    #     for (var i = 0; i < attrInput.length; i++) {
    #         if (arg[attrInput[i]]) { arg['attr_with_melt'] = 1; break; }
    #     }
    # } else {
    #     arg['attr_without_melt'] = 1;
    # }
    
    try:
        attr_with_melt_checked = await page.evaluate("() => document.getElementById('chk_attr_with_melt')?.checked ?? true")
        attr_inputs = ['init_damage', 'init_damage_raw', 'all_damage', 'damage', 'init_defense', 'init_hp', 'init_dex', 'init_wakan', 'all_wakan']
        
        if attr_with_melt_checked:
            # 检查是否有任何属性输入
            has_attr_input = any(param in params_dict for param in attr_inputs)
            if has_attr_input:
                params_dict['attr_with_melt'] = 1
                print("✅ 属性熔炼: 包含熔炼")
        else:
            params_dict['attr_without_melt'] = 1
            print("✅ 属性熔炼: 不包含熔炼")
    except Exception as e:
        print(f"❌ 获取属性熔炼参数失败: {e}")
        params_dict['attr_without_melt'] = 1
    
    # 原JS属性总和熔炼逻辑:
    # if ($('chk_sum_attr_with_melt').checked && arg['sum_attr_value']) {
    #     arg['sum_attr_with_melt'] = 1;
    # } else {
    #     arg['sum_attr_without_melt'] = 1;
    # }
    
    try:
        sum_attr_with_melt_checked = await page.evaluate("() => document.getElementById('chk_sum_attr_with_melt')?.checked ?? true")
        if sum_attr_with_melt_checked and 'sum_attr_value' in params_dict:
            params_dict['sum_attr_with_melt'] = 1
            print("✅ 属性总和熔炼: 包含熔炼")
        else:
            params_dict['sum_attr_without_melt'] = 1
            print("✅ 属性总和熔炼: 不包含熔炼")
    except Exception as e:
        print(f"❌ 获取属性总和熔炼参数失败: {e}")
        params_dict['sum_attr_without_melt'] = 1

    print(f"\n📊 参数收集完成，共获取 {len(params_dict)} 个参数:")
    for key, value in params_dict.items():
        print(f"  {key}: {value}")

    return params_dict


# --- Public API ---

# 异步接口
async def get_equip_search_params_async(use_browser=True):
    URL = 'https://xyq.cbg.163.com/cgi-bin/equipquery.py?act=show_overall_search_equip'
    return await _get_params_async('normal', use_browser, _collect_normal_equip_logic, URL)

async def get_lingshi_search_params_async(use_browser=True):
    URL = 'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py?act=show_overall_search_lingshi'
    return await _get_params_async('lingshi', use_browser, _collect_lingshi_logic, URL)

async def get_pet_search_params_async(use_browser=True):
    URL = 'https://xyq.cbg.163.com/cgi-bin/equipquery.py?act=show_overall_search_pet'
    return await _get_params_async('pet', use_browser, _collect_pet_logic, URL)

async def get_pet_equip_search_params_async(use_browser=True):
    URL = 'https://xyq.cbg.163.com/cgi-bin/equipquery.py?act=show_overall_search_pet_equip'
    return await _get_params_async('pet_equip', use_browser, _collect_pet_equip_logic, URL)

# 同步接口
def get_equip_search_params_sync(use_browser=True):
    URL = 'https://xyq.cbg.163.com/cgi-bin/equipquery.py?act=show_overall_search_equip'
    return _get_params_sync('normal', use_browser, _collect_normal_equip_logic, URL)

def get_lingshi_search_params_sync(use_browser=True):
    URL = 'https://xyq.cbg.163.com/xyq_overall_search.py?act=show_overall_search_lingshi'
    return _get_params_sync('lingshi', use_browser, _collect_lingshi_logic, URL)

def get_pet_search_params_sync(use_browser=True):
    URL = 'https://xyq.cbg.163.com/cgi-bin/equipquery.py?act=show_overall_search_pet'
    return _get_params_sync('pet', use_browser, _collect_pet_logic, URL)

def get_pet_equip_search_params_sync(use_browser=True):
    URL = 'https://xyq.cbg.163.com/cgi-bin/equipquery.py?act=show_overall_search_pet_equip'
    return _get_params_sync('pet_equip', use_browser, _collect_pet_equip_logic, URL)

# 同步版本
def get_search_params(equip_type='normal', use_browser=False):
    """
    同步获取搜索参数的统一接口
    """
    sync_getter_map = {
        'normal': get_equip_search_params_sync,
        'lingshi': get_lingshi_search_params_sync,
        'pet': get_pet_search_params_sync
    }
    
    if equip_type not in sync_getter_map:
        raise ValueError(f"不支持的装备类型: {equip_type}")
        
    return sync_getter_map[equip_type](use_browser=use_browser)


# --- 主测试函数 ---

async def main():
    """测试函数"""
    print("--- 正在测试参数收集模块 ---")
    
    # 测试1: 使用浏览器收集普通装备参数
    print("\n--- 测试1: 浏览器模式 - 普通装备 ---")
    # params_normal = await get_equip_search_params_async(use_browser=True)
    # if params_normal:
    #     print("✅ 成功获取普通装备参数")
    
    # 测试2: 不使用浏览器，加载默认或本地的灵饰参数
    print("\n--- 测试2: 本地/默认模式 - 灵饰 ---")
    params_lingshi = await get_lingshi_search_params_async(use_browser=False)
    if params_lingshi:
        print(f"✅ 成功获取灵饰参数: \n{json.dumps(params_lingshi, ensure_ascii=False, indent=2)}")

    # 测试3: 同步接口
    print("\n--- 测试3: 同步接口 - 召唤兽装备 ---")
    params_pet_sync = get_pet_equip_search_params_sync(use_browser=False)
    if params_pet_sync:
        print(f"✅ 成功获取召唤兽装备参数 (同步): \n{json.dumps(params_pet_sync, ensure_ascii=False, indent=2)}")
    
    # 测试4: 新增宠物搜索接口
    print("\n--- 测试4: 异步接口 - 召唤兽 ---")
    params_pet_async = await get_pet_search_params_async(use_browser=False)
    if params_pet_async:
        print(f"✅ 成功获取召唤兽参数 (异步): \n{json.dumps(params_pet_async, ensure_ascii=False, indent=2)}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 