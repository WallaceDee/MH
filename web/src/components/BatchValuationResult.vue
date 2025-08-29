<template>
  <div class="batch-valuation-result">
    <!-- Loading骨架屏 -->
    <div v-if="loading" class="skeleton-container">
      <el-skeleton :rows="12" animated />
    </div>
    <!-- 结果概览 -->
    <!-- 实际结果 -->
    <template v-else>
      <div class="result-item" :class="getOverviewClass()" style="min-height: unset;">
        <el-row :gutter="20" style="margin-bottom: 20px;">
          <el-col :span="6">
            <el-statistic group-separator="," :precision="2" :value="currentTotalValue / 100" title="估价总值"
              :value-style="{ fontSize: '28px', fontWeight: 'bold' }">
              <template slot="formatter">
                <span v-html="formatPrice(currentTotalValue)"></span>
              </template>
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
      </div>

      <el-row type="flex" style="flex-wrap: wrap;">
        <el-col :span="6" v-for="(item, index) in currentList" :key="item.equip_sn || index" class="result-item"
          :class="getResultItemClass(item)">
      
          <el-row type="flex" align="middle" justify="space-between">
            <el-col style="width: 50px;">
              <EquipmentImage placement="top" :image="false" :equipment="getEquipImageProps(item)"
                :lock-type="item.lock_type" size="small" :popoverWidth="300" />
            </el-col>
            <el-col class="price-info" style="width: calc(100% - 50px);">
              <el-statistic :value-style="getPriceStyle(item.confidence)"> <template slot="formatter">
                  <span v-html="formatPrice(item.estimated_price)"></span>
                </template>
              </el-statistic>
            </el-col>
          </el-row>
          <div class="result-footer">
            <SimilarEquipmentModal :equipment="item" :similar-data="similarData"
              @show="(e) => loadSimilarEquipments(e, item.resultIndex)">
              <el-link href="javascript:void(0)" type="primary" style="font-weight: bold;">{{ item.name || `装备 ${index +
                1}`
                }}</el-link>
            </SimilarEquipmentModal>
            <el-tag :type="getConfidenceTagType(item.confidence)" v-if="!item.error">
              置信度: {{ (item.confidence * 100).toFixed(1) }}%
            </el-tag>
            <el-tag v-else type="danger" :title="item.error">估价失败</el-tag>
          </div>
          <div class="equip-tag-info">
            <el-tag type="success" v-if="getEquipGemInfoAndBlueBlock(item.cDesc).gemLevel">{{ getEquipGemInfoAndBlueBlock(item.cDesc).gemLevel }}锻</el-tag>
            <el-tag v-for="tag in getEquipGemInfoAndBlueBlock(item.cDesc).blueBlock" :key="tag" type="primary">{{ tag }}</el-tag>
          </div>
        </el-col>
      </el-row>
    </template>
    <!-- 关闭按钮 -->
    <div class="dialog-footer" style="text-align: center; margin-top: 20px;">
      <el-button @click="$emit('close')" type="primary">关闭</el-button>
    </div>
  </div>
</template>

<script>
import EquipmentImage from '@/components/EquipmentImage/EquipmentImage.vue'
import SimilarEquipmentModal from '@/components/SimilarEquipmentModal.vue'
import { equipmentMixin } from '@/utils/mixins/equipmentMixin'
import { commonMixin } from '@/utils/mixins/commonMixin'

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
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      similarData: null,
      currentTotalValue: 0,
      currentList: []
    }
  },
  mixins: [equipmentMixin, commonMixin],
  components: {
    EquipmentImage,
    SimilarEquipmentModal
  },
  watch: {
    totalValue(newVal) {
      this.currentTotalValue = newVal
    },
    results(newVal) {
      // 为每个结果添加对应的装备信息
      const resultsWithEquipment = newVal.map((result, index) => ({
        ...result,
        ...this.equipmentList[index],
        resultIndex: index
      }))

      // 分离高置信度和低置信度
      const highConfidenceResults = resultsWithEquipment.filter(result => result.confidence === 1)
      const lowConfidenceResults = resultsWithEquipment.filter(result => result.confidence !== 1)

      // 排序
      highConfidenceResults.sort((a, b) => a.estimated_price - b.estimated_price)
      lowConfidenceResults.sort((a, b) => a.confidence - b.confidence)

      // 合并：低置信度在前，高置信度在后
      this.currentList = [...lowConfidenceResults, ...highConfidenceResults]
    }
  },
  computed: {
    totalCount() {
      return this.results.length
    },
    successCount() {
      return this.results.filter((result) => !result.error).length
    }
  },
  mounted() {
    this.currentTotalValue = this.totalValue
  },
  methods: {
    // 加载相似装备
    async loadSimilarEquipments(equipment, resultIndex) {
      // 使用默认相似度阈值0.8加载
      this.similarData = null
      await this.loadEquipmentValuation(equipment, resultIndex)
    },
    // 统一的装备估价加载方法
    async loadEquipmentValuation(equipment, resultIndex) {
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
        const data = valuationResponse.data

        // 从估价结果中提取相似装备信息
        if (valuationResponse.code === 200 && data?.anchor_count > 0) {
          this.currentTotalValue = this.currentTotalValue - this.results[resultIndex].estimated_price + data.estimated_price
          this.$set(this.results, resultIndex, data)
          // 处理估价响应
          const { data: { anchors: allAnchors } } = await this.$api.equipment.findEquipmentAnchors({
            equipment_data: equipment,
            similarity_threshold: this.valuateParams.similarity_threshold,
            max_anchors: this.valuateParams.max_anchors
          })
          this.similarData = {
            anchor_count: data.anchor_count,
            similarity_threshold: data.similarity_threshold,
            max_anchors: data.max_anchors,
            anchors: allAnchors,
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
        } else if (valuationResponse.code === 400) {
          this.$set(this.results, resultIndex, data)
          // 400错误也要显示界面，只是没有锚点数据
          this.similarData = {
            anchor_count: 0,
            similarity_threshold: this.valuateParams.similarity_threshold,
            max_anchors: this.valuateParams.max_anchors,
            anchors: [],
            statistics: {
              price_range: { min: 0, max: 0 },
              similarity_range: { min: 0, max: 0, avg: 0 }
            }
          }
        }

        console.log('估价和相似装备数据:', valuationResponse.data)
      } catch (error) {
        console.error('加载相似装备或估价失败:', error)
      }
    },

    // 根据置信度获取标签类型
    getConfidenceTagType(confidence) {
      if (confidence >= 0.9) {
        return 'success'  // 绿色 - 高置信度
      } else if (confidence >= 0.7) {
        return ''  // 蓝色 - 中等置信度
      } else if (confidence >= 0.5) {
        return 'info'     // 灰色 - 较低置信度
      } else if (confidence >= 0.3) {
        return 'warning'     // 橙色 - 较低置信度
      } else {
        return 'danger'   // 红色 - 低置信度
      }
    },

    // 根据结果获取结果项的CSS类
    getResultItemClass(result) {
      if (result.error) {
        return 'error'
      }

      // 根据置信度返回不同的类名
      const confidence = result.confidence || 0
      if (confidence >= 0.9) {
        return 'confidence-high'
      } else if (confidence >= 0.7) {
        return 'confidence-medium'
      } else if (confidence >= 0.5) {
        return 'confidence-low'
      } else if (confidence >= 0.3) {
        return 'confidence-very-low'
      } else {
        return 'confidence-extremely-low'
      }
    },

    // 根据置信度获取价格样式
    getPriceStyle(confidence) {
      const baseStyle = { fontSize: '18px', fontWeight: 'bold', justifyContent: 'end' }

      if (!confidence || confidence < 0.3) {
        return { ...baseStyle, color: '#f56c6c' }  // 红色 - 极低置信度
      } else if (confidence < 0.5) {
        return { ...baseStyle, color: '#e6a23c' }  // 橙色 - 很低置信度
      } else if (confidence < 0.7) {
        return { ...baseStyle, color: '#909399' }  // 灰色 - 较低置信度
      } else if (confidence < 0.9) {
        return { ...baseStyle, color: '#409eff' }  // 蓝色 - 中等置信度
      } else {
        return { ...baseStyle, color: '#67c23a' }  // 绿色 - 高置信度
      }
    },

    // 获取概览卡片的颜色类
    getOverviewClass() {
      const successRate = this.totalCount > 0 ? (this.successCount / this.totalCount) : 0
      if (successRate >= 0.9) {
        return 'confidence-high'
      } else if (successRate >= 0.7) {
        return 'confidence-medium'
      } else if (successRate >= 0.5) {
        return 'confidence-low'
      } else if (successRate >= 0.3) {
        return 'confidence-very-low'
      } else {
        return 'confidence-extremely-low'
      }
    }
  }
}
</script>

<style scoped>
.batch-valuation-result {
  width: 960px;
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

/* 根据置信度的悬停效果 */
.result-item.confidence-high:hover {
  background-color: rgba(103, 194, 58, 0.1);
}

.result-item.confidence-medium:hover {
  background-color: rgba(64, 158, 255, 0.1);
}

.result-item.confidence-low:hover {
  background-color: rgba(144, 147, 153, 0.1);
}

.result-item.confidence-very-low:hover {
  background-color: rgba(230, 162, 60, 0.1);
}

.result-item.confidence-extremely-low:hover {
  background-color: rgba(245, 108, 108, 0.1);
}

.result-item.success {
  border-left: 4px solid #67c23a;
}

.result-item.error {
  border-left: 4px solid #f56c6c;
}

/* 根据置信度的颜色变化 */
.result-item.confidence-high {
  border-left: 4px solid #67c23a;
  /* 绿色 - 高置信度 */
  background-color: rgba(103, 194, 58, 0.05);
}

.result-item.confidence-medium {
  border-left: 4px solid #409eff;
  /* 蓝色 - 中等置信度 */
  background-color: rgba(64, 158, 255, 0.05);
}

.result-item.confidence-low {
  border-left: 4px solid #909399;
  /* 灰色 - 较低置信度 */
  background-color: rgba(144, 147, 153, 0.05);
}

.result-item.confidence-very-low {
  border-left: 4px solid #e6a23c;
  /* 橙色 - 很低置信度 */
  background-color: rgba(230, 162, 60, 0.05);
}

.result-item.confidence-extremely-low {
  border-left: 4px solid #f56c6c;
  /* 红色 - 极低置信度 */
  background-color: rgba(245, 108, 108, 0.05);
}

.result-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}


.price-info {
  display: flex;
  align-items: center;
}
:global(.price-info .el-statistic .con){
justify-content: flex-end;
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

/* 骨架屏样式 */
.skeleton-container {
  padding: 20px 0;
}

.skeleton-item {
  padding: 15px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  margin-bottom: 10px;
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.skeleton-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.skeleton-price {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}
.equip-tag-info{
  margin-top: 5px;
}
.equip-tag-info>*{
  margin-right: 5px;
}
</style>
