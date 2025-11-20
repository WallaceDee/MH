<template>
  <div class="login-container">
    <el-card class="login-card" shadow="always">
      <div slot="header" class="login-header">
        <h2>管理员登录</h2>
        <p>梦幻灵瞳 - CBG数据分析平台</p>
      </div>

      <!-- 登录表单 -->
      <el-form
        :model="loginForm"
        :rules="loginRules"
        ref="loginForm"
        label-width="80px"
        @submit.native.prevent="handleLogin"
      >
        <el-form-item label="手机号" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入手机号"
            autocomplete="off"
            prefix-icon="el-icon-user"
          ></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            autocomplete="off"
            prefix-icon="el-icon-lock"
            @keyup.enter.native="handleLogin"
            show-password
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            @click="handleLogin"
            :loading="loading"
            style="width: 100%"
          >
            登录
          </el-button>
        </el-form-item>
        <el-form-item style="margin-bottom: 0;">
          <el-alert
            title="管理后台仅限授权用户使用"
            type="info"
            :closable="false"
            show-icon
          >
          </el-alert>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    // 手机号验证规则
    const validatePhoneNumber = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请输入手机号'))
      } else if (!/^1[3-9]\d{9}$/.test(value)) {
        callback(new Error('请输入正确的手机号格式'))
      } else {
        callback()
      }
    }

    return {
      loading: false,
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { validator: validatePhoneNumber, trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码至少6个字符', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    /**
     * 处理登录
     */
    async handleLogin() {
      if (!this.$refs.loginForm) {
        this.$message.error('表单初始化失败，请刷新页面')
        return
      }

      this.$refs.loginForm.validate(async (valid) => {
        if (!valid) {
          this.$message.warning('请检查登录信息')
          return
        }

        this.loading = true
        try {
          const response = await this.$api.auth.login({
            username: this.loginForm.username,
            password: this.loginForm.password
          })

          if (response.code === 200) {
            // 检查是否是账户未激活的信息提示
            if (response.message && response.message.includes('账户未激活')) {
              this.$message.warning(response.message)
            } else if (response.data && response.data.token) {
              // 登录成功，保存token到localStorage
              localStorage.setItem('auth_token', response.data.token)
              localStorage.setItem('user_info', JSON.stringify(response.data.user))

              this.$message.success('登录成功')

              // 跳转到redirect参数指定的页面，或者首页
              const redirect = this.$route.query.redirect || '/'
              this.$router.push(redirect)
            } else {
              this.$message.warning(response.message || '登录失败')
            }
          } else {
            this.$message.error(response.message || '登录失败')
          }
        } catch (error) {
          console.error('登录失败:', error)
          this.$message.error('登录失败，请检查网络连接')
        } finally {
          this.loading = false
        }
      })
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 450px;
  border-radius: 12px;
  overflow: hidden;
}

.login-header {
  text-align: center;
  padding: 10px 0;
}

.login-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 24px;
}

.login-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.el-form {
  padding: 20px 20px 0;
}

.el-form-item:last-child {
  margin-bottom: 20px;
}

:deep(.el-alert) {
  padding: 8px 12px;
}

:deep(.el-alert__title) {
  font-size: 13px;
}
</style>

