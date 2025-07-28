# 页面刷新监听改进说明

## 问题背景

用户反馈"页面是调整会刷新的，你这个监听会丢失"，这是一个重要的问题。当用户在CBG网站中进行搜索、筛选或其他操作时，页面会发生刷新，导致之前注入的JavaScript监控脚本丢失，从而无法继续捕获API请求。

## 解决方案

### 1. 页面刷新检测机制

**修改文件**: `src/spider/auto_collector.py`

**核心改进**: 在`_monitor_network_requests`方法中添加页面刷新检测

```python
def _monitor_network_requests(self):
    """监控网络请求"""
    last_url = None
    last_script_injection_time = 0
    
    while self.is_collecting:
        try:
            # 检查页面是否刷新（URL变化）
            current_url = self.driver.current_url
            current_time = time.time()
            
            # 检测页面刷新或脚本丢失
            if last_url and last_url != current_url:
                logger.info(f"检测到页面刷新: {last_url} -> {current_url}")
                # 等待页面加载完成
                time.sleep(3)
                # 重新注入监控脚本
                self._inject_monitoring_script()
                last_script_injection_time = current_time
                last_url = current_url
            elif not last_url:
                last_url = current_url
            
            # 定期检查脚本是否还在（每30秒检查一次）
            if current_time - last_script_injection_time > 30:
                try:
                    # 尝试获取脚本注入的全局变量
                    script_exists = self.driver.execute_script("return typeof window.cbgRequests !== 'undefined';")
                    if not script_exists:
                        logger.info("检测到监控脚本丢失，重新注入...")
                        self._inject_monitoring_script()
                        last_script_injection_time = current_time
                except Exception as e:
                    logger.warning(f"检查脚本状态失败，重新注入: {e}")
                    self._inject_monitoring_script()
                    last_script_injection_time = current_time
            
            # 定期处理捕获的请求
            self._process_captured_requests()
            time.sleep(1)  # 每秒检查一次
            
        except Exception as e:
            logger.error(f"监控网络请求失败: {e}")
            time.sleep(5)  # 出错时等待更长时间
```

### 2. 脚本重复注入保护

**改进内容**: 在JavaScript注入脚本中添加重复注入保护机制

```javascript
// 防止重复注入
if (window.cbgMonitoringInitialized) {
    console.log('CBG监控脚本已存在，跳过重复注入');
    return;
}

// 创建全局变量存储请求和响应数据
window.cbgRequests = [];
window.cbgResponses = [];
window.cbgMonitoringInitialized = true;

console.log('CBG监控脚本开始初始化...');
```

### 3. 双重检测机制

系统采用双重检测机制确保监控脚本始终有效：

1. **URL变化检测**: 监控页面URL变化，检测页面刷新
2. **脚本状态检测**: 定期检查监控脚本是否存在
3. **自动恢复**: 检测到问题后自动重新注入脚本

## 功能特点

### 1. 智能检测
- **URL监控**: 实时监控页面URL变化
- **脚本状态检查**: 定期验证监控脚本有效性
- **自动恢复**: 无需人工干预，自动重新注入脚本

### 2. 性能优化
- **重复注入保护**: 防止不必要的重复注入
- **智能等待**: 页面刷新后等待适当时间再注入
- **错误处理**: 完善的异常处理机制

### 3. 用户体验
- **无缝监控**: 用户操作过程中监控不会中断
- **透明处理**: 后台自动处理，用户无需关心技术细节
- **详细日志**: 提供清晰的监控状态日志

## 测试验证

### 测试脚本
创建了`tests/test_page_refresh.py`测试脚本，验证功能正确性：

```python
def test_page_refresh_monitoring():
    """测试页面刷新后的监听功能"""
    # 1. 检查初始脚本注入
    # 2. 模拟页面刷新
    # 3. 验证脚本重新注入
    # 4. 测试重复注入保护
```

### 测试结果
```
✅ 脚本存在: True
✅ 监控初始化: True
✅ 初始脚本注入成功

🔄 模拟页面刷新（访问角色搜索页面）...
INFO: 检测到监控脚本丢失，重新注入...
✅ 页面刷新后脚本重新注入成功

🔄 再次模拟页面刷新（访问装备搜索页面）...
INFO: 检测到页面刷新: https://xyq.cbg.163.com/ -> https://xyq.cbg.163.com/cgi-bin/query.py?act=search_equip
✅ 第二次页面刷新后脚本重新注入成功

🛡️ 测试脚本重复注入保护...
✅ 重复注入测试完成（应该跳过重复注入）
```

## 技术原理

### 1. 页面刷新检测
- 监控`driver.current_url`的变化
- 比较当前URL与上次记录的URL
- 检测到变化时触发重新注入流程

### 2. 脚本状态验证
- 通过JavaScript检查全局变量`window.cbgRequests`是否存在
- 定期执行检查（每30秒一次）
- 发现脚本丢失时自动重新注入

### 3. 重复注入保护
- 使用`window.cbgMonitoringInitialized`标志
- 防止同一页面多次注入相同脚本
- 提高性能和稳定性

## 使用场景

### 1. 正常使用流程
1. 用户启动半自动收集器
2. 在CBG网站中正常操作（搜索、筛选等）
3. 页面刷新时系统自动检测并恢复监控
4. 数据收集持续进行，不会中断

### 2. 异常情况处理
- **网络中断**: 自动重试和恢复
- **脚本丢失**: 自动检测并重新注入
- **页面错误**: 错误处理和日志记录

## 优势特点

### 1. 可靠性提升
- **持续监控**: 页面刷新不会中断数据收集
- **自动恢复**: 无需人工干预，自动处理异常
- **错误容忍**: 完善的错误处理机制

### 2. 用户体验改善
- **无缝操作**: 用户可以正常使用网站功能
- **透明处理**: 后台自动处理技术细节
- **稳定可靠**: 监控脚本始终有效

### 3. 技术先进性
- **智能检测**: 多种检测机制确保准确性
- **性能优化**: 避免不必要的重复操作
- **可维护性**: 清晰的代码结构和日志

## 总结

这次改进彻底解决了页面刷新导致监听丢失的问题：

1. **问题解决**: 页面刷新后监控脚本自动恢复
2. **用户体验**: 用户可以正常操作，无需担心监控中断
3. **技术先进**: 采用多重检测和自动恢复机制
4. **稳定可靠**: 完善的错误处理和日志记录
5. **性能优化**: 防止重复注入，提高系统效率

改进后的半自动收集器更加智能、稳定、可靠，能够适应CBG网站的各种操作场景，为用户提供持续、稳定的数据收集服务！ 