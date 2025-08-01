function get_role_iconid(type_id) {
    var need_fix_range = [[13, 24], [37, 48], [61, 72], [213, 224], [237, 248], [261, 272]];
    for (var i = 0; i < need_fix_range.length; i++) {
        var range = need_fix_range[i];
        if (type_id >= range[0] && type_id <= range[1]) {
            type_id = type_id - 12
            break;
        }
    }
    return type_id;
}
function get_role_kind_name(icon) {
    var kindid = icon;
    if (icon > 200) {
        kindid = ((icon - 200 - 1) % 12 + 1) + 200;
    } else {
        kindid = ((icon - 1) % 12 + 1);
    }
    return RoleKindNameInfo[kindid];
}
(function(win) {
    if (win.RACE_INFO) {
        return;
    }
    win.RACE_INFO = {
        0: "",
        1: "人",
        2: "魔",
        3: "仙"
    };
    win.CHINESE_NUM_CONFIG = {
        1: "一",
        2: "二",
        3: "三",
        4: "四",
        5: "五",
        6: "六",
        7: "七",
        8: "八",
        9: "九",
        10: "十"
    };
    win.ROLE_ZHUAN_ZHI_CONFIG = {
        0: "未飞升",
        1: "飞升",
        2: "渡劫"
    };
}
)(window);
(function(ctx, name, defination) {
    if (ctx[name]) {
        return;
    }
    ctx[name] = defination();
}
)(window, 'RoleInfoParser', function() {
    function each(obj, callback) {
        if (typeOf(obj) === 'array') {
            for (var i = 0, max = obj.length; i < max; i++) {
                callback.call(obj, obj[i], i);
            }
        } else {
            for (var key in obj) {
                if (obj.hasOwnProperty(key)) {
                    callback.call(obj, obj[key], key);
                }
            }
        }
    }
    function typeOf(obj) {
        return Object.prototype.toString.call(obj).split(' ')[1].slice(0, -1).toLowerCase();
    }
    function toArray(obj) {
        return [].slice.call(obj, 0);
    }
    function trim(str) {
        if (str) {
            return str.trim ? str.trim() : str.toString().replace(/^\s+|\s+$/g, '');
        }
        return '';
    }
    function extend(obj) {
        var args = toArray(arguments);
        var obj = args.shift();
        each(args, function(sour) {
            each(sour, function(val, key) {
                obj[key] = val;
            });
        });
        return obj;
    }
    function RoleInfoParser(roleInfo, options) {
        var ctx = this;
        var typeRoleInfo = typeOf(roleInfo);
        switch (typeRoleInfo) {
        case 'object':
            ctx.raw_info = roleInfo;
            break;
        case 'string':
            ctx.raw_info = js_eval(lpc_2_js(trim(roleInfo)));
            break;
        default:
            throw 'roleInfo should be Object or String.';
        }
        options = extend({
            conf: new RoleNameConf(),
            gConf: window.CBG_GAME_CONFIG || {},
            resUrl: window.ResUrl || '',
            serverId: '',
            equipRequestTime: window.EquipRequestTime || '',
            serverCurrentTime: window.ServerCurrentTime || ''
        }, options || {});
        ctx.conf = options.conf;
        ctx.gConf = options.gConf;
        ctx.resUrl = options.resUrl;
        ctx.serverId = options.serverId;
        ctx.equipRequestTime = options.equipRequestTime;
        ctx.serverCurrentTime = options.serverCurrentTime;
        ctx.split_equip_dict = options.split_equip_dict || {};
        ctx.is_support_inquiry = options.is_support_inquiry;
        ctx.inquiry_support_info = options.inquiry_support_info || {};
        ctx.game_ordersn = options.game_ordersn;
        ctx.is_my_equip = options.is_my_equip;
        ctx.equip_level = options.equip_level
        ctx.result = {};
        ctx.parse_role();
    }
    RoleInfoParser.prototype = {
        get_basic_data: function() {
            return extend({}, this.result || {});
        },
        get_skill_data: function() {
            var school_skill_info = {};
            for (var i = 1; i < 8; i++) {
                school_skill_info["school_skill" + i + "_icon"] = EmptySkillImg;
                school_skill_info["school_skill" + i + "_grade"] = "";
                school_skill_info["school_skill" + i + "_name"] = "";
            }
            for (var i = 0; i < this.result["role_skill"]["school_skill"].length; i++) {
                var skill = this.result["role_skill"]["school_skill"][i];
                school_skill_info["school_skill" + skill["skill_pos"] + "_icon"] = skill.skill_icon;
                school_skill_info["school_skill" + skill["skill_pos"] + "_grade"] = skill.skill_grade;
                school_skill_info["school_skill" + skill["skill_pos"] + "_name"] = skill.skill_name;
                school_skill_info["school_skill" + skill["skill_pos"] + "_desc"] = skill.desc;
            }
            return extend(school_skill_info, this.result["role_skill"] || {});
        },
        get_equips_data: function() {
            return extend({}, this.result);
        },
        get_fabao_data: function() {
            var using_fabaos = {};
            var list = this.result["using_fabao"];
            for (var i = 0; i < list.length; i++) {
                var fabao = list[i];
                using_fabaos[fabao["pos"]] = fabao;
            }
            function parse_fabao(fabao_desc, static_desc) {
                var cengshu = /第#G(\d+)#Y层/.exec(fabao_desc);
                cengshu = cengshu ? cengshu[1] : '';
                var wuxing = /五行[:：]#G(.{1,2})#Y/.exec(fabao_desc);
                wuxing = wuxing ? wuxing[1] : '';
                var level = /【法宝等级】\s*(.+?级)/.exec(static_desc || '');
                level = level ? level[1] : '';
                return [cengshu, wuxing, level];
            }
            ;return extend({
                parse_fabao: parse_fabao,
                using_fabaos: using_fabaos
            }, this.result);
        },
        get_pet_data: function() {
            var raw_info = this.raw_info;
            return extend({}, this.result, {
                sbook_skill_total: raw_info['sbook_skill_total'],
                sbook_skill: raw_info['sbook_skill']
            });
        },
        get_rider_data: function() {
            return extend({}, this.result);
        },
        get_clothes_data: function() {
            return extend({}, this.result);
        },
        get_house_data: function() {
            return extend({}, this.result);
        },
        parse_role: function() {
            var ctx = this;
            ctx.parse_basic_role_info();
            ctx.parse_role_skill();
            ctx.parse_equip_info();
            ctx.parse_fabao_info();
            ctx.parse_shenqi_info();
            ctx.parse_huoshenta();
            ctx.parse_lingbao();
            ctx.parse_role_xiulian();
            ctx.parse_pet_ctrl_skill();
            ctx.parse_pet_info();
            ctx.parse_rider_info();
            ctx.parse_clothes_info();
            ctx.parse_xiangrui_info();
            ctx.parse_rider_plan_list();
            ctx.parse_house_info();
            return ctx.result;
        },
        parse_basic_role_info: function() {
            var that = this;
            var ResUrl = this.resUrl;
            var EquipRequestTime = that.equipRequestTime;
            var ServerCurrentTime = that.serverCurrentTime;
            var get_role_icon = function(icon_id) {
                if (window.get_role_iconid) {
                    var role_type = window.get_role_iconid && get_role_iconid(icon_id);
                    return ResUrl + "/images/bigface/" + role_type + ".gif";
                }
                return '';
            };
            var school_name = SchoolNameInfo[this.raw_info["iSchool"]];
            if (!school_name) {
                school_name = "";
            }
            var marry_info = this.get_marry_info(this.raw_info["iMarry"]);
            var tongpao_info = this.get_tongpao_info(this.raw_info["iMarry2"]);
            var relation = "否";
            if (marry_info[0] === "未知" && tongpao_info[0] === "未知") {
                relation = "未知";
            } else if (marry_info[0] === "否" && tongpao_info[0] === "否") {
                relation = "否";
            } else {
                if (marry_info[0] === "是") {
                    relation = "已婚";
                } else if (tongpao_info[0] === "是") {
                    relation = "同袍";
                }
            }
            var community_info = "";
            if (this.raw_info["commu_name"] && this.raw_info["commu_gid"]) {
                community_info = this.raw_info["commu_name"] + "&nbsp;" + this.raw_info["commu_gid"];
            } else if (this.raw_info["commu_name"] == undefined || this.raw_info["commu_gid"] == undefined) {
                community_info = "未知";
            } else {
                community_info = "无";
            }
            var house_fangqi = "";
            var rHouseF = this.raw_info["house_fangqi"] || [];
            if (rHouseF.length) {
                for (var i = 0; i < rHouseF.length; i++) {
                    house_fangqi += rHouseF[i].desc;
                }
            } else {
                house_fangqi = "无";
            }
            var that = this;
            var get_goodness = function() {
                if (that.raw_info["iGoodness"] == null) {
                    return that.raw_info["iBadness"];
                } else {
                    return that.raw_info["iGoodness"];
                }
            };
            var sum_exp = "";
            if (this.raw_info["sum_exp"] === undefined) {
                sum_exp = "未知";
            } else if (this.raw_info["sum_exp"] == 0) {
                sum_exp = "<1亿";
            } else {
                sum_exp = this.raw_info["sum_exp"] + "亿";
            }
            var fly_status = "";
            if (this.raw_info["i3FlyLv"] && this.raw_info["i3FlyLv"] > 0) {
                fly_status = "化圣" + CHINESE_NUM_CONFIG[this.raw_info["i3FlyLv"]];
            } else {
                if (this.raw_info["iZhuanZhi"] >= 0) {
                    fly_status = ROLE_ZHUAN_ZHI_CONFIG[this.raw_info["iZhuanZhi"]];
                }
            }
            this.result["allow_pet_count"] = this.raw_info['iSumAmount'];
            var ach_info;
            if (this.raw_info.achmap) {
                if (this.raw_info.achmap["81732"]) {
                    ach_info = "已获得“一千亿经验”成就";
                } else if (this.raw_info.achmap["80017"]) {
                    ach_info = "已获得“经验狂人”成就";
                }
            }
            var role_info = {
                "sum_exp": sum_exp,
                "icon": get_role_icon(this.raw_info["iIcon"]),
                "iIcon": this.raw_info["iIcon"],
                "role_kind_name": this.parse_role_kind_name(this.raw_info["iIcon"]),
                "role_level": this.raw_info["iGrade"],
                "nickname": this.raw_info["cName"],
                "is_fei_sheng": this.raw_info["iZhuanZhi"] >= 1 ? "是" : "否",
                "fly_status": fly_status,
                "pride": this.raw_info["iPride"],
                "org": this.raw_info["cOrg"],
                "org_offer": this.raw_info["iOrgOffer"],
                "school": school_name,
                "school_offer": this.raw_info["iSchOffer"],
                "hp_max": this.raw_info["iHp_Max"],
                "mp_max": this.raw_info["iMp_Max"],
                "att_all": this.raw_info["iAtt_All"],
                "cor_all": this.raw_info["iCor_All"],
                "damage_all": this.raw_info["iDamage_All"],
                "mag_all": this.raw_info["iMag_All"],
                "def_all": this.raw_info["iDef_All"],
                "str_all": this.raw_info["iStr_All"],
                "dex_all": this.raw_info["iDex_All"],
                "res_all": this.raw_info["iRes_All"],
                "dod_all": this.raw_info["iDod_All"],
                "spe_all": this.raw_info["iSpe_All"],
                "mag_def_all": this.raw_info["iMagDef_All"],
                "point": this.raw_info["iPoint"],
                "cash": this.raw_info["iCash"],
                "saving": this.raw_info["iSaving"],
                "learn_cash": this.raw_info["iLearnCash"],
                "upexp": this.get_real_upexp(),
                "badness": get_goodness(),
                "goodness_sav": this.safe_attr(this.raw_info["igoodness_sav"]),
                "qian_neng_guo": this.raw_info["iNutsNum"],
                "is_married": marry_info[0],
                "partner_id": marry_info[1],
                "is_tongpao": tongpao_info[0],
                "community_info": community_info,
                "house_fangqi": house_fangqi,
                "fangwu_info": this.get_fangwu_info(relation, this.raw_info["rent_level"]),
                "fangwu_owner_info": this.get_fangwu_owner_info(),
                "tingyuan_info": this.get_tingyuan_info(relation, this.raw_info["outdoor_level"]),
                "muchang_info": this.get_muchang_info(relation, this.raw_info["farm_level"]),
                "qian_yuan_dan": this.get_qian_yuan_dan(),
                "is_du_jie": this.raw_info["iZhuanZhi"] == 2 ? "已完成" : "未完成",
                "caiguo": this.raw_info["iCGTotalAmount"],
                "body_caiguo": this.raw_info["iCGBodyAmount"],
                "box_caiguo": this.raw_info["iCGBoxAmount"],
                "chengjiu": this.safe_attr(this.raw_info["AchPointTotal"]),
                "xianyu": this.safe_attr(this.raw_info["xianyu"]),
                "energy": this.safe_attr(this.raw_info["energy"]),
                "add_point": this.safe_attr(this.raw_info["addPoint"]),
                "ji_yuan": this.safe_attr(this.raw_info["jiyuan"]),
                "changesch": this.get_change_school_list(this.raw_info["changesch"]),
                "propkept": this.get_prop_kept(this.raw_info["propKept"], this.raw_info["iGrade"]),
                "hero_score": this.safe_attr(this.raw_info["HeroScore"]),
                "sanjie_score": this.safe_attr(this.raw_info["datang_feat"]),
                "sword_score": this.safe_attr(this.raw_info["sword_score"]),
                "dup_score": this.safe_attr(this.raw_info["dup_score"]),
                "shenqi_score": this.safe_attr(this.raw_info["shenqi_score"]),
                "total_caiguo": this.safe_attr(this.raw_info["iCGTotalAmount"]),
                "shengsijie": this.get_sheng_si_jie(),
                "total_avatar": this.raw_info["total_avatar"],
                "total_horse": this.raw_info["total_horse"],
                "fa_shang": this.raw_info["iTotalMagDam_all"],
                "fa_fang": this.raw_info["iTotalMagDef_all"],
                "ach_info": ach_info,
                "qicai_score": this.raw_info["qicai_score"],
                "xianyu_score": this.raw_info["xianyu_score"]
            };
            if (this.raw_info["more_attr"] && this.raw_info["more_attr"]["attrs"]) {
                role_info['other_attr'] = {};
                for (var i = 0; i < this.raw_info["more_attr"]["attrs"].length; i++) {
                    var item = this.raw_info["more_attr"]["attrs"][i];
                    role_info['other_attr'][item.idx] = item.lv;
                }
            }
            role_info['is_gold_id'] = false;
            role_info['is_xyq_id'] = false;
            each(this.raw_info.idbid_desc || [], function(id) {
                if (id >= 85 && id <= 89) {
                    role_info['is_xyq_id'] = true;
                }
                if (id >= 5 && id <= 8)
                    role_info['is_gold_id'] = true;
            });
            if (role_info['is_xyq_id']) {
                role_info['is_niceid'] = '梦幻西游';
            } else if (role_info['is_gold_id']) {
                role_info['is_niceid'] = '土豪金';
            } else if (this.raw_info["bid"] == undefined) {
                role_info["is_niceid"] = "未知";
            } else {
                role_info["is_niceid"] = this.raw_info["bid"] ? "是" : "否";
            }
            if (this.raw_info["ori_race"] == undefined) {
                role_info["ori_race"] = this.get_race_by_school(this.raw_info["iSchool"]);
            } else {
                var race_name = RACE_INFO[this.raw_info["ori_race"]];
                if (this.raw_info["ori_race"] != this.raw_info["iRace"]) {
                    race_name = '<span style="color:#FFCC00">' + race_name + '</span>';
                }
                role_info["ori_race"] = race_name;
            }
            if (this.raw_info["iPcktPage"] == undefined) {
                var time1 = parseDatetime("2014-07-22 10:00:00");
                var time2 = parseDatetime("2014-07-29 10:00:00");
                var agent_time = parseDatetime(this.equipRequestTime);
                var cur_time = parseDatetime(this.serverCurrentTime);
                var server_id = this.serverId;
                if (server_id === "155" && agent_time > time1) {
                    role_info["package_num"] = "未知";
                } else if ((server_id === "462" || server_id === "2") && agent_time > time2) {
                    role_info["package_num"] = "未知";
                } else {
                    role_info["package_num"] = "无";
                }
            } else {
                var package_num = parseInt(this.raw_info["iPcktPage"]);
                if (package_num > 0 && package_num <= 3) {
                    role_info["package_num"] = package_num;
                } else if (package_num == 0) {
                    role_info["package_num"] = "无";
                } else {
                    role_info["package_num"] = "未知";
                }
            }
            this.result["basic_info"] = role_info;
        },
        parse_role_skill: function() {
            var ResUrl = this.resUrl;
            var life_skill = [];
            var school_skill = [];
            var ju_qing_skill = [];
            var conf = this.conf.skill;
            var that = this;
            var get_skill_icon = function(skill_id) {
                var skill_img = that.make_img_name(skill_id) + ".gif";
                return ResUrl + "/images/role_skills/" + skill_img;
            };
            var raw_skill_info = this.raw_info["all_skills"];
            this.result["yu_shou_shu"] = this.raw_info["all_skills"]["221"];
            for (var skill in raw_skill_info) {
                var info = {
                    "skill_id": skill,
                    "skill_grade": raw_skill_info[skill],
                    "skill_pos": 0
                };
                info["skill_icon"] = get_skill_icon(skill);
                info["icon"] = info["skill_icon"];
                if (conf["life_skill"][skill]) {
                    info["name"] = info["skill_name"] = conf["life_skill"][skill];
                    if (window.CBG_GAME_CONFIG.life_skill_desc && window.CBG_GAME_CONFIG.life_skill_desc[skill]) {
                        var skillConfig = window.CBG_GAME_CONFIG.life_skill_desc[skill];
                        desc = skillConfig.desc || '';
                        info["desc"] = skillConfig.desc || '';
                    }
                    life_skill.push(info);
                } else if (conf["school_skill"][skill]) {
                    info["name"] = info["skill_name"] = conf["school_skill"][skill]["name"];
                    info["skill_pos"] = conf["school_skill"][skill]["pos"]
                    if (window.CBG_GAME_CONFIG.school_skill_desc && window.CBG_GAME_CONFIG.school_skill_desc[skill]) {
                        var skillConfig = window.CBG_GAME_CONFIG.school_skill_desc[skill];
                        info["desc"] = skillConfig.desc || '';
                    }
                    school_skill.push(info);
                } else if (conf["ju_qing_skill"][skill]) {
                    info["name"] = info["skill_name"] = conf["ju_qing_skill"][skill];
                    if (window.CBG_GAME_CONFIG.ju_qing_skill_desc && window.CBG_GAME_CONFIG.ju_qing_skill_desc[skill]) {
                        var skillConfig = window.CBG_GAME_CONFIG.ju_qing_skill_desc[skill];
                        info["desc"] = skillConfig.desc || '';
                    }
                    if (skill === '170' || skill === '197') {
                        if (info.skill_grade > 0) {
                            info.skill_grade--;
                            ju_qing_skill.push(info);
                        }
                    } else {
                        ju_qing_skill.push(info);
                    }
                }
            }
            var shuliandu = {
                "smith_skill": this.safe_attr(this.raw_info["iSmithski"]),
                "sew_skill": this.safe_attr(this.raw_info["iSewski"])
            }
            var result = {
                "life_skill": life_skill,
                "school_skill": school_skill,
                "ju_qing_skill": ju_qing_skill,
                "left_skill_point": this.raw_info["iSkiPoint"],
                "shuliandu": shuliandu
            };
            this.result["role_skill"] = result;
        },
        parse_equip_info: function() {
            var ctx = this;
            var ResUrl = this.resUrl;
            var all_equips = this.raw_info["AllEquip"];
            var get_equip_small_icon = function(itype) {
                return ResUrl + "/images/equip/small/" + itype + ".gif";
            };
            var get_equip_big_icon = function(itype) {
                return ResUrl + "/images/big/" + itype + ".gif";
            };
            var parse_info = function(equip, pos) {
                var iType = parseInt(equip["iType"]);
                var equip_info = this.conf.get_equip_info(iType) || {};
                return {
                    "pos": parseInt(pos),
                    "type": iType,
                    "equip_sn": equip["equip_sn"],
                    "name": equip_info["name"],
                    "desc": equip["cDesc"],
                    "lock_type": this.get_lock_types(equip),
                    "static_desc": htmlEncode(equip_info["desc"]).replace(/#R/g, "<br />"),
                    "small_icon": get_equip_small_icon(iType),
                    "big_icon": get_equip_big_icon(iType),
                    "can_split_agent": equip["can_split_agent"] === 1
                };
            }
            var using_equips = [];
            var not_using_equips = [];
            var split_equips = [];
            for (var pos in all_equips) {
                var equip = all_equips[pos] || {};
                var info = parse_info.call(ctx, equip, pos);
                var pos = parseInt(pos);
                if (info['can_split_agent']) {
                    info['is_support_inquiry'] = ctx.is_support_inquiry;
                    info['serverid'] = ctx.serverId;
                    info['game_ordersn'] = ctx.game_ordersn;
                    info['is_my_equip'] = ctx.is_my_equip;
                    info['is_agent_storage_full'] = ctx.is_my_equip && ctx.inquiry_support_info.daoju === false;
                }
                if (equip.is_split_sale) {
                    var eid = equip.eid;
                    info['eid'] = eid;
                    var split_equip_info = ctx.split_equip_dict && ctx.split_equip_dict[eid];
                    if (split_equip_info) {
                        if (split_equip_info.is_time_lock) {
                            info.lock_type = [9];
                        }
                        info['split_equip_info'] = split_equip_info;
                    }
                    split_equips.push(info);
                } else if ((pos >= 1 && pos <= 6) || [187, 188, 189, 190, 191].contains(pos)) {
                    using_equips.push(info);
                } else {
                    not_using_equips.push(info);
                }
            }
            this.result["using_equips"] = using_equips;
            this.result["not_using_equips"] = not_using_equips;
            this.result["split_equips"] = split_equips;
        },
        parse_fabao_info: function() {
            var ResUrl = this.resUrl;
            var all_fabao = this.raw_info["fabao"];
            var get_fabao_icon = function(itype) {
                return ResUrl + "/images/fabao_new2/" + itype + ".png";
            }
            var using_fabao = [];
            var nousing_fabao = [];
            for (var pos in all_fabao) {
                var fabao_info = this.conf.get_fabao_info(all_fabao[pos]["iType"]);
                var info = {
                    "pos": parseInt(pos),
                    "type": all_fabao[pos]["iType"],
                    "name": fabao_info["name"],
                    "desc": all_fabao[pos]["cDesc"],
                    "icon": get_fabao_icon(all_fabao[pos]["iType"]),
                    "static_desc": fabao_info["desc"]
                };
                if (info.desc) {
                    info.desc = info.desc.replace(/^0/, '');
                }
                if (pos >= 1 && pos <= 4) {
                    using_fabao.push(info);
                } else {
                    nousing_fabao.push(info);
                }
            }
            nousing_fabao.sort(function(a, b) {
                return a.pos - b.pos;
            });
            if (this.raw_info['unused_fabao_sum'] != void (0) && this.raw_info['fabao_storage_size'] != void (0)) {
                this.result['unused_fabao_sum'] = this.raw_info['unused_fabao_sum'];
                this.result['fabao_storage_size'] = this.raw_info['fabao_storage_size'];
            }
            this.result["using_fabao"] = using_fabao;
            this.result["nousing_fabao"] = nousing_fabao;
        },
        handleShenqi: function(shenqi, shenqiID) {
            var ResUrl = this.resUrl;
            var components = shenqi.components;
            var attributes = shenqi.attributes;
            var that = this;
            var shenqi_yellow = this.raw_info["shenqi_yellow"];
            var get_shenqi_icon = function(id) {
                return ResUrl + "/images/shenqi/" + id + "0000.png";
            }
            var shenqi_info = this.conf.get_shenqi_info(shenqiID);
            var attributesText = '';
            for (var i = 0, len = attributes.length; i < len; i++) {
                if (attributes[i].disable == 0) {
                    attributesText += '#G' + attributes[i].attr + '#r';
                }
            }
            if (shenqi_yellow) {
                shenqi_yellow = shenqi_yellow.replace(/^0/, '');
            }
            for (var k = 0, len = components.length; k < len; k++) {
                var buweiPicID = shenqiID > 6214 ? shenqiID - 15 : shenqiID;
                var buweiPic = ResUrl + "/images/shenqi/components/" + buweiPicID + "/s" + (k + 1) + "0000.png";
                var unlock = components[k].unlock;
                if (unlock !== 1) {
                    buweiPic = ResUrl + "/images/shenqi/buweiLock.png"
                }
                components[k]["buweiPic"] = buweiPic;
                var wuxing = components[k].wuxing;
                for (var j = 0; j < wuxing.length; j++) {
                    var status = wuxing[j].status;
                    if (status !== 1) {
                        wuxing[j].wuxingText = "";
                        wuxing[j].lingxiPic = ResUrl + "/images/shenqi/lingxiLock.png";
                        continue;
                    }
                    var wuxingshi_level = wuxing[j].wuxingshi_level;
                    var wuxingID = wuxing[j].id;
                    var wuxingshi_affix = wuxing[j].wuxingshi_affix;
                    wuxing[j].wuxing_affix_text = that.conf.wuxing_affix_info[wuxingshi_affix];
                    switch (wuxingID) {
                    case 1:
                        wuxing[j].wuxingText = "金";
                        break;
                    case 2:
                        wuxing[j].wuxingText = "木";
                        break;
                    case 4:
                        wuxing[j].wuxingText = "土";
                        break;
                    case 8:
                        wuxing[j].wuxingText = " 水";
                        break;
                    case 16:
                        wuxing[j].wuxingText = " 火";
                        break;
                    }
                    if (wuxingshi_level == 1) {
                        wuxing[j].lingxiPic = ResUrl + "/images/shenqi/69020000.png";
                    } else if (wuxingshi_level == 2) {
                        wuxing[j].lingxiPic = ResUrl + "/images/shenqi/69030000.png";
                    } else if (wuxingshi_level == 3) {
                        wuxing[j].lingxiPic = ResUrl + "/images/shenqi/69040000.png";
                    } else {
                        wuxing[j].lingxiPic = ResUrl + "/images/shenqi/lingxiEmpty.png";
                    }
                }
            }
            var info = {
                "name": shenqi_info["name"],
                "icon": get_shenqi_icon(shenqiID),
                "static_desc": shenqi_info["desc"],
                "desc": shenqi_yellow + attributesText
            }
            return {
                info: info,
                components: components
            }
        },
        parse_shenqi_info: function() {
            if (!this.raw_info["shenqi"] || !this.raw_info["shenqi"].id) {
                this.result["shenqi"] = false;
                return false;
            }
            var shenqi = this.raw_info["shenqi"];
            var shenqiID = shenqi.id;
            var isNew = shenqi.suit ? true : false;
            if (isNew) {
                var components = {};
                var shenqinInfo = {
                    isNew: true
                };
                for (var i = 0; i < shenqi.suit.length; i++) {
                    var item = shenqi.suit[i];
                    var data = this.handleShenqi(item, shenqiID);
                    var shenqiKey = 'shenqi' + (i + 1);
                    if (!!item.actived) {
                        shenqinInfo = Object.merge(shenqinInfo, data.info);
                    }
                    components[shenqiKey] = {
                        actived: item.actived,
                        components: data.components
                    }
                }
                this.result["shenqi"] = shenqinInfo;
                this.result["shenqi_components"] = components;
            } else {
                var data = this.handleShenqi(shenqi, shenqiID);
                this.result["shenqi"] = data.info;
                this.result["shenqi_components"] = {
                    shenqi1: {
                        actived: true,
                        components: data.components
                    }
                }
            }
        },
        parse_huoshenta: function() {
            if (this.raw_info["fyj"] === 1) {
                this.result.huoshenta = {
                    icon: ResUrl + "/images/fabao_new2/55238.png",
                    name: '获神塔',
                    desc: this.raw_info["fyj_desc"]
                }
            }
        },
        parse_lingbao: function() {
            var all_lingbao = this.raw_info["lingbao"];
            var using_lingbao = [];
            var nousing_lingbao = [];
            if (all_lingbao) {
                var get_lingbao_icon = function(itype) {
                    return ResUrl + "/images/lingbao/" + itype + ".png";
                }
                for (var pos in all_lingbao) {
                    if (all_lingbao.hasOwnProperty(pos)) {
                        var lingbao_info = this.conf.get_lingbao_info(all_lingbao[pos]["iType"]);
                        var info = {
                            "pos": parseInt(pos),
                            "type": all_lingbao[pos]["iType"],
                            "name": lingbao_info["name"],
                            "desc": all_lingbao[pos]["cDesc"],
                            "icon": get_lingbao_icon(all_lingbao[pos]["iType"]),
                            "static_desc": lingbao_info["desc"]
                        };
                        if (pos == 1 || pos == 2) {
                            using_lingbao.push(info);
                        } else {
                            nousing_lingbao.push(info);
                        }
                    }
                }
            }
            this.result['using_lingbao'] = using_lingbao;
            this.result['nousing_lingbao'] = nousing_lingbao;
        },
        parse_role_xiulian: function() {
            var result = [];
            result.push({
                "name": "攻击修炼",
                "info": this.raw_info["iExptSki1"] + "/" + this.safe_attr(this.raw_info["iMaxExpt1"])
            });
            result.push({
                "name": "防御修炼",
                "info": this.raw_info["iExptSki2"] + "/" + this.safe_attr(this.raw_info["iMaxExpt2"])
            });
            result.push({
                "name": "法术修炼",
                "info": this.raw_info["iExptSki3"] + "/" + this.safe_attr(this.raw_info["iMaxExpt3"])
            });
            result.push({
                "name": "抗法修炼",
                "info": this.raw_info["iExptSki4"] + "/" + this.safe_attr(this.raw_info["iMaxExpt4"])
            });
            result.push({
                "name": "猎术修炼",
                "info": this.raw_info["iExptSki5"]
            });
            this.result["role_xiulian"] = result;
        },
        parse_pet_ctrl_skill: function() {
            var result = [];
            result.push({
                "name": "攻击控制力",
                "grade": this.raw_info["iBeastSki1"]
            });
            result.push({
                "name": "防御控制力",
                "grade": this.raw_info["iBeastSki2"]
            });
            result.push({
                "name": "法术控制力",
                "grade": this.raw_info["iBeastSki3"]
            });
            result.push({
                "name": "抗法控制力",
                "grade": this.raw_info["iBeastSki4"]
            });
            this.result["pet_ctrl_skill"] = result;
        },
        parse_pet_info: function() {
            var ctx = this;
            var ResUrl = this.resUrl;
            var all_pets = this.raw_info["AllSummon"];
            if (!all_pets) {
                all_pets = [];
            }
            var that = this;
            var get_pet_icon = function(itype) {
                return ResUrl + "/images/pets/small/" + itype + ".gif";
            }
            var wuxing_info = {
                0: "未知",
                1: "金",
                2: "木",
                4: "土",
                8: "水",
                16: "火"
            };
            var max_equip_num = 3;
            var get_pet_skill_icon = function(skill_id) {
                return ResUrl + "/images/pet_child_skill/" + that.make_img_name(skill_id) + ".gif";
            };
            var get_pet_equip_icon = function(typeid) {
                return ResUrl + "/images/equip/small/" + typeid + ".gif";
            };
            var get_pet_shipin_icon = function(typeid) {
                return ResUrl + "/images/pet_shipin/small/" + typeid + ".png";
            };
            var get_child_icon = function(child_id) {
                return ResUrl + "/images/child_icon/" + that.make_img_name(child_id) + ".gif";
            };
            var get_child_skill_icon = function(skill_id) {
                return ResUrl + "/images/pet_child_skill/" + that.make_img_name(skill_id) + ".gif";
            };
            var get_pet_name = function(itype) {
                return that.conf.pet_info[itype];
            };
            var get_child_name = function(itype) {
                return that.conf.child_info[itype];
            };
            var get_ending_name = function(ending, itype) {
                if (that.conf.ending_info[ending]instanceof Array) {
                    return that.conf.girl_child_info[itype] ? that.conf.ending_info[ending][1] : that.conf.ending_info[ending][0];
                }
                return that.conf.ending_info[ending];
            };
            var get_neidan_icon = function(neidan_id) {
                return ResUrl + "/images/neidan/" + neidan_id + '.jpg';
            };
            var _this = this;
            var get_yuanxiao = function(input_value) {
                if (!input_value) {
                    return that.safe_attr(input_value);
                }
                var agent_time = parseDatetime(_this.equipRequestTime);
                var cur_time = parseDatetime(_this.serverCurrentTime);
                var fresh_time = new Date(cur_time.getFullYear(),0,1);
                if (agent_time > fresh_time) {
                    return input_value;
                } else {
                    return 0;
                }
            };
            var get_lianshou = function(input_value) {
                if (!input_value) {
                    return that.safe_attr(input_value);
                }
                var agent_time = parseDatetime(_this.equipRequestTime);
                var cur_time = parseDatetime(_this.serverCurrentTime);
                var fresh_time = new Date(cur_time.getFullYear(),8,1);
                if (cur_time < fresh_time) {
                    fresh_time.setFullYear(fresh_time.getFullYear() - 1);
                }
                if (agent_time > fresh_time) {
                    return input_value;
                } else {
                    return 0;
                }
            };
            var findCorrespondingValue = function(arr, targetId) {
                for (var i = 0; i < arr.length; i++) {
                    var objCorresponding = arr[i];
                    if (objCorresponding.hasOwnProperty(targetId)) {
                        return objCorresponding[targetId];
                    }
                }
                return null;
            }
            var get_pet_info = function(pet, is_child) {
                var get_icon = get_pet_icon;
                var get_skill_icon = get_pet_skill_icon;
                var get_name = get_pet_name;
                var info = {};
                var iType = pet["iType"];
                if (is_child && _this.gConf.child_icon_mapping && _this.gConf.child_icon_mapping[iType]) {
                    iType = _this.gConf.child_icon_mapping[iType];
                }
                if (is_child) {
                    if (pet.hasOwnProperty('isnew') && pet.hasOwnProperty('isnew') == 1) {
                        info["isnew"] = pet["isnew"];
                        info["iMagDam_all"] = pet["iMagDam_all"];
                        info["school"] = pet["school"] == 0 ? '无' : SchoolNameInfo[pet["school"]];
                        info["ending"] = get_ending_name(pet["ending"], iType);
                        info["gg"] = pet["gg"];
                        info["zl"] = pet["zl"];
                        info["wl"] = pet["wl"];
                        info["dl"] = pet["dl"];
                        info["nl"] = pet["nl"];
                        info["lm"] = pet["lm"];
                    }
                    get_icon = get_child_icon;
                    get_skill_icon = get_child_skill_icon;
                    get_name = get_child_name;
                }
                info["type_id"] = iType;
                info["equip_sn"] = pet["equip_sn"];
                info["pet_grade"] = pet["iGrade"];
                info["is_baobao"] = pet["iBaobao"] == 0 ? "否" : "是";
                info["icon"] = get_icon(iType);
                info["pet_name"] = get_name(iType);
                info["kind"] = get_name(iType);
                info["blood"] = pet["iHp"];
                info["magic"] = pet["iMp"];
                info["blood_max"] = pet["iHp_max"];
                info["magic_max"] = pet["iMp_max"];
                info["attack"] = pet["iAtt_all"];
                info["defence"] = pet["iDef_All"];
                info["speed"] = pet["iDex_All"];
                info["ling_li"] = pet["iMagDef_all"];
                info["iMagDam"] = pet["iMagDam"];
                info["iMagDef"] = pet["iMagDef"];
                info["lifetime"] = pet["life"] >= 65432 ? "永生" : pet["life"];
                info["ti_zhi"] = pet["iCor_all"];
                info["fa_li"] = pet["iMag_all"];
                info["li_liang"] = pet["iStr_all"];
                info["nai_li"] = pet["iRes_all"];
                info["min_jie"] = pet["iSpe_all"];
                info["qian_neng"] = pet["iPoint"];
                info["cheng_zhang"] = pet["grow"] / 1000;
                info["wu_xing"] = wuxing_info[pet["iAtt_F"]];
                info["gong_ji_zz"] = pet["att"];
                info["fang_yu_zz"] = pet["def"];
                info["ti_li_zz"] = pet["hp"];
                info["fa_li_zz"] = pet["mp"];
                info["su_du_zz"] = pet["spe"];
                info["duo_shan_zz"] = pet["dod"];
                info["used_yuanxiao"] = get_yuanxiao(pet["yuanxiao"]);
                info["used_qianjinlu"] = that.safe_attr(pet["qianjinlu"]);
                info["used_lianshou"] = get_lianshou(pet["lianshou"]);
                info["child_sixwx"] = pet["child_sixwx"];
                info["is_child"] = is_child;
                info["color"] = pet["iColor"];
                info['summon_color'] = pet['summon_color'];
                info['can_split_agent'] = pet["can_split_agent"] == 1;
                if (info['can_split_agent']) {
                    info['is_support_inquiry'] = ctx.is_support_inquiry;
                    info['game_ordersn'] = ctx.game_ordersn;
                    info['serverid'] = ctx.serverId;
                    info['is_my_equip'] = ctx.is_my_equip;
                    info['is_agent_storage_full'] = ctx.is_my_equip && ctx.inquiry_support_info.pet === false;
                }
                var jjExtraAdd = pet["jj_extra_add"];
                if (jjExtraAdd) {
                    info["ti_zhi_add"] = jjExtraAdd["iCor"];
                    info["fa_li_add"] = jjExtraAdd["iMag"];
                    info["li_liang_add"] = jjExtraAdd["iStr"];
                    info["nai_li_add"] = jjExtraAdd["iRes"];
                    info["min_jie_add"] = jjExtraAdd["iSpe"];
                    info["ti_zhi"] -= info["ti_zhi_add"];
                    info["fa_li"] -= info["fa_li_add"];
                    info["li_liang"] -= info["li_liang_add"];
                    info["nai_li"] -= info["nai_li_add"];
                    info["min_jie"] -= info["min_jie_add"];
                }
                info['PET_WUXING_INFO'] = window.PET_WUXING_INFO || {};
                if (pet['core_close'] || pet['core_close'] == 0) {
                    info['core_close'] = pet['core_close'] == 0 ? "已开启" : "已关闭";
                }
                info["genius"] = parseInt(pet["iGenius"] || 0);
                if (info["genius"] != 0) {
                    var desc = '';
                    var name = '';
                    if (window.CBG_GAME_CONFIG.pet_skill_desc && window.CBG_GAME_CONFIG.pet_skill_desc[pet["iGenius"]]) {
                        var skillConfig = window.CBG_GAME_CONFIG.pet_skill_desc[pet["iGenius"]];
                        desc = skillConfig.desc || '';
                        name = skillConfig.name || '';
                    }
                    info["genius_skill"] = {
                        "icon": get_skill_icon(pet["iGenius"]),
                        "skill_type": pet["iGenius"],
                        "name": name,
                        "desc": desc
                    };
                } else {
                    info["genius_skill"] = {};
                }
                info["skill_list"] = [];
                var all_skills = pet["all_skills"];
                if (all_skills) {
                    var all_skill_str = [];
                    for (var typeid in all_skills) {
                        all_skill_str.push('' + typeid);
                    }
                    window.xs_sort_pet_skills && xs_sort_pet_skills(info["type_id"], all_skill_str);
                    for (var i = 0, max = all_skill_str.length; i < max; i++) {
                        var typeid = all_skill_str[i];
                        if (parseInt(typeid) == info["genius"]) {
                            continue;
                        }
                        var skillParam = {
                            "icon": get_skill_icon(typeid),
                            "skill_type": typeid,
                            "level": all_skills[typeid]
                        }
                        function isSuperSkill(id) {
                            var result = false;
                            if (CBG_GAME_CONFIG && CBG_GAME_CONFIG.pet_web_super_skill_options) {
                                for (var i = 0; i < CBG_GAME_CONFIG.pet_web_super_skill_options.length; i++) {
                                    var item = CBG_GAME_CONFIG.pet_web_super_skill_options[i];
                                    if (item[0] == id) {
                                        result = true;
                                        break;
                                    }
                                }
                            }
                            return result;
                        }
                        if (isSuperSkill(typeid)) {
                            skillParam.isSuperSkill = true;
                        }
                        if (window.CBG_GAME_CONFIG.pet_skill_desc && window.CBG_GAME_CONFIG.pet_skill_desc[typeid]) {
                            var skillConfig = window.CBG_GAME_CONFIG.pet_skill_desc[typeid];
                            skillParam.name = skillConfig.name || '';
                            skillParam.desc = skillConfig.desc || '';
                            skillParam.isPetSkill = true;
                        }
                        if (pet['EvolSkill'] && window.CBG_GAME_CONFIG.pet_skill_high_to_other_level_mapping) {
                            var hashEvolSkllAll = [];
                            var hashBothEvolSkllAll = [];
                            var hashLowEvolSkllAll = [];
                            var cifu = pet['EvolSkill'].split("|").map(Number);
                            cifu.forEach(function(ids) {
                                if (!ids || ids == "0") {
                                    return;
                                }
                                var attrdataSkillMap = window.CBG_GAME_CONFIG.pet_skill_high_to_other_level_mapping[ids] || {};
                                if (attrdataSkillMap.high_skill) {
                                    hashEvolSkllAll.push(attrdataSkillMap.high_skill);
                                }
                                if (attrdataSkillMap.low_skill) {
                                    hashEvolSkllAll.push(attrdataSkillMap.low_skill);
                                    var attrdataSkillMapLowSkill = attrdataSkillMap.low_skill
                                    var attrdataSkillMapHighSkill = attrdataSkillMap.high_skill
                                    var attrdataSkillObj = {};
                                    attrdataSkillObj[attrdataSkillMapLowSkill] = attrdataSkillMapHighSkill;
                                    hashBothEvolSkllAll.push(attrdataSkillObj);
                                    hashLowEvolSkllAll.push(attrdataSkillMap.low_skill);
                                }
                            });
                            if (hashEvolSkllAll.contains(Number(typeid))) {
                                if (hashLowEvolSkllAll.contains(Number(typeid)) && all_skill_str.contains(String(findCorrespondingValue(hashBothEvolSkllAll, typeid)))) {
                                    skillParam.hashEvol = false;
                                } else {
                                    skillParam.hashEvol = true;
                                }
                            }
                        }
                        info["skill_list"].push(skillParam);
                    }
                    info['all_skill'] = all_skill_str.join('|');
                } else {
                    info['all_skill'] = '';
                }
                info['all_skills'] = info['all_skill'].split('|');
                if (pet['EvolSkill'] && window.CBG_GAME_CONFIG.pet_skill_high_to_other_level_mapping) {
                    info["evol_skill_list"] = [];
                    var cifu = pet['EvolSkill'].split("|").map(Number);
                    var cifuObj = {};
                    cifu.forEach(function(number) {
                        cifuObj[number] = 1;
                    });
                    var evol_skills = cifuObj;
                    if (evol_skills) {
                        var evol_skill_str = [];
                        for (var typeid in evol_skills) {
                            evol_skill_str.push('' + typeid);
                        }
                        for (var i = 0, max = evol_skill_str.length; i < max; i++) {
                            var typeid = evol_skill_str[i];
                            var evol_skill_hash = window.CBG_GAME_CONFIG.pet_skill_high_to_other_level_mapping[typeid];
                            var evol_skill_item = {
                                "icon": get_skill_icon(typeid),
                                "skill_type": typeid,
                                "level": evol_skills[typeid],
                                "evol_type": typeid
                            }
                            if (window.CBG_GAME_CONFIG.pet_skill_desc && window.CBG_GAME_CONFIG.pet_skill_desc[typeid]) {
                                var skillConfig = window.CBG_GAME_CONFIG.pet_skill_desc[typeid];
                                evol_skill_item.name = skillConfig.name || '';
                                evol_skill_item.desc = skillConfig.desc || '';
                                evol_skill_item.isPetSkill = true;
                            }
                            if (info['all_skills']) {
                                var isHighSkill = info['all_skills'].contains(String(evol_skill_hash.high_skill));
                                var isLowSkill = info['all_skills'].contains(String(evol_skill_hash.low_skill));
                                if (isHighSkill || isLowSkill) {
                                    evol_skill_item.hlightLight = true;
                                    if (!info['all_skills'].contains(String(evol_skill_hash.high_skill))) {
                                        evol_skill_item.icon = get_skill_icon(String(evol_skill_hash.low_skill));
                                        evol_skill_item.evol_type = evol_skill_hash.low_skill;
                                    }
                                    if (isHighSkill) {
                                        evol_skill_item.name = (evol_skill_hash.name || '') + '（进化后获得）';
                                        if (window.CBG_GAME_CONFIG.pet_skill_desc && window.CBG_GAME_CONFIG.pet_skill_desc[String(evol_skill_hash.super_skill)]) {
                                            var skillConfig = window.CBG_GAME_CONFIG.pet_skill_desc[String(evol_skill_hash.super_skill)];
                                            evol_skill_item.desc = skillConfig.desc || ''
                                        }
                                        evol_skill_item.cifuIcon = get_skill_icon(evol_skill_hash.super_skill);
                                    } else {
                                        evol_skill_item.heightCifuIcon = get_skill_icon(evol_skill_hash.high_skill);
                                        evol_skill_item.name += '（进化后获得）';
                                    }
                                } else {
                                    evol_skill_item.name = (evol_skill_hash.name || '') + '（进化后获得）';
                                    evol_skill_item.cifuIcon = get_skill_icon(evol_skill_hash.super_skill);
                                    if (window.CBG_GAME_CONFIG.pet_skill_desc && window.CBG_GAME_CONFIG.pet_skill_desc[String(evol_skill_hash.super_skill)]) {
                                        var skillConfig = window.CBG_GAME_CONFIG.pet_skill_desc[String(evol_skill_hash.super_skill)];
                                        evol_skill_item.desc = skillConfig.desc || ''
                                    }
                                    evol_skill_item.hlightLight = false;
                                }
                            }
                            info["evol_skill_list"].push(evol_skill_item);
                        }
                        info['evol_skill'] = evol_skill_str.join('|');
                    } else {
                        info['evol_skill'] = '';
                    }
                    info['evol_skills'] = info['evol_skill'].split('|');
                }
                info["equip_list"] = [];
                for (var i = 0; i < max_equip_num; i++) {
                    var item = pet["summon_equip" + (i + 1)];
                    if (item) {
                        var equip_name_info = that.conf.get_equip_info(item["iType"]);
                        info["equip_list"].push({
                            "name": equip_name_info["name"],
                            "icon": get_pet_equip_icon(item["iType"]),
                            "type": item["iType"],
                            "desc": item["cDesc"],
                            "lock_type": _this.get_lock_types(item),
                            "static_desc": equip_name_info["desc"].replace(/#R/g, "<br />")
                        });
                    } else {
                        info["equip_list"].push(null);
                    }
                }
                info["shipin_list"] = [];
                if (pet.summon_equip4_type) {
                    info["shipin_list"].push({
                        "name": that.conf.pet_shipin_info[pet.summon_equip4_type],
                        "icon": get_pet_shipin_icon(pet.summon_equip4_type),
                        "type": pet.summon_equip4_type,
                        "desc": pet.summon_equip4_desc
                    });
                }
                info["empty_skill_img"] = ResUrl + "/images/role_skills/empty_skill.gif";
                info["neidan"] = []
                if (pet["summon_core"] != undefined) {
                    for (var p in pet["summon_core"]) {
                        var p_core = pet["summon_core"][p];
                        var desc = '';
                        if (window.CBG_GAME_CONFIG.neidan_desc && window.CBG_GAME_CONFIG.neidan_desc[p]) {
                            var skillConfig = window.CBG_GAME_CONFIG.neidan_desc[p];
                            desc = skillConfig.desc || '';
                        }
                        info["neidan"].push({
                            "name": that.safe_attr(PetNeidanInfo[p]),
                            "icon": get_neidan_icon(p),
                            "level": p_core[0],
                            "desc": desc,
                            "isNeiDan": true
                        });
                    }
                }
                info["jinjie"] = dict_get(pet, "jinjie", {});
                info["lock_type"] = _this.get_lock_types(pet);
                if (pet.csavezz) {
                    get_pet_ext_zz(info, {
                        attrs: 'gong_ji_ext,fang_yu_ext,su_du_ext,duo_shan_ext,ti_li_ext,fa_li_ext',
                        total_attrs: 'gong_ji_zz,fang_yu_zz,su_du_zz,duo_shan_zz,ti_li_zz,fa_li_zz',
                        csavezz: pet.csavezz,
                        carrygradezz: pet.carrygradezz,
                        lastchecksubzz: pet.lastchecksubzz,
                        pet_id: info.type_id,
                        is_super_sum: pet.is_super_sum
                    });
                }
                if (pet.avt_list && pet.avt_list.length) {
                    var avtList = pet['avt_list'];
                    var avt_list_format = [];
                    for (var i = 0; i < avtList.length; i++) {
                        var item = avtList[i];
                        var type = item.type;
                        var conf = window.CBG_GAME_CONFIG.pet_jinyi || {};
                        if (conf[type]) {
                            item.name = conf[type].name;
                        }
                        if (item.in_use) {
                            var sumavt_propsk = pet['sumavt_propsk'];
                            item.sumavt_propsk = (window.CBG_GAME_CONFIG.sumavt_propsk || {})[sumavt_propsk] ? (window.CBG_GAME_CONFIG.sumavt_propsk || {})[sumavt_propsk].label : '';
                        }
                        avt_list_format.push(item);
                    }
                    var current_on_avt = avt_list_format.filter(function(item) {
                        return !!item.in_use;
                    });
                    pet['avt_list_format'] = avt_list_format;
                    pet['current_on_avt'] = current_on_avt[0];
                }
                info['other'] = pet;
                return info;
            }
            var pet_info = [];
            var split_pets = [];
            for (var i = 0; i < all_pets.length; i++) {
                var petItem = all_pets[i];
                var info = get_pet_info(petItem);
                if (petItem.is_split_sale) {
                    var eid = petItem.eid;
                    info['eid'] = eid;
                    var split_pet_info = _this.split_equip_dict && _this.split_equip_dict[eid];
                    if (split_pet_info) {
                        if (split_pet_info.is_time_lock && !info.lock_type.length) {
                            info['lock_type'] = [9];
                        }
                        info['split_pet_info'] = split_pet_info;
                    }
                    split_pets.push(info);
                } else {
                    pet_info.push(info);
                }
            }
            this.result["pet_info"] = pet_info;
            this.result["split_pets"] = split_pets;
            if (this.raw_info["child"] && this.raw_info["child"]["iType"]) {
                this.result["child_info"] = [get_pet_info(this.raw_info["child"], true)];
            } else {
                this.result["child_info"] = [];
            }
            if (this.raw_info["child2"] && this.raw_info["child2"]["iType"]) {
                this.result["child_info"].push(get_pet_info(this.raw_info["child2"], true));
            }
            this.result["special_pet_info"] = this.raw_info["pet"]
        },
        parse_rider_info: function() {
            var ResUrl = this.resUrl;
            var rider_name_info = this.conf.rider_info;
            var get_rider_icon = function(itype) {
                return ResUrl + "/images/riders/" + itype + ".gif";
            }
            var that = this;
            var get_skill_icon = function(typeid) {
                return ResUrl + "/images/rider_skill/" + that.make_img_name(typeid) + ".gif";
            };
            var all_rider = this.raw_info["AllRider"];
            if (!all_rider) {
                all_rider = {};
            }
            var result = [];
            for (var rider in all_rider) {
                var rider_info = this.raw_info["AllRider"][rider];
                var info = {
                    "type": rider_info["iType"],
                    "grade": rider_info["iGrade"],
                    "grow": rider_info["iGrow"] / 100,
                    "exgrow": rider_info["exgrow"] ? (rider_info["exgrow"] / 10000).toFixed(4) : (rider_info["iGrow"] / 100),
                    "ti_zhi": rider_info["iCor"],
                    "magic": rider_info["iMag"],
                    "li_liang": rider_info["iStr"],
                    "nai_li": rider_info["iRes"],
                    "min_jie": rider_info["iSpe"],
                    "qian_neng": rider_info["iPoint"],
                    "icon": get_rider_icon(rider_info["iType"]),
                    "type_name": safe_attr(rider_name_info[rider_info["iType"]]),
                    "mattrib": rider_info["mattrib"] ? rider_info["mattrib"] : "未选择",
                    "empty_skill_icon": this.get_empty_skill_icon()
                };
                info["all_skills"] = [];
                var all_skills = rider_info["all_skills"];
                for (var typeid in all_skills) {
                    var desc = '';
                    var name = ''
                    var grade = all_skills[typeid];
                    if (window.CBG_GAME_CONFIG.zuoqi_skill_desc && window.CBG_GAME_CONFIG.zuoqi_skill_desc[typeid]) {
                        var skillConfig = window.CBG_GAME_CONFIG.zuoqi_skill_desc[typeid];
                        var descName = "lv" + grade + "_desc";
                        desc = skillConfig[descName] || '';
                        name = skillConfig.name || '';
                    }
                    info["all_skills"].push({
                        "type": typeid,
                        "icon": get_skill_icon(typeid),
                        "grade": all_skills[typeid],
                        "isRiderSkill": true,
                        "name": name,
                        "desc": desc
                    });
                }
                result.push(info);
            }
            this.result["rider_info"] = result;
        },
        parse_clothes_info: function() {
            var ResUrl = this.resUrl;
            var all_clothes_info = this.conf.clothes_info;
            var get_clothes_icon = function(itype) {
                return ResUrl + "/images/clothes/" + itype + "0000.gif";
            };
            var all_clothes = this.raw_info["ExAvt"];
            if (all_clothes == undefined) {
                return;
            }
            var oldClothesList = [];
            var iTypeList = [];
            var newClothesMap = {};
            for (var pos in all_clothes) {
                var clothes_info = all_clothes[pos];
                var iType = clothes_info["iType"];
                var clothe_name = clothes_info.cName || safe_attr(all_clothes_info[iType]);
                var info = {
                    "type": iType,
                    "name": clothe_name,
                    "icon": get_clothes_icon(iType),
                    "order": clothes_info["order"],
                    "static_desc": ""
                };
                iTypeList.push(iType);
                if ("extra_info"in clothes_info) {
                    var id = clothes_info["extra_info"];
                    if (id in newClothesMap) {
                        newClothesMap[id].push(info);
                    } else {
                        newClothesMap[id] = [info];
                    }
                } else {
                    oldClothesList.push(info);
                }
            }
            var newClothesList = [];
            if (Object.keys(newClothesMap).length) {
                var clothesTypeConf = this.conf.clothes_type_conf || [];
                for (var i = 0; i < clothesTypeConf.length; i++) {
                    var item = clothesTypeConf[i];
                    var list = [];
                    if (item.id in newClothesMap) {
                        list = newClothesMap[item.id];
                    }
                    newClothesList.push({
                        id: item.id,
                        title: item.name,
                        list: list
                    });
                }
            }
            var sort_func = function(a, b) {
                if (a["order"] && b["order"]) {
                    return a["order"] - b["order"];
                } else {
                    return a["type"] - b["type"];
                }
            }
            if (this.raw_info["title_effect"]) {
                for (var i = 0; i < newClothesList.length; i++) {
                    var list = newClothesList[i].list;
                    if (list.length) {
                        newClothesList[i].list = list.sort(sort_func);
                    }
                }
                var LIMIT_CLOTH_ID = 1;
                if ((LIMIT_CLOTH_ID in newClothesMap && newClothesMap[LIMIT_CLOTH_ID].length > 0) || this.raw_info["total_avatar"] > 10) {
                    this.result['cloth_itype_list'] = iTypeList.join(",");
                }
                function getDuiBiao(data) {
                    var list = [];
                    if (data && data.length) {
                        for (var i = 0; i < data.length; i++) {
                            if (data[i].client_type == 201) {
                                list.push(data[i]);
                            }
                        }
                    }
                    return list;
                }
                this.result['new_clothes'] = newClothesList;
                this.result["chat_effect"] = this.raw_info["chat_effect"];
                this.result["icon_effect"] = this.raw_info["icon_effect"];
                this.result["title_effect"] = this.raw_info["title_effect"];
                this.result["achieve_show"] = getDuiBiao(this.raw_info["achieve_show"]);
                this.result["perform_effect"] = this.raw_info["perform_effect"];
            } else {
                this.result["clothes"] = oldClothesList.sort(sort_func);
            }
            var avtWidget = this.raw_info["avt_widget"];
            if (avtWidget) {
                var widgetConf = window.CBG_GAME_CONFIG.widget_info_for_display || {};
                var list = [];
                for (var key in avtWidget) {
                    if (widgetConf.hasOwnProperty(key)) {
                        list.push({
                            name: widgetConf[key]
                        });
                    }
                }
                var widgetMap = {
                    title: '挂件',
                    list: list
                }
                var newCloth = this.result['new_clothes'];
                if (!newCloth || newCloth.length === 0) {
                    this.result['new_clothes'] = [widgetMap];
                } else {
                    var index = -1;
                    for (var i = 0, len = newCloth.length; i < len; i++) {
                        if (newCloth[i].title === '限量') {
                            index = i;
                            break;
                        }
                    }
                    newCloth.splice(index + 1, 0, widgetMap);
                    this.result['new_clothes'] = newCloth;
                }
            }
        },
        parse_house_info: function() {
            var info = {
                "house_building_material": this.raw_info["house_building_material"],
                "house_building_material_cnt": this.raw_info["house_building_material_cnt"] || 0,
                "house_jiaju": (this.raw_info["house_indoor_fur"] || []).concat(this.raw_info["house_indoor_packet"] || []),
                "house_jiaju_num": (this.raw_info["house_indoor_fur_cnt"] || 0) + (this.raw_info["house_indoor_packet_cnt"] || 0),
                "house_indoor_view": this.raw_info["house_indoor_view"],
                "house_indoor_view_cnt": this.raw_info["house_indoor_view_cnt"] || 0,
                "house_yard_animate": this.raw_info["house_yard_animate"],
                "house_yard_animate_cnt": this.raw_info["house_yard_animate_cnt"] || 0,
                "house_yard_fur": this.raw_info["house_yard_fur"],
                "house_yard_fur_cnt": this.raw_info["house_yard_fur_cnt"] || 0,
                "house_yard_map": this.raw_info["house_yard_map"],
                "house_yard_map_cnt": this.raw_info["house_yard_map_cnt"] || 0
            };
            this.result["house"] = info;
        },
        parse_xiangrui_info: function() {
            var ResUrl = this.resUrl;
            var all_xiangrui_info = this.conf.xiangrui_info;
            var all_skills = this.conf.xiangrui_skill;
            var nosale_xiangrui = this.conf.nosale_xiangrui;
            var get_xiangrui_icon = function(itype) {
                return ResUrl + "/images/xiangrui/" + itype + ".gif";
            };
            var get_skill_icon = function() {
                return ResUrl + "/images/xiangrui_skills/1.gif";
            };
            var all_xiangrui = this.raw_info["HugeHorse"];
            if (all_xiangrui == undefined) {
                return;
            }
            var result = [];
            var nosale_result = [];
            for (var pos in all_xiangrui) {
                var xiangrui_info = all_xiangrui[pos];
                var type = xiangrui_info["iType"];
                var info = {
                    "type": type,
                    "name": xiangrui_info.cName || safe_attr(all_xiangrui_info[type]),
                    "icon": get_xiangrui_icon(type),
                    "skill_name": all_skills[xiangrui_info['iSkill']],
                    "order": xiangrui_info["order"]
                };
                if (xiangrui_info["iSkillLevel"] != undefined) {
                    info["skill_level"] = xiangrui_info["iSkillLevel"] + "级";
                } else {
                    info["skill_level"] = "";
                }
                if (this.conf.nosale_to_sale_xiangrui[pos]) {
                    var nosale = false;
                } else {
                    var nosale = xiangrui_info["nosale"] && xiangrui_info["nosale"] == 1;
                    if (!nosale) {
                        nosale = (nosale_xiangrui[pos] != undefined);
                    }
                }
                if (nosale) {
                    nosale_result.push(info);
                } else {
                    result.push(info);
                }
            }
            var sort_func = function(a, b) {
                if (a["order"] && b["order"]) {
                    return a["order"] - b["order"];
                } else {
                    return a["type"] - b["type"];
                }
            }
            this.result["xiangrui"] = result.sort(sort_func);
            nosale_result.sort(sort_func);
            this.result["nosale_xiangrui"] = nosale_result;
            if (this.raw_info["normal_horse"]) {
                this.result["normal_xiangrui_num"] = this.raw_info["normal_horse"];
            }
        },
        parse_rider_plan_list: function() {
            var ctx = this;
            var ResUrl = this.resUrl;
            this.result["rider_plan_list"] = this.raw_info["Rider_plan_list"];
            this.result["equip_level"] = ctx.equip_level
        },
        safe_attr: function(attr_value, default_value) {
            if (attr_value === undefined || attr_value === null) {
                return default_value !== undefined ? default_value : "未知";
            }
            return attr_value;
        },
        get_marry_info: function(marry, marry2) {
            if (marry == undefined) {
                return ["未知", "未知"];
            }
            if (marry != undefined && marry != 0) {
                return ["是", marry];
            } else {
                return ["否", "不存在"];
            }
        },
        get_tongpao_info: function(tongpao) {
            if (tongpao == undefined) {
                return ["未知", "未知"];
            }
            if (tongpao != undefined && tongpao != 0) {
                return ["是", tongpao];
            } else {
                return ["否", "不存在"];
            }
        },
        get_married_info: function(relation, grade, r_setting) {
            if (relation === "未知" || grade == undefined) {
                return "未知";
            }
            if (grade == 0) {
                return "无";
            }
            if (relation === "已婚") {
                return "夫妻共有";
            } else if (relation === "同袍") {
                return "同袍共有";
            } else {
                return r_setting[grade];
            }
        },
        get_sheng_si_jie: function() {
            var attr = this.raw_info["nine_fight_level"];
            var level = this.safe_attr(attr);
            if (level != '未知') {
                if (level === 0) {
                    return '零层';
                } else {
                    return window.CHINESE_NUM_CONFIG[level] + '层';
                }
            }
            return level;
        },
        get_fangwu_info: function(relation, fangwu_grade) {
            return this.get_married_info(relation, fangwu_grade, this.conf.fangwu_info);
        },
        get_fangwu_owner_info: function() {
            if (!this.raw_info["equip_desc_version_code"]) {
                return "";
            }
            var fangwu_grade = this.raw_info["rent_level"];
            if (fangwu_grade) {
                return this.raw_info["house_real_owner"] ? "否" : "是";
            }
            return "无";
        },
        get_tingyuan_info: function(relation, tingyuan_grade) {
            return this.get_married_info(relation, tingyuan_grade, this.conf.tingyuan_info);
        },
        get_muchang_info: function(relation, muchang_grade) {
            return this.get_married_info(relation, muchang_grade, this.conf.muchang_info);
        },
        get_real_upexp: function() {
            var exp_num = this.raw_info["iUpExp"];
            if (this.raw_info["ExpJw"] == undefined || this.raw_info["ExpJwBase"] == undefined) {
                return exp_num;
            }
            exp_num += this.raw_info["ExpJw"] * this.raw_info["ExpJwBase"];
            return exp_num;
        },
        get_change_school_list: function(change_list) {
            if (change_list == undefined) {
                return "未知";
            }
            if (!change_list || change_list.length === 0) {
                return "无";
            }
            var school_list = [];
            for (var i = 0; i < change_list.length; i++) {
                var school_name = SchoolNameInfo[change_list[i]];
                if (!school_list.contains(school_name)) {
                    school_list.push(school_name);
                }
            }
            return school_list.join(",");
        },
        parse_role_kind_name: function(icon_id) {
            var icon_id = get_role_iconid(icon_id);
            return get_role_kind_name(icon_id)
        },
        get_qian_yuan_dan: function() {
            var ctx = this;
            var agent_time = parseDatetime(ctx.equipRequestTime);
            var check_time = parseDatetime("2015-03-24 08:00:00");
            var test_check_time = parseDatetime("2015-03-17 08:00:00");
            function judge_time() {
                if ([95, 155, 82, 104, 2, 669, 9, 459].contains(parseInt(ctx.serverId))) {
                    if (agent_time < test_check_time) {
                        return true;
                    }
                } else if (agent_time < check_time) {
                    return true;
                }
                return false;
            }
            function check_undefined(v) {
                return v === undefined ? "未知" : v;
            }
            var attrs = {};
            if (judge_time()) {
                attrs.old_value = this.safe_attr(this.raw_info["TA_iAllPoint"], 0);
            } else {
                attrs.new_value = check_undefined(this.raw_info["TA_iAllNewPoint"]);
            }
            return attrs;
        },
        get_race_by_school: function(school) {
            if ([1, 2, 3, 4, 13, 17].contains(school)) {
                return "人";
            } else if ([9, 10, 11, 12, 15, 16].contains(school)) {
                return "魔";
            } else if ([5, 6, 7, 8, 14, 18].contains(school)) {
                return "仙";
            } else {
                return "未知";
            }
        },
        parse_single_prop_kept: function(prop, grade) {
            if (!prop)
                return null;
            var _this = this;
            var attr_list = [];
            for (var key in prop) {
                if (this.PROP_KEPT_KEYS[key] && prop[key] >= (grade * 2 + 10))
                    attr_list.push({
                        key: key,
                        value: prop[key],
                        name: this.PROP_KEPT_KEYS[key]
                    });
            }
            if (attr_list.length < 1)
                return null;
            if (attr_list.length < 2)
                return attr_list[0].name;
            attr_list.sort(function(x, y) {
                return y.value - x.value || _this.PROP_KEPT_KEYS_ORDER.indexOf(x.key) - _this.PROP_KEPT_KEYS_ORDER.indexOf(y.key);
            });
            return attr_list[0].name.substr(0, 1) + attr_list[1].name.substr(0, 1);
        },
        get_prop_kept: function(propKept, grade) {
            var res = [];
            if (propKept) {
                for (var i = 0; i < 4; ++i) {
                    var s = this.parse_single_prop_kept(propKept[i], grade);
                    s && res.push(s);
                }
            }
            return res.length > 0 ? res.join(',') : '无';
        },
        make_img_name: function(img_name) {
            var img_id = parseInt(img_name)
            var addon = "";
            if (img_id < 10) {
                addon = "000";
            } else if (img_id >= 10 && img_id < 100) {
                addon = "00";
            } else if (img_id >= 100 && img_id < 1000) {
                addon = "0";
            }
            return addon + img_name;
        },
        get_lock_types: function(equip) {
            var locks = [];
            if (equip["iLockActive"]) {
                locks.push("huoyue");
            }
            if (equip["iLockGreen"]) {
                locks.push("protect");
            }
            if (equip["iLock"]) {
                locks.push(equip["iLock"]);
            }
            if (equip["iLockNew"]) {
                locks.push(equip["iLockNew"]);
            }
            return locks;
        },
        get_empty_skill_icon: function() {
            return this.resUrl + "/images/role_skills/empty_skill.gif";
        },
        PROP_KEPT_KEYS: {
            iStr: "力量",
            iMag: "魔力",
            iSpe: "敏捷",
            iCor: "体质",
            iRes: "耐力"
        },
        PROP_KEPT_KEYS_ORDER: ['iStr', 'iMag', 'iSpe', 'iCor', 'iRes']
    };
    return RoleInfoParser;
});
