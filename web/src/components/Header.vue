<template>
    <el-header>
        <div class="header-content">
            <el-menu mode="horizontal" :router="true" :default-active="activeMenuIndex">
                <el-menu-item index="/">🏠️<span class="menu-item-text">首页</span></el-menu-item>
                <el-menu-item index="/roles/normal/109,175/1">👥<span class="menu-item-text">角色</span></el-menu-item>
                <el-menu-item index="/roles/empty/109,175/1">🎯<span class="menu-item-text">空号</span></el-menu-item>
                <el-menu-item index="/equipments">⚔️<span class="menu-item-text">装备</span></el-menu-item>
                <el-menu-item index="/pets">🐲<span class="menu-item-text">召唤兽</span></el-menu-item>
                <el-menu-item index="/equipment-desc-creator">🔨<span class="menu-item-text">装备模拟</span></el-menu-item>
                <el-menu-item index="/market-data-status">📊<span class="menu-item-text">数据状态</span></el-menu-item>
                <el-menu-item index="/admin/users">👤<span class="menu-item-text">用户管理</span></el-menu-item>
            </el-menu>
            <div class="header-right">
                <el-popover placement="bottom" width="400" trigger="click" popper-class="cookie-popover"
                    :visible-arrow="false">
                    <el-button slot="reference" :type="cookieButtonType" class="cookie-button" size="mini">
                        {{ cookieButtonText }}
                    </el-button>
                    <div>
                        <CookieStatus :auto-check="true" :show-cache-info="true" :show-actions="true" />
                    </div>
                </el-popover>

                <!-- 用户信息 -->
                <div v-if="isLoggedIn" class="user-info">
                    <el-dropdown @command="handleUserCommand" trigger="click">
                        <span class="user-dropdown">
                            <i class="el-icon-user-solid"></i>
                            <span>{{ userInfo.username }}</span>
                            <i class="el-icon-arrow-down el-icon--right"></i>
                        </span>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item disabled>
                                <span style="color: #909399;">{{ userInfo.is_premium ? '高级用户' : '普通用户' }}</span>
                            </el-dropdown-item>
                            <el-dropdown-item divided command="logout">
                                <i class="el-icon-switch-button"></i> 退出登录
                            </el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </div>
                <el-button v-else type="primary" size="mini" @click="handleLogin" class="login-button">
                    <i class="el-icon-user"></i> 登录
                </el-button>
            </div>
        </div>
    </el-header>
</template>
<script>
import CookieStatus from '@/components/CookieStatus.vue'
export default {
    name: 'Header',
    components: {
        CookieStatus
    },
    data() {
        return {
            userInfo: null,
            isLoggedIn: false
        }
    },
    computed: {
        // 当前激活的菜单项索引
        activeMenuIndex() {
            const path = this.$route.path
            
            // 根据路由路径确定激活的菜单项
            if (path === '/') {
                return '/'
            } else if (path.startsWith('/roles/normal')) {
                return '/roles/normal/109,175/1'
            } else if (path.startsWith('/roles/empty')) {
                return '/roles/empty/109,175/1'
            } else if (path.startsWith('/roles')) {
                return '/roles/normal/109,175/1' // 默认角色页面
            } else if (path.startsWith('/equipments')) {
                return '/equipments'
            } else if (path.startsWith('/pets')) {
                return '/pets'
            } else if (path.startsWith('/equipment-desc-creator')) {
                return '/equipment-desc-creator'
            } else if (path.startsWith('/market-data-status')) {
                return '/market-data-status'
            } else if (path.startsWith('/admin/users')) {
                return '/admin/users'
            }
            
            return '/'
        },
        
        // Cookie缓存相关计算属性
        isCookieCacheValid() {
            return this.$store.getters['cookie/isCookieCacheValid']
        },

        getCacheRemainingMinutes() {
            return this.$store.getters['cookie/getCacheRemainingMinutes']
        },

        // Cookie按钮状态
        cookieButtonType() {
            if (this.isCookieCacheValid) {
                return 'success'
            }
            return 'danger'
        },

        cookieButtonIcon() {
            if (this.isCookieCacheValid) {
                return 'el-icon-check'
            }
            return 'el-icon-close'
        },

        cookieButtonText() {
            if (this.isCookieCacheValid) {
                return '🍪 有效'
            }
            return '🍪 已过期'
        }
    },
    mounted() {
        // 检查登录状态
        this.checkLoginStatus()

        // 监听auth-required事件
        window.addEventListener('auth-required', this.handleAuthRequired)

        // 启动定时器，每分钟更新一次按钮状态
        this.updateTimer = setInterval(() => {
            // 强制更新计算属性
            this.$forceUpdate()
        }, 60000) // 每分钟更新一次
        
        // 监听路由变化 - 每次路由变化时重新检查登录状态
        this.$watch('$route', (to) => {
            // 重新检查登录状态
            this.checkLoginStatus()
            
            // 如果路由需要认证但用户未登录，跳转到登录页
            if (to.matched.some(record => record.meta.requiresAuth) && !this.isLoggedIn) {
                this.$router.push({
                    path: '/login',
                    query: { redirect: to.fullPath }
                })
            }
            
            // 强制更新组件
            this.$forceUpdate()
        }, { immediate: true })
    },
    beforeDestroy() {
        // 清理定时器
        if (this.updateTimer) {
            clearInterval(this.updateTimer)
        }
        // 移除事件监听
        window.removeEventListener('auth-required', this.handleAuthRequired)
    },
    methods: {
        /**
         * 检查登录状态
         * @returns {boolean} 是否已登录
         */
        checkLoginStatus() {
            const token = localStorage.getItem('auth_token')
            const userInfoStr = localStorage.getItem('user_info')
            
            if (token && userInfoStr) {
                try {
                    const userInfo = JSON.parse(userInfoStr)
                    
                    // 验证用户信息的完整性
                    if (userInfo && userInfo.username) {
                        this.userInfo = userInfo
                        this.isLoggedIn = true
                        return true
                    } else {
                        // 用户信息不完整，清除并标记为未登录
                        console.warn('用户信息不完整，清除本地存储')
                        this.clearLocalAuth()
                        return false
                    }
                } catch (error) {
                    console.error('解析用户信息失败:', error)
                    this.clearLocalAuth()
                    return false
                }
            } else {
                this.userInfo = null
                this.isLoggedIn = false
                return false
            }
        },

        /**
         * 清除本地认证信息
         */
        clearLocalAuth() {
            localStorage.removeItem('auth_token')
            localStorage.removeItem('user_info')
            this.userInfo = null
            this.isLoggedIn = false
        },

        /**
         * 验证登录状态（用于需要登录的操作）
         * @param {string} message - 未登录时的提示信息
         * @returns {boolean} 是否已登录
         */
        requireLogin(message = '请先登录') {
            if (!this.isLoggedIn || !this.userInfo) {
                this.$message.warning(message)
                this.$router.push({
                    path: '/login',
                    query: { redirect: this.$route.fullPath }
                })
                return false
            }
            return true
        },

        /**
         * 处理auth-required事件
         */
        handleAuthRequired() {
            console.log('收到 auth-required 事件，清除登录状态')
            this.clearLocalAuth()
            
            // 如果不在登录页，则跳转到登录页
            if (this.$route.path !== '/login') {
                this.$message.warning('登录已过期，请重新登录')
                this.$router.push({
                    path: '/login',
                    query: { redirect: this.$route.fullPath }
                })
            }
        },

        /**
         * 处理登录按钮点击
         */
        handleLogin() {
            this.$router.push({
                path: '/login',
                query: { redirect: this.$route.fullPath }
            })
        },

        /**
         * 处理用户下拉菜单命令
         */
        async handleUserCommand(command) {
            if (command === 'logout') {
                await this.handleLogout()
            }
        },

        /**
         * 处理退出登录
         */
        async handleLogout() {
            try {
                await this.$api.auth.logout()
            } catch (error) {
                console.error('退出登录失败:', error)
            } finally {
                // 清除本地存储
                this.clearLocalAuth()
                this.$message.success('已退出登录')
                // 跳转到登录页
                this.$router.push('/login')
            }
        }
    }
}
</script>
<style scoped>
.header-content .el-menu {
    background: transparent;
}

.header-content .el-menu .menu-item-text {
    background: transparent;
    margin-left: 10px;

}

.header-content .el-menu .is-active {
    font-size: 24px;
}

.header-content .el-menu .is-active .menu-item-text {

    display: none;
}

.el-header {
    background-color: #F5F5F5;
    border-bottom: 1px solid #E7E7E7;
    padding: 0;
    width: 100%;
}

.header-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    height: 100%;
    justify-content: space-between;
}

.header-content h1 {
    margin: 0 20px 0 0;
    font-size: 20px;
}

/* Cookie按钮样式 */
.cookie-button {
    margin-left: auto;
    font-size: 12px;
    padding: 8px 12px;
    border-radius: 4px;
    transition: all 0.3s ease;
}

.cookie-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:global(.cookie-popover) {
    padding: 0 !important;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 12px;
}

.user-info {
    margin-left: 12px;
}

.user-dropdown {
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    padding: 8px 12px;
    border-radius: 4px;
    transition: all 0.3s ease;
    color: #303133;
    font-size: 14px;
}

.user-dropdown:hover {
    background-color: rgba(0, 0, 0, 0.05);
}

.user-dropdown .el-icon-user-solid {
    font-size: 16px;
}

.login-button {
    margin-left: 12px;
}
</style>