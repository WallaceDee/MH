<template>
  <div class="market-data-status">
    <div class="page-header">
      <h1>市场数据状态监控</h1>
      <p>实时监控空角色市场数据和装备数据的加载状态和统计信息</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="refreshStatus" :loading="loading" icon="el-icon-refresh">
        刷新状态
      </el-button>
    </div>

    <!-- 标签页 -->
    <el-card>
      <el-tabs v-model="activeTab" type="card" class="status-tabs">
        <!-- 角色数据标签页 -->
        <el-tab-pane label="角色数据" name="role">
          <div class="tab-content">
            <!-- 角色数据操作栏 -->
            <div class="tab-action-bar">
              <el-button type="success" @click="refreshMarketData" icon="el-icon-download" :disabled="refreshing">
                加载市场数据
              </el-button>

              <el-button type="warning" @click="refreshFullCache" icon="el-icon-refresh" :loading="fullCacheRefreshing">
                同步市场数据
              </el-button>
            </div>

            <!-- 角色数据状态卡片 -->
            <el-row :gutter="20" class="status-cards">
              <!-- 基本状态 -->
              <el-col :span="6">
                <el-card class="status-card">
                  <div slot="header" class="card-header">
                    <i class="el-icon-data-line"></i>
                    <span>数据状态</span>
                  </div>
                  <div class="status-item">
                    <span class="label">数据已加载:</span>
                    <el-tag :type="status.data_loaded ? 'success' : 'danger'">
                      {{ status.data_loaded ? '是' : '否' }}
                    </el-tag>
                  </div>
                  <div class="status-item">
                    <span class="label">数据条数:</span>
                    <span class="value">{{ status.data_count || 0 | numberFormat }}</span>
                  </div>
                  <div class="status-item">
                    <span class="label">MySQL总数:</span>
                    <span class="value">{{ status.mysql_data_count || 0 | numberFormat }} 条</span>
                  </div>
                  <div class="status-item">
                    <span class="label">内存占用:</span>
                    <span class="value">{{ (status.memory_usage_mb || 0).toFixed(2) }} MB</span>
                  </div>
                  <div class="status-item">
                    <span class="label">特征维度:</span>
                    <span class="value">{{ (status.data_columns || []).length }}</span>
                  </div>
                </el-card>
              </el-col>

              <!-- 缓存状态 -->
              <el-col :span="6">
                <el-card class="status-card">
                  <div slot="header" class="card-header">
                    <i class="el-icon-time"></i>
                    <span>缓存状态</span>
                  </div>
                  <div class="status-item">
                    <span class="label">缓存模式:</span>
                    <el-tag type="success">
                      永不过期
                    </el-tag>
                  </div>
                  <div class="status-item">
                    <span class="label">最后刷新:</span>
                    <span class="value">{{ formatTime(status.last_refresh_time) }}</span>
                  </div>
                  <div class="status-item">
                    <span class="label">刷新方式:</span>
                    <span class="value">仅手动刷新</span>
                  </div>
                  <div class="status-item">
                    <span class="label">数据稳定性:</span>
                    <el-tag type="success" size="mini">高</el-tag>
                  </div>
                </el-card>
              </el-col>


              <!-- 数据统计 -->
              <el-col :span="6">
                <el-card class="status-card">
                  <div slot="header" class="card-header">
                    <i class="el-icon-s-data"></i>
                    <span>数据统计</span>
                  </div>
                  <div v-if="status.price_statistics" class="status-item">
                    <span class="label">价格范围:</span>
                    <span class="value">
                      {{ status.price_statistics.min_price | numberFormat }} -
                      {{ status.price_statistics.max_price | numberFormat }}
                    </span>
                  </div>
                  <div v-if="status.price_statistics" class="status-item">
                    <span class="label">平均价格:</span>
                    <span class="value">{{ status.price_statistics.avg_price.toFixed(0) | numberFormat }}</span>
                  </div>
                  <div v-if="status.level_statistics" class="status-item">
                    <span class="label">等级范围:</span>
                    <span class="value">
                      {{ status.level_statistics.min_level }} - {{ status.level_statistics.max_level }}
                    </span>
                  </div>
                  <div v-if="status.role_type_distribution" class="status-item">
                    <span class="label">角色类型:</span>
                    <div class="role-type-tags">
                      <el-tag v-for="(count, type) in status.role_type_distribution" :key="type" size="mini">
                        {{ type }}: {{ count }}
                      </el-tag>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <!-- 数据字段详情卡片 -->
            <el-card class="details-card" v-if="status.data_columns && status.data_columns.length > 0">
              <div slot="header" class="card-header">
                <i class="el-icon-menu"></i>
                <span>数据字段 ({{ status.data_columns.length }})</span>
              </div>
              <div class="columns-grid">
                <el-tag v-for="column in status.data_columns" :key="column" size="small" class="column-tag">
                  {{ column }}
                </el-tag>
              </div>
            </el-card>

            <!-- 数据分析图表 -->
            <div v-if="status.data_count > 0" class="charts-section">
              <div class="section-header">
                <h2>数据分析</h2>
                <p>基于当前市场数据的统计分析和可视化展示</p>
              </div>
              <MarketDataCharts :market-data="status" />
            </div>
          </div>
        </el-tab-pane>

        <!-- 装备数据标签页 -->
        <el-tab-pane label="装备数据" name="equipment">
          <div class="tab-content">
            <!-- 装备数据操作栏 -->
            <div class="tab-action-bar">
              <el-button type="info" @click="refreshEquipmentData" icon="el-icon-box" :disabled="refreshing">
                从redis中加载数据
              </el-button>

              <el-button type="success" @click="incrementalUpdateEquipment" icon="el-icon-refresh-left" 
                :loading="equipmentIncrementalUpdating" :disabled="refreshing">
                增量更新
              </el-button>


              <el-button type="danger" @click="refreshEquipmentFullCache" icon="el-icon-refresh"
                :loading="equipmentCacheRefreshing">
                全量同步装备(mysql)
              </el-button>
            </div>

            <!-- 装备数据状态卡片 -->
            <el-row :gutter="20" class="equipment-status-cards">
              <!-- 装备缓存状态 -->
              <el-col :span="8">
                <el-card class="status-card">
                  <div slot="header" class="card-header">
                    <i class="el-icon-box"></i>
                    <span>装备缓存状态</span>
                  </div>
                  <div class="status-item">
                    <span class="label">数据已加载到内存:</span>
                    <el-tag :type="equipmentMarketDataStatus.data_loaded ? 'success' : 'danger'">
                      {{ equipmentMarketDataStatus.data_loaded ? '是' : '否' }}
                    </el-tag>
                  </div>
                  <div class="status-item">
                    <span class="label">内存数据条数:</span>
                    <span class="value">{{ equipmentMarketDataStatus.data_count || 0 | numberFormat }} 条</span>
                  </div>
                  <div class="status-item">
                    <span class="label">MySQL总数:</span>
                    <span class="value">{{ equipmentMarketDataStatus.mysql_data_count || 0 | numberFormat }} 条</span>
                  </div>
                  <div class="status-item">
                    <span class="label">Redis总数:</span>
                    <span class="value">{{ equipmentMarketDataStatus.redis_data_count || 0 | numberFormat }} 条</span>
                  </div>
                  <div class="status-item">
                    <span class="label">内存占用:</span>
                    <span class="value">{{ (equipmentMarketDataStatus.memory_usage_mb || 0).toFixed(2) }} MB</span>
                  </div>
                  <div class="status-item">
                    <span class="label">特征维度:</span>
                    <span class="value">{{ (equipmentMarketDataStatus.data_columns || []).length }}</span>
                  </div>
                  <div v-if="equipmentMarketDataStatus.last_refresh_time" class="status-item">
                    <span class="label">最后刷新:</span>
                    <span class="value">{{ formatTime(equipmentMarketDataStatus.last_refresh_time) }}</span>
                  </div>
                  <div v-if="equipmentIncrementalStatus.has_new_data" class="status-item">
                    <span class="label">新数据状态:</span>
                    <el-tag type="warning" size="mini">
                      发现 {{ equipmentIncrementalStatus.new_data_count || 0 }} 条新数据
                    </el-tag>
                  </div>
                  <div v-if="equipmentIncrementalStatus.last_update_time" class="status-item">
                    <span class="label">最后增量更新:</span>
                    <span class="value">{{ formatTime(equipmentIncrementalStatus.last_update_time) }}</span>
                  </div>
                </el-card>
              </el-col>

              <!-- 装备数据统计 -->
              <el-col :span="8">
                <el-card class="status-card">
                  <div slot="header" class="card-header">
                    <i class="el-icon-data-analysis"></i>
                    <span>装备数据统计</span>
                  </div>
                  <div v-if="equipmentMarketDataStatus.data_count" class="status-item">
                    <span class="label">总装备数:</span>
                    <span class="value">{{ equipmentMarketDataStatus.data_count | numberFormat }}</span>
                  </div>

                    <div v-if="equipmentMarketDataStatus.price_statistics" class="status-item">
                    <span class="label">价格范围:</span>
                    <span class="value">
                      {{ equipmentMarketDataStatus.price_statistics.min_price | numberFormat }} -
                      {{ equipmentMarketDataStatus.price_statistics.max_price | numberFormat }}
                    </span>
                  </div>
                  <div v-if="equipmentMarketDataStatus.price_statistics" class="status-item">
                    <span class="label">平均价格:</span>
                    <span class="value">{{ equipmentMarketDataStatus.price_statistics.avg_price.toFixed(0) |
                      numberFormat
                    }}</span>
                  </div>
                  <div v-if="equipmentMarketDataStatus.price_statistics" class="status-item">
                    <span class="label">中位数价格:</span>
                    <span class="value">{{ equipmentMarketDataStatus.price_statistics.median_price.toFixed(0) |
                      numberFormat }}</span>
                  </div>
                  <div v-if="equipmentMarketDataStatus.high_value_count" class="status-item">
                    <span class="label">高价值装备:</span>
                    <span class="value">{{ equipmentMarketDataStatus.high_value_count | numberFormat }} 条</span>
                  </div>
                  <div v-if="equipmentMarketDataStatus.special_skill_count" class="status-item">
                    <span class="label">特技装备:</span>
                    <span class="value">{{ equipmentMarketDataStatus.special_skill_count | numberFormat }} 条</span>
                  </div>
                  <div v-if="equipmentMarketDataStatus.level_statistics" class="status-item">
                    <span class="label">等级范围:</span>
                    <span class="value">
                      {{ equipmentMarketDataStatus.level_statistics.min_level }} -
                      {{ equipmentMarketDataStatus.level_statistics.max_level }}
                    </span>
                  </div>
                </el-card>
              </el-col>

              <!-- 装备价格统计 -->
              <el-col :span="8">
                <el-card class="status-card">
                  <div slot="header" class="card-header">
                    <i class="el-icon-coin"></i>
                    <span>装备价格统计</span>
                  </div>
                  <div class="equipment-type-tags">
                      <el-tag v-for="(count, kindid) in equipmentMarketDataStatus.kindid_distribution" :key="kindid"
                        size="mini" :type="getEquipmentTypeColor(kindid)">
                        {{ getEquipmentTypeName(kindid) }}: {{ count }}
                      </el-tag>
                    </div>
                 
                </el-card>
              </el-col>

            </el-row>

            <!-- 装备数据字段详情卡片 -->
            <el-card class="details-card"
              v-if="equipmentMarketDataStatus.data_columns && equipmentMarketDataStatus.data_columns.length > 0">
              <div slot="header" class="card-header">
                <i class="el-icon-menu"></i>
                <span>装备数据字段 ({{ equipmentMarketDataStatus.data_columns.length }})</span>
              </div>
              <div class="columns-grid">
                <el-tag v-for="column in equipmentMarketDataStatus.data_columns" :key="column" size="small"
                  class="column-tag">
                  {{ column }}
                </el-tag>
              </div>
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 召唤兽数据标签页 -->
        <el-tab-pane label="召唤兽数据" name="pet">
          <div class="tab-content">
            <!-- 召唤兽数据操作栏 -->
            <div class="tab-action-bar">
              <el-button type="success" @click="refreshPetData" icon="el-icon-star-off" :disabled="refreshing">
                加载召唤兽数据
              </el-button>

              <el-button type="warning" @click="refreshPetFullCache" icon="el-icon-refresh"
                :loading="petCacheRefreshing">
                同步召唤兽数据
              </el-button>
            </div>

            <!-- 召唤兽数据状态卡片 -->
            <el-row :gutter="20" class="pet-status-cards">
              <!-- 召唤兽缓存状态 -->
              <el-col :span="8">
                <el-card class="status-card">
                  <div slot="header" class="card-header">
                    <i class="el-icon-star-off"></i>
                    <span>召唤兽缓存状态</span>
                  </div>
                  <div class="status-item">
                    <span class="label">数据已加载:</span>
                    <el-tag :type="petMarketDataStatus.data_loaded ? 'success' : 'danger'">
                      {{ petMarketDataStatus.data_loaded ? '是' : '否' }}
                    </el-tag>
                  </div>
                  <div class="status-item">
                    <span class="label">数据条数:</span>
                    <span class="value">{{ petMarketDataStatus.data_count || 0 | numberFormat }} 条</span>
                  </div>
                  <div class="status-item">
                    <span class="label">MySQL总数:</span>
                    <span class="value">{{ petMarketDataStatus.mysql_data_count || 0 | numberFormat }} 条</span>
                  </div>
                  <div class="status-item">
                    <span class="label">内存占用:</span>
                    <span class="value">{{ (petMarketDataStatus.memory_usage_mb || 0).toFixed(2) }} MB</span>
                  </div>
                  <div class="status-item">
                    <span class="label">特征维度:</span>
                    <span class="value">{{ (petMarketDataStatus.data_columns || []).length }}</span>
                  </div>
                  <div v-if="petMarketDataStatus.last_refresh_time" class="status-item">
                    <span class="label">最后刷新:</span>
                    <span class="value">{{ formatTime(petMarketDataStatus.last_refresh_time) }}</span>
                  </div>
                </el-card>
              </el-col>

              <!-- 召唤兽数据统计 -->
              <el-col :span="8">
                <el-card class="status-card">
                  <div slot="header" class="card-header">
                    <i class="el-icon-data-analysis"></i>
                    <span>召唤兽数据统计</span>
                  </div>
                  <div v-if="petMarketDataStatus.data_count" class="status-item">
                    <span class="label">总召唤兽数:</span>
                    <span class="value">{{ petMarketDataStatus.data_count | numberFormat }}</span>
                  </div>

                  <div v-if="petMarketDataStatus.price_statistics" class="status-item">
                    <span class="label">价格范围:</span>
                    <span class="value">
                      {{ petMarketDataStatus.price_statistics.min_price | numberFormat }} -
                      {{ petMarketDataStatus.price_statistics.max_price | numberFormat }}
                    </span>
                  </div>
                  <div v-if="petMarketDataStatus.price_statistics" class="status-item">
                    <span class="label">平均价格:</span>
                    <span class="value">{{ petMarketDataStatus.price_statistics.avg_price.toFixed(0) |
                      numberFormat
                    }}</span>
                  </div>
                  <div v-if="petMarketDataStatus.price_statistics" class="status-item">
                    <span class="label">中位数价格:</span>
                    <span class="value">{{ petMarketDataStatus.price_statistics.median_price.toFixed(0) |
                      numberFormat }}</span>
                  </div>
                  <div v-if="petMarketDataStatus.level_statistics" class="status-item">
                    <span class="label">等级范围:</span>
                    <span class="value">
                      {{ petMarketDataStatus.level_statistics.min_level }} -
                      {{ petMarketDataStatus.level_statistics.max_level }}
                    </span>
                  </div>
                  <div v-if="petMarketDataStatus.role_grade_limit_statistics" class="status-item">
                    <span class="label">携带等级范围:</span>
                    <span class="value">
                      {{ petMarketDataStatus.role_grade_limit_statistics.min_role_grade_limit }} -
                      {{ petMarketDataStatus.role_grade_limit_statistics.max_role_grade_limit }}
                    </span>
                  </div>
                </el-card>
              </el-col>

              <!-- 召唤兽技能统计 -->
              <el-col :span="8">
                <el-card class="status-card">
                  <div slot="header" class="card-header">
                    <i class="el-icon-magic-stick"></i>
                    <span>召唤兽技能统计</span>
                  </div>
                  <div class="pet-skill-tags">
                    <el-tag v-for="(count, skill) in petMarketDataStatus.skill_distribution" :key="skill"
                      size="mini" type="primary">
                      {{ skill }}: {{ count }}
                    </el-tag>
                  </div>
                </el-card>
              </el-col>

            </el-row>

            <!-- 召唤兽数据字段详情卡片 -->
            <el-card class="details-card"
              v-if="petMarketDataStatus.data_columns && petMarketDataStatus.data_columns.length > 0">
              <div slot="header" class="card-header">
                <i class="el-icon-menu"></i>
                <span>召唤兽数据字段 ({{ petMarketDataStatus.data_columns.length }})</span>
              </div>
              <div class="columns-grid">
                <el-tag v-for="column in petMarketDataStatus.data_columns" :key="column" size="small"
                  class="column-tag">
                  {{ column }}
                </el-tag>
              </div>
            </el-card>
          </div>
        </el-tab-pane>

        <!-- Redis详细信息标签页 -->
        <el-tab-pane label="Redis详情" name="redis">
          <div class="tab-content">
            <!-- Redis基本状态卡片 -->
            <el-row :gutter="20" class="redis-basic-status">
              <el-col :span="8">
                <el-card class="status-card">
                  <div slot="header" class="card-header">
                    <i class="el-icon-cpu"></i>
                    <span>Redis连接状态</span>
                  </div>
                  <div class="status-item">
                    <span class="label">连接状态:</span>
                    <el-tag :type="redisStatusComputed.available ? 'success' : 'danger'">
                      {{ redisStatusComputed.available ? '已连接' : '未连接' }}
                    </el-tag>
                  </div>
                  <div v-if="redisStatusComputed.available" class="status-item">
                    <span class="label">Redis主机:</span>
                    <span class="value">{{ redisStatusComputed.host || '-' }}</span>
                  </div>
                  <div v-if="redisStatusComputed.available" class="status-item">
                    <span class="label">Redis端口:</span>
                    <span class="value">{{ redisStatusComputed.port || '-' }}</span>
                  </div>
                  <div v-if="redisStatusComputed.available" class="status-item">
                    <span class="label">Redis数据库:</span>
                    <span class="value">{{ redisStatusComputed.db || 0 }}</span>
                  </div>
                  <div v-if="redisStatusComputed.available" class="status-item">
                    <span class="label">连接池大小:</span>
                    <span class="value">{{ redisStatusComputed.connection_pool_size || 0 }}</span>
                  </div>
                </el-card>
              </el-col>

              <el-col :span="8">
                <el-card class="status-card">
                  <div slot="header" class="card-header">
                    <i class="el-icon-monitor"></i>
                    <span>Redis服务器信息</span>
                  </div>
                  <div v-if="redisStatusComputed.available" class="status-item">
                    <span class="label">Redis版本:</span>
                    <span class="value">{{ redisStatusComputed.redis_version || '-' }}</span>
                  </div>
                  <div v-if="redisStatusComputed.available" class="status-item">
                    <span class="label">内存使用:</span>
                    <span class="value">{{ redisStatusComputed.used_memory_human || '0B' }}</span>
                  </div>
                  <div v-if="redisStatusComputed.available" class="status-item">
                    <span class="label">峰值内存:</span>
                    <span class="value">{{ redisStatusComputed.used_memory_peak_human || '0B' }}</span>
                  </div>
                  <div v-if="redisStatusComputed.available" class="status-item">
                    <span class="label">缓存键数:</span>
                    <span class="value">{{ redisStatusComputed.cache_keys_count || 0 | numberFormat }}</span>
                  </div>
                  <div v-if="redisStatusComputed.available" class="status-item">
                    <span class="label">连接客户端:</span>
                    <span class="value">{{ redisStatusComputed.connected_clients || 0 }}</span>
                  </div>
                </el-card>
              </el-col>

              <el-col :span="8">
                <el-card class="status-card">
                  <div slot="header" class="card-header">
                    <i class="el-icon-time"></i>
                    <span>Redis运行状态</span>
                  </div>
                  <div v-if="redisStatusComputed.available" class="status-item">
                    <span class="label">运行时间:</span>
                    <span class="value">{{ formatUptime(redisStatusComputed.uptime_in_seconds) }}</span>
                  </div>
                  <div v-if="redisStatusComputed.available" class="status-item">
                    <span class="label">命令执行总数:</span>
                    <span class="value">{{ redisStatusComputed.total_commands_processed | numberFormat }}</span>
                  </div>
                  <div v-if="redisStatusComputed.available" class="status-item">
                    <span class="label">缓存命中数:</span>
                    <span class="value">{{ redisStatusComputed.keyspace_hits | numberFormat }}</span>
                  </div>
                  <div v-if="redisStatusComputed.available" class="status-item">
                    <span class="label">缓存未命中数:</span>
                    <span class="value">{{ redisStatusComputed.keyspace_misses | numberFormat }}</span>
                  </div>
                  <div v-if="redisStatusComputed.available" class="status-item">
                    <span class="label">命中率:</span>
                    <span class="value">{{ redisStatusComputed.hit_rate || getHitRate() }}%</span>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <!-- Redis详细信息卡片 -->
            <el-row :gutter="20" class="redis-details" v-if="redisStatusComputed.available">

              <!-- 缓存类型统计 -->
              <el-col :span="12">
                <el-card class="status-card">
                  <div slot="header" class="card-header">
                    <i class="el-icon-collection"></i>
                    <span>缓存类型统计</span>
                  </div>
                  <div v-if="cacheTypeStats && Object.keys(cacheTypeStats).length > 0">
                    <div v-for="(typeInfo, cacheType) in cacheTypeStats" :key="cacheType" class="cache-type-group">
                      <div class="cache-type-header">
                        <span class="label">{{ getCacheTypeLabel(cacheType) }}:</span>
                        <div class="cache-type-summary">
                          <span class="value">{{ typeInfo.count }} 个键</span>
                          <el-tag size="mini" class="ttl-tag" :type="typeInfo.ttl_hours === -1 ? 'success' : 'info'">
                            TTL: {{ typeInfo.ttl_hours === -1 ? '永不过期' : typeInfo.ttl_hours + 'h' }}
                          </el-tag>
                        </div>
                      </div>
                      <div v-if="typeInfo.key_details && typeInfo.key_details.length > 0" class="key-details">
                        <div v-for="keyInfo in typeInfo.key_details" :key="keyInfo.key" class="key-item">
                          <span class="key-name">{{ keyInfo.key }}</span>
                          <el-tag size="mini" :type="keyInfo.ttl_hours === -1 ? 'success' : 'info'" class="key-ttl">
                            {{ keyInfo.ttl_display }}
                          </el-tag>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="no-cache-data">
                    <span>暂无缓存类型数据</span>
                  </div>

                  <!-- 全量缓存详细信息 -->
                  <div v-if="fullCacheInfo && fullCacheInfo.full_cache_exists" class="full-cache-details">
                    <div class="status-item">
                      <span class="label">缓存类型:</span>
                      <el-tag :type="fullCacheInfo.cache_type === 'chunked' ? 'success' : 'info'" size="mini">
                        {{ fullCacheInfo.cache_type === 'chunked' ? '分块缓存' : '传统缓存' }}
                      </el-tag>
                    </div>
                    <div v-if="fullCacheInfo.chunk_info && fullCacheInfo.chunk_info.total_chunks" class="status-item">
                      <span class="label">分块信息:</span>
                      <span class="value">{{ fullCacheInfo.chunk_info.total_chunks }} 块 × {{
                        fullCacheInfo.chunk_info.chunk_size }} 行</span>
                    </div>
                    <div v-if="fullCacheInfo.chunk_info && fullCacheInfo.chunk_info.is_complete !== undefined"
                      class="status-item">
                      <span class="label">完整性:</span>
                      <el-tag :type="fullCacheInfo.chunk_info.is_complete ? 'success' : 'danger'" size="mini">
                        {{ fullCacheInfo.chunk_info.is_complete ? '完整' : '不完整' }}
                      </el-tag>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

      </el-tabs>

    </el-card>
    <!-- 刷新进度对话框 -->
    <el-dialog :title="progressDialogTitle" :visible.sync="showRefreshDialog" width="500px"
      :close-on-click-modal="false" :close-on-press-escape="!refreshing">
      <!-- 刷新进度显示 -->
      <div class="refresh-progress">
        <div class="progress-header">
          <i class="el-icon-loading"></i>
          <span>{{ progressMessage }}</span>
        </div>

        <!-- 进度条 -->
        <el-progress :percentage="refreshProgress" :status="refreshProgress === 100 ? 'success' : null"
          :stroke-width="8" />

        <!-- 进度详情 -->
        <div class="progress-details">
          <div class="progress-item">
            <span class="label">当前状态:</span>
            <span class="value">{{ refreshMessage }}</span>
          </div>
          <div class="progress-item" v-if="refreshedCount > 0">
            <span class="label">已处理:</span>
            <span class="value">{{ refreshedCount }} 条数据</span>
          </div>
          <div class="progress-item" v-if="totalBatches > 0">
            <span class="label">批次进度:</span>
            <span class="value">第 {{ currentBatch }} / {{ totalBatches }} 批</span>
          </div>
          <div class="progress-item" v-if="refreshStartTime">
            <span class="label">已耗时:</span>
            <span class="value">{{ getElapsedTime() }} 秒</span>
          </div>
        </div>
      </div>

      <div slot="footer" class="dialog-footer">
        <el-button @click="cancelRefresh" :disabled="refreshProgress === 100">
          {{ refreshProgress === 100 ? '完成' : '取消' }}
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { systemApi } from '@/api/system'
import MarketDataCharts from '@/components/MarketDataCharts.vue'

export default {
  name: 'MarketDataStatus',
  components: {
    MarketDataCharts
  },
  data() {
    return {
      loading: false,
      refreshing: false,
      showRefreshDialog: false,
      status: {},
      autoRefreshTimer: null,
      // 进度相关
      refreshProgress: 0,
      refreshMessage: '',
      refreshedCount: 0,
      refreshStartTime: null,
      progressTimer: null,
      currentBatch: 0,
      totalBatches: 0,
      // 全量缓存相关
      fullCacheRefreshing: false,
      // 装备数据相关
      equipmentCacheRefreshing: false,
      equipmentLoading: false,  // 区分装备加载和装备同步
      equipmentMarketDataStatus: {},  // 装备市场数据状态
      equipmentIncrementalUpdating: false,  // 装备增量更新状态
      equipmentIncrementalStatus: {},  // 装备增量更新状态信息
      // 召唤兽数据相关
      petCacheRefreshing: false,
      petLoading: false,  // 区分召唤兽加载和召唤兽同步
      petMarketDataStatus: {},  // 召唤兽市场数据状态
      redisStatus: {},  // Redis状态信息
      // 标签页相关
      activeTab: 'role'  // 默认显示角色数据标签页
    }
  },

  computed: {
    // Redis状态信息
    redisStatusComputed() {
      return this.redisStatus || { available: false }
    },

    // 缓存类型统计
    cacheTypeStats() {
      if (this.redisStatus && this.redisStatus.cache_types) {
        return this.redisStatus.cache_types
      }
      return {}
    },

    // 全量缓存信息
    fullCacheInfo() {
      // 从缓存状态API获取详细信息，这里先使用基本信息
      return {
        full_cache_exists: this.status.data_loaded || false,
        cache_type: 'unknown', // 可以通过额外API获取
        chunk_info: {}
      }
    },

    // 装备Redis状态信息
    equipmentRedisStatus() {
      return this.redisStatus || { available: false }
    },

    // 召唤兽Redis状态信息
    petRedisStatus() {
      return this.redisStatus || { available: false }
    },

    // 进度对话框标题
    progressDialogTitle() {
      if (this.petCacheRefreshing) {
        return '同步召唤兽数据'
      } else if (this.petLoading) {
        return '加载召唤兽数据'
      } else if (this.equipmentCacheRefreshing) {
        return '同步装备数据'
      } else if (this.equipmentLoading) {
        return '加载装备数据'
      } else if (this.equipmentIncrementalUpdating) {
        return '增量更新装备数据'
      } else if (this.fullCacheRefreshing) {
        return '同步市场数据'
      } else {
        return '加载市场数据'
      }
    },

    // 进度提示文本
    progressMessage() {
      if (this.petCacheRefreshing) {
        return '正在同步召唤兽数据...'
      } else if (this.petLoading) {
        return '正在加载召唤兽数据...'
      } else if (this.equipmentCacheRefreshing) {
        return '正在同步装备数据...'
      } else if (this.equipmentLoading) {
        return '正在加载装备数据...'
      } else if (this.equipmentIncrementalUpdating) {
        return '正在增量更新装备数据...'
      } else if (this.fullCacheRefreshing) {
        return '正在同步市场数据...'
      } else {
        return '正在加载市场数据...'
      }
    }
  },

  filters: {
    numberFormat(value) {
      if (!value && value !== 0) return '-'
      return new Intl.NumberFormat('zh-CN').format(value)
    }
  },

  mounted() {
    this.refreshStatus()
    // 设置自动刷新状态
    this.startAutoRefresh()

    // 监听页面可见性变化
    document.addEventListener('visibilitychange', this.handleVisibilityChange)
  },

  watch: {
    // 监听标签页切换，切换时刷新对应状态
    activeTab(newTab, oldTab) {
      if (newTab !== oldTab) {
        console.log(`标签页从 ${oldTab} 切换到 ${newTab}，刷新对应状态`)
        this.refreshStatus()
      }
    }
  },

  beforeDestroy() {
    // 清理所有定时器
    this.clearAllTimers()

    // 移除页面可见性监听器
    document.removeEventListener('visibilitychange', this.handleVisibilityChange)
  },

  // 添加 beforeUnmount 钩子（Vue 3兼容）
  beforeUnmount() {
    this.clearAllTimers()
    document.removeEventListener('visibilitychange', this.handleVisibilityChange)
  },

  methods: {
    // 清理所有定时器
    clearAllTimers() {
      if (this.autoRefreshTimer) {
        clearInterval(this.autoRefreshTimer)
        this.autoRefreshTimer = null
        console.log('已清理自动刷新定时器')
      }
      if (this.progressTimer) {
        clearInterval(this.progressTimer)
        this.progressTimer = null
        console.log('已清理进度轮询定时器')
      }
    },

    // 启动自动刷新
    startAutoRefresh() {
      // 清理可能存在的旧定时器
      if (this.autoRefreshTimer) {
        clearInterval(this.autoRefreshTimer)
        this.autoRefreshTimer = null
      }

      // 设置自动刷新状态
      this.autoRefreshTimer = setInterval(() => {
        this.refreshStatus()
      }, 60 * 1000) // 每60秒刷新一次状态

      console.log('自动刷新定时器已启动')
    },

    // 停止自动刷新
    stopAutoRefresh() {
      if (this.autoRefreshTimer) {
        clearInterval(this.autoRefreshTimer)
        this.autoRefreshTimer = null
        console.log('自动刷新定时器已停止')
      }
    },

    // 处理页面可见性变化
    handleVisibilityChange() {
      if (document.hidden) {
        // 页面不可见时停止自动刷新
        console.log('页面不可见，停止自动刷新')
        this.stopAutoRefresh()
      } else {
        // 页面可见时恢复自动刷新
        console.log('页面可见，恢复自动刷新')
        // this.startAutoRefresh()
        // 立即刷新一次状态
        this.refreshStatus()
      }
    },

    async refreshStatus() {
      if (this.loading) return

      this.loading = true
      try {
        // 根据当前激活的标签页只刷新对应的状态
        if (this.activeTab === 'role') {
          const roleResponse = await systemApi.getMarketDataStatus()
          if (roleResponse.code === 200) {
            this.status = roleResponse.data || {}
          }

          // 如果发现正在刷新但前端没有显示进度，恢复进度弹框
          if (roleResponse.data && roleResponse.data.refresh_status === 'running' && !this.refreshing) {
            this.refreshing = true
            this.showRefreshDialog = true
            this.initializeProgress()

            // 从后端恢复进度信息
            this.refreshProgress = roleResponse.data.refresh_progress || 0
            this.refreshMessage = roleResponse.data.refresh_message || '正在处理...'
            this.refreshedCount = roleResponse.data.refresh_processed_records || 0
            this.currentBatch = roleResponse.data.refresh_current_batch || 0
            this.totalBatches = roleResponse.data.refresh_total_batches || 0

            // 如果有开始时间，使用它
            if (roleResponse.data.refresh_start_time) {
              this.refreshStartTime = new Date(roleResponse.data.refresh_start_time).getTime()
            }

            // 开始轮询进度
            this.startProgressPolling()

            this.$message.info('检测到正在进行的数据刷新任务，已恢复进度显示')
          }
        } else if (this.activeTab === 'equipment') {
          const equipmentResponse = await systemApi.getEquipmentMarketDataStatus()
          if (equipmentResponse.code === 200) {
            this.equipmentMarketDataStatus = equipmentResponse.data || {}
          }
        } else if (this.activeTab === 'pet') {
          const petResponse = await systemApi.getPetMarketDataStatus()
          if (petResponse.code === 200) {
            this.petMarketDataStatus = petResponse.data || {}
          }
        } else if (this.activeTab === 'redis') {
          const redisResponse = await systemApi.getRedisStatus()
          if (redisResponse.code === 200) {
            this.redisStatus = redisResponse.data || {}
          }
        }

      } catch (error) {
        console.error('获取市场数据状态失败:', error)
        this.$message.error('获取状态失败，请检查网络连接')
      } finally {
        this.loading = false
      }
    },

    async refreshMarketData() {
      try {
        this.$confirm('刷新市场数据将优先使用缓存快速更新，如需完全重新加载请使用"刷新全量缓存"，是否继续？', '确认刷新', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(async () => {
          this.refreshing = true
          this.showRefreshDialog = true
          this.initializeProgress()
          // 启动后台刷新
          const response = await systemApi.refreshMarketData()

          if (response.code === 200) {
            this.$message.success('数据刷新已启动，正在后台处理...')

            // 开始轮询进度
            this.startProgressPolling()
          } else {
            this.$message.error(response.message || '启动刷新失败')
            this.refreshing = false
            this.showRefreshDialog = false
          }
        }).catch(() => {
          // 用户取消操作
        })
      } catch (error) {
        console.error('启动刷新失败:', error)
        this.$message.error('启动刷新失败，请检查网络连接')
        this.refreshing = false
        this.showRefreshDialog = false
      }
    },


    formatTime(timeStr) {
      if (!timeStr) return '-'
      try {
        const date = new Date(timeStr)
        return date.toLocaleString('zh-CN')
      } catch (error) {
        return timeStr
      }
    },

    // 进度相关方法
    initializeProgress() {
      this.refreshProgress = 0
      this.refreshMessage = '准备开始...'
      this.refreshedCount = 0
      this.refreshStartTime = Date.now()
      this.currentBatch = 0
      this.totalBatches = 0
    },

    startProgressPolling() {
      // 清理可能存在的旧定时器
      if (this.progressTimer) {
        clearInterval(this.progressTimer)
        this.progressTimer = null
      }

      // 开始轮询后端进度
      this.progressTimer = setInterval(async () => {
        if (this.petCacheRefreshing || this.petLoading) {
          await this.updatePetProgressFromBackend()
        } else if (this.equipmentCacheRefreshing || this.equipmentLoading || this.equipmentIncrementalUpdating) {
          await this.updateEquipmentProgressFromBackend()
        } else {
          await this.updateProgressFromBackend()
        }
      }, 10 * 1000) // 每10秒查询一次进度

      console.log('进度轮询定时器已启动')
    },

    async updateProgressFromBackend() {
      try {
        const response = await systemApi.getMarketDataStatus()
        if (response.code === 200) {
          const data = response.data

          // 更新进度信息
          this.refreshProgress = data.refresh_progress || 0
          this.refreshMessage = data.refresh_message || ''
          this.refreshedCount = data.refresh_processed_records || 0
          this.currentBatch = data.refresh_current_batch || 0
          this.totalBatches = data.refresh_total_batches || 0

          // 检查刷新状态
          if (data.refresh_status === 'completed') {
            this.completeProgress()
            this.$message.success(`数据刷新完成！处理了 ${this.refreshedCount} 条数据`)

            // 延迟关闭对话框
            setTimeout(() => {
              this.showRefreshDialog = false
              this.resetProgress()
            }, 2000)

            // 刷新主状态
            setTimeout(() => {
              this.refreshStatus()
            }, 500)

          } else if (data.refresh_status === 'error') {
            this.refreshMessage = data.refresh_message || '刷新失败'
            this.refreshProgress = 0
            this.$message.error('数据刷新失败')
            this.stopProgressTimer()
            this.refreshing = false
            this.fullCacheRefreshing = false
            this.equipmentCacheRefreshing = false
            this.equipmentLoading = false
            this.petCacheRefreshing = false
            this.petLoading = false
          }
          // 如果是 'running' 状态，继续轮询
        }
      } catch (error) {
        console.error('获取进度失败:', error)
      }
    },

    completeProgress() {
      this.refreshProgress = 100
      this.refreshMessage = '刷新完成！'
      this.stopProgressTimer()
      setTimeout(() => {
        this.refreshing = false
        this.fullCacheRefreshing = false
        this.equipmentCacheRefreshing = false
        this.equipmentLoading = false
        this.equipmentIncrementalUpdating = false
        this.petCacheRefreshing = false
        this.petLoading = false
      }, 2000)
    },

    stopProgressTimer() {
      if (this.progressTimer) {
        clearInterval(this.progressTimer)
        this.progressTimer = null
        console.log('进度轮询定时器已停止')
      }
    },

    resetProgress() {
      this.refreshProgress = 0
      this.refreshMessage = ''
      this.refreshedCount = 0
      this.refreshStartTime = null
      this.currentBatch = 0
      this.totalBatches = 0
    },

    cancelRefresh() {
      // 停止进度轮询
      this.stopProgressTimer()

      // 重置所有刷新状态
      this.refreshing = false
      this.fullCacheRefreshing = false
      this.equipmentCacheRefreshing = false
      this.equipmentLoading = false
      this.equipmentIncrementalUpdating = false
      this.equipmentAutoUpdating = false
      this.petCacheRefreshing = false
      this.petLoading = false

      // 重置进度信息
      this.resetProgress()

      // 关闭对话框
      this.showRefreshDialog = false

      if (this.refreshProgress < 100) {
        this.$message.info('已取消刷新操作')
      }

      console.log('刷新操作已取消，所有定时器已清理')
      // TODO: 可以添加取消后台任务的API调用
    },

    getElapsedTime() {
      if (!this.refreshStartTime) return '0'
      return Math.floor((Date.now() - this.refreshStartTime) / 1000)
    },


    // Redis相关方法
    getHitRate() {
      const hits = this.redisStatusComputed.keyspace_hits || 0
      const misses = this.redisStatusComputed.keyspace_misses || 0
      const total = hits + misses

      if (total === 0) return '0.00'
      return ((hits / total) * 100).toFixed(2)
    },

    formatUptime(seconds) {
      if (!seconds) return '0秒'

      const days = Math.floor(seconds / 86400)
      const hours = Math.floor((seconds % 86400) / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)

      if (days > 0) {
        return `${days}天 ${hours}小时`
      } else if (hours > 0) {
        return `${hours}小时 ${minutes}分钟`
      } else {
        return `${minutes}分钟`
      }
    },

    getCacheTypeLabel(cacheType) {
      const labels = {
        'role_data': '角色数据',
        'equipment_data': '装备数据',
        'search_results': '搜索结果',
        'market_analysis': '市场分析',
        'price_trends': '价格趋势'
      }
      return labels[cacheType] || cacheType
    },

    // 全量缓存相关方法
    async refreshFullCache() {
      if (this.fullCacheRefreshing || this.refreshing) return

      try {
        this.$confirm('刷新全量缓存将跳过所有缓存，直接从MySQL重新加载所有empty角色数据，耗时较长但数据最新，是否继续？', '确认刷新', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(async () => {
          // 使用相同的进度显示机制
          this.refreshing = true
          this.fullCacheRefreshing = true
          this.showRefreshDialog = true
          this.initializeProgress()

          const response = await systemApi.refreshFullCache()
          if (response.code === 200) {
            this.$message.success('全量缓存刷新已启动，正在后台处理...')

            // 开始轮询进度
            this.startProgressPolling()
          } else {
            this.$message.error(response.message || '启动全量缓存刷新失败')
            this.refreshing = false
            this.fullCacheRefreshing = false
            this.showRefreshDialog = false
          }
        }).catch(() => {
          // 用户取消操作
        })
      } catch (error) {
        console.error('启动全量缓存刷新失败:', error)
        this.$message.error('启动全量缓存刷新失败，请检查网络连接')
        this.refreshing = false
        this.fullCacheRefreshing = false
        this.showRefreshDialog = false
      }
    },

    // 装备数据相关方法
    async refreshEquipmentData() {
      if (this.refreshing || this.equipmentCacheRefreshing) return

      try {
        this.$confirm('加载装备数据将优先使用现有缓存，如缓存不存在则自动从数据库加载，是否继续？', '确认加载', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        }).then(async () => {
          // 使用相同的进度显示机制
          this.refreshing = true
          this.equipmentLoading = true
          this.showRefreshDialog = true
          this.initializeProgress()

          const response = await systemApi.refreshEquipmentData()
          if (response.code === 200) {
            this.$message.success('装备数据加载已启动，正在后台处理...')

            // 开始轮询装备刷新进度
            this.startProgressPolling()
          } else {
            this.$message.error(response.message || '启动装备数据加载失败')
            this.refreshing = false
            this.equipmentLoading = false
            this.showRefreshDialog = false
          }
        }).catch(() => {
          // 用户取消操作
        })
      } catch (error) {
        console.error('启动装备数据加载失败:', error)
        this.$message.error('启动装备数据加载失败，请检查网络连接')
        this.refreshing = false
        this.equipmentLoading = false
        this.showRefreshDialog = false
      }
    },
    async refreshEquipmentFullCache() {
      if (this.equipmentCacheRefreshing || this.refreshing) return

      try {
        this.$confirm('刷新装备缓存将从MySQL重新加载全量装备数据到Redis，耗时较长，是否继续？', '确认刷新', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(async () => {
          // 使用相同的进度显示机制
          this.refreshing = true
          this.equipmentCacheRefreshing = true
          this.showRefreshDialog = true
          this.initializeProgress()

          const response = await systemApi.refreshEquipmentFullCache()
          if (response.code === 200) {
            this.$message.success('装备缓存刷新已启动，正在后台处理...')

            // 开始轮询装备刷新进度
            this.startProgressPolling()
          } else {
            this.$message.error(response.message || '启动装备缓存刷新失败')
            this.refreshing = false
            this.equipmentCacheRefreshing = false
            this.showRefreshDialog = false
          }
        }).catch(() => {
          // 用户取消操作
        })
      } catch (error) {
        console.error('启动装备缓存刷新失败:', error)
        this.$message.error('启动装备缓存刷新失败，请检查网络连接')
        this.refreshing = false
        this.equipmentCacheRefreshing = false
        this.showRefreshDialog = false
      }
    },

    // 召唤兽数据相关方法
    async refreshPetData() {
      if (this.refreshing || this.petCacheRefreshing) return

      try {
        this.$confirm('加载召唤兽数据将优先使用现有缓存，如缓存不存在则自动从数据库加载，是否继续？', '确认加载', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        }).then(async () => {
          // 使用相同的进度显示机制
          this.refreshing = true
          this.petLoading = true
          this.showRefreshDialog = true
          this.initializeProgress()

          const response = await systemApi.refreshPetData()
          if (response.code === 200) {
            this.$message.success('召唤兽数据加载已启动，正在后台处理...')

            // 开始轮询召唤兽刷新进度
            this.startProgressPolling()
          } else {
            this.$message.error(response.message || '启动召唤兽数据加载失败')
            this.refreshing = false
            this.petLoading = false
            this.showRefreshDialog = false
          }
        }).catch(() => {
          // 用户取消操作
        })
      } catch (error) {
        console.error('启动召唤兽数据加载失败:', error)
        this.$message.error('启动召唤兽数据加载失败，请检查网络连接')
        this.refreshing = false
        this.petLoading = false
        this.showRefreshDialog = false
      }
    },

    async refreshPetFullCache() {
      if (this.petCacheRefreshing || this.refreshing) return

      try {
        this.$confirm('刷新召唤兽缓存将从MySQL重新加载全量召唤兽数据到Redis，耗时较长，是否继续？', '确认刷新', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(async () => {
          // 使用相同的进度显示机制
          this.refreshing = true
          this.petCacheRefreshing = true
          this.showRefreshDialog = true
          this.initializeProgress()

          const response = await systemApi.refreshPetFullCache()
          if (response.code === 200) {
            this.$message.success('召唤兽缓存刷新已启动，正在后台处理...')

            // 开始轮询召唤兽刷新进度
            this.startProgressPolling()
          } else {
            this.$message.error(response.message || '启动召唤兽缓存刷新失败')
            this.refreshing = false
            this.petCacheRefreshing = false
            this.showRefreshDialog = false
          }
        }).catch(() => {
          // 用户取消操作
        })
      } catch (error) {
        console.error('启动召唤兽缓存刷新失败:', error)
        this.$message.error('启动召唤兽缓存刷新失败，请检查网络连接')
        this.refreshing = false
        this.petCacheRefreshing = false
        this.showRefreshDialog = false
      }
    },

    async updatePetProgressFromBackend() {
      try {
        const response = await systemApi.getPetRefreshStatus()
        if (response.code === 200) {
          const data = response.data

          // 更新进度信息
          this.refreshProgress = data.progress || 0
          this.refreshMessage = data.message || ''
          this.refreshedCount = data.processed_records || 0
          this.currentBatch = data.current_batch || 0
          this.totalBatches = data.total_batches || 0

          // 检查刷新状态
          if (data.status === 'completed') {
            this.completeProgress()
            this.$message.success(`召唤兽缓存刷新完成！处理了 ${this.refreshedCount} 条数据`)

            // 延迟关闭对话框
            setTimeout(() => {
              this.showRefreshDialog = false
              this.resetProgress()
            }, 2000)

            // 刷新召唤兽状态
            setTimeout(() => {
              this.refreshPetStatus()
            }, 500)

          } else if (data.status === 'error') {
            this.refreshMessage = data.message || '召唤兽数据处理失败'
            this.refreshProgress = 0
            this.$message.error('召唤兽数据处理失败')
            this.stopProgressTimer()
            this.refreshing = false
            this.petCacheRefreshing = false
            this.petLoading = false
          }
          // 如果是 'running' 状态，继续轮询
        }
      } catch (error) {
        console.error('获取召唤兽刷新进度失败:', error)
      }
    },

    async refreshPetStatus() {
      try {
        const statusResponse = await systemApi.getPetMarketDataStatus()

        if (statusResponse.code === 200) {
          this.petMarketDataStatus = statusResponse.data || {}
        }
      } catch (error) {
        console.error('获取召唤兽状态失败:', error)
      }
    },

    async updateEquipmentProgressFromBackend() {
      try {
        const response = await systemApi.getEquipmentRefreshStatus()
        if (response.code === 200) {
          const data = response.data

          // 更新进度信息
          this.refreshProgress = data.progress || 0
          this.refreshMessage = data.message || ''
          this.refreshedCount = data.processed_records || 0
          this.currentBatch = data.current_batch || 0
          this.totalBatches = data.total_batches || 0

          // 检查刷新状态
          if (data.status === 'completed') {
            this.completeProgress()
            if (this.equipmentIncrementalUpdating) {
              this.$message.success(`装备增量更新完成！处理了 ${this.refreshedCount} 条数据`)
            } else {
              this.$message.success(`装备缓存刷新完成！处理了 ${this.refreshedCount} 条数据`)
            }

            // 延迟关闭对话框
            setTimeout(() => {
              this.showRefreshDialog = false
              this.resetProgress()
            }, 2000)

            // 刷新装备状态和增量更新状态
            setTimeout(() => {
              this.refreshEquipmentStatus()
              this.refreshEquipmentIncrementalStatus()
            }, 500)

          } else if (data.status === 'error') {
            this.refreshMessage = data.message || '装备数据处理失败'
            this.refreshProgress = 0
            this.$message.error('装备数据处理失败')
            this.stopProgressTimer()
            this.refreshing = false
            this.equipmentCacheRefreshing = false
            this.equipmentLoading = false
            this.equipmentIncrementalUpdating = false
          }
          // 如果是 'running' 状态，继续轮询
        }
      } catch (error) {
        console.error('获取装备刷新进度失败:', error)
      }
    },

    async refreshEquipmentStatus() {
      try {
        const statusResponse = await systemApi.getEquipmentMarketDataStatus()

        if (statusResponse.code === 200) {
          this.equipmentMarketDataStatus = statusResponse.data || {}
        }
      } catch (error) {
        console.error('获取装备状态失败:', error)
      }
    },

    async refreshEquipmentIncrementalStatus() {
      try {
        const statusResponse = await systemApi.getEquipmentIncrementalUpdateStatus()

        if (statusResponse.code === 200) {
          this.equipmentIncrementalStatus = statusResponse.data || {}
        }
      } catch (error) {
        console.error('获取装备增量更新状态失败:', error)
      }
    },

    // 装备增量更新相关方法
    async incrementalUpdateEquipment() {
      if (this.equipmentIncrementalUpdating || this.refreshing) return

      try {
        this.$confirm('增量更新将只更新MySQL中的新数据到Redis缓存，速度较快，是否继续？', '确认增量更新', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        }).then(async () => {
          this.refreshing = true
          this.equipmentIncrementalUpdating = true
          this.showRefreshDialog = true
          this.initializeProgress()

          const response = await systemApi.incrementalUpdateEquipment()
          if (response.code === 200) {
            this.$message.success('装备增量更新已启动，正在后台处理...')
            this.startProgressPolling()
          } else {
            this.$message.error(response.message || '启动装备增量更新失败')
            this.refreshing = false
            this.equipmentIncrementalUpdating = false
            this.showRefreshDialog = false
          }
        }).catch(() => {
          // 用户取消操作
        })
      } catch (error) {
        console.error('启动装备增量更新失败:', error)
        this.$message.error('启动装备增量更新失败，请检查网络连接')
        this.refreshing = false
        this.equipmentIncrementalUpdating = false
        this.showRefreshDialog = false
      }
    },


    getEquipmentTypeName(kindid) {
      const kindidOptions = [...window.AUTO_SEARCH_CONFIG.weapon_armors.map(([value, label]) => ({ value, label })), ...window.lingshiKinds.map(([value, label]) => ({ value, label })), {
        value: 29,
        label: '召唤兽装备'
      }]
      const currnt = kindidOptions.find(item => item.value == kindid)
      return currnt?.label || `类型${kindid}`
    },

    getEquipmentTypeColor(kindid) {
      // 根据装备类型返回不同颜色
      if (window.is_weapon_equip(kindid)) {
        return 'danger' // 武器红色
      } else if (window.is_helmet_equip(kindid)) {
        return 'warning' // 头盔橙色
      } else if (window.is_cloth_equip(kindid)) {
        return 'success' // 衣服绿色
      } else if (window.is_shoes_equip(kindid) || window.is_belt_equip(kindid) || window.is_necklace_equip(kindid)) {
        return 'info' // 鞋子腰带项链蓝色
      } else if (window.is_lingshi_equip(kindid)) {
        return 'primary' // 灵饰紫色
      } else {
        return '' // 默认
      }
    }
  }
}
</script>

<style scoped>
.market-data-status {
  padding: 20px;
}

.market-data-status .page-header {
  margin-bottom: 20px;
}

.market-data-status .page-header h1 {
  margin: 0 0 8px 0;
  color: #303133;
}

.market-data-status .page-header p {
  margin: 0;
  color: #909399;
}

.market-data-status .action-bar {
  margin-bottom: 20px;
}

.market-data-status .action-bar .el-button {
  margin-right: 10px;
}

/* 标签页样式 */
.market-data-status .status-tabs {
  margin-bottom: 20px;
}

.market-data-status .status-tabs .el-tabs__content {
  padding: 0;
}

.market-data-status .tab-content {
  padding: 20px 0;
}

.market-data-status .tab-action-bar {
  margin-bottom: 20px;
}

.market-data-status .tab-action-bar .el-button {
  margin-right: 10px;
}

.market-data-status .status-cards {
  margin-bottom: 20px;
}

.market-data-status .status-card .card-header {
  display: flex;
  align-items: center;
}

.market-data-status .status-card .card-header i {
  margin-right: 8px;
  font-size: 16px;
  color: #409EFF;
}

.market-data-status .status-card .status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.market-data-status .status-card .status-item:last-child {
  margin-bottom: 0;
}

.market-data-status .status-card .status-item .label {
  color: #606266;
  font-size: 14px;
}

.market-data-status .status-card .status-item .value {
  color: #303133;
  font-weight: 500;
}

.market-data-status .status-card .status-item .role-type-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.market-data-status .details-card .card-header {
  display: flex;
  align-items: center;
}

.market-data-status .details-card .card-header i {
  margin-right: 8px;
  font-size: 16px;
  color: #409EFF;
}

.market-data-status .details-card .columns-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.market-data-status .details-card .columns-grid .column-tag {
  margin: 0;
}


/* 图表区域样式 */
.charts-section {
  margin-top: 30px;
}

.charts-section .section-header {
  margin-bottom: 20px;
  text-align: center;
}

.charts-section .section-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 20px;
}

.charts-section .section-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

/* 进度显示样式 */
.refresh-progress {
  padding: 20px;
}

.refresh-progress .progress-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  font-size: 16px;
  color: #303133;
}

.refresh-progress .progress-header i {
  margin-right: 8px;
  color: #409EFF;
}

.refresh-progress .progress-details {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.refresh-progress .progress-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.refresh-progress .progress-item:last-child {
  margin-bottom: 0;
}

.refresh-progress .progress-item .label {
  color: #606266;
  font-size: 14px;
}

.refresh-progress .progress-item .value {
  color: #303133;
  font-weight: 500;
}

/* Redis详细信息样式 */
.redis-basic-status {
  margin-bottom: 20px;
}

.redis-details {
  margin-top: 20px;
}

.cache-type-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 缓存类型组样式 */
.cache-type-group {
  margin-bottom: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  background-color: #fafafa;
}

.cache-type-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.cache-type-summary {
  display: flex;
  align-items: center;
  gap: 8px;
}

.key-details {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e4e7ed;
}

.key-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 8px;
  margin: 2px 0;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.key-name {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #606266;
  flex: 1;
  margin-right: 8px;
  word-break: break-all;
}

.key-ttl {
  flex-shrink: 0;
}

.ttl-tag {
  margin: 0;
}

.no-cache-data {
  text-align: center;
  color: #909399;
  padding: 20px 0;
}

.full-cache-details {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

/* 装备数据状态样式 */
.equipment-status-cards {
  margin-top: 20px;
  margin-bottom: 20px;
}

.equipment-type-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* 召唤兽数据状态样式 */
.pet-status-cards {
  margin-top: 20px;
  margin-bottom: 20px;
}

.pet-skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.level-distribution {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  max-height: 60px;
  overflow-y: auto;
}
</style>
