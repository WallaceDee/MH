var SchoolSkills = {
    '大唐官府': ['十方无敌', '无双一击', '神兵鉴赏', '文韬武略', '为官之道', '紫薇之术', '疾风步'],
    '化生寺': ['金刚伏魔', '小乘佛法', '诵经', '佛光普照', '大慈大悲', '岐黄之术', '渡世步'],
    '女儿村': ['毒经', '倾国倾城', '沉鱼落雁', '闭月羞花', '香飘兰麝', '玉质冰肌', '清歌妙舞'],
    '方寸山': ['磬龙灭法', '黄庭经', '霹雳咒', '符之术', '归元心法', '神道无念', '斜月步'],
    '狮驼岭': ['生死搏', '训兽诀', '魔兽神功', '阴阳二气诀', '狂兽诀', '大鹏展翅', '魔兽反噬'],
    '阴曹地府': ['六道轮回', '幽冥术', '拘魂诀', '灵通术', '九幽阴魂', '尸腐恶', '无常步'],
    '魔王寨': ['震天诀', '牛逼神功', '火云术', '火牛阵', '牛虱阵', '回身击', '裂石步'],
    '盘丝洞': ['秋波暗送', '天外魔音', '蛛丝阵法', '迷情大法', '盘丝大法', '移形换影', '姊妹相随'],
    '龙宫': ['破浪诀', '九龙诀', '呼风唤雨', '龙腾', '逆鳞', '游龙术', '龙附'],
    '天宫': ['傲世诀', '天罡气', '清明自在', '宁气诀', '乾坤塔', '混天术', '云霄步'],
    '普陀山': ['护法金刚', '金刚经', '观音咒', '灵性', '五行学说', '五行扭转', '莲花宝座'],
    '五庄观': ['潇湘仙雨', '乾坤袖', '修仙术', '周易学', '混元道果', '明性修身', '七星遁'],
    '神木林': ['瞬息万变', '万灵诸念', '巫咒', '万物轮转', '天人庇护', '神木恩泽', '驭灵咒'],
    '凌波城': ['天地无极', '九转玄功', '武神显圣', '啸傲', '气吞山河', '诛魔', '法天象地'],
    '无底洞': ['枯骨心法', '阴风绝章', '鬼蛊灵蕴', '燃灯灵宝', '地冥妙法', '混元神功', '秘影迷踪']
};
var RoleSearchFormInit = new Class({
    initialize: function() {
        this.$root = $('role_basic_panel');
        this.init_role_level();
        this.gen_equip_levels();
        this.init_taozhuang();
        this.reg_advance_search_fold_ev();
        this.reg_item_selected_ev();
        this.reg_reset_ev();
        this.init_school_skill_tips();
        this.init_zhuang_zhi();
        this.init_xiedai_kid_slider();
        this.select_server = new DropSelectServer($('sel_area'),$('switchto_serverid'));
        $('sel_area').select_server = this.select_server;
        $("btn_do_query").addEvent("click", function() {
            submit_query_form();
        });
        this.init_shenqi();
        this.init_temple();
        this.init_xuan_ling_zhu();
    },
    init_xuan_ling_zhu: function() {
        $('xuan_ling_zhu_type').addEvent('change', function() {
            var $xuanLingZhuLevel = $('xuan_ling_zhu_level');
            var value = $('xuan_ling_zhu_type').value;
            if (value.length > 0) {
                $xuanLingZhuLevel.set('disabled', false);
            } else {
                $xuanLingZhuLevel.set('disabled', true);
                $xuanLingZhuLevel.value = $xuanLingZhuLevel.options[0].value;
            }
        });
    },
    init_temple: function() {
        var cbgConfig = window.CBG_GAME_CONFIG || {};
        var autoSearchConfig = window.AUTO_SEARCH_CONFIG || {};
        var ctx = this;
        var school_info = Object.merge({}, cbgConfig.school_info);
        school_info["99999"] = '无历史门派';
        var selectConfig = [{
            id: ['school_change_list'],
            data: school_info,
            templateId: 'template_btn_li'
        }, {
            id: ['school_list', 'child_school_box'],
            data: cbgConfig.school_info,
            templateId: 'template_btn_li'
        }, {
            id: 'race_list',
            data: cbgConfig.race_info,
            templateId: 'template_btn_li'
        }, {
            id: 'ori_race_list',
            data: autoSearchConfig.ori_race_info,
            templateId: 'template_btn_li'
        }, {
            id: 'child_ending_box',
            data: cbgConfig.ending_info,
            templateId: 'template_btn_li'
        }, {
            id: 'xiangrui_limit_box',
            data: autoSearchConfig.limited_xiangrui,
            templateId: 'template_btn_li'
        }, {
            id: 'xiangrui_normal_box',
            data: autoSearchConfig.normal_xiangrui,
            templateId: 'template_btn_li'
        }, {
            id: 'limit_clothes_panel',
            data: autoSearchConfig.limit_clothes_for_search,
            templateId: 'template_btn_li'
        }, {
            id: 'widget_list_panel',
            data: autoSearchConfig.widget_info || {},
            templateId: 'template_btn_li'
        }, {
            id: ['addon_key_1', 'addon_key_2', 'addon_key_3'],
            data: changeArrayToObject(autoSearchConfig.shenqi_wuxing_attrs),
            templateId: 'template_option'
        }, {
            id: 'attr_point_strategy',
            data: autoSearchConfig.attr_point_strategy,
            templateId: 'template_option'
        }, {
            id: 'tingyuan_level',
            data: cbgConfig.tingyuan_info,
            templateId: 'template_option'
        }, {
            id: 'fangwu_level',
            data: cbgConfig.fangwu_info,
            templateId: 'template_option'
        }, {
            id: 'muchang_level',
            data: cbgConfig.muchang_info,
            templateId: 'template_option'
        }, {
            id: 'equip_teji',
            data: autoSearchConfig.teji_info,
            templateId: 'template_btn_li'
        }, {
            id: 'equip_texiao',
            data: autoSearchConfig.texiao_info,
            templateId: 'template_btn_li'
        }, {
            id: 'front_pet_type',
            data: ctx.get_pet_type_data().front,
            templateId: 'template_btn_li'
        }, {
            id: 'after_pet_type',
            data: ctx.get_pet_type_data().after,
            templateId: 'template_btn_li'
        }, {
            id: 'perform_effect_list',
            data: cbgConfig.perform_effect,
            templateId: 'template_btn_li'
        }, {
            id: 'equip_type_list',
            data: autoSearchConfig.weapon_armors,
            templateId: 'template_btn_li'
        }];
        for (var i = 0; i < selectConfig.length; i++) {
            var item = selectConfig[i];
            var id = item.id;
            if (id instanceof Array) {
                for (var k = 0; k < id.length; k++) {
                    render_to_replace(id[k], item.templateId, {
                        config: item.data
                    });
                }
            } else {
                render_to_replace(item.id, item.templateId, {
                    config: item.data
                });
            }
        }
    },
    get_pet_type_data: function() {
        var front = {};
        var after = {};
        var autoSearchConfig = (window.AUTO_SEARCH_CONFIG || {}).role_pet_types || {};
        for (var key in autoSearchConfig) {
            if (key.length > 1) {
                after[key] = autoSearchConfig[key];
            } else {
                front[key] = autoSearchConfig[key];
            }
        }
        return {
            front: front,
            after: after
        }
    },
    init_role_level: function() {
        $$("#role_level li[data-level]").addEvent('click', function() {
            var level = $(this).get('data-level');
            $('level_min').value = level;
            $('level_max').value = level;
            update_level_btns();
        });
        $$('#level_min, #level_max').addEvent('keyup', update_level_btns);
        function update_level_btns() {
            var level_min = $('level_min').value
              , level_max = $('level_max').value;
            $$("#role_level li[data-level]").each(function(el) {
                var data_level = el.get('data-level');
                if (data_level == level_min && data_level == level_max) {
                    el.addClass('on');
                } else {
                    el.removeClass('on');
                }
            });
        }
    },
    init_taozhuang: function() {
        var con = $('taozhuang_type');
        var suitEffects = AUTO_SEARCH_CONFIG.suit_effects_for_front || {};
        for (var val in suitEffects) {
            if (suitEffects.hasOwnProperty(val)) {
                var option = new Element('option',{
                    'value': val,
                    'html': suitEffects[val]
                });
                con.grab(option);
            }
        }
    },
    init_zhuang_zhi: function() {
        var ctx = this;
        var $root = ctx.$root;
        $root.addEvent('click:relay(.zhuang_zhi)', function() {
            var $zhuangZhiSelect = $('zhuang_zhi_hua_sheng_select');
            var $selectWrap = $('huashengSelect');
            if ($(this).get('data-type') && $(this).get('data-type') == 'huasheng') {
                $selectWrap.removeClass('disabled');
                $zhuangZhiSelect.set('disabled', false);
            } else {
                $selectWrap.addClass('disabled');
                $zhuangZhiSelect.set('disabled', true);
                $('zhuang_zhi_hua_sheng').value = $zhuangZhiSelect.options[0].value;
                $zhuangZhiSelect.selectedIndex = 0;
            }
        });
    },
    init_xiedai_kid_slider: function() {
        var $slider = $('child_skill_num');
        if (!$slider) {
            return;
        }
        var min = parseInt($slider.get('data-min'))
          , max = parseInt($slider.get('data-max'));
        var levelSlider = new LevelSlider($slider,{
            grid: 20,
            offset: -23,
            range: [min, max],
            step: 1,
            default_value: [min, max],
            tipSuffix: ''
        });
    },
    gen_equip_levels: function() {
        var el_list = [$("equip_level_min"), $("equip_level_max")];
        for (var i = 0; i < el_list.length; i++) {
            var el = el_list[i];
            var op = new Element("option",{
                "text": "不限",
                "value": ""
            });
            op.inject(el);
            var j = 10;
            while (j <= 160) {
                var op = new Element("option",{
                    "text": j,
                    "value": j
                });
                op.inject(el);
                j = j + 10;
            }
        }
    },
    reg_advance_search_fold_ev: function() {
        $("btn_advance_search_fold").addEvent("click", function() {
            if ($("advance_search_box").getStyle("display") == "block") {
                $("advance_search_box").setStyle("display", "none");
            } else {
                $("advance_search_box").setStyle("display", "block");
            }
        });
    },
    reg_item_selected_ev: function() {
        $$('.js_selected_li').addEvent('click:relay(li)', function() {
            var el = $(this);
            if (el.hasClass("on")) {
                el.removeClass("on");
            } else {
                el.addClass("on");
            }
        });
    },
    empty_input_box: function(item_list) {
        for (var i = 0; i < item_list.length; i++) {
            if (item_list[i].type != 'radio') {
                $(item_list[i]).value = "";
            }
        }
    },
    reg_reset_ev: function() {
        var self = this;
        $("reset_role_basic").addEvent("click", function() {
            self.empty_input_box($$("#role_basic_panel input[type=text]"));
            $$("#role_basic_panel li.on").removeClass("on");
            $$('#role_basic_panel input[type=radio]').set('checked', false);
            var $zhuangZhiSelect = $('zhuang_zhi_hua_sheng_select');
            $('zhuang_zhi_hua_sheng').value = $zhuangZhiSelect.options[0].value;
            $('huashengSelect').addClass('disabled');
            $zhuangZhiSelect.set('disabled', true);
            $zhuangZhiSelect.selectedIndex = 0;
            return false;
        });
        $("reset_role_attr").addEvent("click", function() {
            self.empty_input_box($$("#role_attr_panel input"));
            $$("#role_attr_panel li.on").removeClass("on");
            $('attr_point_strategy').value = '';
            return false;
        });
        $("reset_role_expt").addEvent("click", function() {
            self.empty_input_box($$("#role_expt_panel input"));
            return false;
        });
        $("reset_role_skills").addEvent("click", function() {
            self.empty_input_box($$("#role_skills_panel input"));
            self.empty_input_box($$("#role_skills_panel select"));
            return false;
        });
        $("reset_role_carry").addEvent("click", function() {
            self.empty_input_box($$("#role_carry_panel input"));
            self.empty_input_box($$("#role_carry_panel select"));
            $$("#role_carry_panel li.on").removeClass("on");
            $("teji_match_signle").checked = true;
            $("teji_match_all").checked = false;
            $("texiao_match_single").checked = true;
            $("texiao_match_all").checked = false;
            $("lingshi_attr_match_single").checked = true;
            $("lingshi_attr_match_all").checked = false;
            $("pet_match_signle").checked = true;
            $("pet_match_all").checked = false;
            $("xiangrui_match_signle").checked = true;
            $("xiangrui_match_all").checked = false;
            $("perform_match_all").checked = false;
            $("special_equip_one").checked = false;
            $('child_skill_num').slider.reset_value();
            $$('.jsShenqiWrap .jsSelect').fireEvent('change');
            $("original_school_skill_1").checked = true;
            $("original_school_skill_0").checked = false;
            return false;
        });
        $("reset_role_other").addEvent("click", function() {
            self.empty_input_box($$("#role_other_box input"));
            self.empty_input_box($$("#role_other_box select"));
            return false;
        });
        $("reset_server_selected").addEvent("click", function() {
            self.select_server.reset_value();
            self.empty_input_box($$("#server_info_box input"));
            $$("#server_info_box li.on").removeClass("on");
            return false;
        });
        $("reset_all").addEvent("click", function() {
            $("reset_role_basic").fireEvent("click");
            $("reset_role_attr").fireEvent("click");
            $("reset_role_expt").fireEvent("click");
            $("reset_role_skills").fireEvent("click");
            $("reset_role_carry").fireEvent("click");
            $("reset_role_other").fireEvent("click");
            $("reset_server_selected").fireEvent("click");
            return false;
        });
    },
    init_school_skill_tips: function() {
        $$("#role_school_skills label").each(function(el, index) {
            var content = ['<div class="tipsContent clearfix">', '<h5>技能', (index + 1) + '对照表</h5>', '<dl>'];
            for (var school in SchoolSkills) {
                content.push('<dt>' + school + '：</dt>');
                content.push('<dd>' + SchoolSkills[school][index] + '</dd>');
            }
            content.push('</dl>');
            content.push('</div>');
            init_popover({
                target: el,
                content: content.join(''),
                class_name: 'tipsBlack popArrowUp schoolSkillTips'
            });
        });
    },
    init_shenqi: function() {
        $$('.jsShenqiWrap .jsSelect').addEvent('change', function() {
            var elSelect = $(this);
            elSelect.getNext('.jsInput').set('disabled', !elSelect.get('value'));
        });
        $$('.jsShenqiWrap .jsInput').forEach(function(input) {
            var elInput = $(input);
            var max = parseInt(elInput.get('data-max')) || null;
            InputLimit.onlyInt(elInput, null, max ? {
                min: 0,
                max: max
            } : null);
        });
    }
});
function check_int_args(args_config_list) {
    var re = /^[0-9]\d*$/;
    var args = {};
    for (var i = 0; i < args_config_list.length; i++) {
        var item = args_config_list[i];
        var item_value = (typeof item[0] == 'string' ? $(item[0] + "") : item[0]).value.trim();
        if (item_value.length == 0) {
            continue;
        }
        if (!re.test(item_value) || item_value.length > 10) {
            return {
                "result": false,
                "msg": item[1] + "填写错误，请重新输入"
            }
        }
        item_value = parseInt(item_value);
        var opts = item[2] || {};
        if (opts.min != void 0 && item_value < opts.min) {
            return {
                "result": false,
                "msg": item[1] + "不能小于" + opts.min
            };
        }
        if (opts.max != void 0 && item_value > opts.max) {
            return {
                "result": false,
                "msg": item[1] + "不能大于" + opts.max
            };
        }
        if (item_value <= 0) {
            continue;
        }
        args[item[0]] = item_value;
    }
    return {
        "result": true,
        "args": args
    };
}
function get_item_selected(item_list) {
    var value_list = [];
    for (var i = 0; i < item_list.length; i++) {
        var item = item_list[i];
        if (item.hasClass("on")) {
            value_list.push(item.getAttribute("data_value"));
        }
    }
    return value_list.join(",");
}
function submit_query_form() {
    var args_config = [["level_min", "角色最低等级"], ["level_max", "角色最高等级"], ["shang_hai", "伤害"], ["ming_zhong", "命中"], ["ling_li", "灵力"], ["fang_yu", "防御"], ["hp", "气血"], ["speed", "速度"], ["fa_shang", "法伤"], ["fa_fang", "法防"], ["qian_neng_guo", "潜能果"], ["expt_gongji", "攻击修炼"], ["expt_fangyu", "防御修炼"], ["expt_fashu", "法术修炼"], ["expt_kangfa", "抗法修炼"], ["max_expt_gongji", "攻击上限"], ["max_expt_fangyu", "防御上限"], ["max_expt_fashu", "法术上限"], ["max_expt_kangfa", "抗法上限"], ["expt_lieshu", "猎术修炼"], ["expt_total", "修炼总和"], ["bb_expt_gongji", "攻击控制"], ["bb_expt_fangyu", "防御控制"], ["bb_expt_fashu", "法术控制"], ["bb_expt_kangfa", "抗法控制"], ["bb_expt_total", "宠修总和"], ["skill_qiang_shen", "强身"], ["skill_shensu", "神速"], ["skill_qiang_zhuang", "强健"], ["skill_ming_xiang", "冥想"], ["skill_dazao", "打造技巧"], ["skill_pengren", "烹饪技巧"], ["skill_caifeng", "裁缝技巧"], ["skill_zhongyao", "中药医疗"], ["skill_qiaojiang", "巧匠之术"], ["skill_lingshi", "灵石技巧"], ["skill_lianjin", "炼金术"], ["skill_jianshen", "健身术"], ["skill_yangsheng", "养生之道"], ["skill_anqi", "暗器技巧"], ["skill_taoli", "逃离技巧"], ["skill_zhuibu", "追捕技巧"], ["skill_ronglian", "熔炼技巧"], ["skill_danyuan", "丹元济会"], ["skill_miaoshou", "妙手空空"], ["skill_baoshi", "宝石工艺"], ["skill_qimen", "奇门遁甲"], ["skill_gudong", "古董评估"], ["skill_xianling", "仙灵店铺"], ["skill_tiaoxi", "调息"], ["skill_dazuo", "打坐"], ["skill_jianzhu", "建筑之术"], ["skill_bianhua", "变化之术"], ["skill_cuiling", "淬灵之术"], ["skill_wind_sense", "风之感应"], ["skill_rain_sense", "雨之感应"], ["skill_snow_sense", "雪之感应"], ["skill_hanmo", "翰墨之道"], ["skill_danqing", "丹青之道"], ["skill_huoyan", "火眼金睛"], ["max_weapon_shang_hai", "携带武器总伤"], ["max_weapon_damage", "携带武器伤害"], ["max_weapon_init_damage", "携带武器初伤（含命中）"], ["max_weapon_init_damage_raw", "携带武器初伤（不含命中）"], ["max_necklace_ling_li", "携带项链灵力"], ["max_necklace_init_wakan", "携带项链初灵"], ["pet_skill_num", "技能数量"], ["pet_advance_skill_num", "高级技能数量"], ["xian_yu", "仙玉"], ["cash", "现金"], ["upexp", "当前经验"], ["badness", "善恶"], ["school_offer", "门贡"], ["org_offer", "帮贡"], ["cheng_jiu", "成就"], ["body_caiguo", "染色折合彩效果数"], ["all_caiguo", "所有染色折算彩果数"], ["box_caiguo", "保存染色方案数"], ["clothes_num", "锦衣数量"], ["school_skill_num", "师门技能数"], ["equip_level_min", "装备最低等级"], ["equip_level_max", "装备最高等级"], ["taozhuang_num", "套装数量"], ["taozhuang_type", "套装类型"], ["has_community", "社区"], ["fangwu_level", "房屋"], ["tingyuan_level", "庭院"], ["muchang_level", "牧场"], ["switchto_serverid", "转服至"], ["school_skill_level", "师门技能等级"], ['sum_exp_min', '角色总经验'], ['sum_exp_max', '角色总经验'], ['lin_shi_fu', '临时符技能'], ['qian_yuan_dan', '乾元丹个数'], ['smith_skill', '打造熟练度'], ['sew_skill', '裁缝熟练度'], ['skill_drive_pet', '驭兽术'], ['lingshi_min_level', '灵饰最低等级'], ['lingshi_max_level', '灵饰最高等级'], ['lingshi_min_duanzao_level', '灵饰最低锻造'], ['lingshi_max_duanzao_level', '灵饰最高锻造'], ['lingshi_attr_2', '灵饰伤害'], ['lingshi_attr_3', '灵饰速度'], ['lingshi_attr_8', '灵饰封印'], ['lingshi_attr_11', '灵饰治疗'], ['lingshi_attr_7', '灵饰法爆'], ['lingshi_attr_4', '灵饰法伤'], ['lingshi_attr_9', '灵饰法伤结果'], ['lingshi_attr_1', '灵饰固伤'], ['lingshi_attr_6', '灵饰物爆'], ['lingshi_attr_12', '灵饰气血'], ['lingshi_attr_13', '灵饰防御'], ['lingshi_attr_14', '灵饰法防'], ['lingshi_attr_17', '灵饰抗封'], ['lingshi_attr_18', '灵饰格挡'], ['lingshi_attr_16', '灵饰抗法爆'], ['lingshi_attr_15', '灵饰抗物爆'], ['growup_pet_num', '成品召唤兽数量'], ['child_attr_total_score', '总属性点', {
        min: 0,
        max: 999999
    }], ['energy', '精力'], ['pride', '人气'], ['xiangrui_num', '祥瑞数量'], ['learn_cash', '储备金'], ['pet_extend_num', '召唤兽栏扩展个数'], ['baggage_extend_num', '行囊扩展个数'], ['sheng_yu_ling_you', '剩余灵佑次数'], ['rider_exgrow_full_num', '满成长坐骑数（后天成长1.0）'], ['sword_score', '剑会积分'], ['hero_score', '比武积分'], ['sbook_skill_num', '召唤兽心得技能', {
        min: 0,
        max: 100
    }], ];
    var input_check = check_int_args(args_config);
    if (!input_check["result"]) {
        alert(input_check["msg"]);
        return;
    }
    var args = input_check["args"];
    if (args["level_min"] != undefined && args["level_max"] != undefined) {
        if (args["level_max"] < args["level_min"]) {
            alert("搜索等级范围填写错误");
            return false;
        }
    }
    if ((args["level_max"] != undefined && args["level_max"] > 175) || (args["level_min"] != undefined && args["level_min"] > 175)) {
        alert("等级超出取值范围:0-175");
        return false;
    }
    if ($("txt_price_min").value.trim().length > 0) {
        var price_min_value = parseFloat($("txt_price_min").value);
        if (!price_min_value || price_min_value <= 0) {
            alert("您输入的最低价格有错误");
            return false;
        }
        if (price_min_value > window.MaxTradeYuan) {
            alert('价格超出取值范围:0-' + MaxTradeYuan);
            return;
        }
        args["price_min"] = parseInt(price_min_value * 100);
    }
    if ($("txt_price_max").value.trim().length > 0) {
        var price_max_value = parseFloat($("txt_price_max").value);
        if (!price_max_value || price_max_value <= 0) {
            alert("您输入的最高价格有错误");
            return false;
        }
        if (price_max_value > window.MaxTradeYuan) {
            alert('价格超出取值范围:0-' + MaxTradeYuan);
            return;
        }
        args["price_max"] = parseInt(price_max_value * 100);
    }
    if (args["price_min"] != undefined && args["price_max"] != undefined) {
        if (args["price_max"] < args["price_min"]) {
            alert("搜索价格范围填写错误");
            return false;
        }
    }
    if (args["lingshi_min_level"] != undefined && args["lingshi_max_level"] != undefined) {
        if (args["lingshi_max_level"] < args["lingshi_min_level"]) {
            alert("灵饰等级最小值不能大于最大值");
            return false;
        }
    }
    if (args["lingshi_min_duanzao_level"] != undefined && args["lingshi_max_duanzao_level"] != undefined) {
        if (args["lingshi_max_duanzao_level"] < args["lingshi_min_duanzao_level"]) {
            alert("锻造等级最小值不能大于最大值");
            return false;
        }
    }
    if (args['sum_exp_min'] && args['sum_exp_max'] && args['sum_exp_min'] > args['sum_exp_max']) {
        alert('角色总经验最小值不能大于最大值');
        return false;
    }
    var school = get_item_selected($$("#school_list li"));
    if (school.length > 0) {
        args["school"] = school;
    }
    var school_change_list = get_item_selected($$("#school_change_list li"));
    if (school_change_list.length > 0) {
        var schoolList = school_change_list.split(",");
        var index = schoolList.indexOf("99999");
        if (index !== -1) {
            schoolList[index] = 0;
        }
        school_change_list = schoolList.join(",");
        args["school_change_list"] = school_change_list;
    }
    var race = get_item_selected($$("#race_list li"));
    if (race.length > 0) {
        args["race"] = race;
    }
    var perform_effect = get_item_selected($$("#perform_effect_list li"));
    if (perform_effect.length > 0) {
        args["perform_effect"] = perform_effect;
        if ($("perform_match_all").checked) {
            args["perform_match_all"] = 1;
        }
    }
    var ori_race = get_item_selected($$("#ori_race_list li"));
    if (ori_race.length > 0) {
        args["ori_race"] = ori_race;
    }
    var teji_list = get_item_selected($$("#equip_teji li"));
    var texiao_list = get_item_selected($$("#equip_texiao li"));
    var equip_type_list = get_item_selected($$("#equip_type_list li"));
    if (teji_list.length + texiao_list.length + equip_type_list.length > 0) {
        if (teji_list.length) {
            args["teji_list"] = teji_list;
        }
        if (texiao_list.length) {
            args["texiao_list"] = texiao_list;
        }
        if (equip_type_list.length) {
            args["own_equips_equip_kind_id"] = equip_type_list;
        }
    }
    if ($("special_equip_one").checked) {
        var specialEquipMaxLevel = Number($("special_equip_max_level").value);
        if ((specialEquipMaxLevel !== "" && !/^[1-9]\d*$/g.test(specialEquipMaxLevel)) || specialEquipMaxLevel > 999) {
            alert("【专用装备等级】必须为1-999的整数");
            return false;
        }
        args["special_equip_max_level"] = specialEquipMaxLevel == "" ? "1" : specialEquipMaxLevel;
    }
    var pet_type_list = get_item_selected($$("#pet_box li"));
    if (pet_type_list.length > 0) {
        args["pet_type_list"] = pet_type_list;
    }
    var shenqiSelects = $$('.jsShenqiWrap .jsSelect');
    for (var i = 0, max = shenqiSelects.length; i < max; i++) {
        var elSelect = $(shenqiSelects[i])
          , elRoot = elSelect.getParent('.jsShenqiWrap')
          , elInput = elSelect.getNext('.jsInput')
        elText = elSelect.getPrevious('.jsText');
        var attr = 'data-key';
        var key = elRoot.get(attr);
        var selectValue = elSelect.get('value')
          , inputValue = parseInt(elInput.get('value')) || 0;
        if (selectValue) {
            var data = JSON.decode(args[key] || '{}');
            data[elSelect.get(attr)] = selectValue;
            var res = check_int_args([[elInput, '神器' + elText.get('text').trim(), {
                min: 0,
                max: parseInt(elInput.get('data-max')) || void 0
            }]]);
            if (!res.result) {
                return alert(res.msg);
            }
            data[elInput.get(attr)] = inputValue;
            args[key] = JSON.encode(data);
        }
    }
    var kid_skill_count_slider = $('child_skill_num').slider;
    var kid_skill_count_slider_min = kid_skill_count_slider.options.range[0];
    var kid_skill_count_slider_max = kid_skill_count_slider.options.range[1];
    args['child_skill_num_min'] = kid_skill_count_slider.value.min;
    args['child_skill_num_max'] = kid_skill_count_slider.value.max;
    if (args['child_skill_num_min'] == kid_skill_count_slider_min && args['child_skill_num_max'] == kid_skill_count_slider_max) {
        delete args['child_skill_num_min'];
        delete args['child_skill_num_max'];
    }
    var xiedai_kid_jieju_list = get_item_selected($$('#child_ending_box li'));
    if (xiedai_kid_jieju_list.length > 0) {
        args["child_ending"] = xiedai_kid_jieju_list;
    }
    var xiedai_kid_school_list = get_item_selected($$('#child_school_box li'));
    if (xiedai_kid_school_list.length > 0) {
        args["child_school"] = xiedai_kid_school_list;
    }
    var xiangrui_list = get_item_selected($$("#xiangrui_box li"));
    if (xiangrui_list.length > 0) {
        args["xiangrui_list"] = xiangrui_list;
    }
    var server_type = get_item_selected($$("#server_type li"));
    if (server_type.length > 0) {
        args["server_type"] = server_type;
    }
    var is_married = $("is_married").value;
    if (is_married.length > 0) {
        args["is_married"] = is_married;
    }
    var is_tongpao = $("is_tongpao").value;
    if (is_tongpao.length > 0) {
        args["is_tongpao"] = is_tongpao;
    }
    var xuan_ling_zhu_type = $("xuan_ling_zhu_type").value;
    if (xuan_ling_zhu_type.length > 0) {
        var xuan_ling_zhu_level = $("xuan_ling_zhu_level").value;
        var rider_plan_str = xuan_ling_zhu_type + "," + xuan_ling_zhu_level;
        args["rider_plan"] = rider_plan_str;
    }
    var attr_point_strategy = $('attr_point_strategy').value;
    if (attr_point_strategy) {
        args['attr_point_strategy'] = attr_point_strategy;
    }
    var jiyuan_and_addpoint_value = parseInt($('jiyuan_and_addpoint').value);
    if (jiyuan_and_addpoint_value) {
        var selected = $$('#jiyuan_and_addpoint_panel .on');
        if (selected.length > 0) {
            var key;
            if (selected.length == 2)
                key = 'jiyuan_and_addpoint';
            else
                key = selected[0].getAttribute('data_value');
            args[key] = jiyuan_and_addpoint_value;
        }
    }
    if ($('is_niceid_new').value)
        args['is_niceid_new'] = $('is_niceid_new').value;
    var limit_clothes = get_item_selected($$("#limit_clothes_panel li"));
    if (limit_clothes.length > 0) {
        args["limit_clothes"] = limit_clothes;
    }
    var widget = get_item_selected($$("#widget_list_panel li"));
    if (widget.length > 0) {
        args["widget_list"] = widget;
    }
    if ($("original_school_skill_0").checked) {
        args["use_original_school_skill_level"] = "1";
    }
    if (Object.getLength(args) == 0) {
        alert("您选择的查询条件过少，请选择更多查询条件");
        return false;
    }
    $$('input[name=zhuang_zhi]').each(function(el) {
        if ($(el).checked) {
            args['zhuang_zhi'] = $(el).value;
        }
    });
    if ($("teji_match_all").checked && args['teji_list']) {
        args["teji_match_all"] = 1;
    }
    if ($("texiao_match_all").checked && args['texiao_list']) {
        args["texiao_match_all"] = 1;
    }
    if ($("pet_match_all").checked && pet_type_list.length > 0) {
        args["pet_match_all"] = 1;
    }
    if ($("xiangrui_match_all").checked && xiangrui_list.length > 0) {
        args["xiangrui_match_all"] = 1;
    }
    if ($("lingshi_attr_match_all").checked) {
        for (var i = 1; i < 19; i++) {
            var lingshiAttrKey = "lingshi_attr_" + i;
            if (args[lingshiAttrKey]) {
                args["lingshi_attr_match_all"] = 1;
                break;
            }
        }
    }
    if ($("duanzao_attr").value && $("duanzao_num").value) {
        var duanzaoArr = $("duanzao_attr").value;
        var duanzaoNum = $("duanzao_num").value;
        args[duanzaoArr] = duanzaoNum;
    }
    if ($("user_serverid") && $("user_serverid").value) {
        args['serverid'] = $("user_serverid").value;
        window.server_selector && server_selector.update_recent_server_list();
    }
    $$('input[name=limit_clothes_logic]').each(function(el) {
        if (el.checked && limit_clothes.length > 0) {
            args['limit_clothes_logic'] = el.value;
        }
    });
    $$('input[name=widget_match_all]').each(function(el) {
        if (el.checked && widget.length > 0) {
            args['widget_match_all'] = el.value;
        }
    });
    $("query_args").value = JSON.encode(args);
    save_args_in_cookie(args, "overall_role_search");
    update_overall_search_saved_query();
    document.query_form.submit();
}
function add_orderby_ev() {
    var elList = $$('#order_menu a[data_attr_name]')
    elList.addEvent("click", function() {
        change_query_order($(this));
        return false;
    });
    fix_overall_search_order_menu(OrderInfo.field_name, OrderInfo.order, $('order_menu'));
}
function show_loading() {
    show_layer_center($("LoadingCover"), $("LoadingImg"));
}
function loading_finish() {
    $("LoadingCover").setStyle("display", "none");
    $("LoadingImg").setStyle("display", "none");
}
var NextProc = null;
function show_query_result(result, txt) {
    NextProc = null;
    if (result["status"] != 0) {
        alert(result["msg"]);
        return;
    }
    if (!result.equip_list && result.msg) {
        result.equip_list = result.msg;
    }
    if (!result.pager && result.paging) {
        result.pager = result.paging;
    }
    if (result["equip_list"].length == 0) {
        render_to_replace("query_result", "no_result", {});
        return;
    }
    for (var i = 0; i < result["equip_list"].length; i++) {
        var equip = result["equip_list"][i]
        equip["iIcon"] = equip["icon"];
        equip["icon"] = ResUrl + '/images/role_icon/small/' + get_role_iconid(equip["icon"]) + '.gif'
    }
    var ctx = {
        result: result,
        "role_list": result["equip_list"],
        "pager": result["pager"]
    }
    QueryResult = result["equip_list"];
    render_to_replace("query_result", "role_list_templ", ctx);
    add_orderby_ev();
    render_to_replace("pager_bar", "pager_templ", {
        "pager": result["pager"]
    });
    var el_list = $$("#soldList a.soldImg");
    for (var i = 0; i < el_list.length; i++) {
        var el = el_list[i];
        el.addEvent("mouseover", function() {
            show_role_tips_box($(this));
        });
        el.addEvent("mouseout", hidden_tips_box);
    }
    window.fireEvent('renderFinish');
}
function show_error() {
    render_to_replace('query_result', 'no_result', {});
    $$('#query_result p').set('html', '系统繁忙，请稍后再试');
}
var OrderInfo = {
    "field_name": "",
    "order": ""
};
var QueryResult = null;
function change_query_order(el, callback) {
    var attr_name = el.getAttribute("data_attr_name") || '';
    var order = 'DESC';
    if (OrderInfo.field_name == attr_name) {
        order = OrderInfo.order === 'DESC' ? 'ASC' : 'DESC';
    }
    if (!attr_name) {
        order = '';
        delete QueryArgs['order_by'];
    } else {
        QueryArgs.order_by = attr_name + ' ' + order;
    }
    OrderInfo.field_name = attr_name;
    OrderInfo.order = order;
    callback && callback(attr_name, order);
    do_query(1);
}
function do_query(page_num) {
    NextProc = "do_query(" + page_num + ")";
    QueryArgs["act"] = SearchAct;
    QueryArgs["page"] = page_num;
    ajax_with_recommend({
        data: Object.merge({}, QueryArgs),
        ajaxGuardParams: {
            return_url: CgiRootUrl + '/xyq_overall_search.py?act=show_search_role_form',
            onSuccess: function() {
                if (window.NextProc) {
                    eval(window.NextProc);
                }
            }
        },
        onRequest: show_loading,
        onSuccess: show_query_result,
        onFailure: show_error,
        onComplete: loading_finish
    });
}
function goto(page_num) {
    do_query(page_num);
}
function make_img_name(img_name) {
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
}
function get_skill_icon(skillid) {
    var img_name = make_img_name(skillid) + ".gif";
    return ResUrl + "/images/role_skills/" + img_name;
}
var Config = new RoleNameConf();
function show_role_tips_box(el) {
    var game_ordersn = el.getAttribute("data_game_ordersn");
    var time_lock = el.getAttribute("data_time_lock");
    var other_info = parse_role_info($("other_info_" + game_ordersn).value);
    var $box = $("TipsBox");
    $box.addClass('tip-for-role');
    if (other_info['iMaxExpt1'] != undefined || other_info['all_skills'] != undefined) {
        show_role_tips_box_common(el, other_info);
        return;
    }
    var role = null;
    for (var i = 0; i < QueryResult.length; i++) {
        if (QueryResult[i]["game_ordersn"] == game_ordersn) {
            role = QueryResult[i];
            break;
        }
    }
    if (!role) {
        return;
    }
    var school_skills = JSON.decode(role["school_skills"]) || [];
    var school_skill_info = {};
    for (var i = 1; i < 8; i++) {
        school_skill_info["school_skill" + i + "_icon"] = EmptySkillImg;
        school_skill_info["school_skill" + i + "_grade"] = "";
        school_skill_info["school_skill" + i + "_name"] = "";
    }
    for (var i = 0; i < school_skills.length; i++) {
        var skill_id = school_skills[i]["id"];
        if (!Config.skill.school_skill[skill_id])
            continue;
        var level = school_skills[i]["level"];
        var pos = Config.skill["school_skill"][skill_id]["pos"];
        var name = Config.skill["school_skill"][skill_id]["name"];
        school_skill_info["school_skill" + pos + "_icon"] = get_skill_icon(skill_id);
        school_skill_info["school_skill" + pos + "_grade"] = level;
        school_skill_info["school_skill" + pos + "_name"] = name;
    }
    role["icon"] = ResUrl + '/images/bigface/' + get_role_iconid(role["iIcon"]) + ".gif";
    role["time_lock"] = time_lock;
    var ctx = {
        "role": role,
        "school_skill": school_skill_info
    };
    render_to_replace("TipsBox", "role_tips_template", ctx);
    adjust_tips_position(el, $box);
}
;(function() {
    if (typeof CreateConfig == 'undefined') {
        return;
    }
    var BasicSubType = {
        shang_hai: "伤害≥",
        ming_zhong: "命中≥",
        ling_li: "灵力≥",
        fang_yu: "防御≥",
        hp: "气血≥",
        speed: "速度≥",
        fa_shang: "法伤≥",
        fa_fang: "法防≥"
    };
    var BodyEquipSubType = {
        max_weapon_shang_hai: "携带武器总伤≥",
        max_weapon_damage: "携带武器伤害≥",
        max_weapon_init_damage: "携带武器初伤（含命中）≥",
        max_weapon_init_damage_raw: "携带武器初伤（不含命中）≥",
        max_necklace_ling_li: "携带项链灵力≥",
        max_necklace_init_wakan: "携带项链初灵≥"
    };
    var LingshiAttr = {
        lingshi_attr_2: "伤害≥",
        lingshi_attr_3: "速度≥",
        lingshi_attr_8: "封印≥",
        lingshi_attr_11: "治疗≥",
        lingshi_attr_7: "法爆≥",
        lingshi_attr_4: "法伤≥",
        lingshi_attr_9: "法伤结果≥",
        lingshi_attr_1: "固伤≥",
        lingshi_attr_6: "物爆≥",
        lingshi_attr_12: "气血≥",
        lingshi_attr_13: "防御≥",
        lingshi_attr_14: "法防≥",
        lingshi_attr_17: "抗封≥",
        lingshi_attr_18: "格挡≥",
        lingshi_attr_16: "抗法爆≥",
        lingshi_attr_15: "抗物爆≥"
    };
    var RoleStatus = {
        xian_yu: "仙玉≥",
        cash: "现金≥",
        upexp: "当前经验≥",
        badness: "善恶≥",
        school_offer: "门贡≥",
        org_offer: "帮贡≥",
        cheng_jiu: "成就≥",
        body_caiguo: "染色折合彩效果数≥",
        all_caiguo: "所有染色折算彩果数≥",
        box_caiguo: "保存染色方案数≥",
        clothes_num: "锦衣数量≥",
        energy: "精力≥",
        pride: "人气≥",
        learn_cash: "储备金≥",
        pet_extend_num: "召唤兽栏扩展个数≥",
        baggage_extend_num: "行囊扩展个数≥",
        sword_score: "剑会积分≥",
        hero_score: "比武积分≥",
        sheng_yu_ling_you: "剩余灵佑次数≥",
        rider_exgrow_full_num: "满成长坐骑数（后天成长1.0）≥",
        sbook_skill_num: "召唤兽心得技能≥"
    };
    var MarriedHouse = {
        has_community: "社区",
        fangwu_level: "房屋",
        tingyuan_level: "庭院",
        muchang_level: "牧场",
        is_married: "婚否",
        is_tongpao: "同袍"
    };
    var RoleSelfXiuLian = {
        expt_gongj: "攻击修炼≥",
        expt_fangyu: "防御修炼≥",
        expt_fashu: "法术修炼≥",
        expt_kangfa: "抗法修炼≥",
        expt_total: "修炼总和≥",
        expt_lieshu: "猎术修炼≥",
        max_expt_gongji: "攻击上限≥",
        max_expt_fangyu: "防御上限≥",
        max_expt_fashu: "法术上限≥",
        max_expt_kangfa: "抗法上限≥"
    };
    var PetControlXiuLian = {
        bb_expt_gongji: "攻击控制≥",
        bb_expt_fangyu: "防御控制≥",
        bb_expt_fashu: "法术控制≥",
        bb_expt_kangfa: "抗法控制≥",
        bb_expt_total: "宠修总和≥",
        skill_drive_pet: "育兽术≥"
    };
    var ShiMenSkill = {
        school_skill_num: "任意数",
        school_skill_level: "技能等级≥",
        lin_shi_fu: "临时符技能≥",
        qian_yuan_dan: "乾元丹个数≥",
        smith_skill: "打造熟练度≥",
        sew_skill: "裁缝熟练度≥"
    };
    var EwaiAttr = {
        qian_neng_guo: "潜能果数≥",
        jiyuan_and_addpoint: "属性总和(机缘属性+月饼粽子)≥",
        ji_yuan_point: "属性总和(机缘属性)≥",
        addon_point: "属性总和(月饼粽子)≥"
    };
    var LiveSkill = {
        skill_qiang_shen: "强身≥",
        skill_shensu: "神速≥",
        skill_qiang_zhuang: "强健≥",
        skill_ming_xiang: "冥想≥",
        skill_dazao: "打造技巧≥",
        skill_pengren: "烹饪技巧≥",
        skill_caifeng: "裁缝技巧≥",
        skill_zhongyao: "中药医疗≥",
        skill_qiaojiang: "巧匠之术≥",
        skill_lingshi: "灵石技巧≥",
        skill_lianjin: "炼金术≥",
        skill_jianshen: "健身术≥",
        skill_yangsheng: "养生之道≥",
        skill_anqi: "暗器技巧≥",
        skill_taoli: "逃离技巧≥",
        skill_zhuibu: "追捕技巧≥",
        skill_ronglian: "熔炼技巧≥",
        skill_cuiling: "淬灵之术≥",
        skill_wind_sense: "风之感应≥",
        skill_rain_sense: "雨之感应≥",
        skill_snow_sense: "雪之感应≥"
    };
    var JuQingSkill = {
        skill_danyuan: "丹元济会≥",
        skill_miaoshou: "妙手空空≥",
        skill_xianling: "仙灵店铺≥",
        skill_jianzhu: "建筑之术≥",
        skill_baoshi: "宝石工艺≥",
        skill_bianhua: "变化之术≥",
        skill_qimen: "奇门遁甲≥",
        skill_huoyan: "火眼金睛≥",
        skill_gudong: "古董评估≥",
        skill_tiaoxi: "调息≥",
        skill_dazuo: "打坐≥",
        skill_hanmo: "翰墨之道≥",
        skill_danqing: "丹青之道≥"
    };
    var RecentSearchConfig = new Class({
        Extends: CreateConfig,
        initialize: function(arg) {
            this.arg = arg;
            this.parent(arg);
        },
        get_config: function() {
            var ctx = this;
            var arg = ctx.arg;
            return [ctx.list({
                name: "门派",
                key: "school",
                listConfig: SchoolNameInfo,
                elem: $("school_list"),
                isLiHasDataValue: true
            }), ctx.list({
                name: "历史门派",
                key: "school_change_list",
                listConfig: Object.merge(SchoolNameInfo, {
                    "0": "无历史门派"
                }),
                elem: $("school_change_list"),
                isLiHasDataValue: true
            }), ctx.list({
                name: "角色",
                key: "race",
                listConfig: RoleKindNameInfo,
                elem: $("race_list"),
                isLiHasDataValue: true
            }), ctx.list({
                name: "原始种族",
                key: "ori_race",
                listConfig: {
                    1: "人",
                    2: "魔",
                    3: "仙"
                },
                elem: $("ori_race_list"),
                isLiHasDataValue: true
            }), ctx.range({
                name: "人物等级",
                key: "level_min",
                elem: "level_min"
            }), ctx.range({
                name: "价格",
                key: "price_min",
                elem: "txt_price_min"
            }), ctx.range({
                name: "角色总经验",
                key: "sum_exp_min",
                elem: "sum_exp_min"
            }), {
                name: "飞升/渡劫/化圣",
                get_val: function() {
                    var desc = "";
                    if (arg.hasOwnProperty("zhuang_zhi")) {
                        var value = arg["zhuang_zhi"];
                        if (value) {
                            if (value == 1) {
                                desc = "已飞升";
                            } else if (value == 2) {
                                desc = "已渡劫";
                            } else {
                                var hsType = $$("#zhuang_zhi_hua_sheng_select option[value=" + value + "]")[0].get("text");
                                desc = "已化圣/化圣境界≥" + hsType;
                            }
                        }
                    }
                    return desc;
                },
                set_val: function() {
                    if (arg.hasOwnProperty("zhuang_zhi")) {
                        var value = arg["zhuang_zhi"];
                        if (value.length > 2 || value > 2) {
                            $('zhuang_zhi_hua_sheng').set({
                                'checked': true,
                                'value': value
                            });
                            $('huashengSelect').removeClass('disabled');
                            var $zhuangZhiSelect = $('zhuang_zhi_hua_sheng_select');
                            $zhuangZhiSelect.set('disabled', false);
                            $zhuangZhiSelect.set('value', value);
                        } else {
                            $$('.zhuang_zhi[value=' + value + ']').set('checked', true);
                        }
                    }
                }
            }, ctx.input_group({
                name: "基础属性",
                inputConfig: BasicSubType
            }), {
                name: "额外属性",
                get_val: ctx.get().input_group(EwaiAttr),
                set_val: function() {
                    if (arg.hasOwnProperty("ji_yuan_point")) {
                        $('ji_yuan_point').addClass('on');
                        $('jiyuan_and_addpoint').set('value', arg["ji_yuan_point"]);
                    }
                    if (arg.hasOwnProperty("addon_point")) {
                        $('addon_point').addClass('on');
                        $('jiyuan_and_addpoint').set('value', arg["addon_point"]);
                    }
                    if (arg.hasOwnProperty("jiyuan_and_addpoint")) {
                        $('jiyuan_and_addpoint').set('value', arg["jiyuan_and_addpoint"]);
                        $$('#ji_yuan_point,#addon_point').addClass('on');
                    }
                    ctx.set().input("qian_neng_guo", "qian_neng_guo");
                }
            }, {
                name: "属性点保存方案",
                get_val: ctx.get().select("attr_point_strategy", "attr_point_strategy"),
                set_val: ctx.set().select.bind(ctx, ["attr_point_strategy", "attr_point_strategy"])
            }, ctx.input_group({
                name: "角色自身修炼",
                inputConfig: RoleSelfXiuLian
            }), ctx.input_group({
                name: "召唤兽控制修炼",
                inputConfig: PetControlXiuLian
            }), ctx.input_group({
                name: "师门技能",
                inputConfig: ShiMenSkill
            }), ctx.input_group({
                name: "生活技能",
                inputConfig: LiveSkill
            }), ctx.input_group({
                name: "剧情技能",
                inputConfig: JuQingSkill
            }), {
                name: "身上装备",
                get_val: function() {
                    var desc = [];
                    var bodyEquipDesc = ctx.get().input_group(BodyEquipSubType);
                    var equipLevelDesc = ctx.get().range("equip_level_min", "equip_level_min");
                    if (bodyEquipDesc != "") {
                        desc.push(bodyEquipDesc);
                    }
                    if (equipLevelDesc != "") {
                        desc.push("装备等级:" + equipLevelDesc);
                    }
                    if (arg.hasOwnProperty("teji_list")) {
                        var matchDesc = arg.hasOwnProperty("teji_match_all") ? "满足全部" : "满足一种";
                        var text = "特技:" + matchDesc + " " + ctx.get().list("teji_list", $$("#equip_teji li"), true);
                        desc.push(text);
                    }
                    if (arg.hasOwnProperty("texiao_list")) {
                        var matchDesc = arg.hasOwnProperty("texiao_match_all") ? "满足全部" : "满足一种";
                        var text = "特效:" + matchDesc + " " + ctx.get().list("texiao_list", $$("#equip_texiao li"), true);
                        desc.push(text);
                    }
                    if (arg.hasOwnProperty("own_equips_equip_kind_id")) {
                        var text = "装备类型:" + ctx.get().list("own_equips_equip_kind_id", $$("#equip_type_list li"), true);
                        desc.push(text);
                    }
                    var duanzaoLevel = get_duan_zao_desc(arg, "equip_duanzao_attr.lv_");
                    if (duanzaoLevel != "") {
                        desc.push("锻造等级：至少有" + duanzaoLevel[1] + "件≥" + duanzaoLevel[0] + "锻的装备");
                    }
                    if (arg.hasOwnProperty("taozhuang_type") || arg.hasOwnProperty("taozhuang_num")) {
                        var type = arg["taozhuang_type"];
                        type = type ? $$("#taozhuang_type option[value=" + type + "]").get("text") : "不限";
                        var num = arg["taozhuang_num"] || "不限";
                        desc.push("至少有" + num + "件" + type + "装备套装");
                    }
                    if (arg.hasOwnProperty("special_equip_max_level")) {
                        var equipLevel = arg["special_equip_max_level"];
                        desc.push("至少有1件专用装备：等级≥" + equipLevel);
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().input_group(BodyEquipSubType);
                    ctx.set().select("equip_level_min", "equip_level_min");
                    ctx.set().select("equip_level_max", "equip_level_max");
                    ctx.set().select("taozhuang_num", "taozhuang_num");
                    ctx.set().select("taozhuang_type", "taozhuang_type");
                    ctx.set().list({
                        key: "teji_list",
                        elem: $("equip_teji"),
                        isLiHasDataValue: true
                    });
                    ctx.set().list({
                        key: "texiao_list",
                        elem: $("equip_texiao"),
                        isLiHasDataValue: true
                    });
                    ctx.set().list({
                        key: "own_equips_equip_kind_id",
                        elem: $("equip_type_list"),
                        isLiHasDataValue: true
                    });
                    set_duan_zao_desc(arg);
                    if (arg.hasOwnProperty("teji_match_all")) {
                        $$("input[name=teji_match_all][value=" + arg["teji_match_all"] + "]").set("checked", true);
                    }
                    if (arg.hasOwnProperty("texiao_match_all")) {
                        $$("input[name=texiao_match_all][value=" + arg["texiao_match_all"] + "]").set("checked", true);
                    }
                    if (arg.hasOwnProperty("special_equip_max_level")) {
                        $("special_equip_one").set("checked", true);
                        $("special_equip_max_level").set("value", arg["special_equip_max_level"]);
                    }
                }
            }, {
                name: "身上灵饰",
                get_val: function() {
                    var desc = [];
                    var lingshiLevelDesc = ctx.get().range("lingshi_min_level", "lingshi_min_level");
                    var duanzaoLevelDesc = ctx.get().range("lingshi_min_duanzao_level", "lingshi_min_duanzao_level");
                    if (lingshiLevelDesc != "") {
                        desc.push("灵饰等级:" + lingshiLevelDesc);
                    }
                    if (duanzaoLevelDesc != "") {
                        desc.push("锻造等级:" + duanzaoLevelDesc);
                    }
                    var matchDesc = arg.hasOwnProperty("lingshi_attr_match_all") ? "满足全部" : "满足一种";
                    var lingshiAttrDesc = ctx.get().input_group(LingshiAttr);
                    if (lingshiAttrDesc != "") {
                        desc.push("属性总条目:" + matchDesc + "," + lingshiAttrDesc);
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().select("lingshi_min_level", "lingshi_min_level");
                    ctx.set().select("lingshi_max_level", "lingshi_max_level");
                    ctx.set().select("lingshi_min_duanzao_level", "lingshi_min_duanzao_level");
                    ctx.set().select("lingshi_max_duanzao_level", "lingshi_max_duanzao_level");
                    ctx.set().input_group(LingshiAttr);
                    if (arg.hasOwnProperty("lingshi_attr_match_all")) {
                        $("lingshi_attr_match_all").set("checked", true);
                    }
                }
            }, {
                name: "身上召唤兽",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("growup_pet_num")) {
                        desc.push("成品召唤兽数量≥" + arg["growup_pet_num"]);
                    }
                    if (arg.hasOwnProperty("pet_type_list")) {
                        var matchDesc = ctx.get().match_rang_list("pet_match_all", "pet_type_list", $$("#pet_type_list li"));
                        desc.push(matchDesc);
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().input("growup_pet_num", "growup_pet_num");
                    ctx.set().list({
                        key: "pet_type_list",
                        elem: $("pet_type_list"),
                        isLiHasDataValue: true
                    })
                    if (arg.hasOwnProperty("pet_match_all")) {
                        $("pet_match_all").set("checked", true);
                    }
                }
            }, {
                name: '神器',
                get_val: function() {
                    var desc = [];
                    var attr = 'data-key';
                    $$('.jsShenqiWrap').forEach(function(el) {
                        var $root = $(el);
                        var key = $root.get(attr);
                        var data = arg[key];
                        if (!data) {
                            return;
                        }
                        try {
                            data = typeof data == 'string' ? JSON.decode(data) : data;
                        } catch (e) {
                            data = {};
                        }
                        var elTitle = $root.getElement('.jsTitle');
                        var res = [];
                        $root.getElements('.jsSelect').forEach(function(select) {
                            var elSelect = $(select)
                              , elInput = elSelect.getNext('.jsInput')
                            elText = elSelect.getPrevious('.jsText');
                            var key1 = elSelect.get(attr)
                              , key2 = elInput.get(attr);
                            if (key2 in data) {
                                res.push(data[key1] + '≥' + data[key2]);
                            }
                        });
                        if (res.length) {
                            desc.push(elTitle.get('text').trim().replace(/套装$/, '') + ' ' + res.join(','));
                        }
                    });
                    return desc.join('; ');
                },
                set_val: function() {
                    $$('.jsShenqiWrap').forEach(function(wrap) {
                        var attr = 'data-key'
                          , elRoot = $(wrap);
                        var key = elRoot.get(attr);
                        var data = arg[key];
                        if (!data) {
                            return;
                        }
                        try {
                            data = typeof data == 'string' ? JSON.decode(data) : data;
                        } catch (e) {
                            data = {};
                        }
                        Object.keys(data).forEach(function(key) {
                            var el = elRoot.getElement('[' + attr + '="' + key + '"]');
                            if (!el) {
                                return;
                            }
                            el.set('value', data[key]);
                        });
                        elRoot.getElements('.jsSelect').fireEvent('change');
                    });
                }
            }, {
                name: '携带孩子:（新版）',
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("child_attr_total_score")) {
                        desc.push("总属性点≥" + arg["child_attr_total_score"]);
                    }
                    if (arg.hasOwnProperty("child_skill_num_min") || arg.hasOwnProperty("child_skill_num_max")) {
                        desc.push('技能数:' + ctx.get().range('child_skill_num_min'));
                    }
                    function fetch_value(text, $list, arr) {
                        var result = [];
                        $list.forEach(function($el) {
                            if (arr.indexOf($el.get('data_value')) >= 0) {
                                result.push($el.get('text').trim());
                            }
                        });
                        return result ? text + ':' + result.join(',') : '';
                    }
                    if (arg.hasOwnProperty("child_ending")) {
                        var text = fetch_value('结局', $$('#child_ending_box li'), arg["child_ending"].split(','));
                        text && desc.push(text);
                    }
                    if (arg.hasOwnProperty("child_school")) {
                        var text = fetch_value('门派', $$('#child_school_box li'), arg["child_school"].split(','));
                        text && desc.push(text);
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().input("child_attr_total_score", "child_attr_total_score");
                    ctx.set().slider({
                        minKey: "child_skill_num_min",
                        maxKey: "child_skill_num_max",
                        defaultRang: [0, 10],
                        elemId: "child_skill_num"
                    });
                    ctx.set().list({
                        key: "child_ending",
                        elem: $("child_ending_box"),
                        isLiHasDataValue: true
                    });
                    ctx.set().list({
                        key: "child_school",
                        elem: $("child_school_box"),
                        isLiHasDataValue: true
                    });
                }
            }, {
                name: "施法特效",
                get_val: function() {
                    var desc = [];
                    ctx.get().list("perform_effect", $$("#perform_effect_list li"), true);
                    if (arg.hasOwnProperty("perform_effect")) {
                        var matchDesc = ctx.get().match_rang_list("perform_match_all", "perform_effect", $$("#perform_effect_list li"));
                        desc.push(matchDesc);
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().list({
                        key: "perform_effect",
                        elem: $("perform_effect_box"),
                        isLiHasDataValue: true
                    });
                    if (arg.hasOwnProperty("perform_match_all")) {
                        $("perform_match_all").set("checked", true);
                    }
                }
            }, {
                name: "身上祥瑞",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("xiangrui_num")) {
                        desc.push("祥瑞数量≥" + arg["xiangrui_num"]);
                    }
                    if (arg.hasOwnProperty("xiangrui_list")) {
                        var matchDesc = ctx.get().match_rang_list("xiangrui_match_all", "xiangrui_list", $$("#xiangrui_box li"));
                        desc.push(matchDesc);
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().input("xiangrui_num", "xiangrui_num");
                    ctx.set().list({
                        key: "xiangrui_list",
                        elem: $("xiangrui_box"),
                        isLiHasDataValue: true
                    });
                    if (arg.hasOwnProperty("xiangrui_match_all")) {
                        $("xiangrui_match_all").set("checked", true);
                    }
                }
            }, {
                name: "限量锦衣",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("limit_clothes")) {
                        var matchDesc = ctx.get().match_rang_list("limit_clothes_logic", "limit_clothes", $$("#limit_clothes_panel li"));
                        desc.push(matchDesc);
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().list({
                        key: "limit_clothes",
                        elem: $("limit_clothes_panel"),
                        isLiHasDataValue: true
                    })
                    if (arg.hasOwnProperty("limit_clothes_logic")) {
                        $$("input[name=limit_clothes_logic][value=" + arg["limit_clothes_logic"] + "]").set("checked", true);
                    }
                }
            }, {
                name: "挂件",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("widget_list")) {
                        var matchDesc = ctx.get().match_rang_list("widget_match_all", "widget_list", $$("#widget_list_panel li"));
                        desc.push(matchDesc);
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().list({
                        key: "widget_list",
                        elem: $("widget_list_panel"),
                        isLiHasDataValue: true
                    })
                    if (arg.hasOwnProperty("widget_match_all")) {
                        $$("input[name=widget_match_all][value=" + arg["widget_match_all"] + "]").set("checked", true);
                    }
                }
            }, {
                name: "角色状态",
                get_val: function() {
                    var desc = [];
                    var rodeIptDesc = ctx.get().input_group(RoleStatus);
                    if (rodeIptDesc != "") {
                        desc.push(rodeIptDesc);
                    }
                    if (arg.hasOwnProperty("is_niceid_new")) {
                        var text = $$("#is_niceid_new option[value=" + arg["is_niceid_new"] + "]").get("text");
                        desc.push("靓号ID:" + text);
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().input_group(RoleStatus);
                    ctx.set().select("is_niceid_new", "is_niceid_new");
                }
            }, {
                name: "婚姻房屋",
                get_val: function() {
                    var desc = [];
                    for (var key in MarriedHouse) {
                        if (arg.hasOwnProperty(key)) {
                            desc.push(MarriedHouse[key] + ":" + ctx.get().select(key, key));
                        }
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().input_group(MarriedHouse);
                }
            }, {
                name: "携带玄灵珠",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty('rider_plan')) {
                        var value = arg["rider_plan"];
                        var arr = value.split(',');
                        if (arr && arr.length && arr.length > 1) {
                            let str = arr[0] == 1 ? "回春" : "破军";
                            desc.push("类型:" + str + ',等级:' + arr[1]);
                        }
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    if (arg.hasOwnProperty('rider_plan')) {
                        var value = arg["rider_plan"];
                        var arr = value.split(',');
                        if (arr && arr.length && arr.length > 1) {
                            $("xuan_ling_zhu_type").set("value", arr[0]);
                            $("xuan_ling_zhu_level").set('disabled', false);
                            $("xuan_ling_zhu_level").set("value", arr[1]);
                        }
                    }
                }
            }, {
                name: "转至某服",
                get_val: function() {
                    var desc = "";
                    if (arg.hasOwnProperty("switchto_serverid") || arg.hasOwnProperty("cross_buy_serverid")) {
                        var value = arg["switchto_serverid"] || arg["cross_buy_serverid"];
                        for (var areaid in server_data) {
                            var server_list = server_data[areaid][1];
                            for (var server in server_list) {
                                if (server_list[server][0] == value) {
                                    var area = server_data[areaid][0][0];
                                    var serverDetail = server_list[server][1];
                                    desc = "可转至" + area + serverDetail + "服务器";
                                    break;
                                }
                            }
                        }
                    }
                    return desc;
                },
                set_val: function() {
                    if (arg.hasOwnProperty("switchto_serverid")) {
                        var value = arg["switchto_serverid"];
                        var serverData = server_data;
                        for (var key in serverData) {
                            var serverConfig = serverData[key];
                            var servers = serverConfig[1];
                            for (var i = 0; i < servers.length; i++) {
                                var configServerId = servers[i][0];
                                if (value == configServerId) {
                                    var areaText = serverConfig[0][0];
                                    var areaId = serverConfig[0][4];
                                    var serverName = servers[i][1];
                                    $('sel_area').set('value', areaId);
                                    var optionElem = new Element('option',{
                                        value: value,
                                        text: serverName,
                                        selected: "selected"
                                    });
                                    $('switchto_serverid').grab(optionElem);
                                    break;
                                }
                            }
                        }
                    }
                }
            }, {
                name: "开服时间",
                get_val: ctx.get().list("server_type", $$("#server_type li"), true),
                set_val: ctx.set().list.bind(ctx, {
                    key: "server_type",
                    elem: $("server_type"),
                    isLiHasDataValue: true
                })
            }]
        }
    });
    function get_duan_zao_desc(arg, attr_) {
        for (var key in arg) {
            var reg = new RegExp("" + attr_ + "","g");
            var re = key.match(reg);
            if (re != null) {
                var val = arg[key];
                var num = key.replace(reg, "");
                return [num, val];
            }
        }
        return "";
    }
    function set_duan_zao_desc(arg) {
        var attr = 'equip_duanzao_attr.lv_';
        for (var key in arg) {
            var reg = new RegExp("" + attr + "","g");
            var re = key.match(reg);
            if (re != null) {
                var val = arg[key];
                $('duanzao_num').set('value', val);
                $('duanzao_attr').set('value', key);
                break;
            }
        }
    }
    window.RecentSearchConfig = RecentSearchConfig;
}
)();
