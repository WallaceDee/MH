#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
梦幻西游藏宝阁装备爬虫模块
专门用于爬取装备数据
"""

import os
import sys
import json
import time
import random
import logging
from datetime import datetime
from urllib.parse import urlencode
import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import re
import threading
from concurrent.futures import ThreadPoolExecutor

# 添加项目根目录到Python路径
from src.utils.project_path import get_project_root
project_root = get_project_root()
sys.path.insert(0, project_root)

from src.tools.setup_requests_session import setup_session
from src.database import db
from src.models.equipment import Equipment
from src.tools.search_form_helper import (
    get_equip_search_params_sync,
    get_lingshi_search_params_sync,
    get_pet_equip_search_params_sync,
    get_equip_search_params_async,
    get_lingshi_search_params_async,
    get_pet_equip_search_params_async,
)
from src.utils.cookie_manager import (
    setup_session_with_cookies, 
    get_playwright_cookies_for_context,
    verify_cookie_validity
)

# 导入特征提取器
from src.evaluator.feature_extractor.lingshi_feature_extractor import LingshiFeatureExtractor
from src.evaluator.feature_extractor.pet_equip_feature_extractor import PetEquipFeatureExtractor
from src.evaluator.feature_extractor.equip_feature_extractor import EquipFeatureExtractor

# 导入装备类型常量
from src.evaluator.constants.equipment_types import LINGSHI_KINDIDS, PET_EQUIP_KINDID,WEAPON_KINDIDS,ARMOR_KINDIDS

class CBGEquipSpider:
    def __init__(self):
        self.session = setup_session()
        self.base_url = 'https://xyq.cbg.163.com/cgi-bin/recommend.py'
        self.output_dir = self.create_output_dir()
        
        # 初始化特征提取器
        self.lingshi_feature_extractor = LingshiFeatureExtractor()
        self.pet_equip_feature_extractor = PetEquipFeatureExtractor()
        self.equip_feature_extractor = EquipFeatureExtractor()
        # 配置专用的日志器，避免与其他模块冲突
        self.logger = self._setup_logger()
        
        # 初始化其他组件
        self.setup_session()
        self.retry_attempts = 1
        
        # 初始化线程池（用于异步数据库操作）
        self._executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix='EquipDB-')
        self.logger.info("线程池初始化完成，最大并发数: 3")

    def _setup_logger(self):
        """设置专用的日志器"""
        # 创建专用的日志器
        logger = logging.getLogger(f'CBGEquipSpider_{id(self)}')
        logger.setLevel(logging.INFO)
        
        # 清除可能存在的处理器，避免重复日志
        if logger.handlers:
            logger.handlers.clear()
        
        # 创建文件处理器
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(self.output_dir, f'cbg_equip_spider_{timestamp}.log')
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
        logger.info(" CBG装备爬虫日志系统初始化完成")
        logger.info(f" 日志文件路径: {log_file}")
        
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
        # 使用统一的Cookie管理
        setup_session_with_cookies(
            self.session, 
            referer='https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py',
            logger=self.logger
        )
    

    def parse_jsonp_response(self, text):
        """解析JSONP响应，提取装备数据"""
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
                self.logger.warning("没有找到任何装备数据")
                return []
                
            equipments = []
            for equip in equip_list:
                try:
                    # 特征提取：当kindid是61、62、63、64时，提取灵饰特征
                    kindid = equip.get('kindid', 0)
                    extracted_attrs = []
                    
                    if kindid in LINGSHI_KINDIDS:  # 灵饰装备类型
                        try:
                            # 使用特征提取器提取附加属性
                            added_attrs_features = self.lingshi_feature_extractor._extract_added_attrs_features(equip)
                            extracted_attrs = added_attrs_features.get('attrs', [])
                            
                            if extracted_attrs:
                                self.logger.debug(f"成功提取灵饰装备(kindid:{kindid})的附加属性: {len(extracted_attrs)}个")
                                # 记录提取到的具体属性
                                for i, attr in enumerate(extracted_attrs):
                                    self.logger.debug(f"  属性{i+1}: {attr['attr_type']} +{attr['attr_value']}")
                            else:
                                self.logger.debug(f"灵饰装备(kindid:{kindid})未提取到附加属性")
                                
                        except Exception as e:
                            self.logger.warning(f"提取灵饰装备特征失败 (kindid:{kindid}): {e}")
                            # 如果特征提取失败，使用原始数据
                            extracted_attrs = equip.get('agg_added_attrs', [])
                    else:
                        # 非灵饰装备，使用原始数据
                        extracted_attrs = equip.get('agg_added_attrs', [])
                    
                    # 初始化 addon_status 变量
                    addon_status = equip.get('addon_status', '')
                    addon_moli = equip.get('addon_moli', 0)

                    if kindid == PET_EQUIP_KINDID:  # 召唤兽装备类型要解析套装
                        try:
                            # 使用召唤兽装备特征提取器解析套装信息
                            desc = equip.get('large_equip_desc', '')
                            if desc:
                                # 创建临时字典来存储解析结果
                                parsed_data = {}
                                self.pet_equip_feature_extractor._parse_suit_info_from_desc(desc, parsed_data)
                                addon_status = parsed_data.get('addon_status', '')
                                print(f"召唤兽装备套装解析结果: {addon_status}")
                                self.logger.debug(f"召唤兽装备套装解析结果: {addon_status}")
                        except Exception as e:
                            self.logger.warning(f"解析召唤兽装备套装信息失败: {e}")
                            # 保持原始值

                    if kindid in WEAPON_KINDIDS + ARMOR_KINDIDS:
                        addon_moli = self.equip_feature_extractor._extract_moli_from_agg_added_attrs(equip.get('agg_added_attrs', '[]'))

                    # 直接保存所有原始字段，不做解析
                    equipment = {
                        # 基本字段直接映射
                        'eid': equip.get('eid'),
                        'equipid': equip.get('equipid'),
                        'equip_sn': equip.get('equip_sn'),
                        'server_name': equip.get('server_name'),
                        'serverid': equip.get('serverid'),
                        'equip_server_sn': equip.get('equip_server_sn'),
                        'seller_nickname': equip.get('seller_nickname'),
                        'seller_roleid': equip.get('seller_roleid'),
                        'area_name': equip.get('area_name'),
                        'equip_name': equip.get('equip_name'),
                        'equip_type': equip.get('equip_type'),
                        'equip_type_name': equip.get('equip_type_name'),
                        'equip_type_desc': equip.get('equip_type_desc'),
                        'level': equip.get('level'),
                        'equip_level': equip.get('equip_level'),
                        'equip_level_desc': equip.get('equip_level_desc'),
                        'level_desc': equip.get('level_desc'),
                        'subtitle': equip.get('subtitle'),
                        'equip_pos': equip.get('equip_pos'),
                        'position': equip.get('position'),
                        'school': equip.get('school'),
                        'role_grade_limit': equip.get('role_grade_limit'),
                        'min_buyer_level': equip.get('min_buyer_level'),
                        'equip_count': equip.get('equip_count'),
                        'price': equip.get('price'),
                        'price_desc': equip.get('price_desc'),
                        'unit_price_desc': equip.get('unit_price_desc'),
                        'min_unit_price': equip.get('min_unit_price'),
                        'accept_bargain': 1 if equip.get('accept_bargain') else 0,
                        'equip_status': equip.get('equip_status'),
                        'equip_status_desc': equip.get('equip_status_desc'),
                        'status_desc': equip.get('status_desc'),
                        'onsale_expire_time_desc': equip.get('onsale_expire_time_desc'),
                        'time_left': equip.get('time_left'),
                        'expire_time': equip.get('expire_time'),
                        'create_time_equip': equip.get('create_time'),
                        'selling_time': equip.get('selling_time'),
                        'selling_time_ago_desc': equip.get('selling_time_ago_desc'),
                        'first_onsale_time': equip.get('first_onsale_time'),
                        'pass_fair_show': equip.get('pass_fair_show'),
                        'fair_show_time': equip.get('fair_show_time'),
                        'fair_show_end_time': equip.get('fair_show_end_time'),
                        'fair_show_end_time_left': equip.get('fair_show_end_time_left'),
                        'fair_show_poundage': equip.get('fair_show_poundage'),
                        
                        # 装备属性
                        'hp': equip.get('hp'),
                        'qixue': equip.get('qixue'),
                        'init_hp': equip.get('init_hp'),
                        'mofa': equip.get('mofa'),
                        'init_wakan': equip.get('init_wakan'),
                        'mingzhong': equip.get('mingzhong'),
                        'fangyu': equip.get('fangyu'),
                        'init_defense': equip.get('init_defense'),
                        'defense': equip.get('defense'),
                        'speed': equip.get('speed'),
                        'minjie': equip.get('minjie'),
                        'init_dex': equip.get('init_dex'),
                        'shanghai': equip.get('shanghai'),
                        'damage': equip.get('damage'),
                        'init_damage': equip.get('init_damage'),
                        'init_damage_raw': equip.get('init_damage_raw'),
                        'all_damage': equip.get('all_damage'),
                        'magic_damage': equip.get('magic_damage'),
                        'magic_defense': equip.get('magic_defense'),
                        'lingli': equip.get('lingli'),
                        'fengyin': equip.get('fengyin'),
                        'anti_fengyin': equip.get('anti_fengyin'),
                        'zongshang': equip.get('zongshang'),
                        
                        # 修炼相关
                        'expt_gongji': equip.get('expt_gongji'),
                        'expt_fangyu': equip.get('expt_fangyu'),
                        'expt_fashu': equip.get('expt_fashu'),
                        'expt_kangfa': equip.get('expt_kangfa'),
                        'max_expt_gongji': equip.get('max_expt_gongji'),
                        'max_expt_fangyu': equip.get('max_expt_fangyu'),
                        'max_expt_fashu': equip.get('max_expt_fashu'),
                        'max_expt_kangfa': equip.get('max_expt_kangfa'),
                        'sum_exp': equip.get('sum_exp'),
                        
                        # 宝宝修炼
                        'bb_expt_gongji': equip.get('bb_expt_gongji'),
                        'bb_expt_fangyu': equip.get('bb_expt_fangyu'),
                        'bb_expt_fashu': equip.get('bb_expt_fashu'),
                        'bb_expt_kangfa': equip.get('bb_expt_kangfa'),
                        
                        # 附加属性
                        'addon_tizhi': equip.get('addon_tizhi'),
                        'addon_liliang': equip.get('addon_liliang'),
                        'addon_naili': equip.get('addon_naili'),
                        'addon_minjie': equip.get('addon_minjie'),
                        'addon_fali': equip.get('addon_fali'),
                        'addon_lingli': equip.get('addon_lingli'),
                        'addon_moli': addon_moli,
                        'addon_total': equip.get('addon_total'),
                        'addon_status': addon_status,
                        'addon_skill_chance': equip.get('addon_skill_chance'),
                        'addon_effect_chance': equip.get('addon_effect_chance'),
                        
                        # 宝石相关
                        'gem_level': equip.get('gem_level'),
                        'xiang_qian_level': equip.get('xiang_qian_level'),
                        
                        # 强化相关
                        'jinglian_level': equip.get('jinglian_level'),
                        
                        # 特技和套装
                        'special_skill': equip.get('special_skill'),
                        'special_effect': json.dumps(equip.get('special_effect'), ensure_ascii=False) if equip.get('special_effect') else '',
                        'suit_skill': equip.get('suit_skill'),
                        'suit_effect': equip.get('suit_effect'),
                        
                        # 其他信息
                        'collect_num': equip.get('collect_num'),
                        'has_collect': 1 if equip.get('has_collect') else 0,
                        'score': equip.get('score'),
                        'icon_index': equip.get('icon_index'),
                        'icon': equip.get('icon'),
                        'equip_face_img': equip.get('equip_face_img'),
                        'kindid': equip.get('kindid'),
                        'game_channel': equip.get('game_channel'),
                        
                        # 订单相关
                        'game_ordersn': equip.get('game_ordersn'),
                        'whole_game_ordersn': equip.get('whole_game_ordersn'),
                        
                        # 跨服相关
                        'allow_cross_buy': equip.get('allow_cross_buy'),
                        'cross_server_poundage': equip.get('cross_server_poundage'),
                        'cross_server_poundage_origin': equip.get('cross_server_poundage_origin'),
                        'cross_server_poundage_discount': equip.get('cross_server_poundage_discount'),
                        'cross_server_poundage_discount_label': equip.get('cross_server_poundage_discount_label'),
                        'cross_server_poundage_display_mode': equip.get('cross_server_poundage_display_mode'),
                        'cross_server_activity_conf_discount': equip.get('cross_server_activity_conf_discount'),
                        
                        # 活动相关
                        'activity_type': equip.get('activity_type'),
                        'joined_seller_activity': 1 if equip.get('joined_seller_activity') else 0,
                        
                        # 拆分相关
                        'is_split_sale': 1 if equip.get('is_split_sale') else 0,
                        'is_split_main_role': 1 if equip.get('is_split_main_role') else 0,
                        'is_split_independent_role': 1 if equip.get('is_split_independent_role') else 0,
                        'is_split_independent_equip': 1 if equip.get('is_split_independent_equip') else 0,
                        'split_equip_sold_happen': 1 if equip.get('split_equip_sold_happen') else 0,
                        'show_split_equip_sold_remind': 1 if equip.get('show_split_equip_sold_remind') else 0,
                        
                        # 保护相关
                        'is_onsale_protection_period': 1 if equip.get('is_onsale_protection_period') else 0,
                        'onsale_protection_end_time': equip.get('onsale_protection_end_time'),
                        'is_vip_protection': 1 if equip.get('is_vip_protection') else 0,
                        'is_time_lock': 1 if equip.get('is_time_lock') else 0,
                        
                        # 测试服相关
                        'equip_in_test_server': 1 if equip.get('equip_in_test_server') else 0,
                        'buyer_in_test_server': 1 if equip.get('buyer_in_test_server') else 0,
                        'equip_in_allow_take_away_server': 1 if equip.get('equip_in_allow_take_away_server') else 0,
                        
                        # 其他标识
                        'is_weijianding': 1 if equip.get('is_weijianding') else 0,
                        'is_show_alipay_privilege': 1 if equip.get('is_show_alipay_privilege') else 0,
                        'is_seller_redpacket_flag': 1 if equip.get('is_seller_redpacket_flag') else 0,
                        'is_show_expert_desc': equip.get('is_show_expert_desc'),
                        'is_show_special_highlight': 1 if equip.get('is_show_special_highlight') else 0,
                        'is_xyq_game_role_kunpeng_reach_limit': 1 if equip.get('is_xyq_game_role_kunpeng_reach_limit') else 0,
                        
                        # 版本和存储相关
                        'equip_onsale_version': equip.get('equip_onsale_version'),
                        'storage_type': equip.get('storage_type'),
                        'agent_trans_time': equip.get('agent_trans_time'),
                        
                        # KOL相关
                        'kol_article_id': equip.get('kol_article_id'),
                        'kol_share_id': equip.get('kol_share_id'),
                        'kol_share_time': equip.get('kol_share_time'),
                        'kol_share_status': equip.get('kol_share_status'),
                        
                        # 推荐相关
                        'reco_request_id': equip.get('reco_request_id'),
                        'appointed_roleid': equip.get('appointed_roleid'),
                        
                        # 团队相关
                        'play_team_cnt': equip.get('play_team_cnt'),
                        
                        # 随机抽奖相关
                        'random_draw_finish_time': equip.get('random_draw_finish_time'),
                        
                        # 详细描述
                        'desc': equip.get('desc'),
                        'large_equip_desc': equip.get('large_equip_desc'),
                        'desc_sumup': equip.get('desc_sumup'),
                        'desc_sumup_short': equip.get('desc_sumup_short'),
                        'diy_desc': equip.get('diy_desc'),
                        'rec_desc': equip.get('rec_desc'),
                        
                        # 搜索相关
                        'search_type': equip.get('search_type'),
                        'tag': equip.get('tag'),
                        
                        # JSON格式字段
                        'gem_value': json.dumps(equip.get('gem_value'), ensure_ascii=False) if equip.get('gem_value') else '',
                        'price_explanation': json.dumps(equip.get('price_explanation'), ensure_ascii=False) if equip.get('price_explanation') else '',
                        'bargain_info': json.dumps(equip.get('bargain_info'), ensure_ascii=False) if equip.get('bargain_info') else '',
                        'diy_desc_pay_info': json.dumps(equip.get('diy_desc_pay_info'), ensure_ascii=False) if equip.get('diy_desc_pay_info') else '',
                        'other_info': equip.get('other_info', ''),
                        'video_info': json.dumps(equip.get('video_info'), ensure_ascii=False) if equip.get('video_info') else '',
                        'agg_added_attrs': json.dumps(extracted_attrs, ensure_ascii=False) if extracted_attrs else '',
                        'dynamic_tags': json.dumps(equip.get('dynamic_tags'), ensure_ascii=False) if equip.get('dynamic_tags') else '',
                        'highlight': json.dumps(equip.get('highlight'), ensure_ascii=False) if equip.get('highlight') else '',
                        'tag_key': equip.get('tag_key', ''),
                        
                        # 原始数据
                        'raw_data_json': json.dumps(equip, ensure_ascii=False)
                    }
                    
                    equipments.append(equipment)
                    
                except Exception as e:
                    self.logger.error(f"解析单个装备数据时出错: {str(e)}")
                    continue
            
            return equipments
            
        except Exception as e:
            self.logger.error(f"解析JSONP响应时发生错误: {str(e)}")
            return None

    def get_search_params(self, use_browser=False, equip_type='normal'):
        """
        获取装备搜索参数
        - use_browser=True: 启动浏览器手动设置参数
        - use_browser=False: 从本地文件或默认配置加载参数
        - equip_type: 'normal', 'lingshi', 'pet'
        """
        params_file = f'config/equip_params_{equip_type}.json'
        
        # 强制浏览器模式：如果use_browser为True，则删除旧参数文件
        if use_browser and os.path.exists(params_file):
            self.logger.info(f"强制浏览器模式，删除旧的参数文件: {params_file}")
            os.remove(params_file)

        # 根据同步/异步模式选择不同的参数获取函数
        # （当前爬虫是同步的，所以使用同步函数）
        params_getter_map = {
            'normal': get_equip_search_params_sync,
            'lingshi': get_lingshi_search_params_sync,
            'pet': get_pet_equip_search_params_sync
        }

        if equip_type not in params_getter_map:
            raise ValueError(f"不支持的装备类型: {equip_type}")

        return params_getter_map[equip_type](use_browser=use_browser)

    def fetch_page_sync(self, page=1, search_params=None, search_type='overall_search_equip'):
        """
        同步获取单页装备数据
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
            equipments = self.parse_jsonp_response(response.text)
            return equipments

        except Exception as e:
            self.logger.error(f"获取装备数据失败 (页码: {page}): {e}")
            return None

    def save_equipment_data(self, equipments):
        """保存装备数据到MySQL数据库"""
        if not equipments:
            self.logger.info("没有装备数据需要保存")
            return 0
        
        try:
            # 确保在Flask应用上下文中执行数据库操作
            from flask import current_app
            from src.app import create_app
            
            # 如果当前没有应用上下文，创建一个
            if not current_app:
                app = create_app()
                with app.app_context():
                    return self._save_equipment_data_with_context(equipments)
            else:
                return self._save_equipment_data_with_context(equipments)
                
        except Exception as e:
            self.logger.error(f"保存装备数据到MySQL数据库失败: {e}")
            return 0
    
    def _filter_equipment_fields(self, equipments):
        """
        过滤装备字段，只保留缓存所需字段（优化内存占用）
        
        Args:
            equipments: 装备数据列表
            
        Returns:
            list: 过滤后的装备数据列表
        """
        from src.evaluator.constants.equipment_types import EQUIPMENT_CACHE_REQUIRED_FIELDS
        
        # 使用列表推导式，更高效
        return [
            {k: v for k, v in equipment.items() if k in EQUIPMENT_CACHE_REQUIRED_FIELDS}
            for equipment in equipments
        ]
    
    def _get_redis_total_count(self):
        """
        获取Redis中的装备总条数
        
        Returns:
            int: Redis中的装备总条数，获取失败返回0
        """
        try:
            from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
            from src.utils.redis_cache import get_redis_cache
            
            collector = EquipMarketDataCollector.get_instance()
            redis_cache = get_redis_cache()
            
            if redis_cache and redis_cache.is_available():
                # 获取Redis Hash的总条数
                full_key = redis_cache._make_key(collector._full_cache_key)
                total_count = redis_cache.client.hlen(full_key)
                self.logger.debug(f"Redis装备总条数: {total_count}")
                return total_count
            else:
                self.logger.warning("Redis不可用，无法获取总条数")
                return 0
                
        except Exception as e:
            self.logger.warning(f"获取Redis总条数失败: {e}")
            return 0
    
    def _publish_dataframe_message(self, new_data_df, data_count):
        """
        发布DataFrame消息到Redis（立即通知前端，只更新内存数据，不包含总数）
        
        Args:
            new_data_df: DataFrame数据
            data_count: 本次新增的数据条数
            
        Returns:
            bool: 发布是否成功
        """
        try:
            from src.utils.redis_pubsub import get_redis_pubsub, MessageType, Channel
            
            pubsub = get_redis_pubsub()
            message = {
                'type': MessageType.EQUIPMENT_DATA_SAVED,
                'data_count': data_count,  # 本次数据量
                'action': 'add_dataframe'  # 只用于立即更新内存缓存
            }
            
            success = pubsub.publish_with_dataframe(Channel.EQUIPMENT_UPDATES, message, new_data_df)
            if success:
                self.logger.info(f"📢 已立即发布DataFrame消息到Redis (本次:{data_count}条)")
            else:
                self.logger.warning("⚠️ 发布DataFrame消息失败")
            
            return success
            
        except Exception as e:
            self.logger.warning(f"⚠️ 发布DataFrame消息失败: {e}")
            return False
    
    def _batch_save_to_mysql(self, equipments):
        """
        批量保存到MySQL，优化数据库查询性能
        
        Args:
            equipments: 装备数据列表
            
        Returns:
            tuple: (新增数量, 更新数量)
        """
        try:
            # 批量查询已存在的装备（一次查询代替N次查询）
            equip_sns = [eq.get('equip_sn') for eq in equipments if eq.get('equip_sn')]
            
            existing_equipments = {}
            if equip_sns:
                existing_list = db.session.query(Equipment).filter(
                    Equipment.equip_sn.in_(equip_sns)
                ).all()
                existing_equipments = {eq.equip_sn: eq for eq in existing_list}
            
            new_equipments = []
            updated_count = 0
            
            # 遍历装备数据，分类为新增和更新
            for equipment_data in equipments:
                try:
                    equip_sn = equipment_data.get('equip_sn')
                    
                    if equip_sn and equip_sn in existing_equipments:
                        # 更新现有记录
                        existing = existing_equipments[equip_sn]
                        for key, value in equipment_data.items():
                            if hasattr(existing, key):
                                setattr(existing, key, value)
                        existing.update_time = datetime.now()
                        updated_count += 1
                    else:
                        # 准备新记录
                        new_equipments.append(Equipment(**equipment_data))
                        
                except Exception as e:
                    self.logger.error(f"处理单个装备数据失败: {e}")
                    continue
            
            # 批量插入新记录
            if new_equipments:
                db.session.bulk_save_objects(new_equipments)
            
            # 提交事务
            db.session.commit()
            
            if len(new_equipments) > 0:
                self.logger.info(f"✅ 成功保存 {len(new_equipments)} 条新装备数据到MySQL数据库")
            if updated_count > 0:
                self.logger.info(f"✅ 更新 {updated_count} 条已存在的装备数据")
            
            return len(new_equipments), updated_count
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"批量保存MySQL失败: {e}")
            raise
    
    def _sync_to_redis_cache(self, new_data_df):
        """
        同步新数据到Redis缓存
        
        Args:
            new_data_df: 新数据的DataFrame
            
        Returns:
            bool: 同步是否成功
        """
        try:
            from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
            
            collector = EquipMarketDataCollector.get_instance()
            redis_success = collector._sync_new_data_to_redis(new_data_df)
            
            if redis_success:
                self.logger.info("✅ 新数据已同步到Redis缓存")
            else:
                self.logger.warning("⚠️ 新数据同步到Redis失败")
            
            return redis_success
            
        except Exception as e:
            self.logger.warning(f"⚠️ 同步新数据到Redis失败: {e}")
            return False
    
    def _save_equipment_data_with_context(self, equipments):
        """在Flask应用上下文中保存装备数据 - 内存缓存优先快速响应 → MySQL → Redis"""
        try:
            # 在子线程中重新导入pandas，确保可用
            import pandas as pd
            
            if not equipments:
                self.logger.info("没有装备数据需要保存")
                return 0
            
            self.logger.info(f"开始保存 {len(equipments)} 条装备数据...")
            
            # 优化：只过滤一次，避免重复代码
            filtered_equipments = self._filter_equipment_fields(equipments)
            new_data_df = pd.DataFrame(filtered_equipments)
            
            # 第一步：立即发布DataFrame消息，快速更新内存缓存（最高优先级，超快响应）
            publish_success = self._publish_dataframe_message(new_data_df, len(equipments))
            
            if publish_success:
                self.logger.info(f"✅ 已立即通知内存缓存更新 {len(equipments)} 条数据（快速响应）")
            else:
                self.logger.warning(f"⚠️ 内存缓存通知发送失败，但继续保存到数据库")
            
            # 第二步：异步批量保存到MySQL和Redis（不阻塞主流程）
            self._submit_async_save_task(equipments, new_data_df)
            
            self.logger.info(f"🎉 装备数据保存流程: 内存缓存(✅已通知) → MySQL(处理中) → Redis(处理中)")
            
            # 返回预估的新增数量（实际数量由异步任务计算）
            return len(equipments)
            
        except Exception as e:
            self.logger.error(f"保存装备数据失败: {e}")
            return 0
    
    def _submit_async_save_task(self, equipments, new_data_df):
        """
        提交异步保存任务到线程池
        
        Args:
            equipments: 装备数据列表
            new_data_df: 过滤后的DataFrame
        """
        try:
            # 使用线程池异步执行保存任务
            future = self._executor.submit(
                self._async_batch_save_worker,
                equipments,
                new_data_df
            )
            
            # 添加完成回调，记录结果
            future.add_done_callback(self._async_save_callback)
            
        except Exception as e:
            self.logger.error(f"❌ 提交异步保存任务失败: {e}")
    
    def _async_save_callback(self, future):
        """异步保存任务完成回调 - 记录MySQL和Redis保存结果"""
        try:
            result = future.result()
            if result:
                saved_count, updated_count, saved_dataframe, redis_synced = result
                self.logger.info(
                    f"✅ 异步保存完成: 新增 {saved_count} 条, 更新 {updated_count} 条, Redis同步: {'成功' if redis_synced else '失败'}"
                )
                
                # 内存缓存已在主线程中立即更新，这里不再发送消息
                if saved_count > 0 and redis_synced:
                    self.logger.info(f"✅ MySQL和Redis保存成功，数据一致性已保证")
                elif saved_count > 0 and not redis_synced:
                    self.logger.warning(f"⚠️ MySQL保存成功但Redis同步失败，内存和MySQL已有数据，需手动同步Redis")
                elif updated_count > 0:
                    self.logger.info(f"📝 无新增数据，更新了 {updated_count} 条现有数据")
                
        except Exception as e:
            self.logger.error(f"❌ 异步保存任务执行失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def _publish_save_complete_message(self, saved_count, updated_count):
        """
        发布保存完成消息（可选，用于显示实际新增和更新数量）
        
        Args:
            saved_count: 新增数量
            updated_count: 更新数量
        """
        try:
            from src.utils.redis_pubsub import get_redis_pubsub, MessageType, Channel
            
            pubsub = get_redis_pubsub()
            message = {
                'type': MessageType.EQUIPMENT_DATA_SAVED,
                'data_count': saved_count,  # 本次实际新增数量
                'updated_count': updated_count,  # 本次更新数量
                'action': 'save_complete'  # 标识这是保存完成消息
            }
            
            # 不需要DataFrame，只发送消息
            success = pubsub.publish(Channel.EQUIPMENT_UPDATES, message)
            if success:
                self.logger.info(f"📢 已发布保存完成消息 (新增:{saved_count}, 更新:{updated_count})")
            
        except Exception as e:
            self.logger.warning(f"⚠️ 发布保存完成消息失败: {e}")
    
    def _async_batch_save_worker(self, equipments, new_data_df):
        """
        异步批量保存工作线程（在线程池中执行）- MySQL → Redis → 通知内存缓存
        
        Args:
            equipments: 装备数据列表
            new_data_df: 过滤后的DataFrame
            
        Returns:
            tuple: (新增数量, 更新数量, 实际保存的DataFrame, Redis同步状态)
        """
        try:
            # 在Flask应用上下文中执行数据库操作
            from src.app import create_app
            app = create_app()
            
            with app.app_context():
                self.logger.info(f"🔄 异步任务开始处理 {len(equipments)} 条装备数据...")
                
                # 第一步：批量保存到MySQL
                saved_count, updated_count = self._batch_save_to_mysql(equipments)
                
                # 第二步：同步到Redis（只在有新数据时）
                redis_synced = False
                saved_dataframe = None
                
                if saved_count > 0:
                    # 同步到Redis缓存
                    redis_synced = self._sync_to_redis_cache(new_data_df)
                    
                    if redis_synced:
                        # 返回实际新增的数据（用于通知内存缓存更新）
                        saved_dataframe = new_data_df.copy()
                        self.logger.info(f"✅ MySQL和Redis保存成功，准备通知内存缓存更新")
                    else:
                        self.logger.warning(f"⚠️ MySQL保存成功但Redis同步失败，不更新内存缓存")
                
                return saved_count, updated_count, saved_dataframe, redis_synced
                
        except Exception as e:
            self.logger.error(f"❌ 异步批量保存工作线程失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return 0, 0, None, False
    
    def __del__(self):
        """析构方法，确保线程池正确关闭"""
        try:
            if hasattr(self, '_executor'):
                self.logger.info("正在关闭线程池...")
                self._executor.shutdown(wait=True, cancel_futures=False)
                self.logger.info("线程池已关闭")
        except Exception as e:
            # 析构时可能logger已经被回收
            print(f"关闭线程池时出错: {e}")

    async def fetch_page(self, page=1, search_params=None, search_type='overall_search_equip'):
        """
        获取单页装备数据
        
        Args:
            page: 页码
            search_params: 搜索参数
            search_type: 搜索类型
            
        Returns:
            list: 解析后的装备数据
        """
        try:
            # 确保search_params不为None
            if search_params is None:
                # 根据search_type提供一个基础的默认值
                if search_type == 'overall_search_lingshi':
                    search_params = { 'level_min': 60, 'level_max': 140 }
                elif search_type == 'overall_search_pet_equip':
                    search_params = { 'level_min': 5, 'level_max': 145 }
                else:
                    search_params = { 'level_min': 60, 'level_max': 160 }

            # 构建请求参数
            params = {
                **search_params,  # 添加搜索参数
                'callback': 'Request.JSONP.request_map.request_0',
                '_': str(int(time.time() * 1000)),
                'act': 'recommd_by_role',
                'page': page,
                'count': 15,
                'search_type': search_type,
                'server_type': 3,# 默认3年外服务器
            }
            
            # 构建完整URL
            url = f"{self.base_url}?{urlencode(params)}"
            
            # 使用Playwright发送请求
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                
                # 设置cookies
                cookies = get_playwright_cookies_for_context(self.logger)
                if cookies:
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
            self.logger.error(f"获取装备第{page}页数据时出错: {e}")
            return None

    async def crawl_all_pages_async(self, max_pages=10, delay_range=None, use_browser=False, equip_type='normal', cached_params=None):
        """
        异步爬取所有装备页面
        - equip_type: 'normal', 'lingshi', 'pet'
        """
        # 首先验证Cookie有效性
        self.logger.info("正在验证Cookie有效性...")
        print("即将调用 verify_cookie_validity_async")
        from src.utils.cookie_manager import verify_cookie_validity_async
        is_valid = await verify_cookie_validity_async(self.logger)
        print("verify_cookie_validity_async 返回：", is_valid)
        if not is_valid:
            self.logger.warning("Cookie验证失败，正在更新Cookie...")
            from src.utils.cookie_manager import _update_cookies_internal
            if not await _update_cookies_internal():
                self.logger.error("Cookie更新失败，无法继续爬取")
                return
            else:
                self.logger.info("Cookie更新成功，重新设置会话")
                # 重新设置会话
                self.setup_session()
        else:
            self.logger.info("Cookie验证通过")

        search_type_map = {
            'normal': 'overall_search_equip',
            'lingshi': 'overall_search_lingshi',
            'pet': 'overall_search_pet_equip',
        }
        search_type = search_type_map.get(equip_type)
        if not search_type:
            self.logger.error(f"未知的装备类型: {equip_type}")
            return

        self.logger.info(f" 开始 {equip_type} 装备爬取，最大页数: {max_pages}")

        # 获取参数
        params_getter_async_map = {
            'normal': get_equip_search_params_async,
            'lingshi': get_lingshi_search_params_async,
            'pet': get_pet_equip_search_params_async
        }
        params_file = f'config/equip_params_{equip_type}.json'
        
        # 强制浏览器模式：如果use_browser为True，则删除旧参数文件
        if use_browser and os.path.exists(params_file):
            self.logger.info(f"强制浏览器模式，删除旧的参数文件: {params_file}")
            os.remove(params_file)
        
        # 使用传入的缓存参数或获取新参数
        if cached_params and not use_browser:
            if 'server_id' in cached_params:
                # 去掉search_type中的'overall_'
                if equip_type == 'normal':
                    search_type = 'search_role_equip'
                else:
                    search_type = search_type.replace('overall_', '')
            search_params = cached_params
            self.logger.info(f" 使用传入的缓存参数: {len(search_params)} 个")
        else:
            search_params = await params_getter_async_map[equip_type](use_browser=use_browser)
            if search_params:
                self.logger.info(f" 使用搜索参数: {len(search_params)} 个")

        if not search_params:
            self.logger.error(f"无法获取 {equip_type} 装备的搜索参数，爬取中止")
            return
            
        total_saved_count = 0
        successful_pages = 0
        
        for page_num in range(1, max_pages + 1):
            try:
                # 确保日志立即输出
                self.logger.info(f"📄 正在爬取 {equip_type} 装备第 {page_num} 页...")
                # 强制刷新日志缓冲
                import sys
                sys.stdout.flush()
                
                equipments = await self.fetch_page(page_num, search_params, search_type)
                
                if equipments is None:
                    self.logger.warning(f" 第 {page_num} 页数据获取失败，尝试重试...")
                    await asyncio.sleep(5) # 等待5秒重试
                    equipments = await self.fetch_page(page_num, search_params, search_type)

                if equipments:
                    saved_count = self.save_equipment_data(equipments)
                    total_saved_count += saved_count
                    successful_pages += 1
                    
                    # 打印每条装备的简要信息
                    for equipment in equipments:
                        price = equipment.get('price_desc', equipment.get('price', '未知'))
                        equip_name = equipment.get('equip_name', '未知装备')
                        level = equipment.get('level', '未知')
                        server_name = equipment.get('server_name', '未知服务器')
                        seller_nickname = equipment.get('seller_nickname', '未知卖家')
                        self.logger.info(f"￥{price} - {equip_name}({level}级) - {server_name} - {seller_nickname}")
                    
                    self.logger.info(f" 第 {page_num} 页完成，获取 {len(equipments)} 条装备，保存 {saved_count} 条")
                    
                    # 判断数据条数是否不足10条，如果不足则说明没有下一页
                    if len(equipments) < 10:
                        self.logger.info(f"📄 第 {page_num} 页数据条数({len(equipments)})不足10条，判断为最后一页，爬取结束")
                        break
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

        self.logger.info(f" {equip_type} 装备爬取完成！成功页数: {successful_pages}/{max_pages}, 总装备数: {total_saved_count}")
        
        # 强制刷新所有日志缓冲区，确保日志被完整写入文件
        import sys
        sys.stdout.flush()
        sys.stderr.flush()
        
        # 刷新日志处理器缓冲区
        for handler in self.logger.handlers:
            if hasattr(handler, 'flush'):
                handler.flush()

    def crawl_all_pages(self, max_pages=10, delay_range=None, use_browser=False, equip_type='normal', cached_params=None):
        """
        同步启动异步装备爬虫的入口
        """
        try:
            asyncio.run(self.crawl_all_pages_async(
                max_pages=max_pages,
                delay_range=delay_range,
                use_browser=use_browser,
                equip_type=equip_type,
                cached_params=cached_params
            ))
        except Exception as e:
            self.logger.error(f"启动装备爬虫失败: {e}")
            import traceback
            traceback.print_exc()