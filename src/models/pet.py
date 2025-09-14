#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
召唤兽数据模型
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean, JSON
from .base import Base

class Pet(Base):
    """召唤兽信息表"""
    __tablename__ = 'pets'
    
    # 主键和基本信息
    equip_sn = Column(String(255), primary_key=True, comment='召唤兽序列号')
    eid = Column(String(255), unique=True, comment='召唤兽唯一标识符')
    equipid = Column(Integer, comment='召唤兽ID')
    
    # 服务器和卖家信息
    server_name = Column(String(255), comment='服务器名称')
    serverid = Column(Integer, comment='服务器ID')
    equip_server_sn = Column(String(255), comment='召唤兽服务器序列号')
    seller_nickname = Column(String(255), comment='卖家昵称')
    seller_roleid = Column(String(255), comment='卖家角色ID')
    area_name = Column(String(255), comment='区域名称')
    
    # 召唤兽基本信息
    equip_name = Column(String(255), comment='召唤兽名称')
    equip_type = Column(String(255), comment='召唤兽类型')
    equip_type_name = Column(String(255), comment='召唤兽类型名称')
    equip_type_desc = Column(Text, comment='召唤兽类型描述')
    level = Column(Integer, comment='召唤兽等级')
    equip_level = Column(Integer, comment='召唤兽等级')
    equip_level_desc = Column(String(255), comment='召唤兽等级描述')
    level_desc = Column(String(255), comment='等级描述')
    subtitle = Column(String(255), comment='副标题')
    equip_pos = Column(Integer, comment='召唤兽位置')
    position = Column(Integer, comment='位置')
    school = Column(Integer, comment='门派限制')
    role_grade_limit = Column(Integer, comment='角色等级限制')
    min_buyer_level = Column(Integer, comment='最低购买者等级')
    equip_count = Column(Integer, comment='召唤兽数量')
    
    # 价格和交易信息
    price = Column(Float, comment='价格')
    price_desc = Column(String(255), comment='价格描述')
    unit_price_desc = Column(String(255), comment='单价描述')
    min_unit_price = Column(Float, comment='最低单价')
    price_explanation = Column(JSON, comment='价格说明')
    accept_bargain = Column(Boolean, default=False, comment='接受还价')
    bargain_info = Column(JSON, comment='还价信息')
    
    # 状态和时间信息
    equip_status = Column(Integer, comment='召唤兽状态')
    equip_status_desc = Column(String(255), comment='召唤兽状态描述')
    status_desc = Column(String(255), comment='状态描述')
    onsale_expire_time_desc = Column(String(255), comment='在售过期时间描述')
    time_left = Column(String(255), comment='剩余时间')
    expire_time = Column(String(255), comment='过期时间')
    create_time_equip = Column(String(255), comment='召唤兽创建时间')
    selling_time = Column(String(255), comment='销售时间')
    selling_time_ago_desc = Column(String(255), comment='销售时间前描述')
    first_onsale_time = Column(String(255), comment='首次上架时间')
    
    # 公示相关
    pass_fair_show = Column(Boolean, default=False, comment='是否通过公示')
    fair_show_time = Column(Integer, default=0, comment='公示时间')
    fair_show_end_time = Column(String(255), comment='公示结束时间')
    fair_show_end_time_left = Column(String(255), comment='公示结束剩余时间')
    fair_show_poundage = Column(Integer, default=0, comment='公示手续费')
    
    # 其他信息
    collect_num = Column(Integer, default=0, comment='收藏数')
    has_collect = Column(Boolean, default=False, comment='是否收藏')
    score = Column(Integer, default=0, comment='评分')
    icon_index = Column(Integer, default=0, comment='图标索引')
    icon = Column(Integer, default=0, comment='图标')
    equip_face_img = Column(String(500), comment='召唤兽头像图片')
    kindid = Column(Integer, comment='种类ID')
    game_channel = Column(String(255), comment='游戏渠道')
    
    # 订单相关
    game_ordersn = Column(String(255), comment='游戏订单号')
    whole_game_ordersn = Column(String(255), comment='完整游戏订单号')
    
    # 跨服相关
    allow_cross_buy = Column(Boolean, default=False, comment='允许跨服购买')
    cross_server_poundage = Column(Integer, default=0, comment='跨服手续费')
    cross_server_poundage_origin = Column(Integer, default=0, comment='原始跨服手续费')
    cross_server_poundage_discount = Column(Float, default=0, comment='跨服手续费折扣')
    cross_server_poundage_discount_label = Column(String(255), comment='跨服手续费折扣标签')
    cross_server_poundage_display_mode = Column(Integer, default=0, comment='跨服手续费显示模式')
    cross_server_activity_conf_discount = Column(Float, default=0, comment='跨服活动配置折扣')
    
    # 活动相关
    activity_type = Column(Integer, default=0, comment='活动类型')
    joined_seller_activity = Column(Boolean, default=False, comment='参与卖家活动')
    
    # 拆分相关
    is_split_sale = Column(Boolean, default=False, comment='是否拆分销售')
    is_split_main_role = Column(Boolean, default=False, comment='是否拆分主角')
    is_split_independent_role = Column(Boolean, default=False, comment='是否独立角色拆分')
    is_split_independent_equip = Column(Boolean, default=False, comment='是否独立召唤兽拆分')
    split_equip_sold_happen = Column(Boolean, default=False, comment='拆分召唤兽销售发生')
    show_split_equip_sold_remind = Column(Boolean, default=False, comment='显示拆分召唤兽销售提醒')
    
    # 保护相关
    is_onsale_protection_period = Column(Boolean, default=False, comment='是否在售保护期')
    onsale_protection_end_time = Column(String(255), comment='在售保护结束时间')
    is_vip_protection = Column(Boolean, default=False, comment='是否VIP保护')
    is_time_lock = Column(Boolean, default=False, comment='是否时间锁定')
    
    # 测试服相关
    equip_in_test_server = Column(Boolean, default=False, comment='召唤兽在测试服')
    buyer_in_test_server = Column(Boolean, default=False, comment='买家在测试服')
    equip_in_allow_take_away_server = Column(Boolean, default=False, comment='召唤兽在允许带走服务器')
    
    # 其他标识
    is_weijianding = Column(Boolean, default=False, comment='是否未鉴定')
    is_show_alipay_privilege = Column(Boolean, default=False, comment='是否显示支付宝特权')
    is_seller_redpacket_flag = Column(Boolean, default=False, comment='是否卖家红包标志')
    is_show_expert_desc = Column(Boolean, default=False, comment='是否显示专家描述')
    is_show_special_highlight = Column(Boolean, default=False, comment='是否显示特殊高亮')
    is_xyq_game_role_kunpeng_reach_limit = Column(Boolean, default=False, comment='是否达到鲲鹏限制')
    
    # 版本和存储相关
    equip_onsale_version = Column(Integer, default=0, comment='召唤兽上架版本')
    storage_type = Column(Integer, default=0, comment='存储类型')
    agent_trans_time = Column(Integer, default=0, comment='代理传输时间')
    
    # KOL相关
    kol_article_id = Column(String(255), comment='KOL文章ID')
    kol_share_id = Column(String(255), comment='KOL分享ID')
    kol_share_time = Column(String(255), comment='KOL分享时间')
    kol_share_status = Column(String(255), comment='KOL分享状态')
    
    # 推荐相关
    reco_request_id = Column(String(255), comment='推荐请求ID')
    appointed_roleid = Column(String(255), comment='指定角色ID')
    
    # 团队相关
    play_team_cnt = Column(Integer, default=0, comment='游戏团队数量')
    
    # 随机抽奖相关
    random_draw_finish_time = Column(String(255), comment='随机抽奖完成时间')
    
    # 详细描述
    desc = Column(Text, comment='描述')
    large_equip_desc = Column(Text, comment='大召唤兽描述')
    desc_sumup = Column(Text, comment='描述总结')
    desc_sumup_short = Column(Text, comment='描述总结简短')
    diy_desc = Column(Text, comment='自定义描述')
    rec_desc = Column(Text, comment='推荐描述')
    diy_desc_pay_info = Column(JSON, comment='自定义描述支付信息')
    
    # 其他复杂数据（JSON格式）
    other_info = Column(JSON, comment='其他信息')
    video_info = Column(JSON, comment='视频信息')
    agg_added_attrs = Column(JSON, comment='聚合附加属性')
    dynamic_tags = Column(JSON, comment='动态标签')
    highlight = Column(JSON, comment='高亮信息')
    tag_key = Column(JSON, comment='标签键')
    tag = Column(String(255), comment='标签')
    
    # 搜索相关
    search_type = Column(String(255), comment='搜索类型')
    
    # decode_desc解析出的字段
    pet_name = Column(String(255), comment='解析出的召唤兽名称')
    type_id = Column(String(255), comment='解析出的类型ID')
    pet_grade = Column(String(255), comment='解析出的召唤兽等级')
    blood = Column(String(255), comment='解析出的气血')
    magic = Column(String(255), comment='解析出的魔法')
    attack = Column(Integer, default=0, comment='解析出的攻击')
    defence = Column(String(255), comment='解析出的防御')
    speed = Column(String(255), comment='解析出的速度')
    soma = Column(String(255), comment='解析出的体质')
    magic_powner = Column(String(255), comment='解析出的魔力')
    strength = Column(String(255), comment='解析出的力量')
    endurance = Column(String(255), comment='解析出的耐力')
    smartness = Column(String(255), comment='解析出的敏捷')
    potential = Column(String(255), comment='解析出的潜力')
    wakan = Column(String(255), comment='解析出的灵力')
    max_blood = Column(String(255), comment='解析出的最大气血')
    max_magic = Column(String(255), comment='解析出的最大魔法')
    lifetime = Column(String(255), comment='解析出的寿命')
    five_aptitude = Column(String(255), comment='解析出的五行')
    attack_aptitude = Column(String(255), comment='解析出的攻击资质')
    defence_aptitude = Column(String(255), comment='解析出的防御资质')
    physical_aptitude = Column(String(255), comment='解析出的体力资质')
    magic_aptitude = Column(String(255), comment='解析出的法力资质')
    speed_aptitude = Column(String(255), comment='解析出的速度资质')
    avoid_aptitude = Column(String(255), comment='解析出的躲避资质')
    growth = Column(Float, default=0.0, comment='解析出的成长率')
    all_skill = Column(Text, comment='解析出的所有技能')
    sp_skill = Column(Text, comment='解析出的特殊技能')
    is_baobao = Column(String(255), comment='解析出的是否宝宝')
    used_qianjinlu = Column(String(255), comment='解析出的千金露使用情况')
    sp_skill_id = Column(String(255), comment='解析出的特殊技能ID')
    all_skills = Column(JSON, comment='解析出的技能列表')
    ti_zhi_add = Column(Integer, default=0, comment='解析出的体质加点')
    fa_li_add = Column(Integer, default=0, comment='解析出的法力加点')
    li_liang_add = Column(Integer, default=0, comment='解析出的力量加点')
    nai_li_add = Column(Integer, default=0, comment='解析出的耐力加点')
    min_jie_add = Column(Integer, default=0, comment='解析出的敏捷加点')
    jinjie = Column(JSON, comment='解析出的进阶信息')
    lx = Column(Integer, default=0, comment='解析出的灵性')
    jinjie_cnt = Column(String(255), comment='解析出的进阶次数')
    texing = Column(JSON, comment='解析出的特性')
    core_close = Column(String(255), comment='解析出的核心关闭状态')
    attack_ext = Column(Integer, default=0, comment='解析出的攻击扩展')
    defence_ext = Column(Integer, default=0, comment='解析出的防御扩展')
    speed_ext = Column(Integer, default=0, comment='解析出的速度扩展')
    avoid_ext = Column(Integer, default=0, comment='解析出的躲避扩展')
    physical_ext = Column(Integer, default=0, comment='解析出的体力扩展')
    magic_ext = Column(Integer, default=0, comment='解析出的法力扩展')
    neidan = Column(JSON, comment='解析出的内丹')
    equip_list = Column(JSON, comment='解析出的装备列表')
    evol_skill_list = Column(JSON, comment='解析出的进化技能列表')
    evol_skills = Column(JSON, comment='解析出的进化技能')
    color = Column(Integer, comment='解析出的颜色')
    summon_color = Column(Integer, comment='解析出的召唤兽颜色')
    iMagDam = Column(Integer, comment='解析出的法术伤害')
    iMagDef = Column(Integer, comment='解析出的法术防御')
    used_sjg = Column(Integer, default=0, comment='解析出的神机阁使用情况')
    used_yuanxiao = Column(Integer, default=0, comment='解析出的元宵使用情况')
    used_lianshou = Column(Integer, default=0, comment='解析出的炼兽使用情况')
    other = Column(JSON, comment='解析出的其他信息')
    
    # 装备估价相关
    equip_list_amount = Column(Integer, default=0, comment='装备总价值（分）')
    equip_list_amount_warning = Column(Integer, default=0, comment='装备总价值是否有异常（0：无异常，1：异常）')
    
    # 元数据
    raw_data_json = Column(Text, comment='原始数据')
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
