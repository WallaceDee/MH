<template>
  <div class="market-data-charts">
    <!-- 图表区域 -->
    <el-row :gutter="20">
      <!-- 等级分布图 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header" class="chart-header">
            <i class="el-icon-s-data"></i>
            <span>等级分布</span>
          </div>
          <div ref="levelChart" class="chart-container"></div>
        </el-card>
      </el-col>

      <!-- 价格分布图 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header" class="chart-header">
            <i class="el-icon-money"></i>
            <span>价格分布</span>
          </div>
          <div ref="priceChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行图表 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 等级与价格关系散点图 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header" class="chart-header">
            <i class="el-icon-s-marketing"></i>
            <span>等级与价格关系</span>
          </div>
          <div ref="levelPriceChart" class="chart-container"></div>
        </el-card>
      </el-col>

      <!-- 门派分布饼图 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header" class="chart-header">
            <i class="el-icon-pie-chart"></i>
            <span>门派分布</span>
          </div>
          <div ref="schoolChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第三行图表 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 服务器分布 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header" class="chart-header">
            <i class="el-icon-s-platform"></i>
            <span>服务器分布（TOP 10）</span>
          </div>
          <div ref="serverChart" class="chart-container"></div>
        </el-card>
      </el-col>

      <!-- 价格趋势（按等级） -->
      <el-col :span="12">
        <el-card class="chart-card">
          <div slot="header" class="chart-header">
            <i class="el-icon-s-finance"></i>
            <span>价格趋势（按等级）</span>
          </div>
          <div ref="priceTrendChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'MarketDataCharts',
  props: {
    marketData: {
      type: Object,
      default: () => ({})
    }
  },
  
  data() {
    return {
      charts: {
        levelChart: null,
        priceChart: null,
        levelPriceChart: null,
        schoolChart: null,
        serverChart: null,
        priceTrendChart: null
      }
    }
  },

  mounted() {
    this.initCharts()
    this.updateCharts()
    
    // 监听窗口大小变化
    window.addEventListener('resize', this.handleResize)
  },

  beforeDestroy() {
    // 清理图表实例
    Object.values(this.charts).forEach(chart => {
      if (chart) {
        chart.dispose()
      }
    })
    
    window.removeEventListener('resize', this.handleResize)
  },

  watch: {
    marketData: {
      handler() {
        this.updateCharts()
      },
      deep: true
    }
  },

  methods: {
    initCharts() {
      // 初始化所有图表
      this.charts.levelChart = echarts.init(this.$refs.levelChart)
      this.charts.priceChart = echarts.init(this.$refs.priceChart)
      this.charts.levelPriceChart = echarts.init(this.$refs.levelPriceChart)
      this.charts.schoolChart = echarts.init(this.$refs.schoolChart)
      this.charts.serverChart = echarts.init(this.$refs.serverChart)
      this.charts.priceTrendChart = echarts.init(this.$refs.priceTrendChart)
    },

    updateCharts() {
      if (!this.marketData || !this.marketData.data_count) {
        this.showNoDataCharts()
        return
      }

      // 从API获取详细数据进行分析
      this.fetchDetailedDataAndUpdateCharts()
    },

    async fetchDetailedDataAndUpdateCharts() {
      try {
        // 调用数据分析接口获取真实数据
        const response = await this.$api.system.getMarketDataAnalysis()
        if (response.code === 200) {
          const analysisData = response.data
          
          // 使用真实数据更新图表
          this.updateLevelDistributionChart(analysisData.level_distribution)
          this.updatePriceDistributionChart(analysisData.price_distribution)
          this.updateLevelPriceRelationChart(analysisData.level_price_relation, analysisData.price_trend)
          this.updateSchoolDistributionChart(analysisData.school_distribution)
          this.updateServerDistributionChart(analysisData.server_distribution)
          this.updatePriceTrendChart(analysisData.price_trend)
        } else {
          console.warn('获取分析数据失败，使用示例数据')
          this.updateChartsWithSampleData()
        }
      } catch (error) {
        console.error('获取分析数据失败:', error)
        this.updateChartsWithSampleData()
      }
    },

    updateLevelDistributionChart(levelData) {
      // 等级分布柱状图
      const categories = levelData ? levelData.categories : ['109-119', '120-129', '130-139', '140-149', '150-159', '160-175']
      const values = levelData ? levelData.values : [120, 200, 150, 80, 60, 90]
      
      const option = {
        title: {
          text: '角色等级分布',
          left: 'center',
          textStyle: { fontSize: 14 }
        },
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c} 个角色'
        },
        xAxis: {
          type: 'category',
          data: categories,
          axisLabel: { fontSize: 12 }
        },
        yAxis: {
          type: 'value',
          axisLabel: { fontSize: 12 }
        },
        series: [{
          data: values,
          type: 'bar',
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
          }
        }]
      }
      
      this.charts.levelChart.setOption(option)
    },

    updatePriceDistributionChart(priceData) {
      // 价格分布直方图
      const categories = priceData ? priceData.categories : ['<1000', '1000-5000', '5000-10000', '10000-20000', '20000-50000', '>50000']
      const values = priceData ? priceData.values : [50, 180, 120, 80, 40, 30]
      
      const option = {
        title: {
          text: '价格分布',
          left: 'center',
          textStyle: { fontSize: 14 }
        },
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c} 个角色'
        },
        xAxis: {
          type: 'category',
          data: categories,
          axisLabel: { fontSize: 12 }
        },
        yAxis: {
          type: 'value',
          axisLabel: { fontSize: 12 }
        },
        series: [{
          data: values,
          type: 'bar',
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#ffd666' },
              { offset: 0.5, color: '#f7ba2a' },
              { offset: 1, color: '#f7ba2a' }
            ])
          }
        }]
      }
      
      this.charts.priceChart.setOption(option)
    },

    updateLevelPriceRelationChart(relationData, trendData) {
      // 等级与价格关系散点图
      const scatterData = relationData ? relationData.data : this.generateScatterData()
      
      const option = {
        title: {
          text: '等级与价格关系',
          left: 'center',
          textStyle: { fontSize: 14 }
        },
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            return `等级: ${params.data[0]}<br/>价格: ${params.data[1].toLocaleString()} 元`
          }
        },
        xAxis: {
          type: 'value',
          name: '等级',
          nameLocation: 'middle',
          nameGap: 30,
          axisLabel: { fontSize: 12 }
        },
        yAxis: {
          type: 'value',
          name: '价格(元)',
          nameLocation: 'middle',
          nameGap: 50,
          axisLabel: { 
            fontSize: 12,
            formatter: function(value) {
              if (value >= 10000) {
                return (value / 10000).toFixed(1) + '万'
              } else if (value >= 1000) {
                return (value / 1000).toFixed(1) + 'k'
              }
              return value
            }
          }
        },
        series: [{
          data: scatterData,
          type: 'scatter',
          itemStyle: {
            color: '#73c0de',
            opacity: 0.6
          }
        }]
      }
      
      this.charts.levelPriceChart.setOption(option)
    },

    updateSchoolDistributionChart(schoolData) {
      // 门派分布饼图
      const data = schoolData 
      const option = {
        title: {
          text: '门派分布',
          left: 'center',
          textStyle: { fontSize: 14 }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: '5%',
          top: 'center',
          textStyle: { fontSize: 10 },
          itemWidth: 10,
          itemHeight: 10,
          itemGap: 8
        },
        series: [{
          type: 'pie',
          radius: ['20%', '45%'],
          center: ['70%', '50%'],
          data: data.map(item => {
            return ({ value: item.value, name: window.CBG_GAME_CONFIG.school_info[item.name] })
        }),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
      
      this.charts.schoolChart.setOption(option)
    },

    updateServerDistributionChart(serverData) {
      const serverNames = serverData.server_ids?.map(id =>{
        console.log('id', id)
        for (let key in window.server_data) {
        let [,children] = window.server_data[key]
        let server = children.find(item => item[0] === id)
        if (server) {
            return server[1]
          }
        }
        return ''
      }) 
      const counts =serverData.counts 
      const option = {
        title: {
          text: '热门服务器 TOP 10',
          left: 'center',
          textStyle: { fontSize: 14 }
        },
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c} 个角色'
        },
        xAxis: {
          type: 'value',
          axisLabel: { fontSize: 12 }
        },
        yAxis: {
          type: 'category',
          data: serverNames,
          axisLabel: { fontSize: 12 }
        },
        series: [{
          data: counts,
          type: 'bar',
          itemStyle: {
            color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
          }
        }]
      }
      
      this.charts.serverChart.setOption(option)
    },

    updatePriceTrendChart(trendData) {
      // 价格趋势线图（按等级）
      const levels = trendData ? trendData.levels : ['109', '119', '129', '139', '149', '159', '169', '175']
      const avgPrices = trendData ? trendData.avg_prices : [3000, 4500, 6000, 8500, 12000, 18000, 25000, 35000]
      
      const option = {
        title: {
          text: '平均价格趋势',
          left: 'center',
          textStyle: { fontSize: 14 }
        },
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            const data = params[0]
            return `等级 ${data.name}: ${data.value.toLocaleString()} 元`
          }
        },
        xAxis: {
          type: 'category',
          data: levels,
          name: '等级',
          nameLocation: 'middle',
          nameGap: 30,
          axisLabel: { fontSize: 12 }
        },
        yAxis: {
          type: 'value',
          name: '平均价格(元)',
          nameLocation: 'middle',
          nameGap: 50,
          axisLabel: { 
            fontSize: 12,
            formatter: function(value) {
              if (value >= 10000) {
                return (value / 10000).toFixed(1) + '万'
              } else if (value >= 1000) {
                return (value / 1000).toFixed(1) + 'k'
              }
              return value
            }
          }
        },
        series: [{
          data: avgPrices,
          type: 'line',
          smooth: true,
          itemStyle: {
            color: '#91cc75'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(145, 204, 117, 0.3)' },
              { offset: 1, color: 'rgba(145, 204, 117, 0.1)' }
            ])
          }
        }]
      }
      
      this.charts.priceTrendChart.setOption(option)
    },

    generateScatterData() {
      // 生成散点图数据（等级vs价格）
      const data = []
      for (let i = 0; i < 200; i++) {
        const level = Math.floor(Math.random() * (175 - 109 + 1)) + 109
        const basePrice = (level - 109) * 300 + 2000
        const price = basePrice + (Math.random() - 0.5) * basePrice * 0.8
        data.push([level, Math.max(1000, price)])
      }
      return data
    },

    showNoDataCharts() {
      // 显示无数据状态
      const noDataOption = {
        title: {
          text: '暂无数据',
          left: 'center',
          top: 'middle',
          textStyle: {
            color: '#999',
            fontSize: 16
          }
        }
      }

      Object.values(this.charts).forEach(chart => {
        if (chart) {
          chart.setOption(noDataOption)
        }
      })
    },

    updateChartsWithSampleData() {
      // 使用示例数据更新图表
      this.updateLevelDistributionChart()
      this.updatePriceDistributionChart()
      this.updateLevelPriceRelationChart()
      this.updateSchoolDistributionChart()
      this.updateServerDistributionChart()
      this.updatePriceTrendChart()
    },

    handleResize() {
      // 处理窗口大小变化
      Object.values(this.charts).forEach(chart => {
        if (chart) {
          chart.resize()
        }
      })
    }
  }
}
</script>

<style scoped>
.market-data-charts {
  padding: 20px;
}

.chart-card {
  height: 450px;
}

.chart-header {
  display: flex;
  align-items: center;
}

.chart-header i {
  margin-right: 8px;
  font-size: 16px;
  color: #409EFF;
}

.chart-container {
  height: 370px;
  width: 100%;
}
</style>
