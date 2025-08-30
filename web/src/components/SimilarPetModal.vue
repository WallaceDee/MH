<template>
  <el-popover  placement="left-end" width="860" trigger="click"
    popper-class="similar-pet-popper" @show="handleShow" v-model="visible">
    <template #reference>
      <el-link type="primary" style="font-size: 12px;">查看相似</el-link>
    </template>
    
    <!-- 相似召唤兽内容 -->
    <div v-if="visible">
      <div v-if="similarData">
        <div class="similar-header">
          <h4>相似召唤兽 (共{{ similarData.anchor_count }}个)<em style="font-size: 12px;">-相似度阈值: {{
            similarData.similarity_threshold }}</em></h4>
          <!-- 召唤兽估价信息 -->
          <PetValuation :valuation="valuation" :target-pet="pet" :equip_sn="pet.equip_sn"/>
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
        <!-- 相似召唤兽表格 -->
        <similar-pet-table v-if="similarData.anchors?.length>0" :anchors="similarData.anchors" :target-pet="pet" />
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
import PetValuation from './PetValuation.vue'
import SimilarPetTable from './SimilarPetTable.vue'
import { commonMixin } from '@/utils/mixins/commonMixin'
export default {
  name: 'SimilarPetModal',
  components: {
    PetValuation,
    SimilarPetTable
  },
  mixins: [commonMixin],
  props: {
    pet: {
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
    }
  },
  data() {
    return {
      visible: false
    }
  },
  methods: {
    handleShow() {
      this.$emit('show', this.pet)
    },
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