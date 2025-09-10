# Side Panel 调试指南

## 问题排查步骤

### 1. 检查扩展是否正确加载
1. 打开 Chrome 浏览器
2. 访问 `chrome://extensions/`
3. 确保"梦幻灵瞳"扩展已启用
4. 检查是否有错误信息

### 2. 检查 Side Panel 是否显示
1. 访问 [梦幻西游藏宝阁](https://cbg.163.com)
2. 查看右侧是否出现 Side Panel
3. 如果没有，尝试点击扩展图标

### 3. 检查控制台日志

#### Background Script 日志
1. 在 `chrome://extensions/` 页面
2. 找到"梦幻灵瞳"扩展
3. 点击"检查视图" → "Service Worker"
4. 查看控制台日志，应该看到：
   - "CBG爬虫助手后台脚本已加载"
   - "DevTools监听器已绑定"
   - "检测到CBG页面加载完成"
   - "startListening 被调用"
   - "DevTools Protocol已连接"

#### Side Panel 日志
1. 打开 Side Panel
2. 右键点击 Side Panel 内容
3. 选择"检查"
4. 查看控制台日志，应该看到：
   - "梦幻灵瞳 Side Panel 脚本已加载"
   - "Side Panel DOM 已加载"
   - "Side Panel 收到消息"
   - "🧪 开始测试消息接收..."

### 4. 常见问题解决

#### 问题1: Side Panel 不显示
**原因**: 缺少 `sidePanel` 权限
**解决**: 确保 manifest.json 中有 `"sidePanel"` 权限

#### 问题2: 消息无法接收
**原因**: 消息监听器配置问题
**解决**: 检查 side-panel.js 中的消息监听器是否正确返回 `true`

#### 问题3: DevTools Protocol 连接失败
**原因**: 其他调试器占用
**解决**: 关闭 Chrome 开发者工具，重新加载页面

#### 问题4: 网络请求无法监听
**原因**: URL 匹配规则问题
**解决**: 检查 `isCbgApiUrl` 方法的匹配规则

### 5. 测试步骤

1. **重新加载扩展**:
   - 在 `chrome://extensions/` 页面
   - 点击扩展的"重新加载"按钮

2. **清除缓存**:
   - 按 F12 打开开发者工具
   - 右键点击刷新按钮
   - 选择"清空缓存并硬性重新加载"

3. **检查网络请求**:
   - 在 CBG 页面按 F12
   - 切换到 Network 标签
   - 刷新页面
   - 查看是否有 CBG 相关的 API 请求

### 6. 调试命令

在 Side Panel 控制台中运行以下命令进行测试：

```javascript
// 测试消息发送
chrome.runtime.sendMessage({ action: 'ping' }, (response) => {
  console.log('Ping 响应:', response);
});

// 获取推荐数据
chrome.runtime.sendMessage({ action: 'getRecommendData' }, (response) => {
  console.log('推荐数据:', response);
});

// 清空数据
chrome.runtime.sendMessage({ action: 'clearRecommendData' });
```

### 7. 预期行为

正常情况下，你应该看到：

1. **扩展加载**: 控制台显示"CBG爬虫助手后台脚本已加载"
2. **Side Panel 打开**: 访问 CBG 页面时自动打开 Side Panel
3. **DevTools 连接**: 控制台显示"DevTools Protocol已连接"
4. **网络监听**: 控制台显示"收到网络请求事件"
5. **数据更新**: Side Panel 显示推荐数据

如果任何一步出现问题，请检查对应的日志信息并按照上述步骤进行排查。
