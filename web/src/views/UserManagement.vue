<template>
  <div class="user-management">
    <el-card class="filters" shadow="never">
      <div slot="header" class="card-header">
        <div><span class="emoji-icon">👥</span> 用户管理</div>
      </div>
      
      <!-- 筛选表单 -->
      <el-form :inline="true" :model="filters" size="mini">
        <el-form-item label="激活状态">
          <el-select v-model="filters.is_active" placeholder="全部" clearable style="width: 120px">
            <el-option label="已激活" value="true"></el-option>
            <el-option label="未激活" value="false"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchUsers">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户列表表格 -->
    <el-card shadow="never" style="margin-top: 20px">
      <el-table
        v-loading="loading"
        :data="users"
        stripe
        style="width: 100%"
        border
      >
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        <el-table-column prop="username" label="手机号" width="130" align="center"></el-table-column>
        <el-table-column prop="email" label="邮箱" width="180" show-overflow-tooltip></el-table-column>
        <el-table-column prop="is_active" label="激活状态" width="100" align="center">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'" size="mini">
              {{ scope.row.is_active ? '已激活' : '未激活' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_premium" label="高级用户" width="100" align="center">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_premium ? 'warning' : ''" size="mini">
              {{ scope.row.is_premium ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fingerprint" label="Fingerprint" width="200" show-overflow-tooltip>
          <template slot-scope="scope">
            <span v-if="scope.row.fingerprint" style="font-family: monospace; font-size: 12px;">
              {{ scope.row.fingerprint.substring(0, 20) }}...
            </span>
            <span v-else style="color: #909399;">未绑定</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180" align="center">
          <template slot-scope="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="last_login_at" label="最后登录" width="180" align="center">
          <template slot-scope="scope">
            {{ scope.row.last_login_at ? formatDateTime(scope.row.last_login_at) : '从未登录' }}
          </template>
        </el-table-column>
        <el-table-column prop="token_expires_at" label="Token过期" width="180" align="center">
          <template slot-scope="scope">
            <span v-if="scope.row.token_expires_at">
              {{ formatDateTime(scope.row.token_expires_at) }}
            </span>
            <span v-else style="color: #909399;">无</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="360" fixed="right" align="center">
          <template slot-scope="scope">
            <el-button
              v-if="!scope.row.is_active"
              type="success"
              size="mini"
              @click="handleActivate(scope.row)"
              :loading="scope.row.activating"
            >
              激活
            </el-button>
            <el-button
              v-else
              type="warning"
              size="mini"
              @click="handleDeactivate(scope.row)"
              :loading="scope.row.deactivating"
            >
              禁用
            </el-button>
            <el-button
              v-if="!scope.row.is_premium"
              type="primary"
              size="mini"
              @click="handleSetPremium(scope.row, true)"
              :loading="scope.row.settingPremium"
            >
              设为高级
            </el-button>
            <el-button
              v-else
              type="info"
              size="mini"
              @click="handleSetPremium(scope.row, false)"
              :loading="scope.row.settingPremium"
            >
              取消高级
            </el-button>
            <el-button
              type="danger"
              plain
              size="mini"
              :disabled="!scope.row.fingerprint"
              @click="handleResetFingerprint(scope.row)"
              :loading="scope.row.resettingFingerprint"
            >
              重置Fingerprint
            </el-button>
            <el-button
              type="danger"
              size="mini"
              @click="handleDelete(scope.row)"
              :loading="scope.row.deleting"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        style="margin-top: 20px; text-align: right;"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        :current-page="pagination.page"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pagination.page_size"
        layout="total, sizes, prev, pager, next, jumper"
        :total="pagination.total"
      ></el-pagination>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'UserManagement',
  data() {
    return {
      loading: false,
      users: [],
      filters: {
        is_active: null
      },
      pagination: {
        page: 1,
        page_size: 20,
        total: 0,
        pages: 0
      }
    }
  },
  mounted() {
    this.fetchUsers()
  },
  methods: {
    /**
     * 获取用户列表
     */
    async fetchUsers() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.page,
          page_size: this.pagination.page_size
        }
        
        // 添加筛选条件
        if (this.filters.is_active !== null && this.filters.is_active !== '') {
          params.is_active = String(this.filters.is_active)
        }
        
        const response = await this.$api.admin.getUserList(params)
        
        if (response.code === 200) {
          const data = response.data
          this.users = data.users || []
          this.pagination.total = data.total || 0
          this.pagination.pages = data.pages || 0
        } else {
          this.$message.error(response.message || '获取用户列表失败')
        }
      } catch (error) {
        console.error('获取用户列表失败:', error)
        this.$message.error('获取用户列表失败，请检查网络连接')
      } finally {
        this.loading = false
      }
    },

    /**
     * 激活用户
     */
    async handleActivate(user) {
      this.$set(user, 'activating', true)
      try {
        const response = await this.$api.admin.activateUser(user.id)
        if (response.code === 200) {
          this.$message.success('用户激活成功')
          user.is_active = true
          this.fetchUsers()
        } else {
          this.$message.error(response.message || '激活失败')
        }
      } catch (error) {
        console.error('激活用户失败:', error)
        this.$message.error('激活用户失败')
      } finally {
        this.$set(user, 'activating', false)
      }
    },

    /**
     * 禁用用户
     */
    async handleDeactivate(user) {
      this.$confirm('确定要禁用该用户吗？禁用后用户将无法登录。', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        this.$set(user, 'deactivating', true)
        try {
          const response = await this.$api.admin.deactivateUser(user.id)
          if (response.code === 200) {
            this.$message.success('用户已禁用')
            user.is_active = false
            this.fetchUsers()
          } else {
            this.$message.error(response.message || '禁用失败')
          }
        } catch (error) {
          console.error('禁用用户失败:', error)
          this.$message.error('禁用用户失败')
        } finally {
          this.$set(user, 'deactivating', false)
        }
      }).catch(() => {})
    },

    /**
     * 设置/取消高级用户
     */
    async handleSetPremium(user, isPremium) {
      this.$set(user, 'settingPremium', true)
      try {
        const response = await this.$api.admin.setPremium(user.id, isPremium)
        if (response.code === 200) {
          this.$message.success(response.message || (isPremium ? '已设置为高级用户' : '已取消高级用户'))
          user.is_premium = isPremium
          this.fetchUsers()
        } else {
          this.$message.error(response.message || '操作失败')
        }
      } catch (error) {
        console.error('设置高级用户失败:', error)
        this.$message.error('操作失败')
      } finally {
        this.$set(user, 'settingPremium', false)
      }
    },

    /**
     * 重置筛选条件
     */
    handleReset() {
      this.filters = {
        is_active: null
      }
      this.pagination.page = 1
      this.fetchUsers()
    },

    /**
     * 分页大小改变
     */
    handleSizeChange(size) {
      this.pagination.page_size = size
      this.pagination.page = 1
      this.fetchUsers()
    },

    /**
     * 页码改变
     */
    handlePageChange(page) {
      this.pagination.page = page
      this.fetchUsers()
    },

    /**
     * 删除用户
     */
    async handleDelete(user) {
      this.$confirm('删除后该用户所有数据将被移除，确认继续？', '提示', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false
      }).then(async () => {
        this.$set(user, 'deleting', true)
        try {
          const response = await this.$api.admin.deleteUser(user.id)
          if (response.code === 200) {
            this.$message.success(response.message || '用户删除成功')
            this.fetchUsers()
          } else {
            this.$message.error(response.message || '删除用户失败')
          }
        } catch (error) {
          console.error('删除用户失败:', error)
          this.$message.error('删除用户失败，请稍后重试')
        } finally {
          this.$set(user, 'deleting', false)
        }
      }).catch(() => {})
    },

    /**
     * 重置Fingerprint
     */
    async handleResetFingerprint(user) {
      if (!user.fingerprint) {
        this.$message.warning('该用户尚未绑定Fingerprint')
        return
      }
      this.$confirm('重置后用户下次登录将无需Fingerprint验证，并会绑定新的Fingerprint，确认继续？', '提示', {
        confirmButtonText: '重置',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        this.$set(user, 'resettingFingerprint', true)
        try {
          const response = await this.$api.admin.resetFingerprint(user.id)
          if (response.code === 200) {
            this.$message.success(response.message || 'Fingerprint已重置')
            user.fingerprint = null
            this.fetchUsers()
          } else {
            this.$message.error(response.message || '重置Fingerprint失败')
          }
        } catch (error) {
          console.error('重置Fingerprint失败:', error)
          this.$message.error('重置Fingerprint失败，请稍后重试')
        } finally {
          this.$set(user, 'resettingFingerprint', false)
        }
      }).catch(() => {})
    },

    /**
     * 格式化日期时间
     */
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return '-'
      try {
        const date = new Date(dateTimeStr)
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
        const seconds = String(date.getSeconds()).padStart(2, '0')
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
      } catch (error) {
        return dateTimeStr
      }
    }
  }
}
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  font-weight: bold;
}

.emoji-icon {
  margin-right: 8px;
  font-size: 18px;
}

.filters {
  margin-bottom: 20px;
}
</style>

