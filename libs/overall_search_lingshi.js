var OverallSearchAct = 'overall_search_lingshi';
var Kinds = [[61, '戒指'], [62, '耳饰'], [63, '手镯'], [64, '佩饰']];
var AddedAttr1 = changeObjectToArray(AUTO_SEARCH_CONFIG.lingshi_added_attr1);
var AddedAttr2 = changeObjectToArray(AUTO_SEARCH_CONFIG.lingshi_added_attr2);
var AddedAttrNum = [[2, '2条'], [3, '3条']];
var AddedAttrRepeatNum = AddedAttrNum;
var SuitEffects = AUTO_SEARCH_CONFIG.lingshi_suit_effects;
var LingshiAttrs = AUTO_SEARCH_CONFIG.lingshi_attrs || [];
var ServerTypes = [[3, '3年以上服'], [2, '1到3年服'], [1, '1年内服']];
var FairShowStatus = [[1, '已上架'], [0, '公示期']];
var OverallLingshiSearcher = new Class({
    initialize: function() {
        this.server_type_checker = new ButtonChecker(ServerTypes,$('server_type_panel'));
        this.fair_show_checker = new ButtonChecker(FairShowStatus,$('fair_show_panel'));
        this.kind_checker = new ButtonChecker(Kinds,$('kind_panel'));
        this.added_attr1_checker = new ButtonChecker(AddedAttr1,$('added_attr1_panel'));
        this.added_attr2_checker = new ButtonChecker(AddedAttr2,$('added_attr2_panel'));
        this.added_attr_num_checker = new ButtonChecker(AddedAttrNum,$('added_attr_num_panel'));
        this.added_attr_repeat_num_checker = new ButtonChecker(AddedAttrNum,$('added_attr_repeat_num_panel'));
        this.select_server = new OverallAppointServer(this.server_type_checker);
        this.init_level_slider();
        this.init_sel_add_attr();
        this.init_suit_effect();
        this.init_synthesized_attr();
        this.init_search_btn();
        this.init_role_search_event();
        this.init_reset_btn();
        this.reset_all();
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
            __this.reset_all();
        });
    },
    reset_all: function() {
        this.reset_basic();
        this.reset_detail();
        this.reset_server_info();
    },
    reset_basic: function() {
        var checkers = [this.level_slider, this.kind_checker];
        this.reset(checkers, []);
    },
    reset_detail: function() {
        var checkers = [this.fair_show_checker, this.added_attr1_checker, this.added_attr2_checker, this.added_attr_num_checker, this.added_attr_repeat_num_checker];
        var txt_inputs = [$('txt_basic_attr_value'), $('txt_price_min'), $('txt_price_max'), $('txt_jinglian_level'), $('sel_add_attr1'), $('sel_add_attr2'), $('sel_add_attr3'), $('sel_suit_effect'), $('txt_suit_effect_level'), $('synthesized_attr_type'), $('txt_synthesized_attr_value')];
        this.reset(checkers, txt_inputs);
        $('sel_basic_attr_type').set('value', '');
        $('chk_has_eazy_effect').checked = false;
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
    init_level_slider: function() {
        this.level_slider = new LevelSlider($('equip_level_slider'),{
            grid: 40,
            offset: -23,
            range: [60, 160],
            step: 20,
            default_value: [60, 160]
        });
    },
    init_sel_add_attr: function() {
        var option_html = '<option value="">不限</option>';
        var add_attr1 = AddedAttr1;
        var add_attr2 = AddedAttr2;
        add_attr1.concat(add_attr2).each(function(item) {
            option_html += '<option value="' + item[0] + '">' + item[1] + '</option>';
        });
        $('sel_add_attr1').set('html', option_html);
        $('sel_add_attr2').set('html', option_html);
        $('sel_add_attr3').set('html', option_html);
        $('sel_add_attr_panel').set('html', $('sel_add_attr_panel').get('html'));
        $$('.j_sel_add_attr').addEvent('click', function() {
            $('added_attr_logic_detail').checked = true;
        });
    },
    init_suit_effect: function() {
        var options = ['<option value="">不限</option>'];
        SuitEffects.each(function(name, index) {
            options.push('<option value="' + (index + 1) + '">' + name + '</option>');
        });
        $('sel_suit_effect').set('html', options.join(''));
        if (Browser.ie) {
            $('sel_suit_effect').setStyle('zoom', 1);
        }
    },
    init_synthesized_attr: function() {
        var options = ['<option value="">不限</option>'];
        LingshiAttrs.each(function(item) {
            options.push('<option value="' + item.value + '">' + item.label + '</option>');
        });
        $('synthesized_attr_type').set('html', options.join(''));
    },
    init_search_btn: function() {
        var __this = this;
        $('btn_lingshi_search').addEvent('click', function() {
            __this.search();
        });
    },
    init_role_search_event: function() {
        var __this = this;
        $('link_search_related_role').addEvent('click', function() {
            __this.search(function(args) {
                document.query_form.search_act.value = "overall_search_role_by_lingshi";
                $('query_args').value = JSON.encode(args);
                document.query_form.submit();
            });
        });
    },
    search: function(func) {
        var arg = {};
        arg['equip_level_min'] = this.level_slider.value.min;
        arg['equip_level_max'] = this.level_slider.value.max;
        var check_items = [['pass_fair_show', this.fair_show_checker, true], ['server_type', this.server_type_checker, true], ['kindid', this.kind_checker, true], ['added_attr_num', this.added_attr_num_checker, false], ['added_attr_repeat_num', this.added_attr_repeat_num_checker, false]];
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
        var added_attr_values = this.added_attr1_checker.get_value_array().concat(this.added_attr2_checker.get_value_array());
        $$('input[name=added_attr_logic]').each(function(el) {
            if (el.checked) {
                arg['added_attr_logic'] = el.value;
            }
        });
        if (arg.added_attr_logic == 'detail') {
            for (var i = 1; i <= 3; ++i) {
                var value = $('sel_add_attr' + i).value;
                if (value > 0)
                    arg['added_attr.' + value] = (arg['added_attr.' + value] || 0) + 1;
            }
        } else {
            if (added_attr_values.length > 0) {
                for (var i = 0; i < added_attr_values.length; i++) {
                    var value = added_attr_values[i];
                    arg['added_attr.' + value] = 1;
                }
            }
        }
        for (var k = 1; k < 20; k++) {
            var addedAttrKey = 'added_attr.' + k;
            var count = [];
            if (arg[addedAttrKey]) {
                break;
            } else {
                if (k == 19) {
                    arg['added_attr_logic'] && delete arg.added_attr_logic;
                }
            }
        }
        if ($('chk_has_eazy_effect').checked) {
            arg['special_effect'] = 1;
        }
        var txt_int_items = [['basic_attr_value', 0, 10000, '技能数量'], ['price_min', 0, MaxTradeYuan, '价格'], ['price_max', 0, MaxTradeYuan, '价格'], ['jinglian_level', 0, 16, '精炼等级'], ['suit_effect_level', 0, 99, '套装等级']];
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
        var basic_attr_type = $("sel_basic_attr_type").value;
        var basic_attr_value = $("txt_basic_attr_value").value;
        if (basic_attr_type.length > 0) {
            if (basic_attr_value.length == 0) {
                arg["basic_attr_value"] = 1;
            }
        }
        var synthesized_attr_type = $("synthesized_attr_type").value;
        var synthesized_attr_value = $("txt_synthesized_attr_value").value;
        if (synthesized_attr_type) {
            arg["synthesized_attr_total"] = JSON.encode({
                [synthesized_attr_type]: synthesized_attr_value || "1"
            });
        }
        var repair_fail = $('txt_repair_fail').value;
        if (repair_fail) {
            if (!/^\d+$/g.test(repair_fail) || repair_fail > 3) {
                return alert('修理失败取值范围是0~3的整数');
            }
            arg['repair_fail'] = repair_fail;
        }
        var suit_effect = $('sel_suit_effect').value;
        var suit_effect_level = $('txt_suit_effect_level').value;
        if (suit_effect) {
            arg['suit_effect'] = suit_effect;
        }
        if ((suit_effect_level || '').trim() !== '') {
            arg['suit_effect_level'] = suit_effect_level;
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
        var basic_attr_type = $('sel_basic_attr_type').value;
        if (basic_attr_type && arg.basic_attr_value) {
            arg[basic_attr_type] = arg.basic_attr_value;
        }
        if (arg.basic_attr_value) {
            delete arg.basic_attr_value;
        }
        if (this.select_server.get_serverid()) {
            arg['serverid'] = this.select_server.get_serverid();
        }
        if ($("user_serverid") && $("user_serverid").value) {
            arg['cross_buy_serverid'] = $("user_serverid").value;
            window.server_selector && server_selector.update_recent_server_list();
        }
        save_args_in_cookie(arg, "overall_lingshi_search");
        var f = func || go_overall_search;
        f(arg);
    }
});
var LingshiDescParser = new Class({
    initialize: function(desc) {
        this.desc = desc;
        this.parse();
    },
    parse: function() {
        var added_attrs = [];
        var lines = this.desc.split('#r').map(function(x) {
            return x.trim()
        });
        lines = lines.filter(function(x) {
            return x != ''
        });
        for (var i = 0; i < lines.length; i++) {
            if (i <= 1) {
                continue;
            }
            var line = lines[i];
            if (line.slice(0, 2) == '#G') {
                added_attrs.push(line.replace(/#G|#c[0-9A-F]{6}/g, "").replace(/^#+|#+$/g, ''));
            }
        }
        this.added_attrs = added_attrs;
    },
    get_added_attr_by_index: function(i) {
        if (this.added_attrs.length > i) {
            return this.added_attrs[i];
        }
        return '';
    },
    get_all: function() {
        return this.added_attrs.join('<br />');
    }
});
function get_basic_attrs(equip) {
    var basic_attrs = [];
    var keys = [['damage', '伤害'], ['defense', '防御'], ['magic_damage', '法术伤害'], ['magic_defense', '法术防御'], ['fengyin', '封印命中等级'], ['anti_fengyin', '抵抗封印等级'], ['speed', '速度']];
    for (var i = 0; i < keys.length; i++) {
        var key_item = keys[i];
        var value = equip[key_item[0]];
        if (value) {
            basic_attrs.push(key_item[1] + "&nbsp;+" + value);
        }
    }
    return basic_attrs.join("&nbsp;");
}
;(function() {
    if (typeof CreateConfig == 'undefined') {
        return;
    }
    var AddedAttr = {
        "added_attr.1": "固伤",
        "added_attr.2": "伤害",
        "added_attr.3": "速度",
        "added_attr.4": "法伤",
        "added_attr.5": "狂暴",
        "added_attr.6": "物理暴击",
        "added_attr.7": "法术暴击",
        "added_attr.8": "封印",
        "added_attr.9": "法伤结果",
        "added_attr.10": "穿刺",
        "added_attr.11": "治疗",
        "added_attr.12": "气血",
        "added_attr.13": "防御",
        "added_attr.14": "法防",
        "added_attr.15": "抗物理暴击",
        "added_attr.16": "抗法术暴击",
        "added_attr.17": "抗封",
        "added_attr.18": "格挡",
        "added_attr.19": "回复"
    };
    var BasicAttr = {
        damage: "戒指·伤害≥",
        defense: "戒指·防御≥",
        magic_damage: "耳饰·法伤≥",
        magic_defense: "耳饰·法防≥",
        fengyin: "手镯·封印≥",
        anti_fengyin: "手镯·抗封≥",
        speed: "佩饰·速度≥"
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
                get_val: ctx.get().range("equip_level_min"),
                set_val: ctx.set().slider.bind(ctx, {
                    minKey: "equip_level_min",
                    maxKey: "equip_level_max",
                    defaultRang: [60, 160],
                    elemId: "equip_level_slider"
                })
            }, ctx.list({
                name: "类型",
                key: "kindid",
                listConfig: Kinds,
                elem: $$('#kind_panel li')
            }), {
                name: "基础属性",
                get_val: function() {
                    var desc = "";
                    for (var key in BasicAttr) {
                        if (arg.hasOwnProperty(key)) {
                            desc = BasicAttr[key] + arg[key];
                        }
                    }
                    return desc;
                },
                set_val: function() {
                    for (var key in BasicAttr) {
                        if (arg.hasOwnProperty(key)) {
                            $('sel_basic_attr_type').set('value', key);
                            $('txt_basic_attr_value').set('value', arg[key]);
                            break;
                        }
                    }
                }
            }, {
                name: "精炼等级≥",
                get_val: function() {
                    if (arg.hasOwnProperty("jinglian_level")) {
                        return arg["jinglian_level"];
                    }
                    return "";
                },
                set_val: function() {
                    arg.hasOwnProperty("jinglian_level") && $('txt_jinglian_level').set('value', arg['jinglian_level']);
                }
            }, {
                name: "附加属性",
                get_val: function() {
                    var attrDesc = [];
                    var logic = "";
                    for (var key in AddedAttr) {
                        if (arg.hasOwnProperty(key)) {
                            attrDesc.push(AddedAttr[key])
                        }
                    }
                    if (arg.hasOwnProperty("added_attr_logic")) {
                        var logic = "满足一种";
                        if (arg["added_attr_logic"] == "and") {
                            logic = "都满足";
                        }
                        if (arg["added_attr_logic"] == "detail") {
                            logic = "详细属性";
                        }
                    }
                    var desc = attrDesc.join(",") + logic;
                    return desc;
                },
                set_val: function() {
                    if (arg.hasOwnProperty("added_attr_logic")) {
                        $$('input[name=added_attr_logic][value=' + arg['added_attr_logic'] + ']').set('checked', true);
                        var addeAttr1 = [];
                        var addeAttr2 = [];
                        for (var key in AddedAttr) {
                            if (arg.hasOwnProperty(key)) {
                                var value = Number(key.split('.')[1]);
                                if (value < 12) {
                                    addeAttr1.push(value);
                                } else {
                                    addeAttr2.push(value);
                                }
                            }
                        }
                        ;if (addeAttr1.length > 0) {
                            set_list_by_value(addeAttr1.join(","), $$('#added_attr1_panel li'));
                        }
                        if (addeAttr2.length > 0) {
                            set_list_by_value(addeAttr2.join(","), $$('#added_attr2_panel li'));
                        }
                    }
                }
            }, {
                name: "综合属性",
                get_val: function() {
                    var result = '';
                    if (arg.hasOwnProperty("synthesized_attr_total")) {
                        var item = JSON.decode(arg["synthesized_attr_total"] || "{}");
                        var key = Object.keys(item)[0];
                        var value = item[key];
                        var txt = $$('#synthesized_attr_type option[value=' + key + ']').get('html');
                        if (txt) {
                            result = txt + '≥' + value;
                        }
                    }
                    return result;
                },
                set_val: function() {
                    if (arg.hasOwnProperty("synthesized_attr_total")) {
                        var item = JSON.decode(arg["synthesized_attr_total"] || "{}");
                        var key = Object.keys(item)[0];
                        var value = item[key];
                        if (key) {
                            $('synthesized_attr_type').set('value', key);
                            $('txt_synthesized_attr_value').set('value', value);
                        }
                    }
                }
            }, {
                name: "属性条目数",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("added_attr_num")) {
                        var value = arg["added_attr_num"];
                        if (value.split(",").length == 2) {
                            desc.push("附加属性条目:2条,3条");
                        } else {
                            desc.push("附加属性条目:" + value + "条");
                        }
                    }
                    if (arg.hasOwnProperty("added_attr_repeat_num")) {
                        var value = arg["added_attr_repeat_num"];
                        if (value.split(",").length == 2) {
                            desc.push("相同属性条目:2条,3条");
                        } else {
                            desc.push("相同属性条目:" + value + "条");
                        }
                    }
                    return desc.length == 0 ? "" : desc.join(",");
                },
                set_val: function() {
                    ctx.set().list({
                        key: "added_attr_repeat_num",
                        elem: $$('#added_attr_repeat_num_panel li')
                    });
                    ctx.set().list({
                        key: "added_attr_num",
                        elem: $$('#added_attr_num_panel li')
                    });
                }
            }, {
                name: "特效",
                get_val: function() {
                    return arg.hasOwnProperty("special_effect") ? "带有“超级简易”" : "";
                },
                set_val: ctx.set().checkbox.bind(ctx, ["special_effect", "chk_has_eazy_effect"])
            }, {
                name: "修理失败",
                get_val: function() {
                    if (arg.hasOwnProperty("repair_fail")) {
                        return "修理失败次数≤" + arg["repair_fail"];
                    }
                    return "";
                },
                set_val: function() {
                    arg.hasOwnProperty("repair_fail") && $('txt_repair_fail').set('value', arg['repair_fail']);
                }
            }, {
                name: "套装效果",
                get_val: function() {
                    var result = '';
                    if (arg.hasOwnProperty("suit_effect")) {
                        var suit_effect;
                        suit_effect = parseInt(arg.suit_effect);
                        if (!isNaN(suit_effect) && SuitEffects[suit_effect - 1]) {
                            result += SuitEffects[suit_effect - 1] + ' ';
                        }
                    }
                    if (arg.hasOwnProperty("suit_effect_level")) {
                        result += '等级≥' + arg.suit_effect_level;
                    }
                    return result;
                },
                set_val: function() {
                    $('sel_suit_effect').set('value', arg.suit_effect);
                    $('txt_suit_effect_level').set('value', arg.suit_effect_level);
                }
            }, ctx.range({
                name: "价格",
                key: "price_min",
                elem: "txt_price_min"
            }), ctx.list({
                name: "出售状态",
                key: "pass_fair_show",
                listConfig: FairShowStatus,
                elem: $$('#fair_show_panel li')
            }), ctx.list({
                name: "开服时间",
                key: "server_type",
                listConfig: ServerTypes,
                elem: $$('#server_type_panel li')
            }), ctx.appoint_server()]
        }
    });
    function set_list_by_value(value, $elem) {
        var parent_el = $elem.getParent()[0];
        var valueList = value.split(",");
        if (parent_el && parent_el.btn_checker) {
            parent_el.btn_checker.restore(valueList);
            return false;
        }
        $elem.forEach(function($li) {
            var liVal = $li.retrieve('value').toString();
            if (valueList.indexOf(liVal) > -1) {
                $li.addClass('on');
            }
        })
    }
    ;window.RecentSearchConfig = RecentSearchConfig;
}
)();
