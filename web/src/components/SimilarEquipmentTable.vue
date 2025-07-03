<template>
  <el-table
    :data="anchors"
    stripe
    max-height="300"
    style="width: 100%"
    sortable
    :sort-by="['price', 'similarity']"
    :sort-order="['ascending', 'descending']"
  >
    <el-table-column fixed prop="price" label="价格 (元)" width="100" sortable>
      <template #default="scope">
        <div v-html="formatFullPrice(scope.row,true)"></div>
      </template>
    </el-table-column>
    <el-table-column fixed label="装备" width="70">
      <template #default="scope">
        <equipment-image :equipment="scope.row" />
      </template>
    </el-table-column>
    <el-table-column prop="similarity" label="相似度" width="80" sortable>
      <template #default="scope">
        <el-tag :type="getSimilarityTagType(scope.row.similarity)">
          {{ scope.row.similarity }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="equip_level" label="等级" width="60"></el-table-column>
    <el-table-column label="特技/特效/套装" width="120">
      <template #default="scope">
        <div class="special-info">
          <div
            class="equip_desc_blue"
            :data-specia-effet="scope.row.special_effect"
            :data-special-skill="scope.row.special_skill"
            v-html="formatSpecialSkillsAndEffects(scope.row.special_effect, scope.row.special_skill)"
          ></div>
          <span
            v-if="scope.row.suit_effect && scope.row.suit_effect !== 0"
            class="suit"
          >
            {{ formatSuitEffect(scope.row.suit_effect) }}
          </span>
        </div>
      </template>
    </el-table-column>
    <el-table-column prop="server_name" label="服务器" width="80">
      <template #default="scope">
        <span>{{ scope.row.server_name }}</span>
        <div v-html="formatFullPrice(scope.row,'cross')"></div>
      </template>
    </el-table-column>
    <el-table-column label="操作" width="80">
      <template #default="scope">
        <el-button type="text" @click="openCBG(scope.row.eid)" class="cbg-link">
          查看
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script>
import EquipmentImage from './EquipmentImage.vue'

export default {
  name: 'SimilarEquipmentTable',
  components: {
    EquipmentImage
  },
  props: {
    anchors: {
      type: Array,
      default: () => []
    }
  },
  methods: {
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
      if (!window.LoginInfo || !window.LoginInfo.login ) {
        return basePrice
      }

      const crossServerPoundage = equipment.cross_server_poundage || 0
      const fairShowPoundage = equipment.fair_show_poundage || 0

      if (!crossServerPoundage|| simple&&simple!=='cross') {
        if(simple&&simple=='cross'){
          return ''
        }
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
      if(simple&&simple=='cross'){
        return additionalFeeHtml
      }
      return basePrice + additionalFeeHtml
    },

    // 获取相似度标签类型
    getSimilarityTagType(similarity) {
      if (similarity >= 0.9) return 'success'
      if (similarity >= 0.8) return 'warning'
      if (similarity >= 0.7) return 'info'
      return 'danger'
    },

    // 格式化特技特效
    formatSpecialSkillsAndEffects(special_effect, special_skill) {
      const specials = []

      // 处理特效（JSON字符串格式）
      if (special_effect && special_effect !== '') {
        try {
          const effects = JSON.parse(special_effect)
          if (Array.isArray(effects)) {
            effects.forEach((effect) => {
              const effectName = this.getSpecialEffectName(parseInt(effect))
              if (effectName) specials.push(`${effectName}`)
            })
          }
        } catch (e) {
          console.warn('解析特效JSON失败:', e, special_effect)
        }
      }

      // 处理特技
      if (special_skill && special_skill !== 0) {
        const skillName = this.getSpecialSkillName(special_skill)
        if (skillName) specials.push(`${skillName}`)
      }

      return specials.join('<br />')
    },

    // 获取特效名称
    getSpecialEffectName(id) {
      // 直接使用全局变量
      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.equip_special_effect) {
        const effectName = window.AUTO_SEARCH_CONFIG.equip_special_effect[id.toString()]
        if (effectName) return effectName
      }

      return `特效${id}`
    },

    // 获取特技名称
    getSpecialSkillName(id) {
      // 直接使用全局变量
      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.equip_special_skills) {
        const skills = window.AUTO_SEARCH_CONFIG.equip_special_skills
        if (Array.isArray(skills)) {
          const skill = skills.find((item) => item[0] === parseInt(id))
          if (skill) return skill[1]
        }
      }

      return `特技${id}`
    },

    // 格式化套装效果
    formatSuitEffect(suit_effect) {
      if (!suit_effect) return ''

      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.suit_added_status) {
        const suitName = window.AUTO_SEARCH_CONFIG.suit_added_status[suit_effect.toString()]
        if (suitName) return `附加状态${suitName}`
      }

      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.suit_append_skills) {
        const suitName = window.AUTO_SEARCH_CONFIG.suit_append_skills[suit_effect.toString()]
        if (suitName) return `追加法术${suitName}`
      }
      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.suit_transform_skills) {
        const suitName = window.AUTO_SEARCH_CONFIG.suit_transform_skills[suit_effect.toString()]
        if (suitName) return `变身术之${suitName}`
      }
      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.suit_transform_charms) {
        const suitName = window.AUTO_SEARCH_CONFIG.suit_transform_charms[suit_effect.toString()]
        if (suitName) return `变化咒之${suitName}`
      }

      return `套装${suit_effect}`
    },

    // 打开CBG链接
    openCBG(eid) {
      const url = `https://xyq-m.cbg.163.com/cgi/mweb/equip/${eid.split('-')[1]}/${eid}`
      window.open(url, '_blank')
    }
  }
}
</script>

<style scoped>
.special-info {
  font-size: 12px;
  color: #409eff;
}

.special-info .skill {
  margin-bottom: 2px;
}

.cbg-link {
  color: #409eff;
  padding: 0;
}

.cbg-link:hover {
  color: #66b1ff;
}

:deep(.equip_desc_blue) {
  color: #3498db;
}
</style> 