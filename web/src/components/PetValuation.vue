<template>
  <div class="valuation-info" :class="confidenceClass">
    <el-row type="flex" align="middle" justify="space-between">
      <el-row type="flex" align="middle">
        <PetImage :pet="targetPet.petData" trigger="hover" :equipFaceImg="targetPet.equip_face_img" />
        <span v-html="formatFullPrice(targetPet)" style="margin-left: 10px"></span>
      </el-row>
      <!-- 刷新和相似界面 -->
      <div style="width: 170px;flex-shrink: 0;">
        <el-button type="primary" @click="$emit('refresh')" size="mini" style="margin-right: 5px;">刷新</el-button>
        <SimilarGetMore :target-equipment="targetPet" type="pet" />
      </div>
    </el-row>
    <div class="valuation-main">
      <span class="valuation-label">召唤兽估价:</span>
      <span class="valuation-price">{{ valuation ? (valuation.estimated_price_yuan + valuation.equip_estimated_price / 100
      ).toFixed(2) + '元' : '-' }} </span>
      <span class="valuation-strategy">({{ valuation ? getStrategyName(valuation.strategy) : '-' }})</span>

      <!-- 价格比率显示 -->
      <span v-if="priceRatio" class="price-ratio" :class="priceRatioClass">
        <el-tag :type="priceRatioTagType" disable-transitions>
          {{ priceRatioText }}
        </el-tag>
      </span>
    </div>
    <div class="valuation-equip">
      <el-tag>裸宠:￥{{ valuation.estimated_price_yuan }}</el-tag> <el-divider direction="vertical" />
      <el-tag type="success">装备:￥{{ valuation.equip_estimated_price / 100 }}</el-tag>
    </div>
    <div class="valuation-details">
      <span class="confidence-display" :class="confidenceTextClass">
        <i :class="confidenceIcon"></i>
        置信度: {{ valuation ? (valuation.confidence * 100).toFixed(1) + '%' : '-' }}
        <span class="confidence-level">{{ confidenceLevel }}</span>
      </span>
      <span>基于{{ valuation ? valuation.anchor_count + '个锚点' : '-' }}</span>
      <span v-if="priceRatio">估价比率: {{ (priceRatio * 100).toFixed(1) }}%</span>
    </div>
  </div>
</template>

<script>
import PetImage from './PetImage.vue'
import { petMixin } from '@/utils/mixins/petMixin'
import { commonMixin } from '@/utils/mixins/commonMixin'
import SimilarGetMore from './SimilarGetMore.vue'
export default {
  name: 'PetValuation',
  components: {
    PetImage,
    SimilarGetMore
  },
  mixins: [petMixin, commonMixin],
  props: {
    valuation: {
      type: Object,
      default: null
    },
    targetPet: {
      type: Object,
      required: true
    }
  },
  computed: {
    // 计算估价与售价的比率
    priceRatio() {
      if (!this.valuation || !this.valuation.estimated_price_yuan || !this.targetPet.price) {
        return null
      }

      const estimatedPrice = parseFloat(this.valuation.estimated_price)
      const sellingPrice = parseFloat(this.targetPet.price)
      if (sellingPrice === 0) return null

      return estimatedPrice / sellingPrice
    },

    // 根据比率生成文本提示
    priceRatioText() {
      if (!this.priceRatio) return ''
      const ratio = this.priceRatio
      const deviation = Math.abs(ratio - 1) * 100
      if (deviation < 5) {
        return `估价极为贴合市场（±${deviation.toFixed(1)}%）`
      } else if (deviation < 10) {
        return `估价较为贴合（±${deviation.toFixed(1)}%）`
      } else if (deviation < 20) {
        return `估价有一定偏差（±${deviation.toFixed(1)}%）`
      } else if (ratio > 1) {
        return `估价高于市场（+${((ratio - 1) * 100).toFixed(1)}%）`
      } else {
        return `估价低于市场（-${((1 - ratio) * 100).toFixed(1)}%）`
      }
    },

    // 价格比率样式类
    priceRatioClass() {
      if (!this.priceRatio) return ''

      const ratio = this.priceRatio
      if (ratio > 1.2) {
        return 'ratio-low' // 估价高于售价，售价偏低
      } else if (ratio < 0.8) {
        return 'ratio-high' // 估价低于售价，售价偏高
      } else {
        return 'ratio-normal'
      }
    },

    priceRatioTagType() {
      if (!this.priceRatio) return ''
      const ratio = this.priceRatio
      const deviation = Math.abs(ratio - 1) * 100
      if (deviation < 5) {
        return 'success'
      } else if (deviation < 10) {
        return 'info'
      } else if (deviation < 20) {
        return 'warning'
      } else {
        return 'danger'
      }
    },

    // 根据置信度返回对应的CSS类
    confidenceClass() {
      if (!this.valuation || !this.valuation.confidence) {
        return 'confidence-extremely-low'
      }

      const confidence = this.valuation.confidence

      if (confidence >= 0.8) {
        return 'confidence-high'        // >= 80%: 高置信度 (绿色)
      } else if (confidence >= 0.6) {
        return 'confidence-medium'      // 60-79%: 中等置信度 (蓝色)
      } else if (confidence >= 0.4) {
        return 'confidence-low'         // 40-59%: 较低置信度 (灰色)
      } else if (confidence >= 0.2) {
        return 'confidence-very-low'    // 20-39%: 很低置信度 (橙色)
      } else {
        return 'confidence-extremely-low' // < 20%: 极低置信度 (红色)
      }
    },

    // 置信度文本颜色类
    confidenceTextClass() {
      if (!this.valuation || !this.valuation.confidence) {
        return 'text-danger'
      }

      const confidence = this.valuation.confidence

      if (confidence >= 0.8) {
        return 'text-success'
      } else if (confidence >= 0.6) {
        return 'text-primary'
      } else if (confidence >= 0.4) {
        return 'text-info'
      } else if (confidence >= 0.2) {
        return 'text-warning'
      } else {
        return 'text-danger'
      }
    },

    // 置信度图标
    confidenceIcon() {
      if (!this.valuation || !this.valuation.confidence) {
        return 'el-icon-warning'
      }

      const confidence = this.valuation.confidence

      if (confidence >= 0.8) {
        return 'el-icon-success'
      } else if (confidence >= 0.6) {
        return 'el-icon-info'
      } else if (confidence >= 0.4) {
        return 'el-icon-warning'
      } else {
        return 'el-icon-error'
      }
    },

    // 置信度等级文本
    confidenceLevel() {
      if (!this.valuation || !this.valuation.confidence) {
        return '极低'
      }

      const confidence = this.valuation.confidence

      if (confidence >= 0.8) {
        return '高'
      } else if (confidence >= 0.6) {
        return '中'
      } else if (confidence >= 0.4) {
        return '较低'
      } else if (confidence >= 0.2) {
        return '很低'
      } else {
        return '极低'
      }
    }
  },
  methods: {
    // 获取策略显示名称
    getStrategyName(strategy) {
      const strategyMap = {
        'fair_value': '公允价值',
        'market_price': '市场价格',
        'weighted_average': '加权平均'
      }
      return strategyMap[strategy] || strategy
    },
  }
}
</script>

<style scoped>
.valuation-info {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 16px;
}

.valuation-main {
  margin: 8px 0;
  font-size: 16px;
  font-weight: bold;
}

.valuation-label {
  color: #606266;
  margin-right: 8px;
}

.valuation-price {
  color: #e6a23c;
  font-size: 18px;
}

.valuation-strategy {
  color: #909399;
  font-size: 12px;
  font-weight: normal;
  margin-left: 8px;
}

.price-ratio {
  margin-left: 12px;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: normal;
}

.ratio-low {
  background: #f0f9ff;
  color: #1890ff;
}

.ratio-high {
  background: #fff2f0;
  color: #ff4d4f;
}

.ratio-normal {
  background: #f6ffed;
  color: #52c41a;
}

.valuation-details {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.valuation-details span {
  white-space: nowrap;
}

/* 置信度显示样式 */
.confidence-display {
  display: flex;
  align-items: center;
  gap: 4px;
}

.confidence-display i {
  font-size: 14px;
}

.confidence-level {
  font-weight: bold;
  font-size: 11px;
  padding: 1px 4px;
  border-radius: 2px;
  background: rgba(0, 0, 0, 0.1);
}

/* 文本颜色类 */
.text-success {
  color: #67c23a !important;
}

.text-primary {
  color: #409eff !important;
}

.text-info {
  color: #909399 !important;
}

.text-warning {
  color: #e6a23c !important;
}

.text-danger {
  color: #f56c6c !important;
}

/* 根据置信度的颜色变化 */
.valuation-info.confidence-high {
  border-left: 4px solid #67c23a;
  /* 绿色 - 高置信度 */
  background: linear-gradient(270deg, #f0f9ff 0%, #e1f3d8 100%);
}

.valuation-info.confidence-medium {
  border-left: 4px solid #409eff;
  /* 蓝色 - 中等置信度 */
  background: linear-gradient(270deg, #f0f8ff 0%, #e1f5fe 100%);
}

.valuation-info.confidence-low {
  border-left: 4px solid #909399;
  /* 灰色 - 较低置信度 */
  background: linear-gradient(270deg, #f8f9fa 0%, #e9ecef 100%);
}

.valuation-info.confidence-very-low {
  border-left: 4px solid #e6a23c;
  /* 橙色 - 很低置信度 */
  background: linear-gradient(270deg, #fdf6ec 0%, #fdf2e9 100%);
}

.valuation-info.confidence-extremely-low {
  border-left: 4px solid #f56c6c;
  /* 红色 - 极低置信度 */
  background: linear-gradient(270deg, #fef0f0 0%, #fde2e2 100%);
}
</style>