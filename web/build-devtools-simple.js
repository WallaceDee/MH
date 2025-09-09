const fs = require('fs');
const path = require('path');
const chokidar = require('chokidar');

// 简单的构建脚本，直接复制和修改文件
function buildDevToolsPanel() {
  console.log('🚀 开始构建DevTools面板...');
  
  const sourceDir = path.join(__dirname, 'src/chrome-extensions');
  const targetDir = path.join(__dirname, 'chrome-extensions');
  
  // 确保目标目录存在
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }
  
  // 创建Vue版本的DevTools面板HTML
  const vueHtmlContent = `<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>CBG爬虫助手 - Vue面板</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-bottom: 20px; }
        .status { margin: 10px 0; padding: 10px; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .info { background: #d1ecf1; color: #0c5460; }
        .warning { background: #fff3cd; color: #856404; }
        .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-warning { background: #ffc107; color: #212529; }
        .btn-danger { background: #dc3545; color: white; }
        .btn:hover { opacity: 0.8; }
        .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }
        .stat-card { background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #007bff; }
        .stat-title { font-weight: bold; color: #495057; margin-bottom: 5px; }
        .stat-value { font-size: 18px; color: #007bff; }
        .feature-list { margin: 20px 0; }
        .feature-item { padding: 8px 0; border-bottom: 1px solid #eee; }
        .feature-item:last-child { border-bottom: none; }
        .log-container { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 10px; margin: 10px 0; max-height: 200px; overflow-y: auto; font-family: monospace; font-size: 12px; }
        .data-display { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 15px; margin: 10px 0; }
        .data-item { margin: 5px 0; padding: 5px; background: white; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🚀 CBG爬虫助手 - Vue面板</h2>
            <p>梦幻西游CBG爬虫系统DevTools面板</p>
        </div>
        
        <div id="status-container">
            <div class="status info">正在检查Vue加载状态...</div>
        </div>
        
        <div class="stats" id="stats-container" style="display: none;">
            <div class="stat-card">
                <div class="stat-title">Vue状态</div>
                <div class="stat-value" id="vue-status">检查中...</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Vue版本</div>
                <div class="stat-value" id="vue-version">检查中...</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">运行时间</div>
                <div class="stat-value" id="runtime">0秒</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">数据量</div>
                <div class="stat-value" id="data-count">0</div>
            </div>
        </div>
        
        <div class="feature-list">
            <h3>🎯 功能测试</h3>
            <div class="feature-item">
                <button id="test-vue-btn" class="btn btn-primary">测试Vue功能</button>
                <span>基础Vue实例创建和挂载测试</span>
            </div>
            <div class="feature-item">
                <button id="test-data-btn" class="btn btn-success">测试数据绑定</button>
                <span>Vue数据响应式绑定测试</span>
            </div>
            <div class="feature-item">
                <button id="test-methods-btn" class="btn btn-warning">测试方法调用</button>
                <span>Vue方法调用和事件处理测试</span>
            </div>
            <div class="feature-item">
                <button id="clear-log-btn" class="btn btn-danger">清空日志</button>
                <span>清空控制台和显示日志</span>
            </div>
        </div>
        
        <div class="data-display" id="data-display" style="display: none;">
            <h3>📊 推荐数据</h3>
            <div id="data-list">暂无数据</div>
        </div>
        
        <div class="log-container" id="log-container">
            <div style="color: #6c757d;">控制台日志将显示在这里...</div>
        </div>
    </div>

    <script src="libs/vue.min.js"></script>
    <script src="devtools-panel.js"></script>
</body>
</html>`;

  const htmlTarget = path.join(targetDir, 'devtools-panel.html');
  fs.writeFileSync(htmlTarget, vueHtmlContent);
  console.log('✅ 已生成 devtools-panel.html');
  
  // 创建Vue版本的JavaScript文件
  const jsContent = `console.log('🚀 CBG爬虫助手Vue面板开始加载...');

// 全局变量
let vueApp = null;
let testCount = 0;
let startTime = Date.now();
let logEntries = [];
let recommendData = [];

// 添加状态信息
function addStatus(message, type = 'info') {
    const container = document.getElementById('status-container');
    if (container) {
        const statusDiv = document.createElement('div');
        statusDiv.className = 'status ' + type;
        statusDiv.textContent = message;
        container.appendChild(statusDiv);
    }
    addLog('状态', message);
}

// 添加日志
function addLog(type, message) {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = \`[\${timestamp}] \${type}: \${message}\`;
    logEntries.push(logEntry);
    console.log(logEntry);
    
    // 更新日志显示
    updateLogDisplay();
}

// 更新日志显示
function updateLogDisplay() {
    const logContainer = document.getElementById('log-container');
    if (logContainer) {
        logContainer.innerHTML = logEntries.slice(-20).join('<br>');
        logContainer.scrollTop = logContainer.scrollHeight;
    }
}

// 更新统计信息
function updateStats() {
    const runtime = Math.floor((Date.now() - startTime) / 1000);
    const dataCount = recommendData.length;
    
    const runtimeEl = document.getElementById('runtime');
    const dataCountEl = document.getElementById('data-count');
    
    if (runtimeEl) runtimeEl.textContent = runtime + '秒';
    if (dataCountEl) dataCountEl.textContent = dataCount;
}

// 更新数据显示
function updateDataDisplay() {
    const dataDisplay = document.getElementById('data-display');
    const dataList = document.getElementById('data-list');
    
    if (recommendData.length > 0) {
        if (dataDisplay) dataDisplay.style.display = 'block';
        if (dataList) {
            dataList.innerHTML = recommendData.map((item, index) => 
                \`<div class="data-item">
                    <strong>请求 \${index + 1}:</strong> \${item.url || '未知URL'}<br>
                    <small>状态: \${item.status || 'pending'} | 时间: \${new Date(item.timestamp || Date.now()).toLocaleTimeString()}</small>
                </div>\`
            ).join('');
        }
    }
}

// 检查Vue加载
function checkVue() {
    addStatus('检查Vue对象是否存在...', 'info');
    
    if (typeof Vue === 'undefined') {
        addStatus('❌ Vue对象不存在！', 'error');
        addStatus('可能的原因：', 'error');
        addStatus('1. libs/vue.min.js文件不存在', 'error');
        addStatus('2. 文件路径错误', 'error');
        addStatus('3. 文件内容损坏', 'error');
        return false;
    }
    
    addStatus('✅ Vue对象存在', 'success');
    addStatus('Vue版本: ' + Vue.version, 'success');
    
    // 更新统计信息
    const vueStatusEl = document.getElementById('vue-status');
    const vueVersionEl = document.getElementById('vue-version');
    const statsContainer = document.getElementById('stats-container');
    
    if (vueStatusEl) vueStatusEl.textContent = '已加载';
    if (vueVersionEl) vueVersionEl.textContent = Vue.version;
    if (statsContainer) statsContainer.style.display = 'grid';
    
    return true;
}

// 创建Vue应用
function createVueApp() {
    try {
        addStatus('尝试创建Vue实例...', 'info');
        
        vueApp = new Vue({
            el: '#status-container',
            data: {
                message: 'Vue实例创建成功！',
                testData: {
                    counter: 0,
                    message: 'Hello Vue!',
                    items: ['项目1', '项目2', '项目3']
                }
            },
            mounted() {
                addStatus('✅ Vue实例已挂载', 'success');
                addLog('Vue', '实例挂载完成');
            },
            methods: {
                testMethod() {
                    this.testData.counter++;
                    addLog('Vue方法', \`testMethod调用，计数器: \${this.testData.counter}\`);
                    return \`方法调用成功，计数器: \${this.testData.counter}\`;
                },
                updateMessage() {
                    this.testData.message = \`更新于 \${new Date().toLocaleTimeString()}\`;
                    addLog('Vue数据', \`消息更新: \${this.testData.message}\`);
                }
            }
        });
        
        addStatus('✅ Vue实例创建成功', 'success');
        return true;
        
    } catch (error) {
        addStatus('❌ Vue实例创建失败: ' + error.message, 'error');
        addLog('错误', 'Vue实例创建失败: ' + error.message);
        return false;
    }
}

// 测试Vue功能
function testVueFunction() {
    testCount++;
    addLog('测试', \`Vue功能测试 #\${testCount}\`);
    
    if (vueApp) {
        addStatus('✅ Vue功能测试成功！', 'success');
        addLog('Vue', '功能测试通过');
    } else {
        addStatus('❌ Vue实例不存在，无法测试', 'error');
        addLog('错误', 'Vue实例不存在');
    }
    
    updateStats();
}

// 测试数据绑定
function testDataBinding() {
    testCount++;
    addLog('测试', \`数据绑定测试 #\${testCount}\`);
    
    if (vueApp) {
        vueApp.updateMessage();
        addStatus('✅ 数据绑定测试成功！', 'success');
        addLog('Vue', '数据绑定测试通过');
    } else {
        addStatus('❌ Vue实例不存在，无法测试数据绑定', 'error');
    }
    
    updateStats();
}

// 测试方法调用
function testMethodCall() {
    testCount++;
    addLog('测试', \`方法调用测试 #\${testCount}\`);
    
    if (vueApp) {
        const result = vueApp.testMethod();
        addStatus('✅ 方法调用测试成功！', 'success');
        addLog('Vue', \`方法调用结果: \${result}\`);
    } else {
        addStatus('❌ Vue实例不存在，无法测试方法调用', 'error');
    }
    
    updateStats();
}

// 清空日志
function clearLogs() {
    logEntries = [];
    const logContainer = document.getElementById('log-container');
    if (logContainer) {
        logContainer.innerHTML = '<div style="color: #6c757d;">日志已清空...</div>';
    }
    addLog('系统', '日志已清空');
}

// 监听Chrome扩展消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('收到消息:', request);
    
    switch (request.action) {
        case 'updateRecommendData':
            recommendData = request.data || [];
            addLog('数据', \`收到推荐数据: \${recommendData.length}条\`);
            updateDataDisplay();
            updateStats();
            break;
        case 'showDebuggerWarning':
            addStatus('⚠️ ' + request.message, 'warning');
            break;
    }
});

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    addStatus('DOM加载完成', 'info');
    addLog('系统', '页面初始化开始');
    
    // 等待Vue脚本加载
    setTimeout(function() {
        const vueLoaded = checkVue();
        
        if (vueLoaded) {
            const appCreated = createVueApp();
            
            if (appCreated) {
                // 绑定测试按钮
                const testVueBtn = document.getElementById('test-vue-btn');
                const testDataBtn = document.getElementById('test-data-btn');
                const testMethodsBtn = document.getElementById('test-methods-btn');
                const clearLogBtn = document.getElementById('clear-log-btn');
                
                if (testVueBtn) testVueBtn.addEventListener('click', testVueFunction);
                if (testDataBtn) testDataBtn.addEventListener('click', testDataBinding);
                if (testMethodsBtn) testMethodsBtn.addEventListener('click', testMethodCall);
                if (clearLogBtn) clearLogBtn.addEventListener('click', clearLogs);
                
                addStatus('🎉 所有功能已就绪！', 'success');
                addLog('系统', 'CBG爬虫助手Vue面板初始化完成');
            } else {
                // 禁用所有按钮
                ['test-vue-btn', 'test-data-btn', 'test-methods-btn'].forEach(id => {
                    const btn = document.getElementById(id);
                    if (btn) {
                        btn.disabled = true;
                        btn.textContent = 'Vue未加载，无法测试';
                    }
                });
            }
        } else {
            // 禁用所有按钮
            ['test-vue-btn', 'test-data-btn', 'test-methods-btn'].forEach(id => {
                const btn = document.getElementById(id);
                if (btn) {
                    btn.disabled = true;
                    btn.textContent = 'Vue未加载，无法测试';
                }
            });
        }
        
        // 开始定期更新统计信息
        setInterval(updateStats, 1000);
        
    }, 100); // 给Vue脚本一些加载时间
});`;

  const jsTarget = path.join(targetDir, 'devtools-panel.js');
  fs.writeFileSync(jsTarget, jsContent);
  console.log('✅ 已生成 devtools-panel.js');
  
  console.log('🎉 DevTools面板构建完成！');
  console.log('📁 输出目录:', targetDir);
}

// 检查是否为开发模式
const isDev = process.argv.includes('--watch') || process.env.NODE_ENV === 'development';

if (isDev) {
  console.log('🔍 开发模式：开始监听文件变化...');
  
  // 监听源文件变化
  const sourceDir = path.join(__dirname, 'src/chrome-extensions');
  const watcher = chokidar.watch(sourceDir, {
    ignored: /(^|[\/\\])\../, // 忽略隐藏文件
    persistent: true,
    ignoreInitial: true
  });
  
  // 首次构建
  buildDevToolsPanel();
  
  // 监听文件变化
  watcher
    .on('change', (filePath) => {
      console.log(`📝 文件变化: ${path.relative(__dirname, filePath)}`);
      buildDevToolsPanel();
    })
    .on('add', (filePath) => {
      console.log(`➕ 新增文件: ${path.relative(__dirname, filePath)}`);
      buildDevToolsPanel();
    })
    .on('unlink', (filePath) => {
      console.log(`🗑️ 删除文件: ${path.relative(__dirname, filePath)}`);
      buildDevToolsPanel();
    })
    .on('error', (error) => {
      console.error('❌ 监听错误:', error);
    });
  
  console.log('✅ 文件监听已启动，按 Ctrl+C 停止');
  
  // 优雅退出
  process.on('SIGINT', () => {
    console.log('\n🛑 停止文件监听...');
    watcher.close();
    process.exit(0);
  });
  
} else {
  // 生产模式：只执行一次构建
  buildDevToolsPanel();
}
