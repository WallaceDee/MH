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
    <el-table-column label="特技/特效/套装" min-width="120">
      <template #default="scope">
        <div class="special-info">
          <div
            class="equip_desc_blue"
            :data-specia-effet="scope.row.special_effect"
            :data-special-skill="scope.row.special_skill"
          ></div>
         <p v-html="formatSpecialSkillsAndEffects(scope.row)"></p>
          <p>  {{ formatSuitEffect(scope.row) }}</p>
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
        <el-link :href="getCBGLinkByType(scope.row.eid, 'equip')" type="danger" target="_blank">藏宝阁</el-link>
      </template>
    </el-table-column>
  </el-table>
</template>

<script>
import EquipmentImage from './EquipmentImage.vue'
import { equipmentMixin } from '@/utils/mixins/equipmentMixin'
import { commonMixin } from '@/utils/mixins/commonMixin'

export default {
  name: 'SimilarEquipmentTable',
  components: {
    EquipmentImage
  },
  mixins: [equipmentMixin, commonMixin],
  props: {
    anchors: {
      type: Array,
      default: () => []
    }
  },
  methods: {

    // 获取特效名称
    getSpecialEffectName(id) {
      // 直接使用全局变量
      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.equip_special_effect) {
        const effectName = window.AUTO_SEARCH_CONFIG.equip_special_effect[id.toString()]
        if (effectName) return effectName
      }

      return `特效${id}`
    },
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
</style> 