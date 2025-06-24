var OverallSearchAct = 'overall_search_pet';
var PetSkills = AUTO_SEARCH_CONFIG.pet_skills_for_search;
var ServerTypes = [[3, '3年以上服'], [2, '1到3年服'], [1, '1年内服']];
var FairShowStatus = [[1, '已上架'], [0, '公示期']];
var FrontStatus = [['pass_fair_show', '已上架'], ['fair_show', '公示期']]
var HighNeidans = changeObjectToArray(AUTO_SEARCH_CONFIG.high_neidans);
var LowNeidans = changeObjectToArray(AUTO_SEARCH_CONFIG.low_neidans);
var cifuSkills = AUTO_SEARCH_CONFIG.pet_web_evol_skill_options || [];
var Colors = [[1, '&nbsp;1&nbsp;'], [2, '&nbsp;2&nbsp;']];
var MengYingConf = changeObjectToArray(AUTO_SEARCH_CONFIG.pet_mengying);
var TexingTypes = AUTO_SEARCH_CONFIG.texing_type_list || changeObjectToArray(AUTO_SEARCH_CONFIG.texing_types);
var TexingPositiveEffectTypes = changeObjectToArray(AUTO_SEARCH_CONFIG.texing_poistive_effect_types);
var FightLevels = changeObjectToArray(AUTO_SEARCH_CONFIG.fight_levels);
var OverallPetSearcher = new Class({
    initialize: function() {
        this.init_equal_advanced_skill_panel($('pet_equal_advanced_skill_panel'));
        this.server_type_checker = new ButtonChecker(ServerTypes,$('server_type_panel'));
        this.front_status_checker = new ButtonChecker(FrontStatus,$('fair_show_panel'));
        this.high_neidan_checker = new ButtonChecker(HighNeidans,$('high_neidan_panel'));
        this.cifu_skills_checker = new ButtonChecker(cifuSkills,$('limit_evol_panel'));
        this.low_neidan_checker = new ButtonChecker(LowNeidans,$('low_neidan_panel'));
        this.color_checker = new ButtonChecker(Colors,$('color_panel'));
        this.mengying_checker = new ButtonChecker(MengYingConf,$('mengying_panel'));
        this.select_server = new OverallAppointServer(this.server_type_checker);
        this.init_pet_select_box();
        this.reg_event();
        this.init_search_btn();
        this.init_role_search_event();
        this.init_reset_btn();
        this.texing_checker = new ButtonChecker(TexingTypes,$('texing_panel'));
        this.positive_effect_checker = new ButtonChecker(TexingPositiveEffectTypes,$('positive_effect_panel'));
        this.negative_effect_checker = new ButtonChecker(TexingPositiveEffectTypes,$('negative_effect_panel'));
        this.fight_level_checker = new ButtonChecker(FightLevels,$('fight_level_panel'));
        this.init_skill_tips();
        this.init_pet_skill();
    },
    init_pet_skill: function() {
        var conf = [{
            id: 'pet_skill_special_panel',
            checker_name: 'skill_special_checker',
            data: AUTO_SEARCH_CONFIG.pet_skills_special || []
        }, {
            id: 'pet_skill_fashu_panel',
            checker_name: 'skill_fashu_checker',
            data: AUTO_SEARCH_CONFIG.pet_skills_mag_high || []
        }, {
            id: 'pet_skill_wuli_panel',
            checker_name: 'skill_wuli_checker',
            data: AUTO_SEARCH_CONFIG.pet_skills_phy_high || []
        }, {
            id: 'pet_skill_tongyong_panel',
            checker_name: 'skill_tongyong_checker',
            data: AUTO_SEARCH_CONFIG.pet_skills_common_high || []
        }, {
            id: 'pet_skill_shenshou_panel',
            checker_name: 'skill_shenshou_checker',
            data: AUTO_SEARCH_CONFIG.pet_god_skills_special || []
        }, {
            id: 'pet_skill_primary_panel',
            checker_name: 'skill_primary_checker',
            data: AUTO_SEARCH_CONFIG.pet_skills_low || []
        }, {
            id: 'pet_skill_super_panel',
            checker_name: 'skill_supersssss_checker',
            data: AUTO_SEARCH_CONFIG.pet_web_super_skill_options || []
        }];
        this.pet_skill_conf = conf;
        var ctx = this;
        for (var i = 0; i < conf.length; i++) {
            var item = conf[i];
            var notSkillId = 'not_' + item.id;
            var notCheckName = 'not_' + item.checker_name;
            var data = item.data;
            ctx[item.checker_name] = new PetSkillButtonChecker(data,$(item.id));
            if (notSkillId == 'not_pet_skill_primary_panel') {
                data = AUTO_SEARCH_CONFIG.pet_skills_low_for_not_exist || [];
            }
            ctx[notCheckName] = new PetSkillButtonChecker(data,$(notSkillId));
        }
    },
    init_skill_tips: function() {
        if (LoginInfo && LoginInfo.login) {
            if (!StoreDB.getItem('not_include_skill_tips')) {
                $('not_include_tips').setStyle('display', '');
            } else {
                $('not_include_tips').setStyle('display', 'none');
            }
        }
    },
    init_equal_advanced_skill_panel: function(panel) {
        var skills = '夜战 感知 吸血 必杀 连击 偷袭 法术连击 法术暴击 法术波动 魔之心 幸运 反震 强力 驱鬼 防御 敏捷 毒'.split(' ');
        var skill_to_id = {};
        PetSkills.each(function(item) {
            skill_to_id[item[1]] = item[0];
        });
        var skills_button_config = [];
        for (var i = 0; i < skills.length; i++) {
            skills_button_config.push([skill_to_id[skills[i]], skills[i]]);
        }
        this.low_skill_checker = new PetSkillButtonChecker(skills_button_config,panel);
    },
    init_reset_btn: function() {
        var __this = this;
        $('reset_basic').addEvent('click', function() {
            __this.reset_basic();
        });
        $('reset_detail').addEvent('click', function() {
            __this.reset_detail();
        });
        $('reset_server_info').addEvent('click', function() {
            __this.reset_server_info();
        });
        $('reset_all').addEvent('click', function() {
            __this.reset_basic();
            __this.reset_detail();
            __this.reset_server_info();
        });
    },
    reset_basic: function() {
        var checkers = [this.front_status_checker, this.fight_level_checker, this.low_skill_checker];
        var ctx = this;
        var pet_skill_conf = this.pet_skill_conf;
        for (var i = 0; i < pet_skill_conf.length; i++) {
            var item = pet_skill_conf[i];
            checkers.push(ctx[item.checker_name]);
            checkers.push(ctx['not_' + item.checker_name]);
        }
        var txt_inputs = [$('txt_level_min'), $('txt_level_max'), $('pet_select_box'), $('txt_skill_num'), $('txt_growth'), $('txt_used_lianshou_max'), $('txt_used_yuanxiao_max'), $('txt_valid_evol_skill_num'), $('txt_attack_aptitude'), $('txt_defence_aptitude'), $('txt_physical_aptitude'), $('txt_magic_aptitude'), $('txt_speed_aptitude_min'), $('txt_speed_aptitude_max'), $('txt_price_min'), $('txt_price_max')];
        var chkbox_inputs = [$('chk_skill_with_suit'), $('chk_suit_as_any_skill'), $('chk_skill_including_advanced'), $('chk_advanced_evol_skill'), $('no_include_sp_skill'), $('evol_skill_mode')];
        this.reset(checkers, txt_inputs, chkbox_inputs);
    },
    reset_detail: function() {
        var checkers = [this.cifu_skills_checker, this.high_neidan_checker, this.low_neidan_checker, this.color_checker, this.texing_checker, this.positive_effect_checker, this.negative_effect_checker, this.mengying_checker];
        var txt_inputs = [$('txt_max_blood'), $('txt_attack'), $('txt_defence'), $('txt_speed_min'), $('txt_speed_max'), $('txt_lingxing'), $('txt_high_neidan_level'), $('txt_low_neidan_level'), $('txt_fashang'), $('txt_fafang')];
        var chkbox_inputs = [$('chk_is_baobao'), $('chk_summon_color')];
        this.reset(checkers, txt_inputs, chkbox_inputs);
    },
    reset_server_info: function() {
        var checkers = [this.server_type_checker, this.select_server];
        this.reset(checkers, []);
    },
    reset: function(checkers, txt_inputs, chkbox_inputs) {
        for (var i = 0; i < checkers.length; i++) {
            checkers[i].reset_value();
        }
        for (var i = 0; i < txt_inputs.length; i++) {
            txt_inputs[i].set('value', '');
        }
        if (chkbox_inputs) {
            for (var i = 0; i < chkbox_inputs.length; i++)
                chkbox_inputs[i].checked = false;
        }
    },
    init_pet_select_box: function() {
        var handle_pet_search = function(keyword) {
            var result = new Array();
            for (var pet_type in SaleablePetNameInfo) {
                if (SaleablePetNameInfo[pet_type].indexOf(keyword) != -1) {
                    var type_name = SaleablePetNameInfo[pet_type];
                    if (result.indexOf(type_name) == -1) {
                        result.push(type_name);
                    }
                }
            }
            return result;
        };
        new AutoComplete($('pet_select_box'),{
            "startPoint": 1,
            "promptNum": 20,
            "handle_func": handle_pet_search,
            "callback": function() {}
        });
    },
    get_pet_type_value: function() {
        var result = [];
        var pet_name = $('pet_select_box').value;
        if (!pet_name) {
            return null;
        }
        for (var pet_type in SaleablePetNameInfo) {
            if (SaleablePetNameInfo[pet_type] == pet_name) {
                result.push(pet_type);
            }
        }
        return result.join(',');
    },
    reg_event: function() {
        var __this = this;
        function expand_skill($this, $list) {
            if ($this.retrieve('spread')) {
                return;
            }
            $list.setStyle('height', 'auto');
            $this.store('spread', true);
            $this.setStyle('display', 'none');
        }
        $('btn_all_skill').addEvent('click', function() {
            expand_skill($(this), $('pet_skill_primary_panel'));
        });
        $('btn_not_all_skill').addEvent('click', function() {
            expand_skill($(this), $('not_pet_skill_wrap'));
        });
        function toogleSkill($this, $toogleElem, text) {
            var skillId = $this.get('data-skill_id');
            var $opposite = $toogleElem.getElement('li[data-skill_id=' + skillId + ']');
            if ($toogleElem.length) {
                for (var i = 0; i < $toogleElem.length; i++) {
                    $opposite = $toogleElem[i].getElement('li[data-skill_id=' + skillId + ']');
                    if ($opposite) {
                        break;
                    }
                }
            }
            if (!$opposite) {
                return;
            }
            if ($this.hasClass('disable') || $opposite.hasClass('on')) {
                new ToastTip(text).show();
                $this.removeClass('on');
            } else if ($this.hasClass('on')) {
                $opposite.addClass('disable');
            } else {
                $opposite.removeClass('disable');
            }
        }
        var $includeList = $$('#pet_skill_wrap .js_include_pet_skill');
        var $notIncludeList = $$('#not_pet_skill_wrap .js_not_include_pet_skill');
        $includeList.addEvent('click:relay(li)', function() {
            toogleSkill($(this), $notIncludeList, '此技能已被不包含技能选中');
        });
        $notIncludeList.addEvent('click:relay(li)', function() {
            toogleSkill($(this), $includeList, '此技能已被包含技能选中');
        });
        var chka = $('chk_skill_with_suit');
        var chkb = $('chk_suit_as_any_skill');
        var clearb = function() {
            if (chka.checked)
                chkb.checked = false;
        }
        var cleara = function() {
            if (chkb.checked)
                chka.checked = false;
        }
        chka.addEvent('change', clearb);
        chkb.addEvent('change', cleara);
        chka.getParent('label').addEvent('click', clearb);
        chkb.getParent('label').addEvent('click', cleara);
        $('btn_tips_know').addEvent('click', function() {
            StoreDB.setItem('not_include_skill_tips', 1);
            $('not_include_tips').setStyle('display', 'none');
        });
    },
    init_search_btn: function() {
        var __this = this;
        $('btn_pet_search').addEvent('click', function() {
            __this.search();
        });
    },
    init_role_search_event: function() {
        var __this = this;
        $('link_search_related_role').addEvent('click', function() {
            __this.search(function(args) {
                document.query_form.search_act.value = "overall_search_role_by_pet";
                $('query_args').value = JSON.encode(args);
                document.query_form.submit();
            });
        });
    },
    get_skill_value: function(arg) {
        var cxt = this;
        var pet_skill_conf = this.pet_skill_conf;
        var skillResult = [];
        var notSkillResult = [];
        for (var i = 0; i < pet_skill_conf.length; i++) {
            var item = pet_skill_conf[i];
            var skillVal = cxt[item.checker_name].get_value();
            var notSkillVal = cxt['not_' + item.checker_name].get_value();
            if (skillVal) {
                skillResult.push(skillVal)
            }
            if (notSkillVal) {
                notSkillResult.push(notSkillVal)
            }
        }
        if (skillResult.length) {
            arg['skill'] = skillResult.join(',');
        }
        if (notSkillResult.length) {
            arg['not_in_skill'] = notSkillResult.join(',');
        }
        return arg;
    },
    search: function(func) {
        var arg = {};
        if ($('pet_select_box').value) {
            var pet_type = this.get_pet_type_value();
            if (!pet_type) {
                alert('不存在你要搜的召唤兽名称');
                return false;
            }
            arg['type'] = pet_type;
        }
        var check_items = [['low_skill', this.low_skill_checker, false], ['front_status', this.front_status_checker, true], ['server_type', this.server_type_checker, true], ['color', this.color_checker, false], ['mengying', this.mengying_checker, false], ['texing', this.texing_checker, false], ['positive_effect', this.positive_effect_checker, false], ['negative_effect', this.negative_effect_checker, false], ['kindid', this.fight_level_checker, true]];
        arg = this.get_skill_value(arg);
        for (var i = 0; i < check_items.length; i++) {
            var item = check_items[i];
            if (item[2] && item[1].is_check_all()) {
                continue;
            }
            var value = item[1].get_value();
            if (value) {
                arg[item[0]] = value;
            }
        }
        var high_neidan_values = this.high_neidan_checker.get_value();
        var low_neidan_values = this.low_neidan_checker.get_value();
        var cifu_skills_values = this.cifu_skills_checker.get_value();
        if (high_neidan_values.length)
            arg['high_neidan'] = high_neidan_values;
        if (low_neidan_values.length)
            arg['low_neidan'] = low_neidan_values;
        if (cifu_skills_values.length) {
            arg['evol_skill'] = cifu_skills_values;
        }
        if ($('chk_skill_with_suit').checked) {
            arg['skill_with_suit'] = 1;
        }
        if ($('evol_skill_mode').checked) {
            arg['evol_skill_mode'] = 1;
        } else {
            arg['evol_skill_mode'] = 0;
        }
        if ($('chk_suit_as_any_skill').checked) {
            arg['suit_as_any_skill'] = 1;
        }
        if ($('chk_skill_including_advanced').checked) {
            arg['skill_including_advanced'] = 1;
        }
        if ($('chk_advanced_evol_skill').checked) {
            arg['advanced_evol_skill'] = 1;
        }
        if ($('chk_is_baobao').checked) {
            arg['is_baobao'] = 1;
        }
        if ($('chk_summon_color').checked) {
            arg['summon_color'] = 1;
        }
        var txt_int_items = [['level_min', 0, 180, '等级'], ['level_max', 0, 180, '等级'], ['skill_num', 0, 10000, '技能数量'], ['valid_evol_skill_num', 0, 4, '有效赐福技能数'], ['attack_aptitude', 0, 10000, '攻击资质'], ['defence_aptitude', 0, 10000, '防御资质'], ['physical_aptitude', 0, 10000, '体力资质'], ['magic_aptitude', 0, 10000, '法力资质'], ['speed_aptitude_min', 0, 10000, '速度资质'], ['speed_aptitude_max', 0, 10000, '速度资质'], ['price_min', 0, MaxTradeYuan, '价格'], ['price_max', 0, MaxTradeYuan, '价格'], ['max_blood', 0, 20000, '气血'], ['attack', 0, 4000, '攻击'], ['defence', 0, 4000, '防御'], ['speed_min', 0, 2000, '速度'], ['speed_max', 0, 2000, '速度'], ['fashang', 0, 99999, '法伤'], ['fafang', 0, 99999, '法防'], ['lingxing', 0, 10000, '灵性'], ['used_lianshou_max', 0, Infinity, '已使用炼兽珍经数量'], ['used_yuanxiao_max', 0, Infinity, '已使用元宵数量'], ['high_neidan_level', 0, Infinity, '高级内丹层数'], ['low_neidan_level', 0, Infinity, '低级内丹层数']];
        var intReg = /^\d+$/;
        for (var i = 0; i < txt_int_items.length; i++) {
            var item = txt_int_items[i];
            var el = $('txt_' + item[0]);
            var value = el.value;
            if (!value) {
                continue;
            }
            if (!intReg.test(value)) {
                alert(item[3] + '必须是整数');
                el.focus();
                return;
            }
            if (!(item[1] <= parseInt(value) && parseInt(value) <= item[2])) {
                alert(item[3] + '超出取值范围:' + item[1] + '-' + item[2]);
                el.focus();
                return;
            }
            arg[item[0]] = parseInt(value);
        }
        if (arg['price_min'] > arg['price_max']) {
            alert('最低价格不能大于最高价格');
            return;
        }
        if (arg['price_min']) {
            arg['price_min'] = arg['price_min'] * 100;
        }
        if (arg['price_max']) {
            arg['price_max'] = arg['price_max'] * 100;
        }
        var growth = $('txt_growth').value;
        if (growth) {
            if (!/^\d\.\d{1,3}$/.test(growth)) {
                alert('成长值错误, 最多3位小数');
                return false;
            } else {
                arg['growth'] = parseInt(parseFloat(growth) * 1000);
            }
        }
        if (this.select_server.get_serverid()) {
            arg['serverid'] = this.select_server.get_serverid();
        }
        if (arg["skill_num"] && arg["skill_num"] > 0 && $('no_include_sp_skill').checked) {
            arg['no_include_sp_skill'] = 1;
        }
        if ($("user_serverid") && $("user_serverid").value) {
            arg['cross_buy_serverid'] = $("user_serverid").value;
            window.server_selector && server_selector.update_recent_server_list();
        }
        save_args_in_cookie(arg, "overall_pet_search");
        var f = func || go_overall_search;
        f(arg);
    }
});
;(function() {
    if (typeof CreateConfig == 'undefined') {
        return;
    }
    var ZiZhi = {
        attack_aptitude: "攻击资质≥",
        defence_aptitude: "防御资质≥",
        physical_aptitude: "体力资质≥",
        magic_aptitude: "法力资质≥",
        speed_aptitude_min: "速度资质≥",
        speed_aptitude_max: "速度资质≤"
    };
    var ShuXing = {
        max_blood: "气血≥",
        attack: "攻击≥",
        defence: "防御≥",
        speed_max: "速度≤",
        speed_min: "速度≥",
        fashang: "法伤≥",
        fafang: "法防≥"
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
            return [{
                name: "类型",
                get_val: function() {
                    var desc = "";
                    if (arg.hasOwnProperty("type")) {
                        var value = +arg["type"].split(",")[0];
                        desc = SaleablePetNameInfo[value];
                    }
                    return desc;
                },
                set_val: function() {
                    if (arg.hasOwnProperty("type")) {
                        var value = arg["type"].split(",")[0];
                        var text = SaleablePetNameInfo[value];
                        $('pet_select_box').set('value', text);
                    }
                }
            }, ctx.range({
                name: "等级",
                key: "level_min",
                elem: "txt_level_min"
            }), ctx.list({
                name: "参战等级",
                key: "kindid",
                listConfig: FightLevels,
                elem: $$('#fight_level_panel li')
            }), {
                name: "技能",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("skill_with_suit")) {
                        desc.push('含套装技能');
                    }
                    if (arg.hasOwnProperty("suit_as_any_skill")) {
                        desc.push('默认套装为任意选中技能');
                    }
                    if (arg.hasOwnProperty("skill")) {
                        var text = ctx.get().list("skill", PetSkills);
                        desc.push(text)
                    }
                    if (arg.hasOwnProperty("skill_including_advanced")) {
                        desc.push('默认等同对应高级技能');
                    }
                    if (arg.hasOwnProperty("low_skill")) {
                        var text = ctx.get().list("low_skill", PetSkills);
                        desc.push(text)
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().checkbox("skill_with_suit", "chk_skill_with_suit");
                    ctx.set().checkbox("suit_as_any_skill", "chk_suit_as_any_skill");
                    ctx.set().checkbox("skill_including_advanced", "chk_skill_including_advanced");
                    if (arg.hasOwnProperty("skill")) {
                        $("btn_all_skill").fireEvent("click");
                        var skillElemId = ['pet_skill_super_panel', 'pet_skill_special_panel', 'pet_skill_fashu_panel', 'pet_skill_wuli_panel', 'pet_skill_tongyong_panel', 'pet_skill_primary_panel'];
                        for (var i = 0; i < skillElemId.length; i++) {
                            ctx.set().list({
                                key: "skill",
                                elem: $$('#' + skillElemId[i] + ' li')
                            });
                        }
                    }
                    ctx.set().list({
                        key: "low_skill",
                        elem: $$('#pet_equal_advanced_skill_panel li')
                    });
                }
            }, {
                name: "不含技能",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("not_in_skill")) {
                        var text = ctx.get().list("not_in_skill", PetSkills);
                        desc.push(text)
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    if (arg.hasOwnProperty("not_in_skill")) {
                        var skillElemId = ['not_pet_skill_super_panel', 'not_pet_skill_special_panel', 'not_pet_skill_fashu_panel', 'not_pet_skill_wuli_panel', 'not_pet_skill_tongyong_panel', 'not_pet_skill_primary_panel'];
                        for (var i = 0; i < skillElemId.length; i++) {
                            ctx.set().list({
                                key: "not_in_skill",
                                elem: $$('#' + skillElemId[i] + ' li')
                            });
                        }
                    }
                }
            }, {
                name: "概况",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("skill_num")) {
                        if (arg.hasOwnProperty("no_include_sp_skill")) {
                            desc.push("技能数量≥" + arg["skill_num"] + "(不含认证)");
                        } else {
                            desc.push("技能数量≥" + arg["skill_num"]);
                        }
                    }
                    if (arg.hasOwnProperty("valid_evol_skill_num")) {
                        if (arg.hasOwnProperty("advanced_evol_skill")) {
                            desc.push("有效赐福技能数≥" + arg["valid_evol_skill_num"] + "(仅包含高级技能赐福)");
                        } else {
                            desc.push("有效赐福技能数≥" + arg["valid_evol_skill_num"]);
                        }
                    }
                    if (arg.hasOwnProperty("growth")) {
                        desc.push("成长≥" + arg["growth"] / 1000);
                    }
                    var GaiKuan = {
                        used_lianshou_max: "已使用炼兽珍经数量≤",
                        used_yuanxiao_max: "已使用元宵数量≤"
                    };
                    var text = ctx.get().input_group(GaiKuan);
                    if (text != "") {
                        desc.push(text);
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    var GaiKuan = {
                        used_lianshou_max: "",
                        used_yuanxiao_max: "",
                        valid_evol_skill_num: "",
                        skill_num: ""
                    };
                    ctx.set().input_group(GaiKuan, "txt_");
                    ctx.set().checkbox("no_include_sp_skill", "no_include_sp_skill");
                    ctx.set().checkbox("advanced_evol_skill", "chk_advanced_evol_skill");
                    if (arg.hasOwnProperty("growth")) {
                        $("txt_growth").set("value", arg["growth"] / 1000);
                    }
                }
            }, ctx.input_group({
                name: "资质",
                inputConfig: ZiZhi,
                elem: "txt_"
            }), ctx.range({
                name: "价格",
                key: "price_min",
                elem: "txt_price_min"
            }), ctx.list({
                name: "出售状态",
                key: "front_status",
                listConfig: FrontStatus,
                elem: $$('#fair_show_panel li')
            }), ctx.input_group({
                name: "属性",
                inputConfig: ShuXing,
                elem: "txt_"
            }), {
                name: "内丹",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("high_neidan")) {
                        var text = ctx.get().list("high_neidan", HighNeidans);
                        desc.push("高级内丹:" + text);
                    }
                    if (arg.hasOwnProperty("high_neidan_level")) {
                        desc.push('高级内丹层数:' + arg["high_neidan_level"]);
                    }
                    if (arg.hasOwnProperty("low_neidan")) {
                        var text = ctx.get().list("low_neidan", LowNeidans);
                        desc.push("低级内丹:" + text);
                    }
                    if (arg.hasOwnProperty("low_neidan_level")) {
                        desc.push('低级内丹层数:' + arg["low_neidan_level"]);
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().list({
                        key: "high_neidan",
                        elem: $$("#high_neidan_panel li")
                    });
                    ctx.set().list({
                        key: "low_neidan",
                        elem: $$("#low_neidan_panel li")
                    });
                    ctx.set().input("high_neidan_level", "txt_high_neidan_level");
                    ctx.set().input("low_neidan_level", "txt_low_neidan_level");
                }
            }, {
                name: "赐福技能",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("evol_skill")) {
                        var text = ctx.get().list("evol_skill", cifuSkills);
                        desc.push("赐福技能:" + text);
                        if (arg.hasOwnProperty("evol_skill_mode") && arg.evol_skill_mode == 1) {
                            desc.push('满足全部');
                        } else {
                            desc.push('满足一种');
                        }
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().checkbox("evol_skill_mode", "evol_skill_mode");
                    ctx.set().list({
                        key: "evol_skill",
                        elem: $$("#limit_evol_panel li")
                    });
                }
            }, {
                name: "幻色丹染色",
                get_val: function() {
                    var desc = "";
                    if (arg.hasOwnProperty("summon_color")) {
                        desc = "包含";
                    }
                    return desc;
                },
                set_val: ctx.set().checkbox.bind(ctx, ["summon_color", "chk_summon_color"])
            }, {
                name: "只显示宝宝",
                get_val: function() {
                    var desc = "";
                    if (arg.hasOwnProperty("is_baobao")) {
                        desc = "是";
                    }
                    return desc;
                },
                set_val: ctx.set().checkbox.bind(ctx, ["is_baobao", "chk_is_baobao"])
            }, ctx.list({
                name: "变异类型",
                key: "color",
                listConfig: Colors,
                elem: $$('#color_panel li')
            }), {
                name: "特性",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("texing")) {
                        var text = ctx.get().list("texing", TexingTypes);
                        desc.push(text)
                    }
                    if (arg.hasOwnProperty("positive_effect")) {
                        var text = ctx.get().list("positive_effect", TexingPositiveEffectTypes);
                        desc.push("正面效果：" + text);
                    }
                    if (arg.hasOwnProperty("negative_effect")) {
                        var text = ctx.get().list("negative_effect", TexingPositiveEffectTypes);
                        desc.push("负面效果：" + text);
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().list({
                        key: "texing",
                        elem: $$('#texing_panel li')
                    });
                    ctx.set().list({
                        key: "positive_effect",
                        elem: $$('#positive_effect_panel li')
                    });
                    ctx.set().list({
                        key: "negative_effect",
                        elem: $$('#negative_effect_panel li')
                    });
                }
            }, ctx.input_group({
                name: "灵性值",
                inputConfig: {
                    lingxing: "灵性值≥"
                },
                elem: "txt_"
            }), ctx.list({
                name: "开服时间",
                key: "server_type",
                listConfig: ServerTypes,
                elem: $$('#server_type_panel li')
            }), ctx.appoint_server()]
        }
    });
    window.RecentSearchConfig = RecentSearchConfig;
}
)();
