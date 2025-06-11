#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
梦幻西游藏宝阁爬虫配置文件
包含所有映射字典和常量定义

注意：
- 技能相关配置（生活技能、师门技能、剧情技能）现在完全从 game_auto_config.js 读取
- 神器、坐骑配置现在完全从 game_auto_config.js 读取
- 门派、庭院、牧场配置现在完全从 game_auto_config.js 读取
- 本文件保留其他基础配置（种族、飞升、房屋等级等）
"""

# 种族门派分类（根据门派判断种族）
HUMAN_SCHOOLS = [1, 2, 3, 4, 13, 17]      # 人族门派
DEMON_SCHOOLS = [9, 10, 11, 12, 15, 16]   # 魔族门派
IMMORTAL_SCHOOLS = [5, 6, 7, 8, 14, 18]   # 仙族门派

# 飞升状态配置
CHINESE_NUM_CONFIG = {
    1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
    6: "六", 7: "七", 8: "八", 9: "九", 10: "十"
}

ROLE_ZHUAN_ZHI_CONFIG = {
    0: "未飞升",
    1: "飞升",
    2: "渡劫"
}

# API相关配置
API_CONFIG = {
    'base_url': 'https://xyq.cbg.163.com/cgi-bin/recommend.py',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'referer': 'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py',
    'delay_range': [1, 3]  # 请求间隔时间范围（秒）
}

# 请求头配置
REQUEST_HEADERS = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Sec-Ch-Ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'script',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-origin'
}

# 数据库字段配置
DB_SCHEMA_CONFIG = {
    'characters': '''
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equip_id TEXT UNIQUE,           -- 装备ID，作为唯一标识
            server_name TEXT,               -- 服务器名称
            seller_nickname TEXT,           -- 卖家昵称
            level INTEGER,                  -- 等级
            price REAL,                     -- 价格
            price_desc TEXT,                -- 价格描述
            school TEXT,                    -- 门派
            area_name TEXT,                 -- 区域名称
            icon_index INTEGER,             -- 图标索引
            kindid INTEGER,                 -- 种类ID
         
            game_ordersn TEXT,              -- 游戏订单号
            pass_fair_show INTEGER DEFAULT 0,  -- 是否通过公示
            fair_show_end_time TEXT,        -- 公示结束时间
            accept_bargain INTEGER DEFAULT 0,  -- 接受还价
            status_desc TEXT,                  -- 角色售卖状态
            onsale_expire_time_desc TEXT,   -- 出售剩余时间
            expire_time TEXT,                -- 角色到期时间
            -- 角色基本信息
            race TEXT,                      -- 种族
            fly_status TEXT,                -- 飞升状态
            collect_num INTEGER DEFAULT 0,  -- 收藏数
            
            -- 技能信息
            life_skills TEXT DEFAULT '',        -- 生活技能
            school_skills TEXT DEFAULT '',      -- 师门技能
            ju_qing_skills TEXT DEFAULT '',     -- 剧情技能
            
            all_pets_json TEXT DEFAULT '',      -- 所有宝宝信息（JSON格式）
            all_equip_json TEXT DEFAULT '',    -- 所有装备信息（JSON格式）
            all_shenqi_json TEXT DEFAULT '',    -- 所有神器信息（JSON格式）
            all_rider_json TEXT DEFAULT '',     -- 所有坐骑信息（JSON格式）
            ex_avt_json TEXT DEFAULT '',        -- 所有锦衣信息（JSON格式）
            
            -- 元数据
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    
    'api_logs': '''
        CREATE TABLE IF NOT EXISTS api_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,                       -- 请求URL
            params TEXT,                    -- 请求参数JSON
            status_code INTEGER,            -- 响应状态码
            response_preview TEXT,          -- 响应预览
            request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 请求时间
        )
    ''',
    
    'large_equip_desc_data': '''
        CREATE TABLE IF NOT EXISTS large_equip_desc_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equip_id TEXT UNIQUE,           -- 关联到characters表的equip_id
            
            -- 基础信息
            character_name TEXT,            -- 角色名(cName)
            character_level INTEGER,        -- 等级(iGrade)
            character_school INTEGER,       -- 门派(iSchool)
            character_icon INTEGER,         -- 图标ID(iIcon)
            user_num TEXT,                  -- 用户ID(usernum)
            
            -- 属性信息
            hp_max INTEGER,                 -- 气血(iHp_Max)
            mp_max INTEGER,                 -- 魔法(iMp_Max)
            att_all INTEGER,                -- 命中(iAtt_All)
            def_all INTEGER,                -- 防御(iDef_All)
            spe_all INTEGER,                -- 敏捷(iSpe_All)
            mag_all INTEGER,                -- 魔力(iMag_All)
            damage_all INTEGER,             -- 伤害(iDamage_All)
            mag_dam_all INTEGER,            -- 法术伤害(iTotalMagDam_all)
            mag_def_all INTEGER,            -- 法术防御(iTotalMagDef_all)
            dod_all INTEGER,                -- 躲避(iDod_All)
            cor_all INTEGER,                -- 体质(iCor_All)
            str_all INTEGER,                -- 力量(iStr_All)
            res_all INTEGER,                -- 耐力(iRes_All)
            dex_all INTEGER,                -- 速度(iDex_All)
            
            -- 经验和修炼
            up_exp INTEGER,                 -- 获得经验(iUpExp)
            sum_exp INTEGER,                -- 总经验(sum_exp)
            expt_ski1 INTEGER,              -- 攻击修炼(iExptSki1)
            expt_ski2 INTEGER,              -- 防御修炼(iExptSki2)
            expt_ski3 INTEGER,              -- 法术修炼(iExptSki3)
            expt_ski4 INTEGER,              -- 抗法修炼(iExptSki4)
            expt_ski5 INTEGER,              -- 猎术修炼(iExptSki5)
            max_expt1 INTEGER,              -- 攻击修炼上限(iMaxExpt1)
            max_expt2 INTEGER,              -- 防御修炼上限(iMaxExpt2)
            max_expt3 INTEGER,              -- 法术修炼上限(iMaxExpt3)
            max_expt4 INTEGER,              -- 抗法修炼上限(iMaxExpt4)
            
            -- 宠物控制技能
            beast_ski1 INTEGER,             -- 攻击控制力(iBeastSki1)
            beast_ski2 INTEGER,             -- 防御控制力(iBeastSki2)
            beast_ski3 INTEGER,             -- 法术控制力(iBeastSki3)
            beast_ski4 INTEGER,             -- 抗法控制力(iBeastSki4)
            
            -- 技能点和属性点
            skill_point INTEGER,            -- 剧情技能剩余点(iSkiPoint)
            attribute_point INTEGER,        -- 属性点(iPoint)
            potential INTEGER,              -- 潜力值(potential)
            max_potential INTEGER,          -- 最大潜力值(max_potential)
            
            -- 金钱相关
            cash INTEGER,                   -- 现金(iCash)
            saving INTEGER,                 -- 存款(iSaving)
            learn_cash INTEGER,             -- 储备金(iLearnCash)
            
            -- 转职飞升相关
            zhuan_zhi INTEGER,              -- 转职状态(iZhuanZhi)
            all_new_point INTEGER,          -- 乾元丹(TA_iAllNewPoint)
            three_fly_lv INTEGER,           -- 化圣等级(i3FlyLv)
            nine_fight_level INTEGER,       -- 生死劫等级(nine_fight_level)
            
            -- 善恶值
            goodness INTEGER,               -- 善恶值(iGoodness)
            badness INTEGER,                -- 罪恶值(iBadness)
            goodness_sav INTEGER,           -- 善恶储存(igoodness_sav)
            
            -- 称谓和帮派
            character_title TEXT,           -- 称谓(title)
            org_name TEXT,                  -- 帮派名称(cOrg)
            org_offer INTEGER,              -- 帮贡(iOrgOffer)
            org_position TEXT,              -- 帮派职位(org_position)
            
            -- 婚姻和结义
            marry_id TEXT,                  -- 结婚对象(iMarry)
            marry2_id TEXT,                 -- 结义对象(iMarry2)
            marry_name TEXT,                -- 结婚对象名称(marry_name)
            
            -- 社区信息
            community_name TEXT,            -- 社区名称(commu_name)
            community_gid TEXT,             -- 社区ID(commu_gid)
            
            -- 成就和评分
            achievement_total INTEGER,      -- 成就点(AchPointTotal)
            hero_score INTEGER,             -- 英雄评分(HeroScore)
            datang_feat INTEGER,            -- 三界功绩(datang_feat)
            sword_score INTEGER,            -- 剑会评分(sword_score)
            dup_score INTEGER,              -- 副本评分(dup_score)
            shenqi_score INTEGER,           -- 神器评分(shenqi_score)
            qicai_score INTEGER,            -- 奇才评分(qicai_score)
            xianyu_score INTEGER,           -- 仙玉积分(xianyu_score)
            
            -- 道具相关
            nuts_num INTEGER,               -- 潜能果数量(iNutsNum)
            cg_total_amount INTEGER,        -- 彩果总数(iCGTotalAmount)
            cg_body_amount INTEGER,         -- 身上彩果(iCGBodyAmount)
            cg_box_amount INTEGER,          -- 仓库彩果(iCGBoxAmount)
            xianyu_amount INTEGER,          -- 仙玉(xianyu)
            energy_amount INTEGER,          -- 精力(energy)
            jiyuan_amount INTEGER,          -- 机缘(jiyuan)
            add_point INTEGER,              -- 加点(addPoint)
            
            -- 背包信息
            packet_page INTEGER,            -- 背包页数(iPcktPage)
            
            -- 房屋相关
            rent_level INTEGER,             -- 房屋等级(rent_level)
            outdoor_level INTEGER,          -- 庭院等级(outdoor_level)
            farm_level INTEGER,             -- 牧场等级(farm_level)
            house_real_owner INTEGER,       -- 房屋真实拥有者(house_real_owner)
            
            -- 其他信息
            pride INTEGER,                  -- 人气(iPride)
            bid_status INTEGER,             -- 靓号状态(bid)
            ori_race INTEGER,               -- 原始种族(ori_race)
            current_race INTEGER,           -- 当前种族(iRace)
            version_code TEXT,              -- 版本码(equip_desc_version_code)
            
            -- JSON数据字段
            all_skills_json TEXT,           -- 所有技能JSON(all_skills)
            all_equip_json TEXT,            -- 所有装备JSON(AllEquip)
            all_summon_json TEXT,           -- 所有召唤兽JSON(AllSummon)
            child_json TEXT,                -- 孩子信息JSON(child)
            child2_json TEXT,               -- 孩子2信息JSON(child2)
            all_rider_json TEXT,            -- 所有坐骑JSON(AllRider)
            ex_avt_json TEXT,               -- 时装JSON(ExAvt)
            huge_horse_json TEXT,           -- 祥瑞JSON(HugeHorse)
            fabao_json TEXT,                -- 法宝JSON(fabao)
            lingbao_json TEXT,              -- 灵宝JSON(lingbao)
            shenqi_json TEXT,               -- 神器JSON(shenqi)
            idbid_desc_json TEXT,           -- 靓号描述JSON(idbid_desc)
            changesch_json TEXT,            -- 转门派历史JSON(changesch)
            prop_kept_json TEXT,            -- 保持属性JSON(propKept)
            more_attr_json TEXT,            -- 更多属性JSON(more_attr)
            raw_data_json TEXT,             -- 原始数据JSON
            
            -- 时间字段
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 更新时间
            
            FOREIGN KEY (equip_id) REFERENCES characters (equip_id)
        )
    '''
}

# 文件路径配置
FILE_PATHS = {
    'cookies_path': 'config/cookies.txt',
    'proxy_list_path': 'config/proxy_list.txt',
    'db_filename': 'cbg_data.db',  # 固定的数据库文件名
    'log_filename': 'cbg_spider.log'
}

# 表创建顺序（处理外键依赖关系）
DB_TABLE_ORDER = ['characters', 'api_logs', 'large_equip_desc_data']

# 数据库表结构配置 - 别名引用
DB_TABLE_SCHEMAS = DB_SCHEMA_CONFIG 