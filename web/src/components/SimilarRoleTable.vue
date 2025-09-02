<template>
  <el-table
    :data="anchors"
    stripe
    max-height="400"
    style="width: 100%"
    sortable
    :sort-by="['price', 'similarity']"
    :sort-order="['ascending', 'descending']"
  >
    <el-table-column fixed prop="price" label="价格 (元)" width="100" sortable>
      <template #default="scope">
        <div class="price-cell">{{ formatPrice(scope.row.price) }}</div>
      </template>
    </el-table-column>

    <el-table-column prop="similarity" label="相似度" width="90" sortable>
      <template #default="scope">
        <el-tag :type="getSimilarityTagType(scope.row.similarity)">
          {{ scope.row.similarity.toFixed(3) }}
        </el-tag>
      </template>
    </el-table-column>

    <el-table-column prop="nickname" label="角色名" width="120">
      <template #default="scope">
        <div class="role-name">{{ scope.row.nickname }}</div>
      </template>
    </el-table-column>

    <el-table-column prop="level" label="等级" width="80" sortable></el-table-column>

    <el-table-column prop="school_desc" label="门派" width="80">
      <template #default="scope">
        <el-tag size="mini" :type="getSchoolTagType(scope.row.school_desc)">
          {{ scope.row.school_desc }}
        </el-tag>
      </template>
    </el-table-column>

    <el-table-column label="修炼信息" min-width="140">
      <template #default="scope">
        <div class="cultivation-info">
          <div class="cultivation-row">
            <span class="cultivation-label">攻防法抗:</span>
            <span class="cultivation-values">
              {{ scope.row.expt_ski1 || 0 }}/{{ scope.row.expt_ski2 || 0 }}/{{ scope.row.expt_ski3 || 0 }}/{{ scope.row.expt_ski4 || 0 }}
            </span>
          </div>
          <div class="cultivation-row">
            <span class="cultivation-label">召兽修炼:</span>
            <span class="cultivation-values">
              {{ scope.row.beast_ski1 || 0 }}/{{ scope.row.beast_ski2 || 0 }}/{{ scope.row.beast_ski3 || 0 }}/{{ scope.row.beast_ski4 || 0 }}
            </span>
          </div>
          <div class="cultivation-row" v-if="scope.row.total_cultivation">
            <span class="cultivation-label">总修炼:</span>
            <span class="cultivation-values total-cultivation">{{ scope.row.total_cultivation }}</span>
          </div>
        </div>
      </template>
    </el-table-column>

    <el-table-column label="特殊属性" min-width="120">
      <template #default="scope">
        <div class="special-attributes">
          <div v-if="scope.row.sum_exp" class="attr-item">
            <span class="attr-label">总经验:</span>
            <span class="attr-value">{{ scope.row.sum_exp }}亿</span>
          </div>
          <div v-if="scope.row.all_new_point" class="attr-item">
            <span class="attr-label">乾元丹:</span>
            <span class="attr-value special-value">{{ scope.row.all_new_point }}点</span>
          </div>
          <div v-if="scope.row.three_fly_lv" class="attr-item">
            <span class="attr-label">化圣:</span>
            <span class="attr-value special-value">{{ scope.row.three_fly_lv }}重</span>
          </div>
          <div v-if="scope.row.school_history_count > 1" class="attr-item">
            <span class="attr-label">转门派:</span>
            <span class="attr-value">{{ scope.row.school_history_count }}次</span>
          </div>
        </div>
      </template>
    </el-table-column>

    <el-table-column prop="server_name" label="服务器" width="90">
      <template #default="scope">
        <div class="server-info">
          <span>{{ scope.row.server_name }}</span>
          <div v-if="scope.row.is_cross_server" class="cross-server-tag">
            <el-tag size="mini" type="info">跨服</el-tag>
          </div>
        </div>
      </template>
    </el-table-column>

    <el-table-column label="操作" width="80" fixed="right">
      <template #default="scope">
        <el-link :href="getCBGLinkByType(scope.row.eid)" type="danger" target="_blank">藏宝阁</el-link>
      </template>
    </el-table-column>
  </el-table>
</template>

<script>
import { commonMixin } from '@/utils/mixins/commonMixin'

export default {
  name: 'SimilarRoleTable',
  mixins: [commonMixin],
  props: {
    anchors: {
      type: Array,
      required: true
    }
  },
  methods: {
    formatPrice(price) {
      if (!price) return '0元'
      return `${(price / 100).toFixed(2)}元`
    },
    getSimilarityTagType(similarity) {
      if (similarity >= 0.9) {
        return 'success'
      } else if (similarity >= 0.7) {
        return 'primary'
      } else if (similarity >= 0.5) {
        return 'info'
      } else if (similarity >= 0.3) {
        return 'warning'
      } else {
        return 'danger'
      }
    },
    getSchoolTagType(school) {
      // 根据门派返回不同的标签类型
      const physicalSchools = ['大唐官府', '狮驼岭', '神木林']
      const magicSchools = ['龙宫', '魔王寨', '五庄观']
      const healSchools = ['普陀山', '化生寺']
      const speedSchools = ['盘丝岭', '女儿村']
      
      if (physicalSchools.includes(school)) {
        return 'danger'
      } else if (magicSchools.includes(school)) {
        return 'primary'
      } else if (healSchools.includes(school)) {
        return 'success'
      } else if (speedSchools.includes(school)) {
        return 'warning'
      } else {
        return 'info'
      }
    }
  }
}
</script>

<style scoped>
.price-cell {
  font-weight: 600;
  color: #e6a23c;
}

.role-name {
  font-weight: 500;
  color: #303133;
}

.cultivation-info {
  font-size: 12px;
}

.cultivation-row {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.cultivation-label {
  color: #909399;
  min-width: 60px;
  font-size: 11px;
}

.cultivation-values {
  color: #606266;
  font-family: monospace;
}

.total-cultivation {
  color: #409eff;
  font-weight: 600;
}

.special-attributes {
  font-size: 12px;
}

.attr-item {
  display: flex;
  align-items: center;
  margin-bottom: 3px;
}

.attr-label {
  color: #909399;
  min-width: 50px;
  font-size: 11px;
}

.attr-value {
  color: #606266;
}

.special-value {
  color: #e6a23c;
  font-weight: 600;
}

.server-info {
  text-align: center;
}

.cross-server-tag {
  margin-top: 4px;
}

/* 表格行悬停效果 */
.el-table tbody tr:hover > td {
  background-color: #f5f7fa !important;
}

/* 相似度标签样式优化 */
.el-tag {
  font-weight: 500;
}
</style> 