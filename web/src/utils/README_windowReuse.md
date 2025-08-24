# 窗口复用管理器使用说明

## 功能概述

窗口复用管理器（WindowReuseManager）是一个用于管理相似窗口复用的工具，可以避免重复打开相同功能的窗口，提升用户体验。

## 主要特性

- **智能窗口检测**: 自动检测已存在的兼容窗口
- **窗口聚焦**: 自动聚焦到已存在的窗口
- **参数同步**: 支持更新已存在窗口的参数
- **跨标签页通信**: 使用 BroadcastChannel API 实现
- **自动清理**: 窗口关闭时自动清理资源

## 使用方法

### 1. 在组件中使用

```javascript
import windowReuseManager from '@/utils/windowReuseManager'

export default {
  methods: {
    async openSimilarWindow() {
      const params = {
        action: 'similar_equip',
        equip_type: 'normal',
        equip_name: '武器名称'
      }
      
      // 检查是否有可复用的窗口
      const existingWindow = await windowReuseManager.checkForExistingWindow(params, 1000)
      
      if (existingWindow) {
        // 聚焦到已存在的窗口
        windowReuseManager.requestFocus(existingWindow.windowId)
        
        // 更新窗口参数（如果需要）
        windowReuseManager.requestUpdateParams(existingWindow.windowId, params)
        return
      }
      
      // 创建新窗口
      this.createNewWindow(params)
    }
  }
}
```

### 2. 在目标页面中自动设置

在需要支持复用的页面（如 auto-params 页面）中，只需要导入管理器即可：

```javascript
// 在 auto-params 页面的 main.js 或组件中
import windowReuseManager from '@/utils/windowReuseManager'

// 管理器会自动设置并监听消息
// 无需额外代码
```

## API 参考

### 方法

#### `checkForExistingWindow(params, timeout)`
检查是否有可复用的窗口

- **params**: 窗口参数对象
- **timeout**: 超时时间（毫秒），默认1000ms
- **返回**: Promise，解析为窗口信息或 false

#### `requestFocus(windowId)`
请求聚焦指定窗口

- **windowId**: 目标窗口ID

#### `requestUpdateParams(windowId, params)`
请求更新指定窗口的参数

- **windowId**: 目标窗口ID
- **params**: 新的参数对象

### 事件

#### `params-updated`
当窗口参数被更新时触发

```javascript
window.addEventListener('params-updated', (event) => {
  const { params, timestamp } = event.detail
  console.log('参数已更新:', params)
  // 重新加载数据或更新UI
})
```

## 兼容性检查

管理器会自动检查以下条件来确定窗口是否兼容：

1. **URL路径**: 必须是 `/auto-params` 页面
2. **action参数**: 必须完全匹配
3. **equip_type参数**: 如果指定了，必须匹配

## 配置选项

可以通过修改 `WindowReuseManager` 类来自定义：

- **channelName**: 广播通道名称
- **超时时间**: 默认1秒
- **兼容性检查逻辑**: 可以添加更多匹配条件

## 注意事项

1. **浏览器支持**: 需要支持 BroadcastChannel API 的现代浏览器
2. **同源策略**: 只能在同源页面间通信
3. **性能考虑**: 超时时间不宜设置过长，避免用户等待
4. **错误处理**: 管理器会自动降级到创建新窗口

## 故障排除

### 常见问题

1. **窗口无法复用**
   - 检查参数是否匹配
   - 确认目标页面已导入管理器
   - 查看控制台是否有错误信息

2. **聚焦失败**
   - 检查目标窗口是否仍然存在
   - 确认浏览器允许窗口聚焦

3. **参数更新失败**
   - 检查参数格式是否正确
   - 确认目标窗口支持参数更新

### 调试模式

在控制台中可以看到详细的日志信息：

```javascript
// 查看管理器状态
console.log(windowReuseManager)

// 手动检查窗口
windowReuseManager.checkForExistingWindow({
  action: 'similar_equip',
  equip_type: 'normal'
})
```

## 扩展功能

可以基于现有框架添加更多功能：

- **窗口分组**: 按功能类型分组管理
- **历史记录**: 记录窗口使用历史
- **智能布局**: 自动调整窗口位置避免重叠
- **快捷键支持**: 添加快捷键切换窗口 