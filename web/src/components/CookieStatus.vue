<template>
  <div class="cookie-status-section">
    <el-alert :title="dynamicCookieStatus.text" :type="dynamicCookieStatus.type" :closable="false" show-icon>
      <el-row class="el-el-alert__title" type="flex" align="middle">
        <span v-if="dynamicCookieStatus.lastModified">
          最后更新: {{ dynamicCookieStatus.lastModified }}
        </span>
        <p v-if="getCacheRemainingMinutes > 0" style="margin-left: 10px; color: #67c23a;">
          ⏰ 缓存有效: {{ getCacheRemainingMinutes }}分钟
        </p>

      </el-row>
      <el-row class="el-alert__description" type="flex" align="middle">
      <el-button type="text" size="mini" style="margin-left: 10px;" @click="handleCheckStatus"
          :loading="cookieChecking" :disabled="cookieUpdating">
          🔍 检查状态
        </el-button>
        <!-- <el-button v-if="getCacheRemainingMinutes > 0" type="text" size="mini" style="margin-left: 5px;" 
          @click="handleClearCache" :disabled="cookieChecking || cookieUpdating">
          🗑️ 清除缓存
        </el-button> -->
        <el-button  type="text" size="mini" @click="handleUpdateCookies"
          :loading="cookieUpdating" :disabled="cookieChecking">
          ♻️ 更新/登录
        </el-button>
        </el-row>
    </el-alert>
  </div>
</template>

<script>
export default {
  name: 'CookieStatus',
  props: {
    // 是否自动检查Cookie状态
    autoCheck: {
      type: Boolean,
      default: true
    },
    // 是否显示缓存信息
    showCacheInfo: {
      type: Boolean,
      default: true
    },
    // 是否显示操作按钮
    showActions: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      // Cookie状态
      cookiesStatus: {
        type: 'info',
        text: '未检查',
        lastModified: null,
        server_validated: false
      },
      // 🍪 更新状态
      cookieUpdating: false,
      cookieChecking: false,
      // 🍪 更新监控定时器
      cookieUpdateTimer: null
    }
  },
  computed: {
    // Cookie缓存相关计算属性
    isCookieCacheValid() {
      return this.$store.getters['cookie/isCookieCacheValid']
    },

    getCacheRemainingMinutes() {
      return this.$store.getters['cookie/getCacheRemainingMinutes']
    },

    getCacheExpiryTime() {
      return this.$store.getters['cookie/getCacheExpiryTime']
    },

    // 动态Cookie状态显示
    dynamicCookieStatus() {
      if (this.isCookieCacheValid) {
        return {
          type: 'success',
          text: '🍪 有效',
          lastModified: '缓存中',
          server_validated: true
        }
      }
      return this.cookiesStatus
    }
  },
  mounted() {
    // 自动检查Cookie状态
    if (this.autoCheck) {
      this.$nextTick(() => {
        this.handleCheckStatus()
      })
    }
  },
  beforeDestroy() {
    // 清理定时器
    this.stopCookieUpdateMonitoring()
  },
  methods: {
    // 处理检查状态
    async handleCheckStatus() {
      if (this.cookieChecking) return

      // 检查缓存是否有效
      if (this.isCookieCacheValid) {
        console.log('使用 🍪 验证缓存，跳过服务器验证')
        return
      }

      this.cookieChecking = true
      try {
        const response = await this.$api.spider.checkCookie()
        if (response.code === 200) {
          const data = response.data
          if (data.valid) {
            // Cookie有效，更新缓存
            this.$store.commit('cookie/updateCookieCache', true)
            this.cookiesStatus = {
              type: 'success',
              text: '🍪 有效',
              lastModified: data.last_modified || '未知',
              server_validated: true
            }
          } else {
            // Cookie无效，清除缓存
            this.$store.commit('cookie/updateCookieCache', false)
            this.cookiesStatus = {
              type: 'error',  
              text: '🍪 已过期',  
              lastModified: data.last_modified || '未知',
              server_validated: false
            }
            this.$notify.warning({
              title: '🍪 已过期',
              message: '需要重新登录'
            })
          }
        } else {
          // 检查失败，清除缓存
          this.$store.commit('cookie/updateCookieCache', false)
          this.cookiesStatus = {
            type: 'danger',
            text: '检查失败',
            lastModified: '未知',
            server_validated: false
          }
          this.$notify.error({
            title: '检查失败',
            message: response.message || '检查Cookies状态失败'
          })
        }
        
        // 触发状态变化事件
        this.$emit('status-change', this.cookiesStatus)
      } catch (error) {
        this.cookiesStatus = {
          type: 'danger',
          text: '检查失败',
          lastModified: '未知',
          server_validated: false
        }
        this.$notify.error({
          title: '检查失败',
          message: '检查🍪状态失败: ' + error.message
        })
        this.$emit('status-change', this.cookiesStatus)
      } finally {
        this.cookieChecking = false
      }
    },

    // 处理清除缓存
    handleClearCache() {
      this.$store.dispatch('cookie/clearCookieCache')
      this.$notify.info({
        title: '缓存已清除',
        message: 'Cookie验证缓存已清除，下次检查将重新验证'
      })
      this.$emit('cache-cleared')
    },

    // 处理更新Cookies
    async handleUpdateCookies() {
      if (this.cookieUpdating) return

      this.cookieUpdating = true
      try {
        this.$notify.info({
          title: '🍪 更新',
          message: '正在启动🍪 更新程序，请在弹出的浏览器中登录...'
        })

        const response = await this.$api.spider.updateCookies()
        if (response.code === 200) {
          // 不立即显示成功，而是提示用户等待
          this.$notify.info({
            title: '🍪 更新',
            message: '🍪 更新程序已启动，请在浏览器中完成登录操作'
          })

          // 更新Cookie状态为"更新中"
          this.cookiesStatus = {
            type: 'warning',
            text: '🍪 更新中...',
            lastModified: '未知',
            server_validated: false
          }

          // 启动状态检查，定期检查🍪 更新是否完成
          this.startCookieUpdateMonitoring()
          
          this.$emit('update-started')
        } else {
          throw new Error(response.message || '🍪 更新失败')
        }
      } catch (error) {
        this.$notify.error('🍪 更新失败: ' + error.message)
        this.$emit('update-failed', error)
      } finally {
        this.cookieUpdating = false
      }
    },

    // 启动🍪 更新监控
    startCookieUpdateMonitoring() {
      // 清除之前的定时器
      if (this.cookieUpdateTimer) {
        clearInterval(this.cookieUpdateTimer)
      }

      let checkCount = 0
      const maxChecks = 60 // 最多检查60次（5分钟）

      this.cookieUpdateTimer = setInterval(async () => {
        checkCount++

        try {
          // 检查任务状态
          const statusResponse = await this.$api.spider.getStatus()
          if (statusResponse.code === 200) {
            const status = statusResponse.data

            if (status.status === 'completed' && status.message.includes('🍪 更新成功')) {
              // 🍪 更新成功
              clearInterval(this.cookieUpdateTimer)
              this.cookieUpdateTimer = null

              // 清除Cookie验证缓存，确保重新验证
              this.updateCookieCache(false)
              
              this.$notify.success({
                title: '🍪 更新',
                message: '🍪 更新成功！'
              })
              this.cookiesStatus = {
                type: 'success',
                text: '🍪 已更新',
                lastModified: '刚刚',
                server_validated: true
              }

              // 重新检查Cookie状态
              await this.handleCheckStatus()
              this.$emit('update-completed')
            } else if (status.status === 'error' && status.message.includes('🍪 更新失败')) {
              // 🍪 更新失败
              clearInterval(this.cookieUpdateTimer)
              this.cookieUpdateTimer = null

              this.$notify.error({
                title: '🍪 更新',
                message: '🍪 更新失败，请重试'
              })
              this.cookiesStatus = {
                type: 'danger',
                text: '🍪 更新失败',
                lastModified: '未知',
                server_validated: false
              }
              this.$emit('update-failed', new Error('🍪 更新失败'))
            }
          }
        } catch (error) {
          console.error('检查 🍪 更新状态失败:', error)
        }

        // 如果检查次数超过限制，停止监控
        if (checkCount >= maxChecks) {
          clearInterval(this.cookieUpdateTimer)
          this.cookieUpdateTimer = null

          this.$notify.warning({
            title: '🍪 更新',
            message: '🍪 更新监控超时，请手动检查状态'
          })
          this.cookiesStatus = {
            type: 'warning',
            text: '🍪 更新状态未知',
            lastModified: '未知',
            server_validated: false
          }
          this.$emit('update-timeout')
        }
      }, 5000) // 每5秒检查一次
    },

    // 停止🍪 更新监控
    stopCookieUpdateMonitoring() {
      if (this.cookieUpdateTimer) {
        clearInterval(this.cookieUpdateTimer)
        this.cookieUpdateTimer = null
      }
    }
  }
}
</script>

<style scoped>
.el-alert__description {
  margin-top: 10px;
}

.el-alert__description p {
  margin: 5px 0;
  display: flex;
  align-items: center;
  color: #606266;
  font-size: 13px;
}
:global(.cookie-status-section .el-alert) {
  align-items: flex-start;
}
</style> 