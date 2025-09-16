var MaxTradeYuan = 1000000;
var AjaxConstants = {
    Failed: 0,
    Ok: 1,
    Error: 2
};
var RACE_INFO = {
    0: "",
    1: "人",
    2: "魔",
    3: "仙"
};
var CHINESE_NUM_CONFIG = {
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
var ROLE_ZHUAN_ZHI_CONFIG = {
    0: "未飞升",
    1: "飞升",
    2: "渡劫"
};
function getPara(paraName) {
    var urlPara = location.search.slice(1);
    var result = new RegExp('(?:^|&)(' + encodeURIComponent(paraName) + ')=([^&]*)','g').exec(urlPara);
    if (result) {
        try {
            return decodeURIComponent(result[2]);
        } catch (e) {
            return "";
        }
    }
    return "";
}
function addUrlPara(name, value, url) {
    var currentUrl = url.split('#')[0];
    if (/\?/g.test(currentUrl)) {
        var reg = new RegExp("(&|\\?)" + name + "=[^\&]*");
        if (reg.test(currentUrl)) {
            currentUrl = currentUrl.replace(reg, '$1' + name + "=" + value);
        } else {
            currentUrl += "&" + name + "=" + value;
        }
    } else {
        currentUrl += "?" + name + "=" + value;
    }
    return currentUrl;
}
function getAbsolutePos(el) {
    var SL = 0
      , ST = 0;
    var is_div = /^div$/i.test(el.tagName);
    if (is_div && el.scrollLeft)
        SL = el.scrollLeft;
    if (is_div && el.scrollTop)
        ST = el.scrollTop;
    var r = {
        x: el.offsetLeft - SL,
        y: el.offsetTop - ST
    };
    if (el.offsetParent) {
        var tmp = getAbsolutePos(el.offsetParent);
        r.x += tmp.x;
        r.y += tmp.y;
    }
    return r;
}
;;(function() {
    var _0x3012 = ['\x73\x75\x62\x73\x74\x72\x69\x6e\x67', '\x61\x74\x6f\x62', '\x63\x68\x61\x72\x43\x6f\x64\x65\x41\x74', '\x70\x75\x73\x68', '\x74\x65\x73\x74'];
    (function(_0x3ed35c, _0x48b8fe) {
        var _0x1ad9d9 = function(_0x8eeda7) {
            while (--_0x8eeda7) {
                _0x3ed35c['push'](_0x3ed35c['shift']());
            }
        };
        _0x1ad9d9(++_0x48b8fe);
    }(_0x3012, 0x153));
    var _0x3a8e = function(_0xc40c11, _0x32bbb2) {
        _0xc40c11 = _0xc40c11 - 0x0;
        var _0x4e269a = _0x3012[_0xc40c11];
        return _0x4e269a;
    };
    !function(_0xcbc80b) {
        _0xcbc80b['\x64\x65\x63\x6f\x64\x65\x5f\x64\x65\x73\x63'] = function g(_0x1c0cdf) {
            if (_0x1c0cdf = _0x1c0cdf['\x72\x65\x70\x6c\x61\x63\x65'](/^\s+|\s+$/g, ''),
            !/^@[\s\S]*@$/[_0x3a8e('0x0')](_0x1c0cdf))
                return _0x1c0cdf;
            var _0x36ab38 = (/\b_k=([^;]*)/['\x65\x78\x65\x63'](document['\x63\x6f\x6f\x6b\x69\x65']) || [])[0x1] || '';
            if (_0x1c0cdf = _0x1c0cdf['\x72\x65\x70\x6c\x61\x63\x65'](/^@|@$/g, ''),
            /^[^@]+@[\s\S]+/['\x74\x65\x73\x74'](_0x1c0cdf)) {
                var _0x33c80e = _0x1c0cdf['\x69\x6e\x64\x65\x78\x4f\x66']('\x40');
                _0x36ab38 = _0x1c0cdf[_0x3a8e('0x1')](0x0, _0x33c80e),
                _0x1c0cdf = _0x1c0cdf['\x73\x75\x62\x73\x74\x72\x69\x6e\x67'](_0x33c80e + 0x1);
            }
            var _0x1b3f48 = function s(_0x1c0cdf) {
                try {
                    // 在Chrome插件环境中，eval被CSP阻止，使用Function构造函数替代
                    var func = new Function('return (' + _0x1c0cdf + ')');
                    return func();
                } catch (_0x40b9c3) {
                    // Function构造函数也失败，尝试JSON.parse
                    try {
                        return JSON.parse(_0x1c0cdf);
                    } catch (e2) {
                        // JSON.parse也失败，尝试手动解析
                        try {
                            // 手动解析简单的JavaScript对象格式
                            var cleaned = _0x1c0cdf.replace(/^\(|\)$/g, '').trim();
                            if (cleaned.startsWith('{') && cleaned.endsWith('}')) {
                                // 尝试修复常见的JavaScript对象格式问题
                                var fixed = cleaned
                                    .replace(/(\d+):/g, '"$1":')  // 修复数字键名
                                    .replace(/,\s*}/g, '}')        // 移除多余的逗号
                                    .replace(/,\s*]/g, ']')        // 移除多余的逗号
                                    .replace(/:\s*([^",\[\]{}]+)([,}\]])/g, function(match, value, ending) {
                                        // 处理未加引号的字符串值
                                        if (value.match(/^[a-zA-Z_][a-zA-Z0-9_]*$/) && 
                                            !value.match(/^\d+$/) && 
                                            value !== 'true' && 
                                            value !== 'false' && 
                                            value !== 'null') {
                                            return ':"' + value + '"' + ending;
                                        }
                                        return match;
                                    });
                                return JSON.parse(fixed);
                            }
                        } catch (e3) {
                            // 所有解析方法都失败，返回原始数据
                            return _0x1c0cdf;
                        }
                    }
                }
            }(_0x1c0cdf = _0xcbc80b[_0x3a8e('0x2')](_0x1c0cdf));
            _0x1b3f48 && '\x6f\x62\x6a\x65\x63\x74' == typeof _0x1b3f48 && _0x1b3f48['\x64'] && (_0x1b3f48 = _0x1b3f48['\x64']);
            
            // 在Chrome插件环境中，需要检查_0x1b3f48是否为有效字符串
            if (!_0x1b3f48 || typeof _0x1b3f48 !== 'string') {
                return _0x1c0cdf; // 返回原始数据
            }
            
            for (var _0x20b9fa = [], _0x10503c = 0x0, _0x1a524d = 0x0; _0x1a524d < _0x1b3f48['\x6c\x65\x6e\x67\x74\x68']; _0x1a524d++) {
                var _0x3641ed = _0x1b3f48['\x63\x68\x61\x72\x43\x6f\x64\x65\x41\x74'](_0x1a524d)
                  , _0x341952 = _0x36ab38[_0x3a8e('0x3')](_0x10503c % _0x36ab38['\x6c\x65\x6e\x67\x74\x68']);
                _0x10503c += 0x1,
                _0x3641ed = 0x1 * _0x3641ed ^ _0x341952,
                _0x20b9fa[_0x3a8e('0x4')](_0x3641ed['\x74\x6f\x53\x74\x72\x69\x6e\x67'](0x2));
            }
            return function d(_0x1c0cdf) {
                for (var _0x36ab38 = [], _0x33c80e = 0x0; _0x33c80e < _0x1c0cdf['\x6c\x65\x6e\x67\x74\x68']; _0x33c80e++)
                    _0x36ab38['\x70\x75\x73\x68'](_0xcbc80b['\x53\x74\x72\x69\x6e\x67']['\x66\x72\x6f\x6d\x43\x68\x61\x72\x43\x6f\x64\x65'](_0xcbc80b['\x70\x61\x72\x73\x65\x49\x6e\x74'](_0x1c0cdf[_0x33c80e], 0x2)));
                return _0x36ab38['\x6a\x6f\x69\x6e']('');
            }(_0x20b9fa);
        }
        ;
    }(window);
}
)();
function get_equip_desc(elemId) {
    return decode_desc($(elemId).value);
}
function decode_equip_list(list, keys) {
    function decode(obj, arr) {
        arr.forEach(function(key) {
            if (typeOf(obj[key]) == 'string') {
                obj[key] = window.decode_desc(obj[key]);
            }
        });
    }
    keys = keys || ['other_info'];
    return (list || []).map(function(data) {
        decode(data, keys);
        return data;
    });
}
function isEmptyObject(obj) {
    for (var name in obj)
        return false;
    return true;
}
function setSelect(selobj, value) {
    for (var i = 0; i < selobj.length; i++) {
        if (selobj.options[i].value == value || selobj.options[i].value + "省" == value || selobj.options[i].value + "区" == value || selobj.options[i].value + "市" == value)
            selobj.options[i].selected = true;
        else
            selobj.options[i].selected = false;
    }
}
function set_select_by_text(sel_obj, target_text, sublength) {
    target_text = target_text.substr(0, sublength);
    var hit = false;
    for (var i = 0; i < sel_obj.length; i++) {
        var option_text = sel_obj.options[i].text;
        option_text = option_text.substr(0, sublength)
        if (target_text == option_text) {
            sel_obj.options[i].selected = true;
            hit = true;
        } else {
            sel_obj.options[i].selected = false;
        }
    }
    return hit;
}
function htmlEncode(s) {
    var str = new String(s);
    str = str.replace(/&/g, "&amp;");
    str = str.replace(/</g, "&lt;");
    str = str.replace(/>/g, "&gt;");
    str = str.replace(/"/g, "&quot;");
    return str;
}
function load_user_menu(url) {
    window.location = url;
}
function clear_old_cookie_var() {
    Cookie.dispose("main_menu_id");
    Cookie.dispose("left_menu_id");
    Cookie.dispose("msg_box_flag");
    if (Cookie.read("wallet_tips") == 2) {
        Cookie.dispose("wallet_tips");
    }
}
function transform_newline(content) {
    return content.replace(/#r/g, "<br>");
}
function checkppc(ppc) {
    return /^\d{3,9}$/.test(ppc);
}
function checkotp(otp) {
    return /^\d{6}$/.test(otp);
}
function get_select_value(select_id) {
    var s = $(select_id);
    var index = s.selectedIndex;
    var val = s.options[index].value;
    return val;
}
function get_select_text(select_id) {
    var s = $(select_id);
    var index = s.selectedIndex;
    var val = s.options[index].text;
    return val;
}
function getDispatcher() {
    var dispatcher = new (new Class({
        Implements: Events
    }));
    dispatcher.delayFire = function(evt, args, delay) {
        setTimeout(function() {
            dispatcher.fireEvent(evt, args);
        }, delay || 0);
        return dispatcher;
    }
    return dispatcher;
}
var Template = new Class({
    initialize: function(template_id, isStrMode) {
        this.options = {
            "tag_re": /<%=?(.*?)%>/g
        };
        this.template = isStrMode ? template_id : this.get_template_source(template_id);
        this.function_body = null;
    },
    get_template_source: function(el_id) {
        var el = $(el_id)
        if (!el.innerHTML) {
            return "";
        }
        return el.innerHTML.trim().replace(/^<!--|-->$|\n|\r/g, "");
    },
    render_to_replace: function(panel_id, data_obj) {
        $(panel_id).innerHTML = this.render(data_obj);
    },
    render: function(data_obj) {
        var context = new Object();
        context = Object.merge(context, data_obj);
        context.__run = this.compile();
        return context.__run();
    },
    get_js_src: function() {
        if (!this.function_body) {
            this.compile();
        }
        return this.function_body;
    },
    compile: function() {
        var start = 0;
        var delimeter = '_%_';
        var body = this.template.replace(this.options.tag_re, function(matchedString, group, offset, fullString) {
            var replace = delimeter + ";\n";
            if (matchedString.charAt(2) == "=") {
                replace += "  __out += " + group + ";\n";
            } else {
                replace += "  " + group + "\n";
            }
            replace += "  __out += " + delimeter;
            return replace;
        })
        var functionBody = "__out += " + delimeter + body + delimeter + ";\n" + "return __out.join(" + delimeter + "" + delimeter + ");\n";
        functionBody = functionBody.replace(/'/g, "\\'");
        var regex = new RegExp(delimeter,'g');
        functionBody = functionBody.replace(regex, "'");
        var re_replace = function foo($1) {
            return "__out.push(" + $1.match(/^__out\s\+\=\s(.*);$/)[1] + ");";
        };
        this.function_body = "var __out = new Array();" + functionBody.replace(/__out\s\+\=\s(.*);/g, re_replace);
        return new Function(this.function_body);
    }
});
function render(template_id, data) {
    var obj = new Template(template_id);
    return obj.render(data);
}
if (window.CBG_JS_REPORT) {
    render = CBG_JS_REPORT.watch(render);
}
function render_to_replace(panel_id, template_id, data) {
    $(panel_id).innerHTML = render(template_id, data);
}
function calcEquipLinkInfo(equip, options) {
    var serverid = equip.serverid || equip.server_id;
    var overall_search = false;
    if (window.ServerInfo && window.equip && serverid != ServerInfo.server_id) {
        overall_search = true;
    }
    options = Object.merge({
        response: null,
        offset: null,
        view_loc: '',
        overall_search: overall_search,
        query: {}
    }, options || {});
    var response = options.response;
    if (!response || !('status'in response)) {
        throw new Error('缺少请求数据，请务必传入');
    }
    var link = HomePage + '/equip?s=' + serverid + '&eid=' + equip.eid + '&client_type=web';
    if (options.overall_search) {
        link += '&o';
    }
    if (options.view_loc) {
        link = addUrlPara('view_loc', options.view_loc, link);
    }
    var tag_key = equip.tag_key;
    if (tag_key && window.addViewLocParams) {
        if (typeof tag_key === 'object') {
            tag_key = JSON.encode(tag_key);
        }
        link = addViewLocParams(link, options.view_loc, equip.tag_key);
    }
    if (window.from_shareid) {
        link = addUrlPara('from_shareid', window.from_shareid, link);
    }
    var exposure = {
        offset: options.offset
    };
    exposure.recommd_tag = equip.tag_key || '';
    if (equip.reco_request_id) {
        exposure.reco_request_id = equip.reco_request_id;
        link = addUrlPara('reco_request_id', equip.reco_request_id, link);
    }
    Object.forEach(options.query, function(value, key) {
        if (value != null && value !== '') {
            link = addUrlPara(key, value, link);
        }
    });
    if (options.view_loc) {
        exposure.view_loc = options.view_loc;
    }
    return {
        link: link,
        exposure: exposure,
        exposure_str: JSON.encode(exposure)
    };
}
function initBuyBtnTrace(btn, equip) {
    equip = equip || window.equip;
    if (!equip || !btn) {
        return;
    }
    btn = $(btn);
    btn.set({
        tid: 'app_pay_1',
        data_trace_json: JSON.encode({
            kindid: equip.kindid,
            game_ordersn: equip.game_ordersn,
            eid: equip.eid,
            storage_type: equip.storage_type
        })
    });
}
function lpc_2_js(lpc_str) {
    var convert_dict = {
        "([": "{",
        "])": "}",
        ",])": "}",
        "({": "[",
        "})": "]",
        ",})": "]"
    };
    function convert($1) {
        var match_str = $1.replace(/\s+/g, '');
        return convert_dict[match_str];
    }
    var parser = new RegExp("\\(\\[|,?\s*\\]\\)|\\({|,?\\s*}\\)",'g');
    return lpc_str.replace(parser, convert);
}
function js_eval(js_str) {
    // 由于Chrome扩展CSP限制，完全避免动态代码执行
    try {
        // 首先尝试直接JSON.parse
        return JSON.parse(js_str);
    } catch (e) {
        // 如果失败，尝试清理字符串后再次解析
        try {
            var cleaned = js_str
                .replace(/^\(/, '')  // 移除开头的括号
                .replace(/\)$/, '')  // 移除结尾的括号
                .replace(/;\s*$/, '') // 移除结尾的分号
                .trim();
            return JSON.parse(cleaned);
        } catch (e2) {
            // 如果还是失败，尝试手动解析简单的对象格式
            try {
                return parseSimpleObject(js_str);
            } catch (e3) {
                // 如果parseSimpleObject也失败，尝试使用eval作为最后手段
                try {
                    if (typeof eval !== 'undefined') {
                        return eval('(' + js_str + ')');
                    }
                } catch (e4) {
                    // eval也失败了
                }
                
                console.error('js_eval failed to parse:', js_str, e3);
                return null;
            }
        }
    }
}

// 手动解析简单对象格式的辅助函数
function parseSimpleObject(str) {
    // 移除括号和分号
    var cleaned = str.replace(/^\(|\)$|;\s*$/g, '').trim();
    
    // 如果是空字符串或null/undefined
    if (!cleaned || cleaned === 'null' || cleaned === 'undefined') {
        return null;
    }
    
    // 尝试解析为JSON
    try {
        return JSON.parse(cleaned);
    } catch (e) {
        // 如果JSON.parse失败，尝试修复JavaScript对象格式
        try {
            // 将数字键名转换为字符串键名，使其符合JSON格式
            var fixed = cleaned.replace(/(\d+):/g, '"$1":');
            return JSON.parse(fixed);
        } catch (e2) {
            // 如果还是失败，尝试更复杂的修复
            try {
                // 处理嵌套对象中的数字键名
                var complexFixed = cleaned
                    .replace(/(\d+):/g, '"$1":')  // 修复数字键名
                    .replace(/,\s*}/g, '}')        // 移除多余的逗号
                    .replace(/,\s*]/g, ']');       // 移除多余的逗号
                return JSON.parse(complexFixed);
            } catch (e3) {
                // 如果还是失败，尝试更复杂的修复
                try {
                    // 处理更复杂的JavaScript对象格式
                    var advancedFixed = cleaned
                        .replace(/(\d+):/g, '"$1":')  // 修复数字键名
                        .replace(/,\s*}/g, '}')        // 移除多余的逗号
                        .replace(/,\s*]/g, ']')        // 移除多余的逗号
                        .replace(/:\s*([^",\[\]{}]+)([,}\]])/g, function(match, value, ending) {
                            // 处理未加引号的字符串值，但排除数字
                            if (value.match(/^[a-zA-Z_][a-zA-Z0-9_]*$/) && !value.match(/^\d+$/)) {
                                return ':"' + value + '"' + ending;
                            }
                            return match;
                        });
                    return JSON.parse(advancedFixed);
                } catch (e4) {
                    // 如果还是失败，尝试使用Function构造函数（Chrome插件环境兼容）
                    try {
                        var func = new Function('return (' + cleaned + ')');
                        return func();
                    } catch (e5) {
                        // Function构造函数也失败了，尝试手动解析
                        try {
                            // 最后尝试：手动解析复杂的JavaScript对象
                            if (cleaned.startsWith('{') && cleaned.endsWith('}')) {
                                return parseComplexObject(cleaned);
                            }
                        } catch (e6) {
                            // 手动解析也失败了
                        }
                    }
                    
                    console.error('parseSimpleObject: All parsing attempts failed, returning null:', cleaned );
                    return null;
                }
            }
        }
    }
}

// 手动解析复杂JavaScript对象的辅助函数
function parseComplexObject(str) {
    try {
        // 使用更智能的方法来解析复杂的JavaScript对象
        var result = {};
        var content = str.slice(1, -1); // 移除大括号
        var depth = 0;
        var inString = false;
        var escapeNext = false;
        var currentKey = '';
        var currentValue = '';
        var currentPair = '';
        var pairs = [];
        
        // 按字符遍历，正确处理嵌套对象和字符串
        for (var i = 0; i < content.length; i++) {
            var char = content[i];
            
            if (escapeNext) {
                currentPair += char;
                escapeNext = false;
                continue;
            }
            
            if (char === '\\') {
                escapeNext = true;
                currentPair += char;
                continue;
            }
            
            if (char === '"' || char === "'") {
                inString = !inString;
                currentPair += char;
                continue;
            }
            
            if (!inString) {
                if (char === '{' || char === '[') {
                    depth++;
                    currentPair += char;
                } else if (char === '}' || char === ']') {
                    depth--;
                    currentPair += char;
                } else if (char === ',' && depth === 0) {
                    pairs.push(currentPair.trim());
                    currentPair = '';
                } else {
                    currentPair += char;
                }
            } else {
                currentPair += char;
            }
        }
        
        if (currentPair.trim()) {
            pairs.push(currentPair.trim());
        }
        
        // 解析每个键值对
        for (var j = 0; j < pairs.length; j++) {
            var pair = pairs[j];
            if (!pair) continue;
            
            var colonIndex = pair.indexOf(':');
            if (colonIndex > 0) {
                var key = pair.substring(0, colonIndex).trim();
                var value = pair.substring(colonIndex + 1).trim();
                
                // 清理键名
                key = key.replace(/^["']|["']$/g, '');
                if (key.match(/^\d+$/)) {
                    key = '"' + key + '"';
                }
                
                // 解析值
                var parsedValue = parseValue(value);
                result[key] = parsedValue;
            }
        }
        
        return result;
    } catch (e) {
        console.warn('parseComplexObject failed:', e);
        return null;
    }
}

// 解析值的辅助函数
function parseValue(value) {
    value = value.trim();
    
    // 处理字符串
    if ((value.startsWith('"') && value.endsWith('"')) || 
        (value.startsWith("'") && value.endsWith("'"))) {
        return value.slice(1, -1);
    }
    
    // 处理数字
    if (value.match(/^-?\d+$/)) {
        return parseInt(value);
    }
    if (value.match(/^-?\d+\.\d+$/)) {
        return parseFloat(value);
    }
    
    // 处理布尔值
    if (value === 'true') return true;
    if (value === 'false') return false;
    if (value === 'null') return null;
    
    // 处理对象
    if (value.startsWith('{') && value.endsWith('}')) {
        return parseComplexObject(value);
    }
    
    // 处理数组
    if (value.startsWith('[') && value.endsWith(']')) {
        try {
            return JSON.parse(value);
        } catch (e) {
            // 手动解析数组
            var arrayContent = value.slice(1, -1);
            var items = [];
            var currentItem = '';
            var depth = 0;
            var inString = false;
            
            for (var i = 0; i < arrayContent.length; i++) {
                var char = arrayContent[i];
                
                if (char === '"' || char === "'") {
                    inString = !inString;
                }
                
                if (!inString) {
                    if (char === '{' || char === '[') {
                        depth++;
                    } else if (char === '}' || char === ']') {
                        depth--;
                    } else if (char === ',' && depth === 0) {
                        items.push(parseValue(currentItem.trim()));
                        currentItem = '';
                        continue;
                    }
                }
                
                currentItem += char;
            }
            
            if (currentItem.trim()) {
                items.push(parseValue(currentItem.trim()));
            }
            
            return items;
        }
    }
    
    // 默认返回原始值
    return value;
}

function safe_attr(attr) {
    if (attr == null || attr == undefined) {
        return "";
    } else {
        return attr;
    }
}
function set_position_center(obj) {
    obj_width = obj.offsetWidth;
    obj_height = obj.offsetHeight;
    with (obj.style) {
        left = document.getScroll().x + (document.documentElement.clientWidth - obj_width) / 2 + "px";
        top = document.getScroll().y + (document.documentElement.clientHeight - obj_height) / 2 + "px";
    }
}
function show_layer_center(cover_el, popup_el) {
    cover_el.setStyle("height", Document.getScrollHeight());
    cover_el.setStyle("display", "block");
    popup_el.setStyle("display", "block");
    popup_el.setStyles({
        "left": ((Window.getWidth() - popup_el.getWidth()) / 2) + "px",
        "top": (Window.getHeight() - popup_el.getHeight()) / 2 + Window.getScrollTop() + "px"
    });
}
function get_documentsize() {
    var size = Object();
    with (document.documentElement) {
        size.width = (scrollWidth > clientWidth) ? scrollWidth : clientWidth;
        size.height = (scrollHeight > clientHeight) ? scrollHeight : clientHeight;
    }
    return size;
}
function effect_back_js(func) {
    if (navigator.userAgent.indexOf("Firefox") > 0) {
        window.onunload = func;
        window.onbeforeunload = function() {
            window.onunload = '';
        }
    }
}
function dateDiff(interval, date1, date2) {
    var objInterval = {
        'D': 1000 * 60 * 60 * 24,
        'H': 1000 * 60 * 60,
        'M': 1000 * 60,
        'S': 1000,
        'T': 1
    };
    interval = interval.toUpperCase();
    var dt1 = Date.parse(date1.replace(/-/g, '/'));
    var dt2 = Date.parse(date2.replace(/-/g, '/'));
    return Math.round((dt2 - dt1) / objInterval[interval]);
}
function get_radio_value(radio_name) {
    var radio_box = document.getElementsByName(radio_name);
    if (radio_box != null) {
        for (var i = 0; i < radio_box.length; i++) {
            if (radio_box[i].checked) {
                return radio_box[i].value;
            }
        }
    } else {
        return null;
    }
}
function get_color_price(price, if_add_unit, text) {
    price = +price;
    if (!price) {
        return '---';
    }
    var cls = "p100";
    var unit = if_add_unit ? "（元）" : "";
    var text = text ? text : "";
    if (price < 100) {
        cls = "p100"
    } else if (price >= 100 && price < 1000) {
        cls = "p1000";
    } else if (price >= 1000 && price < 10000) {
        cls = "p10000";
    } else if (price >= 10000 && price < 100000) {
        cls = "p100000";
    } else if (price >= 100000) {
        cls = "p1000000";
    }
    return "<span class='" + cls + "'>" + text + "￥" + price.toFixed(2) + unit + "</span>"
}
var StorageStype = {
    "equip": 1,
    "pet": 2,
    "money": 3,
    "role": 4
};
function get_login_url(other_arg) {
    var server_name = ServerInfo["server_name"];
    var servername_in_ck = decodeURIComponent(Cookie.read("cur_servername") || "");
    if (servername_in_ck) {
        server_name = servername_in_ck;
    }
    var arg = Object.merge({
        "act": "show_login",
        "area_name": ServerInfo["area_name"],
        "area_id": ServerInfo["area_id"],
        "server_id": ServerInfo["server_id"],
        "server_name": server_name
    }, other_arg || {});
    return HttpsCgiRootUrl + "/show_login.py?" + Object.toQueryString(arg);
}
function logout(url) {
    clear_old_cookie_var();
    window.location = url;
}
function check_offsale_equips() {
    if (!is_user_login())
        return;
    var alert_flag = Cookie.read("remind_offsale");
    if (alert_flag)
        return;
    Cookie.write("remind_offsale", 1, {
        'duration': 1
    });
    alert_flag = Cookie.read("alert_msg_flag");
    if (alert_flag)
        return;
    var offsale_equips_num = Cookie.read('offsale_num');
    if (!offsale_equips_num)
        return;
    offsale_equips_num = offsale_equips_num.toInt();
    if (offsale_equips_num <= 0)
        return;
    Cookie.write("remind_offsale", 1, {
        'duration': 4
    });
    Cookie.write("alert_msg_flag", 1);
    if (window.confirm("藏宝阁提醒您：您有" + offsale_equips_num + "件商品长时间未上架，准备将其重新上架？")) {
        window.location.href = CgiRootUrl + '/userinfo.py?act=my_equips';
        return;
    }
}
function check_user_msg() {
    if (!is_user_login()) {
        return;
    }
    var new_msg_num = Cookie.read("new_msg_num");
    if (!new_msg_num) {
        return;
    }
    new_msg_num = new_msg_num.toInt();
    if (new_msg_num <= 0) {
        return;
    }
    var alert_flag = Cookie.read("alert_msg_flag");
    if (alert_flag) {
        return;
    }
    Cookie.write("alert_msg_flag", 1);
    if (window.confirm("藏宝阁提醒您：您有新的消息，请注意查收。")) {
        window.location.href = CgiRootUrl + '/message.py?act=msg_list';
        return;
    }
}
function alert_login() {
    if (confirm("登录后才能进行该项操作!\n您要登录吗？")) {
        window.location.href = get_login_url();
    }
    return false;
}
function fix_anonymous_menu_link() {
    if (is_user_login()) {
        return;
    }
    $$("#top_sell_menu_a, #top_mycbg_menu_a, #menu_my_order, #sub_menu_appointed_to_me").addEvent("click", alert_login);
    $$("#to_login_link").set('href', get_login_url({}));
    if ($('top_fairshow_menu_a'))
        $("top_fairshow_menu_a").href += '&server_id=' + ServerInfo["server_id"];
    if ($('sub_offsale_query_a'))
        $("sub_offsale_query_a").href += '&server_id=' + ServerInfo["server_id"];
}
var EQUIP_TAKE_BACK = 0;
var EQUIP_STORE = 1;
var EQUIP_SELLING = 2;
var EQUIP_BOOKING = 3;
var EQUIP_PAID = 4;
var EQUIP_TRADE_FINISH = 5;
var EQUIP_TAKE_AWAY = 6;
var EQUIP_PROBLEM_TRADE = 7;
var EQUIP_AUCTION = 8;
var EQUIP_SUB_VERIFING = 101;
var EQUIP_SUB_VERIFY_FAILED = 102;
var EQUIP_SUB_PROBLEM = 701;
var EquipStatus = {};
EquipStatus[EQUIP_TAKE_BACK] = "卖家取回";
EquipStatus[EQUIP_STORE] = "未上架";
EquipStatus[EQUIP_SELLING] = "上架中";
EquipStatus[EQUIP_BOOKING] = "被下单";
EquipStatus[EQUIP_PAID] = "已出售";
EquipStatus[EQUIP_TRADE_FINISH] = "已出售";
EquipStatus[EQUIP_TAKE_AWAY] = "买家取走";
EquipStatus[EQUIP_PROBLEM_TRADE] = "问题物品";
EquipStatus[EQUIP_AUCTION] = "拍卖中";
EquipStatus[EQUIP_SUB_VERIFING] = "上架审核中";
EquipStatus[EQUIP_SUB_VERIFY_FAILED] = "上架审核未通过";
var ORDER_NO_PAY = 1;
var ORDER_PAIED = 2;
var ORDER_CANCEL = 3;
var ORDER_EXPIRED = 4;
var ORDER_REFUNDMENT = 5;
var ORDER_SUCCESS = 6;
var ORDER_REFUNDMENT_FINISH = 7;
var OrderStatus = {};
OrderStatus[ORDER_NO_PAY] = "待付款";
OrderStatus[ORDER_PAIED] = "已付款";
OrderStatus[ORDER_CANCEL] = "已废除";
OrderStatus[ORDER_EXPIRED] = "过期";
OrderStatus[ORDER_REFUNDMENT] = "退款中";
OrderStatus[ORDER_SUCCESS] = "已出售";
OrderStatus[ORDER_REFUNDMENT_FINISH] = "已退款";
var ORDER_INSTALMENT_PENDING = 0;
var ORDER_INSTALMENT_STARTED = 1;
var ORDER_INSTALMENT_FINISHED = 2;
var ORDER_INSTALMENT_FORFEITED_PENDING = 3;
var ORDER_INSTALMENT_FORFEITED_FINISH = 4;
var ORDER_INSTALMENT_ABORT_REFUND = 5;
var ORDER_INSTALMENT_ABORT_REFUND_FINISH = 6;
var ORDER_INSTALMENT_CANCELED = 7;
var ORDER_INSTALMENT_SUCCESS = 8;
var InstalmentStatus = {};
InstalmentStatus[ORDER_INSTALMENT_PENDING] = "待付款";
InstalmentStatus[ORDER_INSTALMENT_STARTED] = "待付尾款";
InstalmentStatus[ORDER_INSTALMENT_FINISHED] = "已付款";
InstalmentStatus[ORDER_INSTALMENT_FORFEITED_PENDING] = "订金扣除";
InstalmentStatus[ORDER_INSTALMENT_FORFEITED_FINISH] = "订金扣除";
InstalmentStatus[ORDER_INSTALMENT_ABORT_REFUND] = "退款中";
InstalmentStatus[ORDER_INSTALMENT_ABORT_REFUND_FINISH] = "退款完成";
InstalmentStatus[ORDER_INSTALMENT_CANCELED] = "已取消分期付";
InstalmentStatus[ORDER_INSTALMENT_SUCCESS] = "已付款";
function can_takeaway_in_24h_fair_show(storage_type, server_time, fair_show_end_time) {
    if (storage_type == StorageStype.equip && server_time && fair_show_end_time) {
        server_time = parseDatetime(server_time);
        fair_show_end_time = parseDatetime(fair_show_end_time);
        if (server_time - fair_show_end_time >= -24 * 60 * 60 * 1000) {
            return true;
        }
    }
    return false;
}
function get_window_height() {
    return Window.getHeight() + Document.getScrollTop();
}
function adjust_tips_position(el, tips_box, fixes) {
    if (tips_box) {
        var TipsBox = tips_box;
    } else {
        var TipsBox = $("TipsBox");
    }
    TipsBox.setStyle("display", "block");
    var styles = {
        "left": el.getOffsets()["x"] + el.getWidth() + 8
    };
    var position = el.getCoordinates();
    var left_pos_check = Window.getWidth() + Document.getScrollLeft();
    if ((styles["left"] + TipsBox.getWidth()) > left_pos_check) {
        styles["left"] = position["left"] - TipsBox.getWidth() - 8;
    }
    if (position["top"] + TipsBox.getHeight() > get_window_height()) {
        var check_pos = position["top"] - TipsBox.getHeight() + el.getHeight();
        if (check_pos > Document.getScrollTop()) {
            styles["top"] = check_pos;
        } else {
            styles["top"] = Document.getScrollTop() + 10;
        }
    } else {
        styles["top"] = position["top"];
    }
    if (fixes) {
        if (fixes['top'])
            styles['top'] += fixes['top'];
        if (fixes['left'])
            styles['left'] += fixes['left'];
    }
    TipsBox.setStyles(styles);
}
function get_window_width() {
    return Window.getWidth() + Document.getScrollLeft();
}
function adjust_tips_position_width(el, tips_box) {
    if (tips_box) {
        var TipsBox = tips_box;
    } else {
        var TipsBox = $("TipsBox");
    }
    TipsBox.setStyle("display", "block");
    var styles = {};
    var position = el.getCoordinates();
    if (position["left"] + TipsBox.getWidth() > get_window_width()) {
        var check_pos = position["left"] - TipsBox.getWidth() + el.getWidth();
        if (check_pos > Document.getScrollLeft()) {
            styles["left"] = check_pos;
        } else {
            styles["left"] = Document.getScrollLeft() + 10;
        }
    } else {
        styles["left"] = position["left"];
    }
    styles["top"] = position["top"] + el.getHeight() + 8;
    TipsBox.setStyles(styles);
}
function trim(str) {
    return str.replace(/(^\s*)|(\s*$)/g, "");
}
var OtpRexp = /^\d{6}$/;
var PpcRexp = /^\d{3,9}$/;
var MobileRexp = /^1\d{10}$/;
var MobileValidCodeRexp = /^\d{6}$/;
function checkMobileMb(mb_type) {
    if (mb_type == 'otp') {
        if (!$('otp_input').value) {
            alert('请输入将军令');
            return false;
        }
        if (!OtpRexp.test($('otp_input').value)) {
            alert('将军令格式错误');
            return false;
        }
    } else if (mb_type == 'ppc') {
        if (!$('ppc_input').value) {
            alert('请输入密保卡密码');
            return false;
        }
        if (!PpcRexp.test($('ppc_input').value)) {
            alert('密保卡密码格式错误');
            return false;
        }
    }
    return true;
}
function is_user_login() {
    if (window.IsLogin === 1) {
        return true;
    }
    var is_login = parseInt(Cookie.read("is_user_login"));
    var login_user_roleid = Cookie.read("login_user_roleid");
    if (is_login == 1 && login_user_roleid) {
        return true;
    } else {
        return false;
    }
}
function gen_login_info() {
    var ctx = {};
    if (is_user_login()) {
        ctx["is_user_login"] = true;
        ctx["login_user_nickname"] = decodeURIComponent(Cookie.read("login_user_nickname"));
        ctx["login_user_icon"] = Cookie.read("login_user_icon");
        ctx["new_msg_num"] = parseInt(Cookie.read("new_msg_num"));
        ctx["login_user_roleid"] = Cookie.read("login_user_roleid");
    } else {
        ctx["is_user_login"] = false;
    }
    var servername_in_ck = decodeURIComponent(Cookie.read("cur_servername"));
    var cur_servername = null;
    var name_list = cur_server_info["servername"];
    for (var i = 0; i < name_list.length; i++) {
        if (servername_in_ck == name_list[i]) {
            cur_servername = name_list[i];
        }
    }
    if (!cur_servername) {
        cur_servername = name_list[0];
    }
    ctx["cur_servername"] = cur_servername;
    ctx["cur_areaname"] = cur_area_info["areaname"];
    return render("login_info_templ", ctx);
}
function gen_msg_num_html(msg_num) {
    var msg = "站内信";
    if (msg_num > 0) {
        msg += "(<span class='cYellow'>" + msg_num + "</span>)";
    }
    return msg;
}
function fix_buy_menu_url() {
    if (!$("top_buy_menu_a")) {
        return false;
    }
    var recommend_url = Cookie.read('recommend_url');
    var go_recommend_page = function() {
        window.location = recommend_url + '&client_type=web';
        return false;
    };
    if (recommend_url) {
        if ($("top_buy_menu_a")) {
            $("top_buy_menu_a").addEvent("click", go_recommend_page);
        }
        if ($("common_query_a")) {
            $("common_query_a").addEvent("click", go_recommend_page);
        }
        return false
    }
    if (!StaticFileConfig["is_using"]) {
        return false;
    }
    var goto_query_page = function() {
        window.location = StaticFileConfig["res_root"] + "/" + ServerInfo["server_id"] + "/buy_equip_list/equip_list1.html";
        return false;
    };
    $("top_buy_menu_a").addEvent("click", goto_query_page);
    if ($("common_query_a"))
        $("common_query_a").addEvent("click", goto_query_page);
}
function save_equip_price_info(equipid, price) {
    var identify = "identify_" + equipid;
    var ck_value = price;
    var ck_time = 10 * (1 / (24 * 60 * 60));
    Cookie.write(identify, ck_value, {
        "duration": ck_time
    });
}
function show_shop_cart_info() {
    var $buy_cart_panel = $("buy_cart_panel");
    if ((window.IsLogin || is_user_login()) && $buy_cart_panel) {
        if (typeof $buy_cart_panel.setStyle === 'function') {
            $buy_cart_panel.setStyle("display", "");
        }
        var order_num = Cookie.read("unpaid_order_num");
        if (!order_num) {
            return;
        }
        order_num = order_num.toInt();
        if (order_num > 0) {
            $("cart_order_num").set("html", "(" + order_num + ")");
        }
    }
}
function show_wallet_guide() {
    if (!is_user_login()) {
        return;
    }
    var WELLET_LOCKED_TIPS = 2;
    var tipsContent;
    var is_wallet_pay_freeze = WalletData.is_pay_freeze == '1' && window.is_user_wallet;
    var freezekey = 'wallet_freeze_dialog_key';
    if (is_wallet_pay_freeze) {
        var lockedTipsHistory = StoreDB.getItem(freezekey);
        $("btn_get_money").setStyle("color", "gray");
        $$(".walletFreeze").each(function(el) {
            el.setStyle("display", "inline-block");
            el.addEvent("click", function() {
                show_wallet_freeze_dialog();
            });
        });
        if (!lockedTipsHistory) {
            show_wallet_freeze_dialog();
            StoreDB.setItem(freezekey, 1);
            return;
        }
    } else {
        StoreDB.removeItem(freezekey)
    }
    if (WalletData.is_locked && Cookie.read("wallet_tips") != WELLET_LOCKED_TIPS) {
        tipsContent = '您的钱包已被锁定，请<span class="cPink" style="margin-left:2px;">联系客服，电话：95163999（24小时）</span>';
        Cookie.write("wallet_tips", WELLET_LOCKED_TIPS, {
            duration: 0
        });
    }
    var target = $$('.userInfo .title')[0];
    if (tipsContent && target) {
        var el_guide = new Element("div#balanceChangeTips.balanceChangeTips.tipsBlack.popArrowUp");
        var html = ['<div class="tipsContent">', tipsContent, '</div>', '<div class="tipsAction">', '<button>我知道了</button>', '</div>'].join('');
        el_guide.inject(document.body);
        var coordinates = target.getCoordinates();
        el_guide.set("html", html);
        el_guide.setStyles({
            "top": coordinates.bottom + 8 + "px",
            "left": coordinates.left - 35 + "px"
        });
        el_guide.getElement("button").addEvent("click", function() {
            el_guide.setStyle("display", "none");
            WebGuide.next();
        });
    }
}
function show_wallet_freeze_dialog() {
    if (WalletData.freeze_link) {
        CBG.confirm(WalletData.freeze_remind, {
            confirmText: '人工申诉',
            cancelText: '放弃'
        }).addEvent('confirm', function() {
            if (WalletData.freeze_link) {
                window.location.href = WalletData.freeze_link;
            }
        }).addEvent('cancel', function() {})
    } else {
        CBG.alert(WalletData.freeze_remind);
    }
}
function init_get_money() {
    var dialog;
    var timer = null;
    function getHtml() {
        var html = ['<div style="position:relative;width:453px;margin:20px;border:1px solid #bdbfdb;background:#ededf4;">', '<div style="float:left;width:185px;padding:12px 20px;border-right:1px solid #bdbfdb;line-height:1.8;">', '<h2 class="f14px fB" style="margin:2px 0 8px;">', '当前可提现：<span class="cDRed">', fen2yuan(Math.max(WalletData.free_balance, 0)), '元</span>', '</h2>', '<p class="cDGray">', '<strong>可提现余额少于钱包余额？</strong><br/>', '卖出商品所得金额需经过72小时考察后方可提现，因此可提现余额有可能暂时少于钱包余额。<br/>', '<a href="https://cbg-xyq.res.netease.com/help/help33.html" target="_blank">提现有疑问？</a>', '</p>', '</div>', '<div style="float:left;width:185px;margin-left:-1px;padding:20px;border-left:1px solid #bdbfdb;text-align:center;font-size:14px;">', '<h2 class="f14px fB">提现金额：</h2>', '<p style="margin:20px 0;white-space:nowrap;">', '<input type="text" placeholder="免手续费" id="get_money_count" style="width:148px" /> 元', '</p>', '<p><a href="#" class="btn1 disabled" id="submit_get_money">提交</a></p>', '</div>', '<div style="position:absolute;left:0;bottom:-20px;width:100%;text-align:center;">', '<span id="get_money_tips" style="display:none;font-size:14px;color:#fff;line-height:34px;padding:0 18px;border-radius:17px;background:#000;">请输入需要存入的金额</span>', '</div>', '<div style="clear:both"></div>', '</div>'];
        return html.join('');
    }
    function initEvents() {
        $("get_money_count").addEvent("keyup", function() {
            var amount = this.value;
            if (amount.charAt(0) == '.') {
                this.value = '0' + amount;
            }
            if (amount == 0) {
                $("submit_get_money").addClass("disabled");
            } else {
                $("submit_get_money").removeClass("disabled");
            }
        });
        $("submit_get_money").addEvent("click", function() {
            var value = $('get_money_count').value;
            if (!value || value.trim() == '' || isNaN(value) || parseFloat(value) <= 0) {
                showTips("请检查输入提现金额");
            } else if (!/^\d*(\.\d{1,2})?$/.test(value.trim())) {
                showTips('抱歉，提现的最小单位是分');
            } else {
                var amount = yuan2fen(value);
                if (amount > WalletData.free_balance) {
                    showTips("最多可提现" + fen2yuan(Math.max(WalletData.free_balance, 0)) + "元，您已超出，请修改金额");
                } else {
                    showConfrim(amount);
                }
            }
        });
    }
    function showTips(content) {
        var el_tips = $("get_money_tips");
        el_tips.set("html", content);
        el_tips.setStyle("display", "inline-block");
        timer && clearTimeout(timer);
        timer = setTimeout(function() {
            el_tips.setStyle("display", "none");
        }, 3000);
    }
    function showConfrim(amount) {
        var tmpl = ['<div style="padding:14px 24px;font-size:14px;line-height:1.7;">', '<p style="padding:6px 12px 6px 0">', '您提现至网易支付的金额为：', '<span class="cDRed fB" style="margin-right:2px;">', fen2yuan(amount), '</span>', '元，是否确认提现？', '</p>', '<div class="divider" style="margin:14px 0;"></div>', '<div class="textCenter">', '<a id="btn_confrim_get_money" class="btn1" href="javascript:;">确认提现</a>', '</div>', '</div>'].join('');
        var confirmDialog = new PopupDialog("提示",tmpl);
        confirmDialog.show();
        $('btn_confrim_get_money').addEvent('click', function() {
            confirmDialog.hide();
            submit(amount);
        });
    }
    function showAuthenticationTips() {
        var tmpl = ['<div style="padding:14px 24px;font-size:14px;line-height:1.7;">', '<p style="text-indent:2em;">抱歉，您还没有在网易支付进行实名认证，余额无法提现，<br>请认证后再操作。</p>', '<div class="divider" style="margin:14px 0;"></div>', '<div class="textCenter"><a class="btn1" href="https://epay.163.com/i.htm?popup=1" target="_blank">前往认证</a></div>', '</div>'].join('');
        new PopupDialog("提示",tmpl).show();
    }
    function showSuccessTips() {
        var tmpl = ['<div style="padding:14px 24px;text-align:center;font-size:14px;line-height:1.7;">', '<img src="/images/qr_pay_suc.png">', '<p style="margin:16px 4px;">提现成功，您可以继续去网易支付提现到银行卡。</p>', '<div class="divider" style="margin:14px 0;"></div>', '<div class="textCenter">', '<a class="btn1" href="https://epay.163.com/servlet/controller?operation=drawCashView" target="_blank">提现至银行卡</a>', '</div>', '</div>'].join('');
        new PopupDialog({
            title: '提示',
            content: tmpl,
            onClose: function() {
                location.reload();
                return true;
            }
        }).show();
    }
    function submit(amount) {
        var url = CgiRootUrl + "/usertrade.py?act=ajax_cbg_wallet_withdraw";
        var params = {
            "amount_fen": amount
        };
        var req = new Request.JSON({
            "url": url,
            onSuccess: function(result) {
                if (result.status != 1) {
                    if (result.need_guide_epay_identity) {
                        showAuthenticationTips();
                    } else {
                        showTips(result.msg);
                    }
                } else {
                    showSuccessTips();
                }
            },
            onFailure: function() {
                showTips('访问出错');
            },
            "noCache": true,
            "async": false
        });
        req.get(params);
    }
    var btn_get_money = $("btn_get_money");
    btn_get_money && btn_get_money.addEvent("click", function() {
        var is_wallet_pay_freeze = WalletData.is_pay_freeze == '1';
        if (is_wallet_pay_freeze) {
            show_wallet_freeze_dialog();
            return;
        }
        dialog = new PopupDialog("提现至网易支付",getHtml());
        dialog.show();
        if (WalletData.free_balance <= 0) {
            $('get_money_count').set("disabled", "disabled");
        } else {
            initEvents();
        }
    });
}
function init_wallet_tips() {
    var tips = ['<div class="tipsContent">', '<div class="walletTipsItem">', '<span class="fl">可提现余额:</span>', '<span class="fr">', fen2yuan(Math.max(WalletData.free_balance, 0)), '元</span>', '</div>', '<div class="walletTipsItem">', '<span class="fl">考察期余额:</span>', '<span class="fr">', fen2yuan(WalletData.checking_balance), '元</span>', '</div>', '</div>', '<div class="tipsDesc">提示：考察期余额72小时后方可购买梦幻币和消耗品，公示期出售商品从公示期结束后开始计算72小时考察期。<br> 钱包余额/优惠券暂不支持与支付宝合并付款</div>'].join('');
    var el_targets = $$('.walletTips');
    if (el_targets.length > 0) {
        el_targets.set('data-popover-cont', tips);
    }
}
function init_wallet() {
    if (window.WalletData) {
        if ($('wallet_balance')) {
            $('wallet_balance').set('html', fen2yuan(WalletData.balance) + '元')
        }
        init_wallet_tips();
        init_get_money();
        show_wallet_guide();
    }
}
function initFrame(iframe_name, src) {
    var iframe_src = src;
    new Request.JSON({
        url: "/cgi/api/gen_login_token",
        onSuccess: function(res) {
            iframe_src = addUrlPara("hide_back", 1, iframe_src);
            iframe_src = addUrlPara("h5_pay", 1, iframe_src);
            if (res && res.status_code === "OK" && res.token) {
                iframe_src = addUrlPara("h5_login_token", res.token, iframe_src);
            }
            $(iframe_name).src = iframe_src;
        }
    }).get({
        safe_code: window.SafeCode,
        client_type: "web"
    });
}
function judgeIsLogin() {
    if (window.is_user_login) {
        if (is_user_login()) {
            return true;
        } else if (window.login_url || window.ServerInfo) {
            var returnUrl = location.href;
            location.href = window.ServerInfo ? get_login_url({
                return_url: returnUrl
            }) : login_url + "&return_url=" + encodeURIComponent(returnUrl);
        } else {
            alert('请登录后再进行操作');
            return false;
        }
    } else {
        alert('请登录后再进行操作');
    }
    return false;
}
;function closeOtherSideBar(newItemId) {
    var currentActiveItem = $$('.right_float_menu > li.on')[0];
    if (currentActiveItem && currentActiveItem.id !== newItemId) {
        currentActiveItem.firstElementChild && currentActiveItem.firstElementChild.click();
    }
}
function init_right_float_menu() {
    if (!$('right_float_pannel'))
        return;
    var trade_history_url = location.hostname.contains('test') ? 'https://main-h5-xyq.test.cbg.163.com/cgi/mweb/history/query' : 'https://xyq-m.cbg.163.com/cgi/mweb/history/query';
    var evaluate_price_url = location.hostname.contains('test') ? 'https://main-h5-xyq.test.cbg.163.com/cgi/mweb/kol/main' : 'https://xyq-m.cbg.163.com/cgi/mweb/kol/main';
    var latest_view_open = false;
    var trade_history = false;
    var evaluate_price = false;
    var isShowingEcardCenter = false;
    function hasTargetText(str) {
        if (/query.py/.test(str) || /equip/.test(str) || /userinfo/.test(str)) {
            return true;
        } else {
            return false;
        }
    }
    $('sprite_link').addEvent('click', function(e) {
        closeOtherSideBar('sprite_link')
    })
    var isShowEvaluateAndtrade = hasTargetText(location.pathname);
    if ($("buy_card_a")) {
        $("buy_card_a").style.display = isShowEvaluateAndtrade ? '' : 'none';
    }
    $("ecard_center").style.display = isShowEvaluateAndtrade ? '' : 'none';
    $("evaluate_price").style.display = isShowEvaluateAndtrade ? '' : 'none';
    $("trade_history").style.display = isShowEvaluateAndtrade ? '' : 'none';
    $("latest_view_btn").addEvent("click", function(e) {
        closeOtherSideBar(e)
        if (!latest_view_open) {
            gen_latest_view(window.page_type && window.page_type == 'overall_search');
            $("recent_list_panel").style.display = ''
            latest_view_open = true;
            this.addClass('on');
        } else {
            latest_view_open = false;
            $("recent_list_panel").style.display = 'none';
            this.removeClass('on');
        }
    });
    $("trade_history").addEvent("click", function(e) {
        closeOtherSideBar('trade_history');
        if (!judgeIsLogin()) {
            return;
        }
        if (window.Browser && Browser.ie) {
            alert('该服务暂不支持该浏览器操作，请更换其他浏览器操作');
            return;
        }
        if (!trade_history) {
            $("trade_history_page_panel").style.display = '';
            trade_history = true;
            this.addClass('on');
            if (!$('tradeHistoryPage_iframe').src) {
                initFrame('tradeHistoryPage_iframe', trade_history_url);
            }
        } else {
            trade_history = false;
            $("trade_history_page_panel").style.display = 'none';
            this.removeClass('on');
        }
    });
    $$("#ecard_center, #buy_card_a").addEvent("click", function(e) {
        closeOtherSideBar('ecard_center');
        if (!judgeIsLogin()) {
            return;
        }
        if (window.Browser && Browser.ie) {
            alert('该服务暂不支持该浏览器操作，请更换其他浏览器操作');
            return;
        }
        if (!isShowingEcardCenter) {
            $("ecard_center_panel").style.display = '';
            isShowingEcardCenter = true;
            $("ecard_center").addClass('on');
            if (!$("ecard_center_iframe").src) {
                var ecard_center_url_origin = location.hostname.contains('test') ? 'https://cbg-main.test.ecard.163.com' : 'https://trade.ecard.163.com';
                var ecard_center_url_path = '/h5/center?p=xyq&hide_back=1&h5_pay=1&from=cbg';
                var ecard_auth_url = ecard_center_url_origin + '/api/ecard/front/v1/auth_login?back_url=' + encodeURIComponent(ecard_center_url_path);
                $("ecard_center_iframe").src = '/cgi-bin/login.py?auth_type=tenant_login&act=product_apply_auth_login&back_url=' + encodeURIComponent(ecard_auth_url);
            }
        } else {
            $("ecard_center_panel").style.display = 'none';
            isShowingEcardCenter = false;
            $("ecard_center").removeClass('on');
        }
    });
    $("evaluate_price").addEvent("click", function(e) {
        closeOtherSideBar('evaluate_price');
        if (!judgeIsLogin()) {
            return;
        }
        if (window.Browser && Browser.ie) {
            alert('该服务暂不支持该浏览器操作，请更换其他浏览器操作');
            return;
        }
        if (!evaluate_price) {
            $("evaluate_page_panel").style.display = '';
            evaluate_price = true;
            this.addClass('on');
            if (!$('evaluatePage_iframe').src) {
                initFrame('evaluatePage_iframe', evaluate_price_url)
            }
        } else {
            $("evaluate_page_panel").style.display = 'none';
            evaluate_price = false;
            this.removeClass('on');
        }
    });
    $('right_float_download_app').addEvent('click', function(e) {
        closeOtherSideBar('right_float_download_app');
    })
    var tt;
    if (Browser.ie6) {
        window.addEvent("scroll", function() {
            if (tt) {
                clearTimeout(tt);
            }
            tt = setTimeout(function() {
                $('right_float_pannel').setStyle("top", (window.getScroll().y + 24) + "px");
            }, 100);
        });
    }
    var el_customer_service_link = $('goto_online_customer_service');
    var customer_service_url = el_customer_service_link.getAttribute('data-href');
    if (el_customer_service_link && customer_service_url && customer_service_url.indexOf('<' + '!--') == -1) {
        if (!is_user_login()) {
            el_customer_service_link.addEvent('click', function() {
                alert_login();
            });
        } else {
            el_customer_service_link.href = customer_service_url;
            el_customer_service_link.target = "_blank";
        }
        el_customer_service_link.getParent().setStyle('display', '');
    }
}
function init_ad() {
    if (window.NoAdInfo == true || !window.xyq_ad_list) {
        return;
    }
    var area_list = $$('.area');
    if (area_list.length != 3) {
        return;
    }
    ;function show_ad_bottom(data) {
        var ul_html = "<ul>";
        var nav_html = "<div>";
        for (var i = 0; i < data.length; i++) {
            var item = data[i];
            ul_html += "<li><a href='" + item.link_url + "' target='_blank' title='" + "" + "' tid=\"web_bottom_1\"" + "data_trace_text='" + item.id + "'><img width='920' height='50' src='" + item.image_url + "' alt='" + "" + "' /></a></li>";
            nav_html += "<a href='" + item.link_url + "'>" + (i + 1) + "</a>";
        }
        nav_html += "</div>";
        ul_html += "</ul>";
        if (data.length > 1) {
            var ad_html = ul_html + nav_html;
        } else {
            var ad_html = ul_html;
        }
        var blank_el = new Element("div",{
            "class": "blank12 hasLayout"
        });
        blank_el.inject(area_list[1], "bottom");
        var el = new Element("div",{
            "id": "cbg_bottom_ad",
            "class": "slide"
        });
        el.inject(area_list[1], "bottom");
        el.set("html", ad_html);
        var movie = $$("#cbg_bottom_ad ul")[0];
        var nav_list = $$("#cbg_bottom_ad div a");
        var switch_start = 1;
        var switch_delay = 5000;
        var auto_switch = function() {
            for (var i = 0; i < nav_list.length; i++) {
                if (switch_start == i) {
                    nav_list[i].addClass("on");
                } else {
                    nav_list[i].removeClass("on");
                }
            }
            movie.tween("top", switch_start * (-50));
            switch_start = switch_start + 1;
            if (switch_start == data.length) {
                switch_start = 0;
            }
        };
        var timer_obj = null;
        if (data.length > 1) {
            nav_list[0].addClass("on");
            timer_obj = setInterval(auto_switch, switch_delay);
            nav_list.each(function(el, idx) {
                el.addEvent("click", function() {
                    return false
                });
                el.addEvent("mouseover", function() {
                    clearInterval(timer_obj);
                    switch_start = idx;
                    auto_switch();
                })
                el.addEvent("mouseout", function() {
                    timer_obj = setInterval(auto_switch, switch_delay);
                })
            });
        }
        ;
    }
    function show_ad_top(data) {
        var whiteList = ['select_server', 'urs_login', 'select_role', 'mibao_auth', 'overall_search'];
        if (whiteList.contains(window.CBG_PAGE_ID)) {
            return;
        }
        var data = data[0];
        var flag = '_ad_top_' + data['id'];
        if (SessionDB.getItem(flag)) {
            return;
        }
        var tmpl = ['<a href="', data['link_url'], '" target="_blank" tid="web_top_ad" data_trace_text="' + data['id'] + '">', '<img src="', data['image_url'], '" width="960" height="120" />', '</a>', '<i class="cbg-tgxc-close" title="关闭"></i>'].join('');
        var $wrapper = new Element('div',{
            'class': 'cbg-tgxc-top'
        });
        $wrapper.set('html', tmpl).injectAfter($$('.areaBtm')[0]);
        $wrapper.getElement('.cbg-tgxc-close').addEvent('click', function() {
            $wrapper.destroy();
            SessionDB.setItem(flag, 1);
        });
    }
    function show_ad_siderbar(data) {
        var $container = $$('.right_float_menu')[0];
        if (!$container) {
            return;
        }
        var data = data[0];
        var tmpl = ['<a href="', data['link_url'], '" target="_blank">', '<img src="', data['image_url'], '" width="100" height="180" />', '</a>'].join('');
        new Element("li",{
            "class": "cbg-tgxc-sider"
        }).set('html', tmpl).inject($container);
    }
    function show_ad_pop(data) {
        var data = data[0];
        var flag = '_ad_pop_' + data['id'];
        if (StoreDB.getItem(flag) || SessionDB.getItem(flag)) {
            return;
        }
        SessionDB.setItem(flag, 1);
        var $wrapper = new Element('div',{
            'class': 'cbg-tgxc-pop'
        });
        var $link = new Element('a',{
            'href': data['link_url'],
            'target': '_blank',
            'style': 'background-image:url(' + data['image_url'] + ')'
        });
        $link.inject($wrapper);
        var $close = new Element('i',{
            'class': 'cbg-tgxc-close',
            'title': '关闭'
        });
        $close.inject($wrapper);
        $close.addEvent('click', function() {
            StoreDB.setItem(flag, 1);
            $wrapper.destroy();
        });
        $wrapper.addEvent('click', function() {
            StoreDB.setItem(flag, 1);
        });
        $wrapper.inject(document.body);
    }
    var conf = {
        'bottom_ad': show_ad_bottom,
        'top_ad': show_ad_top,
        'side_ad': show_ad_siderbar,
        'pop_ad': show_ad_pop
    };
    function render_ad() {
        var ad_list = window.xyq_ad_list;
        for (var pos in conf) {
            var data = ad_list[pos];
            if (data && data.length && conf[pos]) {
                conf[pos](data);
            }
        }
    }
    render_ad();
    try {
        var keys = Object.keys(localStorage || {});
        for (var i = 0, max = keys.length; i < max; i++) {
            var key = keys[i];
            if (key.indexOf('__session__sad_tag_') >= 0) {
                localStorage.removeItem(key);
            }
        }
    } catch (e) {}
}
function init_fake_role_ui() {
    if (window.isFakeRole) {
        $$('.js_global_fake_role').setStyle('display', '');
        $$('.js_global_normal_role').setStyle('display', 'none');
        if ($('js_fake_role_login_tips')) {
            $('js_fake_role_login_tips').setStyle('display', '');
            init_popover({
                target: 'js_fake_role_login_tips',
                content: '<p style="padding: 5px;">目前处于无角色登录状态。只可\n购买角色，不可出售。购买任意区服角色后可解除限制</p>',
                class_name: 'tipsBlack popArrowUp'
            });
        }
    } else {
        $$('.js_global_normal_role').setStyle('display', '');
        $$('.js_global_fake_role').setStyle('display', 'none');
    }
}
window.addEvent('domready', function() {
    if (window.page_type && page_type == "overall_search") {
        if (LoginInfo && LoginInfo.login) {
            var ctx = {
                LoginInfo: LoginInfo
            };
            render_to_replace('login_info_panel', 'login_info_template', ctx);
        }
    }
    show_shop_cart_info();
    init_wallet();
    WebGuide && WebGuide.next();
    init_right_float_menu();
    $$(".js-popoverHook").each(function(el) {
        init_popover({
            target: el,
            content: el.getAttribute("data-popover-cont"),
            content_id: el.getAttribute("data-popover-target"),
            class_name: el.getAttribute("data-popover-class")
        });
    });
    if (history.length <= 1) {
        $$('a[href=javascript:history.go(-1)]').setStyle('display', 'none');
    }
    try {
        init_ad();
    } catch (e) {}
    init_fake_role_ui();
});
var Popup = function(pop_el) {
    this.pop_el = pop_el;
}
Popup.prototype = {
    show_over_layer: function() {
        var overLayer = $('pop_over');
        if (overLayer == null) {
            var overLayer = document.createElement('div');
            overLayer.id = 'pop_over';
            overLayer.className = 'pageCover';
            document.body.appendChild(overLayer);
        }
        document_size = get_documentsize();
        overLayer.style.height = document_size.height + 'px';
        overLayer.style.width = document_size.width + 'px';
        overLayer.style.display = 'block';
    },
    set_size: function() {
        var overLayer = $('pop_over');
        document_size = get_documentsize();
        overLayer.style.height = document_size.height + 'px';
        overLayer.style.width = document_size.width + 'px';
        set_position_center(this.pop_el);
    },
    show: function() {
        this.show_over_layer();
        this.pop_el.style.display = 'block';
        set_position_center(this.pop_el)
        var __this = this;
        window.onresize = function() {
            __this.set_size();
        }
        ;
    },
    hide: function() {
        var overLayer = $('pop_over');
        if (overLayer) {
            overLayer.style.display = 'none';
            this.pop_el.style.display = 'none';
            window.onresize = null;
        }
    }
}
var new_function_desc = '';
var new_function_url = '';
CAPTCHA_LEN = 5;
function parseDatetime(datetime) {
    var reg = /^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/;
    var values = reg.exec(datetime);
    var v = values.slice(1).map(function(v) {
        return parseInt(v, 10)
    });
    return new Date(v[0],v[1] - 1,v[2],v[3],v[4],v[5]);
}
function init_popover(config) {
    var el_target, content, class_name;
    el_target = $(config.target);
    if (config.content) {
        content = transform_newline(config.content);
    } else if (config.content_id) {
        var el_content = $(config.content_id);
        if (el_content) {
            content = el_content.get("html");
        }
    } else {
        return;
    }
    class_name = config.class_name || "popover";
    el_target.addEvents({
        mouseenter: function() {
            var popover = $("popover");
            if (!popover) {
                popover = new Element("div#popover");
                popover.inject(document.body);
            }
            var coordinates = el_target.getCoordinates();
            popover.set({
                "html": content,
                "class": class_name,
                "styles": {
                    "display": "block",
                    "top": coordinates.bottom + 5 + "px",
                    "left": coordinates.right + 5 + "px"
                }
            });
            if (config.mockClick) {
                config.target.click();
            }
        },
        mouseleave: function() {
            var popover = $("popover");
            if (popover) {
                popover.setStyle("display", "none");
            }
        }
    });
}
var PopupDialog = new Class({
    Implements: [Events],
    initialize: function(title, content) {
        if (typeof arguments[0] === 'object') {
            var config = arguments[0];
            this._title = config.title;
            this._content = config.content;
            this._mask = config.mask;
            this._onClose = config.onClose;
            this._autoDispose = config.autoDispose;
        } else {
            this._title = title;
            this._content = content;
        }
        this._autoDispose = (this._autoDispose == null) ? true : this._autoDispose;
        this.setup();
    },
    setup: function() {
        var that = this;
        that.getRoot().set("html", this.getTemplate()).addEvent("click:relay([data-event])", function(e) {
            var evt = this.get('data-event');
            that.fireEvent(evt, [e]);
        }).getElement(".dialogClose").addEvent("click", function() {
            that.hide();
        });
    },
    getRoot: function() {
        if (!this.dialog) {
            var dialog = this.dialog = new Element("div.popupDialog");
            dialog.inject(document.body);
            dialog.setStyle('display', 'none');
        }
        return this.dialog;
    },
    getTemplate: function() {
        var tmpl = ['<div class="dialogWrap">', '<div class="blockTitle">', this._title, '<span class="dialogClose" data-event="close"></span>', '</div>', '<div class="dialogCont">', this._content, '</div>', '</div>'];
        return tmpl.join('');
    },
    showMask: function() {
        if (!this.el_mask) {
            this.el_mask = new Element("div.popupDialogMask");
        }
        this.el_mask.inject(document.body);
    },
    hideMask: function() {
        this.el_mask && this.el_mask.dispose();
    },
    hide: function() {
        var autoDispose = this._autoDispose;
        if (!this._onClose || !this._onClose()) {
            if (autoDispose) {
                this.fireEvent('hide');
                this.dialog && this.dialog.dispose();
            } else {
                this.dialog.setStyle('display', 'none');
            }
            this.hideMask();
        }
        return this;
    },
    show: function() {
        var that = this;
        var dialog = this.dialog;
        dialog.set('style', '');
        dialog.setStyles({
            "right": "50%",
            "margin-top": -dialog.clientHeight / 2,
            "margin-right": -dialog.clientWidth / 2
        });
        dialog.setStyle('width', dialog.getWidth());
        if (this._mask === undefined || this._mask) {
            this.showMask();
        }
        this.fireEvent('show');
        return this;
    }
});
PopupDialog.alert = function(content, opts) {
    if (typeof content === 'object') {
        opts = content;
        content = opts.content || '';
    }
    opts = Object.merge({
        title: '提示',
        buttonText: '确定',
        buttons: [],
        needClose: false
    }, opts || {});
    content = ['<div class="f14px" style="line-height:1.5;padding:20px;min-width:200px;">', content, '<div class="js_buttons_warp"></div>', '</div>'].join('');
    function generateButtons($root) {
        var buttonText = opts.buttonText;
        var buttons = opts.buttons || [];
        var html = '';
        if (buttons.length > 0) {
            var list = [];
            buttons.forEach(function(btn, i) {
                var defCls = 'js_alert_btn_' + i;
                list.push('<a href="javascript:;" ' + (btn.close ? ' data-close="1" ' : '') + (btn.event ? ' data-event="' + btn.event + '"' : '') + ' class="' + (btn.cls ? btn.cls : '') + ' btn1 ' + defCls + '">' + btn.text + '</a>');
                if (btn.onclick) {
                    $root.addEvent('click:relay(.' + defCls + ')', btn.onclick);
                }
            });
            html = list.join('&nbsp;');
        } else if (buttonText) {
            html = '<a href="javascript:;" class="btn1" data-close="1" data-event="close">' + buttonText + '</a>';
        }
        return html ? '<div class="textCenter" style="padding-top:15px;margin-bottom:-5px;">' + html + '</div>' : '';
    }
    var popup = new PopupDialog(opts.title,content);
    var $dialog = popup.dialog;
    if (opts.needClose == false) {
        var $close = $dialog.getElement('.dialogClose');
        $close && $close.dispose();
    }
    $dialog.addEvent('click:relay([data-close])', function() {
        popup.hide();
    });
    $dialog.getElement('.js_buttons_warp').set('html', generateButtons($dialog));
    popup.show();
    return popup;
}
PopupDialog.confirm = function(content, opts) {
    if (typeof content === 'object') {
        opts = content;
        content = opts.content || '';
    }
    opts = opts || {};
    opts = Object.merge({
        title: '提示',
        confirmText: '确定',
        cancelText: '取消',
        buttons: [{
            text: opts.confirmText || '确定',
            event: 'confirm'
        }, {
            text: opts.cancelText || '取消',
            event: 'cancel'
        }]
    }, opts);
    content = ['<div class="f14px" style="line-height:1.5;padding:20px;min-width:200px;">', content, '<div class="js_buttons_warp"></div>', '</div>'].join('');
    function generateButtons($root) {
        var buttonText = opts.buttonText;
        var buttons = opts.buttons || [];
        var html = '';
        if (buttons && buttons.length) {
            var list = [];
            buttons.forEach(function(btn, i) {
                var defCls = 'js_alert_confirm_' + i + (btn.cls ? ' ' + btn.cls : '');
                list.push('<a href="javascript:;" ' + (btn.event ? ' data-event="' + btn.event + '"' : '') + ' class="' + ' btn1 ' + defCls + '">' + btn.text + '</a>');
            });
            html = list.join('&nbsp;');
        }
        return html ? '<div class="textCenter" style="padding-top:15px;margin-bottom:-5px;">' + html + '</div>' : '';
    }
    var popup = new PopupDialog(opts.title,content);
    popup.addEvent('confirm', function() {
        popup.hide();
    });
    popup.addEvent('cancel', function() {
        popup.hide();
    });
    popup.dialog.getElement('.js_buttons_warp').set('html', generateButtons(popup.dialog));
    popup.show();
    return popup;
}
var InfoDialog = new Class({
    Extends: PopupDialog,
    initialize: function(config) {
        config.content = this.getContent(config);
        this.parent(config);
        var $root = this.getRoot();
        $root.addClass('infoDialog');
        var buttons = config.buttons;
        if (!buttons || buttons.length == 0) {
            var self = this;
            buttons = [{
                name: '确定',
                onclick: function() {
                    self.hide();
                }
            }];
        }
        var $buttons = $root.getElement('.buttons');
        for (var i = 0; i < buttons.length; i++) {
            var btn = buttons[i];
            var $btn = new Element('a.btn1');
            $btn.set({
                html: btn.name,
                href: btn.href || 'javascript:;'
            })
            if (btn.target) {
                $btn.set('target', btn.target);
            }
            if (btn.tid) {
                $btn.set('tid', btn.tid);
            }
            if (btn.onclick) {
                $btn.addEvent('click', btn.onclick);
            }
            $btn.inject($buttons);
        }
    },
    getContent: function(config) {
        var icon;
        if (config.type) {
            icon = '<i class="s-icon ' + config.type + '"></i>';
        }
        return ['<div class="' + (icon ? 'iconWrap' : '') + '">', (icon ? icon : ''), '<div class="contentWrap">', '<p class="fB">', (config.subTitle || ''), '</p>', '<p>', (config.info || ''), '</p>', '</div>', '<div class="divider"></div>', '<div class="buttons"></div>', '</div>'].join('');
    }
});
InfoDialog.TYPE = {
    SUCCESS: 's-icon-big-success',
    FAIL: 's-icon-big-fail',
    WARN: 's-icon-big-warn'
}
var PopupManager = new Class({
    initialize: function(popup_id, over_layer_id) {
        this._popup_id = popup_id;
        if (over_layer_id) {
            this._over_layer_id = over_layer_id;
        } else {
            this._over_layer_id = "pop_over";
        }
        this._win_change = null;
    },
    show_over_layer: function() {
        var over_layer = $(this._over_layer_id);
        if (!over_layer) {
            over_layer = new Element("div",{
                "id": this._over_layer_id
            });
            over_layer.addClass("pageCover");
            over_layer.inject(document.body);
        }
        over_layer.setStyle("height", Document.getScrollHeight());
        over_layer.setStyle("display", "block");
    },
    show_popup: function() {
        popup = $(this._popup_id);
        popup.setStyle("display", "block");
        popup.setStyles({
            "left": ((Window.getWidth() - popup.getSize().x) / 2) + "px",
            "top": (Window.getHeight() - popup.getHeight()) / 2 + Window.getScrollTop() + "px"
        });
    },
    hide: function() {
        window.removeEvent("scroll", this._win_change);
        window.removeEvent("resize", this._win_change);
        $(this._popup_id).setStyle("display", "none");
        $(this._over_layer_id).setStyle("display", "none");
    },
    show: function() {
        this.show_over_layer();
        this.show_popup();
        var that = this;
        var win_change = function() {
            if ($(that._popup_id).getStyle("display") != "block") {
                that.hide();
                return;
            }
            that.show_over_layer();
            that.show_popup();
        };
        this._win_change = win_change;
        window.addEvent("scroll", win_change);
        window.addEvent("resize", win_change);
    }
});
function ObjectToString(obj) {
    var result = [];
    for (var p in obj) {
        result.push(p + '=' + obj[p]);
    }
    return result.join('&');
}
function try_login_to_buy(equipid, serverid, server_name, area_id, area_name, eid) {
    var login_url = HttpsCgiRootUrl + '/show_login.py?act=show_login&server_id=' + serverid + '&server_name=' + encodeURIComponent(server_name) + '&area_name=' + encodeURIComponent(area_name) + '&area_id=' + area_id + '&equip_id=' + equipid;
    var equip_refer = getPara('equip_refer') || '1';
    var return_url = HomePage + '/equip?s=' + serverid + '&eid=' + eid + '&equip_refer=' + equip_refer;
    var is_login = parseInt(Cookie.read("is_user_login"));
    if (is_login == 1) {
        var args = {
            "act": "auto_switch_server",
            "go_serverid": serverid,
            "login_url": login_url,
            "return_url": return_url
        };
        var url = CgiRootUrl + "/login_check.py?" + Object.toQueryString(args);
    } else {
        var url = login_url + "&return_url=" + encodeURIComponent(return_url);
    }
    window.open(url);
}
function parse_role_info(raw_info) {
    try {
        raw_info = decode_desc(raw_info);
        return JSON.decode(raw_info);
    } catch (e) {
        return js_eval(lpc_2_js(raw_info));
    }
}
function parse_desc_info(desc_info) {
    try {
        desc_info = decode_desc(desc_info);
        return JSON.decode(desc_info).desc;
    } catch (e) {
        return desc_info;
    }
}
function select_rank(serverid, index) {
    var rank = $('rank_select');
    if (index == 1) {
        window.location = '/static_file/' + serverid + '/rank_pages/worth_rank1.html';
        return
    } else if (index == 2) {
        window.location = '/static_file/' + serverid + '/rank_pages/collect_rank1.html';
        return
    }
}
function dict_get(dict_obj, key, default_value) {
    if (dict_obj[key] != undefined) {
        return dict_obj[key];
    } else {
        return default_value;
    }
}
function gen_highlight_html(highlight_list, separator, if_add_search_link) {
    if (typeof highlight_list === 'string') {
        try {
            highlight_list = eval(highlight_list);
            if (typeof highlight_list === 'string') {
                highlight_list = JSON.decode(highlight_list);
            }
        } catch (e) {}
    }
    var html_list = [];
    for (var i = 0; i < highlight_list.length; i++) {
        var item = highlight_list[i];
        var color = "";
        if (item[1] >= 90) {
            color = "#A805EC";
        } else if (item[1] >= 70 && item[1] <= 80) {
            color = "#F60707";
        } else if (item[1] >= 40 && item[1] <= 60) {
            color = "#0A06ED";
        } else {
            continue;
        }
        if (if_add_search_link) {
            var search_paras = JSON.encode(item).toBase64();
            html_list.push('<a href="#" data_paras="' + search_paras + '" onclick="add_highlight_filter(this);return false;" style="color:' + color + '">' + item[0] + '</a>');
        } else {
            html_list.push('<span style="color:' + color + '">' + item[0] + '</span>');
        }
    }
    return html_list.join(separator);
}
function gen_dynamic_tags_html(dynamicTags, separator) {
    var html_list = [];
    for (var i = 0; i < dynamicTags.length; i++) {
        var item = dynamicTags[i];
        html_list.push('<span style="color: #C17201;">' + item.name + '</span>');
    }
    return html_list.join(separator);
}
function get_sub_kinds(kind_tree, parent_kindid) {
    if (!kind_tree || kind_tree.length != 2) {
        return [];
    }
    var ret = [];
    var sub_kinds = kind_tree[1];
    if (sub_kinds.length > 0) {
        var is_equal = kind_tree[0][0] === parent_kindid;
        for (var i = 0; i < sub_kinds.length; i++) {
            var kind = sub_kinds[i];
            if (is_equal) {
                ret.push({
                    'kindid': kind[0][0],
                    'name': kind[0][1]
                });
                if (parent_kindid == 60) {
                    a = 1;
                }
                ret = ret.concat(get_sub_kinds(kind, kind[0][0]));
            } else {
                ret = ret.concat(get_sub_kinds(kind, parent_kindid));
            }
        }
    }
    return ret;
}
function is_lingshi(kindid) {
    kindid = parseInt(kindid);
    if (kindid == 60) {
        return true;
    }
    var lingshi_kinds = get_sub_kinds(kind, 60);
    for (var i = 0; i < lingshi_kinds.length; i++) {
        if (kindid == lingshi_kinds[i].kindid) {
            return true;
        }
    }
    return false;
}
function is_pet_equip(kindid) {
    if (kindid == 29) {
        return true;
    }
    return false;
}
function handle_advance_search_link(type) {
    var isEquipDetailPage = (window.location.pathname === '/equip');
    var pathname = window.location.pathname;
    var searchFunc = window['show_' + type + '_search_form'];
    if (pathname === '/equip' || pathname.search('equipquery.py') >= 0 || !searchFunc) {
        window.location.href = '/cgi-bin/query.py?act=query&search_menu=' + type;
    } else {
        searchFunc();
    }
}
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
function get_exact_remain_time_desc(seconds, showDays) {
    var text = '';
    if (showDays && seconds >= 86400) {
        text += Math.floor(seconds / 86400) + '天';
        seconds %= 86400;
    }
    if (seconds >= 3600) {
        text += Math.floor(seconds / 3600) + '小时';
        seconds %= 3600;
    }
    if (seconds >= 60) {
        text += Math.floor(seconds / 60) + '分';
        seconds %= 60;
    }
    text += seconds + '秒';
    return text;
}
var popupModal = (function() {
    var cover, popup, popupBody, popupHeader, popupTitle, popupClose;
    var closeCallback;
    return {
        show: function(options) {
            var self = this;
            if (popup === undefined) {
                if (!$("popup")) {
                    popup = new Element("div",{
                        "class": "popup",
                        "id": "popup"
                    });
                    popup.inject(document.body);
                } else {
                    popup = $("popup");
                }
            }
            if (cover === undefined) {
                if (!$("pageCover")) {
                    cover = new Element("div",{
                        "class": "pageCover",
                        "id": "pageCover",
                        "style": {
                            "display": "none"
                        }
                    });
                    cover.inject(document.body);
                } else {
                    cover = $("pageCover");
                }
            }
            if (popupTitle === undefined) {
                popupHeader = new Element("div",{
                    "class": "popupHeader"
                });
                popupTitle = new Element("div",{
                    "class": "popupTitle",
                    html: options.title
                });
                popupClose = new Element("i",{
                    "class": "popupClose",
                    "events": {
                        click: function() {
                            self.hide();
                            closeCallback();
                        }
                    }
                });
                popupTitle.inject(popupHeader);
                popupClose.inject(popupHeader);
                popupHeader.inject(popup);
            } else if (typeof options.title === "string") {
                popupTitle.set("text", options.title);
            }
            if (popupBody === undefined) {
                popupBody = new Element("div",{
                    "class": "popupBody",
                    "html": options.body
                });
                popupBody.inject(popup);
            } else if (typeof options.body === "string") {
                popupBody.set("html", options.body);
            }
            if (typeof options.bodyWidth === "number") {
                var pl = parseFloat(popupBody.getStyle("paddingLeft"));
                var pr = parseFloat(popupBody.getStyle("paddingRight"));
                popup.setStyle("width", options.bodyWidth + pl + pr + "px");
            }
            closeCallback = options.closeCallback || function() {}
            ;
            cover.setStyle("display", "block");
            popup.setStyle("display", "block");
            this.adjust(Document.getScrollHeight());
        },
        adjust: function(height) {
            if (cover && typeof height === "number") {
                cover.setStyle("height", height);
            }
            if (popup) {
                setTimeout(function() {
                    popup.setStyles({
                        "left": ((Window.getWidth() - popup.getWidth()) / 2) + "px",
                        "top": (Window.getHeight() - popup.getHeight()) / 2 + Window.getScrollTop() + "px"
                    });
                }, 0);
            }
        },
        hide: function() {
            cover.setStyle("display", "none");
            popup.setStyle("display", "none");
        }
    }
}
)();
$(window).addEvents({
    scroll: throttle(popupModal.adjust, 200, true),
    resize: throttle(popupModal.adjust, 300, true)
});
function throttle(fn, delay, immediate, debounce) {
    var curr = +new Date(), last_call = 0, last_exec = 0, timer = null, diff, context, args, exec = function() {
        last_exec = curr;
        fn.apply(context, args);
    };
    return function() {
        curr = +new Date();
        context = this,
        args = arguments,
        diff = curr - (debounce ? last_call : last_exec) - delay;
        clearTimeout(timer);
        if (debounce) {
            if (immediate) {
                timer = setTimeout(exec, delay);
            } else if (diff >= 0) {
                exec();
            }
        } else {
            if (diff >= 0) {
                exec();
            } else if (immediate) {
                timer = setTimeout(exec, -diff);
            }
        }
        last_call = curr;
    }
}
function debounce(fn, delay, immediate) {
    return throttle(fn, delay, immediate, true);
}
function switch_select(ctrl_box_id, el_list_id) {
    var v = $(ctrl_box_id).checked;
    var el_list = $$(el_list_id)
    for (var i = 0; i < el_list.length; i++) {
        el_list[i].checked = v;
        el_list[i].setAttribute("checked", v);
    }
}
function cascade_checkbox(el_main, el_sub, callback) {
    el_main.addEvent('click', function() {
        el_sub.set('checked', this.checked)
        callback && callback.call(this);
    });
    el_sub.addEvent('click', function() {
        var isChecked = true;
        for (var i = el_sub.length - 1; i >= 0; i--) {
            if (!el_sub[i].checked) {
                isChecked = false;
                break;
            }
        }
        el_main.checked = isChecked;
    });
}
function init_fingerprint() {
    if (!$("device_id")) {
        return;
    }
    new Fingerprint2().get(function(result, components) {
        $("device_id").value = result;
    });
}
function get_fingerprint() {
    if ($("device_id")) {
        return $("device_id").value;
    } else {
        return "";
    }
}
var BargainPanel = (function() {
    var cover, popup;
    var equip;
    var bargain_loc;
    function setHoverEvent($root, selector, options) {
        if (!selector) {
            return;
        }
        options = Object.merge({
            enter: function() {},
            leave: function() {}
        }, options || {});
        $root.addEvent('mouseenter:relay(' + selector + ')', function(e) {
            options.enter.call(this, e);
        }).addEvent('mouseleave:relay(' + selector + ')', function(e) {
            options.leave.call(this, e);
        });
    }
    var init = function() {
        var timerInput;
        function fnInput(e) {
            var ctx = this;
            clearTimeout(timerInput);
            timerInput = setTimeout(function() {
                update_msg.call(ctx, e);
            }, 400);
        }
        $('bargain_price').addEvents({
            blur: fnInput,
            keyup: fnInput,
            change: fnInput
        });
        $('btn_send_bargain').addEvent('click', send_bargain);
        $('btn_close_bargain').addEvent('click', hide);
        cover = $("pageCoverBargain");
        popup = $("popupWinBargain");
        var fkTip;
        setHoverEvent(popup, '.jsTip', {
            enter: function() {
                if (!fkTip) {
                    fkTip = new FloatTip(this,{
                        icon: false,
                        dir: 'right',
                        x: 5,
                        y: -2
                    });
                }
                fkTip.update(this);
                fkTip.$root.setStyles({
                    'z-index': 10003,
                    'font-size': 12
                });
                var $target = fkTip.$target;
                fkTip.show($target.get('data-title'));
            },
            leave: function() {
                fkTip && fkTip.hide();
                fkTip = null;
            }
        });
        var qrTip;
        setHoverEvent(popup, '.jsDlTip', {
            enter: function() {
                if (!fkTip) {
                    qrTip = new FloatTip(this,{
                        icon: false,
                        dir: 'bottom',
                        x: -44,
                        y: 5
                    });
                    qrTip.$root.setStyles({
                        'z-index': 10002,
                        'padding': 8,
                        'color': '#333',
                        'background': '#fff',
                        'border-radius': 0,
                        'border': '0 none',
                        'box-shadow': '0 0 5px #666'
                    });
                }
                qrTip.show('<p class="textCenter"><img src="/images/qrcode.png" width="149" height="149" style="vertical-align:bottom;margin-bottom:4px;" /><br/>扫描下载</p>');
            },
            leave: function() {
                qrTip && qrTip.hide();
                qrTip = null;
            }
        });
        popup.getElement('.bargainTipRange').set('html', '（还价的范围为<span class="cRed">' + (BargainLimits[1].final_range[0] / 100) + '</span>元-<span class="cRed">' + (BargainLimits[1].final_range[1] / 100) + '</span>元）');
        if (typeOf(window.CurrentEquipRemainBargainTimesToday) === 'number') {
            popup.getElement('.bargainTipLeaveTimes').set('html', window.CurrentEquipRemainBargainTimesToday ? ('您对该商品剩余还价次数：<span class="cRed">' + CurrentEquipRemainBargainTimesToday + '</span>次') : '<span class="cRed">今天对该物品的还价次数已用完</span>');
        }
        popup.getElement('.bargainTipAllLeaveTimes').set('html', RemainBargainTimesToday ? ('今日总还价次数剩余：<span class="cRed">' + RemainBargainTimesToday + '</span>次') : '<span class="cRed">今天的还价次数已用完</span>');
        init = function() {}
        ;
    };
    function show(equip_info, loc) {
        if (!BargainLimits[0]) {
            alert(BargainLimits[1]);
            return;
        }
        if (RemainBargainTimesToday <= 0) {
            return alert("抱歉，今天总还价次数已达上限10次，请明天再来。");
        }
        if (typeOf(window.CurrentEquipRemainBargainTimesToday) === 'number' && CurrentEquipRemainBargainTimesToday <= 0) {
            return alert("抱歉，每天对单个商品还价的次数不能超过3次。");
        }
        init();
        equip = equip_info || window.equip;
        bargain_loc = loc || '';
        $("bargain_price").value = "";
        update_msg();
        show_layer_center(cover, popup);
        $("bargain_price").focus();
    }
    function hide() {
        cover.style.display = popup.style.display = 'none';
    }
    function check_price(price_yuan) {
        if (!/^(\d+)(\.(\d){0,2})?$/.test(price_yuan))
            return "您填写的价格有错误"
        var lim = BargainLimits[1];
        var price = Math.round(price_yuan * 100);
        if (price >= lim.cur_price)
            return "还价价格要低于原价，请重新输入！";
        if (price < Math.round(lim.cur_price * 0.65))
            return "低于可还价范围";
        if (price <= lim.last_bargain_price)
            return '还价价格必须高于上次还价价格(' + (lim.last_bargain_price / 100) + '元)';
        if (price >= lim.last_rebargain_price)
            return '还价价格高于卖家还价价格，请直接购买';
        if (price < lim.equip_min_price)
            return '还价价格不能低于该物品允许的最低价格(' + (lim.equip_min_price / 100) + '元)';
        if (price < lim.final_range[0]) {
            return '低于卖家首次上架价格的50%';
        }
        return null;
    }
    function check_price_level(price_yuan) {
        var price = Math.round(price_yuan * 100);
        var cur_price = BargainLimits[1].cur_price;
        if (price < cur_price * 0.7)
            return {
                text: typeOf(window.CurrentEquipRemainBargainTimesToday) === 'number' ? '极低；您很有可能被卖家标识为恶意还价玩家；请谨慎还价。<span class="s-icon s-icon-ask jsTip" data-title="被标记为恶意还价玩家后，<br/>卖家将不会接收到你的还价信息。"></span>' : '极低',
                color: 'red'
            };
        else if (price < cur_price * 0.9)
            return {
                text: '一般',
                color: 'orange'
            };
        else
            return {
                text: '高',
                color: 'green'
            };
    }
    var isSendingBargain = false;
    function send_bargain() {
        var new_price = $("bargain_price").value.trim();
        var msg = check_price(new_price);
        if (msg) {
            alert(msg);
            return;
        }
        if (isSendingBargain) {
            return;
        }
        var fnFail = function() {
            isSendingBargain = false;
            alert('网络繁忙，请稍候再试');
        };
        var Ajax = new Request.JSON({
            url: CgiRootUrl + "/message.py?act=bargain_by_eid",
            onSuccess: function(data, txt) {
                isSendingBargain = false;
                alert(data.msg);
                setTimeout(function() {
                    location.reload();
                }, 120);
            },
            onFailure: fnFail,
            onError: fnFail
        });
        isSendingBargain = true;
        Ajax.post({
            price: yuantofen(new_price),
            accept_text_message: popup.getElement('.jsAccept').checked ? 1 : 0,
            eid: equip["eid"],
            obj_server_id: equip['server_id'],
            loc: bargain_loc,
            view_loc: getPara('view_loc') || '-'
        });
    }
    function yuantofen(yuan) {
        return Math.round(parseFloat(yuan) * 100);
    }
    function update_msg() {
        var new_price = $("bargain_price").value.trim();
        var warning;
        if (new_price.length > 0) {
            warning = check_price(new_price);
            var price_info = new_price;
            if (warning) {
                warning = '<span class="cRed">' + warning + '</span>';
            } else {
                var level_info = check_price_level(new_price);
                warning = '还价成功率：<span style="color:' + level_info.color + '">' + level_info.text + '</span>';
                if (parseInt(new_price) < 300) {
                    popup.getElement('.jsAccept').set({
                        checked: false,
                        disabled: true
                    }).getParent().addClass('cGray');
                } else {
                    popup.getElement('.jsAccept').set({
                        disabled: false
                    }).getParent().removeClass('cGray');
                }
            }
        } else {
            var price_info = '?';
            var warning = '还价成功率：--';
        }
        $('bargain_warning').set('html', warning);
    }
    return {
        show: show,
        hide: hide
    };
}
)();
var BargainResponsePanel = (function() {
    var cur_msgid, cur_bargainid;
    var cur_loc;
    function init(loc) {
        cur_loc = loc;
        $$('.j_hide_bargain_popup').addEvent('click', function() {
            $("pageCoverBargainOwner").setStyle("display", "none");
            this.getParent('.popupWin').setStyle("display", "none");
            return false;
        });
        $$('.j_bargain_response_action').addEvent('click', function() {
            var datas = $(this).getParent();
            var popup = $(this.getAttribute('data-key') + 'BargainPopupWin');
            popup.getElements('[data-key]').each(function(sub) {
                var key = sub.getAttribute('data-key');
                sub.set('html', datas.getAttribute('data-' + key));
            });
            cur_msgid = datas.getAttribute('data-msgid');
            cur_bargainid = datas.getAttribute('data-bargainid');
            show_layer_center($('pageCoverBargainOwner'), popup);
            return false;
        });
        $('btn_accept_bargain').addEvent('click', function() {
            bargain_response('accept');
        });
        $('btn_refuse_bargain').addEvent('click', function() {
            bargain_response('refuse');
        });
        $('btn_rebargain').addEvent('click', function() {
            var price = $('rebargain_price').value.trim();
            if (!/^\d+(\.\d?\d?)?$/.test(price)) {
                alert('请正确输入价格');
                return;
            }
            price = +price;
            if (price <= $('rebargain_price_min').get('text')) {
                alert('价格过低');
                return;
            }
            if (price >= $('rebargain_price_max').get('text')) {
                alert('价格过高');
                return;
            }
            bargain_response('rebargain', price);
        });
        $('btn_malicious_bargain').addEvent('click', function() {
            var radios = $$('input[name=maliciousBargainRadio]:checked');
            var opt = radios && radios[0] && radios[0].get('value');
            if (opt == 'ignore')
                bargain_response('refuse');
            else if (opt == 'forbidden')
                bargain_response('malicious');
            else
                alert('请选择期望的处理方式');
        });
    }
    function bargain_response(resp_type, resp_price_yuan) {
        url = CgiRootUrl + '/message.py?act=resp_bargain';
        params = {
            msgid: cur_msgid || '',
            bargainid: cur_bargainid || '',
            resp_type: resp_type,
            resp_price: resp_price_yuan || '',
            safe_code: safe_code,
            loc: cur_loc
        }
        var ajax = new Request.JSON({
            url: url,
            onSuccess: function(data, txt) {
                if (data["status"] == 1) {
                    alert("操作成功");
                    window.location.reload();
                } else {
                    alert("操作失败：" + data["msg"]);
                }
            },
            onError: function(text, error) {
                alert("登录超时或者操作失败");
            }
        });
        ajax.post(params);
    }
    return {
        init: init
    };
}
)();
;(function() {
    var isPopupRemindInputInit = false;
    function show_remind_price_panel(change_down_price_desc) {
        $$('#remindful_price').set('value', '');
        if (change_down_price_desc) {
            var $changeDownPriceDesc = $$('#changeDownPriceDesc');
            $changeDownPriceDesc.set('html', '(' + change_down_price_desc + ')');
            $changeDownPriceDesc.setStyle("display", "");
        }
        var $popup = $("popupRemindPrice");
        show_layer_center($("pageRemindPrice"), $popup);
        if ($popup) {
            $popup.removeEvent('click:relay([data-close])').addEvent('click:relay([data-close])', hide_remind_price_panel);
            if (!isPopupRemindInputInit) {
                isPopupRemindInputInit = true;
                InputLimit.onlyInt($popup, '#remindful_price');
            }
        }
    }
    function hide_remind_price_panel() {
        $("pageRemindPrice").setStyle("display", "none");
        $("popupRemindPrice").setStyle("display", "none");
    }
    var IsDoingCollectOP = false;
    function add_collect_remind_price(equip) {
        if (IsDoingCollectOP) {
            return;
        }
        $$('#remindful_price').removeEvent('focus').addEvent('focus', function() {
            $$('#popupRemindPrice .js_error').setStyle('visibility', 'hidden');
        });
        var setError = function(msg) {
            var $err = $$('#popupRemindPrice .js_error');
            $err.setStyle('visibility', 'visible');
            $err.set('html', msg);
        };
        var showSuc = function() {
            (new ToastTip('降价提醒设置成功')).show();
        }
        equip = equip || window.collect_equip || window.equip || {};
        var remindful_price_value = $('remindful_price').get('value').trim();
        var remindful_price = parseFloat(remindful_price_value);
        if (!remindful_price_value) {
            hide_remind_price_panel();
            return showSuc();
        }
        if (isNaN(remindful_price)) {
            return setError('请输入数字');
        }
        if (remindful_price <= 0) {
            return setError("输入的价格需大于0");
        } else if (remindful_price >= equip['price']) {
            return setError("输入的价格需小于当前收藏物品的价格");
        }
        var url = CgiRootUrl + "/userinfo.py?act=ajax_change_remindful_price&initial_set=1";
        url += "&order_sn=" + equip["game_ordersn"];
        url += "&remindful_price=" + remindful_price;
        var success_handler = function(data, txt) {
            IsDoingCollectOP = false;
            if (!data["status"]) {
                alert(data["msg"]);
                return;
            }
            hide_remind_price_panel();
            showSuc();
        };
        var failure_handler = function() {
            IsDoingCollectOP = false;
            alert('提醒价格设置失败，请重试');
        };
        var Ajax = new Request.JSON({
            url: url,
            onSuccess: success_handler,
            onFailure: failure_handler,
            onError: failure_handler,
            noCache: true
        });
        Ajax.get();
        return false;
    }
    var last_fav_tip_elem = null;
    var KEY_FAV_FLOAT_TIP = 'float-tip';
    var KEY_FAV_FLOAT_TIP_TIMER = 'float-tip-timer';
    function clearFavoriteFloatTip(el) {
        el = el || last_fav_tip_elem;
        if (!el) {
            return;
        }
        el = $(el);
        var ft = el.retrieve(KEY_FAV_FLOAT_TIP);
        ft && ft.hide();
        var t = el.retrieve(KEY_FAV_FLOAT_TIP_TIMER);
        clearTimeout(t);
        el.eliminate(KEY_FAV_FLOAT_TIP);
        el.eliminate(KEY_FAV_FLOAT_TIP_TIMER);
        last_fav_tip_elem = null;
    }
    function isCollectNoCounted() {
        var user_level = Cookie.read('login_user_level');
        if (user_level && parseInt(user_level) < 50) {
            return true;
        }
        return false;
    }
    function add_to_favorites(equip, options) {
        if (IsDoingCollectOP) {
            return;
        }
        clearFavoriteFloatTip();
        var isNoCounted = isCollectNoCounted();
        if (isNoCounted) {
            if (!confirm("尊敬的玩家，您好！由于您的角色等级不足50级，收藏该商品后，将不计算在商品收藏数当中，但是收藏功能（查看收藏、降价提醒等）可正常使用，您确定要收藏该商品吗？")) {
                return options.complete();
            }
        }
        equip = equip || window.collect_equip || window.equip || {};
        options = Object.merge({
            elTip: null,
            tipOptions: {
                dir: 'bottom',
                y: 6,
                x: 'auto'
            },
            onSuccess: null,
            success: function(data) {
                if (!data["status"]) {
                    alert(data['msg']);
                    options.complete();
                    return
                }
                equip.add_collect_callback && equip.add_collect_callback(data, isNoCounted);
                options.complete();
                options.onSuccess && options.onSuccess(data, isNoCounted);
                var elTip = options.elTip;
                if (elTip) {
                    clearFavoriteFloatTip(elTip);
                    var floatTip = new FloatTip(elTip,Object.merge({
                        cls: 'collect_suc_ft',
                        autoFixTime: 100
                    }, options.tipOptions));
                    floatTip.show('收藏成功！<a href="javascript:;" class="collect_suc_ft_setting">点此可设置降价提醒</a>');
                    floatTip.$root.addEvent('click:relay(.collect_suc_ft_setting)', function() {
                        clearFavoriteFloatTip(elTip);
                        show_remind_price_panel(data.change_down_price_desc);
                    });
                    var timer = setTimeout(function() {
                        clearFavoriteFloatTip(elTip);
                    }, 4000);
                    elTip.store(KEY_FAV_FLOAT_TIP, floatTip);
                    elTip.store(KEY_FAV_FLOAT_TIP_TIMER, timer);
                    last_fav_tip_elem = elTip;
                } else {
                    (new ToastTip('收藏成功')).show();
                }
            },
            fail: function() {
                alert('收藏失败，请重试');
                options.complete();
            },
            complete: function() {}
        }, options || {});
        var url = CgiRootUrl + "/userinfo.py?act=ajax_add_collect&order_sn=" + equip["game_ordersn"] + "&attention=1&query_tag=" + (window.CurQueryTag || '') + "&obj_server_id=" + equip['server_id'];
        if (equip.collect_refer) {
            url += '&refer=' + equip.collect_refer;
        } else if (window.equip_refer_loc) {
            url += '&refer=' + window.equip_refer_loc;
        }
        if (equip.from_external_id) {
            url += '&from_external_id=' + equip.from_external_id;
        }
        if (equip.refer_app) {
            url += '&refer_app=' + equip.refer_app;
        } else {
            url += '&refer_app=null';
        }
        var requestFailure = function(message) {
            options.fail(message);
        };
        var ajax = new Request.JSON({
            url: url,
            onSuccess: function(data) {
                options.success(data);
            },
            onFailure: requestFailure,
            onError: requestFailure,
            noCache: true
        });
        ajax.get();
    }
    function del_from_favorites(options) {
        if (IsDoingCollectOP) {
            return;
        }
        var isNoCounted = isCollectNoCounted();
        options = Object.merge({
            elTip: null,
            onSuccess: null
        }, options || {});
        var elTip = options.elTip;
        if (elTip == last_fav_tip_elem) {
            clearFavoriteFloatTip(elTip);
        }
        var equip = window.collect_equip || window.equip;
        var url = CgiRootUrl + "/userinfo.py?act=ajax_del_collect&order_sn=" + equip["game_ordersn"];
        if (equip.collect_refer) {
            url += '&refer=' + equip.collect_refer;
        } else if (window.equip_refer_loc) {
            url += '&refer=' + window.equip_refer_loc;
        }
        if (equip.refer_app) {
            url += '&refer_app=' + equip.refer_app;
        } else {
            url += '&refer_app=null';
        }
        var Ajax = new Request.JSON({
            url: url,
            noCache: true,
            onSuccess: function(data, txt) {
                IsDoingCollectOP = false;
                if (data.status != 1) {
                    alert(data.msg);
                    equip.del_collect_error_callback && equip.del_collect_error_callback();
                    return;
                }
                alert("删除收藏成功，请到“我的藏宝阁->我的收藏“里面查看。");
                equip.del_collect_callback && equip.del_collect_callback(data, isNoCounted);
                options.onSuccess && options.onSuccess(data, isNoCounted);
            }
        });
        Ajax.get();
    }
    function login_to_collect() {
        if (confirm("登录后才能进行该项操作!\n您要登录吗？") == true) {
            window.location.href = get_login_url({
                "equip_id": $("equipid") ? $("equipid").value : '',
                "return_url": window.location.href
            });
            return false;
        }
        return false;
    }
    window.add_collect_remind_price = add_collect_remind_price;
    window.add_to_favorites = add_to_favorites;
    window.del_from_favorites = del_from_favorites;
    window.login_to_collect = login_to_collect;
    window.is_collect_no_counted = isCollectNoCounted;
}
)();
function get_descendant_kinds(kind_data, parent_kindid) {
    var kindid = kind_data[0][0];
    var children = kind_data[1];
    var all_child_kinds = [];
    if (children.length == 0 && kindid == parent_kindid) {
        all_child_kinds = [kind_data];
    }
    for (var i = 0; i < children.length; i++) {
        if (kindid == parent_kindid) {
            tmp_parent_kindid = children[i][0][0];
        } else {
            tmp_parent_kindid = parent_kindid
        }
        var child = children[i];
        var child_kinds = get_descendant_kinds(child, tmp_parent_kindid);
        all_child_kinds.extend(child_kinds);
    }
    return all_child_kinds;
}
function get_descendant_kindids(kind_data, parent_kindid) {
    var children = get_descendant_kinds(kind_data, parent_kindid);
    var kindids = [];
    for (var i = 0; i < children.length; i++) {
        var child = children[i];
        kindids.push(child[0][0]);
    }
    return kindids;
}
function fen2yuan(fen) {
    return (fen / 100).toFixed(2);
}
function fen2yuan_float(fen) {
    return fen / 100;
}
function yuan2fen(yuan) {
    return Math.round(parseFloat(yuan) * 100);
}
function safe_json_decode(json) {
    try {
        return JSON.decode(json);
    } catch (e) {
        return null;
    }
}
var AlertDialog = new Class({
    defaultOptions: {
        width: 570,
        confirmText: "确认",
        cancelText: "取消",
        onConfirm: null
    },
    initialize: function(title, content, options) {
        this.options = Object.merge(Object.clone(this.defaultOptions), options);
        this.options.title = title;
        this.options.content = content;
        this.dialog = null;
        this.popup = null;
    },
    getTemplate: function() {
        var tmpl = ['<div class="cont noIndent">', this.options.title ? '<h3 class="cDYellow f14px fB textCenter">' + this.options.title + '</h3>' : '', this.options.content, '<div class="textCenter" style="border-top:1px solid #ccc; padding:15px; text-align:center; margin-top:10px;">', '<input type="button" class="btn1 dialog_btn_confirm" value="' + this.options.confirmText + '" />', '&nbsp;&nbsp;', '<input type="button" class="btn1 dialog_btn_cancel" value="' + this.options.cancelText + '" />', '</div>', '</div>'];
        return tmpl.join('');
    },
    getDialog: function() {
        if (!this.dialog) {
            var id = 'util_alert_dialog';
            var dialog = $(id);
            if (!dialog) {
                dialog = new Element("div",{
                    "class": "popupWin",
                    "id": id
                });
                dialog.setStyle('width', '350px');
                dialog.inject(document.body);
            }
            this.dialog = dialog;
        }
        this.dialog.setStyle('width', this.options.width + 'px');
        return this.dialog;
    },
    getPopup: function() {
        if (!this.popup) {
            this.popup = new Popup(this.getDialog());
        }
        return this.popup;
    },
    show: function() {
        var dialog = this.getDialog();
        dialog.set("html", this.getTemplate());
        var that = this;
        dialog.getElement(".dialog_btn_confirm").addEvent("click", function() {
            that.hide();
            if (that.options.onConfirm) {
                that.options.onConfirm();
            }
        });
        dialog.getElement(".dialog_btn_cancel").addEvent("click", function() {
            that.hide();
        });
        this.getPopup().show();
    },
    hide: function() {
        this.getPopup().hide();
    }
});
var ToastTip = new Class({
    initialize: function(text, options) {
        this.options = Object.merge({
            autoDestroy: false
        }, options || {});
        this.text = text.trim().replace(/\n/g, '<br>');
    },
    getTipDialog: function() {
        if (!this.dialog) {
            var id = 'toast_tip_dialog';
            var dialog = $(id);
            if (!dialog) {
                dialog = new Element('div',{
                    'class': 'ToastTip',
                    'id': id
                });
                dialog.inject(document.body);
            }
            this.dialog = dialog;
        }
        return this.dialog;
    },
    show: function() {
        var dialog = this.getTipDialog();
        dialog.set({
            'style': 'visibility:hidden',
            'html': this.text
        });
        dialog.setStyles({
            'visibility': '',
            'right': '50%',
            'margin-top': -dialog.clientHeight / 2,
            'margin-right': -dialog.clientWidth / 2
        });
        var millisec = 3000;
        if (this.text.length > 20) {
            millisec = Math.max(5000, this.text.length * 100)
        }
        clearTimeout(ToastTip.timer);
        ToastTip.timer = setTimeout(this.hide.bind(this), millisec);
    },
    hide: function() {
        this.getTipDialog().setStyle('display', 'none');
        if (this.options.autoDestroy) {
            this.getTipDialog().destroy();
        }
    }
});
var FloatTip = new Class({
    initialize: function($root, options) {
        var ctx = this;
        ctx.$target = $($root);
        ctx.$root = new Element('div',{
            'class': 'page-tips-float'
        });
        ctx.options = options = Object.merge({
            resize: false,
            autoFixTime: 0,
            icon: true,
            appendTo: 'body',
            dir: 'bottom',
            x: 0,
            y: 0
        }, options || {});
        ctx.fixTimer = null;
        if (options.appendTo) {
            $$(options.appendTo).grab(ctx.$root);
        }
        var cls = options.cls;
        if (cls) {
            ctx.$root.addClass(cls);
        }
        if (!options.icon) {
            ctx.$root.addClass('page-tips-float-no-icon');
        }
    },
    update: function($target) {
        this.$target = $target;
        return this;
    },
    fixPosition: function(dir, x, y) {
        var ctx = this
          , options = ctx.options;
        dir = dir || options.dir;
        x = x || options.x;
        y = y || options.y;
        var $root = ctx.$root
          , $target = ctx.$target;
        var targetInfo = $target.getCoordinates();
        var rootInfo = $root.getCoordinates();
        if (x == 'auto' && (dir == 'top' || dir == 'bottom')) {
            x = (targetInfo.width - rootInfo.width) / 2;
        }
        if (y == 'auto' && (dir == 'left' || dir == 'right')) {
            y = (targetInfo.height - rootInfo.height) / 2;
        }
        'top,left,bottom,right'.split(',').each(function(d) {
            $root.removeClass('page-tips-float-' + d);
        });
        $root.addClass('page-tips-float-' + dir);
        var styles = {};
        switch (dir) {
        case 'left':
            styles = {
                left: targetInfo.left - rootInfo.width + x,
                top: targetInfo.top + y
            };
            break;
        case 'right':
            styles = {
                left: targetInfo.left + targetInfo.width + x,
                top: targetInfo.top + y
            };
            break;
        case 'top':
            styles = {
                left: targetInfo.left + x,
                top: targetInfo.top - rootInfo.height + y
            };
            break;
        default:
            styles = {
                left: targetInfo.left + x,
                top: targetInfo.top + targetInfo.height + y
            };
        }
        var winSize = window.getScrollSize();
        if (rootInfo.width + styles.left >= winSize.x) {
            if (dir == 'bottom' || dir == 'top') {
                styles.left = winSize.x - rootInfo.width - 10;
            } else if (dir == 'right') {
                dir = 'left';
                return dir != options.dir && this.fixPosition(dir, -x, y);
            }
        } else if (dir == 'left' && styles.left < 0) {
            dir = 'right';
            return dir != options.dir && this.fixPosition(dir, -x, y);
        } else if (options.appendTo == 'body') {
            if (dir == 'top' && styles.top < 0) {
                dir = 'bottom';
                return this.fixPosition(dir, x, -y);
            }
        }
        if ($root.getStyle('width') === 'auto') {
            var currentWidth = rootInfo.width - parseInt($root.getStyle('padding-left')) - parseInt($root.getStyle('padding-right')) - parseInt($root.getStyle('border-left')) - parseInt($root.getStyle('border-right'));
            styles.width = currentWidth + 'px';
        }
        $root.setStyles(styles);
        var $coner = $root.getElement('.page-tips-float-coner');
        if ($coner) {
            styles = {};
            rootInfo = $root.getCoordinates();
            var conerSize = $coner.getSize();
            var width = conerSize.x
              , height = conerSize.y;
            switch (dir) {
            case 'left':
                styles = {
                    left: rootInfo.width - 2,
                    top: Math.max(targetInfo.top - rootInfo.top + targetInfo.height / 2 - height / 2, 0)
                };
                break;
            case 'right':
                styles = {
                    left: -width,
                    top: Math.max(targetInfo.top - rootInfo.top + targetInfo.height / 2 - height / 2, 0)
                };
                break;
            case 'top':
                styles = {
                    bottom: -height,
                    left: Math.max(targetInfo.left - rootInfo.left + targetInfo.width / 2 - width / 2, 0)
                };
                break;
            default:
                styles = {
                    top: -height,
                    left: Math.max(targetInfo.left - rootInfo.left + targetInfo.width / 2 - width / 2, 0)
                };
            }
            $coner.setStyles(styles);
        }
        clearTimeout(ctx.fixTimer);
        if (options.resize) {
            if (!ctx._fnResize) {
                ctx._fnResize = ctx.fixPosition.bind(ctx);
                window.addEvent('resize', ctx._fnResize);
            }
        } else if (options.autoFixTime > 0) {
            ctx.fixTimer = setTimeout(ctx.fixPosition.bind(ctx), options.autoFixTime);
        }
    },
    show: function(html) {
        var ctx = this
          , $root = ctx.$root;
        $root.setStyles({
            visibility: 'visible',
            width: 'auto'
        }).set('html', '<i class="page-tips-float-coner"></i>' + html);
        ctx.fixPosition();
        var $closes = $root.getElements('.js-close');
        var fn = function(e) {
            ctx.hide();
            $closes.removeEvent('click', fn);
        };
        $closes.addEvent('click', fn);
        $root.fireEvent('show');
        return $root;
    },
    hide: function(isDestroy) {
        var ctx = this
          , $root = ctx.$root;
        clearTimeout(ctx.fixTimer);
        if (ctx._fnResize) {
            window.removeEvent('resize', ctx._fnResize);
            ctx._fnResize = null;
        }
        isDestroy = isDestroy === void 0 ? true : isDestroy;
        $root.setStyles({
            visibility: 'hidden',
            top: 0,
            left: 0
        });
        $root.fireEvent('hide');
        isDestroy && $root.dispose();
        return $root;
    }
});
var StoreDB = (function() {
    var hasStorage = false;
    var storage = window.localStorage;
    if (storage) {
        try {
            var key = '__test__'
              , oldValue = storage.getItem(key);
            storage.setItem(key, 1);
            storage.getItem(key);
            storage.removeItem(key);
            if (oldValue !== null) {
                storage.setItem(key, oldValue);
            }
            hasStorage = true;
        } catch (e) {}
    }
    if (!hasStorage) {
        var IELocalStorageType = new Class({
            initialize: function() {
                var tagid = 'local_data_tag';
                this.dataTag = $(tagid);
                if (!this.dataTag) {
                    this.dataTag = new Element('div',{
                        id: tagid,
                        styles: {
                            display: 'none',
                            behavior: 'url(#default#userData)'
                        }
                    });
                    var dataTag = this.dataTag;
                    window.addEvent('domready', function() {
                        var $body = $(document.body || document.getElementsByTagName('body')[0]);
                        $body.grabBottom(dataTag);
                    });
                }
                this.filename = 'oXMLUserData';
            },
            getItem: function(key) {
                this.dataTag.load(this.filename);
                return this.dataTag.getAttribute(key);
            },
            setItem: function(key, value) {
                this.dataTag.setAttribute(key, value);
                this.dataTag.save(this.filename);
            },
            removeItem: function(key) {
                this.dataTag.removeAttribute(key);
                this.dataTag.save(this.filename);
            }
        });
        storage = new IELocalStorageType();
        try {
            var key = '__test__'
              , oldValue = storage.getItem(key);
            storage.setItem(key, 1);
            storage.getItem(key);
            storage.removeItem(key);
            if (oldValue != null) {
                storage.setItem(key, oldValue);
            }
            hasStorage = true;
        } catch (e) {}
    }
    if (!hasStorage) {
        storage = {
            getItem: function(key) {
                return Cookie.read(key);
            },
            setItem: function(key, val) {
                return Cookie.write(key, val, {
                    duration: 180
                });
            },
            removeItem: function(key) {
                Cookie.dispose(key);
            }
        }
    }
    return {
        getItem: function(key) {
            var value = storage.getItem(key);
            return value;
        },
        setItem: function(key, val) {
            storage.setItem(key, val);
        },
        removeItem: function(key) {
            storage.removeItem(key);
        }
    };
}
)();
var SessionDB = (function() {
    var flag = '__session__';
    var skey = 'session_keys';
    var storage = StoreDB;
    var getSessionKeys = function() {
        var keys = storage.getItem(skey);
        if (keys) {
            keys = keys.split(';');
        } else {
            keys = [];
        }
        return keys;
    };
    if (!Cookie.read(flag)) {
        Cookie.write(flag, 1);
        var sessionKeys = getSessionKeys();
        for (var i = sessionKeys.length; i--; ) {
            storage.removeItem(sessionKeys[i]);
        }
        storage.removeItem(skey);
    }
    return {
        setItem: function(key, value) {
            try {
                var key = flag + key;
                var sessionKeys = getSessionKeys();
                if (!sessionKeys.contains(key)) {
                    sessionKeys.push(key);
                    storage.setItem(skey, sessionKeys.join(';'));
                }
                storage.setItem(key, value);
            } catch (e) {}
        },
        getItem: function(key) {
            var value;
            try {
                value = storage.getItem(flag + key);
            } catch (e) {}
            return value;
        },
        removeItem: function(key) {
            try {
                storage.removeItem(flag + key);
            } catch (e) {}
        }
    };
}
)();
var WebGuide = {
    list: [],
    add: function(item) {
        this.list.push(item);
    },
    clear: function() {
        this.list = [];
    },
    next: function() {
        var item = this.list.shift();
        item && item.run();
    }
};
var InputLimit = {
    _limit: function($input, selector, fnIsPass, options) {
        options = options || {};
        var min = options.min
          , max = options.max;
        var lastValue = '';
        var keydown = function(e) {
            var value = this.value;
            if (fnIsPass(value, e) == true) {
                lastValue = value;
            }
        };
        var keyup = function(e) {
            var value = this.value;
            if (fnIsPass(value, e) == false) {
                this.value = lastValue;
            }
            if (min != null && this.value < min) {
                this.value = min + '';
            } else if (max != null && this.value > max) {
                this.value = max + '';
            }
            this.value = this.value.trim();
        };
        if (selector) {
            var $root = $input;
            $root.addEvent('keydown:relay(' + selector + ')', keydown).addEvent('keyup:relay(' + selector + ')', keyup);
        } else {
            $input.addEvent('keydown', keydown).addEvent('keyup', keyup);
        }
    },
    onlyNumber: function($input, selector, options) {
        options = Object.merge({
            decimals: null
        }, options || {});
        this._limit($input, selector, function isPass(value) {
            if (options.decimals == null) {
                var numb = Number(value);
                return isNaN(numb) == false;
            } else {
                return !value || (new RegExp('^\\d+(\\.\\d{0,' + options.decimals + '})?$')).test(value);
            }
        }, options);
    },
    onlyInt: function($input, selector, options) {
        this._limit($input, selector, function isPass(value) {
            return /^\d*$/.test(value);
        }, options);
    }
};
function desc_4_mhb(amount) {
    if (amount < 1000000)
        return '';
    msg = '';
    ten_million = parseInt(amount / 10000000) % 10;
    if (ten_million > 0)
        msg += ten_million + '千';
    million = parseInt(amount / 1000000) % 10;
    if (million > 0)
        msg += million + '百';
    if (!ten_million) {
        hundred_thousand = parseInt(amount / 100000) % 10;
        if (hundred_thousand > 0)
            msg += hundred_thousand + '十';
    }
    return '约' + msg + '万';
}
function submit_by_form(options) {
    options = Object.merge({
        method: 'post',
        url: '/',
        data: {}
    }, options || {});
    var data = options.data;
    var form = document.createElement('form');
    var method = options.method.toLowerCase();
    form.setAttribute('method', method);
    form.setAttribute('action', options.url);
    options.target && form.setAttribute('target', options.target);
    Object.each(data, function(value, key) {
        var input = document.createElement('input');
        input.setAttribute('id', key);
        input.setAttribute('name', key);
        input.value = value;
        form.appendChild(input);
    });
    form.style.display = 'none';
    document.getElementsByTagName('body')[0].appendChild(form);
    form.submit();
}
function has_any_game_test_server(serverids) {
    for (var i = 0; i < serverids.length; i++) {
        if (test_server_list.contains(serverids[i])) {
            return true;
        }
    }
    return false;
}
function init_ne_captcha(args, onFailure) {
    args = args || [];
    function init() {
        var params = Object.merge({
            captchaId: 'e8079a8b61ab419e97693235b68a33f9',
            width: '320px'
        }, args[0] || {});
        var fnInit = args[1] || function() {}
        ;
        var fnFailure = args[2] || function() {}
        ;
        initNECaptcha(params, fnInit, fnFailure);
    }
    if (!window.initNECaptcha) {
        Asset.javascript('//cstaticdun.126.net/load.min.js', {
            onLoad: function() {
                if (window.initNECaptcha) {
                    init();
                } else {
                    onFailure && onFailure();
                }
            }
        });
    } else {
        init();
    }
}
var AjaxGuard = (function() {
    var Guard = new Class({
        initialize: function(opts) {
            var href = location.href;
            opts = opts || {};
            this.key_status = opts.key_status || 'status';
            delete opts.key_status;
            this.code = Object.merge({
                simple_captcha: null,
                captcha: null,
                login: null,
                mibao: null,
                otp: null
            }, opts.code || {});
            delete opts.code;
            this.code_params = Object.merge({}, opts.code_params || {});
            delete opts.code_params;
            this.defaultParams = Object.merge({
                return_url: location.href,
                onSuccess: function() {}
            }, opts);
        },
        _getParams: function(key) {
            var return_url = this.defaultParams.return_url;
            var defaults = ({
                login: {
                    url: window.ServerInfo && ServerInfo.server_id ? get_login_url({
                        return_url: return_url
                    }) : function() {
                        Cookie.write('login_return_url', return_url, {
                            path: '/'
                        });
                        return '/';
                    }
                },
                mibao: {
                    url: CgiRootUrl + '/login.py?act=show_mbauth'
                }
            })[key] || {};
            return Object.merge(defaults, this.defaultParams, this.code_params[key] || {});
        },
        isPass: function(result) {
            result = result || {};
            var status = result[this.key_status];
            var keys = Object.keys(this.code);
            for (var i = 0, max = keys.length; i < max; i++) {
                var key = keys[i];
                if (!Guard['show_' + key]) {
                    console.error('AjaxGuard.show_' + key + '() 没有定义');
                }
            }
            for (var i = 0, max = keys.length; i < max; i++) {
                var key = keys[i];
                var code = this.code[key];
                if (code != null && code == status) {
                    Guard['show_' + key](this._getParams(key));
                    return false;
                }
            }
            return true;
        }
    });
    Guard.show_captcha = function(opts) {
        opts = Object.merge({
            onSuccess: null,
            successStatus: 1,
            url: CgiRootUrl + '/login.py',
            act: 'ajax_do_netease_captcha_auth'
        }, opts || {});
        var neCaptcha = null;
        var popup = PopupDialog.alert({
            title: '请完成安全验证',
            buttonText: '',
            content: '<div style="width: 320px;">\
				<div id="ajax_guard_ne_captcha" class="textCenter" style="width: 320px;">验证组件初始中...</div>\
				<div class="blank10"></div>\
				<div class="js_guard_tip textCenter cRed hidden">验证通过</div>\
			</div>'
        });
        function ajax(captcha_validate) {
            var args = {
                act: opts.act,
                version: 'v3',
                client_type: 'web',
                captcha_validate: captcha_validate
            };
            var url = opts.url;
            var fnError = function() {
                alert('系统繁忙，请稍候再试');
                neCaptcha && neCaptcha.refresh();
            };
            var Ajax = new Request.JSON({
                url: url,
                onSuccess: function(result) {
                    if (result.status == opts.successStatus) {
                        var $dialog = popup.dialog;
                        $dialog.getElement('.js_guard_tip').removeClass('hidden');
                        setTimeout(function() {
                            popup.hide();
                            opts.onSuccess && opts.onSuccess();
                        }, 1000);
                    } else {
                        alert(result.msg);
                        neCaptcha && neCaptcha.refresh();
                    }
                },
                onError: fnError,
                onFailure: fnError
            }).post(args);
        }
        function errorHandler() {
            alert("网络异常，请刷新页面重试");
        }
        init_ne_captcha([{
            mode: 'embed',
            element: '#ajax_guard_ne_captcha',
            onReady: function() {},
            onVerify: function(err, data) {
                if (data && data.validate && data.validate.length > 0) {
                    ajax(data.validate);
                }
            }
        }, function(instance) {
            neCaptcha = instance;
        }
        , errorHandler], errorHandler);
    }
    ;
    Guard.show_simple_captcha = function(opts) {
        Guard.show_captcha(Object.merge({
            successStatus: 0,
            act: 'check_search_cpatcha',
            url: CgiRootUrl + '/equipquery.py'
        }, opts || {}));
    }
    ;
    Guard.show_login = function(opts) {
        opts = Object.merge({
            url: '/'
        }, opts || {});
        PopupDialog.alert({
            content: '<div>请登录后，再进行操作</div>',
            buttons: [{
                text: '去登录',
                onclick: function() {
                    window.location.href = get_url_str(opts.url);
                }
            }]
        });
    }
    ;
    Guard.show_mibao = function(opts) {
        opts = Object.merge({
            url: CgiRootUrl + '/login.py?act=show_mbauth',
            return_url: location.href
        }, opts || {});
        PopupDialog.alert({
            content: '<div>请密保验证后，再进行操作</div>',
            buttons: [{
                text: '去验证',
                onclick: function() {
                    var cookieOpts = {
                        path: '/cgi-bin'
                    };
                    Cookie.dispose('return_url');
                    Cookie.dispose('return_url', cookieOpts);
                    Cookie.write('return_url', get_url_str(opts.return_url), cookieOpts);
                    window.location.href = get_url_str(opts.url);
                }
            }]
        });
    }
    ;
    Guard.show_otp = function() {
        PopupDialog.alert({
            buttonText: '',
            content: '<div>\
				为了您的账号安全，请绑定将军令之后继续访问\
				<br />\
				<a class="cDGray" href="https://mkey.163.com/download/?from=cbg-xyq" target="_blank"><span class="title">点击绑定手机将军令&gt;&gt;</span></a>\
			</div>'
        });
    }
    ;
    function get_url_str(url) {
        if (typeof url === 'function') {
            url = url();
        }
        return url;
    }
    Guard.get_url_str = get_url_str;
    return Guard;
}
)();
var MobileAdm = {
    E: new Class({
        Implements: Events
    }),
    ajax: function(method, url, data, opts) {
        var res = new this.E();
        function warn() {
            res.fireEvent('error', [].slice.call(arguments, 0));
        }
        var req = new Request.JSON(Object.merge({
            url: url,
            method: method,
            noCache: true,
            onSuccess: function(data) {
                res.fireEvent('success', [data]);
            },
            onError: warn,
            onFailure: warn
        }, opts || {}));
        req.send(data || {});
        res.ajax = req;
        return res;
    },
    valid: function(opts, autoBindOpts) {
        var ctx = this;
        var res = new ctx.E();
        opts = Object.merge({
            url: '',
            autoBind: true,
            validAction: function(result, done) {
                var unknow = '未知错误';
                if (!result) {
                    done({
                        error: unknow
                    });
                } else {
                    if (result.status == AjaxConstants.Ok) {
                        if (result.mobile) {
                            done({
                                value: result
                            });
                        } else {
                            done({
                                nobind: true
                            });
                        }
                    } else {
                        done({
                            error: result.msg || unknow
                        });
                    }
                }
                return result && result.status == AjaxConstants.Ok && result.mobile;
            },
            autoBindOpts: {}
        }, opts || {});
        if (!opts.url) {
            throw new Error('should set "url"');
        }
        function nobind() {
            if (opts.autoBind) {
                autoBindOpts = autoBindOpts || {};
                ctx.showBindDialog(autoBindOpts, opts).addEvent('bind', function(data) {
                    res.fireEvent('bind', [data]);
                }).addEvent('nobind', function() {
                    res.fireEvent('nobind');
                }).addEvent('error', function(msg) {
                    res.fireEvent('error', [msg]);
                });
            } else {
                res.fireEvent('nobind');
            }
        }
        res.ajax = ctx.ajax('get', opts.url);
        res.ajax.addEvent('success', function(result) {
            opts.validAction(result, function(obj) {
                if (obj.nobind) {
                    nobind();
                } else if (obj.error) {
                    res.fireEvent('error', [obj.error]);
                } else {
                    res.fireEvent('bind', [obj.value, result]);
                }
            });
        }).addEvent('error', function() {
            res.fireEvent('error', ['访问出错']);
        });
        return res;
    },
    showBindDialog: function(opts, validOpts) {
        opts = Object.merge({
            closeAsNoBind: true,
            bindAction: function() {
                window.open('https://epay.163.com/servlet/controller?operation=activateAccount');
            },
            updateText: '<div class="textCenter">为了保障您的资金安全<br/>请绑定一张银行卡<div style="padding-top: 12px;">绑定后即可使用钱包余额继续支付</div></div>',
            bindText: '<div class="textCenter">已完成网易支付手机的绑定<br>并继续支付验证？</div>',
            validAction: null
        }, opts || {});
        var ctx = this;
        var res = new ctx.E();
        var width = 320;
        var evtNobind = 'nobind';
        var evtGiveup = 'giveup';
        if (opts.closeAsNoBind) {
            evtGiveup = evtNobind;
        }
        var dialog1 = PopupDialog.alert({
            title: '升级提示',
            content: '<div style="width:' + width + 'px;">' + opts.updateText + '</div>',
            buttons: [{
                text: '立即绑定',
                event: 'sure',
                close: 1
            }],
            needClose: true
        });
        dialog1.addEvent('sure', function() {
            opts.bindAction();
            var dialog2 = PopupDialog.alert({
                title: '升级提示',
                content: '<div  style="width:' + width + 'px;">' + opts.bindText + '</div>',
                buttons: [{
                    text: '已绑定并继续支付',
                    event: 'sure',
                    close: 1
                }],
                needClose: true
            });
            dialog2.addEvent('sure', function() {
                var validAction = opts.validAction || function(done) {
                    validOpts = validOpts || {};
                    validOpts.autoBind = false;
                    ctx.valid(validOpts, opts).addEvent('bind', function(data) {
                        done({
                            value: data
                        });
                    }).addEvent('nobind', function() {
                        done({
                            nobind: true
                        });
                    }).addEvent('error', function(msg) {
                        done({
                            error: msg
                        });
                    });
                }
                ;
                validAction(function(obj) {
                    obj = obj || {};
                    if (obj.error) {
                        res.fireEvent('error', [obj.error]);
                    } else if (obj.nobind) {
                        res.fireEvent(evtNobind);
                    } else {
                        res.fireEvent('bind', [obj.value]);
                    }
                });
            }).addEvent('close', function() {
                res.fireEvent(evtGiveup);
            });
        }).addEvent('close', function() {
            res.fireEvent(evtGiveup);
        });
        return res;
    },
    smsCode: function(opts) {
        opts = Object.merge({
            mobile: '',
            getSmsCode: function(done) {
                done({
                    error: '请设置 getSmsCode 参数'
                });
            },
            countdown: 60,
            showBtmTip: true,
            btmTip: ''
        }, opts || {});
        var html = ['<div style="padding:24px 64px;">', '<p style="margin:6px 0;">验证码将发送至您的网易支付手机：<span style="color:#3366CC;">', opts.mobile, '</span></p>', '<p style="white-space:nowrap;">', '<input class="j_input_sms_code txt1" type="text" placeholder="请输入短信验证码" /> ', '<input class="txt1 j_sms_btn" type="button" value="获取验证码" style="min-width:100px;text-align:center;color:#333;background:#efefef;" data-event="get_sms_code"/>', '</p>', '<p class="cRed j_error_tip" style="margin:6px 0;white-space:nowrap;">&nbsp;</p>', '<p class="textCenter">', '<a class="btn1" data-event="confirm">确认支付</a>', '</p>', '</div>'];
        if (opts.showBtmTip) {
            html = html.concat(['<div class="divider" style="margin:0 10px;"></div>', '<div style="margin:10px;line-height:1.5;" class="cDGray">', (opts.btmTip || '更换手机号请前往 <a href="https://epay.163.com/accountmobile/replace_mobile_choose.htm" target="_blank">网易支付&gt;</a>'), '</div>']);
        }
        var popup = new PopupDialog('手机安全验证',html.join(''));
        popup.show();
        var $root = popup.dialog;
        var res = new this.E();
        var $err = $root.getElement('.j_error_tip');
        function setError(err) {
            $err && $err.set('html', err || '&nbsp;');
        }
        var $btn = $root.getElement('.j_sms_btn');
        var btnColor = $btn.getStyle('color');
        var btnTimer = null;
        function startCountdown() {
            var index = opts.countdown;
            var clear = function() {
                clearInterval(btnTimer);
                btnTimer = null;
                $btn.setStyle('color', btnColor);
            };
            var check = function() {
                if (index > 0) {
                    $btn.set('value', index + '秒后重新发送');
                    index--;
                } else {
                    $btn.set('value', '重新发送');
                    clear();
                }
            };
            clear();
            btnTimer = setInterval(function() {
                check();
            }, 1000);
            $btn.setStyle('color', '#999');
            check();
        }
        var isGettingCode = false;
        popup.addEvent('get_sms_code', function() {
            if (isGettingCode || btnTimer) {
                return;
            }
            isGettingCode = true;
            setError('');
            opts.getSmsCode(function(obj) {
                isGettingCode = false;
                obj = obj || {};
                if (obj.error) {
                    setError(obj.error);
                } else {
                    startCountdown();
                }
            });
        });
        var $input = $root.getElement('.j_input_sms_code');
        $input.addEvent('keyup', function(e) {
            if ((event.key || '').toLowerCase() == 'enter') {
                popup.fireEvent('get_sms_code', [e]);
            }
        });
        popup.addEvent('confirm', function() {
            var code = $input.get('value');
            setError('');
            if (code) {
                res.fireEvent('code', [code, popup, setError]);
            } else {
                setError('请输入验证码');
            }
        });
        popup.addEvent('close', function() {
            res.fireEvent('giveup');
        });
        res.popup = popup;
        return res;
    }
};
function getProxyAjax(url, data, options) {
    options = Object.merge({
        method: 'get',
        successStatus: 1
    }, options || {});
    var dispatcher = getDispatcher();
    function warn() {
        dispatcher.fireEvent('complete');
        dispatcher.fireEvent('failure', {
            error: '访问出错'
        });
    }
    var ajax = new Request.JSON({
        url: url,
        noCache: true,
        onSuccess: function(result) {
            dispatcher.fireEvent('complete', result);
            if (result && result['status'] == options.successStatus) {
                dispatcher.fireEvent('success', result);
            } else {
                dispatcher.fireEvent('failure', {
                    error: result && result['msg'] || '未知错误'
                });
            }
        },
        onError: warn,
        onFailure: warn,
        onTimeout: warn
    });
    ajax[options.method](data || {});
    return {
        dispatcher: dispatcher,
        ajax: ajax
    };
}
function fakeRoleBuyPopup(cb) {
    PopupDialog.alert({
        content: '<div style="width:290px;text-align:center;">少侠当前暂无角色<br/>无法使用此功能<br/>赶快先买个角色吧</div>',
        needClose: true,
        buttons: [{
            text: '我知道了',
            close: true,
            onclick: function() {
                cb && cb();
            }
        }]
    });
}
function addViewLocParams(url, viewLoc, tagKey) {
    if (url && viewLoc) {
        var loc = encodeURIComponent(viewLoc);
        if (tagKey) {
            loc += "|" + encodeURIComponent(tagKey);
        }
        url = addUrlPara('view_loc', loc, url);
    }
    return url;
}
function floatSub(arg1, arg2) {
    var r1, r2, m, n;
    try {
        r1 = arg1.toString().split(".")[1].length;
    } catch (e) {
        r1 = 0;
    }
    try {
        r2 = arg2.toString().split(".")[1].length;
    } catch (e) {
        r2 = 0;
    }
    m = Math.pow(10, Math.max(r1, r2));
    n = (r1 >= r2) ? r1 : r2;
    return Number(((arg1 * m - arg2 * m) / m).toFixed(n));
}
function changeArrayToObject(array) {
    var obj = {};
    for (var i = 0, max = array.length; i < max; i++) {
        var item = array[i];
        if (item instanceof Array && item.length > 1) {
            obj[item[0]] = item[1];
        } else {
            obj[item] = item;
        }
    }
    return obj;
}
function changeObjectToArray(obj) {
    var array = [];
    for (var key in obj) {
        if (obj.hasOwnProperty(key)) {
            array.push([key, obj[key]]);
        }
    }
    return array;
}
function reverseObj(obj) {
    var newObj = {};
    for (var key in obj) {
        if (obj.hasOwnProperty(key)) {
            newObj[obj[key]] = key;
        }
    }
    return newObj;
}
function exactAdd(num1, num2) {
    var num1Digits = (num1.toString().split('.')[1] || '').length;
    var num2Digits = (num2.toString().split('.')[1] || '').length;
    var baseNum = Math.pow(10, Math.max(num1Digits, num2Digits));
    return (num1 * baseNum + num2 * baseNum) / baseNum;
}
function changeTimeFomateToRemindTime(timeString) {
    if (!timeString) {
        return '';
    }
    var targetTimeStamp = parseDatetime(timeString);
    var currentTimeStamp = new Date().getTime();
    if (targetTimeStamp >= currentTimeStamp) {
        return get_exact_remain_time_desc(targetTimeStamp - currentTimeStamp, true, false);
    }
    return '';
}

// 将关键函数暴露到全局作用域，供其他模块使用
if (typeof window !== 'undefined') {
    window.js_eval = js_eval;
    window.lpc_2_js = lpc_2_js;
    window.decode_desc = decode_desc;
    window.trim = function(str) {
        if (str) {
            return str.trim ? str.trim() : str.toString().replace(/^\s+|\s+$/g, '');
        }
        return '';
    };
}
