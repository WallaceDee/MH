<template>
  <el-popover :data-equip-sn="equipment.equip_sn" :placement="placement" width="640" trigger="click"
    popper-class="similar-equip-popper" v-model="visible" @show="handleShow">
    <template #reference>
      <slot>
        <el-link type="primary" style="font-size: 12px;">查看相似</el-link>
      </slot>
    </template>

    <!-- 相似装备内容 -->
    <div v-if="visible">
      <!-- 加载状态 -->
      <div v-if="valuationLoading" class="loading-info">
        <el-skeleton :rows="12" animated />
      </div>
      <div v-else>
        <div class="similar-header">
          <h4>相似装备 (共{{ similarData.anchor_count }}个) <el-divider direction="vertical" />
            <el-tag type="info" size="mini">相似度阈值: {{ similarData.similarity_threshold }}</el-tag>
            <el-divider direction="vertical" />
            <el-tag type="info" size="mini">最大锚点数: {{ similarData.max_anchors }}</el-tag>
          </h4>
          <!-- 装备估价信息 -->
          <EquipmentValuation :valuation="equipmentValuation" :target-equipment="getEquipImageProps(equipment)"
            @refresh="refresh" />
          <div v-if="similarData.statistics" class="stats">
            <span>
              价格范围:
              <span v-html="formatPrice(similarData.statistics.price_range.min)"></span>
              -
              <span v-html="formatPrice(similarData.statistics.price_range.max)"></span>
            </span>
            <span> 平均相似度: {{ similarData.statistics.similarity_range.avg.toFixed(3) }} </span>
          </div>
        </div>

        <!-- 相似装备表格 -->
        <el-empty v-if="!anchorsLoading && !similarData.anchors?.length" description="暂无数据"></el-empty>
        <similar-equipment-table v-else :anchors="similarData.anchors" :loading="anchorsLoading" />
      </div>
      <!-- 错误状态 -->
      <div v-if="error" class="error-info">
        <el-empty description="加载失败">
          <el-button type="primary" @click="loadSimilarEquipments">重试</el-button>
        </el-empty>
      </div>
    </div>
  </el-popover>
</template>

<script>
import EquipmentValuation from './EquipmentValuation.vue'
import SimilarEquipmentTable from './SimilarEquipmentTable.vue'
import { equipmentMixin } from '@/utils/mixins/equipmentMixin'
import { commonMixin } from '@/utils/mixins/commonMixin'

export default {
  name: 'SimilarEquipmentModal',
  components: {
    EquipmentValuation,
    SimilarEquipmentTable
  },
  mixins: [equipmentMixin, commonMixin],
  props: {
    equipment: {
      type: Object,
      required: true
    },
    placement: {
      type: String,
      default: 'left-end'
    },
    similarityThreshold: {
      type: Number,
      default: 0.8
    },
    maxAnchors: {
      type: Number,
      default: 30
    }
  },
  data() {
    return {
      visible: false,
      valuationLoading: false,  // 装备估价接口加载状态
      anchorsLoading: false,    // 相似装备锚点接口加载状态
      error: false,
      similarData: null,
      equipmentValuation: {}
    }
  },
  computed: {
    // 整体加载状态
    loading() {
      return this.valuationLoading || this.anchorsLoading
    }
  },
  methods: {
    async handleShow() {
      if (!this.similarData) {
        await this.loadSimilarEquipments()
      }
    },

    async refresh() {
      await this.loadSimilarEquipments()
    },

    // 加载相似装备
    async loadSimilarEquipments() {
      this.error = false
      this.equipmentValuation = {}
      this.similarData = null

      try {
        await this.loadEquipmentValuation(this.equipment, this.similarityThreshold)
      } catch (error) {
        console.error('加载相似装备失败:', error)
        this.error = true
      }
    },

    // 统一的装备估价加载方法
    async loadEquipmentValuation(equipment, similarityThreshold) {
      try {
        // 第一个接口：获取估价信息
        this.valuationLoading = true
        const valuationResponse = await this.$api.equipment.getEquipmentValuation({
          equipment_data: equipment,
          strategy: 'fair_value',
          similarity_threshold: similarityThreshold,
          max_anchors: this.maxAnchors
        })
        const data = valuationResponse.data
        this.equipmentValuation = data
        this.similarData = {
          anchor_count: data.anchor_count,
          similarity_threshold: data.similarity_threshold,
          max_anchors: data.max_anchors,
          anchors: [],
          statistics: {
            price_range: data.price_range,
            similarity_range: { min: 0, max: 0, avg: 0 }
          }
        }
        this.valuationLoading = false

        // 处理估价响应
        if (valuationResponse.code === 200 && data.anchor_count && data.anchor_count > 0) {
          // 第二个接口：获取相似装备锚点数据
          this.anchorsLoading = true
          const { data: { anchors: allAnchors } } = await this.$api.equipment.findEquipmentAnchors({
            equipment_data: equipment,
            similarity_threshold: similarityThreshold,
            max_anchors: this.maxAnchors
          })

          this.anchorsLoading = false

          // 从估价结果中提取相似装备信息
          this.$set(this.similarData, 'anchors', allAnchors)
          this.$set(this.similarData, 'statistics', {
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
          })
        }
      } catch (error) {
        console.error('获取装备估价失败:', error)
        throw error
      } finally {
        // 确保在出现异常时也重置加载状态
        this.valuationLoading = false
        this.anchorsLoading = false
      }
    }
  }
}
</script>

<style scoped>
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

.error-info {
  padding: 20px 0;
}

.loading-info {
  padding: 20px;
}

.loading-status {
  margin-bottom: 16px;
}

.loading-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: #409eff;
  font-size: 14px;
}

.loading-item i {
  margin-right: 8px;
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}
</style>
