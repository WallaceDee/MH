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
        <div style="margin-left: auto; display: flex; align-items: center; gap: 10px;">
          <el-dropdown v-if="userInfo" @command="handleUserCommand">
            <span style="color: #fff; cursor: pointer;">
              <i class="el-icon-user"></i> {{ userInfo.username }}
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
          <a v-else href="javascript:void 0;" class=" btn1 js_alert_btn_0"
          @click="showLoginModal = true">登录</a>
        </div>
        <i class="el-icon-full-screen  btn1 js_alert_btn_0" style="color:#fff;line-height: 26px;" v-if="!isInNewWindow"
          href="javascript:void 0;" @click.prevent="openInNewTab"></i>
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
        <a v-if="!pageInfo.hasPager" href="javascript:void 0;" class=" btn1 js_alert_btn_0"
          @click.prevent="refreshCurrentPage">刷新页面</a>
        <a v-if="hasAnyRequestData" href="javascript:void 0;" class=" btn1 js_alert_btn_0"
          @click.prevent="clearData">清空数据</a>
      </div>
    </div>
    <div class="data-section">
      <el-empty v-if="!hasAnyRequestData" class="empty-state" description="暂无数据，请访问梦幻西游藏宝阁页面"></el-empty>
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
              <span class="timestamp">{{ formatTime(item.receivedTime || item.timestamp) }}</span>
            </div>
          </div>
          <div class="response-data">
            <!-- 角色数据渲染 -->
            <el-row :gutter="4">
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
                          <el-tag @click="$auth(handleEquipPrice, role)" style="cursor: pointer;"
                            v-if="get_equip_num(parserRoleData(role)) > 0">
                            ⚔️ {{ get_equip_num(parserRoleData(role)) }}
                          </el-tag>
                          <el-tag type="success" @click="$auth(handlePetPrice, role)" style="cursor: pointer;"
                            v-if="get_pet_num(parserRoleData(role)) > 0">
                            🐲 {{ get_pet_num(parserRoleData(role)) }}
                          </el-tag>
                        </template>
                      </div>

                    </el-col>
                  </el-row>
                  <div>
                    <SimilarRoleModal :disabled="item.status !== 'completed'" :role="{ ...role, roleInfo: parserRoleData(role) }"
                      :search-params="{ selectedDate: selectedDate, roleType: 'normal' }">
                      <div> <el-link type="primary" href="javascript:void 0;" @click.prevent
                          :disabled="item.status !== 'completed'">裸号估价</el-link></div>
                    </SimilarRoleModal>
                  </div>
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

    <!-- 宠物估价结果对话框 -->
    <el-dialog :visible.sync="petValuationDialogVisible" width="1000px" :close-on-click-modal="false"
      :close-on-press-escape="false" custom-class="batch-valuation-dialog">
      <span slot="title" class="el-dialog__title">
        <el-tag size="mini">{{ petValuationDialogTitle.server_name }}</el-tag>
        /
        <el-tag type="info" size="mini">{{ petValuationDialogTitle.school }}</el-tag>/
        <el-link :href="getCBGLinkByType(petValuationDialogTitle.eid)" target="_blank">{{ petValuationDialogTitle.nickname
          }}</el-link>
      </span>
      <PetBatchValuationResult :results="petValuationResults" :total-value="petValuationTotalValue"
        :pet-list="petValuationPetList" :loading="petValuationLoading"  :valuate-params="{
        similarity_threshold: 0.8,
        max_anchors: 30,
        serverid: undefined,
        server_name: undefined
      }" 
        @close="closePetValuationDialog" />
    </el-dialog>
    
    <!-- 登录模态框 -->
    <LoginModal v-model="showLoginModal" @login-success="handleLoginSuccess" />
  </div>
</template>
<script>
import dayjs from 'dayjs'
import RoleImage from '@/components/RoleInfo/RoleImage.vue'
import SimilarRoleModal from '@/components/SimilarRoleModal.vue'
import LoginModal from './LoginModal.vue'
import { initAuthToken, clearAuthToken } from '@/utils/request'
import { api } from '@/utils/request'
import EquipBatchValuationResult from '@/components/EquipBatchValuationResult.vue'
import PetBatchValuationResult from '@/components/PetBatchValuationResult.vue'
import EquipmentImage from '@/components/EquipmentImage/EquipmentImage.vue'
import { commonMixin } from '@/utils/mixins/commonMixin'
import { equipmentMixin } from '@/utils/mixins/equipmentMixin'
import { petMixin } from '@/utils/mixins/petMixin'
import { authMixin } from '@/utils/mixins/authMixin'
import { initFingerprintCookie } from '@/utils/request'
const ROLE_KINDIDS = ['27', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '49', '51', '50', '77', '78', '79', '81', '82']
const PET_KINDIDS = ['1', '65', '66', '67', '68', '69', '70', '71', '75', '80']
const EQUIP_KINDIDS = ['2', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '17', '18', '19', '20', '21', '26', '28', '29', '42', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '72', '73', '74', '83']
export default {
  name: 'DevToolsPanel',
  data() {
    return {
      isSidePanel: true,
      showLoginModal: false,
      userInfo: null,
      pageInfo: {
        hasPager: false,
        currentPage: 0,
        total: 0,
        hasPrev: false,
        hasNext: false
      },
      selectedDate: dayjs().format('YYYY-MM'),
      equipsAndPets: [],
      recommendData: [],
      expandedItems: [],
      processedRequests: new Set(), // 记录已处理的请求ID
      devtoolsConnected: false, // 数据监听连接状态
      connectionStatus: '检查中...', // 连接状态描述
      connectionCheckTimer: null, // 连接检查定时器
      windowWidth: 0, // 窗口宽度，用于响应式判断

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

      // 宠物估价相关数据
      petValuationDialogVisible: false,
      petValuationResults: [],
      petValuationTotalValue: 0,
      petValuationPetList: [],
      petValuationLoading: false,
      petValuationDialogTitle: {},
      batchPetValuateParams: {
        similarity_threshold: 0.7,
        max_anchors: 30
      },
    }
  },
  mixins: [commonMixin, equipmentMixin, petMixin, authMixin],
  components: {
    LoginModal,
    RoleImage,
    SimilarRoleModal,
    EquipBatchValuationResult,
    PetBatchValuationResult,
    EquipmentImage
  },
  computed: {
    // 判断是否在新窗口中打开（基于窗口宽度）
    // 宽度 > 960：新窗口/标签页
    // 宽度 <= 960：SidePanel
    isInNewWindow() {
      return this.windowWidth > 960
    },
    hasAnyRequestData() {
      return this.recommendData.length > 0
    }
  },
  watch: {
    // 监听 equipsAndPets 数据变化，同步到 Vuex
    // DevToolsPanel 只在 Chrome 插件环境下运行，因此可以直接使用 Vuex
    equipsAndPets: {
      handler(newVal) {
        this.$store.dispatch('chromeDevtools/updateEquipsAndPetsData', newVal)
        console.log('DevToolsPanel: equipsAndPets 数据已同步到 Vuex, 数量:', newVal.length)
      },
      deep: true,
      immediate: true
    }
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

    // 初始化窗口宽度
    this.updateWindowWidth()

    // 监听窗口大小变化
    window.addEventListener('resize', this.handleWindowResize)

    // 初始化 fingerprint cookie
    initFingerprintCookie().catch(err => {
      console.error('初始化 fingerprint cookie 失败:', err)
    })
    
    // 只初始化token，不主动验证登录状态
    initAuthToken().catch(err => {
      console.error('初始化token失败:', err)
    })
    
    // 从chrome.storage获取已保存的用户信息（如果有）
    if (typeof chrome !== 'undefined' && chrome.storage) {
      chrome.storage.local.get(['user_info'], (result) => {
        if (result.user_info) {
          this.userInfo = result.user_info
        }
      })
    }
    
    // 监听需要认证的事件
    window.addEventListener('auth-required', this.handleAuthRequired)

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

    // 移除窗口大小变化监听器
    window.removeEventListener('resize', this.handleWindowResize)
    
    // 移除认证事件监听器
    window.removeEventListener('auth-required', this.handleAuthRequired)

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
    // 检查用户信息（仅在需要时调用，不主动验证）
    async checkUserInfo() {
      try {
        const response = await api.get('/auth/me')
        if (response.code === 200 && response.data.user) {
          this.userInfo = response.data.user
          // 保存到chrome.storage
          chrome.storage.local.set({ user_info: response.data.user })
          return true
        } else {
          // Token无效
          this.userInfo = null
          chrome.storage.local.remove(['user_info'])
          return false
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        this.userInfo = null
        chrome.storage.local.remove(['user_info'])
        return false
      }
    },
    
    // 处理需要认证的事件
    handleAuthRequired() {
      this.showLoginModal = true
      this.userInfo = null
    },
    
    // 处理登录成功
    handleLoginSuccess(data) {
      this.userInfo = data.user
      this.showLoginModal = false
      this.$message.success('登录成功')
    },
    
    // 处理用户命令
    handleUserCommand(command) {
      if (command === 'logout') {
        this.handleLogout()
      }
    },
    
    // 处理登出
    async handleLogout() {
      try {
        await api.post('/auth/logout')
      } catch (error) {
        console.error('登出失败:', error)
      } finally {
        clearAuthToken()
        this.userInfo = null
        this.$message.success('已退出登录')
      }
    },
    
    // 更新窗口宽度
    updateWindowWidth() {
      if (typeof window !== 'undefined') {
        this.windowWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth || 0
      }
    },

    // 处理窗口大小变化
    handleWindowResize() {
      this.updateWindowWidth()
    },

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
            // this.$notify.success(message.substring(8)) // 移除"SUCCESS:"前缀
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
    async getPageCookies({ domain = 'xyq.cbg.163.com', showToast = false } = {}) {
      try {
        const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true })

        if (!activeTab) {
          if (showToast) this.$notify.warning('未找到活动标签页')
          throw new Error('未找到活动标签页')
        }

        if (!activeTab.url || !activeTab.url.includes('cbg.163.com')) {
          if (showToast) this.$notify.warning('请先访问梦幻西游藏宝阁页面')
          throw new Error('请先访问梦幻西游藏宝阁页面')
        }

        if (!this.devtoolsConnected) {
          if (showToast) this.$notify.warning('数据监听连接已断开，请重新加载页面')
          throw new Error('数据监听连接已断开，请重新加载页面')
        }

        const result = await chrome.debugger.sendCommand(
          { tabId: activeTab.id },
          'Network.getAllCookies'
        )

        const cookies = Array.isArray(result?.cookies) ? result.cookies : []
        const filteredCookies = domain
          ? cookies.filter(cookie => cookie.domain && cookie.domain.includes(domain))
          : cookies

        if (showToast) {
          if (filteredCookies.length > 0) {
            this.$notify.success({
              title: '获取 Cookies 成功',
              message: `共获取到 ${filteredCookies.length} 个 cookies`,
              duration: 3000
            })
          } else {
            this.$notify.warning(`未获取到域名为 ${domain || '指定域名'} 的 cookies`)
          }
        }

        return filteredCookies
      } catch (error) {
        console.error('获取 Cookies 失败:', error)
        if (showToast) {
          this.$notify.error({
            title: '获取 Cookies 失败',
            message: error.message || '未知错误'
          })
        }
        return []
      }
    },
    parserRoleData(data) {
      const roleInfo = new window.RoleInfoParser(data.large_equip_desc, { equip_level: data.equip_level })
      return roleInfo.result
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
      const applyUpdate = (list) => {
        const targetIndex = list.findIndex(item => item.requestId === requestId)
        if (targetIndex !== -1) {
          this.$set(list[targetIndex], 'status', status)
          if (data && data.type) {
            this.$set(list[targetIndex], 'dataType', data.type)
            this.$set(list[targetIndex], 'requestCategory', data.type)
          }
          if (data && Object.prototype.hasOwnProperty.call(data, 'payload')) {
            this.$set(list[targetIndex], 'parsedPayload', data.payload)
          }
          return true
        }
        return false
      }

      if (applyUpdate(this.recommendData)) {
        return
      }
      applyUpdate(this.equipsAndPets)
    },
    getRequestCategoryByUrl(url) {
      if (!url || typeof url !== 'string') {
        return 'unknown'
      }
      try {
        const decodedUrl = decodeURIComponent(url)
        const lowerUrl = decodedUrl.toLowerCase()
        const contains = (value) => lowerUrl.includes(value)
        const containsAny = (values) => values.some(value => contains(value))

        if (contains('search_type=overall_search_role')) {
          return 'role'
        }
        if (contains('search_type=overall_search_pet')) {
          return 'pet'
        }
        if (containsAny(['search_type=overall_search_equip', 'search_type=overall_search_pet_equip', 'search_type=overall_search_lingshi'])) {
          return 'equipment'
        }

        if (contains('view_loc=overall_search')) {
          if (contains('search_type=overall_search_role')) {
            return 'role'
          }
          if (contains('search_type=overall_search_pet')) {
            return 'pet'
          }
          if (containsAny(['search_type=overall_search_equip', 'search_type=overall_search_pet_equip', 'search_type=overall_search_lingshi'])) {
            return 'equipment'
          }
        }

        if (contains('view_loc=reco_left')) {
          if (contains('recommend_type=1')) {
            return 'role'
          }
          if (contains('recommend_type=3')) {
            return 'pet'
          }
          if (containsAny(['recommend_type=2', 'recommend_type=4'])) {
            return 'equipment'
          }
        }

        if (contains('view_loc=equip_list')) {
          const hasKindId = (kindIds) => kindIds.some(kindid => new RegExp(`kindid=${kindid}(?:&|$)`).test(lowerUrl))
          if (hasKindId(ROLE_KINDIDS)) {
            return 'role'
          }
          if (hasKindId(PET_KINDIDS)) {
            return 'pet'
          }
          if (hasKindId(EQUIP_KINDIDS)) {
            return 'equipment'
          }
        }

        if (contains('view_loc=search_cond')) {
          if (containsAny(['search_role_equip', 'search_pet_equip', 'search_lingshi'])) {
            return 'equipment'
          }
          if (contains('search_type=search_pet')) {
            return 'pet'
          }
          if (contains('search_type=search_role')) {
            return 'role'
          }
        }

        if (contains('act=recommd_by_role')) {
          return 'role'
        }
        if (containsAny(['act=recommd_pet', 'act=recommd_by_pet'])) {
          return 'pet'
        }
        if (containsAny(['act=recommd_by_equip', 'act=recommd_lingshi', 'act=recommd_pet_equip'])) {
          return 'equipment'
        }

        console.warn('未识别的请求类型:', url)
        return 'unknown'
      } catch (error) {
        console.warn('无法解析请求类型:', url, error)
        return 'unknown'
      }
    },
    async processNewData(dataArray) {
      // 类型映射
      const typeMap = {
        'role': '角色',
        'pet': '召唤兽',
        'equipment': '装备'
      }

      // 只处理新完成的请求，避免重复处理
      if (dataArray && dataArray.length > 0) {
        const cookies = await this.getPageCookies({ showToast: false })
        dataArray.forEach(item => {
          if (item.responseData &&
            item.url &&
            item.requestId &&
            !this.processedRequests.has(item.requestId)) {

            // 标记为已处理
            this.processedRequests.add(item.requestId)
            console.log(`开始处理新请求: ${item.requestId}`)

            const requestType = item.requestCategory && item.requestCategory !== 'unknown'
              ? item.requestCategory
              : this.getRequestCategoryByUrl(item.url)

            this.$api.spider.parseResponse({
              url: item.url,
              response_text: item.responseData,
              cookies
            }).then(res => {
              console.log(`请求 ${item.requestId} 解析结果:`, res)
              if (res.code === 200) {
                const typeKey = requestType && requestType !== 'unknown' ? requestType : 'unknown'
                const typeName = typeMap[typeKey] || typeKey
                console.log(`请求 ${item.requestId} 数据类型: ${typeName}`, res.data)
                this.changeRecommendDataStatus({ requestId: item.requestId, status: 'completed', data: { type: typeKey, payload: res.data } })
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
        case 'closeSidePanel':
          // 关闭SidePanel（只能在SidePanel上下文中调用）
          if (!this.isInNewWindow) {
            try {
              window.close()
            } catch (error) {
              console.error('关闭SidePanel失败:', error)
            }
          }
          break
        case 'addRecommendData':
          console.log('接收到增量数据:', request)
          // 处理增量数据
          const categorizedData = (request.data || []).map(item => {
            const category = this.getRequestCategoryByUrl(item.url)
            return {
              ...item,
              status: 'parsing',
              requestCategory: category,
              receivedTime: Date.now() // 添加接收时间，用于显示
            }
          })

          if (categorizedData.length > 0) {
            const roleData = categorizedData.filter(item => item.requestCategory === 'role')
            const otherData = categorizedData.filter(item => item.requestCategory !== 'role')

            if (roleData.length > 0) {
              this.recommendData.unshift(...roleData)
              const maxLength = 10
              if (this.recommendData.length > maxLength) {
                const removedCount = this.recommendData.length - maxLength
                this.recommendData = this.recommendData.slice(0, maxLength)
                console.log(`📊 角色数据长度超过限制，已移除 ${removedCount} 条旧数据`)
              }
              this.getPagerInfo().then(res => {
                this.pageInfo = res
              })
              console.log('📥 接收到角色增量数据，新增:', roleData.length, '总计:', this.recommendData.length)
            }

            if (otherData.length > 0) {
              this.equipsAndPets.unshift(...otherData)
              const maxLength = 20
              if (this.equipsAndPets.length > maxLength) {
                const removedCount = this.equipsAndPets.length - maxLength
                this.equipsAndPets = this.equipsAndPets.slice(0, maxLength)
                console.log(`📊 装备/召唤兽数据超过限制，已移除 ${removedCount} 条旧数据`)
              }
              console.log('📥 接收到装备/召唤兽增量数据，新增:', otherData.length, '总计:', this.equipsAndPets.length)
            }

            const allNewData = [...roleData, ...otherData]
            if (allNewData.length > 0) {
              this.processNewData(allNewData)
            }
          }
          break

        case 'devtoolsConnected':
          this.devtoolsConnected = true
          this.connectionStatus = '已连接'
          // this.$notify.success(request.message)
          break

        case 'showDebuggerWarning':
          this.devtoolsConnected = false
          this.connectionStatus = '连接冲突'
          // this.$notify.warning(request.message)
          break

        case 'clearRecommendData':
          this.recommendData = []
          this.equipsAndPets = []
          this.processedRequests.clear()
          console.log('清空推荐数据和处理记录')
          break


      }
    },


    clearData() {
      this.recommendData = []
      this.equipsAndPets = []
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

      // Chrome DevTools Protocol 的 timestamp 是相对于进程启动时间的单调时间戳（秒）
      // 为了显示准确时间，我们在接收数据时添加了 receivedTime 字段（标准毫秒时间戳）
      // 这里优先使用 receivedTime，如果不存在则尝试处理 timestamp
      let milliseconds
      if (timestamp < 10000000000) {
        // DevTools Protocol 的时间戳（秒），转换为毫秒
        // 由于是相对时间，我们转换为绝对时间显示
        milliseconds = timestamp * 1000
      } else {
        // 标准毫秒时间戳（Date.now()）
        milliseconds = timestamp
      }

      const date = new Date(milliseconds)
      return date.toLocaleTimeString('zh-CN', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
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

        // 如果当前在SidePanel中，关闭SidePanel
        // 注意：只能在SidePanel上下文中调用window.close()
        if (!this.isInNewWindow) {
          try {
            // 延迟一下，确保新标签页已经完全打开
            setTimeout(() => {
              window.close()
            }, 100)
          } catch (closeError) {
            console.error('关闭SidePanel失败:', closeError)
          }
        }

      } catch (error) {
        console.error('打开新标签页失败:', error)

        // 如果chrome.tabs.create失败，尝试使用window.open
        try {
          const extensionUrl = chrome.runtime.getURL('panel.html')
          window.open(extensionUrl, '_blank')
          this.$notify.success('已在新窗口中打开扩展面板')

          // 如果当前在SidePanel中，关闭SidePanel
          // 注意：只能在SidePanel上下文中调用window.close()
          if (!this.isInNewWindow) {
            try {
              // 延迟一下，确保新窗口已经完全打开
              setTimeout(() => {
                window.close()
              }, 100)
            } catch (closeError) {
              console.error('关闭SidePanel失败:', closeError)
            }
          }
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

    async handlePetPrice(role) {
      let roleData = this.parserRoleData(role)
      console.log({roleData,role})
      const { pet_info, split_pets, basic_info } = roleData
      let pet_list = [...pet_info, ...split_pets]
      if (!pet_list || pet_list.length === 0) {
        this.$notify.warning({
          title: '提示',
          message: '没有可估价的宠物'
        })
        return
      }
      pet_list = pet_list.map((item) => {
        //TODO:等级
        const role_grade_limit = window.CBG_GAME_CONFIG.pet_equip_type_to_grade_mapping[item.iType]
        const all_skill = []
        for (var typeid in item.all_skills) {
          all_skill.push('' + typeid)
        }
        // 根据JavaScript逻辑计算evol_skill_list
        const evol_skill_list = this.calculateEvolSkillList(item)
        const texing = JSON.stringify(item.jinjie?.core)
        const lx = item.jinjie?.lx || 0
        const equip_list = []
        for (var i = 0; i < 3; i++) {
          var equip = item['summon_equip' + (i + 1)]
          var equip_info = window.CBG_GAME_CONFIG.equip_info[equip?.iType] || {}
          if (equip) {
            equip_list.push({
              type: equip.iType,
              desc: equip.cDesc,
              name: equip_info.name,
              icon: window.ResUrl + `/images/equip/small/${equip?.iType}.gif`,
              //lock_type: role.RoleInfoParser.get_lock_types(equip),
              static_desc: equip_info.desc?.replace(/#R/g, '<br />')
            })
          } else {
            equip_list.push(null)
          }
        }
        const neidan = []
        if (item.summon_core != undefined) {
          for (var p in item.summon_core) {
            var p_core = item.summon_core[p]
            neidan.push({
              name: window.CBG_GAME_CONFIG.pet_neidans[p] || '',
              level: p_core[0],
              isNeiDan: true
            })
          }
        }
 
        return {
          ...item,
          petData:item,
          //召唤兽特征提取必传参数
          equip_face_img:item.icon,
          role_grade_limit,
          equip_level: item.pet_grade,
          growth: item.cheng_zhang,
          evol_skill_list: JSON.stringify(evol_skill_list),
          sp_skill: item.genius,
          texing,
          lx,
          equip_list: JSON.stringify(equip_list),
          neidan: JSON.stringify(neidan),
          serverid: role.serverid,
          server_name: role.server_name
        }
      })
      this.petValuationDialogTitle = {
        nickname: basic_info.nickname,
        school: basic_info.school,
        server_name: role.server_name,
        eid: role.eid
      }

      try {
        // 先显示弹窗和骨架屏
        this.petValuationDialogVisible = true
        this.petValuationLoading = true
        this.petValuationResults = []
        this.petValuationTotalValue = 0
        this.petValuationPetList = pet_list

        // 调用批量宠物估价API
        const response = await this.$api.pet.batchPetValuation({
          eid: role.eid,
          pet_list: pet_list,
          strategy: 'fair_value',
          similarity_threshold: this.batchPetValuateParams.similarity_threshold,
          max_anchors: this.batchPetValuateParams.max_anchors
        })

        if (response.code === 200) {
          this.petValuationResults = response.data.results || []
          this.petValuationTotalValue = response.data.total_value || 0
          this.petValuationLoading = false
        } else {
          this.$notify.error({
            title: '错误',
            message: response.message || '宠物估价失败'
          })
          this.closePetValuationDialog()
        }
      } catch (error) {
        console.error('宠物估价失败:', error)
        this.$notify.error({
          title: '错误',
          message: '宠物估价失败'
      })
        this.closePetValuationDialog()
      } finally {
        this.petValuationLoading = false
      }
    },

    // 关闭宠物估价结果对话框
    closePetValuationDialog() {
      this.petValuationDialogVisible = false
      this.petValuationResults = []
      this.petValuationTotalValue = 0
      this.petValuationPetList = []
      this.petValuationDialogTitle = {}
    },
  }
}
</script>

<style scoped>
.panel {
  box-sizing: border-box;
  padding: 16px;
  padding-bottom: 40px;
  /* 为底部版本栏留出空间 */
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

</style>
