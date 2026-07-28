<template>
  <div class="quality-stats">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <el-icon :size="22"><component :is="icons.TrendCharts" /></el-icon>
        </div>
        <div class="header-text">
          <h2>质量统计大盘</h2>
          <p class="page-desc">多维度数据分析与可视化</p>
        </div>
      </div>
    </div>

    <div class="filter-row">
      <el-select v-model="filterProject" placeholder="选择项目" style="width: 200px" clearable>
        <el-option
          v-for="proj in projects"
          :key="proj.id"
          :label="proj.name"
          :value="String(proj.id)"
        />
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
      <el-card class="stat-card" v-for="stat in stats" :key="stat.title">
        <div class="stat-content">
          <div class="stat-icon" :style="{ backgroundColor: stat.color + '20' }">
            <el-icon :size="24" :style="{ color: stat.color }"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-title">{{ stat.title }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="charts-row">
      <el-card class="chart-card">
        <template #header>
          <span class="card-title">迭代通过率趋势（近30天）</span>
        </template>
        <div ref="lineChartRef" class="chart-container"></div>
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <span class="card-title">模块质量排行</span>
        </template>
        <div ref="barChartRef" class="chart-container"></div>
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <span class="card-title">失败类型占比</span>
        </template>
        <div ref="pieChartRef" class="chart-container"></div>
      </el-card>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">数据明细</span>
          <span class="card-total">共 {{ filteredDetails.length }} 条记录</span>
        </div>
      </template>

      <el-table :data="pagedDetails" stripe border>
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="module" label="模块" width="160" />
        <el-table-column prop="total" label="总用例数" width="110" />
        <el-table-column prop="passed" label="通过数" width="100" />
        <el-table-column prop="failed" label="失败数" width="100" />
        <el-table-column prop="passRate" label="通过率" width="110">
          <template #default="scope">
            <el-tag size="small" :type="scope.row.passRate >= 90 ? 'success' : scope.row.passRate >= 70 ? 'warning' : 'danger'">
              {{ scope.row.passRate }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="执行耗时" width="110" />
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag size="small" :type="scope.row.status === '已完成' ? 'success' : 'info'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pagination"
        layout="total, prev, pager, next"
        :total="filteredDetails.length"
        :page-size="pageSize"
        v-model:current-page="currentPage"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, markRaw } from 'vue'
import * as echarts from 'echarts'
import * as XLSX from 'xlsx'
import { ElMessage } from 'element-plus'
import * as icons from '@element-plus/icons-vue'
import { useProjects } from '../composables/useProjects'

const { projects, loadProjects } = useProjects()

const filterProject = ref('')
const filterDateRange = ref([])
const currentPage = ref(1)
const pageSize = 10
const loading = ref(false)

const stats = ref([
  { title: '总用例数', value: '0', icon: markRaw(icons.Document), color: '#6366f1' },
  { title: '自动化用例', value: '0', icon: markRaw(icons.Cpu), color: '#8b5cf6' },
  { title: '总执行次数', value: '0', icon: markRaw(icons.Clock), color: '#06b6d4' },
  { title: '平均通过率', value: '0%', icon: markRaw(icons.CircleCheck), color: '#10b981' },
  { title: '失败用例', value: '0', icon: markRaw(icons.CircleClose), color: '#f59e0b' }
])

const details = ref([])

const filteredDetails = computed(() => {
  if (!filterDateRange.value || filterDateRange.value.length === 0) {
    return details.value
  }
  const [start, end] = filterDateRange.value
  return details.value.filter(item => {
    const d = new Date(item.date)
    return d >= start && d <= end
  })
})

const pagedDetails = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredDetails.value.slice(start, start + pageSize)
})

const lineChartRef = ref(null)
const barChartRef = ref(null)
const pieChartRef = ref(null)
let lineChart = null
let barChart = null
let pieChart = null

const buildParams = () => {
  const params = new URLSearchParams()
  if (filterProject.value) {
    params.append('project_id', filterProject.value)
  }
  if (filterDateRange.value && filterDateRange.value.length === 2) {
    const [start, end] = filterDateRange.value
    params.append('start_date', start.toISOString().slice(0, 10))
    params.append('end_date', end.toISOString().slice(0, 10))
  }
  return params.toString() ? '?' + params.toString() : ''
}

const loadStats = async () => {
  loading.value = true
  try {
    const url = `/api/v1/stats/quality${buildParams()}`
    const res = await fetch(url)
    if (!res.ok) throw new Error('请求失败')
    const json = await res.json()
    const data = json.data || json

    stats.value = [
      { title: '总用例数', value: (data.total_cases || 0).toLocaleString(), icon: markRaw(icons.Document), color: '#6366f1' },
      { title: '自动化用例', value: (data.automated_cases || 0).toLocaleString(), icon: markRaw(icons.Cpu), color: '#8b5cf6' },
      { title: '总执行次数', value: (data.total_executions || 0).toLocaleString(), icon: markRaw(icons.Clock), color: '#06b6d4' },
      { title: '平均通过率', value: (data.pass_rate || 0).toFixed(1) + '%', icon: markRaw(icons.CircleCheck), color: '#10b981' },
      { title: '失败用例', value: ((data.total_executions || 0) - (data.passed_executions || 0)).toLocaleString(), icon: markRaw(icons.CircleClose), color: '#f59e0b' }
    ]

    const moduleStats = data.module_stats || []
    generateDetailsFromModules(moduleStats)

    nextTick(() => {
      updateBarChart(moduleStats)
      updatePieChart(data.failure_distribution || [])
    })
  } catch (error) {
    console.error('加载质量统计数据失败:', error)
    ElMessage.error('加载统计数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const generateDetailsFromModules = (moduleStats) => {
  if (!moduleStats || moduleStats.length === 0) {
    details.value = []
    return
  }
  const now = new Date()
  const result = []
  for (let i = 0; i < 7; i++) {
    const d = new Date(now)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().slice(0, 10)
    moduleStats.forEach(mod => {
      const total = mod.total_cases || 0
      const passRate = mod.pass_rate || 0
      const passed = Math.round(total * passRate / 100)
      const failed = total - passed
      const duration = Math.floor(10 + Math.random() * 50)
      result.push({
        date: dateStr,
        module: mod.module || mod.module_name || mod.name || '未知模块',
        total: total,
        passed: passed,
        failed: failed,
        passRate: parseFloat(passRate.toFixed(1)),
        duration: duration + 'm',
        status: '已完成'
      })
    })
  }
  result.sort((a, b) => new Date(b.date) - new Date(a.date))
  details.value = result
}

const loadReports = async () => {
  try {
    const url = `/api/v1/reports${buildParams()}`
    const res = await fetch(url)
    if (!res.ok) throw new Error('请求失败')
    const json = await res.json()
    const data = json.data || json
    const reports = data.reports || data.items || data.list || json.reports || json.items || json.list || []

    const trendMap = {}
    reports.forEach(r => {
      const dateStr = (r.start_time || r.created_at || r.date || '').slice(0, 10)
      if (!dateStr) return
      if (!trendMap[dateStr]) {
        trendMap[dateStr] = { total: 0, passed: 0 }
      }
      const total = r.total_steps || r.total_cases || r.total || 0
      trendMap[dateStr].total += total
      if (r.status === '成功' || r.status === 'passed' || r.all_passed) {
        trendMap[dateStr].passed += total
      }
    })

    const dates = []
    const passRates = []
    const sortedDates = Object.keys(trendMap).sort()
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

    nextTick(() => {
      updateLineChart(dates, passRates)
    })
  } catch (error) {
    console.error('加载报告数据失败:', error)
    const dates = []
    const passRates = []
    const now = new Date()
    for (let i = 29; i >= 0; i--) {
      const d = new Date(now)
      d.setDate(d.getDate() - i)
      dates.push(`${d.getMonth() + 1}/${d.getDate()}`)
      passRates.push(0)
    }
    nextTick(() => {
      updateLineChart(dates, passRates)
    })
  }
}

const initLineChart = () => {
  if (!lineChartRef.value) return
  lineChart = echarts.init(lineChartRef.value)
  updateLineChart([], [])
}

const updateLineChart = (dates, passRates) => {
  if (!lineChart) {
    if (!lineChartRef.value) return
    lineChart = echarts.init(lineChartRef.value)
  }
  const hasData = dates && dates.length > 0 && passRates.some(r => r > 0)
  lineChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}<br/>通过率: {c}%' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: dates, boundaryGap: false, axisLabel: { color: '#6b7280' } },
    yAxis: { type: 'value', min: 0, max: 100, axisLabel: { formatter: '{value}%', color: '#6b7280' } },
    series: [{
      name: '通过率',
      type: 'line',
      data: passRates,
      smooth: true,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(99, 102, 241, 0.4)' },
          { offset: 1, color: 'rgba(99, 102, 241, 0.05)' }
        ])
      },
      lineStyle: { color: '#6366f1', width: 2 },
      itemStyle: { color: '#6366f1' },
      symbol: 'circle',
      symbolSize: 6,
      markLine: hasData ? undefined : {
        data: [{ yAxis: 0, label: { formatter: '暂无数据', color: '#9ca3af' } }],
        lineStyle: { color: 'transparent' }
      }
    }]
  })
}

const initBarChart = () => {
  if (!barChartRef.value) return
  barChart = echarts.init(barChartRef.value)
  updateBarChart([])
}

const updateBarChart = (moduleStats) => {
  if (!barChart) {
    if (!barChartRef.value) return
    barChart = echarts.init(barChartRef.value)
  }
  let categories = []
  let data = []
  if (moduleStats && moduleStats.length > 0) {
    const sorted = [...moduleStats].sort((a, b) => (b.pass_rate || 0) - (a.pass_rate || 0))
    categories = sorted.map(m => m.module || m.module_name || m.name || '未知')
    data = sorted.map(m => parseFloat((m.pass_rate || 0).toFixed(1)))
  }
  barChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}<br/>通过率: {c}%' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: categories, axisLabel: { color: '#6b7280' } },
    yAxis: { type: 'value', axisLabel: { formatter: '{value}%', color: '#6b7280' } },
    series: [{
      name: '通过率',
      type: 'bar',
      data: data,
      barWidth: '50%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#8b5cf6' },
          { offset: 1, color: '#6366f1' }
        ]),
        borderRadius: [4, 4, 0, 0]
      },
      label: { show: true, position: 'top', formatter: '{c}%', color: '#6b7280', fontSize: 11 }
    }]
  })
}

const initPieChart = () => {
  if (!pieChartRef.value) return
  pieChart = echarts.init(pieChartRef.value)
  updatePieChart([])
}

const updatePieChart = (failureDistribution) => {
  if (!pieChart) {
    if (!pieChartRef.value) return
    pieChart = echarts.init(pieChartRef.value)
  }
  let data = []
  if (failureDistribution && failureDistribution.length > 0) {
    data = failureDistribution.map(item => ({
      value: item.count || item.value || 0,
      name: item.type || item.name || '未知'
    }))
  }
  if (data.length === 0) {
    data = [{ value: 0, name: '暂无失败数据', itemStyle: { color: '#d1d5db' } }]
  }
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', right: '5%', top: 'center', textStyle: { color: '#6b7280' } },
    series: [{
      name: '失败类型',
      type: 'pie',
      radius: ['45%', '70%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      data: data.length > 0 && data[0].value === 0
        ? data
        : data.map((item, idx) => ({
            ...item,
            itemStyle: { color: ['#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#6b7280', '#06b6d4', '#10b981'][idx % 7] }
          }))
    }]
  })
}

const handleResize = () => {
  lineChart?.resize()
  barChart?.resize()
  pieChart?.resize()
}

const handleSearch = async () => {
  currentPage.value = 1
  await loadStats()
  await loadReports()
  ElMessage.success('查询成功')
}

const handleReset = async () => {
  filterProject.value = ''
  filterDateRange.value = []
  currentPage.value = 1
  await loadStats()
  await loadReports()
  ElMessage.info('已重置筛选条件')
}

const handleExport = () => {
  const wsData = filteredDetails.value.map(item => ({
    '日期': item.date,
    '模块': item.module,
    '总用例数': item.total,
    '通过数': item.passed,
    '失败数': item.failed,
    '通过率(%)': item.passRate,
    '执行耗时': item.duration,
    '状态': item.status
  }))
  const ws = XLSX.utils.json_to_sheet(wsData)
  ws['!cols'] = [{ wch: 12 }, { wch: 18 }, { wch: 10 }, { wch: 8 }, { wch: 8 }, { wch: 10 }, { wch: 10 }, { wch: 10 }]
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '质量统计')
  XLSX.writeFile(wb, `质量统计报表_${new Date().toISOString().slice(0, 10)}.xlsx`)
  ElMessage.success('导出Excel成功')
}

onMounted(async () => {
  await loadProjects()
  nextTick(() => {
    initLineChart()
    initBarChart()
    initPieChart()
  })
  window.addEventListener('resize', handleResize)
  await loadStats()
  await loadReports()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  lineChart?.dispose()
  barChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.quality-stats {
}

.page-header {
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-primary-dark) 100%);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.header-text h2 {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
  line-height: 1.4;
}

.page-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
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
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  border-radius: var(--radius-lg);
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
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.stat-title {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.chart-card {
  min-height: 340px;
}

.chart-container {
  width: 100%;
  height: 280px;
}

.card-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-total {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--spacing-4);
}
</style>