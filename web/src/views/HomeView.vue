<template>
  <div class="home">
    <!-- 爬虫配置区域 -->
    <el-card class="spider-config-card">
      <div slot="header" class="card-header">
        <span>🕷️ 爬虫配置</span>
      </div>

      <el-tabs v-model="activeTab" type="card" @tab-click="handleTabClick">
        <!-- 角色爬虫 -->
        <el-tab-pane label="👤 角色爬虫" name="role">
          <div class="tab-header">
            <h4>角色数据爬取</h4>
            <div class="quick-actions">
              <el-button size="mini" @click="quickConfigRole('small')">快速配置(小)</el-button>
              <el-button size="mini" @click="quickConfigRole('medium')">快速配置(中)</el-button>
              <el-button size="mini" @click="quickConfigRole('large')">快速配置(大)</el-button>
            </div>
          </div>
          <el-form :model="roleForm" label-width="100px" size="small">
            <el-form-item label="爬取页数">
              <el-input-number v-model="roleForm.max_pages" :min="1" :max="100" style="width: 100%"></el-input-number>
            </el-form-item>
            <el-form-item label="使用浏览器">
              <el-switch v-model="roleForm.use_browser" @change="onRoleBrowserToggle"></el-switch>
            </el-form-item>

            <!-- JSON参数编辑器 -->
            <div v-if="!roleForm.use_browser" class="params-editor">
                <el-button type="text" size="mini" @click="resetRoleParams">重置</el-button>
              <div class="json-editor-wrapper">
                <el-input type="textarea" v-model="roleParamsJson" placeholder="请输入角色爬虫参数JSON" :rows="8"
                  @blur="validateRoleJson" class="json-editor">
                </el-input>
                <div v-if="roleJsonError" class="json-error">
                  <i class="el-icon-warning"></i> {{ roleJsonError }}
                </div>
              </div>
            </div>

            <el-form-item label="延迟范围(秒)">
              <el-row :gutter="10">
                <el-col :span="12">
                  <el-input-number v-model="roleForm.delay_min" :min="1" :max="99"
                    style="width: 100%"></el-input-number>
                </el-col>
                <el-col :span="12">
                  <el-input-number v-model="roleForm.delay_max" :min="1" :max="99"
                    style="width: 100%"></el-input-number>
                </el-col>
              </el-row>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="startRoleSpider" :loading="isRunning" style="width: 100%">
                启动角色爬虫
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 装备爬虫 -->
        <el-tab-pane label="⚔️ 装备爬虫" name="equip">
          <div class="tab-header">
            <h4>装备数据爬取</h4>
            <div class="quick-actions">
              <el-button size="mini" @click="quickConfigEquip('small')">快速配置(小)</el-button>
              <el-button size="mini" @click="quickConfigEquip('medium')">快速配置(中)</el-button>
              <el-button size="mini" @click="quickConfigEquip('large')">快速配置(大)</el-button>
            </div>
          </div>
          <el-form :model="equipForm" label-width="100px" size="small">
            <el-form-item label="装备类型">
              <el-select v-model="equipForm.equip_type" @change="onEquipTypeChange" style="width: 100%">
                <el-option label="普通装备" value="normal"></el-option>
                <el-option label="灵饰装备" value="lingshi"></el-option>
                <el-option label="宠物装备" value="pet"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="爬取页数">
              <el-input-number v-model="equipForm.max_pages" :min="1" :max="100" style="width: 100%"></el-input-number>
            </el-form-item>
            <el-form-item label="使用浏览器">
              <el-switch v-model="equipForm.use_browser" @change="onEquipBrowserToggle"></el-switch>
            </el-form-item>

            <!-- JSON参数编辑器 -->
            <div v-if="!equipForm.use_browser" class="params-editor">
              <el-button type="text" size="mini" @click="resetEquipParams">重置</el-button>
              <div class="json-editor-wrapper">
                <el-input type="textarea" v-model="equipParamsJson" placeholder="请输入装备爬虫参数JSON" :rows="10"
                  @blur="validateEquipJson" class="json-editor">
                </el-input>
                <div v-if="equipJsonError" class="json-error">
                  <i class="el-icon-warning"></i> {{ equipJsonError }}
                </div>
              </div>
            </div>

            <el-form-item label="延迟范围(秒)">
              <el-row :gutter="10">
                <el-col :span="12">
                  <el-input-number v-model="equipForm.delay_min" :min="1" :max="99"
                    style="width: 100%"></el-input-number>
                </el-col>
                <el-col :span="12">
                  <el-input-number v-model="equipForm.delay_max" :min="1" :max="99"
                    style="width: 100%"></el-input-number>
                </el-col>
              </el-row>
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="startEquipSpider" :loading="isRunning" style="width: 100%">
                启动装备爬虫
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 召唤兽爬虫 -->
        <el-tab-pane label="🐲 召唤兽爬虫" name="pet">
          <div class="tab-header">
            <h4>召唤兽数据爬取</h4>
            <div class="quick-actions">
              <el-button size="mini" @click="quickConfigPet('small')">快速配置(小)</el-button>
              <el-button size="mini" @click="quickConfigPet('medium')">快速配置(中)</el-button>
              <el-button size="mini" @click="quickConfigPet('large')">快速配置(大)</el-button>
            </div>
          </div>
          <el-form :model="petForm" label-width="100px" size="small">
            <el-form-item label="爬取页数">
              <el-input-number v-model="petForm.max_pages" :min="1" :max="100" style="width: 100%"></el-input-number>
            </el-form-item>
            <el-form-item label="使用浏览器">
              <el-switch v-model="petForm.use_browser" @change="onPetBrowserToggle"></el-switch>
            </el-form-item>

            <!-- JSON参数编辑器 -->
            <div v-if="!petForm.use_browser" class="params-editor">
                <el-button type="text" size="mini" @click="resetPetParams">重置</el-button>
              <div class="json-editor-wrapper">
                <el-input type="textarea" v-model="petParamsJson" placeholder="请输入召唤兽爬虫参数JSON" :rows="8"
                  @blur="validatePetJson" class="json-editor">
                </el-input>
                <div v-if="petJsonError" class="json-error">
                  <i class="el-icon-warning"></i> {{ petJsonError }}
                </div>
              </div>
            </div>

            <el-form-item label="延迟范围(秒)">
              <el-row :gutter="10">
                <el-col :span="12">
                  <el-input-number v-model="petForm.delay_min" :min="3" :max="99" style="width: 100%"></el-input-number>
                </el-col>
                <el-col :span="12">
                  <el-input-number v-model="petForm.delay_max" :min="3" :max="99" style="width: 100%"></el-input-number>
                </el-col>
              </el-row>
            </el-form-item>
            <el-form-item>
              <el-button type="warning" @click="startPetSpider" :loading="isRunning" style="width: 100%">
                启动召唤兽爬虫
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>


    <!-- 实时日志监控 -->
    <el-card class="logs-card" v-if="true">
      <div slot="header" class="card-header">
        <span>📝 实时日志</span>
        <div>
          <el-select v-model="selectedLogFile" placeholder="选择历史日志文件" size="small"
            style="width: 200px; margin-right: 10px;" @change="onLogFileChange" clearable>
            <el-option label="当前日志" value="current"></el-option>
            <el-option v-for="file in logFiles" :key="file.name" :label="file.name" :value="file.name">
              <span style="float: left">{{ file.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">{{ file.modified }}</span>
            </el-option>
          </el-select>
          <el-button type="text" @click="refreshLogs" :loading="logsLoading" size="small">刷新</el-button>
          <el-button type="text" @click="toggleLogStream" size="small">
            {{ isLogStreaming ? '停止' : '开始' }}实时监控
          </el-button>
          <el-button type="text" @click="clearLogs" size="small">清空</el-button>
        </div>
      </div>
      <div class="status-content">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="status-item">
              <span class="status-label">状态:</span>
              <el-tag :type="getStatusType(currentTaskStatus.status)" size="medium">
                {{ taskStatusText }}
              </el-tag>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="status-item">
              <span class="status-label">进度:</span>
              <div class="progress-wrapper">
                <el-progress 
                  :percentage="currentTaskStatus.progress || 0" 
                  :stroke-width="8"
                  :show-text="true"
                  :text-inside="false">
                </el-progress>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      <div class="logs-content">
        <div class="logs-info" v-if="logsInfo">
          <el-tag size="small" type="info">{{ logsInfo.log_file }}</el-tag>
          <el-tag size="small" type="success">{{ logsInfo.total_lines }} 行</el-tag>
          <el-tag size="small" type="warning">{{ logsInfo.recent_lines }} 行显示</el-tag>
          <el-tag size="small" type="info">{{ logsInfo.last_modified }}</el-tag>
        </div>
        <div class="logs-container" ref="logsContainer">
          <div v-if="logs.length === 0" class="no-logs">
            <i class="el-icon-document"></i>
            <p>暂无日志数据</p>
          </div>
          <div v-else class="log-lines">
            <div v-for="(log, index) in logs" :key="index" class="log-line" :class="getLogLevel(log)">
              <span class="log-time">{{ getLogTime(log) }}</span>
              <span class="log-content">{{ getLogContent(log) }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 第二行 -->
    <el-row :gutter="20">
      <!-- 代理爬虫 -->
      <el-col :span="12">
        <el-card class="spider-card">
          <div slot="header" class="card-header">
            <span>🔄 代理爬虫</span>
          </div>
          <el-form :model="proxyForm" label-width="100px" size="small">
            <el-form-item label="爬取页数">
              <el-input-number v-model="proxyForm.max_pages" :min="1" :max="100" style="width: 100%"></el-input-number>
            </el-form-item>
            <el-form-item label="延迟范围(秒)">
              <el-row :gutter="10">
                <el-col :span="12">
                  <el-input-number v-model="proxyForm.delay_min" :min="1" :max="99"
                    style="width: 100%"></el-input-number>
                </el-col>
                <el-col :span="12">
                  <el-input-number v-model="proxyForm.delay_max" :min="1" :max="99"
                    style="width: 100%"></el-input-number>
                </el-col>
              </el-row>
            </el-form-item>
            <el-form-item>
              <el-button type="info" @click="startProxySpider" :loading="isRunning" style="width: 100%">
                启动代理爬虫
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 工具操作 -->
      <el-col :span="12">
        <el-card class="spider-card">
          <div slot="header" class="card-header">
            <span>🔧 工具操作</span>
          </div>
          <div class="tool-buttons">
            <el-button type="danger" @click="manageProxies" :loading="isRunning"
              style="width: 100%; margin-bottom: 10px;">
              🌐 更新代理IP池
            </el-button>
            <el-button type="primary" @click="runTest" :loading="isRunning" style="width: 100%; margin-bottom: 10px;">
              🧪 运行系统测试
            </el-button>
            <el-button type="warning" @click="stopTask" :disabled="!isRunning"
              style="width: 100%; margin-bottom: 10px;">
              ⏹️ 停止当前任务
            </el-button>
            <el-button type="danger" @click="resetTask" style="width: 100%; margin-bottom: 10px;">
              🔄 重置任务状态
            </el-button>
            <el-button type="info" @click="loadCachedParams" :loading="paramsLoading" style="width: 100%;">
              📋 刷新缓存参数
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <!-- 爬虫配置信息 -->
    <el-card class="config-card">
      <div slot="header" class="card-header">
        <span>⚙️ 爬虫配置</span>
        <el-button type="text" @click="loadConfig" :loading="configLoading">刷新配置</el-button>
      </div>
      <el-descriptions :column="2" v-loading="configLoading" size="small">
        <el-descriptions-item label="默认延迟">
          {{ config.default_delay || '1-3秒' }}
        </el-descriptions-item>
        <el-descriptions-item label="最大重试">
          {{ config.max_retries || 3 }}
        </el-descriptions-item>
        <el-descriptions-item label="超时时间">
          {{ config.timeout || '30秒' }}
        </el-descriptions-item>
        <el-descriptions-item label="用户代理">
          {{ config.user_agent ? '已配置' : '默认' }}
        </el-descriptions-item>
        <el-descriptions-item label="代理状态">
          <el-tag :type="config.proxy_enabled ? 'success' : 'info'">
            {{ config.proxy_enabled ? '已启用' : '未启用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="输出目录">
          {{ config.output_dir || './data' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      // 角色爬虫表单
      roleForm: {
        max_pages: 5,
        use_browser: false,
        delay_min: 8,
        delay_max: 20
      },
      // 装备爬虫表单
      equipForm: {
        equip_type: 'normal',
        max_pages: 5,
        use_browser: false,
        delay_min: 8,
        delay_max: 20
      },
      // 召唤兽爬虫表单
      petForm: {
        max_pages: 5,
        use_browser: false,
        delay_min: 8,
        delay_max: 20
      },
      // 代理爬虫表单
      proxyForm: {
        max_pages: 5,
        delay_min: 8,
        delay_max: 20
      },
      // JSON参数字符串
      roleParamsJson: '',
      equipParamsJson: '',
      petParamsJson: '',
      // JSON验证错误
      roleJsonError: '',
      equipJsonError: '',
      petJsonError: '',
      // 默认参数模板
      defaultParams: {
        role: {
          server_type: 3,
          search_type: 'overall_search_role',
          count: 15,
          view_loc: 'overall_search',
          level_min: 109,
          level_max: 109,
          bb_expt_gongji: 17,
          bb_expt_fangyu: 17,
          bb_expt_fashu: 17,
          bb_expt_kangfa: 17,
        },
        equip_normal: {
          level_min: 0,
          level_max: 180,
          search_type: 'overall_search_equip',
          view_loc: 'overall_search',
          server_type: 3
        },
        equip_lingshi: {
          level_min: 60,
          level_max: 160,
          search_type: 'overall_search_lingshi',
          view_loc: 'overall_search',
          server_type: 3
        },
        equip_pet: {
          level_min: 5,
          level_max: 145,
          equip_pos: '1',
          price_min: 3000,
          server_name: '进贤门',
          server_id: 77,
          areaid: 43,
          search_type: 'search_pet_equip',
          view_loc: 'search_cond'
        },
        pet: {
          level_min: 0,
          level_max: 180,
          search_type: 'overall_search_pet',
          server_type: 3,
          evol_skill_mode: 0,
          count: 15,
          view_loc: 'overall_search'
        }
      },
      // 爬虫配置
      config: {},
      // 文件列表
      items: [],
      // 加载状态
      isRunning: false,
      itemsLoading: false,
      configLoading: false,
      paramsLoading: false,
      logsLoading: false,
      // 日志相关
      logs: [],
      logsInfo: null,
      isLogStreaming: false,
      logEventSource: null,
      // Tab相关
      activeTab: 'role',
      selectedLogFile: 'current',
      logFiles: [],
      // 状态监控
      statusMonitor: null,
      taskStatus: null
    }
  },
  computed: {
    // 当前任务状态信息
    currentTaskStatus() {
      if (!this.taskStatus) {
        return {
          status: 'idle',
          message: '等待任务开始...',
          progress: 0
        }
      }
      return this.taskStatus
    },

    // 任务状态文本
    taskStatusText() {
      const status = this.currentTaskStatus.status
      const statusMap = {
        'idle': '空闲',
        'running': '运行中',
        'completed': '已完成',
        'error': '出错',
        'stopped': '已停止'
      }
      return statusMap[status] || status
    }
  },
  mounted() {
    this.loadConfig()
    this.refreshItems()
    this.initializeDefaultParams()
    this.loadLogFiles()
    // 页面加载时请求一次状态
    this.checkTaskStatus()
  },
  beforeDestroy() {
    this.stopLogStream()
    this.stopStatusMonitor()
  },
  methods: {
    // Tab切换处理
    handleTabClick(tab) {
      console.log('切换到:', tab.name)
      // 可以在这里添加tab切换时的逻辑
    },

    // 快速配置方法
    quickConfigRole(size) {
      const configs = {
        small: { max_pages: 3, delay_min: 2, delay_max: 4 },
        medium: { max_pages: 10, delay_min: 3, delay_max: 6 },
        large: { max_pages: 30, delay_min: 5, delay_max: 8 }
      }
      const config = configs[size]
      Object.assign(this.roleForm, config)
      this.$message.success(`角色爬虫已配置为${size}规模`)
    },

    quickConfigEquip(size) {
      const configs = {
        small: { max_pages: 3, delay_min: 2, delay_max: 4 },
        medium: { max_pages: 10, delay_min: 3, delay_max: 6 },
        large: { max_pages: 30, delay_min: 5, delay_max: 8 }
      }
      const config = configs[size]
      Object.assign(this.equipForm, config)
      this.$message.success(`装备爬虫已配置为${size}规模`)
    },

    quickConfigPet(size) {
      const configs = {
        small: { max_pages: 5, delay_min: 3, delay_max: 6 },
        medium: { max_pages: 50, delay_min: 6, delay_max: 9 },
        large: { max_pages: 100, delay_min: 8, delay_max: 12 }
      }
      const config = configs[size]
      Object.assign(this.petForm, config)
      this.$message.success(`召唤兽爬虫已配置为${size}规模`)
    },

    // 初始化默认参数
    initializeDefaultParams() {
      this.roleParamsJson = JSON.stringify(this.defaultParams.role, null, 2)
      this.equipParamsJson = JSON.stringify(this.defaultParams.equip_normal, null, 2)
      this.petParamsJson = JSON.stringify(this.defaultParams.pet, null, 2)
    },

    // 浏览器模式切换事件
    onRoleBrowserToggle(useBrowser) {
      if (!useBrowser) {
        this.loadCachedParams()
      }
    },

    onEquipBrowserToggle(useBrowser) {
      if (!useBrowser) {
        this.loadCachedParams()
      }
    },

    onPetBrowserToggle(useBrowser) {
      if (!useBrowser) {
        this.loadCachedParams()
      }
    },

    onEquipTypeChange() {
      // 装备类型改变时切换对应的默认参数
      if (!this.equipForm.use_browser) {
        const paramKey = `equip_${this.equipForm.equip_type}`
        if (this.defaultParams[paramKey]) {
          this.equipParamsJson = JSON.stringify(this.defaultParams[paramKey], null, 2)
          this.equipJsonError = ''
        }
      }
    },

    // JSON验证方法
    validateRoleJson() {
      this.roleJsonError = this.validateJson(this.roleParamsJson, 'role')
    },

    validateEquipJson() {
      this.equipJsonError = this.validateJson(this.equipParamsJson, 'equip')
    },

    validatePetJson() {
      this.petJsonError = this.validateJson(this.petParamsJson, 'pet')
    },

    validateJson(jsonStr, type) {
      try {
        if (!jsonStr.trim()) {
          return `${type}参数不能为空`
        }
        const parsed = JSON.parse(jsonStr)
        if (typeof parsed !== 'object' || parsed === null) {
          return 'JSON必须是一个对象'
        }
        return ''
      } catch (e) {
        return `JSON格式错误: ${e.message}`
      }
    },

    // 重置参数方法
    resetRoleParams() {
      this.roleParamsJson = JSON.stringify(this.defaultParams.role, null, 2)
      this.roleJsonError = ''
    },

    resetEquipParams() {
      const paramKey = `equip_${this.equipForm.equip_type}`
      this.equipParamsJson = JSON.stringify(this.defaultParams[paramKey], null, 2)
      this.equipJsonError = ''
    },

    resetPetParams() {
      this.petParamsJson = JSON.stringify(this.defaultParams.pet, null, 2)
      this.petJsonError = ''
    },

    // 加载缓存参数
    async loadCachedParams() {
      this.paramsLoading = true
      try {
        // 这里应该调用后端API获取缓存参数文件内容
        // 后续可以添加 this.$api.spider.getCachedParams() 接口
        this.$message.success('缓存参数已刷新')
      } catch (error) {
        this.$message.error('获取缓存参数失败: ' + error.message)
      } finally {
        this.paramsLoading = false
      }
    },

    // 启动角色爬虫
    async startRoleSpider() {
      if (this.isRunning) return

      if (!this.roleForm.use_browser && this.roleJsonError) {
        this.$message.error('请先修复JSON格式错误')
        return
      }

      try {
        const params = { ...this.roleForm }

        // 如果不使用浏览器，添加缓存参数
        if (!params.use_browser) {
          params.cached_params = JSON.parse(this.roleParamsJson)
        }

        const response = await this.$api.spider.startRole(params)
        if (response.code === 200) {
          this.$message.success('角色爬虫已启动')
          this.activeTab = 'role' // 确保切换到角色tab
          this.isRunning = true // 立即设置运行状态
          // 自动启动实时日志监控
          this.toggleLogStream()
          // 启动状态监控
          this.startStatusMonitor()
        } else {
          this.$message.error(response.message || '启动失败')
        }
      } catch (error) {
        this.$message.error('启动失败: ' + error.message)
      }
    },

    // 启动装备爬虫
    async startEquipSpider() {
      if (this.isRunning) return

      if (!this.equipForm.use_browser && this.equipJsonError) {
        this.$message.error('请先修复JSON格式错误')
        return
      }

      try {
        const params = { ...this.equipForm }

        // 如果不使用浏览器，添加缓存参数
        if (!params.use_browser) {
          params.cached_params = JSON.parse(this.equipParamsJson)
        }

        const response = await this.$api.spider.startEquip(params)
        if (response.code === 200) {
          this.$message.success(`${this.getEquipTypeName(params.equip_type)}爬虫已启动`)
          this.activeTab = 'equip' // 确保切换到装备tab
          this.isRunning = true // 立即设置运行状态
          // 自动启动实时日志监控
          this.toggleLogStream()
          // 启动状态监控
          this.startStatusMonitor()
        } else {
          this.$message.error(response.message || '启动失败')
        }
      } catch (error) {
        this.$message.error('启动失败: ' + error.message)
      }
    },

    // 启动召唤兽爬虫
    async startPetSpider() {
      if (this.isRunning) return

      if (!this.petForm.use_browser && this.petJsonError) {
        this.$message.error('请先修复JSON格式错误')
        return
      }

      try {
        const params = { ...this.petForm }

        // 如果不使用浏览器，添加缓存参数
        if (!params.use_browser) {
          params.cached_params = JSON.parse(this.petParamsJson)
        }

        const response = await this.$api.spider.startPet(params)
        if (response.code === 200) {
          this.$message.success('召唤兽爬虫已启动')
          this.activeTab = 'pet' // 确保切换到召唤兽tab
          this.isRunning = true // 立即设置运行状态
          // 自动启动实时日志监控
          this.toggleLogStream()
          // 启动状态监控
          this.startStatusMonitor()
        } else {
          this.$message.error(response.message || '启动失败')
        }
      } catch (error) {
        this.$message.error('启动失败: ' + error.message)
      }
    },

    // 启动代理爬虫
    async startProxySpider() {
      if (this.isRunning) return

      try {
        const response = await this.$api.spider.startProxy(this.proxyForm)
        if (response.code === 200) {
          this.$message.success('代理爬虫已启动')
          // 代理爬虫没有对应的tab，使用proxy类型
          this.isRunning = true
          // 自动启动实时日志监控
          this.toggleLogStream()
          // 启动状态监控
          this.startStatusMonitor()
        } else {
          this.$message.error(response.message || '启动失败')
        }
      } catch (error) {
        this.$message.error('启动失败: ' + error.message)
      }
    },

    // 管理代理
    async manageProxies() {
      if (this.isRunning) return

      try {
        const response = await this.$api.spider.manageProxy()
        if (response.code === 200) {
          this.$message.success('代理管理器已启动')
          this.isRunning = true
          // 自动启动实时日志监控
          this.toggleLogStream()
          // 启动状态监控
          this.startStatusMonitor()
        } else {
          this.$message.error(response.message || '启动失败')
        }
      } catch (error) {
        this.$message.error('启动失败: ' + error.message)
      }
    },

    // 运行测试
    async runTest() {
      if (this.isRunning) return

      try {
        const response = await this.$api.spider.runTest()
        if (response.code === 200) {
          this.$message.success('系统测试已启动')
          this.isRunning = true
          // 自动启动实时日志监控
          this.toggleLogStream()
          // 启动状态监控
          this.startStatusMonitor()
        } else {
          this.$message.error(response.message || '启动失败')
        }
      } catch (error) {
        this.$message.error('启动失败: ' + error.message)
      }
    },

    // 停止任务
    async stopTask() {
      try {
        const response = await this.$api.spider.stopTask()
        if (response.code === 200) {
          this.$message.success(response.data?.message || '任务已停止')
          this.isRunning = false
          // 停止实时日志监控
          this.stopLogStream()
          // 停止状态监控
          this.stopStatusMonitor()
        } else {
          this.$message.error(response.message || '停止失败')
        }
      } catch (error) {
        this.$message.error('停止失败: ' + error.message)
      }
    },

    // 重置任务状态
    async resetTask() {
      try {
        const response = await this.$api.spider.resetTask()
        if (response.code === 200) {
          this.$message.success(response.data?.message || '任务状态已重置')
          this.isRunning = false
          // 停止实时日志监控
          this.stopLogStream()
          // 停止状态监控
          this.stopStatusMonitor()
        } else {
          this.$message.error(response.message || '重置失败')
        }
      } catch (error) {
        this.$message.error('重置失败: ' + error.message)
      }
    },

    // 加载配置
    async loadConfig() {
      this.configLoading = true
      try {
        const response = await this.$api.spider.getConfig()
        if (response.code === 200) {
          this.config = response.data || response
        }
      } catch (error) {
        this.$message.error('获取配置失败: ' + error.message)
      } finally {
        this.configLoading = false
      }
    },

    // 刷新文件列表
    async refreshItems() {
      this.itemsLoading = true
      try {
        // 使用统一的API调用方式
        const response = await this.$api.spider.getFiles()
        if (response.code === 200) {
          this.items = response.data.items || []
        } else {
          console.error('获取文件列表失败:', response.message)
        }
      } catch (error) {
        console.error('获取文件列表失败:', error)
      } finally {
        this.itemsLoading = false
      }
    },

    // 下载文件
    downloadFile(filename) {
      // 使用正确的下载URL
      const baseURL = process.env.NODE_ENV === 'development'
        ? 'http://localhost:5000'
        : window.location.origin
      window.open(`${baseURL}/api/v1/spider/download/${filename}`)
    },

    // 获取装备类型名称
    getEquipTypeName(type) {
      const names = {
        normal: '普通装备',
        lingshi: '灵饰装备',
        pet: '宠物装备'
      }
      return names[type] || '装备'
    },

    // 日志相关方法
    async refreshLogs() {
      this.logsLoading = true
      try {
        const params = {
          lines: 100,
          type: this.selectedLogFile === 'current' ? 'current' : 'filename',
          spider_type: this.activeTab
        }

        // 如果选择了具体的文件，添加filename参数
        if (this.selectedLogFile && this.selectedLogFile !== 'current') {
          params.filename = this.selectedLogFile
        }

        const response = await this.$api.spider.getLogs(params)
        if (response.code === 200) {
          this.logs = response.data.logs || []
          this.logsInfo = response.data
          this.scrollToBottom()

          // 如果任务正在运行，解析日志计算进度
          if (this.isRunning) {
            this.parseProgressFromLogs()
          }
        } else {
          this.$message.error(response.message || '获取日志失败')
        }
      } catch (error) {
        this.$message.error('获取日志失败: ' + error.message)
      } finally {
        this.logsLoading = false
      }
    },

    toggleLogStream() {
      if (this.isLogStreaming) {
        this.stopLogStream()
        this.$message.info('实时日志监控已停止')
      } else {
        this.startLogStream()
        this.$message.success('实时日志监控已启动')
      }
    },

    startLogStream() {
      if (this.isLogStreaming) return

      try {
        this.logEventSource = this.$api.spider.streamLogs()
        this.isLogStreaming = true

        this.logEventSource.onmessage = (event) => {
          if (event.data) {
            try {
              // 尝试解析JSON数据
              const data = JSON.parse(event.data)
              if (data.log) {
                this.logs.push(data.log)
              } else if (typeof data === 'string') {
                this.logs.push(data)
              }
            } catch (e) {
              // 如果不是JSON，直接作为字符串处理
              this.logs.push(event.data)
            }

            // 保持最多1000行日志
            if (this.logs.length > 1000) {
              this.logs = this.logs.slice(-1000)
            }
            this.scrollToBottom()

            // 如果任务正在运行，解析新日志计算进度
            if (this.isRunning) {
              this.parseProgressFromLogs()
            }
          }
        }

        this.logEventSource.onerror = (error) => {
          console.error('日志流错误:', error)
          // 错误时不停止流，而是尝试重新连接
          setTimeout(() => {
            if (this.isLogStreaming) {
              this.stopLogStream()
              this.startLogStream()
            }
          }, 5000)
        }

        this.logEventSource.onopen = () => {
          console.log('日志流连接已建立')
        }

        // 只在手动启动时显示成功消息，避免页面加载时显示
        if (this.logs.length === 0) {
          this.logs.push('实时日志监控已启动，等待日志数据...')
        }

        // 显示成功消息
        this.$message.success('实时日志监控已启动')
      } catch (error) {
        console.error('启动实时日志监控失败:', error)
        // 静默处理错误，避免显示错误消息
      }
    },

    stopLogStream() {
      if (this.logEventSource) {
        try {
          this.logEventSource.close()
        } catch (e) {
          console.log('关闭日志流连接:', e)
        }
        this.logEventSource = null
      }
      this.isLogStreaming = false
    },

    clearLogs() {
      this.logs = []
      this.logsInfo = null
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.logsContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },

    getLogLevel(log) {
      if (log.includes('ERROR') || log.includes('错误')) return 'log-error'
      if (log.includes('WARNING') || log.includes('警告')) return 'log-warning'
      if (log.includes('INFO') || log.includes('信息')) return 'log-info'
      return 'log-default'
    },

    getLogTime(log) {
      // 提取日志时间戳
      const timeMatch = log.match(/(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/)
      return timeMatch ? timeMatch[1] : ''
    },

    getLogContent(log) {
      // 移除时间戳，返回日志内容
      return log.replace(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[,\d]*\s*/, '')
    },

    onLogFileChange(value) {
      this.selectedLogFile = value

      // 如果正在实时监控，停止它
      if (this.isLogStreaming) {
        this.stopLogStream()
        this.$message.info('已切换到历史日志，实时监控已停止')
      }

      // 刷新日志
      this.refreshLogs()
    },

    async loadLogFiles() {
      try {
        const response = await this.$api.spider.getLogFiles()
        if (response.code === 200) {
          this.logFiles = response.data.items || []
        } else {
          console.error('获取日志文件列表失败:', response.message)
        }
      } catch (error) {
        console.error('获取日志文件列表失败:', error)
      }
    },

    // 状态监控方法
    startStatusMonitor() {
      // 清除可能存在的旧定时器
      this.stopStatusMonitor()

      // 启动状态监控定时器
      this.statusMonitor = setInterval(async () => {
        await this.checkTaskStatus()
      }, 2000) // 每2秒检查一次状态
    },

    // 检查任务状态
    async checkTaskStatus() {
      try {
        const response = await this.$api.spider.getStatus()
        if (response.code === 200) {
          this.taskStatus = response.data
          const status = response.data.status

          // 更新运行状态
          this.isRunning = (status === 'running')

          // 如果任务正在运行，解析日志计算进度
          if (status === 'running') {
            this.parseProgressFromLogs()
          }

          // 如果任务完成或出错，显示消息并停止监控
          if (status === 'completed' || status === 'error' || status === 'stopped') {
            if (status === 'completed') {
              this.$message.success(response.data.message || '任务已完成')
              // 刷新文件列表
              this.refreshItems()
            } else if (status === 'error') {
              this.$message.error(response.data.message || '任务执行出错')
            } else if (status === 'stopped') {
              this.$message.info(response.data.message || '任务已停止')
            }

            // 停止日志流
            this.stopLogStream()

            // 停止状态监控
            this.stopStatusMonitor()
          }
        }
      } catch (error) {
        console.error('状态监控错误:', error)
      }
    },

    // 从日志解析进度 - 简化版本
    parseProgressFromLogs() {
      if (!this.logs || this.logs.length === 0) return

      let totalPages = 0
      let completedPages = 0
      let status = 'running'
      let message = '正在运行...'

      // 1. 从日志中提取最新的CBGSpider任务ID
      let latestTaskId = null
      for (let i = this.logs.length - 1; i >= 0; i--) {
        const match = this.logs[i].match(/CBGSpider_(role|equip|pet|proxy)_\d+/)
        if (match) {
          latestTaskId = match[0]
          break
        }
      }

      // 2. 过滤出当前任务的日志
      let currentTaskLogs = []
      if (latestTaskId) {
        currentTaskLogs = this.logs.filter(log => log.includes(latestTaskId))
      } else {
        // 如果没有找到任务ID，使用所有日志
        currentTaskLogs = this.logs
      }

      // 3. 从当前任务的最新日志开始解析
      for (let i = currentTaskLogs.length - 1; i >= 0; i--) {
        const log = currentTaskLogs[i]

        // 检查完成信息
        if (log.includes('爬取完成')) {
          status = 'completed'
          message = log
          break
        }

        // 检查错误信息
        if (log.includes('ERROR') || log.includes('错误') || log.includes('失败')) {
          status = 'error'
          message = log
          break
        }

        // 解析总页数
        if (log.includes('总页数:')) {
          const totalPagesMatch = log.match(/总页数:\s*(\d+)/)
          if (totalPagesMatch) {
            totalPages = parseInt(totalPagesMatch[1])
          }
        }

        // 解析页面完成信息 - 这是计算进度的关键
        // 匹配格式：第 X 页完成，获取 Y 条数据，保存 Z 条
        const pageCompleteMatch = log.match(/第\s*(\d+)\s*页完成/)
        if (pageCompleteMatch) {
          const pageNum = parseInt(pageCompleteMatch[1])
          // 更新已完成页数（取最大值）
          if (pageNum > completedPages) {
            completedPages = pageNum
            message = `第 ${completedPages} 页完成`
          }
        } else {
          // 尝试其他可能的格式
          const altPageCompleteMatch = log.match(/第\s*(\d+)\s*页.*完成/)
          if (altPageCompleteMatch) {
            const pageNum = parseInt(altPageCompleteMatch[1])
            if (pageNum > completedPages) {
              completedPages = pageNum
              message = `第 ${completedPages} 页完成`
            }
          }
        }

        // 检查初始化信息
        if (log.includes('日志系统初始化完成')) {
          status = 'initializing'
          message = '正在初始化...'
        }
      }

      // 计算进度百分比
      let progress = 0
      if (totalPages > 0 && completedPages > 0) {
        progress = Math.floor((completedPages / totalPages) * 100)
        if (status === 'completed') {
          progress = 100
        }
      }

      // 更新任务状态
      if (this.taskStatus) {
        this.taskStatus.progress = progress
        this.taskStatus.message = message
        this.taskStatus.details = {
          ...this.taskStatus.details,
          current_page: completedPages,
          total_pages: totalPages
        }

        // 如果检测到完成，更新状态
        if (status === 'completed') {
          this.taskStatus.status = 'completed'
        } else if (status === 'error') {
          this.taskStatus.status = 'error'
        }
      }
    },

    stopStatusMonitor() {
      if (this.statusMonitor) {
        clearInterval(this.statusMonitor)
        this.statusMonitor = null
      }
    },

    // 获取状态类型
    getStatusType(status) {
      const typeMap = {
        'idle': 'info',
        'running': 'primary',
        'completed': 'success',
        'error': 'danger',
        'stopped': 'warning'
      }
      return typeMap[status] || 'info'
    },

    // 获取进度状态
    getProgressStatus(status) {
      const statusMap = {
        'idle': '',
        'running': '',
        'completed': 'success',
        'error': 'exception',
        'stopped': 'warning'
      }
      return statusMap[status] || ''
    },


  }
}
</script>

<style scoped>
.home {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.spider-config-card,
.config-card,
.files-card,
.status-card {
  margin-bottom: 20px;
}

.status-content {
  padding: 10px 0;
}

.status-item {
  display: flex;
  align-items: center;
}

.status-label {
  font-weight: bold;
  margin-right: 10px;
}

.status-message {
  color: #666;
  font-size: 14px;
}

/* 进度条样式优化 */
.progress-wrapper {
  flex: 1;
  margin-left: 10px;
}

.status-item .el-progress {
  width: 100%;
}

.status-item .el-progress__text {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.status-item .el-progress-bar__outer {
  background-color: #f0f0f0;
  border-radius: 4px;
  height: 8px;
}

.status-item .el-progress-bar__inner {
  border-radius: 4px;
  transition: width 0.3s ease;
  background: linear-gradient(90deg, #409eff 0%, #67c23a 100%);
}

/* 确保进度条容器有足够空间 */
.status-item {
  display: flex;
  align-items: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.tool-buttons {
  padding: 10px 0;
}

.params-editor {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 6px;
  margin: 15px 0;
  border-left: 4px solid #409eff;
}

.params-editor .el-divider {
  margin: 0 0 15px 0;
}

.json-editor-wrapper {
  position: relative;
}

.json-editor {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.4;
}

.json-editor textarea {
  background-color: #2d3748;
  color: #e2e8f0;
  border: 1px solid #4a5568;
  border-radius: 4px;
  padding: 12px;
}

.json-editor textarea:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.json-error {
  margin-top: 8px;
  padding: 8px 12px;
  background-color: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 4px;
  color: #f56c6c;
  font-size: 12px;
  line-height: 1.4;
}

.json-error i {
  margin-right: 4px;
}

.el-form-item {
  margin-bottom: 18px;
}

.el-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s;
}

.el-card:hover {
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.spider-config-card .el-form {
  padding: 10px 0;
}

.spider-config-card .el-button {
  margin-top: 10px;
}

/* Tab样式优化 */
.spider-config-card .el-tabs__header {
  margin-bottom: 20px;
}

.spider-config-card .el-tabs__item {
  font-size: 14px;
  font-weight: 500;
}

.spider-config-card .el-tabs__item.is-active {
  color: #409eff;
  font-weight: 600;
}

.spider-config-card .el-tab-pane {
  padding: 0 10px;
}

/* Tab头部样式 */
.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.tab-header h4 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.quick-actions {
  display: flex;
  gap: 8px;
}

.quick-actions .el-button {
  font-size: 12px;
  padding: 5px 10px;
}


/* 日志相关样式 */
.logs-card {
  margin-bottom: 20px;
}

.logs-content {
  padding: 10px 0;
}

.logs-info {
  margin-bottom: 15px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.logs-container {
  height: 400px;
  overflow-y: auto;
  background-color: #1e1e1e;
  border-radius: 6px;
  padding: 15px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.4;
}

.no-logs {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
}

.no-logs i {
  font-size: 48px;
  margin-bottom: 10px;
}

.log-lines {
  display: flex;
  flex-direction: column;
}

.log-line {
  padding: 2px 0;
  display: flex;
  align-items: flex-start;
  word-break: break-all;
}

.log-time {
  color: #888;
  min-width: 150px;
  margin-right: 10px;
  flex-shrink: 0;
}

.log-content {
  color: #e2e8f0;
  flex: 1;
}

.log-error {
  background-color: rgba(245, 108, 108, 0.1);
  border-left: 3px solid #f56c6c;
  padding-left: 10px;
}

.log-error .log-content {
  color: #f56c6c;
}

.log-warning {
  background-color: rgba(230, 162, 60, 0.1);
  border-left: 3px solid #e6a23c;
  padding-left: 10px;
}

.log-warning .log-content {
  color: #e6a23c;
}

.log-info {
  background-color: rgba(64, 158, 255, 0.1);
  border-left: 3px solid #409eff;
  padding-left: 10px;
}

.log-info .log-content {
  color: #409eff;
}

.log-default .log-content {
  color: #e2e8f0;
}
</style>
