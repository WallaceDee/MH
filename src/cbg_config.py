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
            yushoushu_skill INTEGER DEFAULT 0,  -- 育兽术技能
            
            all_pets_json TEXT DEFAULT '',      -- 所有宝宝信息（JSON格式）
            all_equip_json TEXT DEFAULT '',    -- 所有装备信息（JSON格式）
            all_shenqi_json TEXT DEFAULT '',    -- 所有神器信息（JSON格式）
            all_rider_json TEXT DEFAULT '',     -- 所有坐骑信息（JSON格式）
            ex_avt_json TEXT DEFAULT '',        -- 所有锦衣信息（JSON格式）
            all_fabao_json TEXT DEFAULT '',    -- 所有法宝信息（JSON格式）
            
            -- 元数据
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    
    'empty_characters': '''
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
            yushoushu_skill INTEGER DEFAULT 0,  -- 育兽术技能
            
            all_pets_json TEXT DEFAULT '',      -- 所有宝宝信息（JSON格式）
            all_equip_json TEXT DEFAULT '',    -- 所有装备信息（JSON格式）
            all_shenqi_json TEXT DEFAULT '',    -- 所有神器信息（JSON格式）
            all_rider_json TEXT DEFAULT '',     -- 所有坐骑信息（JSON格式）
            ex_avt_json TEXT DEFAULT '',        -- 所有锦衣信息（JSON格式）
            all_fabao_json TEXT DEFAULT '',    -- 所有法宝信息（JSON格式）
            
            -- 空号识别信息（空号数据库专用字段）
            empty_reason TEXT DEFAULT '',       -- 空号识别原因
            equip_count INTEGER DEFAULT 0,      -- 物品总数
            high_level_pet_count INTEGER DEFAULT 0,  -- 高等级宠物数量
            
            -- 元数据
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    
    'pets': '''
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eid TEXT UNIQUE,                    -- 宠物唯一标识符
            equipid INTEGER,                    -- 宠物ID
            equip_sn TEXT,                      -- 宠物序列号
            
            -- 服务器和卖家信息
            server_name TEXT,                   -- 服务器名称
            serverid INTEGER,                   -- 服务器ID
            equip_server_sn TEXT,               -- 宠物服务器序列号
            seller_nickname TEXT,               -- 卖家昵称
            seller_roleid TEXT,                 -- 卖家角色ID
            area_name TEXT,                     -- 区域名称
            
            -- 宠物基本信息
            equip_name TEXT,                    -- 宠物名称
            equip_type TEXT,                    -- 宠物类型
            equip_type_name TEXT,               -- 宠物类型名称
            equip_type_desc TEXT,               -- 宠物类型描述
            level INTEGER,                      -- 宠物等级
            equip_level INTEGER,                -- 宠物等级
            equip_level_desc TEXT,              -- 宠物等级描述
            level_desc TEXT,                    -- 等级描述
            subtitle TEXT,                      -- 副标题
            equip_pos INTEGER,                  -- 宠物位置
            position INTEGER,                   -- 位置
            school INTEGER,                     -- 门派限制
            role_grade_limit INTEGER,           -- 角色等级限制
            min_buyer_level INTEGER,            -- 最低购买者等级
            equip_count INTEGER,                -- 宠物数量
            
            -- 价格和交易信息
            price REAL,                         -- 价格
            price_desc TEXT,                    -- 价格描述
            unit_price_desc TEXT,               -- 单价描述
            min_unit_price REAL,                -- 最低单价
            price_explanation TEXT,             -- 价格说明（JSON格式）
            accept_bargain INTEGER DEFAULT 0,   -- 接受还价
            bargain_info TEXT,                  -- 还价信息（JSON格式）
            
            -- 状态和时间信息
            equip_status INTEGER,               -- 宠物状态
            equip_status_desc TEXT,             -- 宠物状态描述
            status_desc TEXT,                   -- 状态描述
            onsale_expire_time_desc TEXT,       -- 在售过期时间描述
            time_left TEXT,                     -- 剩余时间
            expire_time TEXT,                   -- 过期时间
            create_time_equip TEXT,             -- 宠物创建时间
            selling_time TEXT,                  -- 销售时间
            selling_time_ago_desc TEXT,         -- 销售时间前描述
            first_onsale_time TEXT,             -- 首次上架时间
            
            -- 公示相关
            pass_fair_show INTEGER DEFAULT 0,   -- 是否通过公示
            fair_show_time INTEGER DEFAULT 0,   -- 公示时间
            fair_show_end_time TEXT,            -- 公示结束时间
            fair_show_end_time_left TEXT,       -- 公示结束剩余时间
            fair_show_poundage INTEGER DEFAULT 0, -- 公示手续费
            
            -- 宠物属性
            hp INTEGER DEFAULT 0,               -- 气血
            qixue INTEGER DEFAULT 0,            -- 气血（别名）
            init_hp INTEGER DEFAULT 0,          -- 初始气血
            mofa INTEGER DEFAULT 0,             -- 魔法
            init_wakan INTEGER DEFAULT 0,       -- 初始魔力
            mingzhong INTEGER DEFAULT 0,        -- 命中
            fangyu INTEGER DEFAULT 0,           -- 防御
            init_defense INTEGER DEFAULT 0,     -- 初始防御
            defense INTEGER DEFAULT 0,          -- 防御（别名）
            speed INTEGER DEFAULT 0,            -- 速度
            minjie INTEGER DEFAULT 0,           -- 敏捷
            init_dex INTEGER DEFAULT 0,         -- 初始敏捷
            shanghai INTEGER DEFAULT 0,         -- 伤害
            damage INTEGER DEFAULT 0,           -- 伤害（别名）
            init_damage INTEGER DEFAULT 0,      -- 初始伤害
            init_damage_raw INTEGER DEFAULT 0,  -- 原始初始伤害
            all_damage INTEGER DEFAULT 0,       -- 全部伤害
            magic_damage INTEGER DEFAULT 0,     -- 法术伤害
            magic_defense INTEGER DEFAULT 0,    -- 法术防御
            lingli INTEGER DEFAULT 0,           -- 灵力
            fengyin INTEGER DEFAULT 0,          -- 封印
            anti_fengyin INTEGER DEFAULT 0,     -- 抗封印
            zongshang INTEGER DEFAULT 0,        -- 总伤
            
            -- 修炼相关
            expt_gongji INTEGER DEFAULT 0,      -- 攻击修炼
            expt_fangyu INTEGER DEFAULT 0,      -- 防御修炼
            expt_fashu INTEGER DEFAULT 0,       -- 法术修炼
            expt_kangfa INTEGER DEFAULT 0,      -- 抗法修炼
            max_expt_gongji INTEGER DEFAULT 0,  -- 最大攻击修炼
            max_expt_fangyu INTEGER DEFAULT 0,  -- 最大防御修炼
            max_expt_fashu INTEGER DEFAULT 0,   -- 最大法术修炼
            max_expt_kangfa INTEGER DEFAULT 0,  -- 最大抗法修炼
            sum_exp INTEGER DEFAULT 0,          -- 总经验
            
            -- 宝宝修炼
            bb_expt_gongji INTEGER DEFAULT 0,   -- 宝宝攻击修炼
            bb_expt_fangyu INTEGER DEFAULT 0,   -- 宝宝防御修炼
            bb_expt_fashu INTEGER DEFAULT 0,    -- 宝宝法术修炼
            bb_expt_kangfa INTEGER DEFAULT 0,   -- 宝宝抗法修炼
            
            -- 附加属性
            addon_tizhi INTEGER DEFAULT 0,      -- 附加体质
            addon_liliang INTEGER DEFAULT 0,    -- 附加力量
            addon_naili INTEGER DEFAULT 0,      -- 附加耐力
            addon_minjie INTEGER DEFAULT 0,     -- 附加敏捷
            addon_fali INTEGER DEFAULT 0,       -- 附加法力
            addon_lingli INTEGER DEFAULT 0,     -- 附加灵力
            addon_total INTEGER DEFAULT 0,      -- 附加总和
            addon_status INTEGER DEFAULT 0,     -- 附加状态
            addon_skill_chance INTEGER DEFAULT 0, -- 附加技能几率
            addon_effect_chance INTEGER DEFAULT 0, -- 附加效果几率
            
            -- 宝石相关
            gem_level INTEGER DEFAULT 0,        -- 宝石等级
            xiang_qian_level INTEGER DEFAULT 0, -- 镶嵌等级
            gem_value INTEGER DEFAULT 0,        -- 宝石值
            
            -- 强化相关
            jinglian_level INTEGER DEFAULT 0,   -- 精炼等级
            
            -- 特技和套装
            special_skill INTEGER DEFAULT 0,    -- 特技
            special_effect TEXT DEFAULT 0,      -- 特效
            suit_skill INTEGER DEFAULT 0,       -- 套装技能
            suit_effect INTEGER DEFAULT 0,      -- 套装效果
            
            -- 其他信息
            collect_num INTEGER DEFAULT 0,      -- 收藏数
            has_collect INTEGER DEFAULT 0,      -- 是否收藏
            score INTEGER DEFAULT 0,            -- 评分
            icon_index INTEGER DEFAULT 0,       -- 图标索引
            icon INTEGER DEFAULT 0,             -- 图标
            equip_face_img TEXT,                -- 宠物头像图片
            kindid INTEGER,                     -- 种类ID
            game_channel TEXT,                  -- 游戏渠道
            
            -- 订单相关
            game_ordersn TEXT,                  -- 游戏订单号
            whole_game_ordersn TEXT,            -- 完整游戏订单号
            
            -- 跨服相关
            allow_cross_buy INTEGER DEFAULT 0,  -- 允许跨服购买
            cross_server_poundage INTEGER DEFAULT 0,      -- 跨服手续费
            cross_server_poundage_origin INTEGER DEFAULT 0, -- 原始跨服手续费
            cross_server_poundage_discount REAL DEFAULT 0, -- 跨服手续费折扣
            cross_server_poundage_discount_label TEXT,    -- 跨服手续费折扣标签
            cross_server_poundage_display_mode INTEGER DEFAULT 0, -- 跨服手续费显示模式
            cross_server_activity_conf_discount REAL DEFAULT 0,  -- 跨服活动配置折扣
            
            -- 活动相关
            activity_type INTEGER DEFAULT 0,    -- 活动类型
            joined_seller_activity INTEGER DEFAULT 0, -- 参与卖家活动
            
            -- 拆分相关
            is_split_sale INTEGER DEFAULT 0,    -- 是否拆分销售
            is_split_main_role INTEGER DEFAULT 0, -- 是否拆分主角
            is_split_independent_role INTEGER DEFAULT 0, -- 是否独立角色拆分
            is_split_independent_equip INTEGER DEFAULT 0, -- 是否独立宠物拆分
            split_equip_sold_happen INTEGER DEFAULT 0,   -- 拆分宠物销售发生
            show_split_equip_sold_remind INTEGER DEFAULT 0, -- 显示拆分宠物销售提醒
            
            -- 保护相关
            is_onsale_protection_period INTEGER DEFAULT 0, -- 是否在售保护期
            onsale_protection_end_time TEXT,    -- 在售保护结束时间
            is_vip_protection INTEGER DEFAULT 0, -- 是否VIP保护
            is_time_lock INTEGER DEFAULT 0,     -- 是否时间锁定
            
            -- 测试服相关
            equip_in_test_server INTEGER DEFAULT 0,        -- 宠物在测试服
            buyer_in_test_server INTEGER DEFAULT 0,        -- 买家在测试服
            equip_in_allow_take_away_server INTEGER DEFAULT 0, -- 宠物在允许带走服务器
            
            -- 其他标识
            is_weijianding INTEGER DEFAULT 0,   -- 是否未鉴定
            is_show_alipay_privilege INTEGER DEFAULT 0,    -- 是否显示支付宝特权
            is_seller_redpacket_flag INTEGER DEFAULT 0,    -- 是否卖家红包标志
            is_show_expert_desc INTEGER DEFAULT 0,         -- 是否显示专家描述
            is_show_special_highlight INTEGER DEFAULT 0,   -- 是否显示特殊高亮
            is_xyq_game_role_kunpeng_reach_limit INTEGER DEFAULT 0, -- 是否达到鲲鹏限制
            
            -- 版本和存储相关
            equip_onsale_version INTEGER DEFAULT 0, -- 宠物上架版本
            storage_type INTEGER DEFAULT 0,         -- 存储类型
            agent_trans_time INTEGER DEFAULT 0,     -- 代理传输时间
            
            -- KOL相关
            kol_article_id TEXT,                -- KOL文章ID
            kol_share_id TEXT,                  -- KOL分享ID
            kol_share_time TEXT,                -- KOL分享时间
            kol_share_status TEXT,              -- KOL分享状态
            
            -- 推荐相关
            reco_request_id TEXT,               -- 推荐请求ID
            appointed_roleid TEXT,              -- 指定角色ID
            
            -- 团队相关
            play_team_cnt INTEGER DEFAULT 0,    -- 游戏团队数量
            
            -- 随机抽奖相关
            random_draw_finish_time TEXT,       -- 随机抽奖完成时间
            
            -- 详细描述
            desc TEXT,                          -- 描述
            large_equip_desc TEXT,              -- 大宠物描述
            desc_sumup TEXT,                    -- 描述总结
            desc_sumup_short TEXT,              -- 描述总结简短
            diy_desc TEXT,                      -- 自定义描述
            rec_desc TEXT,                      -- 推荐描述
            diy_desc_pay_info TEXT,             -- 自定义描述支付信息（JSON格式）
            
            -- 其他复杂数据（JSON格式）
            other_info TEXT,                    -- 其他信息
            video_info TEXT,                    -- 视频信息（JSON格式）
            agg_added_attrs TEXT,               -- 聚合附加属性（JSON格式）
            dynamic_tags TEXT,                  -- 动态标签（JSON格式）
            highlight TEXT,                     -- 高亮信息（JSON格式）
            tag_key TEXT,                       -- 标签键（JSON格式）
            tag TEXT,                           -- 标签
            
            -- 搜索相关
            search_type TEXT,                   -- 搜索类型
            
            -- 元数据
            raw_data_json TEXT,                 -- 原始数据（JSON格式）
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    
    'equipments': '''
        CREATE TABLE IF NOT EXISTS equipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eid TEXT UNIQUE,                    -- 装备唯一标识符
            equipid INTEGER,                    -- 装备ID
            equip_sn TEXT,                      -- 装备序列号
            
            -- 服务器和卖家信息
            server_name TEXT,                   -- 服务器名称
            serverid INTEGER,                   -- 服务器ID
            equip_server_sn TEXT,               -- 装备服务器序列号
            seller_nickname TEXT,               -- 卖家昵称
            seller_roleid TEXT,                 -- 卖家角色ID
            area_name TEXT,                     -- 区域名称
            
            -- 装备基本信息
            equip_name TEXT,                    -- 装备名称
            equip_type TEXT,                    -- 装备类型
            equip_type_name TEXT,               -- 装备类型名称
            equip_type_desc TEXT,               -- 装备类型描述
            level INTEGER,                      -- 装备等级
            equip_level INTEGER,                -- 装备等级
            equip_level_desc TEXT,              -- 装备等级描述
            level_desc TEXT,                    -- 等级描述
            subtitle TEXT,                      -- 副标题
            equip_pos INTEGER,                  -- 装备位置
            position INTEGER,                   -- 位置
            school INTEGER,                     -- 门派限制
            role_grade_limit INTEGER,           -- 角色等级限制
            min_buyer_level INTEGER,            -- 最低购买者等级
            equip_count INTEGER,                -- 装备数量
            
            -- 价格和交易信息
            price REAL,                         -- 价格
            price_desc TEXT,                    -- 价格描述
            unit_price_desc TEXT,               -- 单价描述
            min_unit_price REAL,                -- 最低单价
            price_explanation TEXT,             -- 价格说明（JSON格式）
            accept_bargain INTEGER DEFAULT 0,   -- 接受还价
            bargain_info TEXT,                  -- 还价信息（JSON格式）
            
            -- 状态和时间信息
            equip_status INTEGER,               -- 装备状态
            equip_status_desc TEXT,             -- 装备状态描述
            status_desc TEXT,                   -- 状态描述
            onsale_expire_time_desc TEXT,       -- 在售过期时间描述
            time_left TEXT,                     -- 剩余时间
            expire_time TEXT,                   -- 过期时间
            create_time_equip TEXT,             -- 装备创建时间
            selling_time TEXT,                  -- 销售时间
            selling_time_ago_desc TEXT,         -- 销售时间前描述
            first_onsale_time TEXT,             -- 首次上架时间
            
            -- 公示相关
            pass_fair_show INTEGER DEFAULT 0,   -- 是否通过公示
            fair_show_time INTEGER DEFAULT 0,   -- 公示时间
            fair_show_end_time TEXT,            -- 公示结束时间
            fair_show_end_time_left TEXT,       -- 公示结束剩余时间
            fair_show_poundage INTEGER DEFAULT 0, -- 公示手续费
            
            -- 装备属性
            hp INTEGER DEFAULT 0,               -- 气血
            qixue INTEGER DEFAULT 0,            -- 气血（别名）
            init_hp INTEGER DEFAULT 0,          -- 初始气血
            mofa INTEGER DEFAULT 0,             -- 魔法
            init_wakan INTEGER DEFAULT 0,       -- 初始魔力
            mingzhong INTEGER DEFAULT 0,        -- 命中
            fangyu INTEGER DEFAULT 0,           -- 防御
            init_defense INTEGER DEFAULT 0,     -- 初始防御
            defense INTEGER DEFAULT 0,          -- 防御（别名）
            speed INTEGER DEFAULT 0,            -- 速度
            minjie INTEGER DEFAULT 0,           -- 敏捷
            init_dex INTEGER DEFAULT 0,         -- 初始敏捷
            shanghai INTEGER DEFAULT 0,         -- 伤害
            damage INTEGER DEFAULT 0,           -- 伤害（别名）
            init_damage INTEGER DEFAULT 0,      -- 初始伤害
            init_damage_raw INTEGER DEFAULT 0,  -- 原始初始伤害
            all_damage INTEGER DEFAULT 0,       -- 总伤害
            magic_damage INTEGER DEFAULT 0,     -- 法术伤害
            magic_defense INTEGER DEFAULT 0,    -- 法术防御
            lingli INTEGER DEFAULT 0,           -- 灵力
            fengyin INTEGER DEFAULT 0,          -- 封印
            anti_fengyin INTEGER DEFAULT 0,     -- 抗封印
            zongshang INTEGER DEFAULT 0,        -- 总伤
            
            -- 修炼相关
            expt_gongji INTEGER DEFAULT 0,      -- 攻击修炼
            expt_fangyu INTEGER DEFAULT 0,      -- 防御修炼
            expt_fashu INTEGER DEFAULT 0,       -- 法术修炼
            expt_kangfa INTEGER DEFAULT 0,      -- 抗法修炼
            max_expt_gongji INTEGER DEFAULT 0,  -- 最大攻击修炼
            max_expt_fangyu INTEGER DEFAULT 0,  -- 最大防御修炼
            max_expt_fashu INTEGER DEFAULT 0,   -- 最大法术修炼
            max_expt_kangfa INTEGER DEFAULT 0,  -- 最大抗法修炼
            sum_exp INTEGER DEFAULT 0,          -- 总经验
            
            -- 宝宝修炼相关
            bb_expt_gongji INTEGER DEFAULT 0,   -- 宝宝攻击修炼
            bb_expt_fangyu INTEGER DEFAULT 0,   -- 宝宝防御修炼
            bb_expt_fashu INTEGER DEFAULT 0,    -- 宝宝法术修炼
            bb_expt_kangfa INTEGER DEFAULT 0,   -- 宝宝抗法修炼
            
            -- 附加属性
            addon_tizhi INTEGER DEFAULT 0,      -- 附加体质
            addon_liliang INTEGER DEFAULT 0,    -- 附加力量
            addon_naili INTEGER DEFAULT 0,      -- 附加耐力
            addon_minjie INTEGER DEFAULT 0,     -- 附加敏捷
            addon_fali INTEGER DEFAULT 0,       -- 附加法力
            addon_lingli INTEGER DEFAULT 0,     -- 附加灵力
            addon_total INTEGER DEFAULT 0,      -- 附加总和
            addon_status TEXT,                 -- 附加状态（套装信息）
            addon_skill_chance INTEGER DEFAULT 0, -- 附加技能几率
            addon_effect_chance INTEGER DEFAULT 0, -- 附加效果几率
            
            -- 宝石相关
            gem_level INTEGER DEFAULT 0,        -- 宝石等级
            gem_value TEXT,                     -- 宝石数值（JSON格式）
            xiang_qian_level INTEGER DEFAULT 0, -- 镶嵌等级
            
            -- 强化相关
            jinglian_level INTEGER DEFAULT 0,   -- 精炼等级
            
            -- 特技和套装
            special_skill INTEGER DEFAULT 0,    -- 特技
            special_effect TEXT,                -- 特效（JSON格式）
            suit_skill INTEGER DEFAULT 0,       -- 套装技能
            suit_effect INTEGER DEFAULT 0,      -- 套装效果
            
            -- 其他信息
            collect_num INTEGER DEFAULT 0,      -- 收藏数
            has_collect INTEGER DEFAULT 0,      -- 是否已收藏
            score INTEGER DEFAULT 0,            -- 评分
            icon_index INTEGER,                 -- 图标索引
            icon TEXT,                          -- 图标
            equip_face_img TEXT,                -- 装备头像图片
            kindid INTEGER,                     -- 种类ID
            game_channel TEXT,                  -- 游戏渠道
            
            -- 订单相关
            game_ordersn TEXT,                  -- 游戏订单号
            whole_game_ordersn TEXT,            -- 完整游戏订单号
            
            -- 跨服相关
            allow_cross_buy INTEGER DEFAULT 0,  -- 允许跨服购买
            cross_server_poundage INTEGER DEFAULT 0, -- 跨服手续费
            cross_server_poundage_origin INTEGER DEFAULT 0, -- 原始跨服手续费
            cross_server_poundage_discount INTEGER DEFAULT 0, -- 跨服手续费折扣
            cross_server_poundage_discount_label TEXT, -- 跨服手续费折扣标签
            cross_server_poundage_display_mode INTEGER DEFAULT 0, -- 跨服手续费显示模式
            cross_server_activity_conf_discount REAL DEFAULT 0, -- 跨服活动配置折扣
            
            -- 活动相关
            activity_type TEXT,                 -- 活动类型
            joined_seller_activity INTEGER DEFAULT 0, -- 参与卖家活动
            
            -- 拆分相关
            is_split_sale INTEGER DEFAULT 0,    -- 是否拆分销售
            is_split_main_role INTEGER DEFAULT 0, -- 是否拆分主角色
            is_split_independent_role INTEGER DEFAULT 0, -- 是否拆分独立角色
            is_split_independent_equip INTEGER DEFAULT 0, -- 是否拆分独立装备
            split_equip_sold_happen INTEGER DEFAULT 0, -- 拆分装备售出发生
            show_split_equip_sold_remind INTEGER DEFAULT 0, -- 显示拆分装备售出提醒
            
            -- 保护相关
            is_onsale_protection_period INTEGER DEFAULT 0, -- 是否在售保护期
            onsale_protection_end_time TEXT,    -- 在售保护结束时间
            is_vip_protection INTEGER DEFAULT 0, -- 是否VIP保护
            is_time_lock INTEGER DEFAULT 0,     -- 是否时间锁定
            
            -- 测试服相关
            equip_in_test_server INTEGER DEFAULT 0, -- 装备在测试服
            buyer_in_test_server INTEGER DEFAULT 0, -- 购买者在测试服
            equip_in_allow_take_away_server INTEGER DEFAULT 0, -- 装备在允许带走服务器
            
            -- 其他标识
            is_weijianding INTEGER DEFAULT 0,   -- 是否未鉴定
            is_show_alipay_privilege INTEGER DEFAULT 0, -- 是否显示支付宝特权
            is_seller_redpacket_flag INTEGER DEFAULT 0, -- 卖家红包标志
            is_show_expert_desc INTEGER DEFAULT -1, -- 是否显示专家描述
            is_show_special_highlight INTEGER DEFAULT 0, -- 是否显示特殊高亮
            is_xyq_game_role_kunpeng_reach_limit INTEGER DEFAULT 0, -- 是否鲲鹏达到限制
            
            -- 版本和存储相关
            equip_onsale_version INTEGER DEFAULT 0, -- 装备在售版本
            storage_type INTEGER DEFAULT 0,     -- 存储类型
            agent_trans_time INTEGER DEFAULT 0, -- 代理传输时间
            
            -- KOL相关
            kol_article_id TEXT,                -- KOL文章ID
            kol_share_id TEXT,                  -- KOL分享ID
            kol_share_time TEXT,                -- KOL分享时间
            kol_share_status TEXT,              -- KOL分享状态
            
            -- 推荐相关
            reco_request_id TEXT,               -- 推荐请求ID
            appointed_roleid TEXT,              -- 指定角色ID
            
            -- 团队相关
            play_team_cnt INTEGER DEFAULT 0,    -- 游戏团队数量
            
            -- 随机抽奖相关
            random_draw_finish_time TEXT,       -- 随机抽奖完成时间
            
            -- 详细描述
            desc TEXT,                          -- 描述
            large_equip_desc TEXT,              -- 大装备描述
            desc_sumup TEXT,                    -- 描述总结
            desc_sumup_short TEXT,              -- 描述总结简短
            diy_desc TEXT,                      -- 自定义描述
            rec_desc TEXT,                      -- 推荐描述
            diy_desc_pay_info TEXT,             -- 自定义描述支付信息（JSON格式）
            
            -- 其他复杂数据（JSON格式）
            other_info TEXT,                    -- 其他信息
            video_info TEXT,                    -- 视频信息（JSON格式）
            agg_added_attrs TEXT,               -- 聚合附加属性（JSON格式）
            dynamic_tags TEXT,                  -- 动态标签（JSON格式）
            highlight TEXT,                     -- 高亮信息（JSON格式）
            tag_key TEXT,                       -- 标签键（JSON格式）
            tag TEXT,                           -- 标签
            
            -- 搜索相关
            search_type TEXT,                   -- 搜索类型
            
            -- 元数据
            raw_data_json TEXT,                 -- 原始数据（JSON格式）
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            sum_amount INTEGER,             -- 最大召唤兽携带数量(iSumAmount)
            version_code TEXT,              -- 版本码(equip_desc_version_code)
            
            -- JSON数据字段
            pet TEXT,                       -- 特殊宠物JSON(pet)
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


# 数据库表创建顺序（处理外键依赖关系）
DB_TABLE_ORDER = ['characters', 'pets', 'equipments', 'large_equip_desc_data']

# 数据库表结构配置 - 别名引用
DB_TABLE_SCHEMAS = DB_SCHEMA_CONFIG 