// Side Panel 事件处理脚本
console.log('梦幻灵瞳 Side Panel 脚本已加载');

// 全局变量
let recommendData = [];
let devtoolsConnected = false;
let connectionStatus = '检查中...';

// 立即初始化消息监听器（不等待DOM加载）
console.log('Side Panel 脚本开始加载');
initMessageListener();

// 等待DOM加载完成后进行其他初始化
document.addEventListener('DOMContentLoaded', function() {
  console.log('Side Panel DOM 已加载');
  checkConnectionStatus();
  
  // 测试消息接收
  setTimeout(() => {
    testMessageReceiving();
  }, 2000);
});

// 初始化消息监听器
function initMessageListener() {
  // 监听来自background script的消息
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Side Panel 收到消息:', request);
    
    switch (request.action) {
      case 'updateRecommendData':
        handleUpdateRecommendData(request.data);
        break;
      case 'devtoolsConnected':
        handleDevtoolsConnected(request.message);
        break;
      case 'showDebuggerWarning':
        handleDebuggerWarning(request.message);
        break;
      case 'clearRecommendData':
        handleClearRecommendData();
        break;
    }
    
    // 返回true保持消息通道开放
    return true;
  });
}

// 处理推荐数据更新
function handleUpdateRecommendData(data) {
  console.log('收到推荐数据更新:', data);
  recommendData = data || [];
  updateUI();
}

// 处理DevTools连接成功
function handleDevtoolsConnected(message) {
  console.log('DevTools连接成功:', message);
  devtoolsConnected = true;
  connectionStatus = '已连接';
  updateConnectionStatus();
}

// 处理调试器警告
function handleDebuggerWarning(message) {
  console.log('调试器警告:', message);
  connectionStatus = '调试器冲突';
  devtoolsConnected = false;
  updateConnectionStatus();
  showNotification(message, 'warning');
}

// 处理清空数据
function handleClearRecommendData() {
  console.log('清空推荐数据');
  recommendData = [];
  updateUI();
}

// 检查连接状态
function checkConnectionStatus() {
  // 发送ping消息检查连接
  chrome.runtime.sendMessage({ action: 'ping' }, (response) => {
    if (chrome.runtime.lastError) {
      console.error('连接检查失败:', chrome.runtime.lastError);
      connectionStatus = '连接失败';
      devtoolsConnected = false;
    } else if (response && response.success) {
      console.log('连接检查成功');
      connectionStatus = '已连接';
      devtoolsConnected = true;
      // 获取当前推荐数据
      getRecommendData();
    } else {
      connectionStatus = '未连接';
      devtoolsConnected = false;
    }
    updateConnectionStatus();
  });
}

// 获取推荐数据
function getRecommendData() {
  chrome.runtime.sendMessage({ action: 'getRecommendData' }, (response) => {
    if (response && response.success) {
      recommendData = response.data || [];
      updateUI();
    }
  });
}

// 更新UI
function updateUI() {
  // 这里需要根据实际的Vue组件结构来更新UI
  // 由于panel.html中使用了Vue组件，我们需要通过Vue实例来更新数据
  if (window.vueApp && window.vueApp.$data) {
    window.vueApp.recommendData = recommendData;
    window.vueApp.devtoolsConnected = devtoolsConnected;
    window.vueApp.connectionStatus = connectionStatus;
  }
  
  // 如果Vue应用还没有加载，我们可以直接操作DOM
  updateDataDisplay();
  
  // 通知Vue组件数据已更新
  if (window.sidePanelMethods && window.sidePanelMethods.vueComponent) {
    window.sidePanelMethods.vueComponent.syncDataWithSidePanel();
  }
}

// 更新连接状态显示
function updateConnectionStatus() {
  if (window.vueApp && window.vueApp.$data) {
    window.vueApp.devtoolsConnected = devtoolsConnected;
    window.vueApp.connectionStatus = connectionStatus;
  }
}

// 更新数据显示（备用方案）
function updateDataDisplay() {
  const dataSection = document.querySelector('.data-section');
  if (!dataSection) return;
  
  if (recommendData.length === 0) {
    dataSection.innerHTML = '<div class="empty-state">暂无数据，请访问梦幻西游藏宝阁页面</div>';
  } else {
    // 这里可以添加更复杂的数据显示逻辑
    console.log('当前推荐数据:', recommendData);
  }
}

// 显示通知
function showNotification(message, type = 'info') {
  // 这里可以集成Element UI的通知组件
  console.log(`${type.toUpperCase()}: ${message}`);
}

// 页面控制方法
function nextPage() {
  if (window.sidePanelMethods && window.sidePanelMethods.vueComponent) {
    // 如果Vue组件已加载，使用Vue组件的方法
    window.sidePanelMethods.vueComponent.nextPage();
  } else {
    // 否则直接发送消息到background script
    chrome.runtime.sendMessage({ action: 'nextPage' });
  }
}

function prevPage() {
  if (window.sidePanelMethods && window.sidePanelMethods.vueComponent) {
    // 如果Vue组件已加载，使用Vue组件的方法
    window.sidePanelMethods.vueComponent.prevPage();
  } else {
    // 否则直接发送消息到background script
    chrome.runtime.sendMessage({ action: 'prevPage' });
  }
}

function getPageInfo() {
  if (window.sidePanelMethods && window.sidePanelMethods.vueComponent) {
    // 如果Vue组件已加载，使用Vue组件的方法
    window.sidePanelMethods.vueComponent.getPageInfo();
  } else {
    // 否则直接发送消息到background script
    chrome.runtime.sendMessage({ action: 'getPageInfo' });
  }
}

function reconnectDevTools() {
  connectionStatus = '重连中...';
  devtoolsConnected = false;
  updateConnectionStatus();
  checkConnectionStatus();
}

function clearData() {
  if (window.sidePanelMethods && window.sidePanelMethods.vueComponent) {
    // 如果Vue组件已加载，使用Vue组件的方法
    window.sidePanelMethods.vueComponent.clearData();
  } else {
    // 否则直接发送消息到background script
    chrome.runtime.sendMessage({ action: 'clearRecommendData' });
  }
}

// 将方法暴露到全局作用域，供Vue组件调用
window.sidePanelMethods = {
  nextPage,
  prevPage,
  getPageInfo,
  reconnectDevTools,
  clearData,
  checkConnectionStatus
};

// 测试消息接收
function testMessageReceiving() {
  console.log('🧪 开始测试消息接收...');
  
  // 发送测试消息到background script
  chrome.runtime.sendMessage({ action: 'ping' }, (response) => {
    if (chrome.runtime.lastError) {
      console.error('❌ 测试消息发送失败:', chrome.runtime.lastError);
    } else {
      console.log('✅ 测试消息发送成功，响应:', response);
    }
  });
  
  // 请求获取推荐数据
  chrome.runtime.sendMessage({ action: 'getRecommendData' }, (response) => {
    if (chrome.runtime.lastError) {
      console.error('❌ 获取推荐数据失败:', chrome.runtime.lastError);
    } else {
      console.log('✅ 获取推荐数据成功，响应:', response);
    }
  });
}

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
  console.log('Side Panel 即将卸载');
});
