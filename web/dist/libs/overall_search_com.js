var QueryStatus = {
    "success": 0,
    "param_error": 1,
    "need_captcha": 2,
    "failed": 3,
    "error": 4
};
var CurSearchValue = {};
CurSearchValue.order_by = {
    key: null,
    sort: null
};
function ajax_with_recommend(opts, recommendResultParse) {
    opts = Object.merge({
        data: {},
        ajaxGuardParams: {},
        onRequest: function() {},
        onSuccess: function() {},
        onFailure: function() {},
        onComplete: function() {}
    }, opts || {});
    opts.onRequest();
    var params = Object.merge({}, opts.data);
    var searchType = params.act;
    params.act = 'recommd_by_role';
    params.count = 15;
    params.search_type = searchType;
    params.view_loc = window.equip_refer_loc || '';
    var recommdRequest = ApiRecommd.queryList(params, {
        onSuccess: function(result) {
            var orgResult = Object.merge({}, result);
            var data = {};
            if (recommendResultParse) {
                data = recommendResultParse(result);
            } else {
                if ('msg'in result || result.status != 1) {
                    data = {
                        status: 1,
                        msg: result.msg
                    };
                } else {
                    data = {
                        status: 0,
                        msg: decode_equip_list(result.equip_list || []),
                        paging: result.pager || {}
                    };
                }
            }
            if (ApiRecommd.passAjaxGuard(orgResult, opts.ajaxGuardParams)) {
                opts.onSuccess(data);
            }
            opts.onComplete();
            window.cbg_tracer && cbg_tracer.listen_equips_exposure();
        },
        onFailure: function() {
            opts.onFailure();
            opts.onComplete();
        }
    });
}
function overall_search(search_arg, page, order_by) {
    if (!page) {
        page = 1;
    }
    var arg = {
        "act": OverallSearchAct,
        "page": page
    };
    if (order_by.key) {
        arg['order_by'] = order_by.key + ' ' + order_by.sort;
    }
    for (p in search_arg) {
        arg[p] = search_arg[p];
    }
    ajax_with_recommend({
        data: arg,
        onRequest: function() {
            $('loading_img').setStyle('display', '');
            $('search_result').empty();
            $('pager').empty();
        },
        onFailure: function() {
            render_to_replace('search_result', 'search_empty_templ');
            $$('#search_result p').set('html', '系统繁忙，请稍后再试');
        },
        onSuccess: function(result) {
            if (result.status != 0) {
                alert(result.msg);
                return;
            }
            if (result.msg.length > 0) {
                var equips = result.msg;
                render_to_replace('search_result', 'search_result_templ', {
                    result: result,
                    'equips': equips
                });
                reg_tips_event();
                fix_overall_search_order_menu(order_by.key, order_by.sort);
            } else {
                render_to_replace('search_result', 'search_empty_templ');
            }
            if (result.paging.num_end > 1) {
                render_to_replace("pager", "pager_templ", {
                    "pager": result.paging
                });
            }
        },
        onComplete: function() {
            $('loading_img').setStyle('display', 'none');
        }
    });
}
function fix_overall_search_order_menu(key, order, $root) {
    key = key || '';
    order = order || '';
    $root = $root || $('order_menu');
    if (!$root) {
        return;
    }
    var elList = $root.getElements('a[data_attr_name]');
    elList.forEach(function($el, i) {
        var name = $el.get('data_attr_name') || '';
        if ($el.get('data_sort_way') == 'single') {
            $el.getParent('th')[name == key ? 'addClass' : 'removeClass']('is-selected');
        } else {
            $el.set('text', $el.get('text').trim().replace(/[↑↓]$/g, ''));
            if (name == key) {
                $el.set('text', $el.get('text') + (order == 'DESC' ? '↓' : '↑'));
            }
        }
    });
}
function go_overall_search(arg) {
    CurSearchValue.arg = arg;
    overall_search(arg, null, CurSearchValue.order_by);
    update_overall_search_saved_query();
}
function goto(page_num) {
    if (CurSearchValue.arg) {
        overall_search(CurSearchValue.arg, page_num, CurSearchValue.order_by);
    }
}
function pager_keydown_handler(src, e) {
    var e = e || window.event;
    var keynum;
    try {
        keynum = e.keyCode
    } catch (e) {
        keynum = e.which
    }
    if (keynum == 13) {
        goto(src.value);
    }
}
function search_order_by(order_key) {
    if (CurSearchValue.order_by.key == order_key) {
        CurSearchValue.order_by.sort = CurSearchValue.order_by.sort == 'DESC' ? 'ASC' : 'DESC';
    } else {
        CurSearchValue.order_by.key = order_key;
        CurSearchValue.order_by.sort = 'DESC';
    }
    overall_search(CurSearchValue.arg, null, CurSearchValue.order_by);
}
function get_name_from_conf(id, conf) {
    for (var i = 0; i < conf.length; i++) {
        if (conf[i][0] == id) {
            return conf[i][1];
        }
    }
}
function get_names_by_value(value, conf) {
    return value.map(function(v) {
        return get_name_from_conf(v, conf)
    });
}
function get_name_from_dict(id, conf) {
    for (var p in conf) {
        if (conf[p] == id) {
            return p;
        }
    }
}
var UserServerSelector = new Class({
    initialize: function() {
        var self = this;
        $("btn_reset_user_server").addEvent("click", function() {
            Cookie.write("cross_server_serverid", "");
            Cookie.write("cross_server_areaname", "");
            Cookie.write("cross_server_servername", "");
            if ($("user_serverid")) {
                $("user_serverid").value = "";
            }
            self.no_server_selected();
            return false;
        });
    },
    no_server_selected: function() {
        render_to_replace("user_server_info_box", "no_server_select_templ", {});
        var self = this;
        $("btn_show_server_select_box").addEvent("click", function() {
            self.show_server_select_box();
            return false;
        });
        self.render_recent_server_list();
    },
    chose_server: function(args) {
        Cookie.write("cross_server_serverid", decodeURIComponent(args["server_id"]));
        Cookie.write("cross_server_areaname", decodeURIComponent(args["area_name"]));
        Cookie.write("cross_server_servername", decodeURIComponent(args["server_name"]));
        this.close_popup_box();
        this.show_user_server_info();
    },
    close_popup_box: function() {
        this.dialog.hide();
    },
    show_server_select_box: function() {
        var tmpl = ['<div class="blockCont">', '<div>', '<div class="searchServerWrap">', '<input id="search_server_input" class="txt1" placeholder="服务器搜索" />', '<div id="search_server_list_panel" class="drop"></div>', '</div>', '<button id="search_server_confirm" class="btn1" style="margin-left:4px;">确定</button>', '</div>', '<div id="area_list_panel"></div>', '<div class="blank12"></div>', '<div id="server_list_panel"></div>', '</div>'].join('');
        this.dialog = new PopupDialog("选择服务器",tmpl);
        var self = this;
        var chose_server = function(args) {
            self.chose_server(args);
        };
        var obj = new SelectServer(chose_server);
        obj.show();
        this.dialog.show();
    },
    show_server: function(serverid, area_name, server_name) {
        var ctx = {
            "serverid": serverid,
            "area_name": area_name,
            "server_name": server_name
        };
        render_to_replace("user_server_info_box", "user_server_info_templ", ctx);
        var self = this;
        $("btn_change_user_server").addEvent("click", function() {
            self.show_server_select_box();
        });
        self.render_recent_server_list();
    },
    show_user_server_info: function() {
        var cross_serverid = Cookie.read("cross_server_serverid");
        if (!cross_serverid) {
            this.no_server_selected();
            return;
        }
        var cross_servername = decodeURIComponent(Cookie.read("cross_server_servername"));
        var cross_areaname = decodeURIComponent(Cookie.read("cross_server_areaname"));
        this.show_server(cross_serverid, cross_areaname, cross_servername);
    },
    render_recent_server_list: function() {
        var self = this;
        if (!$('recent_selected_server')) {
            return;
        }
        try {
            if (localStorage.getItem('recent_server_list')) {
                var recent_server_list = JSON.parse(localStorage.getItem('recent_server_list'));
                var arr = ['<strong class="tit inline-block">最近搜索：</strong>'];
                for (var i = 0; i < recent_server_list.length; i++) {
                    var item = recent_server_list[i];
                    arr.push('<li class="recent_server_item inline-block" data_serverid="' + item.serverid + '">' + item.area_name + '-' + item.server_name + '</li>');
                }
                $('recent_selected_server').innerHTML = arr.join('');
                $$('#recent_selected_server .recent_server_item').each(function(el) {
                    el.addEvent("click", function() {
                        var areaServerName = el.innerHTML.split('-');
                        var serverid = el.getAttribute('data_serverid');
                        Cookie.write("cross_server_serverid", serverid);
                        Cookie.write("cross_server_areaname", areaServerName[0]);
                        Cookie.write("cross_server_servername", areaServerName[1]);
                        var ctx = {
                            "serverid": serverid,
                            "area_name": areaServerName[0],
                            "server_name": areaServerName[1]
                        };
                        render_to_replace("user_server_info_box", "user_server_info_templ", ctx);
                        $("btn_change_user_server").addEvent("click", function() {
                            self.show_server_select_box();
                        });
                        self.render_recent_server_list();
                    });
                });
            }
        } catch (e) {}
    },
    update_recent_server_list: function() {
        if (!$("user_serverid")) {
            return;
        }
        var self = this;
        var recentServerList = [];
        try {
            var serverInfo = {
                area_name: decodeURIComponent(Cookie.read("cross_server_areaname")),
                server_name: decodeURIComponent(Cookie.read("cross_server_servername")),
                serverid: $("user_serverid").value
            };
            if (localStorage.getItem('recent_server_list')) {
                recentServerList = JSON.parse(localStorage.getItem('recent_server_list'));
                var index = -1;
                for (var i = 0; i < recentServerList.length; i++) {
                    var item = recentServerList[i];
                    if (item.serverid === serverInfo.serverid && item.area_name === serverInfo.area_name && item.server_name === serverInfo.server_name) {
                        index = i;
                        break;
                    }
                }
                if (index != -1) {
                    recentServerList.splice(index, 1);
                }
                recentServerList.unshift(serverInfo);
            } else {
                recentServerList.push(serverInfo);
            }
            recentServerList = recentServerList.slice(0, 4);
            localStorage.setItem('recent_server_list', JSON.stringify(recentServerList));
            self.render_recent_server_list();
        } catch (e) {}
    }
});
function get_cross_buy_addon_args() {
    var cross_serverid = Cookie.read("cross_server_serverid");
    if (!cross_serverid) {
        return "";
    }
    var arg = {
        "cross_buy_serverid": cross_serverid,
        "cross_buy_server_name": decodeURIComponent(Cookie.read("cross_server_servername")),
        "cross_buy_area_name": decodeURIComponent(Cookie.read("cross_server_areaname"))
    };
    return Object.toQueryString(arg);
}
var CrossServerBuyOperator = new Class({
    initialize: function() {
        var btn = $("btn_buy");
        var self = this;
        var confirmGradeLimit = false;
        var equipInfoServerid = EquipInfo["serverid"] || EquipInfo["server_id"];
        var checkEquipId = equip.serverid || equip.server_id;
        var isCrossBuy = LoginInfo.serverid != checkEquipId;
        if (!equip["is_selling"]) {
            btn.setStyle("display", "none");
            return;
        }
        if (!AllowCrossBuy || CrossBuyServerids.length <= 1 || !CrossBuyKindids.contains(EquipInfo["kindid"])) {
            btn.addEvent("click", function() {
                if (EquipInfo['is_time_lock'] > 0) {
                    var isConfirm = window.confirm("请注意：购买该物品后将带有" + (EquipInfo.time_lock_days || "150") + "天转服时间锁");
                    if (isConfirm) {
                        CBG.clickLog('lduoajjn', '确认');
                    } else {
                        CBG.clickLog('lduoajjn', '取消');
                        return;
                    }
                }
                if (window.isFakeRole && EquipInfo["storage_type"] != StorageStype.role) {
                    window.fakeRoleBuyPopup && fakeRoleBuyPopup();
                    return;
                }
                try_login_to_buy(EquipInfo["equipid"], equipInfoServerid, EquipInfo["server_name"], EquipInfo["area_id"], EquipInfo["area_name"], EquipInfo["eid"]);
            });
            btn.set("value", '登录"' + EquipInfo["server_name"] + '"购买');
        } else if (this.check_if_can_add_order_directly()) {
            if (!EquipInfo["is_pass_fair_show"] && $("fairshow_buy_info")) {
                $("fairshow_buy_info").setStyle("display", "");
            }
            $("buy_equip_tips").setStyle("display", "");
            btn.addEvent("click", function() {
                if (this.hasClass('disabled'))
                    return;
                if (!!EquipInfo["is_xyq_game_role_kunpeng_reach_limit"]) {
                    CBG.confirm('超级鲲鹏携带上限为2只，若超出限制将无法正常取回，请确认', {
                        confirmText: '确认购买',
                        cancelText: '暂不购买'
                    }).addEvent('confirm', function() {
                        executePurchaseLogic();
                    });
                } else {
                    executePurchaseLogic();
                }
                function executePurchaseLogic() {
                    var equipStorageType = EquipInfo["storage_type"];
                    if (EquipInfo['is_time_lock'] > 0) {
                        if (!window.confirm("请注意：购买该物品后将带有" + (EquipInfo.time_lock_days || "150") + "天转服时间锁"))
                            return;
                    }
                    if (EquipInfo['kindid'] == '85' || EquipInfo['kindid'] == '86') {
                        var isConfirm = window.confirm("礼盒/礼币购买后将调整为绑定状态，是否确认购买");
                        if (!isConfirm) {
                            return;
                        }
                    }
                    if (window.isFakeRole && equipStorageType != StorageStype.role) {
                        window.fakeRoleBuyPopup && fakeRoleBuyPopup();
                        return;
                    }
                    if (!EquipInfo['is_pass_fair_show'] && !$('agree_fair_show_pay').checked) {
                        alert('同意公示期预定收费规则后，才能预定');
                        return false;
                    }
                    var equipServerid = parseInt(equipInfoServerid);
                    var loginServerid = parseInt(LoginInfo["serverid"]);
                    var isEquipInTestServer = test_server_list.contains(equipServerid);
                    var isUserInTestServer = test_server_list.contains(loginServerid);
                    var isEquipInCanTakeAwayServer = window.AllowTakeAwayServerList && AllowTakeAwayServerList.contains(equipServerid);
                    var isEquipOrPet = equipStorageType == StorageStype.equip || equipStorageType == StorageStype.pet;
                    if (equipServerid != loginServerid && !isEquipInCanTakeAwayServer) {
                        if (isEquipInTestServer && !isUserInTestServer) {
                            var ret = confirm("1.此物品所在服务器为本周测试服，购买后需买卖双方服务器更新为相同版本时方可取出（测试服每周二更新）。\n\n2.藏宝阁有未取出物品时无法转服。 ");
                            if (ret !== true) {
                                return;
                            }
                        }
                    }
                    if (has_grade_limit && !confirmGradeLimit) {
                        var isPet = equipStorageType == StorageStype.pet;
                        CBG.clickLog("web_other_4_1", isPet ? '召唤兽' : '装备');
                        var tips = '';
                        if (isPet) {
                            tips = isCrossBuy ? '角色等级不满足召唤兽的参战等级要求时，从游戏取出后180天无法再次寄售、游戏内交易、给与等方式转移。' : '角色等级不满足召唤兽的参战等级要求时，购买后将无法再次寄售。';
                        } else {
                            tips = isCrossBuy ? '当前角色等级不满足该装备的携带等级，从游戏取出后180天无法通过再次寄售、游戏内交易、给与等方式转移' : '当前角色等级不满足该装备的携带等级，购买后将无法再次寄售。';
                        }
                        confirmGradeLimit = confirm(tips);
                        if (confirmGradeLimit) {
                            CBG.clickLog("web_other_4_2", isPet ? '召唤兽' : '装备');
                        }
                        return;
                    }
                    var res = handleDraw(EquipInfo["is_onsale_protection_period"], EquipInfo["is_random_draw_period"], EquipInfo["onsale_protection_end_time"]);
                    if (!res)
                        return;
                    self.check_have_unpaid_cross_server_orders();
                }
            });
            if (EquipInfo["is_pass_fair_show"]) {
                btn.set("value", "下单购买");
            } else {
                btn.set("value", "预订");
            }
            if (equipInfoServerid != LoginInfo["serverid"]) {
                this.display_cross_buy_poundage();
            }
            var prepayInfo = window.prepayInfo || {};
            var PREPAY_BARGAIN = window.PREPAY_BARGAIN || {};
            var status = prepayInfo.status;
            var is_accepted = prepayInfo.is_accepted;
            if (PREPAY_BARGAIN.isPrepayLeftUnpaidHandling(status, is_accepted)) {
                btn.set("value", "待卖家处理");
                btn.addClass('disabled');
            }
            if (PREPAY_BARGAIN.isPrepayLeftUnpaidAccepted(status, is_accepted)) {
                btn.set("value", "前往APP支付尾款");
                btn.addClass('disabled');
            }
            if (prepayInfo.is_booking_by_other) {
                btn.set("value", "被预订");
                btn.addClass('disabled');
            }
            initBuyBtnTrace(btn);
        } else if (this.if_go_login_buy_step()) {
            btn.addEvent("click", function() {
                if (window.isFakeRole && EquipInfo["storage_type"] != StorageStype.role) {
                    window.fakeRoleBuyPopup && fakeRoleBuyPopup();
                    return;
                }
                window.location.href = self.get_login_buy_url();
            });
            btn.set("value", "登录购买");
        } else {
            btn.addEvent("click", function() {
                if (window.isFakeRole && EquipInfo["storage_type"] != StorageStype.role) {
                    window.fakeRoleBuyPopup && fakeRoleBuyPopup();
                    return;
                }
                self.show_popup_select_server_box();
            });
            btn.set("value", "登录购买");
        }
    },
    check_have_unpaid_cross_server_orders: function() {
        var equipInfoServerid = EquipInfo["serverid"] || EquipInfo["server_id"];
        var self = this;
        var url = CgiRootUrl + '/usertrade.py?act=ajax_have_unpaid_cross_server_orders&obj_serverid=' + equipInfoServerid;
        var Ajax = new Request.JSON({
            "url": url,
            "onSuccess": function(res) {
                var status = res.status
                  , has_cross_server_order = res.has_cross_server_order
                  , is_cross_server_order = res.is_cross_server_order;
                if (status && has_cross_server_order == 1 && is_cross_server_order) {
                    self.show_has_cross_order_modal(1);
                } else if (status && has_cross_server_order == 2 && is_cross_server_order) {
                    self.show_has_cross_order_modal(0);
                } else {
                    window.location.href = self.get_add_order_url(false);
                }
            },
            "onError": function() {
                window.location.href = self.get_add_order_url(false);
            }
        });
        Ajax.get();
    },
    show_has_cross_order_modal: function(isNormal) {
        $$('#hasCrossOrderModal,#hasCrossorderMask').setStyle('display', 'block');
        isNormal ? $('normalCrossModal').setStyle('display', 'block') : $('drawCrossModal').setStyle('display', 'block')
        this.handle_cross_order_modal_btn();
    },
    hide_has_cross_order_modal: function() {
        $$('#hasCrossOrderModal,#hasCrossorderMask').setStyle('display', 'none');
    },
    handle_cross_order_modal_btn: function() {
        var self = this;
        $$('.closeCrossModal').addEvent('click', function() {
            self.hide_has_cross_order_modal();
        });
    },
    is_login: function() {
        return LoginInfo && LoginInfo["login"];
    },
    get_add_order_url: function(isForceAddOrder) {
        var equipInfoServerid = EquipInfo["serverid"] || EquipInfo["server_id"];
        var arg = {
            "obj_serverid": equipInfoServerid,
            "eid": EquipInfo["eid"],
            "device_id": get_fingerprint(),
            "equip_refer": getPara("equip_refer"),
            "act": "add_cross_order_by_eid",
            "safe_code": SafeCode,
            "reonsale_identify": window.reonsale_identify || '',
            "view_loc": window.equip_refer_loc
        };
        var from_shareid = getPara('from_shareid');
        if (from_shareid) {
            arg["&from_shareid"] = from_shareid;
        }
        if (isForceAddOrder) {
            arg.force_add_cross_server_order = 1;
        }
        return CgiRootUrl + "/usertrade.py?" + Object.toQueryString(arg);
    },
    display_cross_buy_poundage: function() {
        var equipInfoServerid = EquipInfo["serverid"] || EquipInfo["server_id"];
        var url = CgiRootUrl + "/userinfo.py";
        var args = {
            "obj_serverid": equipInfoServerid,
            "obj_equipid": EquipInfo["equipid"],
            "act": "get_cross_buy_poundage"
        };
        var display_poundage = function(data, txt) {
            if (data["status"] != 1) {
                return;
            }
            var el = $("equip_price_addon_info");
            var cross_server_poundage = data.cross_server_poundage || 0;
            var cross_server_poundage_display_mode = data.cross_server_poundage_display_mode;
            var cross_server_poundage_discount_label = data.cross_server_poundage_discount_label;
            if (cross_server_poundage_display_mode) {
                cross_server_poundage = data.cross_server_poundage_origin || 0;
            }
            if (el) {
                el.innerHTML = "+&nbsp;￥" + fen2yuan(cross_server_poundage) + "（元）(跨服交易费)";
            }
            var $discount = $('cross-server-discount-tag');
            if (cross_server_poundage_display_mode && $discount) {
                if (!cross_server_poundage_discount_label) {
                    cross_server_poundage_discount_label = "下单立减跨服费";
                }
                $discount.getElement('.js_discount_label').set('html', cross_server_poundage_discount_label);
                $discount.getElement('.js_discount_price').set('html', fen2yuan(data.cross_server_poundage_origin - data.cross_server_poundage_discount));
                $discount.setStyle('display', 'inline-block');
            }
        };
        var Ajax = new Request.JSON({
            "url": url,
            "onSuccess": display_poundage,
            "noCache": true
        });
        Ajax.get(args);
    },
    get_login_buy_url: function() {
        var equipInfoServerid = EquipInfo["serverid"] || EquipInfo["server_id"];
        var arg = {
            "obj_serverid": equipInfoServerid,
            "obj_equipid": EquipInfo["equipid"],
            "equip_refer": getPara("equip_refer"),
            "act": "show_cross_server_buy_detail"
        };
        window.equip_refer_loc && (arg['view_loc'] = equip_refer_loc);
        var equip_detail_url = CgiRootUrl + "/usertrade.py?" + Object.toQueryString(arg);
        var login_arg = {
            "server_id": getPara("cross_buy_serverid"),
            "server_name": decodeURIComponent(getPara("cross_buy_server_name")),
            "area_name": decodeURIComponent(getPara("cross_buy_area_name")),
            "return_url": equip_detail_url,
            "act": "show_login"
        };
        return HttpsCgiRootUrl + "/show_login.py?" + Object.toQueryString(login_arg);
    },
    check_if_can_add_order_directly: function() {
        if (!LoginInfo || !LoginInfo["login"]) {
            return false;
        }
        if (CrossBuyServerids.contains(LoginInfo["serverid"])) {
            return true;
        } else {
            return false;
        }
    },
    if_go_login_buy_step: function() {
        var buy_serverid = getPara("cross_buy_serverid");
        var buy_server_name = getPara("cross_buy_server_name");
        var buy_area_name = getPara("cross_buy_area_name");
        if (!buy_serverid || !buy_server_name || !buy_area_name) {
            return false;
        }
        if (!CrossBuyServerids.contains(parseInt(buy_serverid))) {
            return false;
        }
        return true;
    },
    chose_server: function(args, is_show_all_servers) {
        var equip = EquipInfo;
        var equipInfoServerid = EquipInfo["serverid"] || EquipInfo["server_id"];
        var equip_refer = getPara('equip_refer');
        var equip_detail_url = HomePage + "/equip?s=" + equipInfoServerid + "&eid=" + equip["eid"] + "&o";
        if (equip_refer) {
            equip_detail_url += "&equip_refer=" + equip_refer;
        }
        if (window.equip_refer_loc) {
            equip_detail_url += '&view_loc=' + encodeURIComponent(equip_refer_loc);
        }
        var login_arg = {
            "server_id": args["server_id"],
            "server_name": args["server_name"],
            "area_id": args["area_id"],
            "area_name": args["area_name"],
            "return_url": equip_detail_url,
            "act": "show_login"
        };
        var url = HttpsCgiRootUrl + "/show_login.py?" + Object.toQueryString(login_arg);
        window.location.href = url;
    },
    show_popup_select_server_box: function(is_show_all_servers) {
        var tmpl = ['<div class="blockCont">', '<div id="area_list_panel"></div>', '<div class="blank12"></div>', '<div id="server_list_panel"></div>', '<div class="serverTips" style="display:none" id="not_allow_buy_tips">', '您所选择的服务器暂不可购买此商品。建议您返回选择服务器，以便筛选到可交易的商品。', '</div>', '</div>'].join('');
        this.dialog = new PopupDialog("选择服务器",tmpl);
        var self = this;
        var chose_server = function(args) {
            if (!is_show_all_servers && !CrossBuyServerids.contains(parseInt(args["server_id"]))) {
                $("not_allow_buy_tips").setStyle("display", "");
                return;
            }
            self.chose_server(args, is_show_all_servers);
        };
        var disable_server = function(a_el, serverid) {
            if (!is_show_all_servers && !CrossBuyServerids.contains(parseInt(serverid))) {
                a_el.getParent().addClass("disabled");
                a_el.setStyle("cursor", "pointer");
            }
        };
        $("not_allow_buy_tips").setStyle("display", "none");
        var obj = new SelectServer(chose_server,disable_server);
        obj.show();
        this.dialog.show();
    }
});
function save_args_in_cookie(args, search_type) {
    var save_ck_name = getPara("save_ck_name");
    if (save_ck_name) {
        save_ck_name = save_ck_name.replace("#", "");
        var save_data = {};
        Object.merge(save_data, args, {
            "search_type": search_type
        });
        var ck_str = JSON.encode(save_data);
        Cookie.write(save_ck_name, ck_str, {
            "domain": "163.com"
        });
    }
}
function restore_query_form(arg) {
    if (typeof RecentSearchConfig == 'undefined') {
        return;
    }
    $("reset_all").fireEvent("click");
    var config = new RecentSearchConfig(arg).get_config();
    config.forEach(function(component) {
        component.set_val();
    });
}
;var RecentUtil = new Class({
    initialize: function(arg) {
        this.arg = arg;
    },
    get: function() {
        var ctx = this;
        var arg = ctx.arg;
        return {
            list: function(key, listConfig, formElem) {
                if (!arg.hasOwnProperty(key))
                    return "";
                var listArr = arg[key].split(",").map(function(l) {
                    return l.trim();
                });
                var desc = [];
                var formElem = formElem || false;
                if (formElem) {
                    listConfig.forEach(function(li) {
                        listArr.forEach(function(val, i) {
                            if (li.get("data_value") == val) {
                                var text = li.getElement("span").get("text");
                                desc.push(text);
                            }
                        });
                    });
                } else if (listConfig instanceof Array) {
                    listArr.forEach(function(listId) {
                        listConfig.forEach(function(config) {
                            if (config[0] == listId) {
                                desc.push(config[1]);
                            }
                        });
                    });
                } else {
                    listArr.forEach(function(id, i) {
                        desc.push(listConfig[id]);
                    });
                }
                return desc.join(",");
            },
            range: function(minKey) {
                var maxKey = minKey.replace('min', 'max');
                if (!arg.hasOwnProperty(minKey) && !arg.hasOwnProperty(maxKey)) {
                    return "";
                }
                var minVal = "不限";
                var maxVal = "不限";
                var expand = minKey.test(/price/g) ? 100 : 1;
                if (arg.hasOwnProperty(minKey)) {
                    minVal = arg[minKey] / expand;
                }
                if (arg.hasOwnProperty(maxKey)) {
                    maxVal = arg[maxKey] / expand;
                }
                return minVal + "-" + maxVal;
            },
            input_group: function(inputsConfig) {
                var desc = [];
                for (var key in inputsConfig) {
                    if (arg.hasOwnProperty(key)) {
                        desc.push(inputsConfig[key] + arg[key]);
                    }
                }
                return desc.join(",");
            },
            select: function(key, elem) {
                var desc = "";
                if (arg.hasOwnProperty(key)) {
                    desc = $(elem).getElement("option[value=" + arg[key] + "]").get("text");
                }
                return desc;
            },
            match_rang_list: function(matchKey, listKey, $li) {
                var matchDesc = "满足一种";
                if (arg.hasOwnProperty(matchKey)) {
                    if (arg[matchKey] == 1 || arg[matchKey] == "and") {
                        matchDesc = "满足全部";
                    }
                }
                var listDesc = ctx.get().list(listKey, $li, true);
                return matchDesc + ":" + listDesc;
            }
        }
    },
    set: function() {
        var ctx = this;
        var arg = ctx.arg;
        return {
            list: function(option) {
                var option = Object.merge({
                    key: "",
                    elem: "",
                    isLiHasDataValue: false
                }, option);
                var key = option.key
                  , $elem = option.elem
                  , isLiHasDataValue = option.isLiHasDataValue;
                if (!arg.hasOwnProperty(key))
                    return;
                var value = arg[key];
                var valueList = value.split(",");
                if (isLiHasDataValue) {
                    valueList.forEach(function(listValue) {
                        if (key === 'school_change_list' && listValue === '0') {
                            listValue = '99999'
                        }
                        $elem.getElement('li[data_value="' + listValue + '"]').addClass('on');
                    });
                } else {
                    var parent_el = $elem.getParent()[0];
                    if (parent_el && parent_el.btn_checker) {
                        parent_el.btn_checker.restore(valueList);
                        return false;
                    }
                    $elem.forEach(function($li) {
                        var liVal = $li.retrieve('value').toString();
                        if (valueList.indexOf(liVal) > -1) {
                            $li.addClass('on');
                        }
                    });
                }
            },
            slider: function(option) {
                var min = option.defaultRang[0];
                var max = option.defaultRang[1];
                if (arg.hasOwnProperty(option.minKey)) {
                    min = arg[option.minKey];
                }
                if (arg.hasOwnProperty(option.maxKey)) {
                    max = arg[option.maxKey];
                }
                $(option.elemId).slider.set_value([min, max]);
            },
            input: function(key, elemId) {
                arg.hasOwnProperty(key) && $(elemId).set('value', arg[key]);
            },
            checkbox: function(key, elemId) {
                arg.hasOwnProperty(key) && $(elemId).set('checked', true);
            },
            select: function(key, elemId) {
                arg.hasOwnProperty(key) && $(elemId).set('value', arg[key]);
            },
            range: function(minKey, minElemId) {
                var maxKey = minKey.replace("min", "max");
                var maxElemId = minElemId.replace("min", "max");
                var expand = minKey.test(/price/g) ? 100 : 1;
                if (arg.hasOwnProperty(minKey)) {
                    $(minElemId).set('value', arg[minKey] / expand);
                }
                if (arg.hasOwnProperty(maxKey)) {
                    $(maxElemId).set('value', arg[maxKey] / expand);
                }
            },
            input_group: function(inputsConfig, iptElemPrefix) {
                var iptElemPrefix = iptElemPrefix || "";
                for (var key in inputsConfig) {
                    if (arg.hasOwnProperty(key)) {
                        $(iptElemPrefix + key).set("value", arg[key]);
                    }
                }
            }
        }
    }
});
var CreateConfig = new Class({
    Extends: RecentUtil,
    initialize: function(arg) {
        this.arg = arg;
    },
    list: function(option) {
        var ctx = this;
        return Object.merge({}, option, {
            get_val: ctx.get().list(option.key, option.listConfig),
            set_val: ctx.set().list.bind(ctx, {
                key: option.key,
                elem: option.elem,
                isLiHasDataValue: option.isLiHasDataValue || false
            })
        });
    },
    appoint_server: function(option) {
        var arg = this.arg;
        return Object.merge({}, option, {
            name: "指定区服",
            get_val: function() {
                var desc = '';
                if (arg.hasOwnProperty('serverid')) {
                    var value = arg['serverid'];
                    for (var areaid in server_data) {
                        var server_list = server_data[areaid][1];
                        for (var server in server_list) {
                            if (server_list[server][0] == value) {
                                var area = server_data[areaid][0][0];
                                var serverDetail = server_list[server][1];
                                desc = area + '-' + serverDetail;
                                break;
                            }
                        }
                    }
                }
                return desc;
            },
            set_val: function() {
                if (arg.hasOwnProperty('serverid')) {
                    var value = arg['serverid'];
                    for (var areaid in server_data) {
                        var server_list = server_data[areaid][1];
                        for (var server in server_list) {
                            if (server_list[server][0] == value) {
                                var areaId = server_data[areaid][0][4];
                                var dropSelect = new DropSelectServer($('overall_sel_area'),$('ovarall_sel_server'));
                                var $selectAreaOption = $('overall_sel_area').getElement('option[value=' + areaId + ']');
                                if ($selectAreaOption) {
                                    $selectAreaOption.set('selected', 'selected');
                                    dropSelect.gen_server_box();
                                }
                                $('overall_sel_area').fireEvent('change');
                                var $selectServerOption = $('ovarall_sel_server').getElement('option[value=' + value + ']');
                                if ($selectServerOption) {
                                    $selectServerOption.set('selected', 'selected');
                                }
                                $('ovarall_sel_server').fireEvent('change');
                                break;
                            }
                        }
                    }
                }
            }
        })
    },
    range: function(option) {
        var ctx = this;
        return Object.merge({}, option, {
            get_val: ctx.get().range(option.key),
            set_val: ctx.set().range.bind(ctx, [option.key, option.elem])
        });
    },
    input_group: function(option) {
        var ctx = this;
        return Object.merge({}, option, {
            get_val: ctx.get().input_group(option.inputConfig),
            set_val: ctx.set().input_group.bind(ctx, [option.inputConfig, option.elem])
        })
    }
})
var GetSavedQueryDesc = new Class({
    initialize: function(saved_query_list) {
        this.data = saved_query_list;
    },
    get_per_search_desc: function(arg) {
        if (typeof RecentSearchConfig == 'undefined') {
            return [];
        }
        var ctx = this;
        var descArray = []
        var config = new RecentSearchConfig(arg).get_config();
        config.forEach(function(component) {
            var desc = (component.get_val instanceof Function) ? component.get_val() : component.get_val;
            if (desc != "") {
                descArray.push([component.name, desc]);
            }
        });
        return descArray;
    },
    get_all_desc: function() {
        var ctx = this;
        var modalDesc = [];
        var navBarDesc = [];
        if (ctx.data.length > 0) {
            ctx.data.forEach(function(arg) {
                var descArr = ctx.get_per_search_desc(arg);
                if (descArr.length > 0) {
                    modalDesc.push(descArr);
                }
            });
            navBarDesc = ctx.make_desc_for_nav_bar(modalDesc);
        }
        ;return {
            navBarDesc: navBarDesc,
            modalDesc: modalDesc
        };
    },
    make_desc_for_nav_bar: function(allDesc) {
        var navBarTextArr = [];
        allDesc.forEach(function(textArr, index) {
            var NavText = [];
            textArr.forEach(function(desc) {
                var text = desc[0] + ":" + desc[1];
                NavText.push(text);
            });
            var navDesc = NavText.join(' , ');
            if (navDesc.length > 30) {
                navDesc = navDesc.substr(0, 15) + '...';
            }
            navBarTextArr.push(navDesc);
        });
        return navBarTextArr;
    }
});
function select_server_by_homepage(return_url) {
    if (return_url) {
        Cookie.write('login_return_url', return_url);
    }
    location.href = '/';
}
function registerAutoTip($root, options) {
    if (!$root) {
        return
    }
    options = Object.merge({
        target: '.jsAutoTip',
        tip: {
            dir: 'bottom',
            y: 4,
            x: 'auto'
        }
    }, options || {});
    var tip = null;
    var timer = null;
    var cleanup = function() {
        timer && clearTimeout(timer);
        timer = null;
        tip && tip.hide();
        tip = null;
    };
    $root.getElements(options.target).addEvent('mouseenter', function() {
        var $el = $(this);
        cleanup();
        timer = setTimeout(function() {
            var html = $el.get('title') || '';
            var sel = $el.get('data-tip');
            if (sel) {
                var $next = $el.getNext(sel);
                $next && (html = $next.get('html'));
            }
            tip = new FloatTip($el,options.tip);
            tip.show(html);
        }, 120);
    }).addEvent('mouseleave', cleanup);
}
