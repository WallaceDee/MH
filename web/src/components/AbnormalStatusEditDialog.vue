<template>
  <el-dialog
    title="编辑异常状态"
    :visible="visible"
    width="400px"
    :before-close="handleClose"
    @close="handleClose"
  >
    <div class="status-edit-form">
      <el-form :model="form" label-width="80px">
        <el-form-item label="当前状态">
          <el-tag :type="getStatusTagType(currentStatus)">
            {{ getStatusText(currentStatus) }}
          </el-tag>
        </el-form-item>
        
        <el-form-item label="新状态" required>
          <el-select v-model="form.newStatus" placeholder="请选择新状态" style="width: 100%">
            <el-option label="待处理" value="pending"></el-option>
            <el-option label="已解决" value="resolved"></el-option>
            <el-option label="已忽略" value="ignored"></el-option>
            <el-option label="调查中" value="investigating"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="3"
            placeholder="可选：添加状态变更备注"
          ></el-input>
        </el-form-item>
      </el-form>
    </div>
    
    <div slot="footer" class="dialog-footer">
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleConfirm" :loading="loading">
        确定
      </el-button>
    </div>
  </el-dialog>
</template>

<script>
export default {
  name: 'AbnormalStatusEditDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    equipSn: {
      type: String,
      default: ''
    },
    currentStatus: {
      type: String,
      default: 'pending'
    }
  },
  data() {
    return {
      form: {
        newStatus: '',
        notes: ''
      },
      loading: false
    }
  },
  watch: {
    visible(val) {
      if (val) {
        this.form.newStatus = this.currentStatus
        this.form.notes = ''
      }
    }
  },
  methods: {
    handleClose() {
      this.$emit('close')
      this.resetForm()
    },
    
    resetForm() {
      this.form.newStatus = ''
      this.form.notes = ''
      this.loading = false
    },
    
    async handleConfirm() {
      if (!this.form.newStatus) {
        this.$notify.warning({
          title:'提示',
          message:'请选择新状态'
        })
        return
      }
      
      this.loading = true
      try {
        await this.$api.equipment.updateAbnormalEquipmentStatus(this.equipSn, {
          status: this.form.newStatus,
          notes: this.form.notes
        })
        
        this.$notify.success({
          title:'提示',
          message:`异常状态已更新为: ${this.getStatusText(this.form.newStatus)}`
        })
        this.$emit('success', {
          equipSn: this.equipSn,
          newStatus: this.form.newStatus,
          notes: this.form.notes
        })
        this.$emit('close')
        this.resetForm()
      } catch (error) {
        console.error('更新状态失败:', error)
        this.$notify.error({
          title:'提示',
          message:'更新状态失败'
        })
      } finally {
        this.loading = false
      }
    },
    
    getStatusTagType(status) {
      switch (status) {
        case 'pending':
          return 'warning'
        case 'resolved':
          return 'success'
        case 'ignored':
          return 'info'
        case 'investigating':
          return 'danger'
        default:
          return 'info'
      }
    },
    
    getStatusText(status) {
      switch (status) {
        case 'pending':
          return '待处理'
        case 'resolved':
          return '已解决'
        case 'ignored':
          return '已忽略'
        case 'investigating':
          return '调查中'
        default:
          return '未知'
      }
    }
  }
}
</script>

<style scoped>
.status-edit-form {
  padding: 20px 0;
}

.dialog-footer {
  text-align: right;
}
</style> 