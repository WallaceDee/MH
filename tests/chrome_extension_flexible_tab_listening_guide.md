# Chrome扩展灵活标签页监听功能说明

## 功能概述

优化后的Chrome扩展后台脚本现在支持灵活监听当前激活的窗口，不再局限于监听固定的标签页。当用户在不同CBG标签页之间切换时，扩展会自动切换到新激活的标签页进行监听。

## 主要改进

### 1. 多标签页跟踪
- **`activeCbgTabs`**: 跟踪所有CBG标签页的ID
- **`currentTabId`**: 当前正在监听的标签页ID
- **自动管理**: 当标签页打开/关闭时自动更新跟踪列表

### 2. 智能切换机制
- **标签页激活监听**: 当用户切换到CBG标签页时自动开始监听
- **标签页更新监听**: 当CBG页面加载完成时自动开始监听
- **标签页关闭监听**: 当监听的标签页关闭时自动停止监听

### 3. 灵活的状态管理
- **自动断开**: 切换到非CBG页面时自动停止监听
- **无缝切换**: 在不同CBG标签页间切换时无缝转移监听
- **状态通知**: 实时通知side panel连接状态变化

## 核心功能

### 标签页切换逻辑
```javascript
// 切换到指定标签页进行监听
async switchToTab(tabId) {
  // 如果已经在监听该标签页，无需重复操作
  if (this.isListening && this.currentTabId === tabId) {
    return;
  }
  
  // 停止当前监听
  if (this.isListening) {
    await this.stopListening();
  }
  
  // 开始监听新标签页
  this.currentTabId = tabId;
  await this.startListening();
}
```

### 事件监听器
```javascript
// 监听标签页激活
chrome.tabs.onActivated.addListener((activeInfo) => {
  if (tab.url && tab.url.includes('cbg.163.com')) {
    this.activeCbgTabs.add(activeInfo.tabId);
    this.switchToTab(activeInfo.tabId);
  }
});

// 监听标签页更新
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url.includes('cbg.163.com')) {
    this.activeCbgTabs.add(tabId);
    if (!this.isListening || this.currentTabId === tabId) {
      this.switchToTab(tabId);
    }
  }
});

// 监听标签页关闭
chrome.tabs.onRemoved.addListener((tabId) => {
  this.activeCbgTabs.delete(tabId);
  if (this.currentTabId === tabId) {
    this.stopListening();
  }
});
```

## 新增API接口

### 1. 获取CBG标签页信息
```javascript
// 发送消息
chrome.runtime.sendMessage({ action: 'getCbgTabsInfo' });

// 响应格式
{
  success: true,
  data: {
    currentTabId: 123,           // 当前监听的标签页ID
    isListening: true,           // 是否正在监听
    activeCbgTabs: [123, 456],   // 所有CBG标签页ID列表
    totalData: 10                // 当前数据总量
  }
}
```

### 2. 手动切换标签页
```javascript
// 发送消息
chrome.runtime.sendMessage({ 
  action: 'switchToTab', 
  tabId: 123 
});

// 响应格式
{
  success: true,
  message: "已切换到标签页 123"
}
```

## 使用场景

### 场景1: 多标签页浏览
1. 用户打开多个CBG标签页
2. 扩展自动跟踪所有CBG标签页
3. 用户切换到任意CBG标签页时，扩展自动开始监听该标签页

### 场景2: 标签页关闭处理
1. 用户关闭当前监听的标签页
2. 扩展自动停止监听
3. 如果还有其他CBG标签页，等待用户切换到其他标签页

### 场景3: 非CBG页面切换
1. 用户从CBG页面切换到其他网站
2. 扩展自动停止监听
3. 用户切换回CBG页面时，扩展自动恢复监听

## 测试方法

### 1. 使用测试页面
打开 `chrome_extension_tab_switching_test.html` 进行功能测试：
- 检查扩展连接状态
- 查看所有CBG标签页
- 手动切换监听标签页
- 清空推荐数据

### 2. 手动测试步骤
1. 打开多个CBG标签页
2. 观察控制台日志，确认标签页跟踪正常
3. 在不同标签页间切换，确认监听自动切换
4. 关闭标签页，确认监听自动停止

## 日志输出示例

```
标签页激活事件: {tabId: 123}
激活的标签页信息: {tabId: 123, url: "https://xyq.cbg.163.com/...", status: "complete"}
激活CBG页面: https://xyq.cbg.163.com/...
切换到标签页进行监听: 123
停止当前监听，切换到新标签页
✅ 已断开DevTools Protocol连接
开始连接DevTools Protocol到标签页 123
✅ DevTools Protocol已连接
✅ 开始监听网络请求
```

## 注意事项

1. **调试器冲突**: 如果Chrome开发者工具已打开，可能会与扩展的DevTools Protocol冲突
2. **权限要求**: 需要 `debugger` 权限才能使用DevTools Protocol
3. **性能考虑**: 同时只能监听一个标签页，避免资源浪费
4. **错误处理**: 包含完整的错误处理和重试机制

## 兼容性

- Chrome 88+ (支持side panel)
- 支持Manifest V3
- 兼容现有的side panel界面
