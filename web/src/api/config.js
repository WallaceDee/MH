import request from '@/utils/request'

// 配置管理API
export const configApi = {
  // 获取所有搜索参数配置
  getSearchParams() {
    return request({
      url: '/config/search-params',
      method: 'get'
    })
  },

  // 根据类型获取特定的搜索参数配置
  getSearchParamByType(paramType) {
    return request({
      url: `/config/search-params/${paramType}`,
      method: 'get'
    })
  },

  // 更新特定类型的搜索参数配置
  updateSearchParam(paramType, data) {
    return request({
      url: `/config/search-params/${paramType}`,
      method: 'post',
      data
    })
  },

  // 获取配置文件列表
  getConfigFiles() {
    return request({
      url: '/config/files',
      method: 'get'
    })
  }
} 