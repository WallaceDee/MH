#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
梦幻西游藏宝阁召唤兽爬虫模块
专门用于爬取召唤兽（召唤兽）数据
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
import threading
from concurrent.futures import ThreadPoolExecutor

# 添加项目根目录到Python路径
from src.utils.project_path import get_project_root
project_root = get_project_root()
sys.path.insert(0, project_root)

from src.tools.setup_requests_session import setup_session
from src.database import db
from src.models.pet import Pet
from src.tools.search_form_helper import (
    get_pet_search_params_sync,
    get_pet_search_params_async
)
from src.utils.cookie_manager import (
    setup_session_with_cookies, 
    get_playwright_cookies_for_context,
    verify_cookie_validity
)

# 导入召唤兽描述解析相关模块
from src.spider.helper.decode_desc import parse_pet_info

# 导入召唤兽类型常量
from src.evaluator.constants.equipment_types import PET_CACHE_REQUIRED_FIELDS


class CBGPetSpider:
    def __init__(self):
        self.session = setup_session()
        self.base_url = 'https://xyq.cbg.163.com/cgi-bin/recommend.py'
        self.output_dir = self.create_output_dir()
        
        # 配置专用的日志器，避免与其他模块冲突
        self.logger = self._setup_logger()
        
        # 初始化其他组件
        self.setup_session()
        self.retry_attempts = 1
        
        # 初始化线程池（用于异步数据库操作）
        self._executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix='PetDB-')
        self.logger.info("线程池初始化完成，最大并发数: 3")

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
        logger.info(" CBG召唤兽爬虫日志系统初始化完成")
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
            referer='https://xyq.cbg.163.com/cgi-bin/equipquery.py?act=show_overall_search_pet',
            logger=self.logger
        )
    

    def parse_jsonp_response(self, text):
        """解析JSONP响应，提取召唤兽数据"""
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
                self.logger.warning("没有找到任何召唤兽数据")
                return []
                
            pets = []
            for pet in equip_list:
                try:
                    # 引入decode_desc.py中的decode_desc函数，解析desc字段，把解析的字段存入数据库 
                    
                    # 获取并解析召唤兽描述字段
                    raw_desc = pet.get('desc', '')
                    parsed_pet_attrs = {}
                    
                    # 如果存在desc字段，则解析召唤兽属性
                    if raw_desc:
                        try:
                            parsed_pet_attrs = parse_pet_info(raw_desc)
                            self.logger.debug(f"成功解析召唤兽描述，获得{len(parsed_pet_attrs)}个属性字段")
                        except Exception as e:
                            self.logger.warning(f"解析召唤兽描述失败: {e}")
                            parsed_pet_attrs = {}
                    
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
                        'desc': raw_desc,  # 使用解析获取的原始desc字段
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
                    
                    # 添加解析后的召唤兽属性字段 - 直接使用原始字段名
                    if parsed_pet_attrs:
                        # 直接将所有解析出的字段添加到pet_data中
                        for field_name, field_value in parsed_pet_attrs.items():
                            # 对于复杂数据类型（列表和字典），转换为JSON字符串
                            if isinstance(field_value, (list, dict)):
                                pet_data[field_name] = json.dumps(field_value, ensure_ascii=False)
                            else:
                                pet_data[field_name] = field_value
                    
                    pets.append(pet_data)
                    
                except Exception as e:
                    self.logger.error(f"解析单个召唤兽数据时出错: {str(e)}")
                    continue
            
            return pets
            
        except Exception as e:
            self.logger.error(f"解析JSONP响应时发生错误: {str(e)}")
            return None

    def get_search_params(self, use_browser=False):
        """
        获取召唤兽搜索参数
        - use_browser=True: 启动浏览器手动设置参数
        - use_browser=False: 从本地文件或默认配置加载参数
        """
        params_file = 'config/equip_params_pet.json'
        
        # 强制浏览器模式：如果use_browser为True，则删除旧参数文件
        if use_browser and os.path.exists(params_file):
            self.logger.info(f"强制浏览器模式，删除旧的参数文件: {params_file}")
            os.remove(params_file)

        # 使用同步的参数获取函数
        return get_pet_search_params_sync(use_browser=use_browser)

    def fetch_page_sync(self, page=1, search_params=None, search_type='overall_search_pet'):
        """
        同步获取单页召唤兽数据
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
            self.logger.error(f"获取召唤兽数据失败 (页码: {page}): {e}")
            return None

    def save_pet_data(self, pets):
        """保存召唤兽数据到MySQL数据库"""
        if not pets:
            self.logger.info("没有召唤兽数据需要保存")
            return 0
        
        try:
            # 确保在Flask应用上下文中执行数据库操作
            from flask import current_app
            from src.app import create_app
            
            # 如果当前没有应用上下文，创建一个
            if not current_app:
                app = create_app()
                with app.app_context():
                    return self._save_pet_data_with_context(pets)
            else:
                return self._save_pet_data_with_context(pets)
                
        except Exception as e:
            self.logger.error(f"保存召唤兽数据到MySQL数据库失败: {e}")
            return 0
    
    def _filter_pet_fields(self, pets):
        """
        过滤召唤兽字段，只保留缓存所需字段（优化内存占用）
        
        Args:
            pets: 召唤兽数据列表
            
        Returns:
            list: 过滤后的召唤兽数据列表
        """
        # 使用列表推导式，更高效
        return [
            {k: v for k, v in pet.items() if k in PET_CACHE_REQUIRED_FIELDS}
            for pet in pets
        ]
    
    def _get_redis_total_count(self):
        """
        获取Redis中的召唤兽总条数
        
        Returns:
            int: Redis中的召唤兽总条数，获取失败返回0
        """
        try:
            from src.evaluator.market_anchor.pet.pet_market_data_collector import PetMarketDataCollector
            from src.utils.redis_cache import get_redis_cache
            
            collector = PetMarketDataCollector()
            redis_cache = get_redis_cache()
            
            if redis_cache and redis_cache.is_available():
                # 获取Redis Hash的总条数
                full_key = redis_cache._make_key(collector._full_cache_key)
                total_count = redis_cache.client.hlen(full_key)
                self.logger.debug(f"Redis召唤兽总条数: {total_count}")
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
                'type': MessageType.PET_CACHE_UPDATED,
                'data_count': data_count,  # 本次数据量
                'action': 'add_dataframe'  # 只用于立即更新内存缓存
            }
            
            success = pubsub.publish_with_dataframe(Channel.PET_UPDATES, message, new_data_df)
            if success:
                self.logger.info(f"📢 已立即发布DataFrame消息到Redis (本次:{data_count}条)")
            else:
                self.logger.warning("⚠️ 发布DataFrame消息失败")
            
            return success
            
        except Exception as e:
            self.logger.warning(f"⚠️ 发布DataFrame消息失败: {e}")
            return False
    
    def _batch_save_to_mysql(self, pets):
        """
        批量保存到MySQL，优化数据库查询性能
        
        Args:
            pets: 召唤兽数据列表
            
        Returns:
            tuple: (新增数量, 更新数量)
        """
        try:
            # 批量查询已存在的召唤兽（一次查询代替N次查询）
            equip_sns = [pet.get('equip_sn') for pet in pets if pet.get('equip_sn')]
            
            existing_pets = {}
            if equip_sns:
                existing_list = db.session.query(Pet).filter(
                    Pet.equip_sn.in_(equip_sns)
                ).all()
                existing_pets = {pet.equip_sn: pet for pet in existing_list}
            
            new_pets = []
            updated_count = 0
            
            # 遍历召唤兽数据，分类为新增和更新
            # 先对同一批次中的重复数据进行去重（保留最后一个）
            seen_equip_sns = set()
            unique_pets = []
            for pet_data in pets:
                equip_sn = pet_data.get('equip_sn')
                if equip_sn:
                    if equip_sn in seen_equip_sns:
                        # 找到已存在的记录并替换
                        for i, existing_pet in enumerate(unique_pets):
                            if existing_pet.get('equip_sn') == equip_sn:
                                unique_pets[i] = pet_data
                                break
                    else:
                        seen_equip_sns.add(equip_sn)
                        unique_pets.append(pet_data)
                else:
                    # 没有equip_sn的记录直接添加
                    unique_pets.append(pet_data)
            
            for pet_data in unique_pets:
                try:
                    equip_sn = pet_data.get('equip_sn')
                    
                    if equip_sn and equip_sn in existing_pets:
                        # 更新现有记录
                        existing = existing_pets[equip_sn]
                        for key, value in pet_data.items():
                            if hasattr(existing, key):
                                setattr(existing, key, value)
                        existing.update_time = datetime.now()
                        updated_count += 1
                    else:
                        # 准备新记录
                        new_pets.append(Pet(**pet_data))
                        
                except Exception as e:
                    self.logger.error(f"处理单个召唤兽数据失败: {e}")
                    continue
            
            # 批量插入新记录
            if new_pets:
                db.session.bulk_save_objects(new_pets)
            
            # 提交事务
            db.session.commit()
            
            if len(new_pets) > 0:
                self.logger.info(f"✅ 成功保存 {len(new_pets)} 条新召唤兽数据到MySQL数据库")
            if updated_count > 0:
                self.logger.info(f"✅ 更新 {updated_count} 条已存在的召唤兽数据")
            
            return len(new_pets), updated_count
            
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
            from src.evaluator.market_anchor.pet.pet_market_data_collector import PetMarketDataCollector
            
            collector = PetMarketDataCollector()
            redis_success = collector._sync_new_data_to_redis(new_data_df)
            
            if redis_success:
                self.logger.info("✅ 新数据已同步到Redis缓存")
            else:
                self.logger.warning("⚠️ 新数据同步到Redis失败")
            
            return redis_success
            
        except Exception as e:
            self.logger.warning(f"⚠️ 同步新数据到Redis失败: {e}")
            return False
    
    def _save_pet_data_with_context(self, pets):
        """在Flask应用上下文中保存召唤兽数据 - 内存缓存优先快速响应 → MySQL → Redis"""
        try:
            # 在子线程中重新导入pandas，确保可用
            import pandas as pd
            
            if not pets:
                self.logger.info("没有召唤兽数据需要保存")
                return 0
            
            self.logger.info(f"开始保存 {len(pets)} 条召唤兽数据...")
            
            # 优化：只过滤一次，避免重复代码
            filtered_pets = self._filter_pet_fields(pets)
            new_data_df = pd.DataFrame(filtered_pets)
            
            # 第一步：立即发布DataFrame消息，快速更新内存缓存（最高优先级，超快响应）
            publish_success = self._publish_dataframe_message(new_data_df, len(pets))
            
            if publish_success:
                self.logger.info(f"✅ 已立即通知内存缓存更新 {len(pets)} 条数据（快速响应）")
            else:
                self.logger.warning(f"⚠️ 内存缓存通知发送失败，但继续保存到数据库")
            
            # 第二步：异步批量保存到MySQL和Redis（不阻塞主流程）
            self._submit_async_save_task(pets, new_data_df)
            
            self.logger.info(f"🎉 召唤兽数据保存流程: 内存缓存(✅已通知) → MySQL(处理中) → Redis(处理中)")
            
            # 返回预估的新增数量（实际数量由异步任务计算）
            return len(pets)
            
        except Exception as e:
            self.logger.error(f"保存召唤兽数据失败: {e}")
            return 0
    
    def _submit_async_save_task(self, pets, new_data_df):
        """
        提交异步保存任务到线程池
        
        Args:
            pets: 召唤兽数据列表
            new_data_df: 过滤后的DataFrame
        """
        try:
            # 使用线程池异步执行保存任务
            future = self._executor.submit(
                self._async_batch_save_worker,
                pets,
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
    
    def _async_batch_save_worker(self, pets, new_data_df):
        """
        异步批量保存工作线程（在线程池中执行）- MySQL → Redis → 通知内存缓存
        
        Args:
            pets: 召唤兽数据列表
            new_data_df: 过滤后的DataFrame
            
        Returns:
            tuple: (新增数量, 更新数量, 实际保存的DataFrame, Redis同步状态)
        """
        try:
            # 在Flask应用上下文中执行数据库操作
            from src.app import create_app
            app = create_app()
            
            with app.app_context():
                self.logger.info(f"🔄 异步任务开始处理 {len(pets)} 条召唤兽数据...")
                
                # 第一步：批量保存到MySQL
                saved_count, updated_count = self._batch_save_to_mysql(pets)
                
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

    async def fetch_page(self, page=1, search_params=None, search_type='overall_search_pet'):
        """
        获取单页召唤兽数据
        
        Args:
            page: 页码
            search_params: 搜索参数
            search_type: 搜索类型
            
        Returns:
            list: 解析后的召唤兽数据
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
            self.logger.error(f"获取召唤兽第{page}页数据时出错: {e}")
            return None

    async def crawl_all_pages_async(self, max_pages=10, delay_range=None, use_browser=False, cached_params=None):
        """
        异步爬取所有召唤兽页面
        """
        # 首先验证Cookie有效性
        self.logger.info("正在验证Cookie有效性...")
        from src.utils.cookie_manager import verify_cookie_validity_async
        if not await verify_cookie_validity_async(self.logger):
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

        search_type = 'overall_search_pet'

        self.logger.info(f" 开始召唤兽爬取，最大页数: {max_pages}")

        # 获取参数
        params_file = 'config/pet_params.json'
        
        # 强制浏览器模式：如果use_browser为True，则删除旧参数文件
        if use_browser and os.path.exists(params_file):
            self.logger.info(f"强制浏览器模式，删除旧的参数文件: {params_file}")
            os.remove(params_file)
        
        # 使用传入的缓存参数或获取新参数
        if cached_params and not use_browser:
            if 'server_id' in cached_params:
                search_type = 'search_pet'
            search_params = cached_params
            self.logger.info(f" 使用传入的缓存参数: {len(search_params)} 个")
        else:
            search_params = await get_pet_search_params_async(use_browser=use_browser)
            if search_params:
                self.logger.info(f" 使用搜索参数: {search_params}")

        if not search_params:
            self.logger.error(f"无法获取召唤兽的搜索参数，爬取中止")
            return
            
        total_saved_count = 0
        successful_pages = 0
        
        for page_num in range(1, max_pages + 1):
            try:
                # 确保日志立即输出
                self.logger.info(f"📄 正在爬取召唤兽第 {page_num} 页...")
                # 强制刷新日志缓冲
                import sys
                sys.stdout.flush()
                
                pets = await self.fetch_page(page_num, search_params, search_type)
                
                if pets is None:
                    self.logger.warning(f" 第 {page_num} 页数据获取失败，尝试重试...")
                    await asyncio.sleep(5) # 等待5秒重试
                    pets = await self.fetch_page(page_num, search_params, search_type)

                if pets:
                    saved_count = self.save_pet_data(pets)
                    total_saved_count += saved_count
                    successful_pages += 1
                    
                    # 打印每条召唤兽的简要信息
                    for pet in pets:
                        price = pet.get('price_desc', pet.get('price', '未知'))
                        pet_name = pet.get('equip_name', '未知召唤兽')
                        level = pet.get('level', '未知')
                        server_name = pet.get('server_name', '未知服务器')
                        seller_nickname = pet.get('seller_nickname', '未知卖家')
                        desc_sumup_short = pet.get('desc_sumup_short', '无描述')
                        self.logger.info(f" ￥{price} - {pet_name}({level}级) - {desc_sumup_short} - {server_name} - {seller_nickname}")
                    
                    self.logger.info(f" 第 {page_num} 页完成，获取 {len(pets)} 条召唤兽，保存 {saved_count} 条")
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

        self.logger.info(f" 召唤兽爬取完成！成功页数: {successful_pages}/{max_pages}, 总召唤兽数: {total_saved_count}")
        
        # 强制刷新所有日志缓冲区，确保日志被完整写入文件
        import sys
        sys.stdout.flush()
        sys.stderr.flush()
        
        # 刷新日志处理器缓冲区
        for handler in self.logger.handlers:
            if hasattr(handler, 'flush'):
                handler.flush()

    def crawl_all_pages(self, max_pages=10, delay_range=None, use_browser=False, cached_params=None):
        """
        同步启动异步召唤兽爬虫的入口
        """
        try:
            asyncio.run(self.crawl_all_pages_async(
                max_pages=max_pages,
                delay_range=delay_range,
                use_browser=use_browser,
                cached_params=cached_params
            ))
        except Exception as e:
            self.logger.error(f"启动召唤兽爬虫失败: {e}")
            import traceback
            traceback.print_exc()