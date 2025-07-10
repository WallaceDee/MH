#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
梦幻西游藏宝阁爬虫核心模块
使用推荐接口获取角色数据，请通过run.py启动
"""

import os
import sys

# 添加项目根目录到Python路径，解决模块导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # 向上一级到项目根目录
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
from src.cbg_config import DB_TABLE_SCHEMAS, DB_TABLE_ORDER

# 导入解析器类
from src.parser.pet_parser import PetParser
from src.parser.equipment_parser import EquipmentParser
from src.parser.shenqi_parser import ShenqiParser
from src.parser.rider_parser import RiderParser
from src.parser.ex_avt_parser import ExAvtParser
from src.parser.common_parser import CommonParser
from src.parser.fabao_parser import FabaoParser
from src.utils.lpc_helper import LPCHelper

# 导入导出器类
from src.exporter.excel_exporter import CBGExcelExporter
from src.exporter.json_exporter import CBGJSONExporter, export_single_character_to_json

# 导入统一日志工厂
from src.spider.logger_factory import get_spider_logger, log_progress, log_page_complete, log_task_complete, log_error, log_warning, log_info, log_total_pages

# 定义一个特殊的标记，用于表示登录已过期
LOGIN_EXPIRED_MARKER = "LOGIN_EXPIRED"

class CBGSpider:
    def __init__(self):
        self.session = setup_session()
        self.base_url = 'https://xyq.cbg.163.com/cgi-bin/recommend.py'
        self.output_dir = self.create_output_dir()
        
        # 使用按月分割的数据库文件路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        current_month = datetime.now().strftime('%Y%m')
        
        # 正常角色数据库路径
        db_filename = f"cbg_characters_{current_month}.db"
        self.db_path = os.path.join(project_root, 'data', db_filename)
        
        # 空号数据库路径（单独的数据库文件）
        empty_db_filename = f"empty_characters_{current_month}.db"
        self.empty_db_path = os.path.join(project_root, 'data', empty_db_filename)
        
        # 确保data目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 初始化智能数据库助手（正常角色）
        self.smart_db = CBGSmartDB(self.db_path)
        
        # 初始化空号数据库助手（空号专用）
        self.empty_smart_db = CBGSmartDB(self.empty_db_path)
        
        # 配置专用的日志器，使用统一日志工厂
        self.logger, self.log_file = get_spider_logger('role')
        
        # 初始化宠物解析器
        self.pet_parser = PetParser(self.logger)
        
        # 初始化装备解析器
        self.equipment_parser = EquipmentParser(self.logger)
        
        # 初始化神器解析器
        self.shenqi_parser = ShenqiParser(self.logger)
        
        # 初始化坐骑解析器
        self.rider_parser = RiderParser(self.logger)
        
        # 初始化锦衣解析器
        self.ex_avt_parser = ExAvtParser(self.logger)
        
        # 初始化通用解析器
        self.common_parser = CommonParser(self.logger)

        # 初始化法宝解析器
        self.fabao_parser = FabaoParser(self.logger)
        
        # 初始化LPC解析助手
        self.lpc_helper = LPCHelper(self.logger)
        
        # 初始化其他组件
        self.setup_session()
        self.init_database()
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
        # 从cookies.txt文件读取Cookie
        cookie_content = None
        try:
            # 获取项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cookies_path = os.path.join(project_root, 'config/cookies.txt')
            
            with open(cookies_path, 'r', encoding='utf-8') as f:
                cookie_content = f.read().strip()
            if cookie_content:
                self.session.headers.update({'Cookie': cookie_content})
                log_info(self.logger, "成功从config/cookies.txt文件加载Cookie")
            else:
                log_warning(self.logger, "config/cookies.txt文件为空")
                
        except FileNotFoundError:
            log_error(self.logger, "未找到config/cookies.txt文件，请创建该文件并添加有效的Cookie")
        except Exception as e:
            log_error(self.logger, f"读取config/cookies.txt文件失败: {e}")
        
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
            'referer': 'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py'
        }
        
        # 如果有Cookie，添加到请求头中
        if cookie_content:
            headers['Cookie'] = cookie_content
            log_info(self.logger, "Cookie已添加到请求头")
        else:
            log_warning(self.logger, "未找到有效的Cookie，可能影响数据获取")
        
        self.session.headers.update(headers)
    
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
            
            # 创建正常角色相关的表（排除empty_characters表）
            normal_tables = [table for table in DB_TABLE_ORDER if table != 'empty_characters']
            
            for table_name in normal_tables:
                if table_name in DB_TABLE_SCHEMAS:
                    cursor.execute(DB_TABLE_SCHEMAS[table_name])
                    # self.logger.debug(f"正常角色数据库创建表: {table_name}")
                else:
                    log_warning(self.logger, f"未找到表 {table_name} 的结构定义")
            
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
            
            # 在空号数据库中创建characters表（使用empty_characters表结构）
            cursor.execute(DB_TABLE_SCHEMAS['empty_characters'])
            # self.logger.debug(f"空号数据库创建表: characters")
            
            # 也创建large_equip_desc_data表，以防需要存储详细数据
            cursor.execute(DB_TABLE_SCHEMAS['large_equip_desc_data'])
            # self.logger.debug(f"空号数据库创建表: large_equip_desc_data")
            
            conn.commit()
            log_info(self.logger, f"空号数据库初始化完成: {os.path.basename(self.empty_db_path)}")
            
        except Exception as e:
            log_error(self.logger, f"初始化空号数据库失败: {e}")
            raise
        finally:
            conn.close()

    def get_school_name(self, school_id):
        """根据门派ID获取门派名称"""
        return self.common_parser.get_school_name(school_id)
    
    def get_race_name(self, school_id):
        """根据门派ID获取种族名称"""
        return self.common_parser.get_race_name(school_id)
    
    def get_fly_status(self, equip_data):
        """解析飞升状态（从large_equip_desc字段中解析）"""
        return self.common_parser.get_fly_status(equip_data)
    
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
                    return self.extract_character_fields(parsed_data)
            
            log_warning(self.logger, f"LPC->JS解析失败，原始数据前200字符: {clean_desc[:200]}")
            return {}
            
        except Exception as e:
            log_warning(self.logger, f"解析large_equip_desc失败: {e}")
            return {}
    
    def extract_character_fields(self, parsed_data):
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
            
            if not equip_list:
                self.logger.warning("没有找到任何角色数据")
                return []
                
            characters = []
            for equip in equip_list:
                try:
                    # 解析基本信息
                    char = {
                        'eid': equip.get('eid'),
                        'serverName': equip.get('server_name'),
                        'sellerNickname': equip.get('seller_nickname'),  # 使用seller_nickname作为角色名
                        'level': equip.get('level'),
                        'price': float(equip.get('price_desc', '0')),
                        'priceDesc': equip.get('price_desc'),
                        'school': self.get_school_name(equip.get('school')),  # 转换门派为中文
                        'areaName': equip.get('area_name'),
                        'iconIndex': equip.get('icon_index'),
                        'kindId': equip.get('kindid'),
                        'gameOrdersn': equip.get('game_ordersn'),
                        'passFairShow': equip.get('pass_fair_show'),
                        'fairShowEndTime': equip.get('fair_show_end_time'),
                        'acceptBargain': equip.get('accept_bargain'),
                        'statusDesc': equip.get('status_desc'),
                        'onsaleExpireTimeDesc': equip.get('onsale_expire_time_desc'),
                        'expire_time': equip.get('expire_time'),
                        'flyStatus': self.get_fly_status(equip),
                        # 基础字段
                        'collectNum': equip.get('collect_num'),
                        
                        # 角色属性字段
                        'race': self.get_race_name(equip.get('school'))
                    }
                    
                    # 添加large_equip_desc字段（如果存在）
                    if 'large_equip_desc' in equip:
                        char['large_equip_desc'] = equip['large_equip_desc']
                    
                    # 解析角色属性
                    if 'attrs' in equip:
                        attrs = equip['attrs']
                        char['attributes'] = {
                            'hp': attrs.get('hp'),
                            'mp': attrs.get('mp'),
                            'attack': attrs.get('attack'),
                            'defense': attrs.get('defense'),
                            'speed': attrs.get('speed'),
                            'wiz': attrs.get('wiz'),
                            'skills': attrs.get('skills', []),
                            'specialSkill': attrs.get('special_skill'),
                            'sumExp': attrs.get('sum_exp'),
                            'exp': attrs.get('exp'),

                            
                            # 基础属性字段
                            'baseHp': attrs.get('base_hp'),
                            'baseMp': attrs.get('base_mp'),
                            'baseAttack': attrs.get('base_attack'),
                            'baseDefense': attrs.get('base_defense'),
                            'baseSpeed': attrs.get('base_speed'),
                            'baseWiz': attrs.get('base_wiz'),
                            'extraHp': attrs.get('extra_hp'),
                            'extraMp': attrs.get('extra_mp'),
                            'extraAttack': attrs.get('extra_attack'),
                            'extraDefense': attrs.get('extra_defense'),
                            'extraSpeed': attrs.get('extra_speed'),
                            'extraWiz': attrs.get('extra_wiz'),
                            
                            # 其他属性字段
                            
                            # 战斗属性字段
                            'damageAll': attrs.get('damage_all'),
                            'magicDamageAll': attrs.get('magic_damage_all'),
                            'magicDefenseAll': attrs.get('magic_defense_all'),
                            'dodgeAll': attrs.get('dodge_all'),
                            'hitAll': attrs.get('hit_all'),
                            'critAll': attrs.get('crit_all')
                        }
                    
                    # 解析装备信息
                    if 'equip_list' in equip:
                        char['equipments'] = []
                        for item in equip['equip_list']:
                            equipment = {
                                'position': item.get('position'),
                                'name': item.get('name'),
                                'level': item.get('level'),
                                'quality': item.get('quality'),
                                'attributes': item.get('attributes', []),
                                'specialEffects': item.get('special_effects', []),
                                'durability': item.get('durability'),
                                
                                # 新增装备字段
                                'itemId': item.get('item_id'),
                                'type': item.get('type'),
                                'subType': item.get('sub_type'),
                                'color': item.get('color'),
                                'bindType': item.get('bind_type'),
                                'maxDurability': item.get('max_durability'),
                                'repairCount': item.get('repair_count'),
                                'stoneCount': item.get('stone_count'),
                                'stoneAttributes': item.get('stone_attributes', []),
                                'enhanceLevel': item.get('enhance_level'),
                                'enhanceAttributes': item.get('enhance_attributes', []),
                                'specialSkill': item.get('special_skill'),
                                'specialEffect': item.get('special_effect'),
                                'creatorName': item.get('creator_name'),
                                'createTime': item.get('create_time'),
                                'expireTime': item.get('expire_time'),
                                
                                # 锁定状态字段
                                'isLocked': item.get('iLock', 0),
                                'lockType': item.get('iLockType', 0),
                                'lockExpireTime': item.get('iLockExpireTime', 0)
                            }
                            char['equipments'].append(equipment)
                    
                    # 解析宝宝信息
                    
                    # 从large_equip_desc中解析宝宝信息
                    large_desc = equip.get('large_equip_desc', '')
                    if large_desc:
                        try:
                            parsed_data = self.parse_large_equip_desc(large_desc)
                            
                            # 使用装备解析器的统一处理方法
                            char['all_equips'] = self.equipment_parser.process_character_equipment(parsed_data, char.get('sellerNickname', '未知'))
                            # 使用宠物解析器的统一处理方法
                            char['pets'] = self.pet_parser.process_character_pets(parsed_data, char.get('sellerNickname', '未知'))
                                
                        except Exception as e:
                            self.logger.error(f"解析装备/宝宝信息失败: {e}")
                            char['pets'] = []
                            char['all_equips'] = {"装备总数": 0, "使用中装备": [], "未使用装备": [], "拆分销售装备": []}
                    else:
                        self.logger.debug("large_equip_desc为空，跳过宝宝解析")
                        char['pets'] = []
                        char['all_equips'] = {"装备总数": 0, "使用中装备": [], "未使用装备": [], "拆分销售装备": []}
                    
                    characters.append(char)
                    
                except Exception as e:
                    self.logger.error(f"解析单个角色数据时出错: {str(e)}")
                    continue
            
            return characters
            
        except Exception as e:
            self.logger.error(f"解析JSONP响应时发生错误: {str(e)}")
            return None
    
    def save_character_data(self, characters):
        """保存角色数据到数据库"""
        if not characters:
            log_warning(self.logger, "没有要保存的角色数据")
            return 0
            
        saved_count = 0
        for char in characters:
            try:
                # 检查是否需要切换数据库（检查当前月份是否变化）
                current_month = datetime.now().strftime('%Y%m')
                current_db_filename = f"cbg_characters_{current_month}.db"
                current_empty_db_filename = f"empty_characters_{current_month}.db"
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                current_db_path = os.path.join(project_root, 'data', current_db_filename)
                current_empty_db_path = os.path.join(project_root, 'data', current_empty_db_filename)
                
                # 如果当前数据库路径与实例的数据库路径不同，需要重新初始化数据库连接
                if current_db_path != self.db_path or current_empty_db_path != self.empty_db_path:
                    log_info(self.logger, f"检测到月份变化，切换到新的数据库:")
                    log_info(self.logger, f"  正常角色数据库: {current_db_filename}")
                    log_info(self.logger, f"  空号数据库: {current_empty_db_filename}")
                    
                    # 更新数据库路径
                    self.db_path = current_db_path
                    self.empty_db_path = current_empty_db_path
                    
                    # 重新初始化数据库连接
                    self.smart_db = CBGSmartDB(self.db_path)
                    self.empty_smart_db = CBGSmartDB(self.empty_db_path)
                    
                    # 确保新数据库的表结构已创建
                    self.init_database()
                
                # 解析技能信息（如果有large_equip_desc数据）
                life_skills = ''
                school_skills = ''
                ju_qing_skills = ''
                yushoushu_skill = 0

                large_equip_desc = char.get('large_equip_desc')
                server_name = char.get('serverName')
                if(server_name == '花样年华'):
                    log_info(self.logger, f"{char.get('sellerNickname')} 服务器为花样年华,不予记录。")
                    continue
                if large_equip_desc:
                    try:
                        parsed_desc = self.parse_large_equip_desc(large_equip_desc)
                        if parsed_desc and 'all_skills' in parsed_desc:
                            all_skills = parsed_desc['all_skills']
                            if isinstance(all_skills, dict):
                                # 解析各种技能
                                life_skills = self.parse_life_skills(all_skills)
                                school_skills = self.parse_school_skills(all_skills)
                                ju_qing_skills = self.parse_ju_qing_skills(all_skills)
                                yushoushu_skill = self.parse_yushoushu_skill(all_skills)

                    except Exception as e:
                        log_warning(self.logger, f"解析角色 {char.get('eid')} 的技能信息失败: {e}")
                
                # 解析large_equip_desc字段
                parsed_desc = self.parse_large_equip_desc(char.get('large_equip_desc', ''))
                
                # 1. 保存角色基础信息
                character_data = {
                    'equip_id': char.get('eid'),
                    'server_name': server_name,
                    'seller_nickname': char.get('sellerNickname'),
                    'level': char.get('level'),
                    'price': char.get('price'),
                    'price_desc': char.get('priceDesc'),
                    'school': char.get('school'),
                    'area_name': char.get('areaName'),
                    'icon_index': char.get('iconIndex'),
                    'kindid': char.get('kindId'),
                    'game_ordersn': char.get('gameOrdersn'),
                    'pass_fair_show': char.get('passFairShow'),
                    'fair_show_end_time': char.get('fairShowEndTime'),
                    'accept_bargain': char.get('acceptBargain'),
                    'status_desc': char.get('statusDesc'),
                    'onsale_expire_time_desc': char.get('onsaleExpireTimeDesc'),
                    'expire_time': char.get('expire_time'),
                    'race': char.get('race'),
                    'fly_status': char.get('flyStatus'),
                    'collect_num': char.get('collectNum'),
                    'create_time': datetime.now().isoformat(),
                    'life_skills': life_skills,
                    'school_skills': school_skills,
                    'ju_qing_skills': ju_qing_skills,
                    'yushoushu_skill': yushoushu_skill
                }
                
                # 处理宠物数据（保存all_pets_json）
                pets = char.get('pets', [])
                if pets:
                    character_data['all_pets_json'] = json.dumps(pets, ensure_ascii=False)
                    # self.logger.debug(f"保存宝宝信息: 共{len(pets)}只宝宝，中文JSON格式")
                else:
                    character_data['all_pets_json'] = ''
                
                # 处理装备信息（保存到characters表）
                all_equips = char.get('all_equips')
                if all_equips:
                    character_data['all_equip_json'] = json.dumps(all_equips, ensure_ascii=False)
                    # self.logger.debug(f"保存装备信息到characters表: {len(json.dumps(all_equips, ensure_ascii=False))} 字符")
                else:
                    character_data['all_equip_json'] = ''
                
                # 处理神器信息（保存到characters表）
                if parsed_desc and parsed_desc.get('shenqi'):
                    # 使用神器解析器处理神器数据
                    all_shenqi = self.shenqi_parser.process_character_shenqi(parsed_desc, char.get('sellerNickname', ''))
                    if all_shenqi and all_shenqi.get('神器名称'):
                        character_data['all_shenqi_json'] = json.dumps(all_shenqi, ensure_ascii=False)
                        # self.logger.debug(f"保存神器信息到characters表: {len(character_data['all_shenqi_json'])} 字符")
                    else:
                        character_data['all_shenqi_json'] = ''
                else:
                    character_data['all_shenqi_json'] = ''
                
                # 处理坐骑信息（保存到characters表）
                if parsed_desc and parsed_desc.get('AllRider'):
                    # 使用坐骑解析器处理坐骑数据
                    all_rider = self.rider_parser.process_character_rider({'rider': parsed_desc.get('AllRider')}, char.get('sellerNickname', ''))
                    if all_rider and all_rider.get('坐骑列表'):
                        character_data['all_rider_json'] = json.dumps(all_rider, ensure_ascii=False)
                        # self.logger.debug(f"保存坐骑信息到characters表: {len(character_data['all_rider_json'])} 字符")
                    else:
                        character_data['all_rider_json'] = ''
                else:
                    character_data['all_rider_json'] = ''

                # 处理法宝信息（保存到characters表）
                if parsed_desc and parsed_desc.get('fabao_json'):
                    # 使用法宝解析器处理法宝数据
                    all_fabao = self.fabao_parser.process_character_fabao(parsed_desc, char.get('sellerNickname', ''))
                    if all_fabao:
                        character_data['all_fabao_json'] = json.dumps(all_fabao, ensure_ascii=False)
                        # self.logger.debug(f"保存法宝信息到characters表: {len(character_data['all_fabao_json'])} 字符")
                    else:
                        character_data['all_fabao_json'] = ''
                else:
                    character_data['all_fabao_json'] = ''    

                # 处理锦衣信息（保存到characters表）
                if parsed_desc and parsed_desc.get('ExAvt'):
                    # 构建锦衣数据，包含基础信息和特效信息
                    ex_avt_data = {
                        'ExAvt': parsed_desc.get('ExAvt'),
                        'basic_info': {
                            'total_avatar': parsed_desc.get('total_avatar', 0),
                            'xianyu': parsed_desc.get('xianyu', 0),
                            'xianyu_score': parsed_desc.get('xianyu_score', 0),
                            'qicai_score': parsed_desc.get('qicai_score', 0)
                        },
                        'chat_effect': parsed_desc.get('chat_effect'),
                        'icon_effect': parsed_desc.get('icon_effect'),
                        'title_effect': parsed_desc.get('title_effect'),
                        'perform_effect': parsed_desc.get('perform_effect'),
                        'achieve_show': parsed_desc.get('achieve_show', []),
                        'avt_widget': parsed_desc.get('avt_widget', {})
                    }
                    
                    # 使用锦衣解析器处理锦衣数据
                    all_ex_avt = self.ex_avt_parser.process_character_clothes(ex_avt_data, char.get('sellerNickname', ''))
                    # 检查解析结果：ExAvtParser可能返回'锦衣'或'锦衣列表'字段
                    character_data['ex_avt_json'] = json.dumps(all_ex_avt, ensure_ascii=False)
                    # self.logger.debug(f"保存锦衣信息到characters表: {len(character_data['ex_avt_json'])} 字符")
                else:
                    character_data['ex_avt_json'] = ''
                
                # 空号识别逻辑
                is_empty_character = self.is_empty_character(char, all_equips, pets)
                
                if is_empty_character:
                    # 如果是空号，添加空号识别信息并保存到空号数据库
                    empty_reason = self.get_empty_reason(char, all_equips, pets)
                    character_data['empty_reason'] = empty_reason
                    character_data['equip_count'] = all_equips.get('物品总数', 0) if all_equips else 0
                    character_data['high_level_pet_count'] = self.count_high_level_pets(pets)
                    
                    # 保存到空号数据库的characters表
                    try:
                        self.empty_smart_db.save_character(character_data)
                        log_info(self.logger, f"识别并保存空号角色: ￥{char.get('price')} - {char.get('sellerNickname')} - {empty_reason}")
                        saved_count += 1
                    except Exception as e:
                        log_error(self.logger, f"保存空号数据失败: ￥{char.get('price')}, 错误: {e}")
                else:
                    # 如果不是空号，保存到正常角色数据库
                    try:
                        self.smart_db.save_character(character_data)
                        log_info(self.logger, f"识别并保存角色: ￥{char.get('price')} - {char.get('sellerNickname')}")
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
                            'equip_id': char.get('eid'),
                            'character_name': safe_str(parsed_desc.get('cName')),
                            'character_level': safe_int(parsed_desc.get('iGrade')),
                            'character_school': safe_int(parsed_desc.get('iSchool')),
                            'character_icon': safe_int(parsed_desc.get('iIcon')),
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
                            'character_title': safe_str(parsed_desc.get('title')),
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
                        if is_empty_character:
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
                
                # 为每个角色单独导出JSON数据到role_json文件夹
                # try:
                #     # 使用json_exporter中的方法导出
                #     self._export_single_character_json(character_data, large_equip_desc, parsed_desc)
                    
                # except Exception as e:
                #     self.logger.warning(f"保存角色 {character_data.get('equip_id')} 的单独JSON失败: {e}")
                
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
        from src.tools.search_form_helper import verify_cookie_validity
        if not verify_cookie_validity():
            self.logger.warning("Cookie验证失败，正在更新Cookie...")
            # 使用异步方式更新Cookie
            async def update_cookie():
                from src.utils.cookie_updater import _update_cookies_internal
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
        total_characters = 0
        successful_pages = 0
        
        # 输出总页数信息
        log_total_pages(self.logger, max_pages)
        
        # 获取搜索参数
        if search_params is None:
            try:
                if use_browser:
                    # 使用浏览器监听模式
                    log_info(self.logger, "启动浏览器监听模式收集参数...")
                    from src.tools.search_form_helper import get_search_params
                    search_params = get_search_params()
                    if not search_params:
                        search_params = {'server_type': 3}
                        log_warning(self.logger, "未能收集到搜索参数，将使用默认参数")
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
            saved_count = self.save_character_data(page_data)
            total_characters += saved_count
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
        log_task_complete(self.logger, successful_pages, max_pages, total_characters, "角色")
        return total_characters

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
                    cookie_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'cookies.txt')
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
    

    
    def export_to_excel(self, filename=None, months=None):
        """
        导出数据到Excel（使用独立的Excel导出器）
        
        Args:
            filename: 输出文件名
            months: 要导出的月份列表，格式为['202401', '202402']，如果为None则导出所有月份
            
        Returns:
            list: 导出的Excel文件路径列表
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(project_root, 'data')
        
        # 如果没有指定月份，获取所有数据库文件
        if months is None:
            db_files = [f for f in os.listdir(data_dir) if f.endswith('.db')]
        else:
            db_files = [f"cbg_characters_{month}.db" for month in months]
        
        exported_files = []
        for db_file in db_files:
            db_path = os.path.join(data_dir, db_file)
            if not os.path.exists(db_path):
                log_warning(self.logger, f"数据库文件不存在: {db_file}")
                continue
                
            # 为每个数据库创建Excel导出器
            excel_exporter = CBGExcelExporter(db_path, self.output_dir, self.logger)
            
            # 使用导出器导出数据
            excel_file = excel_exporter.export_to_excel(
                filename=f"{filename}_{db_file.replace('.db', '')}" if filename else None
            )
            if excel_file:
                exported_files.append(excel_file)
            
        return exported_files
    
    def export_to_json(self, filename=None, pretty=True, months=None):
        """
        导出数据到JSON（使用独立的JSON导出器）
        
        Args:
            filename: 输出文件名
            pretty: 是否格式化输出JSON
            months: 要导出的月份列表，格式为['202401', '202402']，如果为None则导出所有月份
            
        Returns:
            list: 导出的JSON文件路径列表
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(project_root, 'data')
        
        # 如果没有指定月份，获取所有数据库文件
        if months is None:
            db_files = [f for f in os.listdir(data_dir) if f.endswith('.db')]
        else:
            db_files = [f"cbg_characters_{month}.db" for month in months]
        
        exported_files = []
        for db_file in db_files:
            db_path = os.path.join(data_dir, db_file)
            if not os.path.exists(db_path):
                log_warning(self.logger, f"数据库文件不存在: {db_file}")
                continue
                
            # 为每个数据库创建JSON导出器
            json_exporter = CBGJSONExporter(db_path, self.output_dir, self.logger)
            
            # 使用导出器导出数据
            json_file = json_exporter.export_to_json(
                filename=f"{filename}_{db_file.replace('.db', '')}" if filename else None,
                pretty=pretty
            )
            if json_file:
                exported_files.append(json_file)
            
        return exported_files
    
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
    
    def get_rent_level_name(self, level):
        """转换房屋等级数字为中文名称"""
        return self.common_parser.get_rent_level_name(level)
    
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
    
    def is_empty_character(self, char_data, all_equips, pets):
        """
        判断是否为空号
        空号条件：物品个数等于0，且宠物等级大于100的数量为0
        
        Args:
            char_data: 角色基础数据
            all_equips: 装备数据
            pets: 宠物数据
            
        Returns:
            bool: True表示是空号，False表示不是空号
        """
        try:
            # 检查物品个数
            equip_count = 0
            if all_equips and isinstance(all_equips, dict):
                equip_count = all_equips.get('物品总数', 0)
            
            # 检查高等级宠物数量（等级大于100）
            high_level_pet_count = self.count_high_level_pets(pets)
            
            # 空号判断：物品个数为0 且 高等级宠物数量为0
            is_empty = (equip_count == 0) and (high_level_pet_count == 0)
            
            if is_empty:
                # self.logger.debug(f"识别空号: {char_data.get('sellerNickname')} - 物品数:{equip_count}, 高级宠物数:{high_level_pet_count}")
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
                    pet_level = pet.get('等级', 0)
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
    
    def get_empty_reason(self, char_data, all_equips, pets):
        """
        获取空号识别原因
        
        Args:
            char_data: 角色基础数据
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
                equip_count = all_equips.get('物品总数', 0)
            
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

    def _export_single_character_json(self, character_data, large_equip_desc, parsed_desc):
        """
        内部方法：为单个角色导出JSON数据到role_json文件夹
        
        Args:
            character_data: 角色基础数据
            large_equip_desc: 原始装备描述数据
            parsed_desc: 解析后的装备描述数据
        """
        try:
            # 合并数据
            full_character_data = character_data.copy()
            if large_equip_desc and parsed_desc:
                full_character_data.update(parsed_desc)
            
            # 使用json_exporter中的方法导出
            return export_single_character_to_json(
                character_data=full_character_data,
                output_dir=self.output_dir,
                logger=self.logger
            )
            
        except Exception as e:
            log_error(self.logger, f"导出单个角色JSON失败: {e}")
            return None

def main():
    """简单的测试函数 - 主要使用run.py启动"""
    print("CBG角色爬虫模块")
    print("请使用 'python run.py basic' 启动爬虫")

if __name__ == "__main__":
    main() 