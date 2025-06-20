'use strict';
var ApiRecommd = (function() {
    function noop() {}
    function passAjaxGuard(data, params) {
        var ajaxGuard = new AjaxGuard(Object.merge({
            code: {
                login: 2,
                captcha: 3,
                mibao: 4,
                otp: 5
            }
        }, params || {}));
        return ajaxGuard.isPass(data);
    }
    function request(url, params, opts) {
        params = Object.merge({
            _: new Date / 1
        }, params || {});
        opts = Object.merge({
            needAjaxGuard: false,
            ajaxGuardParams: {},
            onSuccess: noop,
            onFailure: noop,
            onComplete: noop,
            timeout: 10000
        }, opts || {});
        var req = new Request.JSONP(Object.merge({
            url: url
        }));
        req.addEvent('failure', function() {
            var args = arguments;
            opts.onFailure.apply(this, args);
            opts.onComplete.apply(this, args);
            wlog('RECOMMAND_TIMEOUT', ['timeout=' + opts.timeout, 'params=' + JSON.encode(params)].join('|'));
            reportReqLog(req.options, {
                is_success: false
            });
        });
        req.addEvent('success', function(data) {
            if (data && data.equip_list && data.equip_list.length) {
                data.equip_list = decode_equip_list(data.equip_list);
            }
            var args = [data];
            if (data && ('pager'in data)) {
                var pager = data.pager;
                var start = 1;
                var cur = pager.cur_page;
                var total = pager.total_pages;
                var now = {
                    cur_page: cur,
                    num_end: total
                };
                if (cur - 2 > 0) {
                    start = cur - 2;
                }
                now.num_begin = start;
                data.pager = now;
            }
            if (opts.needAjaxGuard) {
                if (passAjaxGuard(data, opts.ajaxGuardParams) == true) {
                    opts.onSuccess.apply(this, args);
                }
            } else {
                opts.onSuccess.apply(this, args);
            }
            opts.onComplete.apply(this, args);
            if (!data) {
                wlog('RECOMMAND_DATA_ERROR', ['result=' + JSON.encode(data).replace(/"/g, '').slice(0, 100), 'url=' + url, 'params=' + JSON.encode(params)].join('|'));
            } else if (params.count && data.pager && data.pager.cur_page < data.pager.num_end) {
                var length = (data.equip_list || []).length || 0;
                if (length < params.count) {
                    wlog('RECOMMAND_COUNT_ERROR', ['tag=' + (data.equip_list && data.equip_list[0] && data.equip_list[0].tag || ''), 'count=' + length + '/' + params.count, 'url=' + url, 'params=' + JSON.encode(params)].join('|'));
                }
            }
            reportReqLog(req.options, {
                is_success: true,
                json_status: data.status_code,
                old_status: data.status
            });
        });
        req.send({
            data: params,
            timeout: opts.timeout
        });
        return req;
    }
    function wlog(msg, info) {
        window.CBG_JS_REPORT && CBG_JS_REPORT.send({
            msg: msg,
            info: info,
            target: location.href
        });
    }
    function reportReqLog(options, moreInfo) {
        try {
            var attrs = cbg_tracer.get_attrs(cbg_tracer.get_common_trace_info());
            var info = Object.merge({
                method: 'GET',
                url: options.url,
                params: JSON.encode(options.data),
                act: options.data.act
            }, moreInfo);
            for (var key in info) {
                attrs.push([key, info[key]]);
            }
            attrs.push(['request_id', cbg_tracer.uuid()]);
            cbg_tracer.send_log('app_request', attrs);
        } catch (e) {}
    }
    return {
        wlog: wlog,
        reportReqLog: reportReqLog,
        passAjaxGuard: passAjaxGuard,
        queryList: function(params, opts) {
            var url = window.Recommd.url;
            return request(url, params, opts);
        }
    };
}
)();
function get_equip_ico_url(equip) {
    var url = '';
    if (window.StorageStype && window.ResUrl && equip) {
        if (equip.storage_type != StorageStype["role"]) {
            var url = ResUrl + "/images/small/" + equip.equip_face_img;
        } else {
            var role_info = js_eval(lpc_2_js(equip.other_info.trim()));
            var icon = get_role_iconid(role_info["iIcon"]);
            var url = ResUrl + "/images/role_icon/small/" + icon + ".gif";
        }
    }
    return url;
}
function get_equip_detail_url(equip, equip_refer, view_loc) {
    equip = equip || {};
    var detail_url = HomePage + "/equip?s=" + equip.server_id + "&eid=" + equip.eid;
    if (window.ServerInfo && equip.server_id != parseInt(ServerInfo.server_id)) {
        detail_url += "&o";
    }
    if (equip_refer) {
        detail_url += '&equip_refer=' + equip_refer;
    }
    if (view_loc && window.addViewLocParams) {
        detail_url = addViewLocParams(detail_url, view_loc, equip.tag_key);
    }
    return detail_url;
}
var RECOMMDS_FN_ID = new Date / 1;
function build_recommands(options) {
    options = Object.merge({
        title: '猜你喜欢',
        needShow: false,
        params: null,
        selector: null
    }, options || {});
    if (options.callback) {
        var fn = '_recommds_fn_' + RECOMMDS_FN_ID++;
        window[fn] = options.callback;
        options.callback = fn;
    }
    var html = ['<div ', 'data_title="' + options.title + '" ', options.per ? 'data_per="' + options.per + '" ' : '', options.count ? 'data_count="' + options.count + '" ' : '', options.refer ? 'equip_refer="' + options.refer + '" ' : '', options.view_loc ? 'view_loc="' + options.view_loc + '" ' : '', options.new_request ? 'data_new_req="1" ' : '', options.cls ? 'class="recommandWrp ' + options.cls + '" ' : 'class="recommandWrp" ', options.callback ? 'data_callback="' + options.callback + '" ' : '', '>', '<textarea style="display: none" class="params hidden">', options.params ? JSON.encode(options.params) : '{"act": "recommd_by_collects", "count": 12}', '</textarea>', options.needShow ? '<div class="show"></div>' : '', '</div>'].join('');
    if (options.selector) {
        $$(options.selector).set('html', html);
    } else {
        document.write(html);
    }
    init_recommands();
}
var DOM_HAD_READY = false;
function init_recommands() {
    if (!DOM_HAD_READY) {
        return;
    }
    var $list = $$('.recommandWrp');
    if ($list.length < 1) {
        return;
    }
    $list.each(function($pt) {
        if ($pt.getAttribute('had_init')) {
            return;
        }
        requestAndInit($pt);
        $pt.setAttribute('had_init', 1);
    });
    function requestAndInit($pt) {
        if ($pt.getAttribute('loading')) {
            return;
        }
        var url = $pt.getAttribute('data_url') || window.Recommd && Recommd.url;
        if (!url) {
            return;
        }
        var count = +($pt.getAttribute('data_count') || 12);
        var page = +($pt.getAttribute('data_page') || 1);
        var params = ($pt.getElement('.params') || {
            value: $pt.getAttribute('data_params') || ''
        }).value.trim();
        try {
            params = JSON.decode(params);
        } catch (e) {
            params = {};
        }
        if (window.StorageStype && params["storage_type"] && params["storage_type"] == StorageStype["money"]) {
            return;
        } else {
            delete params["storage_type"];
        }
        if (!$pt.getAttribute('data_params')) {
            $pt.setAttribute('data_params', JSON.encode(params));
        }
        var viewLoc = $pt.getAttribute('view_loc');
        if (viewLoc) {
            params.view_loc = viewLoc;
        }
        var callback = window[$pt.getAttribute('data_callback')] || function() {}
        ;
        $pt.setAttribute('loading', 1);
        var req = new Request.JSONP({
            url: url,
            onSuccess: function(result) {
                $pt.erase('loading');
                $pt.setAttribute('data_page', page + 1);
                if (result.status !== 1 || (result.equips && result.equips.length <= 0)) {
                    $pt.setAttribute('data_page', 1);
                    callback(false, $pt, result);
                    if (page > 1) {
                        alert('没有更多的相似物品了');
                    }
                    return;
                }
                result.equips = decode_equip_list(result.equips);
                render($pt, result);
                callback(true, $pt, result);
                ApiRecommd.reportReqLog(req.options, {
                    is_success: true,
                    json_status: result.status_code,
                    old_status: result.status
                });
            },
            onError: function() {
                $pt.erase('loading');
                callback(false, $pt);
                ApiRecommd.reportReqLog(req.options, {
                    is_success: false
                });
            }
        }).send({
            data: Object.merge({
                serverid: window.LoginInfo && LoginInfo.serverid ? LoginInfo.serverid : window.ServerInfo && ServerInfo.server_id ? ServerInfo.server_id : window.EquipInfo && EquipInfo.server_id ? EquipInfo.server_id : -1,
                cross_server: 1,
                count: count,
                page: page
            }, params)
        });
    }
    function render($pt, result) {
        var $cnt = $pt.getElement('.show') || $pt;
        var template = new Template('recommands_list_template');
        $cnt.set('html', template.render({
            result: result,
            equips: result.equips,
            title: $pt.getAttribute('data_title'),
            per_page: +($pt.getAttribute('data_per') || 6),
            more_url: $pt.getAttribute('data_more'),
            more_url_text: $pt.getAttribute('data_more_text'),
            view_loc: $pt.getAttribute('view_loc'),
            equip_refer: $pt.getAttribute('equip_refer'),
            isSimilarRecommend: $pt.getAttribute('data-isSimilarRecommend') || false
        }));
        $pt.setStyle('display', 'block');
        bindEvent($pt);
        $pt.removeAttribute('trace_init');
        window.cbg_tracer && cbg_tracer.trace_recommd_in_equip_detail_page($pt);
    }
    function bindEvent($pt) {
        var isNewRequest = !!$pt.getAttribute('data_new_req');
        var $cnt = $pt.getElement('.show') || $pt;
        var $list = $cnt.getElements('.guessList');
        var $change = $cnt.getElement('.change');
        var length = $list.length;
        if (isNewRequest) {
            $change.addEvent('click', function(e) {
                e.stop();
                requestAndInit($pt);
            });
        } else if (length > 1) {
            var index = 1;
            $change.addEvent('click', function(e) {
                e.stop();
                index++;
                if (index > length) {
                    index = 1;
                }
                $list.setStyle('display', 'none');
                $list[index - 1].setStyle('display', 'block');
            });
        } else {
            $change.setStyle('display', 'none');
        }
        if (window.show_tips_box && window.hidden_tips_box) {
            $cnt.getElements('img').addEvent('mouseenter', show_tips_box).addEvent('mouseleave', hidden_tips_box);
        }
    }
}
window.addEvent('load', function() {
    DOM_HAD_READY = true;
    init_recommands();
});
