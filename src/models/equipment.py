#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
装备数据模型
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean
from .base import Base

class Equipment(Base):
    """装备信息表"""
    __tablename__ = 'equipments'
    
    # 主键和基本信息
    equip_sn = Column(String(191), primary_key=True, comment='装备序列号（主键）')
    eid = Column(String(191), comment='装备唯一标识符')
    equipid = Column(Integer, comment='装备ID')
    
    # 服务器和卖家信息
    server_name = Column(Text, comment='服务器名称')
    serverid = Column(Integer, comment='服务器ID')
    equip_server_sn = Column(Text, comment='装备服务器序列号')
    seller_nickname = Column(Text, comment='卖家昵称')
    seller_roleid = Column(String(191), comment='卖家角色ID')
    area_name = Column(Text, comment='区域名称')
    
    # 装备基本信息
    equip_name = Column(Text, comment='装备名称')
    equip_type = Column(Text, comment='装备类型')
    equip_type_name = Column(Text, comment='装备类型名称')
    equip_type_desc = Column(Text, comment='装备类型描述')
    level = Column(Integer, comment='装备等级')
    equip_level = Column(Integer, comment='装备等级')
    equip_level_desc = Column(Text, comment='装备等级描述')
    level_desc = Column(Text, comment='等级描述')
    subtitle = Column(Text, comment='副标题')
    equip_pos = Column(Integer, comment='装备位置')
    position = Column(Integer, comment='位置')
    school = Column(Integer, comment='门派限制')
    role_grade_limit = Column(Integer, comment='角色等级限制')
    min_buyer_level = Column(Integer, comment='最低购买者等级')
    equip_count = Column(Integer, comment='装备数量')
    
    # 价格和交易信息
    price = Column(Float, comment='价格')
    price_desc = Column(Text, comment='价格描述')
    unit_price_desc = Column(Text, comment='单价描述')
    min_unit_price = Column(Float, comment='最低单价')
    price_explanation = Column(Text, comment='价格说明')
    accept_bargain = Column(Boolean, default=False, comment='接受还价')
    bargain_info = Column(Text, comment='还价信息')
    
    # 状态和时间信息
    equip_status = Column(Integer, comment='装备状态')
    equip_status_desc = Column(Text, comment='装备状态描述')
    status_desc = Column(Text, comment='状态描述')
    onsale_expire_time_desc = Column(Text, comment='在售过期时间描述')
    time_left = Column(Text, comment='剩余时间')
    expire_time = Column(Text, comment='过期时间')
    create_time_equip = Column(Text, comment='装备创建时间')
    selling_time = Column(Text, comment='销售时间')
    selling_time_ago_desc = Column(Text, comment='销售时间前描述')
    first_onsale_time = Column(Text, comment='首次上架时间')
    
    # 公示相关
    pass_fair_show = Column(Boolean, default=False, comment='是否通过公示')
    fair_show_time = Column(Integer, default=0, comment='公示时间')
    fair_show_end_time = Column(Text, comment='公示结束时间')
    fair_show_end_time_left = Column(Text, comment='公示结束剩余时间')
    fair_show_poundage = Column(Integer, default=0, comment='公示手续费')
    
    # 装备属性
    hp = Column(Integer, default=0, comment='气血')
    qixue = Column(Integer, default=0, comment='气血（别名）')
    init_hp = Column(Integer, default=0, comment='初始气血')
    mofa = Column(Integer, default=0, comment='魔法')
    init_wakan = Column(Integer, default=0, comment='初始魔力')
    mingzhong = Column(Integer, default=0, comment='命中')
    fangyu = Column(Integer, default=0, comment='防御')
    init_defense = Column(Integer, default=0, comment='初始防御')
    defense = Column(Integer, default=0, comment='防御（别名）')
    speed = Column(Integer, default=0, comment='速度')
    minjie = Column(Integer, default=0, comment='敏捷')
    init_dex = Column(Integer, default=0, comment='初始敏捷')
    shanghai = Column(Integer, default=0, comment='伤害')
    damage = Column(Integer, default=0, comment='伤害（别名）')
    init_damage = Column(Integer, default=0, comment='初始伤害')
    init_damage_raw = Column(Integer, default=0, comment='原始初始伤害')
    all_damage = Column(Integer, default=0, comment='总伤害')
    magic_damage = Column(Integer, default=0, comment='法术伤害')
    magic_defense = Column(Integer, default=0, comment='法术防御')
    lingli = Column(Integer, default=0, comment='灵力')
    fengyin = Column(Integer, default=0, comment='封印')
    anti_fengyin = Column(Integer, default=0, comment='抗封印')
    zongshang = Column(Integer, default=0, comment='总伤')
    
    # 修炼相关
    expt_gongji = Column(Integer, default=0, comment='攻击修炼')
    expt_fangyu = Column(Integer, default=0, comment='防御修炼')
    expt_fashu = Column(Integer, default=0, comment='法术修炼')
    expt_kangfa = Column(Integer, default=0, comment='抗法修炼')
    max_expt_gongji = Column(Integer, default=0, comment='最大攻击修炼')
    max_expt_fangyu = Column(Integer, default=0, comment='最大防御修炼')
    max_expt_fashu = Column(Integer, default=0, comment='最大法术修炼')
    max_expt_kangfa = Column(Integer, default=0, comment='最大抗法修炼')
    sum_exp = Column(Integer, default=0, comment='总经验')
    
    # 宝宝修炼相关
    bb_expt_gongji = Column(Integer, default=0, comment='宝宝攻击修炼')
    bb_expt_fangyu = Column(Integer, default=0, comment='宝宝防御修炼')
    bb_expt_fashu = Column(Integer, default=0, comment='宝宝法术修炼')
    bb_expt_kangfa = Column(Integer, default=0, comment='宝宝抗法修炼')
    
    # 附加属性
    addon_tizhi = Column(Integer, default=0, comment='附加体质')
    addon_liliang = Column(Integer, default=0, comment='附加力量')
    addon_naili = Column(Integer, default=0, comment='附加耐力')
    addon_minjie = Column(Integer, default=0, comment='附加敏捷')
    addon_fali = Column(Integer, default=0, comment='附加法力')
    addon_lingli = Column(Integer, default=0, comment='附加灵力')
    addon_moli = Column(Integer, default=0, comment='附加魔力')
    addon_total = Column(Integer, default=0, comment='附加总和')
    addon_status = Column(Text, comment='附加状态（套装信息）')
    addon_skill_chance = Column(Integer, default=0, comment='附加技能几率')
    addon_effect_chance = Column(Integer, default=0, comment='附加效果几率')
    
    # 宝石相关
    gem_level = Column(Integer, default=0, comment='宝石等级')
    gem_value = Column(Text, comment='宝石数值')
    xiang_qian_level = Column(Integer, default=0, comment='镶嵌等级')
    
    # 强化相关
    jinglian_level = Column(Integer, default=0, comment='精炼等级')
    
    # 特技和套装
    special_skill = Column(Integer, default=0, comment='特技')
    special_effect = Column(Text, comment='特效')
    suit_skill = Column(Integer, default=0, comment='套装技能')
    suit_effect = Column(Integer, default=0, comment='套装效果')
    
    # 其他信息
    collect_num = Column(Integer, default=0, comment='收藏数')
    has_collect = Column(Boolean, default=False, comment='是否已收藏')
    score = Column(Integer, default=0, comment='评分')
    icon_index = Column(Integer, comment='图标索引')
    icon = Column(Text, comment='图标')
    equip_face_img = Column(String(500), comment='装备头像图片')
    kindid = Column(Integer, comment='种类ID')
    game_channel = Column(Text, comment='游戏渠道')
    
    # 订单相关
    game_ordersn = Column(Text, comment='游戏订单号')
    whole_game_ordersn = Column(Text, comment='完整游戏订单号')
    
    # 跨服相关
    allow_cross_buy = Column(Boolean, default=False, comment='允许跨服购买')
    cross_server_poundage = Column(Integer, default=0, comment='跨服手续费')
    cross_server_poundage_origin = Column(Integer, default=0, comment='原始跨服手续费')
    cross_server_poundage_discount = Column(Integer, default=0, comment='跨服手续费折扣')
    cross_server_poundage_discount_label = Column(Text, comment='跨服手续费折扣标签')
    cross_server_poundage_display_mode = Column(Integer, default=0, comment='跨服手续费显示模式')
    cross_server_activity_conf_discount = Column(Float, default=0, comment='跨服活动配置折扣')
    
    # 活动相关
    activity_type = Column(Text, comment='活动类型')
    joined_seller_activity = Column(Boolean, default=False, comment='参与卖家活动')
    
    # 拆分相关
    is_split_sale = Column(Boolean, default=False, comment='是否拆分销售')
    is_split_main_role = Column(Boolean, default=False, comment='是否拆分主角色')
    is_split_independent_role = Column(Boolean, default=False, comment='是否拆分独立角色')
    is_split_independent_equip = Column(Boolean, default=False, comment='是否拆分独立装备')
    split_equip_sold_happen = Column(Boolean, default=False, comment='拆分装备售出发生')
    show_split_equip_sold_remind = Column(Boolean, default=False, comment='显示拆分装备售出提醒')
    
    # 保护相关
    is_onsale_protection_period = Column(Boolean, default=False, comment='是否在售保护期')
    onsale_protection_end_time = Column(Text, comment='在售保护结束时间')
    is_vip_protection = Column(Boolean, default=False, comment='是否VIP保护')
    is_time_lock = Column(Boolean, default=False, comment='是否时间锁定')
    
    # 测试服相关
    equip_in_test_server = Column(Boolean, default=False, comment='装备在测试服')
    buyer_in_test_server = Column(Boolean, default=False, comment='购买者在测试服')
    equip_in_allow_take_away_server = Column(Boolean, default=False, comment='装备在允许带走服务器')
    
    # 其他标识
    is_weijianding = Column(Boolean, default=False, comment='是否未鉴定')
    is_show_alipay_privilege = Column(Boolean, default=False, comment='是否显示支付宝特权')
    is_seller_redpacket_flag = Column(Boolean, default=False, comment='卖家红包标志')
    is_show_expert_desc = Column(Integer, default=-1, comment='是否显示专家描述')
    is_show_special_highlight = Column(Boolean, default=False, comment='是否显示特殊高亮')
    is_xyq_game_role_kunpeng_reach_limit = Column(Boolean, default=False, comment='是否鲲鹏达到限制')
    
    # 版本和存储相关
    equip_onsale_version = Column(Integer, default=0, comment='装备在售版本')
    storage_type = Column(Integer, default=0, comment='存储类型')
    agent_trans_time = Column(Integer, default=0, comment='代理传输时间')
    
    # KOL相关
    kol_article_id = Column(Text, comment='KOL文章ID')
    kol_share_id = Column(Text, comment='KOL分享ID')
    kol_share_time = Column(Text, comment='KOL分享时间')
    kol_share_status = Column(Text, comment='KOL分享状态')
    
    # 推荐相关
    reco_request_id = Column(Text, comment='推荐请求ID')
    appointed_roleid = Column(String(191), comment='指定角色ID')
    
    # 团队相关
    play_team_cnt = Column(Integer, default=0, comment='游戏团队数量')
    
    # 随机抽奖相关
    random_draw_finish_time = Column(Text, comment='随机抽奖完成时间')
    
    # 详细描述
    desc = Column(Text, comment='描述')
    large_equip_desc = Column(Text, comment='大装备描述')
    desc_sumup = Column(Text, comment='描述总结')
    desc_sumup_short = Column(Text, comment='描述总结简短')
    diy_desc = Column(Text, comment='自定义描述')
    rec_desc = Column(Text, comment='推荐描述')
    diy_desc_pay_info = Column(Text, comment='自定义描述支付信息')
    
    # 其他复杂数据（JSON格式）
    other_info = Column(Text, comment='其他信息')
    video_info = Column(Text, comment='视频信息')
    agg_added_attrs = Column(Text, comment='聚合附加属性')
    dynamic_tags = Column(Text, comment='动态标签')
    highlight = Column(Text, comment='高亮信息')
    tag_key = Column(Text, comment='标签键')
    tag = Column(Text, comment='标签')
    
    # 搜索相关
    search_type = Column(Text, comment='搜索类型')
    
    # 元数据
    raw_data_json = Column(Text, comment='原始数据')
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
