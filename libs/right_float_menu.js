(function() {
    if (window.localStorage) {
        return;
    }
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
                $(document.body).grab(this.dataTag);
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
        }
    });
    window.localStorage = new IELocalStorageType();
}
)();
function add_history_view_item(equipid, equip_name, icon_url, price, storage_key, is_overall_search) {
    var item = {
        "equipid": equipid,
        "equip_name": equip_name,
        "icon_url": icon_url,
        "price": price,
        "eid": (window.EquipInfo && EquipInfo.eid) || (window.equip && equip.eid) || "",
        "serverid": (window.EquipInfo && EquipInfo.server_id) || (window.equip && equip.server_id) || (window.ServerInfo && ServerInfo.server_id)
    };
    if (is_overall_search) {
        item["is_overall_search"] = true;
    } else {
        item["is_overall_search"] = false;
    }
    var latest_equips = window.localStorage.getItem(storage_key);
    if (latest_equips) {
        latest_equips = JSON.decode(latest_equips);
    } else {
        latest_equips = [];
    }
    latest_equips.each(function(e, i) {
        if (e.equipid == item.equipid && e.serverid == item.serverid) {
            latest_equips.erase(e);
        }
    });
    latest_equips.unshift(item);
    while (latest_equips.length > 10) {
        latest_equips.pop();
    }
    try {
        window.localStorage.setItem(storage_key, JSON.encode(latest_equips));
    } catch (e) {}
}
function add_latest_view(equipid, equip_name, icon_url, price) {
    add_history_view_item(equipid, equip_name, icon_url, price, "latest_views", false);
}
function add_latest_view_overall_search(equipid, equip_name, icon_url, price) {
    add_history_view_item(equipid, equip_name, icon_url, price, "latest_overall_search", true);
}
function gen_latest_view(is_overall_search) {
    var panel_el = $("recent_list_panel");
    var latest_equips = '';
    try {
        latest_equips = window.localStorage.getItem(is_overall_search ? "latest_overall_search" : "latest_views");
    } catch (e) {}
    if (latest_equips) {
        latest_equips = JSON.decode(latest_equips);
    } else {
        latest_equips = [];
    }
    latest_equips = latest_equips.filter(function(item) {
        return item.serverid;
    });
    if (latest_equips.length > 0) {
        render_to_replace('recent_list_panel', 'recent_list_templ', {
            "equip_list": latest_equips
        });
    } else {
        render_to_replace('recent_list_panel', 'recent_empty_templ');
    }
}
function init_right_float_download_qrcode() {
    var $toggleBtn = $('right_float_download_app');
    var $qrcodeList = $('qrcode_list');
    if ($toggleBtn && $qrcodeList) {
        var now = new Date();
        year = now.getFullYear(),
        month = now.getMonth() + 1,
        date = now.getDate(),
        today = year + '-' + month + '-' + date,
        isMobile = Browser.Platform.android || Browser.Platform.ios;
        if (StoreDB.getItem('_HAD_SHOW_RIGHT_FLOAT_DOWNLOAD_') != today && !isMobile) {
            $qrcodeList.addClass('show_qrcode');
            $('download_app_wrap').addClass('on');
        }
        $toggleBtn.addEvent('click', function() {
            $qrcodeList.toggleClass('show_qrcode');
            $('download_app_wrap').toggleClass('on');
            StoreDB.setItem('_HAD_SHOW_RIGHT_FLOAT_DOWNLOAD_', today);
        });
    }
}
function init_xyq_qrcode_close() {
    var closeBtn = $('qr_close')
      , qrcodeItem = $('qrcode_list')
      , downloadWrap = $('download_app_wrap');
    var now = new Date().getTime();
    var closeTimeStamp = StoreDB.getItem('_HAD_CLOSE_XYQ_QRCODE_');
    if (closeTimeStamp) {
        var diffHours = (now - closeTimeStamp) / 3600 / 1000;
        if (diffHours > 72) {
            qrcodeItem.addClass('show_qrcode');
            StoreDB.removeItem('_HAD_CLOSE_XYQ_QRCODE_')
        } else {
            qrcodeItem.removeClass('show_qrcode');
            downloadWrap.removeClass('on');
        }
    }
    closeBtn.addEvent('click', function() {
        qrcodeItem.removeClass('show_qrcode');
        downloadWrap.removeClass('on');
        StoreDB.setItem('_HAD_CLOSE_XYQ_QRCODE_', new Date().getTime());
    });
}
