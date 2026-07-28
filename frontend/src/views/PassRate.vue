<template>
  <div class="pass-rate">
    <div class="page-header">
      <h2>自动化通过率</h2>
      <p class="page-desc">查看自动化测试通过率统计</p>
    </div>

    <div class="filter-row">
      <el-select v-model="filterProject" placeholder="选择项目" style="width: 180px" clearable @change="handleProjectChange">
        <el-option
          v-for="project in projects"
          :key="project.id"
          :label="project.name"
          :value="String(project.id)"
        />
      </el-select>
      <el-select v-model="filterModule" placeholder="选择模块" style="width: 180px" clearable>
        <el-option label="AI智能用例生成" value="m1" />
        <el-option label="用例管理" value="m2" />
        <el-option label="接口自动化" value="m3" />
        <el-option label="UI自动化" value="m4" />
        <el-option label="性能测试" value="m5" />
      </el-select>
      <el-date-picker
        v-model="filterDateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
      />
      <el-button type="primary" @click="handleSearch">查询</el-button>
      <el-button @click="handleReset">重置</el-button>
      <el-button type="success" @click="handleExport">
        <el-icon><component :is="icons.Download" /></el-icon>
        导出Excel
      </el-button>
    </div>

    <div class="stats-row">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background-color: rgba(99, 102, 241, 0.12)">
            <el-icon :size="24" style="color: #6366f1"><component :is="icons.Document" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ totalCases }}</div>
            <div class="stat-title">总用例数</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background-color: rgba(16, 185, 129, 0.12)">
            <el-icon :size="24" style="color: #10b981"><component :is="icons.CircleCheck" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value stat-success">{{ passedCases }}</div>
            <div class="stat-title">通过用例</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background-color: rgba(239, 68, 68, 0.12)">
            <el-icon :size="24" style="color: #ef4444"><component :is="icons.CircleClose" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value stat-danger">{{ failedCases }}</div>
            <div class="stat-title">失败用例</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card highlight-card">
        <div class="stat-content">
          <div class="stat-icon" style="background-color: rgba(139, 92, 246, 0.12)">
            <el-icon :size="24" style="color: #8b5cf6"><component :is="icons.DataLine" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value stat-rate">{{ passRate }}%</div>
            <div class="stat-title">整体通过率</div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="charts-row">
      <el-card class="chart-card">
        <template #header>
          <span class="card-title">整体通过率仪表</span>
        </template>
        <div ref="gaugeChartRef" class="chart-container"></div>
      </el-card>

      <el-card class="chart-card chart-card-wide">
        <template #header>
          <span class="card-title">每日通过率趋势</span>
        </template>
        <div ref="lineChartRef" class="chart-container"></div>
      </el-card>
    </div>

    <el-card class="chart-card-full">
      <template #header>
        <span class="card-title">各模块通过率对比</span>
      </template>
      <div ref="barChartRef" class="chart-container-large"></div>
    </el-card>

    <el-card style="margin-top: 24px">
      <template #header>
        <div class="card-header">
          <span class="card-title">模块通过率明细</span>
          <span class="card-total">共 {{ moduleStats.length }} 个模块</span>
        </div>
      </template>
      <el-table :data="moduleStats" stripe border>
        <el-table-column prop="module" label="模块名称" width="180" />
        <el-table-column prop="total" label="总用例数" width="120" />
        <el-table-column prop="passed" label="通过数" width="100" />
        <el-table-column prop="failed" label="失败数" width="100" />
        <el-table-column prop="blocked" label="阻塞数" width="100" />
        <el-table-column prop="passRate" label="通过率" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.passRate >= 95 ? 'success' : scope.row.passRate >= 85 ? 'warning' : 'danger'" effect="dark">
              {{ scope.row.passRate }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度条">
          <template #default="scope">
            <el-progress
              :percentage="scope.row.passRate"
              :color="scope.row.passRate >= 95 ? '#10b981' : scope.row.passRate >= 85 ? '#f59e0b' : '#ef4444'"
              :stroke-width="10"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import * as XLSX from 'xlsx'
import { ElMessage } from 'element-plus'
import * as icons from '@element-plus/icons-vue'
import { useProjects } from '../composables/useProjects'

const { projects, loadProjects } = useProjects()

const filterProject = ref('')
const filterModule = ref('')
const filterDateRange = ref([])

const totalCases = ref(0)
const passedCases = ref(0)
const failedCases = ref(0)
const loading = ref(false)
const passRate = computed(() =>
  totalCases.value > 0
    ? ((passedCases.value / totalCases.value) * 100).toFixed(1)
    : '0.0'
)

const moduleStats = ref([])

const gaugeChartRef = ref(null)
const lineChartRef = ref(null)
const barChartRef = ref(null)
let gaugeChart = null
let lineChart = null
let barChart = null

const handleProjectChange = () => {
  filterModule.value = ''
  filterDateRange.value = []
}

const loadData = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filterProject.value) params.append('project_id', filterProject.value)
    if (filterModule.value) params.append('module', filterModule.value)
    if (filterDateRange.value && filterDateRange.value.length === 2) {
      params.append('start_date', filterDateRange.value[0].toISOString().slice(0, 10))
      params.append('end_date', filterDateRange.value[1].toISOString().slice(0, 10))
    }

    const queryString = params.toString() ? `?${params.toString()}` : ''

    const [passRateRes, reportsRes] = await Promise.all([
      fetch(`/api/v1/stats/pass_rate${queryString}`),
      fetch(`/api/v1/reports${queryString}`)
    ])

    if (!passRateRes.ok) throw new Error('Failed to load pass rate data')
    const json = await passRateRes.json()
    const data = json.data || json

    totalCases.value = data.total_cases ?? data.totalCases ?? 0
    passedCases.value = data.passed_cases ?? data.passedCases ?? 0
    failedCases.value = data.failed_cases ?? data.failedCases ?? 0
    const rawStats = data.module_stats ?? data.moduleStats ?? []
    moduleStats.value = rawStats.map(m => ({
      module: m.module || m.name || '',
      total: m.total ?? m.total_cases ?? 0,
      passed: m.passed ?? m.passed_cases ?? 0,
      failed: m.failed ?? m.failed_cases ?? 0,
      blocked: m.blocked ?? m.blocked_cases ?? 0,
      passRate: m.passRate ?? m.pass_rate ?? 0
    }))

    updateGaugeChart()
    updateBarChart()

    if (reportsRes.ok) {
      const json = await reportsRes.json()
      const reports = json.data || json
      updateLineChart(reports.reports ?? reports.data ?? [])
    }

    ElMessage.success('数据加载成功')
  } catch (error) {
    console.error('加载通过率数据失败:', error)
    ElMessage.error('加载数据失败，请重试')
  } finally {
    loading.value = false
  }
}

const initGaugeChart = () => {
  if (!gaugeChartRef.value) return
  gaugeChart = echarts.init(gaugeChartRef.value)
  gaugeChart.setOption({
    series: [{
      type: 'gauge',
      startAngle: 200,
      endAngle: -20,
      min: 0,
      max: 100,
      splitNumber: 10,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
          { offset: 0, color: '#8b5cf6' },
          { offset: 1, color: '#6366f1' }
        ]),
        shadowColor: 'rgba(99, 102, 241, 0.3)',
        shadowBlur: 10
      },
      progress: { show: true, width: 20 },
      pointer: { show: true, length: '60%', width: 6, itemStyle: { color: '#6366f1' } },
      axisLine: { lineStyle: { width: 20, color: [[1, '#e5e7eb']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      anchor: { show: true, size: 14, itemStyle: { color: '#fff', borderWidth: 3, borderColor: '#6366f1' } },
      title: { show: false },
      detail: {
        valueAnimation: true,
        fontSize: 32,
        fontWeight: 700,
        color: '#6366f1',
        formatter: '{value}%',
        offsetCenter: [0, '20%']
      },
      data: [{ value: parseFloat(passRate.value) }]
    }]
  })
}

const updateGaugeChart = () => {
  if (!gaugeChart) return
  gaugeChart.setOption({
    series: [{
      data: [{ value: parseFloat(passRate.value) }]
    }]
  })
}

const initLineChart = () => {
  if (!lineChartRef.value) return
  lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const p = params[0]
        return `${p.axisValue}<br/>通过率: <b>${p.value}%</b>`
      }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: [],
      boundaryGap: false,
      axisLabel: { color: '#6b7280' }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: { formatter: '{value}%', color: '#6b7280' }
    },
    series: [{
      name: '通过率',
      type: 'line',
      data: [],
      smooth: true,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(139, 92, 246, 0.4)' },
          { offset: 1, color: 'rgba(139, 92, 246, 0.05)' }
        ])
      },
      lineStyle: { color: '#8b5cf6', width: 3 },
      itemStyle: { color: '#8b5cf6' },
      symbol: 'circle',
      symbolSize: 8,
      markLine: {
        silent: true,
        lineStyle: { color: '#ef4444', type: 'dashed' },
        data: [{ yAxis: 95, label: { formatter: '警戒线 95%', color: '#ef4444' } }]
      }
    }]
  })
}

const updateLineChart = (reports) => {
  if (!lineChart) return
  if (!reports || reports.length === 0) {
    const dates = []
    const now = new Date()
    for (let i = 29; i >= 0; i--) {
      const d = new Date(now)
      d.setDate(d.getDate() - i)
      dates.push(`${d.getMonth() + 1}/${d.getDate()}`)
    }
    lineChart.setOption({
      xAxis: { data: dates },
      series: [{ data: [] }]
    })
    return
  }
  const trendMap = {}
  reports.forEach(r => {
    const dateStr = (r.start_time || r.created_at || r.date || '').slice(0, 10)
    if (!dateStr) return
    if (!trendMap[dateStr]) {
      trendMap[dateStr] = { total: 0, passed: 0 }
    }
    const total = r.total_steps || r.total_cases || 1
    trendMap[dateStr].total += total
    if (r.status === '成功' || r.status === 'passed' || r.all_passed) {
      trendMap[dateStr].passed += total
    }
  })
  const sortedDates = Object.keys(trendMap).sort()
  const dates = []
  const passRates = []
  if (sortedDates.length === 0) {
    const now = new Date()
    for (let i = 29; i >= 0; i--) {
      const d = new Date(now)
      d.setDate(d.getDate() - i)
      dates.push(`${d.getMonth() + 1}/${d.getDate()}`)
      passRates.push(0)
    }
  } else {
    sortedDates.slice(-30).forEach(dateStr => {
      const entry = trendMap[dateStr]
      const rate = entry.total > 0 ? parseFloat((entry.passed / entry.total * 100).toFixed(1)) : 0
      const parts = dateStr.split('-')
      dates.push(`${parseInt(parts[1])}/${parseInt(parts[2])}`)
      passRates.push(rate)
    })
  }
  lineChart.setOption({
    xAxis: { data: dates },
    series: [{ data: passRates }]
  })
}

const initBarChart = () => {
  if (!barChartRef.value) return
  barChart = echarts.init(barChartRef.value)
  barChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>通过率: {c}%' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: [], axisLabel: { color: '#6b7280', interval: 0, rotate: 15 } },
    yAxis: { type: 'value', min: 0, max: 100, axisLabel: { formatter: '{value}%', color: '#6b7280' } },
    series: [{
      name: '通过率',
      type: 'bar',
      data: [],
      barWidth: '45%',
      label: { show: true, position: 'top', formatter: '{c}%', color: '#374151', fontSize: 12, fontWeight: 600 }
    }]
  })
}

const updateBarChart = () => {
  if (!barChart) return
  const modules = moduleStats.value.map(m => m.module || m.name || '')
  const rates = moduleStats.value.map(m => m.passRate ?? m.pass_rate ?? 0)
  const barData = rates.map(v => ({
    value: v,
    itemStyle: {
      color: v >= 95
        ? new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#10b981' }, { offset: 1, color: '#059669' }])
        : v >= 85
          ? new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#f59e0b' }, { offset: 1, color: '#d97706' }])
          : new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#ef4444' }, { offset: 1, color: '#dc2626' }]),
      borderRadius: [6, 6, 0, 0]
    }
  }))
  barChart.setOption({
    xAxis: { data: modules },
    series: [{ data: barData }]
  })
}

const handleResize = () => {
  gaugeChart?.resize()
  lineChart?.resize()
  barChart?.resize()
}

const handleSearch = () => {
  loadData()
}

const handleReset = () => {
  filterProject.value = ''
  filterModule.value = ''
  filterDateRange.value = []
  loadData()
  ElMessage.info('已重置筛选条件')
}

const handleExport = () => {
  if (moduleStats.value.length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }
  const wsData = moduleStats.value.map(item => ({
    '模块名称': item.module || item.name || '',
    '总用例数': item.total ?? item.total_cases ?? 0,
    '通过数': item.passed ?? item.passed_cases ?? 0,
    '失败数': item.failed ?? item.failed_cases ?? 0,
    '阻塞数': item.blocked ?? item.blocked_cases ?? 0,
    '通过率(%)': item.passRate ?? item.pass_rate ?? 0
  }))
  const ws = XLSX.utils.json_to_sheet(wsData)
  ws['!cols'] = [{ wch: 18 }, { wch: 10 }, { wch: 8 }, { wch: 8 }, { wch: 8 }, { wch: 10 }]
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '通过率统计')
  XLSX.writeFile(wb, `通过率统计报表_${new Date().toISOString().slice(0, 10)}.xlsx`)
  ElMessage.success('导出Excel成功')
}

onMounted(async () => {
  await loadProjects()
  nextTick(() => {
    initGaugeChart()
    initLineChart()
    initBarChart()
  })
  loadData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  gaugeChart?.dispose()
  lineChart?.dispose()
  barChart?.dispose()
})
</script>

<style scoped>
.pass-rate {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.page-desc {
  font-size: 14px;
  color: #6b7280;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  transition: box-shadow 0.3s;
}

.stat-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #1f2937;
}

.stat-success {
  color: #10b981;
}

.stat-danger {
  color: #ef4444;
}

.stat-rate {
  color: #8b5cf6;
}

.stat-title {
  font-size: 14px;
  color: #6b7280;
}

.highlight-card {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.05), rgba(99, 102, 241, 0.05));
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 16px;
  margin-bottom: 24px;
}

@media (max-width: 900px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  min-height: 340px;
}

.chart-card-wide {
  min-height: 340px;
}

.chart-card-full {
  min-height: 380px;
}

.chart-container {
  width: 100%;
  height: 280px;
}

.chart-container-large {
  width: 100%;
  height: 320px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-total {
  font-size: 13px;
  color: #6b7280;
}
</style>