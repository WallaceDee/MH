# Cookie更新问题诊断和解决方案

## 问题描述
用户反馈Cookie没有更新，需要诊断和解决Cookie更新机制的问题。

## 可能的原因分析

### 1. URL监听问题
- **目标URL模式过于具体**: 之前使用了 `recommend_type=1` 参数，可能过于具体
- **URL变化事件未触发**: `framenavigated` 事件可能没有正确触发
- **URL匹配逻辑错误**: 字符串匹配可能有问题

### 2. 登录状态检测问题
- **语法错误**: 之前的 `current_url in 'https://...'` 语法不正确
- **登录页面检测不完整**: 可能遗漏了某些登录相关的URL

### 3. Cookie更新时机问题
- **异步更新失败**: `asyncio.create_task()` 可能没有正确执行
- **页面加载时机**: 更新时机可能过早或过晚

## 已实施的修复

### 1. 修复登录状态检测语法
```python
# 修复前（语法错误）
if current_url == "https://xyq.cbg.163.com/" or current_url == "https://xyq.cbg.163.com" or current_url in 'https://xyq.cbg.163.com/cgi-bin/show_login.py?act=show_login':

# 修复后（正确语法）
if (current_url == "https://xyq.cbg.163.com/" or 
    current_url == "https://xyq.cbg.163.com" or 
    'show_login.py' in current_url):
```

### 2. 添加调试日志
```python
# 添加URL变化监听调试
def url_changed(url):
    logger.info(f"页面URL变化: {url}")  # 新增调试日志
    if target_url_pattern in url:
        logger.info(f"检测到目标URL: {url}")
        asyncio.create_task(self._update_cookies_on_url_change())

# 添加当前URL检查调试
current_url = self.page.url
logger.info(f"当前页面URL: {current_url}")  # 新增调试日志
```

### 3. 简化目标URL模式
```python
# 使用更通用的模式
target_url_pattern = 'https://xyq.cbg.163.com/cgi-bin/query.py?act=recommend_search'
```

## 诊断步骤

### 1. 检查URL监听是否工作
运行程序后，观察日志中是否有：
- `页面URL变化: xxx` 日志
- `检测到目标URL: xxx` 日志

### 2. 检查登录状态检测
观察日志中是否有：
- `当前页面URL: xxx` 日志
- `检测到未登录状态` 或 `检测到已登录状态` 日志

### 3. 检查Cookie更新
观察日志中是否有：
- `检测到目标URL，开始更新Cookie...` 日志
- `Cookie已更新并保存到 xxx` 日志

## 测试方法

### 1. 使用测试脚本
运行 `tests/test_cookie_update.py` 进行详细测试：
```bash
python tests/test_cookie_update.py
```

### 2. 手动测试步骤
1. 启动收集器
2. 在浏览器中手动登录
3. 导航到目标页面
4. 观察日志输出
5. 检查 `config/cookies.txt` 文件是否更新

### 3. 检查文件更新
```bash
# 检查Cookie文件是否存在和更新
ls -la config/cookies.txt
cat config/cookies.txt
```

## 可能的解决方案

### 1. 如果URL监听不工作
```python
# 尝试使用其他事件监听
self.page.on('load', lambda: url_changed(self.page.url))
self.page.on('domcontentloaded', lambda: url_changed(self.page.url))
```

### 2. 如果异步更新失败
```python
# 改为同步更新
def url_changed(url):
    if target_url_pattern in url:
        logger.info(f"检测到目标URL: {url}")
        # 同步更新Cookie
        await self._update_cookies_on_url_change()
```

### 3. 如果URL模式不匹配
```python
# 使用更宽松的匹配
target_url_pattern = 'recommend_search'  # 只匹配关键词
```

## 调试建议

### 1. 启用详细日志
```python
logging.basicConfig(level=logging.DEBUG)
```

### 2. 添加更多调试点
```python
# 在关键位置添加调试日志
logger.debug(f"Cookie更新前检查: {await self.context.cookies()}")
logger.debug(f"Cookie更新后检查: {await self.context.cookies()}")
```

### 3. 检查文件权限
确保程序有权限写入 `config/cookies.txt` 文件。

## 预期结果

修复后应该看到：
1. URL变化时输出调试日志
2. 检测到目标URL时触发Cookie更新
3. Cookie文件成功更新
4. 登录信息成功保存

如果问题仍然存在，请提供详细的日志输出，以便进一步诊断。 