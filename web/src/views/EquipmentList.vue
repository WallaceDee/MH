<template>
  <div class="equipment-list-view">
    <div class="filters">
      <!-- 筛选和搜索表单 -->
      <el-form :inline="true" :model="filters" @submit.native.prevent="fetchEquipments" size="mini">
        <el-form-item label="选择月份">
          <el-date-picker v-model="filters.selectedDate" :clearable="false" type="month" placeholder="选择月份"
            format="yyyy-MM" value-format="yyyy-MM" />
        </el-form-item>
        <el-form-item label="等级范围">
          <div style="width: 500px">
            <el-slider v-model="filters.level_range" range :min="60" :max="160" :step="5" show-input show-input-controls
              :marks="levelMarks" @change="handleLevelRangeChange" />
          </div>
        </el-form-item>
        <el-form-item label="价格范围">
          <el-input-number v-model="filters.price_min" placeholder="最低价格" :min="0" :controls="false"></el-input-number>
          -
          <el-input-number v-model="filters.price_max" placeholder="最高价格" :min="0" :controls="false"></el-input-number>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filters.kindid" placeholder="请选择类型" multiple clearable filterable
            @change="handleKindidChange">
            <el-option v-for="[value, label] in weapon_armors" :key="value" :label="label" :value="value">
            </el-option>
          </el-select>
        </el-form-item>
        <!-- 宠物装备类型选择器 -->
        <el-form-item v-if="showPetEquipType" label="宠物装备类型">
          <el-cascader v-model="filters.equip_type" :options="petEquipTypeOptions" :props="cascaderProps"
            placeholder="请选择宠物装备类型" multiple clearable filterable collapse-tags collapse-tags-tooltip>
          </el-cascader>
        </el-form-item>
        <el-form-item label="特技">
          <el-select v-model="filters.equip_special_skills" placeholder="请选择特技" multiple clearable filterable>
            <el-option v-for="[value, label] in equip_special_skills" :key="value" :label="label" :value="value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="特效">
          <el-select v-model="filters.equip_special_effect" placeholder="请选择特效" multiple clearable filterable>
            <el-option v-for="(label, value) in equip_special_effect" :key="value"
              :label="value === '1' ? label + '/超级简易' : label" :value="value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="套装">
          <el-cascader v-model="filters.suit_effect" :options="suitOptions" placeholder="请选择套装效果" separator="" clearable
            filterable @change="handleSuitChange" />
        </el-form-item>
        <el-form-item label="镶嵌宝石">
          <el-select v-model="filters.gem_value" placeholder="镶嵌宝石" clearable filterable style="width: 100px">
            <el-option v-for="(gemName, value) in gems_name" :key="value" :value="value" :label="gemName">
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
          <el-input-number size="mini" v-model="filters.gem_level" :min="0" :max="16" :step="1" style="width: 120px"
            placeholder="锻练等级" controls-equip_type="right"></el-input-number>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchEquipments">查询</el-button>
        </el-form-item>
      </el-form>
    </div>
    <el-table :data="equipments" stripe style="width: 100%" @sort-change="handleSortChange" :key="tableKey">
      <el-table-column prop="eid" label="操作" width="100" fixed>
        <template #default="scope">
          <el-link :href="getCBGLink(scope.row.eid)" type="danger" target="_blank">藏宝阁</el-link>
          <el-divider direction="vertical"></el-divider>
          <similar-equipment-modal :equipment="scope.row" :similar-data="similarEquipments[scope.row.eid]"
            :valuation="equipmentValuations[scope.row.eid]" :error="similarError[scope.row.eid]"
            :loading="loadingSimilar[scope.row.eid]" @show="loadSimilarEquipments" @retry="retryWithNewThreshold" />
        </template>
      </el-table-column>
      <el-table-column fixed label="装备" width="70">
        <template #default="scope">
          <equipment-image :equipment="scope.row" />
        </template>
      </el-table-column>
      <el-table-column fixed prop="price" label="价格 (元)" width="160" sortable="custom">
        <template #default="scope">
          <div v-html="formatFullPrice(scope.row)"></div>
        </template>
      </el-table-column>

      <el-table-column prop="baoshi" label="宝石" width="100">
        <template #default="scope">
          <div class="gem-container">
            <el-badge v-if="scope.row.gem_level || scope.row.jinglian_level || scope.row.xiang_qian_level"
              :value="scope.row.gem_level * 1 || scope.row.jinglian_level * 1 || scope.row.xiang_qian_level * 1"
              class="gem-badge" type="warning">
              <div class="gem-images">
                <el-image v-for="gemImgSrc in getGemImageByGemValue(scope.row)" :key="gemImgSrc"
                  style="width: 30px; height: 30px; cursor: pointer; margin-right: 2px" :src="gemImgSrc" fit="cover"
                  referrerpolicy="no-referrer">
                </el-image>
              </div>
            </el-badge>
          </div>
        </template>
      </el-table-column>
      <el-table-column v-if="!showPetEquipType" prop="tejigui" label="特技/特效" width="120">
        <template #default="scope">
          <div class="equip_desc_blue" :data-specia-effet="scope.row.special_effect"
            :data-special-skill="scope.row.special_skill" v-html="formatSpecialSkillsAndEffects(scope.row)"></div>
        </template>
      </el-table-column>
      <el-table-column prop="taozhuang" label="套装" width="160">
        <template #default="scope">
          <div class="equip_desc_blue" v-html="formatSuitEffect(scope.row)"></div>
        </template>
      </el-table-column>

      <el-table-column prop="fujia_shuxing" label="附加属性" width="150">
        <template #default="scope">
          <div class="equip_desc_yellow" v-html="formatAddedAttrs(scope.row.agg_added_attrs)"></div>
        </template>
      </el-table-column>
      <el-table-column prop="equip_level" label="等级" width="80" sortable="custom"></el-table-column>
      <el-table-column prop="all_damage" label="总伤" width="100" sortable="custom"></el-table-column>
      <el-table-column prop="init_damage" label="初伤" width="100" sortable="custom">
        <template #default="scope">
          <span class="equip_desc_yellow">{{ scope.row.init_damage || scope.row.damage || scope.row.shanghai || ''}}</span>
        </template>
      </el-table-column>
      <el-table-column prop="init_wakan" label="初灵" width="100" sortable="custom">
        <template #default="scope">
          <span class="equip_desc_yellow">{{
            scope.row.init_wakan ||
            (scope.row.magic_damage
              ? `法术伤害
            +${scope.row.magic_damage}`
              : '')
          }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="init_defense" label="初防" width="100" sortable="custom">
        <template #default="scope">
          <span class="equip_desc_yellow">{{
            scope.row.init_defense ||
            scope.row.defense ||
            scope.row.fangyu ||
            (scope.row.magic_defense
              ? `法术防御
            +${scope.row.magic_defense}`
              : '')
          }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="init_hp" label="初血" width="100" sortable="custom">
        <template #default="scope">
          <span class="equip_desc_yellow">{{ scope.row.init_hp || scope.row.qixue || ''}}</span>
        </template>
      </el-table-column>
      <el-table-column prop="init_dex" label="初敏" width="100" sortable="custom">
        <template #default="scope">
          <span class="equip_desc_yellow">{{ scope.row.init_dex || scope.row.speed || ''}}</span>
        </template>
      </el-table-column>
      <el-table-column prop="server_name" label="服务器" width="120"></el-table-column>
    </el-table>
    <div class="pagination-container">
      <el-pagination @current-change="handlePageChange" :current-page="pagination.page" @size-change="handleSizeChange"
        :page-size="pagination.page_size" :page-sizes="[10, 100, 200, 300, 400]"
        layout="total, sizes, prev, pager, next, jumper" :total="pagination.total">
      </el-pagination>
    </div>
  </div>
</template>

<script>
import SimilarEquipmentModal from '@/components/SimilarEquipmentModal.vue'
import EquipmentImage from '@/components/EquipmentImage.vue'
import dayjs from 'dayjs'
//CBG_GAME_CONFIG.pet_equip_class0
window.petEquipTypes = [
  {
    key: '1',
    catagory: '铠甲',
    items: []
  },
  {
    key: '2',
    catagory: '项圈',
    items: []
  },
  {
    key: '3',
    catagory: '护腕',
    items: []
  }
]

for (var keyIndex in window.CBG_GAME_CONFIG.equip_info) {
  if (keyIndex >= 9101 && keyIndex <= 9316) {
    const current = window.CBG_GAME_CONFIG.equip_info[keyIndex]
    const level = current.desc.match(/等级(\d+)/)[1]
    if (keyIndex >= 9101 && keyIndex <= 9116) {
      window.petEquipTypes[0].items.push({
        ...current,
        keyIndex: parseInt(keyIndex),
        level
      })

    } else if (keyIndex >= 9201 && keyIndex <= 9216) {
      window.petEquipTypes[1].items.push({
        ...current,
        keyIndex: parseInt(keyIndex),
        level
      })

    } else if (keyIndex >= 9301 && keyIndex <= 9316) {
      window.petEquipTypes[2].items.push({
        ...current,
        keyIndex: parseInt(keyIndex),
        level
      })

    }
  }
}
var lingshiKinds = [
  [61, '戒指'],
  [62, '耳饰'],
  [63, '手镯'],
  [64, '佩饰']
]
export default {
  name: 'EquipmentList',
  components: {
    SimilarEquipmentModal,
    EquipmentImage
  },
  data() {
    return {
      weapon_armors: window.AUTO_SEARCH_CONFIG.weapon_armors
        .concat(lingshiKinds)
        .concat([[29, '宠物装备']]),
      equip_special_skills: window.AUTO_SEARCH_CONFIG.equip_special_skills,
      equip_special_effect: window.AUTO_SEARCH_CONFIG.equip_special_effect,
      equipments: [],
      filters: {
        selectedDate: dayjs().format('YYYY-MM'),
        level_range: [60, 160],
        price_min: undefined,
        price_max: undefined,
        kindid: [29],
        equip_type: [], // 宠物装备类型（多选）
        equip_special_skills: [],
        equip_special_effect: [],
        suit_effect: [],
        gem_value: undefined,
        gem_level: undefined,
        sort_by: 'price',
        sort_order: 'asc'
      },
      pagination: {
        page: 1,
        page_size: 10,
        total: 0
      },
      levelMarks: {
        80: '80',
        100: '100',
        120: '120'
      },
      suitOptions: [],
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
        '755_4036':'755_4036',
        '756_4037':'756_4037',
        '757_4038':'757_4038'
      },
      // 相似装备相关数据
      similarEquipments: {}, // 存储每个装备的相似装备数据
      loadingSimilar: {}, // 存储每个装备的加载状态
      similarError: {}, // 存储加载错误信息
      equipmentValuations: {}, // 存储装备估价信息

      // 宠物装备类型配置
      petEquipTypes: window.petEquipTypes,

      // 级联选择器配置
      cascaderProps: {
        value: 'keyIndex',
        label: 'name',
        children: 'items',
        multiple: true,
        emitPath: false
      },

      // 表格重新渲染的key
      tableKey: 0
    }
  },
  computed: {
    // 是否显示宠物装备类型选择器
    showPetEquipType() {
      return this.filters.kindid && this.filters.kindid.includes(29)
    },

    // 级联选择器选项数据
    petEquipTypeOptions() {
      return this.petEquipTypes.map(category => ({
        keyIndex: category.key,
        name: category.catagory,
        items: category.items.map(item => ({
          keyIndex: item.keyIndex,
          name: `${item.name}（${item.level}级）`,
          level: item.level
        }))
      }))
    },

    // 动态表格列配置
    tableColumns() {
      const baseColumns = [
        {
          prop: 'equip_name',
          label: '装备名称',
          width: '200',
          fixed: 'left',
          template: 'equip_name'
        },
        {
          prop: 'price',
          label: '价格',
          width: '120',
          sortable: 'custom',
          template: 'price'
        },
        {
          prop: 'gem_level',
          label: '宝石',
          width: '120',
          template: 'gem_level'
        }
      ]

      // 如果是宠物装备，添加特技/特效列
      if (this.showPetEquipType) {
        baseColumns.push({
          prop: 'tejigui',
          label: '特技/特效',
          width: '120',
          template: 'tejigui'
        })
      }

      // 添加套装列
      baseColumns.push({
        prop: 'taozhuang',
        label: '套装',
        width: '160',
        template: 'taozhuang'
      })

      // 添加其他固定列
      const otherColumns = [
        {
          prop: 'fujia_shuxing',
          label: '附加属性',
          width: '150',
          template: 'fujia_shuxing'
        },
        {
          prop: 'equip_level',
          label: '等级',
          width: '80',
          sortable: 'custom'
        },
        {
          prop: 'all_damage',
          label: '总伤',
          width: '100',
          sortable: 'custom'
        },
        {
          prop: 'init_damage',
          label: '初伤',
          width: '100',
          sortable: 'custom',
          template: 'init_damage'
        },
        {
          prop: 'init_wakan',
          label: '初灵',
          width: '100',
          sortable: 'custom',
          template: 'init_wakan'
        },
        {
          prop: 'init_defense',
          label: '初防',
          width: '100',
          sortable: 'custom',
          template: 'init_defense'
        },
        {
          prop: 'init_hp',
          label: '初血',
          width: '100',
          sortable: 'custom'
        },
        {
          prop: 'init_dex',
          label: '初敏',
          width: '100',
          sortable: 'custom'
        }
      ]

      baseColumns.push(...otherColumns)

      // 如果是宠物装备，添加宠物装备类型列
      if (this.showPetEquipType) {
        baseColumns.push({
          prop: 'equip_type',
          label: '宠物装备类型',
          width: '120',
          template: 'equip_type'
        })
      }

      // 添加服务器列
      baseColumns.push({
        prop: 'server_name',
        label: '服务器',
        width: '120'
      })

      return baseColumns
    }
  },
  watch: {
    // 监听showPetEquipType变化，强制重新渲染表格
    showPetEquipType() {
      this.tableKey += 1
    }
  },
  methods: {
    isLingshi(kindid) {
      return lingshiKinds.some(([id]) => id === kindid)
    },
    openCBG(eid) {
      window.open(this.getCBGLink(eid), '_blank')
    },
    getCBGLink(eid) {
      // return `https://xyq-m.cbg.163.com/cgi/mweb/equip/${eid.split('-')[1]}/${eid}&shareSource=cbg&tfid=f_equip_list&tcid=c_equip_list`
      return `https://xyq-m.cbg.163.com/cgi/mweb/equip/${eid.split('-')[1]}/${eid}`
    },

    async fetchEquipments() {
      const [year, month] = this.filters.selectedDate.split('-')
      try {
        const params = {
          ...this.filters,
          year,
          month,
          page: this.pagination.page,
          page_size: this.pagination.page_size
        }

        // 处理等级范围滑块值
        if (this.filters.level_range && Array.isArray(this.filters.level_range)) {
          params.level_min = this.filters.level_range[0]
          params.level_max = this.filters.level_range[1]
          delete params.level_range
        }

        // 处理套装级联选择器的值
        if (
          this.filters.suit_effect &&
          Array.isArray(this.filters.suit_effect) &&
          this.filters.suit_effect.length === 2
        ) {
          const [suitType, suitValue] = this.filters.suit_effect
          const actualValue = suitValue.split('_').pop() // 提取真实的套装ID

          if (suitType === 'added_status') {
            params.suit_added_status = actualValue
          } else if (suitType === 'suit_effects') {
            params.suit_effect = actualValue
          } else if (suitType === 'transform_skills') {
            params.suit_transform_skills = actualValue
          } else if (suitType === 'transform_charms') {
            params.suit_transform_charms = actualValue
          }

          // 只有在没有设置任何套装参数时才删除原始的suit_effect
          if (
            !params.suit_added_status &&
            !params.suit_effect &&
            !params.suit_transform_skills &&
            !params.suit_transform_charms
          ) {
            delete params.suit_effect
          }
        } else {
          // 当没有选择套装时，删除原始的suit_effect字段
          delete params.suit_effect
        }

        // 移除空的筛选条件
        Object.keys(params).forEach((key) => {
          if (
            params[key] === null ||
            params[key] === '' ||
            (Array.isArray(params[key]) && params[key].length === 0)
          ) {
            delete params[key]
          }
        })

        // 特殊处理：如果不是宠物装备，移除equip_type参数
        if (!params.kindid || !params.kindid.includes(29)) {
          delete params.equip_type
        }

        // 处理宠物装备类型多选参数
        if (params.equip_type && Array.isArray(params.equip_type) && params.equip_type.length === 0) {
          delete params.equip_type
        }

        // 使用新的API
        const response = await this.$api.equipment.getEquipmentList(params)

        if (response.code === 200) {
          this.equipments = response.data.data || []
          this.pagination.total = response.data.total || 0
          this.pagination.page = response.data.page || this.pagination.page
        } else {
          this.$message.error(response.message || '获取装备列表失败')
        }
      } catch (error) {
        console.error('获取装备列表失败:', error)
        this.$message.error('获取装备列表失败')
      }
    },
    handleSizeChange(val) {
      this.pagination.page_size = val
      this.pagination.page = 1
      this.fetchEquipments()
    },
    handlePageChange(newPage) {
      this.pagination.page = newPage
      this.fetchEquipments()
    },
    handleSortChange({ prop, order }) {
      this.filters.sort_by = prop
      this.filters.sort_order = order === 'ascending' ? 'asc' : 'desc'
      this.fetchEquipments()
    },

    // 格式化价格
    formatPrice(price) {
      const priceFloat = parseFloat(price / 100)
      if (!priceFloat) return '---'
      return window.get_color_price(priceFloat)
    },
    // 格式化完整价格信息（包括跨服费用）
    formatFullPrice(equipment, simple = false) {
      const basePrice = this.formatPrice(equipment.price)

      // 检查是否有登录信息和跨服费用
      if (!window.LoginInfo || !window.LoginInfo.login || simple) {
        return basePrice
      }

      const crossServerPoundage = equipment.cross_server_poundage || 0
      const fairShowPoundage = equipment.fair_show_poundage || 0

      if (!crossServerPoundage) {
        return basePrice
      }

      let additionalFeeHtml = ''

      if (equipment.pass_fair_show == 1) {
        // 跨服费
        const crossFee = parseFloat(crossServerPoundage / 100)
        additionalFeeHtml = `<div class="f12px" style="color: #666;">另需跨服费<span class="p1000">￥${crossFee}</span></div>`
      } else {
        // 信息费（跨服费 + 预订费）
        const totalFee = parseFloat((crossServerPoundage + fairShowPoundage) / 100)
        additionalFeeHtml = `<div class="f12px" style="color: #666;">另需信息费<span class="p1000">￥${totalFee}</span></div>`
      }

      return basePrice + additionalFeeHtml
    },

    formatGems(gemLevel, gemValue) {
      if (!gemLevel || gemLevel <= 0) return ''

      let result = []
      if (gemValue) {
        try {
          // // gemValue是JSON字符串格式，如"[4]"
          // const gemIds = JSON.parse(gemValue)
          // if (Array.isArray(gemIds)) {
          //   result = gemIds.map((id) => this.getGemNameById(id))
          // }
        } catch (e) {
          console.error('解析宝石数据失败:', e, gemValue)
        }
      }

      if (result.length > 0) {
        result.push(`锻炼等级：${gemLevel}`)
        return result.join('<br />')
      }

      return `锻炼等级：${gemLevel}`
    },
    // 获取宝石名称
    getGemNameById(id) {
      // 直接使用全局变量
      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.gems_name) {
        const gemName = window.AUTO_SEARCH_CONFIG.gems_name[id.toString()]
        if (gemName) return gemName
      }

      return `宝石${id}`
    },
    // 解析宝石图片
    //太阳石  月亮石4003 光芒石4004 神秘石4005 红宝石4006 黄宝石4007 蓝宝石4008  绿宝石4009  舍利子4012 黑宝石4010 红玛瑙4011 翡翠石1108_4249
    //星辉石 4244
    getGemImageByGemValue({gem_value:gemValue,kindid,fangyu,speed}) {
      const gemIds = (() => {
        try {
          if(kindid===29){
            if(fangyu){
              return ['755_4036']
            }
            if(speed){
              return ['757_4038']
            }
            return ['756_4037']
          }
          return JSON.parse(gemValue || '["4244"]')
        } catch (e) {
          console.error('解析宝石数据失败:', e, gemValue)
        }
        return []
      })()
      console.log(gemIds[0],this.getImageUrl(this.gem_image[gemIds[0]] + '.gif'))
      return gemIds.map((id) => {
        if (this.gem_image[id]) {
          return this.getImageUrl(this.gem_image[id] + '.gif')
        }
      })
    },
    // 解析附加属性
    formatAddedAttrs(aggAddedAttrs) {
      if (!aggAddedAttrs) return ''

      try {
        let attrs = JSON.parse(aggAddedAttrs)
        if (Array.isArray(attrs) && attrs.length > 0) {
          attrs = attrs.map((a) => {
            if (typeof a === 'string') {
              return a
            } else {
              return `${a.attr_type} +${a.attr_value}`
            }
          })
          return attrs.join('<br />')
        }
      } catch (e) {
        console.error('解析附加属性失败:', e, aggAddedAttrs)
      }

      return ''
    },

    // 解析特技特效
    formatSpecialSkillsAndEffects({
      special_effect: specialEffect,
      special_skill: specialSkill,
      kindid,
      large_equip_desc
    }) {
      console.log({ specialEffect, specialSkill })
      const specials = []

      // 处理特效（JSON字符串格式）
      if (specialEffect && specialEffect !== '') {
        try {
          const effects = JSON.parse(specialEffect)
          const isLingshi = this.isLingshi(kindid)
          console.log(large_equip_desc)
          if (Array.isArray(effects)) {
            effects.forEach((effect) => {
              if (isLingshi) {
                // 在large_equip_desc中提取特效
                // 支持两种格式：
                // 1. #c4DBAF4特效：超级简易#r (无等级)
                // 2. #c4DBAF4特效：锐不可当（3级）#r (有等级)

                // 先尝试匹配有等级的特效
                const effectWithLevelMatch = large_equip_desc.match(
                  /#c4DBAF4特效：([^#]+)（(\d+)级）#r/
                )
                if (effectWithLevelMatch) {
                  const effectName = effectWithLevelMatch[1]
                  const effectLevel = effectWithLevelMatch[2]
                  specials.push(`${effectName}（${effectLevel}级）`)
                } else {
                  // 再尝试匹配无等级的特效
                  const effectWithoutLevelMatch = large_equip_desc.match(/#c4DBAF4特效：([^#]+)#r/)
                  if (effectWithoutLevelMatch) {
                    const effectName = effectWithoutLevelMatch[1]
                    specials.push(`${effectName}`)
                  } else {
                    // 如果都没有匹配到特效，使用默认处理方式
                    const effectName = this.getSpecialEffectName(parseInt(effect), isLingshi)
                    if (effectName) specials.push(`${effectName}`)
                  }
                }
              } else {
                const effectName = this.getSpecialEffectName(parseInt(effect), isLingshi)
                if (effectName) specials.push(`${effectName}`)
              }
            })
          }
        } catch (e) {
          console.warn('解析特效JSON失败:', e, specialEffect)
        }
      }

      // 处理特技
      if (specialSkill && specialSkill !== 0) {
        const skillName = this.getSpecialSkillName(specialSkill)
        if (skillName) specials.push(`${skillName}`)
      }

      return specials.join('<br />')
    },
    // 获取特效名称
    getSpecialEffectName(id, isLingshi = false) {
      if (isLingshi) {
        if (id === 1) {
          return '超级简易'
        }
      } else {
        // 直接使用全局变量
        if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.equip_special_effect) {
          const effectName = window.AUTO_SEARCH_CONFIG.equip_special_effect[id.toString()]
          if (effectName) return effectName
        }
      }
      return `特效${id}`
    },
    // 获取特技名称
    getSpecialSkillName(id) {
      // 直接使用全局变量
      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.equip_special_skills) {
        const skills = window.AUTO_SEARCH_CONFIG.equip_special_skills
        if (Array.isArray(skills)) {
          const skill = skills.find((item) => item[0] === parseInt(id))
          if (skill) return skill[1]
        }
      }

      return `特技${id}`
    },
    // 解析套装信息
    formatSuitEffect({ suit_effect: suitEffect, addon_status, kindid }) {
      if (kindid === 29) {
        return addon_status
      }
      if (!suitEffect) return ''

      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.suit_added_status) {
        const suitName = window.AUTO_SEARCH_CONFIG.suit_added_status[suitEffect.toString()]
        if (suitName) return `附加状态${suitName}`
      }

      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.suit_append_skills) {
        const suitName = window.AUTO_SEARCH_CONFIG.suit_append_skills[suitEffect.toString()]
        if (suitName) return `追加法术${suitName}`
      }
      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.suit_transform_skills) {
        const suitName = window.AUTO_SEARCH_CONFIG.suit_transform_skills[suitEffect.toString()]
        if (suitName) return `变身术之${suitName}`
      }
      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.suit_transform_charms) {
        const suitName = window.AUTO_SEARCH_CONFIG.suit_transform_charms[suitEffect.toString()]
        if (suitName) return `变化咒之${suitName}`
      }

      return `套装${suitEffect}`
    },

    loadEquipDescParser() {
      // 只加载装备描述解析器脚本
      if (!window.parse_style_info) {
        const script = document.createElement('script')
        script.src = '/libs/equip_desc_parser.js'
        script.onload = () => {
          console.log('装备描述解析器加载成功')
        }
        script.onerror = () => {
          console.error('装备描述解析器加载失败')
        }
        document.head.appendChild(script)
      }
    },
    handleLevelRangeChange(value) {
      this.filters.level_range = value
      this.fetchEquipments()
    },
    handleSuitChange(value) {
      this.filters.suit_effect = value
      this.fetchEquipments()
    },
    // 处理装备类型变化
    handleKindidChange(value) {
      // 如果不再包含宠物装备，清空宠物装备类型选择
      if (!value || !value.includes(29)) {
        this.filters.equip_type = []
      }
      this.fetchEquipments()
    },
    // 初始化套装选项
    initSuitOptions() {
      const suitOptions = []

      if (window.AUTO_SEARCH_CONFIG) {
        // 附加状态
        if (window.AUTO_SEARCH_CONFIG.suit_added_status) {
          const addedStatusOptions = Object.entries(
            window.AUTO_SEARCH_CONFIG.suit_added_status
          ).map(([value, label]) => ({
            value: `added_status_${value}`,
            label: label
          }))

          if (addedStatusOptions.length > 0) {
            suitOptions.push({
              value: 'added_status',
              label: '附加状态',
              children: addedStatusOptions
            })
          }
        }

        // 追加法术
        if (window.AUTO_SEARCH_CONFIG.suit_effects) {
          const suitEffectsOptions = Object.entries(window.AUTO_SEARCH_CONFIG.suit_effects).map(
            ([value, label]) => ({
              value: `suit_effects_${value}`,
              label: label
            })
          )

          if (suitEffectsOptions.length > 0) {
            suitOptions.push({
              value: 'suit_effects',
              label: '追加法术',
              children: suitEffectsOptions
            })
          }
        }

        // 变身术
        if (window.AUTO_SEARCH_CONFIG.suit_transform_skills) {
          const transformSkillsOptions = Object.entries(
            window.AUTO_SEARCH_CONFIG.suit_transform_skills
          ).map(([value, label]) => ({
            value: `transform_skills_${value}`,
            label: label
          }))

          if (transformSkillsOptions.length > 0) {
            suitOptions.push({
              value: 'transform_skills',
              label: '变身术',
              children: transformSkillsOptions
            })
          }
        }

        // 变化咒
        if (window.AUTO_SEARCH_CONFIG.suit_transform_charms) {
          const transformCharmsOptions = Object.entries(
            window.AUTO_SEARCH_CONFIG.suit_transform_charms
          ).map(([value, label]) => ({
            value: `transform_charms_${value}`,
            label: label
          }))

          if (transformCharmsOptions.length > 0) {
            suitOptions.push({
              value: 'transform_charms',
              label: '变化咒',
              children: transformCharmsOptions
            })
          }
        }
      }

      this.suitOptions = suitOptions
    },

    // 加载相似装备
    async loadSimilarEquipments(equipment) {
      const eid = equipment.eid

      // 如果已经加载过，直接返回
      if (this.similarEquipments[eid] && this.equipmentValuations[eid]) {
        return
      }

      // 使用默认相似度阈值0.85加载
      await this.loadEquipmentValuation(equipment, 0.8)
    },

    // 重试查找相似装备
    async retryWithNewThreshold(eid, newThreshold) {
      // 获取保存的装备数据
      const similarData = this.similarEquipments[eid]
      if (!similarData || !similarData.equipment) {
        this.$message.error('装备数据丢失，请重新点击查看相似')
        return
      }

      const equipment = similarData.equipment
      // 使用新的相似度阈值重新加载
      await this.loadEquipmentValuation(equipment, newThreshold, true)
    },

    // 统一的装备估价加载方法
    async loadEquipmentValuation(equipment, similarityThreshold = 0.85, isRetry = false) {
      const eid = equipment.eid

      try {
        this.$set(this.loadingSimilar, eid, true)
        this.$set(this.similarError, eid, null)

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
          this.$set(this.equipmentValuations, eid, data)

          // 从估价结果中提取相似装备信息
          if (data.anchors && data.anchors.length > 0) {
            this.$set(this.similarEquipments, eid, {
              anchor_count: data.anchor_count,
              similarity_threshold: data.similarity_threshold,
              anchors: data.anchors,
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
            })

            if (isRetry) {
              this.$message.success(`成功找到 ${data.anchor_count} 个相似装备`)
            }
          } else {
            this.$set(this.similarEquipments, eid, {
              anchor_count: 0,
              similarity_threshold: data.similarity_threshold || similarityThreshold,
              anchors: [],
              statistics: {
                price_range: { min: 0, max: 0 },
                similarity_range: { min: 0, max: 0, avg: 0 }
              },
              message: isRetry
                ? '仍未找到符合条件的市场锚点，请尝试更低的相似度阈值'
                : '未找到符合条件的市场锚点，建议降低相似度阈值',
              canRetry: true,
              equipment: equipment
            })

            if (isRetry) {
              this.$message.warning('仍未找到相似装备，请尝试更低的相似度阈值')
            }
          }
        } else if (valuationResponse.code === 400) {
          // 400错误也要显示界面，只是没有锚点数据
          this.$set(this.similarEquipments, eid, {
            anchor_count: 0,
            similarity_threshold: similarityThreshold,
            anchors: [],
            statistics: {
              price_range: { min: 0, max: 0 },
              similarity_range: { min: 0, max: 0, avg: 0 }
            },
            message: valuationResponse.message || '未找到符合条件的市场锚点，建议降低相似度阈值',
            canRetry: true,
            equipment: equipment
          })
          // 清空估价信息，因为无法估价
          this.$set(this.equipmentValuations, eid, null)

          if (isRetry) {
            this.$message.error(valuationResponse.message || '查找相似装备失败')
          }
        } else {
          this.$set(this.similarError, eid, valuationResponse.message || '加载估价和相似装备失败')

          if (isRetry) {
            this.$set(this.similarEquipments, eid, {
              anchor_count: 0,
              similarity_threshold: similarityThreshold,
              anchors: [],
              statistics: {
                price_range: { min: 0, max: 0 },
                similarity_range: { min: 0, max: 0, avg: 0 }
              },
              message: valuationResponse.message || '查找失败，请重试',
              canRetry: true,
              equipment: equipment
            })
            this.$message.error(valuationResponse.message || '查找相似装备失败')
          }
        }

        console.log('估价和相似装备数据:', valuationResponse.data)
      } catch (error) {
        console.error('加载相似装备或估价失败:', error)
        this.$set(this.similarError, eid, `加载失败: ${error.message}`)

        if (isRetry) {
          this.$message.error(`重试失败: ${error.message}`)
        }
      } finally {
        this.$set(this.loadingSimilar, eid, false)
      }
    },

    // 获取图片URL方法
    getImageUrl(imageName, size = 'small') {
      return `https://cbg-xyq.res.netease.com/images/${size}/${imageName}`
    },
  },
  mounted() {
    this.loadEquipDescParser()
    this.initSuitOptions()
    this.fetchEquipments()
  }
}
</script>

<style scoped>
.equipment-list-view {
  padding: 20px;
}

.filters {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

:global(.equip-desc-popper) {
  background-color: #2c3e50;
  padding: 18px;
  border: 2px solid #2782a5;
}

/* 装备描述样式 */
.equip-desc-content {
  overflow-y: auto;
  line-height: 1.6;
  font-size: 14px;
  color: #ecf0f1;
  padding: 10px;
  border-radius: 4px;
}

/* 装备描述颜色样式 */
:deep(.equip_desc_red) {
  color: #e74c3c;
}

:deep(.equip_desc_green) {
  color: #2ecc71;
}

:deep(.equip_desc_blue) {
  color: #3498db;
}

:deep(.equip_desc_black) {
  color: #34495e;
}

:deep(.equip_desc_yellow) {
  color: #f1c40f;
}

:deep(.equip_desc_white) {
  color: #ecf0f1;
}

:deep(.equip_desc_blink) {
  animation: blink 1s infinite;
}

:deep(.equip_desc_underline) {
  text-decoration: underline;
}

@keyframes blink {

  0%,
  50% {
    opacity: 1;
  }

  51%,
  100% {
    opacity: 0.3;
  }
}

/* 相似装备弹窗样式 */
:global(.similar-equip-popper) {
  padding: 16px;
}

/* 宝石显示样式 */
.gem-container {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-top: 10px;
}

.gem-badge {
  equip_type: relative;
}

.gem-images {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 2px;
}

.gem-images .el-image {
  display: inline-block;
  border-radius: 2px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 滑块样式优化 */
</style>
