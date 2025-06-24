<template>
  <div class="equipment-list-view">
    <div class="filters">
      <!-- 筛选和搜索表单 -->
      <el-form :inline="true" :model="filters" @submit.native.prevent="fetchEquipments" size="mini">
        <el-form-item label="等级范围">
          <div style="width:500px;">
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
          <el-select v-model="filters.kindid" placeholder="请选择类型" multiple clearable filterable>
            <el-option v-for="[value, label] in weapon_armors" :key="value" :label="label" :value="value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="特技">
          <el-select v-model="filters.equip_special_skills" placeholder="请选择特技" multiple clearable filterable>
            <el-option v-for="[value, label] in equip_special_skills" :key="value" :label="label" :value="value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="特效">
          <el-select v-model="filters.equip_special_effect" placeholder="请选择特效" multiple clearable filterable>
            <el-option v-for="(label, value) in equip_special_effect" :key="value" :label="label" :value="value">
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
            placeholder="锻练等级" controls-position="right"></el-input-number>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchEquipments">查询</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table :data="equipments" stripe style="width: 100%" @sort-change="handleSortChange">
      <el-table-column fixed label="装备" width="70">
        <template #default="scope">
          <el-popover placement="right" :width="450" trigger="hover" :visible-arrow="false"
            :content="parseEquipDesc(scope.row.large_equip_desc)" raw-content popper-class="equip-desc-popper">
            <template #reference>
              <el-image style="width: 50px; height: 50px; cursor: pointer" :src="getImageUrl(scope.row.equip_face_img)"
                fit="cover" referrerpolicy="no-referrer">
              </el-image>
            </template>
            <div class="equip-desc-content">
              <el-row type="flex" justify="space-between">
                <el-col style="width: 120px; margin-right: 20px">
                  <el-image style="width: 120px; height: 120px" :src="getImageUrl(scope.row.equip_face_img, 'big')"
                    fit="cover" referrerpolicy="no-referrer">
                  </el-image>
                </el-col>
                <el-col>
                  <p>{{ scope.row.equip_name }}</p>
                  <p v-for="(name_desc, index) in scope.row.equip_type_desc.split('#r')" :key="index"
                    style="color: #fff">
                    {{ name_desc }}
                  </p>
                  <div v-html="parseEquipDesc(scope.row.large_equip_desc)"></div>
                </el-col>
              </el-row>
            </div>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column fixed prop="price" label="价格 (元)" width="160" sortable="custom">
        <template #default="scope">
          <div v-html="formatFullPrice(scope.row)"></div>
        </template>
      </el-table-column>
      <el-table-column prop="eid" label="操作" width="200">
        <template #default="scope">
          <el-link :href="getCBGLink(scope.row.eid)" type="danger">藏宝阁</el-link>
          <el-divider direction="vertical"></el-divider>
          <el-popover placement="left" width="600" trigger="click" popper-class="similar-equip-popper"
            @show="loadSimilarEquipments(scope.row)">
            <template #reference>
              <el-link type="success">查看相似</el-link>
            </template>

            <!-- 相似装备表格 -->
            <div v-if="similarEquipments[scope.row.eid]">
              <div class="similar-header">
                <h4>相似装备 (共{{ similarEquipments[scope.row.eid].anchor_count }}个)</h4>
                <p>相似度阈值: {{ similarEquipments[scope.row.eid].similarity_threshold }}</p>
                
                <!-- 装备估价信息 -->
                <div v-if="equipmentValuations[scope.row.eid]" class="valuation-info">
                  <div class="valuation-main">
                    <span class="valuation-label">装备估价:</span>
                    <span class="valuation-price">{{ equipmentValuations[scope.row.eid].estimated_price_yuan }}元</span>
                    <span class="valuation-strategy">({{ getStrategyName(equipmentValuations[scope.row.eid].strategy) }})</span>
                  </div>
                  <div class="valuation-details">
                    <span>置信度: {{ (equipmentValuations[scope.row.eid].confidence * 100).toFixed(1) }}%</span>
                    <span>基于{{ equipmentValuations[scope.row.eid].anchor_count }}个锚点</span>
                  </div>
                </div>
                
                <div v-if="similarEquipments[scope.row.eid].statistics" class="stats">
                  <span>价格范围: <span
                      v-html="formatPrice(similarEquipments[scope.row.eid].statistics.price_range.min)"></span> -
                    <span
                      v-html="formatPrice(similarEquipments[scope.row.eid].statistics.price_range.max)"></span></span>
                  <span>平均相似度: {{ similarEquipments[scope.row.eid].statistics.similarity_range.avg }}</span>
                </div>
              </div>
              <div
                v-if="!similarEquipments[scope.row.eid].anchors || similarEquipments[scope.row.eid].anchors.length === 0"
                class="no-similar">
                <el-empty description="未找到相似装备" :image-size="60" />
              </div>
              <el-table v-else :data="similarEquipments[scope.row.eid].anchors" stripe max-height="400" style="width: 100%"
                sortable :sort-by="['price', 'similarity']" :sort-order="['ascending', 'descending']">
                <el-table-column fixed label="装备" width="70">
                  <template #default="similarScope">
                    <el-popover placement="right" :width="450" trigger="hover" :visible-arrow="false"
                      :content="parseEquipDesc(similarScope.row.large_equip_desc)" raw-content
                      popper-class="equip-desc-popper">
                      <template #reference>
                        <el-image style="width: 50px; height: 50px; cursor: pointer"
                          :src="getImageUrl(similarScope.row.equip_face_img)" fit="cover" referrerpolicy="no-referrer">
                        </el-image>
                      </template>
                      <div class="equip-desc-content">
                        <el-row type="flex" justify="space-between">
                          <el-col style="width: 120px; margin-right: 20px">
                            <el-image style="width: 120px; height: 120px"
                              :src="getImageUrl(similarScope.row.equip_face_img, 'big')" fit="cover"
                              referrerpolicy="no-referrer">
                            </el-image>
                          </el-col>
                          <el-col>
                            <p>{{ similarScope.row.equip_name }}</p>
                            <p v-for="(name_desc, index) in similarScope.row.equip_type_desc.split('#r')" :key="index"
                              style="color: #fff">
                              {{ name_desc }}
                            </p>
                            <div v-html="parseEquipDesc(similarScope.row.large_equip_desc)"></div>
                          </el-col>
                        </el-row>
                      </div>
                    </el-popover>
                  </template>
                </el-table-column>
                <el-table-column fixed prop="price" label="价格 (元)" width="160" sortable>
                  <template #default="similarScope">
                    <div v-html="formatFullPrice(similarScope.row)"></div>
                  </template>
                </el-table-column>
                <el-table-column prop="similarity" label="相似度" width="80" sortable>
                  <template #default="similarScope">
                    <el-tag :type="getSimilarityTagType(similarScope.row.similarity)">
                      {{ similarScope.row.similarity }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="equip_level" label="等级" width="60"></el-table-column>
                <el-table-column label="特技/特效/套装" width="120">
                  <template #default="similarScope">
                    <div class="special-info">
                      <div class="equip_desc_blue" v-html="formatSpecialSkillsAndEffects(similarScope.row.special_effect, similarScope.row.special_skill)
                        "></div>
                      <span v-if="similarScope.row.suit_effect && similarScope.row.suit_effect !== 0" class="suit">
                        {{ formatSuitEffect(similarScope.row.suit_effect) }}
                      </span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="server_name" label="服务器" width="100"></el-table-column>
                <el-table-column label="操作" width="80">
                  <template #default="similarScope">
                    <el-button type="text" @click="openCBG(similarScope.row.eid)" class="cbg-link">
                      查看
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <div v-else-if="similarError[scope.row.eid]" class="error-info">
              <el-alert type="error" :title="similarError[scope.row.eid]" show-icon />
            </div>

            <div v-else class="loading-info">
              <el-skeleton :rows="5" animated />
            </div>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column prop="baoshi" label="宝石" width="100">
        <template #default="scope">
          <div class="gem-container">
            <el-badge v-if="scope.row.gem_level" :value="scope.row.gem_level * 1" class="gem-badge" type="warning">
              <div class="gem-images">
                <el-image v-for="gemImgSrc in getGemImageByGemValue(scope.row.gem_value)" :key="gemImgSrc"
                  style="width: 30px; height: 30px; cursor: pointer; margin-right: 2px;" :src="gemImgSrc" fit="cover"
                  referrerpolicy="no-referrer">
                </el-image>
              </div>
            </el-badge>
            <div v-else class="gem-images">
              <el-image v-for="gemImgSrc in getGemImageByGemValue(scope.row.gem_value)" :key="gemImgSrc"
                style="width: 30px; height: 30px; cursor: pointer; margin-right: 2px;" :src="gemImgSrc" fit="cover"
                referrerpolicy="no-referrer">
              </el-image>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="tejigui" label="特技/特效" width="120">
        <template #default="scope">
          <div class="equip_desc_blue" v-html="formatSpecialSkillsAndEffects(scope.row.special_effect, scope.row.special_skill)
            "></div>
        </template>
      </el-table-column>
      <el-table-column prop="taozhuang" label="套装" width="160">
        <template #default="scope">
          <div class="equip_desc_blue" v-html="formatSuitEffect(scope.row.suit_effect)"></div>
        </template>
      </el-table-column>

      <el-table-column prop="fujia_shuxing" label="附加属性" width="150">
        <template #default="scope">
          <div class="equip_desc_yellow" v-html="formatAddedAttrs(scope.row.agg_added_attrs)"></div>
        </template>
      </el-table-column>
      <el-table-column prop="equip_level" label="等级" width="80" sortable="custom"></el-table-column>
      <el-table-column prop="all_damage" label="总伤" width="100" sortable="custom"></el-table-column>
      <el-table-column prop="init_damage" label="初伤" width="100" sortable="custom"></el-table-column>
      <el-table-column prop="init_wakan" label="初灵" width="100" sortable="custom"></el-table-column>
      <el-table-column prop="init_defense" label="初防" width="100" sortable="custom"></el-table-column>
      <el-table-column prop="init_hp" label="初血" width="100" sortable="custom"></el-table-column>
      <el-table-column prop="init_dex" label="初敏" width="100" sortable="custom"></el-table-column>
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
export default {
  name: 'EquipmentList',
  data() {
    return {
      weapon_armors: window.AUTO_SEARCH_CONFIG.weapon_armors,
      equip_special_skills: window.AUTO_SEARCH_CONFIG.equip_special_skills,
      equip_special_effect: window.AUTO_SEARCH_CONFIG.equip_special_effect,
      equipments: [],
      filters: {
        level_range: [60, 160],
        price_min: undefined,
        price_max: undefined,
        kindid: [],
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
        120: '120',
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
        12: '1108_4249'
      },
      // 相似装备相关数据
      similarEquipments: {}, // 存储每个装备的相似装备数据
      loadingSimilar: {}, // 存储每个装备的加载状态
      similarError: {}, // 存储加载错误信息
      equipmentValuations: {} // 存储装备估价信息
    }
  },
  methods: {
    openCBG(eid) {
      window.open(this.getCBGLink(eid), '_blank')
    },
    getCBGLink(eid) {
      // return `https://xyq-m.cbg.163.com/cgi/mweb/equip/${eid.split('-')[1]}/${eid}&shareSource=cbg&tfid=f_equip_list&tcid=c_equip_list`
      return `https://xyq-m.cbg.163.com/cgi/mweb/equip/${eid.split('-')[1]}/${eid}`
    },
    getImageUrl(equip_face_img, size = 'small') {
      return `https://cbg-xyq.res.netease.com/images/${size}/${equip_face_img}`
    },
    async fetchEquipments() {
      try {
        const params = {
          ...this.filters,
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
        if (this.filters.suit_effect && Array.isArray(this.filters.suit_effect) && this.filters.suit_effect.length === 2) {
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
          if (!params.suit_added_status && !params.suit_effect && !params.suit_transform_skills && !params.suit_transform_charms) {
            delete params.suit_effect
          }
        } else {
          // 当没有选择套装时，删除原始的suit_effect字段
          delete params.suit_effect
        }

        // 移除空的筛选条件
        Object.keys(params).forEach((key) => {
          if (params[key] === null || params[key] === '' || (Array.isArray(params[key]) && params[key].length === 0)) {
            delete params[key]
          }
        })

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
    parseEquipDesc(desc) {
      if (!desc) return ''
      if (typeof window.parse_style_info === 'function') {
        return window.parse_style_info(desc, '#Y')
      }
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
    getGemImageByGemValue(gemValue) {
      const gemIds = (() => {
        try {
          return JSON.parse(gemValue || '[]')
        } catch (e) {
          console.error('解析宝石数据失败:', e, gemValue)
        }
        return []
      })()
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
        const attrs = JSON.parse(aggAddedAttrs)
        if (Array.isArray(attrs) && attrs.length > 0) {
          return attrs.join('<br />')
        }
      } catch (e) {
        console.error('解析附加属性失败:', e, aggAddedAttrs)
      }

      return ''
    },

    // 解析特技特效
    formatSpecialSkillsAndEffects(specialEffect, specialSkill) {
      const specials = []

      // 处理特效（JSON字符串格式）
      if (specialEffect && specialEffect !== '') {
        try {
          const effects = JSON.parse(specialEffect)
          if (Array.isArray(effects)) {
            effects.forEach((effect) => {
              const effectName = this.getSpecialEffectName(parseInt(effect))
              if (effectName) specials.push(`${effectName}`)
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
    getSpecialEffectName(id) {
      // 直接使用全局变量
      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.equip_special_effect) {
        const effectName = window.AUTO_SEARCH_CONFIG.equip_special_effect[id.toString()]
        if (effectName) return effectName
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
    formatSuitEffect(suitEffect) {
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
    // 初始化套装选项
    initSuitOptions() {
      const suitOptions = []

      if (window.AUTO_SEARCH_CONFIG) {
        // 附加状态
        if (window.AUTO_SEARCH_CONFIG.suit_added_status) {
          const addedStatusOptions = Object.entries(window.AUTO_SEARCH_CONFIG.suit_added_status).map(([value, label]) => ({
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
          const suitEffectsOptions = Object.entries(window.AUTO_SEARCH_CONFIG.suit_effects).map(([value, label]) => ({
            value: `suit_effects_${value}`,
            label: label
          }))

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
          const transformSkillsOptions = Object.entries(window.AUTO_SEARCH_CONFIG.suit_transform_skills).map(([value, label]) => ({
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
          const transformCharmsOptions = Object.entries(window.AUTO_SEARCH_CONFIG.suit_transform_charms).map(([value, label]) => ({
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

      // 设置加载状态
      this.$set(this.loadingSimilar, eid, true)
      this.$set(this.similarError, eid, null)

      try {
        // 并行请求相似装备和估价信息
        const [similarResponse, valuationResponse] = await Promise.all([
          // 获取相似装备
          this.$api.equipment.findEquipmentAnchors({
            equipment_data: equipment,
            similarity_threshold: 0.6,
            max_anchors: 20
          }),
          // 获取估价信息
          this.$api.equipment.getEquipmentValuation({
            equipment_data: equipment,
            strategy: 'fair_value'
          })
        ])

        // 处理相似装备响应
        if (similarResponse.code === 200) {
          this.$set(this.similarEquipments, eid, similarResponse.data)
        } else {
          this.$set(this.similarError, eid, similarResponse.message || '加载相似装备失败')
        }

        // 处理估价响应
        if (valuationResponse.code === 200) {
          this.$set(this.equipmentValuations, eid, valuationResponse.data)
        } else {
          console.warn('装备估价获取失败:', valuationResponse.message)
          // 估价失败不影响相似装备显示，只记录警告
        }

        console.log('相似装备数据:', similarResponse.data)
        console.log('估价数据:', valuationResponse.data)
      } catch (error) {
        console.error('加载相似装备或估价失败:', error)
        this.$set(this.similarError, eid, `加载失败: ${error.message}`)
      } finally {
        this.$set(this.loadingSimilar, eid, false)
      }
    },

    // 获取相似度标签类型
    getSimilarityTagType(similarity) {
      if (similarity >= 0.9) return 'success'
      if (similarity >= 0.8) return 'warning'
      if (similarity >= 0.7) return 'info'
      return 'danger'
    },

    // 获取估价策略显示名称
    getStrategyName(strategy) {
      const strategyNames = {
        'fair_value': '公允价值',
        'competitive': '竞争价格',
        'premium': '溢价估值'
      }
      return strategyNames[strategy] || strategy
    }
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

.similar-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.similar-header h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
}

.similar-header p {
  margin: 0 0 8px 0;
  color: #606266;
  font-size: 14px;
}

.stats {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

/* 估价信息样式 */
.valuation-info {
  margin: 12px 0;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.valuation-main {
  margin-bottom: 6px;
  font-size: 14px;
}

.valuation-label {
  color: #606266;
  font-weight: 500;
}

.valuation-price {
  color: #e6a23c;
  font-weight: 600;
  font-size: 16px;
  margin: 0 8px;
}

.valuation-strategy {
  color: #909399;
  font-size: 12px;
}

.valuation-details {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #909399;
}

.equip-name {
  font-weight: 500;
}

.price-text {
  color: #f56c6c;
  font-weight: 600;
}

.special-info {
  font-size: 12px;
  color: #409eff;
}

.special-info .skill {
  margin-bottom: 2px;
}


.cbg-link {
  color: #409eff;
  padding: 0;
}

.cbg-link:hover {
  color: #66b1ff;
}

.no-similar {
  text-align: center;
  padding: 40px 0;
}

.error-info {
  padding: 20px 0;
}

.loading-info {
  padding: 20px;
}

/* 宝石显示样式 */
.gem-container {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-top: 10px;
}

.gem-badge {
  position: relative;
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
