// 全局监听器管理
window.cbgGlobalListeners = window.cbgGlobalListeners || {
  isInitialized: false,
  listeners: []
}

// 创建DevTools标签页
chrome.devtools.panels.create('梦幻灵瞳', 'icons/icon16.png', 'panel.html', function (panel) {
  console.log('CBG爬虫助手DevTools面板已创建')
})

// DevTools Protocol 监听器
class DevToolsListener {
  constructor() {
    this.tabId = null
    this.isListening = false
    this.recommendData = []
    this.init()
  }

  init() {
    this.bindEvents()
  }

  bindEvents() {
    // 避免重复绑定监听器
    if (window.cbgGlobalListeners.isInitialized) {
      console.log('监听器已初始化，跳过重复绑定')
      return
    }

    // 监听标签页更新
    const onUpdatedListener = (tabId, changeInfo, tab) => {
      if (changeInfo.status === 'complete' && tab.url && tab.url.includes('cbg.163.com')) {
        this.tabId = tabId
        this.startListening()
      }
    }

    // 监听标签页激活
    const onActivatedListener = (activeInfo) => {
      chrome.tabs.get(activeInfo.tabId, (tab) => {
        if (tab.url && tab.url.includes('cbg.163.com')) {
          this.tabId = activeInfo.tabId
          this.startListening()
        }
      })
    }

    // 注册监听器
    chrome.tabs.onUpdated.addListener(onUpdatedListener)
    chrome.tabs.onActivated.addListener(onActivatedListener)

    // 记录监听器以便后续清理
    window.cbgGlobalListeners.listeners.push(
      { type: 'onUpdated', listener: onUpdatedListener },
      { type: 'onActivated', listener: onActivatedListener }
    )

    window.cbgGlobalListeners.isInitialized = true
    console.log('DevTools监听器已绑定')

    // 立即检查当前活动标签页
    this.checkCurrentTab()
  }

  // 检查当前活动标签页
  async checkCurrentTab() {
    try {
      const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true })
      if (activeTab && activeTab.url && activeTab.url.includes('cbg.163.com')) {
        console.log('检测到当前活动标签页是CBG页面，立即连接DevTools Protocol')
        this.tabId = activeTab.id
        this.startListening()
      } else {
        console.log('当前活动标签页不是CBG页面，等待用户切换到CBG页面')
      }
    } catch (error) {
      console.error('检查当前标签页失败:', error)
    }
  }

  async startListening() {
    if (this.isListening || !this.tabId) {
      console.log('DevTools Protocol连接条件不满足:', {
        isListening: this.isListening,
        tabId: this.tabId
      })
      return
    }

    try {
      console.log(`开始连接DevTools Protocol到标签页 ${this.tabId}`)

      // 先尝试断开现有连接
      try {
        await chrome.debugger.detach({ tabId: this.tabId })
        console.log('已断开现有调试器连接')
        // 等待一小段时间让连接完全断开
        await new Promise((resolve) => setTimeout(resolve, 200))
      } catch (detachError) {
        // 忽略断开连接的错误，可能没有现有连接
        console.log('没有现有连接需要断开')
      }

      // 连接到DevTools Protocol
      const target = await chrome.debugger.attach({ tabId: this.tabId }, '1.3')
      console.log('✅ DevTools Protocol已连接')

      // 启用Network域
      await chrome.debugger.sendCommand({ tabId: this.tabId }, 'Network.enable')
      console.log('✅ Network域已启用')

      // 监听网络请求
      chrome.debugger.onEvent.addListener((source, method, params) => {
        if (source.tabId === this.tabId) {
          this.handleNetworkEvent(method, params)
        }
      })

      this.isListening = true
      console.log('✅ 开始监听网络请求')

      // 通知面板连接成功
      chrome.runtime.sendMessage({
        action: 'devtoolsConnected',
        message: 'DevTools Protocol连接成功，开始监听网络请求'
      })
    } catch (error) {
      console.error('❌ 启动DevTools监听失败:', error)

      // 如果是调试器已连接的错误，提供用户友好的提示
      if (error.message && error.message.includes('Another debugger is already attached')) {
        console.warn('检测到其他调试器已连接，请关闭Chrome开发者工具后重试')
        this.showDebuggerConflictWarning()
      } else {
        // 其他错误，尝试重试
        console.log('将在3秒后重试连接...')
        setTimeout(() => {
          this.startListening()
        }, 3000)
      }
    }
  }

  showDebuggerConflictWarning() {
    // 通知面板显示警告信息
    chrome.runtime.sendMessage({
      action: 'showDebuggerWarning',
      message: '检测到其他调试器已连接，请关闭Chrome开发者工具后重新加载页面'
    })
  }

  handleNetworkEvent(method, params) {
    switch (method) {
      case 'Network.requestWillBeSent':
        this.handleRequestWillBeSent(params)
        break
      case 'Network.responseReceived':
        this.handleResponseReceived(params)
        break
      case 'Network.loadingFinished':
        this.handleLoadingFinished(params)
        break
    }
  }

  handleRequestWillBeSent(params) {
    const { request, requestId, timestamp } = params
    const url = request.url

    if (this.isCbgApiUrl(url)) {
      console.log('🔍 检测到CBG API请求:', url)

      const requestData = {
        requestId: requestId,
        url: url,
        method: request.method,
        timestamp: timestamp,
        status: 'pending'
      }

      this.recommendData.push(requestData)
      // 只在请求开始时发送一次更新
      this.updateUI()
    }
  }

  handleResponseReceived(params) {
    const { requestId, response, timestamp } = params
    const url = response.url

    if (this.isCbgApiUrl(url)) {
      console.log('📥 检测到CBG API响应:', url)

      // 更新请求数据
      const requestIndex = this.recommendData.findIndex((item) => item.requestId === requestId)

      if (requestIndex !== -1) {
        this.recommendData[requestIndex].response = {
          status: response.status,
          statusText: response.statusText,
          timestamp: timestamp
        }
        this.recommendData[requestIndex].status = 'completed'
      }
      console.log('📊 推荐数据更新:', this.recommendData[requestIndex])
      console.log('📈 当前总数据量:', this.recommendData.length)
      // 响应接收时不发送更新，等数据完全加载后再发送
    }
  }

  async handleLoadingFinished(params) {
    const { requestId } = params

    // 查找对应的请求
    const requestIndex = this.recommendData.findIndex((item) => item.requestId === requestId)

    if (requestIndex !== -1) {
      try {
        // 获取响应内容
        const response = await chrome.debugger.sendCommand(
          { tabId: this.tabId },
          'Network.getResponseBody',
          { requestId: requestId }
        )

        if (response.body) {
          let responseData = response.body || ''
          this.recommendData[requestIndex].responseData = responseData
          this.recommendData[requestIndex].status = 'completed'

          // 只在数据完全加载后发送一次更新
          console.log('📦 请求数据完全加载，发送更新通知')
          this.updateUI()
        }
      } catch (error) {
        console.error('获取响应内容失败:', error)
      }
    }
  }

  isCbgApiUrl(url) {
    if (typeof url !== 'string') return false

    return url.includes('cbg.163.com') && url.includes('recommend.py')
  }

  updateUI() {
    // 通知DevTools面板更新UI
    chrome.runtime.sendMessage({
      action: 'updateRecommendData',
      data: this.recommendData
    })
  }

  getRecommendData() {
    return this.recommendData
  }

  clearRecommendData() {
    this.recommendData = []
    this.updateUI()
  }

  // 清理所有监听器
  cleanup() {
    if (window.cbgGlobalListeners && window.cbgGlobalListeners.listeners) {
      window.cbgGlobalListeners.listeners.forEach(({ type, listener }) => {
        switch (type) {
          case 'onUpdated':
            chrome.tabs.onUpdated.removeListener(listener)
            break
          case 'onActivated':
            chrome.tabs.onActivated.removeListener(listener)
            break
        }
      })
      window.cbgGlobalListeners.listeners = []
      window.cbgGlobalListeners.isInitialized = false
      console.log('所有DevTools监听器已清理')
    }
  }
}

// 初始化DevTools监听器
const devToolsListener = new DevToolsListener()

// 页面卸载时清理监听器
window.addEventListener('beforeunload', () => {
  devToolsListener.cleanup()
})
