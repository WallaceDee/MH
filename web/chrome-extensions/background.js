// 后台脚本
console.log('CBG爬虫助手后台脚本已加载');

// DevTools Protocol 监听器
class DevToolsListener {
  constructor() {
    this.tabId = null
    this.isListening = false
    this.recommendData = []
    this.pendingMessage = null // 存储待发送的消息
    this.init()
  }

  init() {
    this.bindEvents()
  }

  bindEvents() {
    // 监听标签页更新
    const onUpdatedListener = (tabId, changeInfo, tab) => {
      if (changeInfo.status === 'complete' && tab.url && tab.url.includes('cbg.163.com')) {
        console.log('检测到CBG页面加载完成:', tab.url);
        this.tabId = tabId
        this.startListening()
        // 当检测到CBG页面时，不自动打开side panel（避免用户手势错误）
        // chrome.sidePanel.open({ tabId: tabId });
      }
    }

    // 监听标签页激活
    const onActivatedListener = (activeInfo) => {
      chrome.tabs.get(activeInfo.tabId, (tab) => {
        if (tab.url && tab.url.includes('cbg.163.com')) {
          console.log('激活CBG页面:', tab.url);
          this.tabId = activeInfo.tabId
          this.startListening()
          // 当激活CBG页面时，不自动打开side panel（避免用户手势错误）
          // chrome.sidePanel.open({ tabId: activeInfo.tabId });
        }
      })
    }

    // 注册监听器
    chrome.tabs.onUpdated.addListener(onUpdatedListener)
    chrome.tabs.onActivated.addListener(onActivatedListener)

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
    console.log('startListening 被调用，当前状态:', {
      isListening: this.isListening,
      tabId: this.tabId,
      recommendDataLength: this.recommendData.length
    })
    
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

      // 通知side panel连接成功
      this.sendMessageToSidePanel({
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
    // 通知side panel显示警告信息
    this.sendMessageToSidePanel({
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

      const requestData = {
        requestId: requestId,
        url: url,
        method: request.method,
        timestamp: timestamp,
        status: 'pending'
      }

      this.recommendData.push(requestData)
      console.log('📊 推荐数据已添加，当前总数:', this.recommendData.length)
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

    // 检查是否是CBG相关的API请求
    const isCbgDomain = url.includes('cbg.163.com')
    const isApiRequest = url.includes('recommend.py')
    return isCbgDomain && isApiRequest
  }

  updateUI() {
    console.log('📤 发送数据更新到side panel，数据量:', this.recommendData.length)
    // 通知side panel更新UI
    this.sendMessageToSidePanel({
      action: 'updateRecommendData',
      data: this.recommendData
    })
  }

  // 发送消息到side panel，带重试机制
  sendMessageToSidePanel(message, retryCount = 0) {
    const maxRetries = 5
    const retryDelay = 2000 // 2秒

    chrome.runtime.sendMessage(message).then(() => {
      console.log('✅ 消息发送成功:', message.action)
    }).catch((error) => {
      console.warn(`❌ 消息发送失败 (尝试 ${retryCount + 1}/${maxRetries + 1}):`, error.message)
      
      // 检查错误类型
      if (error.message.includes('Could not establish connection')) {
        console.log('接收端不存在，可能是DevTools Panel还未加载完成')
      } else if (error.message.includes('Receiving end does not exist')) {
        console.log('接收端不存在，等待DevTools Panel初始化')
      }
      
      if (retryCount < maxRetries) {
        const delay = retryDelay * (retryCount + 1) // 递增延迟
        console.log(`将在 ${delay}ms 后重试...`)
        setTimeout(() => {
          this.sendMessageToSidePanel(message, retryCount + 1)
        }, delay)
      } else {
        console.error('❌ 消息发送最终失败，停止重试:', message.action)
        // 如果是重要消息，可以考虑存储起来稍后发送
        if (message.action === 'devtoolsConnected') {
          console.log('存储devtoolsConnected消息，等待面板加载后发送')
          this.pendingMessage = message
        }
      }
    })
  }

  getRecommendData() {
    return this.recommendData
  }

  clearRecommendData() {
    this.recommendData = []
    this.updateUI()
  }
}

// 初始化DevTools监听器
const devToolsListener = new DevToolsListener()

// 监听来自side panel的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('后台收到消息:', request);
  
  switch (request.action) {
    case 'ping':
      // 处理ping消息，用于检查连接状态
      console.log('收到ping消息，返回pong');
      
      // 如果有待发送的消息，现在发送
      if (devToolsListener.pendingMessage) {
        console.log('发送待发送的消息:', devToolsListener.pendingMessage.action);
        devToolsListener.sendMessageToSidePanel(devToolsListener.pendingMessage);
        devToolsListener.pendingMessage = null;
      }
      
      sendResponse({ success: true, message: 'pong' });
      return true;
      
    case 'getCookies':
      handleGetCookies(sendResponse);
      return true; // 保持消息通道开放
      
    case 'updateRecommendData':
      // 转发数据到side panel
      chrome.runtime.sendMessage({
        action: 'updateRecommendData',
        data: request.data
      });
      break;
      
    case 'showDebuggerWarning':
      // 转发警告到side panel
      chrome.runtime.sendMessage({
        action: 'showDebuggerWarning',
        message: request.message
      });
      break;
      
    case 'clearRecommendData':
      // 清空推荐数据
      devToolsListener.clearRecommendData();
      break;
      
    case 'getRecommendData':
      // 获取当前推荐数据
      sendResponse({
        success: true,
        data: devToolsListener.getRecommendData()
      });
      return true;
  }
});

// 处理获取Cookie请求
async function handleGetCookies(sendResponse) {
  try {
    // 获取当前活动标签页
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab || !tab.url.includes('cbg.163.com')) {
      sendResponse({ success: false, error: '当前页面不是CBG页面' });
      return;
    }
    
    // 获取Cookie
    const cookies = await chrome.cookies.getAll({ domain: '.163.com' });
    
    // 格式化Cookie字符串
    const cookieString = cookies.map(cookie => `${cookie.name}=${cookie.value}`).join('; ');
    
    sendResponse({ 
      success: true, 
      cookies: cookieString,
      count: cookies.length 
    });
    
  } catch (error) {
    console.error('获取Cookie失败:', error);
    sendResponse({ success: false, error: error.message });
  }
}

// 扩展安装时的初始化
chrome.runtime.onInstalled.addListener((details) => {
  console.log('CBG爬虫助手已安装/更新:', details.reason);
  
  if (details.reason === 'install') {
    // 首次安装时的初始化
    console.log('首次安装，进行初始化...');
  } else if (details.reason === 'update') {
    // 更新时的处理
    console.log('扩展已更新到新版本');
  }
});

// 监听action点击事件（扩展图标点击）
// 延迟注册action监听器，确保Chrome API完全加载
setTimeout(() => {
  try {
    console.log('开始注册action监听器...');
    console.log('chrome对象:', typeof chrome);
    console.log('chrome.action对象:', typeof chrome.action);
    
    if (typeof chrome !== 'undefined' && chrome.action && chrome.action.onClicked) {
      chrome.action.onClicked.addListener((tab) => {
        console.log('扩展图标被点击，当前标签页:', tab.url);
        if (tab.url && tab.url.includes('cbg.163.com')) {
          // 如果当前页面是CBG页面，打开side panel（用户点击扩展图标，这是用户手势）
          chrome.sidePanel.open({ tabId: tab.id });
          console.log('✅ 已打开Side Panel');
        } else {
          // 如果不是CBG页面，提示用户
          chrome.tabs.create({ url: 'https://cbg.163.com' });
          console.log('✅ 已打开CBG页面');
        }
      });
      console.log('✅ Action点击监听器已注册');
    } else {
      console.warn('⚠️ chrome.action API不可用，跳过action监听器注册');
      console.log('chrome.action类型:', typeof chrome.action);
      console.log('chrome.action.onClicked类型:', typeof chrome.action?.onClicked);
      console.log('chrome.action.onClicked.addListener类型:', typeof chrome.action?.onClicked?.addListener);
    }
  } catch (error) {
    console.error('❌ 注册action监听器失败:', error);
    console.error('错误详情:', error.message);
    console.error('错误堆栈:', error.stack);
  }
}, 1000); // 延迟1秒注册
