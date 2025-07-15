<template>
  <!-- TODO:列出有价值的特征在表格列 -->
  <div class="pet-list-view">
    <div class="filters">
      <!-- 筛选和搜索表单 -->
      <el-form :inline="true" :model="filters" @submit.native.prevent="fetchPets" size="mini">
        <el-form-item label="选择月份">
          <el-date-picker v-model="filters.selectedDate" :clearable="false" type="month" placeholder="选择月份"
            format="yyyy-MM" value-format="yyyy-MM" />
        </el-form-item>
        <el-form-item label="等级范围">
          <div style="width: 500px">
            <el-slider v-model="filters.level_range" range :min="0" :max="180" :step="5" show-input show-input-controls
              :marks="levelMarks" @change="handleLevelRangeChange" />
          </div>
        </el-form-item>
        <el-form-item label="价格范围">
          <el-input-number v-model="filters.price_min" placeholder="最低价格" :min="0" :controls="false"></el-input-number>
          -
          <el-input-number v-model="filters.price_max" placeholder="最高价格" :min="0" :controls="false"></el-input-number>
        </el-form-item>
        <el-form-item label="技能">
            <el-cascader v-model="filters.skills" :options="skillOptions" :props="cascaderProps" :show-all-levels="false"
              placeholder="请选择技能" multiple clearable filterable>
              <template slot-scope="{ data }">
                <el-row type="flex"  align="middle">
                    <el-image v-if="data.value" :src="getSkillImage(data.value)" fit="cover" referrerpolicy="no-referrer" style="display: block;width: 24px;height: 24px;margin-right: 4px;"></el-image>
                    <span>{{ data.label }}</span>
                </el-row>
              </template>
            </el-cascader>
        </el-form-item>
        <el-form-item label="技能数量≥">
          <el-input-number v-model="filters.pet_skill_count" placeholder="技能数量" :min="0" controls ></el-input-number>
        </el-form-item>
        <el-form-item label="成长">
          <el-input-number v-model="filters.pet_growth" placeholder="成长" :min="1" :max="1.4" :step="0.1" controls></el-input-number>
        </el-form-item>
        <el-form-item label="灵性值≥">
          <el-input-number v-model="filters.pet_lx" placeholder="灵性值" :min="0" controls ></el-input-number>
        </el-form-item>
        <el-form-item label="特性">
          <el-select v-model="filters.pet_texing" placeholder="请选择特性" multiple clearable filterable>
            <el-option v-for="([value,label]) in texing_type_list" :key="value" :label="label" :value="value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchPets">查询</el-button>
        </el-form-item>
      </el-form>
    </div>
    <el-table :data="pets" stripe style="width: 100%" @sort-change="handleSortChange" :key="tableKey">
      <el-table-column prop="eid" label="操作" width="100" fixed>
        <template #default="scope">
          <el-link :href="getCBGLink(scope.row.eid)" type="danger" target="_blank">藏宝阁</el-link>
          <el-divider direction="vertical"></el-divider>
          <similar-pet-modal :pet="scope.row" :similar-data="similarPets[scope.row.eid]"
            :valuation="petValuations[scope.row.eid]" :error="similarError[scope.row.eid]"
            :loading="loadingSimilar[scope.row.eid]" @show="loadSimilarPets" @retry="retryWithNewThreshold" />
        </template>
      </el-table-column>
      <el-table-column fixed label="召唤兽" width="70">
        <template #default="scope">
          <pet-image :pet="scope.row.petData" :equipFaceImg="scope.row.equip_face_img" :enhanceInfo="getEnhanceInfo(scope.row)"/>
        </template>
      </el-table-column>
      <el-table-column fixed prop="price" label="价格 (元)" width="140" sortable="custom">
        <template #default="scope">
          <div v-html="formatFullPrice(scope.row)"></div>
        </template>
      </el-table-column>
      <el-table-column prop="level" label="等级" width="140" sortable="custom">
        <template #default="scope">
          <p :class="scope.row.petData.is_baobao === '是' ? 'cBlue' : 'equip_desc_red'">
            <span>{{ scope.row.petData.is_baobao === '是' ? '' : '野生' }}</span>
            <span>{{ scope.row.equip_name }}{{ scope.row.petData.is_baobao === '是' ? '宝宝' : '' }}/{{ scope.row.level }}级</span>
          </p>
          <p>参战等级：{{ scope.row.role_grade_limit }}级</p>
        </template>
      </el-table-column>

      <el-table-column prop="growth" label="成长" width="100" sortable="custom">
        <template #default="scope">
          <span class="cDYellow">{{ scope.row.petData.growth }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="skills" label="技能" width="280">
        <template #default="scope">
          <div class="pet-skills" v-html="formatSkills(scope.row)"></div>
        </template>
      </el-table-column>
      <el-table-column prop="petData.texing.name" label="特性" width="60"></el-table-column>
      <el-table-column prop="petData.lx" label="灵性值" width="60"></el-table-column>
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
import SimilarPetModal from '@/components/SimilarPetModal.vue'
import dayjs from 'dayjs'
import PetImage from '@/components/PetImage.vue'

const skillOptions = []
const pet_skill_classification = window.AUTO_SEARCH_CONFIG.pet_skill_classification
for(const lowOrHightKey in pet_skill_classification){
  for(const label in pet_skill_classification[lowOrHightKey]){
    skillOptions.push({
      value:'',
      label:lowOrHightKey.replace('技能','')+label,
      children:pet_skill_classification[lowOrHightKey][label]
    })
  }
}
skillOptions.reverse()
export default {
  name: 'PetList',
  components: {
    SimilarPetModal,
    PetImage
  },
  data() {
    return {
        // 级联选择器配置
      cascaderProps: {
        multiple: true,
        checkStrictly: false, // 不允许选择非叶子节点，只能选择叶子节点
        emitPath: false       // 只返回最后一级的值（技能ID），而不是完整路径
      },
      texing_type_list:window.AUTO_SEARCH_CONFIG.texing_type_list,
      skillOptions,
      pets: [],
      filters: {
        pet_skill_count:0,
        pet_growth:1.0,
        selectedDate: dayjs().format('YYYY-MM'),
        level_range: [0, 180],
        skills:[],
        price_min: undefined,
        price_max: undefined,
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
      tableKey: 0,
      // 相似宠物相关数据
      similarPets: {}, // 存储每个宠物的相似宠物数据
      loadingSimilar: {}, // 存储每个宠物的加载状态
      similarError: {}, // 存储加载错误信息
      petValuations: {}, // 存储宠物估价信息
    }
  },
  methods: {
    getSkillImage(skillId=0) {
      if(skillId===0){
        return ''
      }
      // skillId少于4位数要补0
      const paddedId = skillId.toString().padStart(4, '0')
      return `https://cbg-xyq.res.netease.com/images/skill/${paddedId}.gif`
    },
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

        // 处理技能过滤参数
        if (this.filters.skills && Array.isArray(this.filters.skills) && this.filters.skills.length > 0) {
          // 由于设置了emitPath: false，cascader直接返回技能ID
          params.pet_skills = this.filters.skills
          delete params.skills
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
          this.pets = response.data.data.map((item) => {
            return ({
              ...item,
              petData: this.parsePetInfo(item.desc)
            })
          }) || []
          this.pagination.total = response.data.total || 0
          this.pagination.page = response.data.page || this.pagination.page

          console.log(this.pets.map(item => ({ desc: item.desc, petData: item.petData })))
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
          8,
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

    // 获取增强信息
    getEnhanceInfo(pet) {
      var equip_display_conf = {
        // 高亮技能
        pet: { skill_id_list: [571, 661], is_baobao: 1 },
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
        is_baobao: pet.petData.is_baobao === '是' || false,
        skill_id_list: enhanceInfo.skill_id_list || []
      }
    },

    // 加载相似宠物
    async loadSimilarPets(pet) {
      const eid = pet.eid

      // 如果已经加载过，直接返回
      if (this.similarPets[eid] && this.petValuations[eid]) {
        return
      }

      // 使用默认相似度阈值0.8加载
      await this.loadPetValuation(pet, 0.8)
    },

    // 重试查找相似宠物
    async retryWithNewThreshold(eid, newThreshold) {
      // 获取保存的宠物数据
      const similarData = this.similarPets[eid]
      if (!similarData || !similarData.pet) {
        this.$message.error('宠物数据丢失，请重新点击查看相似')
        return
      }

      const pet = similarData.pet
      // 使用新的相似度阈值重新加载
      await this.loadPetValuation(pet, newThreshold, true)
    },

    // 统一的宠物估价加载方法
    async loadPetValuation(pet, similarityThreshold = 0.8, isRetry = false) {
      const eid = pet.eid

      try {
        this.$set(this.loadingSimilar, eid, true)
        this.$set(this.similarError, eid, null)

        // 获取估价信息（包含相似宠物）
        const valuationResponse = await this.$api.pet.getPetValuation({
          pet_data: pet,
          strategy: 'fair_value',
          similarity_threshold: similarityThreshold,
          max_anchors: 30
        })
        // 处理估价响应
        if (valuationResponse.code === 200) {
          const data = valuationResponse.data
          this.$set(this.petValuations, eid, data)

          // 从估价结果中提取相似宠物信息
          if (data.anchors && data.anchors.length > 0) {
            this.$set(this.similarPets, eid, {
              anchor_count: data.anchor_count,
              similarity_threshold: data.similarity_threshold,
              anchors: data.anchors.map((item) =>({...item, petData: this.parsePetInfo(item.desc)})),
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
              this.$message.success(`成功找到 ${data.anchor_count} 个相似宠物`)
            }
          } else {
            this.$set(this.similarPets, eid, {
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
              pet: pet
            })

            if (isRetry) {
              this.$message.warning('仍未找到相似宠物，请尝试更低的相似度阈值')
            }
          }
        } else if (valuationResponse.code === 400) {
          // 400错误也要显示界面，只是没有锚点数据
          this.$set(this.similarPets, eid, {
            anchor_count: 0,
            similarity_threshold: similarityThreshold,
            anchors: [],
            statistics: {
              price_range: { min: 0, max: 0 },
              similarity_range: { min: 0, max: 0, avg: 0 }
            },
            message: valuationResponse.message || '未找到符合条件的市场锚点，建议降低相似度阈值',
            canRetry: true,
            pet: pet
          })
          // 清空估价信息，因为无法估价
          this.$set(this.petValuations, eid, null)

          if (isRetry) {
            this.$message.error(valuationResponse.message || '查找相似宠物失败')
          }
        } else {
          this.$set(this.similarError, eid, valuationResponse.message || '加载估价和相似宠物失败')

          if (isRetry) {
            this.$set(this.similarPets, eid, {
              anchor_count: 0,
              similarity_threshold: similarityThreshold,
              anchors: [],
              statistics: {
                price_range: { min: 0, max: 0 },
                similarity_range: { min: 0, max: 0, avg: 0 }
              },
              message: valuationResponse.message || '查找失败，请重试',
              canRetry: true,
              pet: pet
            })
            this.$message.error(valuationResponse.message || '查找相似宠物失败')
          }
        }

        console.log('估价和相似宠物数据:', valuationResponse.data)
      } catch (error) {
        console.error('加载相似宠物或估价失败:', error)
        this.$set(this.similarError, eid, `加载失败: ${error.message}`)

        if (isRetry) {
          this.$message.error(`重试失败: ${error.message}`)
        }
      } finally {
        this.$set(this.loadingSimilar, eid, false)
      }
    },
  },
  mounted() {
    this.fetchPets()
    window.parsePetInfo = this.parsePetInfo
  }
}
</script>

<style scoped>
.filters {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
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

/* 相似宠物弹窗样式 */
:global(.similar-pet-popper) {
  padding: 16px;
}
</style>
