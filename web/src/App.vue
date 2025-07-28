<template>
  <el-container>
    <Header />

    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script>
import Header from '@/components/Header.vue'
export default {
  name: 'App',
  components: {
    Header
  }
}
</script>

<style scoped>
:global(.el-card) {
  border-radius: 8px !important;
}

:global(.el-card .el-card__header) {
  padding: 8px 16px;
}

:global(.emoji-icon) {
  display: inline-block;
  border-radius: 6px;
  width: 38px;
  height: 38px;
  background-color: rgba(0, 122, 255, 0.12);
  line-height: 38px;
  text-align: center;
  color: rgb(0, 122, 255);
}
.el-container {
  flex-direction: column;
}
.el-main {
  min-height: calc(100vh - 60px);
  background-color: #ECECEC;
  border: 0 solid #C3C5DE;
}
</style>
