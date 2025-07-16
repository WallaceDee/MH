<template>
  <div v-if="valuation" class="valuation-info">
    <el-row type="flex" align="middle">
      <equipment-image :equipment="targetEquipment" width="50px" height="50px" />
      <span v-html="formatFullPrice(targetEquipment)" style="margin-left: 10px"></span>
    </el-row>
    <div class="valuation-main">
      <span class="valuation-label">装备估价:</span>
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
import EquipmentImage from './EquipmentImage.vue'

export default {
  name: 'EquipmentValuation',
  components: {
    EquipmentImage
  },
  props: {
    valuation: {
      type: Object,
      default: null
    },
    targetEquipment: {
      type: Object,
      required: true
    }
  },
  computed: {
    // 计算估价与售价的比率
    priceRatio() {
      if (!this.valuation || !this.valuation.estimated_price_yuan || !this.targetEquipment.price) {
        return null
      }

      const estimatedPrice = parseFloat(this.valuation.estimated_price_yuan)
      const sellingPrice = parseFloat(this.targetEquipment.price) / 100 // 转换为元

      if (sellingPrice === 0) return null

      return estimatedPrice / sellingPrice
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

    // 根据比率生成样式类
    priceRatioClass() {
      if (!this.priceRatio) return ''

      const ratio = this.priceRatio

      if (ratio >= 1.5) {
        return 'ratio-severe-high'
      } else if (ratio >= 1.2) {
        return 'ratio-high'
      } else if (ratio >= 1.1) {
        return 'ratio-slightly-high'
      } else if (ratio >= 0.95) {
        return 'ratio-reasonable'
      } else if (ratio >= 0.8) {
        return 'ratio-slightly-low'
      } else if (ratio >= 0.5) {
        return 'ratio-low'
      } else {
        return 'ratio-severe-low'
      }
    }
  },
  methods: {
    getStrategyName(strategy) {
      const strategyNames = {
        fair_value: '公允价值',
        competitive: '竞争价格',
        premium: '溢价估值'
      }
      return strategyNames[strategy] || strategy
    },

    // 格式化价格显示
    // 格式化价格
    formatPrice(price) {
      const priceFloat = parseFloat(price / 100)
      if (!priceFloat) return '---'
      return window.get_color_price ? window.get_color_price(priceFloat) : `${priceFloat}元`
    },
    // 格式化完整价格信息（包括跨服费用）
    formatFullPrice(equipment, simple = false) {
      const basePrice = this.formatPrice(equipment.price)

      // 检查是否有登录信息和跨服费用
      if (!window.LoginInfo || !window.LoginInfo.login || simple) {
        return basePrice
      }

      const crossServerPoundage = equipment.cross_server_poundage || 0
      const fairShowPoundage = equipment.fair_show_poundage || 0

      if (!crossServerPoundage) {
        return basePrice
      }

      let additionalFeeHtml = ''

      if (equipment.pass_fair_show == 1) {
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
  margin: 12px 0;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #409eff;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.valuation-main {
  font-size: 14px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.valuation-label {
  color: #606266;
  font-weight: 500;
}

.valuation-price {
  color: #e6a23c;
  font-weight: 600;
  font-size: 16px;
}

.valuation-strategy {
  color: #909399;
  font-size: 12px;
}

.valuation-details {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #909399;
  flex-wrap: wrap;
}

/* 价格比率样式 */
.price-ratio {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 8px;
}

.ratio-severe-high {
  background-color: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fbc4c4;
  font-weight: 600;
}

.ratio-high {
  background-color: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fbc4c4;
}

.ratio-slightly-high {
  background-color: #fdf6ec;
  color: #e6a23c;
  border: 1px solid #f5dab1;
}

.ratio-reasonable {
  background-color: #f0f9ff;
  color: #67c23a;
  border: 1px solid #c2e7b0;
}

.ratio-slightly-low {
  background-color: #f0f9ff;
  color: #409eff;
  border: 1px solid #b3d8ff;
}

.ratio-low {
  background-color: #f4f4f5;
  color: #909399;
  border: 1px solid #d3d4d6;
}

.ratio-severe-low {
  background-color: #f4f4f5;
  color: #909399;
  border: 1px solid #d3d4d6;
  font-weight: 600;
}
</style>
