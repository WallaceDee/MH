<template>
  <div class="market-data-status">
    <div class="page-header">
      <h1>市场数据状态监控</h1>
      <p>实时监控空角色市场数据的加载状态和统计信息</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button 
        type="primary" 
        @click="refreshStatus" 
        :loading="loading"
        icon="el-icon-refresh"
      >
        刷新状态
      </el-button>
      
      <el-button 
        type="success" 
        @click="showRefreshDialog = true"
        icon="el-icon-download"
        :disabled="refreshing"
      >
        刷新市场数据
      </el-button>
    </div>

    <!-- 状态卡片 -->
    <el-row :gutter="20" class="status-cards">
      <!-- 基本状态 -->
      <el-col :span="8">
        <el-card class="status-card">
          <div slot="header" class="card-header">
            <i class="el-icon-data-line"></i>
            <span>数据状态</span>
          </div>
          <div class="status-item">
            <span class="label">数据已加载:</span>
            <el-tag :type="status.data_loaded ? 'success' : 'danger'">
              {{ status.data_loaded ? '是' : '否' }}
            </el-tag>
          </div>
          <div class="status-item">
            <span class="label">数据条数:</span>
            <span class="value">{{ status.data_count || 0 | numberFormat }}</span>
          </div>
          <div class="status-item">
            <span class="label">内存占用:</span>
            <span class="value">{{ (status.memory_usage_mb || 0).toFixed(2) }} MB</span>
          </div>
          <div class="status-item">
            <span class="label">特征维度:</span>
            <span class="value">{{ (status.data_columns || []).length }}</span>
          </div>
        </el-card>
      </el-col>

      <!-- 缓存状态 -->
      <el-col :span="8">
        <el-card class="status-card">
          <div slot="header" class="card-header">
            <i class="el-icon-time"></i>
            <span>缓存状态</span>
          </div>
          <div class="status-item">
            <span class="label">缓存状态:</span>
            <el-tag :type="status.cache_expired ? 'danger' : 'success'">
              {{ status.cache_expired ? '已过期' : '有效' }}
            </el-tag>
          </div>
          <div class="status-item">
            <span class="label">最后刷新:</span>
            <span class="value">{{ formatTime(status.last_refresh_time) }}</span>
          </div>
          <div class="status-item">
            <span class="label">过期时间:</span>
            <span class="value">{{ formatTime(status.cache_expiry_time) }}</span>
          </div>
          <div class="status-item">
            <span class="label">缓存时长:</span>
            <span class="value">{{ status.cache_expiry_hours || 2 }} 小时</span>
          </div>
        </el-card>
      </el-col>

      <!-- 数据统计 -->
      <el-col :span="8">
        <el-card class="status-card">
          <div slot="header" class="card-header">
            <i class="el-icon-s-data"></i>
            <span>数据统计</span>
          </div>
          <div v-if="status.price_statistics" class="status-item">
            <span class="label">价格范围:</span>
            <span class="value">
              {{ status.price_statistics.min_price | numberFormat }} - 
              {{ status.price_statistics.max_price | numberFormat }}
            </span>
          </div>
          <div v-if="status.price_statistics" class="status-item">
            <span class="label">平均价格:</span>
            <span class="value">{{ status.price_statistics.avg_price.toFixed(0) | numberFormat }}</span>
          </div>
          <div v-if="status.level_statistics" class="status-item">
            <span class="label">等级范围:</span>
            <span class="value">
              {{ status.level_statistics.min_level }} - {{ status.level_statistics.max_level }}
            </span>
          </div>
          <div v-if="status.role_type_distribution" class="status-item">
            <span class="label">角色类型:</span>
            <div class="role-type-tags">
              <el-tag 
                v-for="(count, type) in status.role_type_distribution" 
                :key="type" 
                size="mini"
              >
                {{ type }}: {{ count }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细信息 -->
    <el-card class="details-card" v-if="status.data_columns && status.data_columns.length > 0">
      <div slot="header" class="card-header">
        <i class="el-icon-menu"></i>
        <span>数据字段 ({{ status.data_columns.length }})</span>
      </div>
      <div class="columns-grid">
        <el-tag 
          v-for="column in status.data_columns" 
          :key="column"
          size="small"
          class="column-tag"
        >
          {{ column }}
        </el-tag>
      </div>
    </el-card>

    <!-- 数据分析图表 -->
    <div v-if="status.data_count > 0" class="charts-section">
      <div class="section-header">
        <h2>数据分析</h2>
        <p>基于当前市场数据的统计分析和可视化展示</p>
      </div>
      <MarketDataCharts :market-data="status" />
    </div>

    <!-- 刷新数据对话框 -->
    <el-dialog
      title="刷新市场数据"
      :visible.sync="showRefreshDialog"
      width="600px"
      @close="resetRefreshForm"
      :close-on-click-modal="false"
      :close-on-press-escape="!refreshing"
    >
      <!-- 刷新进度显示 -->
      <div v-if="refreshing" class="refresh-progress">
        <div class="progress-header">
          <i class="el-icon-loading"></i>
          <span>正在刷新市场数据...</span>
        </div>
        
        <!-- 进度条 -->
        <el-progress 
          :percentage="refreshProgress" 
          :status="refreshProgress === 100 ? 'success' : null"
          :stroke-width="8"
        />
        
        <!-- 进度详情 -->
        <div class="progress-details">
          <div class="progress-item">
            <span class="label">当前状态:</span>
            <span class="value">{{ refreshMessage }}</span>
          </div>
          <div class="progress-item" v-if="refreshedCount > 0">
            <span class="label">已处理:</span>
            <span class="value">{{ refreshedCount }} 条数据</span>
          </div>
          <div class="progress-item" v-if="totalBatches > 0">
            <span class="label">批次进度:</span>
            <span class="value">第 {{ currentBatch }} / {{ totalBatches }} 批</span>
          </div>
          <div class="progress-item" v-if="refreshStartTime">
            <span class="label">已耗时:</span>
            <span class="value">{{ getElapsedTime() }} 秒</span>
          </div>
        </div>
      </div>

      <!-- 刷新表单 -->
      <el-form v-else :model="refreshForm" label-width="120px">
        <el-form-item label="最大记录数">
          <el-input-number 
            v-model="refreshForm.max_records" 
            :min="100" 
            :max="10000" 
            :step="100"
          />
          <div class="form-tip">建议值: 500-2000，过大可能导致超时</div>
        </el-form-item>
        
        <el-form-item label="等级范围">
          <el-col :span="11">
            <el-input-number v-model="refreshForm.level_min" placeholder="最小等级" :min="1" :max="200" />
          </el-col>
          <el-col :span="2" class="text-center">-</el-col>
          <el-col :span="11">
            <el-input-number v-model="refreshForm.level_max" placeholder="最大等级" :min="1" :max="200" />
          </el-col>
        </el-form-item>

        <el-form-item label="批次大小">
          <el-input-number 
            v-model="refreshForm.batch_size" 
            :min="50" 
            :max="1000" 
            :step="50"
          />
          <div class="form-tip">每批处理的数据条数，建议值: 100-500，过大可能影响响应速度</div>
        </el-form-item>

      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="showRefreshDialog = false" :disabled="refreshing">
          {{ refreshing ? '刷新中...' : '取消' }}
        </el-button>
        <el-button 
          v-if="!refreshing"
          type="primary" 
          @click="refreshMarketData"
        >
          开始刷新
        </el-button>
        <el-button 
          v-else
          type="danger" 
          @click="cancelRefresh"
        >
          取消刷新
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { systemApi } from '@/api/system'
import MarketDataCharts from '@/components/MarketDataCharts.vue'

export default {
  name: 'MarketDataStatus',
  components: {
    MarketDataCharts
  },
  data() {
    return {
      loading: false,
      refreshing: false,
      showRefreshDialog: false,
      status: {},
      refreshForm: {
        max_records: 999,
        level_min: 0,
        level_max: 175,
        batch_size: 200
      },
      autoRefreshTimer: null,
      // 进度相关
      refreshProgress: 0,
      refreshMessage: '',
      refreshedCount: 0,
      refreshStartTime: null,
      progressTimer: null,
      currentBatch: 0,
      totalBatches: 0
    }
  },
  
  filters: {
    numberFormat(value) {
      if (!value && value !== 0) return '-'
      return new Intl.NumberFormat('zh-CN').format(value)
    }
  },

  mounted() {
    this.refreshStatus()
    // 检查是否有正在进行的刷新任务
    this.checkOngoingRefresh()
    // 设置自动刷新状态
    this.autoRefreshTimer = setInterval(() => {
      this.refreshStatus()
    }, 60000) // 每60秒刷新一次状态
  },

  beforeDestroy() {
    if (this.autoRefreshTimer) {
      clearInterval(this.autoRefreshTimer)
    }
    if (this.progressTimer) {
      clearInterval(this.progressTimer)
    }
  },

  methods: {
    async refreshStatus() {
      if (this.loading) return
      
      this.loading = true
      try {
        const response = await systemApi.getMarketDataStatus()
        if (response.code === 200) {
          this.status = response.data || {}
          
          // 如果发现正在刷新但前端没有显示进度，恢复进度弹框
          if (response.data.refresh_status === 'running' && !this.refreshing) {
            this.refreshing = true
            this.showRefreshDialog = true
            this.initializeProgress()
            
            // 从后端恢复进度信息
            this.refreshProgress = response.data.refresh_progress || 0
            this.refreshMessage = response.data.refresh_message || '正在处理...'
            this.refreshedCount = response.data.refresh_processed_records || 0
            this.currentBatch = response.data.refresh_current_batch || 0
            this.totalBatches = response.data.refresh_total_batches || 0
            
            // 如果有开始时间，使用它
            if (response.data.refresh_start_time) {
              this.refreshStartTime = new Date(response.data.refresh_start_time).getTime()
            }
            
            // 开始轮询进度
            this.startProgressPolling()
            
            this.$message.info('检测到正在进行的数据刷新任务，已恢复进度显示')
          }
        } else {
          this.$message.error(response.message || '获取状态失败')
        }
      } catch (error) {
        console.error('获取市场数据状态失败:', error)
        this.$message.error('获取状态失败，请检查网络连接')
      } finally {
        this.loading = false
      }
    },

    async refreshMarketData() {
      this.refreshing = true
      this.initializeProgress()
      
      try {
        // 构建筛选条件
        const filters = {}
        if (this.refreshForm.level_min) filters.level_min = this.refreshForm.level_min
        if (this.refreshForm.level_max) filters.level_max = this.refreshForm.level_max

        const params = {
          max_records: this.refreshForm.max_records,
          filters: Object.keys(filters).length > 0 ? filters : null,
          batch_size: this.refreshForm.batch_size
        }

        // 启动后台刷新
        const response = await systemApi.refreshMarketData(params)
        
        if (response.code === 200) {
          this.$message.success('数据刷新已启动，正在后台处理...')
          
          // 开始轮询进度
          this.startProgressPolling()
        } else {
          this.$message.error(response.message || '启动刷新失败')
          this.refreshing = false
        }
      } catch (error) {
        console.error('启动刷新失败:', error)
        this.refreshMessage = '启动失败'
        this.$message.error('启动刷新失败，请检查网络连接')
        this.refreshing = false
      }
    },

    resetRefreshForm() {
      this.refreshForm = {
        max_records: 999,
        level_min: 0,
        level_max: 175,
        batch_size: 200
      }
    },

    formatTime(timeStr) {
      if (!timeStr) return '-'
      try {
        const date = new Date(timeStr)
        return date.toLocaleString('zh-CN')
      } catch (error) {
        return timeStr
      }
    },

    // 进度相关方法
    initializeProgress() {
      this.refreshProgress = 0
      this.refreshMessage = '准备开始...'
      this.refreshedCount = 0
      this.refreshStartTime = Date.now()
      this.currentBatch = 0
      this.totalBatches = 0
    },

    startProgressPolling() {
      // 开始轮询后端进度
      this.progressTimer = setInterval(async () => {
        await this.updateProgressFromBackend()
      }, 3000) // 每3秒查询一次进度
    },

    async updateProgressFromBackend() {
      try {
        const response = await systemApi.getMarketDataStatus()
        if (response.code === 200) {
          const data = response.data
          
          // 更新进度信息
          this.refreshProgress = data.refresh_progress || 0
          this.refreshMessage = data.refresh_message || ''
          this.refreshedCount = data.refresh_processed_records || 0
          this.currentBatch = data.refresh_current_batch || 0
          this.totalBatches = data.refresh_total_batches || 0
          
          // 检查刷新状态
          if (data.refresh_status === 'completed') {
            this.completeProgress()
            this.$message.success(`数据刷新完成！处理了 ${this.refreshedCount} 条数据`)
            
            // 延迟关闭对话框
            setTimeout(() => {
              this.showRefreshDialog = false
              this.resetProgress()
            }, 2000)
            
            // 刷新主状态
            setTimeout(() => {
              this.refreshStatus()
            }, 500)
            
          } else if (data.refresh_status === 'error') {
            this.refreshMessage = data.refresh_message || '刷新失败'
            this.refreshProgress = 0
            this.$message.error('数据刷新失败')
            this.stopProgressTimer()
            this.refreshing = false
          }
          // 如果是 'running' 状态，继续轮询
        }
      } catch (error) {
        console.error('获取进度失败:', error)
      }
    },

    completeProgress() {
      this.refreshProgress = 100
      this.refreshMessage = '刷新完成！'
      this.stopProgressTimer()
      setTimeout(() => {
        this.refreshing = false
      }, 2000)
    },

    stopProgressTimer() {
      if (this.progressTimer) {
        clearInterval(this.progressTimer)
        this.progressTimer = null
      }
    },

    resetProgress() {
      this.refreshProgress = 0
      this.refreshMessage = ''
      this.refreshedCount = 0
      this.refreshStartTime = null
      this.currentBatch = 0
      this.totalBatches = 0
    },

    cancelRefresh() {
      this.stopProgressTimer()
      this.refreshing = false
      this.resetProgress()
      this.showRefreshDialog = false
      this.$message.info('已取消刷新操作')
      // TODO: 可以添加取消后台任务的API调用
    },

    getElapsedTime() {
      if (!this.refreshStartTime) return '0'
      return Math.floor((Date.now() - this.refreshStartTime) / 1000)
    },

    async checkOngoingRefresh() {
      // 检查是否有正在进行的刷新任务
      try {
        const response = await systemApi.getMarketDataStatus()
        if (response.code === 200 && response.data.refresh_status === 'running') {
          // 发现正在进行的刷新任务，恢复进度弹框
          this.refreshing = true
          this.showRefreshDialog = true
          this.initializeProgress()
          
          // 从后端恢复进度信息
          this.refreshProgress = response.data.refresh_progress || 0
          this.refreshMessage = response.data.refresh_message || '正在处理...'
          this.refreshedCount = response.data.refresh_processed_records || 0
          this.currentBatch = response.data.refresh_current_batch || 0
          this.totalBatches = response.data.refresh_total_batches || 0
          
          // 如果有开始时间，使用它
          if (response.data.refresh_start_time) {
            this.refreshStartTime = new Date(response.data.refresh_start_time).getTime()
          }
          
          // 开始轮询进度
          this.startProgressPolling()
          
          this.$message.info('检测到正在进行的数据刷新任务，已恢复进度显示')
        }
      } catch (error) {
        console.error('检查正在进行的刷新任务失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.market-data-status {
  padding: 20px;
}

.market-data-status .page-header {
  margin-bottom: 20px;
}

.market-data-status .page-header h1 {
  margin: 0 0 8px 0;
  color: #303133;
}

.market-data-status .page-header p {
  margin: 0;
  color: #909399;
}

.market-data-status .action-bar {
  margin-bottom: 20px;
}

.market-data-status .action-bar .el-button {
  margin-right: 10px;
}

.market-data-status .status-cards {
  margin-bottom: 20px;
}

.market-data-status .status-card .card-header {
  display: flex;
  align-items: center;
}

.market-data-status .status-card .card-header i {
  margin-right: 8px;
  font-size: 16px;
  color: #409EFF;
}

.market-data-status .status-card .status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.market-data-status .status-card .status-item:last-child {
  margin-bottom: 0;
}

.market-data-status .status-card .status-item .label {
  color: #606266;
  font-size: 14px;
}

.market-data-status .status-card .status-item .value {
  color: #303133;
  font-weight: 500;
}

.market-data-status .status-card .status-item .role-type-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.market-data-status .details-card .card-header {
  display: flex;
  align-items: center;
}

.market-data-status .details-card .card-header i {
  margin-right: 8px;
  font-size: 16px;
  color: #409EFF;
}

.market-data-status .details-card .columns-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.market-data-status .details-card .columns-grid .column-tag {
  margin: 0;
}

.market-data-status .form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.market-data-status .text-center {
  text-align: center;
  line-height: 32px;
}

/* 图表区域样式 */
.charts-section {
  margin-top: 30px;
}

.charts-section .section-header {
  margin-bottom: 20px;
  text-align: center;
}

.charts-section .section-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 20px;
}

.charts-section .section-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

/* 进度显示样式 */
.refresh-progress {
  padding: 20px;
}

.refresh-progress .progress-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  font-size: 16px;
  color: #303133;
}

.refresh-progress .progress-header i {
  margin-right: 8px;
  color: #409EFF;
}

.refresh-progress .progress-details {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.refresh-progress .progress-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.refresh-progress .progress-item:last-child {
  margin-bottom: 0;
}

.refresh-progress .progress-item .label {
  color: #606266;
  font-size: 14px;
}

.refresh-progress .progress-item .value {
  color: #303133;
  font-weight: 500;
}
</style>
