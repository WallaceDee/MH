<template>
  <div class="pet-batch-valuation-result">
    <!-- Loading骨架屏 -->
    <div v-if="loading" class="skeleton-container">
      <el-skeleton :rows="12" animated />
    </div>
    <!-- 实际结果 -->
    <template v-else>
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-statistic group-separator="," :precision="2" :value="totalValue / 100" title="估价总值" prefix="¥"
            :value-style="{ fontSize: '28px', fontWeight: 'bold', color: '#67c23a' }">
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic group-separator="," :precision="0" :value="successCount" title="成功估价"
            :value-style="{ fontSize: '28px', fontWeight: 'bold', color: '#67c23a' }">
            <template slot="suffix">
              <span style="color: #909399; font-size: 16px">/ {{ totalCount }}</span>
            </template>
          </el-statistic>
        </el-col>
      </el-row>
      <el-row style="flex-wrap: wrap;">
        <el-col :span="8" v-for="(result, index) in results" :key="index">
          <div class="result-item-wrapper">
            <div class="result-item" :class="{ error: result.error, success: !result.error }">
              <div class="result-header">
                <span class="item-index">{{ petList[index].pet_detail.pet_name || `召唤兽 ${index + 1}` }}-{{
                  petList[index].equip_level
                }}级</span>
                <span v-if="!result.error" class="confidence-badge">
                  置信度: {{ (result.confidence * 100).toFixed(1) }}%
                </span>
                <span v-else class="error-badge" :title="result.error">估价失败</span>
              </div>
              <el-row type="flex" align="middle" justify="space-between">
                <el-col style="width: 50px;">
                  <PetImage placement="top" :pet="petList[index].pet_detail" size="small"
                    :equip_sn="petList[index].equip_sn" :equipFaceImg="petList[index].pet_detail.icon" />
                  <SimilarPetModal :pet="genPetData(petList[index])" :similar-data="similarData" :valuation="result"
                    @show="loadSimilarPets" />
                </el-col>
                <el-col class="price-info" :span="12">
                  <el-statistic group-separator="," :precision="2"
                    :value="(result.estimated_price + result.equip_estimated_price) / 100" title="估价" prefix="¥"
                    :value-style="{ color: '#f56c6c', fontSize: '18px', fontWeight: 'bold' }">
                  </el-statistic>
                </el-col>
              </el-row>

              <!-- 宠物详细信息 -->
              <div class="pet-details" v-if="petList[index]">
                <div class="pet-info">
                  <el-tag size="mini" :type="petList[index].is_baobao === '是' ? 'success' : 'danger'">{{
                    petList[index].is_baobao === '是' ? '宝宝' : '野生' }}</el-tag>
                  <el-tag size="mini">{{ petList[index].equip_level }}级</el-tag>
                  <el-tag size="mini" type="success">{{ petList[index].growth }}</el-tag>
                </div>
                <div class="pet-skills">
                  <span class="skill-label">技能:</span>
                  <span class="mini-icon"
                    v-html="formatSkills({ petData: { ...petList[index].pet_detail, sp_skill: petList[index].pet_detail.genius } })"></span>
                </div>
                <div class="pet-equips">
                  <span class="skill-label">装备:<el-tag>￥{{ result.equip_estimated_price / 100 }}</el-tag>
                    <el-link type="danger" @click="showEquipValuation(petList[index])">查看估价</el-link> </span>
                  <table cellspacing="0" cellpadding="0" class="tb03 size50" style="margin: unset;margin-top: 3px;">
                    <tr>
                      <!-- {{ petList[index] }} -->
                      <td v-for="(eItem, index) in JSON.parse(petList[index].equip_list).splice(0, 3)" :key="index">
                        <EquipmentImage v-if="eItem" :placement="'bottom'" :image="false"
                          :equipment="getEquipImageProps(eItem)" size="small" :popoverWidth="300" width="40px"
                          height="40px" />
                        <span v-else>&nbsp;</span>
                      </td>
                    </tr>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </template>
    <!-- 关闭按钮 -->
    <div class="dialog-footer" style="text-align: center; margin-top: 20px;">
      <el-button @click="$emit('close')" type="primary">关闭</el-button>
    </div>
    <!-- 装备估价结果对话框 -->
    <el-dialog append-to-body :title="valuationDialogTitle" :visible.sync="valuationDialogVisible" width="760px"
      :close-on-click-modal="false" :close-on-press-escape="false" custom-class="batch-valuation-dialog">
      <BatchValuationResult :colSpan="8" style="width: 720px;" :results="valuationResults" :total-value="valuationTotalValue"
        :equipment-list="valuationEquipmentList" :valuate-params="valuateParams" :loading="valuationLoading"
        @close="closeValuationDialog" />
    </el-dialog>
  </div>
</template>

<script>
import PetImage from '@/components/PetImage.vue'
import EquipmentImage from '@/components/EquipmentImage/EquipmentImage.vue'
import SimilarPetModal from '@/components/SimilarPetModal.vue'
import BatchValuationResult from '@/components/BatchValuationResult.vue'
import { petMixin } from '@/utils/mixins/petMixin'
import { equipmentMixin } from '@/utils/mixins/equipmentMixin'
export default {
  name: 'PetBatchValuationResult',
  props: {
    results: {
      type: Array,
      required: true
    },
    petList: {
      type: Array,
      required: true
    },
    totalValue: {
      type: Number,
      default: 0
    },
    valuateParams: {
      type: Object,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      // 装备估价结果对话框相关数据
      valuationDialogVisible: false,
      valuationResults: [],
      valuationTotalValue: 0,
      valuationEquipmentList: [],
      valuationLoading: false,
      valuationDialogTitle: '',
      similarData: null
    }
  },
  mixins: [petMixin, equipmentMixin],
  computed: {
    totalCount() {
      return this.results.length
    },
    successCount() {
      return this.results.filter((result) => !result.error).length
    }
  },
  components: {
    PetImage,
    EquipmentImage,
    SimilarPetModal,
    BatchValuationResult
  },
  methods: {
    async showEquipValuation(pet) {
      try {
        // 获取宠物的装备列表
        const equip_list_raw = pet.equip_list || '[]'
        let equip_list = []

        try {
          equip_list = JSON.parse(equip_list_raw)
        } catch (e) {
          console.error('解析装备列表失败:', e)
          this.$notify.error('装备列表格式错误')
          return
        }

        // 过滤有效的装备数据，只取前三个，并补上kindid: 29 
        const validEquipments = equip_list
          .filter((item, index) => item && item.desc && index < 3)
          .map(item => ({
            kindid: 29,  // 硬编码补上召唤兽装备类型ID
            desc: item.desc  // 确保有large_equip_desc字段
          }))

        if (validEquipments.length === 0) {
          this.$notify.warning('该召唤兽没有携带装备')
          return
        }

        // 先显示弹窗和骨架屏
        this.valuationDialogVisible = true
        this.valuationLoading = true
        this.valuationResults = []
        this.valuationTotalValue = 0
        this.valuationEquipmentList = equip_list
        this.valuationDialogTitle = `召唤兽装备估价结果 - ${pet.pet_detail?.pet_name || '未知召唤兽'}`

        // 调用通用的装备批量估价API
        const response = await this.$api.equipment.batchEquipmentValuation({
          equipment_list: validEquipments,
          strategy: 'fair_value',
          similarity_threshold: this.valuateParams.similarity_threshold,
          max_anchors: this.valuateParams.max_anchors
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

          // 显示成功通知
          this.$notify.success({
            title: '装备估价完成',
            message: `成功估价 ${results.length} 件装备，总价值: ${(totalValue / 100).toFixed(2)} 元`
          })

        } else {
          this.$notify.error(response.message || '装备估价失败')
          this.closeValuationDialog()
        }

      } catch (error) {
        console.error('装备估价失败:', error)
        this.$notify.error('装备估价失败')
        this.closeValuationDialog()
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
    genPetData(pet) {
      return { ...pet, petData: pet.pet_detail, equip_face_img: pet.pet_detail.icon }
    },
    // 加载相似宠物
    async loadSimilarPets(pet) {
      this.similarData = null
      await this.loadPetValuation(pet)
    },
    // 统一的宠物估价加载方法
    async loadPetValuation(pet) {
      try {
        // 获取估价信息（包含相似宠物）
        const valuationResponse = await this.$api.pet.getPetValuation({
          pet_data: pet,
          strategy: 'fair_value',
          similarity_threshold: this.valuateParams.similarity_threshold,
          max_anchors: this.valuateParams.max_anchors
        })

        // 处理估价响应
        if (valuationResponse.code === 200) {
          const data = valuationResponse.data
          // 从估价结果中提取相似宠物信息
          if (data.anchor_count > 0) {
            const { data: { anchors: allAnchors } } = await this.$api.pet.findPetAnchors({
              pet_data: pet,
              similarity_threshold: this.valuateParams.similarity_threshold,
              max_anchors: this.valuateParams.max_anchors
            })
            this.similarData = {
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
          } else {
            this.similarData = {
              anchor_count: 0,
              similarity_threshold: data.similarity_threshold || this.valuateParams.similarity_threshold,
              anchors: [],
              statistics: {
                price_range: { min: 0, max: 0 },
                similarity_range: { min: 0, max: 0, avg: 0 }
              },
              pet: pet
            }
          }
        } else if (valuationResponse.code === 400) {
          // 400错误也要显示界面，只是没有锚点数据
          this.similarData = {
            anchor_count: 0,
            similarity_threshold: this.valuateParams.similarity_threshold,
            anchors: [],
            statistics: {
              price_range: { min: 0, max: 0 },
              similarity_range: { min: 0, max: 0, avg: 0 }
            },
            pet: pet
          }
        }

        console.log('估价和相似宠物数据:', valuationResponse.data)
      } catch (error) {
        console.error('加载相似宠物或估价失败:', error)
      }
    }
  }
}
</script>

<style scoped>
/* 批量估价结果样式 */


.pet-batch-valuation-result {
  width: 860px;
  margin: 0 auto;
}

.result-item-wrapper {
  padding: 4px;
}

.result-item {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  min-height: 100px;
}

.result-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
  background-color: #f5f7fa;
}

.result-item.success {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #e1f3d8 100%);
  border-left: 4px solid #67c23a;
}

.result-item.error {
  border-color: #f56c6c;
  background: linear-gradient(135deg, #fef0f0 0%, #fde2e2 100%);
  border-left: 4px solid #f56c6c;
}

.result-item.partial {
  border-color: #e6a23c;
  background: linear-gradient(135deg, #fdf6ec 0%, #fdf2e9 100%);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.item-index {
  font-weight: bold;
  color: #303133;
}

.confidence-badge {
  background: #67c23a;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.error-badge {
  background: #f56c6c;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.price-info {
  text-align: center;
}

.result-footer {
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.equip-tag-info {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.pet-details {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}

.pet-details .size50 td {
  width: 40px;
  height: 40px;
}

.pet-info {
  margin-bottom: 5px;
  font-size: 12px;
  color: #606266;
}

.pet-info>* {
  margin-right: 5px;
}

.pet-skills {
  font-size: 12px;
  color: #606266;
  margin-bottom: 5px;
}

.skill-label {
  font-weight: bold;
  margin: 5px;
}

.skill-text {
  color: #409eff;
}

.skeleton-container {
  padding: 20px;
}

/* 装备估价对话框样式 */
.batch-valuation-dialog {
  width: 1000px !important;
}

:global(.batch-valuation-dialog .el-message-box__content) {
  padding: 0 !important;
}

:global(.batch-valuation-dialog .el-message-box__body) {
  padding: 0 !important;
}

/* 滚动条样式 */
.results-list::-webkit-scrollbar {
  width: 6px;
}

.results-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.results-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.results-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

:global(.mini-icon .tb03 td) {
  width: 28px !important;
  height: 28px !important;
}

:global(.mini-icon .tb03 td img) {
  width: 24px !important;
  height: 24px !important;
}
</style>