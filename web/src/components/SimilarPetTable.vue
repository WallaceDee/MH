<template>
  <el-table :data="anchors" stripe max-height="300" style="width: 100%" sortable :sort-by="['price', 'similarity']"
    :sort-order="['ascending', 'descending']">
    <el-table-column fixed prop="price" label="价格 (元)" width="140" sortable>
      <template #default="scope">
        <span>{{ scope.row.server_name }}</span>
        <div v-html="formatFullPrice(scope.row)"></div>
      </template>
    </el-table-column>
    <el-table-column fixed label="召唤兽" width="70">
      <template #default="scope">
        <pet-image :pet="scope.row.petData" :equipFaceImg="scope.row.equip_face_img" trigger="hover" />
      </template>
    </el-table-column>
    <el-table-column prop="similarity" label="相似度" width="80" sortable>
      <template #default="scope">
        <el-tag :type="getSimilarityTagType(scope.row.similarity)">
          {{ scope.row.similarity }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="level" label="等级" width="140">
      <template #default="scope">
          <p :class="scope.row.petData.is_baobao === '是' ? 'cBlue' : 'equip_desc_red'">
            <span>{{ scope.row.petData.is_baobao === '是' ? '' : '野生' }}</span>
            <span>{{ scope.row.equip_name }}{{ scope.row.petData.is_baobao === '是' ? '宝宝' : '' }}/{{ scope.row.level
            }}级</span>
          </p>
          <p>参战等级：{{ scope.row.role_grade_limit }}级</p>
        </template>
    </el-table-column>
    <el-table-column prop="growth" label="成长" width="60">
      <template #default="scope">
        <span v-html="getColorNumber(scope.row.growth, [1, 1.3])"></span>
      </template>
    </el-table-column>
    <el-table-column prop="lx" label="灵性" width="60"></el-table-column>
    <el-table-column prop="equip_list" label="装备套装" width="80">
      <template #default="{ row: { equip_list } }">
        {{ getEquipSuitEffect(equip_list) }}
      </template>
    </el-table-column>
    <el-table-column label="技能/特性" width="120">
      <template #default="scope">
        <div class="special-info">
          <div class="pet-skills">
            <span v-if="scope.row.all_skill" class="skills-text">
              {{ formatSkillsDiff(scope.row.all_skill,targetPet)}}
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
    <el-table-column label="操作" width="80">
      <template #default="scope">
        <el-link :href="getCBGLinkByType(scope.row.eid, 'pet')" type="danger" target="_blank">藏宝阁</el-link>
      </template>
    </el-table-column>
  </el-table>
</template>

<script>
import PetImage from './PetImage.vue'
import { petMixin } from '@/utils/mixins/petMixin'
import { equipmentMixin } from '@/utils/mixins/equipmentMixin'
import { commonMixin } from '@/utils/mixins/commonMixin'

export default {
  name: 'SimilarPetTable',
  components: {
    PetImage
  },
  mixins: [equipmentMixin, commonMixin, petMixin],
  props: {
    anchors: {
      type: Array,
      default: () => []
    },
    targetPet: {
      type: Object,
      default: null
    }
  },
  methods: {
    getEquipSuitEffect(equipList) {
      if (!equipList) return ''

      try {
        const equipArray = JSON.parse(equipList).filter((equip) => equip)

        // 用于存储套装效果及其出现次数
        const suitEffects = {}

        // 遍历装备数组，提取套装效果
        equipArray.forEach((equip) => {
          if (equip.desc) {
            // 匹配套装效果：套装效果：附加状态 + 技能名称
            const suitMatch = equip.desc.match(/#c4DBAF4套装效果：附加状态#c4DBAF4([^#]+)/)
            if (suitMatch && suitMatch[1]) {
              const suitName = suitMatch[1].trim()
              suitEffects[suitName] = (suitEffects[suitName] || 0) + 1
            }
          }
        })

        // 检查是否有达到3件套的效果
        for (const [suitName, count] of Object.entries(suitEffects)) {
          if (count >= 3) {
            return suitName
          }
          // 如果没有达到3件套，返回装备数量
          return suitName + `(${count}/3)`
        }

        return ''
      } catch (error) {
        console.error('解析装备列表失败:', error)
        return ''
      }
    },
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
