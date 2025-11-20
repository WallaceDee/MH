<template>
  <el-dialog
    :title="isRegister ? '用户注册' : '用户登录'"
    :visible.sync="visible"
    width="400px"
    :close-on-click-modal="true"
    :close-on-press-escape="true"
    :show-close="true"
    :modal="true"
    class="login-modal"
  >
    <!-- 登录表单 -->
    <el-form 
      v-if="!isRegister"
      :model="loginForm" 
      :rules="rules" 
      ref="loginForm" 
      label-width="80px"
    >
      <el-form-item label="手机号" prop="username">
        <el-input 
          v-model="loginForm.username" 
          placeholder="请输入手机号" 
          autocomplete="off"
        ></el-input>
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="loginForm.password"
          type="password"
          placeholder="请输入密码"
          autocomplete="off"
          @keyup.enter.native="handleLogin"
        ></el-input>
      </el-form-item>
    </el-form>
    
    <!-- 注册表单 -->
    <el-form 
      v-else
      :model="registerForm" 
      :rules="registerRules" 
      ref="registerForm" 
      label-width="80px"
    >
      <el-form-item label="手机号" prop="username">
        <el-input 
          v-model="registerForm.username" 
          placeholder="请输入手机号" 
          autocomplete="off"
        ></el-input>
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="registerForm.password"
          type="password"
          placeholder="请输入密码"
          autocomplete="off"
          @keyup.enter.native="handleRegister"
        ></el-input>
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input
          v-model="registerForm.confirmPassword"
          type="password"
          placeholder="请再次输入密码"
          autocomplete="off"
          @keyup.enter.native="handleRegister"
        ></el-input>
      </el-form-item>
    </el-form>
    
    <div slot="footer" class="dialog-footer">
      <el-button @click="toggleMode">{{ isRegister ? '返回登录' : '注册账号' }}</el-button>
      <el-button 
        v-if="!isRegister"
        type="primary" 
        @click="handleLogin" 
        :loading="loading"
      >
        登录
      </el-button>
      <el-button 
        v-else
        type="primary" 
        @click="handleRegister" 
        :loading="loading"
      >
        注册
      </el-button>
    </div>
  </el-dialog>
</template>

<script>
import { api } from '@/utils/request'

export default {
  name: 'LoginModal',
  props: {
    value: {
      type: Boolean,
      default: false
    }
  },
  data() {
    // 密码确认验证
    const validateConfirmPassword = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== this.registerForm.password) {
        callback(new Error('两次输入密码不一致'))
      } else {
        callback()
      }
    }
    
    return {
      visible: this.value,
      loading: false,
      isRegister: false, // 是否显示注册表单
      loginForm: {
        username: '',
        password: ''
      },
      registerForm: {
        username: '',
        password: '',
        confirmPassword: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码至少6个字符', trigger: 'blur' }
        ]
      },
      registerRules: {
        username: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码至少6个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      }
    }
  },
  watch: {
    value(newVal) {
      this.visible = newVal
    },
    visible(newVal) {
      this.$emit('input', newVal)
    }
  },
  methods: {
    async handleLogin() {
      this.$refs.loginForm.validate(async (valid) => {
        if (!valid) return
        
        this.loading = true
        try {
          const response = await api.post('/auth/login', {
            username: this.loginForm.username,
            password: this.loginForm.password
          })
          
          if (response.code === 200) {
            // 检查是否是账户未激活的信息提示
            if (response.message && response.message.includes('账户未激活')) {
              this.$message.info(response.message)
            } else if (response.data && response.data.token) {
              // 保存token到chrome.storage
              await this.saveToken(response.data.token, response.data.user)
              
              this.$message.success('登录成功')
              this.$emit('login-success', response.data)
              this.visible = false
            } else {
              // 其他情况，显示信息提示
              this.$message.info(response.message || '登录失败')
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
    },
    
    toggleMode() {
      this.isRegister = !this.isRegister
      // 等待 DOM 更新后再重置表单
      this.$nextTick(() => {
        if (this.$refs.loginForm) {
          this.$refs.loginForm.resetFields()
        }
        if (this.$refs.registerForm) {
          this.$refs.registerForm.resetFields()
        }
      })
    },
    
    async handleRegister() {
      // 确保表单引用存在
      if (!this.$refs.registerForm) {
        console.error('注册表单引用不存在')
        this.$message.error('表单未准备好，请稍后再试')
        return
      }
      
      this.$refs.registerForm.validate(async (valid) => {
        if (!valid) {
          console.log('表单验证失败，请检查输入')
          this.$message.warning('请检查输入信息是否正确')
          return
        }
        
        console.log('开始注册，手机号:', this.registerForm.username)
        this.loading = true
        try {
          const response = await api.post('/auth/register', {
            username: this.registerForm.username,
            password: this.registerForm.password
          })
          
          console.log('注册响应:', response)
          
          if (response.code === 200) {
            this.$message.success(response.message || '注册成功，请登录')
            // 保存用户名
            const username = this.registerForm.username
            // 切换到登录模式
            this.isRegister = false
            // 等待 DOM 更新后再填充用户名和清空注册表单
            this.$nextTick(() => {
              this.loginForm.username = username
              if (this.$refs.registerForm) {
                this.$refs.registerForm.resetFields()
              }
            })
          } else {
            this.$message.error(response.message || '注册失败')
          }
        } catch (error) {
          console.error('注册失败:', error)
          // 显示更详细的错误信息
          const errorMessage = error.response?.data?.message || error.message || '注册失败，请检查网络连接'
          this.$message.error(errorMessage)
        } finally {
          this.loading = false
        }
      })
    },
    
    async saveToken(token, user) {
      return new Promise((resolve) => {
        chrome.storage.local.set({
          auth_token: token,
          user_info: user
        }, () => {
          resolve()
        })
      })
    }
  }
}
</script>

<style scoped>
.login-modal {
  z-index: 10000;
}

.dialog-footer {
  text-align: right;
}
</style>

