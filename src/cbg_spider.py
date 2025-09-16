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
from sqlalchemy import create_engine, text
from app import create_app

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
        
        # 配置专用的日志器，使用统一日志工厂
        self.logger, self.log_file = get_spider_logger('role')
        
        # 初始化MySQL数据库连接
        self.init_database()

        # 初始化智能数据库助手（使用MySQL）
        self.smart_db = CBGSmartDB(self.db_url)
        
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
        """初始化MySQL数据库连接"""
        try:
            # 创建Flask应用上下文获取数据库配置
            app = create_app()
            
            with app.app_context():
                # 获取数据库配置
                self.db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
                if not self.db_url:
                    raise ValueError("未找到数据库配置")
                
                # 创建数据库引擎
                self.engine = create_engine(
                    self.db_url, 
                    pool_pre_ping=True, 
                    pool_recycle=3600
                )
                
                log_info(self.logger, f"MySQL数据库连接初始化完成: {self.db_url}")
                
                # 测试数据库连接
                try:
                    with self.engine.connect() as conn:
                        result = conn.execute(text("SELECT 1 as test"))
                        test_result = result.fetchone()
                        log_info(self.logger, f"数据库连接测试成功: {test_result[0]}")
                except Exception as e:
                    log_error(self.logger, f"数据库连接测试失败: {e}")
                
        except Exception as e:
            log_error(self.logger, f"初始化MySQL数据库失败: {e}")
            raise

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
        
        
    def _build_role_basic_data(self, char, life_skills, school_skills, ju_qing_skills, yushoushu_skill, is_empty_role):
        """构建角色基础数据"""
        # 预定义字段映射，减少重复的字典访问
        BASIC_FIELDS = [
            'eid', 'equipid', 'equip_sn', 'server_name', 'serverid', 'equip_server_sn',
            'seller_nickname', 'seller_roleid', 'area_name', 'equip_name', 'equip_type',
            'equip_type_name', 'equip_type_desc', 'level', 'equip_level', 'equip_level_desc',
            'level_desc', 'subtitle', 'equip_pos', 'position', 'school', 'role_grade_limit',
            'min_buyer_level', 'equip_count', 'price', 'price_desc', 'unit_price_desc',
            'min_unit_price', 'equip_status', 'equip_status_desc', 'status_desc',
            'onsale_expire_time_desc', 'time_left', 'expire_time', 'selling_time',
            'selling_time_ago_desc', 'first_onsale_time', 'pass_fair_show', 'fair_show_time',
            'fair_show_end_time', 'fair_show_end_time_left', 'fair_show_poundage',
            'collect_num', 'score', 'icon_index', 'icon', 'equip_face_img', 'kindid',
            'game_channel', 'game_ordersn', 'whole_game_ordersn', 'allow_cross_buy',
            'cross_server_poundage', 'cross_server_poundage_origin', 'cross_server_poundage_discount',
            'cross_server_poundage_discount_label', 'cross_server_poundage_display_mode',
            'cross_server_activity_conf_discount', 'activity_type', 'onsale_protection_end_time',
            'is_show_expert_desc', 'equip_onsale_version', 'storage_type', 'agent_trans_time',
            'kol_article_id', 'kol_share_id', 'kol_share_time', 'kol_share_status',
            'reco_request_id', 'appointed_roleid', 'play_team_cnt', 'random_draw_finish_time',
            'desc', 'large_equip_desc', 'desc_sumup', 'desc_sumup_short', 'diy_desc',
            'rec_desc', 'search_type', 'tag', 'other_info', 'tag_key'
        ]
        
        BOOLEAN_FIELDS = [
            'accept_bargain', 'has_collect', 'joined_seller_activity', 'is_split_sale',
            'is_split_main_role', 'is_split_independent_role', 'is_split_independent_equip',
            'split_equip_sold_happen', 'show_split_equip_sold_remind', 'is_onsale_protection_period',
            'is_vip_protection', 'is_time_lock', 'equip_in_test_server', 'buyer_in_test_server',
            'equip_in_allow_take_away_server', 'is_weijianding', 'is_show_alipay_privilege',
            'is_seller_redpacket_flag', 'is_show_special_highlight', 'is_xyq_game_role_kunpeng_reach_limit'
        ]
        
        JSON_FIELDS = [
            'price_explanation', 'bargain_info', 'diy_desc_pay_info', 'video_info',
            'agg_added_attrs', 'dynamic_tags', 'highlight'
        ]
        
        role_data = {}
        
        # 基本字段映射
        for field in BASIC_FIELDS:
            if field == 'create_time_equip':
                role_data[field] = char.get('create_time')
            else:
                role_data[field] = char.get(field, '')
        
        # Boolean字段转换
        for field in BOOLEAN_FIELDS:
            role_data[field] = 1 if char.get(field) else 0
        
        # JSON字段序列化
        for field in JSON_FIELDS:
            value = char.get(field)
            if value:
                try:
                    role_data[field] = json.dumps(value, ensure_ascii=False)
                except (TypeError, ValueError):
                    role_data[field] = ''
            else:
                role_data[field] = ''
        
        # 技能信息
        role_data.update({
            'life_skills': life_skills,
            'school_skills': school_skills,
            'ju_qing_skills': ju_qing_skills,
            'yushoushu_skill': yushoushu_skill,
            'role_type': 'empty' if is_empty_role else 'normal',
            'create_time_equip': char.get('create_time')
        })
        
        return role_data
    
    def _build_large_equip_data(self, char, parsed_desc):
        """构建详细装备数据"""
        def safe_int(value, default=0):
            if value is None:
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        
        def safe_str(value, default=''):
            if value is None:
                return default
            return str(value)
        
        def safe_json_dumps(data):
            if not data:
                return ''
            try:
                return json.dumps(data, ensure_ascii=False)
            except (TypeError, ValueError):
                return ''
        
        # 构建数据字典
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
            'all_new_point': safe_int(parsed_desc.get('TA_iAllNewPoint')),
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
            # JSON字段
            'pet': safe_json_dumps(parsed_desc.get('pet', {})),
            'all_skills_json': safe_json_dumps(parsed_desc.get('all_skills', {})),
            'all_equip_json': safe_json_dumps(parsed_desc.get('AllEquip', {})),
            'all_summon_json': safe_json_dumps(parsed_desc.get('AllSummon', {})),
            'child_json': safe_json_dumps(parsed_desc.get('child', {})),
            'child2_json': safe_json_dumps(parsed_desc.get('child2', {})),
            'all_rider_json': safe_json_dumps(parsed_desc.get('AllRider', {})),
            'ex_avt_json': safe_json_dumps(parsed_desc.get('ExAvt', {})),
            'huge_horse_json': safe_json_dumps(parsed_desc.get('HugeHorse', {})),
            'fabao_json': safe_json_dumps(parsed_desc.get('fabao', {})),
            'lingbao_json': safe_json_dumps(parsed_desc.get('lingbao', {})),
            'shenqi_json': safe_json_dumps(parsed_desc.get('shenqi', {})),
            'idbid_desc_json': safe_json_dumps(parsed_desc.get('idbid_desc', {})),
            'changesch_json': safe_json_dumps(parsed_desc.get('changesch', {})),
            'prop_kept_json': safe_json_dumps(parsed_desc.get('propKept', {})),
            'more_attr_json': safe_json_dumps(parsed_desc.get('more_attr', {}))
        }
        
        # 技能字段
        for i in range(1, 6):
            equip_data[f'expt_ski{i}'] = safe_int(parsed_desc.get(f'iExptSki{i}'))
        for i in range(1, 5):
            equip_data[f'max_expt{i}'] = safe_int(parsed_desc.get(f'iMaxExpt{i}'))
            equip_data[f'beast_ski{i}'] = safe_int(parsed_desc.get(f'iBeastSki{i}'))
        
        return equip_data
    
    def save_role_data(self, roles):
        """批量保存角色数据到数据库，使用统一事务"""
        if not roles:
            log_warning(self.logger, "没有要保存的角色数据")
            return 0
        
        # 准备批量数据
        roles_batch = []
        large_equip_batch = []
        
        for char in roles:
            try:
                # 跳过花样年华服务器
                server_name = char.get('serverName')
                if server_name == '花样年华':
                    log_info(self.logger, f"{char.get('seller_nickname')} 服务器为花样年华,不予记录。")
                    continue
                
                # 解析技能和装备信息
                large_equip_desc = char.get('large_equip_desc', '')
                parsed_desc = self.parse_large_equip_desc(large_equip_desc) if large_equip_desc else {}
                all_skills = parsed_desc.get('all_skills', {})
                
                # 提取技能信息
                life_skills = self.parse_life_skills(all_skills)
                school_skills = self.parse_school_skills(all_skills)
                ju_qing_skills = self.parse_ju_qing_skills(all_skills)
                yushoushu_skill = self.parse_yushoushu_skill(all_skills)
                
                # 空号识别
                is_empty_role = self.is_empty_role(
                    parsed_desc.get('AllEquip', {}), 
                    parsed_desc.get('AllSummon', {}), 
                    char.get('eid')
                )
                
                # 构建角色基础数据
                role_data = self._build_role_basic_data(
                    char, life_skills, school_skills, ju_qing_skills, yushoushu_skill, is_empty_role
                )
                roles_batch.append(role_data)
                
                # 记录日志
                role_type_desc = "(空号)" if is_empty_role else ""
                log_info(self.logger, f"￥{char.get('price_desc')} - {char.get('seller_nickname')}{role_type_desc}")
                
                # 处理详细装备数据
                if large_equip_desc and parsed_desc:
                    try:
                        equip_data = self._build_large_equip_data(char, parsed_desc)
                        large_equip_batch.append(equip_data)
                        self.logger.debug(f"准备详细数据: {char.get('eid')} (role_type: {role_data.get('role_type')})")
                    except Exception as e:
                        self.logger.error(f"解析装备详细信息时出错: {str(e)}")
                
            except Exception as e:
                self.logger.error(f"处理角色 {char.get('eid')} 时出错: {str(e)}")
                continue
        
        # 批量保存数据
        return self._save_batch_data(roles_batch, large_equip_batch)
    
    def _save_batch_data(self, roles_batch, large_equip_batch):
        """批量保存数据"""
        saved_count = 0
        
        # 保存角色数据
        if roles_batch:
            try:
                self.logger.info(f"开始批量保存 {len(roles_batch)} 条角色数据...")
                result = self.smart_db.save_roles_batch(roles_batch)
                if result:
                    saved_count = len(roles_batch)
                    self.logger.info(f"批量保存角色数据成功: {saved_count} 条")
                else:
                    self.logger.error("批量保存角色数据失败")
                    return 0
            except Exception as e:
                self.logger.error(f"批量保存角色数据时出错: {str(e)}")
                return 0
        
        # 保存详细装备数据
        if large_equip_batch:
            try:
                self.logger.info(f"开始批量保存 {len(large_equip_batch)} 条详细装备数据...")
                result = self.smart_db.save_large_equip_batch(large_equip_batch)
                if result:
                    self.logger.info(f"批量保存详细装备数据成功: {len(large_equip_batch)} 条")
                else:
                    self.logger.error("批量保存详细装备数据失败")
            except Exception as e:
                self.logger.error(f"批量保存详细装备数据时出错: {str(e)}")
        
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
        
        # 强制刷新所有日志缓冲区，确保日志被完整写入文件
        import sys
        sys.stdout.flush()
        sys.stderr.flush()
        
        # 刷新日志处理器缓冲区
        for handler in self.logger.handlers:
            if hasattr(handler, 'flush'):
                handler.flush()
                
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
                'server_type': 3,# 默认3年外服务器
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
    
    def is_empty_role(self, all_equips, pets, eid):
        """
        判断是否为空号
        空号条件：物品个数等于0，且召唤兽等级大于100的数量为0
        
        Args:
            all_equips: 装备数据
            pets: 召唤兽数据
            eid: 角色ID
            
        Returns:
            bool: True表示是空号，False表示不是空号
        """
        try:
            # 检查数据库中是否已标记为空号
            if self.check_role_type_in_db(eid) == 'empty':
                return True
            
            # 检查物品个数
            equip_count = 0
            if all_equips and isinstance(all_equips, dict):
                # 计算装备数量（排除特殊字段）
                for key, value in all_equips.items():
                    if key.isdigit() and isinstance(value, dict):
                        equip_count += 1
            
            # 检查高等级召唤兽数量（等级大于100）
            high_level_pet_count = self.count_high_level_pets(pets)
            
            # 空号判断：物品个数为0 且 高等级召唤兽数量为0
            is_empty = (equip_count == 0) and (high_level_pet_count == 0)
            
            if is_empty:
                # self.logger.debug(f"识别空号: {char_data.get('seller_nickname')} - 物品数:{equip_count}, 高级召唤兽数:{high_level_pet_count}")
                pass
            
            return is_empty
            
        except Exception as e:
            log_error(self.logger, f"判断空号时出错: {e}")
            return False
    
    def check_role_type_in_db(self, eid):
        """
        检查数据库中角色的role_type
        
        Args:
            eid: 角色ID
            
        Returns:
            str: 'empty' 或 'normal' 或 None
        """
        try:
            with self.engine.connect() as conn:
                query = text("SELECT role_type FROM roles WHERE eid = :eid")
                result = conn.execute(query, {'eid': eid}).fetchone()
                if result:
                    return result[0]
                return None
        except Exception as e:
            self.logger.error(f"检查角色类型失败: {e}")
            return None
    
    def count_high_level_pets(self, pets):
        """
        统计等级大于100的召唤兽数量
        
        Args:
            pets: 召唤兽数据列表
            
        Returns:
            int: 高等级召唤兽数量
        """
        try:
            if not pets or not isinstance(pets, list):
                return 0
            
            high_level_count = 0
            for pet in pets:
                if isinstance(pet, dict):
                    # 从召唤兽数据中获取等级
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
            log_error(self.logger, f"统计高等级召唤兽时出错: {e}")
            return 0
    