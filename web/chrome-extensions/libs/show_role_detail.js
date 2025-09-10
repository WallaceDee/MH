var RoleInfoShow = new Class({
  initialize: function (role_desc) {
    var decode_desc =
      window.decode_desc ||
      function (str) {
        return str.trim();
      };
    this.role_parser = new RoleInfoParser(
      decode_desc($("equip_desc_value").value),
      {
        resUrl: window.ResUrl,
        serverId: window.ServerInfo.server_id,
        equipRequestTime: window.EquipRequestTime || "",
        serverCurrentTime: window.ServerCurrentTime || "",
        split_equip_dict: window.split_equip_dict || {},
      }
    );
    this.last_tab = null;
    this.last_sub_tab = null;
    this.reg_tab_ev();
  },
  adjust_frame_height: function () {
    if (window.self != window.top) {
      window.reset_iframe && reset_iframe();
    }
  },
  reg_tab_ev: function () {
    var self_obj = this;
    $("role_info_box").set(
      "data-school",
      self_obj.role_parser.get_basic_data().basic_info.school
    );
    $("role_basic").addEvent("click", function () {
      self_obj.show_basic();
      self_obj.adjust_frame_height();
    });
    $("role_skill").addEvent("click", function () {
      self_obj.show_skill();
      self_obj.adjust_frame_height();
    });
    $("role_equips").addEvent("click", function () {
      self_obj.show_equips();
      self_obj.adjust_frame_height();
      self_obj.bind_shenqi_dialog();
    });
    $("role_pets").addEvent("click", function () {
      self_obj.show_pets();
      self_obj.adjust_frame_height();
    });
    $("role_riders").addEvent("click", function () {
      self_obj.show_riders();
      self_obj.adjust_frame_height();
    });
    $("role_clothes").addEvent("click", function () {
      self_obj.show_clothes();
      self_obj.adjust_frame_height();
    });
    $("role_home").addEvent("click", function () {
      self_obj.show_home();
      self_obj.adjust_frame_height();
    });
  },
  switch_tab: function (el) {
    if (this.last_tab) {
      this.last_tab.removeClass("on");
    }
    this.last_tab = el;
    el.addClass("on");
    $("RoleEquipTipsBox").setStyle("display", "none");
  },
  switch_sub_tab: function (el) {
    if (this.last_sub_tab) {
      this.last_sub_tab.removeClass("on");
    }
    el.addClass("on");
    this.last_sub_tab = el;
  },
  show_basic: function () {
    this.switch_tab($("role_basic"));
    var basic_data = this.role_parser.get_basic_data();
    render_to_replace("role_info_box", "role_basic_templ", basic_data);
    $("role_icon").src = basic_data["basic_info"]["icon"];
  },
  show_skill: function () {
    this.switch_tab($("role_skill"));
    render_to_replace(
      "role_info_box",
      "role_skill_templ",
      this.role_parser.get_skill_data()
    );
    this.reg_equip_tips_ev($$("#school_skill_lists img"));
    this.reg_equip_tips_ev($$("#life_skill_lists img"));
    this.reg_equip_tips_ev($$("#juqing_skill_lists img"));
  },
  reg_equip_tips_ev: function (el_list) {
    var _this = this;
    var show_tips_box = function () {
      var el = $(this);
      var box = "RoleEquipTipsBox";
      var isSkill = false;
      if (el.getAttribute("data_tip_box")) {
        box = el.getAttribute("data_tip_box");
        isSkill = true;
      }
      var ctx = {
        name: el.getAttribute("data_equip_name"),
        desc: el.getAttribute("data_equip_desc"),
        type_desc: el.getAttribute("data_equip_type_desc") || "",
        cifu:
          el.getAttribute("data_cifu_icon") ||
          el.getAttribute("data_is_super_skill") ||
          "",
        icon:
          el.getAttribute("data_cifu_icon") ||
          el.getAttribute("data_height_icon") ||
          el.getAttribute("src") ||
          el.getAttribute("data_src"),
      };
      if (isSkill) {
        ctx.isSkill = true;
      }
      if (!ctx.desc) return;
      render_to_replace(box, "role_equip_tips_templ", ctx);
      adjust_tips_position(el, $(box));
      var lock_types = el.getAttribute("lock_types");
      if (lock_types) {
        _this.show_lock(
          $(box).children[0],
          typeOf(lock_types) == "string" ? lock_types.split(",") : lock_types,
          true
        );
      }
    };
    var hidden_tips_box = function () {
      var el = $(this);
      var box = "RoleEquipTipsBox";
      if (el.getAttribute("data_tip_box")) {
        box = el.getAttribute("data_tip_box");
      }
      $(box).setStyle("display", "none");
    };
    for (var i = 0; i < el_list.length; i++) {
      var el = el_list[i];
      el.addEvent("mouseover", show_tips_box);
      el.addEvent("mouseout", hidden_tips_box);
    }
  },
  show_lock: function (el, _lock_types, is_tips) {
    if (_lock_types == null || _lock_types.length < 1) {
      return;
    }
    var lock_types = [];
    for (var i = 0; i < _lock_types.length; i++) {
      var lock_type = _lock_types[i];
      lock_types.push(lock_type);
    }
    if (lock_types.length < 1) {
      return;
    }
    var size = "14px";
    var padding = "0px";
    if (is_tips) {
      size = "28px";
      padding = "10px";
    }
    if (is_tips) {
      var div = document.createElement("div");
      div.style.position = "absolute";
      div.style.height = size;
      div.style.right = padding;
      div.style.top = padding;
      for (var i = 0; i < lock_types.length; i++) {
        var lock_type = lock_types[i];
        if (!lock_type) {
          continue;
        }
        var e = document.createElement("img");
        e.src = window.ResUrlVer + "/images/time_lock_" + lock_type + ".png";
        e.style.height = "14px";
        e.style.width = "14px";
        div.appendChild(e);
      }
      var parentNode = el.parentNode;
      parentNode.appendChild(div);
    } else {
      var leftLock = [];
      var rightLock = [];
      for (var i = 0; i < lock_types.length; i++) {
        var item = lock_types[i];
        if (item == 9 || item === "protect" || item === "huoyue") {
          leftLock.push(item);
        } else {
          rightLock.push(item);
        }
      }
      var rightDiv = document.createElement("div");
      rightDiv.style.position = "absolute";
      rightDiv.style.width = "14px";
      rightDiv.style.right = padding;
      rightDiv.style.top = padding;
      var leftDiv = document.createElement("div");
      leftDiv.style.position = "absolute";
      leftDiv.style.width = "14px";
      leftDiv.style.left = padding;
      leftDiv.style.top = padding;
      function addLockImg(el, arr) {
        for (var i = 0; i < arr.length; i++) {
          var lock_type = arr[i];
          if (!lock_type) {
            continue;
          }
          var e = document.createElement("img");
          e.src = window.ResUrlVer + "/images/time_lock_" + lock_type + ".png";
          e.style.height = "14px";
          e.style.width = "14px";
          el.appendChild(e);
        }
      }
      addLockImg(leftDiv, leftLock.reverse());
      addLockImg(rightDiv, rightLock);
      var parentNode = el.parentNode;
      parentNode.appendChild(leftDiv);
      parentNode.appendChild(rightDiv);
    }
    try {
      var currentStyle = window.getComputedStyle(parentNode);
    } catch (ex) {
      var currentStyle = parentNode.currentStyle;
    }
    if (currentStyle != undefined && currentStyle.position !== "absolute") {
      parentNode.style.position = "relative";
    }
  },
  show_equips: function () {
    this.switch_tab($("role_equips"));
    var equips_data = this.role_parser.get_equips_data();
    render_to_replace("role_info_box", "role_equips_templ", equips_data);
    var using_equips = {};
    for (var i = 0; i < equips_data["using_equips"].length; i++) {
      var equip = equips_data["using_equips"][i];
      using_equips[equip["pos"]] = equip;
    }
    var using_pos_list = [1, 2, 3, 4, 5, 6, 187, 188, 189, 190];
    for (var i = 0; i < using_pos_list.length; i++) {
      var pos = using_pos_list[i];
      var el = $("role_using_equip_" + pos);
      var equip = using_equips[pos];
      if (pos === 2 && !equip) {
        equip = using_equips[191];
      }
      if (equip) {
        el.setAttribute("data_equip_name", equip["name"]);
        el.setAttribute("data_equip_type", equip["type"]);
        el.setAttribute("data_equip_desc", equip["desc"]);
        el.setAttribute("data_equip_type_desc", equip["static_desc"]);
        el.src = equip["small_icon"];
        el.setAttribute("lock_types", equip["lock_type"]);
        this.show_lock(el, equip["lock_type"]);
      } else {
        el.destroy();
      }
    }
    for (var i = 0; i < equips_data["not_using_equips"].length; i++) {
      var equip = equips_data["not_using_equips"][i];
      var el = $("store_equip_tips" + (i + 1));
      el.setAttribute("lock_types", equip["lock_type"]);
      this.show_lock(el, equip["lock_type"]);
    }
    for (var i = 0; i < equips_data["split_equips"].length; i++) {
      var equip = equips_data["split_equips"][i];
      var el = $(equip.eid);
      el.setAttribute("lock_types", equip["lock_type"]);
      this.show_lock(el, equip["lock_type"]);
    }
    var fabao_data = this.role_parser.get_fabao_data();
    var using_fabao = fabao_data.using_fabaos;
    var el_using_fabao = $$("#RoleUsingFabao td");
    var show_index = 0;
    for (var i = 1; i <= 4; i++) {
      if (using_fabao[i]) {
        new Element("img", {
          styles: { width: 50, height: 50 },
          align: "middle",
          data_equip_name: using_fabao[i]["name"],
          data_equip_type: using_fabao[i]["type"],
          data_equip_desc: using_fabao[i]["desc"],
          data_equip_type_desc: using_fabao[i]["static_desc"],
          src: using_fabao[i]["icon"],
        }).inject(el_using_fabao[show_index++]);
      }
      el_using_fabao[i - 1].setStyle("background", "#c0b9dd");
    }
    this.reg_equip_tips_ev($$("#RoleUsingEquips img"));
    this.reg_equip_tips_ev($$("#RoleStoreEquips img"));
    this.reg_equip_tips_ev($$("#RoleSplitEquips img"));
    this.reg_equip_tips_ev($$("#RoleUsingFabao img"));
    this.reg_equip_tips_ev($$("#RoleStoreFabao td"));
    this.reg_equip_tips_ev($$("#RoleStoreShenqi td"));
    this.reg_equip_tips_ev($$("#RoleUsingLingbao td"));
    this.reg_equip_tips_ev($$("#RoleNoUsingLingbao td"));
  },
  show_pet_detail: function (el, pet) {
    this.switch_sub_tab(el);
    if (pet["is_child"] && pet["isnew"]) {
      render_to_replace("pet_detail_panel", "child_detail_templ", { pet: pet });
      this.reg_equip_tips_ev($$("#child_skill_table img"));
    } else {
      render_to_replace("pet_detail_panel", "pet_detail_templ", { pet: pet });
    }
    window.initPetClothEffect && window.initPetClothEffect(pet);
    var el_list = $$(
      "#RolePetEquips img, #RolePetShipin img, #RolePetCifu img, #RolePetCifu .evol_skill_icon, #RolePetSkill img, #RolePetSkill .evol_skill_icon, #RolePetNeidan img"
    );
    this.reg_equip_tips_ev(el_list);
    for (var i = 0; i < el_list.length; i++) {
      var el = el_list[i];
      var types = (el.getAttribute("lock_types") || "").split(",");
      this.show_lock(el, types);
    }
  },
  show_pets: function () {
    this.switch_tab($("role_pets"));
    var pet_data = this.role_parser.get_pet_data();
    render_to_replace("role_info_box", "role_pet_templ", pet_data);
    var that = this;
    function renderPetDetail($list, key) {
      var show_pet_detal = function () {
        var el = $(this);
        var idx = el.getAttribute("data_idx");
        that.show_pet_detail(el, pet_data[key][idx]);
      };
      var el_list = $list;
      for (var i = 0; i < el_list.length; i++) {
        el_list[i].addEvent("click", show_pet_detal);
        var idx = el_list[i].getAttribute("data_idx");
        var pet = pet_data[key][idx];
        that.show_lock(el_list[i], pet["lock_type"]);
      }
    }
    renderPetDetail($$("#RolePets img"), "pet_info");
    renderPetDetail($$("#RoleSplitPets img"), "split_pets");
    var show_child_detal = function () {
      var el = $(this);
      var idx = el.getAttribute("data_idx");
      that.show_pet_detail(el, pet_data["child_info"][idx]);
    };
    var el_list = $$("#RoleChilds img");
    for (var i = 0; i < el_list.length; i++) {
      el_list[i].addEvent("click", show_child_detal);
    }
    if (pet_data["split_pets"].length != 0) {
      $$("#RoleSplitPets img")[0].fireEvent("click");
    } else if (pet_data["pet_info"].length != 0) {
      $$("#RolePets img")[0].fireEvent("click");
    } else if (pet_data["child_info"].length != 0) {
      $$("#RoleChilds img")[0].fireEvent("click");
    }
    if (pet_data.sbook_skill && pet_data.sbook_skill.length > 0) {
      function show_sbook_skill_tips() {
        var el = $(this);
        render_to_replace("RoleEquipTipsBox", "tips_sbook_skill_templ", {
          sbook_skill: pet_data.sbook_skill,
        });
        adjust_tips_position(el, $("RoleEquipTipsBox"));
      }
      function hide_sbook_skill_tips() {
        $("RoleEquipTipsBox").setStyle("display", "none");
      }
      var $showMoreSbookSkill = $("show_more_sbook_skill");
      if ($showMoreSbookSkill) {
        $showMoreSbookSkill.addEvent("mouseover", show_sbook_skill_tips);
        $showMoreSbookSkill.addEvent("mouseout", hide_sbook_skill_tips);
      }
    }
  },
  show_rider_detail: function (el, rider) {
    this.switch_sub_tab(el);
    render_to_replace("rider_detail_panel", "rider_detail_templ", {
      rider: rider,
    });
    var el_list = $$("#RoleRiderSkill img");
    this.reg_equip_tips_ev(el_list);
  },
  show_xiangrui_detail: function (el, xiangrui) {
    this.switch_sub_tab(el);
    render_to_replace("xiangrui_detail_panel", "xiangrui_detail_templ", {
      xiangrui: xiangrui,
    });
  },
  show_xuanlingzhu_detail: function (el, xuanlingzhu) {
    this.switch_sub_tab(el);
    render_to_replace("xuanlingzhu_detail_panel", "xuanlingzhu_detail_templ", {
      xuanlingzhu: xuanlingzhu,
    });
  },
  show_riders: function () {
    this.switch_tab($("role_riders"));
    var rider_data = this.role_parser.get_rider_data();
    render_to_replace("role_info_box", "role_riders_templ", rider_data);
    var that = this;
    var show_rider_detail = function () {
      var el = $(this);
      var idx = el.getAttribute("data_idx");
      that.show_rider_detail(el, rider_data["rider_info"][idx]);
    };
    var el_list = $$("#RoleRiders img");
    for (var i = 0; i < el_list.length; i++) {
      el_list[i].addEvent("click", show_rider_detail);
    }
    if (rider_data["rider_info"].length > 0) {
      $$("#RoleRiders img")[0].fireEvent("click");
    }
    var show_xuanlingzhu_detail = function () {
      var el = $(this);
      var idx = el.getAttribute("data_idx");
      that.show_xuanlingzhu_detail(el, rider_data["rider_plan_list"][idx]);
    };
    var xlz_el_list = $$("#RoleXunlingzhu img");
    for (var i = 0; i < xlz_el_list.length; i++) {
      xlz_el_list[i].addEvent("click", show_xuanlingzhu_detail);
      if (rider_data.rider_plan_list && rider_data["rider_plan_list"][i]) {
        var data = rider_data["rider_plan_list"][i];
        var locks = [];
        if (data.iLockGreen) {
          locks.push("protect");
        }
        if (data.iLockActive) {
          locks.push("huoyue");
        }
        xlz_el_list[i].setAttribute("lock_types", locks.join(","));
        this.show_lock(
          xlz_el_list[i],
          xlz_el_list[i].getAttribute("lock_types")
        );
      }
    }
    if (
      rider_data["rider_plan_list"] &&
      rider_data["rider_plan_list"].length > 0
    ) {
      $$("#RoleXunlingzhu img")[0].fireEvent("click");
    }
  },
  show_clothes: function () {
    this.switch_tab($("role_clothes"));
    render_to_replace(
      "role_info_box",
      "role_clothes_templ",
      this.role_parser.get_clothes_data()
    );
  },
  show_home: function () {
    this.switch_tab($("role_home"));
    render_to_replace(
      "role_info_box",
      "role_home_templ",
      this.role_parser.get_house_data()
    );
  },
  bind_shenqi_dialog: function () {
    $$("#shenqi").addEvent("click", function () {
      $$("#shenqiMask,#shenqiModal").addClass("active");
    });
    $$("#shenqiCloseBtn").addEvent("click", function () {
      $$("#shenqiMask,#shenqiModal").removeClass("active");
    });
    $$("#shenqiModal").addEvent("click:relay(.js_shenqi_tab)", function () {
      var $this = $(this);
      var $root = $("shenqiModal");
      if ($this.hasClass("disable") || $this.hasClass("active")) {
        return;
      }
      var index = $this.get("data-index");
      $root.getElements(".js_shenqi_tab").removeClass("active");
      $this.addClass("active");
      $root.getElements(".js_shenqi_panel").setStyle("display", "none");
      $root.getElements(".js_shenqi_panel")[index].setStyle("display", "");
    });
  },
});
function display_equip_tips(equip_info_id) {
  $(equip_info_id + "_panel").style.display = "block";
  if ($(equip_info_id + "_panel").displayed) {
    return;
  } else {
    $(equip_info_id + "_panel").displayed = true;
  }
  var content_height = $(equip_info_id + "_info").offsetHeight;
  if (content_height < 130) {
    content_height = 130;
  }
  $(equip_info_id + "_equip_layer1").style.height = content_height + 16 + "px";
  $(equip_info_id + "_equip_layer2").style.height = content_height + 10 + "px";
}
function hidden_equip_tips(equip_info_id) {
  $(equip_info_id + "_panel").style.display = "none";
}
function gen_skill_html(templ_id, skill_info) {
  var templ = new Template();
  var empty_skill_img = ResUrl + "/images/role_skills/empty_skill.gif";
  return templ.render(templ_id, {
    skills: skill_info,
    empty_img: empty_skill_img,
  });
}
function get_summon_color_desc(value, iType) {
  var miaoHuaTianNvConf = [102345, 102346];
  if (value == undefined) {
    return "未知";
  } else if (value == 1 && !miaoHuaTianNvConf.contains(Number(iType))) {
    return "是";
  } else {
    return "否";
  }
}
