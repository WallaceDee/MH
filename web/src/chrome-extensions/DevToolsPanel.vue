<template>
  <div class="panel">
    <div class="panel-header">
      <el-row type="flex" align="middle">
        <div style="width: 32px;height: 32px;margin-right: 10px;position: relative;">
          <img src="~@/assets/logo.png" alt="梦幻灵瞳" style="width: 32px;height: 32px;">
          <span class="status-dot"
            :class="{ 'connected': devtoolsConnected, 'disconnected': !devtoolsConnected }"></span>
        </div>
        <h3 style="color: #fff;">梦幻灵瞳</h3>
      </el-row>
      <div class="connection-status">
        <div id="pager" class="fr" v-if="pageInfo.hasPager">
          <el-row class="pages" type="flex" align="middle">
            <span style="color: #fff;margin-right: 10px;"> 第{{ pageInfo.currentPage }}页, 共{{ pageInfo.total }}页 </span>
            <a v-if="pageInfo.hasPrev" href="javascript:void 0;" @click.prevent="prevPage"
              style="line-height: 1.2em;">上一页</a>
            <a v-if="pageInfo.hasNext" href="javascript:void 0;" @click.prevent="nextPage"
              style="line-height: 1.2em;">下一页</a>
          </el-row>
        </div>
        <a v-if="!devtoolsConnected" href="javascript:void 0;" @click="reconnectDevTools">重新连接</a>
        <a v-if="!isInNewWindow" href="javascript:void 0;" class=" btn1 js_alert_btn_0"
          @click.prevent="openInNewTab">新窗口打开</a>
        <a v-if="!pageInfo.hasPager" href="javascript:void 0;" class=" btn1 js_alert_btn_0"
          @click.prevent="refreshCurrentPage">刷新页面</a>
        <a v-if="recommendData.length > 0" href="javascript:void 0;" class=" btn1 js_alert_btn_0"
          @click.prevent="clearData">清空数据</a>
        <a href="javascript:void 0;" class=" btn1 js_alert_btn_0"
          @click.prevent="testAddIframe" style="background: #f56c6c;">测试iframe</a>
      </div>
    </div>
    <div class="data-section">
      <el-empty v-if="recommendData.length === 0" class="empty-state" description="暂无数据，请访问梦幻西游藏宝阁页面"></el-empty>
      <div v-else class="request-list">
        <div v-for="(item, index) in recommendData" :key="item.requestId" class="request-item"
          :class="{ 'parsing': item.status === 'parsing' }">
          <div class="request-info">
            <div class="request-meta">
              <span class="status" :class="item.status">
                <template v-if="item.status === 'parsing'">
                  <i class="el-icon-loading"></i> 解析中...
                </template>
                <template v-else-if="item.status === 'completed'">
                  <i class="el-icon-success"></i> 解析完成
                </template>
                <template v-else>
                  <i class="el-icon-error"></i> 解析失败
                </template>
              </span>
              <el-tag v-if="item.dataType" size="mini" type="info" style="margin-left: 5px;">
                {{ getDataTypeLabel(item.dataType) }}
              </el-tag>
              <span class="timestamp">{{ formatTime(item.timestamp) }}</span>
            </div>
          </div>
          <div v-if="item.responseData && item.dataType" class="response-data">
            <!-- 角色数据渲染 -->
            <el-row :gutter="4" v-if="item.dataType === 'role'">
              <el-col v-for="role in parseListData(item.responseData)?.equip_list" :key="role.eid"
                style="width: 20%;margin-bottom: 2px;margin-top: 2px;">
                <el-card class="role-card" :class="{ 'empty-role': isEmptyRole(parserRoleData(role)) }">
                  <el-row type="flex" justify="space-between">
                    <el-col style="width:50px;flex-shrink: 0;margin-right: 4px;">
                      <RoleImage :key="role.eid" :other_info="role.other_info" :roleInfo="parserRoleData(role)" />
                      <el-link :href="getCBGLinkByType(role.eid, 'role')" type="danger" target="_blank"
                        style="white-space: nowrap;text-overflow: ellipsis;overflow: hidden;display: block;font-size: 12px;">
                        {{ role.seller_nickname }}</el-link>
                    </el-col>
                    <el-col>
                      <div>
                        <el-tag type="success" v-if="role.accept_bargain == 1">接受还价</el-tag>
                        <el-tag type="danger" v-else>拒绝还价</el-tag>
                      </div>
                      <div style="padding: 5px 0;">
                        <span v-html="formatFullPrice(role.price, true)"></span>
                      </div>
                      <div>
                        <el-tag type="danger" v-if="isEmptyRole(parserRoleData(role))">空号</el-tag>
                        <template v-else>
                          <el-tag @click="handleEquipPrice(role)" style="cursor: pointer;" v-if="get_equip_num(parserRoleData(role)) > 0">
                            ⚔️ {{ get_equip_num(parserRoleData(role)) }}
                          </el-tag>
                          <el-tag type="success" @click="handlePetPrice(role)" style="cursor: pointer;" v-if="get_pet_num(parserRoleData(role)) > 0">
                            🐲 {{ get_pet_num(parserRoleData(role)) }}
                          </el-tag>
                        </template>
                      </div>

                    </el-col>
                  </el-row>
                  <div>
                    <SimilarRoleModal :role="{ ...role, roleInfo: parserRoleData(role) }"
                      :search-params="{ selectedDate: selectedDate, roleType: 'normal' }">
                      <div> <el-link type="primary" href="javascript:void 0;" @click.prevent
                          :disabled="item.status !== 'completed'">👤
                          裸号</el-link></div>
                    </SimilarRoleModal>
                  </div>
                </el-card>
              </el-col>
            </el-row>
            
            <!-- 装备数据渲染 -->
            <el-row :gutter="4" v-else-if="item.dataType === 'equipment'">
              <el-col v-for="equip in parseListData(item.responseData)?.equip_list" :key="equip.eid"
                style="width: 20%;margin-bottom: 2px;margin-top: 2px;">
                <el-card class="role-card">
                  <el-row type="flex" justify="space-between">
                    <el-col style="width:50px;flex-shrink: 0;margin-right: 4px;">
                      <EquipmentImage :equipment="equip" />
                      <el-link :href="getCBGLinkByType(equip.eid, 'equip')" type="danger" target="_blank"
                        style="white-space: nowrap;text-overflow: ellipsis;overflow: hidden;display: block;font-size: 12px;">
                        {{ equip.equip_name }}
                      </el-link>
                    </el-col>
                    <el-col>
                      <div style="padding: 5px 0;">
                        <span v-html="formatFullPrice(equip)"></span>
                      </div>
                      <div v-if="equip.highlight" class="equip-desc-content" v-html="gen_highlight(equip.highlight)"></div>
                      <div v-if="equip.equip_level" style="font-size: 12px;">
                        等级: {{ equip.equip_level }}
                      </div>
                      <div v-if="equip.server_name" style="font-size: 12px; color: #909399;">
                        {{ equip.server_name }}
                      </div>
                    </el-col>
                  </el-row>
                </el-card>
              </el-col>
            </el-row>
            
            <!-- 召唤兽数据渲染 -->
            <el-row :gutter="4" v-else-if="item.dataType === 'pet'">
              <el-col v-for="pet in parseListData(item.responseData)?.equip_list" :key="pet.eid"
                style="width: 20%;margin-bottom: 2px;margin-top: 2px;">
                <el-card class="role-card">
                  <el-row type="flex" justify="space-between">
                    <el-col style="width:50px;flex-shrink: 0;margin-right: 4px;">
                      <el-image v-if="pet.avatar_url" :src="pet.avatar_url" style="width: 50px;height: 50px;" fit="cover"></el-image>
                      <el-link :href="getCBGLinkByType(pet.eid, 'pet')" type="danger" target="_blank"
                        style="white-space: nowrap;text-overflow: ellipsis;overflow: hidden;display: block;font-size: 12px;">
                        {{ pet.seller_nickname || pet.name || pet.nickname }}
                      </el-link>
                    </el-col>
                    <el-col>
                      <div style="padding: 5px 0;">
                        <span v-html="formatFullPrice(pet.price, true)"></span>
                      </div>
                      <div v-if="pet.grade" style="font-size: 12px;">
                        等级: {{ pet.grade }}
                      </div>
                      <div v-if="pet.server_name" style="font-size: 12px; color: #909399;">
                        {{ pet.server_name }}
                      </div>
                    </el-col>
                  </el-row>
                </el-card>
              </el-col>
            </el-row>
            <!-- <el-button @click="toggleResponse(index)" size="mini" type="text">
              {{ expandedItems.includes(index) ? '收起' : '展开' }}响应数据
            </el-button>
            <div v-if="expandedItems.includes(index)" class="response-content">
              <pre>{{ JSON.stringify(item.responseData, null, 2) }}</pre>
            </div> -->
          </div>
        </div>
      </div>
    </div>

    <!-- 页面底部版本信息 -->
    <div class="version-footer">
      <span class="version-text">版本 v0.0.1</span>
    </div>

    <!-- 装备估价结果对话框 -->
    <el-dialog :visible.sync="valuationDialogVisible" width="1000px" :close-on-click-modal="false"
      :close-on-press-escape="false" custom-class="batch-valuation-dialog">
      <span slot="title" class="el-dialog__title">
        <el-tag size="mini">{{ valuationDialogTitle.server_name }}</el-tag>
        /
        <el-tag type="info" size="mini">{{ valuationDialogTitle.school }}</el-tag>/
        <el-link :href="getCBGLinkByType(valuationDialogTitle.eid)" target="_blank">{{ valuationDialogTitle.nickname
        }}</el-link>
      </span>
      <EquipBatchValuationResult :results="valuationResults" :total-value="valuationTotalValue"
        :equipment-list="valuationEquipmentList" :valuate-params="batchValuateParams" :loading="valuationLoading"
        @close="closeValuationDialog" />
    </el-dialog>

    <!-- AutoParams配置对话框 -->
    <el-dialog :visible.sync="autoParamsDialogVisible" width="1200px" :close-on-click-modal="false"
      :close-on-press-escape="false" custom-class="auto-params-dialog">
      <span slot="title" class="el-dialog__title">
        <span class="emoji-icon">⚙️</span> 自动参数配置
      </span>
      <AutoParams v-if="autoParamsDialogVisible" :external-params="autoParamsExternalParams" 
        @close="closeAutoParamsDialog" />
    </el-dialog>
  </div>
</template>
<script>
import dayjs from 'dayjs'
import RoleImage from '@/components/RoleInfo/RoleImage.vue'
import SimilarRoleModal from '@/components/SimilarRoleModal.vue'
import EquipBatchValuationResult from '@/components/EquipBatchValuationResult.vue'
import EquipmentImage from '@/components/EquipmentImage/EquipmentImage.vue'
import AutoParams from '@/components/AutoParams.vue'
import { commonMixin } from '@/utils/mixins/commonMixin'
import { equipmentMixin } from '@/utils/mixins/equipmentMixin'
export default {
  name: 'DevToolsPanel',
  data() {
    return {
      pageInfo: {
        hasPager: false,
        currentPage: 0,
        total: 0,
        hasPrev: false,
        hasNext: false
      },
      selectedDate: dayjs().format('YYYY-MM'),
      recommendData: [],
      expandedItems: [],
      processedRequests: new Set(), // 记录已处理的请求ID
      devtoolsConnected: false, // 数据监听连接状态
      connectionStatus: '检查中...', // 连接状态描述
      connectionCheckTimer: null, // 连接检查定时器
      isInNewWindow: false, // 是否在新窗口中打开
      
      // 装备估价相关数据
      valuationDialogVisible: false,
      valuationResults: [],
      valuationTotalValue: 0,
      valuationEquipmentList: [],
      valuationLoading: false,
      valuationDialogTitle: {},
      batchValuateParams: {
        similarity_threshold: 0.7,
        max_anchors: 30
      },
      
      // AutoParams Modal相关数据
      autoParamsDialogVisible: false,
      autoParamsExternalParams: {}
    }
  },
  mixins: [commonMixin, equipmentMixin],
  components: {
    RoleImage,
    SimilarRoleModal,
    EquipBatchValuationResult,
    EquipmentImage,
    AutoParams
  },
  computed: {

  },
  mounted() {
    // 通知background script侧边栏已打开
    if (typeof chrome !== 'undefined' && chrome.runtime) {
      chrome.runtime.sendMessage({
        action: 'sidePanelOpened'
      })
    }

    // 监听页面可见性变化，当页面不可见时通知关闭
    document.addEventListener('visibilitychange', this.handleVisibilityChange)

    this.initMessageListener()
    this.checkConnectionStatus()
    this.checkIfInNewWindow()

    // // 设置定时检查（每5秒检查一次）
    // this.connectionCheckTimer = setInterval(() => {
    //   this.checkConnectionStatus()
    // }, 5000)
  },
  beforeDestroy() {
    // 通知background script侧边栏已关闭
    if (typeof chrome !== 'undefined' && chrome.runtime) {
      chrome.runtime.sendMessage({
        action: 'sidePanelClosed'
      })
    }

    // 移除可见性变化监听器
    document.removeEventListener('visibilitychange', this.handleVisibilityChange)

    // 移除Chrome消息监听器
    this.removeMessageListener()
    // 清理定时器
    if (this.connectionCheckTimer) {
      clearInterval(this.connectionCheckTimer)
      this.connectionCheckTimer = null
    }
    // 清理组件状态
    this.recommendData = []
    this.expandedItems = []
  },
  methods: {
    handleVisibilityChange() {
      // 当页面不可见时，通知background script侧边栏已关闭
      if (document.hidden) {
        if (typeof chrome !== 'undefined' && chrome.runtime) {
          chrome.runtime.sendMessage({
            action: 'sidePanelClosed'
          })
        }
      } else {
        this.getPagerInfo().then(res => {
          this.pageInfo = res
        })
        // 当页面重新可见时，通知background script侧边栏已打开
        if (typeof chrome !== 'undefined' && chrome.runtime) {
          chrome.runtime.sendMessage({
            action: 'sidePanelOpened'
          })
        }
      }
    },

    isEmptyRole(roleInfo) {
      const noEquip = this.get_equip_num(roleInfo) === 0
      let noPet = true
      for (let pet of roleInfo.pet_info) {
        if (pet.pet_grade > 100 && pet.is_baobao === '是') {
          noPet = false
          break
        }
        if (pet.pet_grade > 100 && pet.is_baobao === '否' && pet.all_skills.length > 4) {
          noPet = false
          break
        }
      }
      return noEquip && noPet
    },
    getDataTypeLabel(type) {
      const typeMap = {
        'role': '角色',
        'pet': '召唤兽',
        'equipment': '装备'
      }
      return typeMap[type] || type
    },
    get_pet_num(roleInfo) {
      return roleInfo.pet_info.length + roleInfo.split_pets.length
    },
    get_equip_num(roleInfo) {
      return roleInfo.using_equips.length + roleInfo.not_using_equips.length + roleInfo.split_equips.length
    },
    nextPage() {
      // 通过Chrome调试API查找并点击页面上的分页器
      this.clickPageButton('next')
    },

    prevPage() {
      // 通过Chrome调试API查找并点击页面上的分页器
      this.clickPageButton('prev')
    },

    reconnectDevTools() {
      // 重新连接数据监听
      this.connectionStatus = '重连中...'
      this.checkConnectionStatus()
      this.$notify.info('正在尝试重新连接数据监听...')
    },

    async clickPageButton(direction) {
      try {
        // 获取当前活动标签页
        const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true })

        if (!activeTab || !activeTab.url.includes('cbg.163.com')) {
          this.$notify.warning('请先访问梦幻西游藏宝阁页面')
          return
        }

        // 检查数据监听连接状态
        if (!this.devtoolsConnected) {
          this.$notify.warning('数据监听连接已断开，请重新加载页面')
          return
        }

        // 通过Chrome调试API执行页面JavaScript代码
        const result = await chrome.debugger.sendCommand(
          { tabId: activeTab.id },
          'Runtime.evaluate',
          {
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
          }
        )
        this.pageInfo = await this.getPagerInfo()
        // 处理Chrome调试API的返回结果
        if (result && result.result && result.result.value) {
          const message = result.result.value

          if (message.startsWith('SUCCESS:')) {
            this.$notify.success(message.substring(8)) // 移除"SUCCESS:"前缀
            console.log(`${direction === 'next' ? '下一页' : '上一页'}按钮点击成功`)
          } else if (message.startsWith('ERROR:')) {
            this.$notify.warning(message.substring(6)) // 移除"ERROR:"前缀
            console.warn(`${direction === 'next' ? '下一页' : '上一页'}按钮点击失败:`, message)
          } else {
            this.$notify.error('执行页面操作失败：未知返回结果')
            console.error('页面操作结果异常:', result)
          }
        } else {
          this.$notify.error('执行页面操作失败')
          console.error('页面操作结果异常:', result)
        }

      } catch (error) {
        console.error(`点击${direction === 'next' ? '下一页' : '上一页'}按钮失败:`, error)

        // 检查是否是连接断开错误
        if (error.message && error.message.includes('Could not establish connection')) {
          this.devtoolsConnected = false
          this.connectionStatus = '连接断开'
          this.$notify.error('数据监听连接已断开，请重新加载页面或刷新扩展')
        } else {
          this.$notify.error('操作失败: ' + error.message)
        }
      }
    },

    async getPagerInfo() {
      try {
        // 获取当前活动标签页
        const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true })

        if (!activeTab || !activeTab.url.includes('cbg.163.com')) {
          this.$notify.warning('请先访问梦幻西游藏宝阁页面')
          return
        }

        // 检查数据监听连接状态
        if (!this.devtoolsConnected) {
          this.$notify.warning('数据监听连接已断开，请重新加载页面')
          return
        }

        // 通过Chrome调试API执行页面JavaScript代码获取分页器信息
        //在pagerDiv的innerText中查找 `共100页`，获取100
        const result = await chrome.debugger.sendCommand(
          { tabId: activeTab.id },
          'Runtime.evaluate',
          {
            expression: `
              (function() {
                let hasPager = false
                try {
                  // 查找id为pager的div
                  const pagerDiv = document.getElementById('pager')
                  if (!pagerDiv) {
                    return 'ERROR:未找到分页器元素'
                  }
                  hasPager = true
                  // 获取当前页码
                  const currentPageLink = pagerDiv.querySelector('a.on')
                  let currentPage = 0
                  if (currentPageLink) {
                    currentPage = currentPageLink.textContent.trim()
                  }
                  
                  // 从innerText中查找"共X页"模式
                  let total = 0
                  const innerText = pagerDiv.innerText || pagerDiv.textContent || ''
                  
                  // 手动查找"共"和"页"之间的数字
                  const gongIndex = innerText.indexOf('共')
                  const yeIndex = innerText.indexOf('页', gongIndex)
                  
                  if (gongIndex !== -1 && yeIndex !== -1) {
                    const textBetween = innerText.substring(gongIndex + 1, yeIndex).trim()
                    total = textBetween
                    console.log('textBetween:', textBetween)
                    const numberMatch = textBetween.match(/(\d+)/)
                    if (numberMatch) {
                      total = numberMatch[1]
                    }
                  }
                  
                  // 检查是否有上一页/下一页按钮
                  const hasPrev = pagerDiv.querySelector('a[href*="goto("]') && 
                                 pagerDiv.textContent.includes('上一页')
                  const hasNext = pagerDiv.querySelector('a[href*="goto("]') && 
                                 pagerDiv.textContent.includes('下一页')
                  
                  // return 'SUCCESS:第' + currentPage + '页，共' + total + '页 (上一页:' + (hasPrev ? '有' : '无') + ', 下一页:' + (hasNext ? '有' : '无') + ')'
                  return JSON.stringify({
                    hasPager: hasPager,
                    currentPage: currentPage*1,
                    total: total*1,
                    hasPrev: hasPrev,
                    hasNext: hasNext
                  })
                } catch (error) {
                  return 'ERROR:获取分页器信息失败 - ' + error.message
                }
              })()
            `
          }
        )
        console.log('resultresultresultresult:', result)
        // 处理返回结果
        if (result && result.result && result.result.value) {
          return JSON.parse(result.result.value)
        } else {
          return {
            hasPager: false,
            currentPage: 0,
            total: 0,
            hasPrev: false,
            hasNext: false
          }
        }
      } catch (error) {
        console.error('获取分页器信息失败:', error)
        return {
          hasPager: false,
          currentPage: 0,
          total: 0,
          hasPrev: false,
          hasNext: false
        }
      }
    },
    parserRoleData(data) {
      const roleInfo = new window.RoleInfoParser(data.large_equip_desc, { equip_level: data.equip_level })
      return roleInfo.result
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
      const match = responseDataStr.match(/Request\.JSONP\.request_map\.request_\d+\((.*)\)/)
      let templateJSONStr = '{}'
      if (match) {
        templateJSONStr = match[1]
      } else {
        templateJSONStr = responseDataStr
      }
      try {
        let templateJSON = {}
        if (typeof templateJSONStr === 'string') {
          templateJSON = JSON.parse(templateJSONStr)
        } else {
          // h5
          templateJSON = templateJSONStr
        }
        return templateJSON
      } catch (error) {
        console.error('解析响应数据失败:', error)
        return {}
      }
    },
    initMessageListener() {
      console.log('DevToolsPanel mounted, initializing listener')

      // 使用单例模式确保只有一个监听器
      if (typeof chrome !== 'undefined' && chrome.runtime) {
        // 如果已经有全局监听器，先移除
        if (window.cbgDevToolsListener) {
          chrome.runtime.onMessage.removeListener(window.cbgDevToolsListener)
        }

        // 创建全局监听器
        window.cbgDevToolsListener = (request, sender, sendResponse) => {
          console.log('DevToolsPanel received Chrome message:', request.action)
          this.handleChromeMessage(request, sender, sendResponse)
          sendResponse({ success: true })
        }

        // 注册监听器
        chrome.runtime.onMessage.addListener(window.cbgDevToolsListener)
        console.log('Chrome message listener registered for DevToolsPanel')
      }
    },

    removeMessageListener() {
      // 移除Chrome消息监听器
      if (typeof chrome !== 'undefined' && chrome.runtime && window.cbgDevToolsListener) {
        chrome.runtime.onMessage.removeListener(window.cbgDevToolsListener)
        delete window.cbgDevToolsListener
        console.log('Chrome message listener removed for DevToolsPanel')
      }
    },

    checkConnectionStatus() {
      // 检查Chrome扩展连接状态
      if (typeof chrome !== 'undefined' && chrome.runtime) {
        // 尝试发送ping消息检查连接
        chrome.runtime.sendMessage({ action: 'ping' }, (response) => {
          if (chrome.runtime.lastError) {
            console.log('Chrome extension connection check failed:', chrome.runtime.lastError)
            this.devtoolsConnected = false
            this.connectionStatus = '未连接'
          } else if (response && response.success) {
            console.log('Chrome extension connection check successful:', response)
            this.devtoolsConnected = true
            this.connectionStatus = '已连接'
          } else {
            console.log('Chrome extension connection check failed: invalid response')
            this.devtoolsConnected = false
            this.connectionStatus = '连接异常'
          }
        })
      } else {
        console.log('Chrome runtime not available')
        this.devtoolsConnected = false
        this.connectionStatus = 'Chrome环境不可用'
      }
    },
    changeRecommendDataStatus({ requestId, status, data }) {
      const targetIndex = this.recommendData.findIndex(item => item.requestId === requestId)
      if (targetIndex !== -1) {
        this.$set(this.recommendData[targetIndex], 'status', status)
        // 如果提供了data，更新相关字段
        if (data) {
          if (data.type) {
            this.$set(this.recommendData[targetIndex], 'dataType', data.type)
          }
        }
      }
    },
    processNewData(dataArray) {
      // 类型映射
      const typeMap = {
        'role': '角色',
        'pet': '召唤兽',
        'equipment': '装备'
      }
      
      // 只处理新完成的请求，避免重复处理
      if (dataArray && dataArray.length > 0) {
        dataArray.forEach(item => {
          if (item.responseData &&
            item.url &&
            item.requestId &&
            !this.processedRequests.has(item.requestId)) {

            // 标记为已处理
            this.processedRequests.add(item.requestId)
            console.log(`开始处理新请求: ${item.requestId}`)

            // 调用解析响应数据接口
            this.$api.spider.parseResponse({
              url: item.url,
              response_text: item.responseData
            }).then(res => {
              console.log(`请求 ${item.requestId} 解析结果:`, res)
              if (res.code === 200) {
                const typeName = typeMap[res.data.type] || res.data.type
                console.log(`请求 ${item.requestId} 数据类型: ${typeName}`, res.data)
                this.changeRecommendDataStatus({ requestId: item.requestId, status: 'completed', data: res.data })
              } else {
                console.error(`请求 ${item.requestId} 数据解析失败:`, res.message)
                this.changeRecommendDataStatus({ requestId: item.requestId, status: 'failed' })
              }
            }).catch(error => {
              console.error(`请求 ${item.requestId} 解析请求失败:`, error)
              // 解析失败时移除标记，允许重试
              this.processedRequests.delete(item.requestId)
              this.changeRecommendDataStatus({ requestId: item.requestId, status: 'failed' })
            })
          }
        })
      }
    },

    handleChromeMessage(request, sender, sendResponse) {
      switch (request.action) {
        case 'addRecommendData':
          console.log('接收到增量数据:', request)
          // 处理增量数据
          const newData = request.data.map(item => {
            return {
              ...item,
              status: 'parsing'
            }
          }) || []
          if (newData.length > 0) {
            // 将新数据添加到现有数组中
            this.recommendData.unshift(...newData)
            
            // 控制最大长度为10，移除最旧的数据
            const maxLength = 10
            if (this.recommendData.length > maxLength) {
              const removedCount = this.recommendData.length - maxLength
              this.recommendData = this.recommendData.slice(0, maxLength)
              console.log(`📊 前端数据长度超过限制，已移除 ${removedCount} 条旧数据`)
            }
            
            this.getPagerInfo().then(res => {
              this.pageInfo = res
            })
            console.log('📥 接收到增量数据，新增:', newData.length, '总计:', this.recommendData.length)
            // 处理新数据
            this.processNewData(newData)
          }
          break

        case 'devtoolsConnected':
          this.devtoolsConnected = true
          this.connectionStatus = '已连接'
          this.$notify.success(request.message)
          break

        case 'showDebuggerWarning':
          this.devtoolsConnected = false
          this.connectionStatus = '连接冲突'
          this.$notify.warning(request.message)
          break

        case 'clearRecommendData':
          this.recommendData = []
          this.expandedItems = []
          this.processedRequests.clear()
          console.log('清空推荐数据和处理记录')
          break

        case 'openAutoParamsModal':
          console.log('接收到打开AutoParams Modal请求:', request.params)
          this.openAutoParamsModal(request.params)
          break
      }
    },


    clearData() {
      this.recommendData = []
      this.expandedItems = []
      this.processedRequests.clear() // 清空已处理请求记录
      // 通知background script清空数据
      if (typeof chrome !== 'undefined' && chrome.runtime) {
        chrome.runtime.sendMessage({
          action: 'clearRecommendData'
        })
      }
    },

    // 刷新当前页面
    refreshCurrentPage() {
      if (typeof chrome !== 'undefined' && chrome.runtime) {
        chrome.runtime.sendMessage({
          action: 'refreshCurrentPage'
        }, (response) => {
          if (chrome.runtime.lastError) {
            console.error('刷新页面失败:', chrome.runtime.lastError)
            this.$notify.error({
              title: '刷新失败',
              message: '无法刷新页面，请检查扩展权限'
            })
          } else if (response && response.success) {
            console.log('页面刷新成功:', response.message)
            this.$notify.success({
              title: '刷新成功',
              message: '页面正在刷新...'
            })
          } else {
            console.error('刷新页面失败:', response.error)
            this.$notify.error({
              title: '刷新失败',
              message: response.error || '未知错误'
            })
          }
        })
      } else {
        this.$notify.error({
          title: '刷新失败',
          message: 'Chrome扩展环境不可用'
        })
      }
    },

    toggleResponse(index) {
      const expandedIndex = this.expandedItems.indexOf(index)
      if (expandedIndex > -1) {
        this.expandedItems.splice(expandedIndex, 1)
      } else {
        this.expandedItems.push(index)
      }
    },

    formatTime(timestamp) {
      if (!timestamp) return ''
      
      // 直接使用当前系统时间，避免复杂的时间戳转换
      const now = new Date()
      
      return now.toLocaleTimeString('zh-CN', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },

    checkIfInNewWindow() {
      // 检测是否在新窗口中打开
      try {

        // 方法1: 检查chrome.devtools API是否存在（最可靠的方法）
        if (typeof chrome !== 'undefined' && chrome.devtools && chrome.devtools.inspectedWindow) {
          this.isInNewWindow = false
          console.log('在Chrome扩展SidePanel中打开（通过API检测）')
          return
        }

        // 方法2: 检查URL模式 - 区分SidePanel和新窗口
        const currentUrl = window.location.href
        if (currentUrl.includes('chrome-extension://')) {
          // 检查是否是SidePanel页面
          if (currentUrl.includes('panel.html')) {
            // panel.html是SidePanel页面
            this.isInNewWindow = false
            console.log('在Chrome扩展SidePanel中打开（通过URL检测）')
            return
          } else if (currentUrl.includes('panel.html')) {
            // panel.html是新窗口页面
            this.isInNewWindow = true
            console.log('在新窗口中打开（通过URL检测）')
            return
          }
        }

        // 方法3: 检查页面标题
        if (document.title === '梦幻灵瞳') {
          // 需要进一步区分是SidePanel还是新窗口
          if (currentUrl.includes('panel.html')) {
            this.isInNewWindow = false
            console.log('在Chrome扩展SidePanel中打开（通过标题+URL检测）')
            return
          } else {
            this.isInNewWindow = true
            console.log('在新窗口中打开（通过标题检测）')
            return
          }
        }

        // 方法4: 检查是否在iframe中
        if (window.self !== window.top) {
          this.isInNewWindow = false
          console.log('在Chrome扩展SidePanel中打开（通过iframe检测）')
          return
        }

        // 方法5: 检查parent窗口
        if (window.parent === window) {
          // 顶级窗口，需要进一步判断
          if (currentUrl.includes('panel.html')) {
            this.isInNewWindow = false
            console.log('在Chrome扩展SidePanel中打开（通过parent+URL检测）')
          } else {
            this.isInNewWindow = true
            console.log('在新窗口中打开（通过parent检测）')
          }
        } else {
          this.isInNewWindow = false
          console.log('在Chrome扩展SidePanel中打开（通过parent检测）')
        }

      } catch (error) {
        console.error('检测窗口环境失败:', error)
        // 默认假设在新窗口中
        this.isInNewWindow = true
        console.log('检测失败，默认在新窗口中打开')
      }
    },

    async openInNewTab() {
      try {
        // 直接创建新标签页打开扩展页面
        const extensionUrl = chrome.runtime.getURL('panel.html')

        // 使用chrome.tabs.create在新标签页中打开
        await chrome.tabs.create({
          url: extensionUrl,
          active: true // 激活新标签页
        })

        this.$notify.success('已在新标签页中打开扩展面板')

      } catch (error) {
        console.error('打开新标签页失败:', error)

        // 如果chrome.tabs.create失败，尝试使用window.open
        try {
          const extensionUrl = chrome.runtime.getURL('panel.html')
          window.open(extensionUrl, '_blank')
          this.$notify.success('已在新窗口中打开扩展面板')
        } catch (fallbackError) {
          console.error('备用方法也失败:', fallbackError)
          this.$notify.error('打开新窗口失败: ' + error.message)
        }
      }
    },
    
    // 装备估价相关方法
    async handleEquipPrice(role) {
      const roleData = this.parserRoleData(role)
      const { using_equips, not_using_equips, split_equips, basic_info } = roleData
      const equip_list = [...using_equips, ...not_using_equips, ...split_equips].map((item) => ({ 
        ...item, 
        iType: item.type, 
        cDesc: item.desc, 
        serverid: role.serverid, 
        server_name: role.server_name 
      }))
      
      this.valuationDialogTitle = {
        nickname: basic_info.nickname,
        school: basic_info.school,
        server_name: role.server_name,
        eid: role.eid
      }

      try {
        // 先显示弹窗和骨架屏
        this.valuationDialogVisible = true
        this.valuationLoading = true
        this.valuationResults = []
        this.valuationTotalValue = 0
        this.valuationEquipmentList = equip_list
        
        // 调用批量估价API
        const response = await this.$api.equipment.batchEquipmentValuation({
          eid: role.eid,
          equipment_list: equip_list,
          strategy: 'fair_value',
          similarity_threshold: this.batchValuateParams.similarity_threshold,
          max_anchors: this.batchValuateParams.max_anchors
        })

        if (response.code === 200) {
          const data = response.data
          const results = data.results || []
          const totalValue = results.reduce((sum, result) => {
            return sum + (result.estimated_price || 0)
          }, 0)
          
          // 更新弹窗内容，显示实际数据
          this.valuationResults = results
          this.valuationTotalValue = totalValue
          this.valuationLoading = false
        } else {
          this.$notify.error({
            title: '错误',
            message: response.message || '装备估价失败'
          })
          this.closeValuationDialog()
        }
      } catch (error) {
        console.error('装备估价失败:', error)
        this.$notify.error({
          title: '错误',
          message: '装备估价失败'
        })
        this.closeValuationDialog()
      } finally {
        this.valuationLoading = false
      }
    },
    
    // 关闭装备估价结果对话框
    closeValuationDialog() {
      this.valuationDialogVisible = false
      this.valuationResults = []
      this.valuationTotalValue = 0
      this.valuationEquipmentList = []
      this.valuationDialogTitle = {}
    },
    
    // 宠物估价方法（占位符）
    handlePetPrice(role) {
      this.$notify.info({
        title: '提示',
        message: '宠物估价功能暂未实现'
      })
    },

    // AutoParams Modal相关方法
    openAutoParamsModal(params) {
      console.log('打开AutoParams Modal，参数:', params)
      this.autoParamsExternalParams = params
      this.autoParamsDialogVisible = true
    },

    closeAutoParamsDialog() {
      this.autoParamsDialogVisible = false
      this.autoParamsExternalParams = {}
    },

    // 测试添加iframe方法
    async testAddIframe() {
      try {
        // 获取当前活动标签页
        const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true })

        if (!activeTab) {
          this.$notify.warning('未找到活动标签页')
          return
        }

        // 检查数据监听连接状态
        if (!this.devtoolsConnected) {
          this.$notify.warning('数据监听连接已断开，请重新加载页面')
          return
        }

        // 通过Chrome调试API执行页面JavaScript代码添加iframe
        const result = await chrome.debugger.sendCommand(
          { tabId: activeTab.id },
          'Runtime.evaluate',
          {
            expression: `
              (function() {
                try {
                  // 创建iframe元素
                  const iframe = document.createElement('iframe')
                  iframe.src = 'https://xyq.cbg.163.com/'
                  iframe.style.width = '400px'
                  iframe.style.height = '300px'
                  iframe.style.border = '2px solid #1890ff'
                  iframe.style.borderRadius = '8px'
                  iframe.style.position = 'fixed'
                  iframe.style.top = '50px'
                  iframe.style.right = '20px'
                  iframe.style.zIndex = '9999'
                  iframe.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)'
                  
                  // 添加关闭按钮
                  const closeBtn = document.createElement('div')
                  closeBtn.innerHTML = '×'
                  closeBtn.style.position = 'absolute'
                  closeBtn.style.top = '-10px'
                  closeBtn.style.right = '-10px'
                  closeBtn.style.width = '20px'
                  closeBtn.style.height = '20px'
                  closeBtn.style.backgroundColor = '#ff4d4f'
                  closeBtn.style.color = 'white'
                  closeBtn.style.borderRadius = '50%'
                  closeBtn.style.display = 'flex'
                  closeBtn.style.alignItems = 'center'
                  closeBtn.style.justifyContent = 'center'
                  closeBtn.style.cursor = 'pointer'
                  closeBtn.style.fontSize = '14px'
                  closeBtn.style.fontWeight = 'bold'
                  closeBtn.style.zIndex = '10000'
                  
                  // 创建容器
                  const container = document.createElement('div')
                  container.style.position = 'relative'
                  container.appendChild(iframe)
                  container.appendChild(closeBtn)
                  
                  // 添加关闭事件
                  closeBtn.onclick = function() {
                    document.body.removeChild(container)
                  }
                  
                  // 添加到页面
                  document.body.appendChild(container)
                  
                  return 'SUCCESS:已添加百度iframe到页面'
                } catch (error) {
                  return 'ERROR:添加iframe失败 - ' + error.message
                }
              })()
            `
          }
        )

        // 处理Chrome调试API的返回结果
        if (result && result.result && result.result.value) {
          const message = result.result.value

          if (message.startsWith('SUCCESS:')) {
            this.$notify.success(message.substring(8)) // 移除"SUCCESS:"前缀
            console.log('iframe添加成功')
          } else if (message.startsWith('ERROR:')) {
            this.$notify.warning(message.substring(6)) // 移除"ERROR:"前缀
            console.warn('iframe添加失败:', message)
          } else {
            this.$notify.error('添加iframe失败：未知返回结果')
            console.error('iframe操作结果异常:', result)
          }
        } else {
          this.$notify.error('添加iframe失败')
          console.error('iframe操作结果异常:', result)
        }

      } catch (error) {
        console.error('添加iframe失败:', error)

        // 检查是否是连接断开错误
        if (error.message && error.message.includes('Could not establish connection')) {
          this.devtoolsConnected = false
          this.connectionStatus = '连接断开'
          this.$notify.error('数据监听连接已断开，请重新加载页面或刷新扩展')
        } else {
          this.$notify.error('操作失败: ' + error.message)
        }
      }
    }
  }
}
</script>

<style scoped>
.panel {
  box-sizing: border-box;
  padding: 16px;
  padding-bottom: 40px; /* 为底部版本栏留出空间 */
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  background: #f5f5f5;
  min-height: 100vh;
  background: url(~@/../public/assets/images/areabg.webp) repeat-y;
  width: 960px;
  margin: 0 auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e0e0e0;
}

.panel-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 4px;
  height: 4px;
  border-radius: 50%;
  display: inline-block;
  transition: all 0.3s ease;
}

.status-dot.connected {
  background-color: #52c41a;
  animation: pulse-green-strong 1.5s infinite;
}

.status-dot.disconnected {
  background-color: #faad14;
  animation: pulse-orange-strong 1s infinite;
}

/* 绿色强烈闪烁动画 */
@keyframes pulse-green-strong {
  0% {
    transform: translate(-50%, -50%) scale(1);
    box-shadow: 0 0 0 0 rgba(82, 196, 26, 0.7);
    opacity: 1;
  }

  50% {
    transform: translate(-50%, -50%) scale(1.2);
    box-shadow: 0 0 0 10px rgba(82, 196, 26, 0);
    opacity: 0.8;
  }

  100% {
    transform: translate(-50%, -50%) scale(1);
    box-shadow: 0 0 0 0 rgba(82, 196, 26, 0.7);
    opacity: 1;
  }
}

/* 橙色强烈闪烁动画 */
@keyframes pulse-orange-strong {
  0% {
    transform: translate(-50%, -50%) scale(1);
    box-shadow: 0 0 0 0 rgba(250, 173, 20, 0.7);
    opacity: 1;
  }

  25% {
    transform: translate(-50%, -50%) scale(1.3);
    box-shadow: 0 0 0 8px rgba(250, 173, 20, 0.4);
    opacity: 0.6;
  }

  50% {
    transform: translate(-50%, -50%) scale(1.1);
    box-shadow: 0 0 0 15px rgba(250, 173, 20, 0);
    opacity: 0.8;
  }

  75% {
    transform: translate(-50%, -50%) scale(1.2);
    box-shadow: 0 0 0 5px rgba(250, 173, 20, 0.2);
    opacity: 0.7;
  }

  100% {
    transform: translate(-50%, -50%) scale(1);
    box-shadow: 0 0 0 0 rgba(250, 173, 20, 0.7);
    opacity: 1;
  }
}

.status-text {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.mode-indicator {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: bold;
  margin-left: 8px;
}

.mode-indicator.sidepanel {
  background-color: #1890ff;
  color: white;
}

.mode-indicator.new-window {
  background-color: #52c41a;
  color: white;
}

.new-window-tip {
  margin-bottom: 16px;
  border-radius: 6px;
}

.new-window-tip p {
  margin: 4px 0;
  font-size: 12px;
  line-height: 1.4;
}

.sidebar-tip {
  margin-bottom: 16px;
  border-radius: 6px;
}

.sidebar-tip p {
  margin: 4px 0;
  font-size: 12px;
  line-height: 1.4;
}

.data-section h4 {
  margin: 0 0 12px 0;
  color: #666;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  background: white;
  border-radius: 4px;
  border: 1px dashed #ddd;
}

.request-list {
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  overflow: hidden;
}

.request-item {
  border-bottom: 1px solid #f0f0f0;
  padding: 12px 16px;
  transition: background-color 0.2s;
}

.request-item:last-child {
  border-bottom: none;
}

.request-item:hover {
  background-color: #fafafa;
}

.request-item.parsing {
  background-color: #f0f9ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
  }

  50% {
    box-shadow: 0 4px 16px rgba(24, 144, 255, 0.2);
  }

  100% {
    box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
  }
}

.request-info {
  margin-bottom: 8px;
}

.request-url {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: #333;
  word-break: break-all;
  margin-bottom: 4px;
}

.request-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
}

.method {
  background: #1890ff;
  color: white;
  padding: 2px 6px;
  border-radius: 2px;
  font-weight: bold;
}

.status {
  padding: 2px 6px;
  border-radius: 2px;
  font-weight: bold;
}

.status.pending {
  background: #faad14;
  color: white;
}

.status.completed {
  background: #52c41a;
  color: white;
}

.status.parsing {
  background: #1890ff;
  color: white;
}

.status.parsing .el-icon-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.status.failed {
  background: #ff4d4f;
  color: white;
}

.timestamp {
  color: #999;
}

.response-data {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.response-content {
  margin-top: 8px;
  background: #f8f8f8;
  border-radius: 4px;
  padding: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.response-content pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 11px;
  line-height: 1.4;
  color: #333;
  white-space: pre-wrap;
  word-break: break-word;
}

.role-card /deep/.el-card__body {
  padding: 8px;
}

/* 空号卡片置灰样式 */
.role-card.empty-role {
  opacity: 0.6;
  filter: grayscale(0.8);
  background-color: #f5f5f5;
  border: 1px solid #d9d9d9;
  transition: all 0.3s ease;
}

.role-card.empty-role:hover {
  opacity: 0.8;
  filter: grayscale(0.6);
}

.role-card.empty-role /deep/.el-card__body {
  background-color: #fafafa;
}

/* 空号卡片内的元素也置灰 */
.role-card.empty-role .el-tag {
  opacity: 0.7;
}

.role-card.empty-role .el-link {
  opacity: 0.7;
}

.role-card.empty-role span {
  opacity: 0.7;
}

/* 版本信息底部样式 */
.version-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  text-align: center;
  padding: 8px 0;
  font-size: 12px;
  z-index: 1000;
  border-top: 1px solid #333;
}

.version-text {
  color: #ccc;
  font-weight: 500;
}
</style>
