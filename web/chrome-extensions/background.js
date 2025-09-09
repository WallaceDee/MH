// Chrome插件后台服务工作者 - 仅支持DevTools
class BackgroundService {
  constructor() {
    this.init();
  }

  init() {
    this.bindEvents();
    this.initializeStorage();
  }

  bindEvents() {
    // 监听插件安装
    chrome.runtime.onInstalled.addListener((details) => {
      this.handleInstall(details);
    });

    // 监听来自devtools的消息
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
    });
  }

  async initializeStorage() {
    try {
      const result = await chrome.storage.local.get(['recommendData']);
      
      if (!result.recommendData) {
        await chrome.storage.local.set({ recommendData: [] });
      }
      
      console.log('DevTools存储初始化完成');
    } catch (error) {
      console.error('存储初始化失败:', error);
    }
  }

  handleInstall(details) {
    if (details.reason === 'install') {
      console.log('CBG爬虫助手DevTools插件已安装');
    } else if (details.reason === 'update') {
      console.log('CBG爬虫助手DevTools插件已更新');
    }
  }

  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.action) {
        case 'getRecommendData':
          const data = await this.getRecommendData();
          sendResponse({ success: true, data: data });
          break;

        case 'clearRecommendData':
          await this.clearRecommendData();
          sendResponse({ success: true });
          break;

        case 'saveRecommendData':
          await this.saveRecommendData(message.data);
          sendResponse({ success: true });
          break;


        default:
          sendResponse({ success: false, error: '未知操作' });
      }
    } catch (error) {
      console.error('处理消息失败:', error);
      sendResponse({ success: false, error: error.message });
    }

    return true;
  }

  async getRecommendData() {
    try {
      const result = await chrome.storage.local.get(['recommendData']);
      return result.recommendData || [];
    } catch (error) {
      console.error('获取数据失败:', error);
      return [];
    }
  }

  async clearRecommendData() {
    try {
      await chrome.storage.local.set({ recommendData: [] });
      console.log('DevTools数据已清空');
    } catch (error) {
      console.error('清空数据失败:', error);
    }
  }

  async saveRecommendData(data) {
    try {
      await chrome.storage.local.set({ recommendData: data });
      console.log('DevTools数据已保存');
    } catch (error) {
      console.error('保存数据失败:', error);
    }
  }

}

// 初始化后台服务
new BackgroundService();