import axios from 'axios'
import { Notification } from 'element-ui'

// 判断是否为Chrome插件环境
const isChromeExtension = typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id

// 根据环境设置不同的baseURL
const baseURL = isChromeExtension ? 'http://xyq.lingtong.xyz/cbg/api/v1' : '/api/v1'

// 创建axios实例
const request = axios.create({
  baseURL: baseURL, // API基础路径
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
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