// 后台脚本
console.log('CBG爬虫助手后台脚本已加载');

// 监听来自DevTools的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('后台收到消息:', request);
  
  switch (request.action) {
    case 'getCookies':
      handleGetCookies(sendResponse);
      return true; // 保持消息通道开放
      
    case 'updateRecommendData':
      // 转发数据到所有DevTools面板
      chrome.runtime.sendMessage({
        action: 'updateRecommendData',
        data: request.data
      });
      break;
      
    case 'showDebuggerWarning':
      // 转发警告到所有DevTools面板
      chrome.runtime.sendMessage({
        action: 'showDebuggerWarning',
        message: request.message
      });
      break;
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

// 监听标签页更新
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && tab.url.includes('cbg.163.com')) {
    console.log('检测到CBG页面加载完成:', tab.url);
  }
});

// 监听标签页激活
chrome.tabs.onActivated.addListener((activeInfo) => {
  chrome.tabs.get(activeInfo.tabId, (tab) => {
    if (tab.url && tab.url.includes('cbg.163.com')) {
      console.log('激活CBG页面:', tab.url);
    }
  });
});
