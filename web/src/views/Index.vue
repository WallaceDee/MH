<template>
  <div class="portal-container">
    <!-- 头部横幅区域 -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <i class="el-icon-data-analysis"></i>
          梦幻灵瞳 - CBG数据分析平台
        </h1>
        <p class="hero-subtitle">
          专业的梦幻西游藏宝阁数据分析与估价系统
        </p>
      </div>
    </div>

    <!-- 功能模块区域 -->
    <div class="features-section">
      <div class="section-title">
        <h2>核心功能</h2>
        <p>全面的数据分析与处理工具</p>
      </div>
      
      <div class="features-grid">
        <!-- 数据监控 -->
        <div class="feature-card">
          <div class="feature-icon">
            <i class="el-icon-connection"></i>
          </div>
          <h3>数据监控</h3>
          <p>自动化数据监控，支持角色、装备、召唤兽等多种数据类型</p>
          <div class="feature-stats">
            <span class="stat-item">
              <i class="el-icon-timer"></i>
              实时监控
            </span>
            <span class="stat-item">
              <i class="el-icon-setting"></i>
              智能配置
            </span>
          </div>
        </div>

        <!-- 装备分析 -->
        <div class="feature-card">
          <div class="feature-icon">
            <i class="el-icon-medal"></i>
          </div>
          <h3>装备分析</h3>
          <p>装备数据深度分析，智能估价与相似装备推荐</p>
          <div class="feature-stats">
            <span class="stat-item">
              <i class="el-icon-coin"></i>
              智能估价
            </span>
            <span class="stat-item">
              <i class="el-icon-search"></i>
              相似推荐
            </span>
          </div>
        </div>

        <!-- 角色管理 -->
        <div class="feature-card">
          <div class="feature-icon">
            <i class="el-icon-user"></i>
          </div>
          <h3>角色管理</h3>
          <p>角色信息分析与处理，支持多等级段筛选</p>
          <div class="feature-stats">
            <span class="stat-item">
              <i class="el-icon-filter"></i>
              智能筛选
            </span>
            <span class="stat-item">
              <i class="el-icon-view"></i>
              详情查看
            </span>
          </div>
        </div>

        <!-- 召唤兽分析 -->
        <div class="feature-card">
          <div class="feature-icon">
            <i class="el-icon-star-on"></i>
          </div>
          <h3>召唤兽分析</h3>
          <p>召唤兽数据分析与估价处理</p>
          <div class="feature-stats">
            <span class="stat-item">
              <i class="el-icon-coin"></i>
              估价分析
            </span>
            <span class="stat-item">
              <i class="el-icon-picture"></i>
              图片展示
            </span>
          </div>
        </div>

        <!-- 市场数据 -->
        <div class="feature-card">
          <div class="feature-icon">
            <i class="el-icon-data-board"></i>
          </div>
          <h3>市场数据</h3>
          <p>实时市场数据监控与统计分析</p>
          <div class="feature-stats">
            <span class="stat-item">
              <i class="el-icon-trend-charts"></i>
              趋势分析
            </span>
            <span class="stat-item">
              <i class="el-icon-pie-chart"></i>
              数据可视化
            </span>
          </div>
        </div>

        <!-- 装备模拟 -->
        <div class="feature-card">
          <div class="feature-icon">
            <i class="el-icon-edit"></i>
          </div>
          <h3>装备模拟</h3>
          <p>装备描述生成与模拟工具</p>
          <div class="feature-stats">
            <span class="stat-item">
              <i class="el-icon-magic-stick"></i>
              智能生成
            </span>
            <span class="stat-item">
              <i class="el-icon-picture-outline"></i>
              可视化
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据统计区域 -->
    <div class="stats-section">
      <div class="section-title">
        <h2>数据概览</h2>
        <p>实时数据统计信息</p>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="el-icon-user"></i>
          </div>
          <div class="stat-content">
            <h3>{{ statsData.roleCount || 0 }}</h3>
            <p>角色数量</p>
            <div class="stat-update">
              <i class="el-icon-time"></i>
              <span>最后更新: {{ statsData.roleLastUpdate || '--' }}</span>
            </div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="el-icon-medal"></i>
          </div>
          <div class="stat-content">
            <h3>{{ statsData.equipmentCount || 0 }}</h3>
            <p>装备数量</p>
            <div class="stat-update">
              <i class="el-icon-time"></i>
              <span>最后更新: {{ statsData.equipmentLastUpdate || '--' }}</span>
            </div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="el-icon-star-on"></i>
          </div>
          <div class="stat-content">
            <h3>{{ statsData.petCount || 0 }}</h3>
            <p>召唤兽数量</p>
            <div class="stat-update">
              <i class="el-icon-time"></i>
              <span>最后更新: {{ statsData.petLastUpdate || '--' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'Index',
  data() {
    return {
      statsData: {
        roleCount: 0,
        equipmentCount: 0,
        petCount: 0,
        roleLastUpdate: '--',
        equipmentLastUpdate: '--',
        petLastUpdate: '--'
      }
    }
  },
  mounted() {
    this.loadStatsData()
  },
  methods: {
    // 加载统计数据
    async loadStatsData() {
      try {
        // 并行请求各种统计数据
        const [roleStats, equipmentStats, petStats] = await Promise.all([
          this.$api.role.getRoleStats().catch(() => ({ code: 200, data: { total: 0, lastUpdate: '--' } })),
          this.$api.equipment.getEquipmentStats().catch(() => ({ code: 200, data: { total: 0, lastUpdate: '--' } })),
          this.$api.pet.getPetStats().catch(() => ({ code: 200, data: { total: 0, lastUpdate: '--' } }))
        ])

        // 处理API响应数据，从data字段中获取实际数据
        this.statsData = {
          roleCount: (roleStats.code === 200 && roleStats.data) ? (roleStats.data.total || 0) : 0,
          equipmentCount: (equipmentStats.code === 200 && equipmentStats.data) ? (equipmentStats.data.total || 0) : 0,
          petCount: (petStats.code === 200 && petStats.data) ? (petStats.data.total || 0) : 0,
          roleLastUpdate: (roleStats.code === 200 && roleStats.data) ? (roleStats.data.lastUpdate || '--') : '--',
          equipmentLastUpdate: (equipmentStats.code === 200 && equipmentStats.data) ? (equipmentStats.data.lastUpdate || '--') : '--',
          petLastUpdate: (petStats.code === 200 && petStats.data) ? (petStats.data.lastUpdate || '--') : '--'
        }

        console.log('统计数据加载完成:', this.statsData)
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.portal-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 头部横幅区域 */
.hero-section {
  padding: 80px 20px;
  text-align: center;
  color: white;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 20px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.hero-title i {
  margin-right: 15px;
  color: #ffd700;
}

.hero-subtitle {
  font-size: 1.3rem;
  margin-bottom: 40px;
  opacity: 0.9;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.hero-actions .el-button {
  padding: 15px 30px;
  font-size: 16px;
  border-radius: 50px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.hero-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

/* 功能模块区域 */
.features-section {
  padding: 80px 20px;
  background: white;
}

.section-title {
  text-align: center;
  margin-bottom: 60px;
}

.section-title h2 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 15px;
}

.section-title p {
  font-size: 1.1rem;
  color: #666;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  border-color: #409eff;
}

.feature-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #409eff, #67c23a);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.feature-icon i {
  font-size: 2rem;
  color: white;
}

.feature-card h3 {
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 15px;
  font-weight: 600;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
}

.feature-stats {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  background: #f0f9ff;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #409eff;
  font-weight: 500;
}

/* 数据统计区域 */
.stats-section {
  padding: 80px 20px;
  background: #f8f9fa;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  max-width: 1000px;
  margin: 0 auto;
}

.stat-card {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #67c23a, #85ce61);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon i {
  font-size: 1.5rem;
  color: white;
}

.stat-content h3 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 5px;
  font-weight: 700;
}

.stat-content p {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.stat-update {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #999;
  font-size: 0.8rem;
  margin-top: 5px;
}

.stat-update i {
  font-size: 0.8rem;
}

.stat-update span {
  font-size: 0.8rem;
}


/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .hero-actions .el-button {
    width: 200px;
  }
}
</style>
