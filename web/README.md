# CBG爬虫系统

## 🎯 项目概述

这是一个梦幻西游CBG爬虫系统，采用Flask后端 + Vue.js前端的分离架构，包含数据爬取、处理、分析和展示功能。同时支持Chrome浏览器插件开发。

## 🏗️ 架构特点

### 多入口构建系统
- **Vue Web应用**: 完整的Web管理系统
- **Chrome插件**: 浏览器扩展，支持数据采集和分析
- **统一技术栈**: Vue2 + Element UI + Vue CLI

### 分层架构设计
- **展示层**: Vue.js + Element UI前端
- **接口层**: Flask RESTful API  
- **业务层**: Service类处理业务逻辑
- **数据层**: SQLite数据库 + 文件存储

## 🚀 快速开始

### 环境要求
- Node.js 14+
- Python 3.8+
- Chrome浏览器（用于插件测试）

### 安装依赖
```bash
# 前端依赖
cd web
npm install

# 后端依赖
cd ../src
pip install -r requirements.txt
```

### 开发模式
```bash
# 启动Vue开发服务器
npm run serve

# 启动后端服务
cd ../src
python app.py
```

## 🔧 构建命令

### Vue Web应用
```bash
# 开发构建
npm run build

# 生产构建
npm run build --mode production
```

### Chrome插件
```bash
# 构建插件（包含Vue应用）
npm run build:extension

# 清理后重新构建
npm run build:extension:clean
```

### 完整构建
```bash
# 构建所有项目
npm run build:all
```

## 📱 Chrome插件功能

### 弹窗 (Popup)
- 显示爬虫运行状态
- 快速控制爬虫启动/停止
- 快速设置采集参数
- 快速访问数据面板和设置

### 数据面板 (Dashboard)
- 数据统计概览
- 数据筛选和搜索
- 数据表格展示
- 数据导出功能

### 设置页面 (Settings)
- 爬虫参数配置
- 数据存储设置
- 界面主题设置
- 高级功能配置

## 🛠️ 开发指南

### 添加新的Chrome插件页面

1. **创建Vue组件**
```bash
mkdir src/entries/newpage
touch src/entries/newpage/NewPageApp.vue
touch src/entries/newpage.js
```

2. **创建HTML模板**
```bash
touch public/newpage.html
```

3. **更新配置**
- 在`vue.config.js`中添加新页面配置
- 在`manifest.json`中添加资源访问权限

### 组件开发规范
- 使用Vue2 + Element UI
- 组件名使用PascalCase
- 样式使用scoped
- 遵循Vue官方风格指南

## 📁 项目结构

```
web/
├── src/
│   ├── entries/                 # Chrome插件入口文件
│   │   ├── popup/              # 弹窗组件
│   │   ├── dashboard/          # 数据面板组件
│   │   └── settings/           # 设置页面组件
│   ├── components/             # 公共组件
│   ├── views/                  # 页面组件
│   ├── api/                    # API接口
│   └── main.js                 # 主应用入口
├── public/
│   ├── manifest.json           # Chrome插件配置
│   ├── popup.html              # 弹窗HTML模板
│   ├── dashboard.html          # 数据面板HTML模板
│   ├── settings.html           # 设置页面HTML模板
│   ├── background.js            # 后台脚本
│   ├── content.js               # 内容脚本
│   ├── content.css              # 内容脚本样式
│   └── icons/                  # 插件图标
├── vue.config.js               # Vue CLI配置（多入口）
├── build-chrome.js             # Chrome插件构建脚本
└── package.json                # 项目配置
```

## 🔍 调试技巧

### Chrome插件调试
- **弹窗**: 右键点击插件图标 → "检查弹出内容"
- **后台脚本**: `chrome://extensions/` → 找到插件 → "检查视图：背景页"
- **内容脚本**: 在目标页面按F12 → 查看Console

### 安装插件
1. 构建插件：`npm run build:extension`
2. 打开Chrome → `chrome://extensions/`
3. 开启"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择 `dist-chrome` 目录

## 📚 技术栈

### 前端
- **Vue.js 2.6**: 渐进式JavaScript框架
- **Element UI**: 基于Vue的组件库
- **Vue CLI**: Vue.js开发工具链
- **Vuex**: 状态管理
- **Vue Router**: 路由管理

### 构建工具
- **Webpack**: 模块打包器
- **Babel**: JavaScript编译器
- **ESLint**: 代码质量检查
- **多入口配置**: 支持Vue应用和Chrome插件同时构建

### Chrome插件
- **Manifest V3**: 最新的插件规范
- **Service Worker**: 后台脚本
- **Content Scripts**: 内容脚本
- **Chrome APIs**: 浏览器扩展API

## 🐛 常见问题

### 构建问题
- **ESLint错误**: 检查`.eslintrc.js`配置
- **依赖缺失**: 运行`npm install`
- **权限问题**: 检查文件路径和权限

### 插件问题
- **无法加载**: 检查`manifest.json`配置
- **功能异常**: 查看浏览器控制台错误
- **权限不足**: 检查`permissions`配置

## 📝 更新日志

### v1.0.0
- 初始版本
- 支持多入口构建
- 完整的Chrome插件功能
- Vue2 + Element UI界面
- 网络监听和数据采集功能

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🔗 相关链接

- [Vue.js官方文档](https://vuejs.org/)
- [Element UI组件库](https://element.eleme.cn/)
- [Chrome Extension开发文档](https://developer.chrome.com/docs/extensions/)
- [Vue CLI配置指南](https://cli.vuejs.org/config/) 