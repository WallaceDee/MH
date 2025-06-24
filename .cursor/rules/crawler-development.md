# 爬虫开发规则

## 爬虫开发最佳实践

### 基础规范
- 遵守robots.txt协议
- 设置合理的请求间隔(1-3秒)
- 使用随机User-Agent
- 实现请求重试机制

### 技术选择
- 静态页面: requests + BeautifulSoup
- 动态页面: Selenium 或 Playwright
- 大规模爬取: 考虑使用Scrapy框架
- API接口: 优先使用官方API

### 反爬虫应对
```python
# User-Agent池
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    # 更多UA...
]

# 代理IP支持
PROXIES = {
    'http': 'http://proxy:port',
    'https': 'https://proxy:port'
}

# 请求间隔
import time
time.sleep(random.uniform(1, 3))
```

### 数据处理
- 数据清洗和验证
- 去重处理
- 结构化存储
- 增量更新策略

### 错误处理
- 网络异常重试
- 解析错误跳过
- 详细日志记录
- 监控和报警

### 性能优化
- 多线程/协程并发
- 连接池复用
- 内存使用监控
- 断点续传机制

### 数据存储
- 支持多种格式: JSON, CSV, Excel
- 数据库存储优化
- 文件路径管理
- 定期备份机制 