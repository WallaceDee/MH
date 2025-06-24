# Flask后端架构重构文档

## 🏗️ 重构前后对比

### 重构前问题
- ❌ 单文件 `web_interface.py` (708行)
- ❌ 所有API混在一起
- ❌ 无分层架构
- ❌ 响应格式不统一
- ❌ 无版本控制

### 重构后优势
- ✅ 模块化蓝图架构
- ✅ MVC分层设计
- ✅ 统一响应格式
- ✅ 版本控制 (v1)
- ✅ 易于扩展和维护

## 📁 新项目结构

```
src/
├── app/                              # Flask应用目录
│   ├── __init__.py                   # 应用工厂
│   ├── blueprints/                   # 蓝图目录
│   │   └── api/
│   │       └── v1/                   # API版本1
│   │           ├── __init__.py       # v1蓝图注册
│   │           ├── spider.py         # 爬虫API
│   │           ├── character.py      # 角色API
│   │           ├── equipment.py      # 装备API
│   │           └── system.py         # 系统API
│   ├── controllers/                  # 控制器层
│   │   ├── spider_controller.py     # 爬虫控制器
│   │   ├── character_controller.py  # 角色控制器
│   │   ├── equipment_controller.py  # 装备控制器
│   │   └── system_controller.py     # 系统控制器
│   ├── services/                     # 服务层
│   │   ├── spider_service.py        # 爬虫服务
│   │   ├── character_service.py     # 角色服务
│   │   ├── equipment_service.py     # 装备服务
│   │   └── system_service.py        # 系统服务
│   └── utils/                        # 工具类
│       ├── response.py               # 响应工具
│       ├── logger.py                 # 日志工具
│       └── validator.py              # 验证工具
├── app.py                            # 新的应用启动文件
└── web_interface.py                  # 原文件(可以删除)
```

## 🔄 API路由映射

### 原来的路由
```
/api/status                    → 获取状态
/api/start_basic_spider        → 启动基础爬虫
/api/start_proxy_spider        → 启动代理爬虫
/api/manage_proxies            → 管理代理
/api/files                     → 文件列表
/api/download/<filename>       → 下载文件
```

### 重构后的路由
```
/api/v1/spider/status          → 获取爬虫状态
/api/v1/spider/basic/start     → 启动基础爬虫
/api/v1/spider/proxy/start     → 启动代理爬虫
/api/v1/spider/proxies/manage  → 管理代理
/api/v1/system/files           → 文件列表
/api/v1/system/files/<filename>/download → 下载文件
/api/v1/characters             → 角色API
/api/v1/equipments             → 装备API
```

## 🎯 架构优势

### 1. **模块化设计**
- 每个功能模块独立
- 易于团队协作开发
- 便于单元测试

### 2. **分层架构**
- **Controller**: 处理HTTP请求
- **Service**: 业务逻辑处理
- **Model**: 数据访问层

### 3. **统一响应格式**
```python
{
    "code": 200,
    "data": {},
    "message": "success",
    "timestamp": 1234567890
}
```

### 4. **错误处理**
- 全局错误处理器
- 统一错误格式
- 详细日志记录

### 5. **版本控制**
- API版本化管理
- 向下兼容性
- 渐进式升级

## 🚀 使用方法

### 启动新应用
```bash
python src/app.py
```

### 添加新API
1. 在对应蓝图中添加路由
2. 在控制器中添加处理逻辑
3. 在服务层中添加业务逻辑

### 扩展新版本
1. 创建 `api/v2` 目录
2. 注册新蓝图
3. 保持向下兼容

## 📝 迁移建议

1. **逐步迁移**: 保持原API运行，逐步切换到新API
2. **测试验证**: 确保所有功能正常工作
3. **前端适配**: 更新前端API调用地址
4. **文档更新**: 更新API文档

这个架构设计遵循了Flask最佳实践，为项目的长期维护和扩展奠定了良好基础。 