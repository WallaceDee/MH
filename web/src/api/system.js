import { api } from '@/utils/request'

/**
 * 系统相关API
 */
export const systemApi = {
  /**
   * 获取系统信息
   * @returns {Promise}
   */
  getSystemInfo() {
    return api.get('/system/info')
  },

  /**
   * 获取文件列表
   * @returns {Promise}
   */
  getFiles() {
    return api.get('/system/files')
  },

  /**
   * 下载文件
   * @param {string} filename - 文件名
   * @returns {Promise}
   */
  downloadFile(filename) {
    return api.get(`/system/files/${filename}/download`)
  },

  /**
   * 获取热门服务器列表
   * @returns {Promise} 直接返回服务器分组数组，无包装格式
   */
  getHotServers() {
    return api.get('/system/config-file/hot_server_list.json')
  },

  
  /**
   * 获取限量锦衣祥瑞配置
   * @returns {Promise} 直接返回限量锦衣祥瑞配置
   */
  getLimitedSkinConfig() {
    return api.get('/system/config-file/ex_avt_value.jsonc')
  },

  /**
   * 获取所有搜索参数配置
   * @returns {Promise}
   */
  getSearchParams() {
    return api.get('/system/config/search-params')
  },

  /**
   * 根据类型获取特定的搜索参数配置
   * @param {string} paramType - 参数类型 (role, equip_normal, equip_lingshi, equip_pet, equip_pet_equip, pet)
   * @returns {Promise}
   */
  getSearchParamByType(paramType) {
    return api.get(`/system/config/search-params/${paramType}`)
  },

  /**
   * 更新特定类型的搜索参数配置
   * @param {string} paramType - 参数类型
   * @param {Object} data - 配置数据
   * @returns {Promise}
   */
  updateSearchParam(paramType, data) {
    return api.post(`/system/config/search-params/${paramType}`, data)
  }
} 