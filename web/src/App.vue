<template>
  <el-container>
    <el-header>
      <div class="header-content">
        <h1>CBG数据</h1>
        <el-menu
          mode="horizontal"
          :router="true"
          :default-active="$route.path"
        >
          <el-menu-item index="/characters">角色列表</el-menu-item>
        </el-menu>
      </div>
    </el-header>
    
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script>
export default {
  name: 'App'
}
</script>
<style>
/* CSS Reset */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  line-height: 1.15;
  -webkit-text-size-adjust: 100%;
  -webkit-tap-highlight-color: transparent;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f5;
  color: #333;
}

h1, h2, h3, h4, h5, h6 {
  margin: 0;
  font-weight: 600;
  line-height: 1.2;
}

p {
  margin: 0;
}

ul, ol {
  list-style: none;
  margin: 0;
  padding: 0;
}

a {
  color: inherit;
  text-decoration: none;
}

button {
  border: none;
  background: none;
  font: inherit;
  cursor: pointer;
  outline: none;
}

input, textarea, select {
  font: inherit;
  border: none;
  outline: none;
}

img {
  max-width: 100%;
  height: auto;
  display: block;
}

table {
  border-collapse: collapse;
  border-spacing: 0;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 通用工具类 */
.clearfix::after {
  content: '';
  display: table;
  clear: both;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* 应用容器样式 */
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 响应式断点工具类 */
@media (max-width: 768px) {
  .hide-mobile {
    display: none !important;
  }
}

@media (min-width: 769px) {
  .hide-desktop {
    display: none !important;
  }
}

/* 动画过渡 */
* {
  transition: all 0.2s ease-in-out;
}

/* 禁用选择的元素 */
.no-select {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

/* 文本省略 */
.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.text-ellipsis-multiline {
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
</style>
<style scoped>
.el-header {
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
  padding: 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 100%;
}

.header-content h1 {
  margin: 0 20px 0 0;
  font-size: 20px;
}

.el-main {
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}
</style>
