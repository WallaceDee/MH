var OverallSearchAct = 'overall_search_equip';
var EquipKinds = AUTO_SEARCH_CONFIG.weapon_armors;
var SpecialEffects = changeObjectToArray(AUTO_SEARCH_CONFIG.equip_special_effect);
var SpecialSkills = AUTO_SEARCH_CONFIG.equip_special_skills instanceof Array ? AUTO_SEARCH_CONFIG.equip_special_skills : changeObjectToArray(AUTO_SEARCH_CONFIG.equip_special_skills);
var SuitEffects = changeObjectToArray(AUTO_SEARCH_CONFIG.suit_effects);
var SuitAddedStatus = reverseObj(AUTO_SEARCH_CONFIG.suit_added_status);
var SuitAppendSkills = reverseObj(AUTO_SEARCH_CONFIG.suit_append_skills);
var SuitTransformSkills = reverseObj(AUTO_SEARCH_CONFIG.suit_transform_skills);
var SuitTransformCharms = reverseObj(AUTO_SEARCH_CONFIG.suit_transform_charms);
var SumAttrs = changeObjectToArray(AUTO_SEARCH_CONFIG.sum_attrs);
var ServerTypes = [[3, '3年以上服'], [2, '1到3年服'], [1, '1年内服']];
var FairShowStatus = [[1, '已上架'], [0, '公示期']];
var FrontStatus = [['pass_fair_show', '已上架'], ['fair_show', '公示期']];
var Gems = changeObjectToArray(AUTO_SEARCH_CONFIG.gems_name);
var ProduceFroms = [[1, '系统产出'], [3, '普通打造'], [4, '强化打造']];
var EquipAttrs160 = changeObjectToArray(AUTO_SEARCH_CONFIG.equip_160_attrs);
var OverallEquipSearcher = new Class({
    initialize: function() {
        this.kind_checker = new ButtonChecker(EquipKinds,$('kind_check_panel'));
        this.special_effect_checker = new ButtonChecker(SpecialEffects,$('special_effect_panel'));
        this.special_skill_checker = new ButtonChecker(SpecialSkills.slice(0, 28),$('special_skill_panel'));
        this.sum_attr_checker = new ButtonChecker(SumAttrs,$('sum_attr_panel'));
        this.server_type_checker = new ButtonChecker(ServerTypes,$('server_type_panel'));
        this.front_status_checker = new ButtonChecker(FrontStatus,$('fair_show_panel'));
        this.gem_checker = new ButtonChecker(Gems,$('gem_panel'));
        this.produce_from_checker = new ButtonChecker(ProduceFroms,$('produce_from_panel'));
        this.select_server = new OverallAppointServer(this.server_type_checker);
        this.init_check_mode();
        this.init_level_slider();
        this.init_suit();
        this.init_attr_160();
        this.reg_event();
        this.init_search_btn();
        this.init_role_search_event();
        this.init_reset_btn();
        this.init_role_race();
    },
    init_reset_btn: function() {
        var __this = this;
        $('reset_equip_attr').addEvent('click', function() {
            __this.reset_equip_attr();
        });
        $('reset_server_info').addEvent('click', function() {
            __this.reset_server_info();
        });
        $('reset_all').addEvent('click', function() {
            __this.reset_equip_attr();
            __this.reset_server_info();
        });
    },
    init_role_race: function() {
        var sel_el = $('for_role_race');
        for (var key in RoleKindNameInfo) {
            sel_el.grab(new Element('option',{
                'value': key,
                'html': RoleKindNameInfo[key]
            }));
        }
    },
    init_suit: function() {
        var sel_el = $('sel_short_cut');
        for (var i = 0; i < SuitEffects.length; i++) {
            var item = SuitEffects[i];
            sel_el.grab(new Element('option',{
                'value': item[0],
                'html': item[1]
            }));
        }
        this.suit_value_getter = new SuitValueGetter();
        $('suit_effect_panel').suit_value_getter = this.suit_value_getter;
    },
    init_attr_160: function() {
        var $root = $('160_attr');
        var list = [['', '所有']].concat(EquipAttrs160);
        var html = '';
        list.forEach(function(arr) {
            html += '<option value="' + (arr[0] || '') + '">' + arr[1] + '</option>';
        });
        $root.set('html', html).set('value', '');
    },
    reset_equip_attr: function() {
        var checkers = [this.level_slider, this.kind_checker, this.special_effect_checker, this.special_skill_checker, this.sum_attr_checker, this.gem_checker, this.produce_from_checker, this.front_status_checker];
        var txt_inputs = [$('txt_init_damage'), $('txt_init_damage_raw'), $('txt_init_defense'), $('txt_init_hp'), $('txt_init_dex'), $('txt_init_wakan'), $('txt_all_wakan'), $('txt_all_damage'), $('txt_damage'), $('txt_sum_attr_value'), $('txt_gem_level'), $('txt_hole_num'), $('txt_repair_fail'), $('txt_price_min'), $('txt_price_max'), $('txt_added_status'), $('txt_append_skill'), $('txt_transform_skill'), $('txt_transform_charm')];
        this.reset(checkers, txt_inputs);
        this.reset_check_mode();
        $('chk_star').checked = false;
        $('chk_filter_hun_da_gem').checked = false;
        $('chk_attr_with_melt').checked = true;
        $('chk_sum_attr_with_melt').checked = true;
        $('sel_short_cut').options[0].selected = true;
        $('for_role_race').set('value', '');
        $('for_role_sex').set('value', '');
        $('160_attr').set('value', '');
    },
    reset_server_info: function() {
        var checkers = [this.server_type_checker, this.select_server];
        this.reset(checkers, []);
    },
    reset: function(checkers, txt_inputs) {
        for (var i = 0; i < checkers.length; i++) {
            checkers[i].reset_value();
        }
        for (var i = 0; i < txt_inputs.length; i++) {
            txt_inputs[i].set('value', '');
        }
    },
    reset_check_mode: function() {
        if (this.check_mode != 'or') {
            return;
        }
        $$('#check_mode_panel input').each(function(el, i) {
            if (el.value == 'or') {
                el.checked = false;
            } else {
                el.checked = true;
            }
        });
        this.check_mode = 'and';
        this.set_check_mode();
    },
    init_level_slider: function() {
        this.level_slider = new LevelSlider($('level_slider'),{
            grid: 20,
            offset: -23,
            range: [60, 160],
            step: 10,
            default_value: [60, 160]
        });
    },
    init_check_mode: function() {
        var check_mode = null;
        $$('#check_mode_panel input').each(function(el, i) {
            if (el.checked) {
                check_mode = el.value;
            }
        });
        this.set_check_mode(check_mode);
    },
    set_check_mode: function(check_mode) {
        if (check_mode == 'or') {
            this.special_effect_checker.set_max_num(null);
        } else {
            this.special_effect_checker.set_max_num(16);
        }
        this.special_skill_checker.set_max_num(null);
        this.check_mode = check_mode;
    },
    reg_event: function() {
        var __this = this;
        $('btn_all_special_skill').addEvent('click', function() {
            if ($(this).retrieve('spread')) {
                return;
            }
            __this.special_skill_checker.extend(SpecialSkills.slice(28));
            $(this).store('spread', true);
            $(this).setStyle('display', 'none');
        });
        $$('#check_mode_panel input').addEvent('click', function() {
            var check_mode = this.value;
            if (check_mode == __this.check_mode) {
                return;
            }
            __this.set_check_mode(check_mode);
        });
    },
    init_search_btn: function() {
        var __this = this;
        $('btn_equip_search').addEvent('click', function() {
            if ($(this).get('log-remen')) {
                equip_refer_loc = $(this).get('log-remen');
            } else {
                equip_refer_loc = equip_refer_loc_origin;
            }
            __this.search();
        });
    },
    init_role_search_event: function() {
        var __this = this;
        $('link_search_related_role').addEvent('click', function() {
            __this.search(function(args) {
                document.query_form.search_act.value = "overall_search_role_by_equip";
                $('query_args').value = JSON.encode(args);
                document.query_form.submit();
            });
        });
    },
    search: function(func) {
        var arg = {};
        arg['level_min'] = this.level_slider.value.min;
        arg['level_max'] = this.level_slider.value.max;
        var check_items = [['kindid', this.kind_checker, true], ['special_effect', this.special_effect_checker, false], ['special_skill', this.special_skill_checker, false], ['front_status', this.front_status_checker, true], ['server_type', this.server_type_checker, true], ['gem_value', this.gem_checker, false], ['produce_from', this.produce_from_checker, true]];
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
        if (arg['special_effect']) {
            arg['special_mode'] = this.check_mode;
        }
        var sum_attr_type = this.sum_attr_checker.get_value();
        if (sum_attr_type) {
            arg['sum_attr_type'] = sum_attr_type;
        }
        var txt_int_items = [['init_damage', 0, 10000, '初伤（包含命中）'], ['init_damage_raw', 0, 10000, '初伤（不含命中）'], ['all_damage', 0, 10000, '总伤'], ['damage', 0, 10000, '伤害'], ['init_defense', 0, 10000, '初防'], ['init_hp', 0, 10000, '初血'], ['init_dex', 0, 10000, '初敏'], ['init_wakan', 0, 10000, '初灵'], ['all_wakan', 0, 10000, '总灵'], ['sum_attr_value', 0, 10000, '属性总和'], ['price_min', 0, MaxTradeYuan, '价格'], ['price_max', 0, MaxTradeYuan, '价格'], ['gem_level', 0, 20, '宝石锻炼等级'], ['hole_num', 0, 5, '装备开孔数目'], ['repair_fail', 0, 5, '修理失败次数']];
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
        if ($('chk_star').checked) {
            arg['star'] = 1;
        }
        if (this.select_server.get_serverid()) {
            arg['serverid'] = this.select_server.get_serverid();
        }
        var suit_effect_ret = this.suit_value_getter.get_value();
        if (!suit_effect_ret.valid) {
            alert(suit_effect_ret.value);
            return;
        }
        if (suit_effect_ret.value) {
            arg['suit_effect'] = suit_effect_ret.value;
        }
        if ($("user_serverid") && $("user_serverid").value) {
            arg['cross_buy_serverid'] = $("user_serverid").value;
            window.server_selector && server_selector.update_recent_server_list();
        }
        if ($('for_role_race').value)
            arg['for_role_race'] = $('for_role_race').value;
        if ($('for_role_sex').value)
            arg['for_role_sex'] = $('for_role_sex').value;
        var $160_attr = $('160_attr');
        if ($160_attr.value) {
            arg['160_attr'] = $160_attr.value;
        }
        if ($('chk_filter_hun_da_gem').checked)
            arg['filter_hun_da_gem'] = 1;
        if ($('chk_attr_with_melt').checked) {
            var attrInput = ['init_damage', 'init_damage_raw', 'all_damage', 'damage', 'init_defense', 'init_hp', 'init_dex', 'init_wakan', 'all_wakan'];
            for (var i = 0; i < attrInput.length; i++) {
                if (arg[attrInput[i]]) {
                    arg['attr_with_melt'] = 1;
                    break;
                }
                ;
            }
            ;
        } else {
            arg['attr_without_melt'] = 1;
        }
        if ($('chk_sum_attr_with_melt').checked && arg['sum_attr_value']) {
            arg['sum_attr_with_melt'] = 1;
        } else {
            arg['sum_attr_without_melt'] = 1;
        }
        save_args_in_cookie(arg, "overall_equip_search");
        var f = func || go_overall_search;
        f(arg);
    }
});
var SuitInputAutor = new Class({
    initialize: function(tagid, values, text, getter) {
        this.tagid = tagid;
        this.values = values;
        this.text = text;
        this.getter = getter;
        this.init();
        var that = this;
        $('radio_' + this.tagid).addEvent('click', function() {
            that.getter.chose(that);
        });
        $('txt_' + this.tagid).addEvent('click', function() {
            that.getter.chose(that);
        });
    },
    init: function() {
        var dom_id = 'txt_' + this.tagid;
        var values = this.values;
        new AutoComplete($(dom_id),{
            "startPoint": 1,
            "promptNum": 20,
            "handle_func": function(keyword) {
                var result = new Array();
                for (var p in values) {
                    if (p.indexOf(keyword) != -1) {
                        result.push(p);
                    }
                }
                return result;
            },
            "callback": function() {}
        });
    },
    isChose: function() {
        var radio_id = 'radio_' + this.tagid;
        if ($(radio_id).checked) {
            return true;
        } else {
            return false;
        }
    },
    get_value: function() {
        var dom_id = 'txt_' + this.tagid;
        var values = this.values;
        var keyword = $(dom_id).value;
        if (!keyword || keyword.trim() == '') {
            return [true, null];
        }
        var result = [];
        for (var p in values) {
            if (p.indexOf(keyword) != -1) {
                result.push(values[p]);
            }
        }
        if (result.length == 0) {
            return [false, this.text + keyword + '没有匹配的结果'];
        }
        return [true, result.join(',')];
    },
    set_value: function(val) {
        var dom_id = 'txt_' + this.tagid;
        var radio_id = 'radio_' + this.tagid;
        for (var p in this.values) {
            if (val == this.values[p]) {
                $(dom_id).set('value', p);
                $(radio_id).checked = true;
                this.getter.chose(this);
                return true;
            }
        }
        return false;
    },
    reset: function() {
        $('txt_' + this.tagid).set('value', '');
    }
});
var SuitSelectAutor = new Class({
    initialize: function(tagid, getter) {
        this.tagid = tagid;
        this.getter = getter;
        var that = this;
        $('radio_' + this.tagid).addEvent('click', function() {
            that.getter.chose(that);
        });
        $('sel_' + this.tagid).addEvent('click', function() {
            that.getter.chose(that);
        });
    },
    isChose: function() {
        var radio_id = 'radio_' + this.tagid;
        if ($(radio_id).checked) {
            return true;
        } else {
            return false;
        }
    },
    get_value: function() {
        return [true, $('sel_' + this.tagid).value];
    },
    set_value: function(val) {
        var options = $$('#sel_' + this.tagid + ' option');
        for (var i = 0; i < options.length; i++) {
            var el = options[i];
            if (el.value == val) {
                el.selected = true;
                this.getter.chose(this);
                return true;
            }
        }
        return false;
    },
    reset: function() {
        $('sel_' + this.tagid).options[0].selected = true;
    }
});
var SuitValueGetter = new Class({
    initialize: function() {
        this.autors = [new SuitSelectAutor('short_cut',this), new SuitInputAutor('added_status',SuitAddedStatus,'附加状态',this), new SuitInputAutor('append_skill',SuitAppendSkills,'追加技能',this), new SuitInputAutor('transform_skill',SuitTransformSkills,'变身术之',this), new SuitInputAutor('transform_charm',SuitTransformCharms,'变化咒之',this)];
    },
    get_value: function() {
        for (var i = 0; i < this.autors.length; i++) {
            var autor = this.autors[i];
            if (!autor.isChose()) {
                continue;
            }
            var autor_value = autor.get_value();
            var valid = autor_value[0];
            var msg = autor_value[1];
            if (!valid) {
                return {
                    valid: false,
                    value: msg
                };
            } else {
                return {
                    valid: true,
                    value: msg
                };
            }
        }
    },
    set_value: function(val) {
        for (var i = 0; i < this.autors.length; i++) {
            var autor = this.autors[i];
            if (autor.set_value(val)) {
                break;
            }
        }
    },
    chose: function(chose_autor) {
        for (var i = 0; i < this.autors.length; i++) {
            if (this.autors[i] != chose_autor) {
                this.autors[i].reset();
            }
        }
    }
});
function get_suit_name_by_value(value) {
    var name = get_name_from_conf(value, SuitEffects);
    if (name) {
        return name;
    }
    name = get_name_from_dict(value, SuitAddedStatus);
    if (name) {
        return name;
    }
    name = get_name_from_dict(value, SuitAppendSkills);
    if (name) {
        return '追加法术' + name;
    }
    name = get_name_from_dict(value, SuitTransformSkills);
    if (name) {
        return '变身术之' + name;
    }
    name = get_name_from_dict(value, SuitTransformCharms);
    if (name) {
        return '变化咒之' + name;
    }
    return "";
}
;(function() {
    if (typeof CreateConfig == 'undefined') {
        return;
    }
    var ShuXing = {
        "init_damage": "初伤（包含命中）≥",
        "init_damage_raw": "初伤（不含命中）≥",
        "init_defense": "初防≥",
        "init_hp": "初血≥",
        "init_dex": "初敏≥",
        "init_wakan": "初灵≥",
        "all_wakan": "总灵≥",
        "all_damage": "总伤≥",
        "damage": "伤害≥ "
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
                name: "等级",
                get_val: ctx.get().range("level_min"),
                set_val: ctx.set().slider.bind(ctx, {
                    minKey: "level_min",
                    maxKey: "level_max",
                    defaultRang: [60, 160],
                    elemId: "level_slider"
                })
            }, {
                name: "类型",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("kindid")) {
                        var text = ctx.get().list("kindid", EquipKinds);
                        desc.push(text)
                    }
                    if (arg.hasOwnProperty("for_role_race")) {
                        var value = arg["for_role_race"];
                        var weponDesc = $('for_role_race').getElement('option[value=' + value + ']').get('text');
                        desc.push('武器:' + weponDesc);
                    }
                    if (arg.hasOwnProperty("for_role_sex")) {
                        var value = arg["for_role_sex"];
                        var weponDesc = $('for_role_sex').getElement('option[value=' + value + ']').get('text');
                        desc.push('防具:' + weponDesc);
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().list({
                        key: "kindid",
                        elem: $$("#kind_check_panel li")
                    });
                    ctx.set().select("for_role_race", "for_role_race");
                    ctx.set().select("for_role_sex", "for_role_sex");
                }
            }, {
                name: "特效",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("special_mode")) {
                        var text = arg["special_mode"] == "and" ? "都满足" : "满足一种";
                        desc.push(text);
                    }
                    if (arg.hasOwnProperty("special_effect")) {
                        var text = ctx.get().list("special_effect", SpecialEffects);
                        desc.push(text)
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().list({
                        key: "special_effect",
                        elem: $$("#special_effect_panel li")
                    });
                    if (arg.hasOwnProperty("special_mode")) {
                        var radioVal = arg["special_mode"];
                        $$("#check_mode_panel input[value=" + radioVal + "]")[0].click();
                    }
                }
            }, {
                name: "特技",
                get_val: ctx.get().list("special_skill", SpecialSkills),
                set_val: function() {
                    if (arg.hasOwnProperty("special_skill")) {
                        $("btn_all_special_skill").fireEvent("click");
                        ctx.set().list({
                            key: "special_skill",
                            elem: $$("#special_skill_panel li")
                        });
                    }
                }
            }, {
                name: "套装",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("suit_effect")) {
                        var text = get_suit_name_by_value(arg["suit_effect"]);
                        desc.push(text)
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    if (arg.hasOwnProperty("suit_effect")) {
                        $('radio_short_cut').set('checked', true);
                        if ($('suit_effect_panel').suit_value_getter) {
                            $('suit_effect_panel').suit_value_getter.set_value(arg["suit_effect"]);
                        }
                    }
                }
            }, {
                name: "属性",
                get_val: function() {
                    var desc = [];
                    var shuxingDesc = ctx.get().input_group(ShuXing);
                    if (shuxingDesc != "") {
                        desc.push(shuxingDesc)
                    }
                    if (arg.hasOwnProperty("attr_with_melt")) {
                        desc.push("计算熔炼效果");
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().input_group(ShuXing, "txt_");
                    ctx.set().checkbox("attr_with_melt", "chk_attr_with_melt");
                }
            }, {
                name: "属性计算",
                get_val: function() {
                    var desc = [];
                    var shuxingDesc = ctx.get().list("sum_attr_type", SumAttrs);
                    if (shuxingDesc != "") {
                        desc.push(shuxingDesc)
                    }
                    if (arg.hasOwnProperty("sum_attr_value")) {
                        desc.push("属性总和≥" + arg["sum_attr_value"]);
                    }
                    if (arg.hasOwnProperty("sum_attr_with_melt") && desc.length > 0) {
                        desc.push("计算熔炼效果");
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().list({
                        key: "sum_attr_type",
                        elem: $$("#sum_attr_panel li")
                    });
                    ctx.set().checkbox("sum_attr_with_melt", "chk_sum_attr_with_melt");
                    ctx.set().input("sum_attr_value", "txt_sum_attr_value");
                }
            }, {
                name: "160级装备特性",
                get_val: function() {
                    var desc = "";
                    if (arg.hasOwnProperty("160_attr")) {
                        desc = $$("#160_attr option[value=" + arg["160_attr"] + "]").get("text");
                    }
                    return desc;
                },
                set_val: function() {
                    ctx.set().select("160_attr", "160_attr");
                }
            }, {
                name: "镶嵌宝石",
                get_val: function() {
                    var desc = [];
                    var baoshiDesc = ctx.get().list("gem_value", Gems);
                    if (baoshiDesc != "") {
                        desc.push(baoshiDesc)
                    }
                    if (arg.hasOwnProperty("gem_level")) {
                        desc.push("宝石锻炼等级≥" + arg["gem_level"]);
                    }
                    if (arg.hasOwnProperty("filter_hun_da_gem") && desc.length > 0) {
                        desc.push("过滤混打宝石");
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().list({
                        key: "gem_value",
                        elem: $$("#gem_panel li")
                    });
                    ctx.set().checkbox("filter_hun_da_gem", "chk_filter_hun_da_gem");
                    ctx.set().input("gem_level", "txt_gem_level");
                }
            }, {
                name: "装备开运",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("hole_num")) {
                        desc.push("装备开孔数目≥" + arg["sum_attr_value"]);
                    }
                    if (arg.hasOwnProperty("star")) {
                        desc.push("限开启星位");
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().checkbox("star", "chk_star");
                    ctx.set().input("hole_num", "txt_hole_num");
                }
            }, ctx.list({
                name: "装备产出",
                key: "produce_from",
                listConfig: ProduceFroms,
                elem: $$('#produce_from_panel li')
            }), ctx.input_group({
                name: "修理失败",
                inputConfig: {
                    repair_fail: "修理失败次数≤ "
                },
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
var HotSearch = new Class({
    initialize: function(subBtnId) {
        this.subBtnId = subBtnId;
        this.getTips();
    },
    getTips: function() {
        var ctx = this;
        var Ajax = new Request.JSON({
            "url": CgiRootUrl + '/xyq_overall_search.py?act=get_hot_search_labels',
            "onSuccess": function(res) {
                if (res.status && res.labels.length > 0) {
                    render_to_replace('overall_hot_search_panel', 'overall_hot_search_temp', {
                        labels: res.labels,
                        title: res.title
                    });
                    ctx.bindEvent(res.labels);
                }
            }
        });
        Ajax.get();
    },
    scrollToResultPage: function() {
        var subBtnId = this.subBtnId;
        var offset = $(subBtnId).getCoordinates();
        window.scrollTo(0, offset.bottom);
    },
    resetLevel: function(arg) {
        var resetArg = Object.clone(arg);
        if (arg.hasOwnProperty('level_min')) {
            var minVal = arg['level_min'];
            var maxVal = arg['level_max'];
            if (maxVal < 50) {
                minVal = 60;
                maxVal = 60;
            } else if (minVal > 175) {
                minVal = 160;
                maxVal = 160;
            } else {
                var rangeCofig = [{
                    min: 50,
                    max: 69,
                    real: 60
                }, {
                    min: 70,
                    max: 79,
                    real: 70
                }, {
                    min: 80,
                    max: 89,
                    real: 80
                }, {
                    min: 90,
                    max: 99,
                    real: 90
                }, {
                    min: 100,
                    max: 109,
                    real: 100
                }, {
                    min: 110,
                    max: 119,
                    real: 110
                }, {
                    min: 120,
                    max: 129,
                    real: 120
                }, {
                    min: 130,
                    max: 139,
                    real: 130
                }, {
                    min: 140,
                    max: 149,
                    real: 140
                }, {
                    min: 150,
                    max: 159,
                    real: 150
                }, {
                    min: 160,
                    max: 175,
                    real: 160
                }];
                for (var i = 0; i < rangeCofig.length; i++) {
                    var item = rangeCofig[i];
                    if (minVal >= item.min && maxVal <= item.max) {
                        minVal = item.real;
                        maxVal = item.real;
                        break;
                    }
                }
            }
            resetArg.level_min = minVal;
            resetArg.level_max = maxVal;
        }
        return resetArg;
    },
    addLogTip: function() {
        $(this.subBtnId).set('log-remen', 'search_remen');
    },
    removeLogTip: function() {
        $(this.subBtnId).removeAttribute('log-remen');
    },
    bindEvent: function(labels) {
        var ctx = this;
        $('overall_hot_search_panel').addEvent('click:relay(.jsHotSearchTips)', function() {
            var index = Number($(this).get('data-index'));
            var arg = labels[index].conds;
            var resetArg = ctx.resetLevel(arg);
            restore_query_form(resetArg);
            ctx.addLogTip();
            $(ctx.subBtnId).click();
            setTimeout(function() {
                ctx.scrollToResultPage();
                ctx.removeLogTip();
            }, 500);
        })
    }
})
