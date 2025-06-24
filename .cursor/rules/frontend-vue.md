# Vue.js 前端开发规则

## Vue 2 + Element UI 开发规范

### 组件开发
- 使用单文件组件(.vue)格式
- 组件名使用PascalCase命名
- props使用camelCase，emit事件使用kebab-case
- 组件必须有name属性

### 模板规范
```vue
<template>
  <div class="component-wrapper">
    <!-- 使用语义化HTML标签 -->
    <!-- 避免过深的嵌套层级 -->
  </div>
</template>
```

### 样式规范
- 使用scoped样式避免污染
- CSS类名使用BEM命名法
- 响应式设计，支持移动端
- 使用Element UI的主题色系

### 数据管理
- 复杂状态使用Vuex管理
- API调用统一使用axios
- 错误处理要友好提示用户
- 加载状态要有loading提示

### Element UI 使用
- 优先使用Element UI组件
- 表格要支持分页、排序、筛选
- 表单要有验证规则
- 按钮要有loading状态

### 性能优化
- 长列表使用虚拟滚动
- 图片懒加载
- 路由懒加载
- 合理使用v-if和v-show 

## 项目结构
- 使用Vue 2.6.14 + Element UI
- 单页应用(SPA)架构
- 路由使用Vue Router
- 状态管理使用Vuex

## 组件规范
- 组件名使用PascalCase命名
- 文件名使用PascalCase.vue格式
- 组件内部使用composition API模式时要注意Vue 2兼容性

## API请求规范

### 统一API封装
**所有组件中禁止直接使用axios**，必须使用统一的API封装：

```javascript
// ❌ 错误方式：直接使用axios
import axios from 'axios'
const response = await axios.get('/api/v1/equipment/')

// ✅ 正确方式：使用统一API
const response = await this.$api.equipment.getEquipmentList(params)
```

### API响应处理模式
统一的响应拦截器已经处理了数据格式，使用以下模式：

```javascript
// ✅ 标准处理模式
const response = await this.$api.equipment.getEquipmentList(params)

if (response.success) {
  // 成功处理
  this.equipments = response.items || response.data || []
  this.pagination.total = response.total || 0
  this.pagination.page = response.page || this.pagination.page
} else {
  // 错误处理（响应拦截器已经显示了错误消息）
  this.$message.error(response.message || '操作失败')
}
```

### 后端兼容处理
对于尚未完全迁移的老接口，可以使用code判断：

```javascript
// 兼容老接口的处理方式
if (response.code === 200) {
  // 老接口格式：response.data.data
  this.equipments = response.data.data || []
  this.pagination.total = response.data.total || 0
} else if (response.success) {
  // 新接口格式：response.items/response.data
  this.equipments = response.items || response.data || []
  this.pagination.total = response.total || 0
}
```

### 分页数据处理
分页数据统一使用以下字段：
- `items`: 数据列表
- `total`: 总记录数
- `page`: 当前页码
- `pageSize` 或 `page_size`: 每页大小
- `totalPages`: 总页数

### 错误处理原则
1. **响应拦截器统一处理**：网络错误、HTTP错误自动显示消息
2. **业务错误手动处理**：根据response.success判断业务是否成功
3. **用户友好提示**：所有错误都要给用户明确的提示信息

### API模块组织
API按功能模块组织：
```javascript
// 在组件中使用
this.$api.character.getCharacterList()
this.$api.equipment.getEquipmentList()
this.$api.spider.getSpiderStatus()
```

## 数据绑定
- 使用v-model进行双向绑定
- 复杂数据使用computed属性
- 列表渲染使用v-for，必须绑定key

## 样式规范
- 使用scoped样式避免污染
- 遵循BEM命名规范
- 响应式布局使用Element UI的栅格系统 