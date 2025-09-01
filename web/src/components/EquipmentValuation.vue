<template>
  <div class="valuation-info">
    <el-row type="flex" align="middle" justify="space-between">
      <el-row type="flex" align="middle">
        <EquipmentImage :equipment="targetEquipment" width="50px" height="50px" placement="left" />
        <span v-if="targetEquipment.price" v-html="formatFullPrice(targetEquipment)" style="margin-left: 10px"></span>
        <div v-if="isWeapon" style="margin-left: 10px">
          <div style="margin-bottom: 5px"> <el-tag type="success">属性：+{{ targetEquipment.feature.addon_total }}点{{
            addon_total_standards?.[targetEquipment.feature.equip_level] }}</el-tag>
            <el-divider direction="vertical" />
            <el-tag type="primary">总伤：{{ targetEquipment.feature.all_damage }}/{{
              parseInt(all_damage_standards?.[targetEquipment.feature.equip_level][1]
                + (25 * targetEquipment.feature.equip_level/30)) }}</el-tag>
          </div>
          <div>
            <el-tag type="danger">初伤：{{ targetEquipment.feature.init_damage_raw }}点{{
              init_damage_raw_standards?.[targetEquipment.feature.equip_level] }}</el-tag>
            <el-divider direction="vertical" />
            <el-tag type="danger">初总伤：{{ targetEquipment.feature.init_damage }}点{{
              all_damage_standards?.[targetEquipment.feature.equip_level] }}</el-tag>
          </div>
        </div>
      </el-row>
      <!-- 刷新和相似装备界面 -->
      <div style="width: 170px;flex-shrink: 0;">
        <el-button type="primary" @click="$emit('refresh')" size="mini">刷新</el-button>
        <SimilarGetMore :target-equipment="targetEquipment" />
      </div>
    </el-row>
    <div class="valuation-main">
      <span class="valuation-label">装备估价:</span>
      <span class="valuation-price">{{ valuation ? valuation.estimated_price_yuan + '元' : '-' }}</span>
      <span class="valuation-strategy">({{ valuation ? getStrategyName(valuation.strategy) : '-' }})</span>
      <el-link type="danger" @click.native="markAsAbnormal" size="mini">标记为异常</el-link>

      <!-- 价格比率显示 -->
      <span v-if="priceRatio" class="price-ratio" :class="priceRatioClass">
        <el-tag :type="priceRatioTagType" disable-transitions>
          {{ priceRatioText }}
        </el-tag>
      </span>
    </div>
    <div class="valuation-details">
      <span>置信度: {{ valuation ? (valuation.confidence * 100).toFixed(1) + '%' : '-' }}</span>
      <span>基于{{ valuation ? valuation.anchor_count + '个锚点' : '-' }}</span>
      <span v-if="priceRatio">估价比率: {{ (priceRatio * 100).toFixed(1) }}%</span>
    </div>
  </div>
</template>

<script>
import EquipmentImage from './EquipmentImage/EquipmentImage.vue'
import { equipmentMixin } from '@/utils/mixins/equipmentMixin'
import { commonMixin } from '@/utils/mixins/commonMixin'
import SimilarGetMore from './SimilarGetMore.vue'

export default {
  name: 'EquipmentValuation',
  components: {
    EquipmentImage,
    SimilarGetMore
  },
  mixins: [equipmentMixin, commonMixin],
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
  data() {
    return {
      weaponConfig: null,
      addon_total_standards: null,
      all_damage_standards: null,
      init_damage_raw_standards: null,
    }
  },
  computed: {
    isWeapon() {
      return window.is_weapon_equip(this.targetEquipment?.feature?.kindid)
    },
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
    getWeaponConfig() {
      this.$api.equipment.getWeaponConfig().then(res => {
        if (res.code === 200) {
          this.weaponConfig = res.data
          this.addon_total_standards = res.data.addon_total_standards
          this.all_damage_standards = res.data.all_damage_standards
          this.init_damage_raw_standards = res.data.init_damage_raw_standards
        }
      })
    },
    async markAsAbnormal() {
      try {
        // 调用API标记装备为异常
        const response = await this.$api.equipment.markEquipmentAsAbnormal({
          equipment_data: this.targetEquipment,
          reason: '标记异常',
          notes: '用户手动标记的异常装备'
        })

        if (response.code === 200) {
          this.$notify.success({
            title: '提示',
            message: '装备已标记为异常'
          })
          // 可以触发父组件刷新或其他操作
          this.$emit('abnormal-marked', this.targetEquipment)
        } else {
          this.$notify.error({
            title: '提示',
            message: response.message || '标记异常失败'
          })
        }
      } catch (error) {
        console.error('标记异常失败:', error)
        this.$notify.error({
          title: '提示',
          message: '标记异常失败，请稍后重试'
        })
      }
    },
    getStrategyName(strategy) {
      const strategyNames = {
        fair_value: '公允价值',
        competitive: '竞争价格',
        premium: '溢价估值'
      }
      return strategyNames[strategy] || strategy
    },
  },
  mounted() {
    if (this.isWeapon) {
      this.getWeaponConfig()
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
