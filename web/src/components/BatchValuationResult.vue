<template>
  <div class="batch-valuation-result">
    <!-- 结果概览 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-statistic group-separator="," :precision="2" :value="totalValue / 100" title="估价总值" prefix="¥"
          :value-style="{  fontSize: '28px', fontWeight: 'bold' }">
        </el-statistic>
      </el-col>
      <el-col :span="6">
        <el-statistic group-separator="," :precision="0" :value="successCount" title="成功估价"
          :value-style="{  fontSize: '28px', fontWeight: 'bold' }">
          <template slot="suffix">
            <span style="color: #909399; font-size: 16px">/ {{ totalCount }}</span>
          </template>
        </el-statistic>
      </el-col>
    </el-row>
    <el-row  type="flex" justify="space-between">
      <el-col :span="8" v-for="(result, index) in results" :key="index" class="result-item"
        :class="{ error: result.error, success: !result.error }">
        <div class="result-header">
          <span class="item-index">装备 {{ index + 1 }}</span>
          <span v-if="!result.error" class="confidence-badge">
            置信度: {{ (result.confidence * 100).toFixed(1) }}%
          </span>
          <span v-else class="error-badge" :title="result.error">估价失败</span>
        </div>

        <el-row class="result-content">
          <el-col :span="12">
            <EquipmentImage placement="top" :image="false" :equipment="getEquipImageProps(equipmentList[index])"
              size="small" :popoverWidth="300" />
            <SimilarEquipmentModal :equipment="equipmentList[index]" :loading="loading" @show="loadSimilarEquipments"
              :similar-data="similarData"  :valuation="result"/>
          </el-col>
          <el-col class="price-info" :span="12">

            <el-statistic group-separator="," :precision="2" :value="result.estimated_price_yuan" title="估价" prefix="¥"
              :value-style="{ color: '#f56c6c', fontSize: '18px', fontWeight: 'bold' }">
            </el-statistic>
          </el-col>
        </el-row>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import EquipmentImage from '@/components/EquipmentImage.vue'
import SimilarEquipmentModal from '@/components/SimilarEquipmentModal.vue'
import { equipmentMixin } from '@/utils/mixins/equipmentMixin'
export default {
  name: 'BatchValuationResult',
  props: {
    results: {
      type: Array,
      required: true
    },
    equipmentList: {
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
    }
  },
  data() {
    return {
      loading: false,
      similarData:null
    }
  },
  mixins: [equipmentMixin],
  components: {
    EquipmentImage,
    SimilarEquipmentModal
  },
  computed: {
    totalCount() {
      return this.results.length
    },
    successCount() {
      return this.results.filter((result) => !result.error).length
    }
  },
  methods: {
    closeDialog() {
      this.$emit('close')
    },
    // 加载相似装备
    async loadSimilarEquipments(equipment) {
      // 使用默认相似度阈值0.85加载
      await this.loadEquipmentValuation(equipment)
    },
    // 统一的装备估价加载方法
    async loadEquipmentValuation(equipment, isRetry = false) {
      try {
        // similarity_threshold:0.8,
        // max_anchors:30
        // 获取估价信息（包含相似装备）
        const valuationResponse = await this.$api.equipment.getEquipmentValuation({
          equipment_data: equipment,
          strategy: 'fair_value',
          similarity_threshold: this.valuateParams.similarity_threshold,
          max_anchors: this.valuateParams.max_anchors
        })
        const { data: { anchors } } = await this.$api.equipment.findEquipmentAnchors({
          equipment_data: equipment,
          similarity_threshold: this.valuateParams.similarity_threshold,
          max_anchors: this.valuateParams.max_anchors
        })
        // 处理估价响应
        if (valuationResponse.code === 200) {
          const data = valuationResponse.data

          // 从估价结果中提取相似装备信息
          if (data.anchors && data.anchors.length > 0) {
            this.similarData = {
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
            if (isRetry) {
              this.$message.success(`成功找到 ${data.anchor_count} 个相似装备`)
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
              message: isRetry
                ? '仍未找到符合条件的市场锚点，请尝试更低的相似度阈值'
                : '未找到符合条件的市场锚点，建议降低相似度阈值',
              canRetry: true,
              equipment: equipment
            }

            if (isRetry) {
              this.$message.warning('仍未找到相似装备，请尝试更低的相似度阈值')
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
            message: valuationResponse.message || '未找到符合条件的市场锚点，建议降低相似度阈值',
            canRetry: true,
            equipment: equipment
          }

          if (isRetry) {
            this.$message.error(valuationResponse.message || '查找相似装备失败')
          }
        } else {

          if (isRetry) {
            this.similarData = {
              anchor_count: 0,
              similarity_threshold: this.valuateParams.similarity_threshold,
              anchors: [],
              statistics: {
                price_range: { min: 0, max: 0 },
                similarity_range: { min: 0, max: 0, avg: 0 }
              },
              message: valuationResponse.message || '查找失败，请重试',
              canRetry: true,
              equipment: equipment
            }
            this.$message.error(valuationResponse.message || '查找相似装备失败')
          }
        }

        console.log('估价和相似装备数据:', valuationResponse.data)
      } catch (error) {
        console.error('加载相似装备或估价失败:', error)

        if (isRetry) {
          this.$message.error(`重试失败: ${error.message}`)
        }
      } finally {
        this.loading = false
      }
    },
  }
}
</script>

<style scoped>
.batch-valuation-result {
  width: 720px;
  margin: 0 auto;
}

.result-overview {
  margin-bottom: 30px;
}

.overview-card {
  display: flex;
  justify-content: space-around;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px 20px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.overview-item {
  text-align: center;
  flex: 1;
}

.result-details {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.details-header {
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
}

.details-header h3 {
  margin: 0;
  color: #303133;
}

.results-list {
  max-height: 400px;
  overflow-y: auto;
}

.result-item {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.3s;
  min-height: 100px;
}

.result-item:hover {
  background-color: #f5f7fa;
}

.result-item.success {
  border-left: 4px solid #67c23a;
}

.result-item.error {
  border-left: 4px solid #f56c6c;
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

.result-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price-info {
  display: flex;
  align-items: center;
}

.equipment-info {
  text-align: right;
}

.equip-name {
  font-weight: bold;
  color: #303133;
}

.equip-level {
  color: #909399;
  margin-left: 5px;
}

.error-content {
  color: #f56c6c;
}

.error-message {
  font-size: 14px;
}

.result-actions {
  margin-top: 20px;
  text-align: center;
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
</style>
