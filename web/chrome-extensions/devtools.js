// 创建DevTools标签页
chrome.devtools.panels.create(
    "CBG爬虫助手",
    "icons/icon16.png", 
    "panel.html",
    function(panel) {
        console.log("CBG爬虫助手DevTools面板已创建");
    }
);

// DevTools Protocol 监听器
class DevToolsListener {
  constructor() {
    this.tabId = null;
    this.isListening = false;
    this.recommendData = [];
    this.init();
  }

  init() {
    this.bindEvents();
  }

  bindEvents() {
    // 监听标签页更新
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      if (changeInfo.status === 'complete' && tab.url && tab.url.includes('cbg.163.com')) {
        this.tabId = tabId;
        this.startListening();
      }
    });

    // 监听标签页激活
    chrome.tabs.onActivated.addListener((activeInfo) => {
      chrome.tabs.get(activeInfo.tabId, (tab) => {
        if (tab.url && tab.url.includes('cbg.163.com')) {
          this.tabId = activeInfo.tabId;
          this.startListening();
        }
      });
    });
  }

  async startListening() {
    if (this.isListening || !this.tabId) return;

    try {
      // 先尝试断开现有连接
      try {
        await chrome.debugger.detach({ tabId: this.tabId });
        console.log('已断开现有调试器连接');
        // 等待一小段时间让连接完全断开
        await new Promise(resolve => setTimeout(resolve, 100));
      } catch (detachError) {
        // 忽略断开连接的错误，可能没有现有连接
        console.log('没有现有连接需要断开');
      }

      // 连接到DevTools Protocol
      const target = await chrome.debugger.attach({ tabId: this.tabId }, "1.3");
      console.log('DevTools Protocol已连接');

      // 启用Network域
      await chrome.debugger.sendCommand({ tabId: this.tabId }, "Network.enable");
      
      // 监听网络请求
      chrome.debugger.onEvent.addListener((source, method, params) => {
        if (source.tabId === this.tabId) {
          this.handleNetworkEvent(method, params);
        }
      });

      this.isListening = true;
      console.log('开始监听网络请求');

    } catch (error) {
      console.error('启动DevTools监听失败:', error);
      
      // 如果是调试器已连接的错误，提供用户友好的提示
      if (error.message && error.message.includes('Another debugger is already attached')) {
        console.warn('检测到其他调试器已连接，请关闭Chrome开发者工具后重试');
        this.showDebuggerConflictWarning();
      }
    }
  }

  showDebuggerConflictWarning() {
    // 通知面板显示警告信息
    chrome.runtime.sendMessage({
      action: 'showDebuggerWarning',
      message: '检测到其他调试器已连接，请关闭Chrome开发者工具后重新加载页面'
    });
  }

  handleNetworkEvent(method, params) {
    switch (method) {
      case 'Network.requestWillBeSent':
        this.handleRequestWillBeSent(params);
        break;
      case 'Network.responseReceived':
        this.handleResponseReceived(params);
        break;
      case 'Network.loadingFinished':
        this.handleLoadingFinished(params);
        break;
    }
  }

  handleRequestWillBeSent(params) {
    const { request, requestId, timestamp } = params;
    const url = request.url;

    if (this.isCbgApiUrl(url)) {
      console.log('🔍 检测到CBG API请求:', url);
      
      const requestData = {
        requestId: requestId,
        url: url,
        method: request.method,
        timestamp: timestamp,
        status: 'pending'
      };

      this.recommendData.push(requestData);
      this.updateUI();
    }
  }

  handleResponseReceived(params) {
    const { requestId, response, timestamp } = params;
    const url = response.url;

    if (this.isCbgApiUrl(url)) {
      console.log('📥 检测到CBG API响应:', url);
      
      // 更新请求数据
      const requestIndex = this.recommendData.findIndex(item => 
        item.requestId === requestId
      );
      
      if (requestIndex !== -1) {
        this.recommendData[requestIndex].response = {
          status: response.status,
          statusText: response.statusText,
          timestamp: timestamp
        };
        this.recommendData[requestIndex].status = 'completed';
      }
      console.log('📊 推荐数据更新:', this.recommendData[requestIndex]);
      console.log('📈 当前总数据量:', this.recommendData.length);
      this.updateUI();
    }
  }

  async handleLoadingFinished(params) {
    const { requestId } = params;
    
    // 查找对应的请求
    const requestIndex = this.recommendData.findIndex(item => 
      item.requestId === requestId
    );
    
    if (requestIndex !== -1) {
      try {
        // 获取响应内容
        const response = await chrome.debugger.sendCommand(
          { tabId: this.tabId },
          "Network.getResponseBody",
          { requestId: requestId }
        );

        if (response.body) {
          let responseData = response.body||'';
          this.recommendData[requestIndex].responseData = responseData;
          this.recommendData[requestIndex].status = 'completed';
          this.updateUI();
        }
      } catch (error) {
        console.error('获取响应内容失败:', error);
      }
    }
  }

  isCbgApiUrl(url) {
    if (typeof url !== 'string') return false;
    
    return url.includes('cbg.163.com') && url.includes('recommend.py');
  }

  updateUI() {
    // 通知DevTools面板更新UI
    chrome.runtime.sendMessage({
      action: 'updateRecommendData',
      data: this.recommendData
    });
  }

  getRecommendData() {
    return this.recommendData;
  }

  clearRecommendData() {
    this.recommendData = [];
    this.updateUI();
  }
}

// 初始化DevTools监听器
new DevToolsListener();
