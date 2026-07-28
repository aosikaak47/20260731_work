<template>
  <div class="coverage-container">
    <el-card>
      <template #header>
        <h2>覆盖率统计</h2>
      </template>
      
      <div v-if="!coverage" class="empty-state">
        <el-icon size="64" color="#c0c4cc"><component :is="icons.PieChart" /></el-icon>
        <p>暂无覆盖率数据</p>
        <el-button type="primary" @click="goToUpload">去生成测试用例</el-button>
      </div>
      
      <div v-else class="coverage-content">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="stat-card">
              <div class="stat-icon">
                <el-icon size="32" color="#667eea"><component :is="icons.Document" /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ coverage.total_cases }}</div>
                <div class="stat-label">测试用例总数</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card class="stat-card">
              <div class="stat-icon">
                <el-icon size="32" color="#52c41a"><component :is="icons.CircleCheck" /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ coverage.coverage_rate }}%</div>
                <div class="stat-label">覆盖率</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card class="stat-card">
              <div class="stat-icon">
                <el-icon size="32" color="#faad14"><component :is="icons.Alert" /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ coverage.uncovered_items.length }}</div>
                <div class="stat-label">未覆盖项</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <el-card>
              <template #header>按类型分布</template>
              <div ref="typeChart" class="chart-container"></div>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card>
              <template #header>按优先级分布</template>
              <div ref="priorityChart" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-card style="margin-top: 20px;">
          <template #header>覆盖率详情</template>
          <el-table :data="coverageData" border>
            <el-table-column prop="name" label="指标" />
            <el-table-column prop="value" label="数量" />
            <el-table-column prop="percentage" label="占比" />
          </el-table>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as icons from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()
const coverage = ref(null)
const typeChart = ref(null)
const priorityChart = ref(null)

onMounted(() => {
  const savedCoverage = localStorage.getItem('coverage')
  if (savedCoverage) {
    coverage.value = JSON.parse(savedCoverage)
    nextTick(() => {
      initCharts()
    })
  }
})

const coverageData = computed(() => {
  if (!coverage.value) return []
  const data = []
  const byType = coverage.value.by_type || {}
  
  Object.keys(byType).forEach(key => {
    data.push({
      name: key,
      value: byType[key],
      percentage: coverage.value.total_cases > 0 
        ? ((byType[key] / coverage.value.total_cases) * 100).toFixed(1) + '%' 
        : '0%'
    })
  })
  
  return data
})

const initCharts = () => {
  if (!coverage.value) return
  
  const typeChartInstance = echarts.init(typeChart.value)
  const priorityChartInstance = echarts.init(priorityChart.value)
  
  const typeData = Object.keys(coverage.value.by_type || {}).map(key => ({
    name: key,
    value: coverage.value.by_type[key]
  }))
  
  const priorityData = Object.keys(coverage.value.by_priority || {}).map(key => ({
    name: key,
    value: coverage.value.by_priority[key]
  }))
  
  typeChartInstance.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 18,
          fontWeight: 'bold'
        }
      },
      data: typeData
    }]
  })
  
  priorityChartInstance.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 18,
          fontWeight: 'bold'
        }
      },
      data: priorityData
    }]
  })
  
  window.addEventListener('resize', () => {
    typeChartInstance.resize()
    priorityChartInstance.resize()
  })
}

const goToUpload = () => {
  router.push('/')
}
</script>

<style scoped>
.coverage-container {
  max-width: 1200px;
  margin: 0 auto;
}

.empty-state {
  text-align: center;
  padding: 60px 0;
}

.empty-state p {
  color: #909399;
  margin-top: 10px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.chart-container {
  height: 300px;
}
</style>