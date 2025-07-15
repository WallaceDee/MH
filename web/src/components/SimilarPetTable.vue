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
        <div v-html="formatFullPrice(scope.row, true)"></div>
      </template>
    </el-table-column>
    <el-table-column fixed label="宠物" width="70">
      <template #default="scope">
        <pet-image :pet="scope.row.petData" :equipFaceImg="scope.row.equip_face_img" trigger="hover"/>
      </template>
    </el-table-column>
    <el-table-column prop="similarity" label="相似度" width="80" sortable>
      <template #default="scope">
        <el-tag :type="getSimilarityTagType(scope.row.similarity)">
          {{ scope.row.similarity }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="level" label="等级" width="60"></el-table-column>
    <el-table-column label="技能/特性" width="120">
      <template #default="scope">
        <div class="special-info">
          <div class="pet-skills">
            <span v-if="scope.row.all_skill" class="skills-text">
              {{ formatSkills(scope.row.all_skill) }}
            </span>
          </div>
          <div v-if="scope.row.texing" class="pet-texing">
            <span class="texing-text">
              {{ formatTexing(scope.row.texing) }}
            </span>
          </div>
        </div>
      </template>
    </el-table-column>
    <el-table-column prop="server_name" label="服务器" width="80">
      <template #default="scope">
        <span>{{ scope.row.server_name }}</span>
        <div v-html="formatFullPrice(scope.row, 'cross')"></div>
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
import PetImage from './PetImage.vue'

export default {
  name: 'SimilarPetTable',
  components: {
    PetImage
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
      if (!price) return '---'
      return window.get_color_price ? window.get_color_price(price) : `${price}元`
    },
    
    // 格式化完整价格信息（包括跨服费用）
    formatFullPrice(pet, simple = false) {
      const basePrice = this.formatPrice(pet.price)

      // 检查是否有登录信息和跨服费用
      if (!window.LoginInfo || !window.LoginInfo.login) {
        return basePrice
      }

      const crossServerPoundage = pet.cross_server_poundage || 0
      const fairShowPoundage = pet.fair_show_poundage || 0

      if (!crossServerPoundage || simple && simple !== 'cross') {
        if (simple && simple == 'cross') {
          return ''
        }
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
      if (simple && simple == 'cross') {
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

    // 格式化技能
    formatSkills(allSkill) {
      if (!allSkill) return ''
      const skills = allSkill.split('|')
      return skills.slice(0, 3).join('|') + (skills.length > 3 ? '...' : '')
    },

    // 格式化特性
    formatTexing(texing) {
      if (!texing) return ''
      try {
        const texingObj = JSON.parse(texing)
        return texingObj.name || ''
      } catch (e) {
        return ''
      }
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

.pet-skills {
  margin-bottom: 2px;
}

.skills-text {
  color: #3498db;
}

.pet-texing {
  margin-top: 2px;
}

.texing-text {
  color: #e67e22;
}

.cbg-link {
  color: #409eff;
  padding: 0;
}

.cbg-link:hover {
  color: #66b1ff;
}
</style> 