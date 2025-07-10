import { api } from '@/utils/request'

/**
 * 爬虫相关API
 */
export const spiderApi = {
  /**
   * 获取任务状态
   * @returns {Promise}
   */
  getStatus() {
    return api.get('/spider/status')
  },

  /**
   * 获取爬虫配置
   * @returns {Promise}
   */
  getConfig() {
    return api.get('/spider/config')
  },

  /**
   * 启动基础爬虫
   * @param {Object} data - 爬虫参数
   * @returns {Promise}
   */
  startBasic(data) {
    return api.post('/spider/basic/start', data)
  },

  /**
   * 启动角色爬虫
   * @param {Object} data - 角色爬虫参数
   * @returns {Promise}
   */
  startRole(data) {
    return api.post('/spider/role/start', data)
  },

  /**
   * 启动装备爬虫
   * @param {Object} data - 装备爬虫参数
   * @returns {Promise}
   */
  startEquip(data) {
    return api.post('/spider/equip/start', data)
  },

  /**
   * 启动召唤兽爬虫
   * @param {Object} data - 召唤兽爬虫参数
   * @returns {Promise}
   */
  startPet(data) {
    return api.post('/spider/pet/start', data)
  },

  /**
   * 启动代理爬虫
   * @param {Object} data - 代理爬虫参数
   * @returns {Promise}
   */
  startProxy(data) {
    return api.post('/spider/proxy/start', data)
  },

  /**
   * 管理代理
   * @param {Object} data - 代理管理参数
   * @returns {Promise}
   */
  manageProxy(data = {}) {
    return api.post('/spider/proxy/manage', data)
  },

  /**
   * 运行测试
   * @param {Object} data - 测试参数
   * @returns {Promise}
   */
  runTest(data = {}) {
    return api.post('/spider/test/run', data)
  },

  /**
   * 停止任务
   * @returns {Promise}
   */
  stopTask() {
    return api.post('/spider/task/stop')
  },

  /**
   * 重置任务状态
   * @returns {Promise}
   */
  resetTask() {
    return api.post('/spider/task/reset')
  },

  /**
   * 获取任务日志
   * @param {Object} params - 参数
   * @param {number} params.lines - 返回的日志行数，默认100
   * @param {string} params.type - 日志类型 (current/recent)，默认current
   * @returns {Promise}
   */
  getLogs(params = {}) {
    return api.get('/spider/logs', params)
  },

  /**
   * 从日志文件解析进度信息
   * @param {Object} params - 参数
   * @param {string} params.type - 爬虫类型 (role/equip/pet/proxy)，默认role
   * @returns {Promise}
   */
  getProgress(params = {}) {
    return api.get('/spider/progress', params)
  },

  /**
   * 流式获取实时日志
   * @returns {EventSource}
   */
  streamLogs() {
    // 使用完整的URL，确保连接到正确的后端
    const baseURL = process.env.NODE_ENV === 'development' 
      ? 'http://localhost:5000' 
      : window.location.origin
    return new EventSource(`${baseURL}/api/v1/spider/logs/stream`)
  },

  /**
   * 获取文件列表
   * @returns {Promise}
   */
  getFiles() {
    return api.get('/spider/files')
  },

  /**
   * 获取日志文件列表
   * @returns {Promise}
   */
  getLogFiles() {
    return api.get('/spider/logs/files')
  },

  /**
   * 下载文件
   * @param {string} filename - 文件名
   * @returns {Promise}
   */
  downloadFile(filename) {
    return api.download(`/spider/download/${filename}`, {}, filename)
  }
} 