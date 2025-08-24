<template>
  <el-popover :data-equip-sn="equipment.equip_sn" :placement="placement" width="640" trigger="click"
    popper-class="similar-equip-popper" v-model="visible" @show="handleShow">
    <template #reference>
      <slot>
        <el-link type="primary" style="font-size: 12px;" >查看相似</el-link>
      </slot>
    </template>

    <!-- 相似装备内容 -->
    <div v-if="visible">
      <div v-if="similarData">
        <div class="similar-header">
          <h4>相似装备 (共{{ similarData.anchor_count }}个)  <el-divider direction="vertical" />
            <el-tag type="info" size="mini">相似度阈值: {{ similarData.similarity_threshold }}</el-tag>
            <el-divider direction="vertical" />
            <el-tag type="info" size="mini">最大锚点数: {{ similarData.max_anchors }}</el-tag>
          </h4>
          <!-- 装备估价信息 -->
          <EquipmentValuation :valuation="valuation" :target-equipment="getEquipImageProps(equipment)" @refresh="refresh" />

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
        <similar-equipment-table v-if="similarData.anchors?.length" :anchors="similarData.anchors" />
        <el-empty v-else  description="暂无数据"></el-empty>
      </div>

      <!-- 加载状态 -->
      <div v-else class="loading-info">
        <el-skeleton :rows="12" animated />
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
  mixins: [equipmentMixin,commonMixin],
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
    placement: {
      type: String,
      default: 'left-end'
    }
  },
  data() {
    return {
      visible: false
    }
  },
  methods: {
    handleShow() {
      this.$emit('show', this.equipment)
    },
    refresh() {
      this.handleShow()
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
