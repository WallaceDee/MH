<template>
  <el-popover v-model="visible" :width="715" :data-equip-sn="$attrs.equip_sn" placement="right" trigger="click"
    popper-class="role-info-popover">
    <template #reference>
      <slot></slot>
      <el-image :src="imageUrl" fit="cover" :style="imageStyle" referrerpolicy="no-referrer" style="display: block;">
        <div slot="error" class="image-slot">
          <i class="el-icon-picture-outline"></i>
        </div>
      </el-image>
    </template>
    <div id="role_info_box" v-if="visible">
      <el-tabs v-model="activeName" class="role-info-tabs tabCont">
        <el-tab-pane label="人物/修炼" name="role_basic" v-if="basic_info">
          <div class="cols" style="width: 320px">
            <div class="subTab">
              <h4 class="subTabLeft role_basic_attr_tab" :class="{ off: currentDisplayIndex !== 0 }"
                @click="toggle_display(0)">
                人物状态
              </h4>
              <h4 class="subTabRight role_basic_attr_tab" :class="{ off: currentDisplayIndex !== 1 }"
                @click="toggle_display(1)">
                输出/抗性
              </h4>
            </div>
            <table class="tb02 role_basic_attr_table" width="100%" cellspacing="0" cellpadding="0"
              v-show="currentDisplayIndex === 0">
              <colgroup>
                <col width="180" />
                <col width="140" />
              </colgroup>
              <tr>
                <td><strong>级别：</strong>{{ basic_info.role_level }}</td>
                <td><strong>名称：</strong>{{ htmlEncode(basic_info.nickname) }}</td>
              </tr>
              <tr>
                <td><strong>角色：</strong>{{ basic_info.role_kind_name }}</td>
                <td><strong>人气：</strong>{{ basic_info.pride }}</td>
              </tr>
              <tr>
                <td><strong>帮派：</strong>{{ basic_info.org }}</td>
                <td><strong>帮贡：</strong>{{ basic_info.org_offer }}</td>
              </tr>
              <tr>
                <td>
                  <strong>门派：</strong><span id="kindName">{{ basic_info.school }}</span>
                </td>
                <td><strong>门贡：</strong>{{ basic_info.school_offer }}</td>
              </tr>
              <tr>
                <td><strong>气血：</strong>{{ basic_info.hp_max }}</td>
                <td><strong>体质：</strong>{{ basic_info.cor_all }}</td>
              </tr>
              <tr>
                <td><strong>魔法：</strong>{{ basic_info.mp_max }}</td>
                <td><strong>魔力：</strong>{{ basic_info.mag_all }}</td>
              </tr>
              <tr>
                <td><strong>命中：</strong>{{ basic_info.att_all }}</td>
                <td><strong>力量：</strong>{{ basic_info.str_all }}</td>
              </tr>
              <tr>
                <td><strong>伤害：</strong>{{ basic_info.damage_all }}</td>
                <td><strong>耐力：</strong>{{ basic_info.res_all }}</td>
              </tr>
              <tr>
                <td><strong>防御：</strong>{{ basic_info.def_all }}</td>
                <td><strong>敏捷：</strong>{{ basic_info.spe_all }}</td>
              </tr>
              <tr>
                <td><strong>速度：</strong>{{ basic_info.dex_all }}</td>
                <td><strong>潜力：</strong>{{ basic_info.point }}</td>
              </tr>
              <tr>
                <td v-if="basic_info.fa_shang !== undefined">
                  <strong>法伤：</strong>{{ basic_info.fa_shang }}
                </td>
                <td v-else><strong>躲避：</strong>{{ basic_info.dod_all }}</td>
                <td><strong>靓号特效：</strong>{{ basic_info.is_niceid }}</td>
              </tr>
              <tr>
                <td v-if="basic_info.fa_fang !== undefined">
                  <strong>法防：</strong>{{ basic_info.fa_fang }}
                </td>
                <td v-else><strong>灵力：</strong>{{ basic_info.mag_def_all }}</td>
                <td><strong>成就点数：</strong>{{ basic_info.chengjiu }}</td>
              </tr>
              <tr>
                <td><strong>获得经验：</strong>{{ basic_info.upexp }}</td>
                <td><strong>已用潜能果数量：</strong>{{ basic_info.qian_neng_guo }}</td>
              </tr>
              <tr>
                <td>
                  <span v-if="
                    basic_info.qian_yuan_dan && basic_info.qian_yuan_dan.new_value === undefined
                  ">
                    <strong>已兑换乾元丹数量：</strong>{{ basic_info.qian_yuan_dan.old_value }}
                  </span>
                  <span v-else>
                    <strong>新版乾元丹数量：</strong>{{ basic_info.qian_yuan_dan.new_value }}
                  </span>
                </td>
                <td>
                  <strong>总经验：</strong>{{ basic_info.sum_exp }}
                  <i v-if="basic_info.ach_info" class="question hoverTips">
                    <span class="hoverTipsDetail">{{ basic_info.ach_info }}</span>
                  </i>
                </td>
              </tr>
              <tr>
                <td>
                  <strong>月饼粽子机缘：</strong>{{ (basic_info.add_point || 0) + (basic_info.ji_yuan || 0) }}/{{
                    extraAttrPoints
                  }}
                  <i v-if="extraAttrPoints > 0" class="question hoverTips">
                    <span class="hoverTipsDetail">
                      月饼粽子食用量：{{ basic_info.add_point }}<br /><br />已获得机缘属性：{{
                        basic_info.ji_yuan
                      }}
                    </span>
                  </i>
                </td>
                <td><strong>原始种族：</strong><span v-html="basic_info.ori_race"></span></td>
              </tr>
              <tr>
                <td><strong>历史门派：</strong>{{ basic_info.changesch }}</td>
                <td><strong>属性保存方案：</strong>{{ basic_info.propkept }}</td>
              </tr>
              <tr>
                <td><strong>飞升/渡劫/化圣：</strong>{{ basic_info.fly_status }}</td>
                <td v-if="basic_info.role_level >= 120">
                  <strong>生死劫：</strong>{{ basic_info.shengsijie }}
                </td>
                <td v-else></td>
              </tr>
            </table>
            <table class="tb02 role_basic_attr_table" width="100%" cellspacing="0" cellpadding="0"
              v-show="currentDisplayIndex === 1">
              <template v-if="!basic_info.other_attr">
                <colgroup>
                  <col width="320" />
                </colgroup>
                <tr>
                  <td><br />重新寄售后才能显示</td>
                </tr>
              </template>
              <template v-else>
                <colgroup>
                  <col width="160" />
                  <col width="160" />
                </colgroup>
                <tr>
                  <td colspan="2"><strong style="font-size: 16px; color: white">输出</strong></td>
                </tr>
                <tr>
                  <td><strong>灵力：</strong></td>
                  <td>{{ basic_info.other_attr['14'] }}</td>
                </tr>
                <tr>
                  <td><strong>物理暴击等级：</strong></td>
                  <td>
                    {{ basic_info.other_attr['6'] }}({{
                      (
                        (basic_info.other_attr['6'] * 10) / Math.max(30, basic_info.role_level) || 0
                      ).toFixed(2)
                    }}%)
                  </td>
                </tr>
                <tr>
                  <td><strong>穿刺等级：</strong></td>
                  <td>
                    {{ basic_info.other_attr['8'] }}({{
                      (
                        (basic_info.other_attr['8'] * 3) / Math.max(30, basic_info.role_level) || 0
                      ).toFixed(2)
                    }}%)
                  </td>
                </tr>
                <tr>
                  <td><strong>狂暴等级：</strong></td>
                  <td>
                    {{ basic_info.other_attr['5'] }}({{
                      (
                        (basic_info.other_attr['5'] * 3) / Math.max(30, basic_info.role_level) || 0
                      ).toFixed(2)
                    }}%)
                  </td>
                </tr>
                <tr>
                  <td><strong>法术暴击等级：</strong></td>
                  <td>
                    {{ basic_info.other_attr['7'] }}({{
                      (
                        (basic_info.other_attr['7'] * 10) / Math.max(30, basic_info.role_level) || 0
                      ).toFixed(2)
                    }}%)
                  </td>
                </tr>
                <tr>
                  <td><strong>法术伤害结果：</strong></td>
                  <td>{{ basic_info.other_attr['12'] }}</td>
                </tr>
                <tr>
                  <td><strong>封印命中等级：</strong></td>
                  <td>
                    {{ basic_info.other_attr['1'] }}({{
                      (
                        (basic_info.other_attr['1'] * 10) /
                        Math.max(30, basic_info.role_level + 25) || 0
                      ).toFixed(2)
                    }}%)
                  </td>
                </tr>
                <tr>
                  <td><strong>治疗能力：</strong></td>
                  <td>{{ basic_info.other_attr['3'] }}</td>
                </tr>
                <tr>
                  <td colspan="2"><strong style="font-size: 16px; color: white">抗性</strong></td>
                </tr>
                <tr>
                  <td><strong>抗物理暴击等级：</strong></td>
                  <td>
                    {{ basic_info.other_attr['9'] }}({{
                      (
                        (basic_info.other_attr['9'] * 10) / Math.max(30, basic_info.role_level) || 0
                      ).toFixed(2)
                    }}%)
                  </td>
                </tr>
                <tr>
                  <td><strong>格挡值：</strong></td>
                  <td>{{ basic_info.other_attr['11'] }}</td>
                </tr>
                <tr>
                  <td><strong>抗法术暴击等级：</strong></td>
                  <td>
                    {{ basic_info.other_attr['10'] }}({{
                      (
                        (basic_info.other_attr['10'] * 10) / Math.max(30, basic_info.role_level) ||
                        0
                      ).toFixed(2)
                    }}%)
                  </td>
                </tr>
                <tr>
                  <td><strong>抵抗封印等级：</strong></td>
                  <td>
                    {{ basic_info.other_attr['2'] }}({{
                      (
                        (basic_info.other_attr['2'] * 10) /
                        Math.max(30, basic_info.role_level + 25) || 0
                      ).toFixed(2)
                    }}%)
                  </td>
                </tr>
                <tr>
                  <td><strong>气血回复效果：</strong></td>
                  <td>{{ basic_info.other_attr['4'] }}</td>
                </tr>
                <tr>
                  <td><strong>躲避：</strong></td>
                  <td>{{ basic_info.other_attr['13'] }}</td>
                </tr>
              </template>
            </table>
          </div>

          <div class="cols" style="width: 320px">
            <h4>角色修炼及宠修</h4>
            <table class="tb02" width="49%" cellspacing="0" cellpadding="0" style="float: left">
              <tr v-for="(item, index) in role_xiulian" :key="index">
                <th width="100">{{ item.name }}：</th>
                <td style="white-space: nowrap">{{ item.info }}</td>
              </tr>
            </table>

            <table class="tb02" width="49%" cellspacing="0" cellpadding="0" style="float: right">
              <tr v-if="yu_shou_shu !== undefined">
                <th width="100">育兽术：</th>
                <td>{{ yu_shou_shu }}</td>
              </tr>
              <tr v-for="(item, index) in pet_ctrl_skill" :key="index">
                <th width="100">{{ item.name }}：</th>
                <td>{{ item.grade }}</td>
              </tr>
            </table>

            <div class="blank9" style="clear: both"></div>
            <div class="blank9"></div>
            <h4>积分 其他</h4>
            <table width="92%" class="tb02" cellspacing="0" cellpadding="0">
              <tr>
                <th width="80">比武积分：</th>
                <td>{{ basic_info.hero_score }}</td>
                <th width="80">剑会积分：</th>
                <td>{{ basic_info.sword_score }}</td>
              </tr>
              <tr>
                <th width="80">三界功绩：</th>
                <td>{{ basic_info.sanjie_score }}</td>
                <th width="80">副本积分：</th>
                <td>{{ basic_info.dup_score }}</td>
              </tr>
              <tr>
                <th width="80">神器积分：</th>
                <td>{{ basic_info.shenqi_score }}</td>
                <th></th>
                <td></td>
              </tr>
            </table>
          </div>
        </el-tab-pane>
        <el-tab-pane label="技能" name="role_skill" v-if="school_skill">
          <div class="cols" style="width: 200px">
            <h4>师门技能</h4>
            <div class="skill">
              <p v-if="school_skill.length > 7" class="textCenter cDYellow">师门技能信息有误</p>
              <p v-else-if="school_skill.length == 0" class="textCenter cDYellow">师门技能都是0</p>
              <ul v-else id="school_skill_lists">
                <li style="left: 60px; top: 0">
                  <img referrerpolicy="no-referrer" :src="school_skill2_icon" :data_equip_name="school_skill2_name"
                    data_skill_type="school_skill" :data_equip_desc="school_skill2_desc"
                    data_tip_box="RoleSkillTipsBox" />
                  <p>{{ school_skill2_grade }}</p>
                  <h5>{{ school_skill2_name }}</h5>
                </li>
                <li style="left: 0; top: 50px">
                  <img referrerpolicy="no-referrer" :src="school_skill3_icon" :data_equip_name="school_skill3_name"
                    data_skill_type="school_skill" :data_equip_desc="school_skill3_desc"
                    data_tip_box="RoleSkillTipsBox" />
                  <p>{{ school_skill3_grade }}</p>
                  <h5>{{ school_skill3_name }}</h5>
                </li>
                <li style="left: 120px; top: 50px">
                  <img referrerpolicy="no-referrer" :src="school_skill4_icon" :data_equip_name="school_skill4_name"
                    data_skill_type="school_skill" :data_equip_desc="school_skill4_desc"
                    data_tip_box="RoleSkillTipsBox" />
                  <p>{{ school_skill4_grade }}</p>
                  <h5>{{ school_skill4_name }}</h5>
                </li>
                <li style="left: 0; top: 140px">
                  <img referrerpolicy="no-referrer" :src="school_skill5_icon" :data_equip_name="school_skill5_name"
                    data_skill_type="school_skill" :data_equip_desc="school_skill5_desc"
                    data_tip_box="RoleSkillTipsBox" />
                  <p>{{ school_skill5_grade }}</p>
                  <h5>{{ school_skill5_name }}</h5>
                </li>
                <li style="left: 120px; top: 140px">
                  <img referrerpolicy="no-referrer" :src="school_skill6_icon" :data_equip_name="school_skill6_name"
                    data_skill_type="school_skill" :data_equip_desc="school_skill6_desc"
                    data_tip_box="RoleSkillTipsBox" />
                  <p>{{ school_skill6_grade }}</p>
                  <h5>{{ school_skill6_name }}</h5>
                </li>
                <li style="left: 60px; top: 94px">
                  <img referrerpolicy="no-referrer" :src="school_skill1_icon" :data_equip_name="school_skill1_name"
                    data_skill_type="school_skill" :data_equip_desc="school_skill1_desc"
                    data_tip_box="RoleSkillTipsBox" />
                  <p>{{ school_skill1_grade }}</p>
                  <h5>{{ school_skill1_name }}</h5>
                </li>
                <li style="left: 60px; top: 200px">
                  <img referrerpolicy="no-referrer" :src="school_skill7_icon" :data_equip_name="school_skill7_name"
                    data_skill_type="school_skill" :data_equip_desc="school_skill7_desc"
                    data_tip_box="RoleSkillTipsBox" />
                  <p>{{ school_skill7_grade }}</p>
                  <h5>{{ school_skill7_name }}</h5>
                </li>
              </ul>
            </div>
          </div>

          <div class="cols" style="width: 442px; margin-left: 18px">
            <h4>生活技能</h4>
            <div class="blank12"></div>
            <div v-if="life_skill && life_skill.length > 0">
              <table cellspacing="0" cellpadding="0" class="skillTb" id="life_skill_lists">
                <tr v-for="(row, rowIndex) in skillRows(life_skill, 7)" :key="rowIndex">
                  <td v-for="(item, itemIndex) in row" :key="itemIndex">
                    <img referrerpolicy="no-referrer" :src="item.skill_icon" width="40" height="40"
                      :data_equip_name="item.name" data_skill_type="life_skill" :data_equip_desc="item.desc"
                      data_tip_box="RoleSkillTipsBox" />
                    <p>{{ item.skill_grade }}</p>
                    <h5>{{ item.skill_name }}</h5>
                  </td>
                </tr>
              </table>
            </div>
            <div v-else class="textCenter" style="padding-bottom: 30px">无</div>

            <div class="blank9"></div>
            <h4>剧情技能</h4>
            <div class="blank12"></div>
            <div v-if="ju_qing_skill && ju_qing_skill.length > 0">
              <table cellspacing="0" cellpadding="0" class="skillTb" id="juqing_skill_lists">
                <tr v-for="(row, rowIndex) in skillRows(ju_qing_skill, 7)" :key="rowIndex">
                  <td v-for="(item, itemIndex) in row" :key="itemIndex">
                    <img referrerpolicy="no-referrer" :src="item.skill_icon" width="40" height="40"
                      :data_equip_name="item.name" data_skill_type="ju_qing_skill" :data_equip_desc="item.desc"
                      data_tip_box="RoleSkillTipsBox" />
                    <p>{{ item.skill_grade }}</p>
                    <h5>{{ item.skill_name }}</h5>
                  </td>
                </tr>
              </table>
            </div>
            <div v-else class="textCenter" style="padding-bottom: 30px">无</div>

            <p class="textRight cDYellow">剩余技能点：{{ left_skill_point }}</p>
            <div class="blank9"></div>
            <h4>熟练度</h4>
            <table width="92%" class="tb02" cellspacing="0" cellpadding="0">
              <tr>
                <th width="100">打造熟练度：</th>
                <td>{{ shuliandu.smith_skill }}</td>
                <th width="100">裁缝熟练度：</th>
                <td>{{ shuliandu.sew_skill }}</td>
              </tr>
            </table>
          </div>
        </el-tab-pane>
        <el-tab-pane label="道具/法宝" name="role_equips">
          <div class="cols" style="width: 350px">
            <h4>道具</h4>

            <table width="80%" style="margin: 0 auto" cellspacing="3" cellpadding="3" id="RoleUsingEquips">
              <tr>
                <td colspan="3">
                  <table cellspacing="0" cellpadding="0" class="tb03 size50">
                    <tr>
                      <td>
                        <ItemPopover id="role_using_equip_187" :equipment="get_using_equip(187)" />
                      </td>
                      <td>
                        <ItemPopover id="role_using_equip_187" :equipment="get_using_equip(188)" />
                      </td>
                      <td>
                        <ItemPopover id="role_using_equip_187" :equipment="get_using_equip(190)" />
                      </td>
                      <td>
                        <ItemPopover id="role_using_equip_187" :equipment="get_using_equip(189)" />
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
              <tr>
                <td>
                  <table cellspacing="0" cellpadding="0" class="tb03 size50">
                    <tr>
                      <td>
                        <ItemPopover id="role_using_equip_1" :equipment="get_using_equip(1)" />
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <ItemPopover id="role_using_equip_6" :equipment="get_using_equip(6)" />
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <ItemPopover id="role_using_equip_5" :equipment="get_using_equip(5)" />
                      </td>
                    </tr>
                  </table>
                </td>
                <td>
                  <table class="tb02" cellspacing="0" cellpadding="0">
                    <tr>
                      <th>现金：</th>
                      <td>{{ basic_info.cash }}</td>
                    </tr>
                    <tr>
                      <th>存银：</th>
                      <td>{{ basic_info.saving }}</td>
                    </tr>
                    <tr>
                      <th>储备：</th>
                      <td>{{ basic_info.learn_cash }}</td>
                    </tr>
                    <tr>
                      <th>善恶：</th>
                      <td>{{ basic_info.badness }}</td>
                    </tr>
                    <tr>
                      <th>仙玉：</th>
                      <td>{{ basic_info.xianyu }}</td>
                    </tr>
                    <tr>
                      <th>精力：</th>
                      <td>{{ basic_info.energy }}</td>
                    </tr>
                  </table>
                </td>
                <td>
                  <table cellspacing="0" cellpadding="0" class="tb03 size50">
                    <tr>
                      <td>
                        <ItemPopover :equipment="get_using_equip(4)" id="role_using_equip_4" />
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <ItemPopover :equipment="get_using_equip(2)" id="role_using_equip_2" />
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <ItemPopover :equipment="get_using_equip(3)" id="role_using_equip3" />
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>

            <div class="blank9"></div>
            <table cellspacing="0" cellpadding="0" class="tb03 size50" id="RoleStoreEquips">
              <tr v-for="(row, rowIndex) in storeEquipsRows" :key="rowIndex">
                <td v-for="(equip, colIndex) in row" :key="colIndex">
                  <ItemPopover :id="'store_equip_tips' + (rowIndex * 5 + colIndex + 1)" :equipment="equip
                    ? {
                      equip_sn: equip.equip_sn,
                      equip_face_img: equip.small_icon,
                      equip_name: equip.name,
                      equip_type_desc: equip.static_desc,
                      large_equip_desc: equip.desc,
                      lock_type: equip.lock_type
                    }
                    : null
                    " />
                </td>
                <td v-for="i in 5 - row.length" :key="'empty-' + i">
                  <ItemPopover :equipment="null" />
                </td>
              </tr>
            </table>

            <div v-if="split_equips && split_equips.length" class="blank9"></div>
            <h4 v-if="split_equips && split_equips.length">拆卖道具</h4>
            <table v-if="split_equips && split_equips.length" cellspacing="0" cellpadding="3" class="tb03 size50"
              id="RoleSplitEquips">
              <tr v-for="(row, rowIndex) in splitEquipsRows" :key="rowIndex">
                <td v-for="(equip, colIndex) in row" :key="colIndex">
                  <a style="display: block; width: 100%; height: 100%" :href="getCBGLinkByType(equip.eid, 'equip')"
                    target="_blank" tid="gl03odgw" :data_trace_text="equip.eid">
                    <ItemPopover :equipment="get_using_equip(equip)" />
                  </a>
                </td>
                <td v-for="i in 5 - row.length" :key="'empty-' + i"></td>
              </tr>
            </table>
          </div>

          <div class="cols" style="width: 300px; margin-left: 25px">
            <div class="cols" style="width: 145px; margin-left: 0">
              <h4>神器</h4>
              <div class="blank9"></div>
              <table style="table-layout: fixed" cellspacing="0" cellpadding="0" class="tb03 size50"
                id="RoleStoreShenqi">
                <tr>
                  <el-popover trigger="click" placement="bottom" popper-class="shenqi-info-popover">
                    <template #reference>
                      <td v-if="shenqi" id="shenqi" class="shenqi_td" style="background: #c0b9dd"
                        :data_equip_name="shenqi.name" :data_equip_type="shenqi.type" :data_equip_desc="shenqi.desc"
                        :data_equip_type_desc="shenqi.static_desc">
                        <ItemPopover :equipment="{
                          equip_face_img: shenqi.icon,
                          equip_name: shenqi.name,
                          equip_type_desc: shenqi.static_desc,
                          large_equip_desc: shenqi.desc
                        }" />
                      </td>
                    </template>
                    <div class="shenqi-modal" id="shenqiModal">
                      <h4 class="modal-head">
                        神器属性 <span class="modal-close-btn" id="shenqiCloseBtn"></span>
                      </h4>
                      <div class="shenqi-modal-content">
                        <ul v-if="shenqi?.isNew" class="shenqi-tab">
                          <li v-for="i in 3" :key="i" :class="[
                            'tab-item',
                            'js_shenqi_tab',
                            !shenqi_components['shenqi' + i]
                              ? 'disable'
                              : shenqi_components['shenqi' + i] &&
                                shenqi_components['shenqi' + i].actived
                                ? 'active'
                                : ''
                          ]" :data-index="i - 1" @click="switchShenqiTab(i - 1)">
                            第{{ ['一', '二', '三'][i - 1] }}套属性
                          </li>
                        </ul>

                        <div class="shenqi-list">
                          <div v-for="(modalData, key) in shenqi_components" :key="key" class="js_shenqi_panel"
                            :style="{ display: !modalData.actived ? 'none' : '' }">
                            <div v-for="(component, compIndex) in modalData.components" :key="compIndex"
                              class="shenqi-itme">
                              <div class="shenqi-item-left">
                                <img referrerpolicy="no-referrer" :src="component.buweiPic" />
                              </div>
                              <div class="col-r">
                                <ul class="shenqi-item-center">
                                  <li v-for="(wuxing, wuxingIndex) in component.wuxing" :key="wuxingIndex">
                                    <div v-if="wuxing.status !== 1" class="img-wrap">
                                      <img referrerpolicy="no-referrer" :src="wuxing.lingxiPic" />
                                    </div>
                                    <div v-else>
                                      <div class="img-wrap">
                                        <img referrerpolicy="no-referrer" :src="wuxing.lingxiPic" />
                                        <span v-if="wuxing.wuxing_affix_text" class="cizhui">{{
                                          wuxing.wuxing_affix_text
                                          }}</span>
                                      </div>
                                      <p>{{ wuxing.wuxingText }}</p>
                                    </div>
                                  </li>
                                </ul>
                                <ul class="shenqi-item-right">
                                  <li v-for="(wuxing, wuxingIndex) in component.wuxing" :key="wuxingIndex">
                                    {{ wuxing.attr }}
                                  </li>
                                </ul>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </el-popover>

                  <td v-if="huoshenta" class="shenqi_td" style="background: #c0b9dd" :data_equip_name="huoshenta.name"
                    :data_equip_type="shenqi?.type" :data_equip_desc="huoshenta.desc" data_equip_type_desc="">
                    <ItemPopover :equipment="{
                      equip_face_img: huoshenta.icon,
                      equip_name: huoshenta.name,
                      large_equip_desc: huoshenta.desc
                    }" />
                  </td>
                  <td v-if="!shenqi && !huoshenta" style="background: rgb(192, 185, 221)"></td>
                </tr>
              </table>
            </div>
            <div class="cols" style="width: 145px; margin-right: 0">
              <h4>已装备灵宝</h4>
              <div class="blank9"></div>
              <table style="table-layout: fixed" cellspacing="0" cellpadding="0" class="tb03 size50">
                <tr id="RoleUsingLingbao">
                  <template v-for="(item, i) in using_lingbao.concat([null, null]).slice(0, 2)">
                    <td v-if="item" :key="'lingbao-' + i" style="background: #c0b9dd" :data_equip_name="item.name"
                      :data_equip_type="item.type" :data_equip_desc="item.desc"
                      :data_equip_type_desc="item.static_desc">
                      <ItemPopover :equipment="{
                        equip_face_img: item.icon,
                        equip_name: item.name,
                        equip_type_desc: item.static_desc,
                        large_equip_desc: item.desc
                      }" />
                    </td>
                    <td v-else :key="'empty-' + i" style="background: #c0b9dd"></td>
                  </template>
                </tr>
              </table>
            </div>
          </div>

          <div class="cols" style="width: 300px; margin-left: 24px">
            <div class="blank12"></div>
            <h4>未装备灵宝</h4>
            <div class="blank9"></div>
            <div style="
                max-height: 125px;
                width: 274px;
                overflow: auto;
                overflow-x: hidden;
                margin: 0 auto;
              ">
              <table cellspacing="0" cellpadding="0" class="tb03 size50" id="RoleNoUsingLingbao">
                <tr v-for="(row, rowIndex) in nousingLingbaoRows" :key="rowIndex">
                  <template v-for="(item, colIndex) in row">
                    <td v-if="item" :key="'lingbao-' + colIndex" style="background: #c0b9dd"
                      :data_equip_name="item.name" :data_equip_type="item.type" :data_equip_desc="item.desc"
                      :data_equip_type_desc="item.static_desc">
                      <ItemPopover :equipment="{
                        equip_face_img: item.icon,
                        equip_name: item.name,
                        equip_type_desc: item.static_desc,
                        large_equip_desc: item.desc
                      }" />
                    </td>
                    <td v-else :key="'empty-' + colIndex" style="background: #c0b9dd"></td>
                  </template>
                </tr>
              </table>
            </div>

            <div class="blank12"></div>
            <h4>已装备法宝</h4>
            <div class="blank9"></div>
            <table cellspacing="0" cellpadding="0" class="tb03 size50" id="RoleUsingFabao">
              <tr>
                <td v-for="i in 4" :key="'fabao-' + i" style="background: #c0b9dd">
                  <ItemPopover :equipment="get_using_fabao(i)" align="middle" />
                </td>
              </tr>
            </table>
            <div class="blank12"></div>
            <h4>
              未装备的所有法宝
              <span v-if="unused_fabao_sum !== undefined">({{ unused_fabao_sum }}/{{ fabao_storage_size }})</span>
            </h4>
            <div class="blank9"></div>
            <div id="fabao_table_wrapper" style="
                height: 205px;
                width: 274px;
                overflow: auto;
                overflow-x: hidden;
                margin: 0 auto;
              ">
              <table width="256" style="table-layout: fixed" cellspacing="0" cellpadding="0" class="tb03 size50"
                id="RoleStoreFabao">
                <tr v-for="(row, rowIndex) in storeFabaoRows" :key="rowIndex">
                  <td v-for="(fabao, colIndex) in row" :key="colIndex" v-if="fabao" style="background: #c0b9dd">
                    <ItemPopover :equipment="get_using_fabao(fabao)" />
                  </td>
                  <td v-for="i in 5 - row.length" :key="'empty-' + i" style="background: #c0b9dd"></td>
                </tr>
              </table>
            </div>

            <div class="blank9"></div>
            <table class="tb02" width="100%" cellspacing="0" cellpadding="0">
              <tr>
                <th width="100">行囊扩展：</th>
                <td>{{ basic_info.package_num }}</td>
              </tr>
            </table>
          </div>
        </el-tab-pane>
        <el-tab-pane label="召唤兽/孩子" name="role_pets">
          <div class="cols" style="width: 190px">
            <!-- 拆卖召唤兽 -->
            <div v-if="split_pets && split_pets.length">
              <h4>拆卖召唤兽</h4>
              <div class="blank9"></div>
              <table cellspacing="0" cellpadding="0" class="tb03 size50 pet-split-tb" id="RoleSplitPets">
                <tr v-if="split_pets.length === 0">
                  <td class="noData">无</td>
                </tr>
                <template v-else>
                  <tr v-for="(row, rowIndex) in splitPetsRows" :key="rowIndex">
                    <td v-for="(pet, colIndex) in row" :key="colIndex">
                      <div class="pet-split-img-wrap">
                        <img referrerpolicy="no-referrer" :src="pet.icon" :data_idx="rowIndex * 3 + colIndex"
                          @click="onPetAvatarClick(pet)"
                          :class="{ on: current_pet && current_pet.equip_sn === pet.equip_sn }" />
                      </div>
                      <a :href="getCBGLinkByType(pet.eid, 'equip')" tid="57i8um2f" :data_trace_text="pet.eid"
                        target="_blank" class="btn-pet-detail">查看详情</a>
                    </td>
                    <td v-for="i in 3 - row.length" :key="'empty-' + i"
                      style="width: 54px; height: 54px; display: none">
                      &nbsp;
                    </td>
                  </tr>
                </template>
              </table>
            </div>

            <!-- 召唤兽 -->
            <h4>召唤兽({{ pet_info.length }}/{{ allow_pet_count }})</h4>
            <div class="blank9"></div>
            <table cellspacing="0" cellpadding="0" class="tb03 size50" id="RolePets">
              <tr v-if="pet_info.length === 0">
                <td class="noData">无</td>
              </tr>
              <template v-else>
                <tr v-for="(row, rowIndex) in petInfoRows" :key="rowIndex">
                  <td v-for="(pet, colIndex) in row" :key="colIndex" style="width: 54px; height: 54px; cursor: pointer;position: relative;">
                    <img referrerpolicy="no-referrer" :src="pet.icon" :data_idx="rowIndex * 3 + colIndex"
                      @click="onPetAvatarClick(pet)"
                      :class="{ on: current_pet && current_pet.equip_sn === pet.equip_sn }" />
                    <div v-if="getPetRightLock(pet)?.length > 0"
                      style="position: absolute; width: 14px; right: 0px; top: 0px;">
                      <img v-for="l in getPetRightLock(pet)" :key="l"
                        :src="require(`../../../public/assets/images/time_lock_${l}.webp`)"
                        style="height: 14px; width: 14px; display: block;">
                    </div>
                    <div v-if="getPetLeftLock(pet)?.length > 0"
                      style="position: absolute; width: 14px; left: 0px; top: 0px;">
                      <img v-for="l in getPetLeftLock(pet)" :key="l"
                        :src="require(`../../../public/assets/images/time_lock_${l}.webp`)"
                        style="height: 14px; width: 14px;display: block;">
                    </div>
                  </td>
                  <td v-for="i in 3 - row.length" :key="'empty-' + i" style="width: 54px; height: 54px; display: none">
                    &nbsp;
                  </td>
                </tr>
              </template>
            </table>

            <div class="blank12"></div>

            <!-- 孩子 -->
            <h4>孩子</h4>
            <div class="blank9"></div>
            <table cellspacing="0" cellpadding="0" class="tb03 size50" id="RoleChilds">
              <tr v-if="child_info.length === 0">
                <td class="noData">无</td>
              </tr>
              <template v-else>
                <tr v-for="(row, rowIndex) in childListRows" :key="rowIndex">
                  <td v-for="(child, colIndex) in row" :key="colIndex"
                    style="width: 54px; height: 54px; cursor: pointer">
                    <img referrerpolicy="no-referrer" :src="child.icon" :data_idx="rowIndex * 2 + colIndex"
                      @click="onPetAvatarClick({ index: colIndex, ...child })" :class="{
                        on:
                          current_pet &&
                          current_pet.equip_sn === child.equip_sn &&
                          current_pet.index === colIndex
                      }" />
                  </td>
                  <td v-for="i in 2 - row.length" :key="'empty-' + i" style="width: 54px; height: 54px; display: none">
                    &nbsp;
                  </td>
                </tr>
              </template>
            </table>

            <div class="blank12"></div>

            <!-- 特殊召唤兽 -->
            <h4>特殊召唤兽</h4>
            <div class="blank9"></div>
            <table cellspacing="0" cellpadding="0" class="tb02">
              <tr v-if="special_pet_info === undefined">
                <td colspan="3" class="noData">未知</td>
              </tr>
              <tr v-else-if="special_pet_info.length === 0">
                <td colspan="3" class="noData">无</td>
              </tr>
              <template v-else>
                <template v-for="(pet, petIndex) in special_pet_info">
                  <tr :key="petIndex">
                    <th>{{ pet.cName }}</th>
                    <td>{{ pet.all_skills[0].name }}</td>
                    <td>{{ pet.all_skills[0].value }}</td>
                  </tr>
                  <tr v-for="(skill, skillIndex) in pet.all_skills.slice(1)" :key="skillIndex">
                    <td>&nbsp;</td>
                    <td>{{ skill.name }}</td>
                    <td>{{ skill.value }}</td>
                  </tr>
                </template>
              </template>
            </table>

            <div class="blank12"></div>

            <!-- 召唤兽心得技能 -->
            <h4>召唤兽心得技能</h4>
            <table class="tb02" width="100%" cellspacing="0" cellpadding="0">
              <tbody>
                <tr>
                  <th width="100">已解锁技能数：</th>
                  <td class="sbook-skill-val" id="show_more_sbook_skill">
                    <span v-if="sbook_skill && sbook_skill.length > 0" class="text-underline" :title="sbook_skill.join(',')">{{ sbook_skill.length
                      }}/{{
                        sbook_skill_total }}</span>
                    <span v-else>无</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="cols" style="width: 456px; margin-left: 18px" id="pet_detail_panel">
            <div v-if="pet_info.length === 0 && child_info.length === 0 && split_pets.length === 0">
              <h4>详细信息</h4>
              <div class="blank9"></div>
              <table class="tb02 petZiZhiTb" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                  <td class="noData" style="text-align: center">无</td>
                </tr>
              </table>
            </div>
            <PetDetail v-else-if="current_pet" :current_pet="current_pet" />
          </div>
        </el-tab-pane>
        <el-tab-pane label="坐骑" name="role_riders">
          <div class="cols" style="width: 320px">
            <h4>坐骑</h4>
            <div class="blank9"></div>
            <table cellspacing="0" cellpadding="0" class="tb03 size50" id="RoleRiders">
              <tr v-if="rider_info.length <= 0">
                <td class="noData">无</td>
              </tr>
              <template v-else>
                <tr v-for="(row, rowIndex) in riderRows" :key="rowIndex">
                  <td v-for="(rider, colIndex) in row" :key="colIndex"
                    style="width: 54px; height: 54px; cursor: pointer">
                    <img referrerpolicy="no-referrer" :src="rider.icon" width="50" height="50"
                      :data_idx="rowIndex * 5 + colIndex" @click="current_rider_index = `${rowIndex}-${colIndex}`"
                      :class="{ on: current_rider_index === `${rowIndex}-${colIndex}` }" />
                  </td>
                  <td v-for="i in 5 - row.length" :key="'empty-' + i" style="display: none"></td>
                </tr>
              </template>
            </table>
            <div class="blank12"></div>
            <div id="rider_detail_panel">
              <table class="tb02" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                  <th>类型：</th>
                  <td>{{ currentRider.type_name }}</td>
                  <th>主属性：</th>
                  <td>{{ currentRider.mattrib }}</td>
                </tr>
                <tr>
                  <th>等级：</th>
                  <td>{{ currentRider.grade }}</td>
                  <th>&nbsp;</th>
                  <td>&nbsp;</td>
                </tr>
                <tr>
                  <th>成长：</th>
                  <td>{{ currentRider.exgrow }}</td>
                  <th>&nbsp;</th>
                  <td>&nbsp;</td>
                </tr>
              </table>
              <div class="blank12"></div>
              <div v-if="currentRider && currentRider.all_skills && currentRider.all_skills.length > 0">
                <table cellspacing="0" cellpadding="0" class="skillTb" id="RoleRiderSkill">
                  <tr v-for="(row, rowIndex) in riderSkillRows" :key="rowIndex">
                    <td v-for="(skill, colIndex) in row" :key="colIndex">
                      <img :title="skill.name + ' (' + skill.grade + '级)\n' + skill.desc" referrerpolicy="no-referrer"
                        :src="skill.icon" width="40" height="40" :data_equip_name="skill.name"
                        data_skill_type="riderSkill" :data_equip_desc="skill.desc" :data_equip_level="skill.grade"
                    />
                      <p>{{ skill.grade }}</p>
                    </td>
                    <td v-for="i in 6 - row.length" :key="'empty-' + i"></td>
                  </tr>
                </table>
              </div>
            </div>

            <h4>携带玄灵珠</h4>
            <div class="blank9"></div>
            <div class="roleModuleScroller" style="max-height: 22em">
              <table cellspacing="0" cellpadding="0" class="tb03 size50" id="RoleXunlingzhu">
                <tr v-if="rider_plan_list.length > 0">
                  <td v-for="(riderplan, index) in rider_plan_list" :key="index"
                    style="width: 54px; height: 54px; cursor: pointer">
                    <img referrerpolicy="no-referrer" v-if="riderplan.type == 1" :src="ResUrl + '/images/big/56973.gif'"
                      width="50" height="50" :data_idx="index" @click="current_rider_plan_index = index"
                      :class="{ on: current_rider_plan_index === index }" />
                    <img referrerpolicy="no-referrer" v-else-if="riderplan.type == 2"
                      :src="ResUrl + '/images/big/56974.gif'" width="50" height="50" :data_idx="index"
                      @click="current_rider_plan_index = index" :class="{ on: current_rider_plan_index === index }" />
                    <span v-if="index == 0">第一套</span>
                    <span v-else-if="index == 1">第二套</span>
                  </td>
                </tr>
                <tr v-else>
                  <td class="noData">无</td>
                </tr>
              </table>
              <div class="blank12"></div>
              <div id="xuanlingzhu_detail_panel">
                <div v-if="currentRiderPlan">
                  <table class="tb02" width="100%" cellspacing="0" cellpadding="0">
                    <tr v-if="currentRiderPlan.type === 1">
                      <th style="width: 48px">类型：</th>
                      <td>{{ currentRiderPlan.level }}级回春</td>
                      <th>&nbsp;</th>
                      <td>&nbsp;</td>
                    </tr>
                    <tr v-if="currentRiderPlan.type === 1">
                      <th style="width: 48px">效果：</th>
                      <td>
                        战斗中"召唤"召唤兽或孩子时，恢复自身{{
                          EquipLevel * currentRiderPlan.level
                        }}点气血和{{ currentRiderPlan.level }}点愤怒。
                      </td>
                    </tr>
                    <tr v-if="currentRiderPlan.type === 2">
                      <th style="width: 48px">类型：</th>
                      <td>{{ currentRiderPlan.level }}级破军</td>
                      <th>&nbsp;</th>
                      <td>&nbsp;</td>
                    </tr>
                    <tr v-if="currentRiderPlan.type === 2">
                      <th style="width: 48px">效果：</th>
                      <td>
                        战斗中"召唤"召唤兽或孩子时，有{{
                          currentRiderPlan.level * 12.5
                        }}%几率提升自身1%伤害，持续到战斗结束。
                      </td>
                    </tr>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <div class="cols" style="float: right; width: 320px; margin-right: 28px; margin-bottom: 10px">
            <h4>限量祥瑞</h4>
            <div class="blank9"></div>
            <div v-if="nosale_xiangrui == undefined">
              <p class="textCenter cDYellow">祥瑞信息未知</p>
            </div>
            <div v-else class="roleModuleScroller" style="max-height: 22em">
              <table cellspacing="0" cellpadding="0" class="tb02" id="RoleXiangRui">
                <tr v-if="nosale_xiangrui.length <= 0">
                  <td class="noData">无</td>
                </tr>
                <template v-else>
                  <tr v-for="xiangrui in nosale_xiangrui" :key="xiangrui.name">
                    <th>{{ xiangrui.name }}</th>
                    <td>
                      技能：
                      <span v-if="xiangrui.skill_name">
                        {{ xiangrui.skill_name }}
                        <span v-if="xiangrui.skill_level">&nbsp;{{ xiangrui.skill_level }}</span>
                      </span>
                      <span v-else>无</span>
                    </td>
                  </tr>
                </template>
              </table>
            </div>
          </div>

          <div class="cols" style="float: right; clear: right; width: 320px; margin-right: 28px">
            <h4>普通祥瑞</h4>
            <div class="blank9"></div>
            <div v-if="xiangrui == undefined">
              <p class="textCenter cDYellow">祥瑞信息未知</p>
            </div>
            <div v-else class="roleModuleScroller" style="max-height: 22em">
              <table cellspacing="0" cellpadding="0" class="tb02" id="RoleXiangRui">
                <tr v-if="xiangrui.length <= 0">
                  <td class="noData">无</td>
                </tr>
                <template v-else>
                  <tr>
                    <th>祥瑞总数</th>
                    <td>{{ normal_xiangrui_num ? normal_xiangrui_num : totalXiangruiNum }}</td>
                  </tr>
                  <tr v-for="xiangrui in xiangrui" :key="xiangrui.name">
                    <th>{{ xiangrui.name }}</th>
                    <td>
                      技能：
                      <span v-if="xiangrui.skill_name">
                        {{ xiangrui.skill_name }}
                        <span v-if="xiangrui.skill_level">&nbsp;{{ xiangrui.skill_level }}</span>
                      </span>
                      <span v-else>无</span>
                    </td>
                  </tr>
                </template>
              </table>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="锦衣/外观" name="role_clothes">
          <div class="cols tab-jinyi" style="width: 320px">
            <div class="module">
              <h4>彩果染色</h4>
              <div class="blank9"></div>
              <table v-if="basic_info.body_caiguo !== undefined && basic_info.box_caiguo !== undefined" class="tb02"
                width="100%" cellspacing="0" cellpadding="0">
                <tr>
                  <th width="55%">身上染色折算彩果数：</th>
                  <td>{{ basic_info.body_caiguo }}</td>
                </tr>
                <tr>
                  <th>衣柜已保存染色方案：</th>
                  <td>{{ basic_info.box_caiguo }}</td>
                </tr>
                <tr>
                  <td colspan="2" class="cGray" style="font-size: 12px; padding-left: 0px; padding-right: 0px">
                    （衣柜保存的染色方案包括花豆染色方案和彩果染色方案）
                  </td>
                </tr>
                <tr>
                  <th>所有染色折算彩果数：</th>
                  <td>{{ basic_info.total_caiguo }}</td>
                </tr>
              </table>
              <p v-else-if="basic_info.caiguo !== undefined" class="textCenter cDYellow">
                角色拥有折算彩果总量：{{ basic_info.caiguo }}
              </p>
              <p v-else class="textCenter cDYellow">彩果信息未知</p>
            </div>
            <div v-if="new_clothes !== undefined">
              <div v-for="(item, index) in titleConf" :key="index" class="module module-jinyi">
                <h4>{{ item.title }}</h4>
                <p class="jinyi-num">{{ item.title }}总数：{{ getClothesList(item.key).length }}</p>
                <ul v-if="getClothesList(item.key)" class="jinyi-attr-list">
                  <li v-for="(clothesItem, clothesIndex) in getClothesList(item.key)" :key="clothesIndex" class="item">
                    {{ clothesItem.name }}
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div class="cols" style="width: 320px; margin-left: 18px">
            <h4>锦衣道具栏</h4>
            <div class="blank9"></div>
            <p v-if="clothes === undefined && new_clothes === undefined" class="textCenter cDYellow">
              锦衣信息未知
            </p>

            <div v-else-if="new_clothes !== undefined">
              <ul class="xianyu-wrap">
                <li><i class="icon icon-xianyu"></i>仙玉: {{ basic_info.xianyu }}</li>
                <li>
                  <i class="icon icon-xianyu-jifen"></i>仙玉积分: {{ basic_info.xianyu_score }}
                </li>
                <li><i class="icon icon-qicai-jifen"></i>七彩积分: {{ basic_info.qicai_score }}</li>
              </ul>
              <div class="new-jinyi-list">
                <p class="jinyi-num">锦衣总数：{{ basic_info.total_avatar }}</p>
                <div v-for="(item, index) in new_clothes" :key="index"
                  :class="'module module-jinyi module-jinyi—' + index">
                  <p class="jinyi-sub-title">{{ item.title }}</p>
                  <ul v-if="item.list.length > 0" class="jinyi-attr-list">
                    <li v-for="(clothesItem, clothesIndex) in item.list" :key="clothesIndex" class="item">
                      {{ clothesItem.name }}
                    </li>
                  </ul>
                  <p v-else class="empty">无</p>
                </div>
              </div>
            </div>

            <div v-else>
              <div class="roleModuleScroller" style="max-height: 22em">
                <table cellspacing="0" cellpadding="0" class="tb02" id="RoleClothesi">
                  <tr v-if="clothes.length <= 0">
                    <td class="noData">无</td>
                  </tr>
                  <template v-else>
                    <tr>
                      <th style="text-align: left">
                        锦衣总数 : <span style="color: white">{{ getTotalAvatar() }}</span>
                      </th>
                      <th>&nbsp;</th>
                    </tr>
                    <tr v-for="(row, rowIndex) in clothesRows" :key="rowIndex">
                      <th v-for="(clothesItem, colIndex) in row" :key="colIndex" style="text-align: left">
                        {{ clothesItem ? clothesItem.name : '' }}
                      </th>
                    </tr>
                  </template>
                </table>
              </div>
            </div>
            <div class="blank9"></div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="玩家之家" name="role_home">
          <div class="cols tab-home" style="width:320px;">
            <div class="module">
              <h4>房屋信息</h4>
              <div class="blank9"></div>
              <table width="92%" class="tb02" cellspacing="0" cellpadding="0">
                <tr>
                  <td><strong>婚否：</strong>{{ basic_info.is_married }}</td>
                  <td><strong>同袍：</strong>{{ basic_info.is_tongpao }}</td>
                </tr>
                <tr>
                  <td><strong>居住房屋：</strong>{{ basic_info.fangwu_info }}</td>
                  <td v-if="basic_info.fangwu_owner_info"><strong>是否产权所有人：</strong>{{ basic_info.fangwu_owner_info }}</td>
                </tr>
                <tr>
                  <td><strong>庭院等级：</strong>{{ basic_info.tingyuan_info }}</td>
                  <td><strong>牧场：</strong>{{ basic_info.muchang_info }}</td>
                </tr>
                <tr>
                  <td><strong>社区：</strong>{{ basic_info.community_info }}</td>
                </tr>
                <tr>
                  <td colspan="3"><strong>房契：</strong>{{ basic_info.house_fangqi }}</td>
                </tr>
              </table>
              <div class="module module-jinyi">
                <h4>窗景</h4>
                <p class="jinyi-num">窗景总数：{{ house.house_indoor_view_cnt }}</p>
                <ul v-if="house.house_indoor_view && house.house_indoor_view.length" class="jinyi-attr-list roleplay-attr-list">
                  <li v-for="item in house.house_indoor_view" :key="item.name" class="item">{{ item.name }}</li>
                </ul>
              </div>
              <div class="module module-jinyi">
                <h4>庭院主题</h4>
                <p class="jinyi-num">庭院主题总数：{{ house.house_yard_map_cnt }}</p>
                <ul v-if="house.house_yard_map && house.house_yard_map.length" class="jinyi-attr-list roleplay-attr-list">
                  <li v-for="item in house.house_yard_map" :key="item.name" class="item">{{ item.name }}</li>
                </ul>
              </div>
              <div class="module module-jinyi">
                <h4>庭院特效</h4>
                <p class="jinyi-num">庭院特效总数：{{ house.house_yard_animate_cnt }}</p>
                <ul v-if="house.house_yard_animate && house.house_yard_animate.length" class="jinyi-attr-list roleplay-attr-list">
                  <li v-for="item in house.house_yard_animate" :key="item.name" class="item">{{ item.name }}</li>
                </ul>
              </div>
              <div class="module module-jinyi">
                <h4>庭院饰品</h4>
                <p class="jinyi-num">庭院饰品总数：{{ house.house_yard_fur_cnt }}</p>
                <ul v-if="house.house_yard_fur && house.house_yard_fur.length" class="jinyi-attr-list roleplay-attr-list">
                  <li v-for="item in house.house_yard_fur" :key="item.name" class="item">{{ item.name }}*{{ item.count }}</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div class="cols" style="width:320px; margin-left:18px;">
            <div class="module module-jinyi module-roleplay">
              <h4>建材</h4>
              <p class="jinyi-num">建材总数：{{ house.house_building_material_cnt }}</p>
              <ul v-if="house.house_building_material && house.house_building_material.length" class="jinyi-attr-list roleplay-attr-list">
                <li v-for="item in house.house_building_material" :key="item.name" class="item">
                  <span>{{ item.name }}</span>*{{ item.count }}
                </li>
              </ul>
            </div>
            <div class="module module-jinyi">
              <h4>家具</h4>
              <p class="jinyi-num">家具总数：{{ house.house_jiaju_num }}</p>
              <ul v-if="house.house_jiaju && house.house_jiaju.length" class="jinyi-attr-list roleplay-attr-list">
                <li v-for="item in house.house_jiaju" :key="item.name" class="item">
                  <span>{{ item.name }}</span>*{{ item.count }}
                </li>
              </ul>
            </div>
            <div class="blank9"></div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </el-popover>
</template>

<script>
import { commonMixin } from '@/utils/mixins/commonMixin'
import  ItemPopover  from './ItemPopover.vue'
import PetDetail from './PetDetail.vue'

const riderNumPerLine = 5
export default {
  name: 'RoleImage',
  components: {
    ItemPopover,
    PetDetail
  },
  mixins: [commonMixin],
  props: {
    size: { type: String, default: 'small' },
    width: { type: String, default: '50px' },
    height: { type: String, default: '50px' },
    cursor: { type: String, default: 'pointer' },
    placement: { type: String, default: 'right' },
    popoverWidth: { type: String, default: '400px' },
    other_info: {
      type: String,
      default: ''
    },
    roleInfo: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      ResUrl: window.ResUrl,
      shenqi_visible: false,
      visible: false,
      activeName: 'role_basic',
      basic_info: null,
      school_skill: null,
      life_skill: null,
      ju_qing_skill: null,
      shuliandu: null,
      left_skill_point: 0,
      role_xiulian: [],
      pet_ctrl_skill: [],
      yu_shou_shu: undefined,
      currentDisplayIndex: 0, // 添加当前显示索引
      not_using_equips: null,
      split_equips: null,
      shenqi: null,
      huoshenta: null,
      using_lingbao: null,
      nousing_lingbao: null,
      nousing_fabao: null,
      using_fabao: null,
      unused_fabao_sum: null,
      fabao_storage_size: null,
      shenqi_components: {},
      split_pets: [],
      pet_info: [],
      child_info: [],
      special_pet_info: [],
      sbook_skill: [],
      allow_pet_count: 0,
      sbook_skill_total: 0,
      current_pet: null,
      rider_info: [],
      current_rider_index: '0-0',
      rider_plan_list: [],
      current_rider_plan_index: 0,
      xiangrui: [],
      nosale_xiangrui: [],
      normal_xiangrui_num: 0,
      EquipLevel: 159,
      clothes: null,
      new_clothes: null,
      house: null,
      titleConf: [
        {
          title: '称谓特效',
          key: 'title_effect'
        },
        {
          title: '施法/攻击特效',
          key: 'perform_effect'
        },
        {
          title: '冒泡框',
          key: 'chat_effect'
        },
        {
          title: '头像框',
          key: 'icon_effect'
        },
        {
          title: '彩饰-队标',
          key: 'achieve_show'
        }
      ]
    }
  },
  computed: {
    currentRider() {
      const [rowIndex, colIndex] = this.current_rider_index.split('-').map(Number)
      const rider = this.rider_info[rowIndex * riderNumPerLine + colIndex]
      return rider || {}
    },
    currentRiderPlan() {
      return this.rider_plan_list[this.current_rider_plan_index] || null
    },
    imageUrl() {
      const icon = window.get_role_icon(this.other_info)
      return window.ResUrl + '/images/role_icon/small/' + icon + '.gif'
    },
    imageStyle() {
      return {
        display: 'block',
        width: this.width,
        height: this.height,
        cursor: this.cursor
      }
    },
    extraAttrPoints() {
      const currentFullYear = window.ServerTime
        ? +window.ServerTime.split('-')[0]
        : new Date().getFullYear()
      return (currentFullYear - 2004 + 1) * 3
    },
    // 师门技能相关属性
    school_skill1_icon() {
      return this.school_skill && this.school_skill[0] ? this.school_skill[0].skill_icon : ''
    },
    school_skill1_name() {
      return this.school_skill && this.school_skill[0] ? this.school_skill[0].skill_name : ''
    },
    school_skill1_grade() {
      return this.school_skill && this.school_skill[0] ? this.school_skill[0].skill_grade : ''
    },
    school_skill1_desc() {
      return this.school_skill && this.school_skill[0] ? this.school_skill[0].desc : ''
    },

    school_skill2_icon() {
      return this.school_skill && this.school_skill[1] ? this.school_skill[1].skill_icon : ''
    },
    school_skill2_name() {
      return this.school_skill && this.school_skill[1] ? this.school_skill[1].skill_name : ''
    },
    school_skill2_grade() {
      return this.school_skill && this.school_skill[1] ? this.school_skill[1].skill_grade : ''
    },
    school_skill2_desc() {
      return this.school_skill && this.school_skill[1] ? this.school_skill[1].desc : ''
    },

    school_skill3_icon() {
      return this.school_skill && this.school_skill[2] ? this.school_skill[2].skill_icon : ''
    },
    school_skill3_name() {
      return this.school_skill && this.school_skill[2] ? this.school_skill[2].skill_name : ''
    },
    school_skill3_grade() {
      return this.school_skill && this.school_skill[2] ? this.school_skill[2].skill_grade : ''
    },
    school_skill3_desc() {
      return this.school_skill && this.school_skill[2] ? this.school_skill[2].desc : ''
    },

    school_skill4_icon() {
      return this.school_skill && this.school_skill[3] ? this.school_skill[3].skill_icon : ''
    },
    school_skill4_name() {
      return this.school_skill && this.school_skill[3] ? this.school_skill[3].skill_name : ''
    },
    school_skill4_grade() {
      return this.school_skill && this.school_skill[3] ? this.school_skill[3].skill_grade : ''
    },
    school_skill4_desc() {
      return this.school_skill && this.school_skill[3] ? this.school_skill[3].desc : ''
    },

    school_skill5_icon() {
      return this.school_skill && this.school_skill[4] ? this.school_skill[4].skill_icon : ''
    },
    school_skill5_name() {
      return this.school_skill && this.school_skill[4] ? this.school_skill[4].skill_name : ''
    },
    school_skill5_grade() {
      return this.school_skill && this.school_skill[4] ? this.school_skill[4].skill_grade : ''
    },
    school_skill5_desc() {
      return this.school_skill && this.school_skill[4] ? this.school_skill[4].desc : ''
    },

    school_skill6_icon() {
      return this.school_skill && this.school_skill[5] ? this.school_skill[5].skill_icon : ''
    },
    school_skill6_name() {
      return this.school_skill && this.school_skill[5] ? this.school_skill[5].skill_name : ''
    },
    school_skill6_grade() {
      return this.school_skill && this.school_skill[5] ? this.school_skill[5].skill_grade : ''
    },
    school_skill6_desc() {
      return this.school_skill && this.school_skill[5] ? this.school_skill[5].desc : ''
    },

    school_skill7_icon() {
      return this.school_skill && this.school_skill[6] ? this.school_skill[6].skill_icon : ''
    },
    school_skill7_name() {
      return this.school_skill && this.school_skill[6] ? this.school_skill[6].skill_name : ''
    },
    school_skill7_grade() {
      return this.school_skill && this.school_skill[6] ? this.school_skill[6].skill_grade : ''
    },
    school_skill7_desc() {
      return this.school_skill && this.school_skill[6] ? this.school_skill[6].desc : ''
    },

    // 装备相关计算属性
    storeEquipsRows() {
      const numPerLine = 5
      const equips = this.not_using_equips || []
      const equipsNum = equips.length

      // 计算需要的行数，确保至少有4行
      let loopTimes = parseInt(equipsNum / numPerLine) + (equipsNum % numPerLine ? 1 : 0)
      loopTimes = loopTimes < 4 ? 4 : loopTimes

      const rows = []
      for (let i = 0; i < loopTimes; i++) {
        const items = equips.slice(i * numPerLine, (i + 1) * numPerLine)
        rows.push(items)
      }
      return rows
    },

    splitEquipsRows() {
      if (!this.split_equips || this.split_equips.length === 0) return []
      const numPerLine = 5
      const rows = []
      for (let i = 0; i < this.split_equips.length; i += numPerLine) {
        rows.push(this.split_equips.slice(i, i + numPerLine))
      }
      return rows
    },

    nousingLingbaoRows() {
      const colCount = 5
      const lingbao = this.nousing_lingbao || []
      const max = Math.max(1, Math.ceil(lingbao.length / colCount))
      const rows = []
      for (let i = 0; i < max; i++) {
        const row = []
        for (let j = 0; j < colCount; j++) {
          const index = i * colCount + j
          row.push(lingbao[index] || null)
        }
        rows.push(row)
      }
      return rows
    },

    storeFabaoRows() {
      if (!this.nousing_fabao || this.nousing_fabao.length === 0) return []
      const numPerLine = 5
      const rows = []
      for (let i = 0; i < this.nousing_fabao.length; i += numPerLine) {
        rows.push(this.nousing_fabao.slice(i, i + numPerLine))
      }
      // 确保至少有4行
      while (rows.length < 4) {
        rows.push([])
      }
      return rows
    },

    // 召唤兽相关计算属性
    splitPetsRows() {
      const numPerLine = 3
      const pets = this.split_pets || []
      const petNum = pets.length
      const loopTimes =
        petNum === 0 ? 1 : parseInt(petNum / numPerLine) + (petNum % numPerLine ? 1 : 0)

      const rows = []
      for (let i = 0; i < loopTimes; i++) {
        const items = pets.slice(i * numPerLine, (i + 1) * numPerLine)
        rows.push(items)
      }
      return rows
    },
    petInfoRows() {
      const numPerLine = 3
      const pets = this.pet_info || []
      const petNum = pets.length
      const loopTimes =
        petNum === 0 ? 1 : parseInt(petNum / numPerLine) + (petNum % numPerLine ? 1 : 0)

      const rows = []
      for (let i = 0; i < loopTimes; i++) {
        const items = pets.slice(i * numPerLine, (i + 1) * numPerLine)
        rows.push(items)
      }
      return rows
    },

    childListRows() {
      const numPerLine = 2
      const children = this.child_info || []
      const childNum = children.length
      const loopTimes =
        childNum === 0 ? 1 : parseInt(childNum / numPerLine) + (childNum % numPerLine ? 1 : 0)

      const rows = []
      for (let i = 0; i < loopTimes; i++) {
        const items = children.slice(i * numPerLine, (i + 1) * numPerLine)
        rows.push(items)
      }
      return rows
    },



    // 坐骑相关计算属性
    riderRows() {
      const numPerLine = riderNumPerLine
      const riders = this.rider_info || []
      const riderNum = riders.length
      const loopTimes = parseInt(riderNum / numPerLine) + (riderNum % numPerLine ? 1 : 0)

      const rows = []
      for (let i = 0; i < loopTimes; i++) {
        const items = riders.slice(i * numPerLine, (i + 1) * numPerLine)
        rows.push(items)
      }
      return rows
    },

    // 计算祥瑞总数
    totalXiangruiNum() {
      const nosaleNum = this.nosale_xiangrui ? this.nosale_xiangrui.length : 0
      const totalNum = this.basic_info ? this.basic_info.total_horse : 0

      if (!totalNum && this.xiangrui) {
        const num = this.xiangrui.length
        return num >= 10 ? '大于等于10' : num
      } else {
        return totalNum - nosaleNum
      }
    },

    // 坐骑技能行计算属性
    riderSkillRows() {
      if (!this.currentRider || !this.currentRider.all_skills) return []
      const numPerLine = 6
      const skills = this.currentRider.all_skills
      const skillNum = skills.length
      let loopTimes = parseInt(skillNum / numPerLine) + (skillNum % numPerLine ? 1 : 0)
      if (loopTimes === 0) {
        loopTimes = 1
      }

      const rows = []
      for (let i = 0; i < loopTimes; i++) {
        const items = skills.slice(i * numPerLine, (i + 1) * numPerLine)
        rows.push(items)
      }
      return rows
    },
    clothesRows() {
      const numPerLine = 2
      const rows = []
      for (let i = 0; i < this.clothes.length; i += numPerLine) {
        const row = this.clothes.slice(i, i + numPerLine)
        // 填充空位
        while (row.length < numPerLine) {
          row.push(null)
        }
        rows.push(row)
      }
      return rows
    }
  },
  mounted() {
    this.basic_info = this.roleInfo.basic_info || {}
    this.role_xiulian = this.roleInfo.role_xiulian || []
    this.pet_ctrl_skill = this.roleInfo.pet_ctrl_skill || []
    this.yu_shou_shu = this.roleInfo.role_skill.yu_shou_shu
    this.school_skill = this.roleInfo.role_skill.school_skill
    this.life_skill = this.roleInfo.role_skill.life_skill
    this.ju_qing_skill = this.roleInfo.role_skill.ju_qing_skill
    this.shuliandu = this.roleInfo.role_skill.shuliandu
    this.left_skill_point = this.roleInfo.left_skill_point || 0

    // 装备相关数据
    this.using_equips = this.roleInfo.using_equips || []
    this.not_using_equips = this.roleInfo.not_using_equips || []
    this.split_equips = this.roleInfo.split_equips || []
    this.shenqi = this.roleInfo.shenqi || null
    this.huoshenta = this.roleInfo.huoshenta || null
    this.shenqi_components = this.roleInfo.shenqi_components || {}
    this.using_lingbao = this.roleInfo.using_lingbao || []
    this.nousing_lingbao = this.roleInfo.nousing_lingbao || []
    this.nousing_fabao = this.roleInfo.nousing_fabao || []
    this.using_fabao = this.roleInfo.using_fabao || []
    this.unused_fabao_sum = this.roleInfo.unused_fabao_sum
    this.fabao_storage_size = this.roleInfo.fabao_storage_size

    //召唤兽
    this.split_pets = this.roleInfo.split_pets || []
    this.pet_info = this.roleInfo.pet_info || []
    if (this.pet_info.length > 0) {
      this.current_pet = this.pet_info[0]
    } else if (this.split_pets.length > 0) {
      this.current_pet = this.split_pets[0]
    } else if (this.child_info.length > 0) {
      this.current_pet = this.child_info[0]
    }
    this.child_info = this.roleInfo.child_info || []
    this.special_pet_info = this.roleInfo.special_pet_info || []
    this.sbook_skill = this.roleInfo.sbook_skill || []
    this.allow_pet_count = this.roleInfo.allow_pet_count || 0
    this.sbook_skill_total = this.roleInfo.sbook_skill_total || 0

    //坐骑
    this.rider_info = this.roleInfo.rider_info || []
    this.rider_plan_list = this.roleInfo.rider_plan_list || []
    this.xiangrui = this.roleInfo.xiangrui || []
    this.nosale_xiangrui = this.roleInfo.nosale_xiangrui || []
    this.normal_xiangrui_num = this.roleInfo.normal_xiangrui_num || 0

    // 初始化坐骑选择
    if (this.rider_info.length > 0) {
      this.current_rider_index = '0-0'
    }

    // 初始化玄灵珠选择
    if (this.rider_plan_list.length > 0) {
      this.current_rider_plan_index = 0
    }
    this.EquipLevel = this.basic_info.role_level
    // 初始化锦衣数据
    this.clothes = this.roleInfo.clothes || null
    this.new_clothes = this.roleInfo.new_clothes || null
    
    // 初始化房屋数据
    this.house = this.roleInfo.house || {}
  },
  methods: {
    getPetRightLock(pet) {
      return pet.lock_type?.filter(item => item !== 9 && item !== 'protect' && item !== 'huoyue')
    },
    getPetLeftLock(pet) {
      return pet.lock_type?.filter(item => item === 9 || item === 'protect' || item === 'huoyue')
    },
    onPetAvatarClick(pet) {
      this.current_pet = pet
    },
    get_using_equip(target) {
      const equip =
        typeof target === 'number' ? this.using_equips.find(({ pos }) => pos === target) : target
      if (equip) {
        return {
          equip_sn: equip.equip_sn,
          equip_face_img: equip.small_icon,
          equip_name: equip.name,
          equip_type_desc: equip.static_desc,
          large_equip_desc: equip.desc,
          lock_type: equip.lock_type,

          src: equip.small_icon,
          data_equip_name: equip.name,
          data_equip_type: equip.type,
          data_equip_desc: equip.desc,
          data_equip_type_desc: equip.static_desc
        }
      }
    },
    get_using_fabao(target) {
      const fabao =
        typeof target === 'number' ? this.using_fabao.find(({ pos }) => pos === target) : target
      if (fabao) {
        return {
          equip_sn: fabao.type,
          equip_face_img: fabao.icon,
          equip_name: fabao.name,
          equip_type_desc: fabao.static_desc,
          large_equip_desc: fabao.desc,

          icon: fabao.icon,
          data_equip_name: fabao.name,
          data_equip_type: fabao.type,
          data_equip_desc: fabao.desc,
          data_equip_type_desc: fabao.static_desc
        }
      }
    },
    htmlEncode(str) {
      if (!str) return ''
      return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
    },
    toggle_display(index) {
      // 使用Vue响应式数据控制显示状态
      this.currentDisplayIndex = index
    },
    skillRows(skills, numPerLine) {
      if (!skills || skills.length === 0) return []
      const rows = []
      for (let i = 0; i < skills.length; i += numPerLine) {
        rows.push(skills.slice(i, i + numPerLine))
      }
      return rows
    },
    switchShenqiTab(index) {
      // 检查该套属性是否存在且有效
      const shenqiKey = 'shenqi' + (index + 1)
      const shenqiData = this.shenqi_components[shenqiKey]

      if (!shenqiData) {
        return // 如果该套属性不存在，不执行切换
      }

      // 先将所有套属性设置为非激活状态
      Object.keys(this.shenqi_components).forEach((key) => {
        if (this.shenqi_components[key]) {
          this.shenqi_components[key].actived = false
        }
      })

      // 将选中的套属性设置为激活状态
      this.shenqi_components[shenqiKey].actived = true
    },

    getClothesList(key) {
      return this[key] || []
    },
    getTotalAvatar() {
      if (this.basic_info.total_avatar) {
        return this.basic_info.total_avatar
      }
      return this.clothes.length < 20 ? this.clothes.length : '大于等于20'
    }
  }
}
</script>

<style scoped>
::v-deep .role-info-tabs .el-tabs__nav .el-tabs__item {
  padding: 0 !important;
  width: 98px;
  height: 26px;
  line-height: 26px;
  background: url(../../../public/assets/images/tag1.webp) no-repeat;
  text-align: center;
  float: left;
  margin-right: 3px;
  display: inline;
  color: #748da4;
  cursor: pointer;
}

::v-deep .role-info-tabs .el-tabs__nav .el-tabs__item.is-active {
  background: url(../../../public/assets/images/tag2.webp) no-repeat;
  color: #fff;
}

:global(.role-info-popover) {
  padding: 0 !important;
  background: transparent;
  box-shadow: none;
  border: none;
  font-size: 12px;
}

:global(.role-info-popover .tabCont) {
  padding: 0 !important;
  background: none;
}

:global(.role-info-popover .tabCont) {
  padding: 0 !important;
}

:global(.role-info-popover .el-tabs__header) {
  margin-bottom: 0 !important;
  border-bottom: 2px solid #fff;
}

:global(.role-info-popover .el-tabs__content) {
  padding: 12px;
  background: url(../../../public/assets/images/areabg.webp) repeat-y -100px;
  min-height: 510px;
}

:global(.role-info-popover .el-tabs__active-bar) {
  display: none !important;
}

:global(.shenqi-modal) {
  position: relative;
  top: unset;
  left: unset;
  margin-left: unset;
}

:global(.shenqi-info-popover) {
  padding: 0 !important;
  background: #0a1f28;
  border-color: #0a1f28;
}

:global(.shenqi-info-popover .popper__arrow::after) {
  border-bottom-color: #0a1f28 !important;
}

:global(.role-info-popover .popper__arrow::after) {
  border-right-color: #0a1f28 !important;
}
</style>
