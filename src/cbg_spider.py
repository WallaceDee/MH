#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
梦幻西游藏宝阁爬虫核心模块
使用推荐接口获取角色数据，请通过run.py启动
"""

import os
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
from tools.setup_requests_session import setup_session

# 导入智能数据库助手
try:
    from .utils.smart_db_helper import CBGSmartDB
    from .cbg_config import *
    from .exporter.excel_exporter import CBGExcelExporter
    from .exporter.json_exporter import CBGJSONExporter, export_single_character_to_json
    from .parser.pet_parser import PetParser
    from .parser.equipment_parser import EquipmentParser
    from .parser.shenqi_parser import ShenqiParser
    from .parser.rider_parser import RiderParser
    from .parser.ex_avt_parser import ExAvtParser
    from .parser.common_parser import CommonParser
    from .utils.lpc_helper import LPCHelper
    from .utils.api_logger import log_api_request
    from .utils.cookie_updater import update_cookies_with_playwright
except ImportError:
    from utils.smart_db_helper import CBGSmartDB
    from cbg_config import *
    from exporter.excel_exporter import CBGExcelExporter
    from exporter.json_exporter import CBGJSONExporter, export_single_character_to_json
    from parser.pet_parser import PetParser
    from parser.equipment_parser import EquipmentParser
    from parser.shenqi_parser import ShenqiParser
    from parser.rider_parser import RiderParser
    from parser.ex_avt_parser import ExAvtParser
    from parser.common_parser import CommonParser
    from utils.lpc_helper import LPCHelper
    from utils.api_logger import log_api_request
    from utils.cookie_updater import update_cookies_with_playwright

# 定义一个特殊的标记，用于表示登录已过期
LOGIN_EXPIRED_MARKER = "LOGIN_EXPIRED"

class CBGSpider:
    def __init__(self):
        self.session = setup_session()
        self.base_url = API_CONFIG['base_url']
        self.output_dir = self.create_output_dir()
        
        # 使用按月分割的数据库文件路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        current_month = datetime.now().strftime('%Y%m')
        db_filename = f"{FILE_PATHS['db_filename'].replace('.db', '')}_{current_month}.db"
        self.db_path = os.path.join(project_root, 'data', db_filename)
        
        # 确保data目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 初始化智能数据库助手
        self.smart_db = CBGSmartDB(self.db_path)
        
        # 配置日志
        log_file = os.path.join(self.output_dir, FILE_PATHS['log_filename'])
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
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
        
        # 初始化LPC解析助手
        self.lpc_helper = LPCHelper(self.logger)
        
        # 初始化其他组件
        self.setup_session()
        self.init_database()
        self.retry_attempts = 1 # 为登录失败重试设置次数
    
    def save_debug_file(self, parsed_data, character_name, save_debug=False):
        """保存调试文件"""
        if not save_debug or not parsed_data:
            return
            
        try:
            debug_dir = os.path.join(self.output_dir, 'original_role_json')
            os.makedirs(debug_dir, exist_ok=True)
            
            # 生成文件名（基于角色名称和时间戳）
            char_name = character_name or 'unknown'
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{char_name}_{timestamp}.json"
            filepath = os.path.join(debug_dir, filename)
            
            # 保存JSON数据到文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json.dumps(parsed_data, ensure_ascii=False, indent=2))
            
            self.logger.debug(f"调试文件已保存: {filepath}")
            
        except Exception as e:
            self.logger.error(f"保存调试文件失败: {e}")
    
    def create_output_dir(self):
        """创建输出目录"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_dir = os.path.join('output', timestamp)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def setup_session(self):
        """设置请求会话"""
        # 从cookies.txt文件读取Cookie
        cookie_content = None
        try:
            # 获取项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cookies_path = os.path.join(project_root, FILE_PATHS['cookies_path'])
            
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
            'referer': 'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py'
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
            
            # 按照指定顺序创建表（处理外键依赖关系）
            for table_name in DB_TABLE_ORDER:
                if table_name in DB_TABLE_SCHEMAS:
                    cursor.execute(DB_TABLE_SCHEMAS[table_name])
                    self.logger.debug(f"创建表: {table_name}")
                else:
                    self.logger.warning(f"未找到表 {table_name} 的结构定义")
            
            conn.commit()
            self.logger.info("数据库表初始化完成")
            
        except Exception as e:
            self.logger.error(f"初始化数据库失败: {e}")
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
            
            self.logger.warning(f"LPC->JS解析失败，原始数据前200字符: {clean_desc[:200]}")
            return {}
            
        except Exception as e:
            self.logger.warning(f"解析large_equip_desc失败: {e}")
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
                self.logger.error("响应不是有效的JSONP格式")
                return None
                
            json_str = text[start:end]
            data = json.loads(json_str)
            
            if not isinstance(data, dict):
                self.logger.error("解析JSONP响应失败：响应不是一个有效的JSON对象")
                return None
                
            # 记录所有key
            self.logger.info("API响应数据的所有key:")
            for key in data.keys():
                self.logger.info(f"- {key}")
                
            # 检查API响应状态
            if data.get('status') != 1:
                self.logger.error(data)
                # 检查是否是登录过期
                msg = data.get('msg', 'N/A')
                self.logger.error(f"API返回错误状态: {data.get('status')}, 消息: {msg}")
                # 检查是否是登录过期
                if data.get('status') == 2:
                    self.logger.warning("检测到登录状态失效 (relogin)。")
                    return LOGIN_EXPIRED_MARKER
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
                    self.logger.debug(f"开始解析宝宝信息")
                    
                    # 从large_equip_desc中解析宝宝信息
                    large_desc = equip.get('large_equip_desc', '')
                    if large_desc:
                        try:
                            parsed_data = self.parse_large_equip_desc(large_desc)
                            
                            # 使用装备解析器的统一处理方法
                            if parsed_data and 'AllEquip' in parsed_data:
                                equip_info = self.equipment_parser.process_character_equipment(
                                    parsed_data, char.get('sellerNickname', '未知')
                                )
                                char['all_equips'] = equip_info
                            else:
                                print(f"⚔️ [装备解析] 角色: {char.get('sellerNickname', '未知')}")
                                print("=" * 80)
                                print("✅ 装备解析完成! 总计: 使用中0件, 未使用0件, 拆分销售0件")
                                print("-" * 80)
                                char['all_equips'] = {"装备总数": 0, "使用中装备": [], "未使用装备": [], "拆分销售装备": []}
                            
                            # 保存调试文件（如果需要）
                            self.save_debug_file(parsed_data, char.get('sellerNickname', '未知'), save_debug=True)
                            
                            # 使用宠物解析器的统一处理方法
                            char['pets'] = self.pet_parser.process_character_pets(parsed_data, char.get('sellerNickname', '未知'))
                                
                        except Exception as e:
                            self.logger.error(f"解析宝宝信息失败: {e}")
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
            self.logger.warning("没有要保存的角色数据")
            return 0
            
        saved_count = 0
        for char in characters:
            try:
                # 检查是否需要切换数据库（检查当前月份是否变化）
                current_month = datetime.now().strftime('%Y%m')
                current_db_filename = f"{FILE_PATHS['db_filename'].replace('.db', '')}_{current_month}.db"
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                current_db_path = os.path.join(project_root, 'data', current_db_filename)
                
                # 如果当前数据库路径与实例的数据库路径不同，需要重新初始化数据库连接
                if current_db_path != self.db_path:
                    self.logger.info(f"检测到月份变化，切换到新的数据库: {current_db_filename}")
                    self.db_path = current_db_path
                    # 重新初始化数据库连接
                    self.smart_db = CBGSmartDB(self.db_path)
                    # 确保新数据库的表结构已创建
                    self.init_database()
                
                # 解析技能信息（如果有large_equip_desc数据）
                life_skills = ''
                school_skills = ''
                ju_qing_skills = ''
                
                large_equip_desc = char.get('large_equip_desc')
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
                    except Exception as e:
                        self.logger.warning(f"解析角色 {char.get('eid')} 的技能信息失败: {e}")
                
                # 解析large_equip_desc字段
                parsed_desc = self.parse_large_equip_desc(char.get('large_equip_desc', ''))
                
                # 1. 保存角色基础信息
                character_data = {
                    'equip_id': char.get('eid'),
                    'server_name': char.get('serverName'),
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
                    'ju_qing_skills': ju_qing_skills
                }
                
                # 处理宠物数据（保存all_pets_json）
                pets = char.get('pets', [])
                if pets:
                    character_data['all_pets_json'] = json.dumps(pets, ensure_ascii=False)
                    self.logger.debug(f"保存宝宝信息: 共{len(pets)}只宝宝，中文JSON格式")
                else:
                    character_data['all_pets_json'] = ''
                
                # 处理装备信息（保存到characters表）
                all_equips = char.get('all_equips')
                if all_equips:
                    character_data['all_equip_json'] = json.dumps(all_equips, ensure_ascii=False)
                    self.logger.debug(f"保存装备信息到characters表: {len(json.dumps(all_equips, ensure_ascii=False))} 字符")
                else:
                    character_data['all_equip_json'] = ''
                
                # 处理神器信息（保存到characters表）
                if parsed_desc and parsed_desc.get('shenqi'):
                    # 使用神器解析器处理神器数据
                    all_shenqi = self.shenqi_parser.process_character_shenqi(parsed_desc, char.get('sellerNickname', ''))
                    if all_shenqi and all_shenqi.get('神器名称'):
                        character_data['all_shenqi_json'] = json.dumps(all_shenqi, ensure_ascii=False)
                        self.logger.debug(f"保存神器信息到characters表: {len(character_data['all_shenqi_json'])} 字符")
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
                        self.logger.debug(f"保存坐骑信息到characters表: {len(character_data['all_rider_json'])} 字符")
                    else:
                        character_data['all_rider_json'] = ''
                else:
                    character_data['all_rider_json'] = ''
                
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
                    self.logger.debug(f"保存锦衣信息到characters表: {len(character_data['ex_avt_json'])} 字符")
                else:
                    character_data['ex_avt_json'] = ''
                
                # 使用智能数据库助手保存角色数据
                try:
                    self.smart_db.save_character(character_data)
                except Exception as e:
                    self.logger.error(f"保存角色数据失败: {char.get('eid')}, 错误: {e}")
                
                # 2. 处理详细装备数据（如果存在）
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
                            'version_code': safe_str(parsed_desc.get('equip_desc_version_code')),
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
                        
                        # 使用智能数据库助手保存详细装备数据
                        self.smart_db.save_large_equip_data(equip_data)
                        
                    except Exception as e:
                        self.logger.error(f"解析装备详细信息时出错: {str(e)}")
                
                # 如果代码执行到这里，说明角色保存成功，增加计数
                saved_count += 1
                
                # 为每个角色单独导出JSON数据到role_json文件夹
                try:
                    # 使用json_exporter中的方法导出
                    self._export_single_character_json(character_data, large_equip_desc, parsed_desc)
                    
                except Exception as e:
                    self.logger.warning(f"保存角色 {character_data.get('equip_id')} 的单独JSON失败: {e}")
                
            except Exception as e:
                self.logger.error(f"保存角色 {char.get('eid')} 时出错: {str(e)}")
                continue
                
        self.logger.info(f"✅ 使用智能数据库助手成功保存{saved_count}条角色数据")
        if saved_count > 0:
            self.logger.info(f"🗂️ 每个角色的单独JSON文件已保存到 {self.output_dir}/role_json/ 文件夹")
        return saved_count
    
    def crawl_all_pages(self, max_pages=10, delay_range=None):
        """爬取所有页面的数据"""
        if delay_range is None:
            delay_range = API_CONFIG['delay_range']
        
        self.logger.info(f"开始爬取数据，最大页数: {max_pages}")
        
        total_characters = 0
        successful_pages = 0
        
        for page in range(1, max_pages + 1):
            self.logger.info(f"正在爬取第 {page} 页...")
            
            # 获取数据
            data = self.fetch_page(page=page)
            
            if data:
                # 保存数据
                saved_count = self.save_character_data(data)
                total_characters += saved_count
                successful_pages += 1
                
                self.logger.info(f"第 {page} 页完成，获取 {len(data)} 条数据，保存 {saved_count} 条")
            else:
                self.logger.warning(f"第 {page} 页无数据")
            
            # 随机延时
            if page < max_pages:
                delay = random.uniform(delay_range[0], delay_range[1])
                self.logger.info(f"等待 {delay:.1f} 秒...")
                time.sleep(delay)
        
        self.logger.info(f"爬取完成！成功页数: {successful_pages}/{max_pages}, 总角色数: {total_characters}")
        return total_characters
    
    def extract_server_id_from_eid(self, eid):
        """从eid中提取服务器ID"""
        try:
            if eid and '-' in eid:
                parts = eid.split('-')
                if len(parts) >= 2:
                    return parts[1]
        except Exception:
            pass
        return None
    
    def generate_cbg_link(self, eid):
        """生成CBG角色分享链接"""
        if not eid:
            return None
        
        server_id = self.extract_server_id_from_eid(eid)
        if not server_id:
            return None
        
        # 构建基础CBG链接
        base_url = "https://xyq.cbg.163.com/equip"
        params = f"s={server_id}&eid={eid}&client_type=web&o"
        link = f"{base_url}?{params}"
        
        return link
    
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
            db_files = [f"{FILE_PATHS['db_filename'].replace('.db', '')}_{month}.db" for month in months]
        
        exported_files = []
        for db_file in db_files:
            db_path = os.path.join(data_dir, db_file)
            if not os.path.exists(db_path):
                self.logger.warning(f"数据库文件不存在: {db_file}")
                continue
                
            # 为每个数据库创建Excel导出器
            excel_exporter = CBGExcelExporter(db_path, self.output_dir, self.logger)
            
            # 使用导出器导出数据
            excel_file = excel_exporter.export_to_excel(
                filename=f"{filename}_{db_file.replace('.db', '')}" if filename else None,
                generate_link_callback=self.generate_cbg_link
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
            db_files = [f"{FILE_PATHS['db_filename'].replace('.db', '')}_{month}.db" for month in months]
        
        exported_files = []
        for db_file in db_files:
            db_path = os.path.join(data_dir, db_file)
            if not os.path.exists(db_path):
                self.logger.warning(f"数据库文件不存在: {db_file}")
                continue
                
            # 为每个数据库创建JSON导出器
            json_exporter = CBGJSONExporter(db_path, self.output_dir, self.logger)
            
            # 使用导出器导出数据
            json_file = json_exporter.export_to_json(
                filename=f"{filename}_{db_file.replace('.db', '')}" if filename else None,
                generate_link_callback=self.generate_cbg_link,
                pretty=pretty
            )
            if json_file:
                exported_files.append(json_file)
            
        return exported_files
    
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
        """转换房屋真实拥有者状态为中文名称"""
        return self.common_parser.get_house_real_owner_name(owner_status)
    
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
                generate_link_callback=self.generate_cbg_link,
                logger=self.logger
            )
            
        except Exception as e:
            self.logger.error(f"导出单个角色JSON失败: {e}")
            return None
    
    def fetch_page(self, page=1):
        """获取单页数据"""
        try:
            # 构建请求参数
            params = {
                'callback': 'Request.JSONP.request_map.request_0',
                '_': str(int(time.time() * 1000)),
                'server_type': 3,
                'act': 'recommd_by_role',
                'page': page,
                'count': 15,
                'search_type': 'overall_search_role',
                'view_loc': 'overall_search'
            }
            
            # 构建完整URL
            url = f"{self.base_url}?{urlencode(params)}"
            self.logger.info(f"请求URL: {url}")
            
            # 更新请求头
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
            self.session.headers.update(headers)
            
            # 发送请求
            response = self.session.get(url, timeout=30)
            
            # 记录API请求
            log_api_request(url, params, response.status_code, response.text[:200], 
                          self.logger, self.smart_db)
            
            # 解析响应
            if response.status_code == 200:
                parsed_result = self.parse_jsonp_response(response.text)
                
                # 如果检测到登录过期
                if parsed_result == LOGIN_EXPIRED_MARKER:
                    if self.retry_attempts > 0:
                        self.retry_attempts -= 1
                        self.logger.info("尝试自动更新Cookie并重试...")
                        
                        # 调用Playwright更新Cookie
                        if update_cookies_with_playwright():
                            self.logger.info("Cookie更新成功，重新加载会话并重试请求。")
                            self.setup_session()  # 重新加载Cookie
                            return self.fetch_page(page) # 重试一次
                        else:
                            self.logger.error("Cookie更新失败。无法继续。")
                            return None
                    else:
                        self.logger.error("已达到重试次数上限，停止重试。")
                        return None
                
                return parsed_result
            else:
                self.logger.error(f"请求失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取第{page}页数据时出错: {e}")
            return None

def main():
    """简单的测试函数 - 主要使用run.py启动"""
    print("CBG爬虫模块")
    print("请使用 'python run.py basic' 启动爬虫")

if __name__ == "__main__":
    main() 