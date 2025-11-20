import axios from 'axios'
import { Notification } from 'element-ui'

// 判断是否为Chrome插件环境
const isChromeExtension = typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id

// 根据环境设置不同的baseURL
const baseURL = isChromeExtension ? 'http://localhost:5000/api/v1' : '/api/v1'
// const baseURL = isChromeExtension ? 'http://xyq.lingtong.xyz/api/v1' : '/api/v1'

// 缓存 fingerprint cookie
let cachedFingerprint = ''
let fingerprintCacheTime = 0
const FINGERPRINT_CACHE_DURATION = 5 * 60 * 1000 // 缓存5分钟

// 缓存 auth token
let cachedAuthToken = null
let authTokenCacheTime = 0
const AUTH_TOKEN_CACHE_DURATION = 5 * 60 * 1000 // 缓存5分钟

// 从chrome.storage获取auth token
const getAuthTokenFromStorage = async () => {
  if (!isChromeExtension) {
    return null
  }
  
  return new Promise((resolve) => {
    chrome.storage.local.get(['auth_token'], (result) => {
      if (result.auth_token) {
        cachedAuthToken = result.auth_token
        authTokenCacheTime = Date.now()
        resolve(result.auth_token)
      } else {
        resolve(null)
      }
    })
  })
}

// 获取auth token（同步方法，返回缓存值）
const getAuthToken = () => {
  // 如果缓存过期，异步更新（不阻塞请求）
  const now = Date.now()
  if (now - authTokenCacheTime > AUTH_TOKEN_CACHE_DURATION) {
    getAuthTokenFromStorage().catch(err => {
      console.error('更新 auth token 缓存失败:', err)
    })
  }
  
  return cachedAuthToken
}

// 初始化auth token（供外部调用）
export const initAuthToken = async () => {
  if (isChromeExtension) {
    cachedAuthToken = await getAuthTokenFromStorage()
  }
}

// 清除auth token
export const clearAuthToken = () => {
  cachedAuthToken = null
  authTokenCacheTime = 0
  if (isChromeExtension) {
    chrome.storage.local.remove(['auth_token', 'user_info'])
  }
}

// 从目标窗口获取 fingerprint cookie
const getFingerprintCookieFromTarget = async () => {
  if (!isChromeExtension) {
    return ''
  }

  try {
    // 获取当前活动标签页
    const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true })
    
    if (!activeTab || !activeTab.url || !activeTab.url.includes('cbg.163.com')) {
      return ''
    }

    // 使用 Chrome Debugger API 获取 cookies
    const result = await chrome.debugger.sendCommand(
      { tabId: activeTab.id },
      'Network.getAllCookies'
    )

    const cookies = Array.isArray(result?.cookies) ? result.cookies : []
    
    // 查找 domain 包含 xyq.cbg.163.com 且 name 为 fingerprint 的 cookie
    const fingerprintCookie = cookies.find(
      cookie => cookie.name === 'fingerprint' && 
                cookie.domain && 
                cookie.domain.includes('xyq.cbg.163.com')
    )

    if (fingerprintCookie) {
      cachedFingerprint = fingerprintCookie.value || ''
      fingerprintCacheTime = Date.now()
      return cachedFingerprint
    }

    return ''
  } catch (error) {
    console.error('获取 fingerprint cookie 失败:', error)
    return ''
  }
}

// 获取 fingerprint cookie（同步方法，返回缓存值）
const getFingerprintCookie = () => {
  // 如果缓存过期，异步更新（不阻塞请求）
  const now = Date.now()
  if (now - fingerprintCacheTime > FINGERPRINT_CACHE_DURATION) {
    getFingerprintCookieFromTarget().catch(err => {
      console.error('更新 fingerprint cookie 缓存失败:', err)
    })
  }
  
  return cachedFingerprint
}

// 初始化 fingerprint cookie（供外部调用）
export const initFingerprintCookie = async () => {
  if (isChromeExtension) {
    await getFingerprintCookieFromTarget()
  }
}

// 创建axios实例
const request = axios.create({
  baseURL: baseURL, // API基础路径
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  async config => {
    // 在发送请求之前做些什么
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    
    // 添加fingerprint
    const fingerprint = getFingerprintCookie()||'admin'
    if (fingerprint) {
      config.headers['X-Fingerprint'] = fingerprint
    }
    
    // 添加auth token（排除登录和注册接口）
    if (!config.url.includes('/auth/login') && !config.url.includes('/auth/register')) {
      let token = null
      
      // Chrome扩展环境：从chrome.storage获取token
      if (isChromeExtension) {
        token = getAuthToken()
      } else {
        // Web应用：从localStorage获取token
        token = localStorage.getItem('auth_token')
      }
      
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`
      }
    }
    
    return config
  },
  error => {
    // 对请求错误做些什么
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    // 对响应数据做些什么
    const { data } = response
    
    return data
  },
  error => {
    // 对响应错误做些什么
    console.error('响应错误:', error)
    
    let message = '请求失败'
    let responseData = null
    
    if (error.response) {
      // 服务器响应了错误状态码
      const { status, data } = error.response
      message = data.message || `请求失败 (${status})`
      
      // 如果后端返回了data字段，使用后端的data；否则使用后端的完整响应
      if (data.data !== undefined) {
        responseData = data.data
      } else {
        responseData = data
      }
      
      // 如果是401未授权错误，清除token并触发登录
      if (status === 401) {
        if (isChromeExtension) {
          clearAuthToken()
          // 触发登录事件
          if (typeof window !== 'undefined' && window.dispatchEvent) {
            window.dispatchEvent(new CustomEvent('auth-required'))
          }
        } else {
          // Web应用：清除localStorage并跳转到登录页
          localStorage.removeItem('auth_token')
          localStorage.removeItem('user_info')
          // 触发全局事件，让Header等组件可以监听
          if (typeof window !== 'undefined' && window.dispatchEvent) {
            window.dispatchEvent(new CustomEvent('auth-required'))
          }
        }
      }
      
      console.log('错误响应数据:', responseData)
    } else if (error.request) {
      // 请求已发出但没有收到响应
      message = '网络错误，请检查网络连接'
    } else {
      // 其他错误
      message = error.message || '请求失败'
    }
    
    Notification.error({
      title: '错误',
      message: message
    })
    
    return {
      code: error.response?.status || 500,
      data: responseData,  // 使用后端返回的data，而不是强制设置为null
      message: message,
      timestamp: Date.now()
    }
  }
)

// 导出封装的请求方法
export const api = {
  // GET请求
  get(url, params = {}) {
    return request.get(url, { params })
  },
  
  // POST请求
  post(url, data = {}) {
    return request.post(url, data)
  },
  
  // PUT请求
  put(url, data = {}) {
    return request.put(url, data)
  },
  
  // DELETE请求
  delete(url, params = {}) {
    return request.delete(url, { params })
  },
  
  // 下载文件
  download(url, params = {}, filename) {
    return request.get(url, { 
      params,
      responseType: 'blob'
    }).then(response => {
      if (response.code === 200) {
        // 创建下载链接
        const blob = new Blob([response.data])
        const downloadUrl = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = filename || 'download'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(downloadUrl)
      }
      return response
    })
  }
}

export default request 