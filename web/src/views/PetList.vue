<template>
  <!-- TODO:列出有价值的特征在表格列 -->
  <div class="pet-list-view">
    <div class="filters">
      <!-- 筛选和搜索表单 -->
      <el-form :inline="true" :model="filters" @submit.native.prevent="fetchPets" size="mini">
        <el-form-item label="选择月份">
          <el-date-picker
            v-model="filters.selectedDate"
            :clearable="false"
            type="month"
            placeholder="选择月份"
            format="yyyy-MM"
            value-format="yyyy-MM"
          />
        </el-form-item>
        <el-form-item label="等级范围">
          <div style="width: 500px">
            <el-slider
              v-model="filters.level_range"
              range
              :min="0"
              :max="180"
              :step="5"
              show-input
              show-input-controls
              :marks="levelMarks"
              @change="handleLevelRangeChange"
            />
          </div>
        </el-form-item>
        <el-form-item label="价格范围">
          <el-input-number
            v-model="filters.price_min"
            placeholder="最低价格"
            :min="0"
            :controls="false"
          ></el-input-number>
          -
          <el-input-number
            v-model="filters.price_max"
            placeholder="最高价格"
            :min="0"
            :controls="false"
          ></el-input-number>
        </el-form-item>
        <el-form-item label="召唤兽类型">
          <el-select
            v-model="filters.pet_type"
            placeholder="请选择召唤兽类型"
            multiple
            clearable
            filterable
            @change="handlePetTypeChange"
          >
            <el-option
              v-for="[value, label] in pet_types"
              :key="value"
              :label="label"
              :value="value"
            >
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchPets">查询</el-button>
        </el-form-item>
      </el-form>
    </div>
    <el-table
      :data="pets"
      stripe
      style="width: 100%"
      @sort-change="handleSortChange"
      :key="tableKey"
    >
      <el-table-column prop="eid" label="操作" width="100" fixed>
        <template #default="scope">
          <el-link :href="getCBGLink(scope.row.eid)" type="danger" target="_blank">藏宝阁</el-link>
        </template>
      </el-table-column>
      <el-table-column fixed label="召唤兽" width="70">
        <template #default="scope">
          <PetInfoPopover
            :key="scope.row.equip_sn"
            :petData="scope.row.petData"
            :equipFaceImg="scope.row.equip_face_img"
            :enhanceInfo="getEnhanceInfo(scope.row)"
            :visible="scope.row.showPopover"
          >
            <template #trigger>
              <pet-image :pet="scope.row" />
            </template>
          </PetInfoPopover>
        </template>
      </el-table-column>
      <el-table-column fixed prop="price" label="价格 (元)" width="140" sortable="custom">
        <template #default="scope">
          <div v-html="formatFullPrice(scope.row)"></div>
        </template>
      </el-table-column>
      <el-table-column prop="level" label="等级" width="140" sortable="custom">
        <template #default="scope">
          <p :class="scope.row.petData.is_baobao==='是'?'cBlue':'equip_desc_red'"><span>{{scope.row.petData.is_baobao==='是'?'':'野生'}}</span>
            <span >{{scope.row.equip_name}}{{scope.row.petData.is_baobao==='是'?'宝宝':''}}/{{ scope.row.level }}级</span></p>
          <p>参战等级：{{ scope.row.role_grade_limit }}级</p>
        </template>
      </el-table-column>

      <el-table-column prop="growth" label="成长" width="100" sortable="custom">
        <template #default="scope">
          <span class="cDYellow">{{ scope.row.petData.growth }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="skills" label="技能" width="220">
        <template #default="scope">
          <div class="pet-skills" v-html="formatSkills(scope.row)"></div>
        </template>
      </el-table-column>
      <el-table-column prop="petData.texing.name" label="特性" width="60"></el-table-column>
      <el-table-column prop="petData.lx" label="灵性值" width="60"></el-table-column>
      <el-table-column prop="server_name" label="服务器" width="120"></el-table-column>
    </el-table>
    <div class="pagination-container">
      <el-pagination
        @current-change="handlePageChange"
        :current-page="pagination.page"
        @size-change="handleSizeChange"
        :page-size="pagination.page_size"
        :page-sizes="[10, 100, 200, 300, 400]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="pagination.total"
      >
      </el-pagination>
    </div>
  </div>
</template>

<script>
import PetImage from '@/components/PetImage.vue'
import PetInfoPopover from '@/components/PetInfoPopover.vue'
import dayjs from 'dayjs'

export default {
  name: 'PetList',
  components: {
    PetImage,
    PetInfoPopover
  },
  data() {
    return {
      pet_types: [
        [1, '攻宠'],
        [2, '法宠'],
        [3, '血宠'],
        [4, '速宠'],
        [5, '特殊宠']
      ],
      pets: [],
      filters: {
        selectedDate: dayjs().format('YYYY-MM'),
        level_range: [150, 180],
        price_min: undefined,
        price_max: undefined,
        pet_type: [],
        sort_by: 'price',
        sort_order: 'asc'
      },
      pagination: {
        page: 1,
        page_size: 10,
        total: 0
      },
      levelMarks: {
        60: '60',
        90: '90',
        120: '120',
        150: '150'
      },
      tableKey: 0
    }
  },
  methods: {
    tableRowClassName({ row }) {
      if (row.petData.is_baobao === '否') {
        return 'warning-row'
      }
      return ''
    },
    parse_fashang_fafang(desc_info) {
      try {
        const data = JSON.decode(window.decode_desc(desc_info)) // 对内容解码
        return {
          fashang: data.fashang,
          fafang: data.fafang
        }
      } catch (e) {
        return {}
      }
    },
    openCBG(eid) {
      window.open(this.getCBGLink(eid), '_blank')
    },
    getCBGLink(eid) {
      return `https://xyq-m.cbg.163.com/cgi/mweb/equip/${eid.split('-')[1]}/${eid}`
    },
    parsePetInfo(desc) {
      const pet_desc = window.parse_desc_info(desc)
      const newLinliData = this.parse_fashang_fafang(desc)
      const pet_attrs = window.get_pet_attrs_info(pet_desc, {
        only_basic_attr: false,
        fashang: newLinliData.fashang,
        fafang: newLinliData.fafang
      })
      return pet_attrs
    },
    async fetchPets() {
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

        // 使用新的API
        const response = await this.$api.pet.getPetList(params)

        if (response.code === 200) {
          this.pets =
            response.data.data.map((item) => {
              console.log(this.parsePetInfo(item.desc))
              return ({
              ...item,
              petData: this.parsePetInfo(item.desc)
            })
            }) || []
          this.pagination.total = response.data.total || 0
          this.pagination.page = response.data.page || this.pagination.page
        } else {
          this.$message.error(response.message || '获取召唤兽列表失败')
        }
      } catch (error) {
        console.error('获取召唤兽列表失败:', error)
        this.$message.error('获取召唤兽列表失败')
      }
    },
    handleSizeChange(val) {
      this.pagination.page_size = val
      this.pagination.page = 1
      this.fetchPets()
    },
    handlePageChange(newPage) {
      this.pagination.page = newPage
      this.fetchPets()
    },
    handleSortChange({ prop, order }) {
      this.filters.sort_by = prop
      this.filters.sort_order = order === 'ascending' ? 'asc' : 'desc'
      this.fetchPets()
    },

    // 格式化价格
    formatPrice(price) {
      if (!price) return '---'
      return window.get_color_price(price)
    },
    // 格式化完整价格信息（包括跨服费用）
    formatFullPrice(pet, simple = false) {
      const basePrice = this.formatPrice(pet.price)

      // 检查是否有登录信息和跨服费用
      if (!window.LoginInfo || !window.LoginInfo.login || simple) {
        return basePrice
      }

      const crossServerPoundage = pet.cross_server_poundage || 0
      const fairShowPoundage = pet.fair_show_poundage || 0

      if (!crossServerPoundage) {
        return basePrice
      }

      let additionalFeeHtml = ''

      if (pet.pass_fair_show == 1) {
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

    // 格式化技能
    formatSkills({ petData }) {
      try {
        // 创建一个临时的容器元素
        const tempContainer = document.createElement('div')

        // 调用原始函数，传入临时容器
        const { pet_tip_skill_grid: result } = window.show_pet_skill_in_grade(
          petData.all_skill,
          petData.sp_skill,
          2,
          6,
          {
            pet_skill_url: 'https://cbg-xyq.res.netease.com/images/skill/',
            notice_node_name: 'pet_tip_notice_msg',
            skill_panel_name: 'pet_tip_skill_grid',
            enhance_skills: [],
            table_class: 'tb03'
          },
          petData
        )
        // 如果返回的是DOM节点，将其添加到临时容器
        result.forEach((node) => {
          if (node) {
            tempContainer.appendChild(node)
          }
        })
        // 返回HTML字符串，去掉所有空的td标签
        return tempContainer.innerHTML
      } catch (error) {
        console.error('格式化技能失败:', error)
        return ''
      }
    },

    // 获取技能名称
    getSkillName(skillId) {
      // 这里可以根据技能ID获取技能名称
      // 暂时返回技能ID，后续可以扩展技能名称映射
      return `技能${skillId}`
    },

    handleLevelRangeChange(value) {
      this.filters.level_range = value
      this.fetchPets()
    },

    // 处理召唤兽类型变化
    handlePetTypeChange() {
      this.fetchPets()
    },

    // 处理宠物点击事件
    handlePetClick(pet) {
      try {
        // 解析宠物数据
        const petData = this.parsePetInfo(pet.desc)
        this.$set(pet, 'petData', petData)
      } catch (error) {
        console.error('解析宠物数据失败:', error)
        this.$message.error('获取宠物详细信息失败')
      }
    },

    // 获取增强信息
    getEnhanceInfo(pet) {
      var equip_display_conf = {
        pet: { skill_id_list: [661], is_baobao: 1 },
        search: { is_hide_unreasonable_price_equips: 1 }
      }
      var enhanceInfo = equip_display_conf.pet || {}
      var time_lock = pet.is_time_lock
      time_lock = time_lock > 0 || time_lock == 'true'
      var time_lock_days
      if (time_lock) {
        time_lock_days = pet.time_lock_days
      }
      enhanceInfo.time_lock = time_lock
      enhanceInfo.time_lock_days = time_lock_days
      return {
        time_lock: pet.time_lock || false,
        time_lock_days: pet.time_lock_days || 90,
        is_baobao: pet.petData.is_baobao==='是' || false,
        skill_id_list: enhanceInfo.skill_id_list || []
      }
    },
  },
  mounted() {
    this.fetchPets()
  }
}
</script>

<style scoped>
:global(.el-table .warning-row) {
  background: #DCDFE6;
  border:1px dashed #606266;
}

.pet-list-view {
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

/* 召唤兽名称样式 */
.pet-name {
  font-weight: bold;
  color: #409eff;
}

/* 召唤兽等级样式 */
.pet-level {
  color: #67c23a;
  font-weight: bold;
}

/* 成长值样式 */
.pet-growth {
  color: #e6a23c;
  font-weight: bold;
}

/* 技能样式 */
:global(.pet-skills .tb03 td) {
  width: 30px;
  height: 30px;
}

:global(.pet-skills img) {
  width: 28px;
  height: 28px;
}

:global(.pet-skills img.on) {
  width: 28px;
  height: 28px;
  border: 1px solid #c00;
}

.skill-item {
  display: inline-block;
  background-color: #f0f9ff;
  color: #409eff;
  padding: 2px 6px;
  margin: 1px;
  border-radius: 3px;
  font-size: 12px;
  border: 1px solid #d1ecf1;
}
</style>
