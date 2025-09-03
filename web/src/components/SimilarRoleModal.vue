<template>
  <el-popover :data-role-eid="role.eid" :placement="placement" width="800" trigger="click"
    popper-class="similar-role-popper" v-model="visible" @show="handleShow">
    <template #reference>
      <slot>
        <el-link type="primary" style="font-size: 12px;">查看相似</el-link>
      </slot>
    </template>

    <!-- 相似角色内容 -->
    <div v-if="visible">
      <div v-if="similarData">
        <div class="similar-header">
          <h4>相似角色 (共{{ similarData.anchor_count }}个) <el-divider direction="vertical" />
            <el-tag type="info" size="mini">相似度阈值: {{ similarData.similarity_threshold }}</el-tag>
            <el-divider direction="vertical" />
            <el-tag type="info" size="mini">最大锚点数: {{ similarData.max_anchors }}</el-tag>
          </h4>

          <!-- 角色估价信息 -->
          <div class="valuation-info" :class="confidenceClass">
            <el-row type="flex" align="middle" justify="space-between">
              <el-row type="flex" align="middle">
                <RoleImage :key="role.eid" :other_info="role.other_info" :roleInfo="role.roleInfo" />
                <div style="margin-left: 10px">
                  <div class="role-basic-info">
                    <el-tag type="danger" size="mini">  {{ getServerHeatLabel(role.serverid) }}/{{ role.server_name }}</el-tag>
                    /
                    <el-tag type="primary" size="mini">{{ role.level }}</el-tag>
                    /
                    <el-tag type="info" size="mini">{{ role.roleInfo.basic_info.school }}</el-tag>
                  </div>
                </div>
              </el-row>
              <!-- 刷新按钮 -->
              <div style="width: 60px;flex-shrink: 0;">
                <el-button type="primary" @click="refresh" size="mini">刷新</el-button>
              </div>
            </el-row>

            <div class="valuation-main">
              <span class="valuation-label">角色估价:</span>
              <span class="valuation-price">{{ similarData?.valuation?.estimated_price_yuan || '-' }}元</span>
              <span class="valuation-strategy">({{ getStrategyName(similarData?.valuation?.strategy) }})</span>
            </div>

            <div class="valuation-details">
              <span class="confidence-display" :class="confidenceTextClass">
                <i :class="confidenceIcon"></i>
                置信度: {{ similarData?.valuation ? (similarData.valuation.confidence * 100).toFixed(1) + '%' : '-' }}
                <span class="confidence-level">{{ confidenceLevel }}</span>
              </span>
              <span>锚点数: {{ similarData?.anchor_count || '-' }}</span>
            </div>
          </div>

          <!-- 统计信息 -->
          <div v-if="similarData.statistics" class="stats">
            <span>
              价格范围:
              <span v-html="formatPrice(similarData.statistics.price_range.min)"></span>
              -
              <span v-html="formatPrice(similarData.statistics.price_range.max)"></span>
            </span>
            <span>平均相似度: {{ similarData.statistics.similarity_range.avg.toFixed(3) }}</span>
          </div>
        </div>

        <!-- 相似角色表格 -->
        <similar-role-table v-if="similarData.anchors?.length" :anchors="similarData.anchors" />
        <el-empty v-else description="暂无相似角色数据"></el-empty>
      </div>

      <!-- 加载状态 -->
      <div v-else class="loading-info">
        <el-skeleton :rows="12" animated />
      </div>
    </div>
  </el-popover>
</template>

<script>
import SimilarRoleTable from './SimilarRoleTable.vue'
import { commonMixin } from '@/utils/mixins/commonMixin'
import RoleImage from './RoleInfo/RoleImage.vue'

export default {
  name: 'SimilarRoleModal',
  components: {
    SimilarRoleTable,
    RoleImage
  },
  mixins: [commonMixin],
  props: {
    role: {
      type: Object,
      required: true
    },
    similarData: {
      type: Object,
      default: null
    },
    placement: {
      type: String,
      default: 'left-end'
    }
  },
  data() {
    return {
      visible: false,
      hotServersConfig: window.hotServersConfig || []
    }
  },
  computed: {

    confidenceClass() {
      if (!this.similarData?.valuation?.confidence) {
        return 'confidence-extremely-low'
      }

      const confidence = this.similarData.valuation.confidence

      if (confidence >= 0.8) {
        return 'confidence-high'
      } else if (confidence >= 0.6) {
        return 'confidence-medium'
      } else if (confidence >= 0.4) {
        return 'confidence-low'
      } else if (confidence >= 0.2) {
        return 'confidence-very-low'
      } else {
        return 'confidence-extremely-low'
      }
    },
    confidenceTextClass() {
      if (!this.similarData?.valuation?.confidence) {
        return 'text-danger'
      }

      const confidence = this.similarData.valuation.confidence

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
    confidenceIcon() {
      if (!this.similarData?.valuation?.confidence) {
        return 'el-icon-warning'
      }

      const confidence = this.similarData.valuation.confidence

      if (confidence >= 0.8) {
        return 'el-icon-success'
      } else if (confidence >= 0.6) {
        return 'el-icon-info'
      } else if (confidence >= 0.4) {
        return 'el-icon-question'
      } else if (confidence >= 0.2) {
        return 'el-icon-warning'
      } else {
        return 'el-icon-error'
      }
    },
    confidenceLevel() {
      if (!this.similarData?.valuation?.confidence) {
        return '(数据缺失)'
      }

      const confidence = this.similarData.valuation.confidence

      if (confidence >= 0.8) {
        return '(高)'
      } else if (confidence >= 0.6) {
        return '(中)'
      } else if (confidence >= 0.4) {
        return '(偏低)'
      } else if (confidence >= 0.2) {
        return '(很低)'
      } else {
        return '(极低)'
      }
    }
  },
  watch: {
    visible: {
      handler(newVal) {
        if(newVal) {
          this.loadHotServers()
        }
      },
      immediate: true
    }
  },
  methods: {
    getServerHeatLabel(serverid){
      const serverHeat = this.hotServersConfig.find(item => item.children.find(child => child.server_id === serverid))
      return serverHeat?.server_name||''
    },
    async loadHotServers() {
      if (!window.hotServersConfig) {
        window.hotServersConfig = await this.$api.system.getHotServers()
      }
      this.hotServersConfig = window.hotServersConfig
    },
    handleShow() {
      this.$emit('show', this.role)
    },
    refresh() {
      this.handleShow()
    },
    getStrategyName(strategy) {
      const strategyNames = {
        fair_value: '公允价值',
        competitive: '竞争价格',
        premium: '溢价估值'
      }
      return strategyNames[strategy] || strategy || '-'
    }
  }
}
</script>

<style scoped>
.similar-header {
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.similar-header h4 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

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

.role-basic-info {
  font-size: 14px;
  color: #606266;
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

.confidence-display {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.confidence-display i {
  font-size: 14px;
}

.confidence-level {
  font-size: 11px;
  opacity: 0.8;
}

.loading-info {
  padding: 20px;
}

.stats {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
  flex-wrap: wrap;
  margin-top: 10px;
}

/* 置信度文本颜色 */
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
  background: linear-gradient(270deg, #f0f9ff 0%, #e1f3d8 100%);
}

.valuation-info.confidence-medium {
  border-left: 4px solid #409eff;
  background: linear-gradient(270deg, #f0f8ff 0%, #e1f5fe 100%);
}

.valuation-info.confidence-low {
  border-left: 4px solid #909399;
  background: linear-gradient(270deg, #f8f9fa 0%, #e9ecef 100%);
}

.valuation-info.confidence-very-low {
  border-left: 4px solid #e6a23c;
  background: linear-gradient(270deg, #fdf6ec 0%, #fdf2e9 100%);
}

.valuation-info.confidence-extremely-low {
  border-left: 4px solid #f56c6c;
  background: linear-gradient(270deg, #fef0f0 0%, #fde2e2 100%);
}
</style>
