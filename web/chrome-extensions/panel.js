/******/ (function() { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/chrome-extensions/DevToolsPanel.vue?vue&type=script&lang=js":
/*!**********************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/chrome-extensions/DevToolsPanel.vue?vue&type=script&lang=js ***!
  \**********************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var core_js_modules_es_array_push_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! core-js/modules/es.array.push.js */ "./node_modules/core-js/modules/es.array.push.js");
/* harmony import */ var core_js_modules_es_array_push_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_array_push_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var core_js_modules_es_iterator_constructor_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! core-js/modules/es.iterator.constructor.js */ "./node_modules/core-js/modules/es.iterator.constructor.js");
/* harmony import */ var core_js_modules_es_iterator_constructor_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_iterator_constructor_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var core_js_modules_es_iterator_for_each_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! core-js/modules/es.iterator.for-each.js */ "./node_modules/core-js/modules/es.iterator.for-each.js");
/* harmony import */ var core_js_modules_es_iterator_for_each_js__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_iterator_for_each_js__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var core_js_modules_es_set_difference_v2_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! core-js/modules/es.set.difference.v2.js */ "./node_modules/core-js/modules/es.set.difference.v2.js");
/* harmony import */ var core_js_modules_es_set_difference_v2_js__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_set_difference_v2_js__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var core_js_modules_es_set_intersection_v2_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! core-js/modules/es.set.intersection.v2.js */ "./node_modules/core-js/modules/es.set.intersection.v2.js");
/* harmony import */ var core_js_modules_es_set_intersection_v2_js__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_set_intersection_v2_js__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var core_js_modules_es_set_is_disjoint_from_v2_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! core-js/modules/es.set.is-disjoint-from.v2.js */ "./node_modules/core-js/modules/es.set.is-disjoint-from.v2.js");
/* harmony import */ var core_js_modules_es_set_is_disjoint_from_v2_js__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_set_is_disjoint_from_v2_js__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var core_js_modules_es_set_is_subset_of_v2_js__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! core-js/modules/es.set.is-subset-of.v2.js */ "./node_modules/core-js/modules/es.set.is-subset-of.v2.js");
/* harmony import */ var core_js_modules_es_set_is_subset_of_v2_js__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_set_is_subset_of_v2_js__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var core_js_modules_es_set_is_superset_of_v2_js__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! core-js/modules/es.set.is-superset-of.v2.js */ "./node_modules/core-js/modules/es.set.is-superset-of.v2.js");
/* harmony import */ var core_js_modules_es_set_is_superset_of_v2_js__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_set_is_superset_of_v2_js__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var core_js_modules_es_set_symmetric_difference_v2_js__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! core-js/modules/es.set.symmetric-difference.v2.js */ "./node_modules/core-js/modules/es.set.symmetric-difference.v2.js");
/* harmony import */ var core_js_modules_es_set_symmetric_difference_v2_js__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_set_symmetric_difference_v2_js__WEBPACK_IMPORTED_MODULE_8__);
/* harmony import */ var core_js_modules_es_set_union_v2_js__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! core-js/modules/es.set.union.v2.js */ "./node_modules/core-js/modules/es.set.union.v2.js");
/* harmony import */ var core_js_modules_es_set_union_v2_js__WEBPACK_IMPORTED_MODULE_9___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_set_union_v2_js__WEBPACK_IMPORTED_MODULE_9__);
/* harmony import */ var _components_RoleInfo_RoleImage_vue__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! @/components/RoleInfo/RoleImage.vue */ "./src/components/RoleInfo/RoleImage.vue");











/* harmony default export */ __webpack_exports__["default"] = ({
  name: 'DevToolsPanel',
  data() {
    return {
      recommendData: [],
      expandedItems: [],
      processedRequests: new Set(),
      // 记录已处理的请求ID
      devtoolsConnected: false,
      // DevTools Protocol连接状态
      connectionStatus: '检查中...',
      // 连接状态描述
      connectionCheckTimer: null // 连接检查定时器
    };
  },
  components: {
    RoleImage: _components_RoleInfo_RoleImage_vue__WEBPACK_IMPORTED_MODULE_10__["default"]
  },
  computed: {},
  mounted() {
    this.initMessageListener();
    this.checkConnectionStatus();

    // // 设置定时检查（每5秒检查一次）
    // this.connectionCheckTimer = setInterval(() => {
    //   this.checkConnectionStatus()
    // }, 5000)
  },
  beforeDestroy() {
    // 移除Chrome消息监听器
    this.removeMessageListener();
    // 清理定时器
    if (this.connectionCheckTimer) {
      clearInterval(this.connectionCheckTimer);
      this.connectionCheckTimer = null;
    }
    // 清理组件状态
    this.recommendData = [];
    this.expandedItems = [];
  },
  methods: {
    nextPage() {
      // 通过Chrome调试API查找并点击页面上的分页器
      this.clickPageButton('next');
    },
    prevPage() {
      // 通过Chrome调试API查找并点击页面上的分页器
      this.clickPageButton('prev');
    },
    getPageInfo() {
      // 获取当前分页器信息
      this.getPagerInfo();
    },
    reconnectDevTools() {
      // 重新连接DevTools
      this.connectionStatus = '重连中...';
      this.checkConnectionStatus();
      this.$message.info('正在尝试重新连接DevTools...');
    },
    async clickPageButton(direction) {
      try {
        // 获取当前活动标签页
        const [activeTab] = await chrome.tabs.query({
          active: true,
          currentWindow: true
        });
        if (!activeTab || !activeTab.url.includes('cbg.163.com')) {
          this.$message.warning('请先访问梦幻西游藏宝阁页面');
          return;
        }

        // 检查Chrome调试API连接状态
        if (!this.devtoolsConnected) {
          this.$message.warning('DevTools连接已断开，请重新加载页面');
          return;
        }

        // 通过Chrome调试API执行页面JavaScript代码
        const result = await chrome.debugger.sendCommand({
          tabId: activeTab.id
        }, 'Runtime.evaluate', {
          expression: `
              (function() {
                try {
                  // 查找id为pager的div
                  const pagerDiv = document.getElementById('pager')
                  if (!pagerDiv) {
                    return 'ERROR:未找到分页器元素'
                  }
                  
                  let targetButton = null
                  const isNext = '${direction}' === 'next'
                  
                  if (isNext) {
                    // 查找下一页按钮 - 根据实际HTML格式优化
                    // 1. 优先查找包含"下一页"文本的链接
                    const allLinks = pagerDiv.querySelectorAll('a')
                    for (let link of allLinks) {
                      const text = link.textContent.trim()
                      if (text === '下一页') {
                        targetButton = link
                        break
                      }
                    }
                    
                    // 2. 如果没找到"下一页"，查找包含goto函数的链接（排除当前页）
                    if (!targetButton) {
                      for (let link of allLinks) {
                        const href = link.getAttribute('href')
                        const text = link.textContent.trim()
                        // 查找包含goto且不是当前页的链接
                        if (href && href.includes('goto(') && !link.classList.contains('on')) {
                          // 获取当前页码
                          const currentPageLink = pagerDiv.querySelector('a.on')
                          if (currentPageLink) {
                            const currentPageText = currentPageLink.textContent.trim()
                            const currentPage = parseInt(currentPageText)
                            const linkPage = parseInt(text)
                            // 如果链接页码大于当前页码，说明是下一页
                            if (!isNaN(linkPage) && linkPage > currentPage) {
                              targetButton = link
                              break
                            }
                          }
                        }
                      }
                    }
                  } else {
                    // 查找上一页按钮
                    const allLinks = pagerDiv.querySelectorAll('a')
                    
                    // 1. 优先查找包含"上一页"文本的链接
                    for (let link of allLinks) {
                      const text = link.textContent.trim()
                      if (text === '上一页') {
                        targetButton = link
                        break
                      }
                    }
                    
                    // 2. 如果没找到"上一页"，查找包含goto函数的链接（排除当前页）
                    if (!targetButton) {
                      for (let link of allLinks) {
                        const href = link.getAttribute('href')
                        const text = link.textContent.trim()
                        // 查找包含goto且不是当前页的链接
                        if (href && href.includes('goto(') && !link.classList.contains('on')) {
                          // 获取当前页码
                          const currentPageLink = pagerDiv.querySelector('a.on')
                          if (currentPageLink) {
                            const currentPageText = currentPageLink.textContent.trim()
                            const currentPage = parseInt(currentPageText)
                            const linkPage = parseInt(text)
                            // 如果链接页码小于当前页码，说明是上一页
                            if (!isNaN(linkPage) && linkPage < currentPage) {
                              targetButton = link
                              break
                            }
                          }
                        }
                      }
                    }
                  }
                  
                  if (!targetButton) {
                    return 'ERROR:未找到${direction === 'next' ? '下一页' : '上一页'}按钮'
                  }
                  
                  // 检查按钮是否可点击
                  if (targetButton.disabled || targetButton.classList.contains('disabled')) {
                    return 'ERROR:${direction === 'next' ? '下一页' : '上一页'}按钮不可点击，可能已到${direction === 'next' ? '最后一页' : '第一页'}'
                  }
                  
                  // 获取当前页码信息用于日志
                  const currentPageLink = pagerDiv.querySelector('a.on')
                  let currentPageInfo = ''
                  if (currentPageLink) {
                    const currentPageText = currentPageLink.textContent.trim()
                    currentPageInfo = ' (当前第' + currentPageText + '页)'
                  }
                  
                  // 点击按钮
                  targetButton.click()
                  return 'SUCCESS:已点击${direction === 'next' ? '下一页' : '上一页'}按钮' + currentPageInfo
                } catch (error) {
                  return 'ERROR:执行失败 - ' + error.message
                }
              })()
            `
        });

        // 处理Chrome调试API的返回结果
        if (result && result.result && result.result.value) {
          const message = result.result.value;
          if (message.startsWith('SUCCESS:')) {
            this.$message.success(message.substring(8)); // 移除"SUCCESS:"前缀
            console.log(`${direction === 'next' ? '下一页' : '上一页'}按钮点击成功`);
          } else if (message.startsWith('ERROR:')) {
            this.$message.warning(message.substring(6)); // 移除"ERROR:"前缀
            console.warn(`${direction === 'next' ? '下一页' : '上一页'}按钮点击失败:`, message);
          } else {
            this.$message.error('执行页面操作失败：未知返回结果');
            console.error('页面操作结果异常:', result);
          }
        } else {
          this.$message.error('执行页面操作失败');
          console.error('页面操作结果异常:', result);
        }
      } catch (error) {
        console.error(`点击${direction === 'next' ? '下一页' : '上一页'}按钮失败:`, error);

        // 检查是否是连接断开错误
        if (error.message && error.message.includes('Could not establish connection')) {
          this.devtoolsConnected = false;
          this.connectionStatus = '连接断开';
          this.$message.error('DevTools连接已断开，请重新加载页面或刷新扩展');
        } else {
          this.$message.error('操作失败: ' + error.message);
        }
      }
    },
    async getPagerInfo() {
      try {
        // 获取当前活动标签页
        const [activeTab] = await chrome.tabs.query({
          active: true,
          currentWindow: true
        });
        if (!activeTab || !activeTab.url.includes('cbg.163.com')) {
          this.$message.warning('请先访问梦幻西游藏宝阁页面');
          return;
        }

        // 检查Chrome调试API连接状态
        if (!this.devtoolsConnected) {
          this.$message.warning('DevTools连接已断开，请重新加载页面');
          return;
        }

        // 通过Chrome调试API执行页面JavaScript代码获取分页器信息
        const result = await chrome.debugger.sendCommand({
          tabId: activeTab.id
        }, 'Runtime.evaluate', {
          expression: `
              (function() {
                try {
                  // 查找id为pager的div
                  const pagerDiv = document.getElementById('pager')
                  if (!pagerDiv) {
                    return 'ERROR:未找到分页器元素'
                  }
                  
                  // 获取当前页码
                  const currentPageLink = pagerDiv.querySelector('a.on')
                  let currentPage = '未知'
                  if (currentPageLink) {
                    currentPage = currentPageLink.textContent.trim()
                  }
                  
                  // 获取所有页码链接
                  const allPageLinks = pagerDiv.querySelectorAll('a[href*="goto("]')
                  const pageNumbers = []
                  allPageLinks.forEach(link => {
                    const text = link.textContent.trim()
                    if (text.match(/^\d+$/)) {
                      pageNumbers.push(parseInt(text))
                    }
                  })
                  
                  // 计算总页数（取最大页码）
                  const totalPages = pageNumbers.length > 0 ? Math.max(...pageNumbers) : '未知'
                  
                  // 检查是否有上一页/下一页按钮
                  const hasPrev = pagerDiv.querySelector('a[href*="goto("]') && 
                                 pagerDiv.textContent.includes('上一页')
                  const hasNext = pagerDiv.querySelector('a[href*="goto("]') && 
                                 pagerDiv.textContent.includes('下一页')
                  
                  return 'SUCCESS:第' + currentPage + '页，共' + totalPages + '页 (上一页:' + (hasPrev ? '有' : '无') + ', 下一页:' + (hasNext ? '有' : '无') + ')'
                } catch (error) {
                  return 'ERROR:获取分页器信息失败 - ' + error.message
                }
              })()
            `
        });

        // 处理返回结果
        if (result && result.result && result.result.value) {
          const message = result.result.value;
          if (message.startsWith('SUCCESS:')) {
            this.$message.info(message.substring(8)); // 移除"SUCCESS:"前缀
            console.log('分页器信息获取成功:', message);
          } else if (message.startsWith('ERROR:')) {
            this.$message.warning(message.substring(6)); // 移除"ERROR:"前缀
            console.warn('分页器信息获取失败:', message);
          } else {
            this.$message.error('获取分页器信息失败：未知返回结果');
            console.error('分页器信息获取结果异常:', result);
          }
        } else {
          this.$message.error('获取分页器信息失败');
          console.error('分页器信息获取结果异常:', result);
        }
      } catch (error) {
        console.error('获取分页器信息失败:', error);

        // 检查是否是连接断开错误
        if (error.message && error.message.includes('Could not establish connection')) {
          this.devtoolsConnected = false;
          this.connectionStatus = '连接断开';
          this.$message.error('DevTools连接已断开，请重新加载页面或刷新扩展');
        } else {
          this.$message.error('操作失败: ' + error.message);
        }
      }
    },
    parserRoleData(data) {
      const roleInfo = new window.RoleInfoParser(data.large_equip_desc, {
        equip_level: data.equip_level
      });
      return roleInfo.result;
      // return {
      //   RoleInfoParser: roleInfo,
      //   roleInfo: roleInfo.result,
      //   accept_bargain: data.accept_bargain,
      //   collect_num: data.collect_num,
      //   dynamic_tags: data.dynamic_tags,
      //   eid: data.eid,
      //   highlight: data.highlight,
      //   is_split_independent_role: data.is_split_independent_role,
      //   is_split_main_role: data.is_split_main_role,
      //   large_equip_desc: data.large_equip_desc,
      //   level: data.level,
      //   other_info: data.other_info,
      //   school: data.school,
      //   seller_nickname: data.seller_nickname,
      //   server_name: data.server_name,
      //   serverid: data.serverid,
      //   price: data.price,
      //   sum_exp: data.sum_exp,
      //   create_time: data.create_time,
      //   update_time: data.create_time,
      //   all_equip_json: '',
      //   all_summon_json: '',
      //   split_price_desc: '',
      //   pet_price: '',
      //   equip_price: '',
      //   base_price: '',
      //   history_price: '',
      // }
    },
    parseListData(responseDataStr) {
      // 解析响应数据 Request.JSONP.request_map.request_数字(xxxx) 中的xxxx
      const match = responseDataStr.match(/Request\.JSONP\.request_map\.request_\d+\((.*)\)/);
      let templateJSONStr = '{}';
      if (match) {
        templateJSONStr = match[1];
      }
      try {
        const templateJSON = JSON.parse(templateJSONStr);
        return templateJSON;
      } catch (error) {
        console.error('解析响应数据失败:', error);
        return {};
      }
    },
    initMessageListener() {
      console.log('DevToolsPanel mounted, initializing listener');

      // 使用单例模式确保只有一个监听器
      if (typeof chrome !== 'undefined' && chrome.runtime) {
        // 如果已经有全局监听器，先移除
        if (window.cbgDevToolsListener) {
          chrome.runtime.onMessage.removeListener(window.cbgDevToolsListener);
        }

        // 创建全局监听器
        window.cbgDevToolsListener = (request, sender, sendResponse) => {
          console.log('DevToolsPanel received Chrome message:', request.action);
          this.handleChromeMessage(request, sender, sendResponse);
          sendResponse({
            success: true
          });
        };

        // 注册监听器
        chrome.runtime.onMessage.addListener(window.cbgDevToolsListener);
        console.log('Chrome message listener registered for DevToolsPanel');
      }
    },
    removeMessageListener() {
      // 移除Chrome消息监听器
      if (typeof chrome !== 'undefined' && chrome.runtime && window.cbgDevToolsListener) {
        chrome.runtime.onMessage.removeListener(window.cbgDevToolsListener);
        delete window.cbgDevToolsListener;
        console.log('Chrome message listener removed for DevToolsPanel');
      }
    },
    checkConnectionStatus() {
      // 检查Chrome扩展连接状态
      if (typeof chrome !== 'undefined' && chrome.runtime) {
        // 尝试发送ping消息检查连接
        chrome.runtime.sendMessage({
          action: 'ping'
        }, response => {
          if (chrome.runtime.lastError) {
            console.log('Chrome extension connection check failed:', chrome.runtime.lastError);
            this.devtoolsConnected = false;
            this.connectionStatus = '未连接';
          } else if (response && response.success) {
            console.log('Chrome extension connection check successful:', response);
            this.devtoolsConnected = true;
            this.connectionStatus = '已连接';
          } else {
            console.log('Chrome extension connection check failed: invalid response');
            this.devtoolsConnected = false;
            this.connectionStatus = '连接异常';
          }
        });
      } else {
        console.log('Chrome runtime not available');
        this.devtoolsConnected = false;
        this.connectionStatus = 'Chrome环境不可用';
      }
    },
    handleChromeMessage(request, sender, sendResponse) {
      switch (request.action) {
        case 'updateRecommendData':
          this.recommendData = request.data || [];

          // 只处理新完成的请求，避免重复处理
          if (this.recommendData && this.recommendData.length > 0) {
            this.recommendData.forEach(item => {
              if (item.status === 'completed' && item.responseData && item.url && item.requestId && !this.processedRequests.has(item.requestId)) {
                // 标记为已处理
                this.processedRequests.add(item.requestId);
                console.log(`开始处理新请求: ${item.requestId}`);

                // 调用解析响应数据接口
                this.$api.spider.parseResponse({
                  url: item.url,
                  response_text: item.responseData
                }).then(res => {
                  console.log(`请求 ${item.requestId} 解析结果:`, res);
                  if (res.code === 200) {
                    console.log(`请求 ${item.requestId} 数据解析成功:`, res.data);
                  } else {
                    console.error(`请求 ${item.requestId} 数据解析失败:`, res.message);
                  }
                }).catch(error => {
                  console.error(`请求 ${item.requestId} 解析请求失败:`, error);
                  // 解析失败时移除标记，允许重试
                  this.processedRequests.delete(item.requestId);
                });
              }
            });
          }
          break;
        case 'devtoolsConnected':
          this.devtoolsConnected = true;
          this.connectionStatus = '已连接';
          this.$message.success(request.message);
          break;
        case 'showDebuggerWarning':
          this.devtoolsConnected = false;
          this.connectionStatus = '连接冲突';
          this.$message.warning(request.message);
          break;
        case 'clearRecommendData':
          this.recommendData = [];
          this.expandedItems = [];
          this.processedRequests.clear();
          console.log('清空推荐数据和处理记录');
          break;
      }
    },
    clearData() {
      this.recommendData = [];
      this.expandedItems = [];
      // 通知background script清空数据
      if (typeof chrome !== 'undefined' && chrome.runtime) {
        chrome.runtime.sendMessage({
          action: 'clearRecommendData'
        });
      }
    },
    toggleResponse(index) {
      const expandedIndex = this.expandedItems.indexOf(index);
      if (expandedIndex > -1) {
        this.expandedItems.splice(expandedIndex, 1);
      } else {
        this.expandedItems.push(index);
      }
    },
    formatTime(timestamp) {
      if (!timestamp) return '';
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    }
  }
});

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=script&lang=js":
/*!******************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=script&lang=js ***!
  \******************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _utils_mixins_commonMixin__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @/utils/mixins/commonMixin */ "./src/utils/mixins/commonMixin.js");

/* harmony default export */ __webpack_exports__["default"] = ({
  name: 'EquipmentDesc',
  mixins: [_utils_mixins_commonMixin__WEBPACK_IMPORTED_MODULE_0__.commonMixin],
  props: {
    equipment: {
      type: Object,
      required: true
    },
    image: {
      type: Boolean,
      default: true
    },
    lockType: {
      type: Array,
      default: () => []
    },
    isBinding: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    parseEquipDesc(desc, default_style = '#Y') {
      if (!desc) return '';
      if (typeof window.parse_style_info === 'function') {
        return window.parse_style_info(desc, default_style);
      }
      return desc;
    }
  }
});

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentImage.vue?vue&type=script&lang=js":
/*!*******************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentImage.vue?vue&type=script&lang=js ***!
  \*******************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var core_js_modules_es_iterator_constructor_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! core-js/modules/es.iterator.constructor.js */ "./node_modules/core-js/modules/es.iterator.constructor.js");
/* harmony import */ var core_js_modules_es_iterator_constructor_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_iterator_constructor_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var core_js_modules_es_iterator_filter_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! core-js/modules/es.iterator.filter.js */ "./node_modules/core-js/modules/es.iterator.filter.js");
/* harmony import */ var core_js_modules_es_iterator_filter_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_iterator_filter_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _utils_mixins_commonMixin__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @/utils/mixins/commonMixin */ "./src/utils/mixins/commonMixin.js");
/* harmony import */ var _EquipmentDesc_vue__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./EquipmentDesc.vue */ "./src/components/EquipmentImage/EquipmentDesc.vue");




/* harmony default export */ __webpack_exports__["default"] = ({
  name: 'EquipmentImage',
  mixins: [_utils_mixins_commonMixin__WEBPACK_IMPORTED_MODULE_2__.commonMixin],
  components: {
    EquipmentDesc: _EquipmentDesc_vue__WEBPACK_IMPORTED_MODULE_3__["default"]
  },
  props: {
    image: {
      type: Boolean,
      default: true
    },
    equipment: {
      type: [Object, undefined]
    },
    size: {
      type: String,
      default: 'small'
    },
    width: {
      type: String,
      default: '50px'
    },
    height: {
      type: String,
      default: '50px'
    },
    cursor: {
      type: String,
      default: 'pointer'
    },
    placement: {
      type: String,
      default: 'right'
    },
    popoverWidth: {
      type: Number,
      default: 405
    },
    lockType: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      visible: false,
      features: {}
    };
  },
  computed: {
    isBinding() {
      // 玩家(\d+)专用
      const bindingPattern = /玩家(\d+)专用/;
      const match = this.equipment.large_equip_desc.match(bindingPattern);
      return Boolean(match);
    },
    rightLock() {
      return this.lockType.filter(item => item !== 9 && item !== 'protect' && item !== 'huoyue');
    },
    leftLock() {
      return this.lockType.filter(item => item === 9 || item === 'protect' || item === 'huoyue');
    },
    imageStyle() {
      return {
        display: 'block',
        width: this.width,
        height: this.height,
        cursor: this.cursor
      };
    }
  }
});

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/ItemPopover.vue?vue&type=script&lang=js":
/*!**********************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/ItemPopover.vue?vue&type=script&lang=js ***!
  \**********************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _EquipmentImage_EquipmentImage_vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../EquipmentImage/EquipmentImage.vue */ "./src/components/EquipmentImage/EquipmentImage.vue");

/* harmony default export */ __webpack_exports__["default"] = ({
  name: 'ItemPopover',
  components: {
    EquipmentImage: _EquipmentImage_EquipmentImage_vue__WEBPACK_IMPORTED_MODULE_0__["default"]
  },
  props: {
    placement: {
      type: String,
      default: 'right-start'
    },
    equipment: {
      type: Object,
      default: () => ({})
    }
  },
  computed: {
    lock_type() {
      return this.equipment?.lock_type || [];
    }
  }
});

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/PetDetail.vue?vue&type=script&lang=js":
/*!********************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/PetDetail.vue?vue&type=script&lang=js ***!
  \********************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var core_js_modules_es_array_push_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! core-js/modules/es.array.push.js */ "./node_modules/core-js/modules/es.array.push.js");
/* harmony import */ var core_js_modules_es_array_push_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_array_push_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _ItemPopover_vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./ItemPopover.vue */ "./src/components/RoleInfo/ItemPopover.vue");


/* harmony default export */ __webpack_exports__["default"] = ({
  name: 'PetDetail',
  props: {
    current_pet: {
      type: Object,
      required: true
    }
  },
  components: {
    ItemPopover: _ItemPopover_vue__WEBPACK_IMPORTED_MODULE_1__["default"]
  },
  computed: {
    // 召唤兽详细信息相关计算属性
    isShowNewLingli() {
      return this.current_pet && this.current_pet.iMagDam !== undefined && this.current_pet.iMagDef !== undefined;
    },
    evolSkillRows() {
      if (!this.current_pet || !this.current_pet.evol_skill_list) return [];
      const numPerLine = 4;
      const skills = this.current_pet.evol_skill_list;
      const skillNum = skills.length;
      let loopTimes = parseInt(skillNum / numPerLine) + (skillNum % numPerLine ? 1 : 0);
      loopTimes = loopTimes < 3 ? 3 : loopTimes;
      const rows = [];
      for (let i = 0; i < loopTimes; i++) {
        const items = skills.slice(i * numPerLine, (i + 1) * numPerLine);
        rows.push(items);
      }
      return rows;
    },
    petSkillRows() {
      if (!this.current_pet || !this.current_pet.skill_list) return [];
      const numPerLine = 4;
      const skills = this.current_pet.skill_list;
      const skillNum = skills.length;
      let loopTimes = parseInt(skillNum / numPerLine) + (skillNum % numPerLine ? 1 : 0);
      loopTimes = loopTimes < 3 ? 3 : loopTimes;
      if (this.current_pet.genius) {
        if (skillNum === numPerLine * loopTimes) {
          loopTimes = loopTimes + 1;
        }
      }
      const rows = [];
      for (let i = 0; i < loopTimes; i++) {
        const items = skills.slice(i * numPerLine, (i + 1) * numPerLine);
        rows.push(items);
      }
      return rows;
    }
  },
  methods: {
    // 解析样式信息
    parseStyleInfo(text) {
      if (!text) return '';
      // 这里可以添加样式解析逻辑，暂时直接返回文本
      return window.parse_style_info(text, '#Y');
    },
    // 技能提示相关方法
    showSkillTip(event, skill) {
      // 组装tip内容
      const tipData = {
        name: skill.name,
        desc: skill.desc || '',
        icon: skill.cifuIcon || skill.heightCifuIcon || skill.icon,
        isCifu: skill.cifuIcon || skill.heightCifuIcon ? true : false
      };
      // 渲染内容
      const box = this.$refs.RoleSkillTipsBox;
      if (!box) return;
      box.innerHTML = `<img class="tip-skill-icon" src="${tipData.icon}" referrerpolicy="no-referrer"><div class="skill-text"><p class="cYellow${tipData.isCifu ? ' cifu-name' : ''}">${tipData.name}</p>${window.parse_style_info ? window.parse_style_info(tipData.desc, '#Y') : tipData.desc}`;
      // 定位
      box.style.display = 'block';
      box.style.position = 'fixed';

      // 获取图标元素的位置信息
      const iconRect = event.target.getBoundingClientRect();

      // 计算tooltip的位置（图标正下方）
      let left = iconRect.left;
      let top = iconRect.bottom + 5; // 图标下方5px的位置

      // 处理超出窗口情况
      const boxWidth = 320;
      const boxHeight = 120;

      // 右边界检查
      if (left + boxWidth > window.innerWidth) {
        left = window.innerWidth - boxWidth - 10;
      }

      // 下边界检查，如果超出则显示在图标上方
      if (top + boxHeight > window.innerHeight) {
        top = iconRect.top - boxHeight - 5;
      }

      // 左边界检查
      if (left < 0) {
        left = 10;
      }

      // 上边界检查
      if (top < 0) {
        top = 10;
      }
      box.style.left = left + 'px';
      box.style.top = top + 'px';
      box.style.zIndex = 9999;
    },
    hideSkillTip() {
      const box = this.$refs.RoleSkillTipsBox;
      if (box) box.style.display = 'none';
    },
    // 专门处理内丹的tooltip
    showNeidanTip(event, item) {
      this.showSkillTip(event, item);
    },
    // 召唤兽详细信息相关方法
    getDictValue(obj, key, defaultValue) {
      if (!obj || typeof obj !== 'object') return defaultValue;
      return obj[key] !== undefined ? obj[key] : defaultValue;
    },
    getSummonColorDesc(summonColor) {
      // 这里需要实现get_summon_color_desc的逻辑
      // 暂时返回原值，实际项目中需要根据具体逻辑实现
      return summonColor || '无';
    }
  }
});

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/RoleImage.vue?vue&type=script&lang=js":
/*!********************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/RoleImage.vue?vue&type=script&lang=js ***!
  \********************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var core_js_modules_es_array_push_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! core-js/modules/es.array.push.js */ "./node_modules/core-js/modules/es.array.push.js");
/* harmony import */ var core_js_modules_es_array_push_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_array_push_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var core_js_modules_es_iterator_constructor_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! core-js/modules/es.iterator.constructor.js */ "./node_modules/core-js/modules/es.iterator.constructor.js");
/* harmony import */ var core_js_modules_es_iterator_constructor_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_iterator_constructor_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var core_js_modules_es_iterator_filter_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! core-js/modules/es.iterator.filter.js */ "./node_modules/core-js/modules/es.iterator.filter.js");
/* harmony import */ var core_js_modules_es_iterator_filter_js__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_iterator_filter_js__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var core_js_modules_es_iterator_find_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! core-js/modules/es.iterator.find.js */ "./node_modules/core-js/modules/es.iterator.find.js");
/* harmony import */ var core_js_modules_es_iterator_find_js__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_iterator_find_js__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var core_js_modules_es_iterator_for_each_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! core-js/modules/es.iterator.for-each.js */ "./node_modules/core-js/modules/es.iterator.for-each.js");
/* harmony import */ var core_js_modules_es_iterator_for_each_js__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_iterator_for_each_js__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var core_js_modules_es_iterator_map_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! core-js/modules/es.iterator.map.js */ "./node_modules/core-js/modules/es.iterator.map.js");
/* harmony import */ var core_js_modules_es_iterator_map_js__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_iterator_map_js__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _utils_mixins_commonMixin__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @/utils/mixins/commonMixin */ "./src/utils/mixins/commonMixin.js");
/* harmony import */ var _ItemPopover_vue__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./ItemPopover.vue */ "./src/components/RoleInfo/ItemPopover.vue");
/* harmony import */ var _PetDetail_vue__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./PetDetail.vue */ "./src/components/RoleInfo/PetDetail.vue");









const riderNumPerLine = 5;
/* harmony default export */ __webpack_exports__["default"] = ({
  name: 'RoleImage',
  components: {
    ItemPopover: _ItemPopover_vue__WEBPACK_IMPORTED_MODULE_7__["default"],
    PetDetail: _PetDetail_vue__WEBPACK_IMPORTED_MODULE_8__["default"]
  },
  mixins: [_utils_mixins_commonMixin__WEBPACK_IMPORTED_MODULE_6__.commonMixin],
  props: {
    size: {
      type: String,
      default: 'small'
    },
    width: {
      type: String,
      default: '50px'
    },
    height: {
      type: String,
      default: '50px'
    },
    cursor: {
      type: String,
      default: 'pointer'
    },
    placement: {
      type: String,
      default: 'right'
    },
    popoverWidth: {
      type: String,
      default: '400px'
    },
    other_info: {
      type: String,
      default: ''
    },
    roleInfo: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      limitedSkinList: window.limitedSkinList || [],
      ResUrl: window.ResUrl,
      shenqi_visible: false,
      visible: false,
      activeName: 'role_basic',
      basic_info: null,
      school_skill: null,
      life_skill: null,
      ju_qing_skill: null,
      shuliandu: null,
      left_skill_point: 0,
      role_xiulian: [],
      pet_ctrl_skill: [],
      yu_shou_shu: undefined,
      currentDisplayIndex: 0,
      // 添加当前显示索引
      not_using_equips: null,
      split_equips: null,
      shenqi: null,
      huoshenta: null,
      using_lingbao: null,
      nousing_lingbao: null,
      nousing_fabao: null,
      using_fabao: null,
      unused_fabao_sum: null,
      fabao_storage_size: null,
      shenqi_components: {},
      split_pets: [],
      pet_info: [],
      child_info: [],
      special_pet_info: [],
      sbook_skill: [],
      allow_pet_count: 0,
      sbook_skill_total: 0,
      current_pet: null,
      rider_info: [],
      current_rider_index: '0-0',
      rider_plan_list: [],
      current_rider_plan_index: 0,
      xiangrui: [],
      nosale_xiangrui: [],
      normal_xiangrui_num: 0,
      EquipLevel: 159,
      clothes: null,
      new_clothes: null,
      house: null,
      titleConf: [{
        title: '称谓特效',
        key: 'title_effect'
      }, {
        title: '施法/攻击特效',
        key: 'perform_effect'
      }, {
        title: '冒泡框',
        key: 'chat_effect'
      }, {
        title: '头像框',
        key: 'icon_effect'
      }, {
        title: '彩饰-队标',
        key: 'achieve_show'
      }]
    };
  },
  computed: {
    currentRider() {
      const [rowIndex, colIndex] = this.current_rider_index.split('-').map(Number);
      const rider = this.rider_info[rowIndex * riderNumPerLine + colIndex];
      return rider || {};
    },
    currentRiderPlan() {
      return this.rider_plan_list[this.current_rider_plan_index] || null;
    },
    imageUrl() {
      const icon = window.get_role_icon(this.other_info);
      return window.ResUrl + '/images/role_icon/small/' + icon + '.gif';
    },
    imageStyle() {
      return {
        display: 'block',
        width: this.width,
        height: this.height,
        cursor: this.cursor
      };
    },
    extraAttrPoints() {
      const currentFullYear = window.ServerTime ? +window.ServerTime.split('-')[0] : new Date().getFullYear();
      return (currentFullYear - 2004 + 1) * 3;
    },
    // 师门技能相关属性
    school_skill1_icon() {
      return this.school_skill && this.school_skill[0] ? this.school_skill[0].skill_icon : '';
    },
    school_skill1_name() {
      return this.school_skill && this.school_skill[0] ? this.school_skill[0].skill_name : '';
    },
    school_skill1_grade() {
      return this.school_skill && this.school_skill[0] ? this.school_skill[0].skill_grade : '';
    },
    school_skill1_desc() {
      return this.school_skill && this.school_skill[0] ? this.school_skill[0].desc : '';
    },
    school_skill2_icon() {
      return this.school_skill && this.school_skill[1] ? this.school_skill[1].skill_icon : '';
    },
    school_skill2_name() {
      return this.school_skill && this.school_skill[1] ? this.school_skill[1].skill_name : '';
    },
    school_skill2_grade() {
      return this.school_skill && this.school_skill[1] ? this.school_skill[1].skill_grade : '';
    },
    school_skill2_desc() {
      return this.school_skill && this.school_skill[1] ? this.school_skill[1].desc : '';
    },
    school_skill3_icon() {
      return this.school_skill && this.school_skill[2] ? this.school_skill[2].skill_icon : '';
    },
    school_skill3_name() {
      return this.school_skill && this.school_skill[2] ? this.school_skill[2].skill_name : '';
    },
    school_skill3_grade() {
      return this.school_skill && this.school_skill[2] ? this.school_skill[2].skill_grade : '';
    },
    school_skill3_desc() {
      return this.school_skill && this.school_skill[2] ? this.school_skill[2].desc : '';
    },
    school_skill4_icon() {
      return this.school_skill && this.school_skill[3] ? this.school_skill[3].skill_icon : '';
    },
    school_skill4_name() {
      return this.school_skill && this.school_skill[3] ? this.school_skill[3].skill_name : '';
    },
    school_skill4_grade() {
      return this.school_skill && this.school_skill[3] ? this.school_skill[3].skill_grade : '';
    },
    school_skill4_desc() {
      return this.school_skill && this.school_skill[3] ? this.school_skill[3].desc : '';
    },
    school_skill5_icon() {
      return this.school_skill && this.school_skill[4] ? this.school_skill[4].skill_icon : '';
    },
    school_skill5_name() {
      return this.school_skill && this.school_skill[4] ? this.school_skill[4].skill_name : '';
    },
    school_skill5_grade() {
      return this.school_skill && this.school_skill[4] ? this.school_skill[4].skill_grade : '';
    },
    school_skill5_desc() {
      return this.school_skill && this.school_skill[4] ? this.school_skill[4].desc : '';
    },
    school_skill6_icon() {
      return this.school_skill && this.school_skill[5] ? this.school_skill[5].skill_icon : '';
    },
    school_skill6_name() {
      return this.school_skill && this.school_skill[5] ? this.school_skill[5].skill_name : '';
    },
    school_skill6_grade() {
      return this.school_skill && this.school_skill[5] ? this.school_skill[5].skill_grade : '';
    },
    school_skill6_desc() {
      return this.school_skill && this.school_skill[5] ? this.school_skill[5].desc : '';
    },
    school_skill7_icon() {
      return this.school_skill && this.school_skill[6] ? this.school_skill[6].skill_icon : '';
    },
    school_skill7_name() {
      return this.school_skill && this.school_skill[6] ? this.school_skill[6].skill_name : '';
    },
    school_skill7_grade() {
      return this.school_skill && this.school_skill[6] ? this.school_skill[6].skill_grade : '';
    },
    school_skill7_desc() {
      return this.school_skill && this.school_skill[6] ? this.school_skill[6].desc : '';
    },
    // 装备相关计算属性
    storeEquipsRows() {
      const numPerLine = 5;
      const equips = this.not_using_equips || [];
      const equipsNum = equips.length;

      // 计算需要的行数，确保至少有4行
      let loopTimes = parseInt(equipsNum / numPerLine) + (equipsNum % numPerLine ? 1 : 0);
      loopTimes = loopTimes < 4 ? 4 : loopTimes;
      const rows = [];
      for (let i = 0; i < loopTimes; i++) {
        const items = equips.slice(i * numPerLine, (i + 1) * numPerLine);
        rows.push(items);
      }
      return rows;
    },
    splitEquipsRows() {
      if (!this.split_equips || this.split_equips.length === 0) return [];
      const numPerLine = 5;
      const rows = [];
      for (let i = 0; i < this.split_equips.length; i += numPerLine) {
        rows.push(this.split_equips.slice(i, i + numPerLine));
      }
      return rows;
    },
    nousingLingbaoRows() {
      const colCount = 5;
      const lingbao = this.nousing_lingbao || [];
      const max = Math.max(1, Math.ceil(lingbao.length / colCount));
      const rows = [];
      for (let i = 0; i < max; i++) {
        const row = [];
        for (let j = 0; j < colCount; j++) {
          const index = i * colCount + j;
          row.push(lingbao[index] || null);
        }
        rows.push(row);
      }
      return rows;
    },
    storeFabaoRows() {
      if (!this.nousing_fabao || this.nousing_fabao.length === 0) return [];
      const numPerLine = 5;
      const rows = [];
      for (let i = 0; i < this.nousing_fabao.length; i += numPerLine) {
        rows.push(this.nousing_fabao.slice(i, i + numPerLine));
      }
      // 确保至少有4行
      while (rows.length < 4) {
        rows.push([]);
      }
      return rows;
    },
    // 召唤兽相关计算属性
    splitPetsRows() {
      const numPerLine = 3;
      const pets = this.split_pets || [];
      const petNum = pets.length;
      const loopTimes = petNum === 0 ? 1 : parseInt(petNum / numPerLine) + (petNum % numPerLine ? 1 : 0);
      const rows = [];
      for (let i = 0; i < loopTimes; i++) {
        const items = pets.slice(i * numPerLine, (i + 1) * numPerLine);
        rows.push(items);
      }
      return rows;
    },
    petInfoRows() {
      const numPerLine = 3;
      const pets = this.pet_info || [];
      const petNum = pets.length;
      const loopTimes = petNum === 0 ? 1 : parseInt(petNum / numPerLine) + (petNum % numPerLine ? 1 : 0);
      const rows = [];
      for (let i = 0; i < loopTimes; i++) {
        const items = pets.slice(i * numPerLine, (i + 1) * numPerLine);
        rows.push(items);
      }
      return rows;
    },
    childListRows() {
      const numPerLine = 2;
      const children = this.child_info || [];
      const childNum = children.length;
      const loopTimes = childNum === 0 ? 1 : parseInt(childNum / numPerLine) + (childNum % numPerLine ? 1 : 0);
      const rows = [];
      for (let i = 0; i < loopTimes; i++) {
        const items = children.slice(i * numPerLine, (i + 1) * numPerLine);
        rows.push(items);
      }
      return rows;
    },
    // 坐骑相关计算属性
    riderRows() {
      const numPerLine = riderNumPerLine;
      const riders = this.rider_info || [];
      const riderNum = riders.length;
      const loopTimes = parseInt(riderNum / numPerLine) + (riderNum % numPerLine ? 1 : 0);
      const rows = [];
      for (let i = 0; i < loopTimes; i++) {
        const items = riders.slice(i * numPerLine, (i + 1) * numPerLine);
        rows.push(items);
      }
      return rows;
    },
    // 计算祥瑞总数
    totalXiangruiNum() {
      const nosaleNum = this.nosale_xiangrui ? this.nosale_xiangrui.length : 0;
      const totalNum = this.basic_info ? this.basic_info.total_horse : 0;
      if (!totalNum && this.xiangrui) {
        const num = this.xiangrui.length;
        return num >= 10 ? '大于等于10' : num;
      } else {
        return totalNum - nosaleNum;
      }
    },
    // 坐骑技能行计算属性
    riderSkillRows() {
      if (!this.currentRider || !this.currentRider.all_skills) return [];
      const numPerLine = 6;
      const skills = this.currentRider.all_skills;
      const skillNum = skills.length;
      let loopTimes = parseInt(skillNum / numPerLine) + (skillNum % numPerLine ? 1 : 0);
      if (loopTimes === 0) {
        loopTimes = 1;
      }
      const rows = [];
      for (let i = 0; i < loopTimes; i++) {
        const items = skills.slice(i * numPerLine, (i + 1) * numPerLine);
        rows.push(items);
      }
      return rows;
    },
    clothesRows() {
      const numPerLine = 2;
      const rows = [];
      for (let i = 0; i < this.clothes.length; i += numPerLine) {
        const row = this.clothes.slice(i, i + numPerLine);
        // 填充空位
        while (row.length < numPerLine) {
          row.push(null);
        }
        rows.push(row);
      }
      return rows;
    }
  },
  watch: {
    visible: {
      handler(newVal) {
        if (newVal) {
          this.getLimitedSkinConfig();
        }
      },
      immediate: true
    }
  },
  mounted() {
    this.basic_info = this.roleInfo.basic_info || {};
    this.role_xiulian = this.roleInfo.role_xiulian || [];
    this.pet_ctrl_skill = this.roleInfo.pet_ctrl_skill || [];
    this.yu_shou_shu = this.roleInfo.role_skill.yu_shou_shu;
    this.school_skill = this.roleInfo.role_skill.school_skill;
    this.life_skill = this.roleInfo.role_skill.life_skill;
    this.ju_qing_skill = this.roleInfo.role_skill.ju_qing_skill;
    this.shuliandu = this.roleInfo.role_skill.shuliandu;
    this.left_skill_point = this.roleInfo.left_skill_point || 0;

    // 装备相关数据
    this.using_equips = this.roleInfo.using_equips || [];
    this.not_using_equips = this.roleInfo.not_using_equips || [];
    this.split_equips = this.roleInfo.split_equips || [];
    this.shenqi = this.roleInfo.shenqi || null;
    this.huoshenta = this.roleInfo.huoshenta || null;
    this.shenqi_components = this.roleInfo.shenqi_components || {};
    this.using_lingbao = this.roleInfo.using_lingbao || [];
    this.nousing_lingbao = this.roleInfo.nousing_lingbao || [];
    this.nousing_fabao = this.roleInfo.nousing_fabao || [];
    this.using_fabao = this.roleInfo.using_fabao || [];
    this.unused_fabao_sum = this.roleInfo.unused_fabao_sum;
    this.fabao_storage_size = this.roleInfo.fabao_storage_size;

    //召唤兽
    this.split_pets = this.roleInfo.split_pets || [];
    this.pet_info = this.roleInfo.pet_info || [];
    if (this.pet_info.length > 0) {
      this.current_pet = this.pet_info[0];
    } else if (this.split_pets.length > 0) {
      this.current_pet = this.split_pets[0];
    } else if (this.child_info.length > 0) {
      this.current_pet = this.child_info[0];
    }
    this.child_info = this.roleInfo.child_info || [];
    this.special_pet_info = this.roleInfo.special_pet_info || [];
    this.sbook_skill = this.roleInfo.sbook_skill || [];
    this.allow_pet_count = this.roleInfo.allow_pet_count || 0;
    this.sbook_skill_total = this.roleInfo.sbook_skill_total || 0;

    //坐骑
    this.rider_info = this.roleInfo.rider_info || [];
    this.rider_plan_list = this.roleInfo.rider_plan_list || [];
    this.xiangrui = this.roleInfo.xiangrui || [];
    this.nosale_xiangrui = this.roleInfo.nosale_xiangrui || [];
    this.normal_xiangrui_num = this.roleInfo.normal_xiangrui_num || 0;

    // 初始化坐骑选择
    if (this.rider_info.length > 0) {
      this.current_rider_index = '0-0';
    }

    // 初始化玄灵珠选择
    if (this.rider_plan_list.length > 0) {
      this.current_rider_plan_index = 0;
    }
    this.EquipLevel = this.basic_info.role_level;
    // 初始化锦衣数据
    this.clothes = this.roleInfo.clothes || null;
    this.new_clothes = this.roleInfo.new_clothes || null;

    // 初始化房屋数据
    this.house = this.roleInfo.house || {};
  },
  methods: {
    async getLimitedSkinConfig() {
      if (!window.limitedSkinList) {
        const config = await this.$api.system.getLimitedSkinConfig();
        const limitedSkinList = [];
        for (const itemType in config) {
          for (const kName in config[itemType]) {
            limitedSkinList.push(kName);
          }
        }
        window.limitedSkinList = limitedSkinList;
      }
      this.limitedSkinList = window.limitedSkinList;
    },
    getPetRightLock(pet) {
      return pet.lock_type?.filter(item => item !== 9 && item !== 'protect' && item !== 'huoyue');
    },
    getPetLeftLock(pet) {
      return pet.lock_type?.filter(item => item === 9 || item === 'protect' || item === 'huoyue');
    },
    onPetAvatarClick(pet) {
      this.current_pet = pet;
    },
    get_using_equip(target) {
      const equip = typeof target === 'number' ? this.using_equips.find(({
        pos
      }) => pos === target) : target;
      if (equip) {
        return {
          equip_sn: equip.equip_sn,
          equip_face_img: equip.small_icon,
          equip_name: equip.name,
          equip_type_desc: equip.static_desc,
          large_equip_desc: equip.desc,
          lock_type: equip.lock_type,
          src: equip.small_icon,
          data_equip_name: equip.name,
          data_equip_type: equip.type,
          data_equip_desc: equip.desc,
          data_equip_type_desc: equip.static_desc
        };
      }
    },
    get_using_fabao(target) {
      const fabao = typeof target === 'number' ? this.using_fabao.find(({
        pos
      }) => pos === target) : target;
      if (fabao) {
        return {
          equip_sn: fabao.type,
          equip_face_img: fabao.icon,
          equip_name: fabao.name,
          equip_type_desc: fabao.static_desc,
          large_equip_desc: fabao.desc,
          icon: fabao.icon,
          data_equip_name: fabao.name,
          data_equip_type: fabao.type,
          data_equip_desc: fabao.desc,
          data_equip_type_desc: fabao.static_desc
        };
      }
    },
    htmlEncode(str) {
      if (!str) return '';
      return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    },
    toggle_display(index) {
      // 使用Vue响应式数据控制显示状态
      this.currentDisplayIndex = index;
    },
    skillRows(skills, numPerLine) {
      if (!skills || skills.length === 0) return [];
      const rows = [];
      for (let i = 0; i < skills.length; i += numPerLine) {
        rows.push(skills.slice(i, i + numPerLine));
      }
      return rows;
    },
    switchShenqiTab(index) {
      // 检查该套属性是否存在且有效
      const shenqiKey = 'shenqi' + (index + 1);
      const shenqiData = this.shenqi_components[shenqiKey];
      if (!shenqiData) {
        return; // 如果该套属性不存在，不执行切换
      }

      // 先将所有套属性设置为非激活状态
      Object.keys(this.shenqi_components).forEach(key => {
        if (this.shenqi_components[key]) {
          this.shenqi_components[key].actived = false;
        }
      });

      // 将选中的套属性设置为激活状态
      this.shenqi_components[shenqiKey].actived = true;
    },
    getClothesList(key) {
      return this[key] || [];
    },
    getTotalAvatar() {
      if (this.basic_info.total_avatar) {
        return this.basic_info.total_avatar;
      }
      return this.clothes.length < 20 ? this.clothes.length : '大于等于20';
    }
  }
});

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/chrome-extensions/DevToolsPanel.vue?vue&type=template&id=42c7142d&scoped=true":
/*!*********************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/chrome-extensions/DevToolsPanel.vue?vue&type=template&id=42c7142d&scoped=true ***!
  \*********************************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: function() { return /* binding */ render; },
/* harmony export */   staticRenderFns: function() { return /* binding */ staticRenderFns; }
/* harmony export */ });
var render = function render() {
  var _vm = this,
    _c = _vm._self._c;
  return _c("div", {
    staticClass: "devtools-panel"
  }, [_c("div", {
    staticClass: "panel-header"
  }, [_c("h3", [_vm._v("梦幻灵瞳")]), _vm._v(" "), _c("div", {
    staticClass: "connection-status"
  }, [_c("el-tag", {
    attrs: {
      type: _vm.devtoolsConnected ? "success" : "warning",
      size: "mini"
    }
  }, [_vm._v("\n        " + _vm._s(_vm.connectionStatus) + "\n      ")]), _vm._v(" "), _c("el-button", {
    attrs: {
      size: "mini"
    },
    on: {
      click: _vm.prevPage
    }
  }, [_vm._v("上一页")]), _vm._v(" "), _c("el-button", {
    attrs: {
      size: "mini"
    },
    on: {
      click: _vm.nextPage
    }
  }, [_vm._v("下一页")]), _vm._v(" "), _c("el-button", {
    attrs: {
      size: "mini",
      type: "info"
    },
    on: {
      click: _vm.getPageInfo
    }
  }, [_vm._v("页码信息")]), _vm._v(" "), !_vm.devtoolsConnected ? _c("el-button", {
    attrs: {
      size: "mini",
      type: "warning"
    },
    on: {
      click: _vm.reconnectDevTools
    }
  }, [_vm._v("重连")]) : _vm._e(), _vm._v(" "), _c("el-button", {
    attrs: {
      size: "mini",
      type: "danger"
    },
    on: {
      click: _vm.clearData
    }
  }, [_vm._v("清空数据")])], 1)]), _vm._v(" "), _c("div", {
    staticClass: "data-section"
  }, [_vm.recommendData.length === 0 ? _c("el-empty", {
    staticClass: "empty-state",
    attrs: {
      description: "暂无数据，请访问梦幻西游藏宝阁页面"
    }
  }) : _c("div", {
    staticClass: "request-list"
  }, _vm._l(_vm.recommendData, function (item) {
    return _c("div", {
      key: item.requestId,
      staticClass: "request-item",
      class: {
        completed: item.status === "completed"
      }
    }, [_c("div", {
      staticClass: "request-info"
    }, [_c("div", {
      staticClass: "request-meta"
    }, [_c("span", {
      staticClass: "status",
      class: item.status
    }, [_vm._v(_vm._s(item.status))]), _vm._v(" "), _c("span", {
      staticClass: "timestamp"
    }, [_vm._v(_vm._s(_vm.formatTime(item.timestamp)))])])]), _vm._v(" "), item.responseData ? _c("div", {
      staticClass: "response-data"
    }, [_c("el-row", {
      staticClass: "roles",
      attrs: {
        type: "flex"
      }
    }, _vm._l(_vm.parseListData(item.responseData)?.equip_list, function (role) {
      return _c("span", {
        key: role.eid
      }, [_c("RoleImage", {
        key: role.eid,
        attrs: {
          other_info: role.other_info,
          roleInfo: _vm.parserRoleData(role)
        }
      })], 1);
    }), 0)], 1) : _vm._e()]);
  }), 0)], 1)]);
};
var staticRenderFns = [];
render._withStripped = true;


/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=template&id=26200cad&scoped=true":
/*!*****************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=template&id=26200cad&scoped=true ***!
  \*****************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: function() { return /* binding */ render; },
/* harmony export */   staticRenderFns: function() { return /* binding */ staticRenderFns; }
/* harmony export */ });
var render = function render() {
  var _vm = this,
    _c = _vm._self._c;
  return _c("div", {
    staticClass: "equip-desc-content"
  }, [_vm.lockType.length > 0 ? _c("div", {
    staticStyle: {
      position: "absolute",
      width: "100px",
      right: "12px",
      top: "12px",
      display: "flex",
      "justify-content": "flex-end"
    }
  }, _vm._l(_vm.lockType, function (l) {
    return _c("img", {
      key: l,
      staticStyle: {
        height: "14px",
        width: "14px",
        display: "block"
      },
      attrs: {
        src: __webpack_require__("./public/assets/images sync recursive ^\\.\\/time_lock_.*\\.webp$")(`./time_lock_${l}.webp`)
      }
    });
  }), 0) : _vm._e(), _vm._v(" "), _c("el-row", {
    attrs: {
      type: "flex",
      justify: "space-between"
    }
  }, [_vm.image ? _c("el-col", {
    staticStyle: {
      width: "120px",
      "margin-right": "20px",
      position: "relative"
    }
  }, [_c("el-image", {
    staticStyle: {
      width: "120px",
      height: "120px"
    },
    attrs: {
      src: _vm.getImageUrl(_vm.equipment.equip_face_img, "big"),
      fit: "cover",
      referrerpolicy: "no-referrer"
    }
  }), _vm._v(" "), _vm.isBinding ? _c("div", {
    staticClass: "icon-binding"
  }, [_vm._v("\n                专用\n            ")]) : _vm._e()], 1) : _vm._e(), _vm._v(" "), _c("el-col", [_vm.equipment.equip_name ? _c("p", {
    staticClass: "equip_desc_yellow"
  }, [_vm._v(_vm._s(_vm.equipment.equip_name))]) : _vm._e(), _vm._v(" "), _c("p", {
    domProps: {
      innerHTML: _vm._s(_vm.parseEquipDesc(_vm.equipment.equip_type_desc?.replace(/#R/g, "<br />"), "#n"))
    }
  }), _vm._v(" "), _c("p", {
    domProps: {
      innerHTML: _vm._s(_vm.parseEquipDesc(_vm.equipment.large_equip_desc))
    }
  })])], 1)], 1);
};
var staticRenderFns = [];
render._withStripped = true;


/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentImage.vue?vue&type=template&id=13caaaef&scoped=true":
/*!******************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentImage.vue?vue&type=template&id=13caaaef&scoped=true ***!
  \******************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: function() { return /* binding */ render; },
/* harmony export */   staticRenderFns: function() { return /* binding */ staticRenderFns; }
/* harmony export */ });
var render = function render() {
  var _vm = this,
    _c = _vm._self._c;
  return _vm.equipment ? _c("el-popover", {
    staticStyle: {
      position: "relative",
      display: "block"
    },
    attrs: {
      "close-delay": 0,
      "data-equip-sn": _vm.equipment.equip_sn,
      placement: _vm.placement,
      width: _vm.popoverWidth,
      trigger: "hover",
      "visible-arrow": false,
      "raw-content": "",
      "popper-class": "equip-desc-popper"
    },
    scopedSlots: _vm._u([{
      key: "reference",
      fn: function () {
        return [_c("div", {
          staticStyle: {
            position: "relative",
            overflow: "hidden"
          },
          style: _vm.imageStyle
        }, [_vm.equipment ? _c("el-image", {
          staticStyle: {
            display: "block"
          },
          style: _vm.imageStyle,
          attrs: {
            src: _vm.getImageUrl(_vm.equipment.equip_face_img, _vm.size),
            fit: "cover",
            referrerpolicy: "no-referrer"
          }
        }) : _vm._e(), _vm._v(" "), _vm.isBinding ? _c("div", {
          staticClass: "icon-binding"
        }, [_vm._v("\n        专用\n      ")]) : _vm._e(), _vm._v(" "), _vm.rightLock.length > 0 ? _c("div", {
          staticStyle: {
            position: "absolute",
            width: "14px",
            right: "0px",
            top: "0px"
          }
        }, _vm._l(_vm.rightLock, function (l) {
          return _c("img", {
            key: l,
            staticStyle: {
              height: "14px",
              width: "14px",
              display: "block"
            },
            attrs: {
              src: __webpack_require__("./public/assets/images sync recursive ^\\.\\/time_lock_.*\\.webp$")(`./time_lock_${l}.webp`)
            }
          });
        }), 0) : _vm._e(), _vm._v(" "), _vm.leftLock.length > 0 ? _c("div", {
          staticStyle: {
            position: "absolute",
            width: "14px",
            left: "0px",
            top: "0px"
          }
        }, _vm._l(_vm.leftLock, function (l) {
          return _c("img", {
            key: l,
            staticStyle: {
              height: "14px",
              width: "14px",
              display: "block"
            },
            attrs: {
              src: __webpack_require__("./public/assets/images sync recursive ^\\.\\/time_lock_.*\\.webp$")(`./time_lock_${l}.webp`)
            }
          });
        }), 0) : _vm._e()], 1)];
      },
      proxy: true
    }], null, false, 645254509),
    model: {
      value: _vm.visible,
      callback: function ($$v) {
        _vm.visible = $$v;
      },
      expression: "visible"
    }
  }, [_vm._v(" "), _vm.visible ? _c("EquipmentDesc", {
    attrs: {
      equipment: _vm.equipment,
      "lock-type": _vm.lockType,
      image: _vm.image,
      isBinding: _vm.isBinding
    }
  }) : _vm._e()], 1) : _vm._e();
};
var staticRenderFns = [];
render._withStripped = true;


/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/ItemPopover.vue?vue&type=template&id=641ba552":
/*!*********************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/ItemPopover.vue?vue&type=template&id=641ba552 ***!
  \*********************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: function() { return /* binding */ render; },
/* harmony export */   staticRenderFns: function() { return /* binding */ staticRenderFns; }
/* harmony export */ });
var render = function render() {
  var _vm = this,
    _c = _vm._self._c;
  return _vm.equipment?.large_equip_desc || _vm.equipment?.equip_desc ? _c("EquipmentImage", {
    attrs: {
      image: false,
      "popover-width": 200,
      placement: _vm.placement,
      equipment: _vm.equipment,
      "lock-type": _vm.lock_type
    }
  }) : _vm._e();
};
var staticRenderFns = [];
render._withStripped = true;


/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/PetDetail.vue?vue&type=template&id=67c8d056":
/*!*******************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/PetDetail.vue?vue&type=template&id=67c8d056 ***!
  \*******************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: function() { return /* binding */ render; },
/* harmony export */   staticRenderFns: function() { return /* binding */ staticRenderFns; }
/* harmony export */ });
var render = function render() {
  var _vm = this,
    _c = _vm._self._c;
  return _c("div", {
    staticClass: "hasLayout"
  }, [_c("h4", [_vm._v("\n        详细信息\n        "), _vm.current_pet.other && _vm.current_pet.other.color_str && _vm.current_pet.other.current_on_avt ? _c("span", [_vm._v("(已包含梦影穿戴属性)")]) : _vm._e()]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _vm.current_pet.is_child && _vm.current_pet.isnew ? _c("table", {
    staticClass: "tb02",
    attrs: {
      width: "100%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tr", [_c("td", {
    attrs: {
      width: "152"
    }
  }, [_c("strong", [_vm._v("类型：")]), _vm._v(_vm._s(_vm.current_pet.kind))]), _vm._v(" "), _c("td", {
    attrs: {
      width: "150"
    }
  }, [_c("strong", [_vm._v("气血：")]), _vm._v(_vm._s(_vm.current_pet.blood_max))]), _vm._v(" "), _c("td", {
    attrs: {
      width: "150"
    }
  }, [_c("strong", [_vm._v("根骨：")]), _vm._v(_vm._s(_vm.current_pet.gg))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("等级：")]), _vm._v(_vm._s(_vm.current_pet.pet_grade))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("魔法：")]), _vm._v(_vm._s(_vm.current_pet.magic_max))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("智力：")]), _vm._v(_vm._s(_vm.current_pet.zl))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("悟性：")]), _vm._v(_vm._s(_vm.current_pet.child_sixwx))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("攻击：")]), _vm._v(_vm._s(_vm.current_pet.attack))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("武力：")]), _vm._v(_vm._s(_vm.current_pet.wl))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("门派：")]), _vm._v(_vm._s(_vm.current_pet.school))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("防御：")]), _vm._v(_vm._s(_vm.current_pet.defence))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("定力：")]), _vm._v(_vm._s(_vm.current_pet.dl))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("五行：")]), _vm._v(_vm._s(_vm.current_pet.wu_xing))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("速度：")]), _vm._v(_vm._s(_vm.current_pet.speed))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("念力：")]), _vm._v(_vm._s(_vm.current_pet.nl))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("结局：")]), _vm._v(_vm._s(_vm.current_pet.ending))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("法伤：")]), _vm._v(_vm._s(_vm.current_pet.iMagDam_all))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("灵敏：")]), _vm._v(_vm._s(_vm.current_pet.lm))])]), _vm._v(" "), _c("tr", [_c("td"), _vm._v(" "), _c("td", [_c("strong", [_vm._v("法防：")]), _vm._v(_vm._s(_vm.current_pet.ling_li))]), _vm._v(" "), _c("td")])]) : _c("table", {
    staticClass: "tb02 petZiZhiTb",
    attrs: {
      width: "100%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tr", [_c("td", [_c("strong", [_vm._v("类型：")]), _vm._v(_vm._s(_vm.current_pet.kind))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("等级：")]), _vm._v(_vm._s(_vm.current_pet.pet_grade))]), _vm._v(" "), _vm.current_pet.color ? _c("td", [_c("strong", [_vm._v("变异类型：")]), _vm._v(_vm._s(_vm.current_pet.color) + "\n            ")]) : _c("td", [_c("strong", [_vm._v("是否宝宝：")]), _vm._v(" "), _c("span", {
    style: {
      color: _vm.current_pet.is_baobao === "否" ? "#FF0000" : "#00FF00"
    }
  }, [_vm._v("\n                    " + _vm._s(_vm.current_pet.is_baobao) + "\n                ")])])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("气血：")]), _vm._v(_vm._s(_vm.current_pet.blood_max))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("体质：")]), _vm._v("\n                " + _vm._s(_vm.current_pet.ti_zhi) + "\n                "), _vm.current_pet.ti_zhi_add ? _c("span", {
    staticClass: "color-pink"
  }, [_vm._v("+" + _vm._s(_vm.current_pet.ti_zhi_add))]) : _vm._e()]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("攻击资质：")]), _vm._v("\n                " + _vm._s(_vm.current_pet.gong_ji_zz) + "\n                "), _vm.current_pet.gong_ji_ext ? _c("span", {
    staticClass: "added_attr"
  }, [_vm._v("+" + _vm._s(_vm.current_pet.gong_ji_ext))]) : _vm._e()])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("魔法：")]), _vm._v(_vm._s(_vm.current_pet.magic_max))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("法力：")]), _vm._v("\n                " + _vm._s(_vm.current_pet.fa_li) + "\n                "), _vm.current_pet.fa_li_add ? _c("span", {
    staticClass: "color-pink"
  }, [_vm._v("+" + _vm._s(_vm.current_pet.fa_li_add))]) : _vm._e()]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("防御资质：")]), _vm._v("\n                " + _vm._s(_vm.current_pet.fang_yu_zz) + "\n                "), _vm.current_pet.fang_yu_ext ? _c("span", {
    staticClass: "added_attr"
  }, [_vm._v("+" + _vm._s(_vm.current_pet.fang_yu_ext))]) : _vm._e()])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("攻击：")]), _vm._v(_vm._s(_vm.current_pet.attack))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("力量：")]), _vm._v("\n                " + _vm._s(_vm.current_pet.li_liang) + "\n                "), _vm.current_pet.li_liang_add ? _c("span", {
    staticClass: "color-pink"
  }, [_vm._v("+" + _vm._s(_vm.current_pet.li_liang_add))]) : _vm._e()]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("体力资质：")]), _vm._v("\n                " + _vm._s(_vm.current_pet.ti_li_zz) + "\n                "), _vm.current_pet.ti_li_ext ? _c("span", {
    staticClass: "added_attr"
  }, [_vm._v("+" + _vm._s(_vm.current_pet.ti_li_ext))]) : _vm._e()])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("防御：")]), _vm._v(_vm._s(_vm.current_pet.defence))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("耐力：")]), _vm._v("\n                " + _vm._s(_vm.current_pet.nai_li) + "\n                "), _vm.current_pet.nai_li_add ? _c("span", {
    staticClass: "color-pink"
  }, [_vm._v("+" + _vm._s(_vm.current_pet.nai_li_add))]) : _vm._e()]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("法力资质：")]), _vm._v("\n                " + _vm._s(_vm.current_pet.fa_li_zz) + "\n                "), _vm.current_pet.fa_li_ext ? _c("span", {
    staticClass: "added_attr"
  }, [_vm._v("+" + _vm._s(_vm.current_pet.fa_li_ext))]) : _vm._e()])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("速度：")]), _vm._v(_vm._s(_vm.current_pet.speed))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("敏捷：")]), _vm._v("\n                " + _vm._s(_vm.current_pet.min_jie) + "\n                "), _vm.current_pet.min_jie_add ? _c("span", {
    staticClass: "color-pink"
  }, [_vm._v("+" + _vm._s(_vm.current_pet.min_jie_add))]) : _vm._e()]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("速度资质：")]), _vm._v("\n                " + _vm._s(_vm.current_pet.su_du_zz) + "\n                "), _vm.current_pet.su_du_ext ? _c("span", {
    staticClass: "added_attr"
  }, [_vm._v("+" + _vm._s(_vm.current_pet.su_du_ext))]) : _vm._e()])]), _vm._v(" "), _c("tr", [_vm.isShowNewLingli ? _c("td", [_c("strong", [_vm._v("法伤：")]), _vm._v(_vm._s(_vm.current_pet.iMagDam))]) : _c("td", [_c("strong", [_vm._v("灵力：")]), _vm._v(_vm._s(_vm.current_pet.ling_li))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("潜能：")]), _vm._v(_vm._s(_vm.current_pet.qian_neng))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("躲闪资质：")]), _vm._v("\n                " + _vm._s(_vm.current_pet.duo_shan_zz) + "\n                "), _vm.current_pet.duo_shan_ext ? _c("span", {
    staticClass: "added_attr"
  }, [_vm._v("+" + _vm._s(_vm.current_pet.duo_shan_ext))]) : _vm._e()])]), _vm._v(" "), _c("tr", [_vm.isShowNewLingli ? _c("td", [_c("strong", [_vm._v("法防：")]), _vm._v(_vm._s(_vm.current_pet.iMagDef))]) : _c("td", [_c("strong", [_vm._v("寿命：")]), _vm._v(_vm._s(_vm.current_pet.lifetime))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("成长：")]), _vm._v(_vm._s(_vm.current_pet.cheng_zhang))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("五行：")]), _vm._v(_vm._s(_vm.current_pet.wu_xing))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("已用元宵：")]), _vm._v(_vm._s(_vm.current_pet.used_yuanxiao))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("已用千金露：")]), _vm._v(_vm._s(_vm.current_pet.used_qianjinlu))])]), _vm._v(" "), _c("tr", [_c("td", [_vm.current_pet.is_child ? _c("strong", [_vm._v("悟性：")]) : _vm._e(), _vm._v(" "), _vm.current_pet.is_child && _vm.current_pet.child_sixwx !== undefined ? _c("span", [_vm._v(_vm._s(_vm.current_pet.child_sixwx))]) : _vm.current_pet.is_child ? _c("span", [_vm._v("无")]) : _c("strong", [_vm._v("已用炼兽珍经：")]), _vm._v(" "), !_vm.current_pet.is_child ? _c("span", [_vm._v(_vm._s(_vm.current_pet.used_lianshou))]) : _vm._e()]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("已使用幻色丹：")]), _vm._v(_vm._s(_vm.getSummonColorDesc(_vm.current_pet.summon_color, _vm.current_pet.type_id)) + "\n            ")]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("历史灵性值：")]), _vm._v(_vm._s(_vm.getDictValue(_vm.current_pet.jinjie, "lx", 0)) + "\n            ")])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("已用清灵仙露：")]), _vm._v(_vm._s(_vm.getDictValue(_vm.current_pet.jinjie, "cnt", 0)) + "\n            ")]), _vm._v(" "), _vm.isShowNewLingli ? _c("td", [_c("strong", [_vm._v("寿命：")]), _vm._v(_vm._s(_vm.current_pet.lifetime))]) : _vm._e(), _vm._v(" "), _c("td")])]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("div", {
    staticClass: "hasLayout"
  }, [_c("div", {
    ref: "RoleSkillTipsBox",
    staticClass: "soldDetail",
    staticStyle: {
      width: "320px",
      display: "none"
    },
    attrs: {
      id: "RoleSkillTipsBox"
    }
  }), _vm._v(" "), _c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "210px",
      margin: "0"
    }
  }, [_vm.current_pet.evol_skill_list ? _c("h4", [_vm._v("赐福技能")]) : _vm._e(), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _vm.current_pet.evol_skill_list ? _c("table", {
    staticClass: "tb03",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RolePetCifu"
    }
  }, _vm._l(_vm.evolSkillRows, function (row, rowIndex) {
    return _c("tr", {
      key: rowIndex
    }, _vm._l(row, function (skill, colIndex) {
      return _c("td", {
        key: colIndex,
        staticStyle: {
          position: "relative"
        }
      }, [skill.hlightLight ? _c("img", {
        attrs: {
          referrerpolicy: "no-referrer",
          src: skill.icon,
          width: "40",
          height: "40",
          data_equip_name: skill.name,
          data_skill_type: "cifu",
          data_equip_desc: skill.desc,
          data_tip_box: "RoleSkillTipsBox",
          data_cifu_icon: skill.cifuIcon,
          data_height_icon: skill.heightCifuIcon
        },
        on: {
          mouseenter: function ($event) {
            return _vm.showSkillTip($event, skill);
          },
          mouseleave: _vm.hideSkillTip
        }
      }) : _c("img", {
        staticStyle: {
          filter: "grayscale(100%)"
        },
        attrs: {
          referrerpolicy: "no-referrer",
          src: skill.icon,
          width: "40",
          height: "40",
          data_equip_name: skill.name,
          data_skill_type: "cifu",
          data_equip_desc: skill.desc,
          data_tip_box: "RoleSkillTipsBox",
          data_cifu_icon: skill.cifuIcon,
          data_height_icon: skill.heightCifuIcon
        },
        on: {
          mouseenter: function ($event) {
            return _vm.showSkillTip($event, skill);
          },
          mouseleave: _vm.hideSkillTip
        }
      }), _vm._v(" "), skill.hlightLight ? _c("div", {
        staticClass: "evol_skill_icon",
        attrs: {
          data_src: skill.icon,
          data_equip_name: skill.name,
          data_skill_type: "cifu",
          data_equip_desc: skill.desc,
          data_tip_box: "RoleSkillTipsBox",
          data_cifu_icon: skill.cifuIcon,
          data_height_icon: skill.heightCifuIcon
        }
      }) : _c("div", {
        staticClass: "evol_skill_icon",
        staticStyle: {
          filter: "grayscale(100%)"
        },
        attrs: {
          data_src: skill.icon,
          data_equip_name: skill.name,
          data_skill_type: "cifu",
          data_equip_desc: skill.desc,
          data_tip_box: "RoleSkillTipsBox",
          data_cifu_icon: skill.cifuIcon,
          data_height_icon: skill.heightCifuIcon
        }
      })]);
    }), 0);
  }), 0) : _vm._e(), _vm._v(" "), _vm.current_pet.evol_skill_list ? _c("div", {
    staticClass: "blank12",
    staticStyle: {
      clear: "both"
    }
  }) : _vm._e(), _vm._v(" "), _c("h4", [_vm._v("技能")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("table", {
    staticClass: "tb03",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RolePetSkill"
    }
  }, _vm._l(_vm.petSkillRows, function (row, rowIndex) {
    return _c("tr", {
      key: rowIndex
    }, [_vm._l(row, function (skill, colIndex) {
      return _c("td", {
        key: colIndex,
        staticStyle: {
          position: "relative"
        }
      }, [_c("img", {
        attrs: {
          referrerpolicy: "no-referrer",
          src: skill.icon,
          width: "40",
          height: "40",
          data_equip_name: skill.name,
          data_skill_type: "cifu",
          data_equip_desc: skill.desc,
          data_tip_box: "RoleSkillTipsBox",
          data_is_super_skill: skill.isSuperSkill
        },
        on: {
          mouseenter: function ($event) {
            return _vm.showSkillTip($event, skill);
          },
          mouseleave: _vm.hideSkillTip
        }
      }), _vm._v(" "), skill.hashEvol ? _c("div", {
        staticClass: "evol_skill_icon",
        attrs: {
          data_src: skill.icon,
          data_equip_name: skill.name,
          data_skill_type: "cifu",
          data_equip_desc: skill.desc,
          data_tip_box: "RoleSkillTipsBox",
          data_is_super_skill: skill.isSuperSkill
        }
      }) : _vm._e()]);
    }), _vm._v(" "), _vm._l(4 - row.length, function (i) {
      return [i === 4 - row.length && rowIndex === _vm.petSkillRows.length - 1 && _vm.current_pet.genius ? _c("td", {
        key: "genius-" + i
      }, [_c("img", {
        staticClass: "on",
        attrs: {
          referrerpolicy: "no-referrer",
          src: _vm.current_pet.genius_skill.icon,
          data_equip_name: _vm.current_pet.genius_skill.name,
          data_skill_type: "cifu",
          data_equip_desc: _vm.current_pet.genius_skill.desc,
          data_tip_box: "RoleSkillTipsBox",
          data_is_super_skill: _vm.current_pet.genius_skill.isSuperSkill
        },
        on: {
          mouseenter: function ($event) {
            return _vm.showSkillTip($event, _vm.current_pet.genius_skill);
          },
          mouseleave: _vm.hideSkillTip
        }
      })]) : _c("td", {
        key: "empty-" + i
      })];
    })], 2);
  }), 0), _vm._v(" "), !_vm.current_pet.is_child ? [_c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _vm.current_pet.core_close && _vm.getDictValue(_vm.current_pet.jinjie, "core", {}).id !== undefined ? _c("h4", [_vm._v("\n                    特性:" + _vm._s(_vm.current_pet.core_close) + "\n                ")]) : _c("h4", [_vm._v("特性")]), _vm._v(" "), _vm.getDictValue(_vm.current_pet.jinjie, "core", {}).id !== undefined ? _c("div", {
    staticStyle: {
      "text-align": "left"
    }
  }, [_c("span", [_vm._v(_vm._s(_vm.getDictValue(_vm.current_pet.jinjie, "core", {}).name) + "："), _c("span", {
    domProps: {
      innerHTML: _vm._s(_vm.parseStyleInfo(_vm.getDictValue(_vm.current_pet.jinjie, "core", {}).effect))
    }
  })])]) : _c("div", {
    staticStyle: {
      "text-align": "center"
    }
  }, [_vm._v("无")])] : _vm._e()], 2), _vm._v(" "), _c("div", {
    staticClass: "cols",
    staticStyle: {
      float: "right",
      width: "232px",
      margin: "0"
    }
  }, [!_vm.current_pet.is_child ? _c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "160px",
      margin: "0"
    }
  }, [_c("h4", [_vm._v("装备")]), _vm._v(" "), _c("div", {
    staticClass: "blank6"
  }), _vm._v(" "), _c("table", {
    staticClass: "tb03 size50",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RolePetEquips"
    }
  }, [_c("tr", _vm._l(_vm.current_pet.equip_list, function (equip, index) {
    return _c("td", {
      key: index
    }, [equip ? _c("ItemPopover", {
      attrs: {
        equipment: {
          equip_face_img: equip.icon,
          equip_name: equip.name,
          large_equip_desc: equip.desc,
          equip_type_desc: equip.static_desc
        },
        placement: "top"
      }
    }) : _c("span", [_vm._v(" ")])], 1);
  }), 0)])]) : _vm._e(), _vm._v(" "), !_vm.current_pet.is_child ? _c("div", {
    staticClass: "cols",
    staticStyle: {
      float: "right",
      width: "60px",
      margin: "0"
    }
  }, [_c("h4", [_vm._v("饰品")]), _vm._v(" "), _c("div", {
    staticClass: "blank6"
  }), _vm._v(" "), _c("table", {
    staticClass: "tb03 size50",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RolePetShipin"
    }
  }, [_c("tr", [_c("td", [_vm.current_pet.shipin_list && _vm.current_pet.shipin_list[0] ? _c("img", {
    staticStyle: {
      "max-width": "50px",
      "max-height": "50px",
      background: "#fff",
      "border-radius": "5px"
    },
    attrs: {
      referrerpolicy: "no-referrer",
      src: _vm.current_pet.shipin_list[0].icon,
      data_equip_name: _vm.current_pet.shipin_list[0].name,
      data_equip_type: _vm.current_pet.shipin_list[0].type,
      data_equip_desc: _vm.current_pet.shipin_list[0].desc,
      data_equip_type_desc: "",
      lock_types: _vm.current_pet.shipin_list[0].lock_type
    }
  }) : _c("span", [_vm._v(" ")])])])])]) : _vm._e(), _vm._v(" "), !_vm.current_pet.is_child ? [_c("div", {
    staticClass: "blank12",
    staticStyle: {
      clear: "both"
    }
  }), _vm._v(" "), _c("h4", [_vm._v("内丹")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _vm.current_pet.neidan.length === 0 ? _c("p", {
    staticClass: "textCenter"
  }, [_vm._v("无")]) : _c("table", {
    attrs: {
      width: "100%",
      cellspacing: "3",
      cellpadding: "3",
      id: "RolePetNeidan"
    }
  }, _vm._l(_vm.current_pet.neidan, function (item, index) {
    return _c("tr", {
      key: index
    }, [_c("td", [_c("img", {
      attrs: {
        referrerpolicy: "no-referrer",
        src: item.icon,
        data_equip_name: item.name,
        data_skill_type: "neidan",
        data_equip_desc: item.desc,
        data_equip_level: item.level,
        data_tip_box: "SkillTipsBox"
      },
      on: {
        mouseenter: function ($event) {
          return _vm.showNeidanTip($event, item);
        },
        mouseleave: _vm.hideSkillTip
      }
    })]), _vm._v(" "), _c("th", [_vm._v(_vm._s(item.name))]), _vm._v(" "), _c("td", [_vm._v(_vm._s(item.level) + "层")])]);
  }), 0)] : _vm._e(), _vm._v(" "), _vm.current_pet.other && _vm.current_pet.other.avt_list && _vm.current_pet.other.avt_list.length ? _c("div", {
    staticClass: "blank12"
  }) : _vm._e(), _vm._v(" "), _vm.current_pet.other && _vm.current_pet.other.avt_list && _vm.current_pet.other.avt_list.length ? _c("h4", [_vm._v("\n                梦影\n            ")]) : _vm._e(), _vm._v(" "), _vm.current_pet.other && _vm.current_pet.other.avt_list && _vm.current_pet.other.avt_list.length ? _c("table", {
    staticClass: "tb02",
    attrs: {
      width: "100%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tr", [_c("th", {
    attrs: {
      width: "40%"
    }
  }, [_vm._v("梦影数量：")]), _vm._v(" "), _c("td", [_c("p", {
    staticClass: "fl",
    staticStyle: {
      "line-height": "24px"
    }
  }, [_vm._v("\n                            " + _vm._s(_vm.current_pet.other.avt_list.length) + "\n                        ")]), _vm._v(" "), _vm.current_pet.other.color_str ? _c("button", {
    staticClass: "identify-pet-btn fr",
    attrs: {
      id: "identify-pet-btn"
    },
    on: {
      click: function ($event) {
        return _vm.window.petClothEffect.display();
      }
    }
  }, [_vm._v("\n                            穿戴效果\n                        ")]) : _vm._e()])]), _vm._v(" "), _vm.current_pet.other.color_str && _vm.current_pet.other.current_on_avt ? _c("tr", [_c("th", {
    staticStyle: {
      "vertical-align": "top"
    },
    attrs: {
      width: "40%"
    }
  }, [_vm._v("当前穿戴：")]), _vm._v(" "), _c("td", {
    staticStyle: {
      "vertical-align": "top"
    }
  }, [_c("p", [_vm._v(_vm._s(_vm.current_pet.other.current_on_avt.name))]), _vm._v(" "), _vm.current_pet.other.current_on_avt.sumavt_propsk ? _c("p", {
    staticStyle: {
      color: "#00ff00"
    }
  }, [_vm._v("\n                            (" + _vm._s(_vm.current_pet.other.current_on_avt.sumavt_propsk) + "+1)\n                        ")]) : _vm._e()])]) : _c("tr", [_c("th", {
    staticStyle: {
      "padding-right": "20px"
    },
    attrs: {
      width: "40%"
    }
  }, [_vm._v("未穿戴")]), _vm._v(" "), _c("td")])]) : _vm._e()], 2)])]);
};
var staticRenderFns = [];
render._withStripped = true;


/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/RoleImage.vue?vue&type=template&id=8c1934ec&scoped=true":
/*!*******************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/RoleImage.vue?vue&type=template&id=8c1934ec&scoped=true ***!
  \*******************************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: function() { return /* binding */ render; },
/* harmony export */   staticRenderFns: function() { return /* binding */ staticRenderFns; }
/* harmony export */ });
var render = function render() {
  var _vm = this,
    _c = _vm._self._c;
  return _c("el-popover", {
    attrs: {
      width: 715,
      "data-equip-sn": _vm.$attrs.equip_sn,
      placement: "right",
      trigger: "click",
      "popper-class": "role-info-popover"
    },
    scopedSlots: _vm._u([{
      key: "reference",
      fn: function () {
        return [_vm._t("default"), _vm._v(" "), _c("el-image", {
          staticStyle: {
            display: "block"
          },
          style: _vm.imageStyle,
          attrs: {
            src: _vm.imageUrl,
            fit: "cover",
            referrerpolicy: "no-referrer"
          }
        }, [_c("div", {
          staticClass: "image-slot",
          attrs: {
            slot: "error"
          },
          slot: "error"
        }, [_c("i", {
          staticClass: "el-icon-picture-outline"
        })])])];
      },
      proxy: true
    }], null, true),
    model: {
      value: _vm.visible,
      callback: function ($$v) {
        _vm.visible = $$v;
      },
      expression: "visible"
    }
  }, [_vm._v(" "), _vm.visible ? _c("div", {
    attrs: {
      id: "role_info_box"
    }
  }, [_c("el-tabs", {
    staticClass: "role-info-tabs tabCont",
    model: {
      value: _vm.activeName,
      callback: function ($$v) {
        _vm.activeName = $$v;
      },
      expression: "activeName"
    }
  }, [_vm.basic_info ? _c("el-tab-pane", {
    attrs: {
      label: "人物/修炼",
      name: "role_basic"
    }
  }, [_c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "320px"
    }
  }, [_c("div", {
    staticClass: "subTab"
  }, [_c("h4", {
    staticClass: "subTabLeft role_basic_attr_tab",
    class: {
      off: _vm.currentDisplayIndex !== 0
    },
    on: {
      click: function ($event) {
        return _vm.toggle_display(0);
      }
    }
  }, [_vm._v("\n              人物状态\n            ")]), _vm._v(" "), _c("h4", {
    staticClass: "subTabRight role_basic_attr_tab",
    class: {
      off: _vm.currentDisplayIndex !== 1
    },
    on: {
      click: function ($event) {
        return _vm.toggle_display(1);
      }
    }
  }, [_vm._v("\n              输出/抗性\n            ")])]), _vm._v(" "), _c("table", {
    directives: [{
      name: "show",
      rawName: "v-show",
      value: _vm.currentDisplayIndex === 0,
      expression: "currentDisplayIndex === 0"
    }],
    staticClass: "tb02 role_basic_attr_table",
    attrs: {
      width: "100%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("colgroup", [_c("col", {
    attrs: {
      width: "180"
    }
  }), _vm._v(" "), _c("col", {
    attrs: {
      width: "140"
    }
  })]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("级别：")]), _vm._v(_vm._s(_vm.basic_info.role_level))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("名称：")]), _vm._v(_vm._s(_vm.htmlEncode(_vm.basic_info.nickname)))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("角色：")]), _vm._v(_vm._s(_vm.basic_info.role_kind_name))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("人气：")]), _vm._v(_vm._s(_vm.basic_info.pride))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("帮派：")]), _vm._v(_vm._s(_vm.basic_info.org))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("帮贡：")]), _vm._v(_vm._s(_vm.basic_info.org_offer))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("门派：")]), _c("span", {
    attrs: {
      id: "kindName"
    }
  }, [_vm._v(_vm._s(_vm.basic_info.school))])]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("门贡：")]), _vm._v(_vm._s(_vm.basic_info.school_offer))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("气血：")]), _vm._v(_vm._s(_vm.basic_info.hp_max))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("体质：")]), _vm._v(_vm._s(_vm.basic_info.cor_all))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("魔法：")]), _vm._v(_vm._s(_vm.basic_info.mp_max))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("魔力：")]), _vm._v(_vm._s(_vm.basic_info.mag_all))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("命中：")]), _vm._v(_vm._s(_vm.basic_info.att_all))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("力量：")]), _vm._v(_vm._s(_vm.basic_info.str_all))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("伤害：")]), _vm._v(_vm._s(_vm.basic_info.damage_all))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("耐力：")]), _vm._v(_vm._s(_vm.basic_info.res_all))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("防御：")]), _vm._v(_vm._s(_vm.basic_info.def_all))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("敏捷：")]), _vm._v(_vm._s(_vm.basic_info.spe_all))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("速度：")]), _vm._v(_vm._s(_vm.basic_info.dex_all))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("潜力：")]), _vm._v(_vm._s(_vm.basic_info.point))])]), _vm._v(" "), _c("tr", [_vm.basic_info.fa_shang !== undefined ? _c("td", [_c("strong", [_vm._v("法伤：")]), _vm._v(_vm._s(_vm.basic_info.fa_shang) + "\n              ")]) : _c("td", [_c("strong", [_vm._v("躲避：")]), _vm._v(_vm._s(_vm.basic_info.dod_all))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("靓号特效：")]), _vm._v(_vm._s(_vm.basic_info.is_niceid))])]), _vm._v(" "), _c("tr", [_vm.basic_info.fa_fang !== undefined ? _c("td", [_c("strong", [_vm._v("法防：")]), _vm._v(_vm._s(_vm.basic_info.fa_fang) + "\n              ")]) : _c("td", [_c("strong", [_vm._v("灵力：")]), _vm._v(_vm._s(_vm.basic_info.mag_def_all))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("成就点数：")]), _vm._v(_vm._s(_vm.basic_info.chengjiu))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("获得经验：")]), _vm._v(_vm._s(_vm.basic_info.upexp))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("已用潜能果数量：")]), _vm._v(_vm._s(_vm.basic_info.qian_neng_guo))])]), _vm._v(" "), _c("tr", [_c("td", [_vm.basic_info.qian_yuan_dan && _vm.basic_info.qian_yuan_dan.new_value === undefined ? _c("span", [_c("strong", [_vm._v("已兑换乾元丹数量：")]), _vm._v(_vm._s(_vm.basic_info.qian_yuan_dan.old_value) + "\n                ")]) : _c("span", [_c("strong", [_vm._v("新版乾元丹数量：")]), _vm._v(_vm._s(_vm.basic_info.qian_yuan_dan.new_value) + "\n                ")])]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("总经验：")]), _vm._v(_vm._s(_vm.basic_info.sum_exp) + "\n                "), _vm.basic_info.ach_info ? _c("i", {
    staticClass: "question hoverTips"
  }, [_c("span", {
    staticClass: "hoverTipsDetail"
  }, [_vm._v(_vm._s(_vm.basic_info.ach_info))])]) : _vm._e()])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("月饼粽子机缘：")]), _vm._v(_vm._s((_vm.basic_info.add_point || 0) + (_vm.basic_info.ji_yuan || 0)) + "/" + _vm._s(_vm.extraAttrPoints) + "\n                "), _vm.extraAttrPoints > 0 ? _c("i", {
    staticClass: "question hoverTips"
  }, [_c("span", {
    staticClass: "hoverTipsDetail"
  }, [_vm._v("\n                    月饼粽子食用量：" + _vm._s(_vm.basic_info.add_point)), _c("br"), _c("br"), _vm._v("已获得机缘属性：" + _vm._s(_vm.basic_info.ji_yuan) + "\n                  ")])]) : _vm._e()]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("原始种族：")]), _c("span", {
    domProps: {
      innerHTML: _vm._s(_vm.basic_info.ori_race)
    }
  })])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("历史门派：")]), _vm._v(_vm._s(_vm.basic_info.changesch))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("属性保存方案：")]), _vm._v(_vm._s(_vm.basic_info.propkept))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("飞升/渡劫/化圣：")]), _vm._v(_vm._s(_vm.basic_info.fly_status))]), _vm._v(" "), _vm.basic_info.role_level >= 120 ? _c("td", [_c("strong", [_vm._v("生死劫：")]), _vm._v(_vm._s(_vm.basic_info.shengsijie) + "\n              ")]) : _c("td")])]), _vm._v(" "), _c("table", {
    directives: [{
      name: "show",
      rawName: "v-show",
      value: _vm.currentDisplayIndex === 1,
      expression: "currentDisplayIndex === 1"
    }],
    staticClass: "tb02 role_basic_attr_table",
    attrs: {
      width: "100%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [!_vm.basic_info.other_attr ? [_c("colgroup", [_c("col", {
    attrs: {
      width: "320"
    }
  })]), _vm._v(" "), _c("tr", [_c("td", [_c("br"), _vm._v("重新寄售后才能显示")])])] : [_c("colgroup", [_c("col", {
    attrs: {
      width: "160"
    }
  }), _vm._v(" "), _c("col", {
    attrs: {
      width: "160"
    }
  })]), _vm._v(" "), _c("tr", [_c("td", {
    attrs: {
      colspan: "2"
    }
  }, [_c("strong", {
    staticStyle: {
      "font-size": "16px",
      color: "white"
    }
  }, [_vm._v("输出")])])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("灵力：")])]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.other_attr["14"]))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("物理暴击等级：")])]), _vm._v(" "), _c("td", [_vm._v("\n                  " + _vm._s(_vm.basic_info.other_attr["6"]) + "(" + _vm._s((_vm.basic_info.other_attr["6"] * 10 / Math.max(30, _vm.basic_info.role_level) || 0).toFixed(2)) + "%)\n                ")])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("穿刺等级：")])]), _vm._v(" "), _c("td", [_vm._v("\n                  " + _vm._s(_vm.basic_info.other_attr["8"]) + "(" + _vm._s((_vm.basic_info.other_attr["8"] * 3 / Math.max(30, _vm.basic_info.role_level) || 0).toFixed(2)) + "%)\n                ")])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("狂暴等级：")])]), _vm._v(" "), _c("td", [_vm._v("\n                  " + _vm._s(_vm.basic_info.other_attr["5"]) + "(" + _vm._s((_vm.basic_info.other_attr["5"] * 3 / Math.max(30, _vm.basic_info.role_level) || 0).toFixed(2)) + "%)\n                ")])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("法术暴击等级：")])]), _vm._v(" "), _c("td", [_vm._v("\n                  " + _vm._s(_vm.basic_info.other_attr["7"]) + "(" + _vm._s((_vm.basic_info.other_attr["7"] * 10 / Math.max(30, _vm.basic_info.role_level) || 0).toFixed(2)) + "%)\n                ")])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("法术伤害结果：")])]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.other_attr["12"]))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("封印命中等级：")])]), _vm._v(" "), _c("td", [_vm._v("\n                  " + _vm._s(_vm.basic_info.other_attr["1"]) + "(" + _vm._s((_vm.basic_info.other_attr["1"] * 10 / Math.max(30, _vm.basic_info.role_level + 25) || 0).toFixed(2)) + "%)\n                ")])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("治疗能力：")])]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.other_attr["3"]))])]), _vm._v(" "), _c("tr", [_c("td", {
    attrs: {
      colspan: "2"
    }
  }, [_c("strong", {
    staticStyle: {
      "font-size": "16px",
      color: "white"
    }
  }, [_vm._v("抗性")])])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("抗物理暴击等级：")])]), _vm._v(" "), _c("td", [_vm._v("\n                  " + _vm._s(_vm.basic_info.other_attr["9"]) + "(" + _vm._s((_vm.basic_info.other_attr["9"] * 10 / Math.max(30, _vm.basic_info.role_level) || 0).toFixed(2)) + "%)\n                ")])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("格挡值：")])]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.other_attr["11"]))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("抗法术暴击等级：")])]), _vm._v(" "), _c("td", [_vm._v("\n                  " + _vm._s(_vm.basic_info.other_attr["10"]) + "(" + _vm._s((_vm.basic_info.other_attr["10"] * 10 / Math.max(30, _vm.basic_info.role_level) || 0).toFixed(2)) + "%)\n                ")])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("抵抗封印等级：")])]), _vm._v(" "), _c("td", [_vm._v("\n                  " + _vm._s(_vm.basic_info.other_attr["2"]) + "(" + _vm._s((_vm.basic_info.other_attr["2"] * 10 / Math.max(30, _vm.basic_info.role_level + 25) || 0).toFixed(2)) + "%)\n                ")])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("气血回复效果：")])]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.other_attr["4"]))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("躲避：")])]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.other_attr["13"]))])])]], 2)]), _vm._v(" "), _c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "320px"
    }
  }, [_c("h4", [_vm._v("角色修炼及宠修")]), _vm._v(" "), _c("table", {
    staticClass: "tb02",
    staticStyle: {
      float: "left"
    },
    attrs: {
      width: "49%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, _vm._l(_vm.role_xiulian, function (item, index) {
    return _c("tr", {
      key: index
    }, [_c("th", {
      attrs: {
        width: "100"
      }
    }, [_vm._v(_vm._s(item.name) + "：")]), _vm._v(" "), _c("td", {
      staticStyle: {
        "white-space": "nowrap"
      }
    }, [_vm._v(_vm._s(item.info))])]);
  }), 0), _vm._v(" "), _c("table", {
    staticClass: "tb02",
    staticStyle: {
      float: "right"
    },
    attrs: {
      width: "49%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_vm.yu_shou_shu !== undefined ? _c("tr", [_c("th", {
    attrs: {
      width: "100"
    }
  }, [_vm._v("育兽术：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.yu_shou_shu))])]) : _vm._e(), _vm._v(" "), _vm._l(_vm.pet_ctrl_skill, function (item, index) {
    return _c("tr", {
      key: index
    }, [_c("th", {
      attrs: {
        width: "100"
      }
    }, [_vm._v(_vm._s(item.name) + "：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(item.grade))])]);
  })], 2), _vm._v(" "), _c("div", {
    staticClass: "blank9",
    staticStyle: {
      clear: "both"
    }
  }), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("h4", [_vm._v("积分 其他")]), _vm._v(" "), _c("table", {
    staticClass: "tb02",
    attrs: {
      width: "92%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tr", [_c("th", {
    attrs: {
      width: "80"
    }
  }, [_vm._v("比武积分：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.hero_score))]), _vm._v(" "), _c("th", {
    attrs: {
      width: "80"
    }
  }, [_vm._v("剑会积分：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.sword_score))])]), _vm._v(" "), _c("tr", [_c("th", {
    attrs: {
      width: "80"
    }
  }, [_vm._v("三界功绩：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.sanjie_score))]), _vm._v(" "), _c("th", {
    attrs: {
      width: "80"
    }
  }, [_vm._v("副本积分：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.dup_score))])]), _vm._v(" "), _c("tr", [_c("th", {
    attrs: {
      width: "80"
    }
  }, [_vm._v("神器积分：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.shenqi_score))]), _vm._v(" "), _c("th"), _vm._v(" "), _c("td")])])])]) : _vm._e(), _vm._v(" "), _vm.school_skill ? _c("el-tab-pane", {
    attrs: {
      label: "技能",
      name: "role_skill"
    }
  }, [_c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "200px"
    }
  }, [_c("h4", [_vm._v("师门技能")]), _vm._v(" "), _c("div", {
    staticClass: "skill"
  }, [_vm.school_skill.length > 7 ? _c("p", {
    staticClass: "textCenter cDYellow"
  }, [_vm._v("师门技能信息有误")]) : _vm.school_skill.length == 0 ? _c("p", {
    staticClass: "textCenter cDYellow"
  }, [_vm._v("师门技能都是0")]) : _c("ul", {
    attrs: {
      id: "school_skill_lists"
    }
  }, [_c("li", {
    staticStyle: {
      left: "60px",
      top: "0"
    }
  }, [_c("img", {
    attrs: {
      referrerpolicy: "no-referrer",
      src: _vm.school_skill2_icon,
      data_equip_name: _vm.school_skill2_name,
      data_skill_type: "school_skill",
      data_equip_desc: _vm.school_skill2_desc,
      data_tip_box: "RoleSkillTipsBox"
    }
  }), _vm._v(" "), _c("p", [_vm._v(_vm._s(_vm.school_skill2_grade))]), _vm._v(" "), _c("h5", [_vm._v(_vm._s(_vm.school_skill2_name))])]), _vm._v(" "), _c("li", {
    staticStyle: {
      left: "0",
      top: "50px"
    }
  }, [_c("img", {
    attrs: {
      referrerpolicy: "no-referrer",
      src: _vm.school_skill3_icon,
      data_equip_name: _vm.school_skill3_name,
      data_skill_type: "school_skill",
      data_equip_desc: _vm.school_skill3_desc,
      data_tip_box: "RoleSkillTipsBox"
    }
  }), _vm._v(" "), _c("p", [_vm._v(_vm._s(_vm.school_skill3_grade))]), _vm._v(" "), _c("h5", [_vm._v(_vm._s(_vm.school_skill3_name))])]), _vm._v(" "), _c("li", {
    staticStyle: {
      left: "120px",
      top: "50px"
    }
  }, [_c("img", {
    attrs: {
      referrerpolicy: "no-referrer",
      src: _vm.school_skill4_icon,
      data_equip_name: _vm.school_skill4_name,
      data_skill_type: "school_skill",
      data_equip_desc: _vm.school_skill4_desc,
      data_tip_box: "RoleSkillTipsBox"
    }
  }), _vm._v(" "), _c("p", [_vm._v(_vm._s(_vm.school_skill4_grade))]), _vm._v(" "), _c("h5", [_vm._v(_vm._s(_vm.school_skill4_name))])]), _vm._v(" "), _c("li", {
    staticStyle: {
      left: "0",
      top: "140px"
    }
  }, [_c("img", {
    attrs: {
      referrerpolicy: "no-referrer",
      src: _vm.school_skill5_icon,
      data_equip_name: _vm.school_skill5_name,
      data_skill_type: "school_skill",
      data_equip_desc: _vm.school_skill5_desc,
      data_tip_box: "RoleSkillTipsBox"
    }
  }), _vm._v(" "), _c("p", [_vm._v(_vm._s(_vm.school_skill5_grade))]), _vm._v(" "), _c("h5", [_vm._v(_vm._s(_vm.school_skill5_name))])]), _vm._v(" "), _c("li", {
    staticStyle: {
      left: "120px",
      top: "140px"
    }
  }, [_c("img", {
    attrs: {
      referrerpolicy: "no-referrer",
      src: _vm.school_skill6_icon,
      data_equip_name: _vm.school_skill6_name,
      data_skill_type: "school_skill",
      data_equip_desc: _vm.school_skill6_desc,
      data_tip_box: "RoleSkillTipsBox"
    }
  }), _vm._v(" "), _c("p", [_vm._v(_vm._s(_vm.school_skill6_grade))]), _vm._v(" "), _c("h5", [_vm._v(_vm._s(_vm.school_skill6_name))])]), _vm._v(" "), _c("li", {
    staticStyle: {
      left: "60px",
      top: "94px"
    }
  }, [_c("img", {
    attrs: {
      referrerpolicy: "no-referrer",
      src: _vm.school_skill1_icon,
      data_equip_name: _vm.school_skill1_name,
      data_skill_type: "school_skill",
      data_equip_desc: _vm.school_skill1_desc,
      data_tip_box: "RoleSkillTipsBox"
    }
  }), _vm._v(" "), _c("p", [_vm._v(_vm._s(_vm.school_skill1_grade))]), _vm._v(" "), _c("h5", [_vm._v(_vm._s(_vm.school_skill1_name))])]), _vm._v(" "), _c("li", {
    staticStyle: {
      left: "60px",
      top: "200px"
    }
  }, [_c("img", {
    attrs: {
      referrerpolicy: "no-referrer",
      src: _vm.school_skill7_icon,
      data_equip_name: _vm.school_skill7_name,
      data_skill_type: "school_skill",
      data_equip_desc: _vm.school_skill7_desc,
      data_tip_box: "RoleSkillTipsBox"
    }
  }), _vm._v(" "), _c("p", [_vm._v(_vm._s(_vm.school_skill7_grade))]), _vm._v(" "), _c("h5", [_vm._v(_vm._s(_vm.school_skill7_name))])])])])]), _vm._v(" "), _c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "442px",
      "margin-left": "18px"
    }
  }, [_c("h4", [_vm._v("生活技能")]), _vm._v(" "), _c("div", {
    staticClass: "blank12"
  }), _vm._v(" "), _vm.life_skill && _vm.life_skill.length > 0 ? _c("div", [_c("table", {
    staticClass: "skillTb",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "life_skill_lists"
    }
  }, _vm._l(_vm.skillRows(_vm.life_skill, 7), function (row, rowIndex) {
    return _c("tr", {
      key: rowIndex
    }, _vm._l(row, function (item, itemIndex) {
      return _c("td", {
        key: itemIndex
      }, [_c("img", {
        attrs: {
          referrerpolicy: "no-referrer",
          src: item.skill_icon,
          width: "40",
          height: "40",
          data_equip_name: item.name,
          data_skill_type: "life_skill",
          data_equip_desc: item.desc,
          data_tip_box: "RoleSkillTipsBox"
        }
      }), _vm._v(" "), _c("p", [_vm._v(_vm._s(item.skill_grade))]), _vm._v(" "), _c("h5", [_vm._v(_vm._s(item.skill_name))])]);
    }), 0);
  }), 0)]) : _c("div", {
    staticClass: "textCenter",
    staticStyle: {
      "padding-bottom": "30px"
    }
  }, [_vm._v("无")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("h4", [_vm._v("剧情技能")]), _vm._v(" "), _c("div", {
    staticClass: "blank12"
  }), _vm._v(" "), _vm.ju_qing_skill && _vm.ju_qing_skill.length > 0 ? _c("div", [_c("table", {
    staticClass: "skillTb",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "juqing_skill_lists"
    }
  }, _vm._l(_vm.skillRows(_vm.ju_qing_skill, 7), function (row, rowIndex) {
    return _c("tr", {
      key: rowIndex
    }, _vm._l(row, function (item, itemIndex) {
      return _c("td", {
        key: itemIndex
      }, [_c("img", {
        attrs: {
          referrerpolicy: "no-referrer",
          src: item.skill_icon,
          width: "40",
          height: "40",
          data_equip_name: item.name,
          data_skill_type: "ju_qing_skill",
          data_equip_desc: item.desc,
          data_tip_box: "RoleSkillTipsBox"
        }
      }), _vm._v(" "), _c("p", [_vm._v(_vm._s(item.skill_grade))]), _vm._v(" "), _c("h5", [_vm._v(_vm._s(item.skill_name))])]);
    }), 0);
  }), 0)]) : _c("div", {
    staticClass: "textCenter",
    staticStyle: {
      "padding-bottom": "30px"
    }
  }, [_vm._v("无")]), _vm._v(" "), _c("p", {
    staticClass: "textRight cDYellow"
  }, [_vm._v("剩余技能点：" + _vm._s(_vm.left_skill_point))]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("h4", [_vm._v("熟练度")]), _vm._v(" "), _c("table", {
    staticClass: "tb02",
    attrs: {
      width: "92%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tr", [_c("th", {
    attrs: {
      width: "100"
    }
  }, [_vm._v("打造熟练度：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.shuliandu.smith_skill))]), _vm._v(" "), _c("th", {
    attrs: {
      width: "100"
    }
  }, [_vm._v("裁缝熟练度：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.shuliandu.sew_skill))])])])])]) : _vm._e(), _vm._v(" "), _c("el-tab-pane", {
    attrs: {
      label: "道具/法宝",
      name: "role_equips"
    }
  }, [_c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "350px"
    }
  }, [_c("h4", [_vm._v("道具")]), _vm._v(" "), _c("table", {
    staticStyle: {
      margin: "0 auto"
    },
    attrs: {
      width: "80%",
      cellspacing: "3",
      cellpadding: "3",
      id: "RoleUsingEquips"
    }
  }, [_c("tr", [_c("td", {
    attrs: {
      colspan: "3"
    }
  }, [_c("table", {
    staticClass: "tb03 size50",
    attrs: {
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tr", [_c("td", [_c("ItemPopover", {
    attrs: {
      id: "role_using_equip_187",
      equipment: _vm.get_using_equip(187)
    }
  })], 1), _vm._v(" "), _c("td", [_c("ItemPopover", {
    attrs: {
      id: "role_using_equip_187",
      equipment: _vm.get_using_equip(188)
    }
  })], 1), _vm._v(" "), _c("td", [_c("ItemPopover", {
    attrs: {
      id: "role_using_equip_187",
      equipment: _vm.get_using_equip(190)
    }
  })], 1), _vm._v(" "), _c("td", [_c("ItemPopover", {
    attrs: {
      id: "role_using_equip_187",
      equipment: _vm.get_using_equip(189)
    }
  })], 1)])])])]), _vm._v(" "), _c("tr", [_c("td", [_c("table", {
    staticClass: "tb03 size50",
    attrs: {
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tr", [_c("td", [_c("ItemPopover", {
    attrs: {
      id: "role_using_equip_1",
      equipment: _vm.get_using_equip(1)
    }
  })], 1)]), _vm._v(" "), _c("tr", [_c("td", [_c("ItemPopover", {
    attrs: {
      id: "role_using_equip_6",
      equipment: _vm.get_using_equip(6)
    }
  })], 1)]), _vm._v(" "), _c("tr", [_c("td", [_c("ItemPopover", {
    attrs: {
      id: "role_using_equip_5",
      equipment: _vm.get_using_equip(5)
    }
  })], 1)])])]), _vm._v(" "), _c("td", [_c("table", {
    staticClass: "tb02",
    attrs: {
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tr", [_c("th", [_vm._v("现金：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.cash))])]), _vm._v(" "), _c("tr", [_c("th", [_vm._v("存银：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.saving))])]), _vm._v(" "), _c("tr", [_c("th", [_vm._v("储备：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.learn_cash))])]), _vm._v(" "), _c("tr", [_c("th", [_vm._v("善恶：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.badness))])]), _vm._v(" "), _c("tr", [_c("th", [_vm._v("仙玉：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.xianyu))])]), _vm._v(" "), _c("tr", [_c("th", [_vm._v("精力：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.energy))])])])]), _vm._v(" "), _c("td", [_c("table", {
    staticClass: "tb03 size50",
    attrs: {
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tr", [_c("td", [_c("ItemPopover", {
    attrs: {
      equipment: _vm.get_using_equip(4),
      id: "role_using_equip_4"
    }
  })], 1)]), _vm._v(" "), _c("tr", [_c("td", [_c("ItemPopover", {
    attrs: {
      equipment: _vm.get_using_equip(2),
      id: "role_using_equip_2"
    }
  })], 1)]), _vm._v(" "), _c("tr", [_c("td", [_c("ItemPopover", {
    attrs: {
      equipment: _vm.get_using_equip(3),
      id: "role_using_equip3"
    }
  })], 1)])])])])]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("table", {
    staticClass: "tb03 size50",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RoleStoreEquips"
    }
  }, _vm._l(_vm.storeEquipsRows, function (row, rowIndex) {
    return _c("tr", {
      key: rowIndex
    }, [_vm._l(row, function (equip, colIndex) {
      return _c("td", {
        key: colIndex
      }, [_c("ItemPopover", {
        attrs: {
          id: "store_equip_tips" + (rowIndex * 5 + colIndex + 1),
          equipment: equip ? {
            equip_sn: equip.equip_sn,
            equip_face_img: equip.small_icon,
            equip_name: equip.name,
            equip_type_desc: equip.static_desc,
            large_equip_desc: equip.desc,
            lock_type: equip.lock_type
          } : null
        }
      })], 1);
    }), _vm._v(" "), _vm._l(5 - row.length, function (i) {
      return _c("td", {
        key: "empty-" + i
      }, [_c("ItemPopover", {
        attrs: {
          equipment: null
        }
      })], 1);
    })], 2);
  }), 0), _vm._v(" "), _vm.split_equips && _vm.split_equips.length ? _c("div", {
    staticClass: "blank9"
  }) : _vm._e(), _vm._v(" "), _vm.split_equips && _vm.split_equips.length ? _c("h4", [_vm._v("拆卖道具")]) : _vm._e(), _vm._v(" "), _vm.split_equips && _vm.split_equips.length ? _c("table", {
    staticClass: "tb03 size50",
    attrs: {
      cellspacing: "0",
      cellpadding: "3",
      id: "RoleSplitEquips"
    }
  }, _vm._l(_vm.splitEquipsRows, function (row, rowIndex) {
    return _c("tr", {
      key: rowIndex
    }, [_vm._l(row, function (equip, colIndex) {
      return _c("td", {
        key: colIndex
      }, [_c("a", {
        staticStyle: {
          display: "block",
          width: "100%",
          height: "100%"
        },
        attrs: {
          href: _vm.getCBGLinkByType(equip.eid, "equip"),
          target: "_blank",
          tid: "gl03odgw",
          data_trace_text: equip.eid
        }
      }, [_c("ItemPopover", {
        attrs: {
          equipment: _vm.get_using_equip(equip)
        }
      })], 1)]);
    }), _vm._v(" "), _vm._l(5 - row.length, function (i) {
      return _c("td", {
        key: "empty-" + i
      });
    })], 2);
  }), 0) : _vm._e()]), _vm._v(" "), _c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "300px",
      "margin-left": "25px"
    }
  }, [_c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "145px",
      "margin-left": "0"
    }
  }, [_c("h4", [_vm._v("神器")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("table", {
    staticClass: "tb03 size50",
    staticStyle: {
      "table-layout": "fixed"
    },
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RoleStoreShenqi"
    }
  }, [_c("tr", [_c("el-popover", {
    attrs: {
      trigger: "click",
      placement: "bottom",
      "popper-class": "shenqi-info-popover"
    },
    scopedSlots: _vm._u([{
      key: "reference",
      fn: function () {
        return [_vm.shenqi ? _c("td", {
          staticClass: "shenqi_td",
          staticStyle: {
            background: "#c0b9dd"
          },
          attrs: {
            id: "shenqi",
            data_equip_name: _vm.shenqi.name,
            data_equip_type: _vm.shenqi.type,
            data_equip_desc: _vm.shenqi.desc,
            data_equip_type_desc: _vm.shenqi.static_desc
          }
        }, [_c("ItemPopover", {
          attrs: {
            equipment: {
              equip_face_img: _vm.shenqi.icon,
              equip_name: _vm.shenqi.name,
              equip_type_desc: _vm.shenqi.static_desc,
              large_equip_desc: _vm.shenqi.desc
            }
          }
        })], 1) : _vm._e()];
      },
      proxy: true
    }], null, false, 2357829030)
  }, [_vm._v(" "), _c("div", {
    staticClass: "shenqi-modal",
    attrs: {
      id: "shenqiModal"
    }
  }, [_c("h4", {
    staticClass: "modal-head"
  }, [_vm._v("\n                      神器属性 "), _c("span", {
    staticClass: "modal-close-btn",
    attrs: {
      id: "shenqiCloseBtn"
    }
  })]), _vm._v(" "), _c("div", {
    staticClass: "shenqi-modal-content"
  }, [_vm.shenqi?.isNew ? _c("ul", {
    staticClass: "shenqi-tab"
  }, _vm._l(3, function (i) {
    return _c("li", {
      key: i,
      class: ["tab-item", "js_shenqi_tab", !_vm.shenqi_components["shenqi" + i] ? "disable" : _vm.shenqi_components["shenqi" + i] && _vm.shenqi_components["shenqi" + i].actived ? "active" : ""],
      attrs: {
        "data-index": i - 1
      },
      on: {
        click: function ($event) {
          return _vm.switchShenqiTab(i - 1);
        }
      }
    }, [_vm._v("\n                          第" + _vm._s(["一", "二", "三"][i - 1]) + "套属性\n                        ")]);
  }), 0) : _vm._e(), _vm._v(" "), _c("div", {
    staticClass: "shenqi-list"
  }, _vm._l(_vm.shenqi_components, function (modalData, key) {
    return _c("div", {
      key: key,
      staticClass: "js_shenqi_panel",
      style: {
        display: !modalData.actived ? "none" : ""
      }
    }, _vm._l(modalData.components, function (component, compIndex) {
      return _c("div", {
        key: compIndex,
        staticClass: "shenqi-itme"
      }, [_c("div", {
        staticClass: "shenqi-item-left"
      }, [_c("img", {
        attrs: {
          referrerpolicy: "no-referrer",
          src: component.buweiPic
        }
      })]), _vm._v(" "), _c("div", {
        staticClass: "col-r"
      }, [_c("ul", {
        staticClass: "shenqi-item-center"
      }, _vm._l(component.wuxing, function (wuxing, wuxingIndex) {
        return _c("li", {
          key: wuxingIndex
        }, [wuxing.status !== 1 ? _c("div", {
          staticClass: "img-wrap"
        }, [_c("img", {
          attrs: {
            referrerpolicy: "no-referrer",
            src: wuxing.lingxiPic
          }
        })]) : _c("div", [_c("div", {
          staticClass: "img-wrap"
        }, [_c("img", {
          attrs: {
            referrerpolicy: "no-referrer",
            src: wuxing.lingxiPic
          }
        }), _vm._v(" "), wuxing.wuxing_affix_text ? _c("span", {
          staticClass: "cizhui"
        }, [_vm._v(_vm._s(wuxing.wuxing_affix_text))]) : _vm._e()]), _vm._v(" "), _c("p", [_vm._v(_vm._s(wuxing.wuxingText))])])]);
      }), 0), _vm._v(" "), _c("ul", {
        staticClass: "shenqi-item-right"
      }, _vm._l(component.wuxing, function (wuxing, wuxingIndex) {
        return _c("li", {
          key: wuxingIndex
        }, [_vm._v("\n                                  " + _vm._s(wuxing.attr) + "\n                                ")]);
      }), 0)])]);
    }), 0);
  }), 0)])])]), _vm._v(" "), _vm.huoshenta ? _c("td", {
    staticClass: "shenqi_td",
    staticStyle: {
      background: "#c0b9dd"
    },
    attrs: {
      data_equip_name: _vm.huoshenta.name,
      data_equip_type: _vm.shenqi?.type,
      data_equip_desc: _vm.huoshenta.desc,
      data_equip_type_desc: ""
    }
  }, [_c("ItemPopover", {
    attrs: {
      equipment: {
        equip_face_img: _vm.huoshenta.icon,
        equip_name: _vm.huoshenta.name,
        large_equip_desc: _vm.huoshenta.desc
      }
    }
  })], 1) : _vm._e(), _vm._v(" "), !_vm.shenqi && !_vm.huoshenta ? _c("td", {
    staticStyle: {
      background: "rgb(192, 185, 221)"
    }
  }) : _vm._e()], 1)])]), _vm._v(" "), _c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "145px",
      "margin-right": "0"
    }
  }, [_c("h4", [_vm._v("已装备灵宝")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("table", {
    staticClass: "tb03 size50",
    staticStyle: {
      "table-layout": "fixed"
    },
    attrs: {
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tr", {
    attrs: {
      id: "RoleUsingLingbao"
    }
  }, [_vm._l(_vm.using_lingbao.concat([null, null]).slice(0, 2), function (item, i) {
    return [item ? _c("td", {
      key: "lingbao-" + i,
      staticStyle: {
        background: "#c0b9dd"
      },
      attrs: {
        data_equip_name: item.name,
        data_equip_type: item.type,
        data_equip_desc: item.desc,
        data_equip_type_desc: item.static_desc
      }
    }, [_c("ItemPopover", {
      attrs: {
        equipment: {
          equip_face_img: item.icon,
          equip_name: item.name,
          equip_type_desc: item.static_desc,
          large_equip_desc: item.desc
        }
      }
    })], 1) : _c("td", {
      key: "empty-" + i,
      staticStyle: {
        background: "#c0b9dd"
      }
    })];
  })], 2)])])]), _vm._v(" "), _c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "300px",
      "margin-left": "24px"
    }
  }, [_c("div", {
    staticClass: "blank12"
  }), _vm._v(" "), _c("h4", [_vm._v("未装备灵宝")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("div", {
    staticStyle: {
      "max-height": "125px",
      width: "274px",
      overflow: "auto",
      "overflow-x": "hidden",
      margin: "0 auto"
    }
  }, [_c("table", {
    staticClass: "tb03 size50",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RoleNoUsingLingbao"
    }
  }, _vm._l(_vm.nousingLingbaoRows, function (row, rowIndex) {
    return _c("tr", {
      key: rowIndex
    }, [_vm._l(row, function (item, colIndex) {
      return [item ? _c("td", {
        key: "lingbao-" + colIndex,
        staticStyle: {
          background: "#c0b9dd"
        },
        attrs: {
          data_equip_name: item.name,
          data_equip_type: item.type,
          data_equip_desc: item.desc,
          data_equip_type_desc: item.static_desc
        }
      }, [_c("ItemPopover", {
        attrs: {
          equipment: {
            equip_face_img: item.icon,
            equip_name: item.name,
            equip_type_desc: item.static_desc,
            large_equip_desc: item.desc
          }
        }
      })], 1) : _c("td", {
        key: "empty-" + colIndex,
        staticStyle: {
          background: "#c0b9dd"
        }
      })];
    })], 2);
  }), 0)]), _vm._v(" "), _c("div", {
    staticClass: "blank12"
  }), _vm._v(" "), _c("h4", [_vm._v("已装备法宝")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("table", {
    staticClass: "tb03 size50",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RoleUsingFabao"
    }
  }, [_c("tr", _vm._l(4, function (i) {
    return _c("td", {
      key: "fabao-" + i,
      staticStyle: {
        background: "#c0b9dd"
      }
    }, [_c("ItemPopover", {
      attrs: {
        equipment: _vm.get_using_fabao(i),
        align: "middle"
      }
    })], 1);
  }), 0)]), _vm._v(" "), _c("div", {
    staticClass: "blank12"
  }), _vm._v(" "), _c("h4", [_vm._v("\n            未装备的所有法宝\n            "), _vm.unused_fabao_sum !== undefined ? _c("span", [_vm._v("(" + _vm._s(_vm.unused_fabao_sum) + "/" + _vm._s(_vm.fabao_storage_size) + ")")]) : _vm._e()]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("div", {
    staticStyle: {
      height: "205px",
      width: "274px",
      overflow: "auto",
      "overflow-x": "hidden",
      margin: "0 auto"
    },
    attrs: {
      id: "fabao_table_wrapper"
    }
  }, [_c("table", {
    staticClass: "tb03 size50",
    staticStyle: {
      "table-layout": "fixed"
    },
    attrs: {
      width: "256",
      cellspacing: "0",
      cellpadding: "0",
      id: "RoleStoreFabao"
    }
  }, _vm._l(_vm.storeFabaoRows, function (row, rowIndex) {
    return _c("tr", {
      key: rowIndex
    }, [_vm._l(row, function (fabao, colIndex) {
      return fabao ? _c("td", {
        key: colIndex,
        staticStyle: {
          background: "#c0b9dd"
        }
      }, [_c("ItemPopover", {
        attrs: {
          equipment: _vm.get_using_fabao(fabao)
        }
      })], 1) : _vm._e();
    }), _vm._v(" "), _vm._l(5 - row.length, function (i) {
      return _c("td", {
        key: "empty-" + i,
        staticStyle: {
          background: "#c0b9dd"
        }
      });
    })], 2);
  }), 0)]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("table", {
    staticClass: "tb02",
    attrs: {
      width: "100%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tr", [_c("th", {
    attrs: {
      width: "100"
    }
  }, [_vm._v("行囊扩展：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.package_num))])])])])]), _vm._v(" "), _c("el-tab-pane", {
    attrs: {
      label: "召唤兽/孩子",
      name: "role_pets"
    }
  }, [_c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "190px"
    }
  }, [_vm.split_pets && _vm.split_pets.length ? _c("div", [_c("h4", [_vm._v("拆卖召唤兽")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("table", {
    staticClass: "tb03 size50 pet-split-tb",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RoleSplitPets"
    }
  }, [_vm.split_pets.length === 0 ? _c("tr", [_c("td", {
    staticClass: "noData"
  }, [_vm._v("无")])]) : _vm._l(_vm.splitPetsRows, function (row, rowIndex) {
    return _c("tr", {
      key: rowIndex
    }, [_vm._l(row, function (pet, colIndex) {
      return _c("td", {
        key: colIndex
      }, [_c("div", {
        staticClass: "pet-split-img-wrap"
      }, [_c("img", {
        class: {
          on: _vm.current_pet && _vm.current_pet.equip_sn === pet.equip_sn
        },
        attrs: {
          referrerpolicy: "no-referrer",
          src: pet.icon,
          data_idx: rowIndex * 3 + colIndex
        },
        on: {
          click: function ($event) {
            return _vm.onPetAvatarClick(pet);
          }
        }
      })]), _vm._v(" "), _c("a", {
        staticClass: "btn-pet-detail",
        attrs: {
          href: _vm.getCBGLinkByType(pet.eid, "equip"),
          tid: "57i8um2f",
          data_trace_text: pet.eid,
          target: "_blank"
        }
      }, [_vm._v("查看详情")])]);
    }), _vm._v(" "), _vm._l(3 - row.length, function (i) {
      return _c("td", {
        key: "empty-" + i,
        staticStyle: {
          width: "54px",
          height: "54px",
          display: "none"
        }
      }, [_vm._v("\n                     \n                  ")]);
    })], 2);
  })], 2)]) : _vm._e(), _vm._v(" "), _c("h4", [_vm._v("召唤兽(" + _vm._s(_vm.pet_info.length) + "/" + _vm._s(_vm.allow_pet_count) + ")")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("table", {
    staticClass: "tb03 size50",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RolePets"
    }
  }, [_vm.pet_info.length === 0 ? _c("tr", [_c("td", {
    staticClass: "noData"
  }, [_vm._v("无")])]) : _vm._l(_vm.petInfoRows, function (row, rowIndex) {
    return _c("tr", {
      key: rowIndex
    }, [_vm._l(row, function (pet, colIndex) {
      return _c("td", {
        key: colIndex,
        staticStyle: {
          width: "54px",
          height: "54px",
          cursor: "pointer",
          position: "relative"
        }
      }, [_c("img", {
        class: {
          on: _vm.current_pet && _vm.current_pet.equip_sn === pet.equip_sn
        },
        attrs: {
          referrerpolicy: "no-referrer",
          src: pet.icon,
          data_idx: rowIndex * 3 + colIndex
        },
        on: {
          click: function ($event) {
            return _vm.onPetAvatarClick(pet);
          }
        }
      }), _vm._v(" "), _vm.getPetRightLock(pet)?.length > 0 ? _c("div", {
        staticStyle: {
          position: "absolute",
          width: "14px",
          right: "0px",
          top: "0px"
        }
      }, _vm._l(_vm.getPetRightLock(pet), function (l) {
        return _c("img", {
          key: l,
          staticStyle: {
            height: "14px",
            width: "14px",
            display: "block"
          },
          attrs: {
            src: __webpack_require__("./public/assets/images sync recursive ^\\.\\/time_lock_.*\\.webp$")(`./time_lock_${l}.webp`)
          }
        });
      }), 0) : _vm._e(), _vm._v(" "), _vm.getPetLeftLock(pet)?.length > 0 ? _c("div", {
        staticStyle: {
          position: "absolute",
          width: "14px",
          left: "0px",
          top: "0px"
        }
      }, _vm._l(_vm.getPetLeftLock(pet), function (l) {
        return _c("img", {
          key: l,
          staticStyle: {
            height: "14px",
            width: "14px",
            display: "block"
          },
          attrs: {
            src: __webpack_require__("./public/assets/images sync recursive ^\\.\\/time_lock_.*\\.webp$")(`./time_lock_${l}.webp`)
          }
        });
      }), 0) : _vm._e()]);
    }), _vm._v(" "), _vm._l(3 - row.length, function (i) {
      return _c("td", {
        key: "empty-" + i,
        staticStyle: {
          width: "54px",
          height: "54px",
          display: "none"
        }
      }, [_vm._v("\n                   \n                ")]);
    })], 2);
  })], 2), _vm._v(" "), _c("div", {
    staticClass: "blank12"
  }), _vm._v(" "), _c("h4", [_vm._v("孩子")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("table", {
    staticClass: "tb03 size50",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RoleChilds"
    }
  }, [_vm.child_info.length === 0 ? _c("tr", [_c("td", {
    staticClass: "noData"
  }, [_vm._v("无")])]) : _vm._l(_vm.childListRows, function (row, rowIndex) {
    return _c("tr", {
      key: rowIndex
    }, [_vm._l(row, function (child, colIndex) {
      return _c("td", {
        key: colIndex,
        staticStyle: {
          width: "54px",
          height: "54px",
          cursor: "pointer"
        }
      }, [_c("img", {
        class: {
          on: _vm.current_pet && _vm.current_pet.equip_sn === child.equip_sn && _vm.current_pet.index === colIndex
        },
        attrs: {
          referrerpolicy: "no-referrer",
          src: child.icon,
          data_idx: rowIndex * 2 + colIndex
        },
        on: {
          click: function ($event) {
            return _vm.onPetAvatarClick({
              index: colIndex,
              ...child
            });
          }
        }
      })]);
    }), _vm._v(" "), _vm._l(2 - row.length, function (i) {
      return _c("td", {
        key: "empty-" + i,
        staticStyle: {
          width: "54px",
          height: "54px",
          display: "none"
        }
      }, [_vm._v("\n                   \n                ")]);
    })], 2);
  })], 2), _vm._v(" "), _c("div", {
    staticClass: "blank12"
  }), _vm._v(" "), _c("h4", [_vm._v("特殊召唤兽")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("table", {
    staticClass: "tb02",
    attrs: {
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_vm.special_pet_info === undefined ? _c("tr", [_c("td", {
    staticClass: "noData",
    attrs: {
      colspan: "3"
    }
  }, [_vm._v("未知")])]) : _vm.special_pet_info.length === 0 ? _c("tr", [_c("td", {
    staticClass: "noData",
    attrs: {
      colspan: "3"
    }
  }, [_vm._v("无")])]) : [_vm._l(_vm.special_pet_info, function (pet, petIndex) {
    return [_c("tr", {
      key: petIndex
    }, [_c("th", [_vm._v(_vm._s(pet.cName))]), _vm._v(" "), _c("td", [_vm._v(_vm._s(pet.all_skills[0].name))]), _vm._v(" "), _c("td", [_vm._v(_vm._s(pet.all_skills[0].value))])]), _vm._v(" "), _vm._l(pet.all_skills.slice(1), function (skill, skillIndex) {
      return _c("tr", {
        key: skillIndex
      }, [_c("td", [_vm._v(" ")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(skill.name))]), _vm._v(" "), _c("td", [_vm._v(_vm._s(skill.value))])]);
    })];
  })]], 2), _vm._v(" "), _c("div", {
    staticClass: "blank12"
  }), _vm._v(" "), _c("h4", [_vm._v("召唤兽心得技能")]), _vm._v(" "), _c("table", {
    staticClass: "tb02",
    attrs: {
      width: "100%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tbody", [_c("tr", [_c("th", {
    attrs: {
      width: "100"
    }
  }, [_vm._v("已解锁技能数：")]), _vm._v(" "), _c("td", {
    staticClass: "sbook-skill-val",
    attrs: {
      id: "show_more_sbook_skill"
    }
  }, [_vm.sbook_skill && _vm.sbook_skill.length > 0 ? _c("span", {
    staticClass: "text-underline",
    attrs: {
      title: _vm.sbook_skill.join(",")
    }
  }, [_vm._v(_vm._s(_vm.sbook_skill.length) + "/" + _vm._s(_vm.sbook_skill_total))]) : _c("span", [_vm._v("无")])])])])])]), _vm._v(" "), _c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "456px",
      "margin-left": "18px"
    },
    attrs: {
      id: "pet_detail_panel"
    }
  }, [_vm.pet_info.length === 0 && _vm.child_info.length === 0 && _vm.split_pets.length === 0 ? _c("div", [_c("h4", [_vm._v("详细信息")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("table", {
    staticClass: "tb02 petZiZhiTb",
    attrs: {
      width: "100%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tr", [_c("td", {
    staticClass: "noData",
    staticStyle: {
      "text-align": "center"
    }
  }, [_vm._v("无")])])])]) : _vm.current_pet ? _c("PetDetail", {
    attrs: {
      current_pet: _vm.current_pet
    }
  }) : _vm._e()], 1)]), _vm._v(" "), _c("el-tab-pane", {
    attrs: {
      label: "坐骑",
      name: "role_riders"
    }
  }, [_c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "320px"
    }
  }, [_c("h4", [_vm._v("坐骑")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("table", {
    staticClass: "tb03 size50",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RoleRiders"
    }
  }, [_vm.rider_info.length <= 0 ? _c("tr", [_c("td", {
    staticClass: "noData"
  }, [_vm._v("无")])]) : _vm._l(_vm.riderRows, function (row, rowIndex) {
    return _c("tr", {
      key: rowIndex
    }, [_vm._l(row, function (rider, colIndex) {
      return _c("td", {
        key: colIndex,
        staticStyle: {
          width: "54px",
          height: "54px",
          cursor: "pointer"
        }
      }, [_c("img", {
        class: {
          on: _vm.current_rider_index === `${rowIndex}-${colIndex}`
        },
        attrs: {
          referrerpolicy: "no-referrer",
          src: rider.icon,
          width: "50",
          height: "50",
          data_idx: rowIndex * 5 + colIndex
        },
        on: {
          click: function ($event) {
            _vm.current_rider_index = `${rowIndex}-${colIndex}`;
          }
        }
      })]);
    }), _vm._v(" "), _vm._l(5 - row.length, function (i) {
      return _c("td", {
        key: "empty-" + i,
        staticStyle: {
          display: "none"
        }
      });
    })], 2);
  })], 2), _vm._v(" "), _c("div", {
    staticClass: "blank12"
  }), _vm._v(" "), _c("div", {
    attrs: {
      id: "rider_detail_panel"
    }
  }, [_c("table", {
    staticClass: "tb02",
    attrs: {
      width: "100%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tr", [_c("th", [_vm._v("类型：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.currentRider.type_name))]), _vm._v(" "), _c("th", [_vm._v("主属性：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.currentRider.mattrib))])]), _vm._v(" "), _c("tr", [_c("th", [_vm._v("等级：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.currentRider.grade))]), _vm._v(" "), _c("th", [_vm._v(" ")]), _vm._v(" "), _c("td", [_vm._v(" ")])]), _vm._v(" "), _c("tr", [_c("th", [_vm._v("成长：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.currentRider.exgrow))]), _vm._v(" "), _c("th", [_vm._v(" ")]), _vm._v(" "), _c("td", [_vm._v(" ")])])]), _vm._v(" "), _c("div", {
    staticClass: "blank12"
  }), _vm._v(" "), _vm.currentRider && _vm.currentRider.all_skills && _vm.currentRider.all_skills.length > 0 ? _c("div", [_c("table", {
    staticClass: "skillTb",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RoleRiderSkill"
    }
  }, _vm._l(_vm.riderSkillRows, function (row, rowIndex) {
    return _c("tr", {
      key: rowIndex
    }, [_vm._l(row, function (skill, colIndex) {
      return _c("td", {
        key: colIndex
      }, [_c("img", {
        attrs: {
          title: skill.name + " (" + skill.grade + "级)\n" + skill.desc,
          referrerpolicy: "no-referrer",
          src: skill.icon,
          width: "40",
          height: "40",
          data_equip_name: skill.name,
          data_skill_type: "riderSkill",
          data_equip_desc: skill.desc,
          data_equip_level: skill.grade
        }
      }), _vm._v(" "), _c("p", [_vm._v(_vm._s(skill.grade))])]);
    }), _vm._v(" "), _vm._l(6 - row.length, function (i) {
      return _c("td", {
        key: "empty-" + i
      });
    })], 2);
  }), 0)]) : _vm._e()]), _vm._v(" "), _c("h4", [_vm._v("携带玄灵珠")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("div", {
    staticClass: "roleModuleScroller",
    staticStyle: {
      "max-height": "22em"
    }
  }, [_c("table", {
    staticClass: "tb03 size50",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RoleXunlingzhu"
    }
  }, [_vm.rider_plan_list.length > 0 ? _c("tr", _vm._l(_vm.rider_plan_list, function (riderplan, index) {
    return _c("td", {
      key: index,
      staticStyle: {
        width: "54px",
        height: "54px",
        cursor: "pointer"
      }
    }, [riderplan.type == 1 ? _c("img", {
      class: {
        on: _vm.current_rider_plan_index === index
      },
      attrs: {
        referrerpolicy: "no-referrer",
        src: _vm.ResUrl + "/images/big/56973.gif",
        width: "50",
        height: "50",
        data_idx: index
      },
      on: {
        click: function ($event) {
          _vm.current_rider_plan_index = index;
        }
      }
    }) : riderplan.type == 2 ? _c("img", {
      class: {
        on: _vm.current_rider_plan_index === index
      },
      attrs: {
        referrerpolicy: "no-referrer",
        src: _vm.ResUrl + "/images/big/56974.gif",
        width: "50",
        height: "50",
        data_idx: index
      },
      on: {
        click: function ($event) {
          _vm.current_rider_plan_index = index;
        }
      }
    }) : _vm._e(), _vm._v(" "), index == 0 ? _c("span", [_vm._v("第一套")]) : index == 1 ? _c("span", [_vm._v("第二套")]) : _vm._e()]);
  }), 0) : _c("tr", [_c("td", {
    staticClass: "noData"
  }, [_vm._v("无")])])]), _vm._v(" "), _c("div", {
    staticClass: "blank12"
  }), _vm._v(" "), _c("div", {
    attrs: {
      id: "xuanlingzhu_detail_panel"
    }
  }, [_vm.currentRiderPlan ? _c("div", [_c("table", {
    staticClass: "tb02",
    attrs: {
      width: "100%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_vm.currentRiderPlan.type === 1 ? _c("tr", [_c("th", {
    staticStyle: {
      width: "48px"
    }
  }, [_vm._v("类型：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.currentRiderPlan.level) + "级回春")]), _vm._v(" "), _c("th", [_vm._v(" ")]), _vm._v(" "), _c("td", [_vm._v(" ")])]) : _vm._e(), _vm._v(" "), _vm.currentRiderPlan.type === 1 ? _c("tr", [_c("th", {
    staticStyle: {
      width: "48px"
    }
  }, [_vm._v("效果：")]), _vm._v(" "), _c("td", [_vm._v('\n                      战斗中"召唤"召唤兽或孩子时，恢复自身' + _vm._s(_vm.EquipLevel * _vm.currentRiderPlan.level) + "点气血和" + _vm._s(_vm.currentRiderPlan.level) + "点愤怒。\n                    ")])]) : _vm._e(), _vm._v(" "), _vm.currentRiderPlan.type === 2 ? _c("tr", [_c("th", {
    staticStyle: {
      width: "48px"
    }
  }, [_vm._v("类型：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.currentRiderPlan.level) + "级破军")]), _vm._v(" "), _c("th", [_vm._v(" ")]), _vm._v(" "), _c("td", [_vm._v(" ")])]) : _vm._e(), _vm._v(" "), _vm.currentRiderPlan.type === 2 ? _c("tr", [_c("th", {
    staticStyle: {
      width: "48px"
    }
  }, [_vm._v("效果：")]), _vm._v(" "), _c("td", [_vm._v('\n                      战斗中"召唤"召唤兽或孩子时，有' + _vm._s(_vm.currentRiderPlan.level * 12.5) + "%几率提升自身1%伤害，持续到战斗结束。\n                    ")])]) : _vm._e()])]) : _vm._e()])])]), _vm._v(" "), _c("div", {
    staticClass: "cols",
    staticStyle: {
      float: "right",
      width: "320px",
      "margin-right": "28px",
      "margin-bottom": "10px"
    }
  }, [_c("h4", [_vm._v("限量祥瑞")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _vm.nosale_xiangrui == undefined ? _c("div", [_c("p", {
    staticClass: "textCenter cDYellow"
  }, [_vm._v("祥瑞信息未知")])]) : _c("div", {
    staticClass: "roleModuleScroller",
    staticStyle: {
      "max-height": "22em"
    }
  }, [_c("table", {
    staticClass: "tb02",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RoleXiangRui"
    }
  }, [_vm.nosale_xiangrui.length <= 0 ? _c("tr", [_c("td", {
    staticClass: "noData"
  }, [_vm._v("无")])]) : _vm._l(_vm.nosale_xiangrui, function (xiangrui) {
    return _c("tr", {
      key: xiangrui.name
    }, [_c("th", {
      class: {
        enhance: _vm.limitedSkinList.includes(xiangrui.name)
      }
    }, [_vm._v(_vm._s(xiangrui.name))]), _vm._v(" "), _c("td", [_vm._v("\n                    技能：\n                    "), xiangrui.skill_name ? _c("span", [_vm._v("\n                      " + _vm._s(xiangrui.skill_name) + "\n                      "), xiangrui.skill_level ? _c("span", [_vm._v(" " + _vm._s(xiangrui.skill_level))]) : _vm._e()]) : _c("span", [_vm._v("无")])])]);
  })], 2)])]), _vm._v(" "), _c("div", {
    staticClass: "cols",
    staticStyle: {
      float: "right",
      clear: "right",
      width: "320px",
      "margin-right": "28px"
    }
  }, [_c("h4", [_vm._v("普通祥瑞")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _vm.xiangrui == undefined ? _c("div", [_c("p", {
    staticClass: "textCenter cDYellow"
  }, [_vm._v("祥瑞信息未知")])]) : _c("div", {
    staticClass: "roleModuleScroller",
    staticStyle: {
      "max-height": "22em"
    }
  }, [_c("table", {
    staticClass: "tb02",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RoleXiangRui"
    }
  }, [_vm.xiangrui.length <= 0 ? _c("tr", [_c("td", {
    staticClass: "noData"
  }, [_vm._v("无")])]) : [_c("tr", [_c("th", [_vm._v("祥瑞总数")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.normal_xiangrui_num ? _vm.normal_xiangrui_num : _vm.totalXiangruiNum))])]), _vm._v(" "), _vm._l(_vm.xiangrui, function (xiangrui) {
    return _c("tr", {
      key: xiangrui.name
    }, [_c("th", [_vm._v(_vm._s(xiangrui.name))]), _vm._v(" "), _c("td", [_vm._v("\n                    技能：\n                    "), xiangrui.skill_name ? _c("span", [_vm._v("\n                      " + _vm._s(xiangrui.skill_name) + "\n                      "), xiangrui.skill_level ? _c("span", [_vm._v(" " + _vm._s(xiangrui.skill_level))]) : _vm._e()]) : _c("span", [_vm._v("无")])])]);
  })]], 2)])])]), _vm._v(" "), _c("el-tab-pane", {
    attrs: {
      label: "锦衣/外观",
      name: "role_clothes"
    }
  }, [_c("div", {
    staticClass: "cols tab-jinyi",
    staticStyle: {
      width: "320px"
    }
  }, [_c("div", {
    staticClass: "module"
  }, [_c("h4", [_vm._v("彩果染色")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _vm.basic_info.body_caiguo !== undefined && _vm.basic_info.box_caiguo !== undefined ? _c("table", {
    staticClass: "tb02",
    attrs: {
      width: "100%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tr", [_c("th", {
    attrs: {
      width: "55%"
    }
  }, [_vm._v("身上染色折算彩果数：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.body_caiguo))])]), _vm._v(" "), _c("tr", [_c("th", [_vm._v("衣柜已保存染色方案：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.box_caiguo))])]), _vm._v(" "), _c("tr", [_c("td", {
    staticClass: "cGray",
    staticStyle: {
      "font-size": "12px",
      "padding-left": "0px",
      "padding-right": "0px"
    },
    attrs: {
      colspan: "2"
    }
  }, [_vm._v("\n                  （衣柜保存的染色方案包括花豆染色方案和彩果染色方案）\n                ")])]), _vm._v(" "), _c("tr", [_c("th", [_vm._v("所有染色折算彩果数：")]), _vm._v(" "), _c("td", [_vm._v(_vm._s(_vm.basic_info.total_caiguo))])])]) : _vm.basic_info.caiguo !== undefined ? _c("p", {
    staticClass: "textCenter cDYellow"
  }, [_vm._v("\n              角色拥有折算彩果总量：" + _vm._s(_vm.basic_info.caiguo) + "\n            ")]) : _c("p", {
    staticClass: "textCenter cDYellow"
  }, [_vm._v("彩果信息未知")])]), _vm._v(" "), _vm.new_clothes !== undefined ? _c("div", _vm._l(_vm.titleConf, function (item, index) {
    return _c("div", {
      key: index,
      staticClass: "module module-jinyi"
    }, [_c("h4", [_vm._v(_vm._s(item.title))]), _vm._v(" "), _c("p", {
      staticClass: "jinyi-num"
    }, [_vm._v(_vm._s(item.title) + "总数：" + _vm._s(_vm.getClothesList(item.key).length))]), _vm._v(" "), _vm.getClothesList(item.key) ? _c("ul", {
      staticClass: "jinyi-attr-list"
    }, _vm._l(_vm.getClothesList(item.key), function (clothesItem, clothesIndex) {
      return _c("li", {
        key: clothesIndex,
        staticClass: "item"
      }, [_vm._v("\n                  " + _vm._s(clothesItem.name) + "\n                ")]);
    }), 0) : _vm._e()]);
  }), 0) : _vm._e()]), _vm._v(" "), _c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "320px",
      "margin-left": "18px"
    }
  }, [_c("h4", [_vm._v("锦衣道具栏")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _vm.clothes === undefined && _vm.new_clothes === undefined ? _c("p", {
    staticClass: "textCenter cDYellow"
  }, [_vm._v("\n            锦衣信息未知\n          ")]) : _vm.new_clothes !== undefined ? _c("div", [_c("ul", {
    staticClass: "xianyu-wrap"
  }, [_c("li", [_c("i", {
    staticClass: "icon icon-xianyu"
  }), _vm._v("仙玉: " + _vm._s(_vm.basic_info.xianyu))]), _vm._v(" "), _c("li", [_c("i", {
    staticClass: "icon icon-xianyu-jifen"
  }), _vm._v("仙玉积分: " + _vm._s(_vm.basic_info.xianyu_score) + "\n              ")]), _vm._v(" "), _c("li", [_c("i", {
    staticClass: "icon icon-qicai-jifen"
  }), _vm._v("七彩积分: " + _vm._s(_vm.basic_info.qicai_score))])]), _vm._v(" "), _c("div", {
    staticClass: "new-jinyi-list"
  }, [_c("p", {
    staticClass: "jinyi-num"
  }, [_vm._v("锦衣总数：" + _vm._s(_vm.basic_info.total_avatar))]), _vm._v(" "), _vm._l(_vm.new_clothes, function (item, index) {
    return _c("div", {
      key: index,
      class: "module module-jinyi module-jinyi—" + index
    }, [_c("p", {
      staticClass: "jinyi-sub-title"
    }, [_vm._v(_vm._s(item.title))]), _vm._v(" "), item.list.length > 0 ? _c("ul", {
      staticClass: "jinyi-attr-list"
    }, _vm._l(item.list, function (clothesItem, clothesIndex) {
      return _c("li", {
        key: clothesIndex,
        staticClass: "item",
        style: _vm.limitedSkinList.includes(clothesItem.name) ? "background:rgba(255, 102, 0, 0.5);color:rgb(0,255,0);" : ""
      }, [_vm._v("\n                    " + _vm._s(clothesItem.name) + "\n                  ")]);
    }), 0) : _c("p", {
      staticClass: "empty"
    }, [_vm._v("无")])]);
  })], 2)]) : _c("div", [_c("div", {
    staticClass: "roleModuleScroller",
    staticStyle: {
      "max-height": "22em"
    }
  }, [_c("table", {
    staticClass: "tb02",
    attrs: {
      cellspacing: "0",
      cellpadding: "0",
      id: "RoleClothesi"
    }
  }, [_vm.clothes.length <= 0 ? _c("tr", [_c("td", {
    staticClass: "noData"
  }, [_vm._v("无")])]) : [_c("tr", [_c("th", {
    staticStyle: {
      "text-align": "left"
    }
  }, [_vm._v("\n                      锦衣总数 : "), _c("span", {
    staticStyle: {
      color: "white"
    }
  }, [_vm._v(_vm._s(_vm.getTotalAvatar()))])]), _vm._v(" "), _c("th", [_vm._v(" ")])]), _vm._v(" "), _vm._l(_vm.clothesRows, function (row, rowIndex) {
    return _c("tr", {
      key: rowIndex
    }, _vm._l(row, function (clothesItem, colIndex) {
      return _c("th", {
        key: colIndex,
        staticStyle: {
          "text-align": "left"
        }
      }, [_vm._v("\n                      " + _vm._s(clothesItem ? clothesItem.name : "") + "\n                    ")]);
    }), 0);
  })]], 2)])]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  })])]), _vm._v(" "), _c("el-tab-pane", {
    attrs: {
      label: "玩家之家",
      name: "role_home"
    }
  }, [_c("div", {
    staticClass: "cols tab-home",
    staticStyle: {
      width: "320px"
    }
  }, [_c("div", {
    staticClass: "module"
  }, [_c("h4", [_vm._v("房屋信息")]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  }), _vm._v(" "), _c("table", {
    staticClass: "tb02",
    attrs: {
      width: "92%",
      cellspacing: "0",
      cellpadding: "0"
    }
  }, [_c("tr", [_c("td", [_c("strong", [_vm._v("婚否：")]), _vm._v(_vm._s(_vm.basic_info.is_married))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("同袍：")]), _vm._v(_vm._s(_vm.basic_info.is_tongpao))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("居住房屋：")]), _vm._v(_vm._s(_vm.basic_info.fangwu_info))]), _vm._v(" "), _vm.basic_info.fangwu_owner_info ? _c("td", [_c("strong", [_vm._v("是否产权所有人：")]), _vm._v(_vm._s(_vm.basic_info.fangwu_owner_info))]) : _vm._e()]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("庭院等级：")]), _vm._v(_vm._s(_vm.basic_info.tingyuan_info))]), _vm._v(" "), _c("td", [_c("strong", [_vm._v("牧场：")]), _vm._v(_vm._s(_vm.basic_info.muchang_info))])]), _vm._v(" "), _c("tr", [_c("td", [_c("strong", [_vm._v("社区：")]), _vm._v(_vm._s(_vm.basic_info.community_info))])]), _vm._v(" "), _c("tr", [_c("td", {
    attrs: {
      colspan: "3"
    }
  }, [_c("strong", [_vm._v("房契：")]), _vm._v(_vm._s(_vm.basic_info.house_fangqi))])])]), _vm._v(" "), _c("div", {
    staticClass: "module module-jinyi"
  }, [_c("h4", [_vm._v("窗景")]), _vm._v(" "), _c("p", {
    staticClass: "jinyi-num"
  }, [_vm._v("窗景总数：" + _vm._s(_vm.house.house_indoor_view_cnt))]), _vm._v(" "), _vm.house.house_indoor_view && _vm.house.house_indoor_view.length ? _c("ul", {
    staticClass: "jinyi-attr-list roleplay-attr-list"
  }, _vm._l(_vm.house.house_indoor_view, function (item) {
    return _c("li", {
      key: item.name,
      staticClass: "item"
    }, [_vm._v(_vm._s(item.name))]);
  }), 0) : _vm._e()]), _vm._v(" "), _c("div", {
    staticClass: "module module-jinyi"
  }, [_c("h4", [_vm._v("庭院主题")]), _vm._v(" "), _c("p", {
    staticClass: "jinyi-num"
  }, [_vm._v("庭院主题总数：" + _vm._s(_vm.house.house_yard_map_cnt))]), _vm._v(" "), _vm.house.house_yard_map && _vm.house.house_yard_map.length ? _c("ul", {
    staticClass: "jinyi-attr-list roleplay-attr-list"
  }, _vm._l(_vm.house.house_yard_map, function (item) {
    return _c("li", {
      key: item.name,
      staticClass: "item"
    }, [_vm._v(_vm._s(item.name))]);
  }), 0) : _vm._e()]), _vm._v(" "), _c("div", {
    staticClass: "module module-jinyi"
  }, [_c("h4", [_vm._v("庭院特效")]), _vm._v(" "), _c("p", {
    staticClass: "jinyi-num"
  }, [_vm._v("庭院特效总数：" + _vm._s(_vm.house.house_yard_animate_cnt))]), _vm._v(" "), _vm.house.house_yard_animate && _vm.house.house_yard_animate.length ? _c("ul", {
    staticClass: "jinyi-attr-list roleplay-attr-list"
  }, _vm._l(_vm.house.house_yard_animate, function (item) {
    return _c("li", {
      key: item.name,
      staticClass: "item"
    }, [_vm._v(_vm._s(item.name))]);
  }), 0) : _vm._e()]), _vm._v(" "), _c("div", {
    staticClass: "module module-jinyi"
  }, [_c("h4", [_vm._v("庭院饰品")]), _vm._v(" "), _c("p", {
    staticClass: "jinyi-num"
  }, [_vm._v("庭院饰品总数：" + _vm._s(_vm.house.house_yard_fur_cnt))]), _vm._v(" "), _vm.house.house_yard_fur && _vm.house.house_yard_fur.length ? _c("ul", {
    staticClass: "jinyi-attr-list roleplay-attr-list"
  }, _vm._l(_vm.house.house_yard_fur, function (item) {
    return _c("li", {
      key: item.name,
      staticClass: "item"
    }, [_vm._v(_vm._s(item.name) + "*" + _vm._s(item.count))]);
  }), 0) : _vm._e()])])]), _vm._v(" "), _c("div", {
    staticClass: "cols",
    staticStyle: {
      width: "320px",
      "margin-left": "18px"
    }
  }, [_c("div", {
    staticClass: "module module-jinyi module-roleplay"
  }, [_c("h4", [_vm._v("建材")]), _vm._v(" "), _c("p", {
    staticClass: "jinyi-num"
  }, [_vm._v("建材总数：" + _vm._s(_vm.house.house_building_material_cnt))]), _vm._v(" "), _vm.house.house_building_material && _vm.house.house_building_material.length ? _c("ul", {
    staticClass: "jinyi-attr-list roleplay-attr-list"
  }, _vm._l(_vm.house.house_building_material, function (item) {
    return _c("li", {
      key: item.name,
      staticClass: "item"
    }, [_c("span", [_vm._v(_vm._s(item.name))]), _vm._v("*" + _vm._s(item.count) + "\n              ")]);
  }), 0) : _vm._e()]), _vm._v(" "), _c("div", {
    staticClass: "module module-jinyi"
  }, [_c("h4", [_vm._v("家具")]), _vm._v(" "), _c("p", {
    staticClass: "jinyi-num"
  }, [_vm._v("家具总数：" + _vm._s(_vm.house.house_jiaju_num))]), _vm._v(" "), _vm.house.house_jiaju && _vm.house.house_jiaju.length ? _c("ul", {
    staticClass: "jinyi-attr-list roleplay-attr-list"
  }, _vm._l(_vm.house.house_jiaju, function (item) {
    return _c("li", {
      key: item.name,
      staticClass: "item"
    }, [_c("span", [_vm._v(_vm._s(item.name))]), _vm._v("*" + _vm._s(item.count) + "\n              ")]);
  }), 0) : _vm._e()]), _vm._v(" "), _c("div", {
    staticClass: "blank9"
  })])])], 1)], 1) : _vm._e()]);
};
var staticRenderFns = [];
render._withStripped = true;


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/chrome-extensions/DevToolsPanel.vue?vue&type=style&index=0&id=42c7142d&scoped=true&lang=css":
/*!*******************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/chrome-extensions/DevToolsPanel.vue?vue&type=style&index=0&id=42c7142d&scoped=true&lang=css ***!
  \*******************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../node_modules/css-loader/dist/runtime/getUrl.js */ "./node_modules/css-loader/dist/runtime/getUrl.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_2__);
// Imports



var ___CSS_LOADER_URL_IMPORT_0___ = new URL(/* asset import */ __webpack_require__(/*! ../../public/assets/images/areabg.webp */ "./public/assets/images/areabg.webp"), __webpack_require__.b);
var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
var ___CSS_LOADER_URL_REPLACEMENT_0___ = _node_modules_css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_2___default()(___CSS_LOADER_URL_IMPORT_0___);
// Module
___CSS_LOADER_EXPORT___.push([module.id, "\n.devtools-panel[data-v-42c7142d] {\n  box-sizing: border-box;\n  padding: 16px;\n  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;\n  background: #f5f5f5;\n  min-height: 100vh;\n  background: url(" + ___CSS_LOADER_URL_REPLACEMENT_0___ + ") repeat-y;\n  width: 960px;\n  margin: 0 auto;\n}\n.panel-header[data-v-42c7142d] {\n  display: flex;\n  justify-content: space-between;\n  align-items: center;\n  margin-bottom: 20px;\n  padding-bottom: 12px;\n  border-bottom: 1px solid #e0e0e0;\n}\n.panel-header h3[data-v-42c7142d] {\n  margin: 0;\n  color: #333;\n  font-size: 18px;\n}\n.connection-status[data-v-42c7142d] {\n  display: flex;\n  align-items: center;\n  gap: 10px;\n}\n.data-section h4[data-v-42c7142d] {\n  margin: 0 0 12px 0;\n  color: #666;\n  font-size: 14px;\n}\n.empty-state[data-v-42c7142d] {\n  text-align: center;\n  padding: 40px 20px;\n  color: #999;\n  background: white;\n  border-radius: 4px;\n  border: 1px dashed #ddd;\n}\n.request-list[data-v-42c7142d] {\n  background: white;\n  border-radius: 4px;\n  border: 1px solid #e0e0e0;\n  overflow: hidden;\n}\n.request-item[data-v-42c7142d] {\n  border-bottom: 1px solid #f0f0f0;\n  padding: 12px 16px;\n  transition: background-color 0.2s;\n}\n.request-item[data-v-42c7142d]:last-child {\n  border-bottom: none;\n}\n.request-item[data-v-42c7142d]:hover {\n  background-color: #fafafa;\n}\n.request-item.completed[data-v-42c7142d] {\n  background-color: #f0f9ff;\n  border-left: 3px solid #1890ff;\n}\n.request-info[data-v-42c7142d] {\n  margin-bottom: 8px;\n}\n.request-url[data-v-42c7142d] {\n  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;\n  font-size: 12px;\n  color: #333;\n  word-break: break-all;\n  margin-bottom: 4px;\n}\n.request-meta[data-v-42c7142d] {\n  display: flex;\n  gap: 12px;\n  font-size: 11px;\n}\n.method[data-v-42c7142d] {\n  background: #1890ff;\n  color: white;\n  padding: 2px 6px;\n  border-radius: 2px;\n  font-weight: bold;\n}\n.status[data-v-42c7142d] {\n  padding: 2px 6px;\n  border-radius: 2px;\n  font-weight: bold;\n}\n.status.pending[data-v-42c7142d] {\n  background: #faad14;\n  color: white;\n}\n.status.completed[data-v-42c7142d] {\n  background: #52c41a;\n  color: white;\n}\n.timestamp[data-v-42c7142d] {\n  color: #999;\n}\n.response-data[data-v-42c7142d] {\n  margin-top: 8px;\n  padding-top: 8px;\n  border-top: 1px solid #f0f0f0;\n}\n.response-content[data-v-42c7142d] {\n  margin-top: 8px;\n  background: #f8f8f8;\n  border-radius: 4px;\n  padding: 8px;\n  max-height: 300px;\n  overflow-y: auto;\n}\n.response-content pre[data-v-42c7142d] {\n  margin: 0;\n  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;\n  font-size: 11px;\n  line-height: 1.4;\n  color: #333;\n  white-space: pre-wrap;\n  word-break: break-word;\n}\n", "",{"version":3,"sources":["webpack://./src/chrome-extensions/DevToolsPanel.vue"],"names":[],"mappings":";AAijBA;EACA,sBAAA;EACA,aAAA;EACA,gFAAA;EACA,mBAAA;EACA,iBAAA;EACA,4DAAA;EACA,YAAA;EACA,cAAA;AACA;AAEA;EACA,aAAA;EACA,8BAAA;EACA,mBAAA;EACA,mBAAA;EACA,oBAAA;EACA,gCAAA;AACA;AAEA;EACA,SAAA;EACA,WAAA;EACA,eAAA;AACA;AAEA;EACA,aAAA;EACA,mBAAA;EACA,SAAA;AACA;AAEA;EACA,kBAAA;EACA,WAAA;EACA,eAAA;AACA;AAEA;EACA,kBAAA;EACA,kBAAA;EACA,WAAA;EACA,iBAAA;EACA,kBAAA;EACA,uBAAA;AACA;AAEA;EACA,iBAAA;EACA,kBAAA;EACA,yBAAA;EACA,gBAAA;AACA;AAEA;EACA,gCAAA;EACA,kBAAA;EACA,iCAAA;AACA;AAEA;EACA,mBAAA;AACA;AAEA;EACA,yBAAA;AACA;AAEA;EACA,yBAAA;EACA,8BAAA;AACA;AAEA;EACA,kBAAA;AACA;AAEA;EACA,wDAAA;EACA,eAAA;EACA,WAAA;EACA,qBAAA;EACA,kBAAA;AACA;AAEA;EACA,aAAA;EACA,SAAA;EACA,eAAA;AACA;AAEA;EACA,mBAAA;EACA,YAAA;EACA,gBAAA;EACA,kBAAA;EACA,iBAAA;AACA;AAEA;EACA,gBAAA;EACA,kBAAA;EACA,iBAAA;AACA;AAEA;EACA,mBAAA;EACA,YAAA;AACA;AAEA;EACA,mBAAA;EACA,YAAA;AACA;AAEA;EACA,WAAA;AACA;AAEA;EACA,eAAA;EACA,gBAAA;EACA,6BAAA;AACA;AAEA;EACA,eAAA;EACA,mBAAA;EACA,kBAAA;EACA,YAAA;EACA,iBAAA;EACA,gBAAA;AACA;AAEA;EACA,SAAA;EACA,wDAAA;EACA,eAAA;EACA,gBAAA;EACA,WAAA;EACA,qBAAA;EACA,sBAAA;AACA","sourcesContent":["<template>\n  <div class=\"devtools-panel\">\n    <div class=\"panel-header\">\n      <h3>梦幻灵瞳</h3>\n      <div class=\"connection-status\">\n        <el-tag :type=\"devtoolsConnected ? 'success' : 'warning'\" size=\"mini\">\n          {{ connectionStatus }}\n        </el-tag>\n        <el-button @click=\"prevPage\" size=\"mini\">上一页</el-button>\n        <el-button @click=\"nextPage\" size=\"mini\">下一页</el-button>\n        <el-button @click=\"getPageInfo\" size=\"mini\" type=\"info\">页码信息</el-button>\n        <el-button @click=\"reconnectDevTools\" size=\"mini\" type=\"warning\" v-if=\"!devtoolsConnected\">重连</el-button>\n        <el-button @click=\"clearData\" size=\"mini\" type=\"danger\">清空数据</el-button>\n      </div>\n    </div>\n    <div class=\"data-section\">\n      <el-empty v-if=\"recommendData.length === 0\" class=\"empty-state\" description=\"暂无数据，请访问梦幻西游藏宝阁页面\"></el-empty>\n      <div v-else class=\"request-list\">\n        <div v-for=\"item in recommendData\" :key=\"item.requestId\" class=\"request-item\"\n          :class=\"{ 'completed': item.status === 'completed' }\">\n          <div class=\"request-info\">\n            <div class=\"request-meta\">\n              <span class=\"status\" :class=\"item.status\">{{ item.status }}</span>\n              <span class=\"timestamp\">{{ formatTime(item.timestamp) }}</span>\n            </div>\n          </div>\n          <div v-if=\"item.responseData\" class=\"response-data\">\n            <el-row class=\"roles\" type=\"flex\">\n              <span v-for=\"role in parseListData(item.responseData)?.equip_list\" :key=\"role.eid\">\n                <RoleImage :key=\"role.eid\" :other_info=\"role.other_info\" :roleInfo=\"parserRoleData(role)\" />\n              </span>\n            </el-row>\n          </div>\n        </div>\n      </div>\n    </div>\n  </div>\n</template>\n<script>\nimport RoleImage from '@/components/RoleInfo/RoleImage.vue'\nexport default {\n  name: 'DevToolsPanel',\n  data() {\n    return {\n      recommendData: [],\n      expandedItems: [],\n      processedRequests: new Set(), // 记录已处理的请求ID\n      devtoolsConnected: false, // DevTools Protocol连接状态\n      connectionStatus: '检查中...', // 连接状态描述\n      connectionCheckTimer: null // 连接检查定时器\n    }\n  },\n  components: {\n    RoleImage\n  },\n  computed: {\n\n  },\n  mounted() {\n    this.initMessageListener()\n    this.checkConnectionStatus()\n\n    // // 设置定时检查（每5秒检查一次）\n    // this.connectionCheckTimer = setInterval(() => {\n    //   this.checkConnectionStatus()\n    // }, 5000)\n  },\n  beforeDestroy() {\n    // 移除Chrome消息监听器\n    this.removeMessageListener()\n    // 清理定时器\n    if (this.connectionCheckTimer) {\n      clearInterval(this.connectionCheckTimer)\n      this.connectionCheckTimer = null\n    }\n    // 清理组件状态\n    this.recommendData = []\n    this.expandedItems = []\n  },\n  methods: {\n    nextPage(){\n      // 通过Chrome调试API查找并点击页面上的分页器\n      this.clickPageButton('next')\n    },\n    \n    prevPage(){\n      // 通过Chrome调试API查找并点击页面上的分页器\n      this.clickPageButton('prev')\n    },\n    \n    getPageInfo(){\n      // 获取当前分页器信息\n      this.getPagerInfo()\n    },\n    \n    reconnectDevTools(){\n      // 重新连接DevTools\n      this.connectionStatus = '重连中...'\n      this.checkConnectionStatus()\n      this.$message.info('正在尝试重新连接DevTools...')\n    },\n    \n    async clickPageButton(direction) {\n      try {\n        // 获取当前活动标签页\n        const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true })\n        \n        if (!activeTab || !activeTab.url.includes('cbg.163.com')) {\n          this.$message.warning('请先访问梦幻西游藏宝阁页面')\n          return\n        }\n\n        // 检查Chrome调试API连接状态\n        if (!this.devtoolsConnected) {\n          this.$message.warning('DevTools连接已断开，请重新加载页面')\n          return\n        }\n\n        // 通过Chrome调试API执行页面JavaScript代码\n        const result = await chrome.debugger.sendCommand(\n          { tabId: activeTab.id },\n          'Runtime.evaluate',\n          {\n            expression: `\n              (function() {\n                try {\n                  // 查找id为pager的div\n                  const pagerDiv = document.getElementById('pager')\n                  if (!pagerDiv) {\n                    return 'ERROR:未找到分页器元素'\n                  }\n                  \n                  let targetButton = null\n                  const isNext = '${direction}' === 'next'\n                  \n                  if (isNext) {\n                    // 查找下一页按钮 - 根据实际HTML格式优化\n                    // 1. 优先查找包含\"下一页\"文本的链接\n                    const allLinks = pagerDiv.querySelectorAll('a')\n                    for (let link of allLinks) {\n                      const text = link.textContent.trim()\n                      if (text === '下一页') {\n                        targetButton = link\n                        break\n                      }\n                    }\n                    \n                    // 2. 如果没找到\"下一页\"，查找包含goto函数的链接（排除当前页）\n                    if (!targetButton) {\n                      for (let link of allLinks) {\n                        const href = link.getAttribute('href')\n                        const text = link.textContent.trim()\n                        // 查找包含goto且不是当前页的链接\n                        if (href && href.includes('goto(') && !link.classList.contains('on')) {\n                          // 获取当前页码\n                          const currentPageLink = pagerDiv.querySelector('a.on')\n                          if (currentPageLink) {\n                            const currentPageText = currentPageLink.textContent.trim()\n                            const currentPage = parseInt(currentPageText)\n                            const linkPage = parseInt(text)\n                            // 如果链接页码大于当前页码，说明是下一页\n                            if (!isNaN(linkPage) && linkPage > currentPage) {\n                              targetButton = link\n                              break\n                            }\n                          }\n                        }\n                      }\n                    }\n                  } else {\n                    // 查找上一页按钮\n                    const allLinks = pagerDiv.querySelectorAll('a')\n                    \n                    // 1. 优先查找包含\"上一页\"文本的链接\n                    for (let link of allLinks) {\n                      const text = link.textContent.trim()\n                      if (text === '上一页') {\n                        targetButton = link\n                        break\n                      }\n                    }\n                    \n                    // 2. 如果没找到\"上一页\"，查找包含goto函数的链接（排除当前页）\n                    if (!targetButton) {\n                      for (let link of allLinks) {\n                        const href = link.getAttribute('href')\n                        const text = link.textContent.trim()\n                        // 查找包含goto且不是当前页的链接\n                        if (href && href.includes('goto(') && !link.classList.contains('on')) {\n                          // 获取当前页码\n                          const currentPageLink = pagerDiv.querySelector('a.on')\n                          if (currentPageLink) {\n                            const currentPageText = currentPageLink.textContent.trim()\n                            const currentPage = parseInt(currentPageText)\n                            const linkPage = parseInt(text)\n                            // 如果链接页码小于当前页码，说明是上一页\n                            if (!isNaN(linkPage) && linkPage < currentPage) {\n                              targetButton = link\n                              break\n                            }\n                          }\n                        }\n                      }\n                    }\n                  }\n                  \n                  if (!targetButton) {\n                    return 'ERROR:未找到${direction === 'next' ? '下一页' : '上一页'}按钮'\n                  }\n                  \n                  // 检查按钮是否可点击\n                  if (targetButton.disabled || targetButton.classList.contains('disabled')) {\n                    return 'ERROR:${direction === 'next' ? '下一页' : '上一页'}按钮不可点击，可能已到${direction === 'next' ? '最后一页' : '第一页'}'\n                  }\n                  \n                  // 获取当前页码信息用于日志\n                  const currentPageLink = pagerDiv.querySelector('a.on')\n                  let currentPageInfo = ''\n                  if (currentPageLink) {\n                    const currentPageText = currentPageLink.textContent.trim()\n                    currentPageInfo = ' (当前第' + currentPageText + '页)'\n                  }\n                  \n                  // 点击按钮\n                  targetButton.click()\n                  return 'SUCCESS:已点击${direction === 'next' ? '下一页' : '上一页'}按钮' + currentPageInfo\n                } catch (error) {\n                  return 'ERROR:执行失败 - ' + error.message\n                }\n              })()\n            `\n          }\n        )\n\n        // 处理Chrome调试API的返回结果\n          if (result && result.result && result.result.value) {\n            const message = result.result.value\n            \n            if (message.startsWith('SUCCESS:')) {\n              this.$message.success(message.substring(8)) // 移除\"SUCCESS:\"前缀\n              console.log(`${direction === 'next' ? '下一页' : '上一页'}按钮点击成功`)\n            } else if (message.startsWith('ERROR:')) {\n              this.$message.warning(message.substring(6)) // 移除\"ERROR:\"前缀\n              console.warn(`${direction === 'next' ? '下一页' : '上一页'}按钮点击失败:`, message)\n            } else {\n              this.$message.error('执行页面操作失败：未知返回结果')\n              console.error('页面操作结果异常:', result)\n            }\n          } else {\n            this.$message.error('执行页面操作失败')\n            console.error('页面操作结果异常:', result)\n          }\n          \n        } catch (error) {\n          console.error(`点击${direction === 'next' ? '下一页' : '上一页'}按钮失败:`, error)\n          \n          // 检查是否是连接断开错误\n          if (error.message && error.message.includes('Could not establish connection')) {\n            this.devtoolsConnected = false\n            this.connectionStatus = '连接断开'\n            this.$message.error('DevTools连接已断开，请重新加载页面或刷新扩展')\n          } else {\n            this.$message.error('操作失败: ' + error.message)\n          }\n        }\n    },\n    \n    async getPagerInfo() {\n      try {\n        // 获取当前活动标签页\n        const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true })\n        \n        if (!activeTab || !activeTab.url.includes('cbg.163.com')) {\n          this.$message.warning('请先访问梦幻西游藏宝阁页面')\n          return\n        }\n\n        // 检查Chrome调试API连接状态\n        if (!this.devtoolsConnected) {\n          this.$message.warning('DevTools连接已断开，请重新加载页面')\n          return\n        }\n\n        // 通过Chrome调试API执行页面JavaScript代码获取分页器信息\n        const result = await chrome.debugger.sendCommand(\n          { tabId: activeTab.id },\n          'Runtime.evaluate',\n          {\n            expression: `\n              (function() {\n                try {\n                  // 查找id为pager的div\n                  const pagerDiv = document.getElementById('pager')\n                  if (!pagerDiv) {\n                    return 'ERROR:未找到分页器元素'\n                  }\n                  \n                  // 获取当前页码\n                  const currentPageLink = pagerDiv.querySelector('a.on')\n                  let currentPage = '未知'\n                  if (currentPageLink) {\n                    currentPage = currentPageLink.textContent.trim()\n                  }\n                  \n                  // 获取所有页码链接\n                  const allPageLinks = pagerDiv.querySelectorAll('a[href*=\"goto(\"]')\n                  const pageNumbers = []\n                  allPageLinks.forEach(link => {\n                    const text = link.textContent.trim()\n                    if (text.match(/^\\d+$/)) {\n                      pageNumbers.push(parseInt(text))\n                    }\n                  })\n                  \n                  // 计算总页数（取最大页码）\n                  const totalPages = pageNumbers.length > 0 ? Math.max(...pageNumbers) : '未知'\n                  \n                  // 检查是否有上一页/下一页按钮\n                  const hasPrev = pagerDiv.querySelector('a[href*=\"goto(\"]') && \n                                 pagerDiv.textContent.includes('上一页')\n                  const hasNext = pagerDiv.querySelector('a[href*=\"goto(\"]') && \n                                 pagerDiv.textContent.includes('下一页')\n                  \n                  return 'SUCCESS:第' + currentPage + '页，共' + totalPages + '页 (上一页:' + (hasPrev ? '有' : '无') + ', 下一页:' + (hasNext ? '有' : '无') + ')'\n                } catch (error) {\n                  return 'ERROR:获取分页器信息失败 - ' + error.message\n                }\n              })()\n            `\n          }\n        )\n\n        // 处理返回结果\n        if (result && result.result && result.result.value) {\n          const message = result.result.value\n          \n          if (message.startsWith('SUCCESS:')) {\n            this.$message.info(message.substring(8)) // 移除\"SUCCESS:\"前缀\n            console.log('分页器信息获取成功:', message)\n          } else if (message.startsWith('ERROR:')) {\n            this.$message.warning(message.substring(6)) // 移除\"ERROR:\"前缀\n            console.warn('分页器信息获取失败:', message)\n          } else {\n            this.$message.error('获取分页器信息失败：未知返回结果')\n            console.error('分页器信息获取结果异常:', result)\n          }\n        } else {\n          this.$message.error('获取分页器信息失败')\n          console.error('分页器信息获取结果异常:', result)\n        }\n        \n      } catch (error) {\n        console.error('获取分页器信息失败:', error)\n        \n        // 检查是否是连接断开错误\n        if (error.message && error.message.includes('Could not establish connection')) {\n          this.devtoolsConnected = false\n          this.connectionStatus = '连接断开'\n          this.$message.error('DevTools连接已断开，请重新加载页面或刷新扩展')\n        } else {\n          this.$message.error('操作失败: ' + error.message)\n        }\n      }\n    },\n    parserRoleData(data) {\n      const roleInfo = new window.RoleInfoParser(data.large_equip_desc, { equip_level: data.equip_level })\n      return roleInfo.result\n      // return {\n      //   RoleInfoParser: roleInfo,\n      //   roleInfo: roleInfo.result,\n      //   accept_bargain: data.accept_bargain,\n      //   collect_num: data.collect_num,\n      //   dynamic_tags: data.dynamic_tags,\n      //   eid: data.eid,\n      //   highlight: data.highlight,\n      //   is_split_independent_role: data.is_split_independent_role,\n      //   is_split_main_role: data.is_split_main_role,\n      //   large_equip_desc: data.large_equip_desc,\n      //   level: data.level,\n      //   other_info: data.other_info,\n      //   school: data.school,\n      //   seller_nickname: data.seller_nickname,\n      //   server_name: data.server_name,\n      //   serverid: data.serverid,\n      //   price: data.price,\n      //   sum_exp: data.sum_exp,\n      //   create_time: data.create_time,\n      //   update_time: data.create_time,\n      //   all_equip_json: '',\n      //   all_summon_json: '',\n      //   split_price_desc: '',\n      //   pet_price: '',\n      //   equip_price: '',\n      //   base_price: '',\n      //   history_price: '',\n      // }\n    },\n    parseListData(responseDataStr) {\n      // 解析响应数据 Request.JSONP.request_map.request_数字(xxxx) 中的xxxx\n      const match = responseDataStr.match(/Request\\.JSONP\\.request_map\\.request_\\d+\\((.*)\\)/)\n      let templateJSONStr = '{}'\n      if (match) {\n        templateJSONStr = match[1]\n      }\n      try {\n        const templateJSON = JSON.parse(templateJSONStr)\n        return templateJSON\n      } catch (error) {\n        console.error('解析响应数据失败:', error)\n        return {}\n      }\n    },\n    initMessageListener() {\n      console.log('DevToolsPanel mounted, initializing listener')\n\n      // 使用单例模式确保只有一个监听器\n      if (typeof chrome !== 'undefined' && chrome.runtime) {\n        // 如果已经有全局监听器，先移除\n        if (window.cbgDevToolsListener) {\n          chrome.runtime.onMessage.removeListener(window.cbgDevToolsListener)\n        }\n\n        // 创建全局监听器\n        window.cbgDevToolsListener = (request, sender, sendResponse) => {\n          console.log('DevToolsPanel received Chrome message:', request.action)\n          this.handleChromeMessage(request, sender, sendResponse)\n          sendResponse({ success: true })\n        }\n\n        // 注册监听器\n        chrome.runtime.onMessage.addListener(window.cbgDevToolsListener)\n        console.log('Chrome message listener registered for DevToolsPanel')\n      }\n    },\n\n    removeMessageListener() {\n      // 移除Chrome消息监听器\n      if (typeof chrome !== 'undefined' && chrome.runtime && window.cbgDevToolsListener) {\n        chrome.runtime.onMessage.removeListener(window.cbgDevToolsListener)\n        delete window.cbgDevToolsListener\n        console.log('Chrome message listener removed for DevToolsPanel')\n      }\n    },\n\n    checkConnectionStatus() {\n      // 检查Chrome扩展连接状态\n      if (typeof chrome !== 'undefined' && chrome.runtime) {\n        // 尝试发送ping消息检查连接\n        chrome.runtime.sendMessage({ action: 'ping' }, (response) => {\n          if (chrome.runtime.lastError) {\n            console.log('Chrome extension connection check failed:', chrome.runtime.lastError)\n            this.devtoolsConnected = false\n            this.connectionStatus = '未连接'\n          } else if (response && response.success) {\n            console.log('Chrome extension connection check successful:', response)\n            this.devtoolsConnected = true\n            this.connectionStatus = '已连接'\n          } else {\n            console.log('Chrome extension connection check failed: invalid response')\n            this.devtoolsConnected = false\n            this.connectionStatus = '连接异常'\n          }\n        })\n      } else {\n        console.log('Chrome runtime not available')\n        this.devtoolsConnected = false\n        this.connectionStatus = 'Chrome环境不可用'\n      }\n    },\n\n    handleChromeMessage(request, sender, sendResponse) {\n      switch (request.action) {\n        case 'updateRecommendData':\n          this.recommendData = request.data || []\n\n          // 只处理新完成的请求，避免重复处理\n          if (this.recommendData && this.recommendData.length > 0) {\n            this.recommendData.forEach(item => {\n              if (item.status === 'completed' &&\n                item.responseData &&\n                item.url &&\n                item.requestId &&\n                !this.processedRequests.has(item.requestId)) {\n\n                // 标记为已处理\n                this.processedRequests.add(item.requestId)\n                console.log(`开始处理新请求: ${item.requestId}`)\n\n                // 调用解析响应数据接口\n                this.$api.spider.parseResponse({\n                  url: item.url,\n                  response_text: item.responseData\n                }).then(res => {\n                  console.log(`请求 ${item.requestId} 解析结果:`, res)\n                  if (res.code === 200) {\n                    console.log(`请求 ${item.requestId} 数据解析成功:`, res.data)\n                  } else {\n                    console.error(`请求 ${item.requestId} 数据解析失败:`, res.message)\n                  }\n                }).catch(error => {\n                  console.error(`请求 ${item.requestId} 解析请求失败:`, error)\n                  // 解析失败时移除标记，允许重试\n                  this.processedRequests.delete(item.requestId)\n                })\n              }\n            })\n          }\n          break\n\n        case 'devtoolsConnected':\n          this.devtoolsConnected = true\n          this.connectionStatus = '已连接'\n          this.$message.success(request.message)\n          break\n\n        case 'showDebuggerWarning':\n          this.devtoolsConnected = false\n          this.connectionStatus = '连接冲突'\n          this.$message.warning(request.message)\n          break\n\n        case 'clearRecommendData':\n          this.recommendData = []\n          this.expandedItems = []\n          this.processedRequests.clear()\n          console.log('清空推荐数据和处理记录')\n          break\n      }\n    },\n\n\n    clearData() {\n      this.recommendData = []\n      this.expandedItems = []\n      // 通知background script清空数据\n      if (typeof chrome !== 'undefined' && chrome.runtime) {\n        chrome.runtime.sendMessage({\n          action: 'clearRecommendData'\n        })\n      }\n    },\n\n    toggleResponse(index) {\n      const expandedIndex = this.expandedItems.indexOf(index)\n      if (expandedIndex > -1) {\n        this.expandedItems.splice(expandedIndex, 1)\n      } else {\n        this.expandedItems.push(index)\n      }\n    },\n\n    formatTime(timestamp) {\n      if (!timestamp) return ''\n      const date = new Date(timestamp)\n      return date.toLocaleTimeString()\n    }\n  }\n}\n</script>\n\n<style scoped>\n.devtools-panel {\n  box-sizing: border-box;\n  padding: 16px;\n  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;\n  background: #f5f5f5;\n  min-height: 100vh;\n  background: url(../../public/assets/images/areabg.webp) repeat-y;\n  width: 960px;\n  margin: 0 auto;\n}\n\n.panel-header {\n  display: flex;\n  justify-content: space-between;\n  align-items: center;\n  margin-bottom: 20px;\n  padding-bottom: 12px;\n  border-bottom: 1px solid #e0e0e0;\n}\n\n.panel-header h3 {\n  margin: 0;\n  color: #333;\n  font-size: 18px;\n}\n\n.connection-status {\n  display: flex;\n  align-items: center;\n  gap: 10px;\n}\n\n.data-section h4 {\n  margin: 0 0 12px 0;\n  color: #666;\n  font-size: 14px;\n}\n\n.empty-state {\n  text-align: center;\n  padding: 40px 20px;\n  color: #999;\n  background: white;\n  border-radius: 4px;\n  border: 1px dashed #ddd;\n}\n\n.request-list {\n  background: white;\n  border-radius: 4px;\n  border: 1px solid #e0e0e0;\n  overflow: hidden;\n}\n\n.request-item {\n  border-bottom: 1px solid #f0f0f0;\n  padding: 12px 16px;\n  transition: background-color 0.2s;\n}\n\n.request-item:last-child {\n  border-bottom: none;\n}\n\n.request-item:hover {\n  background-color: #fafafa;\n}\n\n.request-item.completed {\n  background-color: #f0f9ff;\n  border-left: 3px solid #1890ff;\n}\n\n.request-info {\n  margin-bottom: 8px;\n}\n\n.request-url {\n  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;\n  font-size: 12px;\n  color: #333;\n  word-break: break-all;\n  margin-bottom: 4px;\n}\n\n.request-meta {\n  display: flex;\n  gap: 12px;\n  font-size: 11px;\n}\n\n.method {\n  background: #1890ff;\n  color: white;\n  padding: 2px 6px;\n  border-radius: 2px;\n  font-weight: bold;\n}\n\n.status {\n  padding: 2px 6px;\n  border-radius: 2px;\n  font-weight: bold;\n}\n\n.status.pending {\n  background: #faad14;\n  color: white;\n}\n\n.status.completed {\n  background: #52c41a;\n  color: white;\n}\n\n.timestamp {\n  color: #999;\n}\n\n.response-data {\n  margin-top: 8px;\n  padding-top: 8px;\n  border-top: 1px solid #f0f0f0;\n}\n\n.response-content {\n  margin-top: 8px;\n  background: #f8f8f8;\n  border-radius: 4px;\n  padding: 8px;\n  max-height: 300px;\n  overflow-y: auto;\n}\n\n.response-content pre {\n  margin: 0;\n  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;\n  font-size: 11px;\n  line-height: 1.4;\n  color: #333;\n  white-space: pre-wrap;\n  word-break: break-word;\n}\n</style>\n"],"sourceRoot":""}]);
// Exports
/* harmony default export */ __webpack_exports__["default"] = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=style&index=0&id=26200cad&scoped=true&lang=css":
/*!***************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=style&index=0&id=26200cad&scoped=true&lang=css ***!
  \***************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, "\n.icon-binding[data-v-26200cad] {\r\n  position: absolute;\r\n  right: -9px;\r\n  top: -9px;\r\n  color: red;\r\n  border: 3px solid red;\r\n  border-radius: 50%;\r\n  width: 40px;\r\n  height: 40px;\r\n  line-height: 40px;\r\n  font-weight: bold !important;\r\n  font-size: 16px;\r\n  transform: rotate(45deg);\r\n  background-color: rgb(245 108 108 / 20%);\r\n  user-select: none;\n}\r\n", "",{"version":3,"sources":["webpack://./src/components/EquipmentImage/EquipmentDesc.vue"],"names":[],"mappings":";AA4DA;EACA,kBAAA;EACA,WAAA;EACA,SAAA;EACA,UAAA;EACA,qBAAA;EACA,kBAAA;EACA,WAAA;EACA,YAAA;EACA,iBAAA;EACA,4BAAA;EACA,eAAA;EACA,wBAAA;EACA,wCAAA;EACA,iBAAA;AACA","sourcesContent":["<template>\r\n    <div class=\"equip-desc-content\">\r\n        <div v-if=\"lockType.length > 0\"\r\n            style=\"position: absolute; width: 100px; right: 12px; top: 12px; display: flex;justify-content: flex-end;\">\r\n            <img v-for=\"l in lockType\" :key=\"l\" :src=\"require(`../../../public/assets/images/time_lock_${l}.webp`)\"\r\n                style=\"height: 14px; width: 14px;display: block;\">\r\n        </div>\r\n        <el-row type=\"flex\" justify=\"space-between\">\r\n            <el-col v-if=\"image\" style=\"width: 120px; margin-right: 20px;position: relative;\">\r\n                <el-image style=\"width: 120px; height: 120px\" :src=\"getImageUrl(equipment.equip_face_img, 'big')\"\r\n                    fit=\"cover\" referrerpolicy=\"no-referrer\">\r\n                </el-image>\r\n                <div v-if=\"isBinding\" class=\"icon-binding\">\r\n                    专用\r\n                </div>\r\n            </el-col>\r\n            <el-col>\r\n                <p class=\"equip_desc_yellow\" v-if=\"equipment.equip_name\">{{ equipment.equip_name }}</p>\r\n                <p v-html=\"parseEquipDesc(equipment.equip_type_desc?.replace(/#R/g, '<br />'), '#n')\"></p>\r\n                <p v-html=\"parseEquipDesc(equipment.large_equip_desc)\"></p>\r\n            </el-col>\r\n        </el-row>\r\n    </div>\r\n</template>\r\n<script>\r\nimport { commonMixin } from '@/utils/mixins/commonMixin'\r\n\r\nexport default {\r\n    name: 'EquipmentDesc',\r\n    mixins: [commonMixin],\r\n    props: {\r\n        equipment: {\r\n            type: Object,\r\n            required: true\r\n        },\r\n        image: {\r\n            type: Boolean,\r\n            default: true\r\n        },\r\n        lockType: {\r\n            type: Array,\r\n            default: () => []\r\n        },\r\n        isBinding: {\r\n            type: Boolean,\r\n            default: false\r\n        }\r\n    },\r\n  methods: {\r\n    parseEquipDesc(desc, default_style = '#Y') {\r\n      if (!desc) return ''\r\n      if (typeof window.parse_style_info === 'function') {\r\n        return window.parse_style_info(desc, default_style)\r\n      }\r\n      return desc\r\n    },\r\n  }\r\n}\r\n</script>\r\n<style scoped>\r\n.icon-binding {\r\n  position: absolute;\r\n  right: -9px;\r\n  top: -9px;\r\n  color: red;\r\n  border: 3px solid red;\r\n  border-radius: 50%;\r\n  width: 40px;\r\n  height: 40px;\r\n  line-height: 40px;\r\n  font-weight: bold !important;\r\n  font-size: 16px;\r\n  transform: rotate(45deg);\r\n  background-color: rgb(245 108 108 / 20%);\r\n  user-select: none;\r\n}\r\n</style>"],"sourceRoot":""}]);
// Exports
/* harmony default export */ __webpack_exports__["default"] = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentImage.vue?vue&type=style&index=0&id=13caaaef&scoped=true&lang=css":
/*!****************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentImage.vue?vue&type=style&index=0&id=13caaaef&scoped=true&lang=css ***!
  \****************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, "\n/* 装备描述样式 */\n.equip-desc-content[data-v-13caaaef] {\n  overflow-y: auto;\n  font-size: 14px;\n  font-family: 宋体, tahoma, arial, hiragino sans gb, sans-serif;\n  line-height: 22px;\n  color: #ecf0f1;\n  padding: 10px;\n  border-radius: 4px;\n}\n.equip-desc-popper {\n  background-color: #2c3e50 !important;\n  padding: 18px !important;\n  border: 2px solid #2782a5 !important;\n}\n.icon-binding[data-v-13caaaef] {\n  position: absolute;\n  right: -9px;\n  top: -9px;\n  color: red;\n  border: 3px solid red;\n  border-radius: 50%;\n  width: 40px;\n  height: 40px;\n  line-height: 40px;\n  font-weight: bold !important;\n  font-size: 16px;\n  transform: rotate(45deg);\n  background-color: rgb(245 108 108 / 20%);\n  user-select: none;\n}\n", "",{"version":3,"sources":["webpack://./src/components/EquipmentImage/EquipmentImage.vue"],"names":[],"mappings":";AAwGA,WAAA;AACA;EACA,gBAAA;EACA,eAAA;EACA,4DAAA;EACA,iBAAA;EACA,cAAA;EACA,aAAA;EACA,kBAAA;AACA;AAEA;EACA,oCAAA;EACA,wBAAA;EACA,oCAAA;AACA;AAEA;EACA,kBAAA;EACA,WAAA;EACA,SAAA;EACA,UAAA;EACA,qBAAA;EACA,kBAAA;EACA,WAAA;EACA,YAAA;EACA,iBAAA;EACA,4BAAA;EACA,eAAA;EACA,wBAAA;EACA,wCAAA;EACA,iBAAA;AACA","sourcesContent":["<template>\n  <el-popover :close-delay=\"0\" v-if=\"equipment\" :data-equip-sn=\"equipment.equip_sn\" :placement=\"placement\"\n    :width=\"popoverWidth\" trigger=\"hover\" :visible-arrow=\"false\" raw-content v-model=\"visible\"\n    popper-class=\"equip-desc-popper\" style=\"position: relative;display: block;\">\n    <template #reference>\n      <div :style=\"imageStyle\" style=\"position: relative;overflow: hidden;\"> <el-image v-if=\"equipment\"\n          style=\"display: block\" :style=\"imageStyle\" :src=\"getImageUrl(equipment.equip_face_img, size)\" fit=\"cover\"\n          referrerpolicy=\"no-referrer\">\n        </el-image>\n        <div v-if=\"isBinding\" class=\"icon-binding\">\n          专用\n        </div>\n        <div v-if=\"rightLock.length > 0\" style=\"position: absolute; width: 14px; right: 0px; top: 0px;\">\n          <img v-for=\"l in rightLock\" :key=\"l\" :src=\"require(`../../../public/assets/images/time_lock_${l}.webp`)\"\n            style=\"height: 14px; width: 14px; display: block;\">\n        </div>\n        <div v-if=\"leftLock.length > 0\" style=\"position: absolute; width: 14px; left: 0px; top: 0px;\">\n          <img v-for=\"l in leftLock\" :key=\"l\" :src=\"require(`../../../public/assets/images/time_lock_${l}.webp`)\"\n            style=\"height: 14px; width: 14px;display: block;\">\n        </div>\n      </div>\n    </template>\n    <EquipmentDesc :equipment=\"equipment\" :lock-type=\"lockType\" :image=\"image\" v-if=\"visible\" :isBinding=\"isBinding\"/>\n  </el-popover>\n</template>\n\n<script>\nimport { commonMixin } from '@/utils/mixins/commonMixin'\nimport EquipmentDesc from './EquipmentDesc.vue'\nexport default {\n  name: 'EquipmentImage',\n  mixins: [commonMixin],\n  components: {\n    EquipmentDesc\n  },\n  props: {\n    image: {\n      type: Boolean,\n      default: true\n    },\n    equipment: {\n      type: [Object, undefined]\n    },\n    size: {\n      type: String,\n      default: 'small'\n    },\n    width: {\n      type: String,\n      default: '50px'\n    },\n    height: {\n      type: String,\n      default: '50px'\n    },\n    cursor: {\n      type: String,\n      default: 'pointer'\n    },\n    placement: {\n      type: String,\n      default: 'right'\n    },\n    popoverWidth: {\n      type: Number,\n      default: 405\n    },\n    lockType: {\n      type: Array,\n      default: () => []\n    }\n  },\n  data() {\n    return {\n      visible: false,\n      features: {}\n    }\n  },\n  computed: {\n    isBinding() {\n      // 玩家(\\d+)专用\n      const bindingPattern = /玩家(\\d+)专用/\n      const match = this.equipment.large_equip_desc.match(bindingPattern)\n      return Boolean(match)\n    },\n    rightLock() {\n      return this.lockType.filter(item => item !== 9 && item !== 'protect' && item !== 'huoyue')\n    },\n    leftLock() {\n      return this.lockType.filter(item => item === 9 || item === 'protect' || item === 'huoyue')\n    },\n    imageStyle() {\n      return {\n        display: 'block',\n        width: this.width,\n        height: this.height,\n        cursor: this.cursor\n      }\n    },\n  }\n}\n</script>\n\n<style scoped>\n/* 装备描述样式 */\n.equip-desc-content {\n  overflow-y: auto;\n  font-size: 14px;\n  font-family: 宋体, tahoma, arial, hiragino sans gb, sans-serif;\n  line-height: 22px;\n  color: #ecf0f1;\n  padding: 10px;\n  border-radius: 4px;\n}\n\n:global(.equip-desc-popper) {\n  background-color: #2c3e50 !important;\n  padding: 18px !important;\n  border: 2px solid #2782a5 !important;\n}\n\n.icon-binding {\n  position: absolute;\n  right: -9px;\n  top: -9px;\n  color: red;\n  border: 3px solid red;\n  border-radius: 50%;\n  width: 40px;\n  height: 40px;\n  line-height: 40px;\n  font-weight: bold !important;\n  font-size: 16px;\n  transform: rotate(45deg);\n  background-color: rgb(245 108 108 / 20%);\n  user-select: none;\n}\n</style>\n"],"sourceRoot":""}]);
// Exports
/* harmony default export */ __webpack_exports__["default"] = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/RoleImage.vue?vue&type=style&index=0&id=8c1934ec&scoped=true&lang=css":
/*!*****************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/RoleImage.vue?vue&type=style&index=0&id=8c1934ec&scoped=true&lang=css ***!
  \*****************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../../node_modules/css-loader/dist/runtime/getUrl.js */ "./node_modules/css-loader/dist/runtime/getUrl.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_2__);
// Imports



var ___CSS_LOADER_URL_IMPORT_0___ = new URL(/* asset import */ __webpack_require__(/*! ../../../public/assets/images/tag1.webp */ "./public/assets/images/tag1.webp"), __webpack_require__.b);
var ___CSS_LOADER_URL_IMPORT_1___ = new URL(/* asset import */ __webpack_require__(/*! ../../../public/assets/images/tag2.webp */ "./public/assets/images/tag2.webp"), __webpack_require__.b);
var ___CSS_LOADER_URL_IMPORT_2___ = new URL(/* asset import */ __webpack_require__(/*! ../../../public/assets/images/areabg.webp */ "./public/assets/images/areabg.webp"), __webpack_require__.b);
var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
var ___CSS_LOADER_URL_REPLACEMENT_0___ = _node_modules_css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_2___default()(___CSS_LOADER_URL_IMPORT_0___);
var ___CSS_LOADER_URL_REPLACEMENT_1___ = _node_modules_css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_2___default()(___CSS_LOADER_URL_IMPORT_1___);
var ___CSS_LOADER_URL_REPLACEMENT_2___ = _node_modules_css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_2___default()(___CSS_LOADER_URL_IMPORT_2___);
// Module
___CSS_LOADER_EXPORT___.push([module.id, "\n[data-v-8c1934ec] .role-info-tabs .el-tabs__nav .el-tabs__item {\r\n  padding: 0 !important;\r\n  width: 98px;\r\n  height: 26px;\r\n  line-height: 26px;\r\n  background: url(" + ___CSS_LOADER_URL_REPLACEMENT_0___ + ") no-repeat;\r\n  text-align: center;\r\n  float: left;\r\n  margin-right: 3px;\r\n  display: inline;\r\n  color: #748da4;\r\n  cursor: pointer;\n}\n[data-v-8c1934ec] .role-info-tabs .el-tabs__nav .el-tabs__item.is-active {\r\n  background: url(" + ___CSS_LOADER_URL_REPLACEMENT_1___ + ") no-repeat;\r\n  color: #fff;\n}\n.role-info-popover {\r\n  padding: 0 !important;\r\n  background: transparent;\r\n  box-shadow: none;\r\n  border: none;\r\n  font-size: 12px;\n}\n.role-info-popover .tabCont {\r\n  padding: 0 !important;\r\n  background: none;\n}\n.role-info-popover .tabCont {\r\n  padding: 0 !important;\n}\n.role-info-popover .el-tabs__header {\r\n  margin-bottom: 0 !important;\r\n  border-bottom: 2px solid #fff;\n}\n.role-info-popover .el-tabs__content {\r\n  padding: 12px;\r\n  background: url(" + ___CSS_LOADER_URL_REPLACEMENT_2___ + ") repeat-y -100px;\r\n  min-height: 510px;\n}\n.role-info-popover .el-tabs__active-bar {\r\n  display: none !important;\n}\n.shenqi-modal {\r\n  position: relative;\r\n  top: unset;\r\n  left: unset;\r\n  margin-left: unset;\n}\n.shenqi-info-popover {\r\n  padding: 0 !important;\r\n  background: #0a1f28;\r\n  border-color: #0a1f28;\n}\n.shenqi-info-popover .popper__arrow::after {\r\n  border-bottom-color: #0a1f28 !important;\n}\n.role-info-popover .popper__arrow::after {\r\n  border-right-color: #0a1f28 !important;\n}\r\n", "",{"version":3,"sources":["webpack://./src/components/RoleInfo/RoleImage.vue"],"names":[],"mappings":";AAmyDA;EACA,qBAAA;EACA,WAAA;EACA,YAAA;EACA,iBAAA;EACA,6DAAA;EACA,kBAAA;EACA,WAAA;EACA,iBAAA;EACA,eAAA;EACA,cAAA;EACA,eAAA;AACA;AAEA;EACA,6DAAA;EACA,WAAA;AACA;AAEA;EACA,qBAAA;EACA,uBAAA;EACA,gBAAA;EACA,YAAA;EACA,eAAA;AACA;AAEA;EACA,qBAAA;EACA,gBAAA;AACA;AAEA;EACA,qBAAA;AACA;AAEA;EACA,2BAAA;EACA,6BAAA;AACA;AAEA;EACA,aAAA;EACA,mEAAA;EACA,iBAAA;AACA;AAEA;EACA,wBAAA;AACA;AAEA;EACA,kBAAA;EACA,UAAA;EACA,WAAA;EACA,kBAAA;AACA;AAEA;EACA,qBAAA;EACA,mBAAA;EACA,qBAAA;AACA;AAEA;EACA,uCAAA;AACA;AAEA;EACA,sCAAA;AACA","sourcesContent":["<template>\r\n  <el-popover v-model=\"visible\" :width=\"715\" :data-equip-sn=\"$attrs.equip_sn\" placement=\"right\" trigger=\"click\"\r\n    popper-class=\"role-info-popover\">\r\n    <template #reference>\r\n      <slot></slot>\r\n      <el-image :src=\"imageUrl\" fit=\"cover\" :style=\"imageStyle\" referrerpolicy=\"no-referrer\" style=\"display: block;\">\r\n        <div slot=\"error\" class=\"image-slot\">\r\n          <i class=\"el-icon-picture-outline\"></i>\r\n        </div>\r\n      </el-image>\r\n    </template>\r\n    <div id=\"role_info_box\" v-if=\"visible\">\r\n      <el-tabs v-model=\"activeName\" class=\"role-info-tabs tabCont\">\r\n        <el-tab-pane label=\"人物/修炼\" name=\"role_basic\" v-if=\"basic_info\">\r\n          <div class=\"cols\" style=\"width: 320px\">\r\n            <div class=\"subTab\">\r\n              <h4 class=\"subTabLeft role_basic_attr_tab\" :class=\"{ off: currentDisplayIndex !== 0 }\"\r\n                @click=\"toggle_display(0)\">\r\n                人物状态\r\n              </h4>\r\n              <h4 class=\"subTabRight role_basic_attr_tab\" :class=\"{ off: currentDisplayIndex !== 1 }\"\r\n                @click=\"toggle_display(1)\">\r\n                输出/抗性\r\n              </h4>\r\n            </div>\r\n            <table class=\"tb02 role_basic_attr_table\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\"\r\n              v-show=\"currentDisplayIndex === 0\">\r\n              <colgroup>\r\n                <col width=\"180\" />\r\n                <col width=\"140\" />\r\n              </colgroup>\r\n              <tr>\r\n                <td><strong>级别：</strong>{{ basic_info.role_level }}</td>\r\n                <td><strong>名称：</strong>{{ htmlEncode(basic_info.nickname) }}</td>\r\n              </tr>\r\n              <tr>\r\n                <td><strong>角色：</strong>{{ basic_info.role_kind_name }}</td>\r\n                <td><strong>人气：</strong>{{ basic_info.pride }}</td>\r\n              </tr>\r\n              <tr>\r\n                <td><strong>帮派：</strong>{{ basic_info.org }}</td>\r\n                <td><strong>帮贡：</strong>{{ basic_info.org_offer }}</td>\r\n              </tr>\r\n              <tr>\r\n                <td>\r\n                  <strong>门派：</strong><span id=\"kindName\">{{ basic_info.school }}</span>\r\n                </td>\r\n                <td><strong>门贡：</strong>{{ basic_info.school_offer }}</td>\r\n              </tr>\r\n              <tr>\r\n                <td><strong>气血：</strong>{{ basic_info.hp_max }}</td>\r\n                <td><strong>体质：</strong>{{ basic_info.cor_all }}</td>\r\n              </tr>\r\n              <tr>\r\n                <td><strong>魔法：</strong>{{ basic_info.mp_max }}</td>\r\n                <td><strong>魔力：</strong>{{ basic_info.mag_all }}</td>\r\n              </tr>\r\n              <tr>\r\n                <td><strong>命中：</strong>{{ basic_info.att_all }}</td>\r\n                <td><strong>力量：</strong>{{ basic_info.str_all }}</td>\r\n              </tr>\r\n              <tr>\r\n                <td><strong>伤害：</strong>{{ basic_info.damage_all }}</td>\r\n                <td><strong>耐力：</strong>{{ basic_info.res_all }}</td>\r\n              </tr>\r\n              <tr>\r\n                <td><strong>防御：</strong>{{ basic_info.def_all }}</td>\r\n                <td><strong>敏捷：</strong>{{ basic_info.spe_all }}</td>\r\n              </tr>\r\n              <tr>\r\n                <td><strong>速度：</strong>{{ basic_info.dex_all }}</td>\r\n                <td><strong>潜力：</strong>{{ basic_info.point }}</td>\r\n              </tr>\r\n              <tr>\r\n                <td v-if=\"basic_info.fa_shang !== undefined\">\r\n                  <strong>法伤：</strong>{{ basic_info.fa_shang }}\r\n                </td>\r\n                <td v-else><strong>躲避：</strong>{{ basic_info.dod_all }}</td>\r\n                <td><strong>靓号特效：</strong>{{ basic_info.is_niceid }}</td>\r\n              </tr>\r\n              <tr>\r\n                <td v-if=\"basic_info.fa_fang !== undefined\">\r\n                  <strong>法防：</strong>{{ basic_info.fa_fang }}\r\n                </td>\r\n                <td v-else><strong>灵力：</strong>{{ basic_info.mag_def_all }}</td>\r\n                <td><strong>成就点数：</strong>{{ basic_info.chengjiu }}</td>\r\n              </tr>\r\n              <tr>\r\n                <td><strong>获得经验：</strong>{{ basic_info.upexp }}</td>\r\n                <td><strong>已用潜能果数量：</strong>{{ basic_info.qian_neng_guo }}</td>\r\n              </tr>\r\n              <tr>\r\n                <td>\r\n                  <span v-if=\"\r\n                    basic_info.qian_yuan_dan && basic_info.qian_yuan_dan.new_value === undefined\r\n                  \">\r\n                    <strong>已兑换乾元丹数量：</strong>{{ basic_info.qian_yuan_dan.old_value }}\r\n                  </span>\r\n                  <span v-else>\r\n                    <strong>新版乾元丹数量：</strong>{{ basic_info.qian_yuan_dan.new_value }}\r\n                  </span>\r\n                </td>\r\n                <td>\r\n                  <strong>总经验：</strong>{{ basic_info.sum_exp }}\r\n                  <i v-if=\"basic_info.ach_info\" class=\"question hoverTips\">\r\n                    <span class=\"hoverTipsDetail\">{{ basic_info.ach_info }}</span>\r\n                  </i>\r\n                </td>\r\n              </tr>\r\n              <tr>\r\n                <td>\r\n                  <strong>月饼粽子机缘：</strong>{{ (basic_info.add_point || 0) + (basic_info.ji_yuan || 0) }}/{{\r\n                    extraAttrPoints\r\n                  }}\r\n                  <i v-if=\"extraAttrPoints > 0\" class=\"question hoverTips\">\r\n                    <span class=\"hoverTipsDetail\">\r\n                      月饼粽子食用量：{{ basic_info.add_point }}<br /><br />已获得机缘属性：{{\r\n                        basic_info.ji_yuan\r\n                      }}\r\n                    </span>\r\n                  </i>\r\n                </td>\r\n                <td><strong>原始种族：</strong><span v-html=\"basic_info.ori_race\"></span></td>\r\n              </tr>\r\n              <tr>\r\n                <td><strong>历史门派：</strong>{{ basic_info.changesch }}</td>\r\n                <td><strong>属性保存方案：</strong>{{ basic_info.propkept }}</td>\r\n              </tr>\r\n              <tr>\r\n                <td><strong>飞升/渡劫/化圣：</strong>{{ basic_info.fly_status }}</td>\r\n                <td v-if=\"basic_info.role_level >= 120\">\r\n                  <strong>生死劫：</strong>{{ basic_info.shengsijie }}\r\n                </td>\r\n                <td v-else></td>\r\n              </tr>\r\n            </table>\r\n            <table class=\"tb02 role_basic_attr_table\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\"\r\n              v-show=\"currentDisplayIndex === 1\">\r\n              <template v-if=\"!basic_info.other_attr\">\r\n                <colgroup>\r\n                  <col width=\"320\" />\r\n                </colgroup>\r\n                <tr>\r\n                  <td><br />重新寄售后才能显示</td>\r\n                </tr>\r\n              </template>\r\n              <template v-else>\r\n                <colgroup>\r\n                  <col width=\"160\" />\r\n                  <col width=\"160\" />\r\n                </colgroup>\r\n                <tr>\r\n                  <td colspan=\"2\"><strong style=\"font-size: 16px; color: white\">输出</strong></td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>灵力：</strong></td>\r\n                  <td>{{ basic_info.other_attr['14'] }}</td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>物理暴击等级：</strong></td>\r\n                  <td>\r\n                    {{ basic_info.other_attr['6'] }}({{\r\n                      (\r\n                        (basic_info.other_attr['6'] * 10) / Math.max(30, basic_info.role_level) || 0\r\n                      ).toFixed(2)\r\n                    }}%)\r\n                  </td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>穿刺等级：</strong></td>\r\n                  <td>\r\n                    {{ basic_info.other_attr['8'] }}({{\r\n                      (\r\n                        (basic_info.other_attr['8'] * 3) / Math.max(30, basic_info.role_level) || 0\r\n                      ).toFixed(2)\r\n                    }}%)\r\n                  </td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>狂暴等级：</strong></td>\r\n                  <td>\r\n                    {{ basic_info.other_attr['5'] }}({{\r\n                      (\r\n                        (basic_info.other_attr['5'] * 3) / Math.max(30, basic_info.role_level) || 0\r\n                      ).toFixed(2)\r\n                    }}%)\r\n                  </td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>法术暴击等级：</strong></td>\r\n                  <td>\r\n                    {{ basic_info.other_attr['7'] }}({{\r\n                      (\r\n                        (basic_info.other_attr['7'] * 10) / Math.max(30, basic_info.role_level) || 0\r\n                      ).toFixed(2)\r\n                    }}%)\r\n                  </td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>法术伤害结果：</strong></td>\r\n                  <td>{{ basic_info.other_attr['12'] }}</td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>封印命中等级：</strong></td>\r\n                  <td>\r\n                    {{ basic_info.other_attr['1'] }}({{\r\n                      (\r\n                        (basic_info.other_attr['1'] * 10) /\r\n                        Math.max(30, basic_info.role_level + 25) || 0\r\n                      ).toFixed(2)\r\n                    }}%)\r\n                  </td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>治疗能力：</strong></td>\r\n                  <td>{{ basic_info.other_attr['3'] }}</td>\r\n                </tr>\r\n                <tr>\r\n                  <td colspan=\"2\"><strong style=\"font-size: 16px; color: white\">抗性</strong></td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>抗物理暴击等级：</strong></td>\r\n                  <td>\r\n                    {{ basic_info.other_attr['9'] }}({{\r\n                      (\r\n                        (basic_info.other_attr['9'] * 10) / Math.max(30, basic_info.role_level) || 0\r\n                      ).toFixed(2)\r\n                    }}%)\r\n                  </td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>格挡值：</strong></td>\r\n                  <td>{{ basic_info.other_attr['11'] }}</td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>抗法术暴击等级：</strong></td>\r\n                  <td>\r\n                    {{ basic_info.other_attr['10'] }}({{\r\n                      (\r\n                        (basic_info.other_attr['10'] * 10) / Math.max(30, basic_info.role_level) ||\r\n                        0\r\n                      ).toFixed(2)\r\n                    }}%)\r\n                  </td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>抵抗封印等级：</strong></td>\r\n                  <td>\r\n                    {{ basic_info.other_attr['2'] }}({{\r\n                      (\r\n                        (basic_info.other_attr['2'] * 10) /\r\n                        Math.max(30, basic_info.role_level + 25) || 0\r\n                      ).toFixed(2)\r\n                    }}%)\r\n                  </td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>气血回复效果：</strong></td>\r\n                  <td>{{ basic_info.other_attr['4'] }}</td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>躲避：</strong></td>\r\n                  <td>{{ basic_info.other_attr['13'] }}</td>\r\n                </tr>\r\n              </template>\r\n            </table>\r\n          </div>\r\n\r\n          <div class=\"cols\" style=\"width: 320px\">\r\n            <h4>角色修炼及宠修</h4>\r\n            <table class=\"tb02\" width=\"49%\" cellspacing=\"0\" cellpadding=\"0\" style=\"float: left\">\r\n              <tr v-for=\"(item, index) in role_xiulian\" :key=\"index\">\r\n                <th width=\"100\">{{ item.name }}：</th>\r\n                <td style=\"white-space: nowrap\">{{ item.info }}</td>\r\n              </tr>\r\n            </table>\r\n\r\n            <table class=\"tb02\" width=\"49%\" cellspacing=\"0\" cellpadding=\"0\" style=\"float: right\">\r\n              <tr v-if=\"yu_shou_shu !== undefined\">\r\n                <th width=\"100\">育兽术：</th>\r\n                <td>{{ yu_shou_shu }}</td>\r\n              </tr>\r\n              <tr v-for=\"(item, index) in pet_ctrl_skill\" :key=\"index\">\r\n                <th width=\"100\">{{ item.name }}：</th>\r\n                <td>{{ item.grade }}</td>\r\n              </tr>\r\n            </table>\r\n\r\n            <div class=\"blank9\" style=\"clear: both\"></div>\r\n            <div class=\"blank9\"></div>\r\n            <h4>积分 其他</h4>\r\n            <table width=\"92%\" class=\"tb02\" cellspacing=\"0\" cellpadding=\"0\">\r\n              <tr>\r\n                <th width=\"80\">比武积分：</th>\r\n                <td>{{ basic_info.hero_score }}</td>\r\n                <th width=\"80\">剑会积分：</th>\r\n                <td>{{ basic_info.sword_score }}</td>\r\n              </tr>\r\n              <tr>\r\n                <th width=\"80\">三界功绩：</th>\r\n                <td>{{ basic_info.sanjie_score }}</td>\r\n                <th width=\"80\">副本积分：</th>\r\n                <td>{{ basic_info.dup_score }}</td>\r\n              </tr>\r\n              <tr>\r\n                <th width=\"80\">神器积分：</th>\r\n                <td>{{ basic_info.shenqi_score }}</td>\r\n                <th></th>\r\n                <td></td>\r\n              </tr>\r\n            </table>\r\n          </div>\r\n        </el-tab-pane>\r\n        <el-tab-pane label=\"技能\" name=\"role_skill\" v-if=\"school_skill\">\r\n          <div class=\"cols\" style=\"width: 200px\">\r\n            <h4>师门技能</h4>\r\n            <div class=\"skill\">\r\n              <p v-if=\"school_skill.length > 7\" class=\"textCenter cDYellow\">师门技能信息有误</p>\r\n              <p v-else-if=\"school_skill.length == 0\" class=\"textCenter cDYellow\">师门技能都是0</p>\r\n              <ul v-else id=\"school_skill_lists\">\r\n                <li style=\"left: 60px; top: 0\">\r\n                  <img referrerpolicy=\"no-referrer\" :src=\"school_skill2_icon\" :data_equip_name=\"school_skill2_name\"\r\n                    data_skill_type=\"school_skill\" :data_equip_desc=\"school_skill2_desc\"\r\n                    data_tip_box=\"RoleSkillTipsBox\" />\r\n                  <p>{{ school_skill2_grade }}</p>\r\n                  <h5>{{ school_skill2_name }}</h5>\r\n                </li>\r\n                <li style=\"left: 0; top: 50px\">\r\n                  <img referrerpolicy=\"no-referrer\" :src=\"school_skill3_icon\" :data_equip_name=\"school_skill3_name\"\r\n                    data_skill_type=\"school_skill\" :data_equip_desc=\"school_skill3_desc\"\r\n                    data_tip_box=\"RoleSkillTipsBox\" />\r\n                  <p>{{ school_skill3_grade }}</p>\r\n                  <h5>{{ school_skill3_name }}</h5>\r\n                </li>\r\n                <li style=\"left: 120px; top: 50px\">\r\n                  <img referrerpolicy=\"no-referrer\" :src=\"school_skill4_icon\" :data_equip_name=\"school_skill4_name\"\r\n                    data_skill_type=\"school_skill\" :data_equip_desc=\"school_skill4_desc\"\r\n                    data_tip_box=\"RoleSkillTipsBox\" />\r\n                  <p>{{ school_skill4_grade }}</p>\r\n                  <h5>{{ school_skill4_name }}</h5>\r\n                </li>\r\n                <li style=\"left: 0; top: 140px\">\r\n                  <img referrerpolicy=\"no-referrer\" :src=\"school_skill5_icon\" :data_equip_name=\"school_skill5_name\"\r\n                    data_skill_type=\"school_skill\" :data_equip_desc=\"school_skill5_desc\"\r\n                    data_tip_box=\"RoleSkillTipsBox\" />\r\n                  <p>{{ school_skill5_grade }}</p>\r\n                  <h5>{{ school_skill5_name }}</h5>\r\n                </li>\r\n                <li style=\"left: 120px; top: 140px\">\r\n                  <img referrerpolicy=\"no-referrer\" :src=\"school_skill6_icon\" :data_equip_name=\"school_skill6_name\"\r\n                    data_skill_type=\"school_skill\" :data_equip_desc=\"school_skill6_desc\"\r\n                    data_tip_box=\"RoleSkillTipsBox\" />\r\n                  <p>{{ school_skill6_grade }}</p>\r\n                  <h5>{{ school_skill6_name }}</h5>\r\n                </li>\r\n                <li style=\"left: 60px; top: 94px\">\r\n                  <img referrerpolicy=\"no-referrer\" :src=\"school_skill1_icon\" :data_equip_name=\"school_skill1_name\"\r\n                    data_skill_type=\"school_skill\" :data_equip_desc=\"school_skill1_desc\"\r\n                    data_tip_box=\"RoleSkillTipsBox\" />\r\n                  <p>{{ school_skill1_grade }}</p>\r\n                  <h5>{{ school_skill1_name }}</h5>\r\n                </li>\r\n                <li style=\"left: 60px; top: 200px\">\r\n                  <img referrerpolicy=\"no-referrer\" :src=\"school_skill7_icon\" :data_equip_name=\"school_skill7_name\"\r\n                    data_skill_type=\"school_skill\" :data_equip_desc=\"school_skill7_desc\"\r\n                    data_tip_box=\"RoleSkillTipsBox\" />\r\n                  <p>{{ school_skill7_grade }}</p>\r\n                  <h5>{{ school_skill7_name }}</h5>\r\n                </li>\r\n              </ul>\r\n            </div>\r\n          </div>\r\n\r\n          <div class=\"cols\" style=\"width: 442px; margin-left: 18px\">\r\n            <h4>生活技能</h4>\r\n            <div class=\"blank12\"></div>\r\n            <div v-if=\"life_skill && life_skill.length > 0\">\r\n              <table cellspacing=\"0\" cellpadding=\"0\" class=\"skillTb\" id=\"life_skill_lists\">\r\n                <tr v-for=\"(row, rowIndex) in skillRows(life_skill, 7)\" :key=\"rowIndex\">\r\n                  <td v-for=\"(item, itemIndex) in row\" :key=\"itemIndex\">\r\n                    <img referrerpolicy=\"no-referrer\" :src=\"item.skill_icon\" width=\"40\" height=\"40\"\r\n                      :data_equip_name=\"item.name\" data_skill_type=\"life_skill\" :data_equip_desc=\"item.desc\"\r\n                      data_tip_box=\"RoleSkillTipsBox\" />\r\n                    <p>{{ item.skill_grade }}</p>\r\n                    <h5>{{ item.skill_name }}</h5>\r\n                  </td>\r\n                </tr>\r\n              </table>\r\n            </div>\r\n            <div v-else class=\"textCenter\" style=\"padding-bottom: 30px\">无</div>\r\n\r\n            <div class=\"blank9\"></div>\r\n            <h4>剧情技能</h4>\r\n            <div class=\"blank12\"></div>\r\n            <div v-if=\"ju_qing_skill && ju_qing_skill.length > 0\">\r\n              <table cellspacing=\"0\" cellpadding=\"0\" class=\"skillTb\" id=\"juqing_skill_lists\">\r\n                <tr v-for=\"(row, rowIndex) in skillRows(ju_qing_skill, 7)\" :key=\"rowIndex\">\r\n                  <td v-for=\"(item, itemIndex) in row\" :key=\"itemIndex\">\r\n                    <img referrerpolicy=\"no-referrer\" :src=\"item.skill_icon\" width=\"40\" height=\"40\"\r\n                      :data_equip_name=\"item.name\" data_skill_type=\"ju_qing_skill\" :data_equip_desc=\"item.desc\"\r\n                      data_tip_box=\"RoleSkillTipsBox\" />\r\n                    <p>{{ item.skill_grade }}</p>\r\n                    <h5>{{ item.skill_name }}</h5>\r\n                  </td>\r\n                </tr>\r\n              </table>\r\n            </div>\r\n            <div v-else class=\"textCenter\" style=\"padding-bottom: 30px\">无</div>\r\n\r\n            <p class=\"textRight cDYellow\">剩余技能点：{{ left_skill_point }}</p>\r\n            <div class=\"blank9\"></div>\r\n            <h4>熟练度</h4>\r\n            <table width=\"92%\" class=\"tb02\" cellspacing=\"0\" cellpadding=\"0\">\r\n              <tr>\r\n                <th width=\"100\">打造熟练度：</th>\r\n                <td>{{ shuliandu.smith_skill }}</td>\r\n                <th width=\"100\">裁缝熟练度：</th>\r\n                <td>{{ shuliandu.sew_skill }}</td>\r\n              </tr>\r\n            </table>\r\n          </div>\r\n        </el-tab-pane>\r\n        <el-tab-pane label=\"道具/法宝\" name=\"role_equips\">\r\n          <div class=\"cols\" style=\"width: 350px\">\r\n            <h4>道具</h4>\r\n\r\n            <table width=\"80%\" style=\"margin: 0 auto\" cellspacing=\"3\" cellpadding=\"3\" id=\"RoleUsingEquips\">\r\n              <tr>\r\n                <td colspan=\"3\">\r\n                  <table cellspacing=\"0\" cellpadding=\"0\" class=\"tb03 size50\">\r\n                    <tr>\r\n                      <td>\r\n                        <ItemPopover id=\"role_using_equip_187\" :equipment=\"get_using_equip(187)\" />\r\n                      </td>\r\n                      <td>\r\n                        <ItemPopover id=\"role_using_equip_187\" :equipment=\"get_using_equip(188)\" />\r\n                      </td>\r\n                      <td>\r\n                        <ItemPopover id=\"role_using_equip_187\" :equipment=\"get_using_equip(190)\" />\r\n                      </td>\r\n                      <td>\r\n                        <ItemPopover id=\"role_using_equip_187\" :equipment=\"get_using_equip(189)\" />\r\n                      </td>\r\n                    </tr>\r\n                  </table>\r\n                </td>\r\n              </tr>\r\n              <tr>\r\n                <td>\r\n                  <table cellspacing=\"0\" cellpadding=\"0\" class=\"tb03 size50\">\r\n                    <tr>\r\n                      <td>\r\n                        <ItemPopover id=\"role_using_equip_1\" :equipment=\"get_using_equip(1)\" />\r\n                      </td>\r\n                    </tr>\r\n                    <tr>\r\n                      <td>\r\n                        <ItemPopover id=\"role_using_equip_6\" :equipment=\"get_using_equip(6)\" />\r\n                      </td>\r\n                    </tr>\r\n                    <tr>\r\n                      <td>\r\n                        <ItemPopover id=\"role_using_equip_5\" :equipment=\"get_using_equip(5)\" />\r\n                      </td>\r\n                    </tr>\r\n                  </table>\r\n                </td>\r\n                <td>\r\n                  <table class=\"tb02\" cellspacing=\"0\" cellpadding=\"0\">\r\n                    <tr>\r\n                      <th>现金：</th>\r\n                      <td>{{ basic_info.cash }}</td>\r\n                    </tr>\r\n                    <tr>\r\n                      <th>存银：</th>\r\n                      <td>{{ basic_info.saving }}</td>\r\n                    </tr>\r\n                    <tr>\r\n                      <th>储备：</th>\r\n                      <td>{{ basic_info.learn_cash }}</td>\r\n                    </tr>\r\n                    <tr>\r\n                      <th>善恶：</th>\r\n                      <td>{{ basic_info.badness }}</td>\r\n                    </tr>\r\n                    <tr>\r\n                      <th>仙玉：</th>\r\n                      <td>{{ basic_info.xianyu }}</td>\r\n                    </tr>\r\n                    <tr>\r\n                      <th>精力：</th>\r\n                      <td>{{ basic_info.energy }}</td>\r\n                    </tr>\r\n                  </table>\r\n                </td>\r\n                <td>\r\n                  <table cellspacing=\"0\" cellpadding=\"0\" class=\"tb03 size50\">\r\n                    <tr>\r\n                      <td>\r\n                        <ItemPopover :equipment=\"get_using_equip(4)\" id=\"role_using_equip_4\" />\r\n                      </td>\r\n                    </tr>\r\n                    <tr>\r\n                      <td>\r\n                        <ItemPopover :equipment=\"get_using_equip(2)\" id=\"role_using_equip_2\" />\r\n                      </td>\r\n                    </tr>\r\n                    <tr>\r\n                      <td>\r\n                        <ItemPopover :equipment=\"get_using_equip(3)\" id=\"role_using_equip3\" />\r\n                      </td>\r\n                    </tr>\r\n                  </table>\r\n                </td>\r\n              </tr>\r\n            </table>\r\n\r\n            <div class=\"blank9\"></div>\r\n            <table cellspacing=\"0\" cellpadding=\"0\" class=\"tb03 size50\" id=\"RoleStoreEquips\">\r\n              <tr v-for=\"(row, rowIndex) in storeEquipsRows\" :key=\"rowIndex\">\r\n                <td v-for=\"(equip, colIndex) in row\" :key=\"colIndex\">\r\n                  <ItemPopover :id=\"'store_equip_tips' + (rowIndex * 5 + colIndex + 1)\" :equipment=\"equip\r\n                    ? {\r\n                      equip_sn: equip.equip_sn,\r\n                      equip_face_img: equip.small_icon,\r\n                      equip_name: equip.name,\r\n                      equip_type_desc: equip.static_desc,\r\n                      large_equip_desc: equip.desc,\r\n                      lock_type: equip.lock_type\r\n                    }\r\n                    : null\r\n                    \" />\r\n                </td>\r\n                <td v-for=\"i in 5 - row.length\" :key=\"'empty-' + i\">\r\n                  <ItemPopover :equipment=\"null\" />\r\n                </td>\r\n              </tr>\r\n            </table>\r\n\r\n            <div v-if=\"split_equips && split_equips.length\" class=\"blank9\"></div>\r\n            <h4 v-if=\"split_equips && split_equips.length\">拆卖道具</h4>\r\n            <table v-if=\"split_equips && split_equips.length\" cellspacing=\"0\" cellpadding=\"3\" class=\"tb03 size50\"\r\n              id=\"RoleSplitEquips\">\r\n              <tr v-for=\"(row, rowIndex) in splitEquipsRows\" :key=\"rowIndex\">\r\n                <td v-for=\"(equip, colIndex) in row\" :key=\"colIndex\">\r\n                  <a style=\"display: block; width: 100%; height: 100%\" :href=\"getCBGLinkByType(equip.eid, 'equip')\"\r\n                    target=\"_blank\" tid=\"gl03odgw\" :data_trace_text=\"equip.eid\">\r\n                    <ItemPopover :equipment=\"get_using_equip(equip)\" />\r\n                  </a>\r\n                </td>\r\n                <td v-for=\"i in 5 - row.length\" :key=\"'empty-' + i\"></td>\r\n              </tr>\r\n            </table>\r\n          </div>\r\n\r\n          <div class=\"cols\" style=\"width: 300px; margin-left: 25px\">\r\n            <div class=\"cols\" style=\"width: 145px; margin-left: 0\">\r\n              <h4>神器</h4>\r\n              <div class=\"blank9\"></div>\r\n              <table style=\"table-layout: fixed\" cellspacing=\"0\" cellpadding=\"0\" class=\"tb03 size50\"\r\n                id=\"RoleStoreShenqi\">\r\n                <tr>\r\n                  <el-popover trigger=\"click\" placement=\"bottom\" popper-class=\"shenqi-info-popover\">\r\n                    <template #reference>\r\n                      <td v-if=\"shenqi\" id=\"shenqi\" class=\"shenqi_td\" style=\"background: #c0b9dd\"\r\n                        :data_equip_name=\"shenqi.name\" :data_equip_type=\"shenqi.type\" :data_equip_desc=\"shenqi.desc\"\r\n                        :data_equip_type_desc=\"shenqi.static_desc\">\r\n                        <ItemPopover :equipment=\"{\r\n                          equip_face_img: shenqi.icon,\r\n                          equip_name: shenqi.name,\r\n                          equip_type_desc: shenqi.static_desc,\r\n                          large_equip_desc: shenqi.desc\r\n                        }\" />\r\n                      </td>\r\n                    </template>\r\n                    <div class=\"shenqi-modal\" id=\"shenqiModal\">\r\n                      <h4 class=\"modal-head\">\r\n                        神器属性 <span class=\"modal-close-btn\" id=\"shenqiCloseBtn\"></span>\r\n                      </h4>\r\n                      <div class=\"shenqi-modal-content\">\r\n                        <ul v-if=\"shenqi?.isNew\" class=\"shenqi-tab\">\r\n                          <li v-for=\"i in 3\" :key=\"i\" :class=\"[\r\n                            'tab-item',\r\n                            'js_shenqi_tab',\r\n                            !shenqi_components['shenqi' + i]\r\n                              ? 'disable'\r\n                              : shenqi_components['shenqi' + i] &&\r\n                                shenqi_components['shenqi' + i].actived\r\n                                ? 'active'\r\n                                : ''\r\n                          ]\" :data-index=\"i - 1\" @click=\"switchShenqiTab(i - 1)\">\r\n                            第{{ ['一', '二', '三'][i - 1] }}套属性\r\n                          </li>\r\n                        </ul>\r\n\r\n                        <div class=\"shenqi-list\">\r\n                          <div v-for=\"(modalData, key) in shenqi_components\" :key=\"key\" class=\"js_shenqi_panel\"\r\n                            :style=\"{ display: !modalData.actived ? 'none' : '' }\">\r\n                            <div v-for=\"(component, compIndex) in modalData.components\" :key=\"compIndex\"\r\n                              class=\"shenqi-itme\">\r\n                              <div class=\"shenqi-item-left\">\r\n                                <img referrerpolicy=\"no-referrer\" :src=\"component.buweiPic\" />\r\n                              </div>\r\n                              <div class=\"col-r\">\r\n                                <ul class=\"shenqi-item-center\">\r\n                                  <li v-for=\"(wuxing, wuxingIndex) in component.wuxing\" :key=\"wuxingIndex\">\r\n                                    <div v-if=\"wuxing.status !== 1\" class=\"img-wrap\">\r\n                                      <img referrerpolicy=\"no-referrer\" :src=\"wuxing.lingxiPic\" />\r\n                                    </div>\r\n                                    <div v-else>\r\n                                      <div class=\"img-wrap\">\r\n                                        <img referrerpolicy=\"no-referrer\" :src=\"wuxing.lingxiPic\" />\r\n                                        <span v-if=\"wuxing.wuxing_affix_text\" class=\"cizhui\">{{\r\n                                          wuxing.wuxing_affix_text\r\n                                          }}</span>\r\n                                      </div>\r\n                                      <p>{{ wuxing.wuxingText }}</p>\r\n                                    </div>\r\n                                  </li>\r\n                                </ul>\r\n                                <ul class=\"shenqi-item-right\">\r\n                                  <li v-for=\"(wuxing, wuxingIndex) in component.wuxing\" :key=\"wuxingIndex\">\r\n                                    {{ wuxing.attr }}\r\n                                  </li>\r\n                                </ul>\r\n                              </div>\r\n                            </div>\r\n                          </div>\r\n                        </div>\r\n                      </div>\r\n                    </div>\r\n                  </el-popover>\r\n\r\n                  <td v-if=\"huoshenta\" class=\"shenqi_td\" style=\"background: #c0b9dd\" :data_equip_name=\"huoshenta.name\"\r\n                    :data_equip_type=\"shenqi?.type\" :data_equip_desc=\"huoshenta.desc\" data_equip_type_desc=\"\">\r\n                    <ItemPopover :equipment=\"{\r\n                      equip_face_img: huoshenta.icon,\r\n                      equip_name: huoshenta.name,\r\n                      large_equip_desc: huoshenta.desc\r\n                    }\" />\r\n                  </td>\r\n                  <td v-if=\"!shenqi && !huoshenta\" style=\"background: rgb(192, 185, 221)\"></td>\r\n                </tr>\r\n              </table>\r\n            </div>\r\n            <div class=\"cols\" style=\"width: 145px; margin-right: 0\">\r\n              <h4>已装备灵宝</h4>\r\n              <div class=\"blank9\"></div>\r\n              <table style=\"table-layout: fixed\" cellspacing=\"0\" cellpadding=\"0\" class=\"tb03 size50\">\r\n                <tr id=\"RoleUsingLingbao\">\r\n                  <template v-for=\"(item, i) in using_lingbao.concat([null, null]).slice(0, 2)\">\r\n                    <td v-if=\"item\" :key=\"'lingbao-' + i\" style=\"background: #c0b9dd\" :data_equip_name=\"item.name\"\r\n                      :data_equip_type=\"item.type\" :data_equip_desc=\"item.desc\"\r\n                      :data_equip_type_desc=\"item.static_desc\">\r\n                      <ItemPopover :equipment=\"{\r\n                        equip_face_img: item.icon,\r\n                        equip_name: item.name,\r\n                        equip_type_desc: item.static_desc,\r\n                        large_equip_desc: item.desc\r\n                      }\" />\r\n                    </td>\r\n                    <td v-else :key=\"'empty-' + i\" style=\"background: #c0b9dd\"></td>\r\n                  </template>\r\n                </tr>\r\n              </table>\r\n            </div>\r\n          </div>\r\n\r\n          <div class=\"cols\" style=\"width: 300px; margin-left: 24px\">\r\n            <div class=\"blank12\"></div>\r\n            <h4>未装备灵宝</h4>\r\n            <div class=\"blank9\"></div>\r\n            <div style=\"\r\n                max-height: 125px;\r\n                width: 274px;\r\n                overflow: auto;\r\n                overflow-x: hidden;\r\n                margin: 0 auto;\r\n              \">\r\n              <table cellspacing=\"0\" cellpadding=\"0\" class=\"tb03 size50\" id=\"RoleNoUsingLingbao\">\r\n                <tr v-for=\"(row, rowIndex) in nousingLingbaoRows\" :key=\"rowIndex\">\r\n                  <template v-for=\"(item, colIndex) in row\">\r\n                    <td v-if=\"item\" :key=\"'lingbao-' + colIndex\" style=\"background: #c0b9dd\"\r\n                      :data_equip_name=\"item.name\" :data_equip_type=\"item.type\" :data_equip_desc=\"item.desc\"\r\n                      :data_equip_type_desc=\"item.static_desc\">\r\n                      <ItemPopover :equipment=\"{\r\n                        equip_face_img: item.icon,\r\n                        equip_name: item.name,\r\n                        equip_type_desc: item.static_desc,\r\n                        large_equip_desc: item.desc\r\n                      }\" />\r\n                    </td>\r\n                    <td v-else :key=\"'empty-' + colIndex\" style=\"background: #c0b9dd\"></td>\r\n                  </template>\r\n                </tr>\r\n              </table>\r\n            </div>\r\n\r\n            <div class=\"blank12\"></div>\r\n            <h4>已装备法宝</h4>\r\n            <div class=\"blank9\"></div>\r\n            <table cellspacing=\"0\" cellpadding=\"0\" class=\"tb03 size50\" id=\"RoleUsingFabao\">\r\n              <tr>\r\n                <td v-for=\"i in 4\" :key=\"'fabao-' + i\" style=\"background: #c0b9dd\">\r\n                  <ItemPopover :equipment=\"get_using_fabao(i)\" align=\"middle\" />\r\n                </td>\r\n              </tr>\r\n            </table>\r\n            <div class=\"blank12\"></div>\r\n            <h4>\r\n              未装备的所有法宝\r\n              <span v-if=\"unused_fabao_sum !== undefined\">({{ unused_fabao_sum }}/{{ fabao_storage_size }})</span>\r\n            </h4>\r\n            <div class=\"blank9\"></div>\r\n            <div id=\"fabao_table_wrapper\" style=\"\r\n                height: 205px;\r\n                width: 274px;\r\n                overflow: auto;\r\n                overflow-x: hidden;\r\n                margin: 0 auto;\r\n              \">\r\n              <table width=\"256\" style=\"table-layout: fixed\" cellspacing=\"0\" cellpadding=\"0\" class=\"tb03 size50\"\r\n                id=\"RoleStoreFabao\">\r\n                <tr v-for=\"(row, rowIndex) in storeFabaoRows\" :key=\"rowIndex\">\r\n                  <td v-for=\"(fabao, colIndex) in row\" :key=\"colIndex\" v-if=\"fabao\" style=\"background: #c0b9dd\">\r\n                    <ItemPopover :equipment=\"get_using_fabao(fabao)\" />\r\n                  </td>\r\n                  <td v-for=\"i in 5 - row.length\" :key=\"'empty-' + i\" style=\"background: #c0b9dd\"></td>\r\n                </tr>\r\n              </table>\r\n            </div>\r\n\r\n            <div class=\"blank9\"></div>\r\n            <table class=\"tb02\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\">\r\n              <tr>\r\n                <th width=\"100\">行囊扩展：</th>\r\n                <td>{{ basic_info.package_num }}</td>\r\n              </tr>\r\n            </table>\r\n          </div>\r\n        </el-tab-pane>\r\n        <el-tab-pane label=\"召唤兽/孩子\" name=\"role_pets\">\r\n          <div class=\"cols\" style=\"width: 190px\">\r\n            <!-- 拆卖召唤兽 -->\r\n            <div v-if=\"split_pets && split_pets.length\">\r\n              <h4>拆卖召唤兽</h4>\r\n              <div class=\"blank9\"></div>\r\n              <table cellspacing=\"0\" cellpadding=\"0\" class=\"tb03 size50 pet-split-tb\" id=\"RoleSplitPets\">\r\n                <tr v-if=\"split_pets.length === 0\">\r\n                  <td class=\"noData\">无</td>\r\n                </tr>\r\n                <template v-else>\r\n                  <tr v-for=\"(row, rowIndex) in splitPetsRows\" :key=\"rowIndex\">\r\n                    <td v-for=\"(pet, colIndex) in row\" :key=\"colIndex\">\r\n                      <div class=\"pet-split-img-wrap\">\r\n                        <img referrerpolicy=\"no-referrer\" :src=\"pet.icon\" :data_idx=\"rowIndex * 3 + colIndex\"\r\n                          @click=\"onPetAvatarClick(pet)\"\r\n                          :class=\"{ on: current_pet && current_pet.equip_sn === pet.equip_sn }\" />\r\n                      </div>\r\n                      <a :href=\"getCBGLinkByType(pet.eid, 'equip')\" tid=\"57i8um2f\" :data_trace_text=\"pet.eid\"\r\n                        target=\"_blank\" class=\"btn-pet-detail\">查看详情</a>\r\n                    </td>\r\n                    <td v-for=\"i in 3 - row.length\" :key=\"'empty-' + i\"\r\n                      style=\"width: 54px; height: 54px; display: none\">\r\n                      &nbsp;\r\n                    </td>\r\n                  </tr>\r\n                </template>\r\n              </table>\r\n            </div>\r\n\r\n            <!-- 召唤兽 -->\r\n            <h4>召唤兽({{ pet_info.length }}/{{ allow_pet_count }})</h4>\r\n            <div class=\"blank9\"></div>\r\n            <table cellspacing=\"0\" cellpadding=\"0\" class=\"tb03 size50\" id=\"RolePets\">\r\n              <tr v-if=\"pet_info.length === 0\">\r\n                <td class=\"noData\">无</td>\r\n              </tr>\r\n              <template v-else>\r\n                <tr v-for=\"(row, rowIndex) in petInfoRows\" :key=\"rowIndex\">\r\n                  <td v-for=\"(pet, colIndex) in row\" :key=\"colIndex\" style=\"width: 54px; height: 54px; cursor: pointer;position: relative;\">\r\n                    <img referrerpolicy=\"no-referrer\" :src=\"pet.icon\" :data_idx=\"rowIndex * 3 + colIndex\"\r\n                      @click=\"onPetAvatarClick(pet)\"\r\n                      :class=\"{ on: current_pet && current_pet.equip_sn === pet.equip_sn }\" />\r\n                    <div v-if=\"getPetRightLock(pet)?.length > 0\"\r\n                      style=\"position: absolute; width: 14px; right: 0px; top: 0px;\">\r\n                      <img v-for=\"l in getPetRightLock(pet)\" :key=\"l\"\r\n                        :src=\"require(`../../../public/assets/images/time_lock_${l}.webp`)\"\r\n                        style=\"height: 14px; width: 14px; display: block;\">\r\n                    </div>\r\n                    <div v-if=\"getPetLeftLock(pet)?.length > 0\"\r\n                      style=\"position: absolute; width: 14px; left: 0px; top: 0px;\">\r\n                      <img v-for=\"l in getPetLeftLock(pet)\" :key=\"l\"\r\n                        :src=\"require(`../../../public/assets/images/time_lock_${l}.webp`)\"\r\n                        style=\"height: 14px; width: 14px;display: block;\">\r\n                    </div>\r\n                  </td>\r\n                  <td v-for=\"i in 3 - row.length\" :key=\"'empty-' + i\" style=\"width: 54px; height: 54px; display: none\">\r\n                    &nbsp;\r\n                  </td>\r\n                </tr>\r\n              </template>\r\n            </table>\r\n\r\n            <div class=\"blank12\"></div>\r\n\r\n            <!-- 孩子 -->\r\n            <h4>孩子</h4>\r\n            <div class=\"blank9\"></div>\r\n            <table cellspacing=\"0\" cellpadding=\"0\" class=\"tb03 size50\" id=\"RoleChilds\">\r\n              <tr v-if=\"child_info.length === 0\">\r\n                <td class=\"noData\">无</td>\r\n              </tr>\r\n              <template v-else>\r\n                <tr v-for=\"(row, rowIndex) in childListRows\" :key=\"rowIndex\">\r\n                  <td v-for=\"(child, colIndex) in row\" :key=\"colIndex\"\r\n                    style=\"width: 54px; height: 54px; cursor: pointer\">\r\n                    <img referrerpolicy=\"no-referrer\" :src=\"child.icon\" :data_idx=\"rowIndex * 2 + colIndex\"\r\n                      @click=\"onPetAvatarClick({ index: colIndex, ...child })\" :class=\"{\r\n                        on:\r\n                          current_pet &&\r\n                          current_pet.equip_sn === child.equip_sn &&\r\n                          current_pet.index === colIndex\r\n                      }\" />\r\n                  </td>\r\n                  <td v-for=\"i in 2 - row.length\" :key=\"'empty-' + i\" style=\"width: 54px; height: 54px; display: none\">\r\n                    &nbsp;\r\n                  </td>\r\n                </tr>\r\n              </template>\r\n            </table>\r\n\r\n            <div class=\"blank12\"></div>\r\n\r\n            <!-- 特殊召唤兽 -->\r\n            <h4>特殊召唤兽</h4>\r\n            <div class=\"blank9\"></div>\r\n            <table cellspacing=\"0\" cellpadding=\"0\" class=\"tb02\">\r\n              <tr v-if=\"special_pet_info === undefined\">\r\n                <td colspan=\"3\" class=\"noData\">未知</td>\r\n              </tr>\r\n              <tr v-else-if=\"special_pet_info.length === 0\">\r\n                <td colspan=\"3\" class=\"noData\">无</td>\r\n              </tr>\r\n              <template v-else>\r\n                <template v-for=\"(pet, petIndex) in special_pet_info\">\r\n                  <tr :key=\"petIndex\">\r\n                    <th>{{ pet.cName }}</th>\r\n                    <td>{{ pet.all_skills[0].name }}</td>\r\n                    <td>{{ pet.all_skills[0].value }}</td>\r\n                  </tr>\r\n                  <tr v-for=\"(skill, skillIndex) in pet.all_skills.slice(1)\" :key=\"skillIndex\">\r\n                    <td>&nbsp;</td>\r\n                    <td>{{ skill.name }}</td>\r\n                    <td>{{ skill.value }}</td>\r\n                  </tr>\r\n                </template>\r\n              </template>\r\n            </table>\r\n\r\n            <div class=\"blank12\"></div>\r\n\r\n            <!-- 召唤兽心得技能 -->\r\n            <h4>召唤兽心得技能</h4>\r\n            <table class=\"tb02\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\">\r\n              <tbody>\r\n                <tr>\r\n                  <th width=\"100\">已解锁技能数：</th>\r\n                  <td class=\"sbook-skill-val\" id=\"show_more_sbook_skill\">\r\n                    <span v-if=\"sbook_skill && sbook_skill.length > 0\" class=\"text-underline\" :title=\"sbook_skill.join(',')\">{{ sbook_skill.length\r\n                      }}/{{\r\n                        sbook_skill_total }}</span>\r\n                    <span v-else>无</span>\r\n                  </td>\r\n                </tr>\r\n              </tbody>\r\n            </table>\r\n          </div>\r\n\r\n          <div class=\"cols\" style=\"width: 456px; margin-left: 18px\" id=\"pet_detail_panel\">\r\n            <div v-if=\"pet_info.length === 0 && child_info.length === 0 && split_pets.length === 0\">\r\n              <h4>详细信息</h4>\r\n              <div class=\"blank9\"></div>\r\n              <table class=\"tb02 petZiZhiTb\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\">\r\n                <tr>\r\n                  <td class=\"noData\" style=\"text-align: center\">无</td>\r\n                </tr>\r\n              </table>\r\n            </div>\r\n            <PetDetail v-else-if=\"current_pet\" :current_pet=\"current_pet\" />\r\n          </div>\r\n        </el-tab-pane>\r\n        <el-tab-pane label=\"坐骑\" name=\"role_riders\">\r\n          <div class=\"cols\" style=\"width: 320px\">\r\n            <h4>坐骑</h4>\r\n            <div class=\"blank9\"></div>\r\n            <table cellspacing=\"0\" cellpadding=\"0\" class=\"tb03 size50\" id=\"RoleRiders\">\r\n              <tr v-if=\"rider_info.length <= 0\">\r\n                <td class=\"noData\">无</td>\r\n              </tr>\r\n              <template v-else>\r\n                <tr v-for=\"(row, rowIndex) in riderRows\" :key=\"rowIndex\">\r\n                  <td v-for=\"(rider, colIndex) in row\" :key=\"colIndex\"\r\n                    style=\"width: 54px; height: 54px; cursor: pointer\">\r\n                    <img referrerpolicy=\"no-referrer\" :src=\"rider.icon\" width=\"50\" height=\"50\"\r\n                      :data_idx=\"rowIndex * 5 + colIndex\" @click=\"current_rider_index = `${rowIndex}-${colIndex}`\"\r\n                      :class=\"{ on: current_rider_index === `${rowIndex}-${colIndex}` }\" />\r\n                  </td>\r\n                  <td v-for=\"i in 5 - row.length\" :key=\"'empty-' + i\" style=\"display: none\"></td>\r\n                </tr>\r\n              </template>\r\n            </table>\r\n            <div class=\"blank12\"></div>\r\n            <div id=\"rider_detail_panel\">\r\n              <table class=\"tb02\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\">\r\n                <tr>\r\n                  <th>类型：</th>\r\n                  <td>{{ currentRider.type_name }}</td>\r\n                  <th>主属性：</th>\r\n                  <td>{{ currentRider.mattrib }}</td>\r\n                </tr>\r\n                <tr>\r\n                  <th>等级：</th>\r\n                  <td>{{ currentRider.grade }}</td>\r\n                  <th>&nbsp;</th>\r\n                  <td>&nbsp;</td>\r\n                </tr>\r\n                <tr>\r\n                  <th>成长：</th>\r\n                  <td>{{ currentRider.exgrow }}</td>\r\n                  <th>&nbsp;</th>\r\n                  <td>&nbsp;</td>\r\n                </tr>\r\n              </table>\r\n              <div class=\"blank12\"></div>\r\n              <div v-if=\"currentRider && currentRider.all_skills && currentRider.all_skills.length > 0\">\r\n                <table cellspacing=\"0\" cellpadding=\"0\" class=\"skillTb\" id=\"RoleRiderSkill\">\r\n                  <tr v-for=\"(row, rowIndex) in riderSkillRows\" :key=\"rowIndex\">\r\n                    <td v-for=\"(skill, colIndex) in row\" :key=\"colIndex\">\r\n                      <img :title=\"skill.name + ' (' + skill.grade + '级)\\n' + skill.desc\" referrerpolicy=\"no-referrer\"\r\n                        :src=\"skill.icon\" width=\"40\" height=\"40\" :data_equip_name=\"skill.name\"\r\n                        data_skill_type=\"riderSkill\" :data_equip_desc=\"skill.desc\" :data_equip_level=\"skill.grade\"\r\n                    />\r\n                      <p>{{ skill.grade }}</p>\r\n                    </td>\r\n                    <td v-for=\"i in 6 - row.length\" :key=\"'empty-' + i\"></td>\r\n                  </tr>\r\n                </table>\r\n              </div>\r\n            </div>\r\n\r\n            <h4>携带玄灵珠</h4>\r\n            <div class=\"blank9\"></div>\r\n            <div class=\"roleModuleScroller\" style=\"max-height: 22em\">\r\n              <table cellspacing=\"0\" cellpadding=\"0\" class=\"tb03 size50\" id=\"RoleXunlingzhu\">\r\n                <tr v-if=\"rider_plan_list.length > 0\">\r\n                  <td v-for=\"(riderplan, index) in rider_plan_list\" :key=\"index\"\r\n                    style=\"width: 54px; height: 54px; cursor: pointer\">\r\n                    <img referrerpolicy=\"no-referrer\" v-if=\"riderplan.type == 1\" :src=\"ResUrl + '/images/big/56973.gif'\"\r\n                      width=\"50\" height=\"50\" :data_idx=\"index\" @click=\"current_rider_plan_index = index\"\r\n                      :class=\"{ on: current_rider_plan_index === index }\" />\r\n                    <img referrerpolicy=\"no-referrer\" v-else-if=\"riderplan.type == 2\"\r\n                      :src=\"ResUrl + '/images/big/56974.gif'\" width=\"50\" height=\"50\" :data_idx=\"index\"\r\n                      @click=\"current_rider_plan_index = index\" :class=\"{ on: current_rider_plan_index === index }\" />\r\n                    <span v-if=\"index == 0\">第一套</span>\r\n                    <span v-else-if=\"index == 1\">第二套</span>\r\n                  </td>\r\n                </tr>\r\n                <tr v-else>\r\n                  <td class=\"noData\">无</td>\r\n                </tr>\r\n              </table>\r\n              <div class=\"blank12\"></div>\r\n              <div id=\"xuanlingzhu_detail_panel\">\r\n                <div v-if=\"currentRiderPlan\">\r\n                  <table class=\"tb02\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\">\r\n                    <tr v-if=\"currentRiderPlan.type === 1\">\r\n                      <th style=\"width: 48px\">类型：</th>\r\n                      <td>{{ currentRiderPlan.level }}级回春</td>\r\n                      <th>&nbsp;</th>\r\n                      <td>&nbsp;</td>\r\n                    </tr>\r\n                    <tr v-if=\"currentRiderPlan.type === 1\">\r\n                      <th style=\"width: 48px\">效果：</th>\r\n                      <td>\r\n                        战斗中\"召唤\"召唤兽或孩子时，恢复自身{{\r\n                          EquipLevel * currentRiderPlan.level\r\n                        }}点气血和{{ currentRiderPlan.level }}点愤怒。\r\n                      </td>\r\n                    </tr>\r\n                    <tr v-if=\"currentRiderPlan.type === 2\">\r\n                      <th style=\"width: 48px\">类型：</th>\r\n                      <td>{{ currentRiderPlan.level }}级破军</td>\r\n                      <th>&nbsp;</th>\r\n                      <td>&nbsp;</td>\r\n                    </tr>\r\n                    <tr v-if=\"currentRiderPlan.type === 2\">\r\n                      <th style=\"width: 48px\">效果：</th>\r\n                      <td>\r\n                        战斗中\"召唤\"召唤兽或孩子时，有{{\r\n                          currentRiderPlan.level * 12.5\r\n                        }}%几率提升自身1%伤害，持续到战斗结束。\r\n                      </td>\r\n                    </tr>\r\n                  </table>\r\n                </div>\r\n              </div>\r\n            </div>\r\n          </div>\r\n\r\n          <div class=\"cols\" style=\"float: right; width: 320px; margin-right: 28px; margin-bottom: 10px\">\r\n            <h4>限量祥瑞</h4>\r\n            <div class=\"blank9\"></div>\r\n            <div v-if=\"nosale_xiangrui == undefined\">\r\n              <p class=\"textCenter cDYellow\">祥瑞信息未知</p>\r\n            </div>\r\n            <div v-else class=\"roleModuleScroller\" style=\"max-height: 22em\">\r\n              <table cellspacing=\"0\" cellpadding=\"0\" class=\"tb02\" id=\"RoleXiangRui\">\r\n                <tr v-if=\"nosale_xiangrui.length <= 0\">\r\n                  <td class=\"noData\">无</td>\r\n                </tr>\r\n                <template v-else>\r\n                  <tr v-for=\"xiangrui in nosale_xiangrui\" :key=\"xiangrui.name\">\r\n                    <th :class=\"{enhance:limitedSkinList.includes(xiangrui.name)}\">{{ xiangrui.name }}</th>\r\n                    <td>\r\n                      技能：\r\n                      <span v-if=\"xiangrui.skill_name\">\r\n                        {{ xiangrui.skill_name }}\r\n                        <span v-if=\"xiangrui.skill_level\">&nbsp;{{ xiangrui.skill_level }}</span>\r\n                      </span>\r\n                      <span v-else>无</span>\r\n                    </td>\r\n                  </tr>\r\n                </template>\r\n              </table>\r\n            </div>\r\n          </div>\r\n\r\n          <div class=\"cols\" style=\"float: right; clear: right; width: 320px; margin-right: 28px\">\r\n            <h4>普通祥瑞</h4>\r\n            <div class=\"blank9\"></div>\r\n            <div v-if=\"xiangrui == undefined\">\r\n              <p class=\"textCenter cDYellow\">祥瑞信息未知</p>\r\n            </div>\r\n            <div v-else class=\"roleModuleScroller\" style=\"max-height: 22em\">\r\n              <table cellspacing=\"0\" cellpadding=\"0\" class=\"tb02\" id=\"RoleXiangRui\">\r\n                <tr v-if=\"xiangrui.length <= 0\">\r\n                  <td class=\"noData\">无</td>\r\n                </tr>\r\n                <template v-else>\r\n                  <tr>\r\n                    <th>祥瑞总数</th>\r\n                    <td>{{ normal_xiangrui_num ? normal_xiangrui_num : totalXiangruiNum }}</td>\r\n                  </tr>\r\n                  <tr v-for=\"xiangrui in xiangrui\" :key=\"xiangrui.name\">\r\n                    <th>{{ xiangrui.name }}</th>\r\n                    <td>\r\n                      技能：\r\n                      <span v-if=\"xiangrui.skill_name\">\r\n                        {{ xiangrui.skill_name }}\r\n                        <span v-if=\"xiangrui.skill_level\">&nbsp;{{ xiangrui.skill_level }}</span>\r\n                      </span>\r\n                      <span v-else>无</span>\r\n                    </td>\r\n                  </tr>\r\n                </template>\r\n              </table>\r\n            </div>\r\n          </div>\r\n        </el-tab-pane>\r\n        <el-tab-pane label=\"锦衣/外观\" name=\"role_clothes\">\r\n          <div class=\"cols tab-jinyi\" style=\"width: 320px\">\r\n            <div class=\"module\">\r\n              <h4>彩果染色</h4>\r\n              <div class=\"blank9\"></div>\r\n              <table v-if=\"basic_info.body_caiguo !== undefined && basic_info.box_caiguo !== undefined\" class=\"tb02\"\r\n                width=\"100%\" cellspacing=\"0\" cellpadding=\"0\">\r\n                <tr>\r\n                  <th width=\"55%\">身上染色折算彩果数：</th>\r\n                  <td>{{ basic_info.body_caiguo }}</td>\r\n                </tr>\r\n                <tr>\r\n                  <th>衣柜已保存染色方案：</th>\r\n                  <td>{{ basic_info.box_caiguo }}</td>\r\n                </tr>\r\n                <tr>\r\n                  <td colspan=\"2\" class=\"cGray\" style=\"font-size: 12px; padding-left: 0px; padding-right: 0px\">\r\n                    （衣柜保存的染色方案包括花豆染色方案和彩果染色方案）\r\n                  </td>\r\n                </tr>\r\n                <tr>\r\n                  <th>所有染色折算彩果数：</th>\r\n                  <td>{{ basic_info.total_caiguo }}</td>\r\n                </tr>\r\n              </table>\r\n              <p v-else-if=\"basic_info.caiguo !== undefined\" class=\"textCenter cDYellow\">\r\n                角色拥有折算彩果总量：{{ basic_info.caiguo }}\r\n              </p>\r\n              <p v-else class=\"textCenter cDYellow\">彩果信息未知</p>\r\n            </div>\r\n            <div v-if=\"new_clothes !== undefined\">\r\n              <div v-for=\"(item, index) in titleConf\" :key=\"index\" class=\"module module-jinyi\">\r\n                <h4>{{ item.title }}</h4>\r\n                <p class=\"jinyi-num\">{{ item.title }}总数：{{ getClothesList(item.key).length }}</p>\r\n                <ul v-if=\"getClothesList(item.key)\" class=\"jinyi-attr-list\">\r\n                  <li v-for=\"(clothesItem, clothesIndex) in getClothesList(item.key)\" :key=\"clothesIndex\" class=\"item\">\r\n                    {{ clothesItem.name }}\r\n                  </li>\r\n                </ul>\r\n              </div>\r\n            </div>\r\n          </div>\r\n\r\n          <div class=\"cols\" style=\"width: 320px; margin-left: 18px\">\r\n            <h4>锦衣道具栏</h4>\r\n            <div class=\"blank9\"></div>\r\n            <p v-if=\"clothes === undefined && new_clothes === undefined\" class=\"textCenter cDYellow\">\r\n              锦衣信息未知\r\n            </p>\r\n\r\n            <div v-else-if=\"new_clothes !== undefined\">\r\n              <ul class=\"xianyu-wrap\">\r\n                <li><i class=\"icon icon-xianyu\"></i>仙玉: {{ basic_info.xianyu }}</li>\r\n                <li>\r\n                  <i class=\"icon icon-xianyu-jifen\"></i>仙玉积分: {{ basic_info.xianyu_score }}\r\n                </li>\r\n                <li><i class=\"icon icon-qicai-jifen\"></i>七彩积分: {{ basic_info.qicai_score }}</li>\r\n              </ul>\r\n              <div class=\"new-jinyi-list\">\r\n                <p class=\"jinyi-num\">锦衣总数：{{ basic_info.total_avatar }}</p>\r\n                <div v-for=\"(item, index) in new_clothes\" :key=\"index\"\r\n                  :class=\"'module module-jinyi module-jinyi—' + index\">\r\n                  <p class=\"jinyi-sub-title\">{{ item.title }}</p>\r\n                  <ul v-if=\"item.list.length > 0\" class=\"jinyi-attr-list\">\r\n                    <li v-for=\"(clothesItem, clothesIndex) in item.list\" :key=\"clothesIndex\" class=\"item\" :style=\"limitedSkinList.includes(clothesItem.name)? 'background:rgba(255, 102, 0, 0.5);color:rgb(0,255,0);' : ''\" >\r\n                      {{ clothesItem.name }}\r\n                    </li>\r\n                  </ul>\r\n                  <p v-else class=\"empty\">无</p>\r\n                </div>\r\n              </div>\r\n            </div>\r\n\r\n            <div v-else>\r\n              <div class=\"roleModuleScroller\" style=\"max-height: 22em\">\r\n                <table cellspacing=\"0\" cellpadding=\"0\" class=\"tb02\" id=\"RoleClothesi\">\r\n                  <tr v-if=\"clothes.length <= 0\">\r\n                    <td class=\"noData\">无</td>\r\n                  </tr>\r\n                  <template v-else>\r\n                    <tr>\r\n                      <th style=\"text-align: left\">\r\n                        锦衣总数 : <span style=\"color: white\">{{ getTotalAvatar() }}</span>\r\n                      </th>\r\n                      <th>&nbsp;</th>\r\n                    </tr>\r\n                    <tr v-for=\"(row, rowIndex) in clothesRows\" :key=\"rowIndex\">\r\n                      <th v-for=\"(clothesItem, colIndex) in row\" :key=\"colIndex\" style=\"text-align: left\" >\r\n                        {{ clothesItem ? clothesItem.name : '' }}\r\n                      </th>\r\n                    </tr>\r\n                  </template>\r\n                </table>\r\n              </div>\r\n            </div>\r\n            <div class=\"blank9\"></div>\r\n          </div>\r\n        </el-tab-pane>\r\n        <el-tab-pane label=\"玩家之家\" name=\"role_home\">\r\n          <div class=\"cols tab-home\" style=\"width:320px;\">\r\n            <div class=\"module\">\r\n              <h4>房屋信息</h4>\r\n              <div class=\"blank9\"></div>\r\n              <table width=\"92%\" class=\"tb02\" cellspacing=\"0\" cellpadding=\"0\">\r\n                <tr>\r\n                  <td><strong>婚否：</strong>{{ basic_info.is_married }}</td>\r\n                  <td><strong>同袍：</strong>{{ basic_info.is_tongpao }}</td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>居住房屋：</strong>{{ basic_info.fangwu_info }}</td>\r\n                  <td v-if=\"basic_info.fangwu_owner_info\"><strong>是否产权所有人：</strong>{{ basic_info.fangwu_owner_info }}</td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>庭院等级：</strong>{{ basic_info.tingyuan_info }}</td>\r\n                  <td><strong>牧场：</strong>{{ basic_info.muchang_info }}</td>\r\n                </tr>\r\n                <tr>\r\n                  <td><strong>社区：</strong>{{ basic_info.community_info }}</td>\r\n                </tr>\r\n                <tr>\r\n                  <td colspan=\"3\"><strong>房契：</strong>{{ basic_info.house_fangqi }}</td>\r\n                </tr>\r\n              </table>\r\n              <div class=\"module module-jinyi\">\r\n                <h4>窗景</h4>\r\n                <p class=\"jinyi-num\">窗景总数：{{ house.house_indoor_view_cnt }}</p>\r\n                <ul v-if=\"house.house_indoor_view && house.house_indoor_view.length\" class=\"jinyi-attr-list roleplay-attr-list\">\r\n                  <li v-for=\"item in house.house_indoor_view\" :key=\"item.name\" class=\"item\">{{ item.name }}</li>\r\n                </ul>\r\n              </div>\r\n              <div class=\"module module-jinyi\">\r\n                <h4>庭院主题</h4>\r\n                <p class=\"jinyi-num\">庭院主题总数：{{ house.house_yard_map_cnt }}</p>\r\n                <ul v-if=\"house.house_yard_map && house.house_yard_map.length\" class=\"jinyi-attr-list roleplay-attr-list\">\r\n                  <li v-for=\"item in house.house_yard_map\" :key=\"item.name\" class=\"item\">{{ item.name }}</li>\r\n                </ul>\r\n              </div>\r\n              <div class=\"module module-jinyi\">\r\n                <h4>庭院特效</h4>\r\n                <p class=\"jinyi-num\">庭院特效总数：{{ house.house_yard_animate_cnt }}</p>\r\n                <ul v-if=\"house.house_yard_animate && house.house_yard_animate.length\" class=\"jinyi-attr-list roleplay-attr-list\">\r\n                  <li v-for=\"item in house.house_yard_animate\" :key=\"item.name\" class=\"item\">{{ item.name }}</li>\r\n                </ul>\r\n              </div>\r\n              <div class=\"module module-jinyi\">\r\n                <h4>庭院饰品</h4>\r\n                <p class=\"jinyi-num\">庭院饰品总数：{{ house.house_yard_fur_cnt }}</p>\r\n                <ul v-if=\"house.house_yard_fur && house.house_yard_fur.length\" class=\"jinyi-attr-list roleplay-attr-list\">\r\n                  <li v-for=\"item in house.house_yard_fur\" :key=\"item.name\" class=\"item\">{{ item.name }}*{{ item.count }}</li>\r\n                </ul>\r\n              </div>\r\n            </div>\r\n          </div>\r\n          \r\n          <div class=\"cols\" style=\"width:320px; margin-left:18px;\">\r\n            <div class=\"module module-jinyi module-roleplay\">\r\n              <h4>建材</h4>\r\n              <p class=\"jinyi-num\">建材总数：{{ house.house_building_material_cnt }}</p>\r\n              <ul v-if=\"house.house_building_material && house.house_building_material.length\" class=\"jinyi-attr-list roleplay-attr-list\">\r\n                <li v-for=\"item in house.house_building_material\" :key=\"item.name\" class=\"item\">\r\n                  <span>{{ item.name }}</span>*{{ item.count }}\r\n                </li>\r\n              </ul>\r\n            </div>\r\n            <div class=\"module module-jinyi\">\r\n              <h4>家具</h4>\r\n              <p class=\"jinyi-num\">家具总数：{{ house.house_jiaju_num }}</p>\r\n              <ul v-if=\"house.house_jiaju && house.house_jiaju.length\" class=\"jinyi-attr-list roleplay-attr-list\">\r\n                <li v-for=\"item in house.house_jiaju\" :key=\"item.name\" class=\"item\">\r\n                  <span>{{ item.name }}</span>*{{ item.count }}\r\n                </li>\r\n              </ul>\r\n            </div>\r\n            <div class=\"blank9\"></div>\r\n          </div>\r\n        </el-tab-pane>\r\n      </el-tabs>\r\n    </div>\r\n  </el-popover>\r\n</template>\r\n\r\n<script>\r\nimport { commonMixin } from '@/utils/mixins/commonMixin'\r\nimport  ItemPopover  from './ItemPopover.vue'\r\nimport PetDetail from './PetDetail.vue'\r\n\r\nconst riderNumPerLine = 5\r\nexport default {\r\n  name: 'RoleImage',\r\n  components: {\r\n    ItemPopover,\r\n    PetDetail\r\n  },\r\n  mixins: [commonMixin],\r\n  props: {\r\n    size: { type: String, default: 'small' },\r\n    width: { type: String, default: '50px' },\r\n    height: { type: String, default: '50px' },\r\n    cursor: { type: String, default: 'pointer' },\r\n    placement: { type: String, default: 'right' },\r\n    popoverWidth: { type: String, default: '400px' },\r\n    other_info: {\r\n      type: String,\r\n      default: ''\r\n    },\r\n    roleInfo: {\r\n      type: Object,\r\n      required: true\r\n    }\r\n  },\r\n  data() {\r\n    return {\r\n      limitedSkinList:window.limitedSkinList || [],\r\n      ResUrl: window.ResUrl,\r\n      shenqi_visible: false,\r\n      visible: false,\r\n      activeName: 'role_basic',\r\n      basic_info: null,\r\n      school_skill: null,\r\n      life_skill: null,\r\n      ju_qing_skill: null,\r\n      shuliandu: null,\r\n      left_skill_point: 0,\r\n      role_xiulian: [],\r\n      pet_ctrl_skill: [],\r\n      yu_shou_shu: undefined,\r\n      currentDisplayIndex: 0, // 添加当前显示索引\r\n      not_using_equips: null,\r\n      split_equips: null,\r\n      shenqi: null,\r\n      huoshenta: null,\r\n      using_lingbao: null,\r\n      nousing_lingbao: null,\r\n      nousing_fabao: null,\r\n      using_fabao: null,\r\n      unused_fabao_sum: null,\r\n      fabao_storage_size: null,\r\n      shenqi_components: {},\r\n      split_pets: [],\r\n      pet_info: [],\r\n      child_info: [],\r\n      special_pet_info: [],\r\n      sbook_skill: [],\r\n      allow_pet_count: 0,\r\n      sbook_skill_total: 0,\r\n      current_pet: null,\r\n      rider_info: [],\r\n      current_rider_index: '0-0',\r\n      rider_plan_list: [],\r\n      current_rider_plan_index: 0,\r\n      xiangrui: [],\r\n      nosale_xiangrui: [],\r\n      normal_xiangrui_num: 0,\r\n      EquipLevel: 159,\r\n      clothes: null,\r\n      new_clothes: null,\r\n      house: null,\r\n      titleConf: [\r\n        {\r\n          title: '称谓特效',\r\n          key: 'title_effect'\r\n        },\r\n        {\r\n          title: '施法/攻击特效',\r\n          key: 'perform_effect'\r\n        },\r\n        {\r\n          title: '冒泡框',\r\n          key: 'chat_effect'\r\n        },\r\n        {\r\n          title: '头像框',\r\n          key: 'icon_effect'\r\n        },\r\n        {\r\n          title: '彩饰-队标',\r\n          key: 'achieve_show'\r\n        }\r\n      ]\r\n    }\r\n  },\r\n  computed: {\r\n    currentRider() {\r\n      const [rowIndex, colIndex] = this.current_rider_index.split('-').map(Number)\r\n      const rider = this.rider_info[rowIndex * riderNumPerLine + colIndex]\r\n      return rider || {}\r\n    },\r\n    currentRiderPlan() {\r\n      return this.rider_plan_list[this.current_rider_plan_index] || null\r\n    },\r\n    imageUrl() {\r\n      const icon = window.get_role_icon(this.other_info)\r\n      return window.ResUrl + '/images/role_icon/small/' + icon + '.gif'\r\n    },\r\n    imageStyle() {\r\n      return {\r\n        display: 'block',\r\n        width: this.width,\r\n        height: this.height,\r\n        cursor: this.cursor\r\n      }\r\n    },\r\n    extraAttrPoints() {\r\n      const currentFullYear = window.ServerTime\r\n        ? +window.ServerTime.split('-')[0]\r\n        : new Date().getFullYear()\r\n      return (currentFullYear - 2004 + 1) * 3\r\n    },\r\n    // 师门技能相关属性\r\n    school_skill1_icon() {\r\n      return this.school_skill && this.school_skill[0] ? this.school_skill[0].skill_icon : ''\r\n    },\r\n    school_skill1_name() {\r\n      return this.school_skill && this.school_skill[0] ? this.school_skill[0].skill_name : ''\r\n    },\r\n    school_skill1_grade() {\r\n      return this.school_skill && this.school_skill[0] ? this.school_skill[0].skill_grade : ''\r\n    },\r\n    school_skill1_desc() {\r\n      return this.school_skill && this.school_skill[0] ? this.school_skill[0].desc : ''\r\n    },\r\n\r\n    school_skill2_icon() {\r\n      return this.school_skill && this.school_skill[1] ? this.school_skill[1].skill_icon : ''\r\n    },\r\n    school_skill2_name() {\r\n      return this.school_skill && this.school_skill[1] ? this.school_skill[1].skill_name : ''\r\n    },\r\n    school_skill2_grade() {\r\n      return this.school_skill && this.school_skill[1] ? this.school_skill[1].skill_grade : ''\r\n    },\r\n    school_skill2_desc() {\r\n      return this.school_skill && this.school_skill[1] ? this.school_skill[1].desc : ''\r\n    },\r\n\r\n    school_skill3_icon() {\r\n      return this.school_skill && this.school_skill[2] ? this.school_skill[2].skill_icon : ''\r\n    },\r\n    school_skill3_name() {\r\n      return this.school_skill && this.school_skill[2] ? this.school_skill[2].skill_name : ''\r\n    },\r\n    school_skill3_grade() {\r\n      return this.school_skill && this.school_skill[2] ? this.school_skill[2].skill_grade : ''\r\n    },\r\n    school_skill3_desc() {\r\n      return this.school_skill && this.school_skill[2] ? this.school_skill[2].desc : ''\r\n    },\r\n\r\n    school_skill4_icon() {\r\n      return this.school_skill && this.school_skill[3] ? this.school_skill[3].skill_icon : ''\r\n    },\r\n    school_skill4_name() {\r\n      return this.school_skill && this.school_skill[3] ? this.school_skill[3].skill_name : ''\r\n    },\r\n    school_skill4_grade() {\r\n      return this.school_skill && this.school_skill[3] ? this.school_skill[3].skill_grade : ''\r\n    },\r\n    school_skill4_desc() {\r\n      return this.school_skill && this.school_skill[3] ? this.school_skill[3].desc : ''\r\n    },\r\n\r\n    school_skill5_icon() {\r\n      return this.school_skill && this.school_skill[4] ? this.school_skill[4].skill_icon : ''\r\n    },\r\n    school_skill5_name() {\r\n      return this.school_skill && this.school_skill[4] ? this.school_skill[4].skill_name : ''\r\n    },\r\n    school_skill5_grade() {\r\n      return this.school_skill && this.school_skill[4] ? this.school_skill[4].skill_grade : ''\r\n    },\r\n    school_skill5_desc() {\r\n      return this.school_skill && this.school_skill[4] ? this.school_skill[4].desc : ''\r\n    },\r\n\r\n    school_skill6_icon() {\r\n      return this.school_skill && this.school_skill[5] ? this.school_skill[5].skill_icon : ''\r\n    },\r\n    school_skill6_name() {\r\n      return this.school_skill && this.school_skill[5] ? this.school_skill[5].skill_name : ''\r\n    },\r\n    school_skill6_grade() {\r\n      return this.school_skill && this.school_skill[5] ? this.school_skill[5].skill_grade : ''\r\n    },\r\n    school_skill6_desc() {\r\n      return this.school_skill && this.school_skill[5] ? this.school_skill[5].desc : ''\r\n    },\r\n\r\n    school_skill7_icon() {\r\n      return this.school_skill && this.school_skill[6] ? this.school_skill[6].skill_icon : ''\r\n    },\r\n    school_skill7_name() {\r\n      return this.school_skill && this.school_skill[6] ? this.school_skill[6].skill_name : ''\r\n    },\r\n    school_skill7_grade() {\r\n      return this.school_skill && this.school_skill[6] ? this.school_skill[6].skill_grade : ''\r\n    },\r\n    school_skill7_desc() {\r\n      return this.school_skill && this.school_skill[6] ? this.school_skill[6].desc : ''\r\n    },\r\n\r\n    // 装备相关计算属性\r\n    storeEquipsRows() {\r\n      const numPerLine = 5\r\n      const equips = this.not_using_equips || []\r\n      const equipsNum = equips.length\r\n\r\n      // 计算需要的行数，确保至少有4行\r\n      let loopTimes = parseInt(equipsNum / numPerLine) + (equipsNum % numPerLine ? 1 : 0)\r\n      loopTimes = loopTimes < 4 ? 4 : loopTimes\r\n\r\n      const rows = []\r\n      for (let i = 0; i < loopTimes; i++) {\r\n        const items = equips.slice(i * numPerLine, (i + 1) * numPerLine)\r\n        rows.push(items)\r\n      }\r\n      return rows\r\n    },\r\n\r\n    splitEquipsRows() {\r\n      if (!this.split_equips || this.split_equips.length === 0) return []\r\n      const numPerLine = 5\r\n      const rows = []\r\n      for (let i = 0; i < this.split_equips.length; i += numPerLine) {\r\n        rows.push(this.split_equips.slice(i, i + numPerLine))\r\n      }\r\n      return rows\r\n    },\r\n\r\n    nousingLingbaoRows() {\r\n      const colCount = 5\r\n      const lingbao = this.nousing_lingbao || []\r\n      const max = Math.max(1, Math.ceil(lingbao.length / colCount))\r\n      const rows = []\r\n      for (let i = 0; i < max; i++) {\r\n        const row = []\r\n        for (let j = 0; j < colCount; j++) {\r\n          const index = i * colCount + j\r\n          row.push(lingbao[index] || null)\r\n        }\r\n        rows.push(row)\r\n      }\r\n      return rows\r\n    },\r\n\r\n    storeFabaoRows() {\r\n      if (!this.nousing_fabao || this.nousing_fabao.length === 0) return []\r\n      const numPerLine = 5\r\n      const rows = []\r\n      for (let i = 0; i < this.nousing_fabao.length; i += numPerLine) {\r\n        rows.push(this.nousing_fabao.slice(i, i + numPerLine))\r\n      }\r\n      // 确保至少有4行\r\n      while (rows.length < 4) {\r\n        rows.push([])\r\n      }\r\n      return rows\r\n    },\r\n\r\n    // 召唤兽相关计算属性\r\n    splitPetsRows() {\r\n      const numPerLine = 3\r\n      const pets = this.split_pets || []\r\n      const petNum = pets.length\r\n      const loopTimes =\r\n        petNum === 0 ? 1 : parseInt(petNum / numPerLine) + (petNum % numPerLine ? 1 : 0)\r\n\r\n      const rows = []\r\n      for (let i = 0; i < loopTimes; i++) {\r\n        const items = pets.slice(i * numPerLine, (i + 1) * numPerLine)\r\n        rows.push(items)\r\n      }\r\n      return rows\r\n    },\r\n    petInfoRows() {\r\n      const numPerLine = 3\r\n      const pets = this.pet_info || []\r\n      const petNum = pets.length\r\n      const loopTimes =\r\n        petNum === 0 ? 1 : parseInt(petNum / numPerLine) + (petNum % numPerLine ? 1 : 0)\r\n\r\n      const rows = []\r\n      for (let i = 0; i < loopTimes; i++) {\r\n        const items = pets.slice(i * numPerLine, (i + 1) * numPerLine)\r\n        rows.push(items)\r\n      }\r\n      return rows\r\n    },\r\n\r\n    childListRows() {\r\n      const numPerLine = 2\r\n      const children = this.child_info || []\r\n      const childNum = children.length\r\n      const loopTimes =\r\n        childNum === 0 ? 1 : parseInt(childNum / numPerLine) + (childNum % numPerLine ? 1 : 0)\r\n\r\n      const rows = []\r\n      for (let i = 0; i < loopTimes; i++) {\r\n        const items = children.slice(i * numPerLine, (i + 1) * numPerLine)\r\n        rows.push(items)\r\n      }\r\n      return rows\r\n    },\r\n\r\n\r\n\r\n    // 坐骑相关计算属性\r\n    riderRows() {\r\n      const numPerLine = riderNumPerLine\r\n      const riders = this.rider_info || []\r\n      const riderNum = riders.length\r\n      const loopTimes = parseInt(riderNum / numPerLine) + (riderNum % numPerLine ? 1 : 0)\r\n\r\n      const rows = []\r\n      for (let i = 0; i < loopTimes; i++) {\r\n        const items = riders.slice(i * numPerLine, (i + 1) * numPerLine)\r\n        rows.push(items)\r\n      }\r\n      return rows\r\n    },\r\n\r\n    // 计算祥瑞总数\r\n    totalXiangruiNum() {\r\n      const nosaleNum = this.nosale_xiangrui ? this.nosale_xiangrui.length : 0\r\n      const totalNum = this.basic_info ? this.basic_info.total_horse : 0\r\n\r\n      if (!totalNum && this.xiangrui) {\r\n        const num = this.xiangrui.length\r\n        return num >= 10 ? '大于等于10' : num\r\n      } else {\r\n        return totalNum - nosaleNum\r\n      }\r\n    },\r\n\r\n    // 坐骑技能行计算属性\r\n    riderSkillRows() {\r\n      if (!this.currentRider || !this.currentRider.all_skills) return []\r\n      const numPerLine = 6\r\n      const skills = this.currentRider.all_skills\r\n      const skillNum = skills.length\r\n      let loopTimes = parseInt(skillNum / numPerLine) + (skillNum % numPerLine ? 1 : 0)\r\n      if (loopTimes === 0) {\r\n        loopTimes = 1\r\n      }\r\n\r\n      const rows = []\r\n      for (let i = 0; i < loopTimes; i++) {\r\n        const items = skills.slice(i * numPerLine, (i + 1) * numPerLine)\r\n        rows.push(items)\r\n      }\r\n      return rows\r\n    },\r\n    clothesRows() {\r\n      const numPerLine = 2\r\n      const rows = []\r\n      for (let i = 0; i < this.clothes.length; i += numPerLine) {\r\n        const row = this.clothes.slice(i, i + numPerLine)\r\n        // 填充空位\r\n        while (row.length < numPerLine) {\r\n          row.push(null)\r\n        }\r\n        rows.push(row)\r\n      }\r\n      return rows\r\n    }\r\n  },\r\n  watch: {\r\n    visible: {\r\n      handler(newVal) {\r\n        if(newVal) {\r\n          this.getLimitedSkinConfig()\r\n        }\r\n      },\r\n      immediate: true\r\n    }\r\n  },\r\n  mounted() {\r\n    this.basic_info = this.roleInfo.basic_info || {}\r\n    this.role_xiulian = this.roleInfo.role_xiulian || []\r\n    this.pet_ctrl_skill = this.roleInfo.pet_ctrl_skill || []\r\n    this.yu_shou_shu = this.roleInfo.role_skill.yu_shou_shu\r\n    this.school_skill = this.roleInfo.role_skill.school_skill\r\n    this.life_skill = this.roleInfo.role_skill.life_skill\r\n    this.ju_qing_skill = this.roleInfo.role_skill.ju_qing_skill\r\n    this.shuliandu = this.roleInfo.role_skill.shuliandu\r\n    this.left_skill_point = this.roleInfo.left_skill_point || 0\r\n\r\n    // 装备相关数据\r\n    this.using_equips = this.roleInfo.using_equips || []\r\n    this.not_using_equips = this.roleInfo.not_using_equips || []\r\n    this.split_equips = this.roleInfo.split_equips || []\r\n    this.shenqi = this.roleInfo.shenqi || null\r\n    this.huoshenta = this.roleInfo.huoshenta || null\r\n    this.shenqi_components = this.roleInfo.shenqi_components || {}\r\n    this.using_lingbao = this.roleInfo.using_lingbao || []\r\n    this.nousing_lingbao = this.roleInfo.nousing_lingbao || []\r\n    this.nousing_fabao = this.roleInfo.nousing_fabao || []\r\n    this.using_fabao = this.roleInfo.using_fabao || []\r\n    this.unused_fabao_sum = this.roleInfo.unused_fabao_sum\r\n    this.fabao_storage_size = this.roleInfo.fabao_storage_size\r\n\r\n    //召唤兽\r\n    this.split_pets = this.roleInfo.split_pets || []\r\n    this.pet_info = this.roleInfo.pet_info || []\r\n    if (this.pet_info.length > 0) {\r\n      this.current_pet = this.pet_info[0]\r\n    } else if (this.split_pets.length > 0) {\r\n      this.current_pet = this.split_pets[0]\r\n    } else if (this.child_info.length > 0) {\r\n      this.current_pet = this.child_info[0]\r\n    }\r\n    this.child_info = this.roleInfo.child_info || []\r\n    this.special_pet_info = this.roleInfo.special_pet_info || []\r\n    this.sbook_skill = this.roleInfo.sbook_skill || []\r\n    this.allow_pet_count = this.roleInfo.allow_pet_count || 0\r\n    this.sbook_skill_total = this.roleInfo.sbook_skill_total || 0\r\n\r\n    //坐骑\r\n    this.rider_info = this.roleInfo.rider_info || []\r\n    this.rider_plan_list = this.roleInfo.rider_plan_list || []\r\n    this.xiangrui = this.roleInfo.xiangrui || []\r\n    this.nosale_xiangrui = this.roleInfo.nosale_xiangrui || []\r\n    this.normal_xiangrui_num = this.roleInfo.normal_xiangrui_num || 0\r\n\r\n    // 初始化坐骑选择\r\n    if (this.rider_info.length > 0) {\r\n      this.current_rider_index = '0-0'\r\n    }\r\n\r\n    // 初始化玄灵珠选择\r\n    if (this.rider_plan_list.length > 0) {\r\n      this.current_rider_plan_index = 0\r\n    }\r\n    this.EquipLevel = this.basic_info.role_level\r\n    // 初始化锦衣数据\r\n    this.clothes = this.roleInfo.clothes || null\r\n    this.new_clothes = this.roleInfo.new_clothes || null\r\n    \r\n    // 初始化房屋数据\r\n    this.house = this.roleInfo.house || {}\r\n  },\r\n  methods: {\r\n    async getLimitedSkinConfig() {\r\n      if (!window.limitedSkinList) {\r\n        const config = await this.$api.system.getLimitedSkinConfig()\r\n        const limitedSkinList = []\r\n        for (const itemType in config) {\r\n          for (const kName in config[itemType]) {\r\n            limitedSkinList.push(kName)\r\n          }\r\n        }\r\n        window.limitedSkinList  = limitedSkinList\r\n      }\r\n      this.limitedSkinList = window.limitedSkinList\r\n    },\r\n    getPetRightLock(pet) {\r\n      return pet.lock_type?.filter(item => item !== 9 && item !== 'protect' && item !== 'huoyue')\r\n    },\r\n    getPetLeftLock(pet) {\r\n      return pet.lock_type?.filter(item => item === 9 || item === 'protect' || item === 'huoyue')\r\n    },\r\n    onPetAvatarClick(pet) {\r\n      this.current_pet = pet\r\n    },\r\n    get_using_equip(target) {\r\n      const equip =\r\n        typeof target === 'number' ? this.using_equips.find(({ pos }) => pos === target) : target\r\n      if (equip) {\r\n        return {\r\n          equip_sn: equip.equip_sn,\r\n          equip_face_img: equip.small_icon,\r\n          equip_name: equip.name,\r\n          equip_type_desc: equip.static_desc,\r\n          large_equip_desc: equip.desc,\r\n          lock_type: equip.lock_type,\r\n\r\n          src: equip.small_icon,\r\n          data_equip_name: equip.name,\r\n          data_equip_type: equip.type,\r\n          data_equip_desc: equip.desc,\r\n          data_equip_type_desc: equip.static_desc\r\n        }\r\n      }\r\n    },\r\n    get_using_fabao(target) {\r\n      const fabao =\r\n        typeof target === 'number' ? this.using_fabao.find(({ pos }) => pos === target) : target\r\n      if (fabao) {\r\n        return {\r\n          equip_sn: fabao.type,\r\n          equip_face_img: fabao.icon,\r\n          equip_name: fabao.name,\r\n          equip_type_desc: fabao.static_desc,\r\n          large_equip_desc: fabao.desc,\r\n\r\n          icon: fabao.icon,\r\n          data_equip_name: fabao.name,\r\n          data_equip_type: fabao.type,\r\n          data_equip_desc: fabao.desc,\r\n          data_equip_type_desc: fabao.static_desc\r\n        }\r\n      }\r\n    },\r\n    htmlEncode(str) {\r\n      if (!str) return ''\r\n      return str\r\n        .replace(/&/g, '&amp;')\r\n        .replace(/</g, '&lt;')\r\n        .replace(/>/g, '&gt;')\r\n        .replace(/\"/g, '&quot;')\r\n        .replace(/'/g, '&#39;')\r\n    },\r\n    toggle_display(index) {\r\n      // 使用Vue响应式数据控制显示状态\r\n      this.currentDisplayIndex = index\r\n    },\r\n    skillRows(skills, numPerLine) {\r\n      if (!skills || skills.length === 0) return []\r\n      const rows = []\r\n      for (let i = 0; i < skills.length; i += numPerLine) {\r\n        rows.push(skills.slice(i, i + numPerLine))\r\n      }\r\n      return rows\r\n    },\r\n    switchShenqiTab(index) {\r\n      // 检查该套属性是否存在且有效\r\n      const shenqiKey = 'shenqi' + (index + 1)\r\n      const shenqiData = this.shenqi_components[shenqiKey]\r\n\r\n      if (!shenqiData) {\r\n        return // 如果该套属性不存在，不执行切换\r\n      }\r\n\r\n      // 先将所有套属性设置为非激活状态\r\n      Object.keys(this.shenqi_components).forEach((key) => {\r\n        if (this.shenqi_components[key]) {\r\n          this.shenqi_components[key].actived = false\r\n        }\r\n      })\r\n\r\n      // 将选中的套属性设置为激活状态\r\n      this.shenqi_components[shenqiKey].actived = true\r\n    },\r\n\r\n    getClothesList(key) {\r\n      return this[key] || []\r\n    },\r\n    getTotalAvatar() {\r\n      if (this.basic_info.total_avatar) {\r\n        return this.basic_info.total_avatar\r\n      }\r\n      return this.clothes.length < 20 ? this.clothes.length : '大于等于20'\r\n    }\r\n  }\r\n}\r\n</script>\r\n\r\n<style scoped>\r\n::v-deep .role-info-tabs .el-tabs__nav .el-tabs__item {\r\n  padding: 0 !important;\r\n  width: 98px;\r\n  height: 26px;\r\n  line-height: 26px;\r\n  background: url(../../../public/assets/images/tag1.webp) no-repeat;\r\n  text-align: center;\r\n  float: left;\r\n  margin-right: 3px;\r\n  display: inline;\r\n  color: #748da4;\r\n  cursor: pointer;\r\n}\r\n\r\n::v-deep .role-info-tabs .el-tabs__nav .el-tabs__item.is-active {\r\n  background: url(../../../public/assets/images/tag2.webp) no-repeat;\r\n  color: #fff;\r\n}\r\n\r\n:global(.role-info-popover) {\r\n  padding: 0 !important;\r\n  background: transparent;\r\n  box-shadow: none;\r\n  border: none;\r\n  font-size: 12px;\r\n}\r\n\r\n:global(.role-info-popover .tabCont) {\r\n  padding: 0 !important;\r\n  background: none;\r\n}\r\n\r\n:global(.role-info-popover .tabCont) {\r\n  padding: 0 !important;\r\n}\r\n\r\n:global(.role-info-popover .el-tabs__header) {\r\n  margin-bottom: 0 !important;\r\n  border-bottom: 2px solid #fff;\r\n}\r\n\r\n:global(.role-info-popover .el-tabs__content) {\r\n  padding: 12px;\r\n  background: url(../../../public/assets/images/areabg.webp) repeat-y -100px;\r\n  min-height: 510px;\r\n}\r\n\r\n:global(.role-info-popover .el-tabs__active-bar) {\r\n  display: none !important;\r\n}\r\n\r\n:global(.shenqi-modal) {\r\n  position: relative;\r\n  top: unset;\r\n  left: unset;\r\n  margin-left: unset;\r\n}\r\n\r\n:global(.shenqi-info-popover) {\r\n  padding: 0 !important;\r\n  background: #0a1f28;\r\n  border-color: #0a1f28;\r\n}\r\n\r\n:global(.shenqi-info-popover .popper__arrow::after) {\r\n  border-bottom-color: #0a1f28 !important;\r\n}\r\n\r\n:global(.role-info-popover .popper__arrow::after) {\r\n  border-right-color: #0a1f28 !important;\r\n}\r\n</style>\r\n"],"sourceRoot":""}]);
// Exports
/* harmony default export */ __webpack_exports__["default"] = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/vue-style-loader/index.js!./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/chrome-extensions/DevToolsPanel.vue?vue&type=style&index=0&id=42c7142d&scoped=true&lang=css":
/*!************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/vue-style-loader/index.js!./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/chrome-extensions/DevToolsPanel.vue?vue&type=style&index=0&id=42c7142d&scoped=true&lang=css ***!
  \************************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(/*! !!../../node_modules/css-loader/dist/cjs.js!../../node_modules/vue-loader/lib/loaders/stylePostLoader.js!../../node_modules/vue-loader/lib/index.js??vue-loader-options!./DevToolsPanel.vue?vue&type=style&index=0&id=42c7142d&scoped=true&lang=css */ "./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/chrome-extensions/DevToolsPanel.vue?vue&type=style&index=0&id=42c7142d&scoped=true&lang=css");
if(content.__esModule) content = content.default;
if(typeof content === 'string') content = [[module.id, content, '']];
if(content.locals) module.exports = content.locals;
// add the styles to the DOM
var add = (__webpack_require__(/*! !../../node_modules/vue-style-loader/lib/addStylesClient.js */ "./node_modules/vue-style-loader/lib/addStylesClient.js")["default"])
var update = add("7da68598", content, false, {});
// Hot Module Replacement
if(false) // removed by dead control flow
{}

/***/ }),

/***/ "./node_modules/vue-style-loader/index.js!./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=style&index=0&id=26200cad&scoped=true&lang=css":
/*!********************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/vue-style-loader/index.js!./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=style&index=0&id=26200cad&scoped=true&lang=css ***!
  \********************************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(/*! !!../../../node_modules/css-loader/dist/cjs.js!../../../node_modules/vue-loader/lib/loaders/stylePostLoader.js!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./EquipmentDesc.vue?vue&type=style&index=0&id=26200cad&scoped=true&lang=css */ "./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=style&index=0&id=26200cad&scoped=true&lang=css");
if(content.__esModule) content = content.default;
if(typeof content === 'string') content = [[module.id, content, '']];
if(content.locals) module.exports = content.locals;
// add the styles to the DOM
var add = (__webpack_require__(/*! !../../../node_modules/vue-style-loader/lib/addStylesClient.js */ "./node_modules/vue-style-loader/lib/addStylesClient.js")["default"])
var update = add("1841d2e1", content, false, {});
// Hot Module Replacement
if(false) // removed by dead control flow
{}

/***/ }),

/***/ "./node_modules/vue-style-loader/index.js!./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentImage.vue?vue&type=style&index=0&id=13caaaef&scoped=true&lang=css":
/*!*********************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/vue-style-loader/index.js!./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentImage.vue?vue&type=style&index=0&id=13caaaef&scoped=true&lang=css ***!
  \*********************************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(/*! !!../../../node_modules/css-loader/dist/cjs.js!../../../node_modules/vue-loader/lib/loaders/stylePostLoader.js!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./EquipmentImage.vue?vue&type=style&index=0&id=13caaaef&scoped=true&lang=css */ "./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentImage.vue?vue&type=style&index=0&id=13caaaef&scoped=true&lang=css");
if(content.__esModule) content = content.default;
if(typeof content === 'string') content = [[module.id, content, '']];
if(content.locals) module.exports = content.locals;
// add the styles to the DOM
var add = (__webpack_require__(/*! !../../../node_modules/vue-style-loader/lib/addStylesClient.js */ "./node_modules/vue-style-loader/lib/addStylesClient.js")["default"])
var update = add("22456dfe", content, false, {});
// Hot Module Replacement
if(false) // removed by dead control flow
{}

/***/ }),

/***/ "./node_modules/vue-style-loader/index.js!./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/RoleImage.vue?vue&type=style&index=0&id=8c1934ec&scoped=true&lang=css":
/*!**********************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/vue-style-loader/index.js!./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/RoleImage.vue?vue&type=style&index=0&id=8c1934ec&scoped=true&lang=css ***!
  \**********************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(/*! !!../../../node_modules/css-loader/dist/cjs.js!../../../node_modules/vue-loader/lib/loaders/stylePostLoader.js!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./RoleImage.vue?vue&type=style&index=0&id=8c1934ec&scoped=true&lang=css */ "./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/RoleImage.vue?vue&type=style&index=0&id=8c1934ec&scoped=true&lang=css");
if(content.__esModule) content = content.default;
if(typeof content === 'string') content = [[module.id, content, '']];
if(content.locals) module.exports = content.locals;
// add the styles to the DOM
var add = (__webpack_require__(/*! !../../../node_modules/vue-style-loader/lib/addStylesClient.js */ "./node_modules/vue-style-loader/lib/addStylesClient.js")["default"])
var update = add("600b2cec", content, false, {});
// Hot Module Replacement
if(false) // removed by dead control flow
{}

/***/ }),

/***/ "./public/assets/images sync recursive ^\\.\\/time_lock_.*\\.webp$":
/*!*************************************************************!*\
  !*** ./public/assets/images/ sync ^\.\/time_lock_.*\.webp$ ***!
  \*************************************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

var map = {
	"./time_lock_1.webp": "./public/assets/images/time_lock_1.webp",
	"./time_lock_10.webp": "./public/assets/images/time_lock_10.webp",
	"./time_lock_3.webp": "./public/assets/images/time_lock_3.webp",
	"./time_lock_8.webp": "./public/assets/images/time_lock_8.webp",
	"./time_lock_9.webp": "./public/assets/images/time_lock_9.webp",
	"./time_lock_huoyue.webp": "./public/assets/images/time_lock_huoyue.webp",
	"./time_lock_protect.webp": "./public/assets/images/time_lock_protect.webp"
};


function webpackContext(req) {
	var id = webpackContextResolve(req);
	return __webpack_require__(id);
}
function webpackContextResolve(req) {
	if(!__webpack_require__.o(map, req)) {
		var e = new Error("Cannot find module '" + req + "'");
		e.code = 'MODULE_NOT_FOUND';
		throw e;
	}
	return map[req];
}
webpackContext.keys = function webpackContextKeys() {
	return Object.keys(map);
};
webpackContext.resolve = webpackContextResolve;
module.exports = webpackContext;
webpackContext.id = "./public/assets/images sync recursive ^\\.\\/time_lock_.*\\.webp$";

/***/ }),

/***/ "./public/assets/images/areabg.webp":
/*!******************************************!*\
  !*** ./public/assets/images/areabg.webp ***!
  \******************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

"use strict";
module.exports = __webpack_require__.p + "assets/images/areabg.webp";

/***/ }),

/***/ "./public/assets/images/tag1.webp":
/*!****************************************!*\
  !*** ./public/assets/images/tag1.webp ***!
  \****************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

"use strict";
module.exports = __webpack_require__.p + "assets/images/tag1.webp";

/***/ }),

/***/ "./public/assets/images/tag2.webp":
/*!****************************************!*\
  !*** ./public/assets/images/tag2.webp ***!
  \****************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

"use strict";
module.exports = __webpack_require__.p + "assets/images/tag2.webp";

/***/ }),

/***/ "./public/assets/images/time_lock_1.webp":
/*!***********************************************!*\
  !*** ./public/assets/images/time_lock_1.webp ***!
  \***********************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

"use strict";
module.exports = __webpack_require__.p + "assets/images/time_lock_1.webp";

/***/ }),

/***/ "./public/assets/images/time_lock_10.webp":
/*!************************************************!*\
  !*** ./public/assets/images/time_lock_10.webp ***!
  \************************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

"use strict";
module.exports = __webpack_require__.p + "assets/images/time_lock_10.webp";

/***/ }),

/***/ "./public/assets/images/time_lock_3.webp":
/*!***********************************************!*\
  !*** ./public/assets/images/time_lock_3.webp ***!
  \***********************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

"use strict";
module.exports = __webpack_require__.p + "assets/images/time_lock_3.webp";

/***/ }),

/***/ "./public/assets/images/time_lock_8.webp":
/*!***********************************************!*\
  !*** ./public/assets/images/time_lock_8.webp ***!
  \***********************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

"use strict";
module.exports = __webpack_require__.p + "assets/images/time_lock_8.webp";

/***/ }),

/***/ "./public/assets/images/time_lock_9.webp":
/*!***********************************************!*\
  !*** ./public/assets/images/time_lock_9.webp ***!
  \***********************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

"use strict";
module.exports = __webpack_require__.p + "assets/images/time_lock_9.webp";

/***/ }),

/***/ "./public/assets/images/time_lock_huoyue.webp":
/*!****************************************************!*\
  !*** ./public/assets/images/time_lock_huoyue.webp ***!
  \****************************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

"use strict";
module.exports = __webpack_require__.p + "assets/images/time_lock_huoyue.webp";

/***/ }),

/***/ "./public/assets/images/time_lock_protect.webp":
/*!*****************************************************!*\
  !*** ./public/assets/images/time_lock_protect.webp ***!
  \*****************************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

"use strict";
module.exports = __webpack_require__.p + "assets/images/time_lock_protect.webp";

/***/ }),

/***/ "./src/api/equipment.js":
/*!******************************!*\
  !*** ./src/api/equipment.js ***!
  \******************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   equipmentApi: function() { return /* binding */ equipmentApi; }
/* harmony export */ });
/* harmony import */ var _utils_request__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @/utils/request */ "./src/utils/request.js");


/**
 * 装备相关API
 */
const equipmentApi = {
  /**
   * 获取装备列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getEquipmentList(params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/equipment/', params);
  },
  /**
   * 获取装备详情
   * @param {string} equipSn - 装备序列号
   * @param {Object} params - 额外参数（如年月）
   * @returns {Promise}
   */
  getEquipmentDetail(equipSn, params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get(`/equipment/${equipSn}`, params);
  },
  /**
   * 寻找装备市场锚点
   * @param {Object} data - 装备数据和查询参数
   * @returns {Promise}
   */
  findEquipmentAnchors(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/equipment/anchors', data);
  },
  /**
   * 获取装备估价
   * @param {Object} data - 装备数据和估价参数
   * @returns {Promise}
   */
  getEquipmentValuation(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/equipment/valuation', data);
  },
  /**
   * 通过装备SN查找锚点（便捷接口）
   * @param {string} equipSn - 装备序列号
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  findAnchorsBySn(equipSn, params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get(`/equipment/anchors/${equipSn}`, params);
  },
  /**
   * 通过装备SN获取估价（便捷接口）
   * @param {string} equipSn - 装备序列号
   * @param {Object} params - 估价参数
   * @returns {Promise}
   */
  getValuationBySn(equipSn, params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get(`/equipment/valuation/${equipSn}`, params);
  },
  /**
   * 健康检查
   * @returns {Promise}
   */
  healthCheck() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/equipment/health');
  },
  /**
   * 批量装备估价
   * @param {Object} data - 装备列表和估价参数
   * @returns {Promise}
   */
  batchEquipmentValuation(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/equipment/batch-valuation', data);
  },
  /**
   * 提取装备特征
   * @param {Object} data - 装备数据和参数
   * @returns {Promise}
   */
  extractFeatures(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/equipment/extract-features', data);
  },
  /**
   * 批量提取装备特征
   * @param {Object} data - 装备列表和参数
   * @returns {Promise}
   */
  extractFeaturesBatch(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/equipment/extract-features-batch', data);
  },
  /**
   * 获取支持的kindid列表
   * @returns {Promise}
   */
  getSupportedKindids() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/equipment/supported-kindids');
  },
  /**
   * 获取指定kindid的提取器信息
   * @param {number} kindid - 装备类型ID
   * @returns {Promise}
   */
  getExtractorInfo(kindid) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get(`/equipment/extractor-info/${kindid}`);
  },
  /**
   * 删除装备
   * @param {string} equipSn - 装备序列号
   * @param {Object} params - 额外参数（如年月）
   * @returns {Promise}
   */
  deleteEquipment(equipSn, params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.delete(`/equipment/${equipSn}`, params);
  },
  /**
   * 获取灵饰数据
   * @returns {Promise}
   */
  getLingshiConfig() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/equipment/lingshi-config');
  },
  /**
   * 获取武器数据
   * @returns {Promise}
   */
  getWeaponConfig() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/equipment/weapon-config');
  },
  /**
   * 获取召唤兽装备数据
   * @returns {Promise}
   */
  getPetEquipConfig() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/equipment/pet-equip-config');
  },
  /**
   * 获取装备数据
   * @returns {Promise}
   */
  getEquipConfig() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/equipment/equip-config');
  },
  /**
   * 标记装备为异常
   * @param {Object} data - 装备数据和标记原因
   * @returns {Promise}
   */
  markEquipmentAsAbnormal(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/equipment/mark-abnormal', data);
  },
  /**
   * 获取异常装备列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getAbnormalEquipmentList(params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/equipment/abnormal', params);
  },
  /**
   * 更新异常装备状态
   * @param {string} equipSn - 装备序列号
   * @param {Object} data - 更新数据
   * @returns {Promise}
   */
  updateAbnormalEquipmentStatus(equipSn, data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.put(`/equipment/abnormal/${equipSn}`, data);
  },
  /**
   * 删除异常装备记录
   * @param {string} equipSn - 装备序列号
   * @returns {Promise}
   */
  deleteAbnormalEquipment(equipSn) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.delete(`/equipment/abnormal/${equipSn}`);
  }
};

/***/ }),

/***/ "./src/api/index.js":
/*!**************************!*\
  !*** ./src/api/index.js ***!
  \**************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   equipmentApi: function() { return /* reexport safe */ _equipment__WEBPACK_IMPORTED_MODULE_1__.equipmentApi; },
/* harmony export */   petApi: function() { return /* reexport safe */ _pet__WEBPACK_IMPORTED_MODULE_2__.petApi; },
/* harmony export */   roleApi: function() { return /* reexport safe */ _role__WEBPACK_IMPORTED_MODULE_0__.roleApi; },
/* harmony export */   spiderApi: function() { return /* reexport safe */ _spider__WEBPACK_IMPORTED_MODULE_3__.spiderApi; },
/* harmony export */   systemApi: function() { return /* reexport safe */ _system__WEBPACK_IMPORTED_MODULE_4__.systemApi; }
/* harmony export */ });
/* harmony import */ var _role__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./role */ "./src/api/role.js");
/* harmony import */ var _equipment__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./equipment */ "./src/api/equipment.js");
/* harmony import */ var _pet__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./pet */ "./src/api/pet.js");
/* harmony import */ var _spider__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./spider */ "./src/api/spider.js");
/* harmony import */ var _system__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./system */ "./src/api/system.js");
// 统一API入口






// 也可以作为默认导出





/* harmony default export */ __webpack_exports__["default"] = ({
  role: _role__WEBPACK_IMPORTED_MODULE_0__.roleApi,
  equipment: _equipment__WEBPACK_IMPORTED_MODULE_1__.equipmentApi,
  pet: _pet__WEBPACK_IMPORTED_MODULE_2__.petApi,
  spider: _spider__WEBPACK_IMPORTED_MODULE_3__.spiderApi,
  system: _system__WEBPACK_IMPORTED_MODULE_4__.systemApi
});

/***/ }),

/***/ "./src/api/pet.js":
/*!************************!*\
  !*** ./src/api/pet.js ***!
  \************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   petApi: function() { return /* binding */ petApi; }
/* harmony export */ });
/* harmony import */ var _utils_request__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @/utils/request */ "./src/utils/request.js");


/**
 * 召唤兽相关API
 */
const petApi = {
  /**
   * 获取召唤兽列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getPetList(params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/pet/', params);
  },
  /**
   * 获取召唤兽详情
   * @param {string} petSn - 召唤兽序列号
   * @param {Object} params - 额外参数（如年月）
   * @returns {Promise}
   */
  getPetDetail(petSn, params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get(`/pet/${petSn}`, params);
  },
  /**
   * 寻找召唤兽市场锚点
   * @param {Object} data - 召唤兽数据和查询参数
   * @returns {Promise}
   */
  findPetAnchors(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/pet/anchors', data);
  },
  /**
   * 获取召唤兽估价
   * @param {Object} data - 召唤兽数据和估价参数
   * @returns {Promise}
   */
  getPetValuation(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/pet/valuation', data);
  },
  /**
   * 批量召唤兽估价
   * @param {Object} data - 召唤兽列表和估价参数
   * @returns {Promise}
   */
  batchPetValuation(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/pet/batch-valuation', data);
  },
  /**
   * 通过召唤兽SN查找锚点（便捷接口）
   * @param {string} petSn - 召唤兽序列号
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  findAnchorsBySn(petSn, params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get(`/pet/anchors/${petSn}`, params);
  },
  /**
   * 通过召唤兽SN获取估价（便捷接口）
   * @param {string} petSn - 召唤兽序列号
   * @param {Object} params - 估价参数
   * @returns {Promise}
   */
  getValuationBySn(petSn, params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get(`/pet/valuation/${petSn}`, params);
  },
  /**
  * 更新召唤兽装备价格
  * @param {Object} data - 召唤兽数据和估价参数
  * @returns {Promise}
  */
  updatePetEquipmentsPrice(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/pet/update-equipments-price', data);
  },
  /**
   * 健康检查
   * @returns {Promise}
   */
  healthCheck() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/pet/health');
  },
  /**
   * 获取当前年月携带装备但未估价的召唤兽数量
   * @param {Object} params - 查询参数（年月）
   * @returns {Promise}
   */
  getUnvaluedPetsCount(params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/pet/unvalued-count', params);
  },
  /**
   * 批量更新未估价召唤兽的装备价格
   * @param {Object} data - 请求数据（年月）
   * @returns {Promise}
   */
  batchUpdateUnvaluedPets(data = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/pet/batch-update-unvalued', data);
  },
  /**
   * 获取任务状态
   * @param {string} taskId - 任务ID
   * @returns {Promise}
   */
  getTaskStatus(taskId) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get(`/pet/task-status/${taskId}`);
  },
  /**
   * 获取活跃任务列表
   * @returns {Promise}
   */
  getActiveTasks() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/pet/active-tasks');
  },
  /**
   * 停止任务
   * @param {string} taskId - 任务ID
   * @returns {Promise}
   */
  stopTask(taskId) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post(`/pet/stop-task/${taskId}`);
  },
  /**
   * 删除召唤兽
   * @param {string} petSn - 召唤兽序列号
   * @param {Object} params - 查询参数（年月）
   * @returns {Promise}
   */
  deletePet(petSn, params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.delete(`/pet/${petSn}`, params);
  },
  /**
   * 通过equip_sn获取召唤兽详情
   * @param {string} year - 年份
   * @param {string} month - 月份
   * @param {string} equipSn - 召唤兽序列号
   * @returns {Promise}
   */
  getPetByEquipSn(year, month, equipSn) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get(`/pet/${year}/${month}/${equipSn}`);
  }
};

/***/ }),

/***/ "./src/api/role.js":
/*!*************************!*\
  !*** ./src/api/role.js ***!
  \*************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   roleApi: function() { return /* binding */ roleApi; }
/* harmony export */ });
/* harmony import */ var _utils_request__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @/utils/request */ "./src/utils/request.js");


/**
 * 角色相关API
 */
const roleApi = {
  /**
   * 获取角色列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.page_size - 每页大小
   * @param {number} params.year - 年份
   * @param {number} params.month - 月份
   * @param {number} params.level_min - 最低等级
   * @param {number} params.level_max - 最高等级
   * @param {number} params.equip_num - 装备数量限制
   * @param {number} params.pet_num - 召唤兽数量限制
   * @param {number} params.pet_num_level - 召唤兽等级限制
   * @param {string} params.sort_by - 排序字段
   * @param {string} params.sort_order - 排序方向
   * @param {string} params.role_type - 角色类型，'normal' 表示正常角色，'empty' 表示空号角色
   * @returns {Promise}
   */
  getRoleApi(params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/role/', params);
  },
  /**
   * 获取角色详情
   * @param {string} equipId - 角色装备ID
   * @param {Object} params - 额外参数（如年月）
   * @returns {Promise}
   */
  getRoleDetail(equipId, params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get(`/role/${equipId}`, params);
  },
  /**
   * 删除角色
   * @param {string} eid - 角色订单号
   * @param {Object} params - 额外参数（如年月、role_type）
   * @returns {Promise}
   */
  deleteRole(eid, params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.delete(`/role/${eid}`, params);
  },
  /**
   * 切换角色类型（数据迁移）
   * @param {string} eid - 角色订单号
   * @param {Object} params - 查询参数（如年月、role_type/target_role_type）
   * @returns {Promise}
   */
  switchRoleType(eid, params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post(`/role/${eid}/switch-type`, params);
  },
  /**
   * 角色估价
   * @param {Object} params - 估价参数
   * @param {string} params.eid - 角色唯一标识符
   * @param {number} params.year - 年份（可选）
   * @param {number} params.month - 月份（可选）
   * @param {string} params.role_type - 角色类型（可选，默认normal）
   * @param {string} params.strategy - 估价策略（可选，默认fair_value）
   * @param {number} params.similarity_threshold - 相似度阈值（可选，默认0.7）
   * @param {number} params.max_anchors - 最大锚点数量（可选，默认30）
   * @returns {Promise}
   */
  getRoleValuation(params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/role/valuation', params);
  },
  /**
   * 批量角色估价
   * @param {Object} params - 批量估价参数
   * @param {Array} params.eid_list - 角色eid列表
   * @param {number} params.year - 年份（可选）
   * @param {number} params.month - 月份（可选）
   * @param {string} params.role_type - 角色类型（可选，默认normal）
   * @param {string} params.strategy - 估价策略（可选，默认fair_value）
   * @param {number} params.similarity_threshold - 相似度阈值（可选，默认0.7）
   * @param {number} params.max_anchors - 最大锚点数量（可选，默认30）
   * @param {boolean} params.verbose - 是否详细日志（可选，默认false）
   * @returns {Promise}
   */
  batchRoleValuation(params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/role/batch-valuation', params);
  },
  /**
   * 更新角色裸号价格
   * @param {Object} params - 更新参数
   * @param {string} params.eid - 角色唯一标识符
   * @param {number} params.base_price - 裸号价格（分）
   * @param {number} params.year - 年份（可选）
   * @param {number} params.month - 月份（可选）
   * @param {string} params.role_type - 角色类型（可选，默认normal）
   * @returns {Promise}
   */
  updateRoleBasePrice(params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post(`/role/${params.eid}/update-base-price`, params);
  },
  /**
   * 查找相似角色锚点
   * @param {Object} params - 查询参数
   * @param {string} params.eid - 角色唯一标识符
   * @param {number} params.year - 年份
   * @param {number} params.month - 月份
   * @param {string} params.role_type - 角色类型（可选，默认normal）
   * @param {number} params.similarity_threshold - 相似度阈值（可选，默认0.7）
   * @param {number} params.max_anchors - 最大锚点数量（可选，默认30）
   * @returns {Promise}
   */
  findRoleAnchors(params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/role/find-anchors', params);
  },
  /**
   * 健康检查
   * @returns {Promise}
   */
  healthCheck() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/role/health');
  }
};

/***/ }),

/***/ "./src/api/spider.js":
/*!***************************!*\
  !*** ./src/api/spider.js ***!
  \***************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   spiderApi: function() { return /* binding */ spiderApi; }
/* harmony export */ });
/* harmony import */ var _utils_request__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @/utils/request */ "./src/utils/request.js");


/**
 * 爬虫相关API
 */
const spiderApi = {
  /**
   * 获取任务状态
   * @returns {Promise}
   */
  getStatus() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/spider/status');
  },
  /**
   * 获取爬虫配置
   * @returns {Promise}
   */
  getConfig() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/spider/config');
  },
  /**
   * 启动基础爬虫
   * @param {Object} data - 爬虫参数
   * @returns {Promise}
   */
  startBasic(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/spider/basic/start', data);
  },
  /**
   * 启动角色爬虫
   * @param {Object} data - 角色爬虫参数
   * @returns {Promise}
   */
  startRole(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/spider/role/start', data);
  },
  /**
   * 启动装备爬虫
   * @param {Object} data - 装备爬虫参数
   * @returns {Promise}
   */
  startEquip(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/spider/equip/start', data);
  },
  /**
   * 启动召唤兽爬虫
   * @param {Object} data - 召唤兽爬虫参数
   * @returns {Promise}
   */
  startPet(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/spider/pet/start', data);
  },
  /**
   * 启动代理爬虫
   * @param {Object} data - 代理爬虫参数
   * @returns {Promise}
   */
  startProxy(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/spider/proxy/start', data);
  },
  /**
   * 管理代理
   * @param {Object} data - 代理管理参数
   * @returns {Promise}
   */
  manageProxy(data = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/spider/proxy/manage', data);
  },
  /**
   * 停止任务
   * @returns {Promise}
   */
  stopTask() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/spider/task/stop');
  },
  /**
   * 重置任务状态
   * @returns {Promise}
   */
  resetTask() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/spider/task/reset');
  },
  /**
   * 获取任务日志
   * @param {Object} params - 参数
   * @param {number} params.lines - 返回的日志行数，默认100
   * @param {string} params.type - 日志类型 (current/recent)，默认current
   * @returns {Promise}
   */
  getLogs(params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/spider/logs', params);
  },
  /**
   * 从日志文件解析进度信息
   * @param {Object} params - 参数
   * @param {string} params.type - 爬虫类型 (role/equip/pet/proxy)，默认role
   * @returns {Promise}
   */
  getProgress(params = {}) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/spider/progress', params);
  },
  /**
   * 流式获取实时日志
   * @returns {EventSource}
   */
  streamLogs() {
    // 使用完整的URL，确保连接到正确的后端
    const baseURL =  true ? 'http://localhost:5000' : 0;
    return new EventSource(`${baseURL}/api/v1/spider/logs/stream`);
  },
  /**
   * 获取文件列表
   * @returns {Promise}
   */
  getFiles() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/spider/files');
  },
  /**
   * 获取日志文件列表
   * @returns {Promise}
   */
  getLogFiles() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/spider/logs/files');
  },
  /**
   * 下载文件
   * @param {string} filename - 文件名
   * @returns {Promise}
   */
  downloadFile(filename) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.download(`/spider/download/${filename}`, {}, filename);
  },
  /**
   * 启动Playwright收集器
   * @param {Object} data - Playwright收集器参数
   * @param {boolean} data.headless - 是否无头模式
   * @param {string} data.target_url - 目标URL
   * @returns {Promise}
   */
  startPlaywright(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/spider/playwright/start', data);
  },
  /**
   * 检查Cookie状态
   * @returns {Promise}
   */
  checkCookie() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/spider/cookie/check');
  },
  /**
   * 更新Cookie
   * @returns {Promise}
   */
  updateCookies() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/spider/cookie/update');
  },
  /**
   * 解析响应数据
   * @param {Object} data - 解析参数
   * @param {string} data.url - CBG请求的完整URL
   * @param {string} data.response_text - 服务器返回的响应文本
   * @returns {Promise}
   */
  parseResponse(data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post('/spider/parse/response', data);
  }
};

/***/ }),

/***/ "./src/api/system.js":
/*!***************************!*\
  !*** ./src/api/system.js ***!
  \***************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   systemApi: function() { return /* binding */ systemApi; }
/* harmony export */ });
/* harmony import */ var _utils_request__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @/utils/request */ "./src/utils/request.js");


/**
 * 系统相关API
 */
const systemApi = {
  /**
   * 获取系统信息
   * @returns {Promise}
   */
  getSystemInfo() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/system/info');
  },
  /**
   * 获取文件列表
   * @returns {Promise}
   */
  getFiles() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/system/files');
  },
  /**
   * 下载文件
   * @param {string} filename - 文件名
   * @returns {Promise}
   */
  downloadFile(filename) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get(`/system/files/${filename}/download`);
  },
  /**
   * 获取热门服务器列表
   * @returns {Promise} 直接返回服务器分组数组，无包装格式
   */
  getHotServers() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/system/config-file/hot_server_list.json');
  },
  /**
   * 获取限量锦衣祥瑞配置
   * @returns {Promise} 直接返回限量锦衣祥瑞配置
   */
  getLimitedSkinConfig() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/system/config-file/ex_avt_value.jsonc');
  },
  /**
   * 获取所有搜索参数配置
   * @returns {Promise}
   */
  getSearchParams() {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get('/system/config/search-params');
  },
  /**
   * 根据类型获取特定的搜索参数配置
   * @param {string} paramType - 参数类型 (role, equip_normal, equip_lingshi, equip_pet, equip_pet_equip, pet)
   * @returns {Promise}
   */
  getSearchParamByType(paramType) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.get(`/system/config/search-params/${paramType}`);
  },
  /**
   * 更新特定类型的搜索参数配置
   * @param {string} paramType - 参数类型
   * @param {Object} data - 配置数据
   * @returns {Promise}
   */
  updateSearchParam(paramType, data) {
    return _utils_request__WEBPACK_IMPORTED_MODULE_0__.api.post(`/system/config/search-params/${paramType}`, data);
  }
};

/***/ }),

/***/ "./src/chrome-extensions/DevToolsPanel.vue":
/*!*************************************************!*\
  !*** ./src/chrome-extensions/DevToolsPanel.vue ***!
  \*************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _DevToolsPanel_vue_vue_type_template_id_42c7142d_scoped_true__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./DevToolsPanel.vue?vue&type=template&id=42c7142d&scoped=true */ "./src/chrome-extensions/DevToolsPanel.vue?vue&type=template&id=42c7142d&scoped=true");
/* harmony import */ var _DevToolsPanel_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./DevToolsPanel.vue?vue&type=script&lang=js */ "./src/chrome-extensions/DevToolsPanel.vue?vue&type=script&lang=js");
/* harmony import */ var _DevToolsPanel_vue_vue_type_style_index_0_id_42c7142d_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./DevToolsPanel.vue?vue&type=style&index=0&id=42c7142d&scoped=true&lang=css */ "./src/chrome-extensions/DevToolsPanel.vue?vue&type=style&index=0&id=42c7142d&scoped=true&lang=css");
/* harmony import */ var _node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! !../../node_modules/vue-loader/lib/runtime/componentNormalizer.js */ "./node_modules/vue-loader/lib/runtime/componentNormalizer.js");



;


/* normalize component */

var component = (0,_node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_3__["default"])(
  _DevToolsPanel_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__["default"],
  _DevToolsPanel_vue_vue_type_template_id_42c7142d_scoped_true__WEBPACK_IMPORTED_MODULE_0__.render,
  _DevToolsPanel_vue_vue_type_template_id_42c7142d_scoped_true__WEBPACK_IMPORTED_MODULE_0__.staticRenderFns,
  false,
  null,
  "42c7142d",
  null
  
)

/* hot reload */
if (false) // removed by dead control flow
{ var api; }
component.options.__file = "src/chrome-extensions/DevToolsPanel.vue"
/* harmony default export */ __webpack_exports__["default"] = (component.exports);

/***/ }),

/***/ "./src/chrome-extensions/DevToolsPanel.vue?vue&type=script&lang=js":
/*!*************************************************************************!*\
  !*** ./src/chrome-extensions/DevToolsPanel.vue?vue&type=script&lang=js ***!
  \*************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_index_js_vue_loader_options_DevToolsPanel_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib/index.js??clonedRuleSet-1!../../node_modules/vue-loader/lib/index.js??vue-loader-options!./DevToolsPanel.vue?vue&type=script&lang=js */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/chrome-extensions/DevToolsPanel.vue?vue&type=script&lang=js");
 /* harmony default export */ __webpack_exports__["default"] = (_node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_index_js_vue_loader_options_DevToolsPanel_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__["default"]); 

/***/ }),

/***/ "./src/chrome-extensions/DevToolsPanel.vue?vue&type=style&index=0&id=42c7142d&scoped=true&lang=css":
/*!*********************************************************************************************************!*\
  !*** ./src/chrome-extensions/DevToolsPanel.vue?vue&type=style&index=0&id=42c7142d&scoped=true&lang=css ***!
  \*********************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_DevToolsPanel_vue_vue_type_style_index_0_id_42c7142d_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/vue-style-loader/index.js!../../node_modules/css-loader/dist/cjs.js!../../node_modules/vue-loader/lib/loaders/stylePostLoader.js!../../node_modules/vue-loader/lib/index.js??vue-loader-options!./DevToolsPanel.vue?vue&type=style&index=0&id=42c7142d&scoped=true&lang=css */ "./node_modules/vue-style-loader/index.js!./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/chrome-extensions/DevToolsPanel.vue?vue&type=style&index=0&id=42c7142d&scoped=true&lang=css");
/* harmony import */ var _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_DevToolsPanel_vue_vue_type_style_index_0_id_42c7142d_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_DevToolsPanel_vue_vue_type_style_index_0_id_42c7142d_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__);
/* harmony reexport (unknown) */ var __WEBPACK_REEXPORT_OBJECT__ = {};
/* harmony reexport (unknown) */ for(var __WEBPACK_IMPORT_KEY__ in _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_DevToolsPanel_vue_vue_type_style_index_0_id_42c7142d_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__) if(__WEBPACK_IMPORT_KEY__ !== "default") __WEBPACK_REEXPORT_OBJECT__[__WEBPACK_IMPORT_KEY__] = function(key) { return _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_DevToolsPanel_vue_vue_type_style_index_0_id_42c7142d_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__[key]; }.bind(0, __WEBPACK_IMPORT_KEY__)
/* harmony reexport (unknown) */ __webpack_require__.d(__webpack_exports__, __WEBPACK_REEXPORT_OBJECT__);


/***/ }),

/***/ "./src/chrome-extensions/DevToolsPanel.vue?vue&type=template&id=42c7142d&scoped=true":
/*!*******************************************************************************************!*\
  !*** ./src/chrome-extensions/DevToolsPanel.vue?vue&type=template&id=42c7142d&scoped=true ***!
  \*******************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_DevToolsPanel_vue_vue_type_template_id_42c7142d_scoped_true__WEBPACK_IMPORTED_MODULE_0__.render; },
/* harmony export */   staticRenderFns: function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_DevToolsPanel_vue_vue_type_template_id_42c7142d_scoped_true__WEBPACK_IMPORTED_MODULE_0__.staticRenderFns; }
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_DevToolsPanel_vue_vue_type_template_id_42c7142d_scoped_true__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib/index.js??clonedRuleSet-1!../../node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!../../node_modules/vue-loader/lib/index.js??vue-loader-options!./DevToolsPanel.vue?vue&type=template&id=42c7142d&scoped=true */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/chrome-extensions/DevToolsPanel.vue?vue&type=template&id=42c7142d&scoped=true");


/***/ }),

/***/ "./src/chrome-extensions/main.js":
/*!***************************************!*\
  !*** ./src/chrome-extensions/main.js ***!
  \***************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! vue */ "./node_modules/vue/dist/vue.esm.js");
/* harmony import */ var _DevToolsPanel_vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./DevToolsPanel.vue */ "./src/chrome-extensions/DevToolsPanel.vue");
/* harmony import */ var element_ui__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! element-ui */ "./node_modules/element-ui/lib/element-ui.common.js");
/* harmony import */ var element_ui__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(element_ui__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var element_ui_lib_theme_chalk_index_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! element-ui/lib/theme-chalk/index.css */ "./node_modules/element-ui/lib/theme-chalk/index.css");
/* harmony import */ var element_ui_lib_theme_chalk_index_css__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(element_ui_lib_theme_chalk_index_css__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _api__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../api */ "./src/api/index.js");





vue__WEBPACK_IMPORTED_MODULE_4__["default"].config.productionTip = false;
vue__WEBPACK_IMPORTED_MODULE_4__["default"].prototype.$api = _api__WEBPACK_IMPORTED_MODULE_3__["default"];
// 使用Element UI
vue__WEBPACK_IMPORTED_MODULE_4__["default"].use((element_ui__WEBPACK_IMPORTED_MODULE_1___default()), {
  size: 'mini'
});

// 创建Vue应用
new vue__WEBPACK_IMPORTED_MODULE_4__["default"]({
  render: h => h(_DevToolsPanel_vue__WEBPACK_IMPORTED_MODULE_0__["default"])
}).$mount('#app');

/***/ }),

/***/ "./src/components/EquipmentImage/EquipmentDesc.vue":
/*!*********************************************************!*\
  !*** ./src/components/EquipmentImage/EquipmentDesc.vue ***!
  \*********************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _EquipmentDesc_vue_vue_type_template_id_26200cad_scoped_true__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./EquipmentDesc.vue?vue&type=template&id=26200cad&scoped=true */ "./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=template&id=26200cad&scoped=true");
/* harmony import */ var _EquipmentDesc_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./EquipmentDesc.vue?vue&type=script&lang=js */ "./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=script&lang=js");
/* harmony import */ var _EquipmentDesc_vue_vue_type_style_index_0_id_26200cad_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./EquipmentDesc.vue?vue&type=style&index=0&id=26200cad&scoped=true&lang=css */ "./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=style&index=0&id=26200cad&scoped=true&lang=css");
/* harmony import */ var _node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! !../../../node_modules/vue-loader/lib/runtime/componentNormalizer.js */ "./node_modules/vue-loader/lib/runtime/componentNormalizer.js");



;


/* normalize component */

var component = (0,_node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_3__["default"])(
  _EquipmentDesc_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__["default"],
  _EquipmentDesc_vue_vue_type_template_id_26200cad_scoped_true__WEBPACK_IMPORTED_MODULE_0__.render,
  _EquipmentDesc_vue_vue_type_template_id_26200cad_scoped_true__WEBPACK_IMPORTED_MODULE_0__.staticRenderFns,
  false,
  null,
  "26200cad",
  null
  
)

/* hot reload */
if (false) // removed by dead control flow
{ var api; }
component.options.__file = "src/components/EquipmentImage/EquipmentDesc.vue"
/* harmony default export */ __webpack_exports__["default"] = (component.exports);

/***/ }),

/***/ "./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=script&lang=js":
/*!*********************************************************************************!*\
  !*** ./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=script&lang=js ***!
  \*********************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentDesc_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js??clonedRuleSet-1!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./EquipmentDesc.vue?vue&type=script&lang=js */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=script&lang=js");
 /* harmony default export */ __webpack_exports__["default"] = (_node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentDesc_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__["default"]); 

/***/ }),

/***/ "./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=style&index=0&id=26200cad&scoped=true&lang=css":
/*!*****************************************************************************************************************!*\
  !*** ./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=style&index=0&id=26200cad&scoped=true&lang=css ***!
  \*****************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentDesc_vue_vue_type_style_index_0_id_26200cad_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/vue-style-loader/index.js!../../../node_modules/css-loader/dist/cjs.js!../../../node_modules/vue-loader/lib/loaders/stylePostLoader.js!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./EquipmentDesc.vue?vue&type=style&index=0&id=26200cad&scoped=true&lang=css */ "./node_modules/vue-style-loader/index.js!./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=style&index=0&id=26200cad&scoped=true&lang=css");
/* harmony import */ var _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentDesc_vue_vue_type_style_index_0_id_26200cad_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentDesc_vue_vue_type_style_index_0_id_26200cad_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__);
/* harmony reexport (unknown) */ var __WEBPACK_REEXPORT_OBJECT__ = {};
/* harmony reexport (unknown) */ for(var __WEBPACK_IMPORT_KEY__ in _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentDesc_vue_vue_type_style_index_0_id_26200cad_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__) if(__WEBPACK_IMPORT_KEY__ !== "default") __WEBPACK_REEXPORT_OBJECT__[__WEBPACK_IMPORT_KEY__] = function(key) { return _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentDesc_vue_vue_type_style_index_0_id_26200cad_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__[key]; }.bind(0, __WEBPACK_IMPORT_KEY__)
/* harmony reexport (unknown) */ __webpack_require__.d(__webpack_exports__, __WEBPACK_REEXPORT_OBJECT__);


/***/ }),

/***/ "./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=template&id=26200cad&scoped=true":
/*!***************************************************************************************************!*\
  !*** ./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=template&id=26200cad&scoped=true ***!
  \***************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentDesc_vue_vue_type_template_id_26200cad_scoped_true__WEBPACK_IMPORTED_MODULE_0__.render; },
/* harmony export */   staticRenderFns: function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentDesc_vue_vue_type_template_id_26200cad_scoped_true__WEBPACK_IMPORTED_MODULE_0__.staticRenderFns; }
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentDesc_vue_vue_type_template_id_26200cad_scoped_true__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js??clonedRuleSet-1!../../../node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./EquipmentDesc.vue?vue&type=template&id=26200cad&scoped=true */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentDesc.vue?vue&type=template&id=26200cad&scoped=true");


/***/ }),

/***/ "./src/components/EquipmentImage/EquipmentImage.vue":
/*!**********************************************************!*\
  !*** ./src/components/EquipmentImage/EquipmentImage.vue ***!
  \**********************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _EquipmentImage_vue_vue_type_template_id_13caaaef_scoped_true__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./EquipmentImage.vue?vue&type=template&id=13caaaef&scoped=true */ "./src/components/EquipmentImage/EquipmentImage.vue?vue&type=template&id=13caaaef&scoped=true");
/* harmony import */ var _EquipmentImage_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./EquipmentImage.vue?vue&type=script&lang=js */ "./src/components/EquipmentImage/EquipmentImage.vue?vue&type=script&lang=js");
/* harmony import */ var _EquipmentImage_vue_vue_type_style_index_0_id_13caaaef_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./EquipmentImage.vue?vue&type=style&index=0&id=13caaaef&scoped=true&lang=css */ "./src/components/EquipmentImage/EquipmentImage.vue?vue&type=style&index=0&id=13caaaef&scoped=true&lang=css");
/* harmony import */ var _node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! !../../../node_modules/vue-loader/lib/runtime/componentNormalizer.js */ "./node_modules/vue-loader/lib/runtime/componentNormalizer.js");



;


/* normalize component */

var component = (0,_node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_3__["default"])(
  _EquipmentImage_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__["default"],
  _EquipmentImage_vue_vue_type_template_id_13caaaef_scoped_true__WEBPACK_IMPORTED_MODULE_0__.render,
  _EquipmentImage_vue_vue_type_template_id_13caaaef_scoped_true__WEBPACK_IMPORTED_MODULE_0__.staticRenderFns,
  false,
  null,
  "13caaaef",
  null
  
)

/* hot reload */
if (false) // removed by dead control flow
{ var api; }
component.options.__file = "src/components/EquipmentImage/EquipmentImage.vue"
/* harmony default export */ __webpack_exports__["default"] = (component.exports);

/***/ }),

/***/ "./src/components/EquipmentImage/EquipmentImage.vue?vue&type=script&lang=js":
/*!**********************************************************************************!*\
  !*** ./src/components/EquipmentImage/EquipmentImage.vue?vue&type=script&lang=js ***!
  \**********************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentImage_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js??clonedRuleSet-1!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./EquipmentImage.vue?vue&type=script&lang=js */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentImage.vue?vue&type=script&lang=js");
 /* harmony default export */ __webpack_exports__["default"] = (_node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentImage_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__["default"]); 

/***/ }),

/***/ "./src/components/EquipmentImage/EquipmentImage.vue?vue&type=style&index=0&id=13caaaef&scoped=true&lang=css":
/*!******************************************************************************************************************!*\
  !*** ./src/components/EquipmentImage/EquipmentImage.vue?vue&type=style&index=0&id=13caaaef&scoped=true&lang=css ***!
  \******************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentImage_vue_vue_type_style_index_0_id_13caaaef_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/vue-style-loader/index.js!../../../node_modules/css-loader/dist/cjs.js!../../../node_modules/vue-loader/lib/loaders/stylePostLoader.js!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./EquipmentImage.vue?vue&type=style&index=0&id=13caaaef&scoped=true&lang=css */ "./node_modules/vue-style-loader/index.js!./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentImage.vue?vue&type=style&index=0&id=13caaaef&scoped=true&lang=css");
/* harmony import */ var _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentImage_vue_vue_type_style_index_0_id_13caaaef_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentImage_vue_vue_type_style_index_0_id_13caaaef_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__);
/* harmony reexport (unknown) */ var __WEBPACK_REEXPORT_OBJECT__ = {};
/* harmony reexport (unknown) */ for(var __WEBPACK_IMPORT_KEY__ in _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentImage_vue_vue_type_style_index_0_id_13caaaef_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__) if(__WEBPACK_IMPORT_KEY__ !== "default") __WEBPACK_REEXPORT_OBJECT__[__WEBPACK_IMPORT_KEY__] = function(key) { return _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentImage_vue_vue_type_style_index_0_id_13caaaef_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__[key]; }.bind(0, __WEBPACK_IMPORT_KEY__)
/* harmony reexport (unknown) */ __webpack_require__.d(__webpack_exports__, __WEBPACK_REEXPORT_OBJECT__);


/***/ }),

/***/ "./src/components/EquipmentImage/EquipmentImage.vue?vue&type=template&id=13caaaef&scoped=true":
/*!****************************************************************************************************!*\
  !*** ./src/components/EquipmentImage/EquipmentImage.vue?vue&type=template&id=13caaaef&scoped=true ***!
  \****************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentImage_vue_vue_type_template_id_13caaaef_scoped_true__WEBPACK_IMPORTED_MODULE_0__.render; },
/* harmony export */   staticRenderFns: function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentImage_vue_vue_type_template_id_13caaaef_scoped_true__WEBPACK_IMPORTED_MODULE_0__.staticRenderFns; }
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_EquipmentImage_vue_vue_type_template_id_13caaaef_scoped_true__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js??clonedRuleSet-1!../../../node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./EquipmentImage.vue?vue&type=template&id=13caaaef&scoped=true */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/EquipmentImage/EquipmentImage.vue?vue&type=template&id=13caaaef&scoped=true");


/***/ }),

/***/ "./src/components/RoleInfo/ItemPopover.vue":
/*!*************************************************!*\
  !*** ./src/components/RoleInfo/ItemPopover.vue ***!
  \*************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _ItemPopover_vue_vue_type_template_id_641ba552__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./ItemPopover.vue?vue&type=template&id=641ba552 */ "./src/components/RoleInfo/ItemPopover.vue?vue&type=template&id=641ba552");
/* harmony import */ var _ItemPopover_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./ItemPopover.vue?vue&type=script&lang=js */ "./src/components/RoleInfo/ItemPopover.vue?vue&type=script&lang=js");
/* harmony import */ var _node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! !../../../node_modules/vue-loader/lib/runtime/componentNormalizer.js */ "./node_modules/vue-loader/lib/runtime/componentNormalizer.js");





/* normalize component */
;
var component = (0,_node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_2__["default"])(
  _ItemPopover_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__["default"],
  _ItemPopover_vue_vue_type_template_id_641ba552__WEBPACK_IMPORTED_MODULE_0__.render,
  _ItemPopover_vue_vue_type_template_id_641ba552__WEBPACK_IMPORTED_MODULE_0__.staticRenderFns,
  false,
  null,
  null,
  null
  
)

/* hot reload */
if (false) // removed by dead control flow
{ var api; }
component.options.__file = "src/components/RoleInfo/ItemPopover.vue"
/* harmony default export */ __webpack_exports__["default"] = (component.exports);

/***/ }),

/***/ "./src/components/RoleInfo/ItemPopover.vue?vue&type=script&lang=js":
/*!*************************************************************************!*\
  !*** ./src/components/RoleInfo/ItemPopover.vue?vue&type=script&lang=js ***!
  \*************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_index_js_vue_loader_options_ItemPopover_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js??clonedRuleSet-1!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./ItemPopover.vue?vue&type=script&lang=js */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/ItemPopover.vue?vue&type=script&lang=js");
 /* harmony default export */ __webpack_exports__["default"] = (_node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_index_js_vue_loader_options_ItemPopover_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__["default"]); 

/***/ }),

/***/ "./src/components/RoleInfo/ItemPopover.vue?vue&type=template&id=641ba552":
/*!*******************************************************************************!*\
  !*** ./src/components/RoleInfo/ItemPopover.vue?vue&type=template&id=641ba552 ***!
  \*******************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_ItemPopover_vue_vue_type_template_id_641ba552__WEBPACK_IMPORTED_MODULE_0__.render; },
/* harmony export */   staticRenderFns: function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_ItemPopover_vue_vue_type_template_id_641ba552__WEBPACK_IMPORTED_MODULE_0__.staticRenderFns; }
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_ItemPopover_vue_vue_type_template_id_641ba552__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js??clonedRuleSet-1!../../../node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./ItemPopover.vue?vue&type=template&id=641ba552 */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/ItemPopover.vue?vue&type=template&id=641ba552");


/***/ }),

/***/ "./src/components/RoleInfo/PetDetail.vue":
/*!***********************************************!*\
  !*** ./src/components/RoleInfo/PetDetail.vue ***!
  \***********************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _PetDetail_vue_vue_type_template_id_67c8d056__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./PetDetail.vue?vue&type=template&id=67c8d056 */ "./src/components/RoleInfo/PetDetail.vue?vue&type=template&id=67c8d056");
/* harmony import */ var _PetDetail_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./PetDetail.vue?vue&type=script&lang=js */ "./src/components/RoleInfo/PetDetail.vue?vue&type=script&lang=js");
/* harmony import */ var _node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! !../../../node_modules/vue-loader/lib/runtime/componentNormalizer.js */ "./node_modules/vue-loader/lib/runtime/componentNormalizer.js");





/* normalize component */
;
var component = (0,_node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_2__["default"])(
  _PetDetail_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__["default"],
  _PetDetail_vue_vue_type_template_id_67c8d056__WEBPACK_IMPORTED_MODULE_0__.render,
  _PetDetail_vue_vue_type_template_id_67c8d056__WEBPACK_IMPORTED_MODULE_0__.staticRenderFns,
  false,
  null,
  null,
  null
  
)

/* hot reload */
if (false) // removed by dead control flow
{ var api; }
component.options.__file = "src/components/RoleInfo/PetDetail.vue"
/* harmony default export */ __webpack_exports__["default"] = (component.exports);

/***/ }),

/***/ "./src/components/RoleInfo/PetDetail.vue?vue&type=script&lang=js":
/*!***********************************************************************!*\
  !*** ./src/components/RoleInfo/PetDetail.vue?vue&type=script&lang=js ***!
  \***********************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_index_js_vue_loader_options_PetDetail_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js??clonedRuleSet-1!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./PetDetail.vue?vue&type=script&lang=js */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/PetDetail.vue?vue&type=script&lang=js");
 /* harmony default export */ __webpack_exports__["default"] = (_node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_index_js_vue_loader_options_PetDetail_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__["default"]); 

/***/ }),

/***/ "./src/components/RoleInfo/PetDetail.vue?vue&type=template&id=67c8d056":
/*!*****************************************************************************!*\
  !*** ./src/components/RoleInfo/PetDetail.vue?vue&type=template&id=67c8d056 ***!
  \*****************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_PetDetail_vue_vue_type_template_id_67c8d056__WEBPACK_IMPORTED_MODULE_0__.render; },
/* harmony export */   staticRenderFns: function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_PetDetail_vue_vue_type_template_id_67c8d056__WEBPACK_IMPORTED_MODULE_0__.staticRenderFns; }
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_PetDetail_vue_vue_type_template_id_67c8d056__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js??clonedRuleSet-1!../../../node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./PetDetail.vue?vue&type=template&id=67c8d056 */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/PetDetail.vue?vue&type=template&id=67c8d056");


/***/ }),

/***/ "./src/components/RoleInfo/RoleImage.vue":
/*!***********************************************!*\
  !*** ./src/components/RoleInfo/RoleImage.vue ***!
  \***********************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _RoleImage_vue_vue_type_template_id_8c1934ec_scoped_true__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./RoleImage.vue?vue&type=template&id=8c1934ec&scoped=true */ "./src/components/RoleInfo/RoleImage.vue?vue&type=template&id=8c1934ec&scoped=true");
/* harmony import */ var _RoleImage_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./RoleImage.vue?vue&type=script&lang=js */ "./src/components/RoleInfo/RoleImage.vue?vue&type=script&lang=js");
/* harmony import */ var _RoleImage_vue_vue_type_style_index_0_id_8c1934ec_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./RoleImage.vue?vue&type=style&index=0&id=8c1934ec&scoped=true&lang=css */ "./src/components/RoleInfo/RoleImage.vue?vue&type=style&index=0&id=8c1934ec&scoped=true&lang=css");
/* harmony import */ var _node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! !../../../node_modules/vue-loader/lib/runtime/componentNormalizer.js */ "./node_modules/vue-loader/lib/runtime/componentNormalizer.js");



;


/* normalize component */

var component = (0,_node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_3__["default"])(
  _RoleImage_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__["default"],
  _RoleImage_vue_vue_type_template_id_8c1934ec_scoped_true__WEBPACK_IMPORTED_MODULE_0__.render,
  _RoleImage_vue_vue_type_template_id_8c1934ec_scoped_true__WEBPACK_IMPORTED_MODULE_0__.staticRenderFns,
  false,
  null,
  "8c1934ec",
  null
  
)

/* hot reload */
if (false) // removed by dead control flow
{ var api; }
component.options.__file = "src/components/RoleInfo/RoleImage.vue"
/* harmony default export */ __webpack_exports__["default"] = (component.exports);

/***/ }),

/***/ "./src/components/RoleInfo/RoleImage.vue?vue&type=script&lang=js":
/*!***********************************************************************!*\
  !*** ./src/components/RoleInfo/RoleImage.vue?vue&type=script&lang=js ***!
  \***********************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_index_js_vue_loader_options_RoleImage_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js??clonedRuleSet-1!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./RoleImage.vue?vue&type=script&lang=js */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/RoleImage.vue?vue&type=script&lang=js");
 /* harmony default export */ __webpack_exports__["default"] = (_node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_index_js_vue_loader_options_RoleImage_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__["default"]); 

/***/ }),

/***/ "./src/components/RoleInfo/RoleImage.vue?vue&type=style&index=0&id=8c1934ec&scoped=true&lang=css":
/*!*******************************************************************************************************!*\
  !*** ./src/components/RoleInfo/RoleImage.vue?vue&type=style&index=0&id=8c1934ec&scoped=true&lang=css ***!
  \*******************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_RoleImage_vue_vue_type_style_index_0_id_8c1934ec_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/vue-style-loader/index.js!../../../node_modules/css-loader/dist/cjs.js!../../../node_modules/vue-loader/lib/loaders/stylePostLoader.js!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./RoleImage.vue?vue&type=style&index=0&id=8c1934ec&scoped=true&lang=css */ "./node_modules/vue-style-loader/index.js!./node_modules/css-loader/dist/cjs.js!./node_modules/vue-loader/lib/loaders/stylePostLoader.js!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/RoleImage.vue?vue&type=style&index=0&id=8c1934ec&scoped=true&lang=css");
/* harmony import */ var _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_RoleImage_vue_vue_type_style_index_0_id_8c1934ec_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_RoleImage_vue_vue_type_style_index_0_id_8c1934ec_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__);
/* harmony reexport (unknown) */ var __WEBPACK_REEXPORT_OBJECT__ = {};
/* harmony reexport (unknown) */ for(var __WEBPACK_IMPORT_KEY__ in _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_RoleImage_vue_vue_type_style_index_0_id_8c1934ec_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__) if(__WEBPACK_IMPORT_KEY__ !== "default") __WEBPACK_REEXPORT_OBJECT__[__WEBPACK_IMPORT_KEY__] = function(key) { return _node_modules_vue_style_loader_index_js_node_modules_css_loader_dist_cjs_js_node_modules_vue_loader_lib_loaders_stylePostLoader_js_node_modules_vue_loader_lib_index_js_vue_loader_options_RoleImage_vue_vue_type_style_index_0_id_8c1934ec_scoped_true_lang_css__WEBPACK_IMPORTED_MODULE_0__[key]; }.bind(0, __WEBPACK_IMPORT_KEY__)
/* harmony reexport (unknown) */ __webpack_require__.d(__webpack_exports__, __WEBPACK_REEXPORT_OBJECT__);


/***/ }),

/***/ "./src/components/RoleInfo/RoleImage.vue?vue&type=template&id=8c1934ec&scoped=true":
/*!*****************************************************************************************!*\
  !*** ./src/components/RoleInfo/RoleImage.vue?vue&type=template&id=8c1934ec&scoped=true ***!
  \*****************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_RoleImage_vue_vue_type_template_id_8c1934ec_scoped_true__WEBPACK_IMPORTED_MODULE_0__.render; },
/* harmony export */   staticRenderFns: function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_RoleImage_vue_vue_type_template_id_8c1934ec_scoped_true__WEBPACK_IMPORTED_MODULE_0__.staticRenderFns; }
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_1_node_modules_vue_loader_lib_loaders_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_lib_index_js_vue_loader_options_RoleImage_vue_vue_type_template_id_8c1934ec_scoped_true__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js??clonedRuleSet-1!../../../node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!../../../node_modules/vue-loader/lib/index.js??vue-loader-options!./RoleImage.vue?vue&type=template&id=8c1934ec&scoped=true */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-1!./node_modules/vue-loader/lib/loaders/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/lib/index.js??vue-loader-options!./src/components/RoleInfo/RoleImage.vue?vue&type=template&id=8c1934ec&scoped=true");


/***/ }),

/***/ "./src/utils/mixins/commonMixin.js":
/*!*****************************************!*\
  !*** ./src/utils/mixins/commonMixin.js ***!
  \*****************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   commonMixin: function() { return /* binding */ commonMixin; }
/* harmony export */ });
/**
 * 通用方法Mixin
 */
const commonMixin = {
  methods: {
    gen_dynamic_tags(str) {
      if (str) {
        return window.gen_dynamic_tags(JSON.parse(str));
      }
      return '';
    },
    gen_highlight(str) {
      if (str) {
        return window.gen_highlight(JSON.parse(str));
      }
      return '';
    },
    /**
     * 处理分页大小变化
     * @param {number} val - 新的分页大小
     */
    handleSizeChange(val) {
      this.pagination.page_size = val;
      this.pagination.page = 1;
      this.fetchData();
    },
    /**
     * 处理页码变化
     * @param {number} newPage - 新的页码
     */
    handlePageChange(newPage) {
      this.pagination.page = newPage;
      this.fetchData();
    },
    /**
     * 处理排序变化
     * @param {Object} sortInfo - 排序信息
     * @param {string} sortInfo.prop - 排序字段
     * @param {string} sortInfo.order - 排序方向
     */
    handleSortChange({
      prop,
      order
    }) {
      this.filters.sort_by = prop;
      this.filters.sort_order = order === 'ascending' ? 'asc' : 'desc';
      this.fetchData();
    },
    /**
     * 获取相似度标签类型
     * @param {number} similarity - 相似度值
     * @returns {string} 标签类型
     */
    getSimilarityTagType(similarity) {
      if (similarity >= 0.9) return 'success';
      if (similarity >= 0.8) return 'warning';
      if (similarity >= 0.7) return 'info';
      return 'danger';
    },
    /**
     * 格式化特性
     * @param {string} texing - 特性JSON字符串
     * @returns {string} 特性名称
     */
    formatTexing(texing) {
      if (!texing) return '';
      try {
        const texingObj = JSON.parse(texing);
        return texingObj.name || '';
      } catch (e) {
        return '';
      }
    },
    /**
     * 格式化日期
     * @param {number} timestamp - 时间戳
     * @returns {string} 格式化后的日期
     */
    formatDate(timestamp) {
      if (!timestamp) return '-';
      const date = new Date(timestamp * 1000);
      return date.toLocaleString('zh-CN');
    },
    /**
     * 获取带颜色的数字
     * @param {number} val - 数字
     * @param {Array} range - 范围 [min, max]
     * @returns {string} 带颜色的数字HTML
     */
    getColorNumber(val, range = [0, 1]) {
      if (!val) return '-';
      val = +val;
      const [min, max] = range;
      if (!val || val < min || val > max) {
        return '-';
      }
      var cls = 'number-low';
      const stepRange = max - min;
      if (val >= min && val < min + stepRange * 0.25) {
        cls = 'number-low';
      } else if (val >= min + stepRange * 0.25 && val < min + stepRange * 0.5) {
        cls = 'number-medium';
      } else if (val >= min + stepRange * 0.5 && val < min + stepRange * 0.75) {
        cls = 'number-high';
      } else if (val >= min + stepRange * 0.75 && val <= max) {
        cls = 'number-perfect';
      }
      return `<span class="${cls}">${val}</span>`;
    },
    /**
     * 格式化装备价格
     * @param {number} price - 价格（分为单位）
     * @returns {string} 格式化后的价格
     */
    formatPrice(price) {
      const priceFloat = parseFloat(price / 100);
      if (!priceFloat) return '-';
      return window.get_color_price ? window.get_color_price(priceFloat) : `${priceFloat}元`;
    },
    /**
     * 格式化完整价格信息（包括跨服费用）
     * @param {Object} item - 物品对象
     * @param {boolean|string} simple - 是否简化显示
     * @returns {string} 格式化后的完整价格信息
     */
    formatFullPrice(item, simple = false) {
      let basePrice;
      if (typeof item === 'object') {
        basePrice = this.formatPrice(item.price);
      } else {
        basePrice = this.formatPrice(item);
      }

      // 检查是否有登录信息和跨服费用
      if (!window.LoginInfo || !window.LoginInfo.login) {
        return basePrice;
      }
      const crossServerPoundage = item.cross_server_poundage || 0;
      const fairShowPoundage = item.fair_show_poundage || 0;
      if (!crossServerPoundage || simple && simple !== 'cross') {
        if (simple && simple == 'cross') {
          return '';
        }
        return basePrice;
      }
      let additionalFeeHtml = '';
      if (item.pass_fair_show == 1) {
        // 跨服费
        const crossFee = parseFloat(crossServerPoundage / 100);
        additionalFeeHtml = `<div class="f12px" style="color: #666;">跨服费<span class="p1000">￥${crossFee}</span></div>`;
      } else {
        // 信息费（跨服费 + 预订费）
        const totalFee = parseFloat((crossServerPoundage + fairShowPoundage) / 100);
        additionalFeeHtml = `<div class="f12px" style="color: #666;">信息费<span class="p1000">￥${totalFee}</span></div>`;
      }
      if (simple && simple == 'cross') {
        return additionalFeeHtml;
      }
      return basePrice + additionalFeeHtml;
    },
    /**
     * 获取CBG链接（通用版本，支持不同类型）
     * @param {string} eid - 装备/召唤兽ID
     * @param {string} type - 类型：'equip', 'pet', 'role'
     * @returns {string} CBG链接
     */
    getCBGLinkByType(eid, type = 'equip') {
      if (!eid) return '#';
      const serverId = eid.split('-')[1];
      switch (type) {
        // case 'pet':
        //   return `https://xyq-m.cbg.163.com/cgi/mweb/equip/${serverId}/${eid}`
        // case 'role':
        //   return `https://xyq.cbg.163.com/equip?s=${serverId}&eid=${eid}`
        // case 'equip':
        default:
          return `https://xyq-m.cbg.163.com/cgi/mweb/equip/${serverId}/${eid}`;
      }
    },
    /**
     * 防抖函数
     * @param {Function} func - 要防抖的函数
     * @param {number} wait - 等待时间（毫秒）
     * @returns {Function} 防抖后的函数
     */
    debounce(func, wait = 300) {
      let timeout;
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout);
          func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
      };
    },
    /**
     * 节流函数
     * @param {Function} func - 要节流的函数
     * @param {number} limit - 限制时间（毫秒）
     * @returns {Function} 节流后的函数
     */
    throttle(func, limit = 300) {
      let inThrottle;
      return function executedFunction(...args) {
        if (!inThrottle) {
          func.apply(this, args);
          inThrottle = true;
          setTimeout(() => inThrottle = false, limit);
        }
      };
    },
    /**
     * 表格行样式类名
     * @param {Object} params - 参数对象
     * @param {Object} params.row - 行数据
     * @param {number} params.rowIndex - 行索引
     * @returns {string} 样式类名
     */
    tableRowClassName({
      row
    }) {
      // 可以根据业务需求自定义行样式
      if (row.is_special) {
        return 'warning-row';
      }
      return '';
    },
    /**
     * 获取图片URL（统一图片URL生成方法）
     * @param {string} imageName - 图片名称
     * @param {string} size - 图片尺寸 (small/big)
     * @returns {string} 完整的图片URL
     */
    getImageUrl(imageName, size = 'small') {
      if (!imageName) return '';

      // 如果已经是完整URL，直接返回
      if (imageName.startsWith('http://') || imageName.startsWith('https://')) {
        if (size === 'big' && imageName.includes('/images/equip/small/')) {
          return imageName.replace('/images/equip/small/', '/images/big/');
        }
        return imageName;
      }

      // 拼接CBG资源URL
      return `https://cbg-xyq.res.netease.com/images/${size}/${imageName}`;
    }
  }
};

/***/ }),

/***/ "./src/utils/request.js":
/*!******************************!*\
  !*** ./src/utils/request.js ***!
  \******************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   api: function() { return /* binding */ api; }
/* harmony export */ });
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! axios */ "./node_modules/axios/lib/axios.js");
/* harmony import */ var element_ui__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! element-ui */ "./node_modules/element-ui/lib/element-ui.common.js");
/* harmony import */ var element_ui__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(element_ui__WEBPACK_IMPORTED_MODULE_0__);



// 判断是否为Chrome插件环境
const isChromeExtension = typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id;

// 根据环境设置不同的baseURL
const baseURL = isChromeExtension ? 'http://localhost:5000/api/v1' : '/api/v1';

// 创建axios实例
const request = axios__WEBPACK_IMPORTED_MODULE_1__["default"].create({
  baseURL: baseURL,
  // API基础路径
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
request.interceptors.request.use(config => {
  // 在发送请求之前做些什么
  console.log('发送请求:', config.method?.toUpperCase(), config.url);
  return config;
}, error => {
  // 对请求错误做些什么
  console.error('请求错误:', error);
  return Promise.reject(error);
});

// 响应拦截器
request.interceptors.response.use(response => {
  // 对响应数据做些什么
  const {
    data
  } = response;
  return data;
}, error => {
  // 对响应错误做些什么
  console.error('响应错误:', error);
  let message = '请求失败';
  let responseData = null;
  if (error.response) {
    // 服务器响应了错误状态码
    const {
      status,
      data
    } = error.response;
    message = data.message || `请求失败 (${status})`;

    // 如果后端返回了data字段，使用后端的data；否则使用后端的完整响应
    if (data.data !== undefined) {
      responseData = data.data;
    } else {
      responseData = data;
    }
    console.log('错误响应数据:', responseData);
  } else if (error.request) {
    // 请求已发出但没有收到响应
    message = '网络错误，请检查网络连接';
  } else {
    // 其他错误
    message = error.message || '请求失败';
  }
  element_ui__WEBPACK_IMPORTED_MODULE_0__.Notification.error({
    title: '错误',
    message: message
  });
  return {
    code: error.response?.status || 500,
    data: responseData,
    // 使用后端返回的data，而不是强制设置为null
    message: message,
    timestamp: Date.now()
  };
});

// 导出封装的请求方法
const api = {
  // GET请求
  get(url, params = {}) {
    return request.get(url, {
      params
    });
  },
  // POST请求
  post(url, data = {}) {
    return request.post(url, data);
  },
  // PUT请求
  put(url, data = {}) {
    return request.put(url, data);
  },
  // DELETE请求
  delete(url, params = {}) {
    return request.delete(url, {
      params
    });
  },
  // 下载文件
  download(url, params = {}, filename) {
    return request.get(url, {
      params,
      responseType: 'blob'
    }).then(response => {
      if (response.code === 200) {
        // 创建下载链接
        const blob = new Blob([response.data]);
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename || 'download';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);
      }
      return response;
    });
  }
};
/* harmony default export */ __webpack_exports__["default"] = (request);

/***/ }),

/***/ "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAGUlEQVQYV2M4gwH+YwCGIasIUwhT25BVBADtzYNYrHvv4gAAAABJRU5ErkJggg==":
/*!**********************************************************************************************************************************************!*\
  !*** data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAGUlEQVQYV2M4gwH+YwCGIasIUwhT25BVBADtzYNYrHvv4gAAAABJRU5ErkJggg== ***!
  \**********************************************************************************************************************************************/
/***/ (function(module) {

"use strict";
module.exports = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAGUlEQVQYV2M4gwH+YwCGIasIUwhT25BVBADtzYNYrHvv4gAAAABJRU5ErkJggg==";

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			id: moduleId,
/******/ 			loaded: false,
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = __webpack_modules__;
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/amd options */
/******/ 	!function() {
/******/ 		__webpack_require__.amdO = {};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/chunk loaded */
/******/ 	!function() {
/******/ 		var deferred = [];
/******/ 		__webpack_require__.O = function(result, chunkIds, fn, priority) {
/******/ 			if(chunkIds) {
/******/ 				priority = priority || 0;
/******/ 				for(var i = deferred.length; i > 0 && deferred[i - 1][2] > priority; i--) deferred[i] = deferred[i - 1];
/******/ 				deferred[i] = [chunkIds, fn, priority];
/******/ 				return;
/******/ 			}
/******/ 			var notFulfilled = Infinity;
/******/ 			for (var i = 0; i < deferred.length; i++) {
/******/ 				var chunkIds = deferred[i][0];
/******/ 				var fn = deferred[i][1];
/******/ 				var priority = deferred[i][2];
/******/ 				var fulfilled = true;
/******/ 				for (var j = 0; j < chunkIds.length; j++) {
/******/ 					if ((priority & 1 === 0 || notFulfilled >= priority) && Object.keys(__webpack_require__.O).every(function(key) { return __webpack_require__.O[key](chunkIds[j]); })) {
/******/ 						chunkIds.splice(j--, 1);
/******/ 					} else {
/******/ 						fulfilled = false;
/******/ 						if(priority < notFulfilled) notFulfilled = priority;
/******/ 					}
/******/ 				}
/******/ 				if(fulfilled) {
/******/ 					deferred.splice(i--, 1)
/******/ 					var r = fn();
/******/ 					if (r !== undefined) result = r;
/******/ 				}
/******/ 			}
/******/ 			return result;
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	!function() {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = function(module) {
/******/ 			var getter = module && module.__esModule ?
/******/ 				function() { return module['default']; } :
/******/ 				function() { return module; };
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	!function() {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = function(exports, definition) {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/global */
/******/ 	!function() {
/******/ 		__webpack_require__.g = (function() {
/******/ 			if (typeof globalThis === 'object') return globalThis;
/******/ 			try {
/******/ 				return this || new Function('return this')();
/******/ 			} catch (e) {
/******/ 				if (typeof window === 'object') return window;
/******/ 			}
/******/ 		})();
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	!function() {
/******/ 		__webpack_require__.o = function(obj, prop) { return Object.prototype.hasOwnProperty.call(obj, prop); }
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	!function() {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = function(exports) {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/node module decorator */
/******/ 	!function() {
/******/ 		__webpack_require__.nmd = function(module) {
/******/ 			module.paths = [];
/******/ 			if (!module.children) module.children = [];
/******/ 			return module;
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/publicPath */
/******/ 	!function() {
/******/ 		var scriptUrl;
/******/ 		if (__webpack_require__.g.importScripts) scriptUrl = __webpack_require__.g.location + "";
/******/ 		var document = __webpack_require__.g.document;
/******/ 		if (!scriptUrl && document) {
/******/ 			if (document.currentScript && document.currentScript.tagName.toUpperCase() === 'SCRIPT')
/******/ 				scriptUrl = document.currentScript.src;
/******/ 			if (!scriptUrl) {
/******/ 				var scripts = document.getElementsByTagName("script");
/******/ 				if(scripts.length) {
/******/ 					var i = scripts.length - 1;
/******/ 					while (i > -1 && (!scriptUrl || !/^http(s?):/.test(scriptUrl))) scriptUrl = scripts[i--].src;
/******/ 				}
/******/ 			}
/******/ 		}
/******/ 		// When supporting browsers where an automatic publicPath is not supported you must specify an output.publicPath manually via configuration
/******/ 		// or pass an empty string ("") and set the __webpack_public_path__ variable from your code to use your own logic.
/******/ 		if (!scriptUrl) throw new Error("Automatic publicPath is not supported in this browser");
/******/ 		scriptUrl = scriptUrl.replace(/^blob:/, "").replace(/#.*$/, "").replace(/\?.*$/, "").replace(/\/[^\/]+$/, "/");
/******/ 		__webpack_require__.p = scriptUrl;
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/jsonp chunk loading */
/******/ 	!function() {
/******/ 		__webpack_require__.b = document.baseURI || self.location.href;
/******/ 		
/******/ 		// object to store loaded and loading chunks
/******/ 		// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 		// [resolve, reject, Promise] = chunk loading, 0 = chunk loaded
/******/ 		var installedChunks = {
/******/ 			"panel": 0
/******/ 		};
/******/ 		
/******/ 		// no chunk on demand loading
/******/ 		
/******/ 		// no prefetching
/******/ 		
/******/ 		// no preloaded
/******/ 		
/******/ 		// no HMR
/******/ 		
/******/ 		// no HMR manifest
/******/ 		
/******/ 		__webpack_require__.O.j = function(chunkId) { return installedChunks[chunkId] === 0; };
/******/ 		
/******/ 		// install a JSONP callback for chunk loading
/******/ 		var webpackJsonpCallback = function(parentChunkLoadingFunction, data) {
/******/ 			var chunkIds = data[0];
/******/ 			var moreModules = data[1];
/******/ 			var runtime = data[2];
/******/ 			// add "moreModules" to the modules object,
/******/ 			// then flag all "chunkIds" as loaded and fire callback
/******/ 			var moduleId, chunkId, i = 0;
/******/ 			if(chunkIds.some(function(id) { return installedChunks[id] !== 0; })) {
/******/ 				for(moduleId in moreModules) {
/******/ 					if(__webpack_require__.o(moreModules, moduleId)) {
/******/ 						__webpack_require__.m[moduleId] = moreModules[moduleId];
/******/ 					}
/******/ 				}
/******/ 				if(runtime) var result = runtime(__webpack_require__);
/******/ 			}
/******/ 			if(parentChunkLoadingFunction) parentChunkLoadingFunction(data);
/******/ 			for(;i < chunkIds.length; i++) {
/******/ 				chunkId = chunkIds[i];
/******/ 				if(__webpack_require__.o(installedChunks, chunkId) && installedChunks[chunkId]) {
/******/ 					installedChunks[chunkId][0]();
/******/ 				}
/******/ 				installedChunks[chunkId] = 0;
/******/ 			}
/******/ 			return __webpack_require__.O(result);
/******/ 		}
/******/ 		
/******/ 		var chunkLoadingGlobal = self["webpackChunkweb"] = self["webpackChunkweb"] || [];
/******/ 		chunkLoadingGlobal.forEach(webpackJsonpCallback.bind(null, 0));
/******/ 		chunkLoadingGlobal.push = webpackJsonpCallback.bind(null, chunkLoadingGlobal.push.bind(chunkLoadingGlobal));
/******/ 	}();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module depends on other loaded chunks and execution need to be delayed
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, ["vendors"], function() { return __webpack_require__("./src/chrome-extensions/main.js"); })
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;
//# sourceMappingURL=panel.js.map