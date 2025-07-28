# URL监听和Cookie更新优化总结

## 修改说明
根据用户要求，进一步优化了Cookie处理逻辑：
1. 去除Cookie验证检查，直接注入
2. 改为监听页面URL变化，只在检测到特定URL时更新Cookie
3. 不再一直等待，而是异步监听URL变化
4. 简化登录状态检查，通过URL判断登录状态

## 主要修改

### 1. 简化 `_wait_for_login` 方法

**修改前**：
- 使用 `wait_for_url` 等待页面跳转，有超时限制
- 复杂的超时处理和错误恢复逻辑
- 同步等待页面加载完成

**修改后**：
- 使用 `framenavigated` 事件监听URL变化
- 异步处理URL变化，不阻塞主流程
- 检测到目标URL时自动触发Cookie更新

### 修改后的代码

#### 1. 简化的登录状态检查

```python
async def _check_login_status(self):
    """检查登录状态 - 通过URL判断，如果跳转到首页则表示未登录"""
    try:
        current_url = self.page.url
        
        # 如果当前URL是首页，则表示未登录
        if current_url == "https://xyq.cbg.163.com/" or current_url == "https://xyq.cbg.163.com":
            logger.info("检测到未登录状态（页面在首页）")
            return {
                'isLoggedIn': False,
                'currentUrl': current_url,
                'message': '页面在首页，未登录'
            }
        else:
            logger.info(f"检测到已登录状态，当前URL: {current_url}")
            return {
                'isLoggedIn': True,
                'currentUrl': current_url,
                'message': '已登录'
            }
        
    except Exception as e:
        logger.error(f"检查登录状态失败: {e}")
        return {
            'isLoggedIn': False,
            'currentUrl': await self.page.url() if self.page else 'unknown',
            'message': str(e)
        }
```

#### 2. URL监听和Cookie更新

```python
async def _wait_for_login(self):
    """监听页面URL变化，检测到目标URL时更新Cookie"""
    try:
        target_url_pattern = 'https://xyq.cbg.163.com/cgi-bin/query.py?act=recommend_search'
        
        # 监听页面URL变化
        def url_changed(url):
            if target_url_pattern in url:
                logger.info(f"检测到目标URL: {url}")
                # 异步更新Cookie
                asyncio.create_task(self._update_cookies_on_url_change())
        
        # 设置URL变化监听
        self.page.on('framenavigated', lambda frame: url_changed(frame.url) if frame == self.page.main_frame else None)
        
        # 检查当前URL
        current_url = self.page.url
        if target_url_pattern in current_url:
            logger.info(f"当前页面已经是目标地址: {current_url}")
            await self._update_cookies_on_url_change()
        
        logger.info("URL监听已设置，等待页面跳转到目标地址...")

    except Exception as e:
        logger.error(f"设置URL监听失败: {e}")

async def _update_cookies_on_url_change(self):
    """URL变化时更新Cookie"""
    try:
        logger.info("检测到目标URL，开始更新Cookie...")
        
        # 等待页面基本加载
        await asyncio.sleep(2)
        
        # 更新Cookie
        await self._update_cookies()
        
        # 收集 window.LoginInfo 对象
        try:
            login_info = await self.page.evaluate("() => window.LoginInfo")
            if login_info:
                logger.info("成功获取到 window.LoginInfo 对象")
                await self._save_login_info(login_info)
            else:
                logger.warning("window.LoginInfo 对象为空或不存在")
        except Exception as e:
            logger.warning(f"获取 window.LoginInfo 失败: {e}")
            
    except Exception as e:
        logger.error(f"URL变化时更新Cookie失败: {e}")
```

## 核心改进

### 1. 事件驱动监听
- 使用 `framenavigated` 事件监听页面导航
- 只在主框架导航时触发，避免子框架干扰
- 异步处理URL变化，不阻塞主流程

### 2. 智能URL检测
- 检测目标URL模式：`https://xyq.cbg.163.com/cgi-bin/query.py?act=recommend_search`
- 支持URL包含匹配，更灵活的检测
- 检查当前URL，如果已经是目标地址则立即更新

### 3. 简化的登录状态判断
- 通过URL直接判断登录状态
- 如果页面在首页 `https://xyq.cbg.163.com/` 则表示未登录
- 其他URL表示已登录状态
- 移除了复杂的页面元素检查

### 4. 异步Cookie更新
- 使用 `asyncio.create_task()` 异步执行Cookie更新
- 避免阻塞URL监听流程
- 独立的错误处理机制

### 5. 简化的等待逻辑
- 移除了复杂的超时处理
- 不再一直等待页面跳转
- 改为事件驱动的响应式处理

## 工作流程

1. **启动监听**: 设置 `framenavigated` 事件监听器
2. **检查当前状态**: 如果当前页面已经是目标URL，立即更新Cookie
3. **等待URL变化**: 监听页面导航事件
4. **检测目标URL**: 当URL包含目标模式时触发更新
5. **异步更新**: 在后台异步执行Cookie更新和LoginInfo收集
6. **登录状态判断**: 通过URL判断登录状态，首页表示未登录

## 优势

1. **非阻塞**: 不再一直等待，主流程不会被阻塞
2. **响应式**: 事件驱动，响应更及时
3. **高效**: 只在需要时更新Cookie，减少不必要的操作
4. **稳定**: 异步处理，避免超时和错误影响主流程
5. **智能**: 自动检测当前状态，避免重复操作

## 测试验证

创建了测试脚本验证功能：
- `tests/test_url_monitoring.py`: 验证URL监听功能
- `tests/test_simplified_login_check.py`: 验证简化后的登录状态检查
- URL监听功能正常
- 事件驱动机制工作正常
- 异步Cookie更新功能正常
- 登录状态判断逻辑正确
- 错误处理机制完善

## 使用方式

现在收集器的工作方式：
1. 启动时直接注入现有Cookie
2. 设置URL变化监听
3. 用户正常操作，无需等待
4. 当页面跳转到目标URL时自动更新Cookie
5. 通过URL判断登录状态（首页=未登录，其他=已登录）
6. 继续监听和收集数据

这种方式更加用户友好，不会阻塞用户操作，同时确保在需要时及时更新Cookie。登录状态判断也更加简单直接。 