<template>
  <div v-if="valuation" class="valuation-info">
    <el-row type="flex" align="middle">
      <pet-image :pet="targetPet.petData" trigger="hover" :equipFaceImg="targetPet.equip_face_img"/>
      <span v-html="formatFullPrice(targetPet)" style="margin-left: 10px"></span>
    </el-row>
    <div class="valuation-main">
      <span class="valuation-label">宠物估价:</span>
      <span class="valuation-price">{{ valuation.estimated_price_yuan }}元</span>
      <span class="valuation-strategy">({{ getStrategyName(valuation.strategy) }})</span>

      <!-- 价格比率显示 -->
      <span v-if="priceRatio" class="price-ratio" :class="priceRatioClass">
        <el-tag :type="priceRatioTagType" disable-transitions>
          {{ priceRatioText }}
        </el-tag>
      </span>
    </div>
    <div class="valuation-details">
      <span>置信度: {{ (valuation.confidence * 100).toFixed(1) }}%</span>
      <span>基于{{ valuation.anchor_count }}个锚点</span>
      <span v-if="priceRatio">估价比率: {{ (priceRatio * 100).toFixed(1) }}%</span>
    </div>
  </div>
</template>

<script>
import PetImage from './PetImage.vue'

export default {
  name: 'PetValuation',
  components: {
    PetImage
  },
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

      const estimatedPrice = parseFloat(this.valuation.estimated_price_yuan)
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
        return `✅ 估价极为贴合市场（±${deviation.toFixed(1)}%）`
      } else if (deviation < 10) {
        return `🟢 估价较为贴合（±${deviation.toFixed(1)}%）`
      } else if (deviation < 20) {
        return `🟡 估价有一定偏差（±${deviation.toFixed(1)}%）`
      } else if (ratio > 1) {
        return `🔴 估价高于市场（+${((ratio - 1) * 100).toFixed(1)}%）`
      } else {
        return `🔵 估价低于市场（-${((1 - ratio) * 100).toFixed(1)}%）`
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

    // 格式化价格
    formatPrice(price) {
      if (!price) return '---'
      return window.get_color_price ? window.get_color_price(price) : `${price}元`
    },

    // 格式化完整价格信息（包括跨服费用）
    formatFullPrice(pet) {
      const basePrice = this.formatPrice(pet.price)

      // 检查是否有登录信息和跨服费用
      if (!window.LoginInfo || !window.LoginInfo.login) {
        return basePrice
      }

      const crossServerPoundage = pet.cross_server_poundage || 0
      const fairShowPoundage = pet.fair_show_poundage || 0

      if (!crossServerPoundage) {
        return basePrice
      }

      let additionalFeeHtml = ''

      if (pet.pass_fair_show == 1) {
        // 跨服费
        const crossFee = parseFloat(crossServerPoundage / 100)
        additionalFeeHtml = `<div class="f12px" style="color: #666;">另需跨服费<span class="p1000">￥${crossFee}</span></div>`
      } else {
        // 信息费（跨服费 + 预订费）
        const totalFee = parseFloat((crossServerPoundage + fairShowPoundage) / 100)
        additionalFeeHtml = `<div class="f12px" style="color: #666;">另需信息费<span class="p1000">￥${totalFee}</span></div>`
      }

      return basePrice + additionalFeeHtml
    }
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