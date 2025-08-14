<template>
  <div class="home">
    <!-- 爬虫配置区域 -->
    <el-card class="spider-config-card" shadow="never">
      <div slot="header" class="card-header">
        <div><span class="emoji-icon">🤡</span> 配置</div>
      </div>
      <el-row type="flex">
        <div style="width: 140px;text-align: center;">
          <template v-if="externalParams.action">
            <el-col :span="24">
              <p class="cBlue">🎯目标：</p>
            </el-col>
            <EquipmentImage v-if="externalParams.action === 'similar_equip'" :equipment="externalParams"
              :popoverWidth="450" style="display: flex;flex-direction: column;height: 50px;width: 100%;align-items: center;" />
            <PetImage v-if="externalParams.action === 'similar_pet'" :pet="externalParams"
              :equipFaceImg="externalParams.equip_face_img" />
            <template v-if="externalParams.action">
              <el-cascader :options="server_data" size="mini" filterable v-model="server_data_value" clearable />
              <div style="display: inline-block; margin-left: 8px">
                <el-link @click="openCBGSearch" :type="isCookieValid ? 'danger' : 'info'" :style="cbgLinkStyle"
                  :disabled="!isCookieValid">
                  藏宝阁
                </el-link>
                <el-tooltip v-if="!isCookieValid" content="请先登录藏宝阁，确保Cookies有效后再使用此功能" placement="top">
                  <i class="el-icon-warning" style="color: #e6a23c; margin-left: 4px"></i>
                </el-tooltip>
              </div>
            </template>

          </template>
        </div>
        <!-- 全局设置 -->
        <el-form style="width: 100%;flex-shrink: 1;" :model="globalSettings" v-show="activeTab !== 'playwright'">
          <el-row :gutter="20">
            <el-col :span="4">
              <el-form-item label="📄 爬取页数" size="small">
                <el-input-number v-model="globalSettings.max_pages" :min="1" :max="100" controls-position="right"
                  style="width: 100%"></el-input-number>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item :label="`⏱️ 延迟范围(秒) 当前：${globalSettings.delay_min} - ${globalSettings.delay_max} 秒`"
                size="small">
                <el-slider v-model="delayRange" range show-stops :min="5" :max="30" :step="1"
                  @change="onDelayRangeChange" style="width: 100%;display: inline-block;">
                </el-slider>
              </el-form-item>
            </el-col>

          </el-row>
          <el-row>
            <el-col :span="4">
              <el-form-item label="🌐 使用浏览器" size="small">
                <el-switch v-model="globalSettings.use_browser" @change="onGlobalBrowserToggle"></el-switch>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="⚡ 快速配置" size="small" style="width: 100%;">
                <el-row type="flex"><el-button size="mini" @click="quickConfig('small')">10页</el-button>
                  <el-button size="mini" @click="quickConfig('medium')">50页</el-button>
                  <el-button size="mini" @click="quickConfig('large')">100页</el-button></el-row>
              </el-form-item></el-col>
          </el-row>
        </el-form>
      </el-row>

      <el-tabs v-model="activeTab" @tab-click="handleTabClick" tab-position="left">
        <!-- Playwright半自动收集器 -->
        <el-tab-pane label="🎯 Playwright" name="playwright">
          <el-form :model="playwrightForm" label-width="120px" size="small">
            <el-form-item label="无头模式">
              <el-switch v-model="playwrightForm.headless" @change="onHeadlessToggle"></el-switch>
              <span class="form-tip">关闭后可以看到浏览器操作过程</span>
            </el-form-item>

            <el-form-item label="目标URL">
              <el-select v-model="playwrightForm.target_url" style="width: 100%" @change="onTargetUrlChange">
                <el-option label="角色推荐搜索" value="role_recommend"></el-option>
                <el-option label="装备推荐搜索" value="equip_recommend"></el-option>
                <el-option label="宠物推荐搜索" value="pet_recommend"></el-option>
                <el-option label="自定义URL" value="custom"></el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="自定义URL" v-if="playwrightForm.target_url === 'custom'">
              <el-input v-model="playwrightForm.custom_url" placeholder="请输入完整的CBG URL" style="width: 100%">
                <template slot="prepend">https://</template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="startPlaywrightCollector" :loading="isRunning">
                🚀 启动 🎯
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <!-- 角色爬虫 -->
        <el-tab-pane label="👤 角色" name="role">

          <el-form :model="roleForm" label-width="100px" size="small">
            <!-- JSON参数编辑器 -->
            <div v-if="!globalSettings.use_browser" class="params-editor">
              <div class="params-actions">
                <el-button type="text" size="mini" @click="resetRoleParams">重置</el-button>
                <el-button type="primary" size="mini" @click="saveRoleParams" :loading="roleSaving"
                  :disabled="!!roleJsonError">
                  保存配置
                </el-button>
              </div>
              <div class="json-editor-wrapper">
                <el-input type="textarea" v-model="roleParamsJson" placeholder="请输入角色爬虫参数JSON" :rows="8"
                  @blur="validateRoleJson" class="json-editor">
                </el-input>
                <div v-if="roleJsonError" class="json-error">
                  <i class="el-icon-warning"></i> {{ roleJsonError }}
                </div>
              </div>
            </div>

            <el-form-item>
              <el-button type="primary" @click="startRoleSpider" :loading="isRunning">
                🚀 启动 👤
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 装备爬虫 -->
        <el-tab-pane label="⚔️ 装备" name="equip">
          <el-form :model="equipForm" label-width="100px" size="small">
            <el-form-item label="装备类型">
              <el-select v-model="equipForm.equip_type" @change="onEquipTypeChange" style="width: 100%">
                <el-option label="普通装备" value="normal"></el-option>
                <el-option label="灵饰装备" value="lingshi"></el-option>
                <el-option label="宠物装备" value="pet"></el-option>
              </el-select>
            </el-form-item>

            <!-- JSON参数编辑器 -->
            <div v-if="!globalSettings.use_browser" class="params-editor">
              <div class="params-actions">
                <el-button type="text" size="mini" @click="resetEquipParams">重置</el-button>
                <el-button type="primary" size="mini" @click="saveEquipParams" :loading="equipSaving"
                  :disabled="!!equipJsonError">
                  保存配置
                </el-button>
              </div>
              <div class="json-editor-wrapper" v-if="externalParams.action === 'similar_equip'">
                <el-input type="textarea" v-model="externalSearchParams" placeholder="搜索指定参数" :rows="10"
                  @blur="validateEquipJson" class="json-editor">
                </el-input>
                <div v-if="equipJsonError" class="json-error">
                  <i class="el-icon-warning"></i> {{ equipJsonError }}
                </div>
              </div>
              <div class="json-editor-wrapper">
                <el-input type="textarea" v-model="equipParamsJson" placeholder="请输入装备爬虫参数JSON" :rows="10"
                  @blur="validateEquipJson" class="json-editor">
                </el-input>
                <div v-if="equipJsonError" class="json-error">
                  <i class="el-icon-warning"></i> {{ equipJsonError }}
                </div>
              </div>
            </div>

            <el-form-item>
              <el-button type="success" @click="startEquipSpider" :loading="isRunning">
                🚀 启动 ⚔️
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 召唤兽爬虫 -->
        <el-tab-pane label="🐲 召唤兽" name="pet">
          <el-form :model="petForm" label-width="100px" size="small">
            <!-- JSON参数编辑器 -->
            <div v-if="!globalSettings.use_browser" class="params-editor">
              <div class="params-actions">
                <el-button type="text" size="mini" @click="resetPetParams">重置</el-button>
                <el-button type="primary" size="mini" @click="savePetParams" :loading="petSaving"
                  :disabled="!!petJsonError">
                  保存配置
                </el-button>
              </div>
              <div class="json-editor-wrapper" v-if="externalParams.action === 'similar_pet'">
                <el-input type="textarea" v-model="externalSearchParams" placeholder="搜索指定参数" :rows="10"
                  @blur="validateEquipJson" class="json-editor">
                </el-input>
                <div v-if="equipJsonError" class="json-error">
                  <i class="el-icon-warning"></i> {{ equipJsonError }}
                </div>
              </div>
              <div class="json-editor-wrapper">
                <el-input type="textarea" v-model="petParamsJson" placeholder="请输入召唤兽爬虫参数JSON" :rows="8"
                  @blur="validatePetJson" class="json-editor">
                </el-input>
                <div v-if="petJsonError" class="json-error">
                  <i class="el-icon-warning"></i> {{ petJsonError }}
                </div>
              </div>
            </div>

            <el-form-item>
              <el-button type="warning" @click="startPetSpider" :loading="isRunning">
                🚀 启动 🐲
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

      </el-tabs>
    </el-card>
    <!-- 实时日志监控 -->
    <el-card class="logs-card">
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
                <el-progress :percentage="currentTaskStatus.progress || 0" :stroke-width="8" :show-text="true"
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
      <!-- 工具操作 -->
      <el-col :span="24">
        <el-card class="spider-card">
          <div slot="header" class="card-header">
            <span>🔧 工具操作</span>
          </div>
          <div class="tool-buttons">
            <el-button type="danger" @click="manageProxies" :loading="isRunning">
              🌐 更新代理IP池
            </el-button>
            <el-button type="warning" @click="stopTask" :disabled="!isRunning">
              ⏹️ 停止当前任务
            </el-button>
            <el-button type="danger" @click="resetTask">
              🔄 重置任务状态
            </el-button>
            <el-button type="info" @click="loadCachedParams" :loading="paramsLoading">
              📋 刷新缓存参数
            </el-button>
            <el-button type="info" @click="startProxySpider" :loading="isRunning">
              启动代理爬虫
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import str2gbk from 'str2gbk'
import qs from 'qs'
import EquipmentImage from '@/components/EquipmentImage.vue'
import PetImage from '@/components/PetImage.vue'
const server_data_list = []
for (let key in window.server_data) {
  let [parent, children] = window.server_data[key]
  const [label, , , , value] = parent
  children = children.map(([value, label]) => ({ value, label }))
  server_data_list.push({
    label,
    value,
    children
  })
}
export default {
  name: 'HomeView',
  components: {
    EquipmentImage,
    PetImage
  },
  data() {
    return {
      server_data: server_data_list,
      // 全局设置
      globalSettings: {
        max_pages: 5,
        delay_min: 8,
        delay_max: 20,
        use_browser: false // 新增使用浏览器配置
      },
      // 延迟范围滑块
      delayRange: [8, 20],
      // 角色爬虫表单
      roleForm: {
        use_browser: false
      },
      // 装备爬虫表单
      equipForm: {
        equip_type: 'normal',
        use_browser: false
      },
      // 召唤兽爬虫表单
      petForm: {
        use_browser: false
      },
      // 代理爬虫表单
      proxyForm: {},
      // Playwright收集表单
      playwrightForm: {
        headless: false,
        target_url: 'role_recommend',
        custom_url: ''
      },
      // JSON参数字符串
      roleParamsJson: '',
      equipParamsJson: '{}',
      petParamsJson: '',
      // JSON验证错误
      roleJsonError: '',
      equipJsonError: '',
      petJsonError: '',
      // 默认参数模板（将从API动态加载）
      defaultParams: {
        role: {},
        equip_normal: {},
        equip_lingshi: {},
        equip_pet: {},
        equip_pet_equip: {},
        pet: {}
      },
      // 加载状态
      isRunning: false,
      paramsLoading: false,
      logsLoading: false,
      // 日志相关
      logs: [],
      logsInfo: null,
      isLogStreaming: false,
      logEventSource: null,
      // Tab相关
      activeTab: 'playwright',
      selectedLogFile: 'current',
      logFiles: [],
      // 状态监控
      statusMonitor: null,
      taskStatus: null,
      // 保存状态
      roleSaving: false,
      equipSaving: false,
      petSaving: false,
      // 缓存清理定时器
      cacheCleanupTimer: null,

      // 外部参数
      externalSearchParams: '{}',
      targetFeatures: {}
    }
  },
  computed: {
    externalParams() {
      const query = JSON.parse(JSON.stringify(this.$route.query))
      if (query.action === 'similar_pet') {
        query.evol_skill_list = JSON.parse(query.evol_skill_list)
        query.neidan = JSON.parse(query.neidan)
        query.equip_list = JSON.parse(query.equip_list)
        query.texing = JSON.parse(query.texing)
      }
      return query
    },
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
    },
    // 从Vuex store获取server_data_valueTODO:::::
    server_data_value: {
      get() {
        return this.$store?.state.server_data_value || {}
      },
      set(value) {
        this.$store.dispatch('setServerDataValue', value)
      }
    },
    // 检查cookies是否有效
    isCookieValid() {
      return this.$store.getters['cookie/isCookieCacheValid']
    },
    // 藏宝阁链接样式
    cbgLinkStyle() {
      return {
        color: this.isCookieValid ? '#f56c6c' : '#c0c4cc',
        cursor: this.isCookieValid ? 'pointer' : 'not-allowed',
        textDecoration: this.isCookieValid ? 'underline' : 'none'
      }
    }

  },
  watch: {
    // 监听server_data_value变化，同步到Vuex store
    server_data_value: {
      handler(newValue) {
        console.log(newValue, 'newValue')
        if (Array.isArray(newValue) && newValue.length >= 2) {
          this.$store.dispatch('setServerDataValue', newValue)
          const { server_id, areaid, server_name } = this.$store.getters.getCurrentServerData
          this.onExtractQuery({
            ...this.genarateEquipmentSearchParams(this.targetFeatures),
            server_id,
            areaid,
            server_name
          })
        }
      },
      deep: true
    }
  },
  mounted() {
    // 等待Vuex状态恢复后再执行其他操作
    this.$nextTick(() => {
      // 自动清理过期缓存
      this.$store.dispatch('cookie/cleanExpiredCache')

      // 启动缓存清理定时器（每分钟检查一次）
      this.cacheCleanupTimer = setInterval(() => {
        this.$store.dispatch('cookie/cleanExpiredCache')
      }, 60 * 1000)

      this.loadSearchParams()
      this.loadLogFiles()
      // 页面加载时请求一次状态
      this.checkTaskStatus()
      // 初始化延迟范围滑块
      this.delayRange = [this.globalSettings.delay_min, this.globalSettings.delay_max]

      this.loadExternalParams()
    })
    // 初始化时设置默认的server_data_value（如果store中没有的话）
    if (
      this.externalParams.action &&
      (!this.$store?.state.server_data_value || this.$store?.state.server_data_value.length === 0)
    ) {
      this.$store.dispatch('setServerDataValue', [43, 77])
    }
    if (this.externalParams.action) {
      this.getFeatures()
    }
  },
  beforeDestroy() {
    this.stopLogStream()
    this.stopStatusMonitor()
    // 清理缓存清理定时器
    if (this.cacheCleanupTimer) {
      clearInterval(this.cacheCleanupTimer)
    }
  },
  methods: {
    genaratePetSearchParams() {
      const searchParams = {}
      searchParams.skill = this.externalParams.all_skill.replace(/\|/g, ',')
      searchParams.texing = this.externalParams.texing?.id
      searchParams.lingxing = this.externalParams.lx
      searchParams.growth = this.externalParams.growth * 1000
      return searchParams
    },
    genarateEquipmentSearchParams({ kindid, ...features }) {
      const searchParams = {}
      if (window.is_pet_equip(kindid)) {
        searchParams.level = features.equip_level
        searchParams.speed = features.speed > 0 ? features.speed : undefined
        searchParams.shanghai = features.shanghai > 0 ? features.shanghai : undefined
        searchParams.hp = features.qixue > 0 ? features.qixue : undefined
        searchParams.fangyu = features.fangyu > 0 ? features.fangyu : undefined
        let addon_sum = 0
          ;['fali', 'liliang', 'lingli', 'minjie', 'naili'].forEach((item) => {
            searchParams[`addon_${item}`] = this.targetFeatures[`addon_${item}`] > 0 ? 1 : undefined
            if (item === 'minjie' && this.targetFeatures[`addon_${item}`] < 0) {
              searchParams.addon_minjie_reduce = this.targetFeatures[`addon_${item}`] * -1
            } else {
              addon_sum += this.targetFeatures[`addon_${item}`]
            }
          })
        searchParams.addon_sum = addon_sum > 0 ? addon_sum : undefined
        searchParams.addon_sum_min = searchParams.addon_sum
        searchParams.addon_status = features.addon_status
        if (features.fangyu > 0) {
          searchParams.equip_pos = 1
        } else if (features.speed > 0) {
          searchParams.equip_pos = 2
        } else {
          searchParams.equip_pos = 3
        }
      } else if (window.is_lingshi_equip(kindid)) {
        searchParams.kindid = kindid

        // 灵饰附加属性配置
        const { lingshi_added_attr1, lingshi_added_attr2 } = window.AUTO_SEARCH_CONFIG

        // 属性名称映射表 - 前端显示名称到后端字段名的映射
        const attr_name_map = {
          '法伤结果': '法术伤害结果',
          '法伤': '法术伤害',
          '固伤': '固定伤害',
          '法术暴击': '法术暴击等级',
          '物理暴击': '物理暴击等级',
          '封印': '封印命中等级',
          '狂暴': '狂暴等级',
          '穿刺': '穿刺等级',
          '治疗': '治疗能力',
          '伤害': '伤害',
          '速度': '速度',
          '抗法术暴击': '抗法术暴击等级',
          '抗物理暴击': '抗物理暴击等级',
          '抗封': '抵抗封印等级',
          '回复': '气血回复效果',
          '法防': '法术防御',
          '防御': '防御',
          '格挡': '格挡值',
          '气血': '气血'
        }

        // 构建属性值到搜索参数的映射
        const buildAttrValueMapping = () => {
          const mapping = {}

          // 合并两个属性配置
          const allAttrs = { ...lingshi_added_attr1, ...lingshi_added_attr2 }

          // 遍历所有属性，建立映射关系
          Object.entries(allAttrs).forEach(([value, displayName]) => {
            const backendFieldName = attr_name_map[displayName]
            if (backendFieldName) {
              mapping[backendFieldName] = value
            }
          })

          return mapping
        }

        // 处理主属性
        const processMainAttributes = () => {
          const mainAttrs = ['damage', 'defense', 'magic_damage', 'magic_defense', 'fengyin', 'fengyin', 'speed']
          mainAttrs.forEach(attr => {
            if (features[attr] && features[attr] > 0) {
              searchParams[attr] = features[attr]
            }
          })
        }

        // 处理精炼等级
        const processGemLevel = () => {
          if (features.gem_level && features.gem_level > 0) {
            searchParams.jinglian_level = features.gem_level
          }
        }

        // 处理附加属性
        const processAddedAttributes = () => {
          if (!features.attrs || !Array.isArray(features.attrs)) {
            return
          }

          const attrValueMapping = buildAttrValueMapping()
          const addedAttrsCount = {}

          // 统计每种附加属性的出现次数
          features.attrs.forEach(({ attr_type }) => {
            const searchValue = attrValueMapping[attr_type]
            if (searchValue) {
              addedAttrsCount[searchValue] = (addedAttrsCount[searchValue] || 0) + 1
            }
          })

          // 将统计结果添加到搜索参数
          Object.entries(addedAttrsCount).forEach(([value, count]) => {
            searchParams[`added_attr.${value}`] = count
          })
        }

        // 执行处理
        processMainAttributes()
        processGemLevel()
        processAddedAttributes()
      } else {
        // 装备
        searchParams.kindid = kindid
        let addon_sum = 0
          ;['moli', 'liliang', 'tizhi', 'minjie', 'naili'].forEach((item) => {
            searchParams[`addon_${item}`] = this.targetFeatures[`addon_${item}`] > 0 ? 1 : undefined
            if (item === 'minjie' && this.targetFeatures[`addon_${item}`] < 0) {
              searchParams.addon_minjie_reduce = this.targetFeatures[`addon_${item}`] * -1
            } else {
              addon_sum += this.targetFeatures[`addon_${item}`]
            }
          })
        searchParams.addon_sum = addon_sum > 0 ? addon_sum : undefined
        searchParams.addon_sum_min = searchParams.addon_sum
        if (features.equip_level) {
          searchParams.level_min = features.equip_level
          searchParams.level_max = features.equip_level * 1 + 9
        }

        if (features.suit_effect) {
          searchParams.suit_effect = features.suit_effect
        }
        if (features.special_skill) {
          searchParams.special_skill = features.special_skill
        }
        [
          'init_damage',
          'init_damage_raw',
          'init_defense',
          'init_hp',
          'init_dex',
          'init_wakan',
          'all_wakan',
          'all_damage',
          'damage'
        ].forEach((value) => {
          if (features[value]) {
            searchParams[value] = features[value]
          }
        })
      }
      return searchParams
    },
    async getFeatures() {
      const { server_id, areaid, server_name } = this.$store.getters.getCurrentServerData
      let query = {}
      if (this.externalParams.action === 'similar_equip') {
        console.log(this.externalParams.kindid * 1 || 0, 'kindid')
        await this.$api.equipment
          .extractFeatures({
            equipment_data: {
              kindid: this.externalParams.kindid * 1 || undefined,
              type: this.externalParams.type * 1 || undefined,
              large_equip_desc: this.externalParams.large_equip_desc
            },
            data_type: 'equipment'
          })
          .then((res) => {
            if (res.code === 200 && res.data.features) {
              this.targetFeatures = res.data.features
              query = this.genarateEquipmentSearchParams(res.data.features)
            }
          })
      } else if (this.externalParams.action === 'similar_pet') {
        query = this.genaratePetSearchParams()
      }
      this.onExtractQuery({
        ...query,
        server_id,
        areaid,
        server_name
      })
    },
    async openCBGSearch() {
      // 检查cookies是否有效
      const isCookieValid = this.$store.getters['cookie/isCookieCacheValid']

      if (!isCookieValid) {
        // Cookies无效，提示用户先登录
        this.$notify.warning({
          message: '请先登录藏宝阁，确保Cookies有效后再使用此功能',
          duration: 3000,
          showClose: true
        })

        // 可以在这里添加跳转到登录页面的逻辑
        // this.$router.push('/login')
        return
      }

      let prefix = ''
      let search_type = 'search_role_equip'
      let query = {}
      if (this.externalParams.action === 'similar_equip') {
        if (window.is_pet_equip(this.externalParams.kindid)) {
          // 使用Vuex store中的服务器数据
          search_type = 'search_pet_equip'
        } else if (window.is_lingshi_equip(this.externalParams.kindid)) {
          search_type = 'search_lingshi'
        } else {
          search_type += 'hide_lingshi=1&'
        }
        query = this.genarateEquipmentSearchParams(this.targetFeatures)
      } else {
        search_type = 'search_pet'
        query = this.genaratePetSearchParams()
      }
      const serverData = this.$store.getters.getCurrentServerData
      prefix = `https://xyq.cbg.163.com/cgi-bin/recommend.py?callback=Request.JSONP.request_map.request_0&_=${new Date().getTime()}&act=recommd_by_role&server_id=${serverData.server_id
        }&areaid=${serverData.areaid}&server_name=${serverData.server_name
        }&page=1&query_order=price%20ASC&view_loc=search_cond&count=15&search_type=${search_type}&`

      let target_url = prefix + qs.stringify(query)
      console.log(target_url, 'target_url')
      this.$api.spider.startPlaywright({
        headless: false,
        target_url
      })
    },
    /**
    * GBK编码的URL编码
    * @param {string} str - 要编码的字符串
    * @returns {Promise<string>} - GBK编码的URL编码字符串
    */
    encodeGBK(str) {
      if (!str) return ''

      try {
        const gbkBytes = str2gbk(str)
        // 将字节数组转换为URL编码格式
        return Array.from(gbkBytes)
          .map((b) => `%${b.toString(16).toUpperCase().padStart(2, '0')}`)
          .join('')
      } catch (error) {
        console.warn('GBK编码失败，使用UTF-8编码作为降级方案:', error)
        // 降级到UTF-8编码
        return window.encodeURI(str)
      }
    },
    onExtractQuery(query) {
      this.externalSearchParams = JSON.stringify(query, null, 2)
    },
    async loadExternalParams() {
      if (this.externalParams.activeTab) {
        this.activeTab = this.externalParams.activeTab
      }
      if (this.externalParams.equip_type) {
        this.equipForm.equip_type = this.externalParams.equip_type
      }
    },
    // Tab切换处理
    handleTabClick(tab) {
      console.log('切换到:', tab.name)
      // 可以在这里添加tab切换时的逻辑
    },

    // 快速配置方法 - 根据当前activeTab配置
    quickConfig(size) {
      const configs = {
        small: { max_pages: 10, delay_min: 10, delay_max: 15 },
        medium: { max_pages: 50, delay_min: 15, delay_max: 20 },
        large: { max_pages: 100, delay_min: 20, delay_max: 30 }
      }
      const config = configs[size]
      Object.assign(this.globalSettings, config)
      // 同步更新滑块值
      this.delayRange = [this.globalSettings.delay_min, this.globalSettings.delay_max]
    },

    // 延迟范围滑块变化处理
    onDelayRangeChange(value) {
      this.globalSettings.delay_min = value[0]
      this.globalSettings.delay_max = value[1]
    },

    // 加载搜索参数配置
    async loadSearchParams() {
      try {
        this.paramsLoading = true
        const response = await this.$api.config.getSearchParams()

        if (response.code === 200) {
          // 更新默认参数
          this.defaultParams = {
            role: response.data.role || {},
            equip_normal: response.data.equip_normal || {},
            equip_lingshi: response.data.equip_lingshi || {},
            equip_pet: response.data.equip_pet || {},
            equip_pet_equip: response.data.equip_pet_equip || {},
            pet: response.data.pet || {}
          }

          // 初始化JSON编辑器
          this.initializeDefaultParams()
        } else {
          this.$notify.error(response.message || '加载搜索参数配置失败')
          // 使用默认值
          this.initializeDefaultParams()
        }
      } catch (error) {
        console.error('加载搜索参数配置失败:', error)
        this.$notify.error('加载搜索参数配置失败: ' + error.message)
        // 使用默认值
        this.initializeDefaultParams()
      } finally {
        this.paramsLoading = false
      }
    },

    // 初始化默认参数
    initializeDefaultParams() {
      this.roleParamsJson = JSON.stringify(this.defaultParams.role, null, 2)
      // 根据当前装备类型初始化装备参数
      const equipParamKey = this.getEquipParamKey(this.equipForm.equip_type)
      this.equipParamsJson = JSON.stringify(this.defaultParams[equipParamKey], null, 2)
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

    // Playwright收集相关方法
    onHeadlessToggle(headless) {
      if (headless) {
        this.$notify.info({
          title: '无头模式',
          message: '浏览器将在后台运行，不会显示界面'
        })
      } else {
        this.$notify.info({
          title: '有头模式',
          message: '浏览器将显示界面，可以看到操作过程'
        })
      }
    },

    onTargetUrlChange(value) {
      if (value === 'custom') {
        this.playwrightForm.custom_url = ''
      }
    },

    onEquipTypeChange() {
      // 装备类型改变时切换对应的默认参数
      if (!this.equipForm.use_browser) {
        const paramKey = this.getEquipParamKey(this.equipForm.equip_type)
        if (this.defaultParams[paramKey]) {
          this.equipParamsJson = JSON.stringify(this.defaultParams[paramKey], null, 2)
          this.equipJsonError = ''
        }
      }
    },

    // 获取装备参数键
    getEquipParamKey(equipType) {
      const paramKeyMap = {
        normal: 'equip_normal',
        lingshi: 'equip_lingshi',
        pet: 'equip_pet_equip'  // 修复：宠物装备应该使用equip_pet_equip
      }
      return paramKeyMap[equipType] || 'equip_normal'
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
      const paramKey = this.getEquipParamKey(this.equipForm.equip_type)
      this.equipParamsJson = JSON.stringify(this.defaultParams[paramKey], null, 2)
      this.equipJsonError = ''
    },

    resetPetParams() {
      this.petParamsJson = JSON.stringify(this.defaultParams.pet, null, 2)
      this.petJsonError = ''
    },

    // 保存参数方法
    async saveRoleParams() {
      if (this.roleJsonError) {
        this.$notify.error('请先修复JSON格式错误')
        return
      }

      this.roleSaving = true
      try {
        const params = JSON.parse(this.roleParamsJson)
        const response = await this.$api.config.updateSearchParam('role', params)

        if (response.code === 200) {
          this.$notify.success('角色参数配置保存成功')
          // 更新本地默认参数
          this.defaultParams.role = params
        } else {
          this.$notify.error({
            title: '保存失败',
            message: response.message || '保存失败'
          })
        }
      } catch (error) {
        console.error('保存角色参数失败:', error)
        this.$notify.error({
          title: '保存失败',
          message: '保存失败: ' + error.message
        })
      } finally {
        this.roleSaving = false
      }
    },

    async saveEquipParams() {
      if (this.equipJsonError) {
        this.$notify.error('请先修复JSON格式错误')
        return
      }

      this.equipSaving = true
      try {
        const params = JSON.parse(this.equipParamsJson)
        const paramType = this.getEquipParamKey(this.equipForm.equip_type)
        const response = await this.$api.config.updateSearchParam(paramType, params)

        if (response.code === 200) {
          this.$notify.success(`${this.getEquipTypeName(this.equipForm.equip_type)}参数配置保存成功`)
          // 更新本地默认参数
          this.defaultParams[paramType] = params
        } else {
          this.$notify.error({
            title: '保存失败',
            message: response.message || '保存失败'
          })
        }
      } catch (error) {
        console.error('保存装备参数失败:', error)
        this.$notify.error({
          title: '保存失败',
          message: '保存失败: ' + error.message
        })
      } finally {
        this.equipSaving = false
      }
    },

    async savePetParams() {
      if (this.petJsonError) {
        this.$notify.error('请先修复JSON格式错误')
        return
      }

      this.petSaving = true
      try {
        const params = JSON.parse(this.petParamsJson)
        const response = await this.$api.config.updateSearchParam('pet', params)

        if (response.code === 200) {
          this.$notify.success('宠物参数配置保存成功')
          // 更新本地默认参数
          this.defaultParams.pet = params
        } else {
          this.$notify.error({
            title: '保存失败',
            message: response.message || '保存失败'
          })
        }
      } catch (error) {
        console.error('保存宠物参数失败:', error)
        this.$notify.error({
          title: '保存失败',
          message: '保存失败: ' + error.message
        })
      } finally {
        this.petSaving = false
      }
    },

    // 加载缓存参数
    async loadCachedParams() {
      try {
        await this.loadSearchParams()
        this.$notify.success({
          title: '缓存参数',
          message: '缓存参数已刷新'
        })
      } catch (error) {
        this.$notify.error({
          title: '获取失败',
          message: '获取缓存参数失败: ' + error.message
        })
      }
    },

    // 启动角色爬虫
    async startRoleSpider() {
      if (this.isRunning) return

      if (!this.globalSettings.use_browser && this.roleJsonError) {
        this.$notify.error('请先修复JSON格式错误')
        return
      }

      try {
        const params = {
          ...this.globalSettings, // 使用全局设置
          ...this.roleForm // 角色爬虫特有的参数
        }

        // 如果不使用浏览器，添加缓存参数
        if (!params.use_browser) {
          params.cached_params = JSON.parse(this.roleParamsJson)
        }

        const response = await this.$api.spider.startRole(params)
        if (response.code === 200) {
          this.$notify.success({
            title: '爬虫启动',
            message: '角色爬虫已启动'
          })
          this.activeTab = 'role' // 确保切换到角色tab
          this.isRunning = true // 立即设置运行状态
          // 自动启动实时日志监控
          this.toggleLogStream()
          // 启动状态监控
          this.startStatusMonitor()
        } else {
          this.$notify.error({
            title: '启动失败',
            message: response.message || '启动失败'
          })
        }
      } catch (error) {
        this.$notify.error({
          title: '启动失败',
          message: '启动失败: ' + error.message
        })
      }
    },

    // 启动装备爬虫
    async startEquipSpider() {
      if (this.isRunning) return

      if (!this.equipForm.use_browser && this.equipJsonError) {
        this.$notify.error('请先修复JSON格式错误')
        return
      }

      try {
        const params = {
          ...this.equipForm,
          ...this.globalSettings // 使用全局设置
        }

        // 如果不使用浏览器，添加缓存参数
        if (!params.use_browser) {
          params.cached_params = Object.assign(JSON.parse(this.equipParamsJson), JSON.parse(this.externalSearchParams))
        }

        const response = await this.$api.spider.startEquip(params)
        if (response.code === 200) {
          this.$notify.success({
            title: '爬虫启动',
            message: `${this.getEquipTypeName(this.equipForm.equip_type)}爬虫已启动`
          })
          this.activeTab = 'equip' // 确保切换到装备tab
          this.isRunning = true // 立即设置运行状态
          // 自动启动实时日志监控
          this.toggleLogStream()
          // 启动状态监控
          this.startStatusMonitor()
        } else {
          this.$notify.error({
            title: '启动失败',
            message: response.message || '启动失败'
          })
        }
      } catch (error) {
        this.$notify.error({
          title: '启动失败',
          message: '启动失败: ' + error.message
        })
      }
    },

    // 启动召唤兽爬虫
    async startPetSpider() {
      if (this.isRunning) return

      if (!this.petForm.use_browser && this.petJsonError) {
        this.$notify.error('请先修复JSON格式错误')
        return
      }

      try {
        const params = {
          ...this.petForm,
          ...this.globalSettings // 使用全局设置
        }

        // 如果不使用浏览器，添加缓存参数
        if (!params.use_browser) {
          params.cached_params = JSON.parse(this.petParamsJson)
        }

        const response = await this.$api.spider.startPet(params)
        if (response.code === 200) {
          this.$notify.success({
            title: '爬虫启动',
            message: '召唤兽爬虫已启动'
          })
          this.activeTab = 'pet' // 确保切换到召唤兽tab
          this.isRunning = true // 立即设置运行状态
          // 自动启动实时日志监控
          this.toggleLogStream()
          // 启动状态监控
          this.startStatusMonitor()
        } else {
          this.$notify.error({
            title: '启动失败',
            message: response.message || '启动失败'
          })
        }
      } catch (error) {
        this.$notify.error({
          title: '启动失败',
          message: '启动失败: ' + error.message
        })
      }
    },

    // 启动代理爬虫
    async startProxySpider() {
      if (this.isRunning) return

      try {
        const params = {
          ...this.proxyForm,
          ...this.globalSettings // 使用全局设置
        }

        const response = await this.$api.spider.startProxy(params)
        if (response.code === 200) {
          this.$notify.success({
            title: '爬虫启动',
            message: '代理爬虫已启动'
          })
          // 代理爬虫没有对应的tab，使用proxy类型
          this.isRunning = true
          // 自动启动实时日志监控
          this.toggleLogStream()
          // 启动状态监控
          this.startStatusMonitor()
        } else {
          this.$notify.error({
            title: '启动失败',
            message: response.message || '启动失败'
          })
        }
      } catch (error) {
        this.$notify.error({
          title: '启动失败',
          message: '启动失败: ' + error.message
        })
      }
    },

    // 启动Playwright收集
    async startPlaywrightCollector() {
      if (this.isRunning) return

      try {
        const params = {
          headless: this.playwrightForm.headless
          // 不传递target_url，使用后端默认值
        }

        console.log('启动Playwright收集，参数:', params)

        const response = await this.$api.spider.startPlaywright(params)
        if (response.code === 200) {
          this.$notify.success('Playwright收集已启动')
          this.activeTab = 'playwright'
          this.isRunning = true
          // 自动启动实时日志监控
          this.toggleLogStream()
          // 启动状态监控
          this.startStatusMonitor()
        } else {
          this.$notify.error(response.message || '启动失败')
        }
      } catch (error) {
        this.$notify.error('启动失败: ' + error.message)
      }
    },

    // 管理代理
    async manageProxies() {
      if (this.isRunning) return

      try {
        const response = await this.$api.spider.manageProxy()
        if (response.code === 200) {
          this.$notify.success('代理管理器已启动')
          this.isRunning = true
          // 自动启动实时日志监控
          this.toggleLogStream()
          // 启动状态监控
          this.startStatusMonitor()
        } else {
          this.$notify.error(response.message || '启动失败')
        }
      } catch (error) {
        this.$notify.error('启动失败: ' + error.message)
      }
    },
    // 停止任务
    async stopTask() {
      try {
        const response = await this.$api.spider.stopTask()
        if (response.code === 200) {
          this.$notify.success(response.data?.message || '任务已停止')
          this.isRunning = false
          // 停止实时日志监控
          this.stopLogStream()
          // 停止状态监控
          this.stopStatusMonitor()
        } else {
          this.$notify.error(response.message || '停止失败')
        }
      } catch (error) {
        this.$notify.error('停止失败: ' + error.message)
      }
    },

    // 重置任务状态
    async resetTask() {
      try {
        const response = await this.$api.spider.resetTask()
        if (response.code === 200) {
          this.$notify.success(response.data?.message || '任务状态已重置')
          this.isRunning = false
          // 停止实时日志监控
          this.stopLogStream()
          // 停止状态监控
          this.stopStatusMonitor()
        } else {
          this.$notify.error(response.message || '重置失败')
        }
      } catch (error) {
        this.$notify.error('重置失败: ' + error.message)
      }
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
          this.$notify.error(response.message || '获取日志失败')
        }
      } catch (error) {
        this.$notify.error('获取日志失败: ' + error.message)
      } finally {
        this.logsLoading = false
      }
    },

    toggleLogStream() {
      if (this.isLogStreaming) {
        this.stopLogStream()
        this.$notify.info('实时日志监控已停止')
      } else {
        this.startLogStream()
        this.$notify.success('实时日志监控已启动')
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
        this.$notify.success('实时日志监控已启动')
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
        this.$notify.info('已切换到历史日志，实时监控已停止')
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
            if (status === 'error') {
              this.$notify.error(response.data.message || '任务执行出错')
            } else if (status === 'stopped') {
              this.$notify.info(response.data.message || '任务已停止')
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

    // 从日志解析进度 - 精简版，直接正则提取进度百分比
    parseProgressFromLogs() {
      if (!this.logs || this.logs.length === 0) return

      let progress = 0
      let message = '正在运行...'
      let status = 'running'

      // 从后往前找最新的进度日志
      for (let i = this.logs.length - 1; i >= 0; i--) {
        const log = this.logs[i]

        // 匹配进度百分比
        const progressMatch = log.match(/进度\[(\d+)%\]/)
        if (progressMatch) {
          progress = parseInt(progressMatch[1])
          message = log
          break
        }

        // 检查完成信息
        if (log.includes('爬取完成')) {
          status = 'completed'
          message = log
          progress = 100
          break
        }

        // 检查错误信息
        if (log.includes('ERROR') || log.includes('错误') || log.includes('失败')) {
          status = 'error'
          message = log
          break
        }
      }

      // 更新任务状态
      if (this.taskStatus) {
        this.taskStatus.progress = progress
        this.taskStatus.message = message

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

    // 应用全局设置到所有爬虫
    async applyGlobalSettings() {
      this.$notify.info('正在应用全局设置到所有爬虫...')

      try {
        // 更新角色参数
        if (this.defaultParams.role) {
          this.defaultParams.role.max_pages = this.globalSettings.max_pages
          this.defaultParams.role.delay_min = this.globalSettings.delay_min
          this.defaultParams.role.delay_max = this.globalSettings.delay_max
          await this.saveRoleParams()
        }

        // 更新所有装备类型参数
        const equipTypes = ['equip_normal', 'equip_lingshi', 'equip_pet_equip']
        for (const equipType of equipTypes) {
          if (this.defaultParams[equipType]) {
            this.defaultParams[equipType].max_pages = this.globalSettings.max_pages
            this.defaultParams[equipType].delay_min = this.globalSettings.delay_min
            this.defaultParams[equipType].delay_max = this.globalSettings.delay_max

            // 保存到后端
            const response = await this.$api.config.updateSearchParam(equipType, this.defaultParams[equipType])
            if (response.code !== 200) {
              console.warn(`保存${equipType}参数失败:`, response.message)
            }
          }
        }

        // 更新宠物参数
        if (this.defaultParams.pet) {
          this.defaultParams.pet.max_pages = this.globalSettings.max_pages
          this.defaultParams.pet.delay_min = this.globalSettings.delay_min
          this.defaultParams.pet.delay_max = this.globalSettings.delay_max
          await this.savePetParams()
        }

        // 重新初始化JSON编辑器
        this.initializeDefaultParams()

        this.$notify.success('全局设置已应用到所有爬虫！')
      } catch (error) {
        console.error('应用全局设置失败:', error)
        this.$notify.error('应用全局设置失败: ' + error.message)
      }
    },

    // 重置全局设置为默认值
    resetGlobalSettings() {
      this.globalSettings = {
        max_pages: 5,
        delay_min: 8,
        delay_max: 20,
        use_browser: false
      }
      this.$notify.info('全局设置已重置为默认值')
    },

    // 全局使用浏览器模式切换
    onGlobalBrowserToggle(useBrowser) {
      // 如果全局使用浏览器，则所有爬虫都使用浏览器
      if (useBrowser) {
        this.roleForm.use_browser = true
        this.equipForm.use_browser = true
        this.petForm.use_browser = true
        this.loadCachedParams() // 加载缓存参数
      } else {
        // 如果全局不使用浏览器，则所有爬虫都不使用浏览器
        this.roleForm.use_browser = false
        this.equipForm.use_browser = false
        this.petForm.use_browser = false
        this.loadCachedParams() // 加载缓存参数
      }
    },
  }
}
</script>

<style scoped>
/* 卡片样式 */
.spider-config-card,
.logs-card,
.spider-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

/* 状态区域样式 */
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

/* 进度条样式 */
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

/* 工具按钮区域 */
.tool-buttons {
  padding: 10px 0;
}

/* 参数编辑器样式 */
.params-editor {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 6px;
  margin: 15px 0;
  border-left: 4px solid #409eff;
}

.params-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
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

/* 日志相关样式 */
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

/* 表单提示样式 */
.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

/* 图标和颜色样式 */
.emoji-icon {
  font-size: 18px;
  margin-right: 5px;
}

.cBlue {
  color: #409eff;
  font-weight: bold;
}
</style>
