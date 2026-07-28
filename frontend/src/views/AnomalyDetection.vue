<template>
  <div class="anomaly-detection">
    <div class="page-header">
      <div class="header-left">
        <div class="logo-section">
          <el-icon :size="32" class="logo-icon"><component :is="icons.WarningFilled" /></el-icon>
          <div>
            <h1>异常检测</h1>
            <p class="subtitle">AI驱动的实时异常检测与分析</p>
          </div>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <!-- 控制区：报告选择 + 检测按钮 -->
      <el-card class="control-card" shadow="never">
        <div class="control-bar">
          <div class="control-left">
            <span class="control-label">
              <el-icon><component :is="icons.Document" /></el-icon>
              选择性能报告：
            </span>
            <el-select
              v-model="selectedReportId"
              placeholder="请选择性能报告"
              class="report-select"
              :loading="reportsLoading"
              filterable
              @change="handleReportChange"
            >
              <el-option
                v-for="report in reports"
                :key="report.id"
                :label="buildReportLabel(report)"
                :value="report.id"
              />
            </el-select>
            <el-tag v-if="currentReportMeta" size="small" type="info" class="meta-tag">
              {{ currentReportMeta }}
            </el-tag>
          </div>
          <div class="control-right">
            <el-button
              type="primary"
              :icon="icons.VideoPlay"
              :loading="detecting"
              :disabled="!selectedReportId"
              @click="handleDetect"
            >
              {{ detecting ? '正在检测...' : '开始异常检测' }}
            </el-button>
            <el-button
              :icon="icons.Refresh"
              :disabled="detecting"
              @click="loadReports"
            >
              刷新报告
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 空状态 -->
      <el-card v-if="!hasResult && !detecting" class="empty-card" shadow="never">
        <div class="empty-state">
          <el-icon :size="64" class="empty-icon"><component :is="icons.DataAnalysis" /></el-icon>
          <p class="empty-title">暂无检测结果</p>
          <p class="empty-desc">请选择一份性能报告，然后点击「开始异常检测」</p>
        </div>
      </el-card>

      <!-- 检测中骨架 -->
      <el-card v-if="detecting" class="loading-card" shadow="never">
        <div class="loading-state">
          <el-icon :size="48" class="loading-icon"><component :is="icons.Loading" /></el-icon>
          <p class="loading-text">AI 正在分析性能数据，检测异常点...</p>
        </div>
      </el-card>

      <!-- 检测结果 -->
      <template v-if="hasResult">
        <!-- 汇总卡片 -->
        <div class="summary-cards">
          <el-card class="summary-card total" shadow="never">
            <div class="summary-icon"><el-icon :size="24"><component :is="icons.DataLine" /></el-icon></div>
            <div class="summary-info">
              <div class="summary-value">{{ detectionSummary.total }}</div>
              <div class="summary-label">异常总数</div>
            </div>
          </el-card>
          <el-card class="summary-card critical" shadow="never">
            <div class="summary-icon"><el-icon :size="24"><component :is="icons.CircleCloseFilled" /></el-icon></div>
            <div class="summary-info">
              <div class="summary-value">{{ detectionSummary.critical }}</div>
              <div class="summary-label">Critical 严重</div>
            </div>
          </el-card>
          <el-card class="summary-card high" shadow="never">
            <div class="summary-icon"><el-icon :size="24"><component :is="icons.WarningFilled" /></el-icon></div>
            <div class="summary-info">
              <div class="summary-value">{{ detectionSummary.high }}</div>
              <div class="summary-label">High 高优</div>
            </div>
          </el-card>
          <el-card class="summary-card model" shadow="never">
            <div class="summary-icon"><el-icon :size="24"><component :is="icons.Cpu" /></el-icon></div>
            <div class="summary-info">
              <div class="summary-value text-value">{{ detectionSummary.modelUsed || '-' }}</div>
              <div class="summary-label">检测模型</div>
            </div>
          </el-card>
          <el-card class="summary-card time" shadow="never">
            <div class="summary-icon"><el-icon :size="24"><component :is="icons.Timer" /></el-icon></div>
            <div class="summary-info">
              <div class="summary-value text-value">{{ detectionSummary.detectionTime || '-' }}</div>
              <div class="summary-label">检测耗时</div>
            </div>
          </el-card>
        </div>

        <!-- 异常时间线图表 -->
        <el-card class="chart-card timeline-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><component :is="icons.TrendCharts" /></el-icon>
                异常时间线
              </span>
              <div class="header-legend">
                <span v-for="(color, type) in typeColors" :key="type" class="legend-item">
                  <span class="legend-dot" :style="{ backgroundColor: color }"></span>
                  {{ typeLabels[type] }}
                </span>
              </div>
            </div>
          </template>
          <div ref="timelineChartRef" class="chart-container large"></div>
        </el-card>

        <!-- 分布饼图 -->
        <div class="distribution-row">
          <el-card class="chart-card" shadow="never">
            <template #header>
              <span class="card-title">
                <el-icon><component :is="icons.PieChart" /></el-icon>
                按类型分布
              </span>
            </template>
            <div ref="typePieRef" class="chart-container"></div>
          </el-card>
          <el-card class="chart-card" shadow="never">
            <template #header>
              <span class="card-title">
                <el-icon><component :is="icons.PieChart" /></el-icon>
                按严重程度分布
              </span>
            </template>
            <div ref="severityPieRef" class="chart-container"></div>
          </el-card>
        </div>

        <!-- 异常列表 -->
        <el-card class="table-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><component :is="icons.List" /></el-icon>
                异常列表
              </span>
              <div class="filter-bar">
                <el-select v-model="filterType" placeholder="类型筛选" clearable size="small" class="filter-select">
                  <el-option v-for="(label, type) in typeLabels" :key="type" :label="label" :value="type" />
                </el-select>
                <el-select v-model="filterSeverity" placeholder="严重程度筛选" clearable size="small" class="filter-select">
                  <el-option v-for="(label, sev) in severityLabels" :key="sev" :label="label" :value="sev" />
                </el-select>
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索描述..."
                  size="small"
                  clearable
                  class="search-input"
                >
                  <template #prefix>
                    <el-icon><component :is="icons.Search" /></el-icon>
                  </template>
                </el-input>
              </div>
            </div>
          </template>

          <el-table :data="filteredAnomalies" stripe border style="width: 100%">
            <el-table-column type="index" label="#" width="55" align="center" />
            <el-table-column prop="timestamp" label="时间戳" width="170">
              <template #default="scope">
                {{ formatTimestamp(scope.row.timestamp) }}
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="170">
              <template #default="scope">
                <el-tag
                  :color="typeColors[scope.row.type]"
                  effect="dark"
                  size="small"
                  class="type-tag"
                >
                  {{ typeLabels[scope.row.type] || scope.row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="severity" label="严重程度" width="120" align="center">
              <template #default="scope">
                <el-tag
                  :type="severityTagType(scope.row.severity)"
                  :effect="scope.row.severity === 'critical' ? 'dark' : 'light'"
                  size="small"
                >
                  {{ severityLabels[scope.row.severity] || scope.row.severity }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="240" show-overflow-tooltip />
            <el-table-column prop="value" label="异常值" width="120" align="right">
              <template #default="scope">
                <span class="value-cell">{{ formatValue(scope.row.value) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="baseline" label="基线值" width="120" align="right">
              <template #default="scope">
                <span class="baseline-cell">{{ formatValue(scope.row.baseline) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="偏差" width="110" align="center">
              <template #default="scope">
                <span :class="['deviation-cell', deviationClass(scope.row)]">
                  {{ deviationText(scope.row) }}
                </span>
              </template>
            </el-table-column>
          </el-table>

          <div v-if="filteredAnomalies.length === 0" class="no-data">
            <el-icon :size="32"><component :is="icons.Box" /></el-icon>
            <span>没有匹配的异常记录</span>
          </div>
        </el-card>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as icons from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ===== 静态配置 =====
const typeColors = {
  tps_drop: '#8b5cf6',
  response_time_spike: '#ef4444',
  error_rate_spike: '#7f1d1d',
  cpu_overload: '#f59e0b'
}

const typeLabels = {
  tps_drop: 'TPS下降',
  response_time_spike: '响应时间飙升',
  error_rate_spike: '错误率飙升',
  cpu_overload: 'CPU过载'
}

const severityLabels = {
  critical: 'Critical',
  high: 'High',
  medium: 'Medium',
  low: 'Low'
}

// 异常类型对应的指标字段（用于在时间线图表上定位所属指标）
const typeMetricMap = {
  tps_drop: 'tps',
  response_time_spike: 'response_time',
  error_rate_spike: 'error_rate',
  cpu_overload: 'cpu'
}

// ===== 状态 =====
const reports = ref([])
const selectedReportId = ref('')
const reportsLoading = ref(false)
const detecting = ref(false)

const anomalies = ref([])
const timelineData = ref([])
const detectionSummary = reactive({
  total: 0,
  critical: 0,
  high: 0,
  modelUsed: '',
  detectionTime: ''
})

const filterType = ref('')
const filterSeverity = ref('')
const searchKeyword = ref('')

// ===== 图表 =====
const timelineChartRef = ref(null)
const typePieRef = ref(null)
const severityPieRef = ref(null)

let timelineChartInstance = null
let typePieInstance = null
let severityPieInstance = null

// ===== 计算属性 =====
const hasResult = computed(() => anomalies.value.length > 0 || detectionSummary.total > 0)

const currentReportMeta = computed(() => {
  if (!selectedReportId.value) return ''
  const r = reports.value.find(item => item.id === selectedReportId.value)
  if (!r) return ''
  const parts = []
  if (r.environment || r.env) parts.push(r.environment || r.env)
  if (r.start_time || r.created_at) parts.push(r.start_time || r.created_at)
  return parts.join(' · ')
})

const filteredAnomalies = computed(() => {
  let list = anomalies.value
  if (filterType.value) {
    list = list.filter(a => a.type === filterType.value)
  }
  if (filterSeverity.value) {
    list = list.filter(a => (a.severity || '').toLowerCase() === filterSeverity.value)
  }
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    list = list.filter(a => (a.description || '').toLowerCase().includes(kw))
  }
  return list
})

// ===== 工具方法 =====
const buildReportLabel = (report) => {
  const name = report.name || report.title || report.scenario_name || `报告 #${report.id}`
  const time = report.start_time || report.created_at || ''
  return time ? `${name} (${time})` : name
}

const formatTimestamp = (ts) => {
  if (!ts && ts !== 0) return '-'
  const str = String(ts)
  // 纯数字（秒/毫秒时间戳）
  if (/^\d+$/.test(str)) {
    const num = Number(str)
    const ms = str.length > 10 ? num : num * 1000
    const d = new Date(ms)
    if (!isNaN(d.getTime())) {
      return d.toLocaleString('zh-CN', { hour12: false })
    }
  }
  return str
}

const formatValue = (val) => {
  if (val === null || val === undefined || val === '') return '-'
  const num = Number(val)
  if (isNaN(num)) return String(val)
  return Number.isInteger(num) ? String(num) : num.toFixed(2)
}

const severityTagType = (severity) => {
  const s = (severity || '').toLowerCase()
  if (s === 'critical') return 'danger'
  if (s === 'high') return 'danger'
  if (s === 'medium') return 'warning'
  return 'info'
}

const deviationClass = (row) => {
  const val = Number(row.value)
  const base = Number(row.baseline)
  if (isNaN(val) || isNaN(base) || base === 0) return ''
  const type = row.type
  // 对于 tps_drop，下降为异常；其余为上升异常
  if (type === 'tps_drop') return val < base ? 'bad' : 'good'
  return val > base ? 'bad' : 'good'
}

const deviationText = (row) => {
  const val = Number(row.value)
  const base = Number(row.baseline)
  if (isNaN(val) || isNaN(base) || base === 0) return '-'
  const pct = ((val - base) / base) * 100
  const sign = pct >= 0 ? '+' : ''
  return `${sign}${pct.toFixed(1)}%`
}

// ===== API 调用 =====
const loadReports = async () => {
  reportsLoading.value = true
  try {
    const response = await fetch('/api/v1/perf/reports')
    const data = await response.json()
    if (data.success !== false) {
      reports.value = data.reports || []
    } else {
      ElMessage.error(data.message || '加载报告列表失败')
    }
  } catch (error) {
    console.error('加载报告列表失败:', error)
    ElMessage.error('加载报告列表失败，请检查后端服务')
  } finally {
    reportsLoading.value = false
  }
}

const loadReportDetail = async (reportId) => {
  try {
    const response = await fetch(`/api/v1/perf/reports/${reportId}`)
    const data = await response.json()
    if (data.success !== false && data.report) {
      timelineData.value = data.report.timeline || []
    }
  } catch (error) {
    console.error('加载报告详情失败:', error)
  }
}

const handleReportChange = (reportId) => {
  if (!reportId) {
    timelineData.value = []
    return
  }
  loadReportDetail(reportId)
}

const handleDetect = async () => {
  if (!selectedReportId.value) {
    ElMessage.warning('请先选择一份性能报告')
    return
  }
  detecting.value = true
  // 重置结果
  anomalies.value = []
  timelineData.value = []
  resetSummary()

  try {
    // 并行获取报告详情（时间线）与异常检测
    const [detailPromise, detectPromise] = await Promise.all([
      loadReportDetail(selectedReportId.value),
      (async () => {
        const response = await fetch(`/api/v1/perf/ai/anomaly/${selectedReportId.value}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        if (!response.ok) {
          let errorDetail = `HTTP ${response.status}`
          try {
            const errorData = await response.json()
            errorDetail = errorData.detail || errorData.message || errorData.error || errorDetail
          } catch (_) {
            // ignore
          }
          throw new Error(errorDetail)
        }
        return response.json()
      })()
    ])

    void detailPromise

    const data = detectPromise

    if (data.success) {
      const list = data.anomalies || []
      anomalies.value = normalizeAnomalies(list)
      detectionSummary.total = data.total != null ? data.total : list.length
      detectionSummary.modelUsed = data.model_used || data.modelUsed || '-'
      detectionSummary.detectionTime = data.detection_time || data.detectionTime || '-'
      detectionSummary.critical = countSeverity(list, 'critical')
      detectionSummary.high = countSeverity(list, 'high')

      ElMessage.success(`检测完成，共发现 ${detectionSummary.total} 个异常`)

      await nextTick()
      initAllCharts()
      updateAllCharts()
    } else {
      ElMessage.error(data.message || data.error || '异常检测失败')
    }
  } catch (error) {
    console.error('异常检测失败:', error)
    ElMessage.error({
      message: '异常检测失败：' + (error.message || '请检查后端服务'),
      duration: 5000,
      showClose: true
    })
  } finally {
    detecting.value = false
  }
}

const normalizeAnomalies = (list) => {
  return list.map((item, index) => {
    const type = item.type || item.anomaly_type || 'unknown'
    const severity = (item.severity || 'medium').toLowerCase()
    const ts = item.timestamp || item.time || item.ts || index
    return {
      ...item,
      type,
      severity,
      timestamp: ts,
      description: item.description || item.desc || item.message || '-',
      value: item.value != null ? item.value : item.actual_value,
      baseline: item.baseline != null ? item.baseline : item.expected_value
    }
  })
}

const countSeverity = (list, target) => {
  return list.filter(a => (a.severity || '').toLowerCase() === target).length
}

const resetSummary = () => {
  detectionSummary.total = 0
  detectionSummary.critical = 0
  detectionSummary.high = 0
  detectionSummary.modelUsed = ''
  detectionSummary.detectionTime = ''
}

// ===== 图表 =====
function initAllCharts() {
  if (timelineChartRef.value && !timelineChartInstance) {
    timelineChartInstance = echarts.init(timelineChartRef.value)
  }
  if (typePieRef.value && !typePieInstance) {
    typePieInstance = echarts.init(typePieRef.value)
  }
  if (severityPieRef.value && !severityPieInstance) {
    severityPieInstance = echarts.init(severityPieRef.value)
  }
}

function updateAllCharts() {
  updateTimelineChart()
  updateTypePie()
  updateSeverityPie()
}

function buildTimelineAxis() {
  // 优先使用报告详情中的 timeline；若无则从异常列表构建时间轴
  if (timelineData.value && timelineData.value.length > 0) {
    const xs = timelineData.value.map(p => p.timestamp || p.time || p.ts || '')
    return xs.map(x => formatTimestamp(x))
  }
  // 从异常时间戳去重排序
  const xs = [...new Set(anomalies.value.map(a => formatTimestamp(a.timestamp)))]
  return xs.sort()
}

function buildMetricSeries(metricKey) {
  if (timelineData.value && timelineData.value.length > 0) {
    return timelineData.value.map(p => {
      const v = p[metricKey]
      return v != null ? Number(v) : null
    })
  }
  return []
}

function buildAnomalyScatter(metricKey, anomalyType) {
  // 在时间轴上定位异常点，取对应指标的值
  const points = []
  anomalies.value
    .filter(a => a.type === anomalyType)
    .forEach(a => {
      const tsLabel = formatTimestamp(a.timestamp)
      const idx = buildTimelineAxis().indexOf(tsLabel)
      let yVal = Number(a.value)
      // 若时间线存在该指标值，优先使用时间线值，使散点落在曲线上
      if (idx >= 0) {
        const metricVal = buildMetricSeries(metricKey)[idx]
        if (metricVal != null && !isNaN(metricVal)) yVal = metricVal
      }
      if (isNaN(yVal)) yVal = 0
      points.push({
        name: typeLabels[anomalyType] || anomalyType,
        value: [tsLabel, yVal],
        itemStyle: { color: typeColors[anomalyType] },
        anomaly: a
      })
    })
  return points
}

function updateTimelineChart() {
  if (!timelineChartInstance) return
  const xAxisData = buildTimelineAxis()

  const series = []
  const metrics = [
    { key: 'tps', name: 'TPS', color: '#6366f1', type: 'line' },
    { key: 'response_time', name: '响应时间(ms)', color: '#06b6d4', type: 'line' },
    { key: 'error_rate', name: '错误率(%)', color: '#10b981', type: 'line' },
    { key: 'cpu', name: 'CPU(%)', color: '#f59e0b', type: 'line' }
  ]

  let hasTimelineMetrics = false
  metrics.forEach(m => {
    const data = buildMetricSeries(m.key)
    if (data.length > 0) {
      hasTimelineMetrics = true
      series.push({
        name: m.name,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: m.color, width: 2 },
        itemStyle: { color: m.color },
        data: data
      })
    }
  })

  // 异常散点（按类型分组，叠加在对应指标曲线上）
  Object.keys(typeColors).forEach(anomalyType => {
    const metricKey = typeMetricMap[anomalyType]
    const scatterData = buildAnomalyScatter(metricKey, anomalyType)
    if (scatterData.length > 0) {
      series.push({
        name: typeLabels[anomalyType],
        type: 'scatter',
        symbolSize: 14,
        data: scatterData,
        itemStyle: {
          color: typeColors[anomalyType],
          borderColor: '#fff',
          borderWidth: 2,
          shadowBlur: 8,
          shadowColor: typeColors[anomalyType]
        },
        emphasis: {
          focus: 'series',
          label: {
            show: true,
            position: 'top',
            formatter: (p) => p.data.anomaly ? p.data.anomaly.description : p.name
          }
        },
        z: 10
      })
    }
  })

  // 若没有时间线指标且没有异常点，给出占位
  if (series.length === 0) {
    series.push({
      name: '暂无数据',
      type: 'line',
      data: xAxisData.map(() => 0)
    })
  }

  void hasTimelineMetrics

  timelineChartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      top: 0,
      textStyle: { color: '#6b7280' }
    },
    grid: { left: '3%', right: '4%', bottom: '8%', top: '12%', containLabel: true },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { type: 'slider', start: 0, end: 100, height: 18, bottom: 8 }
    ],
    xAxis: {
      type: 'category',
      data: xAxisData,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280', rotate: xAxisData.length > 8 ? 30 : 0 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280' },
      splitLine: { lineStyle: { color: '#f3f4f6' } }
    },
    series
  }, true)
}

function updateTypePie() {
  if (!typePieInstance) return
  const counts = {}
  anomalies.value.forEach(a => {
    const key = a.type || 'unknown'
    counts[key] = (counts[key] || 0) + 1
  })
  const data = Object.keys(counts).map(type => ({
    name: typeLabels[type] || type,
    value: counts[type],
    itemStyle: { color: typeColors[type] || '#909399' }
  }))

  typePieInstance.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { color: '#6b7280' }
    },
    series: [{
      name: '异常类型分布',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['38%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
      labelLine: { show: false },
      data: data.length > 0 ? data : [{ name: '暂无数据', value: 0 }]
    }]
  }, true)
}

function updateSeverityPie() {
  if (!severityPieInstance) return
  const severityColors = {
    critical: '#7f1d1d',
    high: '#ef4444',
    medium: '#f59e0b',
    low: '#909399'
  }
  const counts = {}
  anomalies.value.forEach(a => {
    const key = (a.severity || 'medium').toLowerCase()
    counts[key] = (counts[key] || 0) + 1
  })
  const data = Object.keys(counts).map(sev => ({
    name: severityLabels[sev] || sev,
    value: counts[sev],
    itemStyle: { color: severityColors[sev] || '#909399' }
  }))

  severityPieInstance.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { color: '#6b7280' }
    },
    series: [{
      name: '严重程度分布',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['38%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
      labelLine: { show: false },
      data: data.length > 0 ? data : [{ name: '暂无数据', value: 0 }]
    }]
  }, true)
}

function handleResize() {
  timelineChartInstance?.resize()
  typePieInstance?.resize()
  severityPieInstance?.resize()
}

// 监听筛选变化重绘时间线（异常点可能变化）
watch([filterType, filterSeverity, searchKeyword], () => {
  // 表格筛选不影响图表，图表始终展示全量异常
})

onMounted(() => {
  loadReports()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  timelineChartInstance?.dispose()
  typePieInstance?.dispose()
  severityPieInstance?.dispose()
})
</script>

<style scoped>
.anomaly-detection {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.page-header {
  background: linear-gradient(135deg, #7c3aed 0%, #db2777 100%);
  color: white;
  padding: 24px 32px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  color: #fde047;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.subtitle {
  font-size: 14px;
  opacity: 0.9;
  margin: 4px 0 0 0;
}

.content-wrapper {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 1920px;
  margin: 0 auto;
}

/* 控制区 */
.control-card {
  border-radius: 12px;
}

.control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.control-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.control-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.report-select {
  width: 320px;
}

.meta-tag {
  max-width: 280px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.control-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 空状态 / 加载 */
.empty-card,
.loading-card {
  border-radius: 12px;
}

.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #9ca3af;
  gap: 12px;
}

.empty-icon,
.loading-icon {
  color: #c0c4cc;
}

.loading-icon {
  color: #7c3aed;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-title {
  font-size: 18px;
  font-weight: 500;
  color: #6b7280;
  margin: 0;
}

.empty-desc {
  font-size: 14px;
  color: #9ca3af;
  margin: 0;
}

.loading-text {
  font-size: 15px;
  color: #6b7280;
  margin: 0;
}

/* 汇总卡片 */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.summary-card {
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 8px 8px 20px;
  border-left: 4px solid transparent;
}

.summary-card.total { border-left-color: #6366f1; }
.summary-card.critical { border-left-color: #7f1d1d; }
.summary-card.high { border-left-color: #ef4444; }
.summary-card.model { border-left-color: #8b5cf6; }
.summary-card.time { border-left-color: #06b6d4; }

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.summary-card.total .summary-icon { background: rgba(99, 102, 241, 0.12); color: #6366f1; }
.summary-card.critical .summary-icon { background: rgba(127, 29, 29, 0.12); color: #7f1d1d; }
.summary-card.high .summary-icon { background: rgba(239, 68, 68, 0.12); color: #ef4444; }
.summary-card.model .summary-icon { background: rgba(139, 92, 246, 0.12); color: #8b5cf6; }
.summary-card.time .summary-icon { background: rgba(6, 182, 212, 0.12); color: #06b6d4; }

.summary-info {
  min-width: 0;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.2;
}

.summary-value.text-value {
  font-size: 16px;
  word-break: break-all;
}

.summary-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

/* 图表卡片 */
.chart-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.header-legend {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #6b7280;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.chart-container {
  width: 100%;
  height: 320px;
}

.chart-container.large {
  height: 420px;
}

/* 分布行 */
.distribution-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* 表格 */
.table-card {
  border-radius: 12px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-select {
  width: 160px;
}

.search-input {
  width: 220px;
}

.type-tag {
  color: #fff !important;
  border: none !important;
}

.value-cell {
  color: #ef4444;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.baseline-cell {
  color: #6b7280;
  font-family: 'Courier New', monospace;
}

.deviation-cell {
  font-weight: 600;
  font-size: 13px;
}

.deviation-cell.bad {
  color: #ef4444;
}

.deviation-cell.good {
  color: #10b981;
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #c0c4cc;
  gap: 8px;
}

@media (max-width: 1200px) {
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .distribution-row {
    grid-template-columns: 1fr;
  }

  .report-select {
    width: 240px;
  }
}
</style>
