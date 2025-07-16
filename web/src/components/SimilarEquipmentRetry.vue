<template>
    <div class="similar-pet-retry">
      <el-alert v-if="message" :title="message" type="warning" show-icon style="margin-bottom: 12px;" />
      <el-button v-if="canRetry" type="primary" :loading="loading" @click="$emit('retry', currentThreshold)">
        重试（相似度阈值: {{ currentThreshold }}）
      </el-button>
    </div>
  </template>
  
  <script>
  export default {
    name: 'SimilarPetRetry',
    props: {
      message: {
        type: String,
        default: ''
      },
      canRetry: {
        type: Boolean,
        default: false
      },
      currentThreshold: {
        type: Number,
        default: 0.7
      },
      loading: {
        type: Boolean,
        default: false
      }
    }
  }
  </script>
  
  <style scoped>
  .similar-pet-retry {
    text-align: center;
    padding: 16px 0;
  }
  </style> 