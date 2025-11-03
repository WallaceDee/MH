// 后台脚本
console.log('CBG爬虫助手后台脚本已加载');

// DevTools Protocol 监听器
class DevToolsListener {
  constructor() {
    this.currentTabId = null // 当前监听的标签页ID
    this.isListening = false
    this.recommendData = []
    this.pendingMessage = null // 存储待发送的消息
    this.sentRequests = new Set() // 跟踪已发送的请求ID
    this.activeCbgTabs = new Set() // 跟踪所有CBG标签页
    this.init()
  }

  init() {
    this.bindEvents()
  }

  bindEvents() {
    // 监听标签页更新
    const onUpdatedListener = (tabId, changeInfo, tab) => {
      console.log('标签页更新事件:', {
        tabId,
        changeInfo,
        url: tab?.url,
        status: changeInfo?.status
      })
      
      if (changeInfo.status === 'complete' && tab.url && tab.url.includes('cbg.163.com')) {
        console.log('检测到CBG页面加载完成:', tab.url);
        
        // 如果tab.url就是监听的API请求URL（isCbgApiUrl返回true）
        if (this.isCbgApiUrl && this.isCbgApiUrl(tab.url)) {
          console.log('检测到API请求URL:', tab.url);
          
          // 获取页面返回内容并发送到side panel
          chrome.tabs.sendMessage(tabId, { action: 'getPageContent' }, (response) => {
            if (response && response.content) {
              // 构造请求数据
              const requestData = {
                requestId: 'page_' + Date.now(),
                url: tab.url,
                method: 'GET',
                timestamp: Date.now(),
                status: 'completed',
                responseData: response.content
              };
              
              // 添加到推荐数据数组
              this.recommendData.push(requestData);
              
              // 发送更新到side panel
              this.updateUI();
              
              console.log('✅ API内容已发送到side panel');
            }
          });
        }
        
        this.activeCbgTabs.add(tabId)
        
        // 如果当前没有监听任何标签页，或者激活的是当前监听的标签页，则开始监听
        if (!this.isListening || this.currentTabId === tabId) {
          this.switchToTab(tabId)
        } else {
          console.log('当前正在监听其他标签页，等待用户切换到该标签页')
        }
      } else if (tab.url && !tab.url.includes('cbg.163.com')) {
        // 如果标签页不再是CBG页面，从跟踪列表中移除
        this.activeCbgTabs.delete(tabId)
        if (this.currentTabId === tabId) {
          console.log('当前监听的标签页不再是CBG页面，停止监听')
          this.stopListening()
        }
      }
    }

    // 监听标签页激活
    const onActivatedListener = (activeInfo) => {
      console.log('标签页激活事件:', activeInfo)
      chrome.tabs.get(activeInfo.tabId, (tab) => {
        console.log('激活的标签页信息:', {
          tabId: tab?.id,
          url: tab?.url,
          status: tab?.status
        })
        
        if (tab.url && tab.url.includes('cbg.163.com')) {
          console.log('激活CBG页面:', tab.url);
          this.activeCbgTabs.add(activeInfo.tabId)
          this.switchToTab(activeInfo.tabId)
        } else {
          // 如果激活的不是CBG页面，且当前正在监听该标签页，则停止监听
          if (this.currentTabId === activeInfo.tabId) {
            console.log('激活的标签页不是CBG页面，停止监听')
            this.stopListening()
          }
        }
      })
    }

    // 监听标签页关闭
    const onRemovedListener = (tabId) => {
      console.log('标签页关闭事件:', tabId)
      this.activeCbgTabs.delete(tabId)
      if (this.currentTabId === tabId) {
        console.log('当前监听的标签页已关闭，停止监听')
        this.stopListening()
      }
    }

    // 注册监听器
    chrome.tabs.onUpdated.addListener(onUpdatedListener)
    chrome.tabs.onActivated.addListener(onActivatedListener)
    chrome.tabs.onRemoved.addListener(onRemovedListener)

    console.log('DevTools监听器已绑定')

    // 立即检查当前活动标签页
    this.checkCurrentTab()
  }

  // 检查当前活动标签页
  async checkCurrentTab() {
    try {
      const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true })
      console.log('检查当前活动标签页:', {
        tabId: activeTab?.id,
        url: activeTab?.url,
        status: activeTab?.status
      })
      
      if (activeTab && activeTab.url && activeTab.url.includes('cbg.163.com')) {
        console.log('检测到当前活动标签页是CBG页面，立即连接DevTools Protocol')
        this.activeCbgTabs.add(activeTab.id)
        this.switchToTab(activeTab.id)
      } else {
        console.log('当前活动标签页不是CBG页面，等待用户切换到CBG页面')
        console.log('当前标签页信息:', {
          exists: !!activeTab,
          url: activeTab?.url,
          isCbg: activeTab?.url?.includes('cbg.163.com')
        })
      }
    } catch (error) {
      console.error('检查当前标签页失败:', error)
    }
  }

  // 切换到指定标签页进行监听
  async switchToTab(tabId) {
    console.log('切换到标签页进行监听:', tabId)
    
    // 如果已经在监听该标签页，无需重复操作
    if (this.isListening && this.currentTabId === tabId) {
      console.log('已经在监听该标签页，无需重复操作')
      return
    }
    
    // 停止当前监听
    if (this.isListening) {
      console.log('停止当前监听，切换到新标签页')
      await this.stopListening()
    }
    
    // 开始监听新标签页
    this.currentTabId = tabId
    await this.startListening()
  }

  // 停止监听
  async stopListening() {
    if (!this.isListening) {
      console.log('当前没有在监听，无需停止')
      return
    }
    
    try {
      if (this.currentTabId) {
        await chrome.debugger.detach({ tabId: this.currentTabId })
        console.log('✅ 已断开DevTools Protocol连接')
      }
    } catch (error) {
      console.log('断开连接时出错（可能没有连接）:', error.message)
    }
    
    this.isListening = false
    this.currentTabId = null
    
    // 通知side panel连接断开
    this.sendMessageToSidePanel({
      action: 'devtoolsDisconnected',
      message: '⚠️ 连接已断开，请刷新页面重试'
    })
  }

  async startListening() {
    console.log('startListening 被调用，当前状态:', {
      isListening: this.isListening,
      currentTabId: this.currentTabId,
      recommendDataLength: this.recommendData.length
    })
    
    if (this.isListening) {
      console.log('DevTools Protocol已连接，跳过重复连接')
      return
    }
    
    if (!this.currentTabId) {
      console.log('DevTools Protocol连接条件不满足: 缺少currentTabId')
      return
    }

    try {
      console.log(`开始连接DevTools Protocol到标签页 ${this.currentTabId}`)

      // 先尝试断开现有连接
      try {
        await chrome.debugger.detach({ tabId: this.currentTabId })
        console.log('已断开现有调试器连接')
        // 等待一小段时间让连接完全断开
        await new Promise((resolve) => setTimeout(resolve, 200))
      } catch (detachError) {
        // 忽略断开连接的错误，可能没有现有连接
        console.log('没有现有连接需要断开')
      }

      // 连接到DevTools Protocol
      const target = await chrome.debugger.attach({ tabId: this.currentTabId }, '1.3')
      console.log('✅ DevTools Protocol已连接')

      // 启用Network域
      await chrome.debugger.sendCommand({ tabId: this.currentTabId }, 'Network.enable')
      console.log('✅ Network域已启用')

      // 监听网络请求
      chrome.debugger.onEvent.addListener((source, method, params) => {
        if (source.tabId === this.currentTabId) {
          this.handleNetworkEvent(method, params)
        }
      })

      this.isListening = true
      console.log('✅ 开始监听网络请求')

      // 通知side panel连接成功
      this.sendMessageToSidePanel({
        action: 'devtoolsConnected',
        message: `✅ 连接成功！正在监听当前页面的数据请求`
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
      message: '⚠️ 检测到Chrome开发者工具已打开，请关闭后重新加载页面'
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
          { tabId: this.currentTabId },
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
    // 只发送新增的已完成且有响应数据的数据
    const newData = this.recommendData.filter(item => 
      item.status === 'completed' && 
      item.responseData && 
      !this.sentRequests.has(item.requestId)
    )
    
    if (newData.length > 0) {
      // 标记为已发送
      newData.forEach(item => this.sentRequests.add(item.requestId))
      
      console.log('📤 发送增量数据到side panel，新增数据量:', newData.length, '总数据量:', this.recommendData.length)
      
      // 发送增量数据
      this.sendMessageToSidePanel({
        action: 'addRecommendData',
        data: newData
      })
    } else {
      console.log('📤 没有新数据需要发送')
    }
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
    this.sentRequests.clear() // 清空已发送请求跟踪
    this.updateUI()
  }

  // 获取所有CBG标签页信息
  getCbgTabsInfo() {
    return {
      currentTabId: this.currentTabId,
      isListening: this.isListening,
      activeCbgTabs: Array.from(this.activeCbgTabs),
      totalData: this.recommendData.length
    }
  }

  // 手动切换到指定标签页
  async switchToSpecificTab(tabId) {
    if (this.activeCbgTabs.has(tabId)) {
      await this.switchToTab(tabId)
      return { success: true, message: `已切换到标签页 ${tabId}` }
    } else {
      return { success: false, message: `标签页 ${tabId} 不是CBG页面` }
    }
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
      
    case 'refreshCurrentPage':
      // 刷新当前页面
      handleRefreshCurrentPage(sendResponse);
      return true; // 保持消息通道开放
      
    case 'getCbgTabsInfo':
      // 获取所有CBG标签页信息
      sendResponse({
        success: true,
        data: devToolsListener.getCbgTabsInfo()
      });
      return true;
      
    case 'switchToTab':
      // 切换到指定标签页
      handleSwitchToTab(request.tabId, sendResponse);
      return true; // 保持消息通道开放
      
    case 'closeSidePanel':
      // 关闭SidePanel
      handleCloseSidePanel(request.tabId, sendResponse);
      return true; // 保持消息通道开放
  }
});

// 处理刷新当前页面的请求
async function handleRefreshCurrentPage(sendResponse) {
  try {
    // 优先使用被监控的CBG标签页ID
    const monitoredTabId = devToolsListener.currentTabId;
    
    if (monitoredTabId) {
      // 获取被监控的标签页信息
      try {
        const monitoredTab = await chrome.tabs.get(monitoredTabId);
        
        if (!monitoredTab) {
          sendResponse({ success: false, error: '无法获取被监控的标签页' });
          return;
        }
        
        // 检查是否是插件页面（不应该发生，但做安全检查）
        if (monitoredTab.url && monitoredTab.url.startsWith('chrome-extension://')) {
          sendResponse({ success: false, error: '被监控的标签页是插件页面，无法刷新' });
          return;
        }
        
        // 刷新被监控的标签页
        await chrome.tabs.reload(monitoredTabId);
        
        console.log('✅ 刷新被监控的CBG页面成功:', monitoredTab.url);
        sendResponse({ 
          success: true, 
          message: '页面刷新成功',
          url: monitoredTab.url
        });
        return;
      } catch (tabError) {
        console.warn('获取被监控标签页失败，尝试使用当前活动标签页:', tabError);
        // 如果获取被监控标签页失败，继续使用备用方案
      }
    }
    
    // 备用方案：如果没有正在监控的标签页，尝试使用当前活动标签页
    const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!activeTab) {
      sendResponse({ success: false, error: '无法获取当前活动标签页，且没有正在监控的标签页' });
      return;
    }
    
    // 检查是否是插件页面
    if (activeTab.url && activeTab.url.startsWith('chrome-extension://')) {
      sendResponse({ 
        success: false, 
        error: '当前活动标签页是插件页面，无法刷新。请切换到CBG页面后再试，或者等待监控连接建立。' 
      });
      return;
    }
    
    // 刷新当前活动标签页（备用方案）
    await chrome.tabs.reload(activeTab.id);
    
    console.log('✅ 刷新当前活动标签页成功:', activeTab.url);
    sendResponse({ 
      success: true, 
      message: '页面刷新成功',
      url: activeTab.url
    });
    
  } catch (error) {
    console.error('❌ 刷新页面失败:', error);
    sendResponse({ 
      success: false, 
      error: `刷新页面失败: ${error.message}` 
    });
  }
}

// 处理切换到指定标签页的请求
async function handleSwitchToTab(tabId, sendResponse) {
  try {
    const result = await devToolsListener.switchToSpecificTab(tabId);
    sendResponse(result);
  } catch (error) {
    console.error('❌ 切换标签页失败:', error);
    sendResponse({ 
      success: false, 
      error: `切换标签页失败: ${error.message}` 
    });
  }
}

// 处理关闭SidePanel的请求
// 注意：chrome.sidePanel.close() API不存在，需要通过消息发送给SidePanel让其调用window.close()
async function handleCloseSidePanel(tabId, sendResponse) {
  try {
    // chrome.sidePanel.close() API不存在，需要通过消息传递
    // 发送消息给SidePanel，让它自己调用window.close()
    
    // 获取所有CBG标签页，向它们的SidePanel发送关闭消息
    const cbgTabs = await chrome.tabs.query({ 
      url: ['https://xyq.cbg.163.com/*'] 
    });
    
    if (cbgTabs && cbgTabs.length > 0) {
      // 向所有CBG标签页的SidePanel发送关闭消息
      const messagePromises = cbgTabs.map(tab => {
        if (tab.id) {
          return chrome.runtime.sendMessage({
            action: 'closeSidePanel'
          }).catch(err => {
            // 忽略消息发送失败（可能SidePanel未打开）
            console.log(`向标签页 ${tab.id} 的SidePanel发送关闭消息失败:`, err.message);
            return null;
          });
        }
        return Promise.resolve(null);
      });
      
      await Promise.all(messagePromises);
      console.log('✅ 已向所有CBG标签页的SidePanel发送关闭消息');
      sendResponse({ 
        success: true, 
        message: '已发送关闭消息给SidePanel' 
      });
    } else {
      // 如果没有CBG标签页，尝试向当前活动标签页发送消息
      const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (activeTab && activeTab.id) {
        try {
          await chrome.runtime.sendMessage({
            action: 'closeSidePanel'
          });
          console.log('✅ 已向当前活动标签页的SidePanel发送关闭消息');
          sendResponse({ 
            success: true, 
            message: '已发送关闭消息给SidePanel' 
          });
        } catch (error) {
          console.warn('发送关闭消息失败:', error);
          sendResponse({ 
            success: false, 
            error: `发送关闭消息失败: ${error.message}` 
          });
        }
      } else {
        console.warn('⚠️ 无法发送关闭消息: 没有找到CBG标签页或活动标签页');
        sendResponse({ 
          success: false, 
          error: '无法发送关闭消息: 没有找到CBG标签页或活动标签页' 
        });
      }
    }
  } catch (error) {
    console.error('❌ 发送关闭SidePanel消息失败:', error);
    sendResponse({ 
      success: false, 
      error: `发送关闭消息失败: ${error.message}` 
    });
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
        }
        //如果当前页面是CBG页面，已打开side panel，则打开插件官网页面https://xyq.lintong.com/
        else {
          // 如果不是CBG页面，提示用户
          chrome.tabs.create({ url: 'https://xyq.cbg.163.com/' });
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
