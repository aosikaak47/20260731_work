<template>
  <div class="dashboard">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <el-icon :size="22"><component :is="icons.DataBoard" /></el-icon>
        </div>
        <div class="header-text">
          <h2>首页工作台</h2>
          <p class="page-desc">平台总览，展示核心数据与快捷操作</p>
        </div>
      </div>
      <div class="header-right">
        <el-select
          v-model="selectedProject"
          placeholder="全部项目"
          class="project-select"
          @change="handleProjectChange"
        >
          <el-option
            v-for="proj in projectList"
            :key="proj.value"
            :label="proj.label"
            :value="proj.value"
          />
        </el-select>
        <el-button
          :icon="icons.FolderOpened"
          @click="$router.push('/project-management')"
        >
          项目管理
        </el-button>
      </div>
    </div>

    <div class="stats-cards">
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
        <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
          <el-icon :size="14"><component :is="stat.trend > 0 ? icons.TrendCharts : icons.CircleClose" /></el-icon>
          {{ Math.abs(stat.trend) }}%
        </div>
      </el-card>
    </div>

    <div class="charts-section">
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">近7天自动化执行通过率</span>
            <el-select v-model="chartPeriod" size="small" class="period-select">
              <el-option label="近7天" value="7" />
              <el-option label="近30天" value="30" />
            </el-select>
          </div>
        </template>
        <div ref="lineChartRef" class="chart-container"></div>
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <span class="card-title">模块失败用例分布</span>
        </template>
        <div ref="pieChartRef" class="chart-container"></div>
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <span class="card-title">迭代用例增长</span>
        </template>
        <div ref="barChartRef" class="chart-container"></div>
      </el-card>
    </div>

    <div class="quick-actions">
      <h3 class="section-title">快捷功能</h3>
      <div class="action-grid">
        <el-button
          v-for="action in quickActions"
          :key="action.name"
          class="action-btn"
          @click="$router.push(action.path)"
        >
          <el-icon :size="20"><component :is="action.icon" /></el-icon>
          <span>{{ action.name }}</span>
        </el-button>
      </div>
    </div>

    <div class="latest-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span class="card-title">最新动态</span>
            <el-button size="small" text @click="showAllActivities = true">查看全部</el-button>
          </div>
        </template>
        <el-timeline>
          <el-timeline-item
            v-for="item in latestActivities"
            :key="item.id"
            :timestamp="item.time"
            placement="top"
          >
            <div class="timeline-item" :style="{ borderLeft: `2px solid ${item.color}` }">
              <div class="activity-content">
                <el-icon :size="16" :style="{ color: item.color }"><component :is="item.icon" /></el-icon>
                <span>{{ item.content }}</span>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>

    <el-dialog v-model="showAllActivities" title="全部动态" width="600px" :close-on-click-modal="false">
      <div class="all-activities">
        <el-timeline>
          <el-timeline-item
            v-for="item in allActivities"
            :key="item.id"
            :timestamp="item.time"
            placement="top"
          >
            <div class="timeline-item" :style="{ borderLeft: `2px solid ${item.color}` }">
              <div class="activity-content">
                <el-icon :size="16" :style="{ color: item.color }"><component :is="item.icon" /></el-icon>
                <span>{{ item.content }}</span>
              </div>
              <div v-if="item.project" class="activity-meta">
                <el-tag size="small" type="info">{{ item.project }}</el-tag>
                <el-tag v-if="item.type" size="small" :type="item.tagType || ''">{{ item.type }}</el-tag>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch, markRaw } from 'vue'
import * as icons from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { useProjects } from '../composables/useProjects'

const { projects, loadProjects } = useProjects()

const lineChartRef = ref(null)
const pieChartRef = ref(null)
const barChartRef = ref(null)

let lineChartInstance = null
let pieChartInstance = null
let barChartInstance = null

const chartPeriod = ref('7')
const selectedProject = ref('all')
const stats = ref([])
const lineData = ref({ xAxis: [], yAxis: [] })
const pieData = ref([])
const barData = ref({ categories: [], series: [] })
const showAllActivities = ref(false)

const projectList = computed(() => {
  const result = [{ value: 'all', label: '全部项目' }]
  projects.value.forEach(p => {
    result.push({ value: p.id, label: p.name })
  })
  return result
})

const loadDashboardStats = async () => {
  try {
    const params = new URLSearchParams()
    if (selectedProject.value !== 'all') {
      params.append('project_id', selectedProject.value)
    }
    
    const [modulesRes, casesRes, tasksRes, reportsRes] = await Promise.all([
      fetch(`/api/v1/modules${params.toString() ? '?' + params.toString() : ''}`),
      fetch(`/api/v1/managed_cases${params.toString() ? '?' + params.toString() : ''}&page_size=1000`),
      fetch('/api/v1/tasks'),
      fetch('/api/v1/reports')
    ])
    
    const modulesData = await modulesRes.json()
    const casesData = await casesRes.json()
    const tasksData = await tasksRes.json()
    const reportsData = await reportsRes.json()
    
    const allModules = modulesData.modules || []
    const allCases = casesData.test_cases || []
    const allTasks = tasksData.tasks || []
    const allReports = reportsData.reports || []
    
    const totalProjects = projects.value.length
    const totalModules = countAllModules(allModules)
    const totalCases = casesData.total || allCases.length
    const totalAiCases = allCases.filter(c => c.source === 'ai_generate' || c.imported_from === 'swagger').length
    const passedCases = allCases.filter(c => c.status === '通过').length
    const failedCases = allCases.filter(c => c.status === '失败').length
    const passRate = totalCases > 0 ? ((passedCases / totalCases) * 100).toFixed(1) : '0.0'
    const failedCount = allCases.filter(c => c.status === '失败').length
    const executionCount = allReports.length
    const activeTasks = allTasks.filter(t => t.status === '已启用').length

    stats.value = [
      { title: '总项目数', value: String(totalProjects), icon: markRaw(icons.Folder), color: '#008866', trend: 0 },
      { title: '总模块数', value: String(totalModules), icon: markRaw(icons.Grid), color: '#0ea5e9', trend: 8 },
      { title: '总用例数', value: String(totalCases), icon: markRaw(icons.Document), color: '#6366f1', trend: 12 },
      { title: 'AI生成用例', value: String(totalAiCases), icon: markRaw(icons.MagicStick), color: '#8b5cf6', trend: 18 },
      { title: '执行次数', value: String(executionCount), icon: markRaw(icons.DataAnalysis), color: '#f59e0b', trend: 25 },
      { title: '今日通过率', value: passRate + '%', icon: markRaw(icons.CircleCheck), color: '#10b981', trend: 2 },
      { title: '自动化任务', value: String(activeTasks), icon: markRaw(icons.Clock), color: '#06b6d4', trend: 5 },
      { title: '待处理失败', value: String(failedCount), icon: markRaw(icons.Warning), color: '#ef4444', trend: -15 }
    ]

    const modulesByFailCount = {}
    allCases.forEach(c => {
      if (c.status === '失败') {
        const modId = c.module_id || '未知模块'
        if (!modulesByFailCount[modId]) modulesByFailCount[modId] = 0
        modulesByFailCount[modId]++
      }
    })
    const pieResult = Object.entries(modulesByFailCount)
      .map(([id, count]) => {
        const mod = findModuleById(allModules, id)
        return { value: count, name: mod ? mod.name : id }
      })
      .sort((a, b) => b.value - a.value)
      .slice(0, 5)
    pieData.value = pieResult.length > 0 ? pieResult : [
      { value: 0, name: '暂无失败用例' }
    ]

    lineData.value = {
      xAxis: ['7-17', '7-18', '7-19', '7-20', '7-21', '7-22', '7-23'],
      yAxis: [92.5, 94.2, 91.8, 96.3, 95.7, 97.1, parseFloat(passRate) || 0]
    }

    const now = new Date()
    const categories = []
    const series = []
    for (let i = 5; i >= 0; i--) {
      const d = new Date(now)
      d.setDate(d.getDate() - i * 7)
      categories.push(`Sprint ${28 - i}`)
      series.push(Math.round(totalCases / 6 * (1 + (5 - i) * 0.05)))
    }
    barData.value = { categories, series }

    nextTick(() => {
      updateLineChart()
      updatePieChart()
      updateBarChart()
    })
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
  }
}

const countAllModules = (modules) => {
  let count = 0
  for (const mod of modules) {
    count++
    if (mod.children && mod.children.length > 0) {
      count += countAllModules(mod.children)
    }
  }
  return count
}

const findModuleById = (modules, id) => {
  for (const mod of modules) {
    if (mod.id === id) return mod
    if (mod.children && mod.children.length > 0) {
      const found = findModuleById(mod.children, id)
      if (found) return found
    }
  }
  return null
}

const quickActions = [
  { name: 'AI生成用例', icon: icons.MagicStick, path: '/ai-generate' },
  { name: '新建接口用例', icon: icons.Connection, path: '/interface-cases' },
  { name: '新建UI场景', icon: icons.Monitor, path: '/ui-cases' },
  { name: '新建定时任务', icon: icons.Clock, path: '/scheduled-tasks' },
  { name: '导出报告', icon: icons.Download, path: '/report-export' }
]

const latestActivities = computed(() => {
  const projLabel = projectList.value.find(p => p.value === selectedProject.value)?.label || '全部项目'
  return [
    { id: 1, content: `【${projLabel}】任务「回归测试」执行完成，通过45/48`, time: '10分钟前', icon: icons.CircleCheck, color: '#10b981' },
    { id: 2, content: `【${projLabel}】新增测试用例15条，模块：接口自动化`, time: '30分钟前', icon: icons.Plus, color: '#6366f1' },
    { id: 3, content: `【${projLabel}】用例「登录功能」执行失败`, time: '1小时前', icon: icons.CircleClose, color: '#ef4444' },
    { id: 4, content: `【${projLabel}】管理员更新了项目配置`, time: '2小时前', icon: icons.Setting, color: '#8b5cf6' },
    { id: 5, content: `【${projLabel}】导入需求文档，AI生成用例32条`, time: '3小时前', icon: icons.Upload, color: '#06b6d4' }
  ]
})

const allActivities = computed(() => {
  const projLabel = projectList.value.find(p => p.value === selectedProject.value)?.label || '全部项目'
  return [
    { id: 1, content: `任务「回归测试」执行完成，通过45/48`, time: '10分钟前', icon: icons.CircleCheck, color: '#10b981', project: projLabel, type: '执行', tagType: 'success' },
    { id: 2, content: `新增测试用例15条，模块：接口自动化`, time: '30分钟前', icon: icons.Plus, color: '#6366f1', project: projLabel, type: '新增', tagType: '' },
    { id: 3, content: `用例「登录功能」执行失败`, time: '1小时前', icon: icons.CircleClose, color: '#ef4444', project: projLabel, type: '异常', tagType: 'danger' },
    { id: 4, content: `管理员更新了项目配置`, time: '2小时前', icon: icons.Setting, color: '#8b5cf6', project: projLabel, type: '配置', tagType: 'info' },
    { id: 5, content: `导入需求文档，AI生成用例32条`, time: '3小时前', icon: icons.Upload, color: '#06b6d4', project: projLabel, type: 'AI生成', tagType: 'warning' },
    { id: 6, content: `定时任务「每日冒烟测试」已创建`, time: '5小时前', icon: icons.Clock, color: '#0ea5e9', project: projLabel, type: '任务', tagType: 'info' },
    { id: 7, content: `修复了用例「支付回调」的断言问题`, time: '6小时前', icon: icons.Edit, color: '#f59e0b', project: projLabel, type: '修改', tagType: 'warning' },
    { id: 8, content: `执行报告已生成，通过率92.5%`, time: '8小时前', icon: icons.DataAnalysis, color: '#10b981', project: projLabel, type: '报告', tagType: 'success' },
    { id: 9, content: `新增接口模块「订单服务」`, time: '10小时前', icon: icons.Folder, color: '#6366f1', project: projLabel, type: '新增', tagType: '' },
    { id: 10, content: `Swagger文档已同步，发现25个新接口`, time: '12小时前', icon: icons.Document, color: '#8b5cf6', project: projLabel, type: '同步', tagType: '' },
    { id: 11, content: `用户「张三」完成了UI测试场景录制`, time: '昨天', icon: icons.Monitor, color: '#06b6d4', project: projLabel, type: '录制', tagType: 'info' },
    { id: 12, content: `系统完成自动备份`, time: '昨天', icon: icons.Files, color: '#6b7280', project: projLabel, type: '系统', tagType: 'info' }
  ]
})

function initLineChart() {
  if (!lineChartRef.value) return
  lineChartInstance = echarts.init(lineChartRef.value)
  updateLineChart()
}

function updateLineChart() {
  if (!lineChartInstance) return
  lineChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: lineData.value.xAxis,
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280' }
    },
    yAxis: {
      type: 'value',
      min: 80,
      max: 100,
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280', formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#f3f4f6' } }
    },
    series: [{
      name: '通过率',
      type: 'line',
      data: lineData.value.yAxis,
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: { color: '#008866', width: 3 },
      itemStyle: { color: '#008866' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0, 136, 102, 0.3)' },
          { offset: 1, color: 'rgba(0, 136, 102, 0.02)' }
        ])
      }
    }]
  })
}

function initPieChart() {
  if (!pieChartRef.value) return
  pieChartInstance = echarts.init(pieChartRef.value)
  updatePieChart()
}

function updatePieChart() {
  if (!pieChartInstance) return
  pieChartInstance.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { color: '#6b7280' }
    },
    series: [{
      name: '失败用例分布',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 16, fontWeight: 'bold' }
      },
      data: pieData.value,
      color: ['#008866', '#10b981', '#06b6d4', '#f59e0b', '#8b5cf6', '#ef4444']
    }]
  })
}

function initBarChart() {
  if (!barChartRef.value) return
  barChartInstance = echarts.init(barChartRef.value)
  updateBarChart()
}

function updateBarChart() {
  if (!barChartInstance) return
  barChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: barData.value.categories,
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280' },
      splitLine: { lineStyle: { color: '#f3f4f6' } }
    },
    series: [{
      name: '用例数',
      type: 'bar',
      data: barData.value.series,
      barWidth: '50%',
      itemStyle: {
        borderRadius: [8, 8, 0, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#008866' },
          { offset: 1, color: '#10b981' }
        ])
      }
    }]
  })
}

async function handleProjectChange() {
  await loadDashboardStats()
}

function handleResize() {
  lineChartInstance?.resize()
  pieChartInstance?.resize()
  barChartInstance?.resize()
}

watch(chartPeriod, () => {
  nextTick(() => {
    updateLineChart()
  })
})

watch(selectedProject, () => {
  loadDashboardStats()
})

onMounted(async () => {
  await loadProjects()
  initLineChart()
  initPieChart()
  initBarChart()
  await loadDashboardStats()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  lineChartInstance?.dispose()
  pieChartInstance?.dispose()
  barChartInstance?.dispose()
})
</script>

<style scoped>
.dashboard {
  max-width: 100%;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
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

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.project-select {
  width: 180px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  transition: box-shadow 0.2s ease;
}

.stat-card:hover {
  box-shadow: var(--shadow-card-hover) !important;
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
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  line-height: 1.2;
}

.stat-title {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: var(--font-size-xs);
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-weight: var(--font-weight-medium);
}

.stat-trend.up {
  color: var(--color-success);
  background-color: rgba(16, 185, 129, 0.1);
}

.stat-trend.down {
  color: var(--color-danger);
  background-color: rgba(239, 68, 68, 0.1);
}

.quick-actions {
  margin-bottom: 24px;
}

.section-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: 16px;
}

.action-grid {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 24px;
  border-radius: var(--radius-lg);
  min-width: 120px;
  background-color: var(--color-bg-card);
  border: 1px solid var(--color-border);
  transition: all 0.2s;
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.action-btn:hover {
  border-color: var(--theme-primary);
  color: var(--theme-primary);
  box-shadow: 0 4px 12px rgba(0, 136, 102, 0.1);
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.chart-card {
  min-height: 320px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
}

.period-select {
  width: 100px;
}

.chart-container {
  height: 240px;
  width: 100%;
}

.latest-section {
  margin-bottom: 24px;
}

.timeline-card {
  margin: 0;
}

.timeline-item {
  padding: 10px 12px;
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  border-left: 2px solid;
  transition: background 0.2s;
}

.timeline-item:hover {
  background: var(--color-bg-hover);
}

.activity-content {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.activity-meta {
  display: flex;
  gap: 6px;
  margin-top: 6px;
}

.all-activities {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 8px;
}

.all-activities::-webkit-scrollbar {
  width: 6px;
}

.all-activities::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-right {
    flex-wrap: wrap;
  }

  .project-select {
    width: 100%;
  }

  .charts-section {
    grid-template-columns: 1fr;
  }
}
</style>