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
  },

  /**
   * 获取市场数据状态
   * @returns {Promise}
   */
  getMarketDataStatus() {
    return api.get('/system/market-data/status')
  },

  /**
   * 获取市场数据详细分析
   * @returns {Promise}
   */
  getMarketDataAnalysis() {
    return api.get('/system/market-data/analysis')
  },
  /**
   * 刷新市场数据
   * @returns {Promise}
   */
  refreshMarketData() {
    return api.post('/system/market-data/refresh', {
      force_refresh: false,
      use_cache: true
    })
  },

  /**
   * 刷新全量缓存（不使用缓存，完全重新加载）
   * @returns {Promise}
   */
  refreshFullCache() {
    return api.post('/system/market-data/refresh', {
      force_refresh: true,
      use_cache: true
    })
  },

  /**
   * 获取缓存状态
   * @returns {Promise}
   */
  getCacheStatus() {
    return api.get('/system/market-data/cache-status')
  },

  /**
   * 获取装备缓存状态
   * @returns {Promise}
   */
  getEquipmentCacheStatus() {
    return api.get('/system/equipment/cache-status')
  },

  /**
   * 刷新装备数据（使用缓存）
   * @returns {Promise}
   */
  refreshEquipmentData() {
    return api.post('/system/equipment/refresh', {
      force_refresh: false,
      use_cache: true
    })
  },

  /**
   * 刷新装备全量缓存（不使用缓存，完全重新加载）
   * @returns {Promise}
   */
  refreshEquipmentFullCache() {
    return api.post('/system/equipment/refresh', {
      force_refresh: true,
      use_cache: true
    })
  },

  /**
   * 获取装备市场数据状态
   * @returns {Promise}
   */
  getEquipmentMarketDataStatus() {
    return api.get('/system/market-data/equipment/status')
  },

  getRedisStatus() {
    return api.get('/system/redis/status')
  },


  /**
   * 获取装备刷新进度状态
   * @returns {Promise}
   */
  getEquipmentRefreshStatus() {
    return api.get('/system/equipment/refresh-status')
  }
} 