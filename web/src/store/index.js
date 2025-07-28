import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'

Vue.use(Vuex)

// Cookie验证缓存模块
const cookieModule = {
  namespaced: true,
  state: {
    cookieValidationCache: {
      lastValidTime: null, // 最后一次验证成功的时间戳
      cacheDuration: 5 * 60 * 1000, // 缓存时间：5分钟（毫秒）
      isValid: false // 当前缓存的有效状态
    }
  },
  getters: {
    // 检查缓存是否有效
    isCookieCacheValid: (state) => {
      if (!state.cookieValidationCache.isValid || !state.cookieValidationCache.lastValidTime) {
        return false
      }

      const now = Date.now()
      const timeSinceLastValid = now - state.cookieValidationCache.lastValidTime

      // 如果距离上次验证成功的时间小于缓存时间，则使用缓存
      if (timeSinceLastValid < state.cookieValidationCache.cacheDuration) {
        return true
      }

      // 缓存已过期，自动清理
      return false
    },

    // 获取缓存剩余时间（分钟）
    getCacheRemainingMinutes: (state) => {
      if (!state.cookieValidationCache.isValid || !state.cookieValidationCache.lastValidTime) {
        return 0
      }

      const now = Date.now()
      const timeSinceLastValid = now - state.cookieValidationCache.lastValidTime
      const remainingTime = state.cookieValidationCache.cacheDuration - timeSinceLastValid

      if (remainingTime <= 0) {
        return 0
      }

      return Math.ceil(remainingTime / (60 * 1000))
    },

    // 获取缓存过期时间
    getCacheExpiryTime: (state) => {
      if (!state.cookieValidationCache.isValid || !state.cookieValidationCache.lastValidTime) {
        return null
      }

      return new Date(
        state.cookieValidationCache.lastValidTime + state.cookieValidationCache.cacheDuration
      )
    },

    // 获取缓存状态
    getCookieCache: (state) => {
      return state.cookieValidationCache
    }
  },
  mutations: {
    // 更新Cookie缓存
    updateCookieCache(state, isValid) {
      state.cookieValidationCache.isValid = isValid
      if (isValid) {
        state.cookieValidationCache.lastValidTime = Date.now()
        console.log('Cookie验证缓存已更新，有效期5分钟')
      } else {
        state.cookieValidationCache.lastValidTime = null
        console.log('Cookie验证缓存已清除')
      }
    }
  },
  actions: {
    // 清除Cookie缓存
    clearCookieCache({ commit }) {
      commit('updateCookieCache', false)
    },

    // 清理过期缓存
    cleanExpiredCache({ commit, getters }) {
      if (!getters.isCookieCacheValid) {
        commit('updateCookieCache', false)
        console.log('过期缓存已自动清理')
      }
    }
  }
}

export default new Vuex.Store({
  state: {
    areaid: 43,
    server_id: 77,
    server_name: '进贤门',
    server_data_value: [43, 77] // 第一项是areaid，第二项是server_id
  },
  getters: {
    // 获取当前服务器数据
    getCurrentServerData: (state) => {
      return {
        areaid: state.areaid,
        server_id: state.server_id,
        server_name: state.server_name,
        server_data_value: state.server_data_value
      }
    }
  },
  mutations: {
    // 更新服务器数据
    updateServerData(state, { areaid, server_id, server_name }) {
      state.areaid = areaid
      state.server_id = server_id
      state.server_name = server_name
      state.server_data_value = [areaid, server_id]
    },
    
    // 更新server_data_value
    updateServerDataValue(state, server_data_value) {
      if (Array.isArray(server_data_value) && server_data_value.length >= 2) {
        state.server_data_value = server_data_value
        state.areaid = server_data_value[0]
        state.server_id = server_data_value[1]
        
        // 根据server_data_value查找对应的server_name
        if (window.server_data) {
          for (let key in window.server_data) {
            let [parent, children] = window.server_data[key]
            const [, , , , areaValue] = parent
            if (areaValue === server_data_value[0]) {
              for (let child of children) {
                if (child[0] === server_data_value[1]) {
                  state.server_name = child[1]
                  break
                }
              }
              break
            }
          }
        }
      }
    }
  },
  actions: {
    // 设置服务器数据
    setServerData({ commit }, { areaid, server_id, server_name }) {
      commit('updateServerData', { areaid, server_id, server_name })
    },
    
    // 设置server_data_value
    setServerDataValue({ commit }, server_data_value) {
      commit('updateServerDataValue', server_data_value)
    }
  },
  modules: {
    cookie: cookieModule
  },
  plugins: [
    createPersistedState({
      // 持久化整个store
      key: 'cbg-cookie-cache',
      // 存储方式
      storage: window.localStorage
    })
  ]
})
