# Cursor 规则文件总览

## 📋 规则文件列表

### 🏗️ **architecture-guide.md** - 项目架构指导
- 整体架构原则和设计模式
- 前后端分离架构规范
- 数据流和安全架构设计
- 性能优化和扩展策略

### 🔧 **backend-flask.md** - Flask后端开发规则
- Flask应用架构规范 (应用工厂、蓝图组织)
- RESTful API设计规范
- 统一响应格式 (成功、错误、分页)
- 分层架构 (Controller/Service/Model)
- 错误处理和日志规范
- 版本控制和性能优化

### 🎨 **frontend-vue.md** - Vue前端开发规则
- Vue 2 + Element UI开发规范
- 组件开发最佳实践
- API请求统一封装规范
- 模板和样式规范
- 数据管理和性能优化

### 🔌 **api-usage-guide.md** - API使用指南
- 统一API封装架构和原则
- 响应拦截器处理模式
- 错误处理和加载状态管理
- 前后端数据格式规范
- 从axios迁移到统一API的指导

### 🕷️ **crawler-development.md** - 爬虫开发规则
- 爬虫开发最佳实践
- 反爬虫应对策略
- 数据处理和存储规范
- 性能优化和错误处理

### 🧪 **testing.md** - 测试规则
- 完整测试策略 (单元/集成/E2E)
- 前端、后端、爬虫测试规范
- 覆盖率要求和CI/CD集成

### 📊 **data-processing.md** - 数据处理规则
- 数据清洗和验证规范
- 文件处理和存储优化
- 性能监控和日志记录

## 🎯 规则使用指南

### 规则层级结构
```
项目根目录/
├── .cursorrules              # 📌 通用项目规则 (已删除，使用专门规则)
└── .cursor/rules/            # 📁 专门模块规则
    ├── README.md             # 📖 规则总览 (本文件)
    ├── architecture-guide.md # 🏗️ 架构指导
    ├── backend-flask.md      # 🔧 后端专用
    ├── frontend-vue.md       # 🎨 前端专用
    ├── api-usage-guide.md    # 🔌 API使用指南
    ├── crawler-development.md # 🕷️ 爬虫专用
    ├── testing.md           # 🧪 测试专用
    └── data-processing.md   # 📊 数据处理专用
```

### 规则应用场景

#### 🔧 **Flask后端开发时**
Cursor AI会参考：
- `architecture-guide.md` - 整体架构设计
- `backend-flask.md` - Flask具体规范
- `testing.md` - 后端测试要求
- `data-processing.md` - 数据处理规范

#### 🎨 **Vue前端开发时**
Cursor AI会参考：
- `architecture-guide.md` - 前端架构设计
- `frontend-vue.md` - Vue开发规范
- `api-usage-guide.md` - API使用和封装规范 ⭐
- `testing.md` - 前端测试要求

#### 🔌 **API接口开发/调用时**
Cursor AI会参考：
- `api-usage-guide.md` - 统一API封装使用规范 ⭐
- `architecture-guide.md` - API层架构设计
- `backend-flask.md` - 后端API设计规范
- `frontend-vue.md` - 前端API调用规范

#### 🕷️ **爬虫模块开发时**
Cursor AI会参考：
- `crawler-development.md` - 爬虫专用规则
- `data-processing.md` - 数据处理规范
- `testing.md` - 爬虫测试规范

## 🚀 规则优势

### 1. **模块化管理**
- 每个开发领域有专门的详细规则
- 规则更新不会影响其他模块
- 便于团队不同角色专注自己的规则

### 2. **精准指导**
- 针对性强，开发建议更准确
- 结合具体技术栈给出详细指导
- 包含实际代码示例和最佳实践

### 3. **可扩展性**
- 可以根据项目发展添加新的规则文件
- 支持版本控制和规则演进
- 便于维护和更新

### 4. **一致性保证**
- 统一的代码风格和架构规范
- 标准化的API设计和响应格式
- 规范的错误处理和日志记录
- **统一的API调用方式** (使用this.$api，禁用直接axios) ⭐

## 📝 规则维护

### 更新原则
1. **向前兼容**: 新规则不能破坏现有代码
2. **渐进改进**: 逐步优化和完善规则
3. **实践验证**: 规则要经过实际项目验证
4. **文档同步**: 规则更新要同步更新文档

### 扩展方法
- 添加新技术栈的专门规则文件
- 在现有规则文件中增加新的规范
- 创建特定场景的专用规则
- 根据项目反馈优化规则内容

## 💡 使用建议

1. **开发前**: 先阅读相关规则文件，了解规范要求
2. **开发中**: 让Cursor AI根据规则提供代码建议
3. **代码审查**: 使用规则作为Review标准
4. **团队协作**: 确保所有成员都遵循相同规则
5. **API开发**: 严格遵循统一API封装，禁止组件直接使用axios ⭐

这套规则体系将确保CBG爬虫项目的代码质量、架构一致性和长期可维护性！🎊 