<template>
  <div class="valuation-info">
    <el-row type="flex" align="middle" justify="space-between">
      <el-row type="flex" align="middle">
        <PetImage :pet="targetPet.petData" trigger="hover" :equipFaceImg="targetPet.equip_face_img" />
        <span v-html="formatFullPrice(targetPet)" style="margin-left: 10px"></span>
      </el-row>
      <!-- 无锚点时的重试界面 -->
      <SimilarGetMore :target-equipment="targetPet" type="pet"/>
    </el-row>
    <div class="valuation-main">
      <span class="valuation-label">召唤兽估价:</span>
      <span class="valuation-price">{{ valuation ? (valuation.estimated_price_yuan+valuation.equip_estimated_price/100 ).toFixed(2) + '元' : '-' }} </span>
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
      <el-tag type="success">装备:￥{{ valuation.equip_estimated_price/100 }}</el-tag>
    </div>
    <div class="valuation-details">
      <span>置信度: {{ valuation ? (valuation.confidence * 100).toFixed(1) + '%' : '-' }}</span>
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
</style>