<template>
  <div class="pet-list-view">
    <el-card class="filters" shadow="never">
      <div slot="header" class="card-header">
        <div><span class="emoji-icon">🔍</span> 筛选</div>
      </div>
   
      <!-- 筛选和搜索表单 -->
      <el-form :inline="true" :model="filters" @submit.native.prevent="fetchPets" size="mini">
        <el-form-item label="📅数据月份">
          <el-date-picker v-model="filters.selectedDate" :clearable="false" type="month" placeholder="📅选择月份"
            format="yyyy-MM" value-format="yyyy-MM" />
        </el-form-item>
        <el-form-item label="🔑序列号">
          <el-input v-model="filters.equip_sn" placeholder="🔑序列号"></el-input>
        </el-form-item>
        <el-form-item label="🔢等级">
          <div style="width: 500px">
            <el-slider v-model="filters.level_range" range :min="0" :max="180" :step="5" show-input show-input-controls
              :marks="levelMarks" @change="handleLevelRangeChange" />
          </div>
        </el-form-item>
        <el-form-item label="💲价格">
          <el-input-number v-model="filters.price_min" placeholder="最低价格" :min="0" :controls="false"></el-input-number>
          -
          <el-input-number v-model="filters.price_max" placeholder="最高价格" :min="0" :controls="false"></el-input-number>
        </el-form-item>
        <el-form-item label="🔧技能">
          <el-cascader v-model="filters.skills" :options="skillOptions" :props="cascaderProps" :show-all-levels="false"
            placeholder="🔧请选择技能" multiple clearable filterable>
            <template slot-scope="{ data }">
              <el-row type="flex" align="middle">
                <el-image v-if="data.value" :src="getSkillImage(data.value)" fit="cover" referrerpolicy="no-referrer"
                  style="display: block;width: 24px;height: 24px;margin-right: 4px;"></el-image>
                <span>{{ data.label }}</span>
              </el-row>
            </template>
          </el-cascader>
        </el-form-item>
        <el-form-item label="🔧技能数量≥">
          <el-input-number v-model="filters.pet_skill_count" placeholder="🔧技能数量" :min="0" controls></el-input-number>
        </el-form-item>
        <el-form-item label="📚成长">
          <el-input-number v-model="filters.pet_growth" placeholder="📚成长" :min="1" :max="1.4" :step="0.1"
            controls></el-input-number>
        </el-form-item>
        <el-form-item label="🧝灵性值≥">
          <el-input-number v-model="filters.pet_lx" placeholder="🧝灵性值" :min="0" controls></el-input-number>
        </el-form-item>
        <el-form-item label="🔥特性">
          <el-select v-model="filters.pet_texing" placeholder="🔥请选择特性" multiple clearable filterable>
            <el-option v-for="([value, label]) in texing_type_list" :key="value" :label="label" :value="value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="❌估价异常">
          <el-switch v-model="filters.equip_list_amount_warning" :active-value="1" :inactive-value="0"
            inactive-color="#409EFF" active-color="#F56C6C"></el-switch>
        </el-form-item>
        <el-form-item label="🔍装备估价异常占比率≤" v-if="filters.equip_list_amount_warning === 1">
          <el-input-number v-model="filters.warning_rate" placeholder="装备估价异常占比率" :min="0" :max="99" :step="0.1"
            controls></el-input-number>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchPets">查询</el-button>
        </el-form-item>
      </el-form>
      <el-alert type="warning" @close="batchUpdateUnvaluedPets" :loading="unvaluedPetsLoading"
        v-if="unvaluedPetsCount > 0" :title="` 有（${unvaluedPetsCount}）只召唤兽装备未估价/估价异常`" close-text="更新">
      </el-alert>
  
</el-card>
 
    <el-table :data="pets" stripe style="width: 100%" @sort-change="handleSortChange" :key="tableKey"
      v-loading="tableLoading">
      <el-table-column prop="eid" label="操作" width="100" fixed align="center">
        <template #default="scope">
          <el-link :href="getCBGLinkByType(scope.row.eid, 'pet')" type="danger" target="_blank">藏宝阁</el-link>
          <el-divider direction="vertical"></el-divider>
          <SimilarPetModal :pet="scope.row" :similar-data="similarPets" :valuation="petValuation"
            @show="loadSimilarPets" />
        </template>
      </el-table-column>
      <el-table-column fixed label="召唤兽" width="70" align="center">
        <template #default="scope">
          <PetImage :pet="scope.row.petData" :equip_sn="scope.row.equip_sn" :equipFaceImg="scope.row.equip_face_img"
            :enhanceInfo="getEnhanceInfo(scope.row)" />
        </template>
      </el-table-column>
      <el-table-column fixed prop="price" label="价格 (元)" width="140" sortable="custom" align="center">
        <template #default="scope">
          {{ scope.row.server_name }}
          <div v-html="formatFullPrice(scope.row)"></div>
        </template>
      </el-table-column>
      <el-table-column prop="highlight" label="亮点" width="100" align="center" sortable="custom">>
        <template slot-scope="scope">
          <span v-html="gen_highlight(scope.row.highlight)"></span>
        </template>
      </el-table-column>
      <el-table-column prop="dynamic_tags" label="动态" width="100" align="center" sortable="custom">
        <template slot-scope="scope">
          <span v-html="gen_dynamic_tags(scope.row.dynamic_tags)"></span>
        </template>
      </el-table-column>
      <el-table-column prop="equip_list" label="装备" width="171" sortable="custom" align="center">
        <template #default="{ row: { equip_list, equip_list_amount }, row }">
          <table cellspacing="0" cellpadding="0" class="tb03 size50">
            <tr>
              <td v-for="(eItem, index) in JSON.parse(equip_list).splice(0, 3)" :key="index">
                <EquipmentImage v-if="eItem" :placement="'bottom'" :image="false" :equipment="getEquipImageProps(eItem)"
                  size="small" :popoverWidth="300" />
                <span v-else>&nbsp;</span>
              </td>
            </tr>
          </table>
          <el-row type="flex" justify="space-between" align="middle">
            <p v-if="getEquipSuitEffect(equip_list)" class="cBlue">{{
              getEquipSuitEffect(equip_list) }}套装</p> <span
              v-html="formatFullPrice({ price: equip_list_amount }, true)"></span>
          </el-row>
          <el-button v-if="JSON.parse(equip_list).slice(0, 3).some(item => item)" type="text" size="mini"
            @click="updatePetEquipmentsPrice(row)" :loading="equipmentValuationLoading"
            :disabled="!JSON.parse(equip_list).some(item => item)" style="float:right ;">
            装备估价
          </el-button>
        </template>
      </el-table-column>
      <el-table-column prop="growth" label="成长" width="100" sortable="custom" align="center">
        <template #default="scope">
          <span v-html="getColorNumber(scope.row.growth, [1, 1.3])"></span>
        </template>
      </el-table-column>
      <el-table-column prop="lx" label="灵性" width="80" align="center" sortable="custom">
        <template #default="scope">
          <span v-html="getColorNumber(scope.row.lx, [80, 110])"></span>
        </template>
      </el-table-column>
      <el-table-column prop="skill_count" label="技能" width="280" sortable="custom" align="center">
        <template #default="scope">
          <div class="pet-skills" v-html="formatSkills(scope.row)"></div>
        </template>
      </el-table-column>
      <el-table-column prop="level" label="等级" width="140" sortable="custom" align="center">
        <template #default="scope">
          <p :class="scope.row.petData.is_baobao === '是' ? 'cBlue' : 'equip_desc_red'">
            <span>{{ scope.row.petData.is_baobao === '是' ? '' : '野生' }}</span>
            <span>{{ scope.row.equip_name }}{{ scope.row.petData.is_baobao === '是' ? '宝宝' : '' }}/{{ scope.row.level
            }}级</span>
          </p>
          <p>参战等级：{{ scope.row.role_grade_limit }}级</p>
        </template>
      </el-table-column>
      <el-table-column prop="petData.texing.name" label="特性" width="60" align="center"></el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="scope">
          <el-link href="javascript:void(0)" type="danger" @click.native="handleDelete(scope.row)">删除</el-link>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination-container">
      <el-pagination @current-change="handlePageChange" :current-page="pagination.page" @size-change="handleSizeChange"
        :page-size="pagination.page_size" :page-sizes="[10, 100, 200, 300, 400]"
        layout="total, sizes, prev, pager, next, jumper" :total="pagination.total">
      </el-pagination>
    </div>

    <!-- 装备估价结果对话框 -->
    <el-dialog :title="valuationDialogTitle" :visible.sync="valuationDialogVisible" width="90%"
      :close-on-click-modal="false" :close-on-press-escape="false" custom-class="batch-valuation-dialog">
      <BatchValuationResult :results="valuationResults" :total-value="valuationTotalValue"
        :equipment-list="valuationEquipmentList" :valuate-params="batchValuateParams" :loading="valuationLoading"
        @close="closeValuationDialog" />
    </el-dialog>

    <!-- 任务进度对话框 -->
    <el-dialog title="批量更新进度" :visible.sync="taskProgressVisible" width="500px" :close-on-click-modal="false"
      :close-on-press-escape="false" :show-close="false">
      <div style="text-align: center; padding: 20px;">
        <div style="font-size: 16px; margin-bottom: 20px;">
          正在批量更新召唤兽装备估算价格...
        </div>
        <el-progress :percentage="taskStatus ? taskStatus.progress_percentage || 0 : 0" :stroke-width="16"
          :text-inside="true">
        </el-progress>
        <div style="margin-top: 20px; font-size: 14px; color: #666;">
          已处理: {{ taskStatus ? taskStatus.processed_count || 0 : 0 }} / {{ taskStatus ? taskStatus.total_count || 0 : 0
          }}
        </div>
        <div style="margin-top: 10px; font-size: 14px; color: #666;">
          当前批次: {{ taskStatus ? taskStatus.current_batch || 0 : 0 }} / {{ taskStatus ? taskStatus.total_batches || 0 : 0
          }}
        </div>
        <div style="margin-top: 10px; font-size: 14px; color: #666;">
          已更新: {{ taskStatus ? taskStatus.updated_count || 0 : 0 }}
        </div>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="stopCurrentTask" type="danger">停止任务</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import SimilarPetModal from '@/components/SimilarPetModal.vue'
import BatchValuationResult from '@/components/BatchValuationResult.vue'
import dayjs from 'dayjs'
import PetImage from '@/components/PetImage.vue'
import EquipmentImage from '@/components/EquipmentImage/EquipmentImage.vue'
import { petMixin } from '@/utils/mixins/petMixin'
import { equipmentMixin } from '@/utils/mixins/equipmentMixin'
import { commonMixin } from '@/utils/mixins/commonMixin'
import { petApi } from '@/api/pet'
const skillOptions = []
const pet_skill_classification = window.AUTO_SEARCH_CONFIG.pet_skill_classification
for (const lowOrHightKey in pet_skill_classification) {
  for (const label in pet_skill_classification[lowOrHightKey]) {
    skillOptions.push({
      value: '',
      label: lowOrHightKey.replace('技能', '') + label,
      children: pet_skill_classification[lowOrHightKey][label]
    })
  }
}
skillOptions.reverse()
export default {
  name: 'PetList',
  components: {
    SimilarPetModal,
    PetImage,
    EquipmentImage,
    BatchValuationResult
  },
  mixins: [equipmentMixin, commonMixin, petMixin],
  data() {
    return {
      batchValuateParams: {
        similarity_threshold: 0.8,
        max_anchors: 30
      },
      tableLoading: false, // 表格加载状态
      // 级联选择器配置
      cascaderProps: {
        multiple: true,
        checkStrictly: false, // 不允许选择非叶子节点，只能选择叶子节点
        emitPath: false       // 只返回最后一级的值（技能ID），而不是完整路径
      },
      texing_type_list: window.AUTO_SEARCH_CONFIG.texing_type_list,
      skillOptions,
      pets: [],
      filters: {
        equip_sn: '',
        pet_skill_count: 0,
        pet_growth: 1.0,
        selectedDate: dayjs().format('YYYY-MM'),
        level_range: [0, 180],
        skills: [],
        price_min: undefined,
        price_max: undefined,
        sort_by: 'price',
        sort_order: 'asc',
        equip_list_amount_warning: 0,
        warning_rate: 0.4
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
      // 相似召唤兽相关数据（实时计算，不缓存）
      similarPets: null, // 当前显示的相似召唤兽数据
      petValuation: null, // 当前召唤兽估价信息
      equipmentValuationLoading: false, // 装备批量估价加载状态
      // 装备估价结果对话框相关数据
      valuationDialogVisible: false,
      valuationResults: [],
      valuationTotalValue: 0,
      valuationEquipmentList: [],
      valuationLoading: false,
      valuationDialogTitle: '',
      // 未估价召唤兽数量
      unvaluedPetsCount: 0,
      unvaluedPetsLoading: false,
      // 任务相关数据
      currentTaskId: null,
      taskStatus: {},
      taskProgressTimer: null,
      taskProgressVisible: false,
      taskProgressPercentage: 0,
      taskProgressProcessed: 0,
      taskProgressTotal: 0,
      taskProgressCurrentBatch: 0,
      taskProgressTotalBatches: 0,
      taskProgressUpdated: 0,
    }
  },
  methods: {
    async updatePetEquipmentsPrice({ equip_sn, equip_list, equip_name }) {
      try {
        this.equipmentValuationLoading = true

        // 先过滤装备数据，只取前三个
        const validEquipments = JSON.parse(equip_list)
          .filter((item, index) => item && item.desc && index < 3)
          .map(item => ({ ...item, kindid: 29 }))

        // 先显示弹窗和骨架屏
        this.valuationDialogVisible = true
        this.valuationLoading = true
        this.valuationResults = []
        this.valuationTotalValue = 0
        this.valuationEquipmentList = validEquipments
        this.valuationDialogTitle = `召唤兽装备估价结果 - ${equip_name}`

        // 调用批量估价API
        const response = await petApi.updatePetEquipmentsPrice({
          equip_sn,
          strategy: 'fair_value',
          similarity_threshold: this.batchValuateParams.similarity_threshold,
          max_anchors: this.batchValuateParams.max_anchors,
          year: this.filters.selectedDate.split('-')[0] * 1,
          month: this.filters.selectedDate.split('-')[1] * 1
        })

        if (response.code === 200) {
          const data = response.data
          const results = data.results || []
          const totalValue = results.reduce((sum, result) => {
            return sum + (result.estimated_price || 0)
          }, 0)

          if (results.length === 0) {
            this.$notify.warning('该召唤兽没有携带装备或装备估价失败')
            this.closeValuationDialog()
            return
          }

          // 更新弹窗内容，显示实际数据
          this.valuationResults = results
          this.valuationTotalValue = totalValue
          this.valuationLoading = false
        } else {
          this.$notify.error(response.message || '召唤兽装备估价失败')
          this.closeValuationDialog()
        }
      } catch (error) {
        console.error('召唤兽装备估价失败:', error)
        this.$notify.error('召唤兽装备估价失败')
        this.closeValuationDialog()
      } finally {
        this.equipmentValuationLoading = false
      }
    },
    async fetchPets() {
      const [year, month] = this.filters.selectedDate.split('-')
      try {
        this.tableLoading = true // 开始加载，显示加载状态
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
            const petData = this.parsePetInfo(item.desc)
            return ({
              ...item,
              petData
            })
          }) || []

          this.pagination.total = response.data.total || 0
          this.pagination.page = response.data.page || this.pagination.page
        } else {
          this.$notify.error(response.message || '获取召唤兽列表失败')
        }
      } catch (error) {
        console.error('获取召唤兽列表失败:', error)
        this.$notify.error('获取召唤兽列表失败')
      } finally {
        this.tableLoading = false // 无论成功失败，都结束加载状态
      }
    },
    // 重写 commonMixin 中的方法以适配本页面的数据获取方法名
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
    handleLevelRangeChange(value) {
      this.filters.level_range = value
    },
    // 加载相似召唤兽
    async loadSimilarPets(pet) {
      this.similarPets = null
      this.petValuation = null
      await this.loadPetValuation(pet, 0.8)
    },
    async loadPetValuation({ petData, ...pet }, similarityThreshold = 0.8) {
      try {
        // 获取估价信息（包含相似召唤兽）
        const valuationResponse = await this.$api.pet.getPetValuation({
          pet_data: pet,
          strategy: 'fair_value',
          similarity_threshold: similarityThreshold,
          max_anchors: 30
        })

        // 处理估价响应
        if (valuationResponse.code === 200) {
          const data = valuationResponse.data
          this.petValuation = data
          const { data: { anchors:allAnchors } } = await this.$api.pet.findPetAnchors({
            pet_data: pet,
            similarity_threshold: similarityThreshold,
            max_anchors: 30
          })
          // 从估价结果中提取相似召唤兽信息
          if (data?.anchor_count  > 0) {
            this.similarPets = {
              anchor_count: data.anchor_count,
              similarity_threshold: data.similarity_threshold,
              anchors: allAnchors.map((item) => ({ ...item, petData: this.parsePetInfo(item.desc) })),
              statistics: {
                price_range: {
                  min: Math.min(...allAnchors.map((a) => a.price || 0)),
                  max: Math.max(...allAnchors.map((a) => a.price || 0))
                },
                similarity_range: {
                  min: Math.min(...allAnchors.map((a) => a.similarity || 0)),
                  max: Math.max(...allAnchors.map((a) => a.similarity || 0)),
                  avg:
                    allAnchors.reduce((sum, a) => sum + (a.similarity || 0), 0) /
                    allAnchors.length
                }
              }
            }
            return
          }
        }
        this.similarPets = {
          anchor_count: 0,
          similarity_threshold: similarityThreshold,
          statistics: {
            price_range: { min: 0, max: 0 },
            similarity_range: { min: 0, max: 0, avg: 0 }
          }
        }
      } catch (error) {
        console.error('加载相似召唤兽或估价失败:', error)
      }
    },
    // 关闭装备估价结果对话框
    closeValuationDialog() {
      this.valuationDialogVisible = false
      this.valuationResults = []
      this.valuationTotalValue = 0
      this.valuationEquipmentList = []
      this.valuationLoading = false
      this.valuationDialogTitle = ''
    },

    // 获取未估价召唤兽数量
    async getUnvaluedPetsCount() {
      try {
        this.unvaluedPetsLoading = true
        const [year, month] = this.filters.selectedDate.split('-')

        const response = await petApi.getUnvaluedPetsCount({
          year: parseInt(year),
          month: parseInt(month)
        })

        if (response.code === 200) {
          this.unvaluedPetsCount = response.data.count || 0
        } else {
          console.error('获取未估价召唤兽数量失败:', response.message)
        }
      } catch (error) {
        console.error('获取未估价召唤兽数量失败:', error)
      } finally {
        this.unvaluedPetsLoading = false
      }
    },

    // 批量更新未估价召唤兽装备
    async batchUpdateUnvaluedPets() {
      try {
        this.unvaluedPetsLoading = true
        const [year, month] = this.filters.selectedDate.split('-')

        // 确认对话框
        await this.$confirm(
          `确定要批量更新 ${this.unvaluedPetsCount} 只未估价召唤兽的装备价格吗？此操作可能需要较长时间。`,
          '批量估价确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        const response = await petApi.batchUpdateUnvaluedPets({
          year: parseInt(year),
          month: parseInt(month)
        })

        if (response.code === 200) {
          const data = response.data
          this.currentTaskId = data.task_id
          this.taskStatus = data

          // 显示任务进度对话框
          this.showTaskProgressDialog()

          // 开始监控任务进度
          this.startTaskProgressMonitoring()
        } else {
          this.$notify.error(response.message || '批量更新失败')
        }
      } catch (error) {
        if (error !== 'cancel') { // 用户取消不显示错误
          console.error('批量更新未估价召唤兽装备失败:', error)
          this.$notify.error('批量更新失败')
        }
      } finally {
        this.unvaluedPetsLoading = false
      }
    },

    // 显示任务进度对话框
    showTaskProgressDialog() {
      this.taskProgressVisible = true
    },

    // 开始监控任务进度
    startTaskProgressMonitoring() {
      this.taskProgressTimer = setInterval(async () => {
        if (!this.currentTaskId) {
          this.stopTaskProgressMonitoring()
          return
        }

        try {
          const response = await petApi.getTaskStatus(this.currentTaskId)
          if (response.code === 200) {
            this.taskStatus = response.data

            // 检查任务是否完成
            if (this.taskStatus && this.taskStatus.status === 'completed') {
              this.handleTaskCompleted()
            } else if (this.taskStatus && this.taskStatus.status === 'failed') {
              this.handleTaskFailed()
            } else if (this.taskStatus && this.taskStatus.status === 'cancelled') {
              this.handleTaskCancelled()
            }
          }
        } catch (error) {
          console.error('获取任务状态失败:', error)
        }
      }, 10 * 1000) // 每10秒更新一次
    },

    // 停止监控任务进度
    stopTaskProgressMonitoring() {
      if (this.taskProgressTimer) {
        clearInterval(this.taskProgressTimer)
        this.taskProgressTimer = null
      }
    },

    // 停止当前任务
    async stopCurrentTask() {
      if (this.currentTaskId) {
        try {
          await petApi.stopTask(this.currentTaskId)
          this.$notify.info('已发送停止任务请求')

          // 等待任务状态变为cancelled，然后关闭弹窗
          this.waitForTaskCancelled()
        } catch (error) {
          console.error('停止任务失败:', error)
        }
      }
    },

    // 等待任务取消
    async waitForTaskCancelled() {
      const maxWaitTime = 10000 // 最多等待10秒
      const checkInterval = 1000 // 每1秒检查一次
      const startTime = Date.now()

      console.log('开始等待任务取消...')

      while (Date.now() - startTime < maxWaitTime) {
        try {
          const response = await petApi.getTaskStatus(this.currentTaskId)
          if (response.code === 200 && response.data) {
            const status = response.data.status
            console.log(`任务状态: ${status}`)

            if (status === 'cancelled') {
              // 任务已取消，关闭弹窗
              console.log('任务已取消，关闭弹窗')
              this.handleTaskCancelled()
              return
            } else if (status === 'completed' || status === 'failed') {
              // 任务已完成或失败，也会关闭弹窗
              console.log(`任务状态为 ${status}，关闭弹窗`)
              if (status === 'completed') {
                this.handleTaskCompleted()
              } else {
                this.handleTaskFailed()
              }
              return
            }
          }
        } catch (error) {
          console.error('检查任务状态失败:', error)
        }

        // 等待一段时间再检查
        await new Promise(resolve => setTimeout(resolve, checkInterval))
      }

      // 超时后强制关闭弹窗
      console.warn('等待任务取消超时，强制关闭弹窗')
      this.handleTaskCancelled()
    },

    // 处理任务完成
    handleTaskCompleted() {
      this.stopTaskProgressMonitoring()
      this.taskProgressVisible = false

      if (this.taskStatus) {
        this.$notify.success(
          `批量更新完成！成功更新 ${this.taskStatus.updated_count || 0}/${this.taskStatus.total_count || 0} 只召唤兽的装备价格。`
        )
      } else {
        this.$notify.success('批量更新完成！')
      }

      this.currentTaskId = null
      this.taskStatus = null

      // 重新获取未估价数量
      this.getUnvaluedPetsCount()
      // 刷新召唤兽列表
      this.fetchPets()
    },

    // 处理任务失败
    handleTaskFailed() {
      this.stopTaskProgressMonitoring()
      this.taskProgressVisible = false

      if (this.taskStatus) {
        this.$notify.error(`任务失败: ${this.taskStatus.error_message || '未知错误'}`)
      } else {
        this.$notify.error('任务失败: 未知错误')
      }

      this.currentTaskId = null
      this.taskStatus = null
    },

    // 处理任务取消
    handleTaskCancelled() {
      this.stopTaskProgressMonitoring()
      this.taskProgressVisible = false
      this.$notify.info('任务已取消')
      this.currentTaskId = null
      this.taskStatus = null
    },

    // 删除召唤兽
    async handleDelete(row) {
      try {
        // 确认删除
        await this.$confirm(
          `确定要删除召唤兽 ${row.equip_name || row.equip_sn} 吗？`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        // 获取当前年月
        const [year, month] = this.filters.selectedDate.split('-')

        // 调用删除API
        const response = await petApi.deletePet(row.equip_sn, {
          year,
          month
        })

        if (response.code === 200) {
          this.$notify.success('召唤兽删除成功')
          // 重新获取数据
          await this.fetchPets()
        } else {
          this.$notify.error(response.message || '删除失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除召唤兽失败:', error)
          this.$notify.error('删除召唤兽失败')
        }
      }
    },

    // 检查活跃任务
    async checkActiveTasks() {
      try {
        console.log('开始检查活跃任务...')
        const response = await petApi.getActiveTasks()
        console.log('活跃任务API响应:', response)

        if (response.code === 200 && response.data && response.data.length > 0) {
          console.log('找到活跃任务:', response.data)

          // 找到当前年月对应的活跃任务
          const [year, month] = this.filters.selectedDate.split('-')
          console.log('当前年月:', year, month)

          const currentTask = response.data.find(task => {
            console.log('比较任务:', task.year, task.month, 'vs', year, month)
            return task.year === parseInt(year) && task.month === parseInt(month)
          })

          console.log('匹配的当前任务:', currentTask)

          if (currentTask) {
            this.currentTaskId = currentTask.task_id
            this.taskStatus = currentTask

            // 如果任务还在运行，显示进度对话框并开始监控
            if (currentTask.status === 'running') {
              console.log('恢复运行中的任务:', currentTask.task_id)
              this.showTaskProgressDialog()
              this.startTaskProgressMonitoring()
              this.$notify.info('检测到未完成的任务，已恢复监控')
            } else if (currentTask.status === 'pending') {
              console.log('发现待处理任务:', currentTask.task_id)
              this.$notify.info('检测到待处理的任务，正在等待执行')
            }
          } else {
            console.log('未找到当前年月的活跃任务')
          }
        } else {
          console.log('没有活跃任务或API响应异常')
        }
      } catch (error) {
        console.error('检查活跃任务失败:', error)
      }
    }
  },

  mounted() {
    this.fetchPets()
    this.getUnvaluedPetsCount()
    // 检查是否有活跃任务需要恢复
    this.checkActiveTasks()
  },

  beforeDestroy() {
    // 清理任务进度监控
    this.stopTaskProgressMonitoring()
  }
}
</script>

<style scoped>
.filters {
  margin-bottom:10px;
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

/* 相似召唤兽弹窗样式 */
:global(.similar-pet-popper) {
  padding: 16px;
}

/* 批量估价对话框样式 */
:global(.batch-valuation-dialog) {
  width: 90% !important;
  max-width:1000px !important;
}

:global(.batch-valuation-dialog .el-message-box__content) {
  padding: 0 !important;
}

:global(.batch-valuation-dialog .el-message-box__body) {
  padding: 0 !important;
}
</style>
