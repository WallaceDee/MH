# 解析响应数据API文档

## 接口概述

该接口用于直接解析CBG爬虫的响应数据，接受URL和响应文本参数，调用`_parse_and_save_response`方法进行数据解析和保存。

## 接口信息

- **URL**: `/api/v1/spider/parse/response`
- **方法**: `POST`
- **Content-Type**: `application/json`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| url | string | 是 | CBG请求的完整URL |
| response_text | string | 是 | 服务器返回的响应文本（JSONP格式） |

## 请求示例

```json
{
    "url": "https://xyq.cbg.163.com/cgi-bin/query.py?act=overall_search_role&server_id=9&page=1&order_by=price%20ASC&count=15&search_type=overall_search_role",
    "response_text": "callback_12345({\"errno\":0,\"msg\":\"\",\"data\":{\"page\":1,\"total_page\":10,\"total_count\":100,\"items\":[{\"id\":\"12345\",\"name\":\"测试角色\",\"price\":1000,\"server_name\":\"紫禁城\"}]}});"
}
```

## 响应格式

### 成功响应

```json
{
    "code": 200,
    "data": {
        "success": true,
        "message": "响应数据解析完成",
        "url": "https://xyq.cbg.163.com/cgi-bin/query.py?act=overall_search_role&server_id=9&page=1&order_by=price%20ASC&count=15&search_type=overall_search_role",
        "data_length": 161,
        "type": "role"
    },
    "message": "响应数据解析完成",
    "timestamp": 1757429624
}
```

**data字段说明：**
- `success`: 是否成功
- `message`: 响应消息
- `url`: 原始请求URL
- `data_length`: 响应文本长度
- `type`: 识别的数据类型，可能的值包括：
  - `role`: 角色数据
  - `pet`: 召唤兽数据
  - `equipment`: 装备数据（包括灵饰和召唤兽装备）

### 错误响应

```json
{
    "code": 400,
    "data": null,
    "message": "url参数不能为空",
    "timestamp": 1757429631
}
```

## 支持的数据类型

该接口支持解析以下类型的CBG数据：

1. **角色数据** (`overall_search_role`)
   - URL包含 `act=overall_search_role`
   - 解析角色信息并保存到数据库

2. **装备数据** (`overall_search_equip`)
   - URL包含 `act=overall_search_equip`
   - 解析装备信息并保存到数据库

3. **召唤兽数据** (`overall_search_pet`)
   - URL包含 `act=overall_search_pet`
   - 解析召唤兽信息并保存到数据库

## 使用场景

1. **手动数据解析**: 当需要手动解析特定的CBG响应数据时
2. **数据修复**: 当某些数据解析失败需要重新处理时
3. **测试验证**: 验证解析逻辑是否正确
4. **批量处理**: 批量处理多个响应数据

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误（缺少必填参数、参数类型错误等） |
| 500 | 服务器内部错误（解析失败、数据库错误等） |

## 注意事项

1. **URL格式**: 必须提供完整的CBG请求URL，包含所有查询参数
2. **响应格式**: 响应文本必须是JSONP格式，包含回调函数
3. **数据保存**: 解析成功的数据会自动保存到对应的数据库表中
4. **异步处理**: 接口内部使用异步方式处理数据解析
5. **错误处理**: 解析失败时会返回详细的错误信息

## 测试用例

参考 `tests/test_parse_response_api.py` 文件中的测试用例，包含：

- 正常功能测试（角色、装备、召唤兽数据解析）
- 无效参数测试（缺少参数、参数类型错误等）
- 边界条件测试

## 相关文件

- **控制器**: `src/app/controllers/spider_controller.py`
- **服务层**: `src/app/services/spider_service.py`
- **API蓝图**: `src/app/blueprints/api/v1/spider.py`
- **解析器**: `src/spider/playwright_collector.py`
- **测试文件**: `tests/test_parse_response_api.py`
