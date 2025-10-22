function correct_pet_desc(pet_desc) {
    var num_re = /^[0-9]*$/;
    var PetAttrNum = 33;
    var OldAttrNum = 30;
    var OldestAttrNum = 29;
    var AttrNum = pet_desc.split(";").length;
    if (AttrNum >= PetAttrNum || AttrNum == OldAttrNum || AttrNum == OldestAttrNum) {
        return pet_desc;
    }
    var sep_num = 0;
    var check_num = PetAttrNum - 1 - 1;
    var new_desc = ""
    for (var i = pet_desc.length - 1; i > 0; i--) {
        var ch = pet_desc.charAt(i);
        if (ch != ";" && ch != "|" && !num_re.test(ch)) {
            break;
        } else {
            new_desc = ch + new_desc;
        }
    }
    if (new_desc.charAt(0) != ";") {
        new_desc = ";" + new_desc;
    }
    return "-" + new_desc;
}
var check_undefined = function(item_value) {
    if (item_value == undefined) {
        return "未知";
    } else {
        return item_value;
    }
};
function get_yuanxiao(input_value) {
    if (!input_value) {
        return check_undefined(input_value);
    }
    var agent_time = parseDatetime(EquipRequestTime);
    var cur_time = parseDatetime(ServerCurrentTime);
    var fresh_time = new Date(cur_time.getFullYear(),0,1);
    if (agent_time > fresh_time) {
        return input_value;
    } else {
        return 0;
    }
}
var get_sjg = get_yuanxiao;
function get_lianshou(input_value) {
    if (!input_value) {
        return check_undefined(input_value);
    }
    var agent_time = parseDatetime(EquipRequestTime);
    var cur_time = parseDatetime(ServerCurrentTime);
    var fresh_time = new Date(cur_time.getFullYear(),8,1);
    if (cur_time < fresh_time) {
        fresh_time.setFullYear(fresh_time.getFullYear() - 1);
    }
    if (agent_time > fresh_time) {
        return input_value;
    } else {
        return 0;
    }
}
function get_pet_attrs_info(pet_desc, options) {
    var pet_desc = correct_pet_desc(pet_desc);
    var attrs = pet_desc.split(";");
    var options = options || {};
    var fashang = options.fashang;
    var fafang = options.fafang;
    var only_basic_attr = options.only_basic_attr;
    var get_baobao_info = function(is_baobao) {
        if (is_baobao == undefined) {
            return "未知";
        }
        if (parseInt(is_baobao)) {
            return "是";
        } else {
            return "否";
        }
    };
    var attrs_info = {
        pet_name: attrs[0],
        type_id: attrs[1],
        pet_grade: attrs[2],
        blood: attrs[3],
        magic: attrs[4],
        attack: attrs[5],
        defence: attrs[6],
        speed: attrs[7],
        soma: attrs[9],
        magic_powner: attrs[10],
        strength: attrs[11],
        endurance: attrs[12],
        smartness: attrs[13],
        potential: attrs[14],
        wakan: attrs[15],
        max_blood: attrs[16],
        max_magic: attrs[17],
        lifetime: parseInt(attrs[18], 10) >= 65432 ? "永生" : attrs[18],
        five_aptitude: attrs[19],
        attack_aptitude: attrs[20],
        defence_aptitude: attrs[21],
        physical_aptitude: attrs[22],
        magic_aptitude: attrs[23],
        speed_aptitude: attrs[24],
        avoid_aptitude: attrs[25],
        growth: parseInt(attrs[26], 10) / 1000,
        all_skill: attrs[27],
        sp_skill: attrs[28],
        is_baobao: get_baobao_info(attrs[29]),
        used_qianjinlu: check_undefined(attrs[32]),
        other: attrs[34],
        PET_WUXING_INFO: window.PET_WUXING_INFO || {}
    };
    var allSkills = attrs_info.all_skill ? attrs_info.all_skill.split('|') : [];
    window.xs_sort_pet_skills && xs_sort_pet_skills(attrs_info.type_id, allSkills);
    attrs_info.all_skill = allSkills.join('|');
    var spSkillId = (attrs_info.sp_skill || '0').toString().trim();
    if (spSkillId != '0' && (attrs_info.all_skill || '').search(new RegExp('(^|\\|)' + spSkillId + '($|\\|)')) < 0) {
        allSkills.push(spSkillId);
    }
    attrs_info.sp_skill_id = spSkillId;
    attrs_info.all_skills = allSkills;
    var other_attr = {};
    if (attrs_info["other"]) {
        var pos = pet_desc.indexOf(attrs_info["other"]);
        attrs_info["other"] = js_eval(lpc_2_js(pet_desc.substr(pos)));
        other_attr = attrs_info["other"];
    }
    var jjExtraAdd = other_attr["jj_extra_add"];
    if (jjExtraAdd) {
        attrs_info["ti_zhi_add"] = jjExtraAdd["iCor"];
        attrs_info["fa_li_add"] = jjExtraAdd["iMag"];
        attrs_info["li_liang_add"] = jjExtraAdd["iStr"];
        attrs_info["nai_li_add"] = jjExtraAdd["iRes"];
        attrs_info["min_jie_add"] = jjExtraAdd["iSpe"];
        attrs_info['soma'] -= attrs_info["ti_zhi_add"];
        attrs_info['magic_powner'] -= attrs_info["fa_li_add"];
        attrs_info['strength'] -= attrs_info["li_liang_add"];
        attrs_info['endurance'] -= attrs_info["nai_li_add"];
        attrs_info['smartness'] -= attrs_info["min_jie_add"];
    }
    if (other_attr['avt_list'] && other_attr['avt_list'].length) {
        var avtList = other_attr['avt_list'];
        var avt_list_format = [];
        for (var i = 0; i < avtList.length; i++) {
            var item = avtList[i];
            var type = item.type;
            var conf = window.CBG_GAME_CONFIG.pet_jinyi || {};
            if (conf[type]) {
                item.name = conf[type].name;
            }
            if (item.in_use) {
                var sumavt_propsk = other_attr['sumavt_propsk'];
                item.sumavt_propsk = (window.CBG_GAME_CONFIG.sumavt_propsk || {})[sumavt_propsk] ? (window.CBG_GAME_CONFIG.sumavt_propsk || {})[sumavt_propsk].label : '';
            }
            avt_list_format.push(item);
        }
        var current_on_avt = avt_list_format.filter(function(item) {
            return !!item.in_use;
        });
        other_attr['avt_list_format'] = avt_list_format;
        other_attr['current_on_avt'] = current_on_avt[0];
    }
    if (other_attr["core_close"] || other_attr["core_close"] == 0) {
        attrs_info["core_close"] = other_attr.core_close == 0 ? "已开启" : "已关闭";
    }
    if (other_attr.csavezz) {
        get_pet_ext_zz(attrs_info, {
            attrs: 'attack_ext,defence_ext,speed_ext,avoid_ext,physical_ext,magic_ext',
            total_attrs: 'attack_aptitude,defence_aptitude,speed_aptitude,avoid_aptitude,physical_aptitude,magic_aptitude',
            csavezz: other_attr.csavezz,
            carrygradezz: other_attr.carrygradezz,
            lastchecksubzz: other_attr.lastchecksubzz,
            pet_id: attrs[1],
            is_super_sum: other_attr.is_super_sum
        });
    }
    if (attrs_info["other"]) {
        attrs_info["evol_skill_list"] = parse_evol_skill_list(attrs_info["other"], attrs_info);
        attrs_info["equip_list"] = parse_pet_equips(attrs_info["other"]);
        attrs_info["neidan"] = parse_neidan(attrs_info["other"]);
        attrs_info["color"] = attrs_info["other"]["iColor"];
        attrs_info['summon_color'] = attrs_info.other.summon_color;
        attrs_info.iMagDam = attrs_info.other.iMagDam;
        attrs_info.iMagDef = attrs_info.other.iMagDef;
        if (attrs_info.iMagDam == void 0 && attrs_info.iMagDef == void 0) {
            if (fashang && fafang && !isNaN(fashang) && !isNaN(fafang)) {
                attrs_info.iMagDam = fashang;
                attrs_info.iMagDef = fafang;
            }
        }
    } else {
        attrs_info["neidan"] = [];
    }
    var jinjie_info = dict_get(other_attr, "jinjie", {});
    attrs_info['jinjie'] = jinjie_info;
    attrs_info["lx"] = dict_get(jinjie_info, "lx", 0);
    attrs_info["jinjie_cnt"] = dict_get(jinjie_info, "cnt", "0");
    attrs_info["texing"] = dict_get(jinjie_info, "core", {});
    if (only_basic_attr) {
        return attrs_info;
    }
    attrs_info['used_yuanxiao'] = get_yuanxiao(attrs[30]);
    attrs_info['used_lianshou'] = get_lianshou(attrs[33]);
    if (attrs_info["other"]) {
        attrs_info["used_sjg"] = get_sjg(attrs_info["other"]["sjg"]);
    }
    return attrs_info;
}
function get_pet_shipin_icon(typeid) {
    return ResUrl + "/images/pet_shipin/small/" + typeid + ".png";
}
;function parse_evol_skill_list(pet, attrs_info) {
    var evol_skill_list = [];
    if (pet.EvolSkill && window.CBG_GAME_CONFIG.pet_skill_high_to_other_level_mapping) {
        var cifu = pet['EvolSkill'].split("|").map(Number);
        var cifuObj = {};
        cifu.forEach(function(number) {
            cifuObj[number] = 1;
        });
        var evol_skills = cifuObj;
        if (evol_skills) {
            var evol_skill_str = [];
            for (var typeid in evol_skills) {
                evol_skill_str.push('' + typeid);
            }
            for (var i = 0, max = evol_skill_str.length; i < max; i++) {
                var typeid = evol_skill_str[i];
                var evol_skill_hash = window.CBG_GAME_CONFIG.pet_skill_high_to_other_level_mapping[typeid];
                var petSkillUrlEvol = window.PetSkillUrl || window.ResUrl + '/images/skill/';
                var evol_skill_item = {
                    "skill_type": typeid,
                    "level": evol_skills[typeid],
                    "icon": "" + petSkillUrlEvol + fill_format(typeid) + ".gif ",
                    "evol_type": typeid
                }
                if (window.CBG_GAME_CONFIG.pet_skill_desc && window.CBG_GAME_CONFIG.pet_skill_desc[typeid]) {
                    var skillConfig = window.CBG_GAME_CONFIG.pet_skill_desc[typeid];
                    evol_skill_item.name = skillConfig.name;
                    evol_skill_item.desc = skillConfig.desc;
                }
                if (attrs_info['all_skills']) {
                    var isHighSkill = attrs_info['all_skills'].contains(String(evol_skill_hash.high_skill));
                    var isLowSkill = attrs_info['all_skills'].contains(String(evol_skill_hash.low_skill));
                    if (isHighSkill || isLowSkill) {
                        evol_skill_item.hlightLight = true;
                        if (!attrs_info['all_skills'].contains(String(evol_skill_hash.high_skill))) {
                            evol_skill_item.icon = "" + petSkillUrlEvol + fill_format(evol_skill_hash.low_skill) + ".gif ";
                            evol_skill_item.evol_type = evol_skill_hash.low_skill;
                        }
                        if (isHighSkill) {
                            evol_skill_item.name = (evol_skill_hash.name || '') + '（进化后获得）';
                            if (window.CBG_GAME_CONFIG.pet_skill_desc && window.CBG_GAME_CONFIG.pet_skill_desc[String(evol_skill_hash.super_skill)]) {
                                var skillConfig = window.CBG_GAME_CONFIG.pet_skill_desc[String(evol_skill_hash.super_skill)];
                                evol_skill_item.desc = skillConfig.desc || ''
                            }
                            evol_skill_item.cifuIcon = "" + petSkillUrlEvol + fill_format(evol_skill_hash.super_skill) + ".gif ";
                        } else {
                            evol_skill_item.heightCifuIcon = "" + petSkillUrlEvol + fill_format(evol_skill_hash.high_skill) + ".gif ";
                            evol_skill_item.name += '（进化后获得）';
                        }
                    } else {
                        evol_skill_item.cifuIcon = "" + petSkillUrlEvol + fill_format(evol_skill_hash.super_skill) + ".gif ";
                        evol_skill_item.name = (evol_skill_hash.name || '') + '（进化后获得）';
                        if (window.CBG_GAME_CONFIG.pet_skill_desc && window.CBG_GAME_CONFIG.pet_skill_desc[String(evol_skill_hash.super_skill)]) {
                            var skillConfig = window.CBG_GAME_CONFIG.pet_skill_desc[String(evol_skill_hash.super_skill)];
                            evol_skill_item.desc = skillConfig.desc || ''
                        }
                        evol_skill_item.hlightLight = false;
                    }
                }
                evol_skill_list.push(evol_skill_item);
            }
            attrs_info['evol_skills'] = evol_skill_str;
            return evol_skill_list
        }
    } else {
        return null;
    }
}
function parse_pet_equips(pet) {
    var equip_list = [];
    var max_equip_num = 3;
    var img_dir = ResUrl + "/images/equip/small/";
    for (var i = 0; i < max_equip_num; i++) {
        var item = pet["summon_equip" + (i + 1)];
        if (item) {
            var equip_name_info = RoleNameInfo.get_equip_info(item["iType"]);
            equip_list.push({
                "name": equip_name_info["name"],
                "icon": img_dir + item["iType"] + ".gif",
                "type": item["iType"],
                "desc": item["cDesc"],
                "static_desc": equip_name_info["desc"].replace(/#R/g, "<br />")
            });
        } else {
            equip_list.push(null);
        }
    }
    if (pet.summon_equip4_type)
        equip_list.push({
            "name": RoleNameInfo.pet_shipin_info[pet.summon_equip4_type],
            "icon": get_pet_shipin_icon(pet.summon_equip4_type),
            "type": pet.summon_equip4_type,
            "desc": pet.summon_equip4_desc,
            "static_desc": ''
        });
    return equip_list;
}
function parse_neidan(pet) {
    var neidan_list = [];
    var neidan_data = pet.summon_core;
    if (neidan_data != undefined) {
        for (var p in neidan_data) {
            var neidan_info = neidan_data[p];
            var desc = '';
            if (window.CBG_GAME_CONFIG.neidan_desc && window.CBG_GAME_CONFIG.neidan_desc[p]) {
                var skillConfig = window.CBG_GAME_CONFIG.neidan_desc[p];
                desc = skillConfig.desc || '';
            }
            neidan_list.push({
                "name": safe_attr(PetNeidanInfo[p]),
                "icon": ResUrl + "/images/neidan/" + p + ".jpg",
                "level": neidan_info[0],
                "desc": desc,
                "isNeiDan": true
            });
        }
    }
    return neidan_list;
}
function fill_format(num) {
    if (num / 1000 >= 1) {
        return num;
    }
    if (num / 100 >= 1) {
        return "0" + num;
    }
    if (num / 10 >= 1) {
        return "00" + num;
    }
    return "000" + num;
}
function findCorrespondingValue(arr, targetId) {
    for (var i = 0; i < arr.length; i++) {
        var objCorresponding = arr[i];
        if (objCorresponding.hasOwnProperty(targetId)) {
            return objCorresponding[targetId];
        }
    }
    return null;
}
function show_pet_skill_in_grade(pet_skills, sp_skill, row_len, col_len, conf, pet_attrs) {
    var enhanceIds = conf.enhance_skills || [];
    var enhanceMap = {};
    for (var i = 0, max = enhanceIds.length; i < max; i++) {
        enhanceMap[enhanceIds[i]] = i + 1;
    }
    var all_skills = pet_skills.split("|");
    var offset = 0;
    var enhanceSkill = []
      , normalSkill = []
      , specialSkill = null;
    for (var i = 0, max = all_skills.length; i < max; i++) {
        var skill = all_skills[i];
        if (skill == sp_skill) {
            specialSkill = skill;
        } else {
            (enhanceMap[skill] ? enhanceSkill : normalSkill).push(skill);
        }
    }
    enhanceSkill.sort(function(a, b) {
        return enhanceMap[a] - enhanceMap[b];
    });
    if (specialSkill) {
        normalSkill.push(specialSkill);
    }
    all_skills = [].concat(enhanceSkill, normalSkill);

    var makeGrid = function(skills, row_len, withSpSkill) {
        var grid = document.createElement("table");
        grid.cellspacing = 0;
        grid.cellpadding = 0;
        if (conf.table_class) {
            grid.className = conf.table_class;
        }
        var hashEvolSkllAll = [];
        var hashBothEvolSkllAll = [];
        var hashLowEvolSkllAll = [];
        function isSuperSkill(id) {
            var result = false;
            if (CBG_GAME_CONFIG && CBG_GAME_CONFIG.pet_web_super_skill_options) {
                for (var i = 0; i < CBG_GAME_CONFIG.pet_web_super_skill_options.length; i++) {
                    var item = CBG_GAME_CONFIG.pet_web_super_skill_options[i];
                    if (item[0] == id) {
                        result = true;
                        break;
                    }
                }
            }
            return result;
        }
        for (var i = 0; i < row_len; i++) {
            var r = grid.insertRow(i);
            for (var j = 0; j < col_len; j++) {
                var c = r.insertCell(j);
                c.style.position = "relative";
                var s_i = i * col_len + j + offset;
                if (s_i < skills.length && skills[s_i] == sp_skill) {
                    offset++;
                    s_i++;
                }
                if (s_i < skills.length && skills[s_i] != "") {
                    var skill_id = skills[s_i];
                    var config = {
                        name: '',
                        desc: ''
                    }
                    if (window.CBG_GAME_CONFIG.pet_skill_desc && window.CBG_GAME_CONFIG.pet_skill_desc[skill_id]) {
                        var skillConfig = window.CBG_GAME_CONFIG.pet_skill_desc[skill_id];
                        config.name = skillConfig.name;
                        config.desc = skillConfig.desc;
                    }
                    var tipStr = 'data_tip_box="SkillTipsBox" data_store_name="' + config.name + '" data_store_desc="' + config.desc + '"';
                    if (isSuperSkill(skill_id)) {
                        tipStr += ' data_cifu_icon="' + conf.pet_skill_url + fill_format(skill_id) + '.gif"';
                    }
                    tipStr += ' data_src="' + conf.pet_skill_url + fill_format(skill_id) + '.gif"';
                    var content = "<img data-skill-id=" + skill_id + " referrerpolicy=\"no-referrer\"" + tipStr + " src=\"" + conf.pet_skill_url + fill_format(skill_id) + ".gif\">";
                    if (pet_attrs && pet_attrs.evol_skill_list && window.CBG_GAME_CONFIG.pet_skill_high_to_other_level_mapping) {
                        var cifu = pet_attrs.evol_skill_list;
                        cifu.forEach(function(item) {
                            var ids = item.skill_type
                            if (!ids || ids == "0") {
                                return;
                            }
                            var attrdataSkillMap = window.CBG_GAME_CONFIG.pet_skill_high_to_other_level_mapping[ids] || {};
                            if (attrdataSkillMap.high_skill) {
                                hashEvolSkllAll.push(attrdataSkillMap.high_skill);
                            }
                            if (attrdataSkillMap.low_skill) {
                                hashEvolSkllAll.push(attrdataSkillMap.low_skill);
                                var attrdataSkillMapLowSkill = attrdataSkillMap.low_skill
                                var attrdataSkillMapHighSkill = attrdataSkillMap.high_skill
                                var attrdataSkillObj = {};
                                attrdataSkillObj[attrdataSkillMapLowSkill] = attrdataSkillMapHighSkill;
                                hashBothEvolSkllAll.push(attrdataSkillObj);
                                hashLowEvolSkllAll.push(attrdataSkillMap.low_skill);
                            }
                        });
                        if (hashEvolSkllAll.contains(Number(skill_id))) {
                            if (hashLowEvolSkllAll.contains(Number(skill_id)) && all_skills.contains(String(findCorrespondingValue(hashBothEvolSkllAll, skill_id)))) {
                                var content = "<img data-skill-id=" + skill_id + " referrerpolicy=\"no-referrer\"" + tipStr + " src=\"" + conf.pet_skill_url + fill_format(skill_id) + ".gif\">";
                            } else {
                                var content = "<img data-skill-id=" + skill_id + " referrerpolicy=\"no-referrer\"" + tipStr + " src=\"" + conf.pet_skill_url + fill_format(skill_id) + ".gif\"> <div class='evol_skill_icon' " + tipStr + " ></div>";
                            }
                        }
                    }
                    c.innerHTML = content;
                } else {
                    c.innerHTML = "&nbsp;";
                }
            }
        }
        if (withSpSkill && skills.length <= row_len * col_len && trim(String(sp_skill)) != "0") {
            var config = {
                name: '',
                desc: ''
            }
            if (window.CBG_GAME_CONFIG.pet_skill_desc && window.CBG_GAME_CONFIG.pet_skill_desc[sp_skill]) {
                var skillConfig = window.CBG_GAME_CONFIG.pet_skill_desc[sp_skill];
                config.name = skillConfig.name;
                config.desc = skillConfig.desc;
            }
            var tipStr = 'data_tip_box="SkillTipsBox" data_store_name="' + config.name + '" data_store_desc="' + config.desc + '"';
            if (isSuperSkill(sp_skill)) {
                tipStr += ' data_cifu_icon="true"';
            }
            var sp_cell = grid.rows[row_len - 1].cells[col_len - 1];
            if (hashEvolSkllAll && hashEvolSkllAll.contains(Number(sp_skill))) {
                if (hashLowEvolSkllAll.contains(Number(sp_skill)) && all_skills.contains(String(findCorrespondingValue(hashBothEvolSkllAll, sp_skill)))) {
                    var content = "<img data-skill-id=" + sp_skill + " referrerpolicy=\"no-referrer\"" + tipStr + " src=\"" + conf.pet_skill_url + fill_format(sp_skill) + ".gif\" class=\"on\">";
                } else {
                    var content = "<img data-skill-id=" + sp_skill + " referrerpolicy=\"no-referrer\"" + tipStr + " src=\"" + conf.pet_skill_url + fill_format(sp_skill) + ".gif\" class=\"on\"> <div class='evol_skill_icon'></div>";
                }
            } else {
                var content = "<img data-skill-id=" + sp_skill + " referrerpolicy=\"no-referrer\"" + tipStr + " src=\"" + conf.pet_skill_url + fill_format(sp_skill) + ".gif\" class=\"on\">";
            }
            sp_cell.innerHTML = content;
        }
        return grid;
    }

    var enhanceGrid
    // var $root = $(conf.skill_panel_name);
    if (enhanceSkill && enhanceSkill.length) {
        enhanceGrid = makeGrid(enhanceSkill, Math.ceil(enhanceSkill.length / col_len), false);
        enhanceGrid.classList.add('pet-enhance-table');
        enhanceGrid.classList.add('enhance');
        // $root.appendChild(enhanceGrid);
    }
    // $root.appendChild(makeGrid(normalSkill, row_len, true));
    var notice_node 
    if (conf.notice_node_name && all_skills.length > row_len * col_len) {
        notice_node = document.getElementById(conf.notice_node_name);
        notice_node.style.display = "block";
    }
    return  {
        [conf.skill_panel_name]:[enhanceGrid,makeGrid(normalSkill, row_len, true)],
        [conf.notice_node_name]:notice_node
    }
}
function get_summon_color_desc(value, iType) {
    var miaoHuaTianNvConf = [102345, 102346];
    if (value == undefined) {
        return '未知';
    } else if (value == 1 && !miaoHuaTianNvConf.contains(Number(iType))) {
        return '是';
    } else {
        return '否';
    }
}
function init_pet_enhance_tip($root) {
    var key = 'xyq-pet-enhance-tip';
    var keyAttr = 'data-enhance';
    if (localStorage.getItem(key)) {
        return;
    }
    $root = $root || $$('body')[0];
    var $enhanceList = $root.getElements('[' + keyAttr + '] .enhance');
    if (!$enhanceList.length) {
        return;
    }
    var $parentList = $enhanceList.getParent('[' + keyAttr + ']');
    $parentList = [].slice.call($parentList, 0);
    $parentList.sort(function(a, b) {
        var aIndex = parseInt(a.get('data-enhance-index')) || 0
          , bIndex = parseInt(b.get('data-enhance-index')) || 0;
        return aIndex - bIndex;
    });
    var $pt = $($parentList[0])
      , $enhance = $pt.getElement('.enhance');
    var options = {};
    try {
        options = JSON.decode($pt.get(keyAttr));
    } catch (e) {}
    var isMobile = /mobile/.test(navigator.userAgent.toLocaleLowerCase());
    Object.merge(options, {
        resize: isMobile,
        autoFixTime: isMobile ? 0 : 200
    });
    var tip = new FloatTip($enhance,options);
    tip.$root.addClass('pet-enhance-tip')
    tip.show('<div class="pet-enhance-cnt"><div>部分信息会强化展示（可在APP“我的”设置里的商品设置中关闭）</div><div class="textCenter"><a href="javascript:;" class="js-close pet-enhance-tip-btn">我知道了</a></div></div>').addEvent('hide', function() {
        localStorage.setItem(key, 1);
    });
}
