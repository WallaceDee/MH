# 测试开发规则

## 测试策略和规范

### 测试层级
1. **单元测试**: 测试单个函数/方法
2. **集成测试**: 测试模块间交互
3. **端到端测试**: 测试完整用户流程
4. **性能测试**: 测试系统性能指标

### Python后端测试
```python
# 使用pytest框架
import pytest
from flask import Flask
from your_app import create_app

@pytest.fixture
def client():
    app = create_app(testing=True)
    return app.test_client()

def test_api_endpoint(client):
    response = client.get('/api/v1/data')
    assert response.status_code == 200
    assert 'data' in response.json
```

### 前端测试
- 使用Jest + Vue Test Utils
- 组件单元测试
- 用户交互测试
- 路由测试

### 爬虫测试
```python
# Mock网络请求
import responses
@responses.activate
def test_crawler():
    responses.add(
        responses.GET,
        'http://example.com',
        body='<html>test</html>',
        status=200
    )
    # 测试爬虫逻辑
```

### 测试数据管理
- 使用测试数据库
- Mock外部API
- 测试用例独立性
- 清理测试数据

### 覆盖率要求
- 核心业务逻辑: 90%+
- API接口: 80%+
- 爬虫模块: 70%+
- 前端组件: 60%+

### CI/CD集成
- 代码提交触发测试
- 测试失败阻止合并
- 生成测试报告
- 自动部署测试环境 