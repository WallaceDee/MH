# Cookie管理插件使用文档

## 概述

Cookie管理插件是一个Vue.js插件，提供了简化的Cookie状态管理功能。插件主要提供全局访问方法，具体的Cookie状态管理通过Vuex store和CookieStatus组件实现。

## 功能特性

- ✅ **Vuex状态管理**: 使用Vuex管理Cookie缓存状态
- ✅ **状态持久化**: 使用vuex-persistedstate插件保存状态
- ✅ **组件化**: 提供可复用的Cookie状态组件
- ✅ **事件通知**: 完整的事件回调机制
- ✅ **智能缓存**: 5分钟缓存机制，避免频繁验证

## 安装和配置

### 1. 注册插件

在 `main.js` 中注册插件：

```javascript
import Vue from 'vue'
import CookieManager from './plugins/cookieManager'

Vue.use(CookieManager)
```

### 2. 配置Vuex

确保Vuex store中已配置cookie模块和持久化插件：

```javascript
// store/index.js
import createPersistedState from 'vuex-persistedstate'

export default new Vuex.Store({
  modules: {
    cookie: cookieModule
  },
  plugins: [
    createPersistedState({
      paths: ['cookie'],
      key: 'cbg-cookie-cache',
      storage: window.localStorage
    })
  ]
})
```

## 使用方法

### 1. 使用Cookie状态组件

```vue
<template>
  <div>
    <CookieStatus 
      :auto-check="true"
      :show-cache-info="true"
      :show-actions="true"
      @status-change="onCookieStatusChange"
      @cache-cleared="onCookieCacheCleared"
      @update-started="onCookieUpdateStarted"
      @update-completed="onCookieUpdateCompleted"
      @update-failed="onCookieUpdateFailed"
      @update-timeout="onCookieUpdateTimeout"
    />
  </div>
</template>

<script>
import CookieStatus from '@/components/CookieStatus.vue'

export default {
  components: {
    CookieStatus
  },
  methods: {
    onCookieStatusChange(status) {
      console.log('Cookie状态变化:', status)
    },
    onCookieCacheCleared() {
      console.log('Cookie缓存已清除')
    },
    onCookieUpdateStarted() {
      console.log('Cookie更新已开始')
    },
    onCookieUpdateCompleted() {
      console.log('Cookie更新已完成')
    },
    onCookieUpdateFailed(error) {
      console.log('Cookie更新失败:', error)
    },
    onCookieUpdateTimeout() {
      console.log('Cookie更新超时')
    }
  }
}
</script>
```

### 2. 组件属性

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `auto-check` | Boolean | `true` | 是否自动检查Cookie状态 |
| `show-cache-info` | Boolean | `true` | 是否显示缓存信息 |
| `show-actions` | Boolean | `true` | 是否显示操作按钮 |

### 3. 组件事件

| 事件名 | 参数 | 说明 |
|--------|------|------|
| `status-change` | `status` | Cookie状态变化时触发 |
| `cache-cleared` | - | 缓存清除时触发 |
| `update-started` | - | Cookie更新开始时触发 |
| `update-completed` | - | Cookie更新完成时触发 |
| `update-failed` | `error` | Cookie更新失败时触发 |
| `update-timeout` | - | Cookie更新超时时触发 |

### 4. 在组件中使用Vuex

```vue
<template>
  <div>
    <el-button @click="checkStatus">检查状态</el-button>
    <el-button @click="clearCache">清除缓存</el-button>
    <el-button @click="updateCookies">更新Cookies</el-button>
  </div>
</template>

<script>
export default {
  computed: {
    // Cookie缓存相关计算属性
    isCookieCacheValid() {
      return this.$store.getters['cookie/isCookieCacheValid']
    },
    getCacheRemainingMinutes() {
      return this.$store.getters['cookie/getCacheRemainingMinutes']
    }
  },
  methods: {
    async checkStatus() {
      try {
        const response = await this.$api.spider.checkCookie()
        if (response.code === 200) {
          const data = response.data
          this.$store.commit('cookie/updateCookieCache', data.valid)
        }
      } catch (error) {
        console.error('检查失败:', error)
      }
    },
    
    clearCache() {
      this.$store.dispatch('cookie/clearCookieCache')
    },
    
    async updateCookies() {
      try {
        const response = await this.$api.spider.updateCookies()
        if (response.code === 200) {
          console.log('Cookie更新已启动')
        }
      } catch (error) {
        console.error('更新失败:', error)
      }
    }
  }
}
</script>
```

### 5. 全局访问

通过 `this.$cookieManager` 可以访问插件的全局方法：

```javascript
// 获取缓存状态
const cache = this.$cookieManager.getCache()

// 设置缓存状态
this.$cookieManager.setCache({
  lastValidTime: Date.now(),
  cacheDuration: 300000,
  isValid: true
})

// 重置插件状态
this.$cookieManager.reset()
```

## Vuex Store结构

### State
```javascript
{
  cookieValidationCache: {
    lastValidTime: null,        // 最后一次验证成功的时间戳
    cacheDuration: 300000,      // 缓存时间：5分钟（毫秒）
    isValid: false              // 当前缓存的有效状态
  }
}
```

### Getters
- `isCookieCacheValid`: 检查缓存是否有效
- `getCacheRemainingMinutes`: 获取缓存剩余时间（分钟）
- `getCacheExpiryTime`: 获取缓存过期时间
- `getCookieCache`: 获取完整缓存状态

### Mutations
- `updateCookieCache(isValid)`: 更新Cookie缓存状态

### Actions
- `clearCookieCache()`: 清除Cookie缓存
- `cleanExpiredCache()`: 清理过期缓存

## 状态对象结构

Cookie状态对象包含以下字段：

```javascript
{
  type: 'success' | 'warning' | 'danger' | 'info',
  text: '状态描述文本',
  lastModified: '最后修改时间',
  server_validated: true | false
}
```

## 注意事项

1. **API依赖**: 组件依赖后端API接口，确保以下接口可用：
   - `GET /api/v1/spider/cookie/check` - 检查Cookie状态
   - `POST /api/v1/spider/cookie/update` - 更新Cookie
   - `GET /api/v1/spider/status` - 获取任务状态

2. **Vuex依赖**: 需要Vuex store中的cookie模块，确保正确配置

3. **持久化**: 使用vuex-persistedstate插件实现状态持久化

4. **组件独立性**: CookieStatus组件完全独立，不依赖插件方法

## 示例项目

完整的使用示例请参考 `HomeView.vue` 文件。 