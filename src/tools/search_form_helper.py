import asyncio
from playwright.async_api import async_playwright
import logging
import json
import os
import requests
from functools import partial
import re # Added for regex validation in _collect_pet_logic

# 添加项目根目录到 Python 路径
from src.utils.project_path import get_project_root, get_config_path

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
    },
    'role': {
        'server_type': 3,
        'level_min': 0,
        'level_max': 175,
        'search_type': 'overall_search_role',
        'view_loc': 'overall_search',
        'count': 15
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
    params_file = os.path.join(get_config_path(), f'equip_params_{equip_type}.json')

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
    params_file = os.path.join(get_config_path(), f'equip_params_{equip_type}.json')

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


# Cookie验证功能已迁移到 src/utils/cookie_manager.py

async def _collect_params_base_async(url, collector_logic):
    """参数收集的基础函数 (异步)"""
    try:
        # Cookie 验证和准备
        logger.info("正在验证Cookie有效性...")
        from ..utils.cookie_manager import verify_cookie_validity_async
        if not await verify_cookie_validity_async():
            logger.warning("Cookie验证失败，正在更新Cookie...")
            from ..utils.cookie_manager import _update_cookies_internal
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
            browser = await p.chromium.launch(headless=False, devtools=True, args=['--auto-open-devtools-for-tabs'])
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
                print(f" 搜索参数收集成功！")
            
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
    
    print(" 开始收集灵饰参数...")
    
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
        print(f" 等级范围: {level_values['min']}-{level_values['max']}")
    except Exception as e:
        print(f" 获取等级范围参数失败: {e}")
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
                print(f" {param_name}: {value}")
            else:
                print(f" {param_name}: 无选择")
        except Exception as e:
            print(f" 获取{param_name}参数失败: {e}")
    
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
            print(f" 附加属性逻辑: {added_attr_logic}")
            
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
                        print(f" 详细附加属性{i}: {attr_value}")
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
                    print(f" 附加属性: {attr_value}")
        else:
            print(" 附加属性逻辑: 无选择")
    except Exception as e:
        print(f" 获取附加属性逻辑参数失败: {e}")
    
    # 4. 特效
    try:
        if await page.evaluate('() => document.getElementById("chk_has_eazy_effect")?.checked'):
            params_dict['special_effect'] = 1
            print(" 特效: 超级简易")
        else:
            print(" 特效: 无选择")
    except Exception as e:
        print(f" 获取特效参数失败: {e}")
    
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
                    print(f" {desc}必须是整数: {value}")
                    continue
                
                int_value = int(value)
                if not (min_val <= int_value <= max_val):
                    print(f" {desc}超出取值范围 {min_val}-{max_val}: {int_value}")
                    continue
                
                params_dict[item_name] = int_value
                print(f" {desc}: {int_value}")
            else:
                print(f" {desc}: 无值")
        except Exception as e:
            print(f" 获取{item_name}参数失败: {e}")
    
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
            print(f" 基础属性类型: {basic_attr_type}")
        else:
            print(" 基础属性类型: 无选择")
    except Exception as e:
        print(f" 获取基础属性类型参数失败: {e}")
    
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
            print(f" 综合属性: {synthesized_attr_type} = {synthesized_attr_value}")
        else:
            print(" 综合属性: 无选择")
    except Exception as e:
        print(f" 获取综合属性参数失败: {e}")
    
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
                print(f" 修理失败取值范围是0~3的整数: {repair_fail}")
            else:
                params_dict['repair_fail'] = int(repair_fail)
                print(f" 修理失败次数: {repair_fail}")
        else:
            print(" 修理失败次数: 无值")
    except Exception as e:
        print(f" 获取修理失败参数失败: {e}")
    
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
            print(f" 套装效果: {suit_effect}")
        else:
            print(" 套装效果: 无选择")
    except Exception as e:
        print(f" 获取套装效果参数失败: {e}")
    
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
            print(f" 服务器ID: {serverid}")
        else:
            print(" 服务器ID: 无值")
    except Exception as e:
        print(f" 获取服务器ID参数失败: {e}")
    
    # 跨服购买服务器ID
    try:
        cross_buy_serverid = await page.evaluate("() => document.getElementById('user_serverid')?.value || ''")
        if cross_buy_serverid: 
            params_dict['cross_buy_serverid'] = cross_buy_serverid
            print(f" 跨服购买服务器ID: {cross_buy_serverid}")
        else:
            print(" 跨服购买服务器ID: 无值")
    except Exception as e:
        print(f" 获取跨服购买服务器ID参数失败: {e}")
    
    # 12. 清理临时参数
    if 'basic_attr_value' in params_dict:
        del params_dict['basic_attr_value']
    
    print(f"\n 灵饰参数收集完成，共获取 {len(params_dict)} 个参数:")
    for key, value in params_dict.items():
        print(f"  {key}: {value}")
    
    return params_dict

async def _collect_pet_equip_logic(page):
    """收集召唤兽装备搜索逻辑 - 参考overall_search_pet_equips.js"""
    params_dict = {}
    
    print(" 开始收集召唤兽装备参数...")
    
    # 1. 等级范围参数 - 从LevelSlider对象获取
    try:
        # 按照原JS逻辑：args["level_min"] = SearchFormObj.level_slider.value.min;
        level_values = await page.evaluate('''
            () => {
                if (window.SearchFormObj && window.SearchFormObj.level_slider && window.SearchFormObj.level_slider.value) {
                    return {
                        min: window.SearchFormObj.level_slider.value.min,
                        max: window.SearchFormObj.level_slider.value.max
                    };
                }
                return { min: 5, max: 145 };  // 默认值
            }
        ''')
        
        params_dict['level_min'] = level_values['min']
        params_dict['level_max'] = level_values['max']
        print(f" 等级范围: {level_values['min']}-{level_values['max']}")
    except Exception as e:
        print(f" 获取等级范围参数失败: {e}")
        params_dict['level_min'] = 5
        params_dict['level_max'] = 145
    
    # 2. 装备类型选择
    try:
        # 原JS: var equip_pos = get_item_selected($$("#EquipPosBox li"));
        equip_pos = await page.evaluate('''
            () => {
                const items = document.querySelectorAll("#EquipPosBox li");
                const value_list = [];
                for (let i = 0; i < items.length; i++) {
                    const item = items[i];
                    if (item.classList.contains("on")) {
                        value_list.push(item.getAttribute("data_value"));
                    }
                }
                if (value_list.length == items.length) {
                    return "";
                } else {
                    return value_list.join(",");
                }
            }
        ''')
        
        if equip_pos:
            params_dict['equip_pos'] = equip_pos
            print(f" 装备类型: {equip_pos}")
        else:
            print(" 装备类型: 无选择")
    except Exception as e:
        print(f" 获取装备类型参数失败: {e}")
    
    # 3. 精魄灵石属性
    try:
        # 原JS: var xiangqian_stone_attr = get_item_selected($$('#xiangqian_stone_attr_panel li'));
        xiangqian_stone_attr = await page.evaluate('''
            () => {
                const items = document.querySelectorAll('#xiangqian_stone_attr_panel li');
                const value_list = [];
                for (let i = 0; i < items.length; i++) {
                    const item = items[i];
                    if (item.classList.contains("on")) {
                        value_list.push(item.getAttribute("data_value"));
                    }
                }
                if (value_list.length == items.length) {
                    return "";
                } else {
                    return value_list.join(",");
                }
            }
        ''')
        
        if xiangqian_stone_attr:
            params_dict['xiangqian_stone_attr'] = xiangqian_stone_attr
            print(f" 精魄灵石属性: {xiangqian_stone_attr}")
        else:
            print(" 精魄灵石属性: 无选择")
    except Exception as e:
        print(f" 获取精魄灵石属性参数失败: {e}")
    
    # 4. 附加属性选择
    try:
        # 原JS: var addon_el_list = $$("#addon_skill_box li");
        addon_attrs = await page.evaluate('''
            () => {
                const items = document.querySelectorAll("#addon_skill_box li");
                const result = {};
                for (let i = 0; i < items.length; i++) {
                    const item = items[i];
                    if (item.classList.contains("on")) {
                        const attr_name = item.getAttribute("data_value");
                        result[attr_name] = 1;
                    }
                }
                return result;
            }
        ''')
        
        for attr_name, value in addon_attrs.items():
            params_dict[attr_name] = value
            print(f" 附加属性: {attr_name}")
        
        if not addon_attrs:
            print(" 附加属性: 无选择")
    except Exception as e:
        print(f" 获取附加属性参数失败: {e}")
    
    # 5. 数值输入参数
    try:
        # 原JS: var args_config = [["speed", "速度"], ["fangyu", "防御"], ...];
        int_inputs = [
            ['speed', '速度'],
            ['fangyu', '防御'], 
            ['mofa', '魔法'],
            ['shanghai', '伤害'],
            ['hit_ratio', '命中率'],
            ['hp', '气血'],
            ['xiang_qian_level', '宝石'],
            ['addon_sum_min', '属性总和'],
            ['addon_minjie_reduce', '敏捷减少']
        ]
        
        for field_name, display_name in int_inputs:
            value = await page.evaluate(f'() => document.getElementById("{field_name}")?.value?.trim()')
            if value and value.isdigit() and len(value) <= 9:
                int_value = int(value)
                if int_value > 0:
                    params_dict[field_name] = int_value
                    print(f" {display_name}: {int_value}")
    except Exception as e:
        print(f" 获取数值输入参数失败: {e}")
    
    # 6. 修理失败次数
    try:
        repair_failed_times = await page.evaluate('() => document.getElementById("repair_failed_times")?.value')
        if repair_failed_times:
            params_dict["repair_failed_times"] = repair_failed_times
            print(f" 修理失败次数: {repair_failed_times}")
    except Exception as e:
        print(f" 获取修理失败次数参数失败: {e}")
    
    # 7. 价格范围
    try:
        # 原JS逻辑处理价格
        price_min = await page.evaluate('() => document.getElementById("price_min")?.value?.trim()')
        if price_min:
            try:
                price_min_value = float(price_min)
                if price_min_value > 0:
                    params_dict["price_min"] = int(price_min_value * 100)  # 转换为分
                    print(f" 最低价格: {price_min_value}")
            except ValueError:
                print(" 最低价格格式错误")
        
        price_max = await page.evaluate('() => document.getElementById("price_max")?.value?.trim()')
        if price_max:
            try:
                price_max_value = float(price_max)
                if price_max_value > 0:
                    params_dict["price_max"] = int(price_max_value * 100)  # 转换为分
                    print(f" 最高价格: {price_max_value}")
            except ValueError:
                print(" 最高价格格式错误")
        
        # 价格范围检查
        if params_dict.get("price_min") and params_dict.get("price_max"):
            if params_dict["price_max"] < params_dict["price_min"]:
                print(" 价格范围错误：最高价格小于最低价格")
                params_dict.pop("price_min", None)
                params_dict.pop("price_max", None)
    except Exception as e:
        print(f" 获取价格参数失败: {e}")
    
    # 8. 附加状态
    try:
        addon_status = await page.evaluate('() => document.getElementById("addon_status")?.value')
        if addon_status:
            # 验证附加状态是否有效
            is_valid = await page.evaluate(f'''
                () => {{
                    const valid_values = window.MO_SHOU_YAO_JUE || [];
                    const equip_addon_status = window.EquipAddonStatus || [];
                    return valid_values.includes("{addon_status}") || equip_addon_status.includes("{addon_status}");
                }}
            ''')
            
            if is_valid:
                params_dict["addon_status"] = addon_status
                print(f" 附加状态: {addon_status}")
            else:
                print(f" 附加状态无效: {addon_status}")
    except Exception as e:
        print(f" 获取附加状态参数失败: {e}")
    
    # 9. 套装效果相关
    try:
        # 原JS: var $noSuitEffect = $('no_suit_effect'), $hasSuitEffect = $('has_suit_effect')
        no_suit_effect = await page.evaluate('() => document.getElementById("no_suit_effect")?.checked')
        if no_suit_effect:
            params_dict['include_no_skill'] = 1
            print(" 包含无套装效果")
        
        has_suit_effect = await page.evaluate('() => document.getElementById("has_suit_effect")?.checked')
        has_suit_effect_disabled = await page.evaluate('() => document.getElementById("has_suit_effect")?.disabled')
        
        if has_suit_effect and not has_suit_effect_disabled:
            params_dict['include_can_cover_skill'] = 1
            print(" 包含可覆盖套装效果")
        
        # 属性总和包含伤害
        include_damage = await page.evaluate('() => document.getElementById("addon_sum_include_damage")?.checked')
        if include_damage:
            params_dict['addon_sum_include_damage'] = 1
            print(" 属性总和包含伤害")
    except Exception as e:
        print(f" 获取套装效果参数失败: {e}")
    
    # 10. 服务器类型
    try:
        # 原JS: var check_items = [['server_type', this.server_type_checker, true]];
        server_type = await page.evaluate('''
            () => {
                const items = document.querySelectorAll("#server_type_panel li");
                for (let i = 0; i < items.length; i++) {
                    const item = items[i];
                    if (item.classList.contains("on")) {
                        return item.getAttribute("data_value");
                    }
                }
                return null;
            }
        ''')
        
        if server_type:
            params_dict['server_type'] = server_type
            print(f" 服务器类型: {server_type}")
        else:
            print(" 服务器类型: 无选择")
    except Exception as e:
        print(f" 获取服务器类型参数失败: {e}")
    
    # 11. 指定服务器
    try:
        # 原JS: if (this.select_server.get_serverid()) { args['serverid'] = this.select_server.get_serverid(); }
        serverid = await page.evaluate('''
            () => {
                if (window.SearchFormObj && window.SearchFormObj.select_server && window.SearchFormObj.select_server.get_serverid) {
                    return window.SearchFormObj.select_server.get_serverid();
                }
                return null;
            }
        ''')
        
        if serverid:
            params_dict['serverid'] = serverid
            print(f" 指定服务器: {serverid}")
    except Exception as e:
        print(f" 获取指定服务器参数失败: {e}")
    
    # 12. 跨服购买
    try:
        # 原JS: if ($("user_serverid") && $("user_serverid").value) { args['cross_buy_serverid'] = $("user_serverid").value; }
        user_serverid = await page.evaluate('() => document.getElementById("user_serverid")?.value')
        if user_serverid:
            params_dict['cross_buy_serverid'] = user_serverid
            print(f" 跨服购买服务器: {user_serverid}")
    except Exception as e:
        print(f" 获取跨服购买参数失败: {e}")
    
    # 13. 参数验证
    if not params_dict:
        print(" 没有收集到任何搜索参数")
        return params_dict
    
    print(f" 成功收集到 {len(params_dict)} 个参数")
    return params_dict

async def _collect_pet_logic(page):
    """收集召唤兽搜索逻辑 - 参考overall_search_pet.js"""
    params_dict = {}
    
    print(" 开始收集召唤兽参数...")
    
    # 1. 召唤兽类型 - 原JS: if ($('pet_select_box').value) { var pet_type = this.get_pet_type_value(); arg['type'] = pet_type; }
    try:
        pet_name = await page.evaluate('() => document.getElementById("pet_select_box")?.value')
        if pet_name:
            # 获取召唤兽类型值
            pet_type = await page.evaluate(f'''
                () => {{
                    var result = [];
                    var pet_name = "{pet_name}";
                    if (!pet_name) return null;
                    
                    for (var pet_type in SaleablePetNameInfo) {{
                        if (SaleablePetNameInfo[pet_type] == pet_name) {{
                            result.push(pet_type);
                        }}
                    }}
                    return result.join(',');
                }}
            ''')
            if pet_type:
                params_dict['type'] = pet_type
                print(f" 召唤兽类型: {pet_name} -> {pet_type}")
            else:
                print(f" 召唤兽类型无效: {pet_name}")
    except Exception as e:
        print(f" 获取召唤兽类型参数失败: {e}")
    
    # 2. 收集各种选择器参数 - 原JS: var check_items = [['low_skill', this.low_skill_checker, false], ...]
    check_panels = [
        ['low_skill', 'pet_equal_advanced_skill_panel', False],
        ['front_status', 'fair_show_panel', True],
        ['server_type', 'server_type_panel', True],
        ['color', 'color_panel', False],
        ['mengying', 'mengying_panel', False],
        ['texing', 'texing_panel', False],
        ['positive_effect', 'positive_effect_panel', False],
        ['negative_effect', 'negative_effect_panel', False],
        ['kindid', 'fight_level_panel', True]
    ]
    
    for param_name, panel_id, skip_all in check_panels:
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
                            if ('{param_name}' === 'kindid' && window.FightLevels) {{
                                for (let item of window.FightLevels) {{
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
                            }} else if ('{param_name}' === 'color' && window.Colors) {{
                                for (let item of window.Colors) {{
                                    if (item[1] === text) {{
                                        value = item[0];
                                        break;
                                    }}
                                }}
                            }} else if ('{param_name}' === 'mengying' && window.MengYingConf) {{
                                for (let item of window.MengYingConf) {{
                                    if (item[1] === text) {{
                                        value = item[0];
                                        break;
                                    }}
                                }}
                            }} else if ('{param_name}' === 'texing' && window.TexingTypes) {{
                                for (let item of window.TexingTypes) {{
                                    if (item[1] === text) {{
                                        value = item[0];
                                        break;
                                    }}
                                }}
                            }} else if ('{param_name}' === 'positive_effect' && window.TexingPositiveEffectTypes) {{
                                for (let item of window.TexingPositiveEffectTypes) {{
                                    if (item[1] === text) {{
                                        value = item[0];
                                        break;
                                    }}
                                }}
                            }} else if ('{param_name}' === 'negative_effect' && window.TexingPositiveEffectTypes) {{
                                for (let item of window.TexingPositiveEffectTypes) {{
                                    if (item[1] === text) {{
                                        value = item[0];
                                        break;
                                    }}
                                }}
                            }} else if ('{param_name}' === 'low_skill' && window.PetSkills) {{
                                // 低技能需要特殊处理，获取技能ID
                                const skillId = li.getAttribute('data-skill_id');
                                if (skillId) {{
                                    value = skillId;
                                }}
                            }}
                            
                            selectedValues.push(value);
                        }}
                    }}
                    
                    // 检查是否全选（需要跳过的情况）
                    if ({str(skip_all).lower()}) {{
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
                print(f" {param_name}: {value}")
            else:
                print(f" {param_name}: 无选择")
        except Exception as e:
            print(f" 获取{param_name}参数失败: {e}")
    
    # 3. 技能相关参数 - 原JS: arg = this.get_skill_value(arg);
    try:
        # 收集包含技能
        skill_panels = [
            'pet_skill_super_panel',
            'pet_skill_special_panel', 
            'pet_skill_fashu_panel',
            'pet_skill_wuli_panel',
            'pet_skill_tongyong_panel',
            'pet_skill_primary_panel'
        ]
        
        skill_values = []
        for panel_id in skill_panels:
            panel_skills = await page.evaluate(f'''
                () => {{
                    const panel = document.getElementById('{panel_id}');
                    if (!panel) return [];
                    
                    const selectedSkills = [];
                    const liElements = panel.querySelectorAll('li.on');
                    liElements.forEach(li => {{
                        const skillId = li.getAttribute('data-skill_id');
                        if (skillId) {{
                            selectedSkills.push(skillId);
                        }}
                    }});
                    return selectedSkills;
                }}
            ''')
            skill_values.extend(panel_skills)
        
        if skill_values:
            params_dict['skill'] = ','.join(skill_values)
            print(f" 包含技能: {len(skill_values)}个")
        
        # 收集不包含技能
        not_skill_panels = [
            'not_pet_skill_super_panel',
            'not_pet_skill_special_panel',
            'not_pet_skill_fashu_panel', 
            'not_pet_skill_wuli_panel',
            'not_pet_skill_tongyong_panel',
            'not_pet_skill_primary_panel'
        ]
        
        not_skill_values = []
        for panel_id in not_skill_panels:
            panel_skills = await page.evaluate(f'''
                () => {{
                    const panel = document.getElementById('{panel_id}');
                    if (!panel) return [];
                    
                    const selectedSkills = [];
                    const liElements = panel.querySelectorAll('li.on');
                    liElements.forEach(li => {{
                        const skillId = li.getAttribute('data-skill_id');
                        if (skillId) {{
                            selectedSkills.push(skillId);
                        }}
                    }});
                    return selectedSkills;
                }}
            ''')
            not_skill_values.extend(panel_skills)
        
        if not_skill_values:
            params_dict['not_in_skill'] = ','.join(not_skill_values)
            print(f" 不包含技能: {len(not_skill_values)}个")
            
    except Exception as e:
        print(f" 获取技能参数失败: {e}")
    
    # 4. 内丹和赐福技能
    try:
        # 高级内丹
        high_neidan_values = await page.evaluate('''
            () => {
                const panel = document.getElementById('high_neidan_panel');
                if (!panel) return [];
                
                const selectedValues = [];
                const liElements = panel.querySelectorAll('li.on');
                liElements.forEach(li => {
                    const span = li.querySelector('span');
                    if (span) {
                        const text = span.textContent.trim();
                        if (window.HighNeidans) {
                            for (let item of window.HighNeidans) {
                                if (item[1] === text) {
                                    selectedValues.push(item[0]);
                                    break;
                                }
                            }
                        }
                    }
                });
                return selectedValues;
            }
        ''')
        if high_neidan_values:
            params_dict['high_neidan'] = high_neidan_values
            print(f" 高级内丹: {high_neidan_values}")
        
        # 低级内丹
        low_neidan_values = await page.evaluate('''
            () => {
                const panel = document.getElementById('low_neidan_panel');
                if (!panel) return [];
                
                const selectedValues = [];
                const liElements = panel.querySelectorAll('li.on');
                liElements.forEach(li => {
                    const span = li.querySelector('span');
                    if (span) {
                        const text = span.textContent.trim();
                        if (window.LowNeidans) {
                            for (let item of window.LowNeidans) {
                                if (item[1] === text) {
                                    selectedValues.push(item[0]);
                                    break;
                                }
                            }
                        }
                    }
                });
                return selectedValues;
            }
        ''')
        if low_neidan_values:
            params_dict['low_neidan'] = low_neidan_values
            print(f" 低级内丹: {low_neidan_values}")
        
        # 赐福技能
        cifu_skills_values = await page.evaluate('''
            () => {
                const panel = document.getElementById('limit_evol_panel');
                if (!panel) return [];
                
                const selectedValues = [];
                const liElements = panel.querySelectorAll('li.on');
                liElements.forEach(li => {
                    const span = li.querySelector('span');
                    if (span) {
                        const text = span.textContent.trim();
                        if (window.cifuSkills) {
                            for (let item of window.cifuSkills) {
                                if (item[1] === text) {
                                    selectedValues.push(item[0]);
                                    break;
                                }
                            }
                        }
                    }
                });
                return selectedValues;
            }
        ''')
        if cifu_skills_values:
            params_dict['evol_skill'] = cifu_skills_values
            print(f" 赐福技能: {cifu_skills_values}")
            
    except Exception as e:
        print(f" 获取内丹和赐福技能参数失败: {e}")
    
    # 5. 复选框参数
    checkbox_items = [
        ['skill_with_suit', 'chk_skill_with_suit'],
        ['suit_as_any_skill', 'chk_suit_as_any_skill'],
        ['skill_including_advanced', 'chk_skill_including_advanced'],
        ['advanced_evol_skill', 'chk_advanced_evol_skill'],
        ['is_baobao', 'chk_is_baobao'],
        ['summon_color', 'chk_summon_color']
    ]
    
    for param_name, checkbox_id in checkbox_items:
        try:
            if await page.evaluate(f'() => document.getElementById("{checkbox_id}")?.checked'):
                params_dict[param_name] = 1
                print(f" {param_name}: 已选择")
        except Exception as e:
            print(f" 获取{param_name}参数失败: {e}")
    
    # 6. 赐福技能模式
    try:
        if await page.evaluate('() => document.getElementById("evol_skill_mode")?.checked'):
            params_dict['evol_skill_mode'] = 1
            print(" 赐福技能模式: 满足全部")
        else:
            params_dict['evol_skill_mode'] = 0
            print(" 赐福技能模式: 满足一种")
    except Exception as e:
        print(f" 获取赐福技能模式参数失败: {e}")
        params_dict['evol_skill_mode'] = 0
    
    # 7. 数值输入参数 - 完全按照原始JavaScript逻辑
    txt_int_items = [
        ['level_min', 0, 180, '等级'],
        ['level_max', 0, 180, '等级'],
        ['skill_num', 0, 10000, '技能数量'],
        ['valid_evol_skill_num', 0, 4, '有效赐福技能数'],
        ['attack_aptitude', 0, 10000, '攻击资质'],
        ['defence_aptitude', 0, 10000, '防御资质'],
        ['physical_aptitude', 0, 10000, '体力资质'],
        ['magic_aptitude', 0, 10000, '法力资质'],
        ['speed_aptitude_min', 0, 10000, '速度资质'],
        ['speed_aptitude_max', 0, 10000, '速度资质'],
        ['price_min', 0, 99999, '价格'],
        ['price_max', 0, 99999, '价格'],
        ['max_blood', 0, 20000, '气血'],
        ['attack', 0, 4000, '攻击'],
        ['defence', 0, 4000, '防御'],
        ['speed_min', 0, 2000, '速度'],
        ['speed_max', 0, 2000, '速度'],
        ['fashang', 0, 99999, '法伤'],
        ['fafang', 0, 99999, '法防'],
        ['lingxing', 0, 10000, '灵性'],
        ['used_lianshou_max', 0, 99999, '已使用炼兽珍经数量'],
        ['used_yuanxiao_max', 0, 99999, '已使用元宵数量'],
        ['high_neidan_level', 0, 99999, '高级内丹层数'],
        ['low_neidan_level', 0, 99999, '低级内丹层数']
    ]
    
    for param_name, min_val, max_val, desc in txt_int_items:
        try:
            value = await page.evaluate(f'''
                () => {{
                    const el = document.getElementById('txt_{param_name}');
                    if (!el) return null;
                    const value = el.value;
                    if (!value) return null;
                    
                    // 原JS验证逻辑: var intReg = /^\\d+$/;
                    const intReg = /^\\d+$/;
                    if (!intReg.test(value)) return 'invalid_number';
                    
                    const intValue = parseInt(value);
                    if (!({min_val} <= intValue && intValue <= {max_val})) return 'out_of_range';
                    
                    return intValue;
                }}
            ''')
            
            if value == 'invalid_number':
                print(f" {desc}必须是整数")
                continue
            elif value == 'out_of_range':
                print(f" {desc}超出取值范围 {min_val}-{max_val}")
                continue
            elif value is not None:
                params_dict[param_name] = value
                print(f" {desc}: {value}")
        except Exception as e:
            print(f" 获取{param_name}参数失败: {e}")
    
    # 8. 价格范围检查
    if 'price_min' in params_dict and 'price_max' in params_dict:
        if params_dict['price_max'] < params_dict['price_min']:
            print(" 价格范围错误：最高价格小于最低价格")
            params_dict.pop('price_min', None)
            params_dict.pop('price_max', None)
    
    # 9. 价格处理（原JS: if (arg['price_min']) arg['price_min'] = arg['price_min'] * 100;）
    if 'price_min' in params_dict: 
        params_dict['price_min'] *= 100
        print(f"  价格转换: price_min *= 100 = {params_dict['price_min']}")
    if 'price_max' in params_dict: 
        params_dict['price_max'] *= 100
        print(f"  价格转换: price_max *= 100 = {params_dict['price_max']}")
    
    # 10. 成长值处理 - 原JS: arg['growth'] = parseInt(parseFloat(growth) * 1000);
    try:
        growth = await page.evaluate('() => document.getElementById("txt_growth")?.value')
        if growth:
            # 验证成长值格式: /^\d\.\d{1,3}$/
            if not re.match(r'^\d+\.\d{1,3}$', growth):
                print(f" 成长值错误, 最多3位小数: {growth}")
            else:
                params_dict['growth'] = int(float(growth) * 1000)
                print(f" 成长值: {growth} -> {params_dict['growth']}")
    except Exception as e:
        print(f" 获取成长值参数失败: {e}")
    
    # 11. 服务器相关
    try:
        # 指定服务器
        serverid = await page.evaluate('''
            () => {
                if (window.OverallPetSearcher && window.OverallPetSearcher.select_server) {
                    return window.OverallPetSearcher.select_server.get_serverid();
                }
                return null;
            }
        ''')
        if serverid: 
            params_dict['serverid'] = serverid
            print(f" 服务器ID: {serverid}")
    except Exception as e:
        print(f" 获取服务器ID参数失败: {e}")
    
    # 跨服购买服务器ID
    try:
        cross_buy_serverid = await page.evaluate("() => document.getElementById('user_serverid')?.value || ''")
        if cross_buy_serverid: 
            params_dict['cross_buy_serverid'] = cross_buy_serverid
            print(f" 跨服购买服务器ID: {cross_buy_serverid}")
    except Exception as e:
        print(f" 获取跨服购买服务器ID参数失败: {e}")
    
    # 12. 特殊处理：技能数量不包含认证技能
    try:
        if 'skill_num' in params_dict and params_dict['skill_num'] > 0:
            if await page.evaluate('() => document.getElementById("no_include_sp_skill")?.checked'):
                params_dict['no_include_sp_skill'] = 1
                print(" 技能数量不包含认证技能")
    except Exception as e:
        print(f" 获取技能数量特殊处理参数失败: {e}")
    
    print(f"\n 召唤兽参数收集完成，共获取 {len(params_dict)} 个参数:")
    for key, value in params_dict.items():
        print(f"  {key}: {value}")
    
    return params_dict

async def _collect_normal_equip_logic(page):
    """普通装备参数收集的具体逻辑 - 直接模拟原始JavaScript逻辑"""
    params_dict = {}
    
    print(" 开始收集参数...")
    

    
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
        print(f" 等级范围: {level_values['min']}-{level_values['max']}")
    except Exception as e:
        print(f" 获取等级范围参数失败: {e}")
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
                print(f" {param_name}: 全选，跳过")
                continue
            elif selected_values:
                params_dict[param_name] = selected_values
                print(f" {param_name}: {selected_values}")
            else:
                print(f" {param_name}: 无选择")
                
        except Exception as e:
            print(f" 获取 {param_name} 参数失败: {e}")
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
            print(f" 特效模式: {check_mode}")
        except Exception as e:
            print(f" 获取特效模式参数失败: {e}")
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
            print(f" 属性总和类型: {sum_attr_type}")
        else:
            print(" 属性总和类型: 无选择")
    except Exception as e:
        print(f" 获取属性总和类型参数失败: {e}")
    
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
                print(f" {param_name}: 必须是整数")
                continue
            elif element_value == 'out_of_range':
                print(f" {param_name}: 超出取值范围 {min_val}-{max_val}")
                continue
            elif element_value is not None:
                params_dict[param_name] = element_value
                print(f" {param_name}: {element_value}")
            else:
                print(f" {param_name}: 无值")
                
        except Exception as e:
            print(f" 获取 {param_name} 数值参数失败: {e}")
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
            print(" 星级: 已选择")
        else:
            print(" 星级: 未选择")
    except Exception as e:
        print(f" 获取星级参数失败: {e}")
    
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
            print(f" 服务器ID: {serverid}")
        else:
            print(" 服务器ID: 无值")
    except Exception as e:
        print(f" 获取服务器ID参数失败: {e}")

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
            print(f" 套装效果: {suit_effect}")
        else:
            print(" 套装效果: 无值")
    except Exception as e:
        print(f" 获取套装效果参数失败: {e}")
    
    # 原JS: if ($("user_serverid") && $("user_serverid").value) arg['cross_buy_serverid'] = $("user_serverid").value;
    try:
        cross_buy_serverid = await page.evaluate("() => document.getElementById('user_serverid')?.value || ''")
        if cross_buy_serverid: 
            params_dict['cross_buy_serverid'] = cross_buy_serverid
            print(f" 跨服购买服务器ID: {cross_buy_serverid}")
        else:
            print(" 跨服购买服务器ID: 无值")
    except Exception as e:
        print(f" 获取跨服购买服务器ID参数失败: {e}")
    
    # 原JS: if ($('for_role_race').value) arg['for_role_race'] = $('for_role_race').value;
    try:
        for_role_race = await page.evaluate("() => document.getElementById('for_role_race')?.value || ''")
        if for_role_race: 
            params_dict['for_role_race'] = for_role_race
            print(f" 角色种族: {for_role_race}")
        else:
            print(" 角色种族: 无值")
    except Exception as e:
        print(f" 获取角色种族参数失败: {e}")
    
    # 原JS: if ($('for_role_sex').value) arg['for_role_sex'] = $('for_role_sex').value;
    try:
        for_role_sex = await page.evaluate("() => document.getElementById('for_role_sex')?.value || ''")
        if for_role_sex: 
            params_dict['for_role_sex'] = for_role_sex
            print(f" 角色性别: {for_role_sex}")
        else:
            print(" 角色性别: 无值")
    except Exception as e:
        print(f" 获取角色性别参数失败: {e}")

    # 原JS: var $160_attr = $('160_attr'); if ($160_attr.value) arg['160_attr'] = $160_attr.value;
    try:
        attr_160 = await page.evaluate("() => document.getElementById('160_attr')?.value || ''")
        if attr_160: 
            params_dict['160_attr'] = attr_160
            print(f" 160属性: {attr_160}")
        else:
            print(" 160属性: 无值")
    except Exception as e:
        print(f" 获取160属性参数失败: {e}")

    # 原JS: if ($('chk_filter_hun_da_gem').checked) arg['filter_hun_da_gem'] = 1;
    try:
        hun_da_gem_checked = await page.evaluate("() => document.getElementById('chk_filter_hun_da_gem')?.checked || false")
        if hun_da_gem_checked:
            params_dict['filter_hun_da_gem'] = 1
            print(" 混打宝石过滤: 已选择")
        else:
            print(" 混打宝石过滤: 未选择")
    except Exception as e:
        print(f" 获取混打宝石过滤参数失败: {e}")

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
                print(" 属性熔炼: 包含熔炼")
        else:
            params_dict['attr_without_melt'] = 1
            print(" 属性熔炼: 不包含熔炼")
    except Exception as e:
        print(f" 获取属性熔炼参数失败: {e}")
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
            print(" 属性总和熔炼: 包含熔炼")
        else:
            params_dict['sum_attr_without_melt'] = 1
            print(" 属性总和熔炼: 不包含熔炼")
    except Exception as e:
        print(f" 获取属性总和熔炼参数失败: {e}")
        params_dict['sum_attr_without_melt'] = 1

    print(f"\n 参数收集完成，共获取 {len(params_dict)} 个参数:")
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
    URL = 'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py?act=show_pet_equip_search_form'
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
    URL = 'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py?act=show_pet_equip_search_form'
    return _get_params_sync('pet_equip', use_browser, _collect_pet_equip_logic, URL)

# 同步版本
def get_search_params(equip_type='normal', use_browser=False):
    """
    同步获取搜索参数的统一接口
    """
    sync_getter_map = {
        'normal': get_equip_search_params_sync,
        'lingshi': get_lingshi_search_params_sync,
        'pet': get_pet_search_params_sync,
        'role': get_role_search_params_sync  # 添加角色支持
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
    #     print(" 成功获取普通装备参数")
    
    # 测试2: 不使用浏览器，加载默认或本地的灵饰参数
    print("\n--- 测试2: 本地/默认模式 - 灵饰 ---")
    params_lingshi = await get_lingshi_search_params_async(use_browser=False)
    if params_lingshi:
        print(f" 成功获取灵饰参数: \n{json.dumps(params_lingshi, ensure_ascii=False, indent=2)}")

    # 测试3: 同步接口
    print("\n--- 测试3: 同步接口 - 召唤兽装备 ---")
    params_pet_sync = get_pet_equip_search_params_sync(use_browser=False)
    if params_pet_sync:
        print(f" 成功获取召唤兽装备参数 (同步): \n{json.dumps(params_pet_sync, ensure_ascii=False, indent=2)}")
    
    # 测试4: 新增召唤兽搜索接口
    print("\n--- 测试4: 异步接口 - 召唤兽 ---")
    params_pet_async = await get_pet_search_params_async(use_browser=False)
    if params_pet_async:
        print(f" 成功获取召唤兽参数 (异步): \n{json.dumps(params_pet_async, ensure_ascii=False, indent=2)}")


# 角色搜索参数收集相关函数

async def _collect_role_logic(page):
    """角色参数收集的具体逻辑"""
    params_dict = {}
    
    print(" 开始收集角色搜索参数...")
    
    try:
        # 直接读取隐藏字段 query_args 的值
        query_args_value = await page.evaluate("() => document.getElementById('query_args')?.value || '{}'")
        print(f"📄 获取到 query_args 原始值: {query_args_value}")
        
        if query_args_value and query_args_value != '{}':
            try:
                # 解析 JSON 字符串
                import json
                args_dict = json.loads(query_args_value)
                params_dict.update(args_dict)
                print(f" 成功解析 query_args: {json.dumps(args_dict, ensure_ascii=False)}")
            except json.JSONDecodeError as e:
                print(f" JSON 解析失败: {e}")
                # 如果解析失败，使用默认参数
                params_dict = DEFAULT_PARAMS['role'].copy()
        else:
            print(" query_args 为空，使用默认参数")
            params_dict = DEFAULT_PARAMS['role'].copy()
        
        # 确保必要的字段存在
        if 'server_type' not in params_dict:
            params_dict['server_type'] = 3
        if 'search_type' not in params_dict:
            params_dict['search_type'] = 'overall_search_role'
        if 'view_loc' not in params_dict:
            params_dict['view_loc'] = 'overall_search'
        if 'count' not in params_dict:
            params_dict['count'] = 15
        
        print(f"\n 角色参数收集完成，共获取 {len(params_dict)} 个参数:")
        for key, value in params_dict.items():
            print(f"  {key}: {value}")
        
        return params_dict
        
    except Exception as e:
        print(f" 收集角色参数失败: {e}")
        import traceback
        traceback.print_exc()
        # 返回默认参数
        return DEFAULT_PARAMS['role'].copy()

# 异步接口
async def get_role_search_params_async(use_browser=True):
    """异步获取角色搜索参数"""
    URL = 'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py?act=show_search_role_form'
    return await _get_params_async('role', use_browser, _collect_role_logic, URL)

# 同步接口
def get_role_search_params_sync(use_browser=True):
    """同步获取角色搜索参数"""
    URL = 'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py?act=show_search_role_form'
    return _get_params_sync('role', use_browser, _collect_role_logic, URL)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 