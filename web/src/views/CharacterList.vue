<template>
  <div class="character-list">
    <div class="filter-bar">
      <el-date-picker
        v-model="selectedDate"
        type="month"
        placeholder="选择月份"
        format="yyyy-MM"
        value-format="yyyy-MM"
        @change="handleDateChange"
      />
    </div>

    <el-table
      v-loading="loading"
      :data="characterList"
      border
      style="width: 100%"
    >
      <!-- 基本信息 -->
      <el-table-column prop="character_name" label="角色名" width="120" />
      <el-table-column prop="server" label="服务器" width="150" >
        <template slot-scope="scope">
          {{scope.row.area_name}}/{{scope.row.server_name}}
        </template>
      </el-table-column>
      <el-table-column label="等级/门派/飞升" width="160">
        <template slot-scope="scope">
          {{scope.row.level}}/{{scope.row.school}}/{{ scope.row.fly_status }}
        </template>
      </el-table-column>
      <el-table-column prop="price" label="价格" width="80" />
      <el-table-column prop="onsale_expire_time_desc" label="出售剩余时间" width="110" />
      
      <!-- 修炼信息 -->
      <el-table-column label="修炼信息" width="450">
        <template slot-scope="scope">
          <span>总经验:{{scope.row.sum_exp}}亿</span>
          <span class="ml-10">攻:{{scope.row.expt_ski1}}/{{scope.row.max_expt1}}</span>
          <span class="ml-10">防:{{scope.row.expt_ski2}}/{{scope.row.max_expt2}}</span>
          <span class="ml-10">法:{{scope.row.expt_ski3}}/{{scope.row.max_expt3}}</span>
          <span class="ml-10">抗:{{scope.row.expt_ski4}}/{{scope.row.max_expt4}}</span>
          <span class="ml-10">猎:{{scope.row.expt_ski5}}</span>
        </template>
      </el-table-column>

      <!-- 属性信息 -->
      <el-table-column label="属性" width="380">
        <template slot-scope="scope">
          <span>气血:{{scope.row.hp_max}}</span>
          <span class="ml-10">魔法:{{scope.row.mp_max}}</span>
          <span class="ml-10">伤害:{{scope.row.damage_all}}</span>
          <span class="ml-10">防御:{{scope.row.def_all}}</span>
        </template>
      </el-table-column>

      <!-- 资产信息 -->
      <el-table-column label="资产" width="300">
        <template slot-scope="scope">
          <span>现金:{{scope.row.cash}}</span>
          <span class="ml-10">存款:{{scope.row.saving}}</span>
        </template>
      </el-table-column>

      <!-- 评分信息 -->
      <el-table-column label="积分" width="300">
        <template slot-scope="scope">
          <span class="ml-10">神器:{{scope.row.shenqi_score}}</span>
          <span class="ml-10">副本:{{scope.row.dup_score}}</span>
        </template>
      </el-table-column>
      <!-- 时间信息 -->
      <el-table-column prop="create_time" label="创建时间" width="180" />
    </el-table>

    <div class="pagination">
      <el-pagination
        :current-page.sync="currentPage"
        :page-size.sync="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script>
import dayjs from 'dayjs'

export default {
  name: 'CharacterList',
  
  data() {
    return {
      loading: false,
      characterList: [],
      currentPage: 1,
      pageSize: 20,
      total: 0,
      selectedDate: dayjs().format('YYYY-MM')
    }
  },

  created() {
    this.fetchData()
  },

  methods: {
    async fetchData() {
      this.loading = true
      try {
        const [year, month] = this.selectedDate.split('-')
        const response = await fetch(
          `/api/characters?page=${this.currentPage}&page_size=${this.pageSize}&year=${year}&month=${month}`
        )
        const data = await response.json()

        if (data.error) {
          this.$message.error(data.error)
          return
        }

        this.characterList = data.data
        this.total = data.total
      } catch (error) {
        this.$message.error('获取数据失败：' + error.message)
      } finally {
        this.loading = false
      }
    },

    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
      this.fetchData()
    },

    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchData()
    },

    handleDateChange() {
      this.currentPage = 1
      this.fetchData()
    },

    formatPrice(price) {
      return price ? `¥${(price / 100).toFixed(2)}` : '-'
    },

    formatDate(timestamp) {
      return timestamp ? dayjs(timestamp * 1000).format('YYYY-MM-DD HH:mm:ss') : '-'
    },

    formatMoney(money) {
      return money ? `¥${(money / 100).toFixed(2)}` : '-'
    }
  }
}
</script>

<style scoped>
.character-list {
  padding: 20px;
}

.filter-bar {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.ml-10 {
  margin-left: 10px;
}

/* 设置表格行高 */
.el-table >>> td {
  padding: 5px 0;
}
</style> 