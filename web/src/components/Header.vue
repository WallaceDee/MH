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
            </el-menu>
            <el-popover placement="bottom" width="400" trigger="click" popper-class="cookie-popover"
                :visible-arrow="false">
                <el-button slot="reference" :type="cookieButtonType" class="cookie-button" size="mini">
                    {{ cookieButtonText }}
                </el-button>
                <div>
                    <CookieStatus :auto-check="true" :show-cache-info="true" :show-actions="true" />
                </div>
            </el-popover>
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
        // 启动定时器，每分钟更新一次按钮状态
        this.updateTimer = setInterval(() => {
            // 强制更新计算属性
            this.$forceUpdate()
        }, 60000) // 每分钟更新一次
        
        // 监听路由变化
        this.$watch('$route', () => {
            // 路由变化时强制更新组件
            this.$forceUpdate()
        }, { immediate: true })
    },
    beforeDestroy() {
        // 清理定时器
        if (this.updateTimer) {
            clearInterval(this.updateTimer)
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
</style>