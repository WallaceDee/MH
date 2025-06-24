var SearchFormObj = null;
var QueryArgs = null;
var EquipAddonStatus = AUTO_SEARCH_CONFIG.equip_addon_status;
var ServerTypes = [[3, '3年以上服'], [2, '1到3年服'], [1, '1年内服']];
var PetEquipSearchFormInit = new Class({
    initialize: function() {
        this.level_slider = this.init_level_slider();
        this.init_addon_skill_box();
        this.reg_item_selected_ev();
        this.reg_reset_event();
        this.init_template();
        this.server_type_checker = new ButtonChecker(ServerTypes,$('server_type_panel'));
        this.select_server = new OverallAppointServer(this.server_type_checker);
        var ctx = this;
        $("btn_do_query").addEvent("click", function() {
            ctx.search();
        });
    },
    init_template: function() {
        render_to_replace('xiangqian_stone_attr_panel', 'template_btn_li', {
            config: AUTO_SEARCH_CONFIG.jingpo_stone_attrs
        });
        render_to_replace('addon_skill_box', 'template_btn_li', {
            config: AUTO_SEARCH_CONFIG.addon_attrs
        });
    },
    init_level_slider: function() {
        this.level_slider = new LevelSlider($('level_slider'),{
            grid: 20,
            offset: -23,
            range: [5, 145],
            step: 10,
            default_value: [5, 145]
        });
        return this.level_slider;
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
    init_addon_skill_box: function() {
        var self = this;
        var skill_search = function(keyword) {
            var result = [];
            for (var i = 0; i < SENIOR_YAO_JUE.length; i++) {
                if (SENIOR_YAO_JUE[i].indexOf(keyword) != -1) {
                    if (!result.contains(SENIOR_YAO_JUE[i])) {
                        result.push(SENIOR_YAO_JUE[i]);
                    }
                }
            }
            for (var i = 0; i < PRIMARY_YAO_JUE.length; i++) {
                if (PRIMARY_YAO_JUE[i].indexOf(keyword) != -1) {
                    if (!result.contains(PRIMARY_YAO_JUE[i])) {
                        result.push(PRIMARY_YAO_JUE[i]);
                    }
                }
            }
            for (var i = 0; i < EquipAddonStatus.length; i++) {
                if (EquipAddonStatus[i].indexOf(keyword) != -1) {
                    if (!result.contains(EquipAddonStatus[i])) {
                        result.push(EquipAddonStatus[i]);
                    }
                }
            }
            return result;
        };
        var $addon = $('addon_status');
        new AutoComplete($addon,{
            "startPoint": 1,
            "promptNum": 20,
            "handle_func": skill_search,
            "callback": function() {}
        });
        var $has = $('has_suit_effect'), hasTimer;
        var check = function(e) {
            var ctx = this;
            clearTimeout(hasTimer);
            hasTimer = setTimeout(function() {
                var value = ctx.value.trim();
                var isOk = value && PetEquipSearchFormInit.isAddonStatusOk(value);
                $has.getParent()[isOk ? 'removeClass' : 'addClass']('disabled');
                $has.set('disabled', !isOk);
            }, 200);
        };
        $addon.addEvents({
            keyup: check,
            change: check
        });
    },
    empty_input_box: function(item_list) {
        for (var i = 0; i < item_list.length; i++) {
            $(item_list[i]).value = "";
        }
    },
    clear_select_items: function(item_list) {
        for (var i = 0; i < item_list.length; i++) {
            var item = item_list[i];
            if (item.hasClass("on")) {
                item.removeClass("on");
            }
        }
    },
    reset_server_info: function() {
        var checkers = [this.server_type_checker, this.select_server];
        for (var i = 0; i < checkers.length; i++) {
            checkers[i].reset_value();
        }
    },
    reg_reset_event: function() {
        var self = this;
        $("reset_basic").addEvent("click", function() {
            self.clear_select_items($$("#EquipPosBox li"));
            self.level_slider.reset_value();
            return false;
        });
        $("reset_equips_attr").addEvent("click", function() {
            self.clear_select_items($$("#addon_skill_box li"));
            self.clear_select_items($$("#xiangqian_stone_attr_panel li"));
            self.empty_input_box($$("#PetEquipAttrBox input"));
            self.empty_input_box($$("#PetEquipAttrBox select"));
            return false;
        });
        $("reset_price").addEvent("click", function() {
            self.empty_input_box($$("#EquipPriceBox input"));
            return false;
        });
        $("reset_server_selected").addEvent("click", function() {
            self.reset_server_info();
            return false;
        });
        $("reset_all").addEvent("click", function() {
            $("reset_basic").fireEvent("click");
            $("reset_equips_attr").fireEvent("click");
            $("reset_price").fireEvent("click");
            $("reset_server_selected").fireEvent("click");
            return false;
        });
    },
    search: function() {
        query_pet_equips.call(this);
    }
});
PetEquipSearchFormInit.extend({
    isAddonStatusOk: function(value) {
        if (!MO_SHOU_YAO_JUE.contains(value) && !EquipAddonStatus.contains(value)) {
            return false;
        }
        return true;
    }
});
function check_int_args(args_config_list) {
    var re = /^[0-9]\d*$/;
    var args = {};
    for (var i = 0; i < args_config_list.length; i++) {
        var item = args_config_list[i];
        var item_value = $(item[0] + "").value.trim();
        if (item_value.length == 0) {
            continue;
        }
        if (!re.test(item_value) || item_value.length > 9) {
            return {
                "result": false,
                "msg": item[1] + "填写错误，请重新输入"
            }
        }
        item_value = parseInt(item_value);
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
    if (value_list.length == item_list.length) {
        return "";
    } else {
        return value_list.join(",");
    }
}
function query_pet_equips() {
    var args_config = [["speed", "速度"], ["fangyu", "防御"], ["mofa", "魔法"], ["shanghai", "伤害"], ["hit_ratio", "命中率"], ["hp", "气血"], ["xiang_qian_level", "宝石"], ["addon_sum_min", "属性总和"], ["addon_minjie_reduce", "敏捷减少"]];
    var result = check_int_args(args_config);
    if (!result["result"]) {
        alert(result["msg"]);
        return;
    }
    var args = result["args"];
    args["level_min"] = SearchFormObj.level_slider.value.min;
    args["level_max"] = SearchFormObj.level_slider.value.max;
    var equip_pos = get_item_selected($$("#EquipPosBox li"));
    if (equip_pos) {
        args["equip_pos"] = equip_pos;
    }
    var xiangqian_stone_attr = get_item_selected($$('#xiangqian_stone_attr_panel li'));
    if (xiangqian_stone_attr) {
        args['xiangqian_stone_attr'] = xiangqian_stone_attr;
    }
    var addon_el_list = $$("#addon_skill_box li");
    for (var i = 0; i < addon_el_list.length; i++) {
        var item = addon_el_list[i];
        if (item.hasClass("on")) {
            var attr_name = item.getAttribute("data_value");
            args[attr_name] = 1;
        }
    }
    var repair_failed_times = $("repair_failed_times").value;
    if (repair_failed_times.length > 0) {
        args["repair_failed_times"] = repair_failed_times;
    }
    if ($("price_min").value.trim().length > 0) {
        var price_min_value = parseFloat($("price_min").value);
        if (!price_min_value || price_min_value <= 0) {
            alert("您输入的最低价格有错误");
            return false;
        }
        args["price_min"] = parseInt(price_min_value * 100);
    }
    if ($("price_max").value.trim().length > 0) {
        var price_max_value = parseFloat($("price_max").value);
        if (!price_max_value || price_max_value <= 0) {
            alert("您输入的最高价格有错误");
            return false;
        }
        args["price_max"] = parseInt(price_max_value * 100);
    }
    if (args["price_min"] && args["price_max"]) {
        if (args["price_max"] < args["price_min"]) {
            alert("您输入的价格有错误");
            return false;
        }
    }
    if (args["price_min"] > MaxTradeYuan * 100 || args["price_max"] > MaxTradeYuan * 100) {
        alert("价格超出取值范围:0-" + MaxTradeYuan);
        return false;
    }
    var addon_status = $("addon_status").value;
    if (addon_status.length > 0) {
        if (!PetEquipSearchFormInit.isAddonStatusOk(addon_status)) {
            alert("附加状态填写错误");
            return false;
        }
        args["addon_status"] = addon_status;
    }
    var $noSuitEffect = $('no_suit_effect')
      , $hasSuitEffect = $('has_suit_effect')
      , $includeDamage = $('addon_sum_include_damage');
    if ($noSuitEffect.checked) {
        args['include_no_skill'] = 1;
    }
    if (!$hasSuitEffect.disabled) {
        if ($hasSuitEffect.checked) {
            args['include_can_cover_skill'] = 1;
        }
    }
    if ($includeDamage.checked) {
        args['addon_sum_include_damage'] = 1;
    }
    var check_items = [['server_type', this.server_type_checker, true]];
    for (var i = 0; i < check_items.length; i++) {
        var item = check_items[i];
        if (item[2] && item[1].is_check_all()) {
            continue;
        }
        var value = item[1].get_value();
        if (value) {
            args[item[0]] = value;
        }
    }
    if (this.select_server.get_serverid()) {
        args['serverid'] = this.select_server.get_serverid();
    }
    if ($("user_serverid") && $("user_serverid").value) {
        args['cross_buy_serverid'] = $("user_serverid").value;
        window.server_selector && server_selector.update_recent_server_list();
    }
    if (Object.getLength(args) == 0) {
        alert("请选择搜索条件");
        return false;
    }
    QueryArgs = args;
    save_args_in_cookie(args, "overall_pet_equip_search");
    update_overall_search_saved_query();
    do_query(1);
}
function add_orderby_ev() {
    var el_list = $$("#order_menu a");
    for (var i = 0; i < el_list.length; i++) {
        var el = el_list[i];
        el.addEvent("click", function() {
            change_query_order($(this));
            return false;
        });
    }
    fix_overall_search_order_menu(OrderInfo.field_name, OrderInfo.order, $('order_menu'));
}
var OrderInfo = {
    "field_name": "",
    "order": ""
};
function change_query_order(el) {
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
    do_query(1);
}
function get_equip_addon_attr(equip_desc) {
    var re = new RegExp("#G[^#]+","g");
    var match_result = equip_desc.match(re);
    if (!match_result) {
        return "";
    }
    var attr_list = [];
    for (var i = 0; i < match_result.length; i++) {
        attr_list.push(match_result[i].replace("#G", ""));
    }
    return attr_list.join("&nbsp;");
}
function show_loading() {
    $("loading_img").setStyle("display", "");
}
function loading_finish() {
    $("loading_img").setStyle("display", "none");
}
function show_query_result(result, txt) {
    if (result["status"] != 0) {
        alert(result["msg"]);
        return;
    }
    if (!result["equip_list"] && result.msg) {
        result.equip_list = result.msg;
    }
    if (!result["pager"] && result.paging) {
        result.pager = result.paging;
    }
    if (result["equip_list"].length == 0) {
        render_to_replace("query_result", "no_result", {});
        return;
    }
    for (var i = 0; i < result["equip_list"].length; i++) {
        var equip = result["equip_list"][i]
        equip["equip_icon_url"] = ResUrl + "/images/small/" + equip["icon"];
        equip["addon_attr"] = get_equip_addon_attr(equip["desc"] || equip["equip_desc"] || "");
    }
    var ctx = {
        result: result,
        "equip_list": result["equip_list"],
        "pager": result["pager"]
    }
    QueryResult = result["equip_list"];
    render_to_replace("query_result", "equip_list_templ", ctx);
    add_orderby_ev();
    render_to_replace("pager_bar", "pager_templ", {
        "pager": result["pager"]
    });
    var el_list = $$("#soldList a.soldImg img");
    for (var i = 0; i < el_list.length; i++) {
        var el = el_list[i];
        el.addEvent("mouseover", function() {
            show_equip_tips_box($(this));
        });
        el.addEvent("mouseout", hidden_tips_box);
    }
}
function show_error() {
    render_to_replace('query_result', 'no_result', {});
    $$('#query_result p').set('html', '系统繁忙，请稍后再试');
}
function do_query(page_num) {
    QueryArgs["act"] = "overall_search_pet_equip";
    QueryArgs["page"] = page_num;
    ajax_with_recommend({
        data: Object.merge({}, QueryArgs),
        onRequest: function() {
            show_loading();
            $('query_result').empty();
        },
        onSuccess: show_query_result,
        onFailure: show_error,
        onComplete: loading_finish
    });
}
function goto(page_num) {
    do_query(page_num);
}
;(function() {
    if (typeof CreateConfig == 'undefined') {
        return;
    }
    var EquipAttr = {
        speed: "速度≥",
        fangyu: "防御≥",
        mofa: "魔法≥",
        shanghai: "伤害≥",
        hp: "气血≥",
        hit_ratio: "命中率(%)≥",
        xiang_qian_level: "灵石锻炼等级≥"
    };
    var AddonAttr = {
        addon_tizhi: "体质",
        addon_liliang: "力量",
        addon_fali: "法力",
        addon_lingli: "灵力",
        addon_minjie: "敏捷",
        addon_naili: "耐力"
    };
    var AddonAttrIpt = {
        addon_minjie_reduce: "敏捷减少≥",
        addon_sum_min: "属性总和≥"
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
                name: "装备等级",
                get_val: ctx.get().range("level_min"),
                set_val: ctx.set().slider.bind(ctx, {
                    minKey: "level_min",
                    maxKey: "level_max",
                    defaultRang: [65, 145],
                    elemId: "level_slider"
                })
            }, ctx.list({
                name: "装备类型",
                key: "equip_pos",
                listConfig: PetEquipKindInfo,
                elem: $$('#EquipPosBox'),
                isLiHasDataValue: true
            }), {
                name: "装备属性",
                get_val: function() {
                    var desc = [];
                    var inputDesc = ctx.get().input_group(EquipAttr);
                    if (inputDesc != "") {
                        desc.push(inputDesc);
                    }
                    if (arg.hasOwnProperty("xiangqian_stone_attr")) {
                        var text = "精魄灵石:" + ctx.get().list("xiangqian_stone_attr", $$("#xiangqian_stone_attr_panel li"), true);
                        desc.push(text)
                    }
                    return desc.join(",");
                },
                set_val: function(arg) {
                    ctx.set().list({
                        key: "xiangqian_stone_attr",
                        elem: $$('#xiangqian_stone_attr_panel'),
                        isLiHasDataValue: true
                    });
                    ctx.set().input_group(EquipAttr);
                }
            }, {
                name: "附加属性",
                get_val: function() {
                    var desc = [];
                    for (var key in AddonAttr) {
                        if (arg.hasOwnProperty(key)) {
                            var text = AddonAttr[key];
                            desc.push(text);
                        }
                    }
                    var inputDesc = ctx.get().input_group(AddonAttrIpt);
                    if (inputDesc != "") {
                        desc.push(inputDesc);
                    }
                    if (arg.hasOwnProperty("addon_sum_include_damage")) {
                        desc.push("含属性伤害");
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    for (var key in AddonAttr) {
                        if (arg.hasOwnProperty(key)) {
                            $$('#addon_skill_box li[data_value=' + key + ']').addClass('on');
                        }
                    }
                    ctx.set().input_group(AddonAttrIpt);
                    ctx.set().checkbox("addon_sum_include_damage", "addon_sum_include_damage");
                }
            }, {
                name: "附加状态",
                get_val: function() {
                    var desc = [];
                    if (arg.hasOwnProperty("addon_status")) {
                        desc.push(arg["addon_status"]);
                        if (arg.hasOwnProperty("include_no_skill")) {
                            desc.push("含无套装效果");
                        }
                        if (arg.hasOwnProperty("include_can_cover_skill")) {
                            desc.push("含可覆盖套装效果");
                        }
                    }
                    return desc.join(",");
                },
                set_val: function() {
                    ctx.set().input("addon_status", "addon_status");
                    ctx.set().checkbox("include_no_skill", "no_suit_effect");
                    if (arg.hasOwnProperty("include_can_cover_skill")) {
                        $('has_suit_effect').set('checked', true);
                        $('has_suit_effect').set('disabled', false);
                        $$('#has_suit_effect').getParent()[0].removeClass('disabled');
                    }
                }
            }, {
                name: "修理失败次数",
                get_val: ctx.get().input_group({
                    repair_failed_times: "修理失败次数<="
                }),
                set_val: ctx.set().input.bind(ctx, ["repair_failed_times", "repair_failed_times"])
            }, ctx.range({
                name: "价格",
                key: "price_min",
                elem: "price_min"
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
