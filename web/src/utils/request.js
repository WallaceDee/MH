import axios from 'axios'
import { Message } from 'element-ui'

// 创建axios实例
const request = axios.create({
  baseURL: '/api/v1', // API基础路径
  timeout: 10000, // 请求超时时间
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
    if (error.response) {
      // 服务器响应了错误状态码
      const { status, data } = error.response
      message = data.message || `请求失败 (${status})`
      console.log(message,'messagemessagemessagemessagemessage')
    } else if (error.request) {
      // 请求已发出但没有收到响应
      message = '网络错误，请检查网络连接'
    } else {
      // 其他错误
      message = error.message || '请求失败'
    }
    
    Message.error(message)
    return {
      success: false,
      message
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
      if (response.success !== false) {
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