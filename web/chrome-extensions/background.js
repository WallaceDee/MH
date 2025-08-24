// Chrome插件后台服务工作者
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

    // 监听来自popup和content script的消息
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
    });

    // 监听标签页更新
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      this.handleTabUpdate(tabId, changeInfo, tab);
    });

    // 监听标签页激活
    chrome.tabs.onActivated.addListener((activeInfo) => {
      this.handleTabActivated(activeInfo);
    });
  }

  async initializeStorage() {
    try {
      const result = await chrome.storage.local.get(['crawledCount', 'successCount', 'settings']);
      
      // 初始化默认值
      const defaults = {
        crawledCount: 0,
        successCount: 0,
        settings: {
          autoStart: false,
          delay: 2000,
          maxItems: 1000,
          exportFormat: 'json'
        }
      };

      // 合并现有数据和默认值
      const merged = {};
      for (const key in defaults) {
        merged[key] = { ...defaults[key], ...result[key] };
      }

      await chrome.storage.local.set(merged);
      console.log('存储初始化完成');
    } catch (error) {
      console.error('存储初始化失败:', error);
    }
  }

  handleInstall(details) {
    if (details.reason === 'install') {
      console.log('CBG爬虫助手插件已安装');
      
      // 创建默认设置
      this.createDefaultSettings();

    } else if (details.reason === 'update') {
      console.log('CBG爬虫助手插件已更新到版本:', details.previousVersion);
    }
  }

  async createDefaultSettings() {
    const defaultSettings = {
      autoStart: false,
      delay: 2000,
      maxItems: 1000,
      exportFormat: 'json',
      notifications: true,
      autoSave: true
    };

    try {
      await chrome.storage.local.set({ settings: defaultSettings });
    } catch (error) {
      console.error('创建默认设置失败:', error);
    }
  }

  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.action) {
        case 'getStats':
          const stats = await this.getStats();
          sendResponse({ success: true, data: stats });
          break;

        case 'updateStats':
          await this.updateStats(message.data);
          sendResponse({ success: true });
          break;

        case 'getSettings':
          const settings = await this.getSettings();
          sendResponse({ success: true, data: settings });
          break;

        case 'updateSettings':
          await this.updateSettings(message.data);
          sendResponse({ success: true });
          break;

        case 'exportData':
          await this.exportData(message.data);
          sendResponse({ success: true });
          break;

        case 'clearData':
          await this.clearData();
          sendResponse({ success: true });
          break;

        default:
          sendResponse({ success: false, error: '未知操作' });
      }
    } catch (error) {
      console.error('处理消息失败:', error);
      sendResponse({ success: false, error: error.message });
    }

    // 返回true表示异步响应
    return true;
  }

  async getStats() {
    try {
      const result = await chrome.storage.local.get(['crawledCount', 'successCount']);
      return {
        crawledCount: result.crawledCount || 0,
        successCount: result.successCount || 0,
        successRate: result.crawledCount > 0 ? Math.round((result.successCount / result.crawledCount) * 100) : 0
      };
    } catch (error) {
      console.error('获取统计数据失败:', error);
      return { crawledCount: 0, successCount: 0, successRate: 0 };
    }
  }

  async updateStats(data) {
    try {
      const current = await this.getStats();
      const updated = {
        crawledCount: (current.crawledCount || 0) + (data.count || 0),
        successCount: (current.successCount || 0) + (data.success || 0)
      };

      await chrome.storage.local.set(updated);
      
      // 发送通知
      if (updated.crawledCount > 0) {
        this.showNotification('数据更新', `已采集 ${updated.crawledCount} 条数据`);
      }
    } catch (error) {
      console.error('更新统计数据失败:', error);
    }
  }

  async getSettings() {
    try {
      const result = await chrome.storage.local.get('settings');
      return result.settings || {};
    } catch (error) {
      console.error('获取设置失败:', error);
      return {};
    }
  }

  async updateSettings(newSettings) {
    try {
      const current = await this.getSettings();
      const updated = { ...current, ...newSettings };
      await chrome.storage.local.set({ settings: updated });
      
      console.log('设置已更新:', updated);
    } catch (error) {
      console.error('更新设置失败:', error);
    }
  }

  async exportData(data) {
    try {
      // 创建下载链接
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      // 下载文件
      await chrome.downloads.download({
        url: url,
        filename: `cbg_data_${new Date().toISOString().slice(0, 10)}.json`,
        saveAs: true
      });

      // 清理URL
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      
      console.log('数据导出成功');
    } catch (error) {
      console.error('数据导出失败:', error);
    }
  }

  async clearData() {
    try {
      await chrome.storage.local.set({
        crawledCount: 0,
        successCount: 0
      });
      
      console.log('数据已清空');
    } catch (error) {
      console.error('清空数据失败:', error);
    }
  }

  handleTabUpdate(tabId, changeInfo, tab) {
    // 当页面加载完成时，检查是否是CBG页面
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes('cbg.163.com')) {
      console.log('检测到CBG页面:', tab.url);
      
      // 可以在这里执行一些初始化操作
      this.initializeCbgPage(tabId);
    }
  }

  handleTabActivated(activeInfo) {
    // 当标签页激活时，检查页面状态
    chrome.tabs.get(activeInfo.tabId, (tab) => {
      if (tab.url && tab.url.includes('cbg.163.com')) {
        console.log('激活CBG标签页:', tab.url);
      }
    });
  }

  async initializeCbgPage(tabId) {
    try {
      // 向content script发送初始化消息
      await chrome.tabs.sendMessage(tabId, { action: 'initialize' });
    } catch (error) {
      console.error('初始化CBG页面失败:', error);
    }
  }

  showNotification(title, message) {
    // 显示浏览器通知
    if (chrome.notifications) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon48.png',
        title: title,
        message: message
      });
    }
  }
}

// 初始化后台服务
new BackgroundService(); 