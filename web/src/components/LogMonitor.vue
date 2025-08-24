<template>
  <el-card class="logs-card" :class="{ 'simple-mode': simpleMode }">
    <div slot="header" class="card-header" v-if="!simpleMode">
      <span>📝 实时日志</span>
      <div>
        <el-button type="text" @click="refreshLogs" :loading="logsLoading" size="small">刷新</el-button>
        <el-button type="text" @click="toggleLogStream" size="small">
          {{ isLogStreaming ? '停止' : '开始' }}实时监控
        </el-button>
        <el-button type="text" @click="clearLogs" size="small">清空</el-button>
      </div>
    </div>
    <div class="logs-content">
      <div class="logs-container" ref="logsContainer">
        <div v-if="logs.length === 0" class="no-logs">
          <i class="el-icon-document"></i>
          <p>暂无日志数据</p>
        </div>
        <div v-else class="log-lines">
          <div v-for="(log, index) in logs" :key="index" class="log-line" :class="getLogLevel(log)">
            <span class="log-time">{{ getLogTime(log) }}</span>
            <span class="log-content">{{ getLogContent(log) }}</span>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script>
export default {
  name: 'LogMonitor',
  props: {
    //简易模式
    simpleMode: {
      type: Boolean,
      default: false
    },
    maxLines: {
      type: Number,
      default: 100
    },
    isRunning: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      // 加载状态
      logsLoading: false,
      // 日志相关
      logs: [],
      logsInfo: null,
      isLogStreaming: false,
      logEventSource: null
    }
  },
  watch: {
    isRunning(newVal) {
      if (newVal) {
        this.startLogStream()
      } else {
        this.stopLogStream()
      }
    }
  },
  mounted() {
    // 默认加载当前日志
    this.refreshLogs()
  },
  beforeDestroy() {
    this.stopLogStream()
  },
  methods: {
    // 日志相关方法
    async refreshLogs() {
      this.logsLoading = true
      try {
        const params = {
          lines: this.maxLines,
          type: 'current'
        }

        const response = await this.$api.spider.getLogs(params)
        if (response.code === 200) {
          this.logs = response.data.logs || []
          this.logsInfo = response.data
          this.scrollToBottom()
        } else {
          this.$notify.error(response.message || '获取日志失败')
        }
      } catch (error) {
        this.$notify.error('获取日志失败: ' + error.message)
      } finally {
        this.logsLoading = false
      }
    },

    toggleLogStream() {
      if (this.isLogStreaming) {
        this.stopLogStream()
      } else {
        this.startLogStream()
      }
    },

    startLogStream() {
      if (this.isLogStreaming) return

      try {
        this.logEventSource = this.$api.spider.streamLogs()
        this.isLogStreaming = true

        this.logEventSource.onmessage = (event) => {
          if (event.data) {
            try {
              // 尝试解析JSON数据
              const data = JSON.parse(event.data)
              if (data.log) {
                this.logs.push(data.log)
              } else if (typeof data === 'string') {
                this.logs.push(data)
              }
            } catch (e) {
              // 如果不是JSON，直接作为字符串处理
              this.logs.push(event.data)
            }

            // 保持最多100行日志
            if (this.logs.length > this.maxLines) {
              this.logs = this.logs.slice(-this.maxLines)
            }
            this.scrollToBottom()
          }
        }

        this.logEventSource.onerror = (error) => {
          console.error('日志流错误:', error)
          // 错误时不停止流，而是尝试重新连接
          setTimeout(() => {
            if (this.isLogStreaming) {
              this.stopLogStream()
              this.startLogStream()
            }
          }, 5000)
        }

        this.logEventSource.onopen = () => {
          console.log('日志流连接已建立')
        }

        // 只在手动启动时显示成功消息，避免页面加载时显示
        if (this.logs.length === 0) {
          this.logs.push('实时日志监控已启动，等待日志数据...')
        }
      } catch (error) {
        console.error('启动实时日志监控失败:', error)
        // 静默处理错误，避免显示错误消息
      }
    },

    stopLogStream() {
      if (this.logEventSource) {
        try {
          this.logEventSource.close()
        } catch (e) {
          console.log('关闭日志流连接:', e)
        }
        this.logEventSource = null
      }
      this.isLogStreaming = false
    },

    clearLogs() {
      this.logs = []
      this.logsInfo = null
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.logsContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },

    getLogLevel(log) {
      if (log.includes('ERROR') || log.includes('错误')) return 'log-error'
      if (log.includes('WARNING') || log.includes('警告')) return 'log-warning'
      if (log.includes('INFO') || log.includes('信息')) return 'log-info'
      return 'log-default'
    },

    getLogTime(log) {
      // 提取日志时间戳
      const timeMatch = log.match(/(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/)
      return timeMatch ? timeMatch[1] : ''
    },

    getLogContent(log) {
      // 移除时间戳，返回日志内容
      return log.replace(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[,\d]*\s*/, '')
    }
  }
}
</script>

<style scoped>
/* 卡片样式 */
.logs-card {
  margin-bottom: 20px;
  &.simple-mode {
    margin-bottom: 0;
  }
}
.logs-card.simple-mode :deep(.el-card__body)  {
    padding: 0 !important;
}

.logs-card.simple-mode .logs-content,.logs-card.simple-mode .logs-content .logs-container  {
    height: 200px;
    padding: 0 !important;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

/* 日志相关样式 */
.logs-content {
  padding: 10px 0;
}

.logs-container {
  height: 400px;
  overflow-y: auto;
  background-color: #1e1e1e;
  border-radius: 6px;
  padding: 15px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.4;
}

.no-logs {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
}

.no-logs i {
  font-size: 48px;
  margin-bottom: 10px;
}

.log-lines {
  display: flex;
  flex-direction: column;
}

.log-line {
  padding: 2px 0;
  display: flex;
  align-items: flex-start;
  word-break: break-all;
}

.log-time {
  font-size: 12px;
  color: #888;
  min-width: 130px;
  flex-shrink: 0;
}

.log-content {
  color: #e2e8f0;
  flex: 1;
  font-size: 12px;
}

.log-error {
  background-color: rgba(245, 108, 108, 0.1);
  border-left: 3px solid #f56c6c;
  padding-left: 10px;
}

.log-error .log-content {
  color: #f56c6c;
}

.log-warning {
  background-color: rgba(230, 162, 60, 0.1);
  border-left: 3px solid #e6a23c;
  padding-left: 10px;
}

.log-warning .log-content {
  color: #e6a23c;
}

.log-info {
  background-color: rgba(64, 158, 255, 0.1);
  border-left: 3px solid #409eff;
  padding-left: 10px;
}

.log-info .log-content {
  color: #409eff;
}

.log-default .log-content {
  color: #e2e8f0;
}
</style> 