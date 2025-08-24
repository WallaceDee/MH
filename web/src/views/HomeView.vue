<template>
  <div class="home">
    <!-- 爬虫配置区域 -->
    <AutoParams :isRunning.sync="isRunning" :log="false" />
    <!-- 实时日志监控 -->
    <LogMonitor :isRunning="isRunning" />
  </div>
</template>

<script>
import AutoParams from '@/components/AutoParams.vue'
import LogMonitor from '@/components/LogMonitor.vue'

export default {
  name: 'HomeView',
  components: {
    AutoParams,
    LogMonitor
  },
  data() {
    return {
      // 加载状态
      isRunning: false,
      // 缓存清理定时器
      cacheCleanupTimer: null
    }
  },
  mounted() {
    // 等待Vuex状态恢复后再执行其他操作
    this.$nextTick(() => {
      // 自动清理过期缓存
      this.$store.dispatch('cookie/cleanExpiredCache')

      // 启动缓存清理定时器（每分钟检查一次）
      this.cacheCleanupTimer = setInterval(() => {
        this.$store.dispatch('cookie/cleanExpiredCache')
      }, 60 * 1000)
    })
  },
  beforeDestroy() {
    // 清理缓存清理定时器
    if (this.cacheCleanupTimer) {
      clearInterval(this.cacheCleanupTimer)
    }
  }
}
</script>

<style scoped>
/* 卡片样式 */
.spider-config-card,
.spider-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

/* 状态区域样式 */
.status-content {
  padding: 10px 0;
}

.status-item {
  display: flex;
  align-items: center;
}

.status-label {
  font-weight: bold;
  margin-right: 10px;
}

/* 进度条样式 */
.progress-wrapper {
  flex: 1;
  margin-left: 10px;
}

.status-item .el-progress {
  width: 100%;
}

.status-item .el-progress__text {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.status-item .el-progress-bar__outer {
  background-color: #f0f0f0;
  border-radius: 4px;
  height: 8px;
}

.status-item .el-progress-bar__inner {
  border-radius: 4px;
  transition: width 0.3s ease;
  background: linear-gradient(90deg, #409eff 0%, #67c23a 100%);
}

/* 工具按钮区域 */
.tool-buttons {
  padding: 10px 0;
}

/* 参数编辑器样式 */
.params-editor {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 6px;
  margin: 15px 0;
  border-left: 4px solid #409eff;
}

.params-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.json-editor-wrapper {
  position: relative;
  width: 100%;
}

.json-editor {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.4;
}

.json-editor textarea {
  background-color: #2d3748;
  color: #e2e8f0;
  border: 1px solid #4a5568;
  border-radius: 4px;
  padding: 12px;
}

.json-editor textarea:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.json-error {
  margin-top: 8px;
  padding: 8px 12px;
  background-color: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 4px;
  color: #f56c6c;
  font-size: 12px;
  line-height: 1.4;
}

.json-error i {
  margin-right: 4px;
}

/* 表单提示样式 */
.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

/* 图标和颜色样式 */
.emoji-icon {
  font-size: 18px;
  margin-right: 5px;
}

.cBlue {
  color: #409eff;
  font-weight: bold;
}
</style>
