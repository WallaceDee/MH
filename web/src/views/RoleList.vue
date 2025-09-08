<template>
  <div class="role-list">
    <el-card class="filters" shadow="never">
      <div slot="header" class="card-header">
        <div><span class="emoji-icon">🔍</span> 筛选</div>
      </div>
      <el-form :model="searchForm" class="search-form" :inline="true">
        <el-form-item label="选择月份">
          <el-date-picker v-model="searchForm.selectedDate" :clearable="false" type="month" placeholder="选择月份"
            format="yyyy-MM" value-format="yyyy-MM" @change="handleDateChange" />
        </el-form-item>
        <el-form-item label="人物等级">
          <el-input-number :controls="false" v-model="searchForm.level_min" :min="0" :max="175" style="width: 60px"
            size="mini" @change="handleLevelChange" />
          <span class="mx-2">-</span>
          <el-input-number :controls="false" v-model="searchForm.level_max" :min="0" :max="175" style="width: 60px"
            size="mini" @change="handleLevelChange" />
          <div class="level-quick-select">
            <el-tag size="mini" v-for="level in [109, 129, 155, 159, 175]" :key="level" :effect="getLevelEffect(level)"
              @click="handleQuickLevelSelect(level)" style="cursor: pointer;margin-right: 4px;">
              {{ level }}级
            </el-tag>
          </div>
        </el-form-item>
        <el-form-item label="物品数量≤">
          <el-input v-model.number="searchForm.equip_num" style="width: 60px" clearable />
        </el-form-item>
        <el-form-item label="宠物数量≤">
          <el-input v-model.number="searchForm.pet_num" style="width: 60px" clearable />
        </el-form-item>
        <el-form-item label="宠物等级≥">
          <el-input v-model.number="searchForm.pet_num_level" style="width: 60px" clearable />
        </el-form-item>
        <el-form-item label="接受还价">
          <el-checkbox v-model="searchForm.accept_bargain" true-label="1" false-label="" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <el-checkbox-group v-model="checkedList">
      <el-table ref="roleTable" v-loading="loading" :data="stickyRoleList.concat(tableData)"
        style="width: 100%;border: 1px solid #9ea0bf;" stripe @sort-change="handleSortChange">
        <!-- 基本信息 -->
        <el-table-column width="110" align="center" fixed="left">
          <template #header>
            <el-link :underline="false" v-if="stickyRoleList.length > 0" href="javascript:void(0);"
              @click.native="clearAllStickyRoles" class="cell"
              style="font-size: 12px;font-weight: bold;color: #909399;white-space: nowrap;">批量解锁 ({{
                stickyRoleList.length }})</el-link>
          </template>
          <template slot-scope="scope">
            <div class="sticky-wrapper">
              <RoleImage :key="scope.row.eid" :other_info="scope.row.other_info" :roleInfo="scope.row.roleInfo">
              </RoleImage>
              <el-checkbox :label="scope.row.eid" @change="handleSingleCheckboxChange">锁定</el-checkbox>
            </div><el-link :href="getCBGLinkByType(scope.row.eid, 'role')" type="danger" target="_blank"
              style="white-space: nowrap;text-overflow: ellipsis;overflow: hidden;display: block;font-size: 12px;"> {{
                scope.row.seller_nickname || scope.row.seller_nickname }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="sum_exp" label="门派/等级/经验" width="160" align="center" sortable="custom">
          <template slot-scope="scope">
            <span class="vertical-middle">
              <i class="icon-chai" v-if="scope.row.is_split_independent_role === 1"></i>
              <i class="icon-zheng" v-if="scope.row.is_split_main_role === 1"></i>
              {{ scope.row.server_name }}/
              {{ get_school_name(scope.row.school) }}
            </span>
            <div class="js-level cGray">{{ scope.row.level }}级/{{
              scope.row.sum_exp
            }}亿</div>
          </template>
        </el-table-column>
        <el-table-column prop="highlight" label="亮点" width="100" align="center" sortable="custom">>
          <template slot-scope="scope">
            <span v-html="gen_highlight(scope.row.highlight)"></span>
          </template>
        </el-table-column>
        <el-table-column prop="dynamic_tags" label="动态" width="100" align="center" sortable="custom">
          <template slot-scope="scope">
            <span v-html="gen_dynamic_tags(scope.row.dynamic_tags)"></span>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格 (元)" width="140" sortable="custom" align="center">
          <template #default="scope">
            <div v-html="formatFullPrice(scope.row)"></div>
            <el-tag v-if="get_price_change(scope.row) !== undefined"
              :type="get_price_change(scope.row) < 0 ? 'danger' : 'success'">
              <i :class="`el-icon-${get_price_change(scope.row) < 0 ? 'bottom' : 'top'}`"
                :style="`color: #${get_price_change(scope.row) < 0 ? 'F56C6C;' : '67C23A'}`">{{
                  get_price_change(scope.row) }}</i>
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="估价" width="220" align="center">
          <template #default="scope">
            <div class="role-valuation-cell">
              <div>
                <el-tag>👤<span v-html="formatFullPriceWithoutPerfix({ price: scope.row.base_price })"
                    style="font-size: 12px;"></span></el-tag>
                <el-tag v-if="get_equip_num(scope.row.roleInfo) > 0">⚔️<span
                    v-html="formatFullPriceWithoutPerfix({ price: scope.row.equip_price })"
                    style="font-size: 12px;"></span></el-tag>
                <el-tag v-if="get_pet_num(scope.row.roleInfo) > 0">🐲<span
                    v-html="formatFullPriceWithoutPerfix({ price: scope.row.pet_price })"
                    style="font-size: 12px;"></span></el-tag>
              </div>
              <el-tag type="success">总估价：
                <span
                  v-html="formatFullPriceWithoutPerfix({ price: scope.row.base_price + scope.row.equip_price + scope.row.pet_price })"
                  style="font-size: 12px;"></span></el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="装备估价" width="120" align="center">
          <template #default="scope">
            <SimilarRoleModal :role="scope.row" :similar-data="roleSimilarData"
              @show="loadSimilarRoles($event, scope.$index)">
              <div> <el-link type="primary" href="javascript:void(0)">👤 裸号</el-link></div>
            </SimilarRoleModal>
            <div v-if="get_equip_num(scope.row.roleInfo) > 0"> <el-link
                @click.native="handleEquipPrice(scope.row, scope.$index)" type="primary" href="javascript:void(0)">⚔️ {{
                  get_equip_num(scope.row.roleInfo) }}件</el-link></div>
            <el-link v-if="get_pet_num(scope.row.roleInfo) > 0"
              @click.native="handlSummonePrice(scope.row, scope.$index)" type="primary" href="javascript:void(0)">🐲 {{
                get_pet_num(scope.row.roleInfo) }}只
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="history_price" label="历史价格" width="120" align="center" sortable="custom">
          <template slot-scope="scope">
            <div v-for="(history, index) in JSON.parse(scope.row.history_price)" :key="index" :title="history.timestamp"
              v-html="formatFullPrice(history.price, true)"
              style="text-decoration: line-through;filter: grayscale(100%);"></div>
          </template>
        </el-table-column>
        <el-table-column prop="accept_bargain" label="还价" width="80" align="center" sortable="custom">
          <template slot-scope="scope">
            <el-tag type="success" v-if="scope.row.accept_bargain == 1">接受</el-tag>
            <el-tag type="danger" v-else>拒绝</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="collect_num" label="收藏" width="80" align="center" sortable="custom">
        </el-table-column>
        <!-- 修炼信息 -->
        <el-table-column label="修炼/控制力" min-width="400" align="center">
          <template slot-scope="scope">
            <el-tag v-for="xiulian in scope.row.roleInfo.role_xiulian" :key="xiulian.name">{{ xiulian.name.replace('修炼',
              '') }}{{ xiulian.info }}</el-tag>
            <br>
            <el-tag v-for="ctrl_skill in scope.row.roleInfo.pet_ctrl_skill" :key="ctrl_skill.name">{{ ctrl_skill.name
            }}{{
                ctrl_skill.grade }}</el-tag>
          </template>
        </el-table-column>
        <!-- 时间信息 -->
        <el-table-column prop="update_time" label="创建、更新" width="200">
          <template slot-scope="scope">
            <el-tag type="info">{{ scope.row.create_time }}</el-tag>
            <el-tag>{{ scope.row.update_time }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="server" label="操作" width="100" fixed="right">
          <template slot-scope="scope">
            <el-link href="javascript:void(0)" type="danger" @click.native="handleDelete(scope.row)">删除</el-link>
            <el-link v-if="roleType === 'normal'" type="primary" href="javascript:void(0)"
              @click.native="changeRoleType(scope.row)">转为锚点</el-link>
            <el-link v-else type="primary" href="javascript:void(0)"
              @click.native="changeRoleType(scope.row)">移除锚点</el-link>
          </template>
        </el-table-column>
      </el-table>
    </el-checkbox-group>
    <div class="pagination-container">
      <el-pagination :current-page.sync="currentPage" :page-size.sync="pageSize" :total="total"
        :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next" @size-change="handleSizeChange"
        @current-change="handleCurrentChange" />
    </div>

    <!-- 装备估价结果对话框 -->
    <el-dialog :visible.sync="valuationDialogVisible" width="1000px" :close-on-click-modal="false"
      :close-on-press-escape="false" custom-class="batch-valuation-dialog">
      <span slot="title" class="el-dialog__title">
        <el-tag size="mini">{{ valuationDialogTitle.server_name }}</el-tag>
        /
        <el-tag type="info" size="mini">{{ valuationDialogTitle.school }}</el-tag>/
        <el-link :href="getCBGLinkByType(valuationDialogTitle.eid)" target="_blank">{{ valuationDialogTitle.nickname
        }}</el-link>
      </span>
      <EquipBatchValuationResult :results="valuationResults" :total-value="valuationTotalValue"
        :equipment-list="valuationEquipmentList" :valuate-params="batchValuateParams" :loading="valuationLoading"
        @close="closeValuationDialog" />
    </el-dialog>

    <!-- 宠物估价结果对话框 -->
    <el-dialog :visible.sync="petValuationDialogVisible" width="900px" :close-on-click-modal="false"
      :close-on-press-escape="false" custom-class="batch-valuation-dialog">
      <span slot="title" class="el-dialog__title">
        <el-tag size="mini">{{ petValuationDialogTitle.server_name }}</el-tag>
        /
        <el-tag type="info" size="mini">{{ petValuationDialogTitle.school }}</el-tag>/
        <el-link :href="getCBGLinkByType(petValuationDialogTitle.eid)" target="_blank">{{
          petValuationDialogTitle.nickname
        }}</el-link>
      </span>
      <PetBatchValuationResult :results="petValuationResults" :total-value="petValuationTotalValue"
        :pet-list="petValuationList" :valuate-params="batchValuateParams" :loading="petValuationLoading"
        @close="closePetValuationDialog" />
    </el-dialog>
  </div>
</template>

<script>
import dayjs from 'dayjs'
import EquipBatchValuationResult from '@/components/EquipBatchValuationResult.vue'
import PetBatchValuationResult from '@/components/PetBatchValuationResult.vue'
import SimilarRoleModal from '@/components/SimilarRoleModal.vue'
import RoleImage from '@/components/RoleInfo/RoleImage.vue'
import { commonMixin } from '@/utils/mixins/commonMixin'
export default {
  name: 'RoleList',
  mixins: [commonMixin],
  components: {
    RoleImage,
    EquipBatchValuationResult,
    PetBatchValuationResult,
    SimilarRoleModal
  },
  computed: {
    roleType() {
      return this.$route.params.type || 'normal'
    }
  },
  watch: {
    roleType() {
      this.currentPage = 1

      // 更新路由参数，移除页码参数（因为重置到第1页）
      const newParams = {
        type: this.roleType,
        levelRange: this.$route.params.levelRange
      }

      this.$router.replace({
        name: 'RoleList',
        params: newParams
      })

      this.fetchData()
    },

    // 监听路由参数变化，同步更新表单
    '$route.params.levelRange': {
      handler(newLevelRange) {
        if (newLevelRange) {
          const [min, max] = newLevelRange.split(',').map(Number)
          if (!isNaN(min) && !isNaN(max)) {
            this.searchForm.level_min = min
            this.searchForm.level_max = max
          }
        } else {
          // 当路由参数为 undefined 时，清空表单等级
          this.searchForm.level_min = undefined
          this.searchForm.level_max = undefined
        }
      },
      immediate: true
    },

    // 监听路由参数变化，同步更新页码
    '$route.params.page': {
      handler(newPage) {
        if (newPage) {
          const pageNum = parseInt(newPage)
          if (!isNaN(pageNum) && pageNum > 0) {
            this.currentPage = pageNum
          } else {
            this.currentPage = 1
          }
        } else {
          this.currentPage = 1
        }
      },
      immediate: true
    },

    // 监听路由query参数变化，同步更新搜索表单和排序状态
    '$route.query': {
      handler(newQuery) {
        // 同步搜索表单参数
        if (newQuery.selectedDate) {
          this.searchForm.selectedDate = newQuery.selectedDate
        }
        if (newQuery.equip_num !== undefined) {
          this.searchForm.equip_num = newQuery.equip_num ? parseInt(newQuery.equip_num) : undefined
        }
        if (newQuery.pet_num !== undefined) {
          this.searchForm.pet_num = newQuery.pet_num ? parseInt(newQuery.pet_num) : undefined
        }
        if (newQuery.pet_num_level !== undefined) {
          this.searchForm.pet_num_level = newQuery.pet_num_level ? parseInt(newQuery.pet_num_level) : undefined
        }
        if (newQuery.accept_bargain !== undefined) {
          this.searchForm.accept_bargain = newQuery.accept_bargain
        }

        // 同步排序参数
        if (newQuery.sort_by && newQuery.sort_order) {
          const sortFields = newQuery.sort_by.split(',')
          const sortOrders = newQuery.sort_order.split(',')

          // 清空当前排序状态
          this.sortState = {}

          // 重新设置排序状态
          sortFields.forEach((field, index) => {
            const order = sortOrders[index]
            if (order === 'ASC') {
              this.sortState[field] = 'ascending'
            } else if (order === 'DESC') {
              this.sortState[field] = 'descending'
            }
          })

          // 更新searchForm中的排序参数
          this.$set(this.searchForm, 'sort_by', newQuery.sort_by)
          this.$set(this.searchForm, 'sort_order', newQuery.sort_order)
        } else {
          // 如果没有排序参数，清空排序状态
          this.sortState = {}
          this.$set(this.searchForm, 'sort_by', undefined)
          this.$set(this.searchForm, 'sort_order', undefined)
        }
      },
      immediate: true
    }
  },
  data() {
    return {
      roleSimilarData: null,
      valuationDialogTitle: {
        nickname: '',
        school: '',
        server_name: '',
        eid: ''
      },
      stickyRoleList: [],
      checkedList: [],
      valuationLoading: false,
      batchValuateParams: {
        similarity_threshold: 0.8,
        max_anchors: 30,
        serverid: undefined,
        server_name: undefined
      },
      valuationResults: [],
      valuationTotalValue: 0,
      valuationEquipmentList: [],
      valuationDialogVisible: false,
      // 宠物估价相关
      petValuationResults: [],
      petValuationTotalValue: 0,
      petValuationList: [],
      petValuationDialogVisible: false,
      petValuationLoading: false,
      petValuationDialogTitle: {
        nickname: '',
        school: '',
        server_name: '',
        eid: ''
      },
      // 角色估价相关
      loadingStates: {}, // 用于控制各个操作的加载状态
      loading: false,
      tableData: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,
      searchForm: {
        selectedDate: dayjs().format('YYYY-MM'),
        level_min: undefined,
        level_max: undefined,
        equip_num: undefined,
        pet_num: undefined,
        pet_num_level: undefined,
        sort_by: undefined,
        sort_order: undefined,
        accept_bargain: undefined
      },
      activeCollapse: [],
      sortState: {
        price: null,
        level: null,
        create_time: null
      }
    }
  },

  mounted() {
    const originalGetHeaderCellClass = this.$refs.roleTable.$refs.tableHeader.getHeaderCellClass
    this.$refs.roleTable.$refs.tableHeader.getHeaderCellClass = (rowIndex, columnIndex, row, column) => {
      let classes = originalGetHeaderCellClass(rowIndex, columnIndex, row, column)
      if (this.sortState[column.property]) {
        classes += ' ' + this.sortState[column.property]
      }
      return classes
    }

    // 从localStorage加载锁定的角色列表
    this.loadStickyRoleList()

    this.fetchData()
  },

  beforeDestroy() {
    // 页面卸载前保存数据到localStorage
    this.saveStickyRoleList()
  },

  methods: {
    formatFullPriceWithoutPerfix(item) {
      return this.formatFullPrice(item, true).replace('￥', '').replace('-', '???')
    },
    // 检查路由参数是否有变化的工具方法
    hasRouteChanges(newParams, newQuery = null) {
      const hasParamChanges = JSON.stringify(newParams) !== JSON.stringify(this.$route.params)
      if (newQuery) {
        const hasQueryChanges = JSON.stringify(newQuery) !== JSON.stringify(this.$route.query)
        return hasParamChanges || hasQueryChanges
      }
      return hasParamChanges
    },

    // 安全更新路由的方法
    safeRouteUpdate(newParams, newQuery = null) {
      if (this.hasRouteChanges(newParams, newQuery)) {
        this.$router.replace({
          name: this.$route.name,
          params: newParams,
          query: newQuery || this.$route.query
        })
      }
    },

    get_price_change({ price, history_price }) {
      const history_price_list = JSON.parse(history_price).map(item => item.price)
      if (history_price_list.length === 0) return
      const max_price = Math.max(...history_price_list)
      return (price - max_price) / 100
    },
    // 保存锁定的角色列表到localStorage
    saveStickyRoleList() {
      try {
        // 全量保存数据，包括所有角色信息
        const stickyData = this.stickyRoleList.map(item => {
          // 深拷贝对象，避免引用问题
          const fullData = JSON.parse(JSON.stringify(item))
          // 添加时间戳
          fullData.timestamp = Date.now()
          return fullData
        })

        localStorage.setItem('cbg_sticky_role_list', JSON.stringify(stickyData))
        console.log('锁定角色列表已全量保存到localStorage:', stickyData.length)
      } catch (error) {
        console.error('保存锁定角色列表失败:', error)
      }
    },

    // 从localStorage加载锁定的角色列表
    loadStickyRoleList() {
      try {
        const stored = localStorage.getItem('cbg_sticky_role_list')
        if (stored) {
          const stickyData = JSON.parse(stored)
          // 为每个锁定的角色添加is_sticky标记
          const processedData = stickyData.map(item => ({
            ...item,
            is_sticky: true
          }))

          this.stickyRoleList = processedData
          // 更新checkedList以保持复选框状态同步
          this.checkedList = processedData.map(item => item.eid)
          console.log('从localStorage加载锁定角色列表:', processedData.length)
        }
      } catch (error) {
        console.error('加载锁定角色列表失败:', error)
        // 如果加载失败，清空localStorage中的数据
        localStorage.removeItem('cbg_sticky_role_list')
        this.stickyRoleList = []
        this.checkedList = []
      }
    },
    handleSingleCheckboxChange(checked, event) {
      const eid = event.target.value || event.target.labels[0].textContent
      if (checked) {
        const currentRow = this.tableData.find(item => item.eid === eid)
        if (currentRow) {
          // 检查是否已经存在于stickyRoleList中
          const exists = this.stickyRoleList.find(item => item.eid === eid)
          if (!exists) {
            currentRow.is_sticky = true
            this.stickyRoleList.push(currentRow)
            // this.tableData = this.tableData.filter(item => item.eid !== eid)
            // 保存到localStorage
            this.saveStickyRoleList()

            this.$notify.success({
              title: '锁定成功',
              message: `已锁定角色: ${currentRow.seller_nickname}`,
              duration: 2000
            })
          }
        }
      } else {
        // 从stickyRoleList中移除
        this.stickyRoleList = this.stickyRoleList.filter(item => item.eid !== eid)
        // this.tableData.unshift(this.stickyRoleList.find(item => item.eid === eid))
        // 保存到localStorage
        this.saveStickyRoleList()

        // 找到对应的角色信息用于提示
        const removedRole = this.tableData.find(item => item.eid === eid)
        if (removedRole) {
          this.$notify.info({
            title: '解锁成功',
            message: `已解锁角色: ${removedRole.seller_nickname}`,
            duration: 2000
          })
        }
      }
    },

    // 批量解锁所有锁定的角色
    clearAllStickyRoles() {
      this.$confirm('确定要解锁所有锁定的角色吗？', '确认解锁', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.stickyRoleList = []
        this.checkedList = []
        // 清除localStorage中的数据
        localStorage.removeItem('cbg_sticky_role_list')

        this.$notify.success({
          title: '批量解锁成功',
          message: '已解锁所有锁定的角色',
          duration: 2000
        })
      }).catch(() => {
        // 用户取消操作
      })
    },
    getLevelEffect(level) {
      const [min, max] = this.$route.params.levelRange.split(',').map(Number)
      if (level >= min && level <= max) {
        return 'dark'
      }
      return 'light'
    },
    async changeRoleType(row) {
      try {
        // 确认转移
        await this.$confirm(
          `确定要转移角色 ${row.seller_nickname} 吗？`,
          '确认转移',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        // 获取当前年月
        const [year, month] = this.searchForm.selectedDate.split('-')

        // 调用转移API
        const response = await this.$api.role.switchRoleType(row.eid, {
          year,
          month,
          role_type: this.roleType,
          target_role_type: this.roleType === 'empty' ? 'normal' : 'empty'
        })

        if (response.code === 200) {
          this.$notify.success({
            title: '成功',
            message: '角色转移成功'
          })
          // 重新获取数据
          await this.fetchData()
        } else {
          this.$notify.error({
            title: '错误',
            message: response.message || '转移失败'
          })
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('转移角色失败:', error)
          this.$notify.error({
            title: '错误',
            message: '转移角色失败'
          })
        }
      }
    },
    async handleDelete(row) {
      try {
        // 确认删除
        await this.$confirm(
          `确定要删除角色 ${row.seller_nickname} 吗？`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        // 获取当前年月
        const [year, month] = this.searchForm.selectedDate.split('-')

        // 调用删除API
        const response = await this.$api.role.deleteRole(row.eid, {
          year,
          month,
          role_type: this.roleType
        })

        if (response.code === 200) {
          this.$notify.success({
            title: '成功',
            message: '角色删除成功'
          })
          // 重新获取数据
          await this.fetchData()
        } else {
          this.$notify.error({
            title: '错误',
            message: response.message || '删除失败'
          })
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除角色失败:', error)
          this.$notify.error({
            title: '错误',
            message: '删除角色失败'
          })
        }
      }
    },
    // 关闭装备估价结果对话框
    closeValuationDialog() {
      this.valuationDialogVisible = false
      this.valuationResults = []
      this.valuationTotalValue = 0
      this.valuationEquipmentList = []
      this.valuationLoading = false
      this.valuationDialogTitle = {
        nickname: '',
        school: '',
        server_name: '',
        eid: ''
      }
    },
    // 关闭宠物估价结果对话框
    closePetValuationDialog() {
      this.petValuationDialogVisible = false
      this.petValuationResults = []
      this.petValuationTotalValue = 0
      this.petValuationList = []
      this.petValuationLoading = false
      this.petValuationDialogTitle = {
        nickname: '',
        school: '',
        server_name: '',
        eid: ''
      }
    },
    // 角色估价和相似角色数据加载
    async loadSimilarRoles(role, rowIndex) {
      try {
        this.roleSimilarData = null
        console.log('角色估价和加载相似数据:', role.eid)
        // 显示加载状态
        this.$set(this.loadingStates, `basePrice_${rowIndex}`, true)
        // 调用角色估价接口
        const [year, month] = this.searchForm.selectedDate.split('-')
        const response = await this.$api.role.getRoleValuation({
          eid: role.eid,
          year: parseInt(year),
          month: parseInt(month),
          role_type: this.roleType,
          strategy: 'fair_value',
          similarity_threshold: 0.7,
          max_anchors: 30
        })
        if (response.code === 200) {
          const result = response.data
          const estimatedPrice = result.estimated_price_yuan
          // 更新角色数据中的估价信息（后端已自动更新数据库）
          this.$set(role, 'base_price', result.estimated_price)

          // 查询相似角色锚点数据
          if (result?.anchor_count > 0) {
            try {
              // 调用专门的锚点查询接口
              const anchorsResponse = await this.$api.role.findRoleAnchors({
                eid: role.eid,
                year: parseInt(year),
                month: parseInt(month),
                role_type: this.roleType,
                similarity_threshold: 0.7,
                max_anchors: 30
              })

              if (anchorsResponse.code === 200 && anchorsResponse.data.anchors) {
                const anchorsData = anchorsResponse.data
                const parsedAnchors = anchorsData.anchors.map((item) => {
                  const roleInfo = new window.RoleInfoParser(item.large_equip_desc, { equip_level: item.equip_level })
                  item.RoleInfoParser = roleInfo
                  if (roleInfo.result) {
                    item.roleInfo = roleInfo.result
                  }
                  return item
                })

                // 保存相似角色数据，用于相似角色模态框
                this.roleSimilarData = {
                  anchor_count: anchorsData.anchors.length,
                  similarity_threshold: 0.7,
                  max_anchors: 30,
                  anchors: parsedAnchors,
                  statistics: anchorsData.statistics,
                  valuation: {
                    estimated_price_yuan: estimatedPrice,
                    confidence: result.confidence,
                    strategy: result.strategy || 'fair_value'
                  }
                }
              } else {
                console.warn('未获取到相似角色锚点数据:', anchorsResponse.message)
              }
            } catch (error) {
              console.error('查询相似角色锚点失败:', error)
              // 锚点查询失败不影响估价结果显示
            }
          }

        } else {
          // 估价失败
          this.$notify.error({
            title: '角色估价失败',
            message: response.message || '估价计算失败',
            duration: 3000
          })

          // 显示详细错误信息
          if (response.data && response.data.error) {
            console.error('估价错误详情:', response.data.error)
          }
        }

      } catch (error) {
        console.error('角色估价失败:', error)
        this.$notify.error({
          title: '估价请求失败',
          message: '网络请求异常，请稍后重试',
          duration: 3000
        })
      } finally {
        // 隐藏加载状态
        this.$set(this.loadingStates, `basePrice_${rowIndex}`, false)
      }
    },
    async handlSummonePrice(role, rowIndex) {
      const pet_list_desc = [...role.roleInfo.pet_info, ...role.roleInfo.split_pets]
      let pet_list = JSON.parse(role.all_summon_json)
      console.log('pet_list', pet_list)
      if (!pet_list || pet_list.length === 0) {
        this.$notify.warning({
          title: '提示',
          message: '没有可估价的宠物'
        })
        return
      }
      pet_list = pet_list.map((item) => {
        //TODO:等级
        const role_grade_limit = window.CBG_GAME_CONFIG.pet_equip_type_to_grade_mapping[item.iType]
        const all_skill = []
        for (var typeid in item.all_skills) {
          all_skill.push('' + typeid)
        }
        // 根据JavaScript逻辑计算evol_skill_list
        const evol_skill_list = this.calculateEvolSkillList(item)
        const texing = JSON.stringify(item.jinjie?.core)
        const lx = item.jinjie?.lx || 0
        const equip_list = []
        for (var i = 0; i < 3; i++) {
          var equip = item['summon_equip' + (i + 1)]
          var equip_info = window.CBG_GAME_CONFIG.equip_info[equip?.iType] || {}
          if (equip) {
            equip_list.push({
              type: equip.iType,
              desc: equip.cDesc,
              name: equip_info.name,
              icon: window.ResUrl + `/images/equip/small/${equip?.iType}.gif`,
              //lock_type: role.RoleInfoParser.get_lock_types(equip),
              static_desc: equip_info.desc?.replace(/#R/g, '<br />')
            })
          } else {
            equip_list.push(null)
          }
        }
        const neidan = []
        if (item.summon_core != undefined) {
          for (var p in item.summon_core) {
            var p_core = item.summon_core[p]
            neidan.push({
              name: window.CBG_GAME_CONFIG.pet_neidans[p] || '',
              level: p_core[0],
              isNeiDan: true
            })
          }
        }
        const pet_detail = pet_list_desc.find(pet => pet.equip_sn === item.equip_sn)
        //召唤兽特征提取必传参数
        return {
          pet_detail,
          equip_sn: item.equip_sn,
          role_grade_limit,
          equip_level: item.iGrade,
          growth: item.grow / 1000,
          is_baobao: item.iBaobao == 1 ? '是' : '否',
          all_skill: all_skill.join('|'),
          evol_skill_list: JSON.stringify(evol_skill_list),
          sp_skill: pet_detail.genius,
          texing,
          lx,
          equip_list: JSON.stringify(equip_list),
          neidan: JSON.stringify(neidan),
          serverid: role.serverid,
          server_name: role.server_name
        }
      })

      // 设置宠物估价对话框标题
      this.petValuationDialogTitle = {
        nickname: role.roleInfo.basic_info.nickname,
        school: role.roleInfo.basic_info.school,
        server_name: role.server_name,
        eid: role.eid
      }

      try {
        // 先显示弹窗和骨架屏
        this.petValuationDialogVisible = true
        this.petValuationLoading = true
        this.petValuationResults = []
        this.petValuationTotalValue = 0
        this.petValuationList = pet_list

        // 调用批量宠物估价API
        const response = await this.$api.pet.batchPetValuation({
          eid: role.eid,
          pet_list: pet_list.map(({ pet_detail, ...item }) => {
            return item
          }),
          strategy: 'fair_value',
          similarity_threshold: this.batchValuateParams.similarity_threshold,
          max_anchors: this.batchValuateParams.max_anchors
        })

        if (response.code === 200) {
          const data = response.data
          const results = data.results || []
          const totalValue = results.reduce((sum, result) => {
            return sum + (result.estimated_price || 0) + (result.equip_estimated_price || 0)
          }, 0)
          this.$set(this.tableData[rowIndex], 'pet_price', data.pet_price)
          // 更新弹窗内容，显示实际数据
          this.petValuationResults = results
          this.petValuationTotalValue = totalValue
          this.petValuationLoading = false
        } else {
          this.$notify.error({
            title: '错误',
            message: response.message || '宠物估价失败'
          })
          this.closePetValuationDialog()
        }
      } catch (error) {
        console.error('宠物估价失败:', error)
        this.$notify.error({
          title: '错误',
          message: '宠物估价失败'
        })
        this.closePetValuationDialog()
      } finally {
        this.petValuationLoading = false
      }
    },
    calculateEvolSkillList(pet) {
      const evol_skill_list = []

      if (!pet.EvolSkill || !window.CBG_GAME_CONFIG.pet_skill_high_to_other_level_mapping) {
        return evol_skill_list
      }

      // 解析进化技能ID
      const cifu = pet.EvolSkill.split('|').map(Number)
      const cifuObj = {}
      cifu.forEach(function (number) {
        cifuObj[number] = 1
      })

      const evol_skills = cifuObj
      if (!evol_skills) {
        return evol_skill_list
      }

      const evol_skill_str = []
      for (const typeid in evol_skills) {
        evol_skill_str.push('' + typeid)
      }

      for (let i = 0, max = evol_skill_str.length; i < max; i++) {
        const typeid = evol_skill_str[i]
        const evol_skill_hash = window.CBG_GAME_CONFIG.pet_skill_high_to_other_level_mapping[typeid]

        if (!evol_skill_hash) {
          continue
        }

        const evol_skill_item = {
          skill_type: typeid,
          level: evol_skills[typeid],
          evol_type: typeid
        }

        if (pet.all_skills) {
          const isHighSkill = pet.all_skills[String(evol_skill_hash.high_skill)]
          const isLowSkill = pet.all_skills[String(evol_skill_hash.low_skill)]

          if (isHighSkill || isLowSkill) {
            evol_skill_item.hlightLight = true
            if (!isHighSkill) {
              evol_skill_item.evol_type = evol_skill_hash.low_skill
            }
          } else {
            evol_skill_item.hlightLight = false
          }
        }
        evol_skill_list.push(evol_skill_item)
      }

      return evol_skill_list
    },
    get_pet_num(roleInfo) {
      return roleInfo.pet_info.length + roleInfo.split_pets.length
    },
    get_equip_num(roleInfo) {
      return roleInfo.using_equips.length + roleInfo.not_using_equips.length + roleInfo.split_equips.length
    },
    async handleEquipPrice({ roleInfo: { using_equips, not_using_equips, split_equips, basic_info }, serverid, server_name, eid }, rowIndex) {
      console.log({ rowIndex })
      const equip_list = [...using_equips, ...not_using_equips, ...split_equips].map((item) => ({ ...item, iType: item.type, cDesc: item.desc, serverid, server_name }))
      this.valuationDialogTitle = {
        nickname: basic_info.nickname,
        school: basic_info.school,
        server_name,
        eid
      }

      try {
        // 先显示弹窗和骨架屏
        this.valuationDialogVisible = true
        this.valuationLoading = true
        this.valuationResults = []
        this.valuationTotalValue = 0
        this.valuationEquipmentList = equip_list
        // 调用批量估价API
        const response = await this.$api.equipment.batchEquipmentValuation({
          eid,
          equipment_list: equip_list,
          strategy: 'fair_value',
          similarity_threshold: this.batchValuateParams.similarity_threshold,
          max_anchors: this.batchValuateParams.max_anchors
        })

        if (response.code === 200) {
          const data = response.data
          const results = data.results || []
          const totalValue = results.reduce((sum, result) => {
            return sum + (result.estimated_price || 0)
          }, 0)
          this.$set(this.tableData[rowIndex], 'equip_price', data.equip_price)
          // 更新弹窗内容，显示实际数据
          this.valuationResults = results
          this.valuationTotalValue = totalValue
          this.valuationLoading = false
        } else {
          this.$notify.error({
            title: '错误',
            message: response.message || '装备估价失败'
          })
          this.closeValuationDialog()
        }
      } catch (error) {
        console.error('装备估价失败:', error)
        this.$notify.error({
          title: '错误',
          message: '装备估价失败'
        })
        this.closeValuationDialog()
      } finally {
        this.valuationLoading = false
      }
    },
    get_school_name: window.get_school_name,
    handleSortChange({ prop, order }) {
      this.sortState[prop] = order

      const sortFields = []
      const sortOrders = []
      for (const [field, order] of Object.entries(this.sortState)) {
        if (order) {
          sortFields.push(field)
          sortOrders.push(order === 'ascending' ? 'ASC' : 'DESC')
        }
      }

      this.$set(this.searchForm, 'sort_by', sortFields.join(','))
      this.$set(this.searchForm, 'sort_order', sortOrders.join(','))

      // 更新路由query参数，同步排序状态到地址栏
      const newQuery = { ...this.$route.query }
      const oldSortBy = this.$route.query.sort_by
      const oldSortOrder = this.$route.query.sort_order

      if (sortFields.length > 0) {
        newQuery.sort_by = sortFields.join(',')
        newQuery.sort_order = sortOrders.join(',')
      } else {
        // 如果没有排序，移除排序参数
        delete newQuery.sort_by
        delete newQuery.sort_order
      }

      // 只有当排序参数发生变化时才更新路由
      if (newQuery.sort_by !== oldSortBy || newQuery.sort_order !== oldSortOrder) {
        this.$router.replace({
          name: this.$route.name,
          params: this.$route.params,
          query: newQuery
        })
        this.handleSearch()
      }
    },
    async fetchData() {
      this.loading = true
      try {
        const [year, month] = this.searchForm.selectedDate.split('-')
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          year,
          month,
          role_type: this.roleType // 添加角色类型参数
        }

        // 添加搜索条件
        if (this.searchForm.level_min) {
          params.level_min = this.searchForm.level_min
        }
        if (this.searchForm.level_max) {
          params.level_max = this.searchForm.level_max
        }
        if (this.searchForm.equip_num !== undefined) {
          params.equip_num = this.searchForm.equip_num
        }
        if (this.searchForm.pet_num) {
          params.pet_num = this.searchForm.pet_num
        }
        if (this.searchForm.pet_num_level) {
          params.pet_num_level = this.searchForm.pet_num_level
        }
        if (this.searchForm.accept_bargain) {
          params.accept_bargain = this.searchForm.accept_bargain
        }
        // 排序参数
        if (this.searchForm.sort_by) params.sort_by = this.searchForm.sort_by
        if (this.searchForm.sort_order) params.sort_order = this.searchForm.sort_order

        // 使用新的API
        const response = await this.$api.role.getRoleApi(params)

        if (response.code === 200) {
          // 现在直接使用response.data和response.items
          this.tableData = response.data.data.map(item => {
            const roleInfo = new window.RoleInfoParser(item.large_equip_desc, { equip_level: item.equip_level })
            item.RoleInfoParser = roleInfo
            if (roleInfo.result) {
              item.roleInfo = roleInfo.result
            }
            // 检查当前角色是否在锁定列表中
            item.is_sticky = this.stickyRoleList.some(sticky => sticky.eid === item.eid)
            return item
          }) || []
          this.total = response.data.total || 0
        } else {
          this.$notify.error({
            title: '错误',
            message: response.message || '获取数据失败'
          })
        }
      } finally {
        this.loading = false
      }
    },

    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1

      // 更新路由参数，移除页码参数（因为重置到第1页）
      const newParams = {
        type: this.roleType,
        levelRange: this.$route.params.levelRange
      }

      this.safeRouteUpdate(newParams)

      this.fetchData()
    },

    handleCurrentChange(val) {
      this.currentPage = val

      // 更新路由参数以反映当前页码
      const newParams = {
        type: this.roleType,
        levelRange: this.$route.params.levelRange
      }

      // 只有当页码大于1时才添加到路由参数中
      if (val > 1) {
        newParams.page = val.toString()
      }

      this.safeRouteUpdate(newParams)

      this.fetchData()
    },

    handleDateChange() {
      this.currentPage = 1

      // 更新路由参数，移除页码参数（因为重置到第1页）
      const newParams = {
        type: this.roleType,
        levelRange: this.$route.params.levelRange
      }

      this.safeRouteUpdate(newParams)

      this.fetchData()
    },


    handleQuickLevelSelect(level) {
      this.searchForm.level_min = level
      this.searchForm.level_max = level

      // 检查是否需要更新路由参数
      const currentLevelRange = this.$route.params.levelRange
      const newLevelRange = `${level},${level}`

      // 只有当等级范围发生变化时才更新路由
      if (currentLevelRange !== newLevelRange) {
        this.$router.replace({
          name: 'RoleList',
          params: {
            type: this.roleType,
            levelRange: newLevelRange,
            page: 1
          },
          query: this.$route.query
        })
      }

      this.fetchData()
    },

    handleLevelChange() {
      // 当等级输入框变化时，更新路由参数
      const newLevelRange = this.searchForm.level_min && this.searchForm.level_max
        ? `${this.searchForm.level_min},${this.searchForm.level_max}`
        : undefined

      const currentLevelRange = this.$route.params.levelRange
      if (newLevelRange !== currentLevelRange) {
        this.$router.replace({
          name: 'RoleList',
          params: {
            type: this.roleType,
            levelRange: newLevelRange
          },
          query: this.$route.query
        })
      }
    },

    handleSearch() {
      // 更新路由参数以反映当前的搜索条件
      const newLevelRange = this.searchForm.level_min && this.searchForm.level_max
        ? `${this.searchForm.level_min},${this.searchForm.level_max}`
        : undefined

      // 构建query参数，包含所有搜索表单参数
      const newQuery = { ...this.$route.query }
      
      // 同步搜索表单参数到query
      if (this.searchForm.selectedDate) {
        newQuery.selectedDate = this.searchForm.selectedDate
      } else {
        delete newQuery.selectedDate
      }
      
      if (this.searchForm.equip_num !== undefined && this.searchForm.equip_num !== '') {
        newQuery.equip_num = this.searchForm.equip_num.toString()
      } else {
        delete newQuery.equip_num
      }
      
      if (this.searchForm.pet_num !== undefined && this.searchForm.pet_num !== '') {
        newQuery.pet_num = this.searchForm.pet_num.toString()
      } else {
        delete newQuery.pet_num
      }
      
      if (this.searchForm.pet_num_level !== undefined && this.searchForm.pet_num_level !== '') {
        newQuery.pet_num_level = this.searchForm.pet_num_level.toString()
      } else {
        delete newQuery.pet_num_level
      }
      
      if (this.searchForm.accept_bargain !== undefined && this.searchForm.accept_bargain !== '') {
        newQuery.accept_bargain = this.searchForm.accept_bargain
      } else {
        delete newQuery.accept_bargain
      }

      // 更新路由参数，移除页码参数（因为重置到第1页）
      const newParams = {
        type: this.roleType,
        levelRange: newLevelRange
      }

      // 只有当页码大于1时才添加到路由参数中
      if (this.currentPage > 1) {
        newParams.page = this.currentPage.toString()
      }

      // 检查是否需要更新路由
      const hasParamChanges = JSON.stringify(newParams) !== JSON.stringify(this.$route.params)
      const hasQueryChanges = JSON.stringify(newQuery) !== JSON.stringify(this.$route.query)

      if (hasParamChanges || hasQueryChanges) {
        this.$router.replace({
          name: 'RoleList',
          params: newParams,
          query: newQuery
        })
      }

      this.fetchData()
    },

    handleReset() {
      this.searchForm = {
        selectedDate: dayjs().format('YYYY-MM'),
        level_min: undefined,
        level_max: undefined,
        equip_num: undefined,
        pet_num: undefined,
        pet_num_level: undefined,
        sort_by: undefined,
        sort_order: undefined,
        accept_bargain: undefined
      }

      // 清空排序状态
      this.sortState = {}

      this.currentPage = 1

      // 更新路由参数，移除页码参数（因为重置到第1页）
      const newParams = {
        type: this.roleType,
        levelRange: undefined
      }

      // 清除query中的所有搜索参数
      const newQuery = { ...this.$route.query }
      delete newQuery.selectedDate
      delete newQuery.equip_num
      delete newQuery.pet_num
      delete newQuery.pet_num_level
      delete newQuery.accept_bargain
      delete newQuery.sort_by
      delete newQuery.sort_order

      // 只有当参数发生变化时才更新路由
      const hasParamChanges = JSON.stringify(newParams) !== JSON.stringify(this.$route.params)
      const hasQueryChanges = JSON.stringify(newQuery) !== JSON.stringify(this.$route.query)

      if (hasParamChanges || hasQueryChanges) {
        this.$router.replace({
          name: 'RoleList',
          params: newParams,
          query: newQuery
        })
      }

      this.fetchData()
    },

    handleRoleTypeChange() {
      this.currentPage = 1

      // 更新路由参数，移除页码参数（因为重置到第1页）
      const newParams = {
        type: this.roleType,
        levelRange: this.$route.params.levelRange
      }

      this.safeRouteUpdate(newParams)

      this.fetchData()
    },

    extractServerId(equipId) {
      // 从equip_id中提取服务器ID
      // 格式通常是: 服务器ID_其他信息
      const parts = equipId.split('-')
      return parts[1] || null
    }
  }
}
</script>

<style scoped>
.page-header {
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.filters {
  margin-bottom: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.mx-2 {
  margin: 0 8px;
}

.level-quick-select {
  margin-left: 16px;
  display: inline-block;
}

.level-quick-select .el-button {
  margin-right: 8px;
  margin-bottom: 8px;
}

.cultivation-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cultivation-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.text-gray {
  color: #909399;
  font-size: 12px;
}

.role-link {
  color: #409eff;
  text-decoration: none;
}

.role-link:hover {
  text-decoration: underline;
}

.equip-desc {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sticky-wrapper {
  position: relative;
  width: 50px;
  height: 50px;
  margin: 0 auto;
}

.sticky-wrapper .el-checkbox {
  position: absolute;
  top: 0;
  right: 0;
  font-size: 0;
  line-height: 0;
  display: none;
}

.sticky-wrapper .el-checkbox.is-checked {
  display: block;
}

.sticky-wrapper :deep(.el-checkbox.is-checked .el-checkbox__inner) {
  background-color: #F56C6C !important;
  border-color: #F56C6C !important;
}

.sticky-wrapper :deep(.el-checkbox .el-checkbox__label) {
  display: none;
}

.hover-row .sticky-wrapper .el-checkbox {
  display: block;
}

/* 角色估价单元格样式 */
.role-valuation-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.role-valuation-cell>* {
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
</style>
