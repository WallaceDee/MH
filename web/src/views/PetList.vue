<template>
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
              <el-row type="flex" align="middle">
                <el-image v-if="data.value" :src="getSkillImage(data.value)" fit="cover" referrerpolicy="no-referrer"
                  style="display: block;width: 24px;height: 24px;margin-right: 4px;"></el-image>
                <span>{{ data.label }}</span>
              </el-row>
            </template>
          </el-cascader>
        </el-form-item>
        <el-form-item label="技能数量≥">
          <el-input-number v-model="filters.pet_skill_count" placeholder="技能数量" :min="0" controls></el-input-number>
        </el-form-item>
        <el-form-item label="成长">
          <el-input-number v-model="filters.pet_growth" placeholder="成长" :min="1" :max="1.4" :step="0.1"
            controls></el-input-number>
        </el-form-item>
        <el-form-item label="灵性值≥">
          <el-input-number v-model="filters.pet_lx" placeholder="灵性值" :min="0" controls></el-input-number>
        </el-form-item>
        <el-form-item label="特性">
          <el-select v-model="filters.pet_texing" placeholder="请选择特性" multiple clearable filterable>
            <el-option v-for="([value, label]) in texing_type_list" :key="value" :label="label" :value="value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchPets">查询</el-button>
        </el-form-item>
      </el-form>
    </div>
    <el-table :data="pets" stripe style="width: 100%" @sort-change="handleSortChange" :key="tableKey"
      v-loading="tableLoading">
      <el-table-column prop="eid" label="操作" width="100" fixed align="center">
        <template #default="scope">
          <el-link :href="getCBGLinkByType(scope.row.eid, 'pet')" type="danger" target="_blank">藏宝阁</el-link>
          <el-divider direction="vertical"></el-divider>
          <SimilarPetModal :pet="scope.row" :similar-data="similarPets[scope.row.eid]"
            :valuation="petValuations[scope.row.eid]" :error="similarError[scope.row.eid]"
            :loading="loadingSimilar[scope.row.eid]" @show="loadSimilarPets" @retry="retryWithNewThreshold" />
        </template>
      </el-table-column>
      <el-table-column fixed label="召唤兽" width="70" align="center">
        <template #default="scope">
          <pet-image :pet="scope.row.petData" :equipFaceImg="scope.row.equip_face_img"
            :enhanceInfo="getEnhanceInfo(scope.row)" />
        </template>
      </el-table-column>
      <el-table-column fixed prop="price" label="价格 (元)" width="140" sortable="custom" align="center">
        <template #default="scope">
          {{ scope.row.server_name }}
          <div v-html="formatFullPrice(scope.row)"></div>
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
      <el-table-column prop="equip_list" label="套装" width="100" sortable="custom" align="center">
        <template #default="{ row: { equip_list } }">
          <span v-if="getEquipSuitEffect(equip_list)" class="cBlue" style="text-align: center;">{{
            getEquipSuitEffect(equip_list) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="equip_list" label="装备" width="320" sortable="custom" align="center">
        <template #default="{ row: { equip_list } }">
          <table cellspacing="0" cellpadding="0" class="tb03 size50" id="pet_equip_con" style="transform: scale(0.75);">
            <tr>
              <td v-for="(eItem, index) in JSON.parse(equip_list)" :key="index">
                <EquipmentImage v-if="eItem" :placement="'bottom'" :image="false" :equipment="getEquipImageProps(eItem)"
                  size="small" :popoverWidth="300" />
                <span v-else>&nbsp;</span>
              </td>
              <td v-if="JSON.parse(equip_list).length === 3">&nbsp;</td>
            </tr>
          </table>
          <el-button v-if="JSON.parse(equip_list).some(item => item)" type="text" size="mini"
            @click="batchValuateEquipments(JSON.parse(equip_list))" :loading="equipmentValuationLoading"
            :disabled="!JSON.parse(equip_list).some(item => item)">
            宠物装备估价
          </el-button>
        </template>
      </el-table-column>
      <el-table-column prop="petData.texing.name" label="特性" width="60" align="center"></el-table-column>

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
import BatchValuationResult from '@/components/BatchValuationResult.vue'
import dayjs from 'dayjs'
import PetImage from '@/components/PetImage.vue'
import EquipmentImage from '@/components/EquipmentImage.vue'
import { petMixin } from '@/utils/mixins/petMixin'
import { equipmentMixin } from '@/utils/mixins/equipmentMixin'
import { commonMixin } from '@/utils/mixins/commonMixin'
import { equipmentApi } from '@/api/equipment'
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
    EquipmentImage
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
        pet_skill_count: 0,
        pet_growth: 1.0,
        selectedDate: dayjs().format('YYYY-MM'),
        level_range: [0, 180],
        skills: [],
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
      equipmentValuationLoading: false, // 装备批量估价加载状态
      equipmentValuationResults: {}, // 存储装备批量估价结果
    }
  },
  methods: {
    // 批量装备估价
    async batchValuateEquipments(equipmentList) {
      try {
        // 过滤掉空值和饰品
        const validEquipments = equipmentList.filter((item, index) => item && item.desc && index < 3).map(item => ({ ...item, kindid: 29, large_equip_desc: item.desc }))

        if (validEquipments.length === 0) {
          this.$message.warning('没有有效的装备可以估价')
          return
        }

        this.equipmentValuationLoading = true

        // 调用批量估价API
        const response = await equipmentApi.batchEquipmentValuation({
          equipment_list: validEquipments,
          strategy: 'fair_value',
          similarity_threshold: this.batchValuateParams.similarity_threshold,
          max_anchors: this.batchValuateParams.max_anchors
        })

        if (response.code === 200) {
          const results = response.data.results
          const totalValue = results.reduce((sum, result) => {
            return sum + (result.estimated_price || 0)
          }, 0)

          // 显示估价结果对话框
          this.$msgbox({
            title: '批量装备估价结果',
            message: this.$createElement(BatchValuationResult, {
              props: {
                results: results,
                totalValue: totalValue,
                equipmentList: validEquipments,
                valuateParams: this.batchValuateParams
              },
              on: {
                close: () => {
                  this.$msgbox.close()
                }
              }
            }),
            showCancelButton: false,
            showConfirmButton: false,
            customClass: 'batch-valuation-dialog',
            beforeClose: (action, instance, done) => {
              done()
            }
          }).catch(() => {
            this.equipmentValuationLoading = false
          })

          // 存储结果用于后续使用
          this.equipmentValuationResults = {
            results,
            totalValue,
            timestamp: new Date().toISOString()
          }

        } else {
          this.$message.error(response.message || '批量估价失败')
        }

      } catch (error) {
        console.error('批量装备估价失败:', error)
        this.$message.error('批量装备估价失败: ' + error.message)
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
          this.$message.error(response.message || '获取召唤兽列表失败')
        }
      } catch (error) {
        console.error('获取召唤兽列表失败:', error)
        this.$message.error('获取召唤兽列表失败')
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
            const { data: { anchors } } = await this.$api.pet.findPetAnchors({
              pet_data: pet,
              similarity_threshold: similarityThreshold,
              max_anchors: 30
            })
            this.$set(this.similarPets, eid, {
              anchor_count: data.anchor_count,
              similarity_threshold: data.similarity_threshold,
              anchors: anchors.map((item) => ({ ...item, petData: this.parsePetInfo(item.desc) })),
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

/* 批量估价对话框样式 */
:global(.batch-valuation-dialog) {
  width: 90% !important;
  max-width: 900px !important;
}

:global(.batch-valuation-dialog .el-message-box__content) {
  padding: 0 !important;
}

:global(.batch-valuation-dialog .el-message-box__body) {
  padding: 0 !important;
}
</style>
