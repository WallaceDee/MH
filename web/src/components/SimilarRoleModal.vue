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
      <!-- 加载状态 -->
      <div v-if="valuationLoading" class="loading-info">
        <el-skeleton :rows="12" animated />
      </div>
      <div v-else-if="similarData">
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
                    <el-tag type="danger" size="mini"> {{ getServerHeatLabel(role.serverid) || '其他' }}/{{
                      role.server_name
                      }}</el-tag>
                    /
                    <el-tag type="primary" size="mini">{{ role.level }}</el-tag>
                    /
                    <el-tag type="info" size="mini">{{ role.roleInfo.basic_info.school }}</el-tag>
                  </div>
                </div>
              </el-row>
              <!-- 刷新按钮 -->
              <div style="width: 100px;flex-shrink: 0;display: flex;justify-content: flex-end;">
                <el-button type="primary" @click="refresh" size="mini" :loading="loading">刷新</el-button>
              </div>
            </el-row>

            <div class="valuation-main">
              <span class="valuation-label">角色估价:</span>
              <span class="valuation-price">{{ similarData.valuation?.estimated_price_yuan || '-' }}元</span>
              <span class="valuation-strategy">({{ getStrategyName(similarData.valuation?.strategy) }})</span>
            </div>

            <div class="valuation-details">
              <span class="confidence-display" :class="confidenceTextClass">
                <i :class="confidenceIcon"></i>
                置信度: {{ similarData.valuation ? (similarData.valuation.confidence * 100).toFixed(1) + '%' : '-' }}
                <span class="confidence-level">{{ confidenceLevel }}</span>
              </span>
              <span>锚点数: {{ similarData.anchor_count || '-' }}</span>
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
        <el-empty v-if="!anchorsLoading && !similarData.anchors?.length" description="暂无相似角色数据"></el-empty>
        <similar-role-table v-else :anchors="similarData.anchors" v-loading="anchorsLoading" element-loading-text="正在加载相似角色数据" />
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
    placement: {
      type: String,
      default: 'left-end'
    },
    // 新增：从父组件传入的搜索参数
    searchParams: {
      type: Object,
      default: () => ({
        selectedDate: '2025-01',
        roleType: 'empty'
      })
    }
  },
  data() {
    return {
      visible: false,
      valuationLoading: false,  // 角色估价接口加载状态
      anchorsLoading: false,    // 相似角色锚点接口加载状态
      error: false,
      similarData: null,
      hotServersConfig: window.hotServersConfig || []
    }
  },
  computed: {
    // 整体加载状态
    loading() {
      return this.valuationLoading || this.anchorsLoading
    },
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
        if (newVal) {
          this.loadHotServers()
        }
      },
      immediate: true
    }
  },
  methods: {
    getServerHeatLabel(serverid) {
      const serverHeat = this.hotServersConfig.find(item => item.children.find(child => child.server_id === serverid))
      return serverHeat?.server_name || ''
    },
    async loadHotServers() {
      if (!window.hotServersConfig) {
        window.hotServersConfig = await this.$api.system.getHotServers()
      }
      this.hotServersConfig = window.hotServersConfig
    },
    async handleShow() {
      // 触发父组件事件（保持向后兼容）
      this.$emit('show', this.role)
      // 加载相似角色数据
      await this.loadSimilarRoles()
    },
    async refresh() {
      await this.loadSimilarRoles()
    },
    // 拆分的相似角色数据加载方法
    async loadSimilarRoles() {
      this.error = false
      this.similarData = null

      try {
        await this.loadRoleValuation()
      } catch (error) {
        console.error('加载相似角色失败:', error)
        this.error = true
      }
    },

    // 统一的角色估价加载方法
    async loadRoleValuation() {
      try {
        // 第一个接口：获取角色估价信息
        this.valuationLoading = true
        const response = await this.$api.role.getRoleValuation({
          eid: this.role.eid,
          role_type: this.searchParams.roleType,
          strategy: 'fair_value',
          similarity_threshold: 0.7,
          max_anchors: 30
        })

        if (response.code !== 200) {
          // 估价失败
          this.$notify.error({
            title: '角色估价失败',
            message: response.message || '估价计算失败',
            duration: 3000
          })

          // 显示详细错误信息
          if (response.data && response.data.error) {
            console.error('估价错误详情:', response.data.error)
          }
          throw new Error(response.message || '估价计算失败')
        }

        const result = response.data
        const estimatedPrice = result.estimated_price_yuan

        // 更新角色数据中的估价信息（如果父组件需要的话）
        this.$emit('update-role-price', {
          eid: this.role.eid,
          basePrice: result.estimated_price
        })

        // 初始化相似角色数据
        this.similarData = {
          anchor_count: result.anchor_count,
          similarity_threshold: result.similarity_threshold || 0.7,
          max_anchors: result.max_anchors || 30,
          anchors: [],
          statistics: {
            price_range: {
              min: Math.min(...result.anchors.map((a) => a.price || 0)),
              max: Math.max(...result.anchors.map((a) => a.price || 0)),
              avg: result.anchors.reduce((sum, a) => sum + (a.price || 0), 0) / result.anchors.length
            },
            similarity_range: {
              min: Math.min(...result.anchors.map((a) => a.similarity || 0)),
              max: Math.max(...result.anchors.map((a) => a.similarity || 0)),
              avg: result.anchors.reduce((sum, a) => sum + (a.similarity || 0), 0) / result.anchors.length
            }
          },
          valuation: {
            estimated_price_yuan: estimatedPrice,
            confidence: result.confidence,
            strategy: result.strategy || 'fair_value'
          }
        }

        this.valuationLoading = false

        // 处理估价响应，如果有锚点数据则加载详细信息
        if (result?.anchor_count > 0 && result?.anchors?.length > 0) {
          // 第二个接口：获取相似角色锚点详细数据
          this.anchorsLoading = true

          try {
            // 使用估价结果中的anchor_eids直接获取角色详细信息，避免重复计算
            const anchorsResponse = await this.$api.role.getRoleApi({
              page_size: 99,
              eid_list: result.anchors.map(item => item.eid),
              role_type: 'empty'
            })

            this.anchorsLoading = false
            //合并相似度和数据
            if (anchorsResponse.code === 200 && anchorsResponse.data?.data) {
              const anchorsData = anchorsResponse.data.data
              const parsedAnchors = anchorsData.map((item, index) => {
                const roleInfo = new window.RoleInfoParser(item.large_equip_desc, { equip_level: item.equip_level })
                item.RoleInfoParser = roleInfo
                if (roleInfo.result) {
                  item.roleInfo = roleInfo.result
                }
                item.similarity = result.anchors[index].similarity
                item.features = result.anchors[index].features
                return item
              })

              // 更新相似角色数据
              this.$set(this.similarData, 'anchors', parsedAnchors)
            } else {
              console.warn('未获取到相似角色锚点数据:', anchorsResponse.message)
            }
          } catch (error) {
            console.error('查询相似角色锚点失败:', error)
            // 锚点查询失败不影响估价结果显示
          }
        }

      } catch (error) {
        console.error('角色估价失败:', error)
        this.$notify.error({
          title: '估价请求失败',
          message: '网络请求异常，请稍后重试',
          duration: 3000
        })
        throw error
      } finally {
        // 确保在出现异常时也重置加载状态
        this.valuationLoading = false
        this.anchorsLoading = false
      }
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
