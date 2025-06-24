# API使用指南

## 概述
本项目使用统一的API封装来处理前后端数据交互，避免直接使用axios，提供一致的错误处理和数据格式化。

## 核心架构

### 1. 响应拦截器统一处理
所有API响应都经过统一的响应拦截器处理：

```javascript
// 响应拦截器自动处理
response.interceptors.response.use(
  response => {
    const { data } = response
    if (data.code === 200) {
      return {
        success: true,
        data: data.data,
        message: data.message,
        // 分页数据自动提取
        ...(data.data?.items ? {
          items: data.data.items,
          total: data.data.total,
          page: data.data.page,
          pageSize: data.data.page_size
        } : {})
      }
    } else {
      // 自动显示错误消息
      ElMessage.error(data.message || '请求失败')
      return { success: false, message: data.message, code: data.code }
    }
  }
)
```

### 2. API模块化组织
```
web/src/api/
├── index.js          # 统一导出
├── character.js      # 角色相关API
├── equipment.js      # 装备相关API
└── request.js        # axios封装
```

## 使用规范

### ✅ 正确使用方式

#### 基本API调用
```javascript
// 获取列表数据
const response = await this.$api.equipment.getEquipmentList(params)
if (response.success) {
  this.equipments = response.items || response.data || []
  this.total = response.total || 0
}

// 获取详情数据
const response = await this.$api.character.getCharacterDetail(id)
if (response.success) {
  this.characterDetail = response.data
}

// POST请求
const response = await this.$api.equipment.findEquipmentAnchors({
  equipment_data: equipment,
  similarity_threshold: 0.6
})
if (response.success) {
  this.anchors = response.data.anchors
}
```

#### 兼容老接口
```javascript
// 对于尚未迁移的老接口，使用code判断
const response = await this.$api.equipment.getEquipmentList(params)

if (response.code === 200) {
  // 老接口格式
  this.equipments = response.data.data || []
  this.total = response.data.total || 0
} else if (response.success) {
  // 新接口格式
  this.equipments = response.items || response.data || []
  this.total = response.total || 0
} else {
  // 错误处理
  this.$message.error(response.message || '获取数据失败')
}
```

### ❌ 错误使用方式

```javascript
// ❌ 直接使用axios
import axios from 'axios'
const response = await axios.get('/api/v1/equipment/')

// ❌ 复杂的嵌套数据访问
this.equipments = response.data.data.data  // 太别扭

// ❌ 没有错误处理
const response = await this.$api.equipment.getEquipmentList(params)
this.equipments = response.data  // 没有检查success状态
```

## 数据格式规范

### 分页响应格式
```javascript
{
  success: true,
  data: { /* 原始数据 */ },
  items: [...],      // 数据列表
  total: 1420,       // 总记录数
  page: 1,           // 当前页
  pageSize: 10,      // 每页大小
  totalPages: 142    // 总页数
}
```

### 单条数据响应格式
```javascript
{
  success: true,
  data: { /* 具体数据对象 */ },
  message: "操作成功"
}
```

### 错误响应格式
```javascript
{
  success: false,
  message: "错误信息",
  code: 400
}
```

## 错误处理最佳实践

### 1. 三层错误处理
```javascript
try {
  const response = await this.$api.equipment.getEquipmentList(params)
  
  if (response.success) {
    // 业务成功处理
    this.handleSuccessData(response)
  } else {
    // 业务错误处理（响应拦截器已显示基础错误消息）
    this.handleBusinessError(response)
  }
} catch (error) {
  // 网络错误或其他异常（响应拦截器已显示网络错误消息）
  console.error('请求异常:', error)
  this.handleNetworkError(error)
}
```

### 2. 用户友好的错误提示
```javascript
// 根据不同场景提供具体的错误信息
if (!response.success) {
  switch (response.code) {
    case 404:
      this.$message.error('请求的数据不存在')
      break
    case 403:
      this.$message.error('没有权限访问该数据')
      break
    default:
      this.$message.error(response.message || '操作失败，请稍后重试')
  }
}
```

## 加载状态管理

### 列表加载
```javascript
async fetchData() {
  this.loading = true
  try {
    const response = await this.$api.equipment.getEquipmentList(this.params)
    if (response.success) {
      this.equipments = response.items || []
      this.total = response.total || 0
    }
  } finally {
    this.loading = false
  }
}
```

### 按钮加载
```javascript
async handleExport() {
  this.exportLoading = true
  try {
    const response = await this.$api.character.exportCharactersJson(this.exportParams)
    if (response.success) {
      this.$message.success('导出成功')
    }
  } finally {
    this.exportLoading = false
  }
}
```

## 文件下载处理

```javascript
// API已封装文件下载功能
const response = await this.$api.character.exportSingleCharacterJson(id, params)
// 文件会自动下载，无需额外处理
```

## 常见问题解决

### Q: 为什么不能直接使用axios？
A: 直接使用axios会导致：
- 数据访问路径不一致（data.data.data）
- 错误处理不统一
- 无法享受响应拦截器的数据格式化

### Q: 如何处理老接口和新接口并存？
A: 使用兼容模式，同时检查response.code和response.success

### Q: 响应拦截器已经处理错误了，还需要手动处理吗？
A: 响应拦截器只处理网络错误和显示基础错误消息，业务逻辑错误仍需要手动处理

## 迁移指南

### 从axios迁移到统一API
1. 移除axios导入：`import axios from 'axios'`
2. 替换API调用：`axios.get()` → `this.$api.module.method()`
3. 更新数据访问：`response.data.data.data` → `response.items`
4. 添加错误处理：检查`response.success`状态 