<template>
  <div class="devtools-panel">
    <div class="panel-header">
      <h3>梦幻灵瞳</h3>
      <div class="connection-status">
        <el-tag :type="devtoolsConnected ? 'success' : 'warning'" size="mini">
          {{ connectionStatus }}
        </el-tag>
        <el-button @click="prevPage" size="mini">上一页</el-button>
        <el-button @click="nextPage" size="mini">下一页</el-button>
        <el-button @click="getPageInfo" size="mini" type="info">页码信息</el-button>
        <el-button @click="reconnectDevTools" size="mini" type="warning" v-if="!devtoolsConnected">重连</el-button>
        <el-button @click="clearData" size="mini" type="danger">清空数据</el-button>
      </div>
    </div>
    <div class="data-section">
      <el-empty v-if="recommendData.length === 0" class="empty-state" description="暂无数据，请访问梦幻西游藏宝阁页面"></el-empty>
      <div v-else class="request-list">
        <div v-for="item in recommendData" :key="item.requestId" class="request-item"
          :class="{ 'completed': item.status === 'completed' }">
          <div class="request-info">
            <div class="request-meta">
              <span class="status" :class="item.status">{{ item.status }}</span>
              <span class="timestamp">{{ formatTime(item.timestamp) }}</span>
            </div>
          </div>
          <div v-if="item.responseData" class="response-data">
            <el-row class="roles" type="flex">
              <span v-for="role in parseListData(item.responseData)?.equip_list" :key="role.eid">
                <RoleImage :key="role.eid" :other_info="role.other_info" :roleInfo="parserRoleData(role)" />
              </span>
            </el-row>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import RoleImage from '@/components/RoleInfo/RoleImage.vue'
export default {
  name: 'DevToolsPanel',
  data() {
    return {
      recommendData: [],
      expandedItems: [],
      processedRequests: new Set(), // 记录已处理的请求ID
      devtoolsConnected: false, // DevTools Protocol连接状态
      connectionStatus: '检查中...', // 连接状态描述
      connectionCheckTimer: null // 连接检查定时器
    }
  },
  components: {
    RoleImage
  },
  computed: {

  },
  mounted() {
    this.initMessageListener()
    this.checkConnectionStatus()

    // // 设置定时检查（每5秒检查一次）
    // this.connectionCheckTimer = setInterval(() => {
    //   this.checkConnectionStatus()
    // }, 5000)
  },
  beforeDestroy() {
    // 移除Chrome消息监听器
    this.removeMessageListener()
    // 清理定时器
    if (this.connectionCheckTimer) {
      clearInterval(this.connectionCheckTimer)
      this.connectionCheckTimer = null
    }
    // 清理组件状态
    this.recommendData = []
    this.expandedItems = []
  },
  methods: {
    nextPage(){
      // 通过Chrome调试API查找并点击页面上的分页器
      this.clickPageButton('next')
    },
    
    prevPage(){
      // 通过Chrome调试API查找并点击页面上的分页器
      this.clickPageButton('prev')
    },
    
    getPageInfo(){
      // 获取当前分页器信息
      this.getPagerInfo()
    },
    
    reconnectDevTools(){
      // 重新连接DevTools
      this.connectionStatus = '重连中...'
      this.checkConnectionStatus()
      this.$message.info('正在尝试重新连接DevTools...')
    },
    
    async clickPageButton(direction) {
      try {
        // 获取当前活动标签页
        const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true })
        
        if (!activeTab || !activeTab.url.includes('cbg.163.com')) {
          this.$message.warning('请先访问梦幻西游藏宝阁页面')
          return
        }

        // 检查Chrome调试API连接状态
        if (!this.devtoolsConnected) {
          this.$message.warning('DevTools连接已断开，请重新加载页面')
          return
        }

        // 通过Chrome调试API执行页面JavaScript代码
        const result = await chrome.debugger.sendCommand(
          { tabId: activeTab.id },
          'Runtime.evaluate',
          {
            expression: `
              (function() {
                try {
                  // 查找id为pager的div
                  const pagerDiv = document.getElementById('pager')
                  if (!pagerDiv) {
                    return 'ERROR:未找到分页器元素'
                  }
                  
                  let targetButton = null
                  const isNext = '${direction}' === 'next'
                  
                  if (isNext) {
                    // 查找下一页按钮 - 根据实际HTML格式优化
                    // 1. 优先查找包含"下一页"文本的链接
                    const allLinks = pagerDiv.querySelectorAll('a')
                    for (let link of allLinks) {
                      const text = link.textContent.trim()
                      if (text === '下一页') {
                        targetButton = link
                        break
                      }
                    }
                    
                    // 2. 如果没找到"下一页"，查找包含goto函数的链接（排除当前页）
                    if (!targetButton) {
                      for (let link of allLinks) {
                        const href = link.getAttribute('href')
                        const text = link.textContent.trim()
                        // 查找包含goto且不是当前页的链接
                        if (href && href.includes('goto(') && !link.classList.contains('on')) {
                          // 获取当前页码
                          const currentPageLink = pagerDiv.querySelector('a.on')
                          if (currentPageLink) {
                            const currentPageText = currentPageLink.textContent.trim()
                            const currentPage = parseInt(currentPageText)
                            const linkPage = parseInt(text)
                            // 如果链接页码大于当前页码，说明是下一页
                            if (!isNaN(linkPage) && linkPage > currentPage) {
                              targetButton = link
                              break
                            }
                          }
                        }
                      }
                    }
                  } else {
                    // 查找上一页按钮
                    const allLinks = pagerDiv.querySelectorAll('a')
                    
                    // 1. 优先查找包含"上一页"文本的链接
                    for (let link of allLinks) {
                      const text = link.textContent.trim()
                      if (text === '上一页') {
                        targetButton = link
                        break
                      }
                    }
                    
                    // 2. 如果没找到"上一页"，查找包含goto函数的链接（排除当前页）
                    if (!targetButton) {
                      for (let link of allLinks) {
                        const href = link.getAttribute('href')
                        const text = link.textContent.trim()
                        // 查找包含goto且不是当前页的链接
                        if (href && href.includes('goto(') && !link.classList.contains('on')) {
                          // 获取当前页码
                          const currentPageLink = pagerDiv.querySelector('a.on')
                          if (currentPageLink) {
                            const currentPageText = currentPageLink.textContent.trim()
                            const currentPage = parseInt(currentPageText)
                            const linkPage = parseInt(text)
                            // 如果链接页码小于当前页码，说明是上一页
                            if (!isNaN(linkPage) && linkPage < currentPage) {
                              targetButton = link
                              break
                            }
                          }
                        }
                      }
                    }
                  }
                  
                  if (!targetButton) {
                    return 'ERROR:未找到${direction === 'next' ? '下一页' : '上一页'}按钮'
                  }
                  
                  // 检查按钮是否可点击
                  if (targetButton.disabled || targetButton.classList.contains('disabled')) {
                    return 'ERROR:${direction === 'next' ? '下一页' : '上一页'}按钮不可点击，可能已到${direction === 'next' ? '最后一页' : '第一页'}'
                  }
                  
                  // 获取当前页码信息用于日志
                  const currentPageLink = pagerDiv.querySelector('a.on')
                  let currentPageInfo = ''
                  if (currentPageLink) {
                    const currentPageText = currentPageLink.textContent.trim()
                    currentPageInfo = ' (当前第' + currentPageText + '页)'
                  }
                  
                  // 点击按钮
                  targetButton.click()
                  return 'SUCCESS:已点击${direction === 'next' ? '下一页' : '上一页'}按钮' + currentPageInfo
                } catch (error) {
                  return 'ERROR:执行失败 - ' + error.message
                }
              })()
            `
          }
        )

        // 处理Chrome调试API的返回结果
          if (result && result.result && result.result.value) {
            const message = result.result.value
            
            if (message.startsWith('SUCCESS:')) {
              this.$message.success(message.substring(8)) // 移除"SUCCESS:"前缀
              console.log(`${direction === 'next' ? '下一页' : '上一页'}按钮点击成功`)
            } else if (message.startsWith('ERROR:')) {
              this.$message.warning(message.substring(6)) // 移除"ERROR:"前缀
              console.warn(`${direction === 'next' ? '下一页' : '上一页'}按钮点击失败:`, message)
            } else {
              this.$message.error('执行页面操作失败：未知返回结果')
              console.error('页面操作结果异常:', result)
            }
          } else {
            this.$message.error('执行页面操作失败')
            console.error('页面操作结果异常:', result)
          }
          
        } catch (error) {
          console.error(`点击${direction === 'next' ? '下一页' : '上一页'}按钮失败:`, error)
          
          // 检查是否是连接断开错误
          if (error.message && error.message.includes('Could not establish connection')) {
            this.devtoolsConnected = false
            this.connectionStatus = '连接断开'
            this.$message.error('DevTools连接已断开，请重新加载页面或刷新扩展')
          } else {
            this.$message.error('操作失败: ' + error.message)
          }
        }
    },
    
    async getPagerInfo() {
      try {
        // 获取当前活动标签页
        const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true })
        
        if (!activeTab || !activeTab.url.includes('cbg.163.com')) {
          this.$message.warning('请先访问梦幻西游藏宝阁页面')
          return
        }

        // 检查Chrome调试API连接状态
        if (!this.devtoolsConnected) {
          this.$message.warning('DevTools连接已断开，请重新加载页面')
          return
        }

        // 通过Chrome调试API执行页面JavaScript代码获取分页器信息
        const result = await chrome.debugger.sendCommand(
          { tabId: activeTab.id },
          'Runtime.evaluate',
          {
            expression: `
              (function() {
                try {
                  // 查找id为pager的div
                  const pagerDiv = document.getElementById('pager')
                  if (!pagerDiv) {
                    return 'ERROR:未找到分页器元素'
                  }
                  
                  // 获取当前页码
                  const currentPageLink = pagerDiv.querySelector('a.on')
                  let currentPage = '未知'
                  if (currentPageLink) {
                    currentPage = currentPageLink.textContent.trim()
                  }
                  
                  // 获取所有页码链接
                  const allPageLinks = pagerDiv.querySelectorAll('a[href*="goto("]')
                  const pageNumbers = []
                  allPageLinks.forEach(link => {
                    const text = link.textContent.trim()
                    if (text.match(/^\d+$/)) {
                      pageNumbers.push(parseInt(text))
                    }
                  })
                  
                  // 计算总页数（取最大页码）
                  const totalPages = pageNumbers.length > 0 ? Math.max(...pageNumbers) : '未知'
                  
                  // 检查是否有上一页/下一页按钮
                  const hasPrev = pagerDiv.querySelector('a[href*="goto("]') && 
                                 pagerDiv.textContent.includes('上一页')
                  const hasNext = pagerDiv.querySelector('a[href*="goto("]') && 
                                 pagerDiv.textContent.includes('下一页')
                  
                  return 'SUCCESS:第' + currentPage + '页，共' + totalPages + '页 (上一页:' + (hasPrev ? '有' : '无') + ', 下一页:' + (hasNext ? '有' : '无') + ')'
                } catch (error) {
                  return 'ERROR:获取分页器信息失败 - ' + error.message
                }
              })()
            `
          }
        )

        // 处理返回结果
        if (result && result.result && result.result.value) {
          const message = result.result.value
          
          if (message.startsWith('SUCCESS:')) {
            this.$message.info(message.substring(8)) // 移除"SUCCESS:"前缀
            console.log('分页器信息获取成功:', message)
          } else if (message.startsWith('ERROR:')) {
            this.$message.warning(message.substring(6)) // 移除"ERROR:"前缀
            console.warn('分页器信息获取失败:', message)
          } else {
            this.$message.error('获取分页器信息失败：未知返回结果')
            console.error('分页器信息获取结果异常:', result)
          }
        } else {
          this.$message.error('获取分页器信息失败')
          console.error('分页器信息获取结果异常:', result)
        }
        
      } catch (error) {
        console.error('获取分页器信息失败:', error)
        
        // 检查是否是连接断开错误
        if (error.message && error.message.includes('Could not establish connection')) {
          this.devtoolsConnected = false
          this.connectionStatus = '连接断开'
          this.$message.error('DevTools连接已断开，请重新加载页面或刷新扩展')
        } else {
          this.$message.error('操作失败: ' + error.message)
        }
      }
    },
    parserRoleData(data) {
      const roleInfo = new window.RoleInfoParser(data.large_equip_desc, { equip_level: data.equip_level })
      return roleInfo.result
      // return {
      //   RoleInfoParser: roleInfo,
      //   roleInfo: roleInfo.result,
      //   accept_bargain: data.accept_bargain,
      //   collect_num: data.collect_num,
      //   dynamic_tags: data.dynamic_tags,
      //   eid: data.eid,
      //   highlight: data.highlight,
      //   is_split_independent_role: data.is_split_independent_role,
      //   is_split_main_role: data.is_split_main_role,
      //   large_equip_desc: data.large_equip_desc,
      //   level: data.level,
      //   other_info: data.other_info,
      //   school: data.school,
      //   seller_nickname: data.seller_nickname,
      //   server_name: data.server_name,
      //   serverid: data.serverid,
      //   price: data.price,
      //   sum_exp: data.sum_exp,
      //   create_time: data.create_time,
      //   update_time: data.create_time,
      //   all_equip_json: '',
      //   all_summon_json: '',
      //   split_price_desc: '',
      //   pet_price: '',
      //   equip_price: '',
      //   base_price: '',
      //   history_price: '',
      // }
    },
    parseListData(responseDataStr) {
      // 解析响应数据 Request.JSONP.request_map.request_数字(xxxx) 中的xxxx
      const match = responseDataStr.match(/Request\.JSONP\.request_map\.request_\d+\((.*)\)/)
      let templateJSONStr = '{}'
      if (match) {
        templateJSONStr = match[1]
      }
      try {
        const templateJSON = JSON.parse(templateJSONStr)
        return templateJSON
      } catch (error) {
        console.error('解析响应数据失败:', error)
        return {}
      }
    },
    initMessageListener() {
      console.log('DevToolsPanel mounted, initializing listener')

      // 使用单例模式确保只有一个监听器
      if (typeof chrome !== 'undefined' && chrome.runtime) {
        // 如果已经有全局监听器，先移除
        if (window.cbgDevToolsListener) {
          chrome.runtime.onMessage.removeListener(window.cbgDevToolsListener)
        }

        // 创建全局监听器
        window.cbgDevToolsListener = (request, sender, sendResponse) => {
          console.log('DevToolsPanel received Chrome message:', request.action)
          this.handleChromeMessage(request, sender, sendResponse)
          sendResponse({ success: true })
        }

        // 注册监听器
        chrome.runtime.onMessage.addListener(window.cbgDevToolsListener)
        console.log('Chrome message listener registered for DevToolsPanel')
      }
    },

    removeMessageListener() {
      // 移除Chrome消息监听器
      if (typeof chrome !== 'undefined' && chrome.runtime && window.cbgDevToolsListener) {
        chrome.runtime.onMessage.removeListener(window.cbgDevToolsListener)
        delete window.cbgDevToolsListener
        console.log('Chrome message listener removed for DevToolsPanel')
      }
    },

    checkConnectionStatus() {
      // 检查Chrome扩展连接状态
      if (typeof chrome !== 'undefined' && chrome.runtime) {
        // 尝试发送ping消息检查连接
        chrome.runtime.sendMessage({ action: 'ping' }, (response) => {
          if (chrome.runtime.lastError) {
            console.log('Chrome extension connection check failed:', chrome.runtime.lastError)
            this.devtoolsConnected = false
            this.connectionStatus = '未连接'
          } else if (response && response.success) {
            console.log('Chrome extension connection check successful:', response)
            this.devtoolsConnected = true
            this.connectionStatus = '已连接'
          } else {
            console.log('Chrome extension connection check failed: invalid response')
            this.devtoolsConnected = false
            this.connectionStatus = '连接异常'
          }
        })
      } else {
        console.log('Chrome runtime not available')
        this.devtoolsConnected = false
        this.connectionStatus = 'Chrome环境不可用'
      }
    },

    handleChromeMessage(request, sender, sendResponse) {
      switch (request.action) {
        case 'updateRecommendData':
          this.recommendData = request.data || []

          // 只处理新完成的请求，避免重复处理
          if (this.recommendData && this.recommendData.length > 0) {
            this.recommendData.forEach(item => {
              if (item.status === 'completed' &&
                item.responseData &&
                item.url &&
                item.requestId &&
                !this.processedRequests.has(item.requestId)) {

                // 标记为已处理
                this.processedRequests.add(item.requestId)
                console.log(`开始处理新请求: ${item.requestId}`)

                // 调用解析响应数据接口
                this.$api.spider.parseResponse({
                  url: item.url,
                  response_text: item.responseData
                }).then(res => {
                  console.log(`请求 ${item.requestId} 解析结果:`, res)
                  if (res.code === 200) {
                    console.log(`请求 ${item.requestId} 数据解析成功:`, res.data)
                  } else {
                    console.error(`请求 ${item.requestId} 数据解析失败:`, res.message)
                  }
                }).catch(error => {
                  console.error(`请求 ${item.requestId} 解析请求失败:`, error)
                  // 解析失败时移除标记，允许重试
                  this.processedRequests.delete(item.requestId)
                })
              }
            })
          }
          break

        case 'devtoolsConnected':
          this.devtoolsConnected = true
          this.connectionStatus = '已连接'
          this.$message.success(request.message)
          break

        case 'showDebuggerWarning':
          this.devtoolsConnected = false
          this.connectionStatus = '连接冲突'
          this.$message.warning(request.message)
          break

        case 'clearRecommendData':
          this.recommendData = []
          this.expandedItems = []
          this.processedRequests.clear()
          console.log('清空推荐数据和处理记录')
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
  box-sizing: border-box;
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  background: #f5f5f5;
  min-height: 100vh;
  background: url(../../public/assets/images/areabg.webp) repeat-y;
  width: 960px;
  margin: 0 auto;
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

.connection-status {
  display: flex;
  align-items: center;
  gap: 10px;
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
