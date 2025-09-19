/**
 * 通用方法Mixin
 */
export const commonMixin = {
  methods: {
    gen_dynamic_tags(str) {
      if (str) {
        try {
          return window.gen_dynamic_tags(JSON.parse(str))
        } catch (error) {
          return ''
        }
      }
      return ''
    },
    gen_highlight(str) {
      if (str) {
        try {
          return window.gen_highlight(JSON.parse(str))
        } catch (error) {
          return ''
        }
      }
      return ''
    },
    /**
     * 处理分页大小变化
     * @param {number} val - 新的分页大小
     */
    handleSizeChange(val) {
      this.pagination.page_size = val
      this.pagination.page = 1
      this.fetchData()
    },

    /**
     * 处理页码变化
     * @param {number} newPage - 新的页码
     */
    handlePageChange(newPage) {
      this.pagination.page = newPage
      this.fetchData()
    },

    /**
     * 处理排序变化
     * @param {Object} sortInfo - 排序信息
     * @param {string} sortInfo.prop - 排序字段
     * @param {string} sortInfo.order - 排序方向
     */
    handleSortChange({ prop, order }) {
      this.filters.sort_by = prop
      this.filters.sort_order = order === 'ascending' ? 'asc' : 'desc'
      this.fetchData()
    },

    /**
     * 获取相似度标签类型
     * @param {number} similarity - 相似度值
     * @returns {string} 标签类型
     */
    getSimilarityTagType(similarity) {
      if (similarity >= 0.9) return 'success'
      if (similarity >= 0.8) return 'warning'
      if (similarity >= 0.7) return 'info'
      return 'danger'
    },

    /**
     * 格式化特性
     * @param {string} texing - 特性JSON字符串
     * @returns {string} 特性名称
     */
    formatTexing(texing) {
      if (!texing) return ''
      try {
        const texingObj = JSON.parse(texing)
        return texingObj.name || ''
      } catch (e) {
        return ''
      }
    },
    /**
     * 格式化日期
     * @param {number} timestamp - 时间戳
     * @returns {string} 格式化后的日期
     */
    formatDate(timestamp) {
      if (!timestamp) return '-'
      const date = new Date(timestamp * 1000)
      return date.toLocaleString('zh-CN')
    },
    /**
     * 获取带颜色的数字
     * @param {number} val - 数字
     * @param {Array} range - 范围 [min, max]
     * @returns {string} 带颜色的数字HTML
     */
    getColorNumber(val, range = [0, 1]) {
      if (!val) return '-'
      val = +val
      const [min, max] = range

      if (!val || val < min || val > max) {
        return '-'
      }

      var cls = 'number-low'
      const stepRange = max - min
      if (val >= min && val < min + stepRange * 0.25) {
        cls = 'number-low'
      } else if (val >= min + stepRange * 0.25 && val < min + stepRange * 0.5) {
        cls = 'number-medium'
      } else if (val >= min + stepRange * 0.5 && val < min + stepRange * 0.75) {
        cls = 'number-high'
      } else if (val >= min + stepRange * 0.75 && val <= max) {
        cls = 'number-perfect'
      }

      return `<span class="${cls}">${val}</span>`
    },

    /**
     * 格式化装备价格
     * @param {number} price - 价格（分为单位）
     * @returns {string} 格式化后的价格
     */
    formatPrice(price) {
      const priceFloat = parseFloat(price / 100)
      if (!priceFloat) return '-'
      return window.get_color_price ? window.get_color_price(priceFloat) : `${priceFloat}元`
    },
    /**
     * 格式化完整价格信息（包括跨服费用）
     * @param {Object} item - 物品对象
     * @param {boolean|string} simple - 是否简化显示
     * @returns {string} 格式化后的完整价格信息
     */
    formatFullPrice(item, simple = false) {
      let basePrice 
      if(typeof item === 'object'){
        basePrice = this.formatPrice(item.price)
      }else{
        basePrice = this.formatPrice(item)
      }

      // 检查是否有登录信息和跨服费用
      if (!window.LoginInfo || !window.LoginInfo.login) {
        return basePrice
      }

      const crossServerPoundage = item.cross_server_poundage || 0
      const fairShowPoundage = item.fair_show_poundage || 0

      if (!crossServerPoundage || (simple && simple !== 'cross')) {
        if (simple && simple == 'cross') {
          return ''
        }
        return basePrice
      }

      let additionalFeeHtml = ''

      if (item.pass_fair_show == 1) {
        // 跨服费
        const crossFee = parseFloat(crossServerPoundage / 100)
        additionalFeeHtml = `<div class="f12px" style="color: #666;">跨服费<span class="p1000">￥${crossFee}</span></div>`
      } else {
        // 信息费（跨服费 + 预订费）
        const totalFee = parseFloat((crossServerPoundage + fairShowPoundage) / 100)
        additionalFeeHtml = `<div class="f12px" style="color: #666;">信息费<span class="p1000">￥${totalFee}</span></div>`
      }

      if (simple && simple == 'cross') {
        return additionalFeeHtml
      }
      return basePrice + additionalFeeHtml
    },
    /**
     * 获取CBG链接（通用版本，支持不同类型）
     * @param {string} eid - 装备/召唤兽ID
     * @param {string} type - 类型：'equip', 'pet', 'role'
     * @returns {string} CBG链接
     */
    getCBGLinkByType(eid, type = 'equip') {
      if (!eid) return '#'

      const serverId = eid.split('-')[1]

      switch (type) {
        // case 'pet':
        //   return `https://xyq-m.cbg.163.com/cgi/mweb/equip/${serverId}/${eid}`
        // case 'role':
        //   return `https://xyq.cbg.163.com/equip?s=${serverId}&eid=${eid}`
        // case 'equip':
        default:
          return `https://xyq-m.cbg.163.com/cgi/mweb/equip/${serverId}/${eid}`
      }
    },
    /**
     * 防抖函数
     * @param {Function} func - 要防抖的函数
     * @param {number} wait - 等待时间（毫秒）
     * @returns {Function} 防抖后的函数
     */
    debounce(func, wait = 300) {
      let timeout
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout)
          func.apply(this, args)
        }
        clearTimeout(timeout)
        timeout = setTimeout(later, wait)
      }
    },

    /**
     * 节流函数
     * @param {Function} func - 要节流的函数
     * @param {number} limit - 限制时间（毫秒）
     * @returns {Function} 节流后的函数
     */
    throttle(func, limit = 300) {
      let inThrottle
      return function executedFunction(...args) {
        if (!inThrottle) {
          func.apply(this, args)
          inThrottle = true
          setTimeout(() => (inThrottle = false), limit)
        }
      }
    },

    /**
     * 表格行样式类名
     * @param {Object} params - 参数对象
     * @param {Object} params.row - 行数据
     * @param {number} params.rowIndex - 行索引
     * @returns {string} 样式类名
     */
    tableRowClassName({ row }) {
      // 可以根据业务需求自定义行样式
      if (row.is_special) {
        return 'warning-row'
      }
      return ''
    },

    /**
     * 获取图片URL（统一图片URL生成方法）
     * @param {string} imageName - 图片名称
     * @param {string} size - 图片尺寸 (small/big)
     * @returns {string} 完整的图片URL
     */
    getImageUrl(imageName, size = 'small') {
      if (!imageName) return ''

      // 如果已经是完整URL，直接返回
      if (imageName.startsWith('http://') || imageName.startsWith('https://')) {
        if(size==='big'&&imageName.includes('/images/equip/small/')){
          return imageName.replace('/images/equip/small/', '/images/big/')
        }
        return imageName
      }

      // 拼接CBG资源URL
      return `https://cbg-xyq.res.netease.com/images/${size}/${imageName}`
    }
  }
}

