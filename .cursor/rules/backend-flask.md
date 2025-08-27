# Flask 后端API开发规则

## Flask 应用架构规范

### 项目结构标准
```
src/
├── app/                              # Flask应用目录
│   ├── __init__.py                   # 应用工厂函数
│   ├── blueprints/                   # 蓝图目录
│   │   └── api/
│   │       └── v1/                   # API版本控制
│   │           ├── __init__.py       # 蓝图注册
│   │           ├── spider.py         # 功能模块蓝图
│   │           ├── role.py      # 角色API
│   │           ├── equipment.py      # 装备API
│   │           └── system.py         # 系统API
│   ├── controllers/                  # 控制器层
│   │   ├── spider_controller.py     # 处理HTTP请求
│   │   └── ...                      # 其他控制器
│   ├── services/                     # 服务层
│   │   ├── spider_service.py        # 业务逻辑处理
│   │   └── ...                      # 其他服务
│   └── utils/                        # 工具类
│       ├── response.py               # 统一响应工具
│       ├── logger.py                 # 日志配置
│       └── validator.py              # 数据验证
└── app.py                            # 应用启动文件
```

### 应用工厂模式
```python
# src/app/__init__.py
def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 配置CORS
    CORS(app)
    
    # 设置日志
    setup_logging(app)
    
    # 注册蓝图
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    
    # 注册错误处理器
    register_error_handlers(app)
    
    return app
```

## RESTful API 设计规范

### URL设计原则
- 使用HTTP动词: GET, POST, PUT, DELETE
- URL命名使用复数形式
- 版本控制: `/api/v1/`
- 资源嵌套不超过3层

### 路由组织
```python
# 模块化路由设计
/api/v1/spider/status          → 获取爬虫状态
/api/v1/spider/basic/start     → 启动基础爬虫
/api/v1/spider/proxy/start     → 启动代理爬虫
/api/v1/system/files           → 文件列表
/api/v1/roles             → 角色资源
/api/v1/equipments             → 装备资源
```

## 统一响应格式

### 成功响应
```python
{
    "code": 200,          # 业务状态码
    "data": {},           # 数据内容
    "message": "success", # 响应消息
    "timestamp": 1234567890
}
```

### 错误响应
```python
{
    "code": 400,          # 错误状态码
    "data": None,         # 错误时为null
    "message": "错误信息",  # 错误描述
    "timestamp": 1234567890
}
```

### 分页响应
```python
{
    "code": 200,
    "data": {
        "items": [],      # 数据列表
        "total": 100,     # 总数量
        "page": 1,        # 当前页
        "page_size": 10,  # 每页大小
        "total_pages": 10 # 总页数
    },
    "message": "success",
    "timestamp": 1234567890
}
```

## 分层架构设计

### Controller层职责
- 处理HTTP请求和响应
- 参数验证和格式化
- 调用Service层处理业务逻辑
- 返回统一格式响应

```python
@spider_bp.route('/basic/start', methods=['POST'])
def start_basic_spider():
    """启动基础爬虫"""
    try:
        data = request.json or {}
        result = controller.start_basic_spider(
            max_pages=data.get('pages', 5),
            export_excel=data.get('export_excel', True),
            export_json=data.get('export_json', True)
        )
        return success_response(data=result, message="爬虫已启动")
    except Exception as e:
        return error_response(f"启动爬虫失败: {str(e)}")
```

### Service层职责
- 核心业务逻辑处理
- 数据处理和转换
- 调用外部服务或API
- 事务管理

```python
class SpiderService:
    def run_basic_spider(self, max_pages, export_excel, export_json):
        """运行基础爬虫"""
        try:
            # 业务逻辑处理
            spider = CBGSpider()
            spider.crawl_all_pages(max_pages=max_pages)
            # 返回处理结果
        except Exception as e:
            logger.error(f"基础爬虫出错: {e}")
            raise
```

## 错误处理规范

### 全局错误处理器
```python
def register_error_handlers(app):
    """注册全局错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return error_response("请求参数错误", code=400, http_code=400)
    
    @app.errorhandler(404)
    def not_found(error):
        return error_response("资源不存在", code=404, http_code=404)
    
    @app.errorhandler(500)
    def internal_error(error):
        return error_response("服务器内部错误", code=500, http_code=500)
```

### 异常处理原则
- 使用try-except包装所有业务逻辑
- 返回友好的错误信息
- 记录详细的错误日志
- HTTP状态码要准确

## 蓝图组织规范

### 蓝图结构
```python
# 主蓝图注册
api_v1_bp = Blueprint('api_v1', __name__)
api_v1_bp.register_blueprint(spider_bp, url_prefix='/spider')
api_v1_bp.register_blueprint(role_bp, url_prefix='/roles')

# 功能模块蓝图
spider_bp = Blueprint('spider', __name__)
@spider_bp.route('/status', methods=['GET'])
def get_status():
    # 路由处理逻辑
```

### 模块划分原则
- 按业务功能划分蓝图
- 每个蓝图独立管理
- 路由前缀清晰明确
- 便于版本控制和扩展

## 数据验证

### 参数验证
- 必须验证所有输入参数
- 使用marshmallow进行数据序列化
- 敏感数据要过滤或加密
- SQL注入防护

### 请求数据处理
```python
def start_basic_spider():
    data = request.json or {}
    max_pages = data.get('pages', 5)  # 默认值
    if not isinstance(max_pages, int) or max_pages <= 0:
        return error_response("pages参数必须是正整数")
```

## 日志规范

### 日志配置
```python
def setup_logging(app):
    """配置应用日志"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件和控制台处理器
    file_handler = logging.FileHandler('app.log', encoding='utf-8')
    console_handler = logging.StreamHandler()
    
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
```

### 日志记录规范
```python
logger = logging.getLogger(__name__)

# 记录关键操作
logger.info(f"启动基础爬虫，最大页数: {max_pages}")
logger.error(f"基础爬虫出错: {e}")
logger.warning(f"任务已在运行中: {task_id}")
```

## CORS配置

### 跨域设置
```python
from flask_cors import CORS

# 基础CORS配置
CORS(app)

# 生产环境配置
CORS(app, origins=['http://localhost:8080'])
```

## 性能优化

### 代码优化
- 数据库查询优化
- 使用缓存机制
- 分页查询大数据集
- 异步处理耗时任务

### 并发处理
```python
import threading

def start_background_task():
    """后台任务处理"""
    thread = threading.Thread(target=task_function)
    thread.start()
    return {"task_id": id(thread)}
```

## 版本控制

### API版本管理
- 使用URL路径版本控制: `/api/v1/`
- 保持向下兼容性
- 新版本增量更新
- 文档同步更新

### 版本升级策略
```python
# v1版本
api_v1_bp = Blueprint('api_v1', __name__)

# v2版本(未来)
api_v2_bp = Blueprint('api_v2', __name__)
```

当你帮助我开发Flask后端时，请严格遵循以上架构规范和最佳实践，确保代码的可维护性和扩展性。 