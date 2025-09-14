#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角色数据模型
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Role(Base):
    """角色信息表"""
    __tablename__ = 'roles'
    
    # 主键和基本信息
    eid = Column(String(191), primary_key=True, comment='角色唯一标识符')
    equipid = Column(Integer, comment='角色ID')
    equip_sn = Column(Text, comment='角色序列号')
    
    # 服务器和卖家信息
    server_name = Column(Text, comment='服务器名称')
    serverid = Column(Integer, comment='服务器ID')
    equip_server_sn = Column(Text, comment='角色服务器序列号')
    seller_nickname = Column(Text, comment='卖家昵称')
    seller_roleid = Column(String(191), comment='卖家角色ID')
    area_name = Column(Text, comment='区域名称')
    
    # 角色基本信息，增加role_type字段,默认值为normal
    role_type = Column(Text, default='normal', comment='角色类型')
    equip_name = Column(Text, comment='角色名称')
    equip_type = Column(Text, comment='角色类型')
    equip_type_name = Column(Text, comment='角色类型名称')
    equip_type_desc = Column(Text, comment='角色类型描述')
    level = Column(Integer, comment='角色等级')
    equip_level = Column(Integer, comment='角色等级')
    equip_level_desc = Column(Text, comment='角色等级描述')
    level_desc = Column(Text, comment='等级描述')
    subtitle = Column(Text, comment='副标题')
    equip_pos = Column(Integer, comment='角色位置')
    position = Column(Integer, comment='位置')
    school = Column(Integer, comment='门派限制')
    role_grade_limit = Column(Integer, comment='角色等级限制')
    min_buyer_level = Column(Integer, comment='最低购买者等级')
    equip_count = Column(Integer, comment='角色数量')
    
    # 价格和交易信息
    history_price = Column(Text, comment='历史价格')
    split_price_desc = Column(Text, comment='装备和召唤兽估价价格描述')
    base_price = Column(Float, comment='基本空号价格')
    equip_price = Column(Float, comment='装备估价价格')
    pet_price = Column(Float, comment='召唤兽估价价格')
    price = Column(Float, comment='价格')
    price_desc = Column(Text, comment='价格描述')
    unit_price_desc = Column(Text, comment='单价描述')
    min_unit_price = Column(Float, comment='最低单价')
    price_explanation = Column(Text, comment='价格说明')
    accept_bargain = Column(Boolean, default=False, comment='接受还价')
    bargain_info = Column(Text, comment='还价信息')
    
    # 状态和时间信息
    equip_status = Column(Integer, comment='角色状态')
    equip_status_desc = Column(Text, comment='角色状态描述')
    status_desc = Column(Text, comment='状态描述')
    onsale_expire_time_desc = Column(Text, comment='在售过期时间描述')
    time_left = Column(Text, comment='剩余时间')
    expire_time = Column(Text, comment='过期时间')
    selling_time = Column(Text, comment='销售时间')
    selling_time_ago_desc = Column(Text, comment='销售时间前描述')
    first_onsale_time = Column(Text, comment='首次上架时间')
    
    # 公示相关
    pass_fair_show = Column(Boolean, default=False, comment='是否通过公示')
    fair_show_time = Column(Integer, default=0, comment='公示时间')
    fair_show_end_time = Column(Text, comment='公示结束时间')
    fair_show_end_time_left = Column(Text, comment='公示结束剩余时间')
    fair_show_poundage = Column(Integer, default=0, comment='公示手续费')
    
    # 其他信息
    collect_num = Column(Integer, default=0, comment='收藏数')
    has_collect = Column(Boolean, default=False, comment='是否收藏')
    score = Column(Integer, default=0, comment='评分')
    icon_index = Column(Integer, default=0, comment='图标索引')
    icon = Column(Integer, default=0, comment='图标')
    equip_face_img = Column(String(500), comment='角色头像图片')
    kindid = Column(Integer, comment='种类ID')
    game_channel = Column(Text, comment='游戏渠道')
    
    # 订单相关
    game_ordersn = Column(Text, comment='游戏订单号')
    whole_game_ordersn = Column(Text, comment='完整游戏订单号')
    
    # 跨服相关
    allow_cross_buy = Column(Boolean, default=False, comment='允许跨服购买')
    cross_server_poundage = Column(Integer, default=0, comment='跨服手续费')
    cross_server_poundage_origin = Column(Integer, default=0, comment='原始跨服手续费')
    cross_server_poundage_discount = Column(Float, default=0, comment='跨服手续费折扣')
    cross_server_poundage_discount_label = Column(Text, comment='跨服手续费折扣标签')
    cross_server_poundage_display_mode = Column(Integer, default=0, comment='跨服手续费显示模式')
    cross_server_activity_conf_discount = Column(Float, default=0, comment='跨服活动配置折扣')
    
    # 活动相关
    activity_type = Column(Integer, default=0, comment='活动类型')
    joined_seller_activity = Column(Boolean, default=False, comment='参与卖家活动')
    
    # 拆分相关
    is_split_sale = Column(Boolean, default=False, comment='是否拆分销售')
    is_split_main_role = Column(Boolean, default=False, comment='是否拆分主角')
    is_split_independent_role = Column(Boolean, default=False, comment='是否独立角色拆分')
    is_split_independent_equip = Column(Boolean, default=False, comment='是否独立角色拆分')
    split_equip_sold_happen = Column(Boolean, default=False, comment='拆分角色销售发生')
    show_split_equip_sold_remind = Column(Boolean, default=False, comment='显示拆分角色销售提醒')
    
    # 保护相关
    is_onsale_protection_period = Column(Boolean, default=False, comment='是否在售保护期')
    onsale_protection_end_time = Column(Text, comment='在售保护结束时间')
    is_vip_protection = Column(Boolean, default=False, comment='是否VIP保护')
    is_time_lock = Column(Boolean, default=False, comment='是否时间锁定')
    time_lock_days = Column(Integer, default=0, comment='时间锁定天数')
    
    # 测试服相关
    equip_in_test_server = Column(Boolean, default=False, comment='角色在测试服')
    buyer_in_test_server = Column(Boolean, default=False, comment='买家在测试服')
    equip_in_allow_take_away_server = Column(Boolean, default=False, comment='角色在允许带走服务器')
    
    # 其他标识
    is_weijianding = Column(Boolean, default=False, comment='是否未鉴定')
    is_show_alipay_privilege = Column(Boolean, default=False, comment='是否显示支付宝特权')
    is_seller_redpacket_flag = Column(Boolean, default=False, comment='是否卖家红包标志')
    is_show_expert_desc = Column(Boolean, default=False, comment='是否显示专家描述')
    is_show_special_highlight = Column(Boolean, default=False, comment='是否显示特殊高亮')
    is_xyq_game_role_kunpeng_reach_limit = Column(Boolean, default=False, comment='是否达到鲲鹏限制')
    
    # 版本和存储相关
    equip_onsale_version = Column(Integer, default=0, comment='角色上架版本')
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
    large_equip_desc = Column(Text, comment='大角色描述')
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
    
    # 技能信息
    life_skills = Column(Text, default='', comment='生活技能')
    school_skills = Column(Text, default='', comment='师门技能')
    ju_qing_skills = Column(Text, default='', comment='剧情技能')
    yushoushu_skill = Column(Integer, default=0, comment='育兽术技能')

    raw_data_json = Column(Text, comment='原始数据')
    
    # 元数据
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    detail_info = relationship("LargeEquipDescData", back_populates="role", uselist=False)

class LargeEquipDescData(Base):
    """角色详细描述数据表"""
    __tablename__ = 'large_equip_desc_data'
    
    eid = Column(String(191), ForeignKey('roles.eid'), primary_key=True, comment='关联到roles表的eid')
    time_lock_days = Column(Integer, comment='时间锁定天数')
    
    # 基础信息
    role_name = Column(Text, comment='角色名')
    role_level = Column(Integer, comment='等级')
    role_school = Column(Integer, comment='门派')
    role_icon = Column(Integer, comment='图标ID')
    user_num = Column(Text, comment='用户ID')
    
    # 属性信息
    hp_max = Column(Integer, comment='气血')
    mp_max = Column(Integer, comment='魔法')
    att_all = Column(Integer, comment='命中')
    def_all = Column(Integer, comment='防御')
    spe_all = Column(Integer, comment='敏捷')
    mag_all = Column(Integer, comment='魔力')
    damage_all = Column(Integer, comment='伤害')
    mag_dam_all = Column(Integer, comment='法术伤害')
    mag_def_all = Column(Integer, comment='法术防御')
    dod_all = Column(Integer, comment='躲避')
    cor_all = Column(Integer, comment='体质')
    str_all = Column(Integer, comment='力量')
    res_all = Column(Integer, comment='耐力')
    dex_all = Column(Integer, comment='速度')
    
    # 经验和修炼
    up_exp = Column(Integer, comment='获得经验')
    sum_exp = Column(Integer, comment='总经验')
    expt_ski1 = Column(Integer, comment='攻击修炼')
    expt_ski2 = Column(Integer, comment='防御修炼')
    expt_ski3 = Column(Integer, comment='法术修炼')
    expt_ski4 = Column(Integer, comment='抗法修炼')
    expt_ski5 = Column(Integer, comment='猎术修炼')
    max_expt1 = Column(Integer, comment='攻击修炼上限')
    max_expt2 = Column(Integer, comment='防御修炼上限')
    max_expt3 = Column(Integer, comment='法术修炼上限')
    max_expt4 = Column(Integer, comment='抗法修炼上限')
    
    # 召唤兽控制技能
    beast_ski1 = Column(Integer, comment='攻击控制力')
    beast_ski2 = Column(Integer, comment='防御控制力')
    beast_ski3 = Column(Integer, comment='法术控制力')
    beast_ski4 = Column(Integer, comment='抗法控制力')
    
    # 技能点和属性点
    skill_point = Column(Integer, comment='剧情技能剩余点')
    attribute_point = Column(Integer, comment='属性点')
    potential = Column(Integer, comment='潜力值')
    max_potential = Column(Integer, comment='最大潜力值')
    
    # 金钱相关
    cash = Column(Integer, comment='现金')
    saving = Column(Integer, comment='存款')
    learn_cash = Column(Integer, comment='储备金')
    
    # 转职飞升相关
    zhuan_zhi = Column(Integer, comment='转职状态')
    all_new_point = Column(Integer, comment='乾元丹')
    three_fly_lv = Column(Integer, comment='化圣等级')
    nine_fight_level = Column(Integer, comment='生死劫等级')
    
    # 善恶值
    goodness = Column(Integer, comment='善恶值')
    badness = Column(Integer, comment='罪恶值')
    goodness_sav = Column(Integer, comment='善恶储存')
    
    # 称谓和帮派
    role_title = Column(Text, comment='称谓')
    org_name = Column(Text, comment='帮派名称')
    org_offer = Column(Integer, comment='帮贡')
    org_position = Column(Text, comment='帮派职位')
    
    # 婚姻和结义
    marry_id = Column(Text, comment='结婚对象')
    marry2_id = Column(Text, comment='结义对象')
    marry_name = Column(Text, comment='结婚对象名称')
    
    # 社区信息
    community_name = Column(Text, comment='社区名称')
    community_gid = Column(Text, comment='社区ID')
    
    # 成就和评分
    achievement_total = Column(Integer, comment='成就点')
    hero_score = Column(Integer, comment='英雄评分')
    datang_feat = Column(Integer, comment='三界功绩')
    sword_score = Column(Integer, comment='剑会评分')
    dup_score = Column(Integer, comment='副本评分')
    shenqi_score = Column(Integer, comment='神器评分')
    qicai_score = Column(Integer, comment='奇才评分')
    xianyu_score = Column(Integer, comment='仙玉积分')
    
    # 道具相关
    nuts_num = Column(Integer, comment='潜能果数量')
    cg_total_amount = Column(Integer, comment='彩果总数')
    cg_body_amount = Column(Integer, comment='身上彩果')
    cg_box_amount = Column(Integer, comment='仓库彩果')
    xianyu_amount = Column(Integer, comment='仙玉')
    energy_amount = Column(Integer, comment='精力')
    jiyuan_amount = Column(Integer, comment='机缘')
    add_point = Column(Integer, comment='加点')
    
    # 背包信息
    packet_page = Column(Integer, comment='背包页数')
    
    # 房屋相关
    rent_level = Column(Integer, comment='房屋等级')
    outdoor_level = Column(Integer, comment='庭院等级')
    farm_level = Column(Integer, comment='牧场等级')
    house_real_owner = Column(Integer, comment='房屋真实拥有者')
    
    # 其他信息
    pride = Column(Integer, comment='人气')
    bid_status = Column(Integer, comment='靓号状态')
    ori_race = Column(Integer, comment='原始种族')
    current_race = Column(Integer, comment='当前种族')
    sum_amount = Column(Integer, comment='最大召唤兽携带数量')
    version_code = Column(Text, comment='版本码')
    
    # JSON数据字段（改为Text类型，避免空字符串解析错误）
    pet = Column(Text, comment='特殊召唤兽')
    all_skills_json = Column(Text, comment='所有技能')
    all_equip_json = Column(Text, comment='所有装备')
    all_summon_json = Column(Text, comment='所有召唤兽')
    child_json = Column(Text, comment='孩子信息')
    child2_json = Column(Text, comment='孩子2信息')
    all_rider_json = Column(Text, comment='所有坐骑')
    ex_avt_json = Column(Text, comment='时装')
    huge_horse_json = Column(Text, comment='祥瑞')
    fabao_json = Column(Text, comment='法宝')
    lingbao_json = Column(Text, comment='灵宝')
    shenqi_json = Column(Text, comment='神器')
    idbid_desc_json = Column(Text, comment='靓号描述')
    changesch_json = Column(Text, comment='转门派历史')
    prop_kept_json = Column(Text, comment='保持属性')
    more_attr_json = Column(Text, comment='更多属性')

    # 时间字段
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    role = relationship("Role", back_populates="detail_info")
