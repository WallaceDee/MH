#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
梦幻西游藏宝阁召唤兽爬虫模块
专门用于爬取召唤兽（宠物）数据
"""

import os
import sys
import json
import sqlite3
import time
import random
import logging
from datetime import datetime
from urllib.parse import urlencode
import asyncio
from playwright.async_api import async_playwright

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.tools.setup_requests_session import setup_session
from src.utils.smart_db_helper import CBGSmartDB
from src.cbg_config import DB_TABLE_SCHEMAS, DB_TABLE_ORDER
from src.tools.search_form_helper import (
    get_pet_search_params_sync,
    get_pet_search_params_async,
    verify_cookie_validity,
)


class CBGPetSpider:
    def __init__(self):
        self.session = setup_session()
        self.base_url = 'https://xyq.cbg.163.com/cgi-bin/recommend.py'
        self.output_dir = self.create_output_dir()
        
        # 使用按月分割的数据库文件路径
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        current_month = datetime.now().strftime('%Y%m')
        
        # 宠物数据库路径
        db_filename = f"cbg_pets_{current_month}.db"
        self.db_path = os.path.join(project_root, 'data', db_filename)
        
        # 确保data目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 初始化智能数据库助手
        self.smart_db = CBGSmartDB(self.db_path)
        
        # 配置专用的日志器，避免与其他模块冲突
        self.logger = self._setup_logger()
        
        # 初始化其他组件
        self.setup_session()
        self.init_database()
        self.retry_attempts = 1

    def _setup_logger(self):
        """设置专用的日志器"""
        # 创建专用的日志器
        logger = logging.getLogger(f'CBGPetSpider_{id(self)}')
        logger.setLevel(logging.INFO)
        
        # 清除可能存在的处理器，避免重复日志
        if logger.handlers:
            logger.handlers.clear()
        
        # 创建文件处理器
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(self.output_dir, f'cbg_pet_spider_{timestamp}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='w')
        file_handler.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器到日志器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # 防止日志传播到根日志器，避免重复输出
        logger.propagate = False
        
        # 测试日志写入
        logger.info("🎉 CBG宠物爬虫日志系统初始化完成")
        logger.info(f"📁 日志文件路径: {log_file}")
        
        return logger

    def create_output_dir(self):
        """创建输出目录 - 按年月分组"""
        current_date = datetime.now()
        year_month = current_date.strftime('%Y%m')  # 202506
        output_dir = os.path.join('output', year_month)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def setup_session(self):
        """设置请求会话"""
        # 从cookies.txt文件读取Cookie
        cookie_content = None
        try:
            # 获取项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            cookies_path = os.path.join(project_root, 'config/cookies.txt')
            
            with open(cookies_path, 'r', encoding='utf-8') as f:
                cookie_content = f.read().strip()
            if cookie_content:
                self.session.headers.update({'Cookie': cookie_content})
                self.logger.info("成功从config/cookies.txt文件加载Cookie")
            else:
                self.logger.warning("config/cookies.txt文件为空")
                
        except FileNotFoundError:
            self.logger.error("未找到config/cookies.txt文件，请创建该文件并添加有效的Cookie")
        except Exception as e:
            self.logger.error(f"读取config/cookies.txt文件失败: {e}")
        
        # 设置请求头
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
            'referer': 'https://xyq.cbg.163.com/cgi-bin/equipquery.py?act=show_overall_search_pet'
        }
        
        # 如果有Cookie，添加到请求头中
        if cookie_content:
            headers['Cookie'] = cookie_content
            self.logger.info("Cookie已添加到请求头")
        else:
            self.logger.warning("未找到有效的Cookie，可能影响数据获取")
        
        self.session.headers.update(headers)
    
    def init_database(self):
        """初始化数据库和表结构"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 只创建宠物相关的表
            cursor.execute(DB_TABLE_SCHEMAS['pets'])
            self.logger.debug("宠物数据库创建表: pets")
            
            conn.commit()
            self.logger.info(f"宠物数据库初始化完成: {os.path.basename(self.db_path)}")
            
        except Exception as e:
            self.logger.error(f"初始化宠物数据库失败: {e}")
            raise
        finally:
            conn.close()

    def parse_jsonp_response(self, text):
        """解析JSONP响应，提取宠物数据"""
        try:
            # 提取JSON部分
            start = text.find('(') + 1
            end = text.rfind(')')
            if start <= 0 or end <= 0:
                self.logger.error("响应不是有效的JSONP格式")
                return None
                
            json_str = text[start:end]
            data = json.loads(json_str)
            
            if not isinstance(data, dict):
                self.logger.error("解析JSONP响应失败：响应不是一个有效的JSON对象")
                return None

            equip_list = data.get('equip_list', [])
            
            if not equip_list:
                self.logger.warning(text)
                self.logger.warning("没有找到任何宠物数据")
                return []
                
            pets = []
            for pet in equip_list:
                try:
                    # 直接保存所有原始字段，不做解析
                    pet_data = {
                        # 基本字段直接映射
                        'eid': pet.get('eid'),
                        'equipid': pet.get('equipid'),
                        'equip_sn': pet.get('equip_sn'),
                        'server_name': pet.get('server_name'),
                        'serverid': pet.get('serverid'),
                        'equip_server_sn': pet.get('equip_server_sn'),
                        'seller_nickname': pet.get('seller_nickname'),
                        'seller_roleid': pet.get('seller_roleid'),
                        'area_name': pet.get('area_name'),
                        'equip_name': pet.get('equip_name'),
                        'equip_type': pet.get('equip_type'),
                        'equip_type_name': pet.get('equip_type_name'),
                        'equip_type_desc': pet.get('equip_type_desc'),
                        'level': pet.get('level'),
                        'equip_level': pet.get('equip_level'),
                        'equip_level_desc': pet.get('equip_level_desc'),
                        'level_desc': pet.get('level_desc'),
                        'subtitle': pet.get('subtitle'),
                        'equip_pos': pet.get('equip_pos'),
                        'position': pet.get('position'),
                        'school': pet.get('school'),
                        'role_grade_limit': pet.get('role_grade_limit'),
                        'min_buyer_level': pet.get('min_buyer_level'),
                        'equip_count': pet.get('equip_count'),
                        'price': pet.get('price'),
                        'price_desc': pet.get('price_desc'),
                        'unit_price_desc': pet.get('unit_price_desc'),
                        'min_unit_price': pet.get('min_unit_price'),
                        'accept_bargain': 1 if pet.get('accept_bargain') else 0,
                        'equip_status': pet.get('equip_status'),
                        'equip_status_desc': pet.get('equip_status_desc'),
                        'status_desc': pet.get('status_desc'),
                        'onsale_expire_time_desc': pet.get('onsale_expire_time_desc'),
                        'time_left': pet.get('time_left'),
                        'expire_time': pet.get('expire_time'),
                        'create_time_equip': pet.get('create_time'),
                        'selling_time': pet.get('selling_time'),
                        'selling_time_ago_desc': pet.get('selling_time_ago_desc'),
                        'first_onsale_time': pet.get('first_onsale_time'),
                        'pass_fair_show': pet.get('pass_fair_show'),
                        'fair_show_time': pet.get('fair_show_time'),
                        'fair_show_end_time': pet.get('fair_show_end_time'),
                        'fair_show_end_time_left': pet.get('fair_show_end_time_left'),
                        'fair_show_poundage': pet.get('fair_show_poundage'),
                        
                        # 宠物属性
                        'hp': pet.get('hp'),
                        'qixue': pet.get('qixue'),
                        'init_hp': pet.get('init_hp'),
                        'mofa': pet.get('mofa'),
                        'init_wakan': pet.get('init_wakan'),
                        'mingzhong': pet.get('mingzhong'),
                        'fangyu': pet.get('fangyu'),
                        'init_defense': pet.get('init_defense'),
                        'defense': pet.get('defense'),
                        'speed': pet.get('speed'),
                        'minjie': pet.get('minjie'),
                        'init_dex': pet.get('init_dex'),
                        'shanghai': pet.get('shanghai'),
                        'damage': pet.get('damage'),
                        'init_damage': pet.get('init_damage'),
                        'init_damage_raw': pet.get('init_damage_raw'),
                        'all_damage': pet.get('all_damage'),
                        'magic_damage': pet.get('magic_damage'),
                        'magic_defense': pet.get('magic_defense'),
                        'lingli': pet.get('lingli'),
                        'fengyin': pet.get('fengyin'),
                        'anti_fengyin': pet.get('anti_fengyin'),
                        'zongshang': pet.get('zongshang'),
                        
                        # 修炼相关
                        'expt_gongji': pet.get('expt_gongji'),
                        'expt_fangyu': pet.get('expt_fangyu'),
                        'expt_fashu': pet.get('expt_fashu'),
                        'expt_kangfa': pet.get('expt_kangfa'),
                        'max_expt_gongji': pet.get('max_expt_gongji'),
                        'max_expt_fangyu': pet.get('max_expt_fangyu'),
                        'max_expt_fashu': pet.get('max_expt_fashu'),
                        'max_expt_kangfa': pet.get('max_expt_kangfa'),
                        'sum_exp': pet.get('sum_exp'),
                        
                        # 宝宝修炼
                        'bb_expt_gongji': pet.get('bb_expt_gongji'),
                        'bb_expt_fangyu': pet.get('bb_expt_fangyu'),
                        'bb_expt_fashu': pet.get('bb_expt_fashu'),
                        'bb_expt_kangfa': pet.get('bb_expt_kangfa'),
                        
                        # 附加属性
                        'addon_tizhi': pet.get('addon_tizhi'),
                        'addon_liliang': pet.get('addon_liliang'),
                        'addon_naili': pet.get('addon_naili'),
                        'addon_minjie': pet.get('addon_minjie'),
                        'addon_fali': pet.get('addon_fali'),
                        'addon_lingli': pet.get('addon_lingli'),
                        'addon_total': pet.get('addon_total'),
                        'addon_status': pet.get('addon_status'),
                        'addon_skill_chance': pet.get('addon_skill_chance'),
                        'addon_effect_chance': pet.get('addon_effect_chance'),
                        
                        # 宝石相关
                        'gem_level': pet.get('gem_level'),
                        'xiang_qian_level': pet.get('xiang_qian_level'),
                        'gem_value': pet.get('gem_value'),
                        
                        # 强化相关
                        'jinglian_level': pet.get('jinglian_level'),
                        
                        # 特技和套装
                        'special_skill': pet.get('special_skill'),
                        'special_effect': pet.get('special_effect'),
                        'suit_skill': pet.get('suit_skill'),
                        'suit_effect': pet.get('suit_effect'),
                        
                        # 其他信息
                        'collect_num': pet.get('collect_num'),
                        'has_collect': 1 if pet.get('has_collect') else 0,
                        'score': pet.get('score'),
                        'icon_index': pet.get('icon_index'),
                        'icon': pet.get('icon'),
                        'equip_face_img': pet.get('equip_face_img'),
                        'kindid': pet.get('kindid'),
                        'game_channel': pet.get('game_channel'),
                        
                        # 订单相关
                        'game_ordersn': pet.get('game_ordersn'),
                        'whole_game_ordersn': pet.get('whole_game_ordersn'),
                        
                        # 跨服相关
                        'allow_cross_buy': pet.get('allow_cross_buy'),
                        'cross_server_poundage': pet.get('cross_server_poundage'),
                        'cross_server_poundage_origin': pet.get('cross_server_poundage_origin'),
                        'cross_server_poundage_discount': pet.get('cross_server_poundage_discount'),
                        'cross_server_poundage_discount_label': pet.get('cross_server_poundage_discount_label'),
                        'cross_server_poundage_display_mode': pet.get('cross_server_poundage_display_mode'),
                        'cross_server_activity_conf_discount': pet.get('cross_server_activity_conf_discount'),
                        
                        # 活动相关
                        'activity_type': pet.get('activity_type'),
                        'joined_seller_activity': 1 if pet.get('joined_seller_activity') else 0,
                        
                        # 拆分相关
                        'is_split_sale': 1 if pet.get('is_split_sale') else 0,
                        'is_split_main_role': 1 if pet.get('is_split_main_role') else 0,
                        'is_split_independent_role': 1 if pet.get('is_split_independent_role') else 0,
                        'is_split_independent_equip': 1 if pet.get('is_split_independent_equip') else 0,
                        'split_equip_sold_happen': 1 if pet.get('split_equip_sold_happen') else 0,
                        'show_split_equip_sold_remind': 1 if pet.get('show_split_equip_sold_remind') else 0,
                        
                        # 保护相关
                        'is_onsale_protection_period': 1 if pet.get('is_onsale_protection_period') else 0,
                        'onsale_protection_end_time': pet.get('onsale_protection_end_time'),
                        'is_vip_protection': 1 if pet.get('is_vip_protection') else 0,
                        'is_time_lock': 1 if pet.get('is_time_lock') else 0,
                        
                        # 测试服相关
                        'equip_in_test_server': 1 if pet.get('equip_in_test_server') else 0,
                        'buyer_in_test_server': 1 if pet.get('buyer_in_test_server') else 0,
                        'equip_in_allow_take_away_server': 1 if pet.get('equip_in_allow_take_away_server') else 0,
                        
                        # 其他标识
                        'is_weijianding': 1 if pet.get('is_weijianding') else 0,
                        'is_show_alipay_privilege': 1 if pet.get('is_show_alipay_privilege') else 0,
                        'is_seller_redpacket_flag': 1 if pet.get('is_seller_redpacket_flag') else 0,
                        'is_show_expert_desc': pet.get('is_show_expert_desc'),
                        'is_show_special_highlight': 1 if pet.get('is_show_special_highlight') else 0,
                        'is_xyq_game_role_kunpeng_reach_limit': 1 if pet.get('is_xyq_game_role_kunpeng_reach_limit') else 0,
                        
                        # 版本和存储相关
                        'equip_onsale_version': pet.get('equip_onsale_version'),
                        'storage_type': pet.get('storage_type'),
                        'agent_trans_time': pet.get('agent_trans_time'),
                        
                        # KOL相关
                        'kol_article_id': pet.get('kol_article_id'),
                        'kol_share_id': pet.get('kol_share_id'),
                        'kol_share_time': pet.get('kol_share_time'),
                        'kol_share_status': pet.get('kol_share_status'),
                        
                        # 推荐相关
                        'reco_request_id': pet.get('reco_request_id'),
                        'appointed_roleid': pet.get('appointed_roleid'),
                        
                        # 团队相关
                        'play_team_cnt': pet.get('play_team_cnt'),
                        
                        # 随机抽奖相关
                        'random_draw_finish_time': pet.get('random_draw_finish_time'),
                        
                        # 详细描述
                        'desc': pet.get('desc'),
                        'large_equip_desc': pet.get('large_equip_desc'),
                        'desc_sumup': pet.get('desc_sumup'),
                        'desc_sumup_short': pet.get('desc_sumup_short'),
                        'diy_desc': pet.get('diy_desc'),
                        'rec_desc': pet.get('rec_desc'),
                        
                        # 搜索相关
                        'search_type': pet.get('search_type'),
                        'tag': pet.get('tag'),
                        
                        # JSON格式字段
                        'price_explanation': json.dumps(pet.get('price_explanation'), ensure_ascii=False) if pet.get('price_explanation') else '',
                        'bargain_info': json.dumps(pet.get('bargain_info'), ensure_ascii=False) if pet.get('bargain_info') else '',
                        'diy_desc_pay_info': json.dumps(pet.get('diy_desc_pay_info'), ensure_ascii=False) if pet.get('diy_desc_pay_info') else '',
                        'other_info': pet.get('other_info', ''),
                        'video_info': json.dumps(pet.get('video_info'), ensure_ascii=False) if pet.get('video_info') else '',
                        'agg_added_attrs': json.dumps(pet.get('agg_added_attrs'), ensure_ascii=False) if pet.get('agg_added_attrs') else '',
                        'dynamic_tags': json.dumps(pet.get('dynamic_tags'), ensure_ascii=False) if pet.get('dynamic_tags') else '',
                        'highlight': json.dumps(pet.get('highlight'), ensure_ascii=False) if pet.get('highlight') else '',
                        'tag_key': pet.get('tag_key', ''),
                        
                        # 原始数据
                        'raw_data_json': json.dumps(pet, ensure_ascii=False)
                    }
                    
                    pets.append(pet_data)
                    
                except Exception as e:
                    self.logger.error(f"解析单个宠物数据时出错: {str(e)}")
                    continue
            
            return pets
            
        except Exception as e:
            self.logger.error(f"解析JSONP响应时发生错误: {str(e)}")
            return None

    def get_search_params(self, use_browser=False):
        """
        获取宠物搜索参数
        - use_browser=True: 启动浏览器手动设置参数
        - use_browser=False: 从本地文件或默认配置加载参数
        """
        params_file = 'config/pet_params.json'
        
        # 强制浏览器模式：如果use_browser为True，则删除旧参数文件
        if use_browser and os.path.exists(params_file):
            self.logger.info(f"强制浏览器模式，删除旧的参数文件: {params_file}")
            os.remove(params_file)

        # 使用同步的参数获取函数
        return get_pet_search_params_sync(use_browser=use_browser)

    def fetch_page_sync(self, page=1, search_params=None, search_type='overall_search_pet'):
        """
        同步获取单页宠物数据
        """
        if search_params is None:
            search_params = {}
        
        # 基础参数
        params = {
            'act': search_type,
            'page': page
        }
        
        # 合并搜索参数
        params.update(search_params)
        
        # 构建URL
        url = 'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py?' + urlencode(params)
        self.logger.info(f"正在请求URL: {url}")
        
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            # 解析JSONP响应
            pets = self.parse_jsonp_response(response.text)
            return pets

        except Exception as e:
            self.logger.error(f"获取宠物数据失败 (页码: {page}): {e}")
            return None

    def save_pet_data(self, pets):
        """保存宠物数据到数据库"""
        if not pets:
            self.logger.info("没有宠物数据需要保存")
            return 0
        
        try:
            # 使用正确的方法名：save_pets_batch
            success = self.smart_db.save_pets_batch(pets)
            if success:
                self.logger.info(f"成功保存 {len(pets)} 条宠物数据到数据库")
                return len(pets)
            else:
                self.logger.error("保存宠物数据到数据库失败")
                return 0
        except Exception as e:
            self.logger.error(f"保存宠物数据到数据库失败: {e}")
            return 0

    async def fetch_page(self, page=1, search_params=None, search_type='overall_search_pet'):
        """
        获取单页宠物数据
        
        Args:
            page: 页码
            search_params: 搜索参数
            search_type: 搜索类型
            
        Returns:
            list: 解析后的宠物数据
        """
        try:
            # 确保search_params不为None
            if search_params is None:
                # 提供一个基础的默认值
                search_params = { 'level_min': 0, 'level_max': 180, 'server_type': 3, 'evol_skill_mode': 0 }

            # 构建请求参数
            params = {
                **search_params,  # 添加搜索参数
                'callback': 'Request.JSONP.request_map.request_0',
                '_': str(int(time.time() * 1000)),
                'act': 'recommd_by_role',
                'page': page,
                'count': 15,
                'search_type': search_type,
                'view_loc': 'overall_search',
            }
            
            # 构建完整URL
            url = f"{self.base_url}?{urlencode(params)}"
            
            # 使用Playwright发送请求
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                
                # 设置cookies
                cookie_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'cookies.txt')
                if os.path.exists(cookie_path):
                    with open(cookie_path, 'r', encoding='utf-8') as f:
                        cookie_str = f.read().strip()
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
                
                page_obj = await context.new_page()
                response = await page_obj.goto(url)
                
                if response:
                    text = await response.text()
                    await browser.close()
                    
                    # 解析响应
                    parsed_result = self.parse_jsonp_response(text)
                    return parsed_result
                
                await browser.close()
                return None
                
        except Exception as e:
            self.logger.error(f"获取宠物第{page}页数据时出错: {e}")
            return None

    async def crawl_all_pages_async(self, max_pages=10, delay_range=None, use_browser=False):
        """
        异步爬取所有宠物页面
        """
        # 首先验证Cookie有效性
        self.logger.info("正在验证Cookie有效性...")
        if not verify_cookie_validity():
            self.logger.warning("Cookie验证失败，正在更新Cookie...")
            from src.utils.cookie_updater import _update_cookies_internal
            if not await _update_cookies_internal():
                self.logger.error("Cookie更新失败，无法继续爬取")
                return
            else:
                self.logger.info("Cookie更新成功，重新设置会话")
                # 重新设置会话
                self.setup_session()
        else:
            self.logger.info("Cookie验证通过")

        search_type = 'overall_search_pet'

        self.logger.info(f"🚀 开始宠物爬取，最大页数: {max_pages}")

        # 获取参数
        params_file = 'config/pet_params.json'
        
        # 强制浏览器模式：如果use_browser为True，则删除旧参数文件
        if use_browser and os.path.exists(params_file):
            self.logger.info(f"强制浏览器模式，删除旧的参数文件: {params_file}")
            os.remove(params_file)
            
        search_params = await get_pet_search_params_async(use_browser=use_browser)

        if not search_params:
            self.logger.error(f"无法获取宠物的搜索参数，爬取中止")
            return
            
        self.logger.info(f"📊 使用搜索参数: {len(search_params)} 个")
        
        total_saved_count = 0
        successful_pages = 0
        
        for page_num in range(1, max_pages + 1):
            try:
                # 确保日志立即输出
                self.logger.info(f"📄 正在爬取宠物第 {page_num} 页...")
                # 强制刷新日志缓冲
                import sys
                sys.stdout.flush()
                
                pets = await self.fetch_page(page_num, search_params, search_type)
                
                if pets is None:
                    self.logger.warning(f"❌ 第 {page_num} 页数据获取失败，尝试重试...")
                    await asyncio.sleep(5) # 等待5秒重试
                    pets = await self.fetch_page(page_num, search_params, search_type)

                if pets:
                    saved_count = self.save_pet_data(pets)
                    total_saved_count += saved_count
                    successful_pages += 1
                    
                    # 打印每条宠物的简要信息
                    for pet in pets:
                        price = pet.get('price_desc', pet.get('price', '未知'))
                        pet_name = pet.get('equip_name', '未知宠物')
                        level = pet.get('level', '未知')
                        server_name = pet.get('server_name', '未知服务器')
                        seller_nickname = pet.get('seller_nickname', '未知卖家')
                        desc_sumup_short = pet.get('desc_sumup_short', '无描述')
                        self.logger.info(f"识别并保存宠物: ￥{price} - {pet_name}({level}级) - {desc_sumup_short} - {server_name} - {seller_nickname}")
                    
                    self.logger.info(f"✅ 第 {page_num} 页完成，获取 {len(pets)} 条宠物，保存 {saved_count} 条")
                else:
                    self.logger.info(f"📄 第 {page_num} 页没有数据，爬取结束")
                    break 

                # 添加延迟
                if delay_range and page_num < max_pages:  # 最后一页不需要延迟
                    delay = random.uniform(delay_range[0], delay_range[1])
                    self.logger.info(f"⏳ 等待 {delay:.2f} 秒后继续...")
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"处理第 {page_num} 页时发生异常: {e}")
                import traceback
                traceback.print_exc()
                break

        self.logger.info(f"🎉 宠物爬取完成！成功页数: {successful_pages}/{max_pages}, 总宠物数: {total_saved_count}")

    def crawl_all_pages(self, max_pages=10, delay_range=None, use_browser=False):
        """
        同步启动异步宠物爬虫的入口
        """
        try:
            asyncio.run(self.crawl_all_pages_async(
                max_pages=max_pages,
                delay_range=delay_range,
                use_browser=use_browser
            ))
        except Exception as e:
            self.logger.error(f"启动宠物爬虫失败: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数，用于测试"""
    async def run_test():
        spider = CBGPetSpider()
        
        # --- 测试配置 ---
        use_browser_for_test = True   # 是否使用浏览器获取参数
        max_pages_to_crawl = 2
        # ----------------
        
        print(f"\n--- 正在测试: 宠物爬虫 ---")
        
        try:
            await spider.crawl_all_pages_async(
                max_pages=max_pages_to_crawl, 
                delay_range=(1, 3), 
                use_browser=use_browser_for_test
            )
            print(f"--- ✅ 宠物爬虫测试完成 ---")
        except Exception as e:
            print(f"--- ❌ 宠物爬虫测试失败: {e} ---")
            import traceback
            traceback.print_exc()

    asyncio.run(run_test())

if __name__ == '__main__':
    main()
