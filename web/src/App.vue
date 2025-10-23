<template>
  <el-container>
    <Header v-if="$route.meta.showHeader" />
    <el-main :style="{padding:$route.meta.showHeader?'20px':'0'}">
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
:global(.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell) {
  background-color: #ededf4 !important;
}

:global(.el-table .el-table__fixed-header-wrapper) {
  background-color: #ededf4 !important;
}
/* :global(img) {
  opacity: 0 !important;
}*/
:global(html) {
    /* filter: progid:DXImageTransform.Microsoft.BasicImage(grayscale=1);
    -webkit-filter: grayscale(100%); */
} 
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
  min-height: 100vh;
  background-color: #ECECEC;
  border: 0 solid #C3C5DE;
}

.el-header+.el-container {
  min-height: calc(100vh - 60px);
}
</style>
