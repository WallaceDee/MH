(function() {
    if (window.RoleNameConf || !window.CBG_GAME_CONFIG) {
        return;
    }
    var gConf = window.CBG_GAME_CONFIG;
    function handleEndingInfo(data) {
        if (!data) {
            return;
        }
        for (var key in data) {
            if (data.hasOwnProperty(key) && data[key].indexOf(',') > -1) {
                data[key] = data[key].split(',');
            }
        }
        return data;
    }
    var RoleNameConf = new Class({
        initialize: function() {
            this.skill = {
                "life_skill": gConf.life_skill,
                "school_skill": gConf.school_skill,
                "ju_qing_skill": gConf.ju_qing_skill
            };
            this.rider_info = gConf.rider_info;
            this.equip_info = gConf.equip_info;
            this.pet_info = gConf.pet_info;
            this.fabao_info = gConf.fabao_info;
            this.lingbao_info = gConf.lingbao_info;
            this.pet_shipin_info = gConf.pet_shipin_info;
            this.shenqi_info = gConf.shenqi_info;
            this.wuxing_affix_info = gConf.wuxing_affix_info;
            this.girl_child_info = gConf.girl_child_info;
            this.boy_child_info = gConf.boy_child_info;
            this.child_info = Object.merge(Object.clone(this.girl_child_info), Object.clone(this.boy_child_info));
            this.fangwu_info = gConf.fangwu_info;
            this.tingyuan_info = gConf.tingyuan_info;
            this.muchang_info = gConf.muchang_info;
            this.ending_info = handleEndingInfo(gConf.ending_info);
            this.clothes_info = gConf.clothes_info;
            this.xiangrui_info = gConf.xiangrui_info;
            this.xiangrui_skill = gConf.xiangrui_skill;
            this.clothes_type_conf = gConf.clothes_type_conf;
            this.nosale_xiangrui = gConf.nosale_xiangrui;
            this.nosale_to_sale_xiangrui = {
                113: "流云玉佩",
                219: "烈焰斗猪"
            };
        },
        get_fabao_info: function(typeid) {
            var info = this.fabao_info[parseInt(typeid)];
            var result = {
                "name": "",
                "desc": ""
            };
            if (info) {
                result["name"] = info["name"];
                result["desc"] = info["desc"];
            }
            return result;
        },
        get_lingbao_info: function(typeid) {
            var info = this.lingbao_info[parseInt(typeid)];
            var result = {
                "name": "",
                "desc": ""
            };
            if (info) {
                result["name"] = info["name"];
                result["desc"] = info["desc"];
            }
            return result;
        },
        get_shenqi_info: function(shenqiID) {
            var info = this.shenqi_info[parseInt(shenqiID)];
            var result = {
                "name": "",
                "desc": ""
            };
            if (info) {
                result["name"] = info["name"];
                result["desc"] = info["desc"];
            }
            return result;
        },
        get_equip_info: function(typeid) {
            var info = this.equip_info[parseInt(typeid)];
            var result = {
                "name": "",
                "desc": ""
            };
            if (info) {
                result["name"] = info["name"];
                result["desc"] = info["desc"];
            }
            return result;
        }
    });
    window.RoleNameConf = RoleNameConf;
    window.RoleNameInfo = new RoleNameConf();
}
)();
