# Chrome扩展DevTools面板 - Vue版本

## 概述

这是一个基于Vue 2.6.14 + Element UI的Chrome扩展DevTools面板，用于CBG爬虫助手。

## 文件结构

```
src/chrome-extensions/
├── DevToolsPanel.vue          # Vue组件
├── devtools-panel.js          # 入口文件
├── devtools-panel.html        # HTML模板
└── README.md                  # 说明文档
```

## 构建命令

### 开发模式
```bash
npm run dev:devtools-panel
```
- 监听文件变化，自动重新构建
- 生成source map用于调试

### 生产模式
```bash
npm run build:devtools-panel
```
- 构建生产版本
- 自动复制到Chrome扩展目录
- 代码压缩优化

## 功能特性

### 🎯 统计信息
- Vue状态监控
- 版本信息显示
- 运行时间统计
- 测试次数记录

### 🔧 功能测试
- Vue功能测试
- 数据绑定测试
- 方法调用测试
- 日志管理

### 📊 数据展示
- 实时数据更新
- 列表数据展示
- 状态监控

### 📝 日志系统
- 实时日志显示
- 分类日志记录
- 自动滚动
- 日志清理

## 使用方法

1. **构建面板**：
   ```bash
   npm run build:devtools-panel
   ```

2. **重新加载扩展**：
   - 打开 `chrome://extensions/`
   - 找到CBG爬虫助手扩展
   - 点击"重新加载"

3. **使用面板**：
   - 按F12打开开发者工具
   - 切换到"Vue项目版本"标签页
   - 享受完整的Vue + Element UI体验

## 技术栈

- **Vue 2.6.14** - 前端框架
- **Element UI 2.15.14** - UI组件库
- **Webpack 5** - 模块打包工具
- **Babel** - JavaScript编译器

## 开发说明

- 组件使用Vue 2语法
- 支持Element UI组件
- 响应式数据绑定
- 完整的生命周期管理
- 错误处理和日志记录
