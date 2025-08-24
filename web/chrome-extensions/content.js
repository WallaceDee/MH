// Chrome插件内容脚本 - 在CBG页面上执行
class CbgContentScript {
  constructor() {
    this.isCrawling = false;
    this.crawledData = [];
    this.currentPage = 1;
    this.maxPages = 100;
    this.delay = 2000;
    this.init();
  }

  init() {
    this.bindEvents();
    this.injectUI();
    this.loadSettings();
  }

  bindEvents() {
    // 监听来自popup和background的消息
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
    });

    // 监听页面变化
    this.observePageChanges();
  }

  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.action) {
        case 'initialize':
          this.initialize();
          sendResponse({ success: true });
          break;

        case 'startCrawl':
          await this.startCrawling();
          sendResponse({ success: true });
          break;

        case 'stopCrawl':
          this.stopCrawling();
          sendResponse({ success: true });
          break;

        case 'exportData':
          await this.exportData();
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

  initialize() {
    console.log('CBG页面初始化完成');
    this.updateStatus('页面已就绪');
  }

  async startCrawling() {
    if (this.isCrawling) {
      console.log('采集已在进行中');
      return;
    }

    this.isCrawling = true;
    this.crawledData = [];
    this.currentPage = 1;
    
    console.log('开始数据采集');
    this.updateStatus('开始采集...');
    this.showProgressBar();

    try {
      await this.crawlCurrentPage();
    } catch (error) {
      console.error('采集失败:', error);
      this.updateStatus('采集失败');
      this.isCrawling = false;
    }
  }

  stopCrawling() {
    this.isCrawling = false;
    console.log('停止数据采集');
    this.updateStatus('已停止');
    this.hideProgressBar();
  }

  async crawlCurrentPage() {
    if (!this.isCrawling || this.currentPage > this.maxPages) {
      this.finishCrawling();
      return;
    }

    try {
      this.updateStatus(`正在采集第 ${this.currentPage} 页...`);
      
      // 采集当前页面数据
      const pageData = await this.extractPageData();
      
      if (pageData && pageData.length > 0) {
        this.crawledData.push(...pageData);
        this.updateProgress();
        
        // 发送进度更新
        this.sendProgressUpdate();
        
        console.log(`第 ${this.currentPage} 页采集完成，获得 ${pageData.length} 条数据`);
      }

      // 检查是否有下一页
      if (await this.hasNextPage()) {
        this.currentPage++;
        await this.goToNextPage();
        
        // 延迟后继续采集
        setTimeout(() => {
          if (this.isCrawling) {
            this.crawlCurrentPage();
          }
        }, this.delay);
      } else {
        this.finishCrawling();
      }

    } catch (error) {
      console.error(`第 ${this.currentPage} 页采集失败:`, error);
      this.updateStatus(`第 ${this.currentPage} 页采集失败`);
      
      // 继续下一页
      this.currentPage++;
      setTimeout(() => {
        if (this.isCrawling) {
          this.crawlCurrentPage();
        }
      }, this.delay);
    }
  }

  async extractPageData() {
    const items = [];
    
    try {
      // 查找装备列表项
      const itemElements = document.querySelectorAll('.item-list .item, .equip-item, [data-item]');
      
      for (const element of itemElements) {
        try {
          const itemData = this.extractItemData(element);
          if (itemData) {
            items.push(itemData);
          }
        } catch (error) {
          console.error('提取单个装备数据失败:', error);
        }
      }

      // 如果没有找到标准元素，尝试其他选择器
      if (items.length === 0) {
        const alternativeElements = document.querySelectorAll('.item, .equipment, .goods-item');
        for (const element of alternativeElements) {
          try {
            const itemData = this.extractItemData(element);
            if (itemData) {
              items.push(itemData);
            }
          } catch (error) {
            console.error('提取替代元素数据失败:', error);
          }
        }
      }

    } catch (error) {
      console.error('提取页面数据失败:', error);
    }

    return items;
  }

  extractItemData(element) {
    try {
      // 提取装备名称
      const nameElement = element.querySelector('.item-name, .name, .title, h3, h4');
      const name = nameElement ? nameElement.textContent.trim() : '';

      // 提取价格
      const priceElement = element.querySelector('.price, .cost, .money, .amount');
      const price = priceElement ? this.extractPrice(priceElement.textContent) : '';

      // 提取等级
      const levelElement = element.querySelector('.level, .lvl, .grade');
      const level = levelElement ? this.extractLevel(levelElement.textContent) : '';

      // 提取属性信息
      const attributes = this.extractAttributes(element);

      // 提取链接
      const linkElement = element.querySelector('a');
      const link = linkElement ? linkElement.href : '';

      // 提取图片
      const imgElement = element.querySelector('img');
      const image = imgElement ? imgElement.src : '';

      // 提取时间戳
      const timestamp = new Date().toISOString();

      if (name) {
        return {
          name,
          price,
          level,
          attributes,
          link,
          image,
          timestamp,
          page: this.currentPage
        };
      }

      return null;
    } catch (error) {
      console.error('提取装备数据失败:', error);
      return null;
    }
  }

  extractPrice(text) {
    if (!text) return '';
    
    // 提取数字和单位
    const priceMatch = text.match(/[\d,]+/);
    if (priceMatch) {
      return priceMatch[0].replace(/,/g, '');
    }
    
    return text.trim();
  }

  extractLevel(text) {
    if (!text) return '';
    
    // 提取等级数字
    const levelMatch = text.match(/\d+/);
    if (levelMatch) {
      return levelMatch[0];
    }
    
    return text.trim();
  }

  extractAttributes(element) {
    const attributes = {};
    
    try {
      // 查找属性元素
      const attrElements = element.querySelectorAll('.attr, .property, .stat, .effect');
      
      for (const attrElement of attrElements) {
        const text = attrElement.textContent.trim();
        if (text) {
          // 尝试解析属性名和值
          const attrMatch = text.match(/(.+?)[:：]\s*(.+)/);
          if (attrMatch) {
            attributes[attrMatch[1].trim()] = attrMatch[2].trim();
          } else {
            attributes[text] = '';
          }
        }
      }
    } catch (error) {
      console.error('提取属性失败:', error);
    }
    
    return attributes;
  }

  async hasNextPage() {
    try {
      // 查找下一页按钮
      const nextButton = document.querySelector('.next, .next-page, [data-page="next"], .pagination .next');
      return nextButton && !nextButton.disabled && !nextButton.classList.contains('disabled');
    } catch (error) {
      console.error('检查下一页失败:', error);
      return false;
    }
  }

  async goToNextPage() {
    try {
      const nextButton = document.querySelector('.next, .next-page, [data-page="next"], .pagination .next');
      if (nextButton) {
        nextButton.click();
        
        // 等待页面加载
        await this.waitForPageLoad();
      }
    } catch (error) {
      console.error('跳转下一页失败:', error);
    }
  }

  async waitForPageLoad() {
    return new Promise((resolve) => {
      // 等待页面内容更新
      setTimeout(resolve, 1000);
    });
  }

  updateProgress() {
    const progressBar = document.getElementById('cbg-progress-bar');
    if (progressBar) {
      const progress = (this.currentPage / this.maxPages) * 100;
      progressBar.style.width = `${Math.min(progress, 100)}%`;
      progressBar.textContent = `${this.currentPage}/${this.maxPages}`;
    }
  }

  sendProgressUpdate() {
    chrome.runtime.sendMessage({
      type: 'crawlProgress',
      data: {
        count: this.crawledData.length,
        success: this.crawledData.length,
        currentPage: this.currentPage,
        maxPages: this.maxPages
      }
    });
  }

  finishCrawling() {
    this.isCrawling = false;
    console.log('数据采集完成');
    this.updateStatus('采集完成');
    this.hideProgressBar();
    
    // 发送完成消息
    chrome.runtime.sendMessage({
      type: 'crawlComplete',
      data: {
        total: this.crawledData.length,
        success: this.crawledData.length,
        data: this.crawledData
      }
    });
    
    // 保存数据到本地存储
    this.saveData();
  }

  async saveData() {
    try {
      await chrome.storage.local.set({
        crawledData: this.crawledData,
        lastCrawlTime: new Date().toISOString()
      });
      
      console.log('数据已保存到本地存储');
    } catch (error) {
      console.error('保存数据失败:', error);
    }
  }

  async exportData() {
    try {
      // 获取所有采集的数据
      const result = await chrome.storage.local.get(['crawledData']);
      const data = result.crawledData || this.crawledData;
      
      if (data && data.length > 0) {
        // 发送给background script进行导出
        chrome.runtime.sendMessage({
          action: 'exportData',
          data: data
        });
        
        this.updateStatus('数据导出中...');
      } else {
        this.updateStatus('没有可导出的数据');
      }
    } catch (error) {
      console.error('导出数据失败:', error);
      this.updateStatus('导出失败');
    }
  }

  injectUI() {
    // 注入状态栏
    const statusBar = document.createElement('div');
    statusBar.id = 'cbg-status-bar';
    statusBar.innerHTML = `
      <div class="cbg-status-content">
        <span class="cbg-status-text">CBG爬虫助手已就绪</span>
        <div class="cbg-progress-container" style="display: none;">
          <div class="cbg-progress-bar" id="cbg-progress-bar"></div>
        </div>
      </div>
    `;
    
    // 注入样式
    const style = document.createElement('style');
    style.textContent = `
      #cbg-status-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        z-index: 10000;
        font-size: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
      }
      
      .cbg-status-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      
      .cbg-status-text {
        font-weight: 500;
      }
      
      .cbg-progress-container {
        flex: 1;
        margin-left: 16px;
        background: rgba(255,255,255,0.2);
        border-radius: 4px;
        overflow: hidden;
      }
      
      .cbg-progress-bar {
        height: 20px;
        background: rgba(255,255,255,0.8);
        color: #333;
        text-align: center;
        line-height: 20px;
        font-size: 11px;
        font-weight: 600;
        transition: width 0.3s ease;
        width: 0%;
      }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(statusBar);
  }

  updateStatus(message) {
    const statusText = document.querySelector('#cbg-status-bar .cbg-status-text');
    if (statusText) {
      statusText.textContent = message;
    }
  }

  showProgressBar() {
    const progressContainer = document.querySelector('#cbg-status-bar .cbg-progress-container');
    if (progressContainer) {
      progressContainer.style.display = 'block';
    }
  }

  hideProgressBar() {
    const progressContainer = document.querySelector('#cbg-status-bar .cbg-progress-container');
    if (progressContainer) {
      progressContainer.style.display = 'none';
    }
  }

  observePageChanges() {
    // 监听DOM变化
    const observer = new MutationObserver((mutations) => {
      if (this.isCrawling) {
        // 页面内容变化时，可能需要重新采集
        console.log('页面内容发生变化');
      }
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  async loadSettings() {
    try {
      const result = await chrome.storage.local.get('settings');
      const settings = result.settings || {};
      
      this.delay = settings.delay || 2000;
      this.maxPages = settings.maxPages || 100;
      
      console.log('设置已加载:', settings);
    } catch (error) {
      console.error('加载设置失败:', error);
    }
  }
}

// 初始化内容脚本
new CbgContentScript(); 