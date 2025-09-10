# 梦幻灵瞳 Chrome 扩展 - Side Panel 版本

## 概述

本扩展已从 DevTools 面板迁移到 Chrome Side Panel，提供更好的用户体验和更稳定的功能。

## 主要变更

### 1. 架构变更
- **移除**: DevTools 面板 (`devtools.html`, `devtools.js`)
- **新增**: Side Panel 支持 (`side-panel.js`)
- **修改**: `manifest.json` 配置，添加 `sidePanel` 权限
- **优化**: `background.js` 集成 DevTools Protocol 监听

### 2. 功能特性
- ✅ 自动检测 CBG 页面并打开 Side Panel
- ✅ 实时监听网络请求和响应
- ✅ 支持分页控制和数据获取
- ✅ 与 Vue.js 组件无缝集成
- ✅ 错误处理和重连机制

## 文件结构

```
chrome-extensions/
├── manifest.json          # 扩展配置文件
├── background.js          # 后台脚本（集成DevTools监听）
├── panel.html            # Side Panel 页面
├── side-panel.js         # Side Panel 事件处理脚本
├── panel.js              # Vue.js 应用（webpack打包）
├── vendors.js            # 第三方库（webpack打包）
├── assets/               # 静态资源
├── libs/                 # 工具库
└── test-side-panel.html  # 测试页面
```

## 安装和使用

### 1. 安装扩展
1. 打开 Chrome 浏览器
2. 访问 `chrome://extensions/`
3. 启用"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择 `chrome-extensions` 文件夹

### 2. 使用扩展
1. 访问 [梦幻西游藏宝阁](https://cbg.163.com)
2. Side Panel 会自动打开
3. 在 Side Panel 中查看实时数据
4. 使用分页控制按钮浏览数据

### 3. 手动打开 Side Panel
- 点击扩展图标
- 或使用快捷键（如果配置了）

## 开发说明

### 1. 消息通信
扩展使用 Chrome Runtime API 进行消息通信：

```javascript
// 发送消息到后台脚本
chrome.runtime.sendMessage({ action: 'ping' }, (response) => {
  console.log('响应:', response);
});

// 监听来自后台脚本的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('收到消息:', request);
});
```

### 2. DevTools Protocol 集成
后台脚本集成了 DevTools Protocol 监听：

```javascript
// 连接调试器
await chrome.debugger.attach({ tabId: tabId }, '1.3');

// 启用网络监听
await chrome.debugger.sendCommand({ tabId: tabId }, 'Network.enable');

// 监听网络事件
chrome.debugger.onEvent.addListener((source, method, params) => {
  // 处理网络事件
});
```

### 3. Vue.js 集成
Side Panel 与 Vue.js 组件无缝集成：

```javascript
// 在 side-panel.js 中
if (window.vueApp && window.vueApp.$data) {
  window.vueApp.recommendData = recommendData;
  window.vueApp.devtoolsConnected = devtoolsConnected;
}

// 在 DevToolsPanel.vue 中
mounted() {
  window.vueApp = this;
  this.coordinateWithSidePanel();
}
```

## 测试

### 1. 使用测试页面
打开 `test-side-panel.html` 进行功能测试：

1. 检查扩展状态
2. 测试 Side Panel 功能
3. 测试消息通信
4. 测试 DevTools 连接
5. 测试网络监听

### 2. 手动测试
1. 访问 CBG 页面
2. 检查 Side Panel 是否自动打开
3. 验证数据监听是否正常
4. 测试分页控制功能

## 故障排除

### 1. Side Panel 不自动打开
- 检查 `manifest.json` 中的 `sidePanel` 权限
- 确认 `background.js` 中的事件监听器正常
- 查看控制台错误信息

### 2. 数据监听不工作
- 确认当前页面是 CBG 页面
- 检查 DevTools Protocol 连接状态
- 关闭其他调试器（如 Chrome DevTools）
- 查看后台脚本日志

### 3. 消息通信失败
- 检查扩展权限配置
- 确认消息格式正确
- 查看 `chrome.runtime.lastError` 信息

## 权限说明

```json
{
  "permissions": [
    "activeTab",      // 访问当前标签页
    "storage",        // 本地存储
    "debugger",       // DevTools Protocol
    "cookies",        // Cookie 访问
    "sidePanel"       // Side Panel 功能
  ],
  "host_permissions": [
    "https://*.163.com/*",
    "https://*.cbg.163.com/*"
  ]
}
```

## 更新日志

### v1.0.0 (Side Panel 版本)
- ✅ 迁移到 Side Panel 架构
- ✅ 集成 DevTools Protocol 监听
- ✅ 优化消息通信机制
- ✅ 添加错误处理和重连功能
- ✅ 完善测试和文档

## 技术支持

如有问题，请检查：
1. Chrome 版本是否支持 Side Panel（Chrome 114+）
2. 扩展权限是否正确配置
3. 控制台错误信息
4. 网络连接状态

---

**注意**: 本扩展需要 Chrome 114 或更高版本才能使用 Side Panel 功能。
