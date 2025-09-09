console.log('🚀 CBG爬虫助手Vue面板开始加载...');

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
    const logEntry = `[${timestamp}] ${type}: ${message}`;
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
                `<div class="data-item">
                    <strong>请求 ${index + 1}:</strong> ${item.url || '未知URL'}<br>
                    <small>状态: ${item.status || 'pending'} | 时间: ${new Date(item.timestamp || Date.now()).toLocaleTimeString()}</small>
                </div>`
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
                    addLog('Vue方法', `testMethod调用，计数器: ${this.testData.counter}`);
                    return `方法调用成功，计数器: ${this.testData.counter}`;
                },
                updateMessage() {
                    this.testData.message = `更新于 ${new Date().toLocaleTimeString()}`;
                    addLog('Vue数据', `消息更新: ${this.testData.message}`);
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
    addLog('测试', `Vue功能测试 #${testCount}`);
    
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
    addLog('测试', `数据绑定测试 #${testCount}`);
    
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
    addLog('测试', `方法调用测试 #${testCount}`);
    
    if (vueApp) {
        const result = vueApp.testMethod();
        addStatus('✅ 方法调用测试成功！', 'success');
        addLog('Vue', `方法调用结果: ${result}`);
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
            addLog('数据', `收到推荐数据: ${recommendData.length}条`);
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
});