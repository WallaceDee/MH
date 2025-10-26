/**
 * 窗口复用管理器
 * 用于管理相似窗口的复用，避免重复打开相同功能的窗口
 */
class WindowReuseManager {
  constructor() {
    this.channelName = 'similar-window-reuse'
    this.channel = null
    this.windowId = null
    this.isSetup = false
    this.setup()
  }

  setup() {
    try {
      this.channel = new BroadcastChannel(this.channelName)
      this.windowId = this.generateWindowId()
      this.setupMessageListener()
      this.isSetup = true
      
      // 设置窗口关闭时的清理
      window.addEventListener('beforeunload', () => {
        this.cleanup()
      })
      
      console.log('WindowReuseManager setup completed, windowId:', this.windowId)
    } catch (error) {
      console.warn('Failed to setup WindowReuseManager:', error)
    }
  }

  generateWindowId() {
    return `window_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  setupMessageListener() {
    if (!this.channel) return

    this.channel.onmessage = (event) => {
      const { type, params, windowId, timestamp } = event.data
      
      switch (type) {
        case 'check-window':
          this.handleCheckWindow(params, timestamp)
          break
        case 'focus-window':
          this.handleFocusWindow(windowId, timestamp)
          break
        case 'update-params':
          this.handleUpdateParams(params, timestamp)
          break
        default:
          console.log('Unknown message type:', type)
      }
    }
  }

  handleCheckWindow(params, timestamp) {
    console.log('🔍 收到窗口检查请求，当前窗口ID:', this.windowId)
    console.log('🔍 检查参数:', params)
    
          // 检查当前窗口是否兼容请求的参数
      if (this.isWindowCompatible(params)) {
        console.log('✅ 当前窗口兼容，发送可用消息')
        this.channel.postMessage({
          type: 'window-available',
          windowId: this.windowId,
          params: params,
          timestamp: Date.now()
        })
      } else {
        console.log('❌ 当前窗口不兼容，忽略请求')
      }
  }

  handleFocusWindow(targetWindowId, timestamp) {
    // 如果目标窗口ID匹配，则聚焦当前窗口
    if (targetWindowId === this.windowId) {
      this.focusWindow()
    }
  }

  handleUpdateParams(params, timestamp) {
    console.log('📨 收到参数更新请求:', params)
    
    // 先检查窗口兼容性，只有兼容的窗口才能更新参数
    if (this.isWindowCompatible(params)) {
      console.log('✅ 窗口兼容，开始更新参数...')
      this.refreshWithNewUrl(params)
    } else {
      console.log('❌ 窗口不兼容，忽略参数更新请求')
      console.log('当前窗口参数与请求参数不匹配，无法更新')
    }
  }

  isWindowCompatible(params) {
    try {
      const currentUrl = window.location.href
      console.log('🔍 检查窗口兼容性，当前URL:', currentUrl)
      
      // 检查是否是auto-params页面（支持hash路由）
      if (!currentUrl.includes('/admin/#/auto-params') && !currentUrl.includes('#/admin/auto-params')) {
        console.log('❌ 不是auto-params页面')
        return false
      }

      // 检查action是否匹配（支持hash路由）
      let urlParams
      if (window.location.hash && window.location.hash.includes('?')) {
        // hash路由：从hash中提取查询参数
        const hashQuery = window.location.hash.split('?')[1]
        console.log('🔍 从hash中提取查询参数:', hashQuery)
        urlParams = new URLSearchParams(hashQuery)
      } else {
        // 普通路由：从search中获取参数
        console.log('🔍 从search中获取参数:', window.location.search)
        urlParams = new URLSearchParams(window.location.search)
      }
      
      const currentAction = urlParams.get('action')
      const currentEquipType = urlParams.get('equip_type')
      
      console.log('🔍 当前页面参数 - action:', currentAction, 'equip_type:', currentEquipType)
      console.log('🔍 请求参数 - action:', params.action, 'equip_type:', params.equip_type)
      
      // 基本匹配：action必须相同
      if (currentAction !== params.action) {
        console.log('❌ action不匹配')
        return false
      }

      // 装备类型匹配（如果指定了的话）
      if (params.equip_type && currentEquipType !== params.equip_type) {
        console.log('❌ equip_type不匹配')
        return false
      }

      console.log('✅ 窗口兼容性检查通过')
      // 注意：即使窗口兼容，如果具体装备信息不同，仍然需要更新参数
      return true
    } catch (error) {
      console.warn('Error checking window compatibility:', error)
      return false
    }
  }

  focusWindow() {
    try {
      // 尝试多种聚焦方式
      if (window.focus) {
        window.focus()
      }
      
      // 如果窗口被最小化，尝试恢复
      if (window.screen && window.screen.orientation) {
        // 现代浏览器支持
        window.focus()
      }
      
      // 滚动到顶部
      window.scrollTo(0, 0)
      
      console.log('Window focused:', this.windowId)
    } catch (error) {
      console.warn('Failed to focus window:', error)
    }
  }

  updateWindowParams(params) {
    try {
      // 更新URL参数（支持hash路由）
      let newUrl
      if (window.location.hash && window.location.hash.includes('?')) {
        // hash路由：更新hash中的查询参数
        const [hashPath, hashQuery] = window.location.hash.split('?')
        const urlParams = new URLSearchParams(hashQuery)
        
        Object.keys(params).forEach(key => {
          if (params[key] !== undefined && params[key] !== null) {
            urlParams.set(key, params[key])
          }
        })
        
        newUrl = `${hashPath}?${urlParams.toString()}`
      } else {
        // 普通路由：更新search参数
        const url = new URL(window.location)
        Object.keys(params).forEach(key => {
          if (params[key] !== undefined && params[key] !== null) {
            url.searchParams.set(key, params[key])
          }
        })
        newUrl = url.toString()
      }
      
      // 使用replaceState更新URL，不刷新页面
      window.history.replaceState({}, '', newUrl)
      
      // 触发自定义事件，通知页面内容更新
      const event = new CustomEvent('params-updated', { 
        detail: { params, timestamp: Date.now() } 
      })
      window.dispatchEvent(event)
      
      console.log('📢 已触发参数更新事件:', event)
      console.log('Window params updated:', params)
    } catch (error) {
      console.warn('Failed to update window params:', error)
    }
  }

  refreshWithNewUrl(params) {
    try {
      // 构建新的URL（支持hash路由）
      let newUrl
      if (window.location.hash && window.location.hash.includes('?')) {
        // hash路由：更新hash中的查询参数
        const [hashPath, hashQuery] = window.location.hash.split('?')
        const urlParams = new URLSearchParams(hashQuery)
        
        Object.keys(params).forEach(key => {
          if (params[key] !== undefined && params[key] !== null) {
            urlParams.set(key, params[key])
          }
        })
        
        newUrl = `${hashPath}?${urlParams.toString()}`
      } else {
        // 普通路由：更新search参数
        const url = new URL(window.location)
        Object.keys(params).forEach(key => {
          if (params[key] !== undefined && params[key] !== null) {
            url.searchParams.set(key, params[key])
          }
        })
        newUrl = url.toString()
      }
      
      console.log('🔄 准备用新URL刷新页面:', newUrl)
      
      // 直接用新URL刷新页面
      window.location.href = newUrl
      window.location.reload()
    } catch (error) {
      console.warn('Failed to refresh with new URL:', error)
      // 如果出错，回退到普通刷新
      window.location.reload()
    }
  }

  checkForExistingWindow(params, timeout = 1000) {
    return new Promise((resolve) => {
      if (!this.channel) {
        console.warn('❌ 广播通道未初始化，无法检查窗口复用')
        resolve(false)
        return
      }

      const message = {
        type: 'check-window',
        params: params,
        timestamp: Date.now()
      }

      console.log('📡 发送窗口检查消息:', message)

      // 设置超时
      const timeoutId = setTimeout(() => {
        this.channel.removeEventListener('message', messageHandler)
        console.log('⏰ 窗口检查超时，未找到可复用窗口')
        resolve(false)
      }, timeout)

      // 消息处理器
      const messageHandler = (event) => {
        console.log('📨 收到响应消息:', event.data)
        if (event.data.type === 'window-available' && 
            event.data.params.action === params.action) {
          clearTimeout(timeoutId)
          this.channel.removeEventListener('message', messageHandler)
          console.log('✅ 找到可复用窗口:', event.data)
          
          resolve({
            windowId: event.data.windowId,
            params: event.data.params
          })
        }
      }

      // 添加消息监听器
      this.channel.addEventListener('message', messageHandler)
      
      // 发送检查消息
      this.channel.postMessage(message)
    })
  }

  requestFocus(targetWindowId) {
    if (!this.channel) return

    this.channel.postMessage({
      type: 'focus-window',
      windowId: targetWindowId,
      timestamp: Date.now()
    })
  }

  requestUpdateParams(targetWindowId, params) {
    if (!this.channel) {
      console.warn('❌ 广播通道未初始化，无法发送参数更新请求')
      return
    }

    const message = {
      type: 'update-params',
      windowId: targetWindowId,
      params: params,
      timestamp: Date.now()
    }
    
    console.log('📡 发送参数更新请求到窗口:', targetWindowId)
    console.log('📡 更新参数:', params)
    this.channel.postMessage(message)
  }

  extractParamsFromUrl(url) {
    try {
      if (!url) return {}
      
      // 支持hash路由
      let queryString = ''
      if (url.includes('#')) {
        const hashPart = url.split('#')[1]
        if (hashPart.includes('?')) {
          queryString = hashPart.split('?')[1]
        }
      } else if (url.includes('?')) {
        queryString = url.split('?')[1]
      }
      
      if (!queryString) return {}
      
      const urlParams = new URLSearchParams(queryString)
      const params = {}
      
      // 提取所有参数
      for (const [key, value] of urlParams.entries()) {
        params[key] = value
      }
      
      console.log('🔍 从URL解析参数:', params)
      return params
    } catch (error) {
      console.warn('解析URL参数失败:', error)
      return {}
    }
  }

  cleanup() {
    if (this.channel) {
      this.channel.close()
      this.channel = null
    }
    this.isSetup = false
  }

  // 获取当前状态信息
  getStatus() {
    return {
      channelName: this.channelName,
      channel: !!this.channel,
      windowId: this.windowId,
      isSetup: this.isSetup
    }
  }
}

// 创建全局实例
const windowReuseManager = new WindowReuseManager()

export default windowReuseManager 