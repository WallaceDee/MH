<template>
  <div class="home">
    <el-row :gutter="20">
      <!-- 基础爬虫 -->
      <el-col :span="8">
        <el-card class="spider-card">
          <div slot="header" class="card-header">
            <span>🚀 基础爬虫</span>
          </div>
          <el-form :model="basicForm" label-width="80px">
            <el-form-item label="爬取页数">
              <el-input-number v-model="basicForm.pages" :min="1" :max="100"></el-input-number>
            </el-form-item>
            <el-form-item label="导出选项">
              <el-checkbox-group v-model="basicForm.exports">
                <el-checkbox label="excel">Excel</el-checkbox>
                <el-checkbox label="json">JSON</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="startBasicSpider" :loading="isRunning">
                启动基础爬虫
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 代理爬虫 -->
      <el-col :span="8">
        <el-card class="spider-card">
          <div slot="header" class="card-header">
            <span>🔄 代理爬虫</span>
          </div>
          <el-form :model="proxyForm" label-width="80px">
            <el-form-item label="爬取页数">
              <el-input-number v-model="proxyForm.pages" :min="1" :max="100"></el-input-number>
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="startProxySpider" :loading="isRunning">
                启动代理爬虫
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 代理管理 -->
      <el-col :span="8">
        <el-card class="spider-card">
          <div slot="header" class="card-header">
            <span>🔧 代理管理</span>
          </div>
          <p style="margin-bottom: 20px">获取和管理代理IP池</p>
          <el-button type="warning" @click="manageProxies" :loading="isRunning">
            更新代理IP
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- 任务状态 -->
    <el-card class="status-card" v-if="taskStatus.status !== 'idle'">
      <div slot="header" class="card-header">
        <span>📊 任务状态</span>
      </div>
      <div class="status-content">
        <el-alert
          :title="`状态: ${taskStatus.status}`"
          :description="taskStatus.message"
          :type="getStatusType(taskStatus.status)"
          show-icon
          :closable="false">
        </el-alert>
        <el-progress
          v-if="taskStatus.status === 'running'"
          :percentage="taskStatus.progress"
          :stroke-width="18"
          class="progress-bar">
        </el-progress>
      </div>
    </el-card>

    <!-- 文件列表 -->
    <el-card class="files-card">
      <div slot="header" class="card-header">
        <span>📁 输出内容</span>
        <el-button type="primary" size="small" @click="refreshItems">刷新</el-button>
      </div>
      <el-table :data="items" v-loading="itemsLoading">
        <el-table-column label="类型" width="70">
          <template slot-scope="scope">
            <span style="font-size: 20px;">{{ scope.row.is_dir ? '📁' : '📄' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="180"></el-table-column>
        <el-table-column prop="size" label="大小" width="100">
          <template slot-scope="scope">
            {{ scope.row.is_dir ? '-' : formatFileSize(scope.row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="modified" label="修改时间" width="180"></el-table-column>
        <el-table-column label="操作" width="100">
          <template slot-scope="scope">
            <el-button
              type="primary"
              size="mini"
              @click="downloadFile(scope.row.name)"
              :disabled="scope.row.is_dir">
              下载
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 系统信息 -->
    <el-card class="system-card">
      <div slot="header" class="card-header">
        <span>ℹ️ 系统信息</span>
      </div>
      <el-descriptions :column="1" v-loading="systemInfoLoading">
        <el-descriptions-item label="Python版本">
          {{ systemInfo.python_version ? systemInfo.python_version.split(' ')[0] : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="工作目录">
          {{ systemInfo.working_directory || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="当前时间">
          {{ systemInfo.current_time || '-' }}
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
      basicForm: {
        pages: 5,
        exports: ['excel', 'json']
      },
      proxyForm: {
        pages: 5
      },
      taskStatus: {
        status: 'idle',
        message: '',
        progress: 0
      },
      items: [],
      systemInfo: {},
      isRunning: false,
      itemsLoading: false,
      systemInfoLoading: false,
      statusTimer: null
    }
  },
  mounted() {
    this.refreshItems()
    this.loadSystemInfo()
    this.updateStatus()
  },
  beforeDestroy() {
    this.clearStatusTimer()
  },
  methods: {
    async startBasicSpider() {
      if (this.isRunning) return
      
      try {
        const response = await this.$http.post('/api/spider/start_basic_spider', {
          pages: this.basicForm.pages,
          export_excel: this.basicForm.exports.includes('excel'),
          export_json: this.basicForm.exports.includes('json')
        })
        
        if (response.data.error) {
          this.$message.error(response.data.error)
        } else {
          this.$message.success('基础爬虫已启动')
          this.startStatusMonitoring()
        }
      } catch (error) {
        this.$message.error('启动失败: ' + error.message)
      }
    },

    async startProxySpider() {
      if (this.isRunning) return
      
      try {
        const response = await this.$http.post('/api/spider/start_proxy_spider', {
          pages: this.proxyForm.pages
        })
        
        if (response.data.error) {
          this.$message.error(response.data.error)
        } else {
          this.$message.success('代理爬虫已启动')
          this.startStatusMonitoring()
        }
      } catch (error) {
        this.$message.error('启动失败: ' + error.message)
      }
    },

    async manageProxies() {
      if (this.isRunning) return
      
      try {
        const response = await this.$http.post('/api/spider/manage_proxies')
        
        if (response.data.error) {
          this.$message.error(response.data.error)
        } else {
          this.$message.success('代理管理器已启动')
          this.startStatusMonitoring()
        }
      } catch (error) {
        this.$message.error('启动失败: ' + error.message)
      }
    },

    startStatusMonitoring() {
      this.clearStatusTimer()
      this.statusTimer = setInterval(this.updateStatus, 1000)
    },

    async updateStatus() {
      try {
        const response = await this.$http.get('/api/spider/status')
        this.taskStatus = response.data
        
        this.isRunning = this.taskStatus.status === 'running'
        
        if (this.taskStatus.status !== 'running') {
          this.clearStatusTimer()
          if (this.taskStatus.status === 'completed') {
            this.refreshItems()
          }
        }
      } catch (error) {
        console.error('获取状态失败:', error)
      }
    },

    async refreshItems() {
      this.itemsLoading = true
      try {
        const response = await this.$http.get('/api/spider/files')
        this.items = response.data.items || []
      } catch (error) {
        this.$message.error('获取列表失败: ' + error.message)
      } finally {
        this.itemsLoading = false
      }
    },

    async loadSystemInfo() {
      this.systemInfoLoading = true
      try {
        const response = await this.$http.get('/api/spider/system_info')
        this.systemInfo = response.data
      } catch (error) {
        this.$message.error('获取系统信息失败: ' + error.message)
      } finally {
        this.systemInfoLoading = false
      }
    },

    downloadFile(filename) {
      window.open(`${this.$http.defaults.baseURL}/api/spider/download/${filename}`)
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },

    getStatusType(status) {
      switch (status) {
        case 'running': return 'info'
        case 'completed': return 'success'
        case 'error': return 'error'
        default: return 'info'
      }
    },

    clearStatusTimer() {
      if (this.statusTimer) {
        clearInterval(this.statusTimer)
        this.statusTimer = null
      }
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.spider-card,
.status-card,
.files-card,
.system-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.status-content {
  padding: 10px 0;
}

.progress-bar {
  margin-top: 15px;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>
