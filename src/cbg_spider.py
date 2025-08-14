#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
梦幻西游藏宝阁爬虫核心模块
使用推荐接口获取角色数据，请通过run.py启动
"""

import os
import sys

# 添加项目根目录到Python路径，解决模块导入问题
from src.utils.project_path import get_project_root
project_root = get_project_root()
sys.path.insert(0, project_root)

import requests
import json
import sqlite3
import time
import random
import re
import pandas as pd
from datetime import datetime
from urllib.parse import urlencode
import logging
from src.tools.setup_requests_session import setup_session
import asyncio
from playwright.async_api import async_playwright
from src.utils.smart_db_helper import CBGSmartDB

# 导入数据库配置
from src.cbg_config import DB_SCHEMA_CONFIG

# 导入解析器类
from src.parser.common_parser import CommonParser
from src.utils.lpc_helper import LPCHelper

# 导入统一日志工厂
from src.spider.logger_factory import get_spider_logger, log_progress, log_page_complete, log_task_complete, log_error, log_warning, log_info, log_total_pages

# 导入统一Cookie管理
from src.utils.cookie_manager import setup_session_with_cookies, get_playwright_cookies_for_context

# 定义一个特殊的标记，用于表示登录已过期
LOGIN_EXPIRED_MARKER = "LOGIN_EXPIRED"

class CBGSpider:
    def __init__(self):
        self.session = setup_session()
        self.base_url = 'https://xyq.cbg.163.com/cgi-bin/recommend.py'
        self.output_dir = self.create_output_dir()
        
        # 使用按月分割的数据库文件路径
        from src.utils.project_path import get_data_path
        current_month = datetime.now().strftime('%Y%m')
        
        # 正常角色数据库路径
        db_filename = f"cbg_roles_{current_month}.db"
        self.db_path = os.path.join(get_data_path(), current_month, db_filename)
        
        # 空号数据库路径（单独的数据库文件）
        empty_db_filename = f"cbg_empty_roles_{current_month}.db"
        self.empty_db_path = os.path.join(get_data_path(), current_month, empty_db_filename)
        
        # 确保data目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 配置专用的日志器，使用统一日志工厂
        self.logger, self.log_file = get_spider_logger('role')
        
        # 延迟初始化数据库，避免在导入时创建文件
        self.init_database()

        # 初始化智能数据库助手（正常角色）
        self.smart_db = CBGSmartDB(self.db_path)
        
        # 初始化空号数据库助手（空号专用）
        self.empty_smart_db = CBGSmartDB(self.empty_db_path)
        
        # 初始化通用解析器
        self.common_parser = CommonParser(self.logger)

        # 初始化LPC解析助手
        self.lpc_helper = LPCHelper(self.logger)
        
        # 初始化其他组件
        self.setup_session()
        
        self.retry_attempts = 1 # 为登录失败重试设置次数



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
    
    def init_database(self):
        """初始化数据库和表结构"""
        try:
            # 初始化正常角色数据库
            self.init_normal_database()
            
            # 初始化空号数据库
            self.init_empty_database()
            
            log_info(self.logger, "所有数据已初始化完毕")
                
        except Exception as e:
            log_error(self.logger, f"初始化数据库失败: {e}")
            raise
    
    def init_normal_database(self):
        """初始化正常角色数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建roles表
            cursor.execute(DB_SCHEMA_CONFIG['roles'])
            
            # 也创建large_equip_desc_data表，以防需要存储详细数据
            cursor.execute(DB_SCHEMA_CONFIG['large_equip_desc_data'])
            
            conn.commit()
            log_info(self.logger, f"正常角色数据库初始化完成: {os.path.basename(self.db_path)}")
            
        except Exception as e:
            log_error(self.logger, f"初始化正常角色数据库失败: {e}")
            raise
        finally:
            conn.close()
    
    def init_empty_database(self):
        """初始化空号数据库"""
        try:
            conn = sqlite3.connect(self.empty_db_path)
            cursor = conn.cursor()
            
            # 创建roles表
            cursor.execute(DB_SCHEMA_CONFIG['roles'])
            
            # 也创建large_equip_desc_data表，以防需要存储详细数据
            cursor.execute(DB_SCHEMA_CONFIG['large_equip_desc_data'])
            
            conn.commit()
            log_info(self.logger, f"空号数据库初始化完成: {os.path.basename(self.empty_db_path)}")
            
        except Exception as e:
            log_error(self.logger, f"初始化空号数据库失败: {e}")
            raise
        finally:
            conn.close()

    def parse_large_equip_desc(self, large_desc):
        """解析large_equip_desc字段，提取详细的角色信息
        
        简化版本：只使用lpc_to_js方法进行解析
        """
        if not large_desc or not isinstance(large_desc, str):
            return {}
        
        try:
            # 移除可能的编码标记
            clean_desc = large_desc.strip()
            if clean_desc.startswith('@') and clean_desc.endswith('@'):
                clean_desc = clean_desc[1:-1]
            
            # 只使用lpc_to_js方法进行解析
            js_format = self.lpc_helper.lpc_to_js(clean_desc, return_dict=False)
            if js_format:
                # 然后用js_eval解析JavaScript格式字符串
                parsed_data = self.lpc_helper.js_eval(js_format)
                if parsed_data and isinstance(parsed_data, dict) and len(parsed_data) > 0:
                    return self.extract_role_fields(parsed_data)
            
            log_warning(self.logger, f"LPC->JS解析失败，原始数据前200字符: {clean_desc[:200]}")
            return {}
            
        except Exception as e:
            log_warning(self.logger, f"解析large_equip_desc失败: {e}")
            return {}
    
    def extract_role_fields(self, parsed_data):
        """从解析后的数据中提取角色字段"""
        if not isinstance(parsed_data, dict):
            return {}
        
        # 提取关键字段
        result = {
            # 基础信息
            'cName': parsed_data.get('cName'),  # 角色名
            'iGrade': parsed_data.get('iGrade'),  # 等级
            'iSchool': parsed_data.get('iSchool'),  # 门派
            'iIcon': parsed_data.get('iIcon'),  # 图标ID
            'usernum': parsed_data.get('usernum'),  # 用户ID
            
            # 属性信息
            'iHp_Max': parsed_data.get('iHp_Max'),  # 气血
            'iMp_Max': parsed_data.get('iMp_Max'),  # 魔法
            'iAtt_All': parsed_data.get('iAtt_All'),  # 命中
            'iDef_All': parsed_data.get('iDef_All'),  # 防御
            'iSpe_All': parsed_data.get('iSpe_All'),  # 敏捷
            'iMag_All': parsed_data.get('iMag_All'),  # 魔力
            'iDamage_All': parsed_data.get('iDamage_All'),  # 伤害
            'iTotalMagDam_all': parsed_data.get('iTotalMagDam_all'),  # 法术伤害
            'iTotalMagDef_all': parsed_data.get('iTotalMagDef_all'),  # 法术防御(总法术防御)
            'iDod_All': parsed_data.get('iDod_All'),  # 躲避
            'iCor_All': parsed_data.get('iCor_All'),  # 体质
            'iStr_All': parsed_data.get('iStr_All'),  # 力量
            'iRes_All': parsed_data.get('iRes_All'),  # 耐力
            'iDex_All': parsed_data.get('iDex_All'),  # 速度
            
            # 经验和修炼
            'iUpExp': parsed_data.get('iUpExp'),  # 获得经验
            'sum_exp': parsed_data.get('sum_exp'),  # 总经验
            'iExptSki1': parsed_data.get('iExptSki1'),  # 攻击修炼
            'iExptSki2': parsed_data.get('iExptSki2'),  # 防御修炼
            'iExptSki3': parsed_data.get('iExptSki3'),  # 法术修炼
            'iExptSki4': parsed_data.get('iExptSki4'),  # 抗法修炼
            'iExptSki5': parsed_data.get('iExptSki5'),  # 猎术修炼
            'iMaxExpt1': parsed_data.get('iMaxExpt1'),  # 攻击修炼上限
            'iMaxExpt2': parsed_data.get('iMaxExpt2'),  # 防御修炼上限
            'iMaxExpt3': parsed_data.get('iMaxExpt3'),  # 法术修炼上限
            'iMaxExpt4': parsed_data.get('iMaxExpt4'),  # 抗法修炼上限
            
            # 召唤兽控制技能
            'iBeastSki1': parsed_data.get('iBeastSki1'),  # 攻击控制力
            'iBeastSki2': parsed_data.get('iBeastSki2'),  # 防御控制力
            'iBeastSki3': parsed_data.get('iBeastSki3'),  # 法术控制力
            'iBeastSki4': parsed_data.get('iBeastSki4'),  # 抗法控制力
            
            # 点数信息
            'iSkiPoint': parsed_data.get('iSkiPoint'),  # 剧情技能剩余点
            'iPoint': parsed_data.get('iPoint'),  # 属性点
            'potential': parsed_data.get('potential'),  # 潜力值
            'max_potential': parsed_data.get('max_potential'),  # 最大潜力值
            
            # 金钱相关
            'iCash': parsed_data.get('iCash'),  # 现金
            'iSaving': parsed_data.get('iSaving'),  # 存款
            'iLearnCash': parsed_data.get('iLearnCash'),  # 储备金
            
            # 转职飞升相关
            'iZhuanZhi': parsed_data.get('iZhuanZhi'),  # 转职状态
            'i3FlyLv': parsed_data.get('i3FlyLv'),  # 化圣等级
            'nine_fight_level': parsed_data.get('nine_fight_level'),  # 生死劫等级
            
            # 其他所有字段
            **{k: v for k, v in parsed_data.items() if k not in [
                'cName', 'iGrade', 'iSchool', 'iIcon', 'usernum',
                'iHp_Max', 'iMp_Max', 'iAtt_All', 'iDef_All', 'iSpe_All', 'iMag_All',
                'iDamage_All', 'iTotalMagDam_all', 'iTotalMagDef_all', 'iDod_All', 'iCor_All', 'iStr_All', 'iRes_All', 'iDex_All',
                'iUpExp', 'sum_exp', 'iExptSki1', 'iExptSki2', 'iExptSki3', 'iExptSki4', 'iExptSki5',
                'iMaxExpt1', 'iMaxExpt2', 'iMaxExpt3', 'iMaxExpt4',
                'iBeastSki1', 'iBeastSki2', 'iBeastSki3', 'iBeastSki4',
                'iSkiPoint', 'iPoint', 'potential', 'max_potential',
                'iCash', 'iSaving', 'iLearnCash',
                'iZhuanZhi', 'i3FlyLv', 'nine_fight_level'
            ]},
            
            # 原始数据
            'raw_data': parsed_data
        }
        
        return result
    
    def lpc_to_js(self, lpc_str):
        """将LPC格式转换为JavaScript格式"""
        return self.lpc_helper.lpc_to_js(lpc_str, return_dict=False)
    
    def parse_jsonp_response(self, text):
        """解析JSONP响应，提取完整的角色数据"""
        try:
            # 提取JSON部分
            start = text.find('(') + 1
            end = text.rfind(')')
            if start <= 0 or end <= 0:
                log_error(self.logger, "响应不是有效的JSONP格式")
                return None
                
            json_str = text[start:end]
            data = json.loads(json_str)
            
            if not isinstance(data, dict):
                self.logger.error("解析JSONP响应失败：响应不是一个有效的JSON对象")
                return None

            equip_list = data.get('equip_list', [])
            return equip_list
            
        except Exception as e:
            self.logger.error(f"解析JSONP响应时发生错误: {str(e)}")
            return None
        
        
    def save_role_data(self, roles):
        """保存角色数据到数据库"""
        if not roles:
            log_warning(self.logger, "没有要保存的角色数据")
            return 0
        
        # 确保数据库已初始化
        # self._ensure_database_initialized()
            
        saved_count = 0
        for char in roles:
            try:
                # 解析技能信息（如果有large_equip_desc数据）
                life_skills = ''
                school_skills = ''
                ju_qing_skills = ''
                yushoushu_skill = 0

                large_equip_desc = char.get('large_equip_desc', '')
                server_name = char.get('serverName')
                if(server_name == '花样年华'):
                    log_info(self.logger, f"{char.get('seller_nickname')} 服务器为花样年华,不予记录。")
                    continue
              
                # 解析large_equip_desc字段
                parsed_desc = self.parse_large_equip_desc(large_equip_desc)
                all_skills = parsed_desc.get('all_skills', {})
                # 解析各种技能
                life_skills = self.parse_life_skills(all_skills)
                school_skills = self.parse_school_skills(all_skills)
                ju_qing_skills = self.parse_ju_qing_skills(all_skills)
                yushoushu_skill = self.parse_yushoushu_skill(all_skills)

                # 1. 保存角色基础信息
                role_data = {
                    # 基本字段直接映射
                    'eid': char.get('eid'),
                    'equipid': char.get('equipid'),
                    'equip_sn': char.get('equip_sn'),
                    'server_name': char.get('server_name'),
                    'serverid': char.get('serverid'),
                    'equip_server_sn': char.get('equip_server_sn'),
                    'seller_nickname': char.get('seller_nickname'),
                    'seller_roleid': char.get('seller_roleid'),
                    'area_name': char.get('area_name'),
                    'equip_name': char.get('equip_name'),
                    'equip_type': char.get('equip_type'),
                    'equip_type_name': char.get('equip_type_name'),
                    'equip_type_desc': char.get('equip_type_desc'),
                    'level': char.get('level'),
                    'equip_level': char.get('equip_level'),
                    'equip_level_desc': char.get('equip_level_desc'),
                    'level_desc': char.get('level_desc'),
                    'subtitle': char.get('subtitle'),
                    'equip_pos': char.get('equip_pos'),
                    'position': char.get('position'),
                    'school': char.get('school'),
                    'role_grade_limit': char.get('role_grade_limit'),
                    'min_buyer_level': char.get('min_buyer_level'),
                    'equip_count': char.get('equip_count'),
                    'price': char.get('price'),
                    'price_desc': char.get('price_desc'),
                    'unit_price_desc': char.get('unit_price_desc'),
                    'min_unit_price': char.get('min_unit_price'),
                    'accept_bargain': 1 if char.get('accept_bargain') else 0,
                    'equip_status': char.get('equip_status'),
                    'equip_status_desc': char.get('equip_status_desc'),
                    'status_desc': char.get('status_desc'),
                    'onsale_expire_time_desc': char.get('onsale_expire_time_desc'),
                    'time_left': char.get('time_left'),
                    'expire_time': char.get('expire_time'),
                    'create_time_equip': char.get('create_time'),
                    'selling_time': char.get('selling_time'),
                    'selling_time_ago_desc': char.get('selling_time_ago_desc'),
                    'first_onsale_time': char.get('first_onsale_time'),
                    'pass_fair_show': char.get('pass_fair_show'),
                    'fair_show_time': char.get('fair_show_time'),
                    'fair_show_end_time': char.get('fair_show_end_time'),
                    'fair_show_end_time_left': char.get('fair_show_end_time_left'),
                    'fair_show_poundage': char.get('fair_show_poundage'),
                
                    # 其他信息
                    'collect_num': char.get('collect_num'),
                    'has_collect': 1 if char.get('has_collect') else 0,
                    'score': char.get('score'),
                    'icon_index': char.get('icon_index'),
                    'icon': char.get('icon'),
                    'equip_face_img': char.get('equip_face_img'),
                    'kindid': char.get('kindid'),
                    'game_channel': char.get('game_channel'),
                    
                    # 订单相关
                    'game_ordersn': char.get('game_ordersn'),
                    'whole_game_ordersn': char.get('whole_game_ordersn'),
                    
                    # 跨服相关
                    'allow_cross_buy': char.get('allow_cross_buy'),
                    'cross_server_poundage': char.get('cross_server_poundage'),
                    'cross_server_poundage_origin': char.get('cross_server_poundage_origin'),
                    'cross_server_poundage_discount': char.get('cross_server_poundage_discount'),
                    'cross_server_poundage_discount_label': char.get('cross_server_poundage_discount_label'),
                    'cross_server_poundage_display_mode': char.get('cross_server_poundage_display_mode'),
                    'cross_server_activity_conf_discount': char.get('cross_server_activity_conf_discount'),
                    
                    # 活动相关
                    'activity_type': char.get('activity_type'),
                    'joined_seller_activity': 1 if char.get('joined_seller_activity') else 0,
                    
                    # 拆分相关
                    'is_split_sale': 1 if char.get('is_split_sale') else 0,
                    'is_split_main_role': 1 if char.get('is_split_main_role') else 0,
                    'is_split_independent_role': 1 if char.get('is_split_independent_role') else 0,
                    'is_split_independent_equip': 1 if char.get('is_split_independent_equip') else 0,
                    'split_equip_sold_happen': 1 if char.get('split_equip_sold_happen') else 0,
                    'show_split_equip_sold_remind': 1 if char.get('show_split_equip_sold_remind') else 0,
                    
                    # 保护相关
                    'is_onsale_protection_period': 1 if char.get('is_onsale_protection_period') else 0,
                    'onsale_protection_end_time': char.get('onsale_protection_end_time'),
                    'is_vip_protection': 1 if char.get('is_vip_protection') else 0,
                    'is_time_lock': 1 if char.get('is_time_lock') else 0,
                    
                    # 测试服相关
                    'equip_in_test_server': 1 if char.get('equip_in_test_server') else 0,
                    'buyer_in_test_server': 1 if char.get('buyer_in_test_server') else 0,
                    'equip_in_allow_take_away_server': 1 if char.get('equip_in_allow_take_away_server') else 0,
                    
                    # 其他标识
                    'is_weijianding': 1 if char.get('is_weijianding') else 0,
                    'is_show_alipay_privilege': 1 if char.get('is_show_alipay_privilege') else 0,
                    'is_seller_redpacket_flag': 1 if char.get('is_seller_redpacket_flag') else 0,
                    'is_show_expert_desc': char.get('is_show_expert_desc'),
                    'is_show_special_highlight': 1 if char.get('is_show_special_highlight') else 0,
                    'is_xyq_game_role_kunpeng_reach_limit': 1 if char.get('is_xyq_game_role_kunpeng_reach_limit') else 0,
                    
                    # 版本和存储相关
                    'equip_onsale_version': char.get('equip_onsale_version'),
                    'storage_type': char.get('storage_type'),
                    'agent_trans_time': char.get('agent_trans_time'),
                    
                    # KOL相关
                    'kol_article_id': char.get('kol_article_id'),
                    'kol_share_id': char.get('kol_share_id'),
                    'kol_share_time': char.get('kol_share_time'),
                    'kol_share_status': char.get('kol_share_status'),
                    
                    # 推荐相关
                    'reco_request_id': char.get('reco_request_id'),
                    'appointed_roleid': char.get('appointed_roleid'),
                    
                    # 团队相关
                    'play_team_cnt': char.get('play_team_cnt'),
                    
                    # 随机抽奖相关
                    'random_draw_finish_time': char.get('random_draw_finish_time'),
                    
                    # 详细描述
                    'desc': char.get('desc'), # 使用解析获取的原始desc字段
                    'large_equip_desc': char.get('large_equip_desc'),
                    'desc_sumup': char.get('desc_sumup'),
                    'desc_sumup_short': char.get('desc_sumup_short'),
                    'diy_desc': char.get('diy_desc'),
                    'rec_desc': char.get('rec_desc'),
                    
                    # 搜索相关
                    'search_type': char.get('search_type'),
                    'tag': char.get('tag'),
                    
                    # JSON格式字段
                    'price_explanation': json.dumps(char.get('price_explanation'), ensure_ascii=False) if char.get('price_explanation') else '',
                    'bargain_info': json.dumps(char.get('bargain_info'), ensure_ascii=False) if char.get('bargain_info') else '',
                    'diy_desc_pay_info': json.dumps(char.get('diy_desc_pay_info'), ensure_ascii=False) if char.get('diy_desc_pay_info') else '',
                    'other_info': char.get('other_info', ''),
                    'video_info': json.dumps(char.get('video_info'), ensure_ascii=False) if char.get('video_info') else '',
                    'agg_added_attrs': json.dumps(char.get('agg_added_attrs'), ensure_ascii=False) if char.get('agg_added_attrs') else '',
                    'dynamic_tags': json.dumps(char.get('dynamic_tags'), ensure_ascii=False) if char.get('dynamic_tags') else '',
                    'highlight': json.dumps(char.get('highlight'), ensure_ascii=False) if char.get('highlight') else '',
                    'tag_key': char.get('tag_key', ''),
                    'life_skills': life_skills,
                    'school_skills': school_skills,
                    'ju_qing_skills': ju_qing_skills,
                    'yushoushu_skill': yushoushu_skill,
                    # 原始数据
                    'raw_data_json': json.dumps(char, ensure_ascii=False)
                }
               
                # 空号识别逻辑
                is_empty_role = self.is_empty_role(parsed_desc.get('AllEquip', {}), parsed_desc.get('AllSummon', {}))
                
                if is_empty_role:
                    # 如果是空号，添加空号识别信息并保存到空号数据库
                    empty_reason = self.get_empty_reason(parsed_desc.get('AllEquip', {}), parsed_desc.get('AllSummon', {}))
                    # 保存到空号数据库的roles表
                    try:
                        self.empty_smart_db.save_role(role_data)
                        log_info(self.logger, f"￥{char.get('price')} - {char.get('seller_nickname')}(空号) - {empty_reason}")
                        saved_count += 1
                    except Exception as e:
                        log_error(self.logger, f"保存空号数据失败: ￥{char.get('price')}, 错误: {e}")
                else:
                    # 如果不是空号，保存到正常角色数据库
                    try:
                        self.smart_db.save_role(role_data)
                        log_info(self.logger, f"￥{char.get('price')} - {char.get('seller_nickname')}")
                        saved_count += 1
                    except Exception as e:
                        log_error(self.logger, f"保存角色数据失败: ￥{char.get('price')}, 错误: {e}")
                
                # 2. 处理详细装备数据（如果存在）
                # 注意：即使是空号，也要尝试解析详细数据（如果API返回了的话）
                if large_equip_desc:
                    try:
                        # 创建详细装备数据字典
                        def safe_int(value, default=0):
                            """安全转换为整数"""
                            if value is None:
                                return default
                            try:
                                return int(value)
                            except (ValueError, TypeError):
                                return default
                        
                        def safe_str(value, default=''):
                            """安全转换为字符串"""
                            if value is None:
                                return default
                            return str(value)
                        
                        # 构建详细角色数据
                        equip_data = {
                            'eid': char.get('eid'),
                            'time_lock_days': safe_int(char.get('time_lock_days')),
                            'role_name': safe_str(parsed_desc.get('cName')),
                            'role_level': safe_int(parsed_desc.get('iGrade')),
                            'role_school': safe_int(parsed_desc.get('iSchool')),
                            'role_icon': safe_int(parsed_desc.get('iIcon')),
                            'user_num': safe_str(parsed_desc.get('usernum')),
                            'hp_max': safe_int(parsed_desc.get('iHp_Max')),
                            'mp_max': safe_int(parsed_desc.get('iMp_Max')),
                            'att_all': safe_int(parsed_desc.get('iAtt_All')),
                            'def_all': safe_int(parsed_desc.get('iDef_All')),
                            'spe_all': safe_int(parsed_desc.get('iSpe_All')),
                            'mag_all': safe_int(parsed_desc.get('iMag_All')),
                            'damage_all': safe_int(parsed_desc.get('iDamage_All')),
                            'mag_dam_all': safe_int(parsed_desc.get('iTotalMagDam_all')),
                            'mag_def_all': safe_int(parsed_desc.get('iTotalMagDef_all')),
                            'dod_all': safe_int(parsed_desc.get('iDod_All')),
                            'cor_all': safe_int(parsed_desc.get('iCor_All')),
                            'str_all': safe_int(parsed_desc.get('iStr_All')),
                            'res_all': safe_int(parsed_desc.get('iRes_All')),
                            'dex_all': safe_int(parsed_desc.get('iDex_All')),
                            'up_exp': safe_int(parsed_desc.get('iUpExp')),
                            'sum_exp': safe_int(parsed_desc.get('sum_exp')),
                            'expt_ski1': safe_int(parsed_desc.get('iExptSki1')),
                            'expt_ski2': safe_int(parsed_desc.get('iExptSki2')),
                            'expt_ski3': safe_int(parsed_desc.get('iExptSki3')),
                            'expt_ski4': safe_int(parsed_desc.get('iExptSki4')),
                            'expt_ski5': safe_int(parsed_desc.get('iExptSki5')),
                            'max_expt1': safe_int(parsed_desc.get('iMaxExpt1')),
                            'max_expt2': safe_int(parsed_desc.get('iMaxExpt2')),
                            'max_expt3': safe_int(parsed_desc.get('iMaxExpt3')),
                            'max_expt4': safe_int(parsed_desc.get('iMaxExpt4')),
                            'beast_ski1': safe_int(parsed_desc.get('iBeastSki1')),
                            'beast_ski2': safe_int(parsed_desc.get('iBeastSki2')),
                            'beast_ski3': safe_int(parsed_desc.get('iBeastSki3')),
                            'beast_ski4': safe_int(parsed_desc.get('iBeastSki4')),
                            'all_new_point':safe_int(parsed_desc.get('TA_iAllNewPoint')),
                            'skill_point': safe_int(parsed_desc.get('iSkiPoint')),
                            'attribute_point': safe_int(parsed_desc.get('iPoint')),
                            'potential': safe_int(parsed_desc.get('potential')),
                            'max_potential': safe_int(parsed_desc.get('max_potential')),
                            'cash': safe_int(parsed_desc.get('iCash')),
                            'saving': safe_int(parsed_desc.get('iSaving')),
                            'learn_cash': safe_int(parsed_desc.get('iLearnCash')),
                            'zhuan_zhi': safe_int(parsed_desc.get('iZhuanZhi')),
                            'three_fly_lv': safe_int(parsed_desc.get('i3FlyLv')),
                            'nine_fight_level': safe_int(parsed_desc.get('nine_fight_level')),
                            'goodness': safe_int(parsed_desc.get('iGoodness')),
                            'badness': safe_int(parsed_desc.get('iBadness')),
                            'goodness_sav': safe_int(parsed_desc.get('igoodness_sav')),
                            'role_title': safe_str(parsed_desc.get('title')),
                            'org_name': safe_str(parsed_desc.get('cOrg')),
                            'org_offer': safe_int(parsed_desc.get('iOrgOffer')),
                            'org_position': safe_str(parsed_desc.get('org_position')),
                            'marry_id': safe_str(parsed_desc.get('iMarry')),
                            'marry2_id': safe_str(parsed_desc.get('iMarry2')),
                            'marry_name': safe_str(parsed_desc.get('marry_name')),
                            'community_name': safe_str(parsed_desc.get('commu_name')),
                            'community_gid': safe_str(parsed_desc.get('commu_gid')),
                            'achievement_total': safe_int(parsed_desc.get('AchPointTotal')),
                            'hero_score': safe_int(parsed_desc.get('HeroScore')),
                            'datang_feat': safe_int(parsed_desc.get('datang_feat')),
                            'sword_score': safe_int(parsed_desc.get('sword_score')),
                            'dup_score': safe_int(parsed_desc.get('dup_score')),
                            'shenqi_score': safe_int(parsed_desc.get('shenqi_score')),
                            'qicai_score': safe_int(parsed_desc.get('qicai_score')),
                            'xianyu_score': safe_int(parsed_desc.get('xianyu_score')),
                            'nuts_num': safe_int(parsed_desc.get('iNutsNum')),
                            'cg_total_amount': safe_int(parsed_desc.get('iCGTotalAmount')),
                            'cg_body_amount': safe_int(parsed_desc.get('iCGBodyAmount')),
                            'cg_box_amount': safe_int(parsed_desc.get('iCGBoxAmount')),
                            'xianyu_amount': safe_int(parsed_desc.get('xianyu')),
                            'energy_amount': safe_int(parsed_desc.get('energy')),
                            'jiyuan_amount': safe_int(parsed_desc.get('jiyuan')),
                            'add_point': safe_int(parsed_desc.get('addPoint')),
                            'packet_page': safe_int(parsed_desc.get('iPcktPage')),
                            'rent_level': safe_int(parsed_desc.get('rent_level')),
                            'outdoor_level': safe_int(parsed_desc.get('outdoor_level')),
                            'farm_level': safe_int(parsed_desc.get('farm_level')),
                            'house_real_owner': safe_int(parsed_desc.get('house_real_owner')),
                            'pride': safe_int(parsed_desc.get('iPride')),
                            'bid_status': safe_int(parsed_desc.get('bid')),
                            'ori_race': safe_int(parsed_desc.get('ori_race')),
                            'current_race': safe_int(parsed_desc.get('iRace')),
                            'sum_amount': safe_int(parsed_desc.get('iSumAmount')),
                            'version_code': safe_str(parsed_desc.get('equip_desc_version_code')),
                            'pet': json.dumps(parsed_desc.get('pet', {}), ensure_ascii=False),
                            'all_skills_json': json.dumps(parsed_desc.get('all_skills', {}), ensure_ascii=False),
                            'all_equip_json': json.dumps(parsed_desc.get('AllEquip', {}), ensure_ascii=False),
                            'all_summon_json': json.dumps(parsed_desc.get('AllSummon', {}), ensure_ascii=False),
                            'child_json': json.dumps(parsed_desc.get('child', {}), ensure_ascii=False),
                            'child2_json': json.dumps(parsed_desc.get('child2', {}), ensure_ascii=False),
                            'all_rider_json': json.dumps(parsed_desc.get('AllRider', {}), ensure_ascii=False),
                            'ex_avt_json': json.dumps(parsed_desc.get('ExAvt', {}), ensure_ascii=False),
                            'huge_horse_json': json.dumps(parsed_desc.get('HugeHorse', {}), ensure_ascii=False),
                            'fabao_json': json.dumps(parsed_desc.get('fabao', {}), ensure_ascii=False),
                            'lingbao_json': json.dumps(parsed_desc.get('lingbao', {}), ensure_ascii=False),
                            'shenqi_json': json.dumps(parsed_desc.get('shenqi', {}), ensure_ascii=False),
                            'idbid_desc_json': json.dumps(parsed_desc.get('idbid_desc', {}), ensure_ascii=False),
                            'changesch_json': json.dumps(parsed_desc.get('changesch', {}), ensure_ascii=False),
                            'prop_kept_json': json.dumps(parsed_desc.get('propKept', {}), ensure_ascii=False),
                            'more_attr_json': json.dumps(parsed_desc.get('more_attr', {}), ensure_ascii=False),
                            'raw_data_json': json.dumps(parsed_desc, ensure_ascii=False)
                        }
                        
                        # 根据是否为空号选择对应的数据库保存详细装备数据
                        if is_empty_role:
                            # 空号数据保存到空号数据库
                            self.logger.debug(f"保存空号详细数据到空号数据库: {char.get('eid')}")
                            success = self.empty_smart_db.save_large_equip_data(equip_data)
                            if success:
                                self.logger.debug(f"空号详细数据保存成功: {char.get('eid')}")
                            else:
                                self.logger.error(f"空号详细数据保存失败: {char.get('eid')}")
                        else:
                            # 正常角色数据保存到正常数据库
                            self.logger.debug(f"保存正常角色详细数据到正常数据库: {char.get('eid')}")
                            success = self.smart_db.save_large_equip_data(equip_data)
                            if success:
                                self.logger.debug(f"正常角色详细数据保存成功: {char.get('eid')}")
                            else:
                                self.logger.error(f"正常角色详细数据保存失败: {char.get('eid')}")
                        
                    except Exception as e:
                        self.logger.error(f"解析装备详细信息时出错: {str(e)}")
                
            except Exception as e:
                self.logger.error(f"保存角色 {char.get('eid')} 时出错: {str(e)}")
                continue
                
        # if saved_count > 0:
        #     self.logger.info(f"🗂️ 每个角色的单独JSON文件已保存到 {self.output_dir}/role_json/ 文件夹")
        return saved_count
    
    def crawl_all_pages(self, max_pages=10, delay_range=None, search_params=None, use_browser=False):
        """
        爬取所有页面的数据
        
        Args:
            max_pages: 最大爬取页数
            delay_range: 延迟范围，格式为(min_seconds, max_seconds)
            search_params: 搜索参数，如果提供则直接使用这些参数
            use_browser: 是否使用浏览器监听模式获取参数
            
        Returns:
            list: 所有页面的数据列表
        """
        # 首先验证Cookie有效性
        self.logger.info("正在验证Cookie有效性...")
        from src.utils.cookie_manager import verify_cookie_validity
        if not verify_cookie_validity(self.logger):
            self.logger.warning("Cookie验证失败，正在更新Cookie...")
            # 使用异步方式更新Cookie
            async def update_cookie():
                from src.utils.cookie_manager import _update_cookies_internal
                return await _update_cookies_internal()
            
            if not asyncio.run(update_cookie()):
                self.logger.error("Cookie更新失败，无法继续爬取")
                return 0
            else:
                self.logger.info("Cookie更新成功，重新设置会话")
                # 重新设置会话
                self.setup_session()
        else:
            self.logger.info("Cookie验证通过")

        current_page = 1
        total_roles = 0
        successful_pages = 0
        
        # 输出总页数信息
        log_total_pages(self.logger, max_pages)
        
        # 获取搜索参数
        if search_params is None:
            try:
                if use_browser:
                    # 使用浏览器监听模式收集角色参数
                    log_info(self.logger, "启动浏览器监听模式收集角色参数...")
                    from src.tools.search_form_helper import get_role_search_params_sync
                    search_params = get_role_search_params_sync(use_browser=True)
                    if not search_params:
                        search_params = {'server_type': 3}
                        log_warning(self.logger, "未能收集到角色搜索参数，将使用默认参数")
                    else:
                        log_info(self.logger, f"成功收集到角色搜索参数: {json.dumps(search_params, ensure_ascii=False)}")
                else:
                        log_info(self.logger, f"成功收集到搜索参数: {json.dumps(search_params, ensure_ascii=False)}")

            except Exception as e:
                log_warning(self.logger, f"加载搜索参数失败: {e}")
                search_params = {'server_type': 3}
        
        while current_page <= max_pages:
            # 使用统一的进度日志格式
            log_progress(self.logger, current_page, max_pages)
            
            # 获取当前页数据
            page_data = self.fetch_page(current_page, search_params)
            
            if not page_data:
                log_error(self.logger, f"第 {current_page} 页数据获取失败，停止爬取")
                break
                
            # 保存数据
            saved_count = self.save_role_data(page_data)
            total_roles += saved_count
            successful_pages += 1
            
            # 使用统一的页面完成日志格式
            log_page_complete(self.logger, current_page, len(page_data), saved_count)
    
            # 检查是否还有下一页
            # if len(page_data) < 15:  # 如果返回的数据少于15条，说明是最后一页
            #     self.logger.info("已到达最后一页")
            #     break
                
            current_page += 1
            
            # 添加随机延迟（最后一页完成后不需要等待）
            if delay_range and current_page <= max_pages:
                min_delay, max_delay = delay_range
                delay = random.uniform(min_delay, max_delay)
                log_info(self.logger, f"等待 {delay:.2f} 秒后继续...")
                time.sleep(delay)
        
        # 使用统一的任务完成日志格式
        log_task_complete(self.logger, successful_pages, max_pages, total_roles, "角色")
        return total_roles

    def fetch_page(self, page=1, search_params=None):
        """
        获取单页数据
        
        Args:
            page: 页码
            search_params: 搜索参数
            
        Returns:
            dict: 解析后的数据
        """
        try:
            # 确保search_params不为None
            if search_params is None:
                search_params = {'server_type': 3}
            
            # 构建请求参数
            params = {
                **search_params,  # 添加搜索参数
                'callback': 'Request.JSONP.request_map.request_0',
                '_': str(int(time.time() * 1000)),
                'act': 'recommd_by_role',
                'page': page,
                'count': 15,
                'search_type': 'overall_search_role',
                "order_by": "price ASC"
            }
            
            # 构建完整URL
            url = f"{self.base_url}?{urlencode(params)}"
            
            # 使用Playwright发送请求
            async def fetch_with_playwright():
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context()
                    
                    # 设置cookies
                    cookies = get_playwright_cookies_for_context(self.logger)
                    if cookies:
                        await context.add_cookies(cookies)
                    
                    page = await context.new_page()
                    response = await page.goto(url)
                    
                    if response:
                        text = await response.text()
                        await browser.close()
                        return text
                    await browser.close()
                    return None
            
            # 运行异步函数
            response_text = asyncio.run(fetch_with_playwright())
            
            if not response_text:
                log_error(self.logger, "请求失败，未获取到响应")
                return None

            # 解析响应
            parsed_result = self.parse_jsonp_response(response_text)
            
            return parsed_result
                
        except Exception as e:
            log_error(self.logger, f"获取第{page}页数据时出错: {e}")
            return None

    def parse_yushoushu_skill(self, skills_data):
        """解析育兽术技能数据"""
        return self.common_parser.parse_yushoushu_skill(skills_data)
    
    def parse_life_skills(self, skills_data):
        """解析生活技能数据"""
        return self.common_parser.parse_life_skills(skills_data)
    
    def parse_school_skills(self, skills_data):
        """解析师门技能数据"""
        return self.common_parser.parse_school_skills(skills_data)
    
    def parse_ju_qing_skills(self, skills_data):
        """解析剧情技能数据"""
        return self.common_parser.parse_ju_qing_skills(skills_data)

    def get_outdoor_level_name(self, level):
        """转换庭院等级数字为中文名称"""
        return self.common_parser.get_outdoor_level_name(level)
    
    def get_farm_level_name(self, level):
        """转换牧场等级数字为中文名称"""
        return self.common_parser.get_farm_level_name(level)
    
    def get_house_real_owner_name(self, owner_status):
        """获取房屋真实拥有者名称"""
        owner_names = {0: "无", 1: "自己", 2: "配偶"}
        return owner_names.get(owner_status, "未知")
    
    def is_empty_role(self, all_equips, pets):
        """
        判断是否为空号
        空号条件：物品个数等于0，且宠物等级大于100的数量为0
        
        Args:
            all_equips: 装备数据
            pets: 宠物数据
            
        Returns:
            bool: True表示是空号，False表示不是空号
        """
        try:
            # 检查物品个数
            equip_count = 0
            if all_equips and isinstance(all_equips, dict):
                # 计算装备数量（排除特殊字段）
                for key, value in all_equips.items():
                    if key.isdigit() and isinstance(value, dict):
                        equip_count += 1
            
            # 检查高等级宠物数量（等级大于100）
            high_level_pet_count = self.count_high_level_pets(pets)
            
            # 空号判断：物品个数为0 且 高等级宠物数量为0
            is_empty = (equip_count == 0) and (high_level_pet_count == 0)
            
            if is_empty:
                # self.logger.debug(f"识别空号: {char_data.get('seller_nickname')} - 物品数:{equip_count}, 高级宠物数:{high_level_pet_count}")
                pass
            
            return is_empty
            
        except Exception as e:
            log_error(self.logger, f"判断空号时出错: {e}")
            return False
    
    def count_high_level_pets(self, pets):
        """
        统计等级大于100的宠物数量
        
        Args:
            pets: 宠物数据列表
            
        Returns:
            int: 高等级宠物数量
        """
        try:
            if not pets or not isinstance(pets, list):
                return 0
            
            high_level_count = 0
            for pet in pets:
                if isinstance(pet, dict):
                    # 从宠物数据中获取等级
                    pet_level = pet.get('iGrade', 0)
                    if isinstance(pet_level, (int, float)) and pet_level > 100:
                        high_level_count += 1
                    elif isinstance(pet_level, str):
                        try:
                            level_num = int(pet_level)
                            if level_num > 100:
                                high_level_count += 1
                        except ValueError:
                            continue
            
            return high_level_count
            
        except Exception as e:
            log_error(self.logger, f"统计高等级宠物时出错: {e}")
            return 0
    
    def get_empty_reason(self, all_equips, pets):
        """
        获取空号识别原因
        
        Args:
            all_equips: 装备数据
            pets: 宠物数据
            
        Returns:
            str: 空号识别原因
        """
        try:
            reasons = []
            
            # 检查物品数量
            equip_count = 0
            if all_equips and isinstance(all_equips, dict):
                # 计算装备数量（排除特殊字段）
                for key, value in all_equips.items():
                    if key.isdigit() and isinstance(value, dict):
                        equip_count += 1
            
            if equip_count == 0:
                reasons.append("无物品")
            
            # 检查高等级宠物
            high_level_pet_count = self.count_high_level_pets(pets)
            if high_level_pet_count == 0:
                total_pets = len(pets) if pets else 0
                if total_pets == 0:
                    reasons.append("无宠物")
                else:
                    reasons.append(f"无高级宠物(共{total_pets}只宠物)")
            
            return " + ".join(reasons) if reasons else "空号"
            
        except Exception as e:
            log_error(self.logger, f"获取空号原因时出错: {e}")
            return "识别异常"