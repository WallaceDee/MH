<template>
  <div>
    <el-card class="spider-config-card" shadow="never" style="margin-bottom: 10px;">
      <div slot="header" class="card-header">
        <div><span class="emoji-icon">🎯</span> 模拟目标装备</div>
      </div>

      <el-row type="flex" align="top" style="margin-bottom: 10px;">
        <el-row type="flex" justify="space-between" class="simulate-wrapper" style="flex-shrink: 0;">
          <el-col style="width: 120px; margin-right: 20px">
            <el-image style="width: 120px; height: 120px" :src="getImageUrl(equipment.equip_face_img, 'big')"
              fit="cover" referrerpolicy="no-referrer">
            </el-image>
          </el-col>
          <el-col>
            <p class="equip_desc_yellow" v-if="equipment.equip_name">{{ equipment.equip_name }}</p>
            <p v-html="parseEquipDesc(equipment.equip_type_desc?.replace(/#R/g, '<br />'), '#n')"></p>
            <p v-html="parseEquipDesc(equipment.large_equip_desc)"></p>
          </el-col>
        </el-row>
        <div style="margin-left: 10px; width: 60px;flex-shrink: 0;">
          <el-button type="success" size="mini" style="margin-bottom: 10px;" @click="takeSnapshot">拍照</el-button>
          <br>
          <SimilarEquipmentModal :equipment="equipment" :similar-data="similarEquipments"
            :valuation="equipmentValuation" placement="left-start" @show="loadSimilarEquipments">
            <el-button type="primary" size="mini">估价</el-button>
          </SimilarEquipmentModal>
        </div>
        <div style="margin-left: 10px; height: 300px; overflow-y: auto;width: 100%;">
          <el-tabs value="first">
            <el-tab-pane label="快照列表" name="first">
              <div v-if="snapshots.length === 0" style="color: #999; text-align: center; padding: 20px;">
                暂无快照，点击拍照按钮创建快照
              </div>
              <div v-else>
                <div v-for="snapshot in snapshots" :key="snapshot.id" style="margin-bottom: 10px;">
                  <el-tag type="success" style="cursor: pointer; margin-right: 5px;"
                    @click="showSnapshotDetail(snapshot)" @close="deleteSnapshot(snapshot.id)" closable>
                    {{ snapshot.name }}
                  </el-tag>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="异常数据" name="second">
              <div class="abnormal-data-container">
                <!-- 工具栏 -->
                <el-row class="abnormal-toolbar">
                  <el-select v-model="abnormalStatusFilter" placeholder="状态筛选" size="mini"
                    style="width: 120px; margin-right: 10px;">
                    <el-option label="全部" value=""></el-option>
                    <el-option label="待处理" value="pending"></el-option>
                    <el-option label="已解决" value="resolved"></el-option>
                    <el-option label="已忽略" value="ignored"></el-option>
                    <el-option label="调查中" value="investigating"></el-option>
                  </el-select>
                  <el-button type="primary" size="mini" @click="loadAbnormalData" :loading="loadingAbnormal">
                    <i class="el-icon-refresh"></i> 刷新
                  </el-button>
                  <el-button type="danger" size="mini" @click="clearAllAbnormal" style="margin-left: 10px;">
                    <i class="el-icon-delete"></i> 清空所有
                  </el-button>

                  <!-- 分页 -->
                  <div v-if="abnormalTotal > 0" class="abnormal-pagination">
                    <el-pagination @current-change="handleAbnormalPageChange" :current-page="abnormalPage"
                      :page-size="abnormalPageSize" :total="abnormalTotal" layout="total, prev, pager, next" small>
                    </el-pagination>
                  </div>
                </el-row>

                <!-- 异常装备列表 -->
                <el-empty v-if="abnormalEquipments.length === 0" description="暂无数据"></el-empty>
                <el-row v-else type="flex" style="flex-wrap: wrap;" class="abnormal-list">
                  <el-card v-for="item in abnormalEquipments" :key="item.id" class="abnormal-item" shadow="hover">
                    <div class="abnormal-header">
                      <div class="equipment-info">
                        <EquipmentImage :equipment="item.equipment_data" />
                        <div style="margin-left: 10px;">
                          <SimilarEquipmentModal :equipment="item.equipment_data" :similar-data="similarEquipments"
                            :valuation="equipmentValuation" placement="left-start" @show="loadSimilarEquipments">
                            <el-link href="javascript:void(0);" class="equipment-name">{{ item.equipment_data.equip_name
                              || '未知装备' }}</el-link>
                          </SimilarEquipmentModal>
                          <p class="equipment-sn">序列号: {{ item.equip_sn }}</p>
                        </div>
                      </div>
                      <div class="abnormal-actions">
                        <el-tag :type="getStatusTagType(item.status)" size="mini">{{ getStatusText(item.status)
                        }}</el-tag>
                        <el-dropdown @command="handleAbnormalAction" trigger="click" style="margin-left: 10px;">
                          <el-button type="text" size="mini">
                            <i class="el-icon-more"></i>
                          </el-button>
                          <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item :command="`view_${item.equip_sn}`">查看详情</el-dropdown-item>
                            <el-dropdown-item :command="`edit_${item.equip_sn}`">编辑状态</el-dropdown-item>
                            <el-dropdown-item :command="`delete_${item.equip_sn}`" divided>删除记录</el-dropdown-item>
                          </el-dropdown-menu>
                        </el-dropdown>
                      </div>
                    </div>

                    <div class="abnormal-content">
                      <div class="abnormal-details">
                        <p><strong>标记原因:</strong> {{ item.mark_reason }}</p>
                        <p v-if="item.notes"><strong>备注:</strong> {{ item.notes }}</p>
                        <p><strong>标记时间:</strong> {{ formatTime(item.mark_time) }}</p>
                      </div>
                    </div>
                  </el-card>
                </el-row>

              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-row>
    </el-card>
    <el-card class="spider-config-card" shadow="never">
      <div slot="header" class="card-header">
        <div><span class="emoji-icon">⚙️</span> 配置</div>
      </div>
      <el-form inline>
        <el-form-item label="装备类型">
          <el-select v-model="iType" placeholder="请选择" filterable>
            <el-option v-for="[type, equip] in filteredEquipInfo" :key="type" :label="equip.name" :value="type">
              <div style="
                  width: 400px;
                  background-color: #2c3e50 !important;
                  display: flex;
                  align-items: center;
                ">
                <el-image style="width: 34px; height: 34px; display: block; flex-shrink: 0"
                  :src="getImageUrl(type + '.gif', 'big')" fit="cover" referrerpolicy="no-referrer">
                </el-image>
                <p class="equip_desc_yellow" style="
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    padding-left: 5px;
                  ">
                  {{ equip.name }}-<span style="color: #fff; font-size: 12px">{{
                    equip.desc
                    }}</span>
                </p>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <div>
          <el-form-item label="等级">
            <el-input-number v-model="level" :min="0" :max="200" :step="5" />
          </el-form-item>
          <el-form-item label="五行">
            <el-select v-model="wu_xing" placeholder="请选择五行">
              <el-option label="金" value="金" />
              <el-option label="木" value="木" />
              <el-option label="水" value="水" />
              <el-option label="火" value="火" />
              <el-option label="土" value="土" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="耐久度">
          <el-input-number v-model="naijiu" :min="0" :max="1000" :step="100" />
        </el-form-item>
        <el-form-item label="修理失败次数">
          <el-input-number v-model="repair_fail" :min="0" :max="3" :step="1" />
        </el-form-item>
        <el-form-item>
          <template slot="label">
            属性 <el-button type="text" @click="clearAttrs">清空属性</el-button>
          </template>
          <el-form-item v-for="item in addonOptions" :key="item[0]" :label="item[1]">
            <el-input-number v-model="addon[item[0]]" controls-position="right" />
          </el-form-item>
        </el-form-item>
        <div>
          <el-form-item label="锻炼等级">
            <el-input-number v-model="gemLevel" :min="0" :max="100" :step="1" />
          </el-form-item>
          <el-form-item label="镶嵌宝石">
            <el-select v-model="gemType" placeholder="镶嵌宝石" clearable filterable multiple style="width: 100px">
              <el-option v-for="(gemName, value) in gems_name" :key="value" :value="gemName" :label="gemName">
                <el-row type="flex" justify="space-between">
                  <el-col style="width: 34px; height: 34px; margin-right: 10px">
                    <el-image style="width: 34px; height: 34px; cursor: pointer"
                      :src="getImageUrl(gem_image[value] + '.gif')" fit="cover" referrerpolicy="no-referrer">
                    </el-image>
                  </el-col>
                  <el-col style="width: 100px">
                    {{ gemName }}
                  </el-col>
                </el-row>
              </el-option>
            </el-select>
          </el-form-item>
        </div>
        <div v-if="is_lingshi_equip">
          <div v-for="(attr, index) in attrs_list" :key="index">
            <el-form-item label="属性">
              <el-select v-model="attrs_list[index].attr_type" placeholder="请选择属性" clearable
                @change="(val) => changeAttrTypeRange(val, index)">
                <el-option v-for="(range, key, index) in currentLevelLingshiConfig" :key="index" :label="key"
                  :value="key" :data-range="JSON.stringify(range)">
                </el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="属性值">
              <el-input-number v-model="attrs_list[index].attr_value" :min="attrs_list[index].range[0]"
                :max="attrs_list[index].range[1]" :step="1" />
            </el-form-item>
          </div>
        </div>
        <template v-else>
          <el-form-item label="特技">
            <el-select v-model="special_skill" placeholder="请选择特技" clearable filterable>
              <el-option v-for="[value, label] in equip_special_skills" :key="value" :label="label" :value="label">
              </el-option>
            </el-select>
          </el-form-item>
          <br>
        </template>
        <el-form-item label="特效">
          <el-select v-model="special_effect" placeholder="请选择特效" multiple clearable filterable>
            <el-option v-for="(label, value) in equip_special_effect" :key="value"
              :label="value === '1' ? label + '/超级简易' : label" :value="label">
            </el-option>
          </el-select>
        </el-form-item>
        <br>
        <template v-if="!is_lingshi_equip">
          <el-form-item label="套装">
            <el-cascader :options="suitOptions" placeholder="请选择套装效果" separator="" clearable filterable
              @change="handleSuitChange" />
          </el-form-item>
          <br>
          <el-form-item label="开运孔数">
            <el-input-number v-model="kaiyun_num" :min="0" :max="10" :step="1" />
            双开运孔:<el-switch v-model="isDoubleKaiyun"></el-switch>
          </el-form-item>

          <el-form-item label="熔炼">
            <el-form-item v-for="item in filteredRonglianOptions" :key="item[0]" :label="item[1]">
              <el-input-number v-model="ronglian_addon[item[0]]" controls-position="right" />
            </el-form-item>
          </el-form-item>
        </template>
      </el-form>
    </el-card>

    <!-- 快照详情弹窗 -->
    <el-dialog title="快照详情" :visible.sync="snapshotDialogVisible" width="600px"
      :before-close="() => { snapshotDialogVisible = false; currentSnapshot = null; }">
      <div v-if="currentSnapshot" class="snapshot-detail">
        <div class="snapshot-header">
          <h3>{{ currentSnapshot.name }}</h3>
          <p class="snapshot-time">创建时间：{{ new Date(currentSnapshot.timestamp).toLocaleString() }}</p>
        </div>

        <div class="equipment-preview">
          <el-row type="flex" align="top">
            <el-col style="width: 120px; margin-right: 20px">
              <el-image style="width: 120px; height: 120px"
                :src="getImageUrl(currentSnapshot.equipment.equip_face_img, 'big')" fit="cover"
                referrerpolicy="no-referrer">
              </el-image>
            </el-col>
            <el-col>
              <p class="equip_desc_yellow" v-if="currentSnapshot.equipment.equip_name">
                {{ currentSnapshot.equipment.equip_name }}
              </p>
              <p v-html="parseEquipDesc(currentSnapshot.equipment.equip_type_desc?.replace(/#R/g, '<br />'), '#n')"></p>
              <p v-html="parseEquipDesc(currentSnapshot.equipment.large_equip_desc)"></p>
            </el-col>
          </el-row>
        </div>
      </div>

      <span slot="footer" class="dialog-footer">
        <el-button @click="snapshotDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="restoreSnapshot">恢复此快照</el-button>
      </span>
    </el-dialog>

    <!-- 异常状态编辑对话框 -->
    <AbnormalStatusEditDialog :visible="statusEditDialogVisible" :equip-sn="currentEditEquipSn"
      :current-status="currentEditStatus" @success="handleStatusEditSuccess" @close="handleStatusEditClose" />
  </div>
</template>

<script>
import { commonMixin } from '@/utils/mixins/commonMixin'
import SimilarEquipmentModal from '@/components/SimilarEquipmentModal.vue'
import EquipmentImage from '../components/EquipmentImage.vue'
import AbnormalStatusEditDialog from '../components/AbnormalStatusEditDialog.vue'
const suitOptions = []

if (window.AUTO_SEARCH_CONFIG) {
  // 附加状态
  if (window.AUTO_SEARCH_CONFIG.suit_added_status) {
    const addedStatusOptions = Object.entries(
      window.AUTO_SEARCH_CONFIG.suit_added_status
    ).map(([, label]) => ({
      value: `附加状态${label}`,
      label: label
    }))

    if (addedStatusOptions.length > 0) {
      suitOptions.push({
        value: '附加状态',
        label: '附加状态',
        children: addedStatusOptions
      })
    }
  }

  // 追加法术
  if (window.AUTO_SEARCH_CONFIG.suit_effects) {
    const suitEffectsOptions = Object.entries(window.AUTO_SEARCH_CONFIG.suit_effects).map(
      ([, label]) => ({
        value: `追加法术${label}`,
        label: label
      })
    )

    if (suitEffectsOptions.length > 0) {
      suitOptions.push({
        value: '追加法术',
        label: '追加法术',
        children: suitEffectsOptions
      })
    }
  }

  // 变身术
  if (window.AUTO_SEARCH_CONFIG.suit_transform_skills) {
    const transformSkillsOptions = Object.entries(
      window.AUTO_SEARCH_CONFIG.suit_transform_skills
    ).map(([, label]) => ({
      value: `变身术之${label}`,
      label: label
    }))

    if (transformSkillsOptions.length > 0) {
      suitOptions.push({
        value: '变身术之',
        label: '变身术之',
        children: transformSkillsOptions
      })
    }
  }

  // 变化咒
  if (window.AUTO_SEARCH_CONFIG.suit_transform_charms) {
    const transformCharmsOptions = Object.entries(
      window.AUTO_SEARCH_CONFIG.suit_transform_charms
    ).map(([, label]) => ({
      value: `变化咒之${label}`,
      label: label
    }))

    if (transformCharmsOptions.length > 0) {
      suitOptions.push({
        value: '变化咒之',
        label: '变化咒之',
        children: transformCharmsOptions
      })
    }
  }
}
export default {
  name: 'EquipmentDescCreator',
  components: {
    SimilarEquipmentModal,
    EquipmentImage,
    AbnormalStatusEditDialog
  },
  mixins: [commonMixin],
  data() {
    return {
      suitOptions,
      // 添加localStorage key
      storageKey: 'equipment_desc_creator_data',
      // 添加快照相关的storage key
      snapshotStorageKey: 'equipment_snapshots',
      // 添加快照列表数据
      snapshots: [],
      // 添加快照详情弹窗控制
      snapshotDialogVisible: false,
      currentSnapshot: null,
      lingshiPerGemAdd: {
        伤害: 4,
        法术伤害结果: 3,
        物理暴击等级: 4,
        固定伤害: 4,
        封印命中等级: 4,
        抗法术暴击等级: 8,
        抗物理暴击等级: 8,
        抵抗封印等级: 8,
        格挡值: 8,
        气血: 28,
        气血回复效果: 4,
        治疗能力: 3,
        法术伤害: 4,
        法术暴击等级: 4,
        法术防御: 8,
        狂暴等级: 3,
        穿刺等级: 4,
        速度: 3,
        防御: 8
      },
      lingshiConfig: {},
      similarEquipments: null,
      equipmentValuation: null,
      equip_info: window.CBG_GAME_CONFIG.equip_info,
      equip_special_skills: window.AUTO_SEARCH_CONFIG.equip_special_skills,
      equip_special_effect: window.AUTO_SEARCH_CONFIG.equip_special_effect,

      iType: '1007',
      level: 0,
      wu_xing: '土',
      naijiu: 500,
      repair_fail: 0,
      gemLevel: 0,
      suit_effect: '',
      gemType: [],
      special_skill: '',
      special_effect: [],
      creator: '榄核小华为你',
      kaiyun_num: 0,
      isDoubleKaiyun: false,
      attrs_list: [
        {
          attr_type: '',
          attr_value: 0,
          range: [0, 0]
        },
        {
          attr_type: '',
          attr_value: 0,
          range: [0, 0]
        },
        {
          attr_type: '',
          attr_value: 0,
          range: [0, 0]
        }
      ],
      addon: {
        tizhi: 0,
        naili: 0,
        moli: 0,
        minjie: 0,
        liliang: 0,
        wakan: 0,
        magic_damage: 0,
        magic_defence: 0,
        mofa: 0,
        mingzhong: 0,
        shanghai: 0,
        speed: 0,
        defence: 0,
        hp: 0,
        fengyin: 0,
        anti_fengyin: 0,
      },
      ronglian_addon: {
        tizhi: 0,
        naili: 0,
        moli: 0,
        minjie: 0,
        liliang: 0,
        defence: 0,
        hp: 0,
        wakan: 0,
        magic_defence: 0,
        mofa: 0
      },
      addonOptions: [
        ['shanghai', '伤害'],
        ['mingzhong', '命中'],
        ['defence', '防御'],
        ['hp', '气血'],
        ['speed', '速度'],
        ['wakan', '灵力'],
        ['tizhi', '体质'],
        ['moli', '魔力'],
        ['liliang', '力量'],
        ['naili', '耐力'],
        ['minjie', '敏捷'],
        ['magic_damage', '法术伤害'],
        ['magic_defence', '法防'],
        ['mofa', '魔法'],
        ['fengyin', '封印命中等级'],
        ['anti_fengyin', '抵抗封印等级'],
      ],
      features: {},
      currentKindid: 0,
      gems_name: window.AUTO_SEARCH_CONFIG.gems_name,
      gem_image: {
        1: '4011',
        2: '4002',
        3: '4012',
        4: '4004',
        5: '4003',
        6: '4010',
        7: '4005',
        8: '4007',
        9: '4006',
        10: '4008',
        11: '4009',
        12: '1108_4249',
        4244: '4244',
        '755_4036': '755_4036',
        '756_4037': '756_4037',
        '757_4038': '757_4038'
      },
      // 异常装备相关数据
      abnormalEquipments: [],
      abnormalPage: 1,
      abnormalPageSize: 10,
      abnormalTotal: 0,
      abnormalStatusFilter: '',
      loadingAbnormal: false,
      // 状态编辑对话框
      statusEditDialogVisible: false,
      currentEditEquipSn: '',
      currentEditStatus: ''
    }
  },
  computed: {
    // 添加计算属性来过滤装备信息，解决linter错误
    filteredEquipInfo() {
      return Object.entries(this.equip_info).filter(([, equip]) => {
        const level_match = equip.desc.match(/等级\s*(\d+)/)
        let level = 60
        if (level_match) {
          level = parseInt(level_match[1])
        }
        return equip.desc && equip.desc.indexOf('等级') !== -1 && equip.desc.indexOf('召唤兽') === -1 && level >= 60
      }
      )
    },
    // 添加计算属性来过滤熔炼属性选项，解决linter错误
    filteredRonglianOptions() {
      return this.addonOptions.filter(item =>
        this.ronglian_addon[item[0]] !== undefined
      )
    },
    currentLevelLingshiConfig() {
      return this.lingshiConfig[this.level]?.attrs || this.lingshiConfig['60']?.attrs || {}
    },
    is_lingshi_equip() {
      return window.is_lingshi_equip(this.currentKindid)
    },
    is_shoes_equip() {
      return window.is_shoes_equip(this.currentKindid)
    },
    is_belt_equip() {
      return window.is_belt_equip(this.currentKindid)
    },
    is_necklace_equip() {
      return window.is_necklace_equip(this.currentKindid)
    },
    is_helmet_equip() {
      return window.is_helmet_equip(this.currentKindid)
    },
    is_weapon_equip() {
      return window.is_weapon_equip(this.currentKindid)
    },
    is_cloth_equip() {
      return window.is_cloth_equip(this.currentKindid)
    },
    equip_params() {
      return {
        type: this.iType * 1,
        large_equip_desc: this.large_equip_desc
      }
    },
    // equip_type_desc
    equip_desc() {
      const target = this.equip_info[this.iType]
      if (target) {
        return {
          equip_name: target.name,
          equip_type_desc: target.desc
        }
      }
      return {
        equip_name: '',
        equip_type_desc: ''
      }
    },
    equip_face_img() {
      return this.iType + '.gif'
    },
    equipment() {
      return {
        cDesc: this.large_equip_desc,
        iType: this.iType * 1,
        large_equip_desc: this.large_equip_desc,
        equip_face_img: this.equip_face_img,
        ...this.equip_desc
      }
    },
    large_equip_desc() {
      let desc = ''
      let descList = ['']
      if (this.is_lingshi_equip) {
        //等级 100#r伤害 +21#r耐久度 81  修理失败 3次
        // #r精炼等级 3
        // #r#G速度 +12 #cEE82EE[+9]
        // #r#G治疗能力 +8 #cEE82EE[+9]
        // #r#G物理暴击等级 +14 #cEE82EE[+12]
        // #r#W制造者：★↑小龙↑★强化打造#
        const level_desc = `等级 ${this.level}`
        desc += level_desc
        let main_attr_desc = ''
        const main_attr = this.addonOptions.find(([addon_key]) => {
          if (this.currentKindid === 61 && (addon_key === 'shanghai' || addon_key === 'defence')) {
            return this.addon[addon_key] > 0
          } else if (this.currentKindid === 62 && (addon_key === 'magic_damage' || addon_key === 'magic_defence')) {
            return this.addon[addon_key] > 0
          } else if (this.currentKindid === 63 && (addon_key === 'fengyin' || addon_key === 'anti_fengyin')) {
            return this.addon[addon_key] > 0
          }else if (this.currentKindid === 64 && (addon_key === 'speed')) {
            return this.addon[addon_key] > 0
          }
          return false
        })

        if (main_attr) {
          let main_attr_label = main_attr[1]
          if (main_attr_label === '法防') {
            main_attr_label = '法术防御'
          }
          main_attr_desc = `${main_attr_label} +${this.addon[main_attr[0]]}`
          desc += '#r' + main_attr_desc
        }

        //耐久行
        let naijiu_desc = `耐久度 ${this.naijiu}`
        if (this.repair_fail > 0) {
          naijiu_desc += ` 修理失败 ${this.repair_fail}次`
        }
        desc += '#r' + naijiu_desc
        descList.push(naijiu_desc)
        //特效行 #c4DBAF4特效：#c4DBAF4精致#Y #c4DBAF4简易#Y
        if (this.special_effect.length > 0) {
          let special_effect_desc = '#c4DBAF4特效：'
          this.special_effect.forEach((effect, index) => {
            if (index > 0) {
              special_effect_desc += ' '
            }
            if (effect === '无级别') {
              effect += '超级简易'
            }
            special_effect_desc += `#c4DBAF4${effect}#Y`
          })
          desc += '#r' + special_effect_desc
          descList.push(special_effect_desc)
        }
        //宝石行
        if (this.gemLevel > 0) {
          const gem_desc = `精炼等级 ${this.gemLevel}`
          desc += '#r' + gem_desc
          descList.push(gem_desc)
        }
        //属性行
        // #r#G速度 +12 #cEE82EE[+9]
        this.attrs_list.forEach((attr) => {
          if (attr.attr_type) {
            let attr_desc = `#G${attr.attr_type} +${attr.attr_value}`
            if (this.gemLevel > 0) {
              const currentAdd = (this.lingshiPerGemAdd[attr.attr_type] || 0) * this.gemLevel
              attr_desc += ` #cEE82EE[+${currentAdd}]`
            }
            desc += '#r' + attr_desc
            descList.push(attr_desc)
          }
        })

        //制造者信息
        const creator = `#W制造者：${this.creator}强化打造#`
        desc += '#r' + creator
        descList.push(creator)
      } else {
        //等级行
        let level_desc = `等级 ${this.level}`
        if (this.is_weapon_equip || this.is_cloth_equip || this.is_shoes_equip) {
          level_desc += `  五行 ${this.wu_xing}`
        }
        desc += '#r' + level_desc
        descList.push(level_desc)

        //武器伤害命中行
        if (this.is_weapon_equip) {
          const shanghai_mingzhong_desc = `命中 ${this.addon.mingzhong} 伤害 ${this.addon.shanghai}`
          desc += '#r' + shanghai_mingzhong_desc
          descList.push(shanghai_mingzhong_desc)
        }

        //防御行
        if (
          this.is_cloth_equip ||
          this.is_helmet_equip ||
          this.is_belt_equip ||
          this.is_shoes_equip ||
          this.is_helmet_equip
        ) {
          const defence_desc = `防御 +${this.addon.defence}`
          desc += '#r' + defence_desc
          descList.push(defence_desc)
        }
        if (this.is_helmet_equip) {
          // 魔法 +65
          const mofa_desc = ` 魔法 +${this.addon.mofa}`
          desc += mofa_desc

          const currentLine = descList.pop()
          descList.push(currentLine + mofa_desc)
        }
        if (this.is_belt_equip || this.is_cloth_equip) {
          const hp_desc = ` 气血 +${this.addon.hp}`
          desc += hp_desc

          const currentLine = descList.pop()
          descList.push(currentLine + hp_desc)
        }
        if (this.is_shoes_equip) {
          const hp_desc = ` 敏捷 +${this.addon.minjie}`
          desc += hp_desc

          const currentLine = descList.pop()
          descList.push(currentLine + hp_desc)
        }

        //灵力行
        if (this.is_necklace_equip) {
          const wakan_desc = `灵力 +${this.addon.wakan}`
          desc += '#r' + wakan_desc
          descList.push(wakan_desc)
        }

        //耐久行
        let naijiu_desc = `耐久度 ${this.naijiu}`
        if (this.repair_fail > 0) {
          naijiu_desc += ` 修理失败 ${this.repair_fail}次`
        }
        desc += '#r' + naijiu_desc
        descList.push(naijiu_desc)

        //宝石行
        if (this.gemLevel > 0) {
          const gem_desc = `锻炼等级 ${this.gemLevel}  镶嵌宝石 ${this.gemType.join('、 ')}`
          desc += '#r' + gem_desc
          descList.push(gem_desc)
        }
        //属性加成行
        let addon_desc = '#G'
        this.addonOptions
          .filter(([addon_key]) => {
            if (this.is_weapon_equip && (addon_key === 'shanghai' || addon_key === 'mingzhong')) {
              return false
            }
            if (this.is_necklace_equip && addon_key === 'wakan') {
              return false
            }
            if (this.is_helmet_equip && (addon_key === 'defence' || addon_key === 'mofa')) {
              return false
            }
            if (this.is_belt_equip && (addon_key === 'defence' || addon_key === 'hp')) {
              return false
            }
            if (this.is_shoes_equip && (addon_key === 'minjie' || addon_key === 'defence')) {
              return false
            }
            if (this.is_cloth_equip && (addon_key === 'hp' || addon_key === 'defence')) {
              return false
            }
            if (this.addon[addon_key] !== 0 && this.addon[addon_key] !== undefined) {
              return true
            }
          })
          .forEach(([addon_key, label], index) => {
            if (index > 0) {
              addon_desc += ' '
            }
            addon_desc += `#G${label} ${this.addon[addon_key] > 0 ? `+${this.addon[addon_key]}` : this.addon[addon_key]
              }#Y`
          })
        desc += '#r' + addon_desc
        descList.push(addon_desc)

        //特技行
        if (this.special_skill) {
          const special_skill_desc = `#c4DBAF4特技：#c4DBAF4${this.special_skill}#Y#Y`
          desc += '#r' + special_skill_desc
          descList.push(special_skill_desc)
        }

        //特效行 #c4DBAF4特效：#c4DBAF4精致#Y #c4DBAF4简易#Y
        if (this.special_effect.length > 0) {
          let special_effect_desc = '#c4DBAF4特效：'
          this.special_effect.forEach((effect, index) => {
            if (index > 0) {
              special_effect_desc += ' '
            }
            if (effect === '无级别') {
              effect += '限制'
            }
            special_effect_desc += `#c4DBAF4${effect}#Y`
          })
          desc += '#r' + special_effect_desc
          descList.push(special_effect_desc)
        }

        //套装行 #c4DBAF4套装效果：变身术之修罗傀儡妖#Y#Y
        if (this.suit_effect) {
          let suit_effect_desc = `#c4DBAF4套装效果：${this.suit_effect}#Y#Y`
          desc += '#r' + suit_effect_desc
          descList.push(suit_effect_desc)
        }

        if (this.kaiyun_num > 0) {
          //开运行'#G开运孔数：5孔/5孔#G'
          let kaiyun_desc = `#G开运孔数：${this.kaiyun_num}孔/${this.kaiyun_num}孔#G`
          if (this.isDoubleKaiyun) {
            kaiyun_desc += ` (双${this.kaiyun_num}孔)`
          }
          desc += '#r' + kaiyun_desc
          descList.push(kaiyun_desc)
        }
        //制造者信息
        const creator = `#W制造者：${this.creator}强化打造#Y`
        desc += '#r' + creator
        descList.push(creator)

        //熔炼行
        //制造者：poison′阿狸强化打造#Y#r#Y熔炼效果：#r#Y#r-1体质 +3耐力 #r+26防御#Y
        let ronglian_desc = ''
        const ronglian_list = []
        for (let key in this.ronglian_addon) {
          if (this.ronglian_addon[key] !== 0 && this.ronglian_addon[key] !== undefined) {
            ronglian_list.push(
              `${this.ronglian_addon[key] > 0
                ? `+${this.ronglian_addon[key]}`
                : this.ronglian_addon[key]
              }${this.addonOptions.find((item) => item[0] === key)[1]}`
            )
          }
        }
        ronglian_list.forEach((str, index) => {
          if (index > 0) {
            ronglian_desc += ' '
          }
          if (index % 2 === 0) {
            ronglian_desc += '#r'
          }
          ronglian_desc += str
        })
        if (ronglian_list.length > 0) {
          ronglian_desc = `#Y熔炼效果：#r#Y${ronglian_desc}#Y`
          desc += '#r' + ronglian_desc
          descList.push(ronglian_desc)
        }
      }
      console.log(desc, 'desc')
      console.log(descList.join('#r'), 'descList.join(\'#r\')')
      console.log(desc === descList.join('#r'))
      return desc
    }
  },
  watch: {
    // 监听所有表单数据变化，自动保存到localStorage
    iType: { handler: 'saveToLocalStorage', deep: true },
    level: { handler: 'saveToLocalStorage', deep: true },
    wu_xing: { handler: 'saveToLocalStorage', deep: true },
    naijiu: { handler: 'saveToLocalStorage', deep: true },
    repair_fail: { handler: 'saveToLocalStorage', deep: true },
    gemLevel: { handler: 'saveToLocalStorage', deep: true },
    gemType: { handler: 'saveToLocalStorage', deep: true },
    special_skill: { handler: 'saveToLocalStorage', deep: true },
    suit_effect: { handler: 'saveToLocalStorage', deep: true },
    special_effect: { handler: 'saveToLocalStorage', deep: true },
    kaiyun_num: { handler: 'saveToLocalStorage', deep: true },
    isDoubleKaiyun: { handler: 'saveToLocalStorage', deep: true },
    attrs_list: { handler: 'saveToLocalStorage', deep: true },
    addon: { handler: 'saveToLocalStorage', deep: true },
    ronglian_addon: { handler: 'saveToLocalStorage', deep: true },
    equip_params: {
      handler(newVal) {
        this.$api.equipment
          .extractFeatures({
            equipment_data: newVal,
            data_type: 'equipment'
          })
          .then((res) => {
            this.features = res.data.features
            this.currentKindid = res.data.kindid
          })
      },
      immediate: true
    },
    equip_desc: {
      handler(val) {
        // 在描述中尝试提取等级
        const desc = val.equip_type_desc
        const level_match = desc.match(/等级\s*(\d+)/)
        if (level_match) {
          this.level = parseInt(level_match[1])
        }
      },
      immediate: true
    }
  },
  methods: {
    clearAttrs() {
      this.addon = {
        tizhi: 0,
        naili: 0,
        moli: 0,
        minjie: 0,
        liliang: 0,
        wakan: 0,
        magic_damage: 0,
        magic_defence: 0,
        mofa: 0,
        mingzhong: 0,
        shanghai: 0,
        speed: 0,
        defence: 0,
        hp: 0,
        fengyin: 0,
        anti_fengyin: 0,
      }
    },
    handleSuitChange(value) {
      this.suit_effect = value[1]
    },
    // 保存数据到localStorage
    saveToLocalStorage() {
      try {
        const dataToSave = {
          iType: this.iType,
          level: this.level,
          wu_xing: this.wu_xing,
          naijiu: this.naijiu,
          repair_fail: this.repair_fail,
          gemLevel: this.gemLevel,
          gemType: this.gemType,
          special_skill: this.special_skill,
          special_effect: this.special_effect,
          kaiyun_num: this.kaiyun_num,
          isDoubleKaiyun: this.isDoubleKaiyun,
          attrs_list: this.attrs_list,
          addon: this.addon,
          ronglian_addon: this.ronglian_addon,
          suit_effect: this.suit_effect
        }
        localStorage.setItem(this.storageKey, JSON.stringify(dataToSave))
      } catch (error) {
        console.error('保存数据到localStorage失败:', error)
      }
    },

    // 从localStorage加载数据
    loadFromLocalStorage() {
      try {
        const savedData = localStorage.getItem(this.storageKey)
        if (savedData) {
          const data = JSON.parse(savedData)

          // 恢复所有表单数据
          if (data.iType !== undefined) this.iType = data.iType
          if (data.level !== undefined) this.level = data.level
          if (data.wu_xing !== undefined) this.wu_xing = data.wu_xing
          if (data.naijiu !== undefined) this.naijiu = data.naijiu
          if (data.repair_fail !== undefined) this.repair_fail = data.repair_fail
          if (data.gemLevel !== undefined) this.gemLevel = data.gemLevel
          if (data.gemType !== undefined) this.gemType = data.gemType
          if (data.special_skill !== undefined) this.special_skill = data.special_skill
          if (data.special_effect !== undefined) this.special_effect = data.special_effect
          if (data.kaiyun_num !== undefined) this.kaiyun_num = data.kaiyun_num
          if (data.isDoubleKaiyun !== undefined) this.isDoubleKaiyun = data.isDoubleKaiyun
          if (data.attrs_list !== undefined) this.attrs_list = data.attrs_list
          if (data.addon !== undefined) this.addon = data.addon
          if (data.ronglian_addon !== undefined) this.ronglian_addon = data.ronglian_addon

          console.log('从localStorage恢复数据成功')
        }
      } catch (error) {
        console.error('从localStorage加载数据失败:', error)
      }
    },

    // 清除localStorage缓存
    clearLocalStorage() {
      try {
        localStorage.removeItem(this.storageKey)
        console.log('localStorage缓存已清除')
        this.$notify.success({
          title: '提示',
          message: 'localStorage缓存已清除'
        })
      } catch (error) {
        console.error('清除localStorage缓存失败:', error)
        this.$notify.error({
          title: '提示',
          message: '清除缓存失败'
        })
      }
    },

    changeAttrTypeRange(type, index) {
      const range = this.currentLevelLingshiConfig[type]
      this.$set(this.attrs_list[index], 'range', range)
    },
    getLingshiData() {
      this.$api.equipment.getLingshiData().then((res) => {
        this.lingshiConfig = res.data
      })
    },
    // 加载相似装备
    async loadSimilarEquipments(equipment) {
      // 每次都重新计算，不使用缓存
      this.equipmentValuation = null
      this.similarEquipments = null
      await this.loadEquipmentValuation(equipment, 0.8)
    },

    // 统一的装备估价加载方法
    async loadEquipmentValuation(equipment, similarityThreshold) {
      try {
        // 获取估价信息（包含相似装备）
        const valuationResponse = await this.$api.equipment.getEquipmentValuation({
          equipment_data: equipment,
          strategy: 'fair_value',
          similarity_threshold: similarityThreshold,
          max_anchors: 30
        })

        // 处理估价响应
        if (valuationResponse.code === 200) {
          const data = valuationResponse.data
          this.equipmentValuation = data

          const {
            data: { anchors }
          } = await this.$api.equipment.findEquipmentAnchors({
            equipment_data: equipment,
            similarity_threshold: similarityThreshold,
            max_anchors: 30
          })
          // 从估价结果中提取相似装备信息
          if (data.anchors && data.anchors.length > 0) {
            this.similarEquipments = {
              anchor_count: data.anchor_count,
              similarity_threshold: data.similarity_threshold,
              anchors: anchors,
              statistics: {
                price_range: {
                  min: Math.min(...data.anchors.map((a) => a.price || 0)),
                  max: Math.max(...data.anchors.map((a) => a.price || 0))
                },
                similarity_range: {
                  min: Math.min(...data.anchors.map((a) => a.similarity || 0)),
                  max: Math.max(...data.anchors.map((a) => a.similarity || 0)),
                  avg:
                    data.anchors.reduce((sum, a) => sum + (a.similarity || 0), 0) /
                    data.anchors.length
                }
              }
            }
            return
          }
        }
        this.similarEquipments = {
          anchor_count: 0,
          similarity_threshold: similarityThreshold,
          anchors: [],
          statistics: {
            price_range: { min: 0, max: 0 },
            similarity_range: { min: 0, max: 0, avg: 0 }
          }
        }
        console.log('估价和相似装备数据:', valuationResponse.data)
      } catch (error) {
        console.error('加载相似装备或估价失败:', error)
      }
    },
    parseEquipDesc(desc, default_style = '#Y') {
      if (!desc) return ''
      if (typeof window.parse_style_info === 'function') {
        return window.parse_style_info(desc, default_style)
      }
      return desc
    },
    takeSnapshot() {
      // 弹出输入框让用户输入快照名称
      this.$prompt('请输入快照名称', '创建快照', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /\S+/,
        inputErrorMessage: '快照名称不能为空'
      }).then(({ value }) => {
        const snapshotData = {
          id: Date.now(),
          name: value,
          timestamp: new Date().toISOString(),
          // 保存当前所有装备配置数据
          equipment: {
            iType: this.iType,
            level: this.level,
            wu_xing: this.wu_xing,
            naijiu: this.naijiu,
            repair_fail: this.repair_fail,
            gemLevel: this.gemLevel,
            gemType: [...this.gemType],
            special_skill: this.special_skill,
            special_effect: [...this.special_effect],
            kaiyun_num: this.kaiyun_num,
            isDoubleKaiyun: this.isDoubleKaiyun,
            attrs_list: JSON.parse(JSON.stringify(this.attrs_list)),
            addon: { ...this.addon },
            ronglian_addon: { ...this.ronglian_addon },
            suit_effect: this.suit_effect,
            // 保存装备显示信息
            equip_name: this.equipment.equip_name,
            equip_type_desc: this.equipment.equip_type_desc,
            equip_face_img: this.equipment.equip_face_img,
            large_equip_desc: this.large_equip_desc
          }
        }

        this.snapshots.unshift(snapshotData) // 新快照放在最前面
        this.saveSnapshotsToStorage()
        this.$notify.success({
          title: '提示',
          message: `快照 "${value}" 已创建！`
        })
      }).catch(() => {
        // 用户取消输入
      })
    },
    showSnapshotDetail(snapshot) {
      this.currentSnapshot = snapshot
      this.snapshotDialogVisible = true
    },
    deleteSnapshot(id) {
      this.snapshots = this.snapshots.filter(s => s.id !== id)
      this.saveSnapshotsToStorage()
      this.$notify.success({
        title: '提示',
        message: '快照已删除！'
      })
    },
    restoreSnapshot() {
      if (this.currentSnapshot) {
        // 恢复所有装备配置数据
        this.iType = this.currentSnapshot.equipment.iType
        this.level = this.currentSnapshot.equipment.level
        this.wu_xing = this.currentSnapshot.equipment.wu_xing
        this.naijiu = this.currentSnapshot.equipment.naijiu
        this.repair_fail = this.currentSnapshot.equipment.repair_fail
        this.gemLevel = this.currentSnapshot.equipment.gemLevel
        this.gemType = [...this.currentSnapshot.equipment.gemType]
        this.special_skill = this.currentSnapshot.equipment.special_skill
        this.special_effect = [...this.currentSnapshot.equipment.special_effect]
        this.kaiyun_num = this.currentSnapshot.equipment.kaiyun_num
        this.isDoubleKaiyun = this.currentSnapshot.equipment.isDoubleKaiyun
        this.attrs_list = JSON.parse(JSON.stringify(this.currentSnapshot.equipment.attrs_list))
        this.addon = { ...this.currentSnapshot.equipment.addon }
        this.ronglian_addon = { ...this.currentSnapshot.equipment.ronglian_addon }
        this.suit_effect = this.currentSnapshot.equipment.suit_effect

        // 关闭弹窗并清空当前快照
        this.snapshotDialogVisible = false
        this.currentSnapshot = null

        this.$notify.success('快照已恢复！')
      }
    },
    saveSnapshotsToStorage() {
      localStorage.setItem(this.snapshotStorageKey, JSON.stringify(this.snapshots))
    },
    // 异常数据相关方法
    async loadAbnormalData() {
      this.loadingAbnormal = true
      try {
        const params = {
          page: this.abnormalPage,
          page_size: this.abnormalPageSize,
          status: this.abnormalStatusFilter
        }
        const response = await this.$api.equipment.getAbnormalEquipmentList(params)
        if (response.code === 200) {
          this.abnormalEquipments = response.data.items || []
          this.abnormalTotal = response.data.total || 0
        } else {
          this.$notify.error(response.message || '加载异常装备数据失败')
        }
      } catch (error) {
        console.error('加载异常装备数据失败:', error)
        this.$notify.error('加载异常装备数据失败')
      } finally {
        this.loadingAbnormal = false
      }
    },
    handleAbnormalPageChange(val) {
      this.abnormalPage = val
      this.loadAbnormalData()
    },
    clearAllAbnormal() {
      this.$confirm('确定要清空所有异常装备记录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        // 这里可以实现批量删除的逻辑，暂时显示提示
        this.$notify.info('批量删除功能待实现')
        this.loadAbnormalData() // 刷新列表
      }).catch(() => {
        // 用户取消
      })
    },
    handleAbnormalAction(command) {
      const [action, equip_sn] = command.split('_')
      if (action === 'view') {
        this.showSnapshotDetail({
          id: Date.now(), // 模拟ID
          name: `异常装备-${equip_sn}`,
          timestamp: new Date().toISOString(),
          equipment: {
            iType: this.iType,
            level: this.level,
            wu_xing: this.wu_xing,
            naijiu: this.naijiu,
            repair_fail: this.repair_fail,
            gemLevel: this.gemLevel,
            gemType: [...this.gemType],
            special_skill: this.special_skill,
            special_effect: [...this.special_effect],
            kaiyun_num: this.kaiyun_num,
            isDoubleKaiyun: this.isDoubleKaiyun,
            attrs_list: JSON.parse(JSON.stringify(this.attrs_list)),
            addon: { ...this.addon },
            ronglian_addon: { ...this.ronglian_addon },
            suit_effect: this.suit_effect,
            equip_name: this.equipment.equip_name,
            equip_type_desc: this.equipment.equip_type_desc,
            equip_face_img: this.equipment.equip_face_img,
            large_equip_desc: this.large_equip_desc
          }
        })
      } else if (action === 'edit') {
        // 打开状态编辑对话框
        this.currentEditEquipSn = equip_sn
        this.currentEditStatus = this.abnormalEquipments.find(item => item.equip_sn === equip_sn)?.status || 'pending'
        this.statusEditDialogVisible = true
      } else if (action === 'delete') {
        this.$confirm(`确定要删除序列号为 ${equip_sn} 的异常装备记录吗？`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(async () => {
          try {
            await this.$api.equipment.deleteAbnormalEquipment(equip_sn)
            this.$notify.success(`序列号为 ${equip_sn} 的异常装备记录已删除！`)
            this.loadAbnormalData() // 刷新列表
          } catch (error) {
            this.$notify.error('删除记录失败')
          }
        }).catch(() => {
          // 用户取消
        })
      }
    },
    getStatusTagType(status) {
      switch (status) {
        case 'pending':
          return 'warning'
        case 'resolved':
          return 'success'
        case 'ignored':
          return 'info'
        case 'investigating':
          return 'danger'
        default:
          return 'info'
      }
    },
    getStatusText(status) {
      switch (status) {
        case 'pending':
          return '待处理'
        case 'resolved':
          return '已解决'
        case 'ignored':
          return '已忽略'
        case 'investigating':
          return '调查中'
        default:
          return '未知'
      }
    },
    formatTime(timeStr) {
      if (!timeStr) return '未知时间'
      try {
        const date = new Date(timeStr)
        return date.toLocaleString('zh-CN')
      } catch (error) {
        return timeStr
      }
    },
    // 处理状态编辑成功
    handleStatusEditSuccess(data) {
      // 刷新异常装备列表
      this.loadAbnormalData()
    },

    // 处理状态编辑对话框关闭
    handleStatusEditClose() {
      this.statusEditDialogVisible = false
      this.currentEditEquipSn = ''
      this.currentEditStatus = ''
    }
  },
  mounted() {
    this.getLingshiData()
    // 组件挂载后自动加载缓存数据
    this.loadFromLocalStorage()
    // 加载快照数据
    const savedSnapshots = localStorage.getItem(this.snapshotStorageKey)
    if (savedSnapshots) {
      this.snapshots = JSON.parse(savedSnapshots)
    }
    // 加载异常装备数据
    this.loadAbnormalData()
  }
}
</script>

<style scoped>
.simulate-wrapper {
  width: 400px;
  border-radius: 5px;
  background-color: #2c3e50 !important;
  padding: 18px !important;
  border: 2px solid #2782a5 !important;
  font-size: 14px;
  font-family: 宋体, tahoma, arial, hiragino sans gb, sans-serif;
  line-height: 22px;
}

/* 快照相关样式 */
.snapshot-detail {
  padding: 20px 0;
}

.snapshot-header {
  text-align: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.snapshot-header h3 {
  margin: 0 0 10px 0;
  color: #303133;
}

.snapshot-time {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.equipment-preview {
  border-radius: 5px;
  background-color: #2c3e50 !important;
  padding: 18px !important;
  border: 2px solid #2782a5 !important;
  font-size: 14px;
  font-family: 宋体, tahoma, arial, hiragino sans gb, sans-serif;
  line-height: 22px;
}

.equipment-preview .equip_desc_yellow {
  color: #e6a23c;
  font-weight: bold;
  margin: 0 0 10px 0;
}

.equipment-preview p {
  margin: 5px 0;
  line-height: 1.6;
}

/* 异常数据相关样式 */
.abnormal-data-container {
  padding: 10px 0;
}

.abnormal-toolbar {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.no-data {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.no-data i {
  font-size: 48px;
  margin-bottom: 10px;
}

.no-data p {
  margin: 5px 0;
}

.abnormal-list {
  max-height: 400px;
  overflow-y: auto;
}

.abnormal-item {
  margin: 8px;
  border: 1px solid #ebeef5;
  width: 300px;
}

.abnormal-item:hover {
  border-color: #409eff;
}

.abnormal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.equipment-info {
  display: flex;
  align-items: center;
}

.equipment-name {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.equipment-sn {
  margin: 0;
  color: #909399;
  font-size: 12px;
}

.abnormal-actions {
  display: flex;
  align-items: center;
}

.abnormal-content {
  display: flex;
  gap: 20px;
}

.abnormal-details {
  flex: 1;
}

.abnormal-details p {
  margin: 5px 0;
  font-size: 12px;
  color: #606266;
}

.equipment-preview-mini {
  flex: 1;
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.equipment-preview-mini p {
  margin: 3px 0;
  font-size: 11px;
  line-height: 1.4;
}

.abnormal-pagination {
  text-align: center;
}
</style>