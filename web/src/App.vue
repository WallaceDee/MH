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
