<template>
  <el-popover
    :data-equip-sn="equipment.equip_sn"
    placement="left-end"
    width="640"
    trigger="click"
    popper-class="similar-equip-popper"
    @show="handleShow"
  >
    <template #reference>
      <el-link type="success">查看相似</el-link>
    </template>

    <!-- 相似装备内容 -->
    <div v-if="similarData">
      <div class="similar-header">
        <h4>相似装备 (共{{ similarData.anchor_count }}个)<em style="font-size: 12px;">-相似度阈值: {{ similarData.similarity_threshold }}</em></h4>
        <!-- 装备估价信息 -->
        <equipment-valuation :valuation="valuation" :target-equipment="equipment" />

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

      <!-- 无锚点时的重试界面 -->
      <similar-equipment-retry
        v-if="!similarData.anchors || similarData.anchors.length === 0"
        :message="similarData.message"
        :can-retry="similarData.canRetry"
        :current-threshold="similarData.similarity_threshold"
        :loading="loading"
        @retry="handleRetry"
      />

      <!-- 相似装备表格 -->
      <similar-equipment-table v-else :anchors="similarData.anchors" />
    </div>

    <!-- 错误信息 -->
    <div v-else-if="error" class="error-info">
      <el-alert type="error" :title="error" show-icon />
    </div>

    <!-- 加载状态 -->
    <div v-else class="loading-info">
      <el-skeleton :rows="5" animated />
    </div>
  </el-popover>
</template>

<script>
import EquipmentValuation from './EquipmentValuation.vue'
import SimilarEquipmentRetry from './SimilarEquipmentRetry.vue'
import SimilarEquipmentTable from './SimilarEquipmentTable.vue'

export default {
  name: 'SimilarEquipmentModal',
  components: {
    EquipmentValuation,
    SimilarEquipmentRetry,
    SimilarEquipmentTable
  },
  props: {
    equipment: {
      type: Object,
      required: true
    },
    similarData: {
      type: Object,
      default: null
    },
    valuation: {
      type: Object,
      default: null
    },
    error: {
      type: String,
      default: ''
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    handleShow() {
      this.$emit('show', this.equipment)
    },

    handleRetry(threshold) {
      this.$emit('retry', this.equipment.eid, threshold)
    },

    // 格式化价格
    formatPrice(price) {
      const priceFloat = parseFloat(price / 100)
      if (!priceFloat) return '---'
      return window.get_color_price ? window.get_color_price(priceFloat) : `${priceFloat}元`
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
</style>
