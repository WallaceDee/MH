# 🌐 代理IP轮换系统使用指南

## 📖 概述

代理IP轮换系统是一套完整的解决方案，用于提升爬虫的性能和稳定性，避免IP被封锁。系统包含三个核心模块：

1. **`proxy_rotation_system.py`** - 代理IP轮换核心系统
2. **`proxy_source_manager.py`** - 免费代理IP源管理器  
3. **`cbg_crawler_with_proxy.py`** - 完整的CBG爬虫集成示例

## 🚀 快速开始

### 方法一：使用免费代理（推荐新手）

```bash
# 1. 自动获取免费代理IP
python3 proxy_source_manager.py

# 2. 测试代理可用性
python3 proxy_rotation_system.py

# 3. 运行集成爬虫
python3 cbg_crawler_with_proxy.py
```

### 方法二：使用付费代理

1. 创建 `proxy_list.txt` 文件，添加你的代理IP：
```
# 支持多种格式
http://127.0.0.1:8080
https://username:password@proxy.example.com:3128
socks5://127.0.0.1:1080
192.168.1.100:8080:username:password
```

2. 运行测试：
```bash
python3 proxy_rotation_system.py
```

## 📋 详细功能介绍

### 1. 代理IP轮换管理器 (`ProxyRotationManager`)

#### 核心功能
- ✅ **多格式代理支持**: HTTP/HTTPS/SOCKS5
- ✅ **智能轮换策略**: 基于成功率和响应时间
- ✅ **自动故障检测**: 自动标记失败代理
- ✅ **统计分析**: 详细的使用统计和性能监控
- ✅ **线程安全**: 支持多线程并发使用

#### 支持的代理格式
```python
# 简单格式
"127.0.0.1:8080"

# 带协议
"http://127.0.0.1:8080"
"https://proxy.example.com:3128" 
"socks5://127.0.0.1:1080"

# 带认证
"http://username:password@proxy.example.com:8080"

# 四段格式
"127.0.0.1:8080:username:password"
```

#### 代理选择策略
```python
# 策略1: 新代理随机选择
# 策略2: 基于成功率(70%) + 响应时间(30%)的权重选择
score = success_rate * 0.7 + time_weight * 0.3
```

### 2. 免费代理源管理器 (`ProxySourceManager`)

#### 支持的免费代理源
- 🌐 **free-proxy-list.net** - 高匿名代理
- 🌐 **proxy-list.download** - HTTP/HTTPS代理
- 🌐 **pubproxy.com** - API接口代理
- 🌐 **gimmeproxy.com** - 单个代理API

#### 自动获取流程
```python
# 1. 从多个源并行获取
# 2. 去重处理
# 3. 保存到proxy_list.txt
# 4. 按来源统计
```

### 3. CBG爬虫集成 (`CBGProxyCrawler`)

#### 核心特性
- 🔄 **自动重试机制**: 代理失败时自动切换
- 📊 **性能监控**: 记录每个代理的响应时间
- 🚫 **反爬虫检测**: 智能识别被封锁的代理
- ⚡ **并行爬取**: 支持多线程并发

## 🛠 高级配置

### 自定义代理选择策略

```python
class CustomProxyManager(ProxyRotationManager):
    def _select_best_proxy(self, proxies):
        # 自定义选择逻辑
        # 例如：优先选择特定地区的代理
        china_proxies = [p for p in proxies if p.get('country') == 'China']
        if china_proxies:
            return random.choice(china_proxies)
        return super()._select_best_proxy(proxies)
```

### 配置并发爬取

```python
# 调整最大并发数
proxy_manager = ProxyRotationManager(max_workers=5)

# 设置请求间隔
crawler.parallel_crawl_with_proxy(1, 50, delay_range=(2, 5))
```

### 代理池健康监控

```python
# 定期清理失败代理
def cleanup_failed_proxies():
    active_count = len([p for p in proxy_manager.proxy_pool if p['status'] == 'active'])
    if active_count < 3:  # 可用代理少于3个时
        # 重新获取代理
        source_manager = ProxySourceManager()
        new_proxies = source_manager.get_proxies_from_all_sources()
        # 更新代理池...
```

## ⚡ 性能优化建议

### 1. 代理池管理
```python
# 定期更新代理池（每4-6小时）
# 保持至少10-20个可用代理
# 及时清理失败率>50%的代理
```

### 2. 请求策略
```python
# 合理设置请求间隔
delay_range = (1, 3)  # 1-3秒随机间隔

# 错峰爬取（避开网站高峰期）
best_hours = [2, 3, 4, 5, 6]  # 凌晨时段

# 分批处理大量数据
batch_size = 10  # 每批10页
```

### 3. 反反爬虫
```python
# 随机User-Agent
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...',
    # ... 更多UA
]

# 模拟真实用户行为
time.sleep(random.uniform(1, 5))  # 随机停留时间
```

## 🔧 故障排除

### 常见问题

#### 1. 所有代理都不可用
```bash
# 解决方案：
python3 proxy_source_manager.py  # 重新获取免费代理
# 或手动添加付费代理到proxy_list.txt
```

#### 2. 代理响应慢
```python
# 调整超时设置
proxy_manager.test_proxy(proxy, timeout=15)  # 增加到15秒

# 过滤慢速代理
fast_proxies = [p for p in proxies if p['response_time'] < 5.0]
```

#### 3. 被目标网站检测
```python
# 增加请求间隔
time.sleep(random.uniform(3, 8))

# 减少并发数
max_workers = 2

# 使用高匿名代理
anonymous_proxies = [p for p in proxies if p.get('anonymity') == 'high anonymity']
```

### 调试技巧

```python
# 启用详细日志
logging.getLogger().setLevel(logging.DEBUG)

# 查看代理统计
proxy_manager.show_proxy_status()

# 测试单个代理
proxy_manager.test_proxy(proxy, test_url="http://httpbin.org/ip")
```

## 📊 监控与统计

### 实时监控指标
- 📈 **成功率**: 每个代理的请求成功率
- ⏱️ **响应时间**: 平均响应时间统计
- 🔄 **轮换频次**: 代理使用频率分布
- ❌ **失败原因**: 超时、连接错误、HTTP状态码统计

### 性能报告
```python
# 生成性能报告
stats = proxy_manager.get_proxy_stats()
print(f"总代理数: {stats['total_proxies']}")
print(f"可用代理: {stats['active_proxies']}")
print(f"平均响应时间: {avg_response_time:.2f}秒")
```

## 🚨 安全注意事项

### 1. 代理安全
- ❌ 避免使用来源不明的代理
- ✅ 定期更换代理IP
- ✅ 监控代理的网络流量
- ✅ 使用HTTPS代理处理敏感数据

### 2. 爬虫合规
- ✅ 遵守robots.txt规则
- ✅ 设置合理的请求频率
- ✅ 避免对目标服务器造成负载压力
- ✅ 尊重网站的服务条款

### 3. 数据保护
- ✅ 加密存储代理凭据
- ✅ 定期清理日志文件
- ✅ 避免在代码中硬编码敏感信息

## 📈 扩展应用

### 1. 其他网站爬虫
```python
# 轻松适配到其他网站
class CustomWebCrawler(CBGProxyCrawler):
    def __init__(self, proxy_manager, target_url):
        super().__init__(proxy_manager)
        self.target_url = target_url
    
    def fetch_page_data(self, page):
        # 自定义页面获取逻辑
        pass
```

### 2. API请求代理
```python
# 为API请求添加代理支持
def api_request_with_proxy(url, data, proxy_manager):
    proxy = proxy_manager.get_next_proxy()
    session = create_session_with_proxy(proxy)
    return session.post(url, json=data)
```

### 3. 定时任务集成
```python
# 结合crontab实现定时爬取
# 0 */6 * * * cd /path/to/project && python3 cbg_crawler_with_proxy.py
```

## 🎯 最佳实践总结

1. **代理池维护**：保持足够的代理数量，定期更新
2. **智能重试**：失败时自动切换代理，避免无谓的重试
3. **性能监控**：密切关注成功率和响应时间
4. **请求控制**：合理控制并发数和请求频率
5. **错误处理**：完善的异常处理和日志记录
6. **安全合规**：遵守相关法律法规和网站规则

---

## 🆘 技术支持

如果遇到问题，请检查：
1. 网络连接是否正常
2. 代理IP是否有效
3. 目标网站是否有反爬虫措施
4. Python依赖包是否完整安装

系统设计灵活，可根据具体需求进行定制和扩展。 