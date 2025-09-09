<template>
  <div class="devtools-panel">
    <div class="panel-header">
      <h3>CBG爬虫助手</h3>
      <el-button @click="clearData" size="mini" type="danger">清空数据</el-button>
    </div>

    <div class="data-section">
      <h4>检测到的请求 ({{ recommendData.length }})</h4>
      <div v-if="recommendData.length === 0" class="empty-state">
        暂无数据，请访问CBG页面并触发推荐请求
      </div>
      <div v-else class="request-list">
        <div v-for="(item, index) in recommendData" :key="item.requestId" class="request-item"
          :class="{ 'completed': item.status === 'completed' }">
          <div class="request-info">
            <div class="request-url">{{ item.url }}</div>
            <div class="request-meta">
              <span class="method">{{ item.method }}</span>
              <span class="status" :class="item.status">{{ item.status }}</span>
              <span class="timestamp">{{ formatTime(item.timestamp) }}</span>
            </div>
          </div>
          <div v-if="item.responseData" class="response-data">
            <el-button @click="toggleResponse(index)" size="mini" type="text">
              {{ expandedItems.includes(index) ? '收起' : '展开' }}响应数据
            </el-button>
            <div v-if="expandedItems.includes(index)" class="response-content">
              <pre>{{ JSON.stringify(item.responseData, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DevToolsPanel',
  data() {
    return {
      recommendData: [],
      expandedItems: []
    }
  },
  computed: {

  },
  mounted() {
    this.initMessageListener()
  },
  beforeDestroy() {
    // 移除Chrome消息监听器
    if (typeof chrome !== 'undefined' && chrome.runtime && this.chromeMessageListener) {
      chrome.runtime.onMessage.removeListener(this.chromeMessageListener)
      console.log('Chrome message listener removed for DevToolsPanel')
    }
    // 清理组件状态
    this.recommendData = []
    this.expandedItems = []
  },
  methods: {
    initMessageListener() {
      console.log('DevToolsPanel mounted, initializing listener')
      
      // 直接监听Chrome消息
      if (typeof chrome !== 'undefined' && chrome.runtime) {
        // 清理所有现有的监听器（确保只有一个在运行）
        this.cleanupAllListeners()
        
        // 创建新的监听器
        this.chromeMessageListener = (request, sender, sendResponse) => {
          console.log('DevToolsPanel received Chrome message:', request.action)
          this.handleChromeMessage(request, sender, sendResponse)
          sendResponse({ success: true })
        }
        
        // 注册监听器
        chrome.runtime.onMessage.addListener(this.chromeMessageListener)
        console.log('Chrome message listener registered for DevToolsPanel')
      }
    },

    cleanupAllListeners() {
      // 移除所有可能存在的Chrome消息监听器
      if (typeof chrome !== 'undefined' && chrome.runtime) {
        // 尝试移除当前组件的监听器
        if (this.chromeMessageListener) {
          chrome.runtime.onMessage.removeListener(this.chromeMessageListener)
        }
        
        // 清理全局监听器（如果存在）
        if (window.cbgMessageListener) {
          chrome.runtime.onMessage.removeListener(window.cbgMessageListener)
          delete window.cbgMessageListener
        }
        
        console.log('All Chrome message listeners cleaned up')
      }
    },

    handleChromeMessage(request, sender, sendResponse) {
      switch (request.action) {
        case 'updateRecommendData':
          this.recommendData = request.data || []
          
          // 处理每个完成的请求数据
          if (this.recommendData && this.recommendData.length > 0) {
            this.recommendData.forEach(item => {
              if (item.status === 'completed' && item.responseData && item.url) {
                // 调用解析响应数据接口
                this.$api.spider.parseResponse({
                  url: item.url,
                  response_text: item.responseData
                }).then(res => {
                  console.log('解析结果:', res)
                  if (res.code === 200) {
                    console.log('数据解析成功:', res.data)
                  } else {
                    console.error('数据解析失败:', res.message)
                  }
                }).catch(error => {
                  console.error('解析请求失败:', error)
                })
              }
            })
          }
          break

        case 'showDebuggerWarning':
          this.$message.warning(request.message)
          break

        case 'clearRecommendData':
          this.recommendData = []
          this.expandedItems = []
          console.log('清空推荐数据')
          break
      }
    },


    clearData() {
      this.recommendData = []
      this.expandedItems = []
      // 通知background script清空数据
      if (typeof chrome !== 'undefined' && chrome.runtime) {
        chrome.runtime.sendMessage({
          action: 'clearRecommendData'
        })
      }
    },

    toggleResponse(index) {
      const expandedIndex = this.expandedItems.indexOf(index)
      if (expandedIndex > -1) {
        this.expandedItems.splice(expandedIndex, 1)
      } else {
        this.expandedItems.push(index)
      }
    },

    formatTime(timestamp) {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      return date.toLocaleTimeString()
    }
  }
}
</script>

<style scoped>
.devtools-panel {
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  background: #f5f5f5;
  min-height: 100vh;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e0e0e0;
}

.panel-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.data-section h4 {
  margin: 0 0 12px 0;
  color: #666;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  background: white;
  border-radius: 4px;
  border: 1px dashed #ddd;
}

.request-list {
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  overflow: hidden;
}

.request-item {
  border-bottom: 1px solid #f0f0f0;
  padding: 12px 16px;
  transition: background-color 0.2s;
}

.request-item:last-child {
  border-bottom: none;
}

.request-item:hover {
  background-color: #fafafa;
}

.request-item.completed {
  background-color: #f0f9ff;
  border-left: 3px solid #1890ff;
}

.request-info {
  margin-bottom: 8px;
}

.request-url {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: #333;
  word-break: break-all;
  margin-bottom: 4px;
}

.request-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
}

.method {
  background: #1890ff;
  color: white;
  padding: 2px 6px;
  border-radius: 2px;
  font-weight: bold;
}

.status {
  padding: 2px 6px;
  border-radius: 2px;
  font-weight: bold;
}

.status.pending {
  background: #faad14;
  color: white;
}

.status.completed {
  background: #52c41a;
  color: white;
}

.timestamp {
  color: #999;
}

.response-data {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.response-content {
  margin-top: 8px;
  background: #f8f8f8;
  border-radius: 4px;
  padding: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.response-content pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 11px;
  line-height: 1.4;
  color: #333;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
