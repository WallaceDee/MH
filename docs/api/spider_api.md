# CBG爬虫 API 使用说明

基于 `run.py` 的功能，提供完整的爬虫 API 服务。

## 接口概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/spider/status` | 获取任务状态 |
| GET | `/api/v1/spider/config` | 获取爬虫配置信息 |
| POST | `/api/v1/spider/basic/start` | 启动基础爬虫（通用） |
| POST | `/api/v1/spider/role/start` | 启动角色爬虫 |
| POST | `/api/v1/spider/equip/start` | 启动装备爬虫 |
| POST | `/api/v1/spider/pet/start` | 启动召唤兽爬虫 |
| POST | `/api/v1/spider/proxy/start` | 启动代理爬虫 |
| POST | `/api/v1/spider/proxy/manage` | 管理代理IP |
| POST | `/api/v1/spider/test/run` | 运行测试 |
| POST | `/api/v1/spider/task/stop` | 停止当前任务 |
| GET | `/api/v1/spider/logs` | 获取任务日志 |
| GET | `/api/v1/spider/logs/stream` | 流式获取实时日志 |

## 详细接口说明

### 1. 获取任务状态

**GET** `/api/v1/spider/status`

获取当前正在运行的任务状态。

**响应示例：**
```json
{
    "code": 200,
    "data": {
        "status": "running",           // idle, running, completed, error
        "message": "正在爬取角色数据...",
        "progress": 30                // 0-100
    },
    "message": "获取状态成功",
    "timestamp": 1234567890
}
```

### 2. 获取爬虫配置信息

**GET** `/api/v1/spider/config`

获取可用的爬虫类型和配置选项。

**响应示例：**
```json
{
    "code": 200,
    "data": {
        "spider_types": [
            {"value": "role", "label": "角色数据", "description": "爬取角色交易数据"},
            {"value": "equip", "label": "装备数据", "description": "爬取装备交易数据"},
            {"value": "pet", "label": "召唤兽数据", "description": "爬取召唤兽交易数据"}
        ],
        "equip_types": [
            {"value": "normal", "label": "普通装备", "description": "武器、防具等普通装备"},
            {"value": "lingshi", "label": "灵饰", "description": "灵饰装备"},
            {"value": "pet", "label": "召唤兽装备", "description": "召唤兽装备"}
        ],
        "default_config": {
            "pages": 5,
            "delay_min": 5.0,
            "delay_max": 8.0,
            "use_browser": true
        }
    },
    "message": "获取配置成功",
    "timestamp": 1234567890
}
```

### 3. 启动基础爬虫（通用接口）

**POST** `/api/v1/spider/basic/start`

支持所有类型的爬虫启动，通过参数控制爬虫类型。

**请求参数：**
```json
{
    "spider_type": "role",        // 必需: role/equip/pet
    "equip_type": "normal",       // 可选: normal/lingshi/pet (仅spider_type=equip时需要)
    "max_pages": 5,               // 可选: 爬取页数，默认5
    "use_browser": true,          // 可选: 是否使用浏览器，默认true
    "delay_min": 5.0,             // 可选: 最小延迟秒数，默认5.0
    "delay_max": 8.0              // 可选: 最大延迟秒数，默认8.0
}
```

**响应示例：**
```json
{
    "code": 200,
    "data": {
        "task_id": 140234567890,
        "config": {
            "spider_type": "role",
            "equip_type": null,
            "max_pages": 5,
            "use_browser": true,
            "delay_range": [5.0, 8.0]
        }
    },
    "message": "爬虫已启动",
    "timestamp": 1234567890
}
```

### 4. 启动角色爬虫

**POST** `/api/v1/spider/role/start`

专门用于爬取角色数据的接口。

**请求参数：**
```json
{
    "max_pages": 10,              // 可选: 爬取页数，默认5
    "use_browser": true,          // 可选: 是否使用浏览器，默认true
    "delay_min": 5.0,             // 可选: 最小延迟秒数，默认5.0
    "delay_max": 8.0              // 可选: 最大延迟秒数，默认8.0
}
```

### 5. 启动装备爬虫

**POST** `/api/v1/spider/equip/start`

专门用于爬取装备数据的接口。

**请求参数：**
```json
{
    "equip_type": "lingshi",      // 必需: normal/lingshi/pet
    "max_pages": 5,               // 可选: 爬取页数，默认5
    "use_browser": true,          // 可选: 是否使用浏览器，默认true
    "delay_min": 5.0,             // 可选: 最小延迟秒数，默认5.0
    "delay_max": 8.0              // 可选: 最大延迟秒数，默认8.0
}
```

**装备类型说明：**
- `normal`: 普通装备（武器、防具等）
- `lingshi`: 灵饰装备
- `pet`: 召唤兽装备

### 6. 启动召唤兽爬虫

**POST** `/api/v1/spider/pet/start`

专门用于爬取召唤兽数据的接口。

**请求参数：**
```json
{
    "max_pages": 8,               // 可选: 爬取页数，默认5
    "use_browser": true,          // 可选: 是否使用浏览器，默认true
    "delay_min": 5.0,             // 可选: 最小延迟秒数，默认5.0
    "delay_max": 8.0              // 可选: 最大延迟秒数，默认8.0
}
```

**召唤兽爬虫特色功能：**
- 支持完整的召唤兽属性：等级、气血、伤害、防御、速度、法伤、法防等
- 支持召唤兽筛选条件：召唤兽类型、技能数量、成长值、资质范围等
- 支持浏览器手动设置复杂搜索条件
- 数据按月分割存储：cbg_pets_YYYYMM.db

### 7. 启动代理爬虫

**POST** `/api/v1/spider/proxy/start`

使用代理IP进行爬取。

**请求参数：**
```json
{
    "max_pages": 10               // 可选: 爬取页数，默认5
}
```

### 8. 管理代理IP

**POST** `/api/v1/spider/proxy/manage`

获取和管理代理IP池。

**请求参数：** 无

### 9. 运行测试

**POST** `/api/v1/spider/test/run`

运行爬虫系统测试。

**请求参数：** 无

### 10. 停止当前任务

**POST** `/api/v1/spider/task/stop`

停止正在运行的任务。

**请求参数：** 无

**响应示例：**
```json
{
    "code": 200,
    "data": {
        "message": "任务停止请求已发送（subprocess可能仍在运行）"
    },
    "message": "停止任务请求已发送",
    "timestamp": 1234567890
}
```

## 前端集成示例

### JavaScript/Vue.js 示例

```javascript
// 获取爬虫配置
const getSpiderConfig = async () => {
    const response = await this.$api.spider.getConfig()
    return response.data
}

// 启动角色爬虫
const startRoleSpider = async () => {
    const params = {
        max_pages: 10,
        use_browser: true,
        delay_min: 5.0,
        delay_max: 8.0
    }
    const response = await this.$api.spider.startRoleSpider(params)
    if (response.code === 200) {
        console.log('角色爬虫已启动:', response.data.task_id)
    }
}

// 启动装备爬虫
const startEquipSpider = async () => {
    const params = {
        equip_type: 'lingshi',
        max_pages: 5,
        use_browser: true
    }
    const response = await this.$api.spider.startEquipSpider(params)
    if (response.code === 200) {
        console.log('装备爬虫已启动:', response.data.task_id)
    }
}

// 监控任务状态
const monitorTaskStatus = () => {
    const interval = setInterval(async () => {
        const response = await this.$api.spider.getStatus()
        if (response.code === 200) {
            const status = response.data
            console.log(`任务状态: ${status.status}, 进度: ${status.progress}%`)
            
            if (status.status === 'completed' || status.status === 'error') {
                clearInterval(interval)
                console.log('任务完成:', status.message)
            }
        }
    }, 2000) // 每2秒检查一次状态
}
```

### Python 客户端示例

```python
import requests
import time

class CBGSpiderClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
    
    def get_status(self):
        """获取任务状态"""
        response = requests.get(f'{self.base_url}/api/v1/spider/status')
        return response.json()
    
    def start_role_spider(self, max_pages=5):
        """启动角色爬虫"""
        data = {'max_pages': max_pages}
        response = requests.post(f'{self.base_url}/api/v1/spider/role/start', json=data)
        return response.json()
    
    def start_equip_spider(self, equip_type='normal', max_pages=5):
        """启动装备爬虫"""
        data = {
            'equip_type': equip_type,
            'max_pages': max_pages
        }
        response = requests.post(f'{self.base_url}/api/v1/spider/equip/start', json=data)
        return response.json()
    
    def monitor_task(self, interval=2):
        """监控任务执行"""
        while True:
            status = self.get_status()
            if status['code'] == 200:
                task_status = status['data']['status']
                progress = status['data']['progress']
                message = status['data']['message']
                
                print(f"状态: {task_status}, 进度: {progress}%, 消息: {message}")
                
                if task_status in ['completed', 'error']:
                    break
            
            time.sleep(interval)

# 使用示例
client = CBGSpiderClient()

# 启动角色爬虫
result = client.start_role_spider(max_pages=10)
print("启动结果:", result)

# 监控任务
client.monitor_task()
```

## 错误处理

所有接口都返回统一的错误格式：

```json
{
    "code": 400,
    "data": null,
    "message": "具体错误信息",
    "timestamp": 1234567890
}
```

常见错误：
- `400`: 参数错误
- `500`: 服务器内部错误
- 已有任务在运行中
- 爬虫执行失败

## 注意事项

1. **任务并发限制**: 同时只能运行一个爬虫任务
2. **浏览器模式**: 使用浏览器模式时，需要手动设置搜索参数
3. **延迟设置**: 合理设置延迟避免被网站反爬
4. **数据存储**: 爬取的数据会自动保存到 `data/` 目录下对应的数据库文件
5. **任务停止**: 停止任务只能停止Python线程，子进程可能仍在运行

## 对应的 run.py 命令

API调用等价的命令行操作：

| API调用 | 等价命令 |
|---------|----------|
| `POST /api/v1/spider/role/start` | `python run.py basic --type role --pages 10` |
| `POST /api/v1/spider/equip/start` (normal) | `python run.py basic --type equip --equip-type normal` |
| `POST /api/v1/spider/equip/start` (lingshi) | `python run.py basic --type equip --equip-type lingshi --use-browser` |
| `POST /api/v1/spider/pet/start` | `python run.py basic --type pet --pages 8` |
| `POST /api/v1/spider/proxy/start` | `python run.py proxy --pages 10` |
| `POST /api/v1/spider/proxy/manage` | `python run.py proxy-manager` |
| `POST /api/v1/spider/test/run` | `python run.py test` |

### 11. 获取任务日志

**GET** `/api/v1/spider/logs`

获取爬虫任务的日志信息。

**请求参数：**
```
?lines=100&type=current
```

- `lines`: 返回的日志行数，默认100
- `type`: 日志类型，可选值：
  - `current`: 当前任务的日志（默认）
  - `recent`: 最近的日志文件

**响应示例：**
```json
{
    "code": 200,
    "data": {
        "logs": [
            "2025-07-08 11:41:38,222 - CBGSpider_2518535832464 - INFO - 日志文件路径: output\\202507\\cbg_spider_20250708_114138.log",
            "2025-07-08 11:41:38,223 - CBGSpider_2518535832464 - INFO - 成功从config/cookies.txt文件加载Cookie",
            "2025-07-08 11:41:38,224 - CBGSpider_2518535832464 - INFO - Cookie已添加到请求头"
        ],
        "log_file": "cbg_spider_20250708_114138.log",
        "total_lines": 150,
        "recent_lines": 100,
        "last_modified": "2025-07-08 11:45:30"
    },
    "message": "获取日志成功",
    "timestamp": 1234567890
}
```

### 12. 流式获取实时日志

**GET** `/api/v1/spider/logs/stream`

使用Server-Sent Events (SSE) 实时获取日志更新。

**请求参数：** 无

**响应格式：**
```
data: 2025-07-08 11:41:38,222 - CBGSpider_2518535832464 - INFO - 正在爬取第1页...

data: 2025-07-08 11:41:42,156 - CBGSpider_2518535832464 - INFO - 第1页爬取完成，获取到15条数据

data: 2025-07-08 11:41:45,789 - CBGSpider_2518535832464 - INFO - 正在爬取第2页...
```

**前端使用示例：**
```javascript
// 创建EventSource连接
const eventSource = new EventSource('/api/v1/spider/logs/stream')

// 监听日志消息
eventSource.onmessage = (event) => {
    if (event.data) {
        console.log('新日志:', event.data)
        // 将日志添加到界面显示
        this.logs.push(event.data)
    }
}

// 监听错误
eventSource.onerror = (error) => {
    console.error('日志流错误:', error)
    eventSource.close()
}

// 关闭连接
// eventSource.close()
```

## 日志监控功能

### 日志级别颜色标识

- **ERROR**: 红色 - 错误信息
- **WARNING**: 橙色 - 警告信息  
- **INFO**: 蓝色 - 信息日志
- **DEBUG**: 灰色 - 调试信息

### 日志文件位置

日志文件存储在 `output/YYYYMM/` 目录下，按月份分类：
- `cbg_spider_YYYYMMDD_HHMMSS.log` - 角色爬虫日志
- `cbg_equip_spider_YYYYMMDD_HHMMSS.log` - 装备爬虫日志
- `cbg_pet_spider_YYYYMMDD_HHMMSS.log` - 召唤兽爬虫日志

### 实时监控建议

1. **启动任务时自动加载日志**: 任务启动后自动获取最新日志
2. **实时流监控**: 使用SSE实时获取日志更新
3. **日志过滤**: 支持按日志级别过滤显示
4. **日志搜索**: 支持关键词搜索日志内容
5. **日志导出**: 支持将日志导出为文件 