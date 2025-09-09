<template>
  <div class="devtools-panel">
    <div class="header">
      <h2>🚀 CBG爬虫助手 - Vue版本</h2>
      <p>基于Vue 2.6.14 + Element UI的DevTools面板</p>
    </div>
    
    <div class="stats-container">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-title">Vue状态</div>
            <div class="stat-value" :class="vueStatusClass">{{ vueStatus }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-title">Vue版本</div>
            <div class="stat-value">{{ vueVersion }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-title">运行时间</div>
            <div class="stat-value">{{ runtime }}秒</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-title">测试次数</div>
            <div class="stat-value">{{ testCount }}</div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="feature-section">
      <h3>🎯 功能测试</h3>
      <el-row :gutter="10">
        <el-col :span="6">
          <el-button type="primary" @click="testVueFunction" :disabled="!vueLoaded">
            测试Vue功能
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="success" @click="testDataBinding" :disabled="!vueLoaded">
            测试数据绑定
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="warning" @click="testMethodCall" :disabled="!vueLoaded">
            测试方法调用
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="danger" @click="clearLogs">
            清空日志
          </el-button>
        </el-col>
      </el-row>
    </div>

    <div class="data-section">
      <h3>📊 数据展示</h3>
      <el-card>
        <div class="data-item">
          <strong>测试数据:</strong>
          <p>计数器: {{ testData.counter }}</p>
          <p>消息: {{ testData.message }}</p>
          <p>时间: {{ testData.timestamp }}</p>
        </div>
        <div class="data-item">
          <strong>列表数据:</strong>
          <el-tag v-for="(item, index) in testData.items" :key="index" style="margin-right: 5px;">
            {{ item }}
          </el-tag>
        </div>
      </el-card>
    </div>

    <div class="log-section">
      <h3>📝 日志信息</h3>
      <el-card>
        <div class="log-container" ref="logContainer">
          <div v-for="(log, index) in logs" :key="index" :class="['log-entry', log.type]">
            <span class="log-time">[{{ log.time }}]</span>
            <span class="log-type">{{ log.type }}:</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
          <div v-if="logs.length === 0" class="no-logs">
            暂无日志信息...
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DevToolsPanel',
  data() {
    return {
      vueLoaded: false,
      vueVersion: '未知',
      startTime: Date.now(),
      testCount: 0,
      testData: {
        counter: 0,
        message: 'Hello Vue!',
        timestamp: '',
        items: ['项目1', '项目2', '项目3']
      },
      logs: []
    }
  },
  computed: {
    vueStatus() {
      return this.vueLoaded ? '已加载' : '未加载'
    },
    vueStatusClass() {
      return this.vueLoaded ? 'success' : 'error'
    },
    runtime() {
      return Math.floor((Date.now() - this.startTime) / 1000)
    }
  },
  mounted() {
    this.initializeVue()
    this.startTimer()
  },
  methods: {
    initializeVue() {
      this.addLog('系统', 'Vue组件初始化开始')
      
      // 检查Vue是否可用
      if (typeof Vue !== 'undefined') {
        this.vueLoaded = true
        this.vueVersion = Vue.version
        this.addLog('Vue', `Vue ${Vue.version} 已加载`)
        this.addLog('系统', 'Vue组件初始化完成')
      } else {
        this.addLog('错误', 'Vue对象不存在')
      }
    },
    
    startTimer() {
      setInterval(() => {
        this.$forceUpdate() // 强制更新以刷新运行时间
      }, 1000)
    },
    
    testVueFunction() {
      this.testCount++
      this.addLog('测试', `Vue功能测试 #${this.testCount}`)
      
      if (this.vueLoaded) {
        this.addLog('Vue', '功能测试通过')
        this.$message.success('Vue功能测试成功！')
      } else {
        this.addLog('错误', 'Vue实例不存在')
        this.$message.error('Vue未加载，无法测试')
      }
    },
    
    testDataBinding() {
      this.testCount++
      this.addLog('测试', `数据绑定测试 #${this.testCount}`)
      
      // 更新测试数据
      this.testData.counter++
      this.testData.message = `更新于 ${new Date().toLocaleTimeString()}`
      this.testData.timestamp = new Date().toLocaleString()
      
      this.addLog('Vue', '数据绑定测试通过')
      this.$message.success('数据绑定测试成功！')
    },
    
    testMethodCall() {
      this.testCount++
      this.addLog('测试', `方法调用测试 #${this.testCount}`)
      
      const result = this.testMethod()
      this.addLog('Vue', `方法调用结果: ${result}`)
      this.$message.success('方法调用测试成功！')
    },
    
    testMethod() {
      this.testData.counter++
      return `方法调用成功，计数器: ${this.testData.counter}`
    },
    
    clearLogs() {
      this.logs = []
      this.addLog('系统', '日志已清空')
      this.$message.info('日志已清空')
    },
    
    addLog(type, message) {
      const log = {
        time: new Date().toLocaleTimeString(),
        type: type,
        message: message
      }
      this.logs.push(log)
      
      // 限制日志数量
      if (this.logs.length > 50) {
        this.logs = this.logs.slice(-50)
      }
      
      // 滚动到底部
      this.$nextTick(() => {
        if (this.$refs.logContainer) {
          this.$refs.logContainer.scrollTop = this.$refs.logContainer.scrollHeight
        }
      })
    }
  }
}
</script>

<style scoped>
.devtools-panel {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.header h2 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.header p {
  margin: 0;
  color: #7f8c8d;
}

.stats-container {
  margin-bottom: 30px;
}

.stat-card {
  text-align: center;
}

.stat-title {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.stat-value.success {
  color: #27ae60;
}

.stat-value.error {
  color: #e74c3c;
}

.feature-section {
  margin-bottom: 30px;
}

.feature-section h3 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.data-section {
  margin-bottom: 30px;
}

.data-section h3 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.data-item {
  margin-bottom: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
}

.data-item:last-child {
  margin-bottom: 0;
}

.log-section h3 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.log-container {
  max-height: 300px;
  overflow-y: auto;
  background: #2c3e50;
  color: #ecf0f1;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.log-entry {
  margin-bottom: 5px;
  padding: 2px 0;
}

.log-entry:last-child {
  margin-bottom: 0;
}

.log-time {
  color: #95a5a6;
  margin-right: 10px;
}

.log-type {
  font-weight: bold;
  margin-right: 10px;
}

.log-entry.system .log-type {
  color: #3498db;
}

.log-entry.Vue .log-type {
  color: #2ecc71;
}

.log-entry.测试 .log-type {
  color: #f39c12;
}

.log-entry.错误 .log-type {
  color: #e74c3c;
}

.log-message {
  color: #ecf0f1;
}

.no-logs {
  color: #7f8c8d;
  font-style: italic;
  text-align: center;
  padding: 20px;
}
</style>
