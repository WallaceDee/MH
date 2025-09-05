// Chrome插件内容脚本 - 在CBG页面上执行
(function() {
  'use strict';
  
  // 防止重复加载
  if (window.cbgCrawlerLoaded) {
    console.log('CBG爬虫助手已加载，跳过重复加载');
    return;
  }
  window.cbgCrawlerLoaded = true;
  
  console.log(' CBG爬虫助手开始加载...');
  
  // 全局变量
  let recommendData = [];
  let isListening = false;
  let originalFetch = null;
  let originalXHROpen = null;
  let originalXHRSend = null;
  let originalCreateElement = null;

  // 检查URL是否匹配CBG相关接口
  function isCbgApiUrl(url) {
    if (typeof url !== 'string') return false;
    
    const cbgPatterns = [
      'recommend.py'
    ];
    
    return url.includes('cbg.163.com') && cbgPatterns.some(pattern => url.includes(pattern));
  }

  // 处理拦截到的请求
  function handleInterceptedRequest(type, url, options) {
    const requestData = {
      type: type,
      url: url,
      method: options?.method || 'GET',
      timestamp: new Date().toISOString(),
      requestBody: options?.body || null,
      headers: options?.headers || null
    };

    console.log('🔍 拦截到CBG API请求:', requestData);
    recommendData.push({
      ...requestData,
      response: null,
      status: 'pending'
    });

    updateUI();
    updateDataDisplay();
  }

  // 处理拦截到的响应
  async function handleInterceptedResponse(type, url, response) {
    try {
      let responseData = null;
      
      if (type === 'fetch') {
        try {
          responseData = await response.clone().json();
        } catch (e) {
          try {
            responseData = await response.clone().text();
          } catch (e2) {
            responseData = '无法解析响应数据';
          }
        }
      } else if (type === 'xhr') {
        try {
          responseData = JSON.parse(response.responseText);
        } catch (e) {
          responseData = response.responseText;
        }
      } else if (type === 'jsonp') {
        responseData = response;
      }

      const responseInfo = {
        type: type,
        url: url,
        status: 200,
        statusText: 'OK',
        timestamp: new Date().toISOString(),
        data: responseData
      };

      console.log('📥 监听到CBG API响应:', responseInfo);
      console.log('📥 响应数据类型:', typeof responseData);
      console.log('📥 响应数据内容:', responseData);

      // 更新对应的请求数据
      const requestIndex = recommendData.findIndex(item => 
        item.url === url && item.status === 'pending'
      );
      
      if (requestIndex !== -1) {
        recommendData[requestIndex].response = responseInfo;
        recommendData[requestIndex].status = 'completed';
        console.log('✅ 更新请求数据，索引:', requestIndex);
      } else {
        recommendData.push({
          type: type,
          url: url,
          method: 'GET',
          timestamp: new Date().toISOString(),
          requestBody: null,
          response: responseInfo,
          status: 'completed'
        });
        console.log('✅ 添加新的响应记录');
      }

      updateUI();
      updateDataDisplay();
    } catch (error) {
      console.error('处理响应数据失败:', error);
    }
  }

  // 处理请求错误
  function handleInterceptedError(type, url, error) {
    console.error('❌ 请求失败:', error);
    
    const requestIndex = recommendData.findIndex(item => 
      item.url === url && item.status === 'pending'
    );
    
    if (requestIndex !== -1) {
      recommendData[requestIndex].response = {
        type: type,
        url: url,
        status: 0,
        statusText: 'Error',
        timestamp: new Date().toISOString(),
        data: error.message
      };
      recommendData[requestIndex].status = 'error';
    }

    updateUI();
    updateDataDisplay();
  }


  // 拦截动态脚本加载
  function interceptDynamicScripts() {
    // 监听DOM变化，捕获动态添加的script标签
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        mutation.addedNodes.forEach(function(node) {
          if (node.nodeType === 1 && node.tagName === 'SCRIPT') { // Element node
            const src = node.src || node.getAttribute('src');
            if (src && isCbgApiUrl(src)) {
              console.log('🔍 拦截到动态添加的CBG API JSONP请求:', src);
              handleInterceptedRequest('jsonp', src, { method: 'GET' });
              
              // 解析URL获取回调函数名
              const urlObj = new URL(src);
              const callback = urlObj.searchParams.get('callback');
              console.log('🔍 动态JSONP回调函数名:', callback);
              //Request.JSONP.request_map.request_0
              if (callback) {
                // 拦截全局回调函数
                //Request.JSONP.request_map.request_0
               const callbackPath = 'Request.JSONP.request_map.request_0'.split('.')
                let originalCallback = window
                callbackPath.forEach((path,index) => {
                  originalCallback = originalCallback[path];
                });
                console.log('🔍 动态原始回调函数:', originalCallback);
                
                window[callback] = function(data) {
                  console.log('📥 拦截到动态JSONP响应数据:', data);
                  console.log('📥 动态JSONP响应数据类型:', typeof data);
                  console.log('📥 动态JSONP响应数据内容:', JSON.stringify(data, null, 2));
                  handleInterceptedResponse('jsonp', src, data);
                  
                  // 调用原始回调函数
                  if (originalCallback) {
                    console.log('📥 调用动态原始回调函数');
                    originalCallback(data);
                  }
                };
              }
              
              // 监听script加载完成
              node.addEventListener('load', function() {
                console.log('📥 动态JSONP请求加载完成:', src);
              });
              
              node.addEventListener('error', function() {
                console.error('❌ 动态JSONP请求失败:', src);
                handleInterceptedError('jsonp', src, new Error('JSONP请求失败'));
              });
            }
          }
        });
      });
    });
    
    observer.observe(document.documentElement, {
      childList: true,
      subtree: true
    });
  }

  // 更新UI
  function updateUI() {
    const indicator = document.getElementById('cbg-listener-indicator');
    const count = document.getElementById('data-count');
    
    if (indicator && count) {
      count.textContent = `(${recommendData.length})`;
    }
  }

  // 更新数据显示
  function updateDataDisplay() {
    const container = document.getElementById('cbg-data-display');
    if (!container) return;

    if (recommendData.length === 0) {
      container.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">暂无数据</p>';
      return;
    }

    let html = '';
    recommendData.forEach((item, index) => {
      const statusColor = item.status === 'completed' ? '#4CAF50' : 
                         item.status === 'error' ? '#f44336' : '#ff9800';
      
      html += `
        <div style="
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          padding: 15px;
          margin: 10px 0;
          background: white;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        ">
          <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
          ">
            <div style="font-weight: bold; color: #333;">
              请求 #${index + 1} - ${item.type.toUpperCase()} ${item.method}
            </div>
            <div style="
              padding: 2px 8px;
              border-radius: 12px;
              font-size: 11px;
              background: ${statusColor};
              color: white;
            ">
              ${item.status}
            </div>
          </div>
          
          <div style="
            font-size: 12px;
            color: #666;
            margin: 5px 0;
            word-break: break-all;
            background: #f5f5f5;
            padding: 8px;
            border-radius: 3px;
          ">
            <strong>URL:</strong> ${item.url}
          </div>
          
          <div style="
            font-size: 12px;
            color: #666;
            margin: 5px 0;
          ">
            <strong>时间:</strong> ${new Date(item.timestamp).toLocaleString()}
          </div>
          
          ${item.response ? `
            <div style="
              background: #e8f5e8;
              border-left: 3px solid #4CAF50;
              padding: 10px;
              margin: 10px 0;
              font-family: monospace;
              font-size: 11px;
              white-space: pre-wrap;
              max-height: 300px;
              overflow-y: auto;
              border-radius: 3px;
            ">
              <strong>响应数据:</strong><br>
              ${JSON.stringify(item.response.data || item.response, null, 2)}
            </div>
          ` : ''}
        </div>
      `;
    });

    container.innerHTML = html;
  }

  // 创建UI
  function createUI() {
    if (document.getElementById('cbg-listener-indicator')) return;
    if (!document.body) return;

    // 创建监听状态指示器
    const indicator = document.createElement('div');
    indicator.id = 'cbg-listener-indicator';
    indicator.innerHTML = `
      <div style="
        position: fixed;
        top: 10px;
        right: 10px;
        background: #4CAF50;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 10000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        display: block;
        cursor: pointer;
        font-family: Arial, sans-serif;
      ">
        <span>🔍 监听中...</span>
        <span id="data-count" style="margin-left: 8px;">(0)</span>
      </div>
    `;
    document.body.appendChild(indicator);

    // 创建数据显示面板
    const dataPanel = document.createElement('div');
    dataPanel.id = 'cbg-data-panel';
    dataPanel.innerHTML = `
      <div style="
        position: fixed;
        top: 50px;
        right: 10px;
        width: 500px;
        max-height: 600px;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        font-family: Arial, sans-serif;
        display: none;
      ">
        <div style="
          padding: 15px;
          border-bottom: 1px solid #eee;
          background: #f8f9fa;
          border-radius: 8px 8px 0 0;
          display: flex;
          justify-content: space-between;
          align-items: center;
        ">
          <h3 style="margin: 0; font-size: 14px; color: #333;">CBG API 监听结果</h3>
          <div>
            <button id="clear-data-btn" style="
              background: #f44336;
              color: white;
              border: none;
              padding: 4px 8px;
              border-radius: 3px;
              font-size: 11px;
              cursor: pointer;
              margin-right: 8px;
            ">清空</button>
            <button id="close-panel-btn" style="
              background: #666;
              color: white;
              border: none;
              padding: 4px 8px;
              border-radius: 3px;
              font-size: 11px;
              cursor: pointer;
            ">关闭</button>
          </div>
        </div>
        <div id="cbg-data-display" style="
          padding: 15px;
          max-height: 500px;
          overflow-y: auto;
        ">
          <p style="text-align: center; color: #666; padding: 20px;">暂无数据</p>
        </div>
      </div>
    `;
    document.body.appendChild(dataPanel);

    // 添加事件监听
    const indicatorElement = document.getElementById('cbg-listener-indicator');
    const dataPanelElement = document.getElementById('cbg-data-panel');
    const clearBtn = document.getElementById('clear-data-btn');
    const closeBtn = document.getElementById('close-panel-btn');

    if (indicatorElement) {
      indicatorElement.addEventListener('click', function() {
        if (dataPanelElement.style.display === 'none') {
          dataPanelElement.style.display = 'block';
          updateDataDisplay();
        } else {
          dataPanelElement.style.display = 'none';
        }
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener('click', function() {
        recommendData = [];
        updateUI();
        updateDataDisplay();
      });
    }

    if (closeBtn) {
      closeBtn.addEventListener('click', function() {
        dataPanelElement.style.display = 'none';
      });
    }
  }

  // 启动监听
  function startListening() {
    if (isListening) return;
    
    isListening = true;
    interceptDynamicScripts();
  }

  // 立即启动监听
  startListening();

  // 等待DOM加载完成后创建UI
  function waitForDOM() {
    if (document.body) {
      createUI();
    } else if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', createUI);
    } else {
      const observer = new MutationObserver(() => {
        if (document.body) {
          observer.disconnect();
          createUI();
        }
      });
      observer.observe(document.documentElement, {
        childList: true,
        subtree: true
      });
    }
  }

  // 等待DOM
  waitForDOM();

  // 监听消息
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    switch (message.action) {
      case 'getRecommendData':
        sendResponse({ success: true, data: recommendData });
        break;
      case 'clearRecommendData':
        recommendData = [];
        updateUI();
        updateDataDisplay();
        sendResponse({ success: true });
        break;
    }
  });

})();