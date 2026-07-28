<template>
  <div class="perf-monitor">
    <div class="page-header">
      <div class="header-left">
        <h2>实时监控</h2>
        <p class="page-desc">实时监控性能测试运行状态</p>
      </div>
      <div class="header-right">
        <el-icon :size="18" class="header-icon"><DataLine /></el-icon>
        <span class="filter-label">选择测试：</span>
        <el-select
          v-model="selectedTestId"
          placeholder="请选择测试"
          class="test-select"
          filterable
          @change="handleTestChange"
        >
          <el-option
            v-for="t in testOptions"
            :key="t.id"
            :label="`${t.name}${t.status === 'running' ? ' (运行中)' : ''}`"
            :value="t.id"
          />
        </el-select>
        <el-tag v-if="isRunning" type="success" effect="dark" class="running-tag">
          <el-icon class="pulse-icon"><VideoPlay /></el-icon>
          运行中
        </el-tag>
        <el-tag v-else-if="selectedTestId" type="info" effect="dark">已停止</el-tag>
      </div>
    </div>

    <div class="stats-cards">
      <div
        v-for="card in statCards"
        :key="card.key"
        class="stat-card"
        :style="{ background: card.gradient }"
      >
        <div class="stat-card-inner">
          <div class="stat-icon-wrap">
            <el-icon :size="26"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-title">{{ card.title }}</div>
          </div>
        </div>
        <div class="stat-spark">{{ card.unit }}</div>
      </div>
    </div>

    <div class="charts-section">
      <div class="chart-card dark-card">
        <div class="card-header">
          <span class="card-title">TPS & 响应时间</span>
          <span class="card-sub">实时滚动 · 3s</span>
        </div>
        <div ref="tpsRtChartRef" class="chart-container"></div>
      </div>

      <div class="chart-card dark-card">
        <div class="card-header">
          <span class="card-title">CPU & 内存使用率</span>
          <span class="card-sub">实时滚动 · 3s</span>
        </div>
        <div ref="cpuMemChartRef" class="chart-container"></div>
      </div>

      <div class="chart-card dark-card">
        <div class="card-header">
          <span class="card-title">错误率</span>
          <span class="card-sub">实时滚动 · 3s</span>
        </div>
        <div ref="errorChartRef" class="chart-container"></div>
      </div>
    </div>

    <div class="table-section dark-card">
      <div class="card-header">
        <span class="card-title">最近监控数据</span>
        <el-button
          size="small"
          type="primary"
          plain
          :icon="icons.Refresh"
          @click="fetchMonitorData"
        >
          刷新
        </el-button>
      </div>
      <el-table
        :data="tableData"
        stripe
        style="width: 100%"
        max-height="360"
        class="dark-table"
        empty-text="暂无监控数据"
      >
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="{ row }">{{ formatTime(row.timestamp) }}</template>
        </el-table-column>
        <el-table-column prop="tps" label="TPS" width="100" />
        <el-table-column prop="avg_rt" label="平均响应(ms)" width="140" />
        <el-table-column prop="error_rate" label="错误率(%)" width="120">
          <template #default="{ row }">
            <span :class="row.error_rate > 0 ? 'cell-error' : ''">{{ row.error_rate }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="cpu" label="CPU(%)" width="110" />
        <el-table-column prop="memory" label="内存(%)" width="110" />
        <el-table-column prop="active_threads" label="活跃线程" width="120" />
        <el-table-column prop="active_connections" label="活跃连接" width="120" />
        <el-table-column prop="network_in" label="入网(KB/s)" width="130" />
        <el-table-column prop="network_out" label="出网(KB/s)" width="130" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as icons from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const { DataLine, VideoPlay, Refresh } = icons

const selectedTestId = ref('')
const testOptions = ref([])
const timeline = ref([])
const current = ref({})
const isRunning = ref(false)

let pollTimer = null
let tpsRtChart = null
let cpuMemChart = null
let errorChart = null

const tpsRtChartRef = ref(null)
const cpuMemChartRef = ref(null)
const errorChartRef = ref(null)

const MAX_POINTS = 60

const statCards = computed(() => {
  const c = current.value || {}
  return [
    {
      key: 'tps',
      title: '当前 TPS',
      value: fmtNum(c.tps),
      unit: 'req/s',
      icon: icons.DataLine,
      gradient: 'linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)'
    },
    {
      key: 'rt',
      title: '平均响应时间',
      value: fmtNum(c.avg_rt),
      unit: 'ms',
      icon: icons.Timer,
      gradient: 'linear-gradient(135deg, #0891b2 0%, #06b6d4 100%)'
    },
    {
      key: 'error',
      title: '错误率',
      value: fmtNum(c.error_rate),
      unit: '%',
      icon: icons.Warning,
      gradient: 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)'
    },
    {
      key: 'cpu',
      title: 'CPU 使用率',
      value: fmtNum(c.cpu),
      unit: '%',
      icon: icons.Cpu,
      gradient: 'linear-gradient(135deg, #ea580c 0%, #f59e0b 100%)'
    },
    {
      key: 'memory',
      title: '内存使用率',
      value: fmtNum(c.memory),
      unit: '%',
      icon: icons.Files,
      gradient: 'linear-gradient(135deg, #059669 0%, #10b981 100%)'
    },
    {
      key: 'threads',
      title: '活跃线程',
      value: fmtInt(c.active_threads),
      unit: 'threads',
      icon: icons.Connection,
      gradient: 'linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%)'
    }
  ]
})

const tableData = computed(() => {
  return [...timeline.value].slice(-20).reverse()
})

function fmtNum(v) {
  if (v === undefined || v === null || v === '') return '--'
  const n = Number(v)
  if (isNaN(n)) return '--'
  return Number.isInteger(n) ? String(n) : n.toFixed(2)
}

function fmtInt(v) {
  if (v === undefined || v === null || v === '') return '--'
  const n = Number(v)
  return isNaN(n) ? '--' : String(Math.round(n))
}

function formatTime(ts) {
  if (!ts) return '--'
  const d = new Date(ts)
  if (isNaN(d.getTime())) return String(ts)
  const pad = (n) => String(n).padStart(2, '0')
  return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

async function loadTestOptions() {
  try {
    const res = await fetch('/api/v1/perf/tests?status=running')
    const data = await res.json()
    const running = (data.success && data.tests) ? data.tests : []
    testOptions.value = running
    // 允许选择任意测试：再拉取全部测试列表合并
    try {
      const allRes = await fetch('/api/v1/perf/tests')
      const allData = await allRes.json()
      const all = (allData.success && allData.tests) ? allData.tests : []
      const existIds = new Set(running.map(t => t.id))
      all.forEach(t => {
        if (!existIds.has(t.id)) testOptions.value.push(t)
      })
    } catch (e) {
      console.warn('加载全部测试列表失败:', e)
    }
    if (!selectedTestId.value && testOptions.value.length > 0) {
      selectedTestId.value = testOptions.value[0].id
      handleTestChange(selectedTestId.value)
    }
  } catch (error) {
    console.error('加载测试列表失败:', error)
    testOptions.value = []
  }
}

async function fetchMonitorData() {
  if (!selectedTestId.value) return
  try {
    const res = await fetch(`/api/v1/perf/monitor/${selectedTestId.value}`)
    const data = await res.json()
    if (!data.success) return
    const payload = data.data || {}
    isRunning.value = !!payload.is_running
    current.value = payload.current || {}
    const tl = Array.isArray(payload.timeline) ? payload.timeline : []
    // 限制最大点数，实现滚动效果
    timeline.value = tl.slice(-MAX_POINTS)
    nextTick(() => {
      updateTpsRtChart()
      updateCpuMemChart()
      updateErrorChart()
    })
  } catch (error) {
    console.error('获取监控数据失败:', error)
  }
}

function handleTestChange() {
  // 清空历史数据
  timeline.value = []
  current.value = {}
  isRunning.value = false
  stopPolling()
  fetchMonitorData()
  startPolling()
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(() => {
    fetchMonitorData()
  }, 3000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function buildTimeLabels() {
  return timeline.value.map(p => formatTime(p.timestamp))
}

function initTpsRtChart() {
  if (!tpsRtChartRef.value) return
  tpsRtChart = echarts.init(tpsRtChartRef.value, 'dark')
  tpsRtChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: {
      data: ['TPS', '响应时间(ms)'],
      textStyle: { color: '#cbd5e1' },
      top: 0
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [],
      axisLabel: { color: '#94a3b8' },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: [
      {
        type: 'value',
        name: 'TPS',
        position: 'left',
        axisLabel: { color: '#94a3b8' },
        splitLine: { lineStyle: { color: '#1e293b' } },
        axisLine: { lineStyle: { color: '#334155' } }
      },
      {
        type: 'value',
        name: 'RT(ms)',
        position: 'right',
        axisLabel: { color: '#94a3b8' },
        splitLine: { show: false },
        axisLine: { lineStyle: { color: '#334155' } }
      }
    ],
    series: [
      {
        name: 'TPS',
        type: 'line',
        smooth: true,
        symbol: 'none',
        yAxisIndex: 0,
        data: [],
        lineStyle: { color: '#6366f1', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(99, 102, 241, 0.35)' },
            { offset: 1, color: 'rgba(99, 102, 241, 0.02)' }
          ])
        }
      },
      {
        name: '响应时间(ms)',
        type: 'line',
        smooth: true,
        symbol: 'none',
        yAxisIndex: 1,
        data: [],
        lineStyle: { color: '#06b6d4', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(6, 182, 212, 0.25)' },
            { offset: 1, color: 'rgba(6, 182, 212, 0.02)' }
          ])
        }
      }
    ]
  })
}

function updateTpsRtChart() {
  if (!tpsRtChart) return
  tpsRtChart.setOption({
    xAxis: { data: buildTimeLabels() },
    series: [
      { data: timeline.value.map(p => p.tps) },
      { data: timeline.value.map(p => p.avg_rt) }
    ]
  })
}

function initCpuMemChart() {
  if (!cpuMemChartRef.value) return
  cpuMemChart = echarts.init(cpuMemChartRef.value, 'dark')
  cpuMemChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', valueFormatter: (v) => (v == null ? '--' : v + '%') },
    legend: {
      data: ['CPU', '内存'],
      textStyle: { color: '#cbd5e1' },
      top: 0
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [],
      axisLabel: { color: '#94a3b8' },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: { color: '#94a3b8', formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#1e293b' } },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    series: [
      {
        name: 'CPU',
        type: 'line',
        smooth: true,
        symbol: 'none',
        data: [],
        lineStyle: { color: '#f59e0b', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 158, 11, 0.35)' },
            { offset: 1, color: 'rgba(245, 158, 11, 0.02)' }
          ])
        }
      },
      {
        name: '内存',
        type: 'line',
        smooth: true,
        symbol: 'none',
        data: [],
        lineStyle: { color: '#10b981', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(16, 185, 129, 0.35)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0.02)' }
          ])
        }
      }
    ]
  })
}

function updateCpuMemChart() {
  if (!cpuMemChart) return
  cpuMemChart.setOption({
    xAxis: { data: buildTimeLabels() },
    series: [
      { data: timeline.value.map(p => p.cpu) },
      { data: timeline.value.map(p => p.memory) }
    ]
  })
}

function initErrorChart() {
  if (!errorChartRef.value) return
  errorChart = echarts.init(errorChartRef.value, 'dark')
  errorChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', valueFormatter: (v) => (v == null ? '--' : v + '%') },
    legend: {
      data: ['错误率'],
      textStyle: { color: '#cbd5e1' },
      top: 0
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: [],
      axisLabel: { color: '#94a3b8' },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#94a3b8', formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#1e293b' } },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    series: [
      {
        name: '错误率',
        type: 'bar',
        data: [],
        barWidth: '50%',
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#ef4444' },
            { offset: 1, color: '#7f1d1d' }
          ])
        }
      }
    ]
  })
}

function updateErrorChart() {
  if (!errorChart) return
  errorChart.setOption({
    xAxis: { data: buildTimeLabels() },
    series: [{ data: timeline.value.map(p => p.error_rate) }]
  })
}

function handleResize() {
  tpsRtChart?.resize()
  cpuMemChart?.resize()
  errorChart?.resize()
}

watch(selectedTestId, (val) => {
  if (val) handleTestChange()
})

onMounted(async () => {
  await loadTestOptions()
  nextTick(() => {
    initTpsRtChart()
    initCpuMemChart()
    initErrorChart()
  })
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  stopPolling()
  window.removeEventListener('resize', handleResize)
  tpsRtChart?.dispose()
  cpuMemChart?.dispose()
  errorChart?.dispose()
})
</script>

<style scoped>
.perf-monitor {
  padding: 20px;
  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
  min-height: 100%;
  color: #e2e8f0;
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
  flex: 1;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 4px;
}

.page-desc {
  font-size: 14px;
  color: #94a3b8;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  color: #6366f1;
}

.filter-label {
  font-size: 14px;
  color: #cbd5e1;
}

.test-select {
  width: 240px;
}

.running-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.pulse-icon {
  animation: pulse 1.2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  border-radius: 14px;
  padding: 20px;
  color: #fff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s, box-shadow 0.2s;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.35);
}

.stat-card::before {
  content: '';
  position: absolute;
  top: -40px;
  right: -40px;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.stat-card-inner {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  z-index: 1;
}

.stat-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.18);
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
  line-height: 1.2;
}

.stat-title {
  font-size: 13px;
  opacity: 0.9;
  margin-top: 2px;
}

.stat-spark {
  position: absolute;
  bottom: 12px;
  right: 16px;
  font-size: 12px;
  opacity: 0.85;
  z-index: 1;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.dark-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 14px;
  padding: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.chart-card {
  min-height: 320px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #f1f5f9;
}

.card-sub {
  font-size: 12px;
  color: #64748b;
}

.chart-container {
  height: 260px;
  width: 100%;
}

.table-section {
  margin-bottom: 24px;
}

.dark-table {
  background: transparent;
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: #0f172a;
  --el-table-border-color: #334155;
  --el-table-header-text-color: #cbd5e1;
  --el-table-text-color: #e2e8f0;
  --el-table-row-hover-bg-color: rgba(99, 102, 241, 0.12);
}

.cell-error {
  color: #f87171;
  font-weight: 600;
}

:deep(.dark-table .el-table__body-wrapper) {
  background-color: transparent;
}

:deep(.dark-table th.el-table__cell) {
  background-color: #0f172a !important;
}

:deep(.dark-table tr) {
  background-color: transparent !important;
}

:deep(.dark-table .el-table__row:hover > td.el-table__cell) {
  background-color: rgba(99, 102, 241, 0.12) !important;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-right {
    flex-wrap: wrap;
  }

  .test-select {
    width: 100%;
  }

  .charts-section {
    grid-template-columns: 1fr;
  }
}
</style>
